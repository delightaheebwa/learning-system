#!/usr/bin/env python3
"""Batch file ops for the learning-system workspace (open-terminal sidecar).

Purpose: collapse many sequential read/write tool calls into ONE command so
agent sessions stay far below the model's cumulative context limit.

Usage:
  ops.py state TRACK              Standard session-start bundle for TRACK (aie|swe).
                                  One call replaces: Learning Profile read, Active
                                  Concepts track slice, Attempts.json, Mistakes.md,
                                  log tail, index head.
  ops.py bundle SPEC [SPEC...]    Read many targets in one call. SPEC syntax:
                                    PATH            whole file
                                    PATH:N-M        lines N..M (1-based, inclusive)
                                    PATH:-N         last N lines
                                    PATH@REGEX      lines matching REGEX (ignore-case)
   ops.py apply < SPEC.json        Apply a batch of writes from JSON on stdin:
                                     {"writes":   [{"path": "...", "content": "..."}],
                                      "appends":  [{"path": "...", "content": "..."}],
                                      "replaces": [{"path": "...", "find": "...",
                                                    "replace_with": "..."}]}
                                   Prints a per-op summary. Use with a quoted heredoc.
  ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type memory|concept|procedure|design]
                                  Record one answer in Attempts.json (interval_index
                                  +1 pass / +2 on 2 consecutive passes / -1 fail,
                                  next_review from type schedule). Prints mastery +
                                  next_review for the skill to copy via apply.
  ops.py mastery [TRACK]           Advisory recency-weighted mastery report
                                   (0.00-1.00 + Feynman status, not blocking).

All paths resolve under the workspace root (/home/user/learning-system). Escapes are rejected.
"""

import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def _detect_root() -> Path:
    """Resolve the learning-system workspace root.

    The real checkout lives at /home/delinux/learning-system locally but at
    /home/user/learning-system inside the Open WebUI Open Terminal container, so
    hardcoding one path breaks the other. Auto-detect by looking for the
    distinctive 'Learning System/Core' substructure; honor an env override.
    """
    candidates = [
        os.environ.get("LEARNING_SYSTEM_ROOT", ""),
        "/home/delinux/learning-system",
        "/home/user/learning-system",
        os.path.expanduser("~/learning-system"),
    ]
    for c in candidates:
        c = (c or "").strip()
        if c and os.path.isdir(os.path.join(c, "Learning System", "Core")):
            return Path(c).resolve()
    # Degenerate fallback: no checkout with the expected substructure was found
    # (e.g. a misconfigured environment). Best-effort the canonical container path
    # rather than crashing; callers will then see MISSING reads, not a stack trace.
    return Path("/home/user/learning-system").resolve()


ROOT = _detect_root()
MAX_LINE = 4000

DEFAULT_INTERVALS = {
    "memory": [0, 1, 3, 7, 14, 30, 60],
    "concept": [3, 7, 14, 30],
    "procedure": [3, 7, 14],
    "design": [14, 28],
}
ATTEMPTS_PATH = "Learning System/Core/Attempts.json"
MISTAKES_PATH = "Learning System/Core/🧯 Mistakes.md"
MASTERY_WEIGHTS = [0.4, 0.25, 0.15, 0.1, 0.1]


def _resolve(p: str) -> Path:
    path = (ROOT / p).resolve() if not p.startswith("/") else Path(p).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ValueError(f"path escapes workspace: {p}")
    return path


def _read_lines(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.splitlines(), text


def _section_slice(lines, pattern):
    """Return the slice from a heading matching `pattern` up to the next heading
    of equal-or-higher level (so a track section captures its table body, not
    just the heading line). Returns (text, error)."""
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return None, f"BAD REGEX: {e}"
    headings = [i for i, l in enumerate(lines) if re.match(r"^#{1,6}\s", l)]
    start = None
    for i in headings:
        if rx.search(lines[i]):
            start = i
            break
    if start is None:
        return None, "(no matching section)"
    level = (len(lines[start]) - len(lines[start].lstrip("#"))) or 1
    end = len(lines)
    for j in headings:
        if j > start and (len(lines[j]) - len(lines[j].lstrip("#"))) <= level:
            end = j
            break
    return "\n".join(lines[start:end]), None


def do_state(track: str) -> None:
    track = track.lower().strip()
    specs = [
        ("Learning System/Core/💡 Learning Profile.md", ""),
        # Section selector (#heading) pulls the whole track block (header + table
        # rows) — the old `^## {track}\b|^### ` grep matched only heading lines.
        (f"Learning System/Core/📚 Active Concepts.md#^## {track}\\b", ""),
        (ATTEMPTS_PATH, ""),
        (MISTAKES_PATH, ""),
        ("Knowledge Wiki/log.md:-25", ""),
        ("Knowledge Wiki/index.md:1-40", ""),
    ]
    for spec, _ in specs:
        do_bundle(spec)


def do_bundle(*specs: str) -> None:
    for spec in specs:
        spec = spec.strip()
        path_part, note, selector = spec, "whole file", None

        if "#" in spec:
            path_part, pattern = spec.split("#", 1)
            note, selector = f"section /{pattern}/i", ("section", pattern)
        elif "@" in spec:
            path_part, pattern = spec.rsplit("@", 1)
            note, selector = f"grep /{pattern}/i", ("grep", pattern)
        else:
            m = re.search(r":(\d+)?-(\d+)?$", spec)
            if m:
                a, b = m.group(1), m.group(2)
                path_part = spec[: m.start()]
                if a is None:  # :-N -> last N lines
                    note, selector = f"last {b} lines", ("tail", int(b))
                else:  # :N-M or :N-
                    lo = int(a)
                    hi = int(b) if b else None
                    note = f"lines {lo}-{hi or 'end'}"
                    selector = ("range", lo, hi)

        path = _resolve(path_part)
        print(f"===== FILE: {path_part} [{note}] =====")
        if not path.is_file():
            print("MISSING")
            continue
        lines, text = _read_lines(path)
        total = len(lines)

        if selector is None:
            out = text
        elif selector[0] == "tail":
            out = "\n".join(lines[-selector[1]:])
        elif selector[0] == "range":
            lo, hi = selector[1], selector[2] or total
            lo = max(1, lo)
            out = "\n".join(lines[lo - 1: hi])
        elif selector[0] == "section":
            out, err = _section_slice(lines, selector[1])
            if err:
                print(err)
                continue
        else:  # grep
            try:
                rx = re.compile(selector[1], re.IGNORECASE)
            except re.error as e:
                print(f"BAD REGEX: {e}")
                continue
            hits = [(i + 1, ln) for i, ln in enumerate(lines) if rx.search(ln)]
            out = "\n".join(f"{i}: {ln[:MAX_LINE]}" for i, ln in hits) if hits else "(no matches)"
            print(f"({len(hits)} matching lines)")
            print(out)
            continue

        print(out if out else "(empty)")


def _load_attempts() -> tuple:
    p = _resolve(ATTEMPTS_PATH)
    if not p.is_file():
        return {"concepts": {}, "meta": {"version": 1, "intervals": DEFAULT_INTERVALS}}, p
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("concepts", {})
    meta = data.setdefault("meta", {})
    meta.setdefault("intervals", DEFAULT_INTERVALS)
    return data, p


def _intervals_for(data: dict, ctype: str):
    sched = (data.get("meta") or {}).get("intervals") or DEFAULT_INTERVALS
    return sched.get(ctype, sched.get("concept", [3, 7, 14, 30]))


def compute_mastery(attempts: list) -> float:
    """Recency-weighted mastery 0-1 with confidence caps ({1:0.5, 2:0.8})."""
    if not attempts:
        return 0.0
    recent = attempts[-5:][::-1]  # most recent first
    weights = MASTERY_WEIGHTS[: len(recent)]
    total = sum(weights)
    score = sum(w * (1.0 if a.get("is_correct") else 0.0) for w, a in zip(weights, recent)) / total
    n = len(attempts)
    if n == 1:
        score = min(score, 0.5)
    elif n == 2:
        score = min(score, 0.8)
    return round(score, 2)


def do_attempt(concept: str, result: str, feynman: str = None, date: str = None,
               qtype: str = None, ctype: str = None) -> None:
    result = (result or "").lower().strip()
    if result not in ("pass", "fail"):
        print(f"ATTEMPT FAILED: result must be pass|fail, got {result!r}")
        sys.exit(2)
    is_correct = result == "pass"
    day = date or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        print(f"ATTEMPT FAILED: bad --date {day!r}, want YYYY-MM-DD")
        sys.exit(2)
    data, path = _load_attempts()
    entry = data["concepts"].get(concept)
    if entry is None:
        entry = {
            "type": (ctype or "concept").lower().strip(),
            "attempts": [],
            "interval_index": 0,
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "last_reviewed": day,
            "next_review": day,
            "feynman": None,
        }
        data["concepts"][concept] = entry
    if is_correct:
        entry["consecutive_correct"] = int(entry.get("consecutive_correct", 0)) + 1
        entry["consecutive_wrong"] = 0
        step = 2 if entry["consecutive_correct"] >= 2 else 1
        entry["interval_index"] = int(entry.get("interval_index", 0)) + step
    else:
        entry["consecutive_wrong"] = int(entry.get("consecutive_wrong", 0)) + 1
        entry["consecutive_correct"] = 0
        entry["interval_index"] = int(entry.get("interval_index", 0)) - 1
    sched = _intervals_for(data, entry.get("type", "concept"))
    entry["interval_index"] = max(0, min(int(entry["interval_index"]), len(sched) - 1))
    entry["attempts"].append({"date": day, "is_correct": is_correct,
                              "result": result, "q_type": qtype})
    entry["last_reviewed"] = day
    entry["next_review"] = (datetime.strptime(day, "%Y-%m-%d").date()
                            + timedelta(days=sched[entry["interval_index"]])).isoformat()
    if feynman in ("feynman_pass", "feynman_fail"):
        entry["feynman"] = "pass" if feynman == "feynman_pass" else "fail"
    elif feynman is not None:
        print(f"ATTEMPT FAILED: feynman must be feynman_pass|feynman_fail, got {feynman!r}")
        sys.exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mastery = compute_mastery(entry["attempts"])
    feyn = entry.get("feynman") or "—"
    print(f"ATTEMPT OK: {concept} {result} mastery {mastery:.2f} — Feynman: {feyn}")
    print(f"next_review {entry['next_review']} (interval_index {entry['interval_index']})")


def do_mastery(track: str = "") -> None:
    data, _ = _load_attempts()
    concepts = data.get("concepts", {})
    names = sorted(concepts)
    if track:
        # Filter to the track's Active Concepts section when available.
        try:
            apath = _resolve("Learning System/Core/📚 Active Concepts.md")
            if apath.is_file():
                lines = apath.read_text(encoding="utf-8", errors="replace").splitlines()
                section, err = _section_slice(lines, rf"^## {re.escape(track)}\b")
                if not err and section:
                    in_section = {n for n in names if n in section}
                    if in_section:
                        names = sorted(in_section)
        except Exception:
            pass
    if not names:
        print("(no concepts)")
        return
    for n in names:
        e = concepts[n]
        m = compute_mastery(e.get("attempts", []))
        print(f"{n} mastery {m:.2f} — Feynman: {e.get('feynman') or '—'} "
              f"(next {e.get('next_review')})")


def _apply_op(kind: str, op: dict) -> str:
    p = _resolve(op["path"])
    if kind == "write":
        p.parent.mkdir(parents=True, exist_ok=True)
        existed = p.exists()
        p.write_text(op["content"], encoding="utf-8")
        return f"{'overwrote' if existed else 'created'} ({len(op['content'])} chars)"
    if kind == "append":
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(op["content"])
        return "appended"
    if kind == "replace":
        text = p.read_text(encoding="utf-8")
        find = op["find"]
        n = text.count(find)
        expected = op.get("count", n)
        if n == 0:
            return "ERROR: find-string not found"
        if expected != 1 and n != expected:
            return f"ERROR: found {n} occurrences, expected {expected}"
        p.write_text(text.replace(find, op["replace_with"], 1) if expected == 1 else text.replace(find, op["replace_with"]), encoding="utf-8")
        return f"replaced {min(n, expected) if expected > 1 else 1} occurrence(s)"


def do_apply(stream) -> None:
    try:
        spec = json.load(stream)
    except json.JSONDecodeError as e:
        print(f"APPLY FAILED: invalid JSON: {e}")
        sys.exit(1)
    results = []
    for kind in ("writes", "appends", "replaces"):
        for op in spec.get(kind, []):
            singular = kind.rstrip("s")
            try:
                res = _apply_op(singular, op)
            except Exception as e:
                res = f"ERROR: {e}"
            results.append((singular, op.get("path"), res))
            print(f"[{singular}] {op.get('path')} -> {res}")
    failed = sum(1 for _, _, r in results if r.startswith("ERROR"))
    print(f"APPLY DONE: {len(results)} op(s), {failed} failed")


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(2)
    cmd, *rest = argv
    if cmd == "bundle":
        do_bundle(*rest)
    elif cmd == "state":
        if not rest:
            print("usage: ops.py state TRACK")
            sys.exit(2)
        do_state(rest[0])
    elif cmd == "apply":
        do_apply(sys.stdin)
    elif cmd == "attempt":
        # attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date D] [--qtype T] [--type C]
        if len(rest) < 2:
            print('usage: ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type C]')
            sys.exit(2)
        concept, result = rest[0], rest[1]
        feynman = qtype = ctype = day = None
        positional = []
        i = 2
        while i < len(rest):
            tok = rest[i]
            if tok == "--date" and i + 1 < len(rest):
                day = rest[i + 1]; i += 2
            elif tok == "--qtype" and i + 1 < len(rest):
                qtype = rest[i + 1]; i += 2
            elif tok == "--type" and i + 1 < len(rest):
                ctype = rest[i + 1]; i += 2
            else:
                positional.append(tok); i += 1
        if positional:
            feynman = positional[0]
        do_attempt(concept, result, feynman=feynman, date=day, qtype=qtype, ctype=ctype)
    elif cmd == "mastery":
        do_mastery(rest[0] if rest else "")
    else:
        print(f"unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
