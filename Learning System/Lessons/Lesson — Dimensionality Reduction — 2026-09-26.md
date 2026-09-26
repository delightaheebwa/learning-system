# Lesson — Dimensionality Reduction (PCA, t-SNE, UMAP) — Phase 1 L10 — 2026-09-26

**Status: paused at Checkpoint 1/6, mini 1/2** (CP1 mini 1 sealed; exit ticket 3/3)
**Resume from:** CP1 mini 2 — where the new directions come from ($Av = \lambda v$ on the covariance matrix: eigenvectors = the new basis, eigenvalues = variance along each) — then CP1 practice, then CP2.
**Lang:** Python (lesson header: Python; NumPy + scikit-learn, optional umap-learn)

**Sources (live-fetched 2026-09-25, hashes in Scout digest):**
- Rohit P1 L10 `docs/en.md` — `Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - rohit.md` (sha256 9b65271b…)
- Shlens, *A Tutorial on PCA* — `…- shlens.md`
- Wattenberg et al., *How to Use t-SNE Effectively* (Distill 2016) — `…- distill.md`
- UMAP docs + parameters + FAQ — `…- umap.md`, `…- umap-params.md`, `…- umap-faq.md`
- 3Blue1Brown, Eigenvectors & eigenvalues — `…- 3b1b-eigen.md`
- Scout digest: `Learning System/.tmp/context-01a0d78c-dbff-7362-bcea-13f8df10005b-dimensionality-reduction.json` (first-fetch baseline, no drift check possible; no failed refs)

## Probe (graded, verifier-agreed 7/9)

| # | Strand | Result |
|---|---|---|
| 1 | Eigen picture (Av=λv, stays on own span) | ✅ C sure |
| 2 | Curse of dimensionality (distance concentration) | ❌ "I don't know" — new material |
| 3 | Covariance entries (off-diag co-movement, diag variance) | ✅ A sure |
| 4 | After centering: "features are orthogonal" (hunch) | ❌ structural slip — repaired in-session |
| 5 | Projection = dot product along u | ✅ B sure |
| 6 | Perplexity 2^H: 3 bits → 8 | ✅ B sure (fuzzy tag recovering) |
| 7 | t-SNE knob prediction | "some number of choices to pick from" (hunch) — ungraded elicitation |
| 8 | KL ≥ 0, =0 iff Q=P, asymmetric | ✅ A sure |
| 9 | Continuous values → PMF picked (sure) | ❌ PDF — the 09-24 flagged regression, recurs |
| 10 | Why no point-probability from a PDF | ✅ "intervals… not reading off exact probability" |

**Strand verdicts:** eigen solid · projection solid · KL solid · perplexity recovering · covariance unstable (orthogonality slip) · PMF/PDF unstable (label slip, mechanism intact per Q10) · curse-of-dim unknown/new.

## CP1 — The object PCA decomposes ✅ mini 1

- **Elicit (ungraded):** cm/inches pair, centered — off-diagonal large or zero? → learner: **large**, "indicates high variance which is what PCA prioritizes."
- **Consolidate (fact-check PASS 5/5):** centering is NOT decorrelation — after centering, entry (i,j) = dot product of the two centered feature columns (×1/(n−1)); diagonal = individual variances. Centering shifts the origin (uncentered PCA finds the mean direction, not spread directions). Making off-diagonals zero = PCA's goal, not centering's effect. Sharpened learner's "high variance" reasoning: diagonal = variance of one feature; off-diagonal = co-movement of two.
- **Learner check-back (confirmed):** diagonal = variance around the data's center; off-diagonal = "how much they vary together"; PCA diagonalizes so "each feature provides distinct information" — matched to Shlens's two goals (kill redundancy, rank by variance); precision added: PCA finds a **new basis** (linear combinations), it does not edit the original features.
- **Exit ticket (quiz-audit PASS_WITH_FLAGS lows-only cycle 2; grades verifier-agreed 3/3):** E1 B sure (PCA finds the new basis zeroing overlap) · E2 A sure (diagonal = variance around center) · E3 own-words pass ("all centering does is ensure the center is the data's center; pca finds the unique directions that together tell the whole story").

## Checkpoint plan (remaining)

- **CP1 mini 2:** where the new directions come from — $Av=\lambda v$ on the covariance matrix; eigenvectors = new basis, eigenvalues = variance along each (3B1B span picture; learner's Q1 pass is the anchor). Then CP1 practice.
- **CP2:** the 5-step PCA recipe from scratch (Python), on synthetic data.
- **CP3:** choosing k — explained-variance ratio, elbow, reconstruction error = sum of dropped eigenvalues; PCA anomaly detection.
- **CP4:** t-SNE — neighborhoods; perplexity = the learner's banked 2^H applied to the neighbor distribution (name-collision reframe); objective = KL(P‖Q) — L09 bridge; Distill misreading protocol (sizes meaningless; distances only at tuned perplexity — ⚠️ contradiction with Rohit's unconditional rule, resolved as safe-default vs fragile exception).
- **CP5:** UMAP — manifold learning, n_neighbors/min_dist as local↔global dials (umap-params sweep); ⚠️ Rohit's "better global structure" vs umap-faq's goal-not-guarantee (outlier pull-together failure mode); centering-only vs standardize decision (umap-faq conditional default).
- **CP6:** kernel PCA (RBF) + the real contradiction: Rohit's "high variance = important" as definition vs Shlens's assumption-that-can-fail (ferris wheel; MSE-optimal for reconstruction). Method-choice map → SHIP `outputs/skill-dimensionality-reduction.md`.
- **Final:** cumulative quiz + Feynman explain-back.

## Verification summary (this session)

- quiz-audit: probe batch (3 cycles: cycle-1 ISSUES position/length parity, cycle-2 ISSUES p6 key transposition + p8 length, cycle-3 PASS) · exit ticket (cycle-1 ISSUES length/stem leaks, cycle-2 PASS_WITH_FLAGS lows-only, accepted silently).
- grade-audit: probe batch 9 items (agrees:true on all: pass 1,3,5,6,8,10; fail 2,4,9) · exit ticket 3/3 (agrees:true).
- fact-check: CP1 mini-1 consolidation 5/5 PASS · learner check-back confirmation 4/4 PASS.
- Attempts logged (ops.py): Eigenvalues & Eigenvectors pass · Variance & Covariance fail (probe Q4) then pass (exit ticket) · Perplexity pass · KL Divergence pass · PMF vs PDF fail (probe Q9).
