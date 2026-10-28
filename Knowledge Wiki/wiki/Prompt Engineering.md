<!-- provenance: status=synthesis (`## My understanding` block status=learner-note) | source=raw/sources/2026-10-28 - prompt-engineering - rohit.md + anthropic.md + cot-wei.md + openai.md + dair.md + dair-cot.md + dair-settings.md + prompt-engineer.md + claude-best-practices.md | verified-by=— | date=2026-10-28 -->

# Prompt Engineering

**Insight:** a prompt executes nothing — it conditions each next-token distribution. Every ambiguity the text leaves is a fork the model must sample from, so a vague prompt spreads probability mass over many candidate continuations while a precise one deletes arms and piles the same mass onto a few survivors. "The model takes your prompt literally" therefore means the model takes *the conditioning the text implies* seriously, not that it obeys instructions. The half of the discipline this model cannot yet do is the ruler: without an eval harness that holds fixed cases and re-runs on every change, "desired quality" has no measurement, and a prompt change can silently regress a case that already passed.

## My understanding

> status=learner-note — the learner's own words, verbatim, preserved in order. Never paraphrased, polished, or merged below. Versions are the learner's; annotations between them are the AI's.

**Version 1** — 2026-10-28, first closed-book model (handwritten notes, transcribed and confirmed; one unreadable word filled in by the learner as "clarity"; confidence `sure`):

> "Prompt engineering is very much alive. It has just become table stakes for all AI engineers. The usual structure is role, context, constraints, output. Prompt engineering consists of clarity, patterns, anti-patterns, context window, constraints, role, output format. Models take your prompts literally — here we need to be precise. Prompt engineering is the process of tweaking the prompt in order to get the desired quality results."

**Breaking case** (annotation — not the learner's words, recorded between versions so the evolution scar stays visible):

- Two mechanism presses on *"models take your prompts literally"* produced only circular chains — first a "generic prompt → generic output" restatement with no distributional middle, then the banned word reused with a model-as-decider agency picture. Both failed; the first was tagged `sure`, the illusion-of-competence signal.
- The row-4 counterexample: a prompt v1 that passes article 1, a v2 that fixes article 2 while regressing article 1, a v3 that fixes article 1 and regresses article 2. Every step satisfies the v1 definition *as written* — "tweaking the prompt in order to get the desired quality results" on the case in front — yet the loop oscillates forever and nothing in the definition can register that v2 is worse than v1.

**Version 2 — partial, NOT formally captured** (row-3 middle patched on a fresh surface, 2026-10-28; the learner's own restatement, verbatim):

> "A leaves room for more arms and more probability mass is more split amongst those arms leading to generic output since the next tokens are condtioned to come from a wider space. B leaves less room for more arms and less probability mass is split amongst those arms and is piled on to a few leading to more precise output since the next tokens are conditioned to come from a narrower space. Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."

This is **not** a v2 of the whole model: rows 4 (measurement layer) and 5 (failure regime) were still open when the session paused, and the graduation capture (entailment check, clone) was never reached. Row 4 stands at the learner's own diagnosis *"its missing a way to measure success"* plus the half-retrieved noun *"prompt harness"* — the unpacking question ("what does it hold, and when does it run, so the article-1 regression gets seen?") was left unanswered at pause.

**Named missing pieces:** (1) the measurement layer — v1 says nothing about how "desired quality" is known or compared across versions; (2) the failure regime — v1 names no case where better-structured prompting makes things worse; (3) the temperature-0 non sequitur — the first patch for the eval gap ("set temperature to zero and measure the quality") conflated decoding determinism with a quality measurement, repaired in-session to *decoding determinism ≠ goodness*.

## Source framing: the two-distribution picture

The curriculum states the mechanism in output terms rather than sampler terms, which is exactly where v1 stalled:

> "The first prompt activates a generic distribution of marketing emails in the model's training data. The second activates a narrow, high-quality slice. Same model. Same parameters. Wildly different outputs." — `2026-10-28 - prompt-engineering - rohit.md`

> "The number one prompt engineering mistake is being vague when you could be specific. Every ambiguity in your prompt is a branch point where the model guesses. Sometimes it guesses right. Sometimes it does not."

> "The specific version constrains the output space. Fewer valid outputs means higher probability of getting the one you want."

**External angle** — the mechanism the learner assembled to make those sentences true (their words in the "Version 2" block above): at an unresolved fork the mass splits across all plausible candidate arms and the autoregressive loop samples from that split (respecting the split weights, not uniform randomness); a precise instruction deletes arms, so the same mass concentrates on the survivors. This is the same distribution the model already knew from sampling — see [[Sampling from a Language Model]] and [[Softmax Function]]; a prompt is conditioning applied to that object, never a program handed to an executor.

## Anatomy and the core pattern set (solid at triage)

- Three message slots, in priority order: **system message** ("the invisible hand. It sets the model's identity, behavioral constraints, and output rules. The model treats this as highest-priority context."), **user message** ("the task"), and **assistant prefill** ("the secret weapon" — start the assistant turn with a partial string and the model continues from there). Prefill availability is provider- and version-bounded (see the disagreement note below).
- The curriculum's learning objective names the pattern set the learner already held: "Apply the core prompt engineering patterns (role, context, constraints, output format) to transform vague requests into precise instructions".
- Role prompting, with its limit: "The more specific the role, the narrower the distribution, the higher the quality. But there is a limit. If the role is so specific that few training examples match, the model will hallucinate."

## The measurement layer: eval-first — **OPEN (row 4)**

Anthropic puts the ruler *before* the tweaking, and the lesson's own build objective is a harness:

> "This guide assumes that you have: A clear definition of the success criteria for your use case; Some ways to empirically test against those criteria; A first draft prompt you want to improve. If not, spend time establishing that first." — `2026-10-28 - prompt-engineering - anthropic.md`

> "Not every success criterion or failing eval is best solved by prompt engineering. For example, you can sometimes improve latency and cost more easily by choosing a different model."

> "Implement a prompt testing harness that evaluates prompt changes against a set of expected outputs" — Rohit, learning objectives; the harness code section sits in the curriculum's "build it" part, past the learner's read point.

**What is still missing (do not fill it in here):** what a harness *holds* (a fixed case set + expected outputs + a scoring rule) and *when it runs* (on every prompt change, so a regression on article 1 is visible before v3 ships). Temperature is a lab-bench control, not the ruler: "Test with temperature=0 first to isolate prompt quality from sampling randomness" / "Temperature=0.0 makes the output deterministic -- the same input produces the same output every time. This is essential for testing and reproducibility." Determinism makes a run repeatable; it does not say the output is good.

## The failure regime — **UNATTACKED (row 5)**

The lesson and its sources carry at least two cases where more / better-structured prompting makes output worse:

- **Over-specific roles hallucinate.** "If the role is so specific that few training examples match, the model will hallucinate. 'You are the world's foremost expert on quantum gravity string topology' will produce confident nonsense because the model has very little high-quality text at that intersection."
- **Chain-of-thought can hurt on small models.** "chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of ∼ 100B parameters" / "chain of thought actually hurts performance for most models smaller than 10B parameters" (Wei et al.).

## ⚠️ Sources disagree — the CoT payoff is conditional, not a flat bonus

Both sides, verbatim:

- **Rohit (unconditional):** "Prompting the model to show intermediate reasoning steps, which improves accuracy on math, logic, and multi-step problems by 10-40%", and in Further Reading: "the foundational paper showing that 'think step by step' improves LLM accuracy by 10-40% on reasoning tasks".
- **Wei et al. 2022 (conditional on scale):** "chain-of-thought prompting is an emergent ability of model scale" — "That is, chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of ∼ 100B parameters."

This is a **real disagreement**, not a wording difference: the 10–40% figure is the large-model regime, and below ~10B the same technique *hurts*. A prompt-engineering model that only carries "CoT gives 10–40%" is broken at the small-model end.

**Second disagreement (apparent, version-bounded):** assistant prefill — Rohit presents it as a general "secret weapon" ("Anthropic's API supports this"), while the Anthropic docs are model/version-specific. Treat prefill as availability-checked per provider and per model, not as a portable pattern.

## Not yet taught (available as later attack material)

Temperature / top-p sampling mechanics (DAIR settings), the prefill availability contradiction above, and the CoT conditional-vs-unconditional disagreement. None of these were owed to the learner; they are attack material for the resume or for `/review`.

## Open questions

- [ ] **The eval layer (row 4):** a prompt testing harness — what does it hold, and when does it run, so the article-1 regression gets seen? Learner holds the noun; the mechanism is unassembled.
- [ ] **The failure regime (row 5):** where does better-structured prompting make things worse — and what does the learner's own model predict there?
- [ ] Formal **v2 capture** is pending (graduation not reached: entailment check, naive-student clone, battery remainder).

## Related

- [[Sampling from a Language Model]] — the sampling loop a prompt conditions
- [[Softmax Function]] — where the next-token distribution comes from
- [[Token]] — the unit of the "narrower space"
- [[AI Engineering from Scratch — Roadmap]] — the curriculum this lesson comes from
