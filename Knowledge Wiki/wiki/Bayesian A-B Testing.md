# Bayesian A-B Testing

> **Source:** Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Conjugate Priors]], [[Sequential Bayesian Updating]], [[Posterior Probability]]

## The Frequentist Procedure It Replaces

Frequentist A/B testing asks a skeptical, counter-intuitive question: 'Assuming both buttons are actually identical, how surprising is the difference we just saw?'

1. **Null hypothesis (default):** assume zero difference between A and B.
2. **Collect data, measure difference:** run the experiment, record conversions, observe a gap.
3. **p-value (skeptic's metric):** probability of seeing a gap this big purely by chance.
4. **Decision (p < 0.05):** if p < 5%, conclude the outcome is too rare to be luck — ship the winner.

## Setup

Two button colors, A (blue) vs B (green). Start both with a Beta(1,1) prior — no preference. Observe: A: 50 clicks/1000 views → Beta(51,951), mean ≈ 0.051. B: 65/1000 → Beta(66,936), mean ≈ 0.066.

## The Decision: P(B > A)

Computing P(B's true rate exceeds A's) analytically is hard; Monte Carlo makes it trivial — draw 100,000 samples from each Beta posterior, take the fraction where B > A:

`P(B > A) = mean(samples_B > samples_A)`

Ship B if P(B>A) > 0.95; ship A if < 0.05; otherwise keep collecting.

## Why Bayesian Beats Frequentist

| Aspect | Frequentist | Bayesian |
|--------|-------------|----------|
| Output | p-value | P(B > A) |
| Interpretation | 'How surprising is this data if A=B?' | 'How likely is B better than A?' |
| Early stopping | Inflates false positives | Safe at any point |
| Prior knowledge | Not used | Encoded as Beta prior |

Three killer advantages: a **direct probability statement** ('97% chance B is better'); **no peeking problem** (check anytime — the posterior doesn't depend on when you looked); and **prior knowledge** (encode past tests as the Beta prior to decide faster on scarce early data).
