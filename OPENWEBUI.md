# Open WebUI Setup & Operating Guide

This file is the canonical guide for running the learning system in **Open WebUI**
using native features. The repo at `/home/user/learning-system` (Open Terminal
workspace) is the source of truth for all state; Open WebUI holds the control
layer (skills, subagents, model presets, prompts, gate Pipe) that routes triggers.

> **2026-08-25 — tools → subagents:** the three gate tools (`fact_check`,
> `review_gate`, `quiz_gate`) were retired after persistent HTTP 500 failures.
> All verification now runs as **foreground subagent tasks** (`delegate_task`,
> `background:false`) with Pydantic envelope validation (`gate_schema.py`).
> The Python tool files remain in `Skills/learning-review/openwebui/` as dormant
> fallbacks; fixed verifier prompts live in the global `subagents.system_prompt`
> (keyed by `GATE:`). Enforcement is via the gate **Pipe/Filter**
> `Skills/learning-review/openwebui/gate_pipe.py` (see "Gate enforcement").

## Architecture

| Concern | Open WebUI mechanism | Model — change it in ONE place |
| --- | --- | --- |
| Scout (exploration) | **Scout** preset | Workspace → Models → Scout → base model |
| Tutor (probe/plan/teach) | **Learning Tutor** preset | Workspace → Models → Learning Tutor → base model |
| Clerk (ingest + review) | **Clerk** preset | Workspace → Models → Clerk → base model |
| Slash-command triggers | **Prompts** (`/review`, `/ingest`, `/teach`, `/lesson`, `/continue`) — `/swe` is legacy (SWE archived; redirects to AIEFS) | — |
| Deterministic gate | **Gate Pipe** Filter (`gate_pipe.py` + `gate_schema.py`) — outlet, priority 10, bound to Tutor + Clerk | Function Valves (priority, max_retries, digest_ttl_days) |
| Fixed verifier prompts | Global **subagents.system_prompt** (keyed `GATE:fact_check` / `GATE:quiz_audit` / `GATE:review`) | Settings → Subagents |
| Repo + git | **Open Terminal** sandbox `/home/user/learning-system` (container) vs `/home/delinux/learning-system` (WSL). Docker Desktop runs Windows-side, separate from WSL — WSL must use `http://host.docker.internal:3000` | — |
| Ephemeral Scout digest | `Learning System/.tmp/context-<chat_id>-<slug>.json` (gitignored, 7-day TTL) — now includes `rohit_hash` + `external_refs` + `lang_recommendation` + `roadmap_sha` + `fetched_at`; adaptive re-fetch; `📦 Concept Archive.md` strictly out of scope | — |
| Web search / grounding | **Web Search** (SearXNG) — Scout uses it to fetch `docs/en.md` + Further Reading external refs live (Rohit is a source, not the source) | — |

### Models: one field per task

To change the model for any task, edit exactly one field in the Open WebUI UI
(table above). It takes effect on the next message. Nothing in this repo needs
to change — skills and prompts refer to models by role ("the subagent default
model"), never by ID.

Rules:

- Each preset's base model is whatever its preset's `base_model_id` is set to.
- The gate Pipe is bound only to Tutor and Clerk; Scout is exempt.
- Gates must use a model *different* from the Tutor so the tutor never grades its own output (configure subagent default model separately).

### Gate enforcement (Pipe)

The gate Pipe (`gate_pipe.py`, outlet) blocks before render:

- **Scout digest for new lessons:** a Tutor turn responding to a new `/teach`/`/lesson` (no `Lessons/Lesson — <slug> — *.md` yet) requires a `.tmp/context-<chat>-<slug>.json` digest and a prior `Scout` message in the same chat (7-day TTL, slug must match trigger). Resume of an existing lesson grounds in `Lessons/` + `Sessions/` and bypasses this check, so stale/missing digests don't confuse Tutor.
- **Receipts:** every non-trivial Tutor (claims) and Clerk (wiki) message requires a foreground `GATE:*` envelope dispatched via `delegate_task` (`background:false`) with a child internal chat (`meta.parent_message_id == draft.id`) whose task parses as the envelope schema and whose assistant output parses as the verdict schema covering every `claims[].id`. Retry cap 2 per user turn (durably counted in `Chat.meta.gate_state`); after cap, `⛔ Withheld` banner. Block codes: `NO_SCOUT_CONTEXT`, `NO_DELEGATION`, `MALFORMED_ENVELOPE`, `MALFORMED_VERDICTS`.

## One-time setup

The setup script (`scripts/setup_openwebui.py`) creates everything:

1. **Workspace → Skills** — import the 4 `Skills/*/SKILL.md` files.
2. **Functions → Gate Pipe** — installs `gate_pipe` (inlined `gate_schema.py`) as Filter type, priority 10, bound to Tutor + Clerk.
3. **Subagent system prompt** — sets global `subagents.system_prompt` to the `GATE:*` templates.
4. **Workspace → Models** — creates **Scout**, **Learning Tutor**, **Clerk** presets (each with its system prompt, capabilities, and skill bindings; Tutor/Clerk have `filterIds: [gate_pipe]`).
5. **Workspace → Prompts** — creates the 6 slash commands below.
6. **Open Terminal** — repo at `/home/user/learning-system`; git push is wired.

*(Legacy, dormant: the `fact_check` / `review_gate` / `quiz_gate` Tools and their setup. Do not bind them.)*

### Preset system prompts (summary)

- **Scout:** gather MISSION/CURRICULUM/RESOURCES + relevant Active Concepts rows (do not grep SWE archive) + live `phases/<phase>/<lesson>/docs/en.md` **plus every URL in its `## Further Reading`** (Rohit is a source, not the source; synthesize); hash and surface drift (`SCOUT DIGEST: ⚠️ Upstream changed`), capture `lang_recommendation` (Python/TS/Rust per header); write `.tmp/context-<chat>-<slug>.json` + post `SCOUT DIGEST:` in chat. Special: Mission 0 Catch-Up (P0+P1.01–06, 80/20) synthesizes 5 strands. No phase cache (live fetch).
- **Learning Tutor:** assume Scout digest (now includes `rohit_hash`+`external_refs`+`lang`+`roadmap_sha`) / session context or existing `Lessons/` file; do not gather context or write wiki pages; verify claims via foreground `GATE:fact_check` (cite both Rohit + external refs) before presenting; respect per-lesson language (Python/TS/Rust); handoff to Clerk via `Pending Ingest.json` at lesson end. Order: Mission 0 Catch-Up (in-progress) → Phase 1 L07.
- **Clerk:** reads `Pending Ingest.json`, writes wiki/Active Concepts, dispatches `GATE:review`, applies fixes, cleans digest and marker, commits.

**Environment note (Docker Desktop Windows-side, separate from WSL):** WSL must target `http://host.docker.internal:3000`; workspace repo at `/home/user/learning-system` (container) vs `/home/delinux/learning-system` (WSL). See `Learning System/MISSION.md`.

### Prompts

`/swe` — **Legacy** (SWE archived 2026-09-01) — redirects to AIEFS review. Use `/review` instead.
`/review` — Run a review session on the **AIEFS** track (SWE `swe` is archived). Load `learning-system`, follow Review flow.
`/ingest` — `Ingest the following content: {{content}} — Switch to Clerk, load learning-system, follow Ingest flow, then commit and push.`
`/teach` — `Teach me about: {{topic}} — Switch to Scout to gather context, then to Learning Tutor, load learning-teach, run probe → plan → teach. Gate enforces foreground GATE envelopes.`
`/lesson` — `Run the next curriculum lesson. Switch to Scout to gather context for the next lesson, then to Learning Tutor, load learning-teach.`
`/continue` — `Continue the current lesson where we left off. Load learning-teach. If the lesson file exists, it is the source of truth — no Scout digest needed.`
`/pause` — `Pause the current lesson where we are. Switch to the Learning Tutor preset, load learning-teach, run the pause protocol (exit ticket for today's checkpoints only, partial lesson file with Status + Resume-from pointer, partial Pending Ingest.json), then hand to Clerk with /ingest to bank today's progress. Partial ingests keep the lesson in-progress and the Scout digest alive; curriculum row becomes in-progress (paused N/M).`

## Operating notes

- Skills are lazy-loaded via `view_skill`; keep each `description` crisp.
- Verification is synchronous per step: one foreground `delegate_task` per gate, fold verdicts in before presenting. Fixed prompts live in global `subagents.system_prompt`; do not weaken them.
- Scout digests are ephemeral (`.tmp/`, gitignored). `Clerk` deletes the consumed digest and clears `Pending Ingest.json` on success. Orphans older than 7 days are swept on the next Tutor/Clerk inlet (the Filter runs only on those presets; Scout is exempt).
- Routine consistency (prerequisites, self-contradiction, coverage) is the tutor's own responsibility.

## Maintenance

- **Model changes:** UI only (see table). No repo edits, no installer flags.
- **Gate tuning:** Function Valves for `gate_pipe` (priority, max_retries, digest_ttl_days) + global `subagents.system_prompt`.
- The repo is canonical. After editing any `Skills/*/SKILL.md`, re-import the changed skill in Open WebUI (or re-run the setup script) — skills do not auto-sync. Re-running preserves UI-chosen models.
- Re-run the setup script after adding/removing prompts or changing system prompts. It is idempotent.
