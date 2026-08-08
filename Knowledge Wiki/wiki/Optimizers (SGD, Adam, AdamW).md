# Optimizers (SGD, Adam, AdamW)

The optimizer decides *how* to update weights after computing gradients. Different optimizers behave very differently.

| Optimizer | How It Works | When to Use | Typical LR |
|-----------|-------------|-------------|-----------|
| **SGD** | `weight -= lr × gradient` — simplest. | Maximum control or well-tuned schedules | 0.01–0.1 |
| **SGD + Momentum** | Builds velocity in consistent directions (like a ball rolling downhill) | Better than plain SGD. Good for CNNs. | 0.01, momentum=0.9 |
| **Adam** | Adaptive learning rate per parameter. Combines momentum + RMSprop. | **The default choice.** Works well out of the box. | 0.001 |
| **AdamW** | Adam with *decoupled* weight decay. Better regularization. | Transformers, modern architectures. Preferred over Adam. | 0.001, weight_decay=0.01 |

## Practical Rule

Start with **Adam** (lr=0.001) for new projects. If it doesn't converge, try **AdamW**. Only switch to SGD if you need to reproduce a paper's results (classic CNN papers use SGD+momentum).

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- **Further reading:** [PyTorch Optimizers Docs](https://pytorch.org/docs/stable/optim.html)

## Connections

- Prerequisites: Training Loop Pattern, Gradient Descent
- Leads to: Regularization Techniques
