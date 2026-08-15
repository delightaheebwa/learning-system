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

## Fixture Tests vs Smoke Tests (2026-08-15)

Two distinct layers for testing a parser that reads live OS files (see [[Testable Seam]]):

- **Fixture tests (deterministic):** feed known static text into the pure parser (`parse_meminfo`) and assert *exact* values — `assert(mem.total_kb == 16384256)`. The input never changes, so the output must be exact.
- **Smoke tests (live/system):** run against the real `/proc/meminfo` via the I/O layer (`read_meminfo`) and assert *range/sanity bounds*, not exact numbers — memory fluctuates between clock cycles, so exact asserts would be flaky. A smoke test is a sanity shield: "did the system layer succeed and return plausible physical bounds?"

Smoke-test invariant pattern (see [[Sentinel Values vs Presence Flags]]):

```c
TEST_CHECK((read_meminfo("/proc/meminfo", &memory) == 0) &&
           (memory.total_kb > 0) &&
           (memory.available_kb <= memory.total_kb));
```

Boundary lessons from this pattern:
- **`total_kb > 0`** guards a downstream divide-by-zero (`100.0 * used_kb / total_kb` crashes when total is 0).
- **`available_kb <= total_kb`** is the true invariant — strict `<` is brittle because `==` is reachable on fresh/controlled systems (no reclaimable overhead).
- A **missing key** (`MemAvailable` absent) with a `{0}` default silently passes `<=` — the missing-field check belongs in the smoke test too.

## One Line Summary

One happy-path fixture proves nothing about production; boundary fixtures prove the parser fails *safely* and *precisely*; smoke tests prove live reads stay within physical sanity bounds.

## Sources

- Teach C Course — Lesson 2: Your First Tests
- Gemini Socratic tutoring on fixtures (notebook: https://gemini.google.com/app/e21b1624e3b156a0)
- Gemini Socratic session — robust `/proc/meminfo` smoke test (notebook: https://gemini.google.com/app/e338aa05afbec7a2)
