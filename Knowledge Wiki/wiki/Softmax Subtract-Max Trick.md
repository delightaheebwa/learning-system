# Softmax Subtract-Max Trick

> **Type:** procedure · **Track:** AIEFS · **Source:** Rohit P1 L06 + Gundersen log-sum-exp · **Lang:** Python
> **Insight:** Subtract max(z) before exp to prevent float overflow. Mathematically identical.

## The Problem

exp(x) overflows when x > ~709 in float64.

## The Fix

softmax(z_i) = exp(z_i − max(z)) / Σ exp(z_j − max(z))

Max cancels in numerator/denominator.

## Implementation

```python
def softmax_safe(z):
    m = max(z)
    exps = [math.exp(x - m) for x in z]
    return [e / sum(exps) for e in exps]
```

## What It Does NOT Do

Does NOT force sum to 1. Purely numerical stability.

## Related

- [[Softmax Function]]
- [[Negative Log-Likelihood (NLL)]]
