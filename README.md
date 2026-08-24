# Learning System + Knowledge Wiki (Open WebUI)

A local-first, spaced-repetition learning system and Karpathy-style personal wiki,
built to run in **self-hosted Open WebUI** using native features (Skills, Tools,
a Model preset, and Prompts) with the repo as the source of truth.

- **Repo:** https://github.com/delightaheebwa/learning-system
- **Track:** SWE (Software Engineering Fundamentals) — Shell & Terminal, Makefiles, C, testing. AI Engineering (aie) archived.
- **Scheduling:** manual — say `/swe` or `/review` to run a review session; `/ingest` to add content; `/teach` / `/lesson` to learn.

## Layout

```
OPENWEBUI.md              setup + operating guide (read this first)
scripts/setup_openwebui.py  one-shot installer: skills, tools, model preset, prompts
Learning System/          live state + history
  Core/                     💡 Learning Profile, 📚 Active Concepts (the review schedule),
                            📦 Concept Archive, templates
  Sessions/  Reviews/  Concept Notes/  Archive/   session notes, review notes, atomic pages, history
  AGENTS.md                 behavioral conventions (consistency checks, git sync)
Knowledge Wiki/           curated wiki (raw/sources, raw/assets, wiki/, index.md, log.md, AGENTS.md)
Skills/                   operating rules, imported into Open WebUI as Skills
  learning-system/SKILL.md        review + ingest flows
  learning-teach/SKILL.md         probe → plan → teach loop (+ fact-check & quiz-audit subagent gates, lesson-end review gate)
  learning-review/SKILL.md        ingest quality gate (review-gate subagent task — standalone ingests AND lesson-end ingests)
  llm-wiki/SKILL.md               wiki building/maintenance rules
  learning-review/openwebui/      dormant legacy tools: review_gate.py · fact_check.py · quiz_gate.py · templates/
```

## Setup in Open WebUI (one time)

Run the installer, then start chatting:

```bash
OPENWEBUI_API_KEY=sk-... python3 scripts/setup_openwebui.py
```

That creates/updates: the 4 Skills, the **Learning Tutor** Model preset, and the
6 Prompts (`/swe`, `/review`, `/ingest`, `/teach`, `/lesson`, `/continue`).
Verification gates run as background subagent tasks (`delegate_task`) on Open
WebUI's **subagent default model** — set that to a model different from the
tutor. (The legacy `review_gate` + `fact_check` + `quiz_gate` Tools are dormant;
do not bind them to the preset.)
After install, models are changed in **one place each in the Open WebUI UI** —
see `OPENWEBUI.md`. The installer only applies model values on a **first
install** (or when empty); re-running it preserves your UI-chosen models.
See `OPENWEBUI.md` for the full walkthrough, the system prompt, and the prompt texts.

The repo must also be present in the Open Terminal workspace at
`/home/user/learning-system` (the model's file workspace) with git push wired —
see `OPENWEBUI.md` and `Learning System/AGENTS.md`.

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory