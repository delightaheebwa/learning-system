# Bytecode

**Bytecode** is a portable intermediate representation between source code and machine code. It is not tied to any specific CPU architecture.

## How it's used

1. Source code is compiled to bytecode
2. A [[Virtual Machine]] reads the bytecode and executes it (or [[JIT Compilation|JIT-compiles]] it to machine code)

## Why bytecode?

- **Portability** — same bytecode runs on any device that has the right VM
- **Speed** — bytecode is closer to machine code than source, so the VM can execute it faster than interpreting raw source
- **Separation of concerns** — language designers focus on the language → bytecode compiler; VM implementers focus on the device-specific translation

## Examples

- **Java `.class` files** — bytecode for the JVM
- **Python `.pyc` files** — bytecode for the Python VM
- **WebAssembly (Wasm)** — bytecode for browsers

## Related

- [[Virtual Machine]]
- [[Compiler]]
- [[Interpreter]]
- [[JIT Compilation]]

---

*Source: [[2026-05-29 - compilers-interpreters-virtual-machines]]*
