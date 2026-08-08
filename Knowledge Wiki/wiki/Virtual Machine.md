# Virtual Machine

A **Virtual Machine (VM)** is a program that emulates a hypothetical chip — a "fake chip" that acts as a lightning-fast translator on the user's computer.

## How it works

- Reads [[Bytecode]] line by line
- Translates each bytecode instruction into native machine code for the real CPU
- Executes the translated instructions

## Why VMs exist

Without a VM, compiled code only runs on the specific chip architecture it was compiled for. A VM lets the same bytecode run anywhere — the VM handles the device-specific translation.

The hard work is building different VM implementations for every major device (Windows, Mac, Linux, different CPU architectures) so that programs "just work everywhere instantly."

## Examples

- **JVM (Java Virtual Machine)** — runs Java bytecode
- **Python VM** — runs Python bytecode (`.pyc` files)
- **JavaScript engines** (V8, SpiderMonkey) — run JavaScript, often with [[JIT Compilation]]

## Related

- [[Bytecode]]
- [[Compiler]]
- [[Interpreter]]
- [[JIT Compilation]]
- [[Runtime]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*
