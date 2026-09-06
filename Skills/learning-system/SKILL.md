---
name: learning-system
description: Run the spaced-repetition learning system in Open WebUI. Triggers — "review" (review the AIEFS track), "ingest" (ingest new content), "teach me X"/"learn"/"study" (teaching loop, delegated to the learning-teach skill), "lesson"/"continue" (next curriculum lesson, delegated to learning-teach). Loads the Core state files from the repo at /home/user/learning-system, executes the review/ingest/teach flow, and persists session notes, wiki updates, and Active Concepts changes. Active roadmap is AI Engineering from Scratch (Rohit); SWE is archived.
---

# Learning System

The active learning system, running in Open WebUI against the repo at `/home/user/learning-system` (Open Terminal workspace). Trigger by saying a track ("swe"), "ingest", a learning intent, or "lesson"/"continue" for the next curriculum lesson.

**Trigger routing (read first):**
- **"review" → review flow** on the AIEFS track (SWE `swe` is archived — redirect to AIEFS if requested).
- **"teach me X" / "learn" / "study" → teaching loop** — `Skills/learning-teach/SKILL.md`, NOT a review. "review" alone means the review flow.
- **"lesson" / "continue" → next curriculum lesson** — `Skills/learning-teach/SKILL.md` (Rohit roadmap order; Mission 0 Catch-Up 80/20 first, then Phase 1 L07).

## Context discipline (hard rules — read first)

Sessions die when the running conversation outgrows the model's context window: cutoffs hit mid-flow (~20 tool calls) because every tool output stays in the transcript forever. The fix is fewer, denser tool calls — not smaller messages.

- **Batch all reads.** Never chain multiple full-file `read_file` calls for state. Use the batch tool ONCE instead (`run_command`, paths are repo-root-relative):
  - Session start: `python3 scripts/ops.py state <track>`
  - Any mix of ranges/tails/greps: `python3 scripts/ops.py bundle "PATH:N-M" "PATH:-N" "PATH@regex1|regex2"`
- **Read wiki pages by section.** First `bundle "Knowledge Wiki/wiki/<page>.md@^## "` to list its headings, then fetch only the section you actually enrich.
- **Batch all writes.** Persistence at session end = ONE apply call, not N `write_file` calls:
  `python3 scripts/ops.py apply <<'SPEC'` then a JSON spec, then `SPEC`.
  Spec: `{"writes":[{"path","content"}],"appends":[{path,content}],"replaces":[{"path","find","replace_with"}]}`.
- Target **≤12 tool calls per flow**. Never re-read a file already in context. Never dump whole files you only need one row of.

## State files (repo root: `/home/user/learning-system`)

- `Learning System/Core/💡 Learning Profile.md` — learner preferences. Read at session start.
- `Learning System/Core/📚 Active Concepts.md` — per-track concept rows (now **aiefs** active; swe archived 2026-09-01) with `Type` column (`memory | concept | procedure | design`). Type drives scheduler intervals. Grep/range only the needed track — never the whole file; `📦 Concept Archive.md` is strictly out of scope.
- `Learning System/Core/Attempts.json` — evidence-based mastery sidecar (attempt history, interval_index state machine, Feynman pass). Bundled by `ops.py state`; report via `ops.py mastery <track>` — **advisory only** (scores shown, not blocking).
- `Learning System/Core/🧯 Mistakes.md` — structured wrong-answer ledger (error_type + self-attribution). Due mistakes are priority-1 in review queue.
- `Learning System/Core/📦 Concept Archive.md` — paused/archived concepts (SWE archived 2026-09-01). **Do not grep** — strictly out of scope per user decision. Search only on explicit revive request.
- `Learning System/Sessions/`, `Learning System/Reviews/`, `Learning System/Concept Notes/`, `Learning System/Archive/` — writes land here.
- `Learning System/MISSION.md`, `Learning System/CURRICULUM.md`, `Learning System/GLOSSARY.md`, `Learning System/RESOURCES.md` — mission, curriculum, glossary, curated readings (AIEFS; Rohit is a source, not the source).

## Teaching flow (delegation) — Scout → Tutor → Clerk

Trigger: "teach me X", "lesson", or "continue". The pipeline runs in the **same chat**, switching presets.

0. **Scout (if new lesson):** if no `Lessons/Lesson — <slug> — *.md` exists for the requested topic/lesson and no `.tmp/context-<chat_id>-<slug>.json` (7-day TTL) is present, switch to the **Scout** preset first. Scout reads `MISSION.md`, `CURRICULUM.md`, `RESOURCES.md`, relevant Active Concepts rows, **and the curriculum source for the next lesson — `phases/<phase>/<lesson>/docs/en.md` plus every URL in its `## Further Reading`** (Rohit is a source, not the source; see `RESOURCES.md`). Per-URL fetch loop (terminal first, in order, one command per URL — stop at first success): (a) direct `curl -L --max-time 30` into `.tmp/`; (b) PDFs → extract with `python3 -c "import pypdf"` (no pdftotext in sandbox; on 404 try one obvious mirror, then move on); (c) YouTube → `yt-dlp --skip-download --write-auto-subs` transcript, never page-fetch; (d) bot-blocked HTML → `curl https://r.jina.ai/<url>` (no key); (e) Web Search snippet last. Hash with `sha256sum`, compare to prior digest hash if present, surface drift (`SCOUT DIGEST: ⚠️ Upstream changed`), and write `Learning System/.tmp/context-<chat_id>-<slug>.json` with `{goal, slug, tracks, concept_rows, prereqs, source_refs:[rohit_source, ...external_refs], rohit_hash, external_refs_hashes, failed_refs:[{url, reason}], lang_recommendation, fetched_at, roadmap_sha, synthesis}` (every source/external ref entry carries `excerpt` ~500 chars + `takeaways` + `adds_vs_rohit`; Rohit = agenda, externals = enrichment) + post `SCOUT DIGEST:` (headings + 3–5 bullet synthesis of FETCHED refs vs Rohit + failed_refs list when non-empty — never synthesize unfetched sources; record the failure and continue). `prereqs` is load-bearing for the Tutor: `[{concept, keywords:[aliases/variants], why}]` covering every load-bearing dependency of the lesson, with keywords spanning notation + plain-language variants (e.g. `{concept:"conditional probability", keywords:["P(A|B)","posterior","joint|marginal"], why:"..."}`). Language per lesson header (`Languages:`) decides `lang_recommendation` (Python / TypeScript / Rust; Julia optional). No caching layer is used (decision 2026-09-01 — live fetch each lesson). The Tutor's gate Pipe requires this digest for new lessons (resume of an existing `Lessons/` file bypasses the check). **Adaptive rule:** before each new lesson, Scout re-fetches the live docs + Further Reading and checks for change; Tutor prefers the live combined sources over parametric memory. `📦 Concept Archive.md` is strictly out of scope — do not grep it.
1. Load `Learning System/MISSION.md` + `Learning System/CURRICULUM.md` to determine the next lesson (or the requested topic). Order: **Mission 0 Catch-Up (P0+P1.01–06, 80/20, `in-progress`) is first**; after it passes, next is **Phase 1, Lesson 07 — Bayes' Theorem** (decision 2026-09-01 — jump). If resuming (`Lessons/` file exists), the lesson file + last `Sessions/` note are the source of truth — no Scout digest needed.
2. **`lesson`/`continue`:** pick the next lesson per `CURRICULUM.md`'s current mission (strictly sequential order); Mission 0 → Phase 1 L07 → Phase 1 L08 … → Phase 19. If the lesson is resumable (mid-lesson state exists), resume where left off. A `done` lesson is never re-taught — retrieval-verify instead. `not-started*` rows (Phase 0, Phase 1 L01–L06) are covered by the catch-up — retrieval-check on demand, not re-taught.
3. **`teach me X`:** in current-mission scope → treat as a curriculum node (add/route it); out of scope → one-off that still feeds Pending Ingest for Clerk, and surface the "switching focus?" question. For AIEFS, scope = `CURRICULUM.md` 20-phase map; map is navigational, not contractual — after each phase, decide to go deeper / branch.
4. Delegate the full probe → plan → teach loop to the `learning-teach` skill. Claim verification runs via **foreground** `GATE:fact_check` envelopes (gate_pipe) citing **both** `rohit_source` and `external_refs` URLs; question batches are audited via `GATE:quiz_audit` envelopes before showing. The Tutor **does not** write wiki pages/Active Concepts rows — it writes `Learning System/Core/Pending Ingest.json` and hands off to **Clerk** at lesson end (see `learning-teach`). Build language follows `lang_recommendation` (per-lesson Rohit header), not a default.

## Review flow

Trigger: "review" (AIEFS). `swe` is archived — redirect to AIEFS.

1. Track selection: `aiefs` / `aie` → AIEFS table (active — Mission 0 catch-up + Phases 0–19). `swe` is archived 2026-09-01 (do not revive without explicit request); if user says "swe", note it is archived and offer AIEFS. Neither → assume AIEFS.
2. Session start — ONE call: `run_command` → `python3 scripts/ops.py state <track>`. This now returns Learning Profile + your track's Active Concepts rows + Attempts.json (advisory mastery scores) + 🧯 Mistakes.md. Do not read those files separately.
3. Build the queue:
   - Slots 1–2 = due mistakes from `🧯 Mistakes.md` where Next Retry ≤ today (`active`/`review`), oldest first (priority-1, DeepTutor pattern).
   - Remaining 3 slots = type-aware due reviews (Next Review ≤ today), shuffled. Adjacency constraint: no two consecutive concepts from the same Source (if impossible, shuffle anyway).
4. Per concept: one question, one answer (≤1 line), targeting the 20% insight worth 80%. Math (paper accommodation): ask for the final result computed on paper — e.g., "Work on paper, reply with just the final number / chosen letter (A–D)." Never require typing full LaTeX/formulas verbatim into the chat box. Correct final answer validates formula recall — do not skip math concepts.
5. Question type alternation by Last Q Type: blank/definitional → discriminative; discriminative → definitional.
6. After each answer: grade pass/fail, then verify the grade with ONE **foreground** `GATE:grade_audit` envelope via `delegate_task` (`background:false`) before presenting it — batch per concept (`{"gate":"grade_audit","concept","question","learner_answer","claimed_verdict":"pass|fail","source_excerpt"}` with a Concept Note / Lesson / Wiki excerpt fetched via `bundle`; include `feynman_transcript` for `concept`/`design` explain-backs). The gate Pipe (`gate_pipe.py`) validates the receipt before the Tutor's grade renders (retry cap 2/turn → `⛔ Withheld`). If the verifier disagrees (`correct_verdict` differs), use its verdict. Then record via `python3 scripts/ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail]` — this updates Attempts.json (recency-weighted mastery 0–1, confidence cap {1:0.5, 2:0.8}, interval_index +1 on pass / +2 on 2 consecutive passes / -1 on fail, next_review). On fail also append row to `🧯 Mistakes.md` with error_type (`structural|deviation|application|metacognitive`) and self-attribution; on next correct recall bump Retries, after 2 consecutive correct mark `graduated`. For `concept`/`design` types, elicit Feynman explain-back (own words, when/why, nearest-neighbor distinction, one example) and pass `feynman_pass`/`feynman_fail` — score shown but **not blocking** (advisory mode). Then write `Reviews/Review — [Concept] — [Date].md` and update Active Concepts `last_reviewed`/`next_review` (from Attempts.json) / `Last Q Type`.
7. Cap 5. Then ask "Any you want to dig deeper on?" — if yes, deep-dive one concept.
8. Surface open questions from Active Concepts. Also surface advisory mastery line for each concept (e.g. `mastery 0.50 — Feynman: —`) alongside Held/Advanced note for calibration.

Intervals (type-aware, from `mastery.py`): memory [0d,1d,3d,7d,14d,30d,60d] · concept [3d,7d,14d,30d] · procedure [3d,7d,14d] · design [14d,28d]. Mastery (advisory): memory/procedure ≥0.9 quantitative; concept/design require Feynman pass — display mastery 0.00–0.80 etc. alongside Held/Advanced for one review cycle, then gate becomes blocking.

## Ingest flow — via Clerk (handoffs from Tutor and standalone `/ingest`)

Trigger: "ingest" with content to add (NOT a review). **Run on the Clerk preset** (reads `Pending Ingest.json` when the ingest originates from a lesson). Standalone `/ingest` also routes to Clerk.

1. If `Learning System/Core/Pending Ingest.json` exists (lesson handoff), read it — it contains `{lesson_file, session_file, concepts, source_url|source_file, created_at}`. Use `lesson_file` as the source of content to ingest.
2. Otherwise extract concepts from the supplied content.
3. Overlap check — ONE bundle call with an alternation regex over candidate keywords: `python3 scripts/ops.py bundle "Learning System/Core/📚 Active Concepts.md@kw1|kw2|kw3"` (or `#^## <track>` to pull the full track section). No separate grep/read calls per keyword.
4. Overlap → enrich the existing wiki page + insight row with the genuinely new details; set `last_reviewed` today; write the session note as enrichment (not new ingest). Read only the target page's relevant section (headings first via `@^## `).
5. No overlap → new concept: status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`.
6. Outside focus area → ask about switching focus. Stagger schedules for multiple new concepts.
7. Persist EVERYTHING in one apply call (`ops.py apply` heredoc): wiki page(s), index.md update, log.md entry, session note. Do not interleave write_file calls between reasoning steps.
8. Dispatch ONE **foreground** `GATE:review` envelope via `delegate_task` on the wiki content you just wrote (you already have it from your own writes — do NOT re-read). The gate Pipe (`gate_pipe.py`) validates the receipt before the Clerk's final message renders. Pass `lesson_ref` when from a lesson. Fix flagged issues (one more apply call); max 2 cycles; then: if `Pending Ingest.json` has `partial:true` (a `/pause` handoff), ingest today's concepts and KEEP both the `.tmp/context-*.json` digest and the lesson `in-progress` (clear only the marker, commit + push) — the digest's 7-day TTL still applies. Only a final (non-partial) ingest deletes the consumed digest, clears the marker, and lets the curriculum row go `done`.

### Handwritten notes

If the source is an image (handwritten notes, photo of a page), transcribe it verbatim before extraction:

- Use a vision-capable model available in Open WebUI to read the image, or ask the user to provide the text.
- Input: the image at {filepath}; transcribe verbatim preserving structure (headings, bullets, diagrams in brackets); light cleanup only (fix obvious spelling, expand unambiguous abbreviations like 'bc' → 'because'); no rephrasing, summarization, or interpretation.
- Retry once on failure; if still failing, tell the user — never silently skip the image.

## End-of-session writes

1. Update Active Concepts — statuses, dates, new concepts, open questions. Preserve existing rows.
2. On `consolidated`: move to `Archive/Consolidated/[concept].md` (name, date, insight, wiki link, related), remove from Active, update Mastery Summary.
3. Write `Sessions/Session — [Topic] — [Date].md` (date, topic, concepts, statuses, open questions) with a one-line interleaving summary, e.g. "Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional".
4. Consistency check — ONE bundle call re-grepping only the touched rows: `python3 scripts/ops.py bundle "Learning System/Core/📚 Active Concepts.md@<concept1>|<concept2>" "Knowledge Wiki/index.md@<title>" "Knowledge Wiki/log.md:-3"`; verify today's `last_reviewed`, correct `next_review`, `Last Q Type`, all ingested concepts present, wiki pages in index.md, log entry present. Fix discrepancies in a single apply call. If the user claims stale dates are wrong, cross-check session notes.
5. Confirm completion — what was saved, what's due next.

## Open WebUI adaptation

- **Source of truth:** this GitHub repo. Load state files from the repo (`/home/user/learning-system` — `host.docker.internal:3000` from WSL when Docker Desktop runs Windows-side, separate from WSL; `/home/user/learning-system` in container vs `/home/delinux/learning-system` in WSL) before every flow; keep Open WebUI mirror content in sync with the repo, never the other way around.
- **Pipeline presets:** `Scout` → `Tutor` → `Clerk` in the same chat (switch preset per message). Scout writes the ephemeral digest (now includes `rohit_hash` + `external_refs` + `lang_recommendation` + `roadmap_sha`; adaptive re-fetch, Further Reading synthesis; `📦 Concept Archive.md` strictly out of scope); Tutor teaches; Clerk ingests. See `OPENWEBUI.md`.
- **Gate Pipe:** `Skills/learning-review/openwebui/gate_pipe.py` (Filter, inlet/outlet) blocks Tutor/Clerk output without valid foreground `GATE:*` receipts and enforces Scout digest for new lessons (7-day TTL). Fixed verifier wording lives in global `subagents.system_prompt` — send data only.
- **Review gate (Clerk):** dispatch ONE foreground `GATE:review` envelope on the wiki content you wrote. Applies to handoffs from Tutor and standalone `/ingest`.
- **Teaching verification (Tutor):** batch load-bearing claims into foreground `GATE:fact_check` envelopes (cite both `rohit_source` and `external_refs`) before presenting them; fold verdicts in before continuing. Build language follows the lesson's Rohit header.
- **Review grading (Tutor):** verify each pass/fail with a foreground `GATE:grade_audit` envelope (concept/question/learner_answer/claimed_verdict/source_excerpt) before presenting the grade; fold the verdict in before `ops.py attempt`.
- **After writes:** commit and push per `Learning System/AGENTS.md` (paths: `/home/user/learning-system`).