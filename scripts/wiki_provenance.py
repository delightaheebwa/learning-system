#!/usr/bin/env python3
"""wiki_provenance — provenance lint/stamp for Knowledge Wiki pages (P0.6).

Every page in Knowledge Wiki/wiki/*.md must carry a provenance marker on its
first lines:

    <!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->

Trust order (see Knowledge Wiki/AGENTS.md and AGENTS.md): a raw source outranks
a verified claim, which outranks labelled AI synthesis, which outranks learner
notes. An **unstamped page is treated as `unverified`** — the wiki is AI
synthesis derived from sources, not a source itself.

Usage (run from the repo root):
  python3 scripts/wiki_provenance.py            report status counts + offenders
  python3 scripts/wiki_provenance.py --check    exit 1 if any page lacks a marker
  python3 scripts/wiki_provenance.py --json     machine-readable report
  python3 scripts/wiki_provenance.py --stamp [--status unverified] [--date YYYY-MM-DD]
                                                add a default marker to unstamped
                                                pages (idempotent; never rewrites
                                                an existing marker)
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = REPO_ROOT / "Knowledge Wiki" / "wiki"
MARKER_RE = re.compile(r"<!--\s*provenance:\s*(.*?)-->", re.IGNORECASE | re.DOTALL)
STATUS_RE = re.compile(r"status\s*=\s*([a-z][a-z-]*)", re.IGNORECASE)
VALID_STATUS = {"verified", "synthesis", "learner-note", "unverified"}


def _pages() -> list[Path]:
    if not WIKI_DIR.is_dir():
        return []
    return sorted(p for p in WIKI_DIR.glob("*.md") if p.is_file())


def read_status(text: str) -> str | None:
    m = MARKER_RE.search(text)
    if not m:
        return None
    s = STATUS_RE.search(m.group(1))
    if not s:
        return None
    status = s.group(1).lower()
    return status if status in VALID_STATUS else "unverified"


def marker(status: str, source: str, verified_by: str, date: str) -> str:
    return (
        f"<!-- provenance: status={status} | source={source} | "
        f"verified-by={verified_by} | date={date} -->\n\n"
    )


def scan() -> dict:
    counts: dict[str, int] = {s: 0 for s in VALID_STATUS}
    missing: list[str] = []
    invalid: list[str] = []
    for p in _pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        status = read_status(text)
        if status is None:
            missing.append(p.name)
        else:
            counts[status] = counts.get(status, 0) + 1
            if status not in VALID_STATUS:
                invalid.append(p.name)
    return {
        "total": len(_pages()),
        "counts": counts,
        "missing": missing,
        "invalid": invalid,
    }


def do_report(report: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    c = report["counts"]
    print(f"wiki pages: {report['total']}")
    for s in ("verified", "synthesis", "learner-note", "unverified"):
        print(f"  {s:12} {c.get(s, 0)}")
    print(f"  missing      {len(report['missing'])}")
    if report["missing"]:
        print("unstamped (treated as unverified):")
        for name in report["missing"][:30]:
            print(f"  - {name}")
        if len(report["missing"]) > 30:
            print(f"  … and {len(report['missing']) - 30} more")


def do_stamp(status: str, date: str) -> int:
    if status not in VALID_STATUS:
        print(f"bad --status {status!r}; want one of {sorted(VALID_STATUS)}")
        return 2
    stamped = 0
    for p in _pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        if MARKER_RE.search(text):
            continue
        line = marker(status, source="legacy", verified_by="—", date=date)
        p.write_text(line + text, encoding="utf-8")
        stamped += 1
    print(f"stamped {stamped} page(s) status={status}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    check = "--check" in args
    if "--stamp" in args:
        status = "unverified"
        if "--status" in args:
            status = args[args.index("--status") + 1]
        date = args[args.index("--date") + 1] if "--date" in args else datetime.date.today().isoformat()
        return do_stamp(status, date)
    report = scan()
    do_report(report, as_json)
    if check and (report["missing"] or report["invalid"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
