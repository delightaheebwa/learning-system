# Adam (adaptive moments)

Adam combines two running averages per weight — momentum (first moment, mean gradient) and RMSProp (second moment, mean squared gradient) — with a bias-correction step, to give each weight its own adaptive learning rate without manual tuning.

## The equations (Kingma & Ba, 2015)

Given gradient \(g\) at step \(t\), with \(\beta_1 = 0.9\), \(\beta_2 = 0.999\), \(\epsilon = 10^{-8}\):

- First moment: \(m \leftarrow \beta_1 m + (1 - \beta_1) g\) — mean gradient (direction)
- Second moment: \(v \leftarrow \beta_2 v + (1 - \beta_2) g^2\) — mean squared gradient (scale)

Bias correction:

- \(\hat{m} = m / (1 - \beta_1^t)\)
- \(\hat{v} = v / (1 - \beta_2^t)\)

Update:

- \(w \leftarrow w - \eta \, \hat{m} / (\sqrt{\hat{v}} + \epsilon)\)

Default: \(\eta = 0.001\).

## Why bias correction

Both \(m\) and \(v\) are initialized to zero. On early steps, this zero-initialization biases the estimates downward (too small), making the first steps timid. Dividing by \((1 - \beta^t)\) compensates: at \(t=1\), \(\hat{m} = g\) (the true gradient, unshrunk), and as \(t\) grows, \(\beta^t \to 0\) so the correction fades to 1. It is not a hack — it compensates for the cold-start artifact and becomes irrelevant once history accumulates.

## Optimizer lineage (Ruder's genealogy)

1. SGD — one shared \(\eta\) for every weight. Can't handle weights with wildly different gradient scales.
2. Adagrad — divides by running *sum* of \(g^2\). Adapts per weight but the sum only grows, so effective lr shrinks to zero.
3. RMSProp — replaces the sum with an exponentially decaying *average* of \(g^2\) (\(v\)). Fixes the collapse.
4. Adam = RMSProp + momentum + bias correction. Combines both averages, corrects cold start.

## Key insight from Rosenbrock race (CP3, 2026-09-08)

On a clean, smooth, deterministic benchmark (Rosenbrock), **SGD with momentum converged first** (~2941 steps) while **Adam converged later** (~6156 steps). The per-weight adaptivity Adam provides is not needed on a two-dimensional problem with uniform curvature structure — the overhead costs time. But on real neural nets (sparse, high-dimensional, wildly different gradient scales per weight), Adam's self-tuning is a major practical advantage.

SGD with momentum also achieves lower final loss on many practical tasks because its residual noise prevents settling into sharp minima (which generalize worse) — Adam's aggressive flattening can land in a sharp basin.

## When to use

- **Adam** is the robust default — good out of the box with no tuning.
- **SGD + momentum** often achieves better final accuracy when tuning budget allows, because its noise aids generalization.
- The choice is task-dependent, not a fixed hierarchy.

## Related pages

- [[Gradient descent]]
- [[Momentum (SGD with Momentum)]]
- [[Learning Rate]]
- [[Optimizers (SGD, Adam, AdamW)]]

## Sources

- Kingma & Ba, "Adam: A Method for Stochastic Optimization" (2015)
- Ruder, "An overview of gradient descent optimization algorithms"
- Lesson: Phase 1 L08 — Optimization (Gradient Descent Family), 2026-09-07/08
