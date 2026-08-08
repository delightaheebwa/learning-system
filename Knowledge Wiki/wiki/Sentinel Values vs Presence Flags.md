# Sentinel Values vs Presence Flags

## Overview

A **sentinel value** is a payload value reused to mean "absent" (e.g. `0` or `-1` meaning "not found"). The trap: if that value is also a legitimate domain value, you can't tell a real zero from a missing field.

## The Trap

Parsing `/proc/meminfo` into a struct that returns success when the fields are non-zero:

```c
return (out->total_kb != 0 && out->available_kb != 0) ? 0 : -1;
```

Two failure modes:

1. **Valid zeroes:** `MemAvailable: 0 kB` (an out-of-memory container) is a *successful parse* of zero, but the check treats it as a parsing failure (false negative).
2. **Accidental true negative:** a field never present stays `0` (thanks to `struct memory memory = {0}`), which happens to satisfy the error branch — but only because `0` was recycled to mean both "uninitialized" and "zero memory". The check is correct *by coincidence*, not by design.

Reusing payload values to represent *structural* status (present vs missing) is a classic systems-programming trap: `0` is simultaneously a valid quantity and an absence marker — ambiguous.
## The Naive Fix the Lesson Teaches (Teach C Lesson 3)

The lesson's practice fix is the two-field sentinel check this page replaces:

```c
return out->total_kb != 0 ? 0 : -1;   // lesson starter: only checks total
// practice fix — still a sentinel check:
return (out->total_kb != 0 && out->available_kb != 0) ? 0 : -1;
```

Requiring both fields is better than one, but both are sentinel checks on payload values — the presence-flag version below is the robust replacement.

## The Fix: Separate Presence from Value

**Explicit presence flags:**

```c
struct memory {
    unsigned long total_kb;
    unsigned long available_kb;
    bool has_total;
    bool has_available;
};
```

Inside the parse loop, set the flag when the key is matched:

```c
if (strcmp(key, "MemTotal") == 0) {
    out->total_kb = value;
    out->has_total = true;
}
```

Return success on structural presence, not on non-zero payload:

```c
return (out->has_total && out->has_available) ? 0 : -1;
```

`true != false` checks are valid but redundant — write `out->has_total` directly.

**Alternatives:** bitmask flags (`found_mask |= MEM_TOTAL_BIT`) checked after the loop, or field counters.

## Key Insight

- Decouple *structural presence* from *numeric payload*. Presence is tracked by flags; the value stores only the quantity.
- In C, explicit comparisons like `x != false` simplify to `x`.

## Sources

- Gemini Socratic tutoring on parsing `/proc/meminfo` (notebook: https://gemini.google.com/app/8870dcd71e2919f5)
- Teach C Course — Lesson 3: Acutest and the Parser Seam (practice exercise)
