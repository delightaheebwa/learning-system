# Learning System + Knowledge Wiki (Open WebUI)

A local-first, spaced-repetition learning system and Karpathy-style personal wiki,
originally built with Zo + Obsidian, now adapted to run in **self-hosted Open WebUI**.

- **Repo:** https://github.com/delightaheebwa/learning-system
- **Track:** SWE (Software Engineering Fundamentals) — Shell & Terminal, Makefiles, C, testing. AI Engineering (aie) archived.
- **Scheduling:** manual — say `swe` or `review` to run a review session; `ingest` to add new content.

## Layout

```
Learning System/          live state + history
  Core/                     💡 Learning Profile, 📚 Active Concepts (the review schedule),
                            📦 Concept Archive, 📖 Scripture Memory, templates
  Sessions/                 session notes
  Reviews/                  spaced-repetition review notes (+ Quality Gates/ verdicts)
  Concept Notes/            atomic concept pages
  Archive/                  reference-only history
  AGENTS.md                 behavioral conventions (consistency checks, git sync)
Knowledge Wiki/           curated wiki
  raw/sources/  raw/assets/  immutable raw layer
  wiki/                     short single-idea pages, aggressively cross-linked
  index.md  log.md  AGENTS.md
Skills/                   operating rules for the assistant (Open WebUI-tuned)
  learning-system/SKILL.md          ingest + review flows
  learning-review/SKILL.md          quality gate (verification of ingest output)
  learning-review/templates/        fixed review prompt template
  learning-review/model-config.json review model config
  learning-review/openwebui/        Open WebUI review-gate Tool + install guide
  llm-wiki/SKILL.md                 wiki building/maintenance rules
```

## Setup in Open WebUI (one time)

1. **Workspace → Knowledge**: optionally create a collection "Learning System Skills"
   and upload the three `Skills/*/SKILL.md` files so any chat can pull them.
2. **Workspace → Tools**: install the review gate — paste
   `Skills/learning-review/openwebui/review_gate.py` into a new Tool, set the
   Valves (base URL, API key, review model, optional repo path).
   Full guide: `Skills/learning-review/openwebui/README.md`.
3. **Chat**: trigger the system by saying `swe`, `ingest <content>`, or `review`.
   The assistant loads the state from this repo, follows `Skills/learning-system`,
   runs the gate after every ingest, and commits/pushes changes.

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory
