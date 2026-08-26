#!/usr/bin/env python3
"""
setup_openwebui — one-shot installer for the Learning System in Open WebUI.

Creates (or updates) everything the system needs, using the Open WebUI REST API:

  - 4 Skills        from Skills/*/SKILL.md
  - 3 Model presets Scout / Learning Tutor / Clerk
  - 1 Gate Filter   (Function) gate_pipe — deterministic delegation gate
  - 6 Prompts       /swe /review /ingest /teach /lesson /continue
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

- Read MISSION.md, CURRICULUM.md, RESOURCES.md, relevant Active Concepts rows (bundle, not full reads), and the curriculum source for the requested topic.
- Write a digest to Learning System/.tmp/context-<chat_id>-<slug>.json with {goal, slug, tracks, concept_rows, source_refs, created_at}
  and post a short SCOUT DIGEST: summary in chat (headings + key refs).
- Do not teach, quiz, or write wiki pages. Hand off to Tutor.""",
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
        "system": """You are the Learning Tutor for Delight's spaced-repetition learning system.

The learning system's live state lives in the Git repo at /home/user/learning-system (Open Terminal). Read and write files there with the terminal, and commit + push at the end of every session (see Learning System/AGENTS.md).

Assumption: Scout has already gathered context for this lesson into the session and .tmp/context-<chat>-<slug>.json. Do not gather it yourself; use what is in the session. If you are resuming a lesson (Lessons/ file exists), ground in that file + Sessions/ + CURRICULUM.md.

Routing (when a trigger fires, load the matching skill with view_skill and follow it — do not improvise):
- "swe" / "review" → review flow → view_skill "learning-system"
- "ingest <content>" → hand off to Clerk — do not ingest here
- "teach me X" / "learn" / "study" / "lesson" / "continue" → teaching flow → view_skill "learning-teach"; verify batched load-bearing claims with foreground GATE:fact_check envelopes before presenting them, audit question batches with GATE:quiz_audit subagent before showing, and handoff ingest to Clerk at lesson end (do not write wiki pages yourself)
- wiki work → view_skill "llm-wiki"

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

    print("== Skills ==")
    for rel in SKILLS:
        skill_id, name, desc, content = parse_skill_md(os.path.join(REPO_ROOT, rel))
        payload = {"id": skill_id, "name": name, "description": desc, "content": content, "meta": {"tags": []}, "is_active": True, "access_grants": []}
        status, resp = c.post("/api/v1/skills/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created skill {skill_id}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/skills/id/{skill_id}/update", payload)
            print(f"  ~ updated skill {skill_id}" if status2 == 200 else f"  ! failed to update {skill_id}")

    print("== Gate Filter (Function) ==")
    # Combine gate_pipe + gate_schema into one Function content (gate_schema imported as sibling, but we inline for single-function install)
    try:
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_schema.py"), "r", encoding="utf-8") as f:
            schema_src = f.read()
        with open(os.path.join(REPO_ROOT, "Skills/learning-review/openwebui/gate_pipe.py"), "r", encoding="utf-8") as f:
            pipe_src = f.read()
        # Remove the try/except import block that pulls gate_schema when inlined — schema_src already defines those symbols
        # The block is multi-line; find it by markers rather than fragile regex
        if "from gate_schema import" in pipe_src:
            start = pipe_src.find("try:\n    from gate_schema import")
            if start != -1:
                end_marker = "extract_json_block = lambda t: None"
                end = pipe_src.find(end_marker, start)
                if end != -1:
                    end = pipe_src.find("\n", end)
                    if end != -1:
                        end += 1
                    pipe_src_inlined = pipe_src[:start] + "# gate_schema inlined above — already defined in schema_src\npass\n" + pipe_src[end:]
                else:
                    pipe_src_inlined = pipe_src
            else:
                pipe_src_inlined = pipe_src
        else:
            pipe_src_inlined = pipe_src
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
        status, resp = c.post("/api/v1/functions/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created function {GATE_FILTER_ID}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/functions/id/{GATE_FILTER_ID}/update", payload)
            print(f"  ~ updated function {GATE_FILTER_ID}" if status2 == 200 else f"  ! failed to update {GATE_FILTER_ID}")
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
        status, resp = c.post("/api/v1/models/create", payload, conflict_marker="MODEL_ID_TAKEN")
        if resp is not None:
            print(f"  + created model {preset['id']} (base: {base})")
        elif status == 400:
            status2, _ = c.post("/api/v1/models/model/update", payload)
            print(f"  ~ updated model {preset['id']} (base preserved: {base})" if status2 == 200 else f"  ! failed to update {preset['id']}")
        else:
            print(f"  ! model {preset['id']} status {status}")

    print("== Prompts ==")
    for p in PROMPTS:
        payload = {"command": p["command"], "name": p["name"], "content": p["content"], "access_grants": []}
        status, resp = c.post("/api/v1/prompts/create", payload, conflict_marker="ID_TAKEN")
        if resp is not None:
            print(f"  + created prompt /{p['command']}")
        elif status == 400:
            status2, _ = c.post(f"/api/v1/prompts/id/{p['command']}/update", payload)
            print(f"  ~ updated prompt /{p['command']}" if status2 == 200 else f"  ! failed to update /{p['command']}")

    print("\nDone. Verify: Workspace → Models (Scout/Tutor/Clerk) and Functions → Gate Pipe.")
    print("Gate Filter is bound to Tutor and Clerk only; Scout is exempt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
