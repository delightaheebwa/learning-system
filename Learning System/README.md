# 📚 Zo + Obsidian Learning System

A local-first, spaced-repetition learning system that turns Zo into a rigorous tutor. It forces retrieval instead of passive reading, checks prerequisites, and preserves memory across sessions.

## How it works

Say a track ("aie", "swe"), "ingest", "review", or anything like "teach me X" — Zo runs the **`Skills/learning-system`** skill, which handles reviews, ingestion, and the writes below. Scripture memory runs through `Skills/scripture-memory` ("meditate").

Agent behavioral conventions (consistency checks, git sync) live in `AGENTS.md`.

## Layout

- `Core/` — live state: `💡 Learning Profile.md`, `📚 Active Concepts.md` (the review schedule), `📦 Concept Archive.md`, `📖 Scripture Memory.md`, session/review templates
- `Sessions/` — session notes
- `Reviews/` — review notes
- `Concept Notes/` — atomic concept pages
- `Archive/` — reference-only historical material
- `Knowledge Wiki/` (sibling folder) — curated wiki pages, `index.md`, `log.md`

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory
