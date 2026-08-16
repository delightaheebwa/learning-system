---
name: learning-review
description: "Quality-gate and fact-check learning system ingest output before it is finalized. Runs after every ingest session: an independent review agent (configurable model) flags accuracy, correctness, clarity, and completeness issues with severity; the implementer fixes them; max 2 cycles, then remaining flags surface to the user. Verification gate for learning system ingest output. Does NOT gate teaching artifacts — those are verified live by the learning-teach skill (background fact-checking)."
compatibility: Open WebUI (self-hosted)
metadata:
  author: delight
  home: https://github.com/delightaheebwa/learning-system
---

# Learning System Review Gate

Verification gate for the learning system. Runs automatically at the end of every **ingest** session (delegated from the Learning System rule), or on demand.

Scope: **ingest outputs only** — wiki pages, Active Concepts insight rows, question seeds. Review sessions, mechanical date updates, and **teaching artifacts** are NOT gated.

Teaching artifacts (lesson files under `Learning System/Lessons/`, learning records, glossary entries promoted by lessons) are verified **live, in-stream** by the `learning-teach` skill — a background sub-agent fact-checks claims during plan/teach against `RESOURCES.md` + web, before they reach the user. They do **not** go through this gate. See `Skills/learning-teach/SKILL.md`.

## Config

`model-config.json` in this skill's directory:

```json
{
  "review_model": "your-openwebui-model-id",
  "api_base": "http://localhost:3000/api/chat/completions",
  "api_key_env": "OPENWEBUI_API_KEY"
}
```

- `review_model` — the Open WebUI model id used for reviews (any model your instance can serve).
- `api_base` — your Open WebUI chat-completions endpoint.
- `api_key_env` — environment variable holding the API key for that endpoint (create one in Admin Panel → API Keys).
- You (the implementer) must NOT edit the config to weaken the reviewer, and must NOT write or alter the review prompt — the gate owns the prompt (`templates/review.template.md`, mirrored inside the tool).

## Steps

### 1. Determine ingest type

From the session note and Active Concepts changes:

- **New concept** (no overlap existed) → run BOTH gates (quality + factual).
- **Enrichment** (existing concept updated) → quality gate only.

### 2. Quality gate (always, independent review agent)

Call the **terminal CLI runner** (`Skills/learning-review/openwebui/gate_cli.py`), which fetches the source, reads the wiki files, and calls a SECOND model (Mimo v2.5 by default) in Open WebUI — the reviewer is genuinely independent of the chat model. Pass ONLY the source URL, concept names, and the file paths you wrote:

```bash
python3 Skills/learning-review/openwebui/gate_cli.py \
  --source "<source URL the ingest came from>" \
  --concepts "Concept One,Concept Two" \
  --wiki "Knowledge Wiki/wiki/Concept One.md,Knowledge Wiki/wiki/Concept Two.md" \
  --model "mimo-v2.5" \
  --base-url "http://host.docker.internal:3000" \
  --pass-number 1
```

- The API key is read from the env var `OPENWEBUI_API_KEY` or `~/.config/learning-system/openwebui_key` (0600) — never passed on the command line.
- The runner validates that every wiki path exists BEFORE calling the review model. If a path is wrong, it fails fast (exit 2) — fix the path and re-run. Never pass a path you have not actually written.
- It fetches `source` itself; a dead URL aborts the review (exit 2, no verdict written). Use a stable URL (raw GitHub, course page), not a workspace path.
- The verdict JSON is printed to stdout. Save it to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show the result to the user.
- `--pass-number` is the cycle number (1 or 2) — it goes into the filename only; it does NOT soften the review. Exit code: 0 = PASS, 1 = ISSUES, 2 = error.

**In-chat fallback (CLI unavailable):** the implementer acts as the independent reviewer using the fixed template in `templates/review.template.md` against the fetched source text and the wiki text, then reports issues with severity. Same rules below, same 2-cycle cap.

### 3. Factual gate (new concepts only, same session)

For each NEW concept, spot-check key factual claims with web search. This is a same-session self-audit, not a child call — the point is "did you check your claims", not a second opinion.

- For each concept insight, identify 1–2 load-bearing factual claims (mechanisms, formulas, definitions).
- Search each against authoritative sources (web search / known references).
- Flag any claim that doesn't match. If search is inconclusive, do NOT flag — note it as unverified for the user instead.

### 4. Fix loop (max 2 cycles)

- If the quality gate returns issues (or factual gate flags claims): the implementer fixes the wiki/insight/question seeds, then re-runs the quality gate ONLY with `pass_number = 2` and the SAME `source`, `concepts`, `wiki_paths` values.
- Cap: **2 cycles total.** After cycle 2, anything still flagged gets surfaced to the user — no third LLM pass.
- The reviewer never rewrites content. The implementer owns final wording.

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
- Never run this gate on teaching artifacts. Teaching uses live background fact-checking (`learning-teach`), not this Mimo gate; the two verification paths are deliberately separate.

## Manual trigger

Run on demand for an existing ingest: call the same tool with `source`, `concepts`, and `wiki_paths` pointing at the relevant files, same as step 2.
