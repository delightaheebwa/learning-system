#!/usr/bin/env python3
"""Batch file ops for the learning-system workspace (open-terminal sidecar).

Purpose: collapse many sequential read/write tool calls into ONE command so
agent sessions stay far below the model's cumulative context limit.

Usage:
  ops.py state TRACK              Standard session-start bundle for TRACK (aiefs|aie|swe).
                                  One call replaces: Learning Profile read, Active
                                  Concepts track slice, Attempts.json, Mistakes.md,
                                  log tail, index head.
  ops.py state TRACK --review     Compact review-session context: Learning Profile +
                                  the computed due queue (same as `queue`). Use this
                                  instead of the full `state` dump when starting a
                                  /review session.
  ops.py queue TRACK [--date YYYY-MM-DD] [--slots N] [--json] [--digest PATH]
                                  Compute the deterministic review queue: up to 2
                                  priority-1 due mistakes (oldest first) then due
                                  reviews from Attempts.json, shuffled with a
                                  same-Source adjacency guard and per-concept
                                  question-type alternation. Prints a human table
                                  (default), the queue JSON (--json), or writes the
                                  review digest skeleton to PATH (--digest).
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
  ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type memory|concept|procedure|design] [--confidence sure|hunch|no-idea] [--hints N] [--mode normal|solo]
                                  Record one answer in Attempts.json (interval_index
                                  +1 pass / +2 on 2 consecutive passes / -1 fail,
                                  next_review from type schedule). Prints mastery +
                                  next_review for the skill to copy via apply.
  ops.py mastery [TRACK] [--json]  Advisory mastery report: recency-weighted
                                  score plus per-dimension (recall, conceptual,
                                  procedural, transfer, independence, stability)
                                  from the attempt evidence. --json for machines.
                                   (0.00-1.00 + Feynman status, not blocking).

All paths resolve under the workspace root (/home/user/learning-system). Escapes are rejected.
"""

import json
import os
import random
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
    dynamic = []
    script_path = Path(__file__).resolve()
    dynamic.extend(str(p) for p in (script_path.parent, *script_path.parents))
    cwd = Path.cwd().resolve()
    dynamic.extend(str(p) for p in (cwd, *cwd.parents))

    candidates = [
        os.environ.get("LEARNING_SYSTEM_ROOT", ""),
        *dynamic,
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
ACTIVE_PATH = "Learning System/Core/📚 Active Concepts.md"
WIKI_DIR = "Knowledge Wiki/wiki"
MASTERY_WEIGHTS = [0.4, 0.25, 0.15, 0.1, 0.1]
ERROR_TYPES = ("structural", "deviation", "application", "metacognitive")

# Question types that evidence each mastery dimension (P0.4). Untagged or
# unknown q_types count toward recall only. Dimensions without any evidencing
# attempt report None ("unknown"), never a false zero.
RECALL_Q_TYPES = {"definitional", "free_recall", "recall-mcq", "recall_mcq", "micro-check"}
PROCEDURAL_Q_TYPES = {"computational", "applied", "procedure"}
TRANSFER_Q_TYPES = {"transfer", "novel", "error-detect", "error_detect"}


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
    if track == "aiefs":
        # Active AIEFS concepts live under per-lesson headings (Mission 0
        # Catch-Up, Phase 1 …), not a single `## aiefs` heading — pull the
        # live concept tables wholesale instead of one section.
        concept_spec = ("Learning System/Core/📚 Active Concepts.md@^\\| ", "")
    else:
        concept_spec = (f"Learning System/Core/📚 Active Concepts.md#^## {track}\\b", "")
    specs = [
        ("Learning System/Core/💡 Learning Profile.md", ""),
        # Section selector (#heading) pulls the whole track block (header + table
        # rows) — the old `^## {track}\b|^### ` grep matched only heading lines.
        concept_spec,
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


def _recent_correctness(attempts: list) -> float:
    """Recency-weighted correctness 0-1 over the last (up to 5) attempts."""
    if not attempts:
        return 0.0
    recent = attempts[-5:][::-1]  # most recent first
    weights = MASTERY_WEIGHTS[: len(recent)]
    total = sum(weights)
    return sum(w * (1.0 if a.get("is_correct") else 0.0) for w, a in zip(weights, recent)) / total


def compute_mastery(attempts: list) -> float:
    """Recency-weighted mastery 0-1 with confidence caps ({1:0.5, 2:0.8})."""
    if not attempts:
        return 0.0
    score = _recent_correctness(attempts)
    n = len(attempts)
    if n == 1:
        score = min(score, 0.5)
    elif n == 2:
        score = min(score, 0.8)
    return round(score, 2)


def _feynman_state(entry: dict):
    """Normalise the feynman field to True/False/None."""
    f = entry.get("feynman")
    if isinstance(f, dict):
        f = f.get("pass")
    if f in (True, "pass"):
        return True
    if f in (False, "fail"):
        return False
    return None


def compute_dimensions(entry: dict) -> dict:
    """Per-dimension mastery (0-3, or None when no evidence exists).

    Advisory, heuristic, and deliberately explicit about its inputs (P0.4):
      recall        recency-weighted correctness of recall-type attempts
      conceptual    driven by the Feynman explain-back flag
      procedural    correctness of computational/applied/procedure attempts
      transfer      correctness of transfer/novel/error-detect attempts
      independence  the last AI-free (mode="solo") attempt; None if never tested
      stability     interval_index (how long a gap the concept has survived)
    A dimension with no evidencing attempt is None (unknown), never 0, so an
    untested dimension cannot masquerade as a failed one."""
    attempts = entry.get("attempts", []) or []

    def dim(sel):
        if not sel:
            return None
        return int(round(3 * _recent_correctness(sel)))

    recall_sel = [a for a in attempts if (a.get("q_type") in RECALL_Q_TYPES) or not a.get("q_type")]
    solo = [a for a in attempts if a.get("mode") == "solo"]
    conceptual = None
    feyn = _feynman_state(entry)
    if feyn is not None:
        conceptual = 3 if feyn else 0
    return {
        "recall": dim(recall_sel),
        "conceptual": conceptual,
        "procedural": dim([a for a in attempts if a.get("q_type") in PROCEDURAL_Q_TYPES]),
        "transfer": dim([a for a in attempts if a.get("q_type") in TRANSFER_Q_TYPES]),
        "independence": (3 if solo[-1].get("is_correct") else 0) if solo else None,
        "stability": min(3, int(entry.get("interval_index", 0) or 0)),
    }


def independence_ok(entry: dict) -> bool:
    """False only when a failed AI-free (solo) attempt is on record.

    Absence of solo evidence is *unknown*, not failure, so existing concepts
    are grandfathered until `/solo` produces a real test (P0.4/P0.5)."""
    return compute_dimensions(entry).get("independence") != 0


def _parse_date(s: str):
    s = (s or "").strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_table_rows(path: Path, min_cols: int):
    """Parse markdown table rows into cell lists, skipping the header and the
    separator row. Cells are split on '|'; ragged rows shorter than min_cols are
    dropped. The caller is responsible for joining any over-flowing trailing
    cells (e.g. free-text notes that contain a literal '|')."""
    if not path.is_file():
        return []
    rows = []
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < min_cols:
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c != ""):
            continue
        rows.append(cells)
    return rows


def _track_matches(row_track: str, track: str) -> bool:
    rt = (row_track or "").lower().strip()
    t = track.lower().strip()
    if t in ("aiefs", "aie"):
        return rt in ("aiefs", "aie")
    return rt == t


def _active_rows(track: str):
    """Return (track_rows map, all_rows list) parsed from Active Concepts.md."""
    rows = _parse_table_rows(_resolve(ACTIVE_PATH), 8)
    all_rows, track_rows = [], {}
    for c in rows:
        if c[0].lower() == "concept":
            continue
        rec = {
            "concept": c[0], "track": c[1], "type": c[2], "status": c[3],
            "source": c[4], "last_reviewed": c[5], "next_review": c[6],
            "last_q_type": c[7], "notes": " | ".join(c[8:]).strip(),
        }
        all_rows.append(rec)
        track_rows[rec["concept"]] = rec
    if track:
        track_rows = {k: v for k, v in track_rows.items() if _track_matches(v["track"], track)}
    return track_rows, all_rows


def _mistakes_rows():
    """Parse the mistakes ledger. error_type is located by matching the enum
    (robust to literal '|' in the question/expected/self-attribution cells);
    status/retries/next_retry are always the last three cells."""
    rows = _parse_table_rows(_resolve(MISTAKES_PATH), 9)
    out = []
    for c in rows:
        if c[0].lower() == "date":
            continue
        idx = next((i for i in range(4, len(c)) if c[i].lower() in ERROR_TYPES), None)
        if idx is None or len(c) < 9:
            continue
        out.append({
            "date": c[0], "concept": c[1], "question": c[2],
            "expected": " | ".join(c[3:idx]),
            "error_type": c[idx].lower(),
            "self_attribution": " | ".join(c[idx + 1:len(c) - 3]),
            "status": c[-3].lower(), "retries": c[-2], "next_retry": c[-1],
        })
    return out


def _source_key(entry: dict) -> str:
    """Normalize the Source column so the adjacency guard compares the same
    lesson/mission origin: drop the language parenthetical, prefer a
    'rohit pn lnn' token, else the lowercased text."""
    src = (entry.get("source") or "").lower()
    src = re.sub(r"\([^)]*\)", "", src)
    m = re.search(r"rohit\s+p\d+\s+l\d+", src)
    return (m.group(0) if m else src).strip()


def _concept_excerpt(name: str, notes: str) -> str:
    """Best-effort grounding excerpt for a queue entry: the wiki page's Insight
    line + first body paragraph, else the Active Concepts notes cell."""
    try:
        wiki = _resolve(WIKI_DIR)
        target = None
        direct = _resolve(f"{WIKI_DIR}/{name}.md")
        if direct.is_file():
            target = direct
        elif wiki.is_dir():
            files = os.listdir(wiki)
            low = name.lower()
            exact = [f for f in files if f.lower() == f"{low}.md"]
            fuzzy = [f for f in files if low in f.lower() or f[:-3].lower() in low]
            pick = (exact or fuzzy or [None])[0]
            if pick:
                target = _resolve(f"{WIKI_DIR}/{pick}")
        if target is not None and target.is_file():
            lines = [l.strip() for l in target.read_text(encoding="utf-8", errors="replace").splitlines()]
            insight = next((l for l in lines if "**Insight:**" in l), "")
            insight = re.sub(r"^>\s*", "", insight)
            body = [l for l in lines if l and not l.startswith(("#", ">", "|"))]
            parts = [insight] if insight else []
            if body:
                parts.append(" ".join(body[:3]))
            ex = " ".join(parts).strip()
            if ex:
                return ex[:500]
    except Exception:
        pass
    return (notes or "").strip()[:500]


def _question_type(last_q: str) -> str:
    """Alternate by Last Q Type: definitional -> discriminative; everything else
    (discriminative, computational, memory, blank) -> definitional."""
    return "definitional" if (last_q or "").strip().lower() == "discriminative" else "discriminative"


def _order_adjacency(entries, keyfn, initial_key=None):
    """Reorder so no two consecutive entries share a Source key whenever a valid
    arrangement exists (most-frequent-remaining-key first, never the previous
    key). Falls back to the remaining order when the constraint is impossible."""
    groups = {}
    for e in entries:
        groups.setdefault(keyfn(e), []).append(e)
    result = []
    last = initial_key
    while len(result) < len(entries):
        keys = [k for k, v in groups.items() if v]
        if not keys:
            break
        pickable = [k for k in keys if k != last] or keys
        best = max(pickable, key=lambda k: len(groups[k]))
        result.append(groups[best].pop(0))
        last = best
    return result


def _queue_entry(row: dict, attempts: dict, due_kind: str, mistake=None) -> dict:
    name = row["concept"]
    e = attempts.get(name, {}) or {}
    last_q = row.get("last_q_type") or ""
    return {
        "concept": name,
        "type": row.get("type", "concept"),
        "source": row.get("source", ""),
        "last_q_type": last_q,
        "question_type": _question_type(last_q),
        "due_kind": due_kind,
        "last_reviewed": row.get("last_reviewed", ""),
        "next_review": e.get("next_review") or row.get("next_review", ""),
        "mastery": compute_mastery(e.get("attempts", [])),
        "feynman": e.get("feynman") or None,
        "error_type": (mistake or {}).get("error_type"),
        "self_attribution": (mistake or {}).get("self_attribution"),
        "source_excerpt": _concept_excerpt(name, row.get("notes", "")),
    }


def _build_queue(track: str, day: date, slots: int = 5) -> dict:
    """Compute the deterministic review queue and return the payload dict."""
    data, _ = _load_attempts()
    attempts = data.get("concepts", {})
    track = (track or "aiefs").lower().strip()
    track_rows, all_rows = _active_rows(track)
    notes = []

    # Slots 1-2: due mistakes (active/review, next retry <= day), oldest first,
    # one per concept.
    due_mistakes, seen = [], set()
    for m in sorted(_mistakes_rows(), key=lambda r: r["date"]):
        if m["status"] not in ("active", "review"):
            continue
        nr = _parse_date(m["next_retry"])
        if not nr or nr > day:
            continue
        if m["concept"] in seen:
            continue
        row = track_rows.get(m["concept"])
        if row is None:
            other = next((r for r in all_rows if r["concept"] == m["concept"]), None)
            if other is not None:
                notes.append(f"due mistake '{m['concept']}' is in track '{other['track']}', not '{track}'")
            else:
                notes.append(f"due mistake '{m['concept']}' has no Active Concepts row")
            continue
        seen.add(m["concept"])
        due_mistakes.append((m, row))
        if len(due_mistakes) >= 2:
            break

    # Remaining slots: due reviews from Attempts.json (scheduler truth).
    candidates = []
    for name, row in track_rows.items():
        if name in seen:
            continue
        e = attempts.get(name)
        if not e:
            if (_parse_date(row.get("next_review")) or date.max) <= day:
                notes.append(f"'{name}' due in Active Concepts ({row['next_review']}) but missing from Attempts.json")
            continue
        nr = _parse_date(e.get("next_review"))
        if nr and nr <= day:
            candidates.append((name, row, e))

    rng = random.Random(f"{track}:{day.isoformat()}")
    rng.shuffle(candidates)
    ordered = _order_adjacency(
        candidates, keyfn=lambda t: _source_key(t[1]),
        initial_key=_source_key(due_mistakes[-1][1]) if due_mistakes else None)

    queue = [_queue_entry(row, attempts, "mistake", m) for m, row in due_mistakes]
    for name, row, _e in ordered[:max(0, slots - len(queue))]:
        queue.append(_queue_entry(row, attempts, "review"))

    # Drift: Active Concepts next_review vs Attempts.json (scheduler truth).
    for name, row in track_rows.items():
        e = attempts.get(name)
        if e and row.get("next_review") and e.get("next_review") and row["next_review"] != e["next_review"]:
            notes.append(f"'{name}' Next Review {row['next_review']} (AC) != {e['next_review']} (Attempts)")

    # Dedupe + cap the drift notes (report, never fix).
    notes = list(dict.fromkeys(notes))[:12]

    return {
        "track": track, "date": day.isoformat(),
        "due_mistakes": len(due_mistakes), "due_reviews": len(queue) - len(due_mistakes),
        "slots": slots, "queue": queue, "warnings": notes,
    }


def do_queue(track: str, day: date, slots: int = 5, as_json: bool = False,
             digest_path: str = None) -> None:
    payload = _build_queue(track, day, slots)

    if digest_path:
        p = _resolve(digest_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        digest = {
            "track": payload["track"], "digest": digest_path,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "position": None, "queue": payload["queue"],
            "due_mistakes": payload["due_mistakes"], "due_reviews": payload["due_reviews"],
            "warnings": payload["warnings"],
        }
        p.write_text(json.dumps(digest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"WROTE {digest_path} ({len(payload['queue'])} queue entr"
              f"{'y' if len(payload['queue']) == 1 else 'ies'})")
        if not as_json:
            _print_queue_table(payload)
        return

    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    _print_queue_table(payload)


def _print_queue_table(payload: dict) -> None:
    q = payload["queue"]
    print(f"REVIEW QUEUE — track {payload['track']} — {payload['date']}    "
          f"({len(q)} slot(s): {payload['due_mistakes']} due mistake(s), {payload['due_reviews']} due review(s))")
    if not q:
        print("(nothing due — no mistakes or reviews on or before today)")
    for i, e in enumerate(q, 1):
        tail = f"mastery {e['mastery']:.2f}"
        if e["due_kind"] == "mistake":
            tail += f" · error_type {e['error_type']}"
        print(f"{i}. [{e['due_kind']}] {e['concept']} — {e['type']} · {e['source']} · "
              f"last Q {e['last_q_type'] or '—'} → ask {e['question_type']} · {tail}")
        if e.get("self_attribution"):
            print(f"     self-attribution: {e['self_attribution'][:160]}")
    if payload["warnings"]:
        print("NOTES:")
        for n in payload["warnings"]:
            print(f" - {n}")


def do_attempt(concept: str, result: str, feynman: str = None, date: str = None,
               qtype: str = None, ctype: str = None, confidence: str = None,
               hints: int = None, mode: str = None) -> None:
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
    rec = {"date": day, "is_correct": is_correct, "result": result, "q_type": qtype}
    # Optional per-attempt evidence (P0.4): confidence tag, hints used, and
    # whether the attempt was AI-free ("solo"). Recorded only when supplied so
    # existing callers and stored attempts are unaffected.
    if confidence:
        rec["confidence"] = confidence
    if hints is not None:
        rec["hints"] = int(hints)
    if mode:
        rec["mode"] = mode
    entry["attempts"].append(rec)
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


def do_mastery(track: str = "", as_json: bool = False) -> None:
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
    rows = []
    for n in names:
        e = concepts[n]
        rows.append({
            "concept": n,
            "mastery": compute_mastery(e.get("attempts", [])),
            "feynman": e.get("feynman"),
            "next_review": e.get("next_review"),
            "dimensions": compute_dimensions(e),
        })
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for r in rows:
        d = r["dimensions"]
        pretty = " ".join(
            f"{k[:4]} {'—' if v is None else v}"
            for k, v in d.items()
        )
        print(f"{r['concept']} mastery {r['mastery']:.2f} — Feynman: {r['feynman'] or '—'} "
              f"(next {r['next_review']}) | {pretty}")


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
            print("usage: ops.py state TRACK [--review]")
            sys.exit(2)
        track = next((t for t in rest if not t.startswith("--")), "aiefs")
        if "--review" in rest:
            do_bundle("Learning System/Core/💡 Learning Profile.md")
            do_queue(track, date.today(), 5)
        else:
            do_state(track)
    elif cmd == "queue":
        track = next((t for t in rest if not t.startswith("--")), "aiefs")
        day = date.today()
        slots = 5
        as_json = False
        digest_path = None
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok == "--date" and i + 1 < len(rest):
                parsed = _parse_date(rest[i + 1])
                if parsed is None:
                    print(f"queue: bad --date {rest[i + 1]!r}, want YYYY-MM-DD")
                    sys.exit(2)
                day = parsed; i += 2
            elif tok == "--slots" and i + 1 < len(rest):
                try:
                    slots = max(1, int(rest[i + 1]))
                except ValueError:
                    print(f"queue: bad --slots {rest[i + 1]!r}")
                    sys.exit(2)
                i += 2
            elif tok == "--digest" and i + 1 < len(rest):
                digest_path = rest[i + 1]; i += 2
            elif tok == "--json":
                as_json = True; i += 1
            else:
                i += 1
        do_queue(track, day, slots, as_json=as_json, digest_path=digest_path)
    elif cmd == "apply":
        do_apply(sys.stdin)
    elif cmd == "attempt":
        # attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date D] [--qtype T] [--type C]
        if len(rest) < 2:
            print('usage: ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail] [--date YYYY-MM-DD] [--qtype TYPE] [--type C]')
            sys.exit(2)
        concept, result = rest[0], rest[1]
        feynman = qtype = ctype = day = confidence = mode = None
        hints = None
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
            elif tok == "--confidence" and i + 1 < len(rest):
                confidence = rest[i + 1]; i += 2
            elif tok == "--hints" and i + 1 < len(rest):
                try:
                    hints = int(rest[i + 1])
                except ValueError:
                    print(f"ATTEMPT FAILED: --hints must be an integer, got {rest[i + 1]!r}")
                    sys.exit(2)
                i += 2
            elif tok == "--mode" and i + 1 < len(rest):
                mode = rest[i + 1]; i += 2
            else:
                positional.append(tok); i += 1
        if positional:
            feynman = positional[0]
        do_attempt(concept, result, feynman=feynman, date=day, qtype=qtype, ctype=ctype,
                   confidence=confidence, hints=hints, mode=mode)
    elif cmd == "mastery":
        as_json = "--json" in rest
        track = next((t for t in rest if not t.startswith("--")), "")
        do_mastery(track, as_json=as_json)
    else:
        print(f"unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
