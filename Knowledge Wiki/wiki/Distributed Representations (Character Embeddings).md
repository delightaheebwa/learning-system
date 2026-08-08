# Distributed Representations (Character Embeddings)

Instead of one-hot vectors (27-dim, sparse), each character is mapped to a small **dense** vector — say 10 floating-point numbers. These are learned during training.

**Key property:** Similar characters end up with similar vectors. Vowels ('a', 'e', 'i') cluster together. Consonants that appear in similar contexts ('t', 's' before 'h') cluster together. This isn't hardcoded — it emerges from the data.

A dense vector of 10 floats can encode rich information about a character's role (is it a vowel? does it commonly start words? does it pair with 'h'?). A one-hot vector of 27 entries carries exactly 1 bit of information.

**In PyTorch:** `nn.Embedding(27, 10)` gives a learnable lookup table mapping each integer index to its 10-dim vector — same as one-hot @ W but more efficient.

---

## Why "Continuous" Matters

The real upgrade from one-hot to embeddings isn't the size — it's the jump from **discrete** to **continuous**.

**Discrete (one-hot):** Characters are isolated buckets. 'a' is `[1,0,0,...]`, 'b' is `[0,1,0,...]`. There's *nothing* between them. No distance to measure. No smooth interpolation. The model can't tell how "close" two characters are — they're just different categories.

**Continuous (embeddings):** Characters live in a smooth geometric space where every dimension is a floating-point number. 'a' at `[0.2, 0.5]`, 'e' at `[0.21, 0.49]` — they sit next to each other. You can:
- Measure distance (Euclidean, cosine)
- Slide from one to another with interpolation
- Learn that characters in the same neighborhood share properties

That smoothness is also what makes gradient descent work. Gradients need continuous values to flow back through. If your input is a hard `[1,0,0]` with no in-between values, there's nothing to differentiate. With continuous embeddings, small changes in the embedding parameters produce small changes in the output — and those small deltas are exactly what backpropagation uses.

> Discrete: jumping between rigid, separate buckets.
> Continuous: placing things on a smooth geometric map where distance = similarity.

Related: [[One-Hot Encoding]] | [[Hidden Layers Generalize via Shared Weights]]

Part of: Socratic tutoring session on neural network scalability (Gemini)

Source: Discrete vs. Continuous Representations — Gemini tutoring session on why continuous embeddings enable gradient learning