# KNOWLEDGE BASE — Active Concepts

> Purpose: Active learning record for the current focus area. The assistant reads this at the start of learning sessions.
> Paused/archived concepts: `Learning System/Core/📦 Concept Archive.md` (searched on demand, not auto-loaded)
> Scripture memory (archived 2026-09-08): `Learning System/Archive/frozen/📖 Scripture Memory.md`

## Metadata

- **Tracks:** AIEFS (AI Engineering from Scratch — Rohit, 20 phases; Mission 0 Catch-Up P0+P1.01–06 80/20)
- **Learner:** Aheebwa Delight
- **Source:** AI Engineering from Scratch — https://github.com/rohitg00/ai-engineering-from-scratch — phases/*/docs/en.md + Further Reading (Rohit is a source, not the source)
- **Previous Tracks:** AI Engineering (aie) — archived 2026-07-28; SWE (swe) — archived 2026-09-01 (43 concepts → 📦 Concept Archive.md)
- **Last Updated:** 2026-09-14 — audit cleanup: AC Next Review synced to Attempts.json (4 rows), 'Conjugate Priors (Beta-Binomial)' renamed to canonical 'Conjugate Priors', 'Learning Rate' Attempts entry backfilled, KL Divergence row banked at CP4 ingest; 29 live concepts.
- **Last Updated:** 2026-09-15 — CP5-mid (mutual information) partial ingest: new `Mutual Information` row (idea-level, `developing`); `KL Divergence` row realigned to Attempts.json (`last_reviewed` 2026-09-15, `next_review` 2026-10-15) with the regression + re-seal note; IT section header and position pointers moved to paused mid-5/6; 30 live concepts.
- **Interleaving:** Active (shuffle + adjacency constraint + alternating question types)
- **System:** Open WebUI Learning System

---

## Live System Notes

- Use **"review"** to trigger AIEFS track reviews (SWE `swe` is archived — redirects to AIEFS)
- Use **"lesson"/"continue"** to run the next AIEFS curriculum lesson: Mission 0 Catch-Up is **done**; Phase 1 L07 (Bayes) **done**; Phase 1 L08 Optimization **done** (2026-09-10); **Phase 1 L09 — Information Theory is paused mid-Checkpoint 5/6 (2026-09-15): CP1–CP4 banked (CP4 re-sealed after the 09-15 resume warm-up regression) and the CP5 idea + four-form breakdown of I(X;Y) delivered — resume INSIDE CP5 at the KL-connection walkthrough, then CP5 practice (fresh computation) + Feynman, NOT at the idea**. See `Learning System/CURRICULUM.md`; delegated to `learning-teach` — probe → plan → teach, live fact-checking.
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

- **AIEFS (AI Engineering from Scratch):** Mission 0 catch-up done; P1 L07 done; P1 L08 Optimization **done** (2026-09-10); P1 L09 Information Theory paused mid-Checkpoint 5/6 (2026-09-15; CP1–CP4 banked — CP4 re-sealed after a resume warm-up regression — CP5 idea + four-form breakdown delivered, resume inside CP5 at the KL-connection walkthrough) — **30 live concepts** (all `developing`; counted from the `aiefs` rows of the table below on 2026-09-15: Mission 0 Catch-Up section 6 · Bayes & Statistical Thinking section 20 — of which 12 are L07 Bayes and 8 are L08 Optimization — · Information Theory section 4; total 6 + 20 + 4 = 30. Supersedes the 2026-09-14 "29 live concepts" figure.)
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
| Chain Rule for Neural Networks | aiefs | procedure | developing | Rohit P1 L05 + CS231n (Python) | 2026-09-12 | 2026-09-26 | definitional | Gradients multiply across layers (not add) because variables are dependent. |
| PMF vs PDF | aiefs | concept | developing | Rohit P1 L06 + CS229 (Python) | 2026-09-15 | 2026-09-22 | definitional | PMF=discrete probability, PDF=density (integrate), CDF=cumulative. |
| Softmax Subtract-Max Trick | aiefs | procedure | developing | Rohit P1 L06 + Gundersen (Python) | 2026-09-11 | 2026-09-25 | discriminative | Subtract max(z) before exp to prevent overflow. Identical result. |
| Cosine Similarity | aiefs | concept | developing | Rohit P1 L02 + 3B1B (Python) | 2026-09-15 | 2026-10-15 | discriminative | Unit vectors u·v=cos(θ). Measures alignment −1 to +1. |
| 4-Layer AI Environment Stack | aiefs | concept | developing | Rohit P0 L01-L12 (Python) | 2026-09-16 | 2026-09-23 | definitional | System→Packages→Runtimes→AI Libs. GPU issue = Runtimes. Layer order still shaky 09-12 (swapped 2–3: Runtimes before Packages). |
| Cross-Entropy from NLL | aiefs | concept | developing | Rohit P1 L06 + P1 L09 + Olah + PyTorch CrossEntropyLoss (Python) | 2026-09-16 | 2026-10-16 | definitional | H(P,Q)=Σ q(x)(−log₂ p(x)): weights from truth Q, surprises from model P (Olah convention here; Rohit/ML flips letters, P=truth → ≥H(P)). = CE loss = NLL (−log ŷ_correct under one-hot). Floor = the data's entropy H(Q): coin Q=(0.75,0.25) vs fair P → H(P,Q)=1.0 bit, floor 0.811, KL 0.189. Floor ≠ model's H(P). REGRESSED 09-14 (warm-up W4): picked reversed inequality H(P,Q) ≤ H(Q) — direction re-inverted; re-seal due 09-17. CP4 (KL) practice pass 09-14; Next Review realigned to Attempts.json (09-21). |

### Bayes' Theorem & Statistical Thinking (Phase 1 Lesson 07)

| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |
|---------|-------|------|--------|--------|---------------|-------------|-------------|---------------|
| Adam (adaptive moments) | aiefs | procedure | developing | Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python) | 2026-09-12 | 2026-09-26 | discriminative | m = direction (β₁=0.9); v = scale (β₂=0.999). Bias correction: m̂=m/(1-β₁ᵗ), v̂=v/(1-β₂ᵗ). Self-tuner per weight. SGD+M can beat Adam on generalization (sharp vs flat minima). Default lr=0.001. |
| Bayes' Theorem | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-12 | 2026-10-12 | definitional | |
| Prior Probability | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-16 | 2026-10-16 | definitional | |
| Likelihood | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Posterior Probability | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Base Rate Fallacy | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Naive Bayes | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Laplace Smoothing | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| Conditional Independence | aiefs | concept | developing | Phase 1 L07 notes | 2026-09-05 | 2026-09-12 | discriminative | |
| MLE vs MAP Estimation | aiefs | concept | developing | Rohit P1 L07 + lesson 2026-09-05 (Python) | 2026-09-15 | 2026-09-18 | definitional | MAP = MLE × prior; Gaussian prior = L2, Laplace prior = L1. |
| Conjugate Priors | aiefs | concept | developing | Rohit P1 L07 + Think Bayes (Python) | 2026-09-07 | 2026-09-14 | discriminative | Beta(a,b) + s/f → Beta(a+s,b+f). Update = addition. |
| Sequential Bayesian Updating | aiefs | concept | developing | Rohit P1 L07 (Python) | 2026-09-16 | 2026-10-16 | definitional | Today's posterior = tomorrow's prior. Order-invariant. |
| Bayesian A/B Testing | aiefs | procedure | developing | Rohit P1 L07 (Python) | 2026-09-08 | 2026-09-14 | discriminative | P(B>A) via Monte Carlo; safe early stopping. |
| Gradient Descent (vanilla) | aiefs | procedure | developing | Rohit P1 L08 + handwritten notes 2026-09-08 (Python) | 2026-09-10 | 2026-09-24 | definitional | w = w - lr*grad. No formula for η (empirical). Too big → overshoot/bounce; too small → freezes. Zigzag vs overshoot are different failures. GD never converged on Rosenbrock (20k steps). |
| Learning Rate | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-08 (Python) | 2026-09-15 | 2026-09-22 | discriminative | Step size η. No formula — tune empirically. Too big → overshoot/bounce; too small → freezes. Adam 0.001, SGD+M 0.01. lr and optimizer choice are coupled. |
| Momentum (SGD with Momentum) | aiefs | procedure | developing | Rohit P1 L08 + Goh Distill + handwritten notes 2026-09-08 (Python) | 2026-09-16 | 2026-09-30 | discriminative | v = βv + g (β=0.9). Selective accumulator: keeps consistent, cancels zigzag. Direction-dependent step size via eigenvalue λ: big steps along valley (small λ), small steps across walls (large λ). Won this lesson's Rosenbrock race (2941 steps; run-specific ordering — Rohit's defaults expect Adam fastest). |
| Saddle Points (critical point triage) | aiefs | concept | developing | Rohit P1 L08 + Ruder/Dauphin 2014 + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-09-17 | definitional | Mixed-sign Hessian eigenvalues. Local min needs all d signs positive ≈(1/2)^d, exponentially tiny. Dauphin=saddles; Li 2018=sharp/flat visualization. GD stalls (update ∝ grad=0). |
| Mini-batch Noise (two effects) | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-10 (Python) | 2026-09-15 | 2026-10-15 | discriminative | Optimization: noisy grad almost never zero → escapes saddles. Generalization: avoids sharp minima → flat basins → better test accuracy. "escape"→saddles; "settle into"→sharp. |
| Learning-rate Schedules (four types) | aiefs | concept | developing | Rohit P1 L08 + Ruder + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-09-17 | definitional | Read η-vs-t curves: early phase (only warmup ramps up) + end behavior (only cosine has nonzero floor η_min; exponential→0 no floor; step=staircase). 0.999 halves η every ~700 steps. |
| Optimizer Selection (Rohit heuristic) | aiefs | concept | developing | Rohit P1 L08 + handwritten notes 2026-09-10 (Python) | 2026-09-10 | 2026-10-10 | definitional | Adam 0.001 default → SGD+M 0.01/0.9 for best final accuracy → AdamW for transformers; always schedule long runs. Rosenbrock race is an artifact. |

### Information Theory — Entropy, KL Divergence (Phase 1 Lesson 09) — in-progress (paused mid-Checkpoint 5/6, 2026-09-15; CP1–CP4 banked, CP4 re-sealed — CP5 idea + four-form breakdown delivered; resume inside CP5 at the KL-connection walkthrough)

| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |
|---------|-------|------|--------|--------|---------------|-------------|-------------|---------------|
| Information Content (Surprise) | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-11 | 2026-10-11 | discriminative | I(x)=−log p(x). Rare events→large surprise; p=1→zero. Minus makes it non-negative; −log p ≈ optimal code length. |
| Entropy (Average Surprise) | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-11 | 2026-10-12 | discriminative | H(P)=E[−log p(X)], weighted by p(x). Fair coin 1 bit; fair die +2.585 bits. Max at uniform, 0 at deterministic. |
| KL Divergence | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-15 | 2026-10-15 | discriminative | KL(Q∥P)=Σ q·log₂(q/p)=H(P,Q)−H(Q)=CE−H(data). Weights ← truth Q, scores ← model P (Olah letters here; Rohit/ML flips → D_KL(P∥Q)=H(P,Q)−H(P)). ≥0, =0 iff P=Q; NOT symmetric (coin Q=(0.75,0.25) vs fair P: 0.189 vs 0.208 bits; second pair Q=(0.6,0.4) vs P=(0.9,0.1): 0.449 vs 0.326 bits); minimizing CE ≡ minimizing KL (H(data) constant in θ); ∞ when the model zeroes a data event — H(Q) stays finite, both CE and KL +∞ → smoothing (add-1/Laplace; label smoothing CP6). REGRESSED 09-15 (resume warm-up: ∞ case, identity sign, non-symmetry, all sure) → re-sealed same session (RS1 0.278 bits, exit ticket 0.326 bits); non-symmetry re-sealed but SHALLOW — keep a symmetric-pair item in reviews. attempts: fail, fail, pass → interval_index 3. |
| Mutual Information | aiefs | concept | developing | Rohit P1 L09 + Olah (Python) | 2026-09-15 | 2026-09-22 | definitional | I(X;Y)=H(X)−H(X|Y)=H(Y)−H(Y|X)=H(X)+H(Y)−H(X,Y)=ΣΣ p·log₂(p/(p·p))=KL(p(x,y)∥p(x)p(y)). ≥0, =0 iff independent, symmetric, I(X;X)=H(X), ≤ min(H(X),H(Y)). Olah bars = overlap (union H(X,Y)); V(X,Y)=H(X|Y)+H(Y|X) is a metric (0 iff each determines the other). Worked joint [[0.45,0.05],[0.05,0.45]] → H(X)=1, H(X|Y)=0.469, I=0.531 bits. Used for feature ranking (catches non-linear dependence) and decision-tree information gain. **IDEA-LEVEL ONLY: four forms + properties delivered and fact-checked; fresh I(X;Y) computation on a NEW joint NOT yet tested (CP5 practice next session) and NO Feynman attempted — not banked.** |
