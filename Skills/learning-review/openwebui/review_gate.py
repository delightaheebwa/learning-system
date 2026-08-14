"""
review_gate — Learning System quality gate for Open WebUI.

Runs the independent review gate defined in Skills/learning-review/SKILL.md:
  - validates every wiki path exists (fail fast, like the original script's exit 2)
  - fetches the source URL itself (dead URL aborts, like exit 1)
  - builds the review prompt from a FIXED template (never editable at runtime)
  - calls the configured review model via the Open WebUI chat-completions API
  - returns the verdict JSON, which the chat saves to
    Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json

INSTALL
-------
1. Open WebUI → Admin Panel → Workspace → Tools → "+" (Create Tool).
2. Paste this whole file, name it "review_gate", Save.
3. Open your profile → Tools → enable review_gate for the chat you use.
4. Set the Valves (gear icon): Open WebUI base URL, an API key
   (Admin Panel → API Keys → generate one), and the review model id.
   If you leave repo_path empty, wiki-path validation is skipped.

Then just ask in chat after an ingest: "run the review gate"
(source/concepts/wiki paths are passed automatically by the model).
"""

import json
import os
import re
from datetime import datetime, timezone

try:
    from pydantic import BaseModel, Field
except Exception:
    BaseModel = None
    Field = None

try:
    from open_webui.tools import tools
except Exception:
    def tools(fn):
        return fn

# --------------------------------------------------------------------------
# Fixed review prompt. Keep in sync with
# Skills/learning-review/templates/review.template.md (this copy is the one
# used at runtime when the repo is not on the server).
# --------------------------------------------------------------------------
REVIEW_TEMPLATE = """# Learning System Review Gate — Review Prompt (fixed template)

You are an independent, critical reviewer for a spaced-repetition learning system.
Your job is to catch problems in ingest output. You are a critic, not a rewrite bot:
never rewrite content, only flag issues with severity.

## Inputs

- SOURCE URL: {source}
- SOURCE CONTENT (fetched from the URL; if empty, say so and review for internal consistency only):
{source_content}

- CONCEPTS: {concepts}
- WIKI FILES REVIEWED: {wiki_paths}
- WIKI CONTENT (each file, separated by === FILE ===):
{wiki_content}

- PASS (cycle): {pass_number}

## Scope

Review ONLY:
1. The wiki pages listed above.
2. The Active Concepts insight rows / question seeds derived from this ingest.

Mechanical date updates and review session notes are out of scope.

## What to check

1. **Accuracy / correctness** — claims that contradict the source content, wrong mechanisms, wrong formulas or definitions, invented facts.
2. **Clarity** — phrasing that would mislead a learner or is so ambiguous it fails to teach.
3. **Completeness** — load-bearing points from the source that were dropped or misrepresented.

## Rules

- Only flag issues worth fixing. High/medium severity only; low-severity nits get one combined note.
- Each issue: severity (high | medium | low), location (file/section), issue (specific and actionable).
- Material in the wiki pages that is NOT present in the source must be flagged as a scope problem unless a scope note in the page explains the addition.
- Output ONLY valid JSON with this schema:

```json
{{
  "verdict": "PASS" | "ISSUES",
  "issues": [
    {{ "severity": "high|medium|low", "location": "...", "issue": "..." }}
  ]
}}
```

- `"verdict": "PASS"` only when there are no high/medium issues."""


def _http_get(url, timeout):
    """Fetch a URL. Tries requests, then urllib (stdlib) as fallback."""
    try:
        import requests  # noqa
        resp = requests.get(url, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "review_gate/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")


def _http_post_json(url, payload, api_key, timeout):
    """POST JSON to the Open WebUI chat-completions API."""
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        import requests  # noqa
        resp = requests.post(url, data=body, headers=headers, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        import urllib.request
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")


def _extract_json(text):
    """Pull a JSON object out of a model response (handles code fences/prose)."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start:end + 1]
    try:
        return json.loads(text)
    except Exception:
        raise ValueError(f"Review model did not return valid JSON: {text[:500]}")


class Tools:
    class Valves:
        if BaseModel is not None and Field is not None:
            openwebui_base_url: str = Field(
                default=os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3000"),
                description="Your Open WebUI base URL, e.g. http://localhost:3000",
            )
            openwebui_api_key: str = Field(
                default=os.environ.get("OPENWEBUI_API_KEY", ""),
                description="API key (Admin Panel → API Keys). Falls back to env OPENWEBUI_API_KEY.",
            )
            review_model: str = Field(
                default=os.environ.get("REVIEW_GATE_MODEL", ""),
                description="Model id for reviews, e.g. gpt-4o. Empty = try server default.",
            )
            repo_path: str = Field(
                default=os.environ.get("LEARNING_REPO_PATH", ""),
                description="Absolute path to the learning-system repo on this server (for wiki path validation).",
            )
            timeout: int = Field(default=60, description="HTTP timeout in seconds.")

    @tools
    def review_gate(self, source: str, concepts: str, wiki_paths: str, pass_number: int = 1) -> str:
        """
        Run the independent review gate on learning-system ingest output.
        source: URL the ingest came from (must be a live, stable URL).
        concepts: comma-separated concept names.
        wiki_paths: comma-separated wiki file paths (relative to the repo, e.g. "Knowledge Wiki/wiki/Concept.md").
        pass_number: cycle number (1 or 2) — filename only, never softens the review.
        Returns verdict JSON; save it to Learning System/Reviews/Quality Gates/.
        """
        valves = getattr(self, "valves", None)
        base_url = getattr(valves, "openwebui_base_url", "") or os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3000")
        api_key = getattr(valves, "openwebui_api_key", "") or os.environ.get("OPENWEBUI_API_KEY", "")
        model = getattr(valves, "review_model", "") or os.environ.get("REVIEW_GATE_MODEL", "")
        repo_path = getattr(valves, "repo_path", "") or os.environ.get("LEARNING_REPO_PATH", "")
        timeout = getattr(valves, "timeout", 60)

        concept_list = [c.strip() for c in concepts.split(",") if c.strip()]
        path_list = [p.strip() for p in wiki_paths.split(",") if p.strip()]

        if not concept_list:
            return json.dumps({"error": "no concepts given"}, indent=2)
        if not path_list:
            return json.dumps({"error": "no wiki paths given"}, indent=2)

        # 1. Validate wiki paths (fail fast, like exit 2 in the original script).
        missing = []
        wiki_content_parts = []
        for p in path_list:
            full = os.path.join(repo_path, p) if repo_path else p
            if not os.path.isfile(full):
                missing.append(p)
            else:
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        wiki_content_parts.append(f"=== FILE: {p} ===\n{f.read()}")
                except Exception as e:
                    missing.append(f"{p} (unreadable: {e})")
        if missing:
            return json.dumps(
                {"error": "wiki path(s) do not exist — fix and re-run", "missing": missing},
                indent=2,
            )

        # 2. Fetch source (dead URL aborts, like exit 1).
        try:
            status, source_content = _http_get(source, timeout)
            if status >= 400:
                return json.dumps(
                    {"error": f"source URL returned HTTP {status} — aborting, no verdict written", "source": source},
                    indent=2,
                )
        except Exception as e:
            return json.dumps(
                {"error": f"could not fetch source URL — aborting, no verdict written: {e}", "source": source},
                indent=2,
            )

        # 3. Build the fixed prompt.
        prompt = REVIEW_TEMPLATE.format(
            source=source,
            source_content=source_content[:60000],
            concepts=", ".join(concept_list),
            wiki_paths=", ".join(path_list),
            wiki_content="\n\n".join(wiki_content_parts)[:120000],
            pass_number=pass_number,
        )

        # 4. Call the review model via Open WebUI chat-completions.
        if not api_key:
            return json.dumps(
                {"error": "no API key configured — set the Valve or env OPENWEBUI_API_KEY"},
                indent=2,
            )
        url = base_url.rstrip("/") + "/api/chat/completions"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        if model:
            payload["model"] = model
        try:
            status, resp_text = _http_post_json(url, payload, api_key, timeout)
        except Exception as e:
            return json.dumps({"error": f"review model call failed: {e}"}, indent=2)
        if status >= 400:
            return json.dumps(
                {"error": f"review model call returned HTTP {status}: {resp_text[:500]}"},
                indent=2,
            )
        try:
            data = json.loads(resp_text)
            verdict = _extract_json(data["choices"][0]["message"]["content"])
        except Exception as e:
            return json.dumps({"error": f"could not parse review model response: {e}"}, indent=2)

        # 5. Return verdict JSON in the repo's existing schema.
        return json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "source": source,
                "concepts": concept_list,
                "wiki_paths": path_list,
                "pass": str(pass_number),
                "model": model or "(server default)",
                "verdict": verdict,
            },
            indent=2,
        )
