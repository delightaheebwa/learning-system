# Saddle Points (Critical-Point Triage)

A critical point is where the gradient is exactly zero. A **saddle point** is a critical point that is a minimum in some directions and a maximum in others — flat, but not a minimum.

## Triage via Hessian eigenvalues

| Signs of λ | Classification |
|---|---|
| All λ ≥ 0 (positive semi-definite) | Local minimum |
| All λ ≤ 0 (negative semi-definite) | Local maximum |
| Mixed signs | **Saddle** |

Example: \(f(x,y)\) with \(\lambda_1 = 2, \lambda_2 = -4\) → saddle.

## Why saddles dominate in high dimensions

A strict local minimum needs **all** \(d\) eigenvalue signs positive. Treated as roughly independent coin flips, the chance of that is about \((1/2)^d\) — exponentially tiny. A saddle needs only **one** sign to disagree. So in a network with a million weights, a critical point is almost surely a saddle. (The coin-flip model is an intuition aid, not an exact law about real Hessian spectra.)

**Attribution that matters:** the saddle-dominance argument is Dauphin et al. (2014), via Ruder's survey — *not* Li et al. (2018). Li et al. contributed the filter-normalization *visualization* of loss landscapes (sharp vs flat minima).

## Why vanilla GD stalls there

The update \(w \leftarrow w - \eta\,\nabla L(w)\) is proportional to the gradient. At the exact saddle point the gradient is zero → no step is taken. (Sliding off along the negative-curvature direction only happens *after* a nudge moves you off the point.)

## Related pages

- [[Mini-batch Noise (two effects)]] — noisy gradients escape saddles
- [[Momentum (SGD with Momentum)]]
- [[Learning-rate Schedules (four types)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-07/10
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md` + [Ruder's survey](https://ruder.io/optimizing-gradient-descent/) (Dauphin et al. 2014)
