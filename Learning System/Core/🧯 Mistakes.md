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
| 2026-08-21 | What is the Shell | What does `#` in prompt `missing:~#` mean? | root/superuser (max privileges, prompt warns danger) | deviation | Thought # = guest — inverted privilege meaning | review | 1 | 2026-09-09 |
| 2026-08-19 | man & Documentation | What is the primary layer for authoritative command docs? | man (→ --help quick → tldr examples → LLM) | application | Had tldr/--help but missed man as primary | review | 1 | 2026-09-07 |
| 2026-08-19 | find | Why quote "*.zip" in `find -name "*.zip"`? | Prevent GLOB expansion (shell would expand * before find) — opposite of word-splitting | deviation | Retried 2026-08-24, failed INVERTED: claimed quotes enable glob expansion & unquoted hunts literal *.zip — actually the shell expands globs BEFORE find unless quoted (live-demo confirmed); retried 2026-08-25 — inverted a 3rd time even with a slow step-by-step trace of bash rewriting *.zip before find runs | review | 1 | 2026-09-08 |
| 2026-08-20 | Bash Quoting | Which quoting expands $ / $(cmd)? | Double "..." expands; single '...' literal; ANSI-C $'...' escapes only | structural | Flipped ANSI-C vs double-quote semantics; correct recall 2026-08-25 (discriminative — all three placements right) | review | 1 | 2026-09-24 |
| 2026-08-23 | sed (Stream Editor) | What does /g do in s/pat/rep/g? | Global: every match per line (not "do nothing else") | deviation | Misread /g as no-op; correct recall 2026-08-25 — predicted single-vs-global output and placed g correctly ('all occurrences in the line') | review | 1 | 2026-09-08 |
| 2026-08-25 | Shell Built-ins & Process Isolation | (probe) Which runs in the current shell and can change cwd? (quiz Q5) A script runs `mkdir /tmp/x && cd /tmp/x`; after exit, which survives? | built-in AND function run in the current shell (both can change cwd); a script AND an external command run in a child process (their cd is lost). Disk writes (mkdir) PERSIST; process-memory state (cwd) does NOT. | application | Probe: conflated disk side-effects with process state (picked that a script's cd changes the parent shell). Quiz Q5 recurred 'sure': said BOTH mkdir and cd persist — the disk-vs-memory split still wobbles when both effects appear in one script. | active | 0 | 2026-08-31 |
| 2026-08-28 | Vim Modal Editing | What does the `c` command do in Normal mode (as in `cw`)? | change = delete the motion, then enter Insert mode (NOT copy=that's `y`, NOT visual=that's `v`) | deviation | Answered 'hunch' D (enters Visual mode); had correctly said "make an edit in insert mode" during teaching, then slipped to the neighboring verb under quiz retrieval | active | 0 | 2026-08-31 |
| 2026-08-28 | Vim Composable Commands | What's the difference between `ci)` and `ct)`? | `i`=inner/inside (touch only between the parens, parens stay); `t`=up-to (delete from cursor to just before the next `)`) | deviation | Answered 'hunch' A (inverted: thought ci) eats the parens and ct) is inside); had answered `ci)`→"fizzbuzz()" correctly during teaching, then inverted i-vs-t under contrast | active | 0 | 2026-08-31 |
| 2026-08-25 | Process Substitution | Rewrite `diff $(ls ~/projectA) $(ls ~/projectB)` with <(); what does each substitution put in place? | $() splices output TEXT then word-splits — listing boundary melts, bare names resolve against wrong cwd; <(cmd) wraps ONE command and substitutes a pipe PATH (/dev/fd/N) so file-argument programs can consume it | application | Read both expansions as "combined list"; wrapped both listings in one <() so bash tried to execute filenames → empty pipes → diff falsely reported no differences | active | 0 | 2026-08-31 |
| 2026-08-25 | Shebang & Script Execution | Why does `bash run.sh` work without chmod +x, and what job does `#!` do in each invocation? | `./run.sh` = KERNEL executes the file directly → needs x bit, reads #! as absolute interpreter path and spawns it with the script; `bash run.sh` = bash READS the file (needs only r) → shebang is just a comment | structural | Thought #! means "look in this directory"; didn't separate the kernel-executes-file route from the bash-reads-file route | active | 0 | 2026-08-31 |
| 2026-08-26 | fd | What is fd and what is its key default behavior versus find? | fd is a faster, more intuitive find replacement; respects .gitignore by default (skips ignored files) for focused results out of the box | structural | Recalled identity (find alternative, easier syntax) but missed the load-bearing .gitignore-respecting default; retry 2026-08-29 again named the minor default (skips hidden) instead of the repo-aware .gitignore one | active | 0 | 2026-08-30 |

| 2026-08-28 | grep | What does `*` mean in a grep regex (vs a shell glob like `*.zip`)? | regex `*` repeats the PREVIOUS char (zero or more); glob `*` = any chars; `grep 'a*'` matches every line | application | Knew shell glob `*` = any characters; carried it into grep regex, missing that regex `*` repeats the preceding atom | active | 0 | 2026-08-31 |

| 2026-08-29 | PATH & Program Discovery | Where does the shell look when you type a bare command name, and why does it skip cwd? | Walks $PATH — a colon-separated list of DIRECTORIES — in order, looking for a file named `python` inside each; cwd is deliberately absent from PATH (security: a planted `ls` in cwd could not shadow the real one) | structural | Named the mechanic (PATH walk) but inverted the detail (PATH entries are dirs, not paths ending in the command) and missed why cwd is excluded | active | 0 | 2026-09-01 |

## Archived with C project (2026-08-25)

> Rows paused when the C-project strand was archived; kept verbatim, no longer in the review queue.

| 2026-08-20 | GCC Compilation Stages | Map flags to stages | -E preprocess, -S compile->asm, -c assemble->.o, link no-flag | structural | Mapped -r/-e, missed -E/-S/-c | active | 0 | 2026-08-24 |
| 2026-08-21 | C Integer Mechanics (Underflow & Type Promotion) | Why does (used/total)*100 give 0% for 8M/16M? | Integer division truncates before float; lead with 100.0 * to promote | structural | Inverted cause/cure (called promotion the problem) | active | 0 | 2026-08-24 |
| 2026-08-23 | C Memory Regions (Stack vs Heap vs Swap) | Does returning stack array leak or dangle? | Dangling (frame destroyed); stack cannot leak, only heap leaks | structural | Inverted dangling vs leak | active | 0 | 2026-08-24 |
| 2026-08-23 | C String Buffer Boundaries | Why char buf[SIZE+1]? | +1 for NUL terminator; validate before strcpy, else overflow | deviation | Named NUL but missed bounds-check-before-copy | active | 0 | 2026-08-24 |
| 2026-09-05 | 4-Layer AI Environment Stack | torch imports but CUDA/GPU not visible — which stack layer? | Runtimes (CUDA/runtime layer), not System | structural | Placed GPU-invisible at System layer; missed the Runtimes split (learner wording not supplied — inferred from answer) | active | 0 | 2026-09-08 |
| 2026-09-05 | Cosine Similarity | cos(A,B) vs cos(A,C) for A=[1,0], B=[0,1], C=[2,0]; why does this prove magnitude-invariance where dot fails? | cos=0 vs cos=1; dot conflates magnitude (dot(A,C)=2 vs dot(A,A)=1 for the same direction) | structural | Answered in angles (90/0 deg) not cosines; claimed dot tells the better similarity story — inverted (learner wording not supplied — inferred from answer) | active | 0 | 2026-09-08 |
