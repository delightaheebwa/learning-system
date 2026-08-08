# Static Fixtures & Boundary Cases

## Overview

A **fixture** is controlled, predictable sample data used as test input. It turns a moving target (live OS text, real user input) into a fixed puzzle. **Boundary/adversarial fixtures** deliberately push the parser outside its happy path to prove it fails cleanly instead of crashing or corrupting.

## Why Fixtures

A parser tested only against real files is tested against whatever the machine happens to produce — you never know what you actually covered. A static fixture gives the test a fixed contract: "given THIS text, output must be THAT". A failure now means the parser, not the environment (see [[Testable Seam]]).

## Boundary Fixture Classes

1. **Format drift** — tabs instead of spaces, multiple leading spaces, different line endings. Real kernels/OS versions format text differently.
2. **Malformed input** — missing headers, truncated lines, extra fields. Parser should return a clean error, not crash or corrupt memory.
3. **Extreme values** — numbers exceeding 32-bit limits (RAM sizes), very long strings, exceeding buffer sizes.
4. **Empty/null input** — zero-byte files handled gracefully.
5. **Cross-platform variants** — Linux 5.x vs 6.x, different distributions → separate fixtures per known format.

## The Production Blind Spot

Fixture assumptions break in production: a kernel update adds or drops stats, a locale changes formatting, a user's config differs. The parser made assumptions that held for *one* fixture but failed on varied inputs. Test with many fixtures — including hostile ones — not one happy path.

## One Line Summary

One happy-path fixture proves nothing about production; boundary fixtures prove the parser fails *safely* and *precisely*.

## Sources

- Teach C Course — Lesson 2: Your First Tests
- Gemini Socratic tutoring on fixtures (notebook: https://gemini.google.com/app/e21b1624e3b156a0)
