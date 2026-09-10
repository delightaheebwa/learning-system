# Mini-batch Noise (Two Effects)

The noise in SGD and mini-batches is not a bug. It does two genuinely different things — keep them on two different questions.

| Effect | Mechanism | Answers |
|---|---|---|
| **Optimization** | The noisy mini-batch gradient is **almost never exactly zero**, so SGD doesn't stall at **saddles / plateaus** | "Can I keep moving?" |
| **Generalization** | Noise stops you settling into **sharp minima** → you land in **flat minima** → better test accuracy | "Am I parking in a wide valley or a narrow crack?" |

## Full-batch exact vs mini-batch noisy estimate

With full-batch GD the gradient uses the entire dataset every step — the exact gradient. At a saddle where the true gradient is exactly zero, there is no direction to move, so it can sit on the flat spot. With mini-batch GD the gradient uses only a small random slice — a noisy estimate of the true gradient. Even where the true gradient is zero, the mini-batch estimate usually is not, and that random push moves the iterate off the saddle. (Handwritten notes, 2026-09-09.)

## The anchor

"**Escape**" goes with **saddles** (optimization). "**Avoid / settle into**" goes with **sharp minima** (generalization). One is about *moving*, one is about *where you stop*.

Saying "noise helps generalization" and "noise escapes saddles" in the same breath without separating them is the classic conflation — they act at different stages (training progress vs train→test gap).

## Why it matters: SGD vs Adam on test accuracy

Sharp minima are narrow pits overfit to training quirks — they generalize poorly. Flat minima are wide basins, whole neighborhoods of good solutions robust to the train→test shift — they generalize well. This is one reason SGD with momentum often beats Adam on final test accuracy even where Adam's adaptivity makes faster early progress: SGD's noise keeps it out of the sharp pits. (Visualization: Li et al. 2018, filter normalization.)

## Related pages

- [[Saddle Points (critical point triage)]]
- [[Optimizers (SGD, Adam, AdamW)]]
- [[Optimizer Selection (Rohit heuristic)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-10
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md` + [Li et al. 2018](https://arxiv.org/abs/1712.09913)
