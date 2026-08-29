#!/usr/bin/env python3
"""Batch file ops for the learning-system workspace (open-terminal sidecar).

Purpose: collapse many sequential read/write tool calls into ONE command so
agent sessions stay far below the model's cumulative context limit.

Usage:
  ops.py state TRACK              Standard session-start bundle for TRACK (aie|swe).
                                  One call replaces: Learning Profile read, Active
                                  Concepts track slice, log tail, index head.
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

All paths resolve under the workspace root (/home/user/learning-system). Escapes are rejected.
"""

import json
import os
import re
import sys
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
    else:
        print(f"unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
