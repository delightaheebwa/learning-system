# Knowledge Wiki — Local Schema & Operating Rules

This file documents how the wiki layer of this repo is structured and maintained. The canonical build/maintenance rules live in `Skills/llm-wiki/SKILL.md`; this file is the local contract for the files in this folder.

## Layout

```
raw/sources/   immutable raw layer — source notes and clipped text, never edited after ingest
raw/assets/    screenshots and attachments, linked from the source notes
wiki/          curated wiki pages — short, single-idea pages, aggressively cross-linked
index.md       catalog of all wiki pages (updated on every ingest)
log.md         chronological record of ingests (one entry per ingest)
```

## Rules

- **Raw sources are immutable.** Once ingested into `raw/sources/`, a source is never rewritten; corrections land in the wiki layer or a new source note.
- **Wiki pages are short** — one main idea per page. Split, don't bloat.
- **Cross-link aggressively.** Related ideas connect with `[[wikilinks]]` / relative markdown links.
- **Revise, don't duplicate.** If a concept already has a page, update it with genuinely new material instead of creating a near-copy.
- **Contradictions are stated directly.** If new material conflicts with an old claim, say so on the page.
- **Keep unresolved questions visible.** Never drop an open question during maintenance.
- **index.md and log.md are updated on every ingest** (per `Skills/learning-system/SKILL.md`).

## Source of truth

This repo is authoritative. Any Open WebUI mirror (Knowledge base / Notes) is a convenience copy that must never be edited and pushed back; always update the repo copy first.