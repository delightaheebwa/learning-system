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
- Fixed verifier prompts now live in the global `subagents.system_prompt` (keyed by `GATE:`), not in this file. The envelope schemas are in `Skills/learning-review/openwebui/gate_schema.py`; the gate Pipe (`gate_pipe.py`) blocks Clerk output without a receipt. Do not bypass by editing the sysprompt.
- This file's template below is the canonical reference for `GATE:review`; the live prompt is the `GATE:review` section of `subagents.system_prompt`.

### Review prompt template (canonical — lives in subagents.system_prompt as GATE:review)

```
# GATE:review — same as below; subagent fetches SOURCE itself and Pipe checks substring
# See gate_schema.GATEReviewEnvelope: {gate:"review", concepts[], wiki_content, source_url|source_file, lesson_ref, pass_number}
# Verdict: {"verdict":"PASS|ISSUES","issues":[{"severity":"high|medium|low","location":"...","issue":"..."}]}

You are an independent, critical reviewer for a spaced-repetition learning system.
Your job is to catch problems in ingest output. You are a critic, not a rewrite bot:
never rewrite content, only flag issues with severity.

## Inputs

- SOURCE URL: <stable source URL>  OR  SOURCE FILE: <repo path>
- SOURCE CONTENT: <fetched; if empty, review for internal consistency>
- CONCEPTS: <comma-separated concept names>
- WIKI CONTENT: <full text>
- PASS (cycle): <1 or 2>
- LESSON REF: <Lessons/...md when from Tutor handoff>

## Scope / What to check / Rules — as before:
Review ONLY wiki content + Active Concepts rows; check accuracy/correctness, clarity, completeness;
high/medium only; output ONLY valid JSON {"verdict":"PASS|ISSUES","issues":[...]}, PASS only when no high/medium.
```

## Steps

### 1. Determine ingest type

From the session note and Active Concepts changes:

- **New concept** (no overlap existed) → run BOTH gates (quality + factual).
- **Enrichment** (existing concept updated) → quality gate only.

### 2. Quality gate — foreground GATE:review envelope (Pipe-enforced)

Dispatch ONE **foreground** `GATE:review` envelope via `delegate_task` (`background:false`) validated by `gate_pipe.py`:

```json
{"gate":"review","concepts":["Concept"],"wiki_content":"...","source_url":"https://...","lesson_ref":"Lessons/...md","pass_number":1}
```

Use `source_file` instead of `source_url` when the source is a repo file. The Pipe verifies the child chat receipt (foreground, schema, verdict coverage) before the Clerk's final message renders; blocked drafts show `⛔ BLOCKED (<code>)` with fix instructions. Save the returned verdict JSON to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show the result to the user.

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
- Never skip the gates silently. If a gate can't run (e.g. the subagent task fails), say so and surface what was unverified — the Pipe's `⛔ BLOCKED` is the enforcement, not a silent skip.
- The Pipe caps retries at 2 per user turn; after cap the Clerk's output shows `⛔ Withheld` and requires a manual fix.
- Never run this gate on lesson files, learning records, or glossary promotions. Those use foreground `GATE:fact_check` envelopes via `learning-teach`, not this gate; the two verification paths are deliberately separate.

## Manual trigger

Run on demand for an existing ingest: dispatch the same review-gate subagent task with `SOURCE URL`, `CONCEPTS`, and `WIKI CONTENT` pointing at the relevant files, same as step 2.