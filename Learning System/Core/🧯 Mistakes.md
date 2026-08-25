# Mistakes — Structured Wrong-Answer Ledger

> Purpose: Every failed review/probe/quiz item is recorded here with its error type and self-attribution.
> This is the priority-1 queue (DeepTutor pattern). Due mistakes are asked BEFORE normal due reviews.
> Lifecycle: `active` → `review` → `graduated` (retired after 2 consecutive correct recalls).
> Advisory only for now — mistakes do not block, but surface first in review selection.

## How to record (during review/teach sessions)
- **concept**: exact Concept name as in Active Concepts.md
- **question**: the question asked
- **expected**: server-side expected answer (short, not leaked)
- **error_type**: `structural | deviation | application | metacognitive`
  - structural = knowledge architecture wrong
  - deviation = understood but slipped / misread
  - application = knew but applied wrong
  - metacognitive = blank / "I don't know"
- **self_attribution**: learner's own words on why
- **status**: `active` (needs retry), `review` (1 correct so far), `graduated` (2 consecutive correct, retired)
- **retries**: count of correct recalls since creation

## Queue rule (review flow)
- Slots 1–2 of each 5-review session = due mistakes (`active`/`review` where Next Retry <= today), sorted by oldest first.
- Remaining 3 slots = type-aware due reviews (Attempts.json) shuffled with adjacency guard (no two same Source consecutively).

## Table

| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-21 | What is the Shell | What does `#` in prompt `missing:~#` mean? | root/superuser (max privileges, prompt warns danger) | deviation | Thought # = guest — inverted privilege meaning | active | 0 | 2026-08-24 |
| 2026-08-19 | man & Documentation | What is the primary layer for authoritative command docs? | man (→ --help quick → tldr examples → LLM) | application | Had tldr/--help but missed man as primary | review | 1 | 2026-09-07 |
| 2026-08-19 | find | Why quote "*.zip" in `find -name "*.zip"`? | Prevent GLOB expansion (shell would expand * before find) — opposite of word-splitting | deviation | Retried 2026-08-24, failed INVERTED: claimed quotes enable glob expansion & unquoted hunts literal *.zip — actually the shell expands globs BEFORE find unless quoted (live-demo confirmed); retried 2026-08-25 — inverted a 3rd time even with a slow step-by-step trace of bash rewriting *.zip before find runs | active | 0 | 2026-08-28 |
| 2026-08-20 | Bash Quoting | Which quoting expands $ / $(cmd)? | Double "..." expands; single '...' literal; ANSI-C $'...' escapes only | structural | Flipped ANSI-C vs double-quote semantics; correct recall 2026-08-25 (discriminative — all three placements right) | review | 1 | 2026-09-24 |
| 2026-08-23 | sed (Stream Editor) | What does /g do in s/pat/rep/g? | Global: every match per line (not "do nothing else") | deviation | Misread /g as no-op | active | 0 | 2026-08-24 |
| 2026-08-25 | Shell Built-ins & Process Isolation | Which runs in the current shell and can change cwd — a function, a script, a built-in, or an external command? | built-in AND function run in the current shell (both can change cwd); a script AND an external command run in a child process (their cd is lost on exit). Only disk writes (mkdir/touch) persist across the boundary. | application | Conflated disk side-effects with process state: reasoned "scripts cause side effects → run in own process", then picked that a script's cd changes the parent shell's cwd. Had the right principle (cd mutates shell state) but didn't extend it to scripts. | active | 0 | 2026-08-28 |
| 2026-08-25 | Process Substitution | Rewrite `diff $(ls ~/projectA) $(ls ~/projectB)` with <(); what does each substitution put in place? | $() splices output TEXT then word-splits — listing boundary melts, bare names resolve against wrong cwd; <(cmd) wraps ONE command and substitutes a pipe PATH (/dev/fd/N) so file-argument programs can consume it | application | Read both expansions as "combined list"; wrapped both listings in one <() so bash tried to execute filenames → empty pipes → diff falsely reported no differences | active | 0 | 2026-08-28 |

## Archived with C project (2026-08-25)

> Rows paused when the C-project strand was archived; kept verbatim, no longer in the review queue.

| 2026-08-20 | GCC Compilation Stages | Map flags to stages | -E preprocess, -S compile->asm, -c assemble->.o, link no-flag | structural | Mapped -r/-e, missed -E/-S/-c | active | 0 | 2026-08-24 |
| 2026-08-21 | C Integer Mechanics (Underflow & Type Promotion) | Why does (used/total)*100 give 0% for 8M/16M? | Integer division truncates before float; lead with 100.0 * to promote | structural | Inverted cause/cure (called promotion the problem) | active | 0 | 2026-08-24 |
| 2026-08-23 | C Memory Regions (Stack vs Heap vs Swap) | Does returning stack array leak or dangle? | Dangling (frame destroyed); stack cannot leak, only heap leaks | structural | Inverted dangling vs leak | active | 0 | 2026-08-24 |
| 2026-08-23 | C String Buffer Boundaries | Why char buf[SIZE+1]? | +1 for NUL terminator; validate before strcpy, else overflow | deviation | Named NUL but missed bounds-check-before-copy | active | 0 | 2026-08-24 |
