# Lesson — Information Theory (Phase 1 L09) — 2026-09-11

Status: **paused mid-Checkpoint 5/6 (2026-09-15)** — CP5 idea + four-form breakdown delivered; KL-connection walkthrough + CP5 practice pending

## Resume from
Resume **inside CP5** (mutual information), NOT at the idea. 2026-09-15 outcome: warm-up on CP4 REGRESSED (W1 pass; W2 ∞-case fail-sure; W4 identity stated as CE + H(data) fail-sure; W3 hunch-correct → isomorphic re-probe W3′ fail-sure on non-symmetry) → CP4 re-seal re-delivered (identity minus-not-plus, ∞ case, non-symmetry; fact-checked 5/5) → retrieval RS1 on-paper pass (KL(Q∥P) = 0.278 bits for Q=(0.8,0.2), P=(0.5,0.5), sure). CP5 idea delivered (fact-checked 6/6) + the four-form breakdown of I(X;Y) walked step by step (fact-checked 4/4; running example joint [[0.45,0.05],[0.05,0.45]]: H(X)=H(Y)=1, H(X|Y)=0.469, I=0.531; learner's Step-1 intuition "the certainty gained from knowing Y" affirmed with the edge that X is NOT fully certain after Y). **Learner asked for slower, step-by-step pacing with more questions next session — save material as-is and continue the breakdown.** Pause exit ticket 3/3 pass (E1 KL identity on-paper 0.326 bits; E2 ∞ case A; E3 MI idea free recall). Attempts: KL Divergence fail, fail, pass (interval_index 3, next_review 2026-10-15); Mutual Information pass (interval_index 1, next_review 2026-09-22). Resume from: **walk the KL connection slowly — I(X;Y) = KL(p(x,y)∥p(x)p(y)) was stated in the CP5 idea but not yet walked step by step** — then bars/extremes consolidation, then CP5 practice (fresh computation of I(X;Y) on a NEW joint — the learner has only mapped the worked example's numbers, not computed fresh — then grade), then Pause #2, then CP6 (perplexity + bits/nats + label smoothing). Convention note (for CP5+): this lesson uses Olah-style H(P,Q) with weights from truth Q, surprises from model P, so the floor is H(Q); Rohit/ML convention flips the letters (P = data → H(P,Q) ≥ H(P)). Anchor phrase: "the entropy term is always the data's entropy". The learner asked about the letter convention on 2026-09-12 and got the verified reconciliation.
**CP3 floor-direction re-seal — OPEN, retrieval due 2026-09-17:** Mistakes row dated 2026-09-14 (active, retries 0). The re-seal EXPLANATION was delivered inside CP4's opening on 2026-09-14 (KL ≥ 0 → H(P,Q) ≥ H(data), fact-checked) but NO passing retrieval re-test has been recorded yet — ask the direction-inequality question on 2026-09-17 or at the next review. (2026-09-15 note: today's W4 plus-vs-minus identity error is a closely-related failure family but is NOT the floor-direction re-test — the 09-17 re-test stays due.)

## Checkpoints
Lettering used throughout this list: **this lesson's Olah letters — model P, truth/data Q**, so every subtracted entropy below is H(data). (Rohit/ML letters flip P and Q; translate before comparing to the `en.md`.)

1. CP1 — Surprise I(x) = −log p — ✅ done (sign fixed: 3 / 0.014 / 0 all correct)
2. CP2 — Entropy H(P) = expected surprise — ✅ done (sign re-sealed on the 2026-09-11 exit ticket; die entropy +2.585 bits)
3. CP3 — Cross-entropy H(P,Q) = CE loss = NLL — ✅ done (2026-09-12: practice 1 bit exact; floor misconception corrected + re-sealed on exit ticket E3; convention question answered, verified). ⚠️ 2026-09-14 resume warm-up W4 REGRESSED the floor DIRECTION (picked H(P,Q) ≤ H(Q), tag sure; floor identity itself correct on W2) — explanation re-delivered at CP4's opening 09-14; the RETRIEVAL re-test is still due 2026-09-17 (Mistakes row active).
4. CP4 — KL = CE − H(data), i.e. KL(Q∥P) = H(P,Q) − H(Q) in this lesson's letters (not H(P) — H(P) is the model's own entropy) — ✅ done (2026-09-14: idea fact-checked 5/5; asymmetry clarification fact-checked 4/4; practice P1 a/b/c = 1.000 / 0.469 / 0.531 bits + P2 C all correct+sure; grade-audit PASS; attempts: KL Divergence + Cross-Entropy from NLL pass). ⚠️ 2026-09-15 resume warm-up REGRESSED CP4 (identity plus-error + ∞-case + non-symmetry, all sure) → re-sealed same session: fact-checked re-lay + RS1 on-paper pass (0.278 bits) + exit ticket E1/E2 pass — holds again under test (attempts interval_index 3, next_review 2026-10-15).
5. CP5 — Mutual information I(X;Y) — **in-progress, idea delivered (2026-09-15)**: idea fact-checked 6/6; four-form breakdown fact-checked 4/4 (Step 1 intuition confirmed; Steps 2–4 delivered); KL-connection walkthrough + practice pending
6. CP6 — Perplexity + bits/nats + label smoothing — pending

## Sources
Scout digest: context-p1l09-information-theory.json (live-fetched 2026-09-11, no drift)
Rohit en.md + Olah (Visual Information Theory) + PyTorch CrossEntropyLoss + Shannon 1948

## Build language
Python (Rohit `Language: Python`)

## Priority-1 misconception (tracking)
−log sign inversion — recurred 3× (probe Q1, probe Q5 CE-vs-KL, CP2 die entropy). CP1, CP2 re-sealed on the 2026-09-11 exit ticket. Re-tested again 2026-09-12 (warm-up W1 = +3 bits, sure; CP3 practice + exit ticket all sign-correct) — holds across 4 consecutive tests.

## Floor misconception (second tracked, 2026-09-12)
"Floor = model's entropy" — answered 1 bit (model H(P)) instead of H(Q) ≈ 0.811 for Q=(0.75,0.25). Corrected same session; re-sealed on exit ticket E3 (picked H(Q)≈0.47 over near-miss H(P)≈0.81 on a new coin). Mistakes row → review, retries=1.
⚠️ REGRESSED 2026-09-14 resume warm-up: W4 picked the REVERSED inequality H(P,Q) ≤ H(Q) (tag sure) while W2 identified floor=H(Q)≈0.881 correctly — floor's identity known, direction re-inverted. Own Mistakes row dated 2026-09-14 (active, due 2026-09-17). Attempt logged under canonical key Cross-Entropy from NLL (fail, then same-day CP4-practice pass — NOT a floor-direction retrieval re-test; next_review 2026-09-21).
