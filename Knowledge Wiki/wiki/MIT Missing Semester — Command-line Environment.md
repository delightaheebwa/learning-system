# MIT Missing Semester — Command-line Environment

**Source:** [Command-line Environment](https://missing.csail.mit.edu/2026/command-line-environment/)
**Track:** SWE (Software Engineering Fundamentals)
**Taught:** 2026-08-18 (lesson B2)

## Signals (software interrupts)

A **signal** is a short asynchronous message the kernel (or another process) delivers to a process — a "software interrupt" — that makes it stop and react. The receiving process can **catch, ignore, or take the default action** (often terminate). That's why Ctrl-C "sometimes fails" — the target gets a vote.

### The graceful-to-hard kill ladder

| Signal | Sent by | Catchable? | Purpose |
|---|---|---|---|
| SIGINT | `Ctrl-C` | Yes | polite interrupt |
| SIGTERM | `kill <pid>` | Yes | "exit gracefully, clean up first" |
| SIGKILL | `kill -9 <pid>` | **No** | nuclear option — always works, skips cleanup |

Rule of thumb: try Ctrl-C → `kill` (SIGTERM) → only if it still won't die, `kill -9`. SIGKILL's cost is no cleanup: orphaned child processes, unsaved state.

## Job Control

- `Ctrl-Z` sends **SIGTSTP** (terminal stop) — *suspends*, doesn't kill.
- `jobs` — list unfinished jobs with job numbers (`[1]`, `[2]`, …).
- `fg %1` — resume job 1 in the foreground; `bg %1` — resume in the background.
- `cmd &` — start in the background directly; `$!` — PID of the last background job.

**SIGHUP trap:** a backgrounded process is still a *child of the terminal*; closing the terminal sends SIGHUP (hangup) and kills it. Survive with `nohup cmd &` (before) or `disown %1` (after).

## Environment Variables

- `FOO=bar` — local to the current shell only.
- `export FOO=bar` — puts `FOO` in the environment block every child process inherits.
- `printenv` lists current env vars; `unset FOO` removes one.
- Convention: env vars are ALL_CAPS (`HOME`, `PATH`, `DEBUG`); local shell vars are lowercase.

## Return Codes & Boolean Operators

- Exit code `0` = success; nonzero = failure. `$?` holds the last command's code.
- `&&` / `||` are **short-circuiting** operators on return codes, not values:
  - `grep -q pat file && echo found` — runs only if grep succeeded (0).
  - `grep -q pat file || echo "not found"` — runs only if grep failed.
- `if`/`while` also test return codes.

## Aliases

`alias ll='ls -lh'` — the shell expands `ll` to `ls -lh` *before* running it. No space around `=`. Aliases can't take arguments mid-command (use functions for that); `\ll` bypasses, `unalias ll` removes.

## Dotfiles

Plain-text config files whose names start with `.` (e.g. `~/.bashrc`, `~/.gitconfig`, `~/.vimrc`, `~/.tmux.conf`, `~/.ssh/config`) — hidden from the default `ls` by convention. Organize them in a version-controlled folder and symlink into place for portability and quick re-install.

## Terminal Multiplexers (tmux)

tmux runs several shell sessions in one terminal via **sessions → windows → panes**, and lets you **detach** (`<C-b> d`) and **reattach** (`tmux a`) later — invaluable on remote machines (replaces `nohup` tricks).

## SSH (brief)

`ssh alice@server` opens a remote shell; key-based auth (public-key crypto) is preferred over passwords. `scp`/`rsync` copy files; `~/.ssh/config` stores per-host defaults.

## Key Takeaways

1. A signal is a *message* a process may react to — not a forced kill (except SIGKILL).
2. Job control = signals + the shell's bookkeeping (`jobs`, `fg`, `bg`).
3. Background jobs die with the terminal (SIGHUP) unless `nohup`/`disown` protect them.
4. `export` makes a variable heritable; `alias` is pre-run shorthand; dotfiles are the config convention.
