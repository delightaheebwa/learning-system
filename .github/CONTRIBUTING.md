# Contributing

Thanks for wanting to help. This project spans **two repositories** that together
form one learning system. Knowing which repo a change belongs in is the single
most important thing before you open anything.

## The two-repo map

| Repo | Role | Holds state? |
|---|---|---|
| [`delightaheebwa/learning-system`](https://github.com/delightaheebwa/learning-system) (you are here) | The product and the single source of truth. Learning state, skill files, the Open WebUI installer, and the deterministic gate. | **Yes** — `Learning System/`, `Knowledge Wiki/` |
| [`delightaheebwa/learning-pi`](https://github.com/delightaheebwa/learning-pi) | The **pi control layer**: skills, subagents, prompts, the verification gate, and audit scripts for the [pi](https://github.com/) runtime. | **No** |

State lives in **this** repo and never moves. `learning-pi` installs as an overlay
(`~/learning-pi/install.sh ~/learning-system` symlinks its `.pi/` into the state
checkout and git-excludes it), so changes to the pi layer never leak into this
repo and vice versa.

## Where to ask

- **Questions, ideas, show-and-tell, build-log chatter** → [Discussions](https://github.com/delightaheebwa/learning-system/discussions). Use it first.
- **Bugs, concrete feature requests, tracked work** → [Issues](https://github.com/delightaheebwa/learning-system/issues).
- **Security problems** → follow [`SECURITY.md`](SECURITY.md). Do **not** open a public issue.

Rule of thumb: if it needs a decision or an owner, it is an issue; if it needs a
conversation, it is a discussion.

## Before you open a PR

1. Read [`AGENTS.md`](AGENTS.md). It is the authoritative context for anyone
   changing this repo, and it documents the invariants below. PRs that break them
   will be asked to change.
2. Read [`OPENWEBUI.md`](OPENWEBUI.md) for the architecture if you are touching
   skills, prompts, models, or the gate.
3. Target the `main` branch. Keep PRs small and single-purpose.

## What changes where

Changes reach the live system through different mechanisms — route accordingly:

- **Skill markdown** (`Skills/*/SKILL.md`) — behavior. These do **not** auto-sync;
  they take effect only after re-import in Open WebUI or a re-run of the installer.
  Say so in your PR.
- **Python** (`scripts/`, the gate Filter) — install/enforce. Keep the
  `gate_schema.py` envelope contracts stable; any envelope change must be mirrored
  in `gate_pipe.py`, the installer payload, and the `GATE:` prompts.
- **State** (`Learning System/`, `Knowledge Wiki/`) — live data. Follow the
  consistency-check and git-sync rules in `Learning System/AGENTS.md`.

## Conventions

- **No comments in code unless asked.** Match the style of the file you edit.
- **Never commit** secrets, `Learning System/.tmp/`, or `Pending Ingest.json`
  (the latter two are gitignored).
- **Commit the tracked dirs**: `Learning System/`, `Knowledge Wiki/`, `Skills/`,
  plus the root docs and `scripts/`/`infra/` when they change.
- The gate Pipe is load-bearing. Do not weaken it to make a test pass.

## pi-layer specifics

If your change touches `learning-pi`:

- Editing `.pi/` (`extensions/`, `skills/`, `agents/`, `APPEND_SYSTEM.md`) does
  **not** affect a running pi session. Run `/reload` (or restart pi) and confirm
  the new behavior before claiming it works.
- Update [`AUDIT-ROADMAP.md`](https://github.com/delightaheebwa/learning-pi/blob/main/AUDIT-ROADMAP.md)
  when a staged item lands.

## Verifying

There is **no build, test runner, or linter** wired into this repo. Verify the
way `AGENTS.md` describes: re-read the edited `SKILL.md`, run
`python3 -m py_compile` where Python changed, run `python3 -m unittest
scripts.ops_test` for `ops.py` changes, and state any re-import or installer step
your change requires.

By contributing, you agree to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).
