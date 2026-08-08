# One-Hot Encoding

Categorical variables (like character indices 0-26) can't be directly multiplied by a weight matrix. One-hot encoding converts each integer index into a binary vector of length `num_classes` — all zeros except a single 1 at the index.

```python
xenc = F.one_hot(xs, num_classes=27).float()
# shape: (N, 27) — N examples, each a 27-dim vector
```

**Why not use the integer directly?** Multiplying an integer by a weight implies ordinal relationships — that "a" (1) is closer to "b" (2) than "y" (25). Character indices have no ordinal meaning, so one-hot preserves the categorical nature.

**Key limitation:** One-hot vectors are 27-dimensional but carry only 1 bit of information — extremely sparse. This is why embeddings (dense vectors learned from data) replace one-hots in larger models.

Part of: Neural Networks: Zero to Hero — makemore Part 2 (Karpathy Lecture 2)

[[Bigram Language Model]] | [[Softmax Function]] | [[Row-Select Property]] | [[Distributed Representations (Character Embeddings)]]
