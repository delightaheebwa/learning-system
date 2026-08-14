---
name: learning-system
description: Run the spaced-repetition learning system. Triggers — "swe" (review the swe track), "ingest" (ingest new content), or "learn"/"study"/"teach me"/"review" (start a review session). Loads the Core state files, executes the review or ingest flow, and persists session notes, wiki updates, and Active Concepts changes.
compatibility: Open WebUI (self-hosted)
metadata:
  author: delight
  home: https://github.com/delightaheebwa/learning-system
---

# Learning System

The active learning system. Trigger by saying a track ("swe"), "ingest", or a learning intent.

## State files

- `Learning System/Core/💡 Learning Profile.md` — learner preferences. Read at session start.
- `Learning System/Core/📚 Active Concepts.md` — per-track concept rows (aie, swe). The review schedule's sole source of truth. Grep/range only the needed track — never the whole file.
- `Learning System/Core/📦 Concept Archive.md` — paused/archived concepts. Grep on demand; never auto-load.
- `Learning System/Core/📖 Scripture Memory.md` — handled by the scripture-memory skill, not this one.
- `Learning System/Sessions/`, `Learning System/Reviews/`, `Learning System/Concept Notes/`, `Learning System/Archive/` — writes land here.

## Review flow

Trigger: "swe", "review", or a learning request.

1. Track selection: "swe" → swe table; "aie" → aie table (currently archived — ask the user before unarchiving); neither → ask which track.
2. Load `💡 Learning Profile.md`; read only the relevant track's table from `📚 Active Concepts.md`.
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
2. For each: grep Active Concepts for overlap (same topic, same source, overlapping keywords).
3. Overlap → enrich the existing wiki page + insight row with the genuinely new details; set `last_reviewed` today; write the session note as enrichment (not new ingest).
4. No overlap → new concept: status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`.
5. Outside focus area → ask about switching focus. Stagger schedules for multiple new concepts.
6. Create/update the wiki page; update `Knowledge Wiki/index.md` and `Knowledge Wiki/log.md`; write a session note.
7. Run the learning-review gate (`Skills/learning-review/SKILL.md`): an independent review flags accuracy/clarity/completeness issues with severity; implementer fixes; max 2 cycles; factual web-check on new concepts only. Do not finalize the ingest until the gate reports.

### Handwritten notes

If the source is an image (handwritten notes, photo of a page), transcribe it verbatim before extraction:

- Use a vision-capable model available in Open WebUI to read the image, or ask the user to provide the text.
- Input: the image at {filepath}; transcribe verbatim preserving structure (headings, bullets, diagrams in brackets); light cleanup only (fix obvious spelling, expand unambiguous abbreviations like 'bc' → 'because'); no rephrasing, summarization, or interpretation.
- Retry once on failure; if still failing, tell the user — never silently skip the image.

## End-of-session writes

1. Update Active Concepts — statuses, dates, new concepts, open questions. Preserve existing rows.
2. On `consolidated`: move to `Archive/Consolidated/[concept].md` (name, date, insight, wiki link, related), remove from Active, update Mastery Summary.
3. Write `Sessions/Session — [Topic] — [Date].md` (date, topic, concepts, statuses, open questions) with a one-line interleaving summary, e.g. "Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional".
4. Consistency check: re-read Active Concepts; verify every reviewed concept has today's `last_reviewed`, correct `next_review`, correct `Last Q Type`, all ingested concepts present, wiki pages in index.md, log.md has today's entry. Fix any discrepancy. If the user claims stale dates are wrong, cross-check session notes.
5. Confirm completion — what was saved, what's due next.

## Open WebUI adaptation

- **Source of truth:** this GitHub repo. Load state files from the repo before every flow; keep Open WebUI Notes/Knowledge in sync with the repo, never the other way around.
- **Review gate (ingest step 7):** run the Open WebUI review-gate tool from `Skills/learning-review/openwebui/review_gate.py` (install once in Admin → Workspace → Tools). If it isn't installed, use the in-chat fallback defined in `Skills/learning-review/SKILL.md` (same rules, same template).
- **After writes:** commit and push per `Learning System/AGENTS.md` (now including `Skills/`).
