# Perplexity

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 (Information Theory) + PyTorch `CrossEntropyLoss` docs · **Lang:** Python
> **Insight:** Perplexity = 2^H in bits (e^H in nats) — the *effective number of equally likely choices* a model is hesitating between. A uniform model over k outcomes has perplexity exactly k.

## Definition

PPL = 2^{H(P,Q)} with the cross-entropy in bits, or e^{H(P,Q)} with it in nats (see [[Bits vs Nats]]).

Equivalent reading: PPL = 1 / (the geometric mean of the probabilities the model assigns to the true tokens) — exponentiating the average log-probability undoes the log and turns "average surprise" into "a count of choices". It is a monotone re-expression of cross-entropy, so ranking perplexities is ranking cross-entropies; only compare models on the *same* tokenization.

## The uniform anchor

Uniform over k → H = log₂ k → PPL = 2^{log₂ k} = k. So perplexity reads directly as "as uncertain as if it were choosing uniformly among k options".

- GPT-2 ≈ 30 on standard LM benchmarks; modern frontier models sit in the single digits.
- Perplexity is reported per token; a change of tokenizer changes the number without changing the model.

## Two unrelated "uniform"s (2026-09-24)

- Perplexity's uniform = a **hypothetical yardstick**: every distribution has PPL = 2^H, and a *non-uniform* model can have PPL 7. Nothing in the model is uniform.
- [[Label Smoothing]]'s uniform = a **real ingredient** of the training target (the ε/K share).

Same word, unrelated mechanisms. The staging differs too: perplexity is an **evaluation-time, output-side** conversion (mainly LM reporting), while label smoothing is a **training-time, input-side** modification of the target. There is no cross-entropy → perplexity → smoothing pipeline.

## Unit discipline (the practiced slip, 2026-09-24)

Give the entropy in the base whose exponential you use: cross-entropy in bits → 2^H; in nats → e^H. A 5-bit cross-entropy converted with e^H gave 11.048 ≈ e^{2.4} instead of 2^5 = 32; the repair is the detector on [[Bits vs Nats]] ("bits → base 2, nats → base e"). Cross-model comparison must convert first — 4 nats = 5.77 bits > 5 bits.

## Nearest neighbour

[[Cross-Entropy from NLL]] is the number; perplexity is that number re-expressed as a count of equally likely choices. It is *not* the model's own entropy H(P) — it is built from the cross-entropy against the data, so its floor is the data's entropy expressed in the same base.

## Related

- [[Cross-Entropy from NLL]]
- [[Entropy (Average Surprise)]]
- [[Bits vs Nats]]
- [[Label Smoothing]]
- [[Logits & Log-odds]]

## Source

- Rohit ai-engineering-from-scratch — `phases/01-math-foundations/09-information-theory/docs/en.md`
- PyTorch `torch.nn.CrossEntropyLoss` — https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- Lesson `Learning System/Lessons/Lesson — Information Theory — 2026-09-11.md` (CP6, 2026-09-24), teaching note `Learning System/Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`, Learning Record 0008.
