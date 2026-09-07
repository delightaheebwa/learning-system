# Lesson — Optimization (Gradient Descent Family) — 2026-09-07

> **Track:** AIEFS · **Phase 1, Lesson 08** · **Lang:** Python
> **Status: PAUSED at Checkpoint 2/5** (student-paced breakpoint)

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

## Resume from: Checkpoint 3 (Adam)

**Re-seal first (2 min):** the two GD failure modes were conflated in E1 — **zigzag** (narrow valley, gradient points across walls) vs **overshoot** (lr too large, diverge/bounce). Confirm distinction before Adam.

Then: Checkpoint 3 (Adam: first/second moments + bias correction, Kingma & Ba) → CP4 (saddle points + why noise escapes — the two probe `unknown` strands) → CP5 (LR schedules + sharp/flat minima, Li et al.) → SHIP (Rosenbrock 3-optimizer comparison + optimizer-choice prompt artifact).

## Concepts (today)

- Gradient Descent (vanilla) — procedure
- Learning Rate — concept
- Momentum (SGD with Momentum) — procedure
