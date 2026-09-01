# KNOWLEDGE BASE — Active Concepts

> Purpose: Active learning record for the current focus area. The assistant reads this at the start of learning sessions.
> Paused/archived concepts: `Learning System/Core/📦 Concept Archive.md` (searched on demand, not auto-loaded)
> Scripture memory: `Learning System/Core/📖 Scripture Memory.md`

## Metadata

- **Tracks:** AIEFS (AI Engineering from Scratch — Rohit, 20 phases; Mission 0 Catch-Up P0+P1.01–06 80/20)
- **Learner:** Aheebwa Delight
- **Source:** AI Engineering from Scratch — https://github.com/rohitg00/ai-engineering-from-scratch — phases/*/docs/en.md + Further Reading (Rohit is a source, not the source)
- **Previous Tracks:** AI Engineering (aie) — archived 2026-07-28; SWE (swe) — archived 2026-09-01 (43 concepts → 📦 Concept Archive.md)
- **Last Updated:** 2026-09-01 — switched to AIEFS (Rohit); Mission 0 catch-up 80/20 P0+P1.01–06; next Phase 1 L07; SWE archived (strictly out of scope); live fetch per lesson (no cache).
- **Interleaving:** Active (shuffle + adjacency constraint + alternating question types)
- **System:** Open WebUI Learning System

---

## Live System Notes

- Use **"review"** to trigger AIEFS track reviews (SWE `swe` is archived — redirects to AIEFS)
- Use **"lesson"/"continue"** to run the next AIEFS curriculum lesson: **Mission 0 Catch-Up (P0+P1.01–06, 80/20, in-progress)** is first, next real lesson after catch-up is **Phase 1 L07 Bayes' Theorem** (decision 2026-09-01 — jump). See `Learning System/CURRICULUM.md`; delegated to `learning-teach` — probe → plan → teach, live fact-checking.
- Each trigger runs a separate review session limited to that track's due concepts (cap of 5 per session)
- `Sessions/` is the session history for the active learning system
- `Reviews/` stores spaced-repetition review notes
- `Concept Notes/` stores reusable atomic concept pages
- `Archive/` and `📦 Concept Archive.md` are reference-only
- This file is the source of truth for what is due and what is developing
- No more than 5 review concepts per session; overflow stays queued
- Previous tracks (aie, makemore) archived on 2026-07-28 — all reviews paused
- **Consolidation:** When a concept reaches `consolidated` status, it is moved to `Archive/Consolidated/[name].md` with a link to its Knowledge Wiki note and removed from this table.

---

## SWE Track — Shell & Terminal (MIT Missing Semester) — ARCHIVED 2026-09-01

> **Archived.** All SWE concepts moved to `📦 Concept Archive.md` (section `Paused Concepts — SWE (Archived 2026-09-01)`). This track is paused; reviews are disabled. See `Learning System/Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md`.

> Archived 2026-09-01: 43 concepts paused. No active SWE rows.
## Mastery Summary

- **AIEFS (AI Engineering from Scratch):** catch-up 80/20 P0+P1.01–06 in-progress; Phase 1 L07 is next; 0 active non-catch-up concepts yet (see CURRICULUM.md Mission 0 + 20 phases).
- **Not Started:** 20 phases (Phases 0–19) navigational; after each phase decide to go deeper / branch.
- **Paused:** ~146 (103 prior + 43 SWE archived 2026-09-01) — see `📦 Concept Archive.md` (SWE visibility strictly out of scope)
- **Consolidated:** 0
- **Total concepts tracked:** ~118

---

## Open Questions

> Questions that emerged during sessions but haven't been fully resolved yet. The assistant surfaces these at the start of every session.

- None currently| Chain Rule for Neural Networks | procedure | developing | Rohit P1 L05 + CS231n | Python | 2026-09-01 | 2026-09-04 | definitional | Gradients multiply across layers (not add) because variables are dependent. |
| PMF vs PDF | concept | developing | Rohit P1 L06 + CS229 | Python | 2026-09-01 | 2026-09-04 | definitional | PMF=discrete probability, PDF=density (integrate), CDF=cumulative. |
| Softmax Subtract-Max Trick | procedure | developing | Rohit P1 L06 + Gundersen | Python | 2026-09-01 | 2026-09-04 | definitional | Subtract max(z) before exp to prevent overflow. Identical result. |
| Cosine Similarity | concept | developing | Rohit P1 L02 + 3B1B | Python | 2026-09-01 | 2026-09-04 | definitional | Unit vectors u·v=cos(θ). Measures alignment −1 to +1. |
| 4-Layer AI Environment Stack | concept | developing | Rohit P0 L01-L12 | Python | 2026-09-01 | 2026-09-04 | definitional | System→Packages→Runtimes→AI Libs. GPU issue = Runtimes. |
| Cross-Entropy from NLL | concept | developing | Rohit P1 L06 + CS229 | Python | 2026-09-01 | 2026-09-04 | definitional | L=−log(p_correct). Minimizing pushes true class toward 1. |