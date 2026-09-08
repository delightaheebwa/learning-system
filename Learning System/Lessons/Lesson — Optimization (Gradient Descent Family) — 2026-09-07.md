# Lesson — Optimization (Gradient Descent Family) — 2026-09-07

> **Track:** AIEFS · **Phase 1, Lesson 08** · **Lang:** Python
> **Status: PAUSED at Checkpoint 4/5** (student-paced breakpoint, 2026-09-08)

## Sources

- Rohit: `phases/01-math-foundations/08-optimization/docs/en.md`
- Ruder — gradient descent survey · Goh — Why Momentum Really Works (Distill) · Kingma & Ba — Adam (2015) · Li et al. — Loss Landscape (2018)
- Scout digest: `Learning System/.tmp/context-current-p1l08-optimization.json`

## Probe verdict (2026-09-07)

| Strand | State | Evidence |
|---|---|---|
| Gradient = steepest ascent, step opposite | **solid** | Q1 C sure, Q7 correct |
| Learning-rate overshoot | **solid** | Q2 A sure |
| Chain rule multiplies | **solid** | Q3 D sure + prior pass (2026-09-05) |
| Cross-entropy = −log | **solid** | Q5 D sure — *09-06 structural mistake resolved* |
| Why mini-batch noise helps | **unknown** | Q4 B hunch (lucky) + Q8 wrong reason ("overfitting") |
| Saddle point vs local min | **unknown** | Q6 answered "local minimum" |

## Checkpoints completed

### Checkpoint 1 — Loss landscape & vanilla gradient descent ✅

- \(w \leftarrow w - \eta\nabla L(w)\); gradient points uphill, we step opposite.
- Learning rate = most important hyperparameter (too large → diverge/bounce; too small → crawl).
- Rosenbrock \(f(x,y)=(1-x)^2+100(y-x^2)^2\), min at (1,1), narrow curved valley.
- Built `GradientDescent` + `rosenbrock_gradient`. Paper practice: one step from (−1,1), η=0.0005 → grad (−4,0) → (−0.998,1). Correct.

### Checkpoint 2 — Momentum ✅

- \(v \leftarrow \beta v + g,\ w \leftarrow w - \eta v\), β=0.9.
- Goh's deeper mechanism: momentum rescales effective step size per Hessian eigenvector direction, equalizing convergence across curvature.
- Velocity accumulates along-valley (x, consistent sign) and cancels across-walls (y, oscillates).
- Built `SGDMomentum`. Paper practice: v1=(−4,0), step → (−0.9996,1). Correct.
- Exit check (why x direction): **passed** — named direction + "toward minimum"; reason sharpened to selective accumulation.

## Exit ticket (pause) — 2026-09-07

| Item | Answer | Verdict |
|---|---|---|
| E1 (GD struggle in valley) | D sure | ❌ — said overshoot (lr) instead of zigzag |
| E2 (momentum accumulates along x) | B sure | ✅ |
| E3 (momentum update in words) | — | ✅ — "90% previous speed + gradient" |

## Re-seal (2026-09-08) — zigzag vs overshoot ✅ PASSED

- (A) large η → **overshoot** (diverge/bounce), fix = smaller η · (B) narrow curved valley → **zigzag**, fix = momentum.
- E1 conflation resolved.

### Checkpoint 3 — Adam ✅ (2026-09-08)

- Adam = momentum (m, β₁=0.9) + RMSprop (v, β₂=0.999) + bias correction, Kingma & Ba 2015.
- Lineage (Ruder): SGD → Adagrad (running sum of g², collapses lr to 0) → RMSprop (decaying avg fixes it) → Adam (adds momentum + bias correction).
- \\(m \\leftarrow \\beta_1 m + (1-\\beta_1)g\\); \\(v \\leftarrow \\beta_2 v + (1-\\beta_2)g^2\\); update \\(w \\leftarrow w - \\eta\\hat{m}/(\\sqrt{\\hat{v}}+\\epsilon)\\).
- Bias correction \\(\\hat{m}=m/(1-\\beta_1^t)\\) — fixes zero-init cold start (first steps too timid); fades to 1 as t grows.
- Built `Adam` class + ran 3-optimizer race on Rosenbrock: Vanilla GD never converged (5.7e-05, zigzag), Momentum converged ~2941 steps (2.2e-29), Adam ~6156 steps (4.6e-13). **Momentum fastest on this clean deterministic benchmark** — Adam slower, its per-weight adaptivity unneeded here.
- Exit check: Q1 (why vanilla GD stuck = zigzag, not sharpness — corrected 'sharp'→'narrow') ✅; Q2 (β₁=mean grad direction, β₂=mean grad² scale — corrected swapped roles/v-label) ✅.
- Attempts recorded: Adam, Momentum, Gradient Descent (vanilla) — all pass, interval_index 1.

## Exit ticket (pause) — 2026-09-08

| Item | Answer | Verdict |
|---|---|---|
| P1 (β₁/β₂ roles) | B sure | ✅ |
| P2 (race result) | C sure | ✅ |
| P3 (bias correction why) | — | ✅ — cold start, zero-init shrinks early steps, (1−βᵗ) un-shrinks until history accumulates |

## Checkpoint 4 — saddle points + mini-batch noise (OPEN, taught but NOT exit-checked)

- Critical-point triage via Hessian: local min (PSD, all λ≥0) · local max (NSD) · saddle (mixed-sign λ).
- High-dim: saddle points dominate ~exponentially in d (Dauphin et al. 2014, via Ruder) — NOT Li et al. 2018 (that's filter-norm loss-surface smoothing).
- Vanilla GD stalls at a saddle (∇=0). Mini-batch noise makes the gradient a non-zero random variable → nudge off saddle. This is an *optimization* effect (escape stall), distinct from noise's *regularization* effect (train-test gap).
- **Resolved probe Q6** (local min → saddle) & **Q8** (overfitting → escape-stall mechanism).
- Exit check (3 items) **not yet administered** — resume here.

## Resume from: Checkpoint 4 exit check (3 items)

Ask the CP4 exit-check (Hessian signs + stall; why high-d → saddles; optimization vs generalization reason for noise). Then CP5 (LR schedules + sharp/flat minima) → SHIP (Rosenbrock race artifact + optimizer-choice prompt).

## Concepts (banked today, 2026-09-08)

- Gradient Descent (vanilla) — procedure ✅
- Learning Rate — concept ✅
- Momentum (SGD with Momentum) — procedure ✅
- Adam (adaptive moments) — procedure ✅ (NEW today)
