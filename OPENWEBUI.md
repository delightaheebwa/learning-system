# Open WebUI Setup & Operating Guide

This file is the canonical guide for running the learning system in **Open WebUI**
using native features. The repo at `/home/user/learning-system` (Open Terminal
workspace) is the source of truth for all state; Open WebUI holds the control
layer (skills, subagents, model preset, prompts) that routes triggers.

> **2026-08-25 — tools → subagents:** the three gate tools (`fact_check`,
> `review_gate`, `quiz_gate`) were retired after persistent HTTP 500 failures.
> All verification now runs as **background subagent tasks** (`delegate_task`).
> The Python tool files remain in `Skills/learning-review/openwebui/` as dormant
> fallbacks; their fixed prompt templates live on inside the skills below.

## Architecture

| Concern | Open WebUI mechanism | Model — change it in ONE place |
| --- | --- | --- |
| Tutor (all flows) | the "Learning Tutor" **Model preset** | Workspace → Models → Learning Tutor → **base model** field |
| Slash-command triggers | **Prompts** (`/swe`, `/review`, `/ingest`, `/teach`, `/lesson`, `/continue`) | — |
| All verification gates (fact-check · quiz audit · ingest review) | **background subagents via `delegate_task`** — batched, independent | Open WebUI **subagent default model** (Settings → subagents) |
| Repo + git | **Open Terminal** sandbox `/home/user/learning-system` | — |
| Web search / grounding | **Web Search** (SearXNG) | — |

### Models: one field per task

To change the model for any task, edit exactly one field in the Open WebUI UI
(table above). It takes effect on the next message. Nothing in this repo needs
to change — skills and prompts refer to models by role ("the subagent default
model"), never by ID.

Rules:

- The tutor model is whatever the **Learning Tutor preset's base model** is set to.
- Every gate runs on the **subagent default model** configured in Open WebUI.
- Gates must use a model *different* from the tutor so the tutor never grades its own output.

## One-time setup

The setup script (`scripts/setup_openwebui.py` in this repo, or the steps below
reproduced manually) creates everything in Open WebUI:

1. **Workspace → Skills** — import the 4 `Skills/*/SKILL.md` files
   (`learning-system`, `learning-teach`, `learning-review`, `llm-wiki`). Their
   `name`/`description` frontmatter auto-fills the skill fields; the body is the
   content. These are loaded on demand by the model via `view_skill`, so they do
   not bloat every message.
2. **Subagent model** — set Open WebUI's **subagent default model** to a model
   different from the tutor (this is the independent gate reviewer). The skills'
   fixed subagent prompts carry the verification rules — no tools are needed.
3. **Workspace → Models** — create the **Learning Tutor** preset on your chosen
   base model:
   - System prompt: see below.
   - Skills: bind all 4.
   - Capabilities: enable Web Search, Memory, Task Management.
4. **Workspace → Prompts** — create the 6 slash commands below.
5. **Open Terminal** — the repo is cloned at `/home/user/learning-system`; git
   push is wired (see `Learning System/AGENTS.md`).

*(Legacy, dormant: the `fact_check` / `review_gate` / `quiz_gate` Tools and their
setup in `scripts/setup_openwebui.py`. Do not bind them to the preset; kept only
as fallback if subagents ever need replacing.)*

### Learning Tutor — system prompt

```
You are the Learning Tutor for Delight's spaced-repetition learning system.

The learning system's live state lives in the Git repo at
/home/user/learning-system (Open Terminal). Read and write files there with the
terminal, and commit + push at the end of every session (see
Learning System/AGENTS.md).

Routing (when a trigger fires, load the matching skill with view_skill and
follow it — do not improvise the workflow):
- "swe" / "review" → review flow → view_skill "learning-system"
- "ingest <content>" → ingest flow → view_skill "learning-system", then run the
  review-gate subagent task on the wiki content you wrote, then commit + push
- "teach me X" / "learn" / "study" / "lesson" / "continue" → teaching flow →
  view_skill "learning-teach"; batch load-bearing claims and verify them via a
  fact-check subagent before presenting them, audit every question batch (probe
  and end-of-lesson quiz) via a quiz-audit subagent before showing it to the
  learner, and run a review-gate subagent task on any wiki content or Active
  Concepts rows the lesson produced before finalizing
- wiki work (Ingest/queries/lint) → view_skill "llm-wiki"

All verification gates run as background subagent tasks (`delegate_task`) on
Open WebUI's subagent default model; you run on the Learning Tutor preset's base
model. To change any model, see the model-per-task table in OPENWEBUI.md.
```

### Prompts

`/swe`
```
Run a review session on the swe track. Load the learning-system skill
(view_skill "learning-system"), then follow its Review flow.
```

`/review`
```
Run a review session. Load the learning-system skill (view_skill
"learning-system"), then follow its Review flow.
```

`/ingest`
```
Ingest the following content into the learning system:
{{content | textarea:placeholder="Paste the content or a URL to ingest"}}

Load the learning-system skill (view_skill "learning-system"), follow its
Ingest flow, read the wiki pages you wrote via the terminal, run the
review-gate subagent task, then commit and push.
```

`/teach`
```
Teach me about: {{topic | text:placeholder="Topic to learn"}}

Load the learning-teach skill (view_skill "learning-teach"), then run the
probe → plan → teach loop. Batch load-bearing claims and verify them via a
fact-check subagent before presenting them, and audit every question batch with
a quiz-audit subagent before showing it.
```

`/lesson`
```
Run the next curriculum lesson. Load the learning-teach skill (view_skill
"learning-teach"), determine the next lesson from Learning System/CURRICULUM.md,
and teach it.
```

`/continue`
```
Continue the current lesson where we left off. Load the learning-teach skill
(view_skill "learning-teach").
```

## Operating notes

- Skills are lazy-loaded: only the `name` + `description` manifest is in
  context; the model calls `view_skill` to load the full instructions. Keep each
  skill's `description` crisp — it is what routes the model to the right skill.
- The gate subagent runs the **subagent default model** — a different model from
  the tutor by design, so the tutor does not grade its own output.
- Verification is asynchronous: batch claims/questions/content into ONE
  subagent task per gate, dispatch via `delegate_task`, and fold the verdicts in
  before presenting to the learner or finalizing an ingest. The fixed prompt
  templates for each gate live inside the skills (`learning-teach`,
  `learning-review`) — do not weaken them.
- Routine consistency (prerequisites, self-contradiction, coverage) is the
  tutor's own responsibility per `learning-teach`.

## Maintenance

- **Model changes:** UI only (see "Models: one field per task" above). No repo edits, no installer run, no flags.
- **Subagent default model:** change it in Open WebUI's subagent settings; every gate picks it up on the next task.
- The repo is canonical. After editing any `Skills/*/SKILL.md`, re-import the
  changed skill in Open WebUI (or re-run the setup script) — skills do not
  auto-sync from the repo. Re-running the script is safe: it preserves your UI-chosen models.
- Re-run the setup script after adding/removing prompts or changing the system prompt.