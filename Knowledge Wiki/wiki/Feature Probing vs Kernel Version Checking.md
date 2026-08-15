# Feature Probing vs Kernel Version Checking

## Overview

When a kernel feature may be absent (e.g. `MemAvailable` in `/proc/meminfo`, only added in **Linux 3.14**), production tools like `free` and `top` do **not** check the kernel version. They **probe for the feature at runtime** and degrade gracefully with a fallback formula.

## Why Not Version Checking

1. **Backports make versions lie** — enterprise distros (RHEL, Debian) backport features to older kernels; a 3.10 kernel from RHEL can have `MemAvailable`. `uname` also can be spoofed.
2. **Multi-binary shims are a maintenance nightmare** — shipping a separate `free` for 2.6 / 3.10 / 4.20 / 5.x is unmanageable; users expect one binary that "just works" across kernel generations.

## The Pattern: Runtime Feature Probing

Ask "is the feature present?", never "what version are you?":

```c
memory.available_kb = ULONG_MAX;   // sentinel: "not seen yet"
// parse /proc/meminfo...
if (memory.available_kb == ULONG_MAX) {
    // MemAvailable line never appeared → feature unsupported on this kernel
}
```

The sentinel value doubling as a feature probe is the same idea as [[Sentinel Values vs Presence Flags]] — `ULONG_MAX` is outside the legitimate domain, so "still sentinel" reliably means "absent".

## Graceful Fallback Math

When `MemAvailable` is absent (pre-3.14), estimate from fields present since Linux 2.6:

```
Estimated Available ≈ MemFree + Buffers + Cached
```

Not as precise as the kernel's internal estimation, but remarkably close for older systems.

## Key Insight

- **Probe capability, not version.** Version strings are fragile (backports, spoofing); feature presence is truth.
- Degrade gracefully: use the real value when present, a documented fallback formula when not — never crash, never lie.
- This is why the smoke test keeps the sentinel check (`available_kb != ULONG_MAX`): the sentinel is both a correctness check and the feature probe.

## Sources

- Gemini Socratic session — robust `/proc/meminfo` smoke test (notebook: https://gemini.google.com/app/e338aa05afbec7a2)
