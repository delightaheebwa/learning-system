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
| 2026-09-05 | 4-Layer AI Environment Stack | torch imports but CUDA/GPU not visible — which stack layer? | Runtimes (CUDA/runtime layer), not System | structural | Placed GPU-invisible at System layer; missed the Runtimes split (learner wording not supplied — inferred from answer) | active | 1 | 2026-09-19 |
| 2026-09-05 | Cosine Similarity | cos(A,B) vs cos(A,C) for A=[1,0], B=[0,1], C=[2,0]; why does this prove magnitude-invariance where dot fails? | cos=0 vs cos=1; dot conflates magnitude (dot(A,C)=2 vs dot(A,A)=1 for the same direction) | structural | Answered in angles (90/0 deg) not cosines; claimed dot tells the better similarity story — inverted (learner wording not supplied — inferred from answer) | graduated | 2 | 2026-09-14 |
| 2026-09-06 | Cross-Entropy from NLL | Which statement about CE loss is TRUE? (A–D) | B — CE reduces to −log(ŷ_correct) for one-hot; gradient is softmax(z) − y | structural | Thought CE applies fixed penalty; inverted −log mechanism (said it keeps values small when it amplifies small probabilities into large penalties) | graduated | 2 | 2026-09-16 |
| 2026-09-07 | Gradient Descent Failure Modes (zigzag vs overshoot) | Why does vanilla GD struggle in the Rosenbrock valley? | Zigzags across narrow walls (gradient points across them); overshoot is a DIFFERENT failure (lr too large) | application | Conflated two failure modes — attributed valley struggle to overshoot (lr) instead of zigzag | review | 1 | 2026-09-19 |
| 2026-09-10 | Mini-batch Noise (two effects) | Q3ii: name the OTHER effect of mini-batch noise (the one that shows up in test accuracy) | Generalization/regularization: noise prevents settling into sharp minima (sharp generalize poorly, flat generalize well). Optimization (escape stall) is the FIRST effect, not the answer here | structural | Correction-over-rotation from 09-07 ("overfitting" → escape-stall); retained only the escape-stall half, dropped the generalization half. Recurred 4x across lesson; final re-seal passed (optimization=saddle escape / generalization=sharp-minima avoidance) | graduated | 2 | 2026-09-13 |
| 2026-09-10 | Learning-rate Schedules (four types) | Discriminate cosine vs warmup (early phase) and cosine vs exponential (floor) | Read the eta-vs-time curve on two axes: early phase (only warmup ramps up) and end behavior (only cosine has a nonzero floor eta_min; exponential → 0, no floor) | structural | Pattern-matched names against keyword "smooth/decaying" instead of reading the curve; ignored end behavior both times (transposed exponential's decay factor 0.999 into cosine's floor slot) | active | 0 | 2026-09-17 |
| 2026-09-10 | Learning-rate Schedules (four types) | Discriminate schedule from stem cues (unstable-start → warmup; nonzero-floor → cosine); compute floor value | Read the curve's start/end, not the name: warmup = ramp-up, cosine = nonzero floor eta_min, exponential = no floor. Floor value = the eta_min printed in the problem | structural | Pattern-matched schedule names to 'smooth decay' keywords; 3 confident misses (cosine-vs-warmup, cosine-vs-exponential, floor 0.001-vs-0.05). Floor-value slip itself is deviation (read prior example's number) | active | 0 | 2026-09-13 |
| 2026-09-11 | Cross-Entropy from NLL | Probe Q1 (−log₂(1/8)=?) + Q5 (CE vs H(P) relationship) | −log₂(1/8) = +3 bits (sign positive, not negative); cross-entropy is never below the entropy of the distribution that supplies the weights (the data/truth): in this lesson's Olah letters that is H(P,Q) ≥ H(Q) (the unlabeled "H(P,Q) ≥ H(P)" holds only under the Rohit/en.md ML letters where P = truth); KL = CE − H(data), i.e. KL(Q∥P) = H(P,Q) − H(Q), not "CE − H(P)" (here 1.0 − 0.811 ≈ 0.189, whereas CE − H(P) = 1.0 − 1.0 = 0) | structural | Recurrence of 09-06 −log inversion (sign flipped on −log); conflated CE with KL's subtraction shape | active | 0 | 2026-09-14 |
| 2026-09-11 | Entropy (Average Surprise) | CP2 practice: entropy of a fair 6-sided die | H = −Σ(1/6)log₂(1/6) = −log₂(1/6) = +log₂ 6 ≈ +2.585 bits (positive) | structural | Recurrence of −log sign inversion — CP1 fixed surprise, then flipped again on die entropy | review | 1 | 2026-09-17 |
| 2026-09-12 | Cross-Entropy from NLL | P3b follow-up: what is the floor of H(P,Q) for a coin that is truly Q=(0.75,0.25) when your model is perfect? | H(Q) = −0.75·log₂0.75 − 0.25·log₂0.25 ≈ 0.811 bits — the floor is the TRUE distribution's entropy, not the model's | structural | Took the floor as the model's own entropy (fair coin H(P)=1 bit) instead of H(Q)≈0.811; H(P,Q) got the weights right (1 bit exact). RE-SEALED same day: CP3 exit ticket E3 picked floor=H(Q)≈0.47 bits (truth) over the near-miss D=H(P)≈0.81 on a NEW coin, tag sure | review | 1 | 2026-09-19 |
| 2026-09-14 | Cross-Entropy from NLL | Resume warm-up W4: which inequality holds — H(P,Q) ≤ H(Q) or H(P,Q) ≥ H(Q)? | H(P,Q) ≥ H(Q), equality iff P = Q — the floor is the data's entropy H(Q), never below it | structural | Picked the reversed inequality H(P,Q) ≤ H(Q) (tag sure) one question after correctly identifying the floor as H(Q)≈0.881 on W2 — floor's identity sealed, direction re-inverted (learner wording inferred from W2/W4 picks) | active | 0 | 2026-09-17 |
| 2026-09-11 | PMF vs PDF | (question text not preserved in session notes; fail logged in Attempts.json, discriminative) | PMF = discrete probability; PDF = density (integrate for probability) | structural | Backfilled 2026-09-12 during review: 09-11 fail never reached the ledger; surrounding 09-11 errors were −log-sign inversions (structural) | review | 1 | 2026-09-22 |
| 2026-09-14 | MLE vs MAP Estimation | What does MAP add on top of MLE, and which prior gives L2 vs L1? | MAP = MLE × prior; Gaussian → L2, Laplace → L1 | structural | Named the prior half but not the mapping ('the penalty prior' without the Gaussian/Laplace split) | active | 0 | 2026-09-18 |
| 2026-09-15 | KL Divergence | Resume warm-up on CP4: (W2) when the model zeroes a data event, is cross-entropy finite with KL +∞, or both +∞? (W4) state the KL identity in the lesson's letters; (W3′) for P=(0.9,0.1), Q=(0.6,0.4), is KL(Q∥P) = KL(P∥Q)? | Both H(P,Q) and KL(Q∥P) go to +∞ while H(Q) stays finite; KL(Q∥P) = H(P,Q) − H(Q) (minus, never plus); the gap is directed — 0.449 vs 0.326 bits, so the two are not equal | structural | Sure-wrong three times in a resume warm-up (the ∞ case, the identity sign stated as 'KL = CE + H(data)', and non-symmetry picked as 'equal exactly when both are uniform') — one turn after a hunch-correct non-symmetry pick, i.e. wrong-direction overconfidence. Repaired same session via a fact-checked re-seal; held on RS1 on-paper (KL(Q∥P) = 0.278 bits) and pause exit ticket E1 (0.326 bits) / E2 (A). Row stays active until the 2026-09-17 CP3 floor-direction re-test also clears (session-note recommendation: graduate both together) | active | 0 | 2026-09-17 |
