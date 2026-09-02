# Bayes' Theorem

> **Source:** Phase 1, Lesson 2 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Phase:** 1 · Math Foundations
> **Related:** [[Prior Probability]], [[Posterior Probability]], [[Likelihood]], [[Base Rate Fallacy]], [[Naive Bayes]], [[Laplace Smoothing]]

## Core Formula

$$P(H|E) = rac{P(E|H) \cdot P(H)}{P(E)}$$

**Components:**
- **Prior P(H):** Your belief before seeing any evidence — the base rate.
- **Likelihood P(E|H):** How probable the evidence is if the hypothesis is true.
- **Evidence P(E):** Total probability of seeing E under all possibilities (Law of Total Probability):
  - `P(E) = P(E|H)·P(H) + P(E|¬H)·P(¬H)`
- **Posterior P(H|E):** Belief after incorporating evidence.

## Why It Matters for AI/ML

AI models (ML, deep learning) work on probabilities. Bayes' Theorem is the mathematical framework for how an AI system incorporates new evidence to refine its confidence over time. Start with a belief, see evidence, update.

Without understanding this, you'll misinterpret model outputs, set bad thresholds, and ship overconfident predictions.

## Intuitive Example (Librarian/Farmer)

"Steve is meek and shy — is he a librarian or farmer?" Use the prior (how many librarians vs farmers exist), the likelihood (what proportion of each group fits the description), and compute the posterior.

## Disease Test Example

A disease affects 1 in 1000 people. A test is 99% sensitive, 1% false positive rate.

- P(disease) = 0.001 (prior / base rate)
- P(positive|disease) = 0.99 (likelihood)
- P(positive|healthy) = 0.01 (false positive rate)
- P(positive) = 0.99×0.001 + 0.01×0.999 = 0.01098
- P(disease|positive) = (0.99×0.001) / 0.01098 ≈ **9%**

**Intuitive:** In a group of 1000 people, 1 is sick (caught by test) and ~10 healthy people false-positive → 11 positive results, only 1 truly sick → ~1/11 ≈ 9%.

## Key Insight

The prior dominates when a condition is rare — even accurate tests produce mostly false positives.