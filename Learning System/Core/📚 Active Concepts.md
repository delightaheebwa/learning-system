# KNOWLEDGE BASE — Active Concepts

> Purpose: Active learning record for the current focus area. The assistant reads this at the start of learning sessions.
> Paused/archived concepts: `Learning System/Core/📦 Concept Archive.md` (searched on demand, not auto-loaded)
> Scripture memory (archived 2026-09-08): `Learning System/Archive/frozen/📖 Scripture Memory.md`

## Metadata

- **Tracks:** AIEFS (AI Engineering from Scratch — Rohit, 20 phases; Mission 0 Catch-Up P0+P1.01–06 80/20)
- **Learner:** Aheebwa Delight
- **Source:** AI Engineering from Scratch — https://github.com/rohitg00/ai-engineering-from-scratch — phases/*/docs/en.md + Further Reading (Rohit is a source, not the source)
- **Previous Tracks:** AI Engineering (aie) — archived 2026-07-28; SWE (swe) — archived 2026-09-01 (43 concepts → 📦 Concept Archive.md)
- **Last Updated:** 2026-09-07 — schedule fix (UTC): 9-col normalize (Track=aiefs, language folded into Source), catch-up section header restored; next Phase 1 L07; SWE archived (strictly out of scope); live fetch per lesson (no cache).
- **Interleaving:** Active (shuffle + adjacency constraint + alternating question types)
- **System:** Open WebUI Learning System

---

## Live System Notes

- Use **"review"** to trigger AIEFS track reviews (SWE `swe` is archived — redirects to AIEFS)
- Use **"lesson"/"continue"** to run the next AIEFS curriculum lesson: Mission 0 Catch-Up is **done**; Phase 1 L07 (Bayes) **done**; **resume Phase 1 L08 — Optimization (paused Checkpoint 2/5)**. See `Learning System/CURRICULUM.md`; delegated to `learning-teach` — probe → plan → teach, live fact-checking.
- Each trigger runs a separate review session limited to that track's due concepts (cap of 5 per session)
- `Sessions/` is the session history for the active learning system
- `Reviews/` stores spaced-repetition review notes
- `Concept Notes/` is archived (`Archive/frozen/concept-notes/`) — atomic pages live in `Knowledge Wiki/wiki/`
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

- **AIEFS (AI Engineering from Scratch):** Mission 0 catch-up done; P1 L07 done; P1 L08 Optimization in-progress (paused 2/5) — 21 live concepts (see CURRICULUM.md).
- **Not Started:** 20 phases (Phases 0–19) navigational; after each phase decide to go deeper / branch.
- **Paused:** ~146 (103 prior + 43 SWE archived 2026-09-01) — see `📦 Concept Archive.md` (SWE visibility strictly out of scope)
- **Consolidated:** 0
- **Total concepts tracked:** ~118

---

## Open Questions

> Questions that emerged during sessions but haven't been fully resolved yet. The assistant surfaces these at the start of every session.

- None currently

### Mission 0 Catch-Up — 80/20 Foundations (P0 + P1.01–06)

| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |
|---------|-------|------|--------|--------|---------------|-------------|-------------|---------------|
| Chain Rule for Neural Networks | aiefs | procedure | developing | Rohit P1 L05 + CS231n (Python) | 2026-09-05 | 2026-09-12 | discriminative | Gradients multiply across layers (not add) because variables are dependent. |
| PMF vs PDF | aiefs | concept | developing | Rohit P1 L06 + CS229 (Python) | 2026-09-05 | 2026-09-12 | discriminative | PMF=discrete probability, PDF=density (integrate), CDF=cumulative. |
| Softmax Subtract-Max Trick | aiefs | procedure | developing | Rohit P1 L06 + Gundersen (Python) | 2026-09-05 | 2026-09-12 | discriminative | Subtract max(z) before exp to prevent overflow. Identical result. |
| Cosine Similarity | aiefs | concept | developing | Rohit P1 L02 + 3B1B (Python) | 2026-09-08 | 2026-09-14 | definitional | Unit vectors u·v=cos(θ). Measures alignment −1 to +1. |
| 4-Layer AI Environment Stack | aiefs | concept | developing | Rohit P0 L01-L12 (Python) | 2026-09-08 | 2026-09-10 | definitional | System→Packages→Runtimes→AI Libs. GPU issue = Runtimes. |
| Cross-Entropy from NLL | aiefs | concept | developing | Rohit P1 L06 + CS229 (Python) | 2026-09-09 | 2026-09-15 | discriminative | L=−log(p_correct). Minimizing pushes true class toward 1. |

### Bayes' Theorem & Statistical Thinking (Phase 1 Lesson 07)

| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |
|---------|-------|------|--------|--------|---------------|-------------|-------------|---------------|
| Adam (adaptive moments) | aiefs | procedure | developing | Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python) | 2026-09-08 | 2026-09-11 | definitional | m = direction (β₁=0.9); v = scale (β₂=0.999). Bias correction: m̂=m/(1-β₁ᵗ), v̂=v/(1-β₂ᵗ). Self-tuner per weight. SGD+M can beat Adam on generalization (sharp vs flat minima). Default lr=0.001. |
| Bayes' Theorem | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Prior Probability | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Likelihood | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Posterior Probability | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Base Rate Fallacy | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Naive Bayes | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Laplace Smoothing | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Conditional Independence | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| MLE vs MAP Estimation | aiefs | concept | developing | Rohit P1 L07 + lesson 2026-09-05 (Python) | 2026-09-08 | 2026-09-14 | discriminative | MAP = MLE × prior; Gaussian prior = L2, Laplace prior = L1. |
| Conjugate Priors (Beta-Binomial) | aiefs | concept | developing | Rohit P1 L07 + Think Bayes (Python) | 2026-09-08 | 2026-09-14 | discriminative | Beta(a,b) + s/f → Beta(a+s,b+f). Update = addition. |
| Sequential Bayesian Updating | aiefs | concept | developing | Rohit P1 L07 (Python) | 2026-09-09 | 2026-09-15 | discriminative | Today's posterior = tomorrow's prior. Order-invariant. |
| Bayesian A/B Testing | aiefs | procedure | developing | Rohit P1 L07 (Python) | 2026-09-08 | 2026-09-14 | discriminative | P(B>A) via Monte Carlo; safe early stopping. |
| Gradient Descent (vanilla) | aiefs | procedure | developing | Rohit P1 L08 + handwritten notes 2026-09-08 (Python) | 2026-09-08 | 2026-09-11 | definitional | w = w - lr*grad. No formula for η (empirical). Too big → overshoot/bounce; too small → freezes. Zigzag vs overshoot are different failures. GD never converged on Rosenbrock (20k steps). |
| Learning Rate | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-08 (Python) | 2026-09-08 | 2026-09-11 | definitional | Step size η. No formula — tune empirically. Too big → overshoot/bounce; too small → freezes. Adam 0.001, SGD+M 0.01. lr and optimizer choice are coupled. |
| Momentum (SGD with Momentum) | aiefs | procedure | developing | Rohit P1 L08 + Goh Distill + handwritten notes 2026-09-08 (Python) | 2026-09-08 | 2026-09-11 | definitional | v = βv + g (β=0.9). Selective accumulator: keeps consistent, cancels zigzag. Direction-dependent step size via eigenvalue λ: big steps along valley (small λ), small steps across walls (large λ). Won this lesson's Rosenbrock race (2941 steps; run-specific ordering — Rohit's defaults expect Adam fastest). |
| Saddle Points (critical point triage) | aiefs | concept | developing | Rohit P1 L08 + Ruder/Dauphin 2014 + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-09-17 | definitional | Mixed-sign Hessian eigenvalues. Local min needs all d signs positive ≈(1/2)^d, exponentially tiny. Dauphin=saddles; Li 2018=sharp/flat visualization. GD stalls (update ∝ grad=0). |
| Mini-batch Noise (two effects) | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-09-17 | definitional | Optimization: noisy grad almost never zero → escapes saddles. Generalization: avoids sharp minima → flat basins → better test accuracy. "escape"→saddles; "settle into"→sharp. |
| Learning-rate Schedules (four types) | aiefs | concept | developing | Rohit P1 L08 + Ruder + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-09-17 | definitional | Read η-vs-t curves: early phase (only warmup ramps up) + end behavior (only cosine has nonzero floor η_min; exponential→0 no floor; step=staircase). 0.999 halves η every ~700 steps. |
| Optimizer Selection (Rohit heuristic) | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-10-10 | definitional | Adam 0.001 default → SGD+M 0.01/0.9 for best final accuracy → AdamW for transformers; always schedule long runs. Rosenbrock race is an artifact. |

### Information Theory — Entropy, KL Divergence (Phase 1 Lesson 09) — in-progress (paused 2/6)

| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |
|---------|-------|------|--------|--------|---------------|-------------|-------------|---------------|
| Information Content (Surprise) | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-11 | 2026-10-11 | discriminative | I(x)=−log p(x). Rare events→large surprise; p=1→zero. Minus makes it non-negative; −log p ≈ optimal code length. |
| Entropy (Average Surprise) | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-11 | 2026-09-18 | discriminative | H(P)=E[−log p(X)], weighted by p(x). Fair coin 1 bit; fair die +2.585 bits. Max at uniform, 0 at deterministic. |
