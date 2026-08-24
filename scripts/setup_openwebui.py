#!/usr/bin/env python3
"""
setup_openwebui — one-shot installer for the Learning System in Open WebUI.

Creates (or updates) everything the system needs, using the Open WebUI REST API:

  - 4 Skills        from Skills/*/SKILL.md
  - 3 Tools         review_gate + fact_check + quiz_gate
  - 1 Model preset  "Learning Tutor"
  - 6 Prompts       /swe /review /ingest /teach /lesson /continue

Models are configured AFTER install in the Open WebUI UI (one field per task —
see OPENWEBUI.md). The values below are BOOTSTRAP DEFAULTS applied at install
time only; rerunning this script re-applies them and will overwrite any UI
hot-swaps. Use the --*-model flags or env vars to set different bootstrap
values without editing this file.

Usage:
  OPENWEBUI_API_KEY=sk-... python3 scripts/setup_openwebui.py [--base-url http://localhost:3000]

Requirements: Python 3 stdlib only. Run on the host (or anywhere the Open WebUI
API is reachable). Idempotent: existing items are updated, not duplicated.

Values:
  - Tool valves are set to call the API from inside the Open WebUI container
    (http://localhost:8080). If your deployment differs, pass --tool-base-url.
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
TOOLS = [
    {
        "id": "review_gate",
        "name": "review_gate",
        "file": "Skills/learning-review/openwebui/review_gate.py",
        "valve_key": "review_model",
        "flag": "--review-model",
        "env": "OPENWEBUI_REVIEW_MODEL",
        "bootstrap_default": "ox-alpha-free",
    },
    {
        "id": "fact_check",
        "name": "fact_check",
        "file": "Skills/learning-review/openwebui/fact_check.py",
        "valve_key": "fact_check_model",
        "flag": "--fact-check-model",
        "env": "OPENWEBUI_FACT_CHECK_MODEL",
        "bootstrap_default": "ox-alpha-free",
    },
    {
        "id": "quiz_gate",
        "name": "quiz_gate",
        "file": "Skills/learning-review/openwebui/quiz_gate.py",
        "valve_key": "quiz_model",
        "flag": "--quiz-model",
        "env": "OPENWEBUI_QUIZ_MODEL",
        "bootstrap_default": "ox-alpha-free",
    },
]

TUTOR_FLAG = "--tutor-model"
TUTOR_ENV = "OPENWEBUI_TUTOR_MODEL"
TUTOR_BOOTSTRAP_DEFAULT = "deepseek-v4-pro"

MODEL = {
    "id": "learning-tutor",
    "name": "Learning Tutor",
    "description": "Delight's spaced-repetition learning system: swe/review, ingest, teach/lesson, and the Karpathy-style wiki.",
    "skillIds": ["learning-system", "learning-teach", "learning-review", "llm-wiki"],
    "toolIds": ["review_gate", "fact_check", "quiz_gate"],
    "capabilities": {
        "file_context": True,
        "file_upload": True,
        "web_search": True,
        "code_interpreter": True,
        "terminal": True,
        "citations": True,
        "status_updates": True,
        "memory": True,
        "builtin_tools": True,
        "vision": False,
        "image_generation": False,
        "usage": True,
    },
}

SYSTEM_PROMPT = """You are the Learning Tutor for Delight's spaced-repetition learning system.

The learning system's live state lives in the Git repo at /home/user/learning-system (Open Terminal). Read and write files there with the terminal, and commit + push at the end of every session (see Learning System/AGENTS.md).

Routing (when a trigger fires, load the matching skill with view_skill and follow it — do not improvise the workflow):
- "swe" / "review" → review flow → view_skill "learning-system"
- "ingest <content>" → ingest flow → view_skill "learning-system", then run the review_gate tool on the wiki content you wrote, then commit + push
- "teach me X" / "learn" / "study" / "lesson" / "continue" → teaching flow → view_skill "learning-teach"; verify load-bearing claims with the fact_check tool before presenting them, audit every question batch (probe and end-of-lesson quiz) with the quiz_gate tool before showing it to the learner, and run the review_gate tool on any wiki content or Active Concepts rows the lesson produced before finalizing
- wiki work (Ingest/queries/lint) → view_skill "llm-wiki"

Each gate/fact-check model is whatever is set on that tool's Valves; you are running on the Learning Tutor preset's base model. To change any model, see the model-per-task table in OPENWEBUI.md."""

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
        "content": "Ingest the following content into the learning system:\n{{content | textarea:placeholder=\"Paste the content or a URL to ingest\"}}\n\nLoad the learning-system skill (view_skill \"learning-system\"), follow its Ingest flow, read the wiki pages you wrote via the terminal, run the review_gate tool, then commit and push.",
    },
    {
        "command": "teach",
        "name": "Teach Me",
        "content": "Teach me about: {{topic | text:placeholder=\"Topic to learn\"}}\n\nLoad the learning-teach skill (view_skill \"learning-teach\"), then run the probe → plan → teach loop. Verify load-bearing claims with the fact_check tool before presenting them, and audit every question batch with the quiz_gate tool before showing it.",
    },
    {
        "command": "lesson",
        "name": "Next Lesson",
        "content": "Run the next curriculum lesson. Load the learning-teach skill (view_skill \"learning-teach\"), determine the next lesson from Learning System/CURRICULUM.md, and teach it.",
    },
    {
        "command": "continue",
        "name": "Continue Lesson",
        "content": "Continue the current lesson where we left off. Load the learning-teach skill (view_skill \"learning-teach\").",
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
            print(f"    ! HTTP {e.code} on {method} {path}: {body[:300]}")
            return e.code, None
        except Exception as e:
            print(f"    ! request failed on {method} {path}: {e}")
            return None, None

    def post(self, path, payload, conflict_marker=""):
        return self._request("POST", path, payload, conflict_marker)


def parse_skill_md(path):
    """Return (id, name, description, content) from a SKILL.md file."""
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
    ap.add_argument("--tool-base-url", default=os.environ.get("OPENWEBUI_TOOL_BASE_URL", "http://localhost:8080"))
    ap.add_argument("--api-key", default=os.environ.get("OPENWEBUI_API_KEY", ""))
    ap.add_argument(TUTOR_FLAG, default=os.environ.get(TUTOR_ENV, TUTOR_BOOTSTRAP_DEFAULT),
                    help="bootstrap tutor base model (after install, change in UI: Learning Tutor preset)")
    for t in TOOLS:
        ap.add_argument(t["flag"], default=os.environ.get(t["env"], t["bootstrap_default"]),
                        help=f"bootstrap model for {t['id']} (after install, change in UI: tool Valves)")
    args = ap.parse_args()

    if not args.api_key:
        key_file = os.path.expanduser("~/.openwebui_key")
        if os.path.isfile(key_file):
            args.api_key = open(key_file).read().strip()
    if not args.api_key:
        print("ERROR: OPENWEBUI_API_KEY not set", file=sys.stderr)
        return 2

    c = Client(args.base_url, args.api_key)
    api_key = args.api_key
    tool_valves_common = {"openwebui_base_url": args.tool_base_url, "openwebui_api_key": api_key}

    print("== Skills ==")
    for rel in SKILLS:
        skill_id, name, desc, content = parse_skill_md(os.path.join(REPO_ROOT, rel))
        payload = {
            "id": skill_id,
            "name": name,
            "description": desc,
            "content": content,
            "meta": {"tags": []},
            "is_active": True,
            "access_grants": [],
        }
        status, resp = c.post("/api/v1/skills/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created skill {skill_id}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/skills/id/{skill_id}/update", payload)
            print(f"  ~ updated skill {skill_id}" if status2 == 200 else f"  ! failed to update {skill_id}")

    print("== Tools ==")
    tool_model_by_id = {t["id"]: getattr(args, t["flag"].lstrip("-").replace("-", "_")) for t in TOOLS}
    for t in TOOLS:
        with open(os.path.join(REPO_ROOT, t["file"]), "r", encoding="utf-8") as f:
            content = f.read()
        payload = {"id": t["id"], "name": t["name"], "content": content, "meta": {}, "access_grants": []}
        status, resp = c.post("/api/v1/tools/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created tool {t['id']}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/tools/id/{t['id']}/update", payload)
            print(f"  ~ updated tool {t['id']}" if status2 == 200 else f"  ! failed to update {t['id']}")
        # valves (bootstrap model values — after install, change models in the UI)
        valves = {**tool_valves_common, t["valve_key"]: tool_model_by_id[t["id"]]}
        vstatus, vresp = c.post(f"/api/v1/tools/id/{t['id']}/valves/update", valves)
        if vresp is not None:
            print(f"  + set valves on {t['id']} ({t['valve_key']}={valves[t['valve_key']]})")

    print("== Model preset ==")
    payload = {
        "id": MODEL["id"],
        "base_model_id": args.tutor_model,
        "name": MODEL["name"],
        "params": {"system": SYSTEM_PROMPT},
        "meta": {
            "description": MODEL["description"],
            "capabilities": MODEL["capabilities"],
            "skillIds": MODEL["skillIds"],
            "toolIds": MODEL["toolIds"],
            "knowledge": [],
        },
        "access_grants": [],
        "is_active": True,
    }
    status, resp = c.post("/api/v1/models/create", payload, conflict_marker="MODEL_ID_TAKEN")
    if resp is not None:
        print(f"  + created model {MODEL['id']}")
    elif status == 400:
        status2, _ = c.post("/api/v1/models/model/update", payload)
        print(f"  ~ updated model {MODEL['id']}" if status2 == 200 else f"  ! failed to update model {MODEL['id']}")

    print("== Prompts ==")
    for p in PROMPTS:
        payload = {"command": p["command"], "name": p["name"], "content": p["content"], "access_grants": []}
        status, resp = c.post("/api/v1/prompts/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created prompt /{p['command']}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/prompts/id/{p['command']}/update", payload)
            print(f"  ~ updated prompt /{p['command']}" if status2 == 200 else f"  ! failed to update /{p['command']}")

    print("\nDone. Verify in Open WebUI → Workspace → Models → Learning Tutor.")
    print("Models are now configured in the UI (one field per task) — see OPENWEBUI.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())