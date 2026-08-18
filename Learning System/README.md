# 📚 Learning System (Open WebUI)

A local-first, spaced-repetition learning system that turns your Open WebUI assistant into a rigorous tutor. It forces retrieval instead of passive reading, checks prerequisites, and preserves memory across sessions. Originally built with Zo + Obsidian; adapted for self-hosted Open WebUI.

## How it works

Say "swe", "ingest", "review", or anything like "teach me X" — the assistant runs the **`Skills/learning-system`** skill, which handles reviews, ingestion, and the writes below. The review gate is the `review_gate` tool (`minimax-m3`); teaching verification is the `fact_check` tool (`deepseek-v4-flash`). See `OPENWEBUI.md` at the repo root for the full setup.

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
