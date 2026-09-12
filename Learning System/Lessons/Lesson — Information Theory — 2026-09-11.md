# Lesson — Information Theory (Phase 1 L09) — 2026-09-11

Status: **paused at Checkpoint 2/6** — resume at CP3 (cross-entropy)

## Resume from
Resume at **CP3 — cross-entropy** H(P,Q) = CE loss = NLL. (CP2's −log sign was re-sealed on the 2026-09-11 exit ticket: die entropy = +log₂ 6 ≈ +2.585 bits.)

## Checkpoints
1. CP1 — Surprise I(x) = −log p — ✅ done (sign fixed: 3 / 0.014 / 0 all correct)
2. CP2 — Entropy H(P) = expected surprise — ✅ done (sign re-sealed on the 2026-09-11 exit ticket; die entropy +2.585 bits)
3. CP3 — Cross-entropy H(P,Q) = CE loss = NLL — pending
4. CP4 — KL = CE − H(P) — pending
5. CP5 — Mutual information I(X;Y) — pending
6. CP6 — Perplexity + bits/nats + label smoothing — pending

## Sources
Scout digest: context-p1l09-information-theory.json (live-fetched 2026-09-11, no drift)
Rohit en.md + Olah (Visual Information Theory) + PyTorch CrossEntropyLoss + Shannon 1948

## Build language
Python (Rohit `Language: Python`)

## Priority-1 misconception (tracking)
−log sign inversion — recurred 3× (probe Q1, probe Q5 CE-vs-KL, CP2 die entropy). CP1 and CP2 both re-sealed by the 2026-09-11 exit ticket (Mistakes row bumped to review/retries=1). Re-test the sign on the next cross-entropy checkpoint before advancing.
