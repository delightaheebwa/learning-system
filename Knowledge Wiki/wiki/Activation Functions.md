# Activation Functions

Without activations, stacking linear layers collapses into one big linear function — no matter how deep. Activation functions introduce **non-linearity**, the source of neural networks' representational power.

## Common Functions

| Function | Output Range | Use Case |
|----------|-------------|----------|
| **ReLU** | `[0, ∞)` | Hidden layers — default choice |
| **Sigmoid** | `(0, 1)` | Binary output (disease probability) |
| **Softmax** | `(0, 1)`, sums to 1 | Multi-class output (which disease?) |

- ReLU is the default for hidden layers across almost all architectures
- Sigmoid squashes to a probability for binary decisions
- Softmax converts logits to a probability distribution over C classes
- **Critical:** Do NOT put softmax in `forward()` when using `nn.CrossEntropyLoss()` — it applies softmax internally

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14
- **Further reading:** [Goodfellow §6.3](https://www.deeplearningbook.org/contents/mlp.html)

## Connections
- Prerequisites: PyTorch Model Building
