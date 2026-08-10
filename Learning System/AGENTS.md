# Learning System Workspace Notes

This folder contains the active Obsidian-style learning system for Zo.

## Current structure

- `🧭 SYSTEM PROMPT — AI Tutor.md` is the operating protocol
- `Templates/💡 Learning Profile.md` stores learner preferences
- `Templates/📚 Knowledge Base.md` stores the persistent concept memory
- `Sessions/` stores completed learning sessions
- `Reviews/` stores spaced-repetition review notes
- `Concept Notes/` stores reusable atomic concept pages
- `Archive/` stores reference-only historical material

## Maintenance rules

- Keep the live system local-first and Obsidian-friendly
- Preserve existing note names where possible
- Update the Knowledge Base after sessions and reviews
- Keep archive content separate from active learning history
- Prefer small, targeted edits to existing notes instead of wholesale renames
- The active tutor protocol is now v3: use `pending_mastery`, ask for confidence before evaluation, cap review sessions at 5 concepts, and use mixed practice periodically to improve transfer

## Version control

- This folder + `Knowledge Wiki/` are tracked in the Git repo at the workspace root, pushed to GitHub `delightaheebwa/learning-system` (public, branch `main`).
- After any session that edits these folders, commit and push (see the Git Sync rule): `git add "Learning System" "Knowledge Wiki" && git commit && git push`.
- The root `.gitignore` allowlists only these two directories — never commit anything else.

## Handwritten notes ingestion (vision delegation)

When the user shares images of handwritten notes (or any image as learning source material) during an ingest session, the active agent delegates text extraction to the Mimo v2.5 custom model via the Zo Ask API — regardless of whether the active model has vision. See the **Handwritten Notes Ingest — Mimo v2.5 Vision Delegation** rule for the exact steps and prompt.

- Model: `byok:77723e9c-69c1-4fb1-9284-045c4e3f0ee8` (Mimo v2.5)
- Endpoint: `POST https://api.zo.computer/zo/ask` with `Authorization: Bearer $ZO_CLIENT_IDENTITY_TOKEN`
- Mimo transcribes verbatim (light cleanup only); the active agent does concept extraction, wiki updates, and the rest of the ingest pipeline.
