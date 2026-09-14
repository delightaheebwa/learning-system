# Lesson — Information Theory (Phase 1 L09) — 2026-09-11

Status: **in-progress at Checkpoint 4/6 — CP4 idea + practice done (graded pass 2026-09-14); at CP4 Pause #2**

## Resume from
At **CP4 Pause #2** (post-practice). Next: on learner "no questions" → **CP5 — mutual information**; if the learner pauses instead, run a CP3+CP4 exit ticket (2–3 retrieval items) and refresh `Pending Ingest.json`. CP4 was practiced and graded 2026-09-14: P1 (a/b/c = 1.000 / 0.469 / 0.531 bits) + P2 (C), all correct with tag sure — grade-audit PASS agreeing; attempts logged: "KL Divergence" pass (interval_index 1, next_review 2026-09-21) and "Cross-Entropy from NLL" pass (next_review 2026-09-21). Convention note (for CP5+): this lesson uses Olah-style H(P,Q) with weights from truth Q, surprises from model P, so the floor is H(Q); Rohit/ML convention flips the letters (P = data → H(P,Q) ≥ H(P)). Anchor phrase: "the entropy term is always the data's entropy". The learner asked about the letter convention on 2026-09-12 and got the verified reconciliation.
**CP3 floor-direction re-seal — OPEN, retrieval due 2026-09-17:** Mistakes row dated 2026-09-14 (active, retries 0). The re-seal EXPLANATION was delivered inside CP4's opening on 2026-09-14 (KL ≥ 0 → H(P,Q) ≥ H(data), fact-checked) but NO passing retrieval re-test has been recorded yet — ask the direction-inequality question on 2026-09-17 or at the next review.

## Checkpoints
Lettering used throughout this list: **this lesson's Olah letters — model P, truth/data Q**, so every subtracted entropy below is H(data). (Rohit/ML letters flip P and Q; translate before comparing to the `en.md`.)

1. CP1 — Surprise I(x) = −log p — ✅ done (sign fixed: 3 / 0.014 / 0 all correct)
2. CP2 — Entropy H(P) = expected surprise — ✅ done (sign re-sealed on the 2026-09-11 exit ticket; die entropy +2.585 bits)
3. CP3 — Cross-entropy H(P,Q) = CE loss = NLL — ✅ done (2026-09-12: practice 1 bit exact; floor misconception corrected + re-sealed on exit ticket E3; convention question answered, verified). ⚠️ 2026-09-14 resume warm-up W4 REGRESSED the floor DIRECTION (picked H(P,Q) ≤ H(Q), tag sure; floor identity itself correct on W2) — explanation re-delivered at CP4's opening 09-14; the RETRIEVAL re-test is still due 2026-09-17 (Mistakes row active).
4. CP4 — KL = CE − H(data), i.e. KL(Q∥P) = H(P,Q) − H(Q) in this lesson's letters (not H(P) — H(P) is the model's own entropy) — ✅ done (2026-09-14: idea fact-checked 5/5; asymmetry clarification fact-checked 4/4; practice P1 a/b/c = 1.000 / 0.469 / 0.531 bits + P2 C all correct+sure; grade-audit PASS; attempts: KL Divergence + Cross-Entropy from NLL pass, next_review 2026-09-21). At Pause #2.
5. CP5 — Mutual information I(X;Y) — pending
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
⚠️ REGRESSED 2026-09-14 resume warm-up: W4 picked the REVERSED inequality H(P,Q) ≤ H(Q) (tag sure) while W2 identified floor=H(Q)≈0.881 correctly — floor's identity known, direction re-inverted. Own Mistakes row dated 2026-09-14 (active, due 2026-09-17). Attempt logged under canonical key Cross-Entropy from NLL (fail, then same-day re-seal pass; next_review 2026-09-21).
