# Laplace Smoothing (Add-1 Smoothing)

> **Source:** Phase 1, Lesson 2 — Bayes' Theorem & Statistical Thinking (AIEFS Rohit)
> **Related:** [[Naive Bayes]], [[Bayes' Theorem]]

## The Problem

If a word never appeared during training → zero frequency → kills the entire probability product (log(0) is undefined).

## The Fix

Add 1 count to every word-class pair:

$$P(\text{word} | \text{class}) = \frac{\text{count}(\text{word}, \text{class}) + 1}{\text{total words in class} + \text{vocabulary size}}$$

Keeps probability normalized but never zero.

## Why It Works

The +1 is a small correction that prevents any probability from being exactly zero, while the denominator adjustment (adding vocabulary size) keeps the distribution properly normalized.