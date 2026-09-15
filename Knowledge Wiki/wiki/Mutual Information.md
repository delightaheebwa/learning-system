# Mutual Information

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** I(X;Y) is how many bits of X's uncertainty knowing Y removes — the information the two variables share. Symmetric, never negative, and exactly zero when they are independent.

## The defining idea

How much does knowing Y tell me about X? Start from X's own uncertainty H(X) ([[Entropy (Average Surprise)]]) and subtract what is still uncertain once Y is known — the conditional entropy H(X|Y):

**I(X;Y) = H(X) − H(X|Y)**

Mutual information is the *uncertainty deleted*, not "X is now certain": if H(X|Y) > 0 some doubt remains, and MI is only the amount that went away. Two extremes anchor it — if Y determines X perfectly then H(X|Y) = 0 and I(X;Y) = H(X) (all of X's uncertainty, no more); if Y tells you nothing about X then H(X|Y) = H(X) and I(X;Y) = 0.

## Four equivalent forms

1. **Deleted uncertainty:** I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X)
2. **Bars / set form (Olah):** I(X;Y) = H(X) + H(Y) − H(X,Y) — double-count the overlap, subtract the union once
3. **Surprise form:** I(X;Y) = Σ_x Σ_y p(x,y)·log₂( p(x,y) / (p(x)·p(y)) ) — how much more (or less) often the pair occurs than chance would predict
4. **KL form:** I(X;Y) = KL( p(x,y) ∥ p(x)·p(y) ) — the joint, measured against the independence baseline ([[KL Divergence]])

Form 4 is the unification: mutual information *is* a KL divergence — the bits wasted by coding the pairs as though X and Y were independent. Form 1 is where the ≥ 0 and the symmetry are easiest to see, form 2 is the picture, form 3 is what you compute cell by cell.

## Properties

- **I(X;Y) ≥ 0** — read off form 4 with KL ≥ 0 (Gibbs' inequality).
- **I(X;Y) = 0 iff X and Y are independent** — then p(x,y) = p(x)·p(y) for every cell, every log-ratio is 0, and the shared information is 0.
- **Symmetric: I(X;Y) = I(Y;X).** "How much Y tells me about X" is the same number as the reverse. This is exactly what [[KL Divergence]] does *not* do — here the arguments are the joint and the product of its marginals, and relabelling X ↔ Y relabels both together, so nothing changes.
- **I(X;X) = H(X)** — a variable tells you everything about itself (H(X) − H(X|X) = H(X) − 0). So MI is bounded above by the entropy of either variable.
- **I(X;Y) ≤ min(H(X), H(Y))** — a variable cannot carry more information about X than X itself contains (for two binary variables: at most 1 bit).

## The bars picture (Olah)

Draw a bar of length H(X) and a bar of length H(Y):

- the **overlap** is I(X;Y);
- the **union** is H(X,Y);
- the **non-overlapping parts** are H(X|Y) and H(Y|X).

H(X,Y) counts the overlap twice (once inside each bar) and the rest once, so H(X) + H(Y) − H(X,Y) leaves a single copy of the overlap — form 2 is that bookkeeping. The picture also shows the bound: two bars can overlap by at most the shorter bar, i.e. ≤ min(H(X), H(Y)).

The same picture yields **variation of information**, a distance between two variables:

V(X,Y) = H(X|Y) + H(Y|X) = H(X,Y) − I(X,Y)

It is 0 exactly when each variable determines the other (the bars coincide), and as large as H(X) + H(Y) when they are independent (no overlap at all) — a genuine metric built out of MI.

## Worked example — the joint [[0.45, 0.05], [0.05, 0.45]]

| P(X,Y) | Y = 0 | Y = 1 | p(x) |
|---|---|---|---|
| **X = 0** | 0.45 | 0.05 | 0.5 |
| **X = 1** | 0.05 | 0.45 | 0.5 |
| **p(y)** | 0.5 | 0.5 | 1 |

Marginals are the row and column sums → both a fair coin, so **H(X) = H(Y) = 1 bit**. Conditionals: given Y = 0 the column becomes (0.45, 0.05)/0.5 = (0.9, 0.1), entropy ≈ 0.137 + 0.332 = 0.469 bits; the Y = 1 column gives the same, and averaging over Y (0.5 each) gives **H(X|Y) = 0.469 bits**.

```
I(X;Y) = H(X) − H(X|Y) = 1.000 − 0.469 = 0.531 bits
```

The other forms agree:

```
bars:     H(X) + H(Y) − H(X,Y) = 1.000 + 1.000 − 1.469 = 0.531
          (H(X,Y) = −[2·0.45·log₂0.45 + 2·0.05·log₂0.05] ≈ 1.469 bits)
surprise: 2·0.45·log₂(0.45/0.25) + 2·0.05·log₂(0.05/0.25) ≈ 0.763 − 0.232 = 0.531
KL:       KL(joint ∥ product of marginals) = 0.531
```

Cell by cell, the surprise form reads the correlation straight off the table: the diagonal cells are 1.8× more likely than chance predicts (0.45 vs 0.25, ≈ +0.848 bits each) while the off-diagonal cells are 0.2× as likely (0.05 vs 0.25, ≈ −2.322 bits each); any cell whose ratio is exactly 1 contributes 0. Here V(X,Y) = 0.469 + 0.469 = 0.938 bits — the variables are 0.938 bits "away" from being each other's function.

Contrast with independence: the joint [[0.25, 0.25], [0.25, 0.25]] has the same marginals but every cell equals p(x)·p(y), so every log-ratio is 0 and I(X;Y) = 0. Same marginals, zero shared information — MI measures the *dependence*, not the marginals.

## Where it is used

- **Feature selection:** rank features by I(feature; label) — it catches any dependence, including non-linear ones that correlation misses. Example: X uniform on {−1, 0, 1}, Y = X². Covariance(X,Y) = 0, yet Y is a deterministic function of X, so H(Y|X) = 0 and I(X;Y) = H(Y) ≈ 0.918 bits. Correlation says "unrelated"; MI says "0.92 bits of relationship".
- **Decision trees:** a split is chosen to minimise the remaining uncertainty of the label, H(Y|X) — which is exactly maximising I(X;Y) for the chosen feature. A tree's "information gain" *is* mutual information.
- **Redundancy / independence checks:** I(X;Y) ≈ 0 means Y carries nothing about X; I(X;Y) = H(X) means X is a deterministic function of Y (a redundant feature if X is an input and Y another input).

## Nearest neighbour

[[Entropy (Average Surprise)]] is one distribution's own uncertainty; [[Cross-Entropy from NLL]] scores a model against the truth; [[KL Divergence]] is the directed excess of one distribution over another. Mutual information is a KL too, but between a *joint* and the *product of its own marginals* — which is why it is symmetric, non-negative, and 0 only at independence. Against [[Covariance and correlation]]: correlation only sees linear alignment, MI sees any dependence at all.

## Related

- [[Entropy (Average Surprise)]]
- [[KL Divergence]]
- [[Cross-Entropy from NLL]]
- [[Information Content (Surprise)]]
- [[Joint, marginal, and conditional probabilities]]
- [[Independence of random variables]]

## Open questions

- Maximum possible overlap of two binary MI bars: it is ≤ min(H(X), H(Y)) = 1 bit — two binary variables can share at most 1 bit (channel-capacity territory). Planted as a warm-up; still open.

## Source

Rohit P1 L09 `docs/en.md` (https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/09-information-theory/docs/en.md) + Olah, *Visual Information Theory* (https://colah.github.io/posts/2015-09-Visual-Information/) — the four forms, the bars picture and the variation of information follow Olah; Rohit supplies the ML framing and the feature-selection/decision-tree uses.
