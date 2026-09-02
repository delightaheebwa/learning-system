# Base Rate Fallacy

> **Source:** Phase 1, Lesson 2 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Bayes' Theorem]], [[Prior Probability]], [[Posterior Probability]]

## Definition

The mistake of focusing on new evidence (a test result or description) while ignoring how common or rare the event actually is in reality.

## Example

A 99% accurate disease test on a 1/1000 prevalence disease → P(disease|positive) ≈ 9%, not 99%. People intuitively focus on the test accuracy (99%) and ignore the base rate (0.1%).

## Why It Matters for AI/ML

- Misinterpreting model outputs by ignoring class imbalance
- Setting bad confidence thresholds
- Shipping overconfident predictions on rare events

## The Fix

Always account for the prior. Bayes' Theorem forces you to incorporate base rates into your reasoning.