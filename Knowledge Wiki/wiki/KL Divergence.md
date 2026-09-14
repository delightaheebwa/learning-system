# KL Divergence

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** KL(Q∥P) = Σ q(x)·log₂(q(x)/p(x)) = H(P,Q) − H(Q) — the extra bits a model wastes over the truth's own entropy. Never negative, zero only when the model *is* the data, and not symmetric.

## Definition

KL(Q∥P) = Σ_x q(x)·log₂(q(x)/p(x))

In this lesson's letters **Q is the truth — it supplies the weights — and P is the model — it supplies the scored probabilities** — the same lettering as [[Cross-Entropy from NLL]]. Each event contributes its surprise *gap* log₂(q/p), averaged over what actually happens. (Rohit's `en.md` and most ML code flip the letters and write D_KL(P∥Q) = H(P,Q) − H(P); it is the same identity with the letters renamed — see the conventions table on the cross-entropy page.)

The operational form is cross-entropy minus the data's entropy:

**KL(Q∥P) = H(P,Q) − H(Q) = CE − H(data)**

## Two properties that define it

- **KL(Q∥P) ≥ 0** (Gibbs' inequality) — H(Q) is the average length of the optimal code for the truth ([[Entropy (Average Surprise)]]), and no other code beats it; the difference is the excess the model's distribution costs. For the coin below: 1.0 − 0.811 ≈ 0.189 bits.
- **KL(Q∥P) = 0 iff P = Q** — equality exactly when the model agrees with the data on every event. Terms where q < p contribute negatively and terms where q > p positively, and Gibbs' inequality says the positives always win unless the two distributions match.

## Not symmetric

KL measures a *directed* gap: swapping which distribution supplies the weights changes the average. Coin — truth Q = (0.75, 0.25), model P = (0.5, 0.5):

```
KL(Q∥P) = H(P,Q) − H(Q) = 1.000 − 0.811 ≈ 0.189 bits   (CE − the data's entropy)
KL(P∥Q) = H(Q,P) − H(P) = 1.208 − 1.000 ≈ 0.208 bits   (the same move, letters swapped)
```

Both are small and both are non-negative, but they are different numbers — so "the KL" means nothing until the direction is named. Cross-entropy is directional in exactly the same way (the same swap moves CE from 1.000 to 1.208 bits).

## Why minimizing cross-entropy ≡ minimizing KL

H(Q) depends only on the data, so it is a constant with respect to the model's parameters:

min_θ H(P_θ, Q) = H(Q) + min_θ KL(Q∥P_θ)

Same argmin, same gradient direction — training on [[Negative Log-Likelihood (NLL)]] / cross-entropy *is* pulling the model distribution toward the data distribution. In general the floor H(Q) is unreachable; KL is the part that can be driven toward 0.

## Infinity, and why smoothing exists

If an event has q(x) > 0 while the model puts p(x) = 0, that one term q(x)·log₂(q/p) is +∞ — cross-entropy and KL become infinite there, not merely large. A hard count-based model can hit that zero exactly (Naive Bayes with an unseen count — see [[Add-1 Smoothing]], [[Laplace Smoothing]]); a softmax model only approaches p(x) = 0 as a logit → −∞, so it yields a loss that grows without bound and a log-probability that eventually underflows to −inf. Never assign zero probability to something that can happen — label smoothing is the loss-side version of the same fix (CP6, not yet taught).

## Units

log₂ → bits, ln → nats (1 nat ≈ 1.4427 bits, so 0.189 bits ≈ 0.131 nats). Changing the base multiplies every KL and cross-entropy number by the same constant, so it never moves the minimum — but mixing bits and nats is a silent factor of 1.4427. PyTorch's native losses report nats.

## Nearest neighbour

[[Entropy (Average Surprise)]] is one distribution's own expected surprise — the best achievable average code length, reached only when the model equals the data. [[Cross-Entropy from NLL]] is H(Q) + KL: the model's average surprise measured against the truth. KL is the *difference* between the two — the waste. Cross-entropy is what the training loop computes; KL is what that number is actually spending itself on.

## Related

- [[Entropy (Average Surprise)]]
- [[Cross-Entropy from NLL]]
- [[Negative Log-Likelihood (NLL)]]
- [[Add-1 Smoothing]]
- [[Laplace Smoothing]]
