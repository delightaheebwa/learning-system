# Naive Bayes Classifier

> **Source:** Phase 1, Lesson 2 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[Laplace Smoothing]], [[Conditional Independence]]

## Formula

$$P(\text{class} | f_1, f_2, \dots, f_n) = P(\text{class}) \cdot P(f_1 | \text{class}) \cdot P(f_2 | \text{class}) \dots P(f_n | \text{class}) / P(\text{features})$$

Multiply the likelihoods of all features together.

## The "Naive" Part

Naive Bayes assumes every word/feature is **conditionally independent** given the class — meaning once you know it's spam, knowing "free" appeared tells you nothing extra about whether "money" appeared.

## Why It Still Works

Despite this false assumption, Naive Bayes still works because the classifier only needs to **rank classes correctly**, not produce calibrated probabilities.

## Variants

- **Multinomial Naive Bayes:** for text classification (word counts)
- **Gaussian Naive Bayes:** for continuous features
- **Bernoulli Naive Bayes:** for binary features

## Zero Frequency Problem

If a word never appeared during training → zero frequency → kills the entire product / log(0) undefined. Fix: [[Laplace Smoothing]].