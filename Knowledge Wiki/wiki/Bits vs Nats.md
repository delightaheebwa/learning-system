# Bits vs Nats

> **Type:** memory · **Track:** AIEFS · **Source:** Rohit P1 L09 + PyTorch `CrossEntropyLoss` docs · **Lang:** Python
> **Insight:** Bits and nats are the same information quantity in different log bases — the base is a *unit*, not a change of quantity. 1 nat = 1.4427 bits.

## The three units

| Unit | Log base | Where it shows up |
|------|----------|-------------------|
| bit (shannon) | log₂ | information theory, textbook entropy, this lesson's arithmetic |
| nat | ln | ML losses — PyTorch / TensorFlow cross-entropy is in **nats** by default |
| hartley (ban, dit) | log₁₀ | rare, historical |

## Conversion

1 nat = 1/ln 2 bits ≈ 1.4427 bits; 1 bit ≈ 0.6931 nats. Multiply, never mix: 2.3 nats × 1.4427 ≈ 3.3 bits, and 4 nats = 5.77 bits.

The base is a constant factor on every surprise term, so it rescales entropies and divergences *without* changing their order, their zero points, or identities like KL = CE − H.

## The detector (from the practiced slip, 2026-09-24)

**Read the unit before choosing the exponent:** cross-entropy in bits → [[Perplexity]] = 2^H; in nats → PPL = e^H. Applying e^H to a bits-valued H gave 11.048 ≈ e^{2.4} instead of 2^5 = 32 — the formula was right in shape, the unit was ignored. Cross-model comparison (final-quiz Q5) needs a common base first.

## Nearest neighbour

Not the same as changing the *distribution*: entropy's weights p(x) are untouched by the base. It is also not numerical stability (that is [[Softmax Subtract-Max Trick]]).

## Related

- [[Entropy (Average Surprise)]]
- [[Information Content (Surprise)]]
- [[Cross-Entropy from NLL]]
- [[Perplexity]]
- [[KL Divergence]]

## Source

- Rohit ai-engineering-from-scratch — `phases/01-math-foundations/09-information-theory/docs/en.md`
- PyTorch `torch.nn.CrossEntropyLoss` — https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html (nats by default)
- Lesson `Learning System/Lessons/Lesson — Information Theory — 2026-09-11.md` (CP6, 2026-09-24), teaching note `Learning System/Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`, Learning Record 0008.
