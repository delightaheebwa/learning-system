# SWE Foundations Glossary

> Canonical language for the SWE Foundations (Stage 0) workspace. One glossary for the workspace, per-track subheadings.
> Add a term only when the user understands it (compressed knowledge, not a dictionary). Be opinionated; keep definitions tight.
> As understanding deepens, revise in place.

## SWE

- **Testable seam**: The boundary where a controlled input replaces the real environment (e.g. `parse_meminfo(text, out)` instead of `read_meminfo(path, out)`); the second is where most bugs live, so most unit tests belong there.
- **Fixture**: Controlled sample data that makes a moving target predictable (stable text with exact asserts).
- **Smoke test**: A live read with range/sanity bounds, not exact values (e.g. `total > 0`, `available <= total`).
- **Arrange–Act–Assert (AAA)**: Three recognizable test phases — arrange inputs, act on the behavior under test, assert the observable result. If you can't point to the Act, the test checks too much.
- **Red–green–refactor**: The TDD loop — fail for a meaningful reason, make it pass, improve design without changing protected behavior.
- **Make**: A build tool, not a compiler — checks prerequisites and runs a recipe when a target is out of date (timestamp comparison).
- **Signal**: An asynchronous message the kernel delivers to a process (a "software interrupt") that it may catch, ignore, or default-handle — the mechanism behind Ctrl-C (SIGINT), Ctrl-Z (SIGTSTP), and `kill` (SIGTERM/SIGKILL).
- **Job control**: The shell's toolkit for pausing and resuming processes — `Ctrl-Z` suspends, `fg`/`bg` resume, `jobs` lists; background jobs die with the terminal (SIGHUP) unless `nohup`/`disown` protect them.
- **`is_pid_name`**: A predicate that accepts names made entirely of digits, rejecting `self`, `thread-self`, and other kernel entries; validate the string, don't use `atoi==0` to mean "not a PID".

## Color taxonomy (Primary Colors) — see `Knowledge Wiki/wiki/SWE Primary Colors & Roadmap.md`

- **Process**: How humans build reliably — testing, debugging, git, reading code.
- **Systems**: What the machine actually does — OS, processes, memory layout.
- **Interaction**: How things talk — I/O, protocols, network, UIs.
- **Computation**: How we transform data — algorithms, logic, complexity.
- **State**: How we remember things — memory, files, databases.
- **Abstraction**: How we tame complexity — functions, modules, interfaces.

<!-- AIE terms (paused track) would live under a future ## AIE subheading. -->