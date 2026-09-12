# Lesson — Information Theory (Phase 1 L09) — 2026-09-11

Status: **paused at Checkpoint 3/6** — resume at CP4 (KL divergence)

## Resume from
Resume at **CP4 — KL divergence** (KL = CE − H(data); re-emit the full CP4 teaching block from the 2026-09-12 session — the learner asked for it to be brought back, and it has NOT been answered/practiced yet). Convention note for CP4: this lesson uses Olah-style H(P,Q) with weights from truth Q, surprises from model P, so the floor is H(Q); Rohit/ML convention flips the letters (P = data → H(P,Q) ≥ H(P)). The learner asked about this and got the verified reconciliation — anchor phrase: "the entropy term is always the data's entropy".

## Checkpoints
Lettering used throughout this list: **this lesson's Olah letters — model P, truth/data Q**, so every subtracted entropy below is H(data). (Rohit/ML letters flip P and Q; translate before comparing to the `en.md`.)

1. CP1 — Surprise I(x) = −log p — ✅ done (sign fixed: 3 / 0.014 / 0 all correct)
2. CP2 — Entropy H(P) = expected surprise — ✅ done (sign re-sealed on the 2026-09-11 exit ticket; die entropy +2.585 bits)
3. CP3 — Cross-entropy H(P,Q) = CE loss = NLL — ✅ done (2026-09-12: practice 1 bit exact; floor misconception corrected + re-sealed on exit ticket E3; convention question answered, verified)
4. CP4 — KL = CE − H(data), i.e. KL(Q∥P) = H(P,Q) − H(Q) in this lesson's letters (not H(P) — H(P) is the model's own entropy) — pending
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
