---
name: learning-teach
description: "Teach the user through the probe → plan → teach loop, applying the SWE Foundations (Stage 0) mission, philosophy (unconditional truths, motivated discovery, guided Socratic, Bloom climb, Feynman explain-back, automatic interleaving), and the review-free live fact-checking rule. Triggers: 'teach me X', 'lesson', 'continue'."
compatibility: Open WebUI (self-hosted)
metadata:
  author: Delight Aheebwa
  home: https://github.com/delightaheebwa/learning-system
---

# Learning Teach

The teaching half of the learning system. Runs on whatever model the user picked in the picker that day — never hardcode a model id; the gate model (review) is separately configured in `learning-review`.

## Scope & state

- Mission: `Learning System/MISSION.md` (Stage 0 — SWE Foundations).
- Curriculum: `Learning System/CURRICULUM.md` — the authoritative "what's next" map (two strands, deterministic rotation, colors as labels).
- Sources: `Learning System/Curriculum/sources/terminal-system-monitor/` (immutable HTML course) + MIT Missing Semester + `Learning System/RESOURCES.md` (curated primary readings).
- Glossary: `Learning System/GLOSSARY.md`. Learning records: `Learning System/Learning Records/`. Lessons: `Learning System/Lessons/`.
- Learner state: `Learning System/Core/📚 Active Concepts.md` → grep/range the **relevant** track and concepts only. Never read the whole file per concept during probing (user constraint).
- You teach **from** the sources (derive fresh markdown lessons), you do not reformat the HTML into markdown.

## The loop (probe → plan → teach)

### 1. Probe (find the edge)
- Read only relevant state: the target lesson's dependent concepts (grep `📚 Active Concepts.md`), recent learning records, glossary terms. Never the whole file.
- Ask 3–8 graded multiple-choice questions (always offer "I don't know"), broad → narrow, binary-searching each dependency strand to the boundary. Stop per-strand once the edge is found; hard cap 3–8.
- If the user discloses prior knowledge ("I already know X"), note it and record it (see Learning Records trigger 2).

### 2. Plan (force the reasoning)
- Reason out the dependency path from current understanding → goal. Fire a **background fact-check sub-agent** (`deepseek-v4-flash`) against RESOURCES.md + web; correct anything before it reaches the user.
- Present the plan as a **Mermaid graph** (renders in Open WebUI) and persist it in the session note. The graph must be a real dependency ordering — it forces reasoning out, not decoration.

### 3. Teach (one reasoning step at a time)
- Each step: (a) unconditional truth (or "all X are Y"/definition) if the step has one, (b) motivated discovery — "why would anyone try this?", (c) **guided Socratic** question wherever the user has prior knowledge to connect to; tell the minimum hint/analogy the moment they stall (never pure Socratic — matches Learning Profile).
- **Hook-in:** open with the mission-grounded "why this matters" hook. **Wonder-out:** close with open "what if…?" questions feeding the Open Questions principle.
- **Bloom climb (phase-mapped):** introduction targets Remember/Understand; practice climbs Apply → Analyze → Evaluate; the capstone is Create. Every lesson climbs at least to Apply. Not every lesson reaches every level (short lessons).
- Live background fact-checking runs during planning and teach; the Mimo review gate is **ingest-only** (do not invoke it on teaching artifacts).

### 4. Lesson end (advancement gate)
- **Two-tier quiz:** retrieval items (spaced, storage strength) + higher-order items ("explain why / predict / modify").
- **Feynman explain-back:** the user explains the idea back in plain terms (one short paragraph). The lesson is not `done` until this passes.
- **Fuzziness inference (no self-rating):** deduce from answers — "I don't know", hedging/vague phrasing, self-corrections, wrong answers on already-reviewed concepts, fluent explain-back but failed retrieval. High fuzziness → drop a rung (analogy, smaller step, re-probe). Low → climb.
- Write a **Learning Record** (trigger 1) with the highest Bloom level demonstrated in **Evidence**; note a corrected misconception (trigger 3) when it happens.
- If the lesson corresponds to an existing curriculum row: advance it only when practice complete + retrieval pass + Feynman pass; write the session note (`Sessions/Session — … — date.md`) and a lesson file (`Lessons/Lesson — … — date.md`).

## Interleaving (automatic)

1. **Curriculum level:** next lesson follows CURRICULUM.md's deterministic strand rotation (A ↔ B).
2. **Retrieval level:** each lesson's end quiz mixes 1–2 prior related concepts from the *other* strand.
3. **Review level:** unchanged (the existing SRS shuffle/adjacency/alternation) — not this skill's job.

Within a lesson, **introduction stays sequential** (one color at a time). Interleaving is for practice and retrieval.

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