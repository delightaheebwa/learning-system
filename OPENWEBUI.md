# Open WebUI Setup & Operating Guide

This file is the canonical guide for running the learning system in **Open WebUI**
using native features. The repo at `/home/user/learning-system` (Open Terminal
workspace) is the source of truth for all state; Open WebUI holds the control
layer (skills, tools, model preset, prompts) that routes triggers.

## Architecture

| Concern | Open WebUI mechanism | Model — change it in ONE place |
| --- | --- | --- |
| Tutor (all flows) | the "Learning Tutor" **Model preset** | Workspace → Models → Learning Tutor → **base model** field |
| Slash-command triggers | **Prompts** (`/swe`, `/review`, `/ingest`, `/teach`, `/lesson`, `/continue`) | — |
| Teaching fact-check (load-bearing claims) | `fact_check` **Tool** (synchronous, independent) | Workspace → Tools → fact_check → ⚙ Valves → `fact_check_model` |
| Ingest quality gate (standalone ingest + lesson-end) | `review_gate` **Tool** (independent) | Workspace → Tools → review_gate → ⚙ Valves → `review_model` |
| Question-batch audit (probe + end-of-lesson quiz) | `quiz_gate` **Tool** (independent, pre-presentation) | Workspace → Tools → quiz_gate → ⚙ Valves → `quiz_model` |
| Repo + git | **Open Terminal** sandbox `/home/user/learning-system` | — |
| Web search / grounding | **Web Search** (SearXNG) | — |

### Models: one field per task

To change the model for any task, edit exactly one field in the Open WebUI UI
(table above). It takes effect on the next message. Nothing in this repo needs
to change — skills and prompts refer to models by role ("the reviewer model set
on the tool's Valve"), never by ID.

Rules:

- The tutor model is whatever the **Learning Tutor preset's base model** is set to.
- Each gate/fact-check model is whatever that **tool's Valve** is set to.
- Gates/fact-check must use a model *different* from the tutor so the tutor never grades its own output.
- `scripts/setup_openwebui.py` applies model values **only on first install** (or when a
  valve/base-model is empty). It reads each tool's current valve and the preset's current
  base model first and preserves any value already set in the UI — so re-running it after a
  skill edit never resets your models. The `--tutor-model` / `--review-model` /
  `--fact-check-model` / `--quiz-model` flags exist only for fresh installs.

## One-time setup

The setup script (`scripts/setup_openwebui.py` in this repo, or the steps below
reproduced manually) creates everything in Open WebUI:

1. **Workspace → Skills** — import the 4 `Skills/*/SKILL.md` files
   (`learning-system`, `learning-teach`, `learning-review`, `llm-wiki`). Their
   `name`/`description` frontmatter auto-fills the skill fields; the body is the
   content. These are loaded on demand by the model via `view_skill`, so they do
   not bloat every message.
2. **Workspace → Tools** — create `review_gate` (paste
   `Skills/learning-review/openwebui/review_gate.py`), `fact_check` (paste
   `Skills/learning-review/openwebui/fact_check.py`), and `quiz_gate` (paste
   `Skills/learning-review/openwebui/quiz_gate.py`). Set each tool's Valves:
   base URL (inside the Open WebUI container, `http://localhost:8080`), API key
   (Admin → API Keys), and the tool's model Valve.
3. **Workspace → Models** — create the **Learning Tutor** preset on your chosen
   base model:
   - System prompt: see below.
   - Skills: bind all 4.
   - Tools: enable `review_gate`, `fact_check`, and `quiz_gate`.
   - Capabilities: enable Web Search, Memory, Task Management.
4. **Workspace → Prompts** — create the 6 slash commands below.
5. **Open Terminal** — the repo is cloned at `/home/user/learning-system`; git
   push is wired (see `Learning System/AGENTS.md`).

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
  review_gate tool on the wiki content you wrote, then commit + push
- "teach me X" / "learn" / "study" / "lesson" / "continue" → teaching flow →
  view_skill "learning-teach"; verify load-bearing claims with the fact_check
  tool before presenting them, audit every question batch (probe and
  end-of-lesson quiz) with the quiz_gate tool before showing it to the learner,
  and run the review_gate tool on any wiki content or Active Concepts rows the
  lesson produced before finalizing
- wiki work (Ingest/queries/lint) → view_skill "llm-wiki"

Each gate/fact-check model is whatever is set on that tool's Valves; you are
running on the Learning Tutor preset's base model. To change any model, see the
model-per-task table in OPENWEBUI.md.
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
review_gate tool, then commit and push.
```

`/teach`
```
Teach me about: {{topic | text:placeholder="Topic to learn"}}

Load the learning-teach skill (view_skill "learning-teach"), then run the
probe → plan → teach loop. Verify load-bearing claims with the fact_check tool
before presenting them, and audit every question batch with the quiz_gate tool
before showing it.
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
- The review gate and fact-check are **different models** by design so the tutor
  does not grade its own output.
- Teaching verification is synchronous (`fact_check` tool returns a verdict
  before the tutor continues). Routine consistency (prerequisites,
  self-contradiction, coverage) is the tutor's own responsibility per
  `learning-teach`.

## Maintenance

- **Model changes:** UI only (see "Models: one field per task" above). No repo edits, no installer run, no flags.
- The repo is canonical. After editing any `Skills/*/SKILL.md`, re-import the
  changed skill in Open WebUI (or re-run the setup script) — skills do not
  auto-sync from the repo. Re-running the script is safe: it preserves your UI-chosen models.
- Re-run the setup script after adding/removing prompts, tools, or changing the
  system prompt.