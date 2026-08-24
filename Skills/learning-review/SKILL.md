---
name: learning-review
description: Quality-gate learning system ingest output before it is finalized — wherever it originates. Runs after every standalone ingest session AND at the end of any teaching lesson that produced wiki pages or Active Concepts rows: a review-gate subagent task (on Open WebUI's subagent default model) flags accuracy, correctness, clarity, and completeness issues with severity; the implementer fixes them; max 2 cycles, then remaining flags surface to the user.
---

# Learning System Review Gate

Verification gate for the learning system's ingest output. Runs automatically:

1. At the end of every standalone **ingest** session (delegated from the learning-system skill).
2. At the end of any **teaching lesson** that wrote wiki pages and/or Active Concepts rows (delegated from the learning-teach skill — see its "Lesson-end ingest gate" step), or on demand.

Scope: **ingest output wherever it originates** — wiki pages, Active Concepts insight rows, question seeds, from both standalone ingests and lesson-end ingests. Review sessions and mechanical date updates are NOT gated.

Lesson files under `Learning System/Lessons/`, learning records, and glossary entries promoted by lessons are verified live by the `learning-teach` skill using batched fact-check subagent tasks during plan/teach, before they reach the user. They do **not** go through this gate. See `Skills/learning-teach/SKILL.md`. The two verification paths are deliberately separate.

## Config

- Reviewer model: Open WebUI's **subagent default model** (Settings → subagents) — always different from the tutor model so the tutor never reviews its own output. To change models, edit that one field in Open WebUI — see the model-per-task table in `OPENWEBUI.md`.
- The gate owns the review prompt below (fixed template). Do not weaken the reviewer by editing the template or switching the subagent model to soften reviews.

### Review prompt template (fixed)

```
# Learning System Review Gate — Review Prompt (fixed template)

You are an independent, critical reviewer for a spaced-repetition learning system.
Your job is to catch problems in ingest output. You are a critic, not a rewrite bot:
never rewrite content, only flag issues with severity.

## Inputs

- SOURCE URL: <stable source URL>
- SOURCE CONTENT: <text fetched from the URL; if it could not be fetched, say so
  and review for internal consistency only>
- CONCEPTS: <comma-separated concept names>
- WIKI CONTENT (the ingest output being reviewed): <full text>
- PASS (cycle): <1 or 2>

## Scope

Review ONLY:
1. The wiki content above.
2. The Active Concepts insight rows / question seeds derived from this ingest.

Mechanical date updates and review session notes are out of scope.

## What to check

1. **Accuracy / correctness** — claims that contradict the source content, wrong mechanisms, wrong formulas or definitions, invented facts.
2. **Clarity** — phrasing that would mislead a learner or is so ambiguous it fails to teach.
3. **Completeness** — load-bearing points from the source that were dropped or misrepresented.

## Rules

- Only flag issues worth fixing. High/medium severity only; low-severity nits get one combined note.
- Each issue: severity (high | medium | low), location (file/section), issue (specific and actionable).
- Material in the wiki content that is NOT present in the source must be flagged as a scope problem unless a scope note explains the addition.
- Output ONLY valid JSON — a single JSON object, no prose before or after:
  {"verdict": "PASS" | "ISSUES", "issues": [{"severity": "high|medium|low", "location": "...", "issue": "..."}]}
- "verdict": "PASS" only when there are no high/medium issues.
```

## Steps

### 1. Determine ingest type

From the session note and Active Concepts changes:

- **New concept** (no overlap existed) → run BOTH gates (quality + factual).
- **Enrichment** (existing concept updated) → quality gate only.

### 2. Quality gate (independent review subagent)

Dispatch ONE review-gate subagent task (`delegate_task`) built from the fixed template above:

- `SOURCE URL` — the stable URL the ingest came from (raw GitHub, course page — never a workspace path). Fetch the source content first (terminal/web) and include it; a dead URL means abort the gate with an error — no verdict.
- `CONCEPTS` — comma-separated concept names.
- `WIKI CONTENT` — the full text of the wiki page(s) you wrote (you already have it from your own writes — do NOT re-read from disk).
- `PASS (cycle)` — the cycle number (1 or 2).

The subagent runs on Open WebUI's subagent default model as the independent reviewer. Save the returned verdict JSON to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show the result to the user.

### 3. Factual gate (new concepts only, same session)

For each NEW concept, spot-check key factual claims with web search. This is a same-session self-audit — the point is "did you check your claims", not a second opinion.

- For each concept insight, identify 1–2 load-bearing factual claims (mechanisms, formulas, definitions).
- Search each against authoritative sources (web search / known references).
- Flag any claim that doesn't match. If search is inconclusive, do NOT flag — note it as unverified for the user instead.

### 4. Fix loop (max 2 cycles)

- If the quality gate returns issues (or factual gate flags claims): fix the wiki/insight/question seeds, then re-run the quality gate ONLY with `PASS (cycle) = 2` and the SAME source, concepts, and wiki content.
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
- Never skip the gates silently. If a gate can't run (e.g. the subagent task fails), say so and surface what was unverified.
- Never run this gate on lesson files, learning records, or glossary promotions. Those use batched fact-check subagent tasks via `learning-teach`, not this gate; the two verification paths are deliberately separate.

## Manual trigger

Run on demand for an existing ingest: dispatch the same review-gate subagent task with `SOURCE URL`, `CONCEPTS`, and `WIKI CONTENT` pointing at the relevant files, same as step 2.