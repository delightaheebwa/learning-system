# L2 Regularization as Smoothing

In the counting approach, add-1 smoothing prevents zero probabilities. In the neural approach, the equivalent is L2 regularization — penalizing large weights:

```python
reg_loss = 0.01 * (W**2).mean()
loss = negative_log_likelihood + reg_loss
```

**The mechanism:** When `W = 0`, logits = 0, exp(0) = 1 for every class. Softmax produces a **uniform** distribution — the smoothest possible. The regularization strength controls how hard weights are pulled toward zero, just like the number of fake counts controls smoothness.

| Approach | Smoothness Mechanism | Effect on Distribution |
|---|---|---|
| Counting | Add fake counts (+1 → +k) | Pulls toward uniform |
| Neural | L2 penalty on W | Pulls toward uniform |

**Why it matters:** Smoothing/regularization prevents overconfidence — forcing the model to reserve probability mass for unseen events. Without it, a single unseen bigram makes the loss infinite.

Related: [[Add-1 Smoothing]] | [[Regularization Tug-of-War]]

Part of: Neural Networks: Zero to Hero — Karpathy Lecture 2 + Socratic tutoring session
