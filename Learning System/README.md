# 📚 Learning System (Open WebUI)

A local-first, spaced-repetition learning system that turns your Open WebUI assistant into a rigorous tutor. It forces retrieval instead of passive reading, checks prerequisites, and preserves memory across sessions. Originally built with Zo + Obsidian; adapted for self-hosted Open WebUI.

## How it works

Say "swe", "ingest", "review", or anything like "teach me X" — the assistant runs the **`Skills/learning-system`** skill, which handles reviews, ingestion, and the writes below. The review gate is the `review_gate` tool (runs after standalone ingests AND at lesson end when a lesson wrote wiki content); teaching verification is the `fact_check` tool; question batches (probe and end-of-lesson quiz) are audited by the `quiz_gate` tool before the learner sees them. Each model is set in one place in Open WebUI — see `OPENWEBUI.md` at the repo root for the full setup and the model-per-task table.

Agent behavioral conventions (consistency checks, git sync) live in `AGENTS.md`.

## Layout

- `Core/` — live state: `💡 Learning Profile.md`, `📚 Active Concepts.md` (the review schedule), `📦 Concept Archive.md`, `📖 Scripture Memory.md`, session/review templates
- `Sessions/` — session notes
- `Reviews/` — review notes
- `Concept Notes/` — atomic concept pages
- `Archive/` — reference-only historical material
- `Knowledge Wiki/` (sibling folder) — curated wiki pages, `index.md`, `log.md`
- `Skills/` (repo root) — Open WebUI-tuned operating rules: `learning-system`, `learning-review` (quality gate), `llm-wiki`

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory
