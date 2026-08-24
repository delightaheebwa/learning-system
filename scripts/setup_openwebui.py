#!/usr/bin/env python3
"""
setup_openwebui — one-shot installer for the Learning System in Open WebUI.

Creates (or updates) everything the system needs, using the Open WebUI REST API:

  - 4 Skills        from Skills/*/SKILL.md
  - 1 Model preset  "Learning Tutor"
  - 6 Prompts       /swe /review /ingest /teach /lesson /continue

All verification gates run as background subagent tasks (`delegate_task`) on
Open WebUI's subagent default model — no Tools are installed or bound. The
legacy review_gate/fact_check/quiz_gate Tools are dormant; their .py files stay
in Skills/learning-review/openwebui/ as fallbacks only (see OPENWEBUI.md).

Models are configured AFTER install in the Open WebUI UI (one field per task —
see OPENWEBUI.md). The values below are FIRST-INSTALL BOOTSTRAP defaults only:
the installer reads the Learning Tutor's current base model first and PRESERVES
any non-empty value already set in the UI. Re-running this script (e.g. after
editing a skill) therefore never resets your models — change models exclusively
in the UI.

Usage:
  OPENWEBUI_API_KEY=sk-... python3 scripts/setup_openwebui.py [--base-url http://localhost:3000]

Requirements: Python 3 stdlib only. Run on the host (or anywhere the Open WebUI
API is reachable). Idempotent: existing items are updated, not duplicated.

Values:
  - (Legacy note: the dormant review_gate/fact_check/quiz_gate Tools are NOT
    installed by this script. If you ever need them again, their .py files are
    in Skills/learning-review/openwebui/.)
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
TUTOR_BOOTSTRAP_DEFAULT = "deepseek-v4-pro"

MODEL = {
    "id": "learning-tutor",
    "name": "Learning Tutor",
    "description": "Delight's spaced-repetition learning system: swe/review, ingest, teach/lesson, and the Karpathy-style wiki.",
    "skillIds": ["learning-system", "learning-teach", "learning-review", "llm-wiki"],
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
- "ingest <content>" → ingest flow → view_skill "learning-system", then run the review-gate subagent task (delegate_task) on the wiki content you wrote, then commit + push
- "teach me X" / "learn" / "study" / "lesson" / "continue" → teaching flow → view_skill "learning-teach"; verify batched load-bearing claims with a fact-check subagent task before presenting them, audit every question batch (probe and end-of-lesson quiz) with a quiz-audit subagent task before showing it to the learner, and run the review-gate subagent task on any wiki content or Active Concepts rows the lesson produced before finalizing
- wiki work (Ingest/queries/lint) → view_skill "llm-wiki"

All verification gates run as background subagent tasks (`delegate_task`) on Open WebUI's subagent default model; you are running on the Learning Tutor preset's base model. To change any model, see the model-per-task table in OPENWEBUI.md."""

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
        "content": "Ingest the following content into the learning system:\n{{content | textarea:placeholder=\"Paste the content or a URL to ingest\"}}\n\nLoad the learning-system skill (view_skill \"learning-system\"), follow its Ingest flow, read the wiki pages you wrote via the terminal, run the review-gate subagent task (delegate_task), then commit and push.",
    },
    {
        "command": "teach",
        "name": "Teach Me",
        "content": "Teach me about: {{topic | text:placeholder=\"Topic to learn\"}}\n\nLoad the learning-teach skill (view_skill \"learning-teach\"), then run the probe → plan → teach loop. Verify batched load-bearing claims with a fact-check subagent task before presenting them, and audit every question batch with a quiz-audit subagent task before showing it.",
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

    def get(self, path):
        return self._request("GET", path)


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
    ap.add_argument("--api-key", default=os.environ.get("OPENWEBUI_API_KEY", ""))
    ap.add_argument(TUTOR_FLAG, default=os.environ.get(TUTOR_ENV, TUTOR_BOOTSTRAP_DEFAULT),
                    help="first-install bootstrap tutor base model (existing UI value is preserved)")
    args = ap.parse_args()

    if not args.api_key:
        key_file = os.path.expanduser("~/.openwebui_key")
        if os.path.isfile(key_file):
            args.api_key = open(key_file).read().strip()
    if not args.api_key:
        print("ERROR: OPENWEBUI_API_KEY not set", file=sys.stderr)
        return 2

    c = Client(args.base_url, args.api_key)

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

    print("== Model preset ==")
    # Preserve an already-configured tutor base model (UI is the source of truth).
    tutor_base = args.tutor_model
    mstatus, mresp = c.get(f"/api/v1/models/model?id={MODEL['id']}")
    if mstatus == 200 and isinstance(mresp, dict):
        current = ((mresp.get("base_model_id") or "").strip()
                   or ((mresp.get("info") or {}).get("base_model_id") or "").strip())
        if current:
            tutor_base = current
            print(f"  = preserved {MODEL['id']} base model = {current} (set in UI)")
    payload = {
        "id": MODEL["id"],
        "base_model_id": tutor_base,
        "name": MODEL["name"],
        "params": {"system": SYSTEM_PROMPT},
        "meta": {
            "description": MODEL["description"],
            "capabilities": MODEL["capabilities"],
            "skillIds": MODEL["skillIds"],
            "knowledge": [],
        },
        "access_grants": [],
        "is_active": True,
    }
    status, resp = c.post("/api/v1/models/create", payload, conflict_marker="MODEL_ID_TAKEN")
    if resp is not None:
        print(f"  + created model {MODEL['id']} (base: {tutor_base})")
    elif status == 400:
        status2, _ = c.post("/api/v1/models/model/update", payload)
        print(f"  ~ updated model {MODEL['id']} (base preserved: {tutor_base})" if status2 == 200 else f"  ! failed to update model {MODEL['id']}")

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
    print("Models are configured in the UI only (one field per task) — see OPENWEBUI.md.")
    print("Re-running this installer preserves your UI-chosen models.")
    return 0


if __name__ == "__main__":
    sys.exit(main())