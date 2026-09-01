# Chain Rule for Neural Networks

> **Type:** procedure · **Track:** AIEFS · **Source:** Rohit P1 L05 + CS231n optimization-2 · **Lang:** Python
> **Insight:** Gradients multiply across layers (not add) because intermediate variables are dependent.

## Definition

The chain rule states: if y = f(g(x)), then dy/dx = f'(g(x)) · g'(x).

For a multi-layer neural network with layers a1 → a2 → a3 → loss:

```
∂Loss/∂w1 = ∂Loss/∂a3 × ∂a3/∂a2 × ∂a2/∂a1 × ∂a1/∂w1
```

Each factor is a **local derivative** — how much the next variable changes given this one.

## Why Multiplication, Not Addition

Variables in a neural network are **dependent** (chained): a2 depends on a1, which depends on w1. The effects compound multiplicatively. Addition would only be correct if the variables were independent.

**Analogy (soccer):** Pass the ball through Player A (×5) then Player B (×3). Total displacement = 5 × 3 = 15, not 5 + 3 = 8. Each player scales what they receive.

## Role in Backpropagation

Backpropagation IS the chain rule applied layer by layer, from loss backward to each weight.

## Common Mistake

Using **addition** (+) instead of **multiplication** (×) when computing gradients through layers.

## Related

- [[Backpropagation]]
- [[Reverse-Mode Autodiff & Backprop]]
- [[Chain Rule Decomposition]]
