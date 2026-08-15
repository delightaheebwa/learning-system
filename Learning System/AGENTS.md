# Learning System — Agent Conventions

This folder + `Knowledge Wiki/` are the active learning system. The operating procedure lives in `file Skills/learning-system/SKILL.md` — that skill is the authority for review/ingest flows and file layout. This file holds only behavioral conventions.

## Multi-File Consistency Check

After any multi-file session (wiki page + index + log + Active Concepts + session note), re-read all touched files and verify:

- Wiki page created → in `Knowledge Wiki/index.md` under Concepts
- Ingest → `Knowledge Wiki/log.md` has today's entry
- Concept reviewed/added → `last_reviewed` = today in `Core/📚 Active Concepts.md`
- Concept reviewed/added → `next_review` calculated from current interval
- Wiki link in table → points to existing wiki page
- Session note → exists in `Sessions/` with today's date

Report ✅/❌ per item. Fix failures immediately.

## Git Sync

The learning system lives in the Git repo at the workspace root, tracked against GitHub remote `origin` (https://github.com/delightaheebwa/learning-system, public, branch `main`). Repo covers `Learning System/`, `Knowledge Wiki/`, and `Skills/` (the Open WebUI-tuned operating rules, including the review-gate tool).

After final edits in a session (consistency checks pass, writes complete), ALWAYS commit and push:

1. `cd /home/workspace && git add "Learning System" "Knowledge Wiki" "Skills"`
2. `git commit -m "<short summary of session changes>"`
3. `git push`

Verify with `git status` (clean) and `git log --oneline -1`. Never commit files outside the three directories.

### Git auth (automated)

Credentials are stored on this machine at `~/.git-credentials` (0600) with `credential.helper store` configured — `git push` works without interactive auth. If a push ever fails with auth errors, re-run the device-flow login once (`gh auth login` or a PAT stored the same way) to refresh the credential; no need to do it per-commit.