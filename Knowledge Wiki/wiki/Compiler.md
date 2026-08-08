# Compiler

A **compiler** is a pipeline that translates source code (C++, Rust, Go) into machine code that a CPU can execute directly.

## Pipeline stages

1. **Frontend** — source-language-specific; handles lexing, parsing, semantic analysis
2. **Backend** — target-architecture-specific; handles optimization and code generation
3. **Optimization** — improves the generated code for speed/size by leveraging knowledge of the target chip's strengths and weaknesses
4. **Code generation** — produces the final machine code or intermediate representation

### Why compilers can optimize heavily

Unlike an \[\[Interpreter\]\], a compiler sees the **entire program at once** before any code runs. This "big picture" view enables powerful optimizations:

- **Math simplification** — replacing slow formulas with faster tricks the CPU prefers (e.g., `x * 2` → `x << 1`)
- **Dead code elimination** — removing lines and branches that never actually execute
- **Register allocation** — placing frequently accessed data directly into the CPU's fastest internal memory slots (registers) instead of slower RAM

An interpreter, executing line-by-line, simply doesn't have time for this analysis — it trades optimization for instant feedback.

## Output forms

- **Machine code** — native instructions for a specific CPU
- **Bytecode** — portable intermediate code that runs on a \[\[Virtual Machine\]\]
- **Three-address code** — a simple intermediate representation used internally by compilers

## Compiled vs Interpreted

See: \[\[Compiled vs Interpreted\]\]

## Related

- \[\[Interpreter\]\]
- \[\[Virtual Machine\]\]
- \[\[Bytecode\]\]
- \[\[JIT Compilation\]\]
- \[\[Transpiler\]\]

---

*Source: \[\[2026-05-29 - compilers-interpreters-virtual-machines\]\]*