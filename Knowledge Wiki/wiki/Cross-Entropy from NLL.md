# Cross-Entropy from NLL

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L06 + CS229 · **Lang:** Python
> **Insight:** L = −log(p_correct). Minimizing pushes true class toward 1. Measures model surprise.

## Definition

L = −Σ y_j log(ŷ_j) = −log(ŷ_i) for one-hot labels.

## Interpretation

−log(ŷ_i) = surprise. Small ŷ_i → large loss → big gradient.

## Minimizing

Pushes ŷ_i toward 1. Does NOT make all outputs equal.

## Softmax Connection

Gradient: ∂L/∂z_j = softmax(z)_j − y_j.

## Related

- [[Negative Log-Likelihood (NLL)]]
- [[Softmax Function]]
- [[Loss Functions (PyTorch)]]
