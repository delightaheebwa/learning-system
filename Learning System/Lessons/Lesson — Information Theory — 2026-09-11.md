# Lesson — Information Theory (Phase 1 L09) — 2026-09-11

Status: **paused at Checkpoint 2/6** (entropy practice)

## Resume from
Re-seal the −log sign — flipped AGAIN on the die-entropy computation (answered −2.585; correct is +log₂ 6 ≈ +2.585 bits). Then continue CP3 cross-entropy.

## Checkpoints
1. CP1 — Surprise I(x) = −log p — ✅ done (sign fixed: 3 / 0.014 / 0 all correct)
2. CP2 — Entropy H(P) = expected surprise — ⏸ in-progress (concept taught; practice sign-flipped)
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
−log sign inversion — recurred 3× today (probe Q1 sign, probe Q5 CE-vs-KL, CP2 die entropy). CP1 re-sealed surprise; entropy still fragile. Next checkpoint re-tests it before advancing.
