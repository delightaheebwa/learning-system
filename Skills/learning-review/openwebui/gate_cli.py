#!/usr/bin/env python3
"""CLI runner for the Learning System review gate.

Calls the independent review model (e.g. Mimo v2.5) in Open WebUI from the
terminal, so the gate is a genuine second model — not the chat model reviewing
its own work.

Usage:
  OPENWEBUI_API_KEY=sk-... python3 gate_cli.py \
      --source "https://..." \
      --concepts "Concept One,Concept Two" \
      --wiki "Knowledge Wiki/wiki/Concept One.md,Knowledge Wiki/wiki/Concept Two.md" \
      [--pass-number 1] [--model "Mimo v2.5"] \
      [--base-url http://host.docker.internal:3000] [--repo-path /path/to/repo]

All options can also come from env vars (OPENWEBUI_API_KEY, OPENWEBUI_BASE_URL,
REVIEW_GATE_MODEL, LEARNING_REPO_PATH). Never pass the key on the command line
if you can avoid it — env var or a 0600 config file is better.

Exit codes: 0 = verdict PASS, 1 = verdict ISSUES, 2 = error / no verdict.
"""

import argparse
import json
import os
import sys

from review_gate import Tools


def main() -> int:
    p = argparse.ArgumentParser(description="Run the Learning System review gate via a second model in Open WebUI.")
    p.add_argument("--source", required=True, help="URL the ingest came from (stable URL).")
    p.add_argument("--concepts", required=True, help="Comma-separated concept names.")
    p.add_argument("--wiki", required=True, help="Comma-separated wiki file paths relative to the repo.")
    p.add_argument("--pass-number", type=int, default=1, help="Cycle number (1 or 2). Filename only.")
    p.add_argument("--model", default=os.environ.get("REVIEW_GATE_MODEL", ""), help="Review model id in Open WebUI (e.g. 'Mimo v2.5').")
    p.add_argument("--base-url", default=os.environ.get("OPENWEBUI_BASE_URL", "http://host.docker.internal:3000"), help="Open WebUI base URL.")
    p.add_argument("--repo-path", default=os.environ.get("LEARNING_REPO_PATH", ""), help="Absolute path to the repo on this machine (for wiki path validation).")
    args = p.parse_args()

    # API key: --api-key is intentionally NOT offered as a flag.
    # Lookup order: env var OPENWEBUI_API_KEY, then ~/.config/learning-system/openwebui_key (0600).
    api_key = os.environ.get("OPENWEBUI_API_KEY", "")
    if not api_key:
        key_file = os.path.expanduser("~/.config/learning-system/openwebui_key")
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                api_key = f.read().strip()
        except Exception:
            api_key = ""
    if not api_key:
        print(json.dumps({"error": "no API key — set OPENWEBUI_API_KEY or write ~/.config/learning-system/openwebui_key (0600)"}, indent=2))
        return 2

    os.environ["OPENWEBUI_BASE_URL"] = args.base_url
    os.environ["OPENWEBUI_API_KEY"] = api_key
    os.environ["REVIEW_GATE_MODEL"] = args.model
    if args.repo_path:
        os.environ["LEARNING_REPO_PATH"] = args.repo_path

    out = Tools().review_gate(
        source=args.source,
        concepts=args.concepts,
        wiki_paths=args.wiki,
        pass_number=args.pass_number,
    )
    print(out)

    try:
        d = json.loads(out)
        v = d.get("verdict", {}).get("verdict")
        if v == "PASS":
            return 0
        if v == "ISSUES":
            return 1
        return 2
    except Exception:
        return 2


if __name__ == "__main__":
    sys.exit(main())
