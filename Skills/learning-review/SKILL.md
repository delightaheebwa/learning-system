---
name: learning-review
description: Quality-gate learning system ingest output before it is finalized — wherever it originates. Runs after every standalone ingest session AND at the end of any teaching lesson that produced wiki pages or Active Concepts rows: the review_gate tool calls an independent review model (set on the tool's Valve) that flags accuracy, correctness, clarity, and completeness issues with severity; the implementer fixes them; max 2 cycles, then remaining flags surface to the user.
---

# Learning System Review Gate

Verification gate for the learning system's ingest output. Runs automatically:

1. At the end of every standalone **ingest** session (delegated from the learning-system skill).
2. At the end of any **teaching lesson** that wrote wiki pages and/or Active Concepts rows (delegated from the learning-teach skill — see its "Lesson-end ingest gate" step), or on demand.

Scope: **ingest output wherever it originates** — wiki pages, Active Concepts insight rows, question seeds, from both standalone ingests and lesson-end ingests. Review sessions and mechanical date updates are NOT gated.

Lesson files under `Learning System/Lessons/`, learning records, and glossary entries promoted by lessons are verified live by the `learning-teach` skill using the `fact_check` tool during plan/teach, before they reach the user. They do **not** go through this gate. See `Skills/learning-teach/SKILL.md`. The two verification paths are deliberately separate.

## Config

- Review model: set as the `review_model` Valve on the `review_gate` tool. To change models, edit that one field in Open WebUI (Workspace → Tools → review_gate → ⚙ Valves) — see the model-per-task table in `OPENWEBUI.md`.
- The gate owns the review prompt. Do not weaken the reviewer by editing the prompt or the model valve to soften reviews.

## Steps

### 1. Determine ingest type

From the session note and Active Concepts changes:

- **New concept** (no overlap existed) → run BOTH gates (quality + factual).
- **Enrichment** (existing concept updated) → quality gate only.

### 2. Quality gate (independent review model)

Call the **`review_gate` tool** with:

- `source` — the stable URL the ingest came from (raw GitHub, course page — never a workspace path).
- `concepts` — comma-separated concept names.
- `wiki_content` — the full text of the wiki page(s) you wrote, read via the terminal.
- `pass_number` — the cycle number (1 or 2). Filename only; it does NOT soften the review.

The tool fetches the source itself (a dead URL aborts with an error — no verdict), builds the fixed review prompt, and calls the Valve-configured reviewer model in Open WebUI as the independent reviewer. Save the returned verdict JSON to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show the result to the user.

### 3. Factual gate (new concepts only, same session)

For each NEW concept, spot-check key factual claims with web search. This is a same-session self-audit — the point is "did you check your claims", not a second opinion.

- For each concept insight, identify 1–2 load-bearing factual claims (mechanisms, formulas, definitions).
- Search each against authoritative sources (web search / known references).
- Flag any claim that doesn't match. If search is inconclusive, do NOT flag — note it as unverified for the user instead.

### 4. Fix loop (max 2 cycles)

- If the quality gate returns issues (or factual gate flags claims): fix the wiki/insight/question seeds, then re-run the quality gate ONLY with `pass_number = 2` and the SAME `source`, `concepts`, `wiki_content` values.
- Cap: **2 cycles total.** After cycle 2, anything still flagged gets surfaced to the user — no third LLM pass.
- The reviewer never rewrites content. You own final wording.

### 5. Report

Tell the user concisely:

- Gate result per concept (passed after N cycles / flags remaining), with the verdict file path(s)
- What was fixed
- Anything unverified or still flagged (with the specifics)

## Rules

- Only flag issues worth fixing. High/medium severity only; low-severity nits get one combined note.
- Reviewer is a critic, not a rewrite bot.
- Hard stop after 2 cycles. Remaining flags go to the user, always.
- Factual gate runs on new concepts only — enrichments have survived at least one human review.
- Never skip the gates silently. If a gate can't run (e.g. tool call fails), say so and surface what was unverified.
- Never run this gate on lesson files, learning records, or glossary promotions. Those use the `fact_check` tool via `learning-teach`, not this gate; the two verification paths are deliberately separate.

## Manual trigger

Run on demand for an existing ingest: call the same tool with `source`, `concepts`, and `wiki_content` pointing at the relevant files, same as step 2.