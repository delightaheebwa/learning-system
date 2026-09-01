# Mission: AI Engineering from Scratch (Rohit) — Foundations → Production

## Why

Build real AI systems end-to-end, from math foundations to shipped agents and production infrastructure — not just calling APIs. The curriculum is **AI Engineering from Scratch** by Rohit Ghumare (https://github.com/rohitg00/ai-engineering-from-scratch): 523 lessons, 20 phases, ~323h, Python/TypeScript/Rust, every lesson ships a reusable artifact (prompt/skill/agent/MCP). Full map: `Knowledge Wiki/wiki/AI Engineering from Scratch — Roadmap.md` and `Learning System/CURRICULUM.md`.

Rohit is **a source, not the source** — his roadmap gives direction and sequence; Scout gathers `docs/en.md` **plus** every link in its `## Further Reading` (§6) and curated `RESOURCES.md` entries, synthesizing primary sources (papers, docs, 3Blue1Brown, Stanford notes) rather than copying one narrative.

The learning loop (OpenWebUI: Scout → Tutor → Clerk) adapts to upstream changes: Scout re-fetches the live `phases/<phase>/<lesson>/docs/en.md` + Further Reading before each new lesson, surfaces drift (`SCOUT DIGEST: ⚠️ Upstream changed`), and the Tutor prefers the live combined sources.

## Current Phase

- **Catch-Up (Mission 0):** 80/20 reactivation of Phase 0 + Phase 1 L01–L06 (up to Probability & Distributions) — `in-progress`. Covers: 4-layer env stack, vectors/matrices/dot product, transforms/eigen, calculus substrate, probability core (PMF/PDF, CLT, softmax/log-sum-exp, cross-entropy).
- **Next real lesson after catch-up:** **Phase 1, Lesson 07 — Bayes' Theorem & Statistical Thinking** (per decision 2026-09-01 — jump, not Phase 0 L01). See `CURRICULUM.md` Mission 2.
- **Full map:** Missions 1–21 = Phases 0–19 (20 phases). Present for navigation; not a contract to finish end-to-end — after each phase, decide to go deeper / branch / build a learning system around a topic.

## Success looks like

- You can set up a reproducible AI env (uv/venv, verify.py, GPU/MPS check) and explain the 4-layer stack.
- You can implement vectors, matrices, `W@x+b`, PMF/PDF/softmax+NLL from scratch, and state why CLT makes normals dominate.
- Through later phases you climb: backprop from scratch → transformers → LLMs → agents → multimodal → infrastructure → ethics → capstones, shipping one artifact per lesson.
- Every artifact is built (not pasted) and verified (tests + evidence: command, cwd, exit code, artifact diff).

## Constraints

- Manual triggers; moderate pace; step-by-step + real-world analogies where they clarify without distorting (flexible, accuracy-first — soccer removed).
- Lessons sequential within a phase; phases in roadmap order. **Branching allowed** after a phase (deeper dive) — orthogonal to interleaving.
- Interleaving lives only in review flow (SRS shuffle + adjacency + question-type alternation) — never inside lessons/quizzes.
- Guided Socratic questioning (never pure Socratic — resolve confusion immediately).
- Push toward higher-order thinking (Bloom), phase-mapped; lessons short and completable.
- Advancement only after practice + retrieval check + Feynman explain-back (Learning Record).
- Local-first repo (`/home/user/learning-system` in container, `/home/delinux/learning-system` in WSL); OpenWebUI is control layer.
- OpenWebUI runs in **Docker Desktop on Windows side, separate from WSL** — base URL `http://host.docker.internal:3000` from WSL, not `localhost:3000`; `~/.git-credentials` lives in Open Terminal volume. See `OPENWEBUI.md`.
- Archived SWE Primary Colors roadmap is paused and strictly out of scope for Scout/Tutor grep (see `📦 Concept Archive.md`).

## Out of scope

- SWE Primary Colors roadmap (archived 2026-09-01 — `Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md`, wiki banner).
- Terminal System Monitor C project (archived 2026-08-24) and legacy Scripture Memory skill.
- Phase caching layer (ignored per decision 2026-09-01 — live fetch each lesson; no `Curriculum/cache/`).
