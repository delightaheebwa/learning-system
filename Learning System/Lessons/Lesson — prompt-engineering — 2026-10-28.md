# Lesson — Prompt Engineering (Phase 11 L01, LLM Engineering)

**Date:** 2026-10-28
**Status:** Paused mid-triage — row 4 open (eval layer), row 5 unattacked
**Source:** https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/01-prompt-engineering (fetched live 2026-10-28; Scout digest `Learning System/.tmp/context-01a1823e-0f24-70c3-b793-e78c1d3019a9-prompt-engineering.json`, scout-audit PASS; 9 raw files under `Knowledge Wiki/raw/sources/2026-10-28 - prompt-engineering - *.md`)
**Flow:** [[FLOW:teach]] — learner-supplied material + handwritten notes
**Material read by learner:** the lesson up to the "build it" part (learner-reported)

## Material

- Lesson core: "Prompt engineering is not dead… What changed is that it became table stakes. Every serious AI engineer needs it."
- Intro frame: "every token you send is an instruction, and the model follows instructions literally. Write better instructions, get better outputs."
- Core pattern set: role, context, constraints, output format.
- Vague vs engineered prompt: "The first prompt activates a generic distribution… the second activates a narrow, high-quality slice." / "Every ambiguity in your prompt is a branch point where the model guesses." / "constrains output space. Fewer valid outputs means higher probability."
- Role prompting limit: "If the role is so specific that few training examples match, the model will hallucinate."
- Learning objectives include: "Implement a prompt testing harness that evaluates prompt changes against a set of expected outputs."
- Temperature/sampling section (learner has not read past "build it"): temp 0.0 = deterministic / top token; "Test with temperature=0 first to isolate prompt quality from sampling randomness."
- Externals: Anthropic (eval-first: success criteria + empirical tests + first draft BEFORE tweaking; "Not every success criterion or failing eval is best solved by prompt engineering"), Wei et al. (CoT emergent ~100B+, small models get *worse*), OpenAI (instructions parameter, developer>user priority), DAIR (temperature/top-p mechanisms), PE2 meta-prompting.
- Scout-flagged contradictions: assistant prefill availability (Rohit vs Anthropic docs — real, version-bounded); CoT benefit unconditional "10–40%" (Rohit) vs conditional ~100B (Wei et al.) — real; prompt-engineering scope (Rohit vs Anthropic) and role-mechanism wording — apparent.

## Learner model (v1) — verbatim, handwritten photo, transcribed + confirmed

> "Prompt engineering is very much alive. It has just become table stakes for all AI engineers. The usual structure is role, context, constraints, output. Prompt engineering consists of clarity, patterns, anti-patterns, context window, constraints, role, output format. Models take your prompts literally — here we need to be precise. Prompt engineering is the process of tweaking the prompt in order to get the desired quality results."

(The one unreadable word was filled in by the learner as "clarity." Confidence tag: **sure**.)

## Triage

| # | Claim (verbatim) | Bucket | Reason / evidence |
|---|---|---|---|
| 1 | "Prompt engineering is very much alive… table stakes for all AI engineers." | solid | matches source ("not dead… became table stakes") |
| 2 | "The usual structure is role, context, constraints, output." | solid | source names exactly these four as the core pattern |
| 3 | "Models take your prompts literally — here we need to be precise." | suspect → **REPAIRED (closed)** | vague — no mechanism; repaired via fork-arm/mass picture (see Repair mode) |
| 4 | "the process of tweaking the prompt in order to get the desired quality results" | missing → **OPEN** | no measurement layer: nothing says how "desired quality" is known; Anthropic puts success criteria + tests + first draft *before* tweaking |
| 5 | (absent) failure regime | missing → not yet attacked | model names no case where better-structured prompting hurts; sources contain two (CoT below ~100B hurts — Wei et al.; over-specific role hallucinates — Rohit) |

Attack order: 3 → 4 → 5. Dependency: 4 and 5 both required row 3's mechanism.

## Pre-attack prediction (row 3)

Prompt: "given p(next|context), no executor — what does your prompt text actually do to the output?"
Learner (verbatim): "i think my prompt text steers the model's next token choices for each token in the output from right left to right" — **correct** (conditioning each next-token distribution, left to right). Recorded as micro-check pass.

## Attacks (in dependency order)

### Attack 1 — row 3, mechanism press ("literally")

Prompt: vague vs precise instruction — what changes at the next-token distribution level, what shows up in output; and what does "taken literally" mean when nothing is executed?
- **Attempt 1 (verdict: FAIL, miss_class cue, confidence sure → illusion-of-competence signal):** "with vague tokens, it conditions the next token distribution in the direction of 'generic tokens' leading to a generic output while with precise tokens… more precise output. so to take your prompt literally would then mean that 'you asked with a generic request, i then gave you a generic response'…" — circular restatement, no distributional middle.
- Rung R3 (source return): "The first prompt activates a generic distribution… the second activates a narrow, high-quality slice." / "Every ambiguity in your prompt is a branch point where the model guesses."
- **Attempt 2 (verdict: FAIL, miss_class structural):** "a vague prompt leaves a lot of ambiguity unresolved for the model and hence it simply fills in the gaps with what is generic… a generic prompt activates a generic distribution" — banned word used twice; model-as-decider agency picture; no spread-vs-peaked middle.
- Push-down nudge: "a model that only computes a probability distribution — what is the stuff it fills gaps with? Name the currency."
- Learner: "tokens with the high probability of coming next in a generic response given the generic prompt" — named probability, still circled.

### Repair mode — row 3 gap (miss_class structural, tactic push_down) — CLOSED

- **Step 1/2 (Socratic, landed):** at a fork the instruction leaves unresolved, where does the mass go, what does the loop emit? Learner: "the probability mass splits. if context favors no candidate, the a token is chosen at random" — check PASS (graded). Sharpening given: the sample respects the split weights, not uniform randomness.
- **Step 2/2 (Socratic, landed):** precise instruction ("exactly 5 bullets, each with a number, no intro") — what happens to fork arms and mass? Learner: "it narrows the number of choices each of those arms has hence more mass piles up on fewer arms compared to other arms." — check PASS (graded); matches source "fewer valid outputs means higher probability."
- **Fresh-surface close (graded PASS):** new case, prompts A ("Summarize this.") vs B ("Summarize this article in exactly 3 sentences, past tense, no numbers, and end with the single most important takeaway.") — chain operated correctly on both.
- **Learner restatement (verbatim):** "A leaves room for more arms and more probability mass is more split amongst those arms leading to generic output since the next tokens are condtioned to come from a wider space. B leaves less room for more arms and less probability mass is split amongst those arms and is piled on to a few leading to more precise output since the next tokens are conditioned to come from a narrower space. Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."

### Attack 2 — row 4, counterexample trap ("tweak to get desired quality")

- **Prediction attempt (verdict: FAIL, miss_class careless):** "i guess the model produces something mediocre as you've said" — restated the setup; question restated for free.
- Learner: "the next move would then be to simply tweak again" — their definition operating; loop has no end, quality re-decided per run.
- **Counterexample:** v1 passes article 1 → v2 fixes article 2, regresses article 1 → v3 fixes article 1, regresses article 2. Every step satisfies the definition *as written* (desired quality on the case in front) yet the process oscillates forever and can never register v2 worse than v1. Asked: what is missing that would let it *see* the oscillation?
- **Attempt (verdict: FAIL, miss_class structural):** "its missing a way to measure success. so we should set temperature to zero and measure the quality." — diagnosis kernel correct; remedy conflated decoding determinism with a quality measurement.
- Push-down nudge: "what does temp 0 actually change about a run, and does flipping it change whether the output is good?" Learner: "it jsut makes the model pick the top choice in the next token distribution every time. flipping it i think wont change whether the output is good or not." — distinction landed (recorded micro-check pass). Lesson nuance banked: Rohit recommends testing at temp 0 to *isolate prompt quality from sampling randomness* — a cleaner lab bench, not the ruler.
- **Self-repair attempt in progress when paused:** learner half-retrieved "prompt harness" from the lesson (source confirms the term: "implement a prompt testing harness that evaluates prompt changes against a set of expected outputs"). Unpacking question posed — **unanswered**: "A harness: what does it hold, and when does it run — so the article-1 regression gets seen?"

## Repair steps

| Step | Fact (target) | Rests on | Check | Learner answer | Verdict |
|---|---|---|---|---|---|
| R3-repair 1/2 | mass splits across all plausible candidates at unresolved forks; loop samples from the split | p(next\|context), autoregressive loop, learner's own "probability" currency | where does mass go at the "dogs are…" fork; what does the loop emit | "the probability mass splits. if context favors no candidate, the a token is chosen at random" | pass (graded) |
| R3-repair 2/2 | precise instruction deletes fork arms; mass concentrates on survivors | step 1 + weighted-sampling sharpening | what does "exactly 5 bullets, each with a number, no intro" do to arms and mass | "it narrows the number of choices each of those arms has hence more mass piles up on fewer arms compared to other arms." | pass (graded) |

## Model patch (v1 → breaking case → current state)

- **v1 (verbatim):** the handwritten model quoted above.
- **Breaking case:** the v1/v2/v3 article oscillation (row 4) — definition satisfied at every step, no way to see the regression; plus the two failed mechanism chains on row 3 before the fork-arm repair.
- **Current state (assembled only from the learner's verbatim session words):** v1 with row 3's middle patched by the fresh-surface answer: vague prompt → more arms, mass split wide → generic output; precise prompt → fewer arms, mass piled on survivors → narrower space → precise output; *"Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."* Row 4 stands at "its missing a way to measure success" + the half-retrieved term "prompt harness," unpacking not yet done.
- **Formal v2 capture:** not yet taken (graduation step not reached).

## Pause exit ticket

- Question (per pause flow): "state the part of your current prompt-engineering model you are least sure about, and one case you think might break it."
- **Unanswered** at learner's explicit instruction (laptop shutdown). Recorded as FAIL, confidence no-idea, miss_class cue. Not softened.

## Resume

1. **Row 4 (open, first):** re-pose the harness unpacking question — "a prompt testing harness: what does it hold, and when does it run, so the article-1 regression gets seen?" Learner holds the noun; the mechanism must be assembled in their words. If the unpacking fails, repair mode on the eval-layer gap (source pointer: Anthropic raw file "Before prompt engineering" list; Rohit harness learning objective; Rohit harness code section is past the learner's read point — "build it" — read on demand at resume).
2. **Row 5 (not attacked):** failure regime — attack (likely counterexample/perturbation) using Wei et al. CoT-below-~100B and Rohit's role-over-specificity hallucination passages.
3. **Graduation:** v2 capture → entailment check → naive-student clone (qualitative target: tool/technique choice, e.g., CoT-on-small-model or prefill decision) → battery remainder (perturbation/sabotage not yet exercised) → consolidation diagram → handoff.
4. Note: temperature/top-p mechanics, prefill contradiction, and the CoT 10–40% conditional-vs-unconditional contradiction have **not** been taught; they are available as later attack material, not owed to the learner.
