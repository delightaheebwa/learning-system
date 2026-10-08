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

## Provenance & trust order

The wiki is a **synthesis layer, not a source**. Trust flows *from* evidence:

> raw source > verified claim > labelled AI synthesis > learner note

Every page carries a provenance marker on its first lines:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

- `verified` — a claim checked against the cited source by a verifier
  (fact-check / review-gate) or a human.
- `synthesis` — AI synthesis from the source(s), not independently re-checked.
- `learner-note` — the learner's own understanding/notes.
- `unverified` — not yet classified (the default; treated as synthesis-quality,
  never authoritative).

**An unstamped page is treated as `unverified`.** A wiki page is never a source of
truth for a claim it does not cite; the citation is the evidence, the page is the
map. Corrections update the status in place and, when a claim changes, state the
change on the page. If a source is retracted, mark the dependent pages
`unverified` and re-check them — do not leave a corrected claim looking verified.

Lint / stamp: `python3 scripts/wiki_provenance.py [--check | --json | --stamp]`.

## Source of truth

This repo is authoritative. Any Open WebUI mirror (Knowledge base / Notes) is a convenience copy that must never be edited and pushed back; always update the repo copy first.