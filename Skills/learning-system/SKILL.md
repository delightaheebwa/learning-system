---
name: learning-system
description: Run the spaced-repetition learning system in Open WebUI. Triggers — "swe"/"review" (review the swe track), "ingest" (ingest new content), "teach me X"/"learn"/"study" (teaching loop, delegated to the learning-teach skill), "lesson"/"continue" (next curriculum lesson, delegated to learning-teach). Loads the Core state files from the repo at /home/user/learning-system, executes the review/ingest/teach flow, and persists session notes, wiki updates, and Active Concepts changes.
---

# Learning System

The active learning system, running in Open WebUI against the repo at `/home/user/learning-system` (Open Terminal workspace). Trigger by saying a track ("swe"), "ingest", a learning intent, or "lesson"/"continue" for the next curriculum lesson.

**Trigger routing (read first):**
- **"swe" / "review" → review flow** (below).
- **"teach me X" / "learn" / "study" → teaching loop** — `Skills/learning-teach/SKILL.md`, NOT a review. "review" alone means the review flow.
- **"lesson" / "continue" → next curriculum lesson** — `Skills/learning-teach/SKILL.md`.

## Context discipline (hard rules — read first)

Sessions die when the running conversation outgrows the model's context window: cutoffs hit mid-flow (~20 tool calls) because every tool output stays in the transcript forever. The fix is fewer, denser tool calls — not smaller messages.

- **Batch all reads.** Never chain multiple full-file `read_file` calls for state. Use the batch tool ONCE instead (`run_command`, paths are repo-root-relative):
  - Session start: `python3 /home/user/.ops/ops.py state <track>`
  - Any mix of ranges/tails/greps: `python3 /home/user/.ops/ops.py bundle "PATH:N-M" "PATH:-N" "PATH@regex1|regex2"`
- **Read wiki pages by section.** First `bundle "Knowledge Wiki/wiki/<page>.md@^## "` to list its headings, then fetch only the section you actually enrich.
- **Batch all writes.** Persistence at session end = ONE apply call, not N `write_file` calls:
  `python3 /home/user/.ops/ops.py apply <<'SPEC'` then a JSON spec, then `SPEC`.
  Spec: `{"writes":[{"path","content"}],"appends":[{path,content}],"replaces":[{"path","find","replace_with"}]}`.
- Target **≤12 tool calls per flow**. Never re-read a file already in context. Never dump whole files you only need one row of.

## State files (repo root: `/home/user/learning-system`)

- `Learning System/Core/💡 Learning Profile.md` — learner preferences. Read at session start.
- `Learning System/Core/📚 Active Concepts.md` — per-track concept rows (aie, swe). The review schedule's sole source of truth. Grep/range only the needed track — never the whole file.
- `Learning System/Core/📦 Concept Archive.md` — paused/archived concepts. Grep on demand; never auto-load.
- `Learning System/Sessions/`, `Learning System/Reviews/`, `Learning System/Concept Notes/`, `Learning System/Archive/` — writes land here.
- `Learning System/MISSION.md`, `Learning System/CURRICULUM.md`, `Learning System/GLOSSARY.md`, `Learning System/RESOURCES.md` — mission, curriculum, glossary, curated readings.

## Teaching flow (delegation)

Trigger: "teach me X", "lesson", or "continue".

1. Load `Learning System/MISSION.md` + `Learning System/CURRICULUM.md` to determine the next lesson (or the requested topic).
2. **`lesson`/`continue`:** pick the next lesson per `CURRICULUM.md`'s deterministic two-strand rotation; if the lesson is resumable (mid-lesson state exists), resume where left off. A `done` lesson is never re-taught — retrieval-verify instead.
3. **`teach me X`:** in Stage-0 scope → treat as a curriculum node (add/route it); out of scope → one-off that still feeds Active Concepts + wiki, and surface the "switching focus?" question (mirrors the ingest flow).
4. Delegate the full probe → plan → teach loop to the `learning-teach` skill. Teaching verification is done live with the `fact_check` tool (`deepseek-v4-flash`); the `review_gate` tool (`minimax-m3`) is **ingest-only**.

## Review flow

Trigger: "swe", "review", or a learning request.

1. Track selection: "swe" → swe table; "aie" → aie table (currently archived — ask the user before unarchiving); neither → ask which track.
2. Session start — ONE call: `run_command` → `python3 /home/user/.ops/ops.py state <track>`. This returns Learning Profile + your track's Active Concepts rows. Do not read those files separately.
3. Find rows with Next Review on/before today. Shuffle. Adjacency constraint: no two consecutive concepts from the same Source (if impossible, shuffle anyway).
4. Per concept: one question, one answer (≤1 line), targeting the 20% insight worth 80%. Math: ask insight/result, never notation.
5. Question type alternation by Last Q Type: blank/definitional → discriminative; discriminative → definitional.
6. After each: write `Reviews/Review — [Concept] — [Date].md`; update `last_reviewed` (today), `next_review` (next interval), `Last Q Type` (type just asked).
7. Cap 5. Then ask "Any you want to dig deeper on?" — if yes, deep-dive one concept.
8. Surface open questions from Active Concepts.

Intervals: 3d → 7d → 14d → 30d → 90d → consolidated. No separate review queue — compute from Next Review.

## Ingest flow

Trigger: "ingest" with content to add (NOT a review).

1. Extract concepts from the content.
2. Overlap check — ONE bundle call with an alternation regex over candidate keywords: `python3 /home/user/.ops/ops.py bundle "Learning System/Core/📚 Active Concepts.md@kw1|kw2|kw3"` (or `@^### ` to pull the full track section). No separate grep/read calls per keyword.
3. Overlap → enrich the existing wiki page + insight row with the genuinely new details; set `last_reviewed` today; write the session note as enrichment (not new ingest). Read only the target page's relevant section (headings first via `@^## `).
4. No overlap → new concept: status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`.
5. Outside focus area → ask about switching focus. Stagger schedules for multiple new concepts.
6. Persist EVERYTHING in one apply call (`ops.py apply` heredoc): wiki page(s), index.md update, log.md entry, session note. Do not interleave write_file calls between reasoning steps.
7. Run the learning-review gate (`review_gate` tool, `minimax-m3`) on the wiki content you just wrote (you already have it from your own spec — do NOT re-read it from disk). Pass the source URL and concept names too. An independent review flags accuracy/clarity/completeness issues with severity; you fix them (one more apply call); max 2 cycles. Do not finalize the ingest until the gate reports.

### Handwritten notes

If the source is an image (handwritten notes, photo of a page), transcribe it verbatim before extraction:

- Use a vision-capable model available in Open WebUI to read the image, or ask the user to provide the text.
- Input: the image at {filepath}; transcribe verbatim preserving structure (headings, bullets, diagrams in brackets); light cleanup only (fix obvious spelling, expand unambiguous abbreviations like 'bc' → 'because'); no rephrasing, summarization, or interpretation.
- Retry once on failure; if still failing, tell the user — never silently skip the image.

## End-of-session writes

1. Update Active Concepts — statuses, dates, new concepts, open questions. Preserve existing rows.
2. On `consolidated`: move to `Archive/Consolidated/[concept].md` (name, date, insight, wiki link, related), remove from Active, update Mastery Summary.
3. Write `Sessions/Session — [Topic] — [Date].md` (date, topic, concepts, statuses, open questions) with a one-line interleaving summary, e.g. "Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional".
4. Consistency check — ONE bundle call re-grepping only the touched rows: `python3 /home/user/.ops/ops.py bundle "Learning System/Core/📚 Active Concepts.md@<concept1>|<concept2>" "Knowledge Wiki/index.md@<title>" "Knowledge Wiki/log.md:-3"`; verify today's `last_reviewed`, correct `next_review`, `Last Q Type`, all ingested concepts present, wiki pages in index.md, log entry present. Fix discrepancies in a single apply call. If the user claims stale dates are wrong, cross-check session notes.
5. Confirm completion — what was saved, what's due next.

## Open WebUI adaptation

- **Source of truth:** this GitHub repo. Load state files from the repo (`/home/user/learning-system`) before every flow; keep Open WebUI mirror content in sync with the repo, never the other way around.
- **Review gate (ingest step 7):** call the `review_gate` tool, which invokes a SECOND model (`minimax-m3`) as the independent reviewer. Pass the source URL, concept names, and the wiki content (read via the terminal). See `OPENWEBUI.md` at the repo root for setup.
- **Teaching verification:** call the `fact_check` tool (`deepseek-v4-flash`) for load-bearing claims before presenting them.
- **After writes:** commit and push per `Learning System/AGENTS.md` (paths: `/home/user/learning-system`).