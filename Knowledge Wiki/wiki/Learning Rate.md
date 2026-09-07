# Learning Rate

The scalar that controls how far each gradient-descent step moves: \(w \leftarrow w - \eta\,\nabla L(w)\). It is the single most important hyperparameter in optimization.

## The tradeoff

- **Too large** — the update overshoots the valley, bouncing between walls or diverging entirely.
- **Too small** — you crawl toward the answer over thousands of unnecessary steps.
- **No formula exists** — the right value is found by experiment.

## Starting points (Rohit rule of thumb)

| Optimizer | Starting lr |
|-----------|-------------|
| Adam | 0.001 |
| SGD with momentum | 0.01 (momentum=0.9) |

## Schedules

A fixed lr is a compromise — large steps early for fast progress, small steps late for fine-tuning. Common schedules: step decay, exponential decay, cosine annealing, warmup-then-decay (warmup is standard for large models to prevent early instability).

## Related pages

- [[Gradient descent]]
- [[Momentum (SGD with Momentum)]]
- [[Optimizers (SGD, Adam, AdamW)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-07
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md`
