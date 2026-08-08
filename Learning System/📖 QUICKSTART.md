# 📖 QUICKSTART — Learning System v3

Use this to start and maintain a session in Obsidian.

---

## Before you begin

Make sure these files exist in the vault:

- `Learning System/🧭 SYSTEM PROMPT — AI Tutor.md`
- `Learning System/Templates/💡 Learning Profile.md`
- `Learning System/Templates/📚 Knowledge Base.md`

The rest of the vault structure should be present too:

- `Learning System/Sessions/`
- `Learning System/Reviews/`
- `Learning System/Concept Notes/`
- `Learning System/Archive/`

---

## Step 1 — Start a new chat with Zo

Open Zo and start a new learning conversation.

---

## Step 2 — Activate the learning system

You have a conditional rule set up: whenever you express an intent to learn, Zo automatically loads the tutor protocol. Just say what you want to learn — e.g., "I want to review directional derivatives" or "Teach me about probability distributions" — and Zo handles the rest.

No pasting, no manual setup. Zo reads the system prompt, your Learning Profile, and the Knowledge Base automatically.

---

## Step 3 — Confirm today’s date

Zo should ask you to confirm the current date first.

---

## Step 4 — Let Zo load your memory files

Zo reads:

- `Templates/💡 Learning Profile.md`
- `Templates/📚 Knowledge Base.md`

If the Learning Profile is still empty or incomplete, Zo should run the learner diagnostic first.

---

## Step 5 — Teach one concept at a time

For each concept, Zo should:

1. explain it clearly
2. connect it to your analogy domain
3. ask a direct recall question
4. ask for confidence before evaluation
5. evaluate honestly
6. give one applied practice scenario
7. close by linking to the next concept

Do not accept “I get it” without proof.

If a concept only gets one good answer, Zo should treat that as `pending_mastery`, not final mastery.

---

## Step 6 — Handle reviews carefully

Zo should:

- review due concepts before new teaching
- handle at most 5 review concepts in one session (8 in catch-up mode)
- put overflow into the review queue
- automatically activate catch-up mode when the queue exceeds 8 items
- use novel questions for developing or `pending_mastery` concepts

Every third session can become mixed practice once the learner has enough stable mastered concepts. Check `STATUS.md` for the current review load and scheduled reviews.

---

## Step 7 — Save the end-of-session outputs

At the end of a session, Zo should produce:

- an updated Knowledge Base
- a new Session Note
- any needed Review Notes

Save them in:

- `Learning System/Templates/📚 Knowledge Base.md`
- `Learning System/Sessions/Session — [Topic] — [Date].md`
- `Learning System/Reviews/Review — [Concept] — [Date].md`

---

## Step 8 — Keep the vault tidy

Use `Concept Notes/` for reusable concept pages.
Use `Archive/` for old or superseded material that should remain available but not active.

---

## Step 9 — Mirror backup

If you want cloud backup, mirror the full `Learning System/` folder to Google Drive with the same structure.

---

## Obsidian CLI workflow

A good terminal workflow is:

- search for a concept or note
- print the relevant note
- create or update the session/review note
- keep the Knowledge Base current

If you want, I can next help you define a concrete Obsidian CLI command workflow for this vault.
