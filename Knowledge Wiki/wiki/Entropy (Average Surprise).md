# Entropy (Average Surprise)

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** H(P) = E[−log p(X)] — the probability-weighted average of surprise. Max at uniform, 0 at deterministic.

## Definition

H(P) = −Σ p(x) log p(x) = Σ p(x)·(−log p(x)).

## Expectation reading

E[X] = Σ p(x)·x weights each value by its probability. Entropy is the expectation *of the surprise* −log p(x), with p(x) as the weight — not "the expected value of p(x)".

## Rare events don't blow it up

A 1-in-1000 event has surprise ≈ 9.97 bits but contributes only 0.001 × 9.97 ≈ 0.01 bits, because it is weighted by its tiny probability. p·log p → 0 as p → 0.

## Examples

- Fair coin: H = 1.0 bit (maximum for a binary variable)
- 99%-heads coin: H ≈ 0.08 bits (near-certain → almost nothing learned per flip)
- Fair die: H = +log₂ 6 ≈ 2.585 bits (positive — entropy is non-negative)

## Nearest neighbor

Entropy is a property of one distribution; [[Cross-Entropy from NLL]] measures a distribution *against* another. Entropy is also the average length of the optimal code (Olah).

## Related

- [[Information Content (Surprise)]]
- [[Cross-Entropy from NLL]]
- [[PMF vs PDF]]
