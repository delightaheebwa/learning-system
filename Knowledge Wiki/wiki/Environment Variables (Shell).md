# Environment Variables (Shell)

> Source: Lecture 2 written notes (website, Fri 2026-08-21) + MIT Missing Semester. Ingested 2026-08-24.

## What they are

Every process receives a bag of `KEY=value` **strings** from its parent. Whenever a program calls another program, it passes along its environment variables — that is how settings flow down a process tree. List them with `env`; print one with `echo $HOME`. Like shell variables generally, they have no types — everything is a string.

## Setting them — three scopes

1. **Per-command:** `TZ=Asia/Tokyo date` prepends an assignment to a single command — only *that* child sees `TZ`. Afterwards `echo $TZ` prints nothing: the variable never entered your shell. (The notes demonstrate this with `T2=Asia/Tokyo date` → `echo $T2` empty.)
2. **Shell-local:** `FOO=1` creates a variable owned by the shell process itself. Children do **not** inherit it.
3. **Exported:** `export DEBUG=1` (or `export DEBUG` for an existing var) marks the variable part of the environment, so every child inherits it. Check: `bash -c 'echo $DEBUG'` → `1`.

## Deleting: `unset`

`unset DEBUG` removes the variable from the environment/shell.

## Why export/unset must be built-ins

They mutate the **shell's own memory** (its environment). A child program cannot modify its parent's environment — OS process isolation forbids it (see [[MIT Missing Semester — Shell]] § Shell Built-ins vs External Programs).

## Common uses & gotchas

- `$PATH` is just another environment variable — extend with `export PATH=$PATH:/new/dir`.
- Per-command assignment is idiomatic for one-off config: `DEBUG=1 ./server`.
- Forgetting `export` is the classic bug: the script you call sees an empty variable while `echo $VAR` in the shell looks fine.

Related: [[Positional & Special Shell Parameters]] · [[Exit Codes & Short-Circuit Control Flow]]
