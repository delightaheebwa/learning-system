# Knowledge Wiki schema

## Purpose

Maintain a Karpathy-style persistent wiki from raw sources.

## Layout

- `raw/sources/` holds immutable source notes.
- `raw/assets/` holds screenshots and other attachments.
- `wiki/` holds curated pages.
- `index.md` catalogs the wiki.
- `log.md` records ingests, queries, and lint passes.

## Operating rules

- Preserve raw sources.
- Update the wiki incrementally.
- Create or revise pages instead of duplicating them.
- Add open questions when the source is ambiguous.
- Link related pages with `[[wikilinks]]`.
- Update `index.md` and `log.md` on every ingest.
- **MANDATORY: Consistency verification** — After any wiki write, verify that:
  - Every new wiki page appears in `index.md` under Concepts (using the `[[Page name]]` format).
  - `log.md` has an entry for today with the concepts that were added.
  - If missing, fix immediately — do not leave the wiki in an inconsistent state.
