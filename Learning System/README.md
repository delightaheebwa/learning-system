# 📚 Zo + Obsidian Learning System — v3

A local-first, spaced-repetition learning system that turns Zo into a rigorous tutor inside Obsidian.

This is the **active learning system** for new sessions. It keeps a clean separation between live notes, reusable concept notes, session history, review history, and archive/reference material.

---

## Why this exists

AI explanations can feel like understanding even when they are not. This system is designed to prevent that by forcing retrieval, checking prerequisites, and preserving memory across sessions.

---

## Live system

The live system is the active working set:

- `Templates/💡 Learning Profile.md`
- `Templates/📚 Knowledge Base.md`
- `Sessions/`
- `Reviews/`
- `Concept Notes/`

Zo reads these before teaching, updates them after each session, and uses them to keep continuity.

---

## Protocol upgrade note

The active tutor protocol now uses stricter mastery rules:

- `pending_mastery` sits between `developing` and `mastered`
- first good answer = progress, not final mastery
- review sessions are capped at 5 concepts
- each review asks for confidence before evaluation
- every third session can become mixed/interleaved practice when the learner has enough stable concepts

---

## Archive policy

Archive content is reference-only.

Use `Archive/` for old or superseded material that should remain available but should not be treated as current learning history.

---

## Historical source

The current local implementation was adapted from the earlier Notion-based system called **Persistent AI Tutor** and the original local learning folder.

---

## Build status

- Local vault scaffold: complete
- Learning workflow: active
- Review tracking: active
- Obsidian-friendly folder structure: active
- Cloud mirror backup: intended via Google Drive sync

---

## Folder structure

```text
Learning System/
├── AGENTS.md
├── 🧭 SYSTEM PROMPT — AI Tutor.md
├── 📖 QUICKSTART.md
├── Templates/
│   ├── 💡 Learning Profile.md
│   ├── 📚 Knowledge Base.md
│   ├── 📝 Session Note Template.md
│   └── 🔄 Review Note Template.md
├── Sessions/
├── Reviews/
├── Concept Notes/
└── Archive/
```

---

## How the workflow runs

```text
Start a chat with Zo
  ↓
Paste the system prompt
  ↓
Zo confirms today’s date
  ↓
Zo reads the Learning Profile and Knowledge Base
  ↓
Zo runs due reviews first
  ↓
Zo surfaces open questions
  ↓
Zo teaches one concept at a time
  ↓
Zo writes the updated session note + knowledge base updates
  ↓
You save the outputs in Obsidian
```

---

## Obsidian + terminal workflow

This vault is designed to work well with the Obsidian CLI and a terminal-based habit:

- search notes quickly
- print templates or recent notes
- create session notes and review notes
- keep the Knowledge Base current

If you later want a cloud mirror, sync the same folder structure to Google Drive.

---

## Core principles

- **Clarity is not comprehension**
- **Prerequisites come first**
- **Retrieval beats recognition**
- **Open questions stay open until resolved**
- **The Knowledge Base is the persistent memory**

---

## Key files

- System Prompt: `🧭 SYSTEM PROMPT — AI Tutor.md`
- Quickstart: `📖 QUICKSTART.md`
- Learning Profile: `Templates/💡 Learning Profile.md`
- Knowledge Base: `Templates/📚 Knowledge Base.md`
- Session Notes: `Sessions/`
- Review Notes: `Reviews/`
- Concept Notes: `Concept Notes/`
- Archive: `Archive/`
