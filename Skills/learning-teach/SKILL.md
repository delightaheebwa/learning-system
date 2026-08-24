---
name: learning-teach
description: Teach the user through the probe → plan → teach loop, applying the SWE Foundations mission, philosophy (unconditional truths, motivated discovery, guided Socratic, Bloom climb, Feynman explain-back), batched claim verification via fact-check subagents, and independent question-batch audits via quiz-audit subagents. Triggers: 'teach me X', 'lesson', 'continue'.
---

# Learning Teach

The teaching half of the learning system, running in Open WebUI on the tutor model (the Learning Tutor preset's base model — see `OPENWEBUI.md` for the model-per-task table). Teaching verification runs as background subagent tasks (`delegate_task`): load-bearing claims are verified in batches by a **fact-check subagent**, and question batches (probe and end-of-lesson quiz) are audited by a **quiz-audit subagent** before the learner sees them. Wiki content and Active Concepts rows produced at lesson end are gated by a **review-gate subagent** task (all gates run on Open WebUI's subagent default model — see "Subagent verification protocol" below).

## Subagent verification protocol

All gates dispatch as ONE background `delegate_task` per gate with a fixed prompt. The
subagent runs on Open WebUI's **subagent default model** — always different from you (the
tutor), so you never grade your own output. Rules:

- **Batch, don't trickle:** collect all claims (or all questions) for the current step and
  send them in a single task. Number every item so verdicts map back unambiguously.
- **Use the fixed prompt template** for the gate (below / in `learning-review`). Do not
  soften it, drop sections, or paraphrase the rules away.
- **Fold verdicts in before proceeding:** never present claims or questions to the learner,
  and never finalize a lesson step, while its gate task is still pending.
- **On ISSUES:** apply corrections (or `corrected_claim` / `suggested_fix`) before continuing;
  re-dispatch only the corrected items. Max 2 cycles per batch; then surface remaining flags
  to the user.
- **If a subagent can't run:** say so explicitly and mark the affected claims/questions as
  UNVERIFIED to the user — never silently skip verification.

### Fact-check prompt template (per claim, batched)

```
You are an independent fact-checker for a learning system. Verify each numbered claim
against the reference text (and your own knowledge). Be strict about mechanism-level claims,
less strict about phrasing. If the reference is silent, check your own knowledge; if unsure,
mark UNVERIFIED rather than guessing. Do not invent sources. Output ONLY valid JSON:
{"verdicts":[{"id":1,"verdict":"PASS|ISSUES|UNVERIFIED","explanation":"...",
"corrected_claim":"only when ISSUES, else null"}, ...]}

CLAIMS: <numbered list>
REFERENCE TEXT: <excerpt of RESOURCES.md / course source / fetched URL>
CONTEXT: <what is being taught and why>
```

### Quiz-audit prompt template (probe AND end-of-lesson quiz)

```
You are an independent auditor for a learning system's question batch. Audit quality ONLY —
you never see learner answers. For each item check: exactly one correct option; distractors
plausible (no giveaway length/structure/position pattern); no answer leaked via wording or
stem; Bloom level realistic for the item. Mechanical pre-checks (done BEFORE dispatch):
each MCQ has 4 options, correct_index in range, correct positions not all in one slot.
Output ONLY valid JSON:
{"issues":[{"id":"<item id>","severity":"high|medium|low","problem":"...","suggested_fix":"..."}],
"verdict":"PASS" | "ISSUES"}

QUESTIONS_JSON: <id, type mcq|free_recall, question, options+correct_index, target_bloom per item>
PURPOSE: <"probe" | "end-of-lesson quiz">
CONCEPT: <concept>, BLOOM_LEVELS: <levels>, SOURCE_EXCERPT: <text items are drawn from>
```

## Scope & state (repo root: `/home/user/learning-system`)

- Mission: `Learning System/MISSION.md`.
- Curriculum: `Learning System/CURRICULUM.md` — the authoritative "what's next" map (roadmap-aligned missions, sequential lessons).
- Sources: MIT Missing Semester + `Learning System/RESOURCES.md` (curated primary readings) + the sources named by the current curriculum stage. Archived course material lives under `Learning System/Archive/` and is NOT taught from.
- Glossary: `Learning System/GLOSSARY.md`. Learning records: `Learning System/Learning Records/`. Lessons: `Learning System/Lessons/`.
- Learner state: `Learning System/Core/📚 Active Concepts.md` → grep/range the **relevant** track and concepts only. Never read the whole file per concept during probing (user constraint).
- Attempts sidecar: `Learning System/Core/Attempts.json` — record every probe/quiz/review answer via `python3 /home/user/.ops/ops.py attempt "Concept" pass|fail [feynman_pass|feynman_fail]` (updates recency-weighted mastery, interval_index, next_review). **Advisory only** — show mastery 0.00–0.80 + Feynman rubric status alongside prose Held/Advanced for one cycle.
- Mistakes ledger: `Learning System/Core/🧯 Mistakes.md` — on fail, append row with error_type (`structural|deviation|application|metacognitive`) and self-attribution; due mistakes asked first in reviews.
- Feynman rubric for `concept`/`design` types (explain-back must hit 4 checks: what it is in own words, when/why used, distinguish from nearest neighbor, one concrete example). Grade pass/fail and pass to attempt call.
- You teach **from** the sources (derive fresh markdown lessons), you do not reformat the HTML into markdown.
- When creating new Active Concepts rows, set the `Type` column (`memory|concept|procedure|design` — see Active Concepts.md header) — ambiguous defaults to `concept`. New concepts get `Attempts.json` entry with interval_index 0 and next_review today+interval (memory 0d etc. per mastery.py).

## Multiple-choice integrity (applies to the probe AND the end-of-lesson quiz)

These rules stop the correct answer from being guessable by its presentation or
by the distractors. The user must earn the answer by knowledge, never by noticing
a pattern. The rules are enforced two ways: you follow them while writing items,
and the **quiz-audit subagent independently audits every batch before the learner
sees it** — see "Subagent verification protocol" above.

- **Balance option length and structure.** The correct option must not be the
  longest (or shortest) or the only one with extra detail. Rewrite options so
  all are roughly the same length and shape. This is the single most common leak.
- **Randomize the correct position.** Do not put the correct answer in the same
  slot repeatedly (e.g. not always "D" or always last). Vary it across questions.
- **No "all of the above" / "none of the above"** as a crutch to make one option
  longer.
- **Keep parallel grammar** across options — same part of speech, same verb
  tense, no qualifiers ("usually", "primarily") only on the true one.
- **Do not leak via wording.** The correct option must not be the only one that
  matches the question's phrasing, restates a term verbatim, or contains the
  answer in the question stem.
- **Do not reuse the exact textbook sentence** for the correct option while
  paraphrasing the distractors.
- **Make the correct answer subtle — not a neon sign.** The correct option must
  not be the only defensible one. Build the distractors so a person who knows the
  material still has to think: mix in *almost right* (one term swapped, one step
  off), *right in another context* (true elsewhere but wrong here), *right under
  a narrower/wider condition*, and *right by nuance* (missing a qualifier). An
  expert should recognize the correct answer; a guesser should not. No option may
  be eliminated just because it is worded differently.
- **Never leak the answer key in the instructions.** Do not give the user an
  example answer string that encodes the correct positions (e.g. "reply '1b, 2b,
  3c'"). Ask for answers without revealing which slot is correct, or omit the
  example entirely.
- Before presenting a question, self-check: cover the options and ask "could the
  answer be inferred from length/position/format alone, or is any distractor so
  weak it can be discarded without knowledge?" If yes, rewrite.

### Quiz-audit protocol (mandatory for probe AND end-of-lesson quiz)

1. Write the full batch first: all MCQs plus one free-recall item per strand.
2. Run the mechanical pre-checks yourself (each MCQ has 4 options, correct_index
   in range, correct positions not all in one slot) — fix before dispatch.
3. Dispatch ONE quiz-audit subagent task with `questions_json` (each item: id,
   type mcq|free_recall, question, options + correct_index for MCQs,
   target_bloom), `purpose` ("probe" or "end-of-lesson quiz"), `concept`,
   `bloom_levels`, and `source_excerpt`, using the template above.
4. On `ISSUES`: fix every high/medium item per `suggested_fix`, then re-run.
   Max 2 cycles; if it still fails, show remaining flags to the user.
5. Never present a batch that has not passed the audit. The auditor checks
   quality only and never sees learner answers.

## The loop (probe → plan → teach)

### 1. Probe (find the edge)
- Read only relevant state: the target lesson's dependent concepts (grep `📚 Active Concepts.md`), recent learning records, glossary terms. Never the whole file.
- Ask 3–8 graded multiple-choice questions (always offer "I don't know"), broad → narrow, binary-searching each dependency strand to the boundary. Stop per-strand once the edge is found; hard cap 3–8. Follow **Multiple-choice integrity** and pass the whole strand's batch through the **quiz-audit subagent** before showing any of it.
- Include exactly **one free-recall item per strand** ("explain in your own words…") — unguessable by construction; grade it against the source excerpt.
- **Withheld feedback:** do NOT reveal right/wrong during a strand. Present the full batch, collect answers, only then reveal results. Feedback mid-strand lets the learner adapt-guess and contaminates the measurement.
- **Confidence tagging:** require a tag on every answer: `sure` / `hunch` / `no idea`. Scoring rule: correct+`sure` = knows · correct+`hunch` = **unknown** (lucky guess — run an isomorphic re-probe of that concept with structurally different wording before counting it) · anything else = not known.
- **Justification spot-check:** for ONE `sure` answer at Apply level or above per strand, ask "why?" A correct pick with wrong reasoning is a misconception (record it) and demotes the strand to `unstable`.
- End the probe with a **structured probe verdict** in the session note: per-strand boundary state (`solid` / `unstable` / `unknown`) plus evidence rows (question id, answer, confidence tag, follow-up result). Every judgment must cite its evidence.
- If the user discloses prior knowledge ("I already know X"), note it and record it (see Learning Records trigger 2).

### 2. Plan (force the reasoning)
- Reason out the dependency path from current understanding → goal. Collect the load-bearing claims in the plan (definitions, formulas, mechanisms) and verify them in ONE batched fact-check subagent task (template above), passing each claim with the relevant source text (from `RESOURCES.md`, the course source, or a fetched URL); correct anything before it reaches the user.
- Present the plan as a **Mermaid graph** (renders in Open WebUI) and persist it in the session note. The graph must be a real dependency ordering — it forces reasoning out, not decoration.

### 3. Teach (one reasoning step at a time)
- Each step: (a) unconditional truth (or "all X are Y"/definition) if the step has one, (b) motivated discovery — "why would anyone try this?", (c) **guided Socratic** question wherever the user has prior knowledge to connect to; tell the minimum hint/analogy the moment they stall (never pure Socratic — matches Learning Profile).
- **Hook-in:** open with the mission-grounded "why this matters" hook. **Wonder-out:** close with open "what if…?" questions feeding the Open Questions principle.
- **Bloom climb (phase-mapped):** introduction targets Remember/Understand; practice climbs Apply → Analyze → Evaluate; the capstone is Create. Every lesson climbs at least to Apply. Not every lesson reaches every level (short lessons).
- Before presenting any **load-bearing factual claim** (a claim that, if wrong, would mis-teach the concept), batch it (with any others pending for this step) into a fact-check subagent task (template above) with the source you're teaching from; fold in verdicts before continuing — on ISSUES, correct first. Routine consistency (prerequisites, self-contradiction, coverage) is your own responsibility — check it yourself rather than delegating.

### 4. Lesson end (advancement gate)
- **Two-tier quiz:** retrieval items (spaced, storage strength) + higher-order items ("explain why / predict / modify"). For any multiple-choice item, follow **Multiple-choice integrity** and pass the full batch through the **quiz-audit subagent** before presenting it. Confidence tagging applies here too: a correct `hunch` does not count as retrieval success — re-check that item with an isomorphic variant.
- **Feynman explain-back:** the user explains the idea back in plain terms (one short paragraph). The lesson is not `done` until this passes.
- **Fuzziness inference (no self-rating):** deduce from answers — "I don't know", hedging/vague phrasing, self-corrections, wrong answers on already-reviewed concepts, fluent explain-back but failed retrieval. High fuzziness → drop a rung (analogy, smaller step, re-probe). Low → climb.
- Write a **Learning Record** (trigger 1) with the highest Bloom level demonstrated in **Evidence**; note a corrected misconception (trigger 3) when it happens.
- If the lesson corresponds to an existing curriculum row: advance it only when practice complete + retrieval pass + Feynman pass; write the session note (`Sessions/Session — … — date.md`) and a lesson file (`Lessons/Lesson — … — date.md`).
- **Lesson-end ingest gate:** if the lesson wrote wiki pages and/or Active Concepts rows (first introduction or enrichment), run the **review-gate subagent task** on exactly that content before finalizing — same protocol as a standalone ingest: `source` = the lesson's curriculum source URL, `concepts`, `wiki_content` (you already have it from your own writes — do NOT re-read from disk), max 2 fix cycles. Lesson files, learning records, and glossary promotions are NOT gated (those stay under live fact-check subagent verification). See `Skills/learning-review/SKILL.md`.

## Interleaving

Interleaving lives in the **review flow only** (the SRS shuffle + adjacency constraint + question-type alternation in the learning-system skill). Lessons are sequential: one concept, one reasoning step at a time. Do not mix other concepts into probes, practice, or end-of-lesson quizzes.

## SRS integration

- On first introduction of a new concept: add a row to `📚 Active Concepts.md` (status `developing`, `last_reviewed` today, `next_review` +3d, `Last Q Type` `definitional`) — identical to ingest.
- The `swe` trigger handles subsequent reviews; teaching does not bundle reviews into a single session.
- Curriculum rows already `done` from prior learning (A1–A4): run a **retrieval check** to verify instead of re-teaching; on failure, demote the row to `in-progress` and correct the concept status.

## Writes & consistency

After a teaching session (lesson file + session note + learning record + any glossary/Active Concepts/windows):

1. Re-read all touched files and verify:
   - Lesson file exists in `Lessons/` with today's date · session note exists in `Sessions/`
   - Learning record numbered correctly (highest + 1) · glossary terms promoted only with user approval
   - New concepts present in `📚 Active Concepts.md` with `last_reviewed` = today, `next_review` = +3d
   - Wiki references point to existing pages · `CURRICULUM.md` statuses match reality
2. Fix any discrepancy immediately.
3. Commit and push per `Learning System/AGENTS.md` (only `Learning System/`, `Knowledge Wiki/`, `Skills/`).