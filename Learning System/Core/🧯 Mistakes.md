# Mistakes — Structured Wrong-Answer Ledger

> Purpose: Every failed review/probe/quiz item is recorded here with its error type and self-attribution.
> This is the priority-1 queue (DeepTutor pattern). Due mistakes are asked BEFORE normal due reviews.
> Lifecycle: `active` → `review` → `graduated` (retired after 2 consecutive correct recalls).
> Advisory only for now — mistakes do not block, but surface first in review selection.
> **Live queue = AIEFS rows only.** SWE-era mistakes: `Archive/SWE-2026-09-01/mistakes.md`;
> C-project mistakes: `Archive/C-project/mistakes.md` (refactor 2026-09-09).

## How to record (during review/teach sessions)
- **concept**: exact Concept name as in Active Concepts.md
- **question**: the question asked
- **expected**: server-side expected answer (short, not leaked)
- **error_type**: `structural | deviation | application | metacognitive`
  - structural = knowledge architecture wrong
  - deviation = understood but slipped / misread
  - application = knew but applied wrong
  - metacognitive = blank / "I don't know"
- **self_attribution**: learner's own words on why
- **status**: `active` (needs retry), `review` (1 correct so far), `graduated` (2 consecutive correct, retired)
- **retries**: count of correct recalls since creation

## Queue rule (review flow)
- Slots 1–2 of each 5-review session = due mistakes (`active`/`review` where Next Retry <= today), sorted by oldest first.
- Remaining 3 slots = type-aware due reviews (Attempts.json) shuffled with adjacency guard (no two same Source consecutively).

## Table

| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-05 | 4-Layer AI Environment Stack | torch imports but CUDA/GPU not visible — which stack layer? | Runtimes (CUDA/runtime layer), not System | structural | Placed GPU-invisible at System layer; missed the Runtimes split (learner wording not supplied — inferred from answer) | active | 0 | 2026-09-10 |
| 2026-09-05 | Cosine Similarity | cos(A,B) vs cos(A,C) for A=[1,0], B=[0,1], C=[2,0]; why does this prove magnitude-invariance where dot fails? | cos=0 vs cos=1; dot conflates magnitude (dot(A,C)=2 vs dot(A,A)=1 for the same direction) | structural | Answered in angles (90/0 deg) not cosines; claimed dot tells the better similarity story — inverted (learner wording not supplied — inferred from answer) | review | 1 | 2026-09-14 |
| 2026-09-06 | Cross-Entropy from NLL | Which statement about CE loss is TRUE? (A–D) | B — CE reduces to −log(ŷ_correct) for one-hot; gradient is softmax(z) − y | structural | Thought CE applies fixed penalty; inverted −log mechanism (said it keeps values small when it amplifies small probabilities into large penalties) | review | 1 | 2026-09-16 |
| 2026-09-07 | Gradient Descent Failure Modes (zigzag vs overshoot) | Why does vanilla GD struggle in the Rosenbrock valley? | Zigzags across narrow walls (gradient points across them); overshoot is a DIFFERENT failure (lr too large) | application | Conflated two failure modes — attributed valley struggle to overshoot (lr) instead of zigzag | active | 0 | 2026-09-10 |
| 2026-09-10 | Mini-batch Noise (two effects) | Q3ii: name the OTHER effect of mini-batch noise (the one that shows up in test accuracy) | Generalization/regularization: noise prevents settling into sharp minima (sharp generalize poorly, flat generalize well). Optimization (escape stall) is the FIRST effect, not the answer here | structural | Correction-over-rotation from 09-07 ("overfitting" → escape-stall); retained only the escape-stall half, dropped the generalization half. Recurred 4x across lesson; final re-seal passed (optimization=saddle escape / generalization=sharp-minima avoidance) | review | 1 | 2026-09-13 |
| 2026-09-10 | Learning-rate Schedules (four types) | Discriminate cosine vs warmup (early phase) and cosine vs exponential (floor) | Read the eta-vs-time curve on two axes: early phase (only warmup ramps up) and end behavior (only cosine has a nonzero floor eta_min; exponential → 0, no floor) | structural | Pattern-matched names against keyword "smooth/decaying" instead of reading the curve; ignored end behavior both times (transposed exponential's decay factor 0.999 into cosine's floor slot) | active | 0 | 2026-09-17 |
| 2026-09-10 | Learning-rate Schedules (four types) | Discriminate schedule from stem cues (unstable-start → warmup; nonzero-floor → cosine); compute floor value | Read the curve's start/end, not the name: warmup = ramp-up, cosine = nonzero floor eta_min, exponential = no floor. Floor value = the eta_min printed in the problem | structural | Pattern-matched schedule names to 'smooth decay' keywords; 3 confident misses (cosine-vs-warmup, cosine-vs-exponential, floor 0.001-vs-0.05). Floor-value slip itself is deviation (read prior example's number) | active | 0 | 2026-09-13 |
| 2026-09-11 | Cross-Entropy from NLL | Probe Q1 (−log₂(1/8)=?) + Q5 (CE vs H(P) relationship) | −log₂(1/8) = +3 bits (sign positive, not negative); CE H(P,Q) ≥ H(P) with equality only when Q=P; the subtraction CE−H(P) is KL divergence, not CE itself | structural | Recurrence of 09-06 −log inversion (sign flipped on −log); conflated CE with KL's subtraction shape | active | 0 | 2026-09-14 |
| 2026-09-11 | Entropy (Average Surprise) | CP2 practice: entropy of a fair 6-sided die | H = −Σ(1/6)log₂(1/6) = −log₂(1/6) = +log₂ 6 ≈ +2.585 bits (positive) | structural | Recurrence of −log sign inversion — CP1 fixed surprise, then flipped again on die entropy | review | 1 | 2026-09-17 |
