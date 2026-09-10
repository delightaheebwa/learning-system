# Optimizer Selection (Rohit Heuristic)

Given a training run, which optimizer do you reach for?

1. **Start with Adam** — \(\eta = 0.001\). Works for most problems without tuning.
2. **Switch to SGD with momentum** — \(\eta = 0.01\), momentum 0.9 — when you need the *best final accuracy* and can afford more tuning.
3. **Use AdamW** (Adam with **decoupled weight decay**) for transformers.

Standing rule: **always use a learning-rate schedule for runs longer than a few epochs.** Unstable → reduce \(\eta\); too slow → increase it.

## Why "switch to SGD for best accuracy" isn't a contradiction

Adam is the "just works" default, yet SGD+M wins on *final* accuracy — that's the sharp-vs-flat-minima story: Adam's aggressive per-parameter adaptivity makes fast early progress but can settle into **sharp minima** (poor generalization). SGD's noise keeps it out of those pits, landing in **flat minima**. See [[Mini-batch Noise (two effects)]].

## The race was an artifact

In this lesson's run, momentum beat Adam (~2941 vs ~6156 steps to converge) on the Rosenbrock function — but note Rohit's own defaults expect the opposite ("Expected output: Adam converges fastest"; Rohit uses Adam lr=0.01 vs SGD+M lr=0.0001). The ordering flips with hyperparameter choices, which is itself the point: a toy-race ranking is hyperparameter-dependent, not a general result. And Rosenbrock is a clean, deterministic, 2-D, *ill-conditioned* toy — its minimum sits in "a narrow curved valley that is easy to find but hard to follow" — with no noise, no sparsity, no sharp minima. **Do not generalize that ranking to real training.** The race taught how the knobs work, not which wins in practice.

## Related pages

- [[Optimizers (SGD, Adam, AdamW)]] — older reference table; its "Practical Rule" (only switch to SGD to reproduce papers) is superseded by this heuristic
- [[Learning Rate]] · [[Adam (adaptive moments)]] · [[Momentum (SGD with Momentum)]] · [[Learning-rate Schedules (four types)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-10 (SHIP)
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md`
