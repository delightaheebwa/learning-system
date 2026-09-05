#!/usr/bin/env python3
"""
setup_openwebui — one-shot installer for the Learning System in Open WebUI.

Creates (or updates) everything the system needs, using the Open WebUI REST API:

  - 4 Skills        from Skills/*/SKILL.md
  - 3 Model presets Scout / Learning Tutor / Clerk
  - 1 Gate Filter   (Function) gate_pipe — deterministic delegation gate
  - 7 Prompts       /swe /review /ingest /teach /lesson /continue /pause
  - Subagent system prompt (keyed GATE: templates)

All verification gates run as foreground subagent tasks (delegate_task) with
Pydantic envelope validation; fixed prompts live in the global subagent system
prompt. Legacy Tools remain dormant.

Models are configured AFTER install in the Open WebUI UI (one field per task —
see OPENWEBUI.md). The values below are FIRST-INSTALL BOOTSTRAP defaults only:
the installer preserves any non-empty base_model_id already set in the UI.
Re-running never resets your models.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILLS = [
    "Skills/learning-system/SKILL.md",
    "Skills/learning-teach/SKILL.md",
    "Skills/learning-review/SKILL.md",
    "Skills/llm-wiki/SKILL.md",
]

TUTOR_FLAG = "--tutor-model"
TUTOR_ENV = "OPENWEBUI_TUTOR_MODEL"
TUTOR_BOOTSTRAP_DEFAULT = "ox-alpha-free"
SCOUT_BOOTSTRAP_DEFAULT = "ox-alpha-free"
CLERK_BOOTSTRAP_DEFAULT = "ox-alpha-free"

# ---------------------------------------------------------------------------
# Gate Filter source (installed as Function type filter)
# ---------------------------------------------------------------------------
GATE_FILTER_ID = "gate_pipe"
GATE_FILTER_FILES = [
    "Skills/learning-review/openwebui/gate_pipe.py",
    "Skills/learning-review/openwebui/gate_schema.py",
]

SUBAGENT_SYSTEM_PROMPT = """You are an independent verifier for the learning system's delegation gates.

You receive ONLY data via GATE envelopes — never freeform tutor prompts.

GATE:fact_check — verify each numbered claim against the fetched source (and your own knowledge). Be strict on mechanism claims, lenient on phrasing. If the source is silent, check your own knowledge; if unsure, mark UNVERIFIED rather than guessing. Output ONLY valid JSON:
{"verdicts":[{"id":1,"verdict":"PASS|ISSUES|UNVERIFIED","explanation":"...","corrected_claim":"only when ISSUES else null"}, ...]}

GATE:quiz_audit — audit question batches (probe + end-of-lesson quiz) for quality ONLY — you never see learner answers. Check: exactly one correct option; distractors plausible; no answer leaked via wording/stem; Bloom level realistic; mechanical pre-checks (4 options, correct_index in range). Output ONLY valid JSON:
{"verdict":"PASS|ISSUES","issues":[{"id":"q1","severity":"high|medium|low","problem":"...","suggested_fix":"..."}]}

GATE:review — review ONLY the wiki content against source + lesson ref for accuracy/correctness, clarity, completeness. Flag only high/medium. Output ONLY valid JSON:
{"verdict":"PASS|ISSUES","issues":[{"severity":"high|medium|low","location":"...","issue":"..."}]}

Do not invent sources. Do not rewrite content. Verdict PASS only when zero high/medium issues.
"""

PRESETS = [
    {
        "id": "scout",
        "name": "Scout",
        "description": "Exploration preset — gathers context (web search, repo, curriculum) and writes .tmp/context-<chat>-<slug>.json for Tutor.",
        "skillIds": ["llm-wiki", "learning-system"],
        "capabilities": {
            "file_context": True, "file_upload": True, "web_search": True,
            "code_interpreter": True, "terminal": True, "citations": True,
            "status_updates": True, "memory": True, "builtin_tools": True,
            "vision": False, "image_generation": False, "usage": True,
        },
        "system": """You are Scout for the learning system. Your only job is to gather context for the next lesson.

- Read MISSION.md, CURRICULUM.md, RESOURCES.md, relevant Active Concepts rows (bundle, not full reads; do NOT grep 📦 Concept Archive.md — SWE archived, strictly out of scope), and the curriculum source for the requested topic.
- For each new lesson, the curriculum source is TWO layers: (1) Rohit's `phases/<phase>/<lesson>/docs/en.md` (live fetch from https://raw.githubusercontent.com/rohitg00/ai-engineering-from-scratch/main/phases/.../docs/en.md) — Rohit is a source, not the source — and (2) **every URL in that file's `## Further Reading`** (2–4 external refs per lesson, e.g. 3Blue1Brown, Stanford CS229, log-sum-exp blog for P1 L06). Fetch each URL with the ordered per-URL loop below (terminal first — you have curl, yt-dlp, ffmpeg, jq, sha256sum, and Python pypdf in Open Terminal; Web Search fetch is the LAST resort, not the first). Hash each fetched body with sha256sum, compare to any prior digest hash and surface drift as `SCOUT DIGEST: ⚠️ Upstream changed:` if hashes differ. Capture per-lesson `Languages:` header as `lang_recommendation` (Python / TypeScript / Rust; Julia optional, Python-first for Phase 1).
- Per-URL fetch loop (try in order, stop at first success; record failures and CONTINUE — never abort the digest over one URL): (a) direct `curl -L --max-time 30 -o Learning System/.tmp/fetch-<slug>-<n> <url>` for Rohit raw / blogs / PDFs; (b) PDF → extract text with `python3 -c "import pypdf"` (no pdftotext in the sandbox); on 404, try one obvious mirror (e.g. CS229 notes2.pdf → lectures-spring2022/main_notes.pdf) then move on; (c) YouTube → transcript via `yt-dlp --skip-download --write-auto-subs --sub-langs en --convert-subs srt -o "Learning System/.tmp/%(id)s.%(ext)s" <url>` — never page-fetch a video; (d) bot-blocked HTML → `curl -L --max-time 30 https://r.jina.ai/<url>` (no key needed); (e) Web Search snippet as last resort. On total failure write `{url, status:"failed", reason}` into `failed_refs` and continue with the remaining URLs. Partial digest + explicit `failed_refs` always beats stalling. Synthesize ONLY fetched sources — never invent content for failed ones.
- Write a digest to Learning System/.tmp/context-<chat_id>-<slug>.json with {goal, slug, tracks, concept_rows, prereqs, source_refs:[rohit_source, ...external_refs], rohit_hash, external_refs_hashes, failed_refs:[{url, reason}], lang_recommendation, roadmap_sha, fetched_at, created_at} and post a short SCOUT DIGEST: summary in chat (headings + 3–5 bullet synthesis of FETCHED external refs vs Rohit + language + adaptive note if drift + explicit failed_refs list when non-empty). The `prereqs` field is load-bearing for the Tutor's personalization: a list of {concept, keywords:[aliases/variants], why} for every load-bearing dependency of this lesson (e.g. Bayes → {concept:"conditional probability", keywords:["P(A|B)","posterior","joint|marginal"], why:"Bayes is defined via conditional probability"}). Keywords must include notation + plain-language variants (e.g. PMF → ["PMF","probability mass","PMF vs PDF"]) so the Tutor searches rather than guesses.
- Special: Mission 0 Catch-Up (P0 + P1.01–06, 80/20) — synthesize 5 strands (tooling / vectors-matrices / transforms-eigen / calculus-chain-rule / probability) from Phase 0 (12 lessons) + Phase 1 L01–L06 docs/en.md + their Further Reading combined.
- Cache is ignored per decision 2026-09-01 — live fetch each lesson, no phase cache layer.
- Do not teach, quiz, or write wiki pages. Hand off to Tutor. Adaptive rule: re-fetch live before each new lesson; Tutor prefers live combined sources over parametric memory.""",
        "bootstrap_env": "OPENWEBUI_SCOUT_MODEL",
        "bootstrap_default": SCOUT_BOOTSTRAP_DEFAULT,
    },
    {
        "id": "learning-tutor",
        "name": "Learning Tutor",
        "description": "Delight's spaced-repetition learning system: probe → plan → teach with foreground GATE verification.",
        "skillIds": ["learning-system", "learning-teach", "learning-review", "llm-wiki"],
        "capabilities": {
            "file_context": True, "file_upload": True, "web_search": True,
            "code_interpreter": True, "terminal": True, "citations": True,
            "status_updates": True, "memory": True, "builtin_tools": True,
            "vision": False, "image_generation": False, "usage": True,
        },
        "system": r"""You are the Learning Tutor for Delight's spaced-repetition learning system.

The learning system's live state lives in the Git repo at /home/user/learning-system (Open Terminal — Docker Desktop Windows-side, separate from WSL: base URL is http://host.docker.internal:3000 from WSL; workspace repo at /home/user/learning-system in container vs /home/delinux/learning-system in WSL). Read and write files there with the terminal, and commit + push at the end of every session (see Learning System/AGENTS.md).

Assumption: Scout has already gathered context for this lesson into the session and .tmp/context-<chat>-<slug>.json (now includes rohit_source + external_refs + rohit_hash/external_refs_hashes + lang_recommendation + roadmap_sha + fetched_at, adaptively re-fetched; 📦 Concept Archive.md strictly out of scope). Do not gather it yourself; use what is in the session. If you are resuming a lesson (Lessons/ file exists), ground in that file + Sessions/ + CURRICULUM.md.

Order: Mission 0 Catch-Up (P0 + P1.01–06, 80/20, 6–8 MCQs + 2 free-recall, in-progress) is first; after it passes, next is Phase 1 Lesson 07 — Bayes' Theorem (decision 2026-09-01 — jump, not Phase 0 L01). Full 20-phase map is navigational, not contractual; after each phase, decide to go deeper / branch.

Routing (when a trigger fires, load the matching skill with view_skill and follow it — do not improvise):
- "review" → review flow (AIEFS) → view_skill "learning-system" (SWE archived — redirect to AIEFS if requested)
- "ingest <content>" → hand off to Clerk — do not ingest here
- "teach me X" / "learn" / "study" / "lesson" / "continue" / "pause" → teaching flow → view_skill "learning-teach"; Rohit docs/en.md is a source, not the source — teach from combined Scout digest (docs/en.md + Further Reading external refs) + RESOURCES.md; verify batched load-bearing claims with foreground GATE:fact_check envelopes (cite both rohit_source and external_refs) before presenting them, audit question batches with GATE:quiz_audit subagent before showing, respect per-lesson lang_recommendation (Python / TypeScript / Rust; Julia optional), and handoff ingest to Clerk at lesson end AND at every /pause (partial ingest, digest survives — do not write wiki pages yourself)
- wiki work → view_skill "llm-wiki"

Breakpoints are first-class: the student decides lesson length via /pause ("let's stop here"); every lesson is checkpointed so a pause/resume is always clean. A partial Clerk ingest keeps the lesson in-progress and the Scout digest alive.

Language: build language follows the lesson's Rohit `Languages:` header (captured as lang_recommendation); Python for math/ML (Phases 0–12), TypeScript for Tools/Agents/Protocols (Phases 13–17), Rust where listed. Cache is ignored (live fetch each lesson).

Math formatting (OpenWebUI KaTeX — follow exactly so equations render instead of showing as raw code):
- Inline math: use \(...\) only, never single-$ ($...$ does not render).
- Display math: put \[ and \] each on their own line with the equation between, never $$...$$ inline and never fenced ```math/```latex code blocks.
- This applies to learner-facing prose only — GATE delegate_task JSON envelopes stay raw JSON.

All verification gates run as foreground subagent tasks (delegate_task, background:false) with envelope validation via the gate Filter; subagent prompt is fixed in global subagents.system_prompt — send data only.""",
        "bootstrap_env": TUTOR_ENV,
        "bootstrap_default": TUTOR_BOOTSTRAP_DEFAULT,
    },
    {
        "id": "clerk",
        "name": "Clerk",
        "description": "Ingest preset — reads Pending Ingest.json, writes wiki/Active Concepts, and delegates GATE:review.",
        "skillIds": ["learning-system", "llm-wiki", "learning-review"],
        "capabilities": {
            "file_context": True, "file_upload": True, "web_search": True,
            "code_interpreter": True, "terminal": True, "citations": True,
            "status_updates": True, "memory": True, "builtin_tools": True,
            "vision": False, "image_generation": False, "usage": True,
        },
        "system": """You are Clerk for the learning system. You ingest lesson output into the durable store.

- Read Learning System/Core/Pending Ingest.json (written by Tutor at lesson end).
- Write wiki pages and Active Concepts rows, then dispatch a foreground GATE:review envelope via delegate_task on the exact content you wrote.
- Apply reviewer fixes (max 2 cycles), then delete the source .tmp/context-*.json digest and clear Pending Ingest.json, commit + push.""",
        "bootstrap_env": "OPENWEBUI_CLERK_MODEL",
        "bootstrap_default": CLERK_BOOTSTRAP_DEFAULT,
    },
]

PROMPTS = [
    {
        "command": "swe",
        "name": "SWE Review Session",
        "content": "Run a review session on the swe track. Load the learning-system skill (view_skill \"learning-system\"), then follow its Review flow.",
    },
    {
        "command": "review",
        "name": "Review Session",
        "content": "Run a review session. Load the learning-system skill (view_skill \"learning-system\"), then follow its Review flow.",
    },
    {
        "command": "ingest",
        "name": "Ingest Content",
        "content": "Ingest the following content into the learning system:\n{{content | textarea:placeholder=\"Paste the content or a URL to ingest\"}}\n\nSwitch to the Clerk preset and load the learning-system skill (view_skill \"learning-system\"), follow its Ingest flow, then commit and push.",
    },
    {
        "command": "teach",
        "name": "Teach Me",
        "content": "Teach me about: {{topic | text:placeholder=\"Topic to learn\"}}\n\nFirst, switch to the Scout preset to gather context for this topic. Then switch to the Learning Tutor preset, load the learning-teach skill (view_skill \"learning-teach\"), and run the probe → plan → teach loop. The gate Filter enforces foreground GATE envelopes — do not bypass it.",
    },
    {
        "command": "lesson",
        "name": "Next Lesson",
        "content": "Run the next curriculum lesson. Switch to the Scout preset to gather context for the next lesson, then switch to the Learning Tutor preset, load the learning-teach skill (view_skill \"learning-teach\"), and determine the next lesson from Learning System/CURRICULUM.md.",
    },
    {
        "command": "continue",
        "name": "Continue Lesson",
        "content": "Continue the current lesson where we left off. Load the learning-teach skill (view_skill \"learning-teach\"). If the lesson file exists, it is the source of truth — no Scout digest needed.",
    },
    {
        "command": "pause",
        "name": "Pause Lesson",
        "content": "Pause the current lesson where we are. Switch to the Learning Tutor preset, load the learning-teach skill (view_skill \"learning-teach\"), and run the pause protocol: exit ticket for today's checkpoints only, partial lesson file with Status + Resume-from pointer, partial Pending Ingest.json, then hand to the Clerk preset with /ingest to bank today's progress. The gate Filter enforces foreground GATE envelopes — do not bypass it.",
    },
]


class Client:
    def __init__(self, base_url: str, api_key: str):
        self.base = base_url.rstrip("/")
        self.key = api_key

    def _request(self, method: str, path: str, payload=None, expect_error_text: str = ""):
        url = self.base + path
        data = None
        headers = {"Authorization": f"Bearer {self.key}"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
                return resp.status, json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if expect_error_text and expect_error_text in body:
                return e.code, None
            print(f"    ! HTTP {e.code} on {method} {path}: {body[:400]}")
            return e.code, None
        except Exception as e:
            print(f"    ! request failed on {method} {path}: {e}")
            return None, None

    def post(self, path, payload, conflict_marker=""):
        return self._request("POST", path, payload, conflict_marker)

    def get(self, path):
        return self._request("GET", path)
    def put(self, path, payload):
        return self._request("PUT", path, payload)


def parse_skill_md(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    frontmatter = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end + 4:].lstrip("\n")
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip().strip('"').strip("'")
    skill_id = frontmatter.get("name", os.path.splitext(os.path.basename(path))[0])
    name = frontmatter.get("name", skill_id).replace("-", " ").title()
    description = frontmatter.get("description", "")
    return skill_id, name, description, body


def main() -> int:
    ap = argparse.ArgumentParser(description="Install the Learning System into Open WebUI.")
    ap.add_argument("--base-url", default=os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3000"))
    ap.add_argument("--api-key", default=os.environ.get("OPENWEBUI_API_KEY", ""))
    ap.add_argument(TUTOR_FLAG, default=os.environ.get(TUTOR_ENV, TUTOR_BOOTSTRAP_DEFAULT))
    args = ap.parse_args()

    if not args.api_key:
        key_file = os.path.expanduser("~/.openwebui_key")
        if os.path.isfile(key_file):
            args.api_key = open(key_file).read().strip()
    if not args.api_key:
        print("ERROR: OPENWEBUI_API_KEY not set", file=sys.stderr)
        return 2

    c = Client(args.base_url, args.api_key)

    def upsert(path_create: str, path_update: str, payload: dict, conflict_marker: str, label: str) -> None:
        status, resp = c.post(path_create, payload, conflict_marker=conflict_marker)
        if resp is not None:
            print(f"  + created {label}")
            return
        if status == 400:
            status2, _ = c.post(path_update, payload)
            ok = status2 == 200
            print(f"  ~ updated {label}" if ok else f"  ! failed to update {label}")

    print("== Skills ==")
    for rel in SKILLS:
        skill_id, name, desc, content = parse_skill_md(os.path.join(REPO_ROOT, rel))
        payload = {"id": skill_id, "name": name, "description": desc, "content": content, "meta": {"tags": []}, "is_active": True, "access_grants": []}
        upsert("/api/v1/skills/create", f"/api/v1/skills/id/{skill_id}/update", payload, "ID_TAKEN", f"skill {skill_id}")

    print("== Gate Filter (Function) ==")
    # Combine gate_pipe + gate_schema into one Function content (gate_schema imported as sibling, but we inline for single-function install)
    def inline_gate_filter(schema_src: str, pipe_src: str) -> str:
        if "from gate_schema import" not in pipe_src:
            return pipe_src
        start = pipe_src.find("try:\n    from gate_schema import")
        if start == -1:
            return pipe_src
        end_marker = "extract_json_block = lambda t: None"
        end = pipe_src.find(end_marker, start)
        if end == -1:
            return pipe_src
        end = pipe_src.find("\n", end)
        if end != -1:
            end += 1
        return pipe_src[:start] + "# gate_schema inlined above — already defined in schema_src\npass\n" + pipe_src[end:]

    try:
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_schema.py"), "r", encoding="utf-8") as f:
            schema_src = f.read()
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_pipe.py"), "r", encoding="utf-8") as f:
            pipe_src = f.read()
        pipe_src_inlined = inline_gate_filter(schema_src, pipe_src)
        # Sanity check: the inlined content must still compile
        try:
            compile(schema_src + "\n\n" + pipe_src_inlined, "<gate_pipe_inlined>", "exec")
        except SyntaxError as e:
            print(f"  ! inlined gate content failed to compile: {e} — aborting Function install")
            raise
        function_content = schema_src + "\n\n" + pipe_src_inlined
        payload = {
            "id": GATE_FILTER_ID,
            "name": "Gate Pipe",
            "description": "Deterministic delegation gate — blocks Tutor/Clerk output without foreground GATE receipts; Scout digest 7-day TTL.",
            "content": function_content,
            "meta": {"tags": []},
            "is_active": True,
            "access_grants": [],
        }
        upsert("/api/v1/functions/create", f"/api/v1/functions/id/{GATE_FILTER_ID}/update", payload, "ID_TAKEN", f"function {GATE_FILTER_ID}")
        # Ensure Valves priority is set (filter ordering)
        c.post(f"/api/v1/functions/id/{GATE_FILTER_ID}/valves/update", {"priority": 10, "max_retries": 2, "digest_ttl_days": 7})
    except Exception as e:
        print(f"  ! gate filter install failed: {e}")

    print("== Subagent system prompt ==")
    # Best-effort: set global subagents.system_prompt via config API
    try:
        status, _ = c.post("/api/v1/configs/update", {"subagents.system_prompt": SUBAGENT_SYSTEM_PROMPT})
        if status in (200, 201):
            print("  ~ set subagents.system_prompt")
        else:
            print("  ! subagents.system_prompt not set via API — set manually in Settings → Subagents")
    except Exception as e:
        print(f"  ! subagents.system_prompt: {e} — set manually in Settings → Subagents")

    print("== Model presets ==")
    for preset in PRESETS:
        env_val = os.environ.get(preset["bootstrap_env"], preset["bootstrap_default"])
        # Preserve existing base_model_id if already configured (UI is source of truth)
        mstatus, mresp = c.get(f"/api/v1/models/model?id={preset['id']}")
        base = env_val
        if mstatus == 200 and isinstance(mresp, dict):
            current = ((mresp.get("base_model_id") or "").strip() or ((mresp.get("info") or {}).get("base_model_id") or "").strip())
            if current:
                base = current
                print(f"  = preserved {preset['id']} base = {current}")
        # Bind gate filter to Tutor and Clerk (not Scout)
        filter_ids = [GATE_FILTER_ID] if preset["id"] in ("learning-tutor", "clerk") else []
        payload = {
            "id": preset["id"],
            "base_model_id": base,
            "name": preset["name"],
            "params": {"system": preset["system"]},
            "meta": {"description": preset["description"], "capabilities": preset["capabilities"], "skillIds": preset["skillIds"], "knowledge": [], "filterIds": filter_ids},
            "access_grants": [], "is_active": True,
        }
        # Models use 401 for duplicate (not 400) — handle both
        status, resp = c.post("/api/v1/models/create", payload, conflict_marker="MODEL_ID_TAKEN")
        if resp is not None:
            print(f"  + created model {preset['id']} (base: {base})")
        elif status in (400, 401):
            status2, _ = c.post("/api/v1/models/model/update", payload)
            print(f"  ~ updated model {preset['id']} (base preserved: {base})" if status2 == 200 else f"  ! failed to update {preset['id']}")
        else:
            print(f"  ! model {preset['id']} status {status}")

    print("== Prompts ==")
    for p in PROMPTS:
        payload = {"command": p["command"], "name": p["name"], "content": p["content"], "access_grants": []}
        upsert("/api/v1/prompts/create", f"/api/v1/prompts/id/{p['command']}/update", payload, "ID_TAKEN", f"prompt /{p['command']}")

    print("\nDone. Verify: Workspace → Models (Scout/Tutor/Clerk) and Functions → Gate Pipe.")
    print("Gate Filter is bound to Tutor and Clerk only; Scout is exempt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
