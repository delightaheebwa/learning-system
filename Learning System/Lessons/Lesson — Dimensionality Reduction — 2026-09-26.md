# Lesson — Dimensionality Reduction (PCA, t-SNE, UMAP) — Phase 1 L10 — 2026-09-26

**Status:** paused at Checkpoint 2/6, mini 0/4 (CP1 fully sealed 2026-09-30; CP2 not started)
**Resume from:** CP2 mini 1 — the 5-step PCA recipe from scratch in Python on synthetic data (center → covariance → `np.linalg.eigh` → sort → project), first micro-step: the recipe overview + why each step exists; anchors: toy-cloud det roots (4.59/0.16, 10/0), `C v = λ v` on the covariance, eigenbasis-diagonal framing.
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

## Resume session 2026-09-30 — CP1 mini 2 sealed

- **Warm-up (verifier-agreed 2/2):** diagonal = variance around center (C sure); centering ≠ decorrelation, off-diagonal = co-movement, PCA zeroes it (sure). Attempts: V&C pass.
- **Mini 2 delivered in slow-down mode (learner asked to properly grasp the three pieces):**
  - **Piece 1 — variance bookkeeping:** toy cloud (2,1), (−2,−0.5), (0,−0.5); learner first misread bracketed pairs as feature columns (5/4.25/−4.5), self-diagnosed on a locating question, second attempt still had two arithmetic slips (C11 4.5: extra unit in sum of squares; C12 1.25: (−2)×(−0.5) taken as 0.5 not +1), repaired with detectors (sum twice before dividing; negative×negative = positive); final re-attempt exact: **4 / 0.75 / 1.5** ✓ (grade-audit agreed).
  - **Piece 2 — where λ comes from:** elicit prediction correct ("one to be bigger than the other… one direction is more elongated/scaled"); consolidated: λ ≥ 0 always (eigenvalues of a covariance = variances along directions), det route $\det(C−\lambda I)=0$ with the 3B1B squish-into-a-line anchor. Practice: on $C=\begin{bmatrix}4&1.5\\1.5&0.75\end{bmatrix}$ learner derived $\lambda^2−4.75\lambda+0.75=0$, roots **4.59 / 0.16** ✓ (trace sanity 4.75, ratio ~28).
  - **Piece 3 — eigenbasis diagonalization:** elicit prediction correct in learner's own words ("movement in one direction has absolutely no co-movement with the other since they are perpendicular"); consolidated: entry = overlap of spread between two axes; eigenbasis = THE perpendicular basis along the blob's own long/short axes → off-diagonal exactly 0; any symmetric matrix goes diagonal in its eigenbasis (3B1B); PCA = that coordinate change manufactured on purpose (Shlens: choosing P diagonalizes $C_Y$ — "this was the goal for PCA"). Round-cloud degenerate case pocketed for CP3.
  - **Figure:** standalone viz turn (cm/inches cloud + λ bars 10.1/0.016 + two-bases covariance table 3.41→0), viz-audit PASS (numbers recomputed from the 20 plotted points). Follow-up clarify answered: all numbers come from the same 20 dots; λ's are eigenvalues of the same matrix, not new data; trace balance 8.79+1.34 ≈ 10.1+0.016.
- **CP1 practice (integrative, verifier-agreed):** 2-dot cloud (2,1), (−2,−1), n=2: (a) $C=\begin{bmatrix}8&4\\4&2\end{bmatrix}$ ✓ · (b) λ = **10, 0** ✓ (det = λ(λ−10)) · (c) first answered "cloud smaller/compact" ✗ — self-located via locating question (dots far apart, trace 10 big); repaired to: λ=0 ⇒ zero spread perpendicular, pure line through the origin, perfectly correlated, PCA could keep one axis and lose nothing; contrast sealed: compact = small trace, not small per-direction λ.
- **Pause exit ticket (quiz-audit PASS; grade-audit agreed 2/3):** X1 A sure ✓ (entry = centered dot product ÷ (n−1)) · X2 B sure ✓ (det(C−λI)=0) · X3 ✗ first half right (perpendicular eigen-axes ⇒ no co-movement), second half mislabeled: eigenbasis diagonal entries called "correlations of the feature columns with themselves" — corrected to the λ's = variance along each eigenvector direction (correlation only after dividing by both standard deviations). Same label-inversion shape as the PMF-vs-PDF thread (mechanism intact, name slipped under pressure) — Mistakes row candidate.
- **Attempts this session (ops.py):** Variance & Covariance pass, pass, then fail (X3 label slip) · Eigenvalues & Eigenvectors pass, pass (det practice + exit ticket).

## Checkpoint plan (remaining)

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
