---
name: llm-wiki
description: "Build and maintain a Karpathy-style personal LLM wiki from notes, screenshots, clipped pages, and other source files. Use when the user says \"Ingest\", wants to dump notes or screenshots into a persistent wiki, asks to implement an LLM wiki, or wants the wiki queried, linted, cross-linked, or updated."
compatibility: Open WebUI (self-hosted)
metadata:
  home: https://github.com/delightaheebwa/learning-system
---

# LLM Wiki

## Overview

Turn raw sources into a persistent markdown wiki. Keep the source layer immutable, the wiki layer curated, and the index/log updated on every ingest.

## Standard layout

Use this workspace layout unless the user already has a better one:

- `Knowledge Wiki/raw/sources/` for source notes and clipped text
- `Knowledge Wiki/raw/assets/` for screenshots and other attachments
- `Knowledge Wiki/wiki/` for curated wiki pages
- `Knowledge Wiki/index.md` for the catalog of pages
- `Knowledge Wiki/log.md` for the chronological record
- `Knowledge Wiki/AGENTS.md` for the local schema and operating rules

## Ingest

When the user says `Ingest`, treat it as a source-processing job.

1. Preserve every raw source in `raw/sources/`.
2. Copy screenshots or other attachments into `raw/assets/` and link them from the source note.
3. Read the source carefully and extract:
   - core claims
   - entities
   - concepts
   - open questions
   - contradictions or weak spots
4. Update the wiki layer with small, focused pages.
5. Update `index.md` and append a log entry.
6. Keep unresolved questions visible instead of dropping them.

If the source is mostly screenshots, make a source note that embeds the images and then build the wiki pages from the extracted ideas.

## Wiki maintenance

- Keep raw sources immutable.
- Prefer short pages with one main idea.
- Use wiki links aggressively so related ideas connect.
- Revise existing pages instead of duplicating them.
- If new material contradicts an old claim, say so directly.
- If a concept appears often, give it its own page.

## Query

When the user asks a question about the wiki, read `index.md` first, then open the relevant pages, then synthesize the answer. Prefer explicit source references back to the wiki pages and raw sources.

## Lint

Periodically check for:

- orphan pages
- stale claims
- missing cross-links
- duplicate pages
- unresolved questions
- concepts that should become their own pages

## Output discipline

- Use markdown.
- Use relative links inside the wiki.
- Keep filenames stable and descriptive.
- When in doubt, create a note rather than losing information.

## Open WebUI adaptation

- The wiki lives in `Knowledge Wiki/` inside the repo — that is authoritative.
- In Open WebUI you may also mirror pages into Knowledge/Notes for retrieval, but the repo copy wins; update both, never just one.
- `index.md` and `log.md` are updated on every ingest (see the learning-system skill).
