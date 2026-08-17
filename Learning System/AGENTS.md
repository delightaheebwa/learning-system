# Learning System — Agent Conventions

This folder + `Knowledge Wiki/` are the active learning system. The operating procedure lives in `file Skills/learning-system/SKILL.md` — that skill is the authority for review/ingest flows and file layout. This file holds only behavioral conventions.

## Repo location

The working copy lives at **`/home/user/learning-system`** inside the Open WebUI **Open Terminal** workspace (a persistent container volume). GitHub (https://github.com/delightaheebwa/learning-system) is the durable source of truth; this working copy is where the model reads and writes, and git is the sync mechanism.

## Multi-File Consistency Check

After any multi-file session (wiki page + index + log + Active Concepts + session note), re-read all touched files and verify:

- Wiki page created → in `Knowledge Wiki/index.md` under Concepts
- Ingest → `Knowledge Wiki/log.md` has today's entry
- Concept reviewed/added → `last_reviewed` = today in `Core/📚 Active Concepts.md`
- Concept reviewed/added → `next_review` calculated from current interval
- Wiki link in table → points to existing wiki page
- Session note → exists in `Sessions/` with today's date

Teaching sessions additionally verify (per `Skills/learning-teach/SKILL.md`):

- Lesson file → exists in `Learning System/Lessons/` with today's date
- Learning record → numbered `highest + 1` in `Learning System/Learning Records/`, with Bloom level + Feynman explain-back in Evidence
- Curriculum lesson advanced → only if practice + retrieval pass + Feynman pass; status in `Learning System/CURRICULUM.md` matches reality
- New concepts from teaching → `developing` with `last_reviewed` = today, `next_review` = +3d
- Glossary additions → promoted only with user approval

Report ✅/❌ per item. Fix failures immediately.

## Git Sync

The working copy is the Git repo at `/home/user/learning-system`, tracked against GitHub remote `origin` (https://github.com/delightaheebwa/learning-system, public, branch `main`). Repo covers `Learning System/`, `Knowledge Wiki/`, and `Skills/` (the Open WebUI-tuned operating rules, including the review-gate and fact-check tools), plus `OPENWEBUI.md` and `scripts/`.

After final edits in a session (consistency checks pass, writes complete), ALWAYS commit and push:

1. `cd /home/user/learning-system && git add "Learning System" "Knowledge Wiki" "Skills"`
2. `git commit -m "<short summary of session changes>"`
3. `git push`

Verify with `git status` (clean) and `git log --oneline -1`. Never commit files outside the three directories (plus `OPENWEBUI.md`, `scripts/` when they change).

### Git auth (automated)

Credentials are stored in the Open Terminal sandbox home at `~/.git-credentials` (0600) with `credential.helper store` configured — `git push` works without interactive auth. If a push ever fails with auth errors, refresh the credential: re-run the one-time setup (write the PAT to `~/.git-credentials` + `git config --global credential.helper store`).