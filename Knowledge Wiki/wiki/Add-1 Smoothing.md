# Add-1 Smoothing

## Overview
**Add-1 (Laplace) smoothing** adds a small fake count to every possible bigram entry, ensuring no entry is ever zero. This prevents log(0) = -∞ from breaking the loss function.

## Why It's Needed
- Many bigrams never appear in training (e.g. "JQ" in English names)
- Without smoothing, the model assigns P = 0 to unseen bigrams
- NLL loss computes -ln(P) → -ln(0) = +∞ → entire average loss becomes NaN

## Implementation
```python
P = (N + 1).float()
P /= P.sum(1, keepdim=True)
```

Adding 1 to every count is equivalent to L2 regularization in the neural network version — pulling weights toward zero (uniform distribution).

## Effect
- Every bigram gets a tiny non-zero probability (e.g., P(JQ) ≈ 0.00003)
- -ln(0.00003) ≈ 10.4 instead of ∞
- The loss remains finite and trainable

## Trade-off
Higher smoothing → more uniform distribution → lower confidence on seen patterns. Use dev set to tune the smoothing strength (the fake count value).

## Source
Karpathy, "makemore Part 1" — Neural Networks: Zero to Hero, Lecture 2.
