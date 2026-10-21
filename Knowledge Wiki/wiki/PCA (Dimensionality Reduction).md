<!-- provenance: status=synthesis | source=Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - rohit.md (Rohit P1 L10) + Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - shlens.md (Shlens, A Tutorial on PCA) + Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md (scikit-learn KernelPCA) + Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md | verified-by=— | date=2026-10-21 | learner-note block: the "## My understanding" section is the learner's verbatim note (learner-note; five statements as of 2026-10-21, nothing overwritten) -->


# PCA (Dimensionality Reduction)

> Related: [[Covariance and correlation]], [[Variance is Non-Negative (PSD Covariance)]], [[PCA Sign Ambiguity (svd_flip)]], [[Curse of Dimensionality]], [[Linear Algebra Intuition]], [[Matrix Transformations]]

**Principal Component Analysis (PCA)** rewrites a dataset in a new basis whose axes are the directions the data actually spreads along, ranked by how much spread each axis carries. The stated goals this track teaches against (Shlens): **remove redundancy** and **rank by variance**. The new coordinates are the *principal component scores*.

## The recipe

**center → covariance → eigenvectors → sort by λ → project**

1. **Center** — subtract the per-feature mean: `Xc = X - X.mean(0)`. Centering moves the origin (and nothing else); it is *not* decorrelation, and without it the covariance is measured about the wrong point.
2. **Covariance** — `C = np.cov(Xc, rowvar=False)`. The result is `d×d` and symmetric: diagonal = each feature's variance, off-diagonal = co-movement. The sample count `n` appears **only inside the entries**, through the `1/(n-1)` normalization — never as a matrix dimension.
3. **Eigenvectors** — `vals, vecs = np.linalg.eigh(C)`. The **eigenvectors are the new axes**; each eigenvalue λ is the variance along its eigenvector. `eigh` returns λ **ascending** and puts the eigenvectors in the **columns**; `vecs` is `d×d` regardless of `n`.
4. **Sort by λ** — `order = vals.argsort()[::-1]`. Sorting is what makes "top-k" well defined.
5. **Project** — `V = vecs[:, order[:k]]` (`d×k`) and `Xp = Xc @ V` (`n×k`). The projection rewrites the **data points**; diagonalizing `C` is the sibling result (the same change of basis applied to the matrix instead of the points).

```
C  = np.cov(Xc, rowvar=False)        # d x d, symmetric, n only via 1/(n-1)
vals, vecs = np.linalg.eigh(C)       # ascending lambda; eigenvectors are COLUMNS
order = vals.argsort()[::-1]         # a reversal -> biggest lambda first
V  = vecs[:, order[:k]]              # d x k  (columns = directions)
Xp = Xc @ V                          # n x k  (rows = points)
```

## Choosing k — the elbow and the threshold (2026-10-07)

Two rules answer two different questions, and they need not agree.

- **Explained-variance ratio.** Axis `i` carries `λ_i / Σλ` of the total spread, so the cumulative sum is the fraction retained by `k` axes. "Keep 95%" is a *target*: take the smallest `k` whose cumulative ratio reaches it.
- **Reconstruction error.** The spread you *discard* by keeping `k` axes is exactly `Σ_{dropped} λ_j` — the global counterpart of the per-point error in the next section. Kept fraction and dropped sum are two views of one pie, `Σλ = trace(C)`.
- **The elbow convention.** The elbow is the first bar whose **incoming drop** is small — where the drops themselves stop shrinking; you keep the bars **before** it. On a scree of `λ = 100, 80, 40, 35, …` the incoming drops are `20, 40, 5`, the flat zone starts at the fourth bar, so `k = 3`. On the 2026-10-07 practice scree `λ = 50, 24, 4, 2` (Σλ = 80) the drops are `26, 20, 2` ⇒ flat zone at the fourth bar ⇒ `k = 3` (kept `50 + 24 + 4 = 78`).
- **Height-as-position detector.** On a scree, `k` is the *position* you choose; the bar heights are the `λ` menu. "The elbow is at 24" reads a height where an index belongs. Walk the **drops**, not the heights.
- **The two rules can disagree — but not here.** On the practice scree the 95% rule also returns `k = 3` (`78 ≥ 0.95 × 80 = 76`), so elbow and threshold **agree** on this scree. The elbow-vs-threshold disagreement (the 95% target landing inside a long flat tail) is a real phenomenon on other screes, not a property of this one.
- **Etymology anchor:** *scree* is the rock pile at the base of a cliff (Cattell 1966) — cliff = structure, rubble = noise tail, elbow = where they meet.

## Layout detectors

- **Shape detector:** a shape containing `n` can hold points; an all-`d` shape holds directions only. `vecs` is `d×d` even when `n` is large — its rows are **component slots** (the x-/y-slots of each direction), never data points. `d == n` is the trap: both shapes then read `d×d`, so inspect what the array *holds*, not the shape alone.
- **`rowvar` detector:** `np.cov` defaults to `rowvar=True` — **each row is a variable**. For the points-as-rows, features-as-columns layout you must pass `rowvar=False` (or transpose first), otherwise the covariance is built along the wrong axis.
- **Slice detector:** `[::-1]` **reverses** (keeps every element, order flipped); `[:-1]` **drops the last element**. `vals.argsort()` is **1-D** (shape `(d,)`), so `vals.argsort()[:, :-1]` is an **`IndexError`** — *loud*, not silent; the `[rows, cols]` slice shape belongs to `vecs`, never to the 1-D index array. The genuinely **silent** trap is the *missing reversal*: `order = vals.argsort()` then `order[:k]` quietly keeps the **smallest**-λ vectors in `components_` (no error raised); `vals.argsort()[:-1]` is merely a 1-D truncation — it drops the last (largest-λ) index. Descending λ is a **reversal** of the ascending order, not a truncation.

## Variance bookkeeping detectors (paper walk 2026-10-05)

Every entry of `C` is a centered dot product **divided by `n−1`** — one less than the rows you summed, because centering has already consumed one degree of freedom. Handing back the `n×d` centered matrix, or dividing by `n`, are the two slips that still produce a plausible-looking `C`.

- **Divisor detector:** the denominator is *rows summed − 1*. On the cloud with rows (1,0), (5,2), (3,4) the centered dot products are `8 / 4 / 8` and scale by `1/2`, giving `C = [[4,2],[2,4]]`; dividing by `n = 3` gives the wrong `[[8/3,4/3],[4/3,8/3]]` (the dot products themselves were right).
- **Diagonal detector:** only the **diagonal** entries are variances (each feature's self-dot); the off-diagonal is the co-movement of the two features. Calling the off-diagonal a variance is a relapse of the CP1 diagonal-roles idea — the check is *self-dot ⇒ diagonal*.
- **Pie detector (total variance):** the spread the eigenvalues share is `Σλ = trace(C)`. The fraction of variance kept by the top axis is therefore `λ_top / Σλ` — **not** `1 − λ2/λ1`, which treats the top eigenvalue as if it were the whole pie. On `C = [[4,2],[2,4]]`, `λ = 6, 2`, so the kept fraction is `6/8 = 3/4`.

The same cloud, end to end on paper: mean `(3,2)` → centered rows → `C = [[4,2],[2,4]]` → `λ = 6, 2` → the `λ = 6` eigenvector is the axis kept for `k = 1` → `3/4` of the total variance retained.

## PCA as an anomaly detector (2026-10-07)

Reconstruction error is **per sample**, not global. Project `x_i` onto the top-`k` subspace, reconstruct `x̂_i`, and

```
error_i = ‖x_i − x̂_i‖² = Σ_{dropped axes} (coordinate)² = (distance from x_i across the kept subspace)²
```

- **Recipe:** fit PCA on **normal** data, keep top-`k`, compute each sample's own reconstruction error, then **flag** the samples whose error crosses a threshold. (Rohit: "samples with high reconstruction error are outliers that do not fit the learned subspace.")
- **Geometry — along = normal, across = suspect.** A huge coordinate on a **kept** direction survives the projection: the reconstruction lands far *along* the subspace, still inside it, with a small error. A huge coordinate on a **dropped** direction is exactly the part thrown away — that *is* the error. The detector measures distance **across** the subspace, not along it.
- **Worked instance (CP3 practice, 2026-10-07):** a point whose per-sample error is `5.7` against a normal cloud whose errors are all `< 0.3` is flagged; its offending coordinate lives on a dropped axis.
- **Limitation:** a point far out **along** the subspace is never flagged — the detector is subspace-relative, so "normal" means "fits the learned subspace", not "sits near the other points".
- **Global vs per-sample:** `Σ_{dropped} λ_j` says how much structure the truncation discarded for the whole cloud; `error_i` says whether *this* point fits. Same decomposition, different scope — the first is a property of `k`, the second of the point.

### Shape fit lives across, depth lives along (2026-10-08)

The reconstruction error asks **one question only**: how far the point sits *across* the kept subspace. Three clarifications fall out of that.

- **The error is a shape test, not a crowd test.** Normal data spreads enormously *along* the big-|λ| directions, so a point far out along the subspace is "more of the normal direction" — small error, silent flag. Catching it needs a **stacked depth-style check**: the kept coordinates compared against the *training* range (standard practice pairs the `Q`/SPE squared-prediction-error statistic with Hotelling's `T²` / Mahalanobis depth). Shape fit lives across; depth lives along.
- **Unit vs signal.** Every residual lives in the dropped subspace *by construction* — that subspace is the **unit**, like degrees Celsius. "It is in the dropped directions" is therefore not evidence of anything; what the flag reads is the residual's **length**, against a threshold set from the training residuals.
- **Directions get dropped; points never do.** The compression discards every point's across-coordinate identically. Residual size decides *flagged / not flagged*; it never decides *kept / dropped*.

**Frame-inversion detector (the practiced slip, 2026-10-08).** Asked which point *escapes* the flag, the learner answered with the flagged signature (a huge coordinate on a dropped axis — the loudest alarm, not an escape). On "escapes / gets missed" questions, restate **what the detector measures** before choosing: the alarm fires on across-dropped-axis distance; far-along-kept is silent. Micro-check: a point 1,000 units out along a line-cloud's single kept axis → **missed**.

## The round cloud — the isotropic degenerate case (2026-10-07)

When the covariance is a multiple of the identity, `C = λI`, **every direction is an eigenvector** (3Blue1Brown anchor: a matrix that scales everything equally has a single eigenvalue but *every* vector is an eigenvector). Consequences:

- the λ ranking is a **total tie**, so the "top" `k` axes are **arbitrary** — any orthogonal basis will do;
- the scree is **flat**: no elbow anywhere, and no bar is a natural place to stop;
- "keep 95%" cannot drop a single bar: with ten equal bars (`Σλ = 1000`, target `950`) dropping one loses `100` ⇒ `900 < 950`.

**Compression needs unequal spread — shape, not size.** PCA's power to keep `k < d` axes comes from anisotropy, not from the number of features or the size of the total variance.

**The trace pie is fixed under rotation.** `Σλ = trace(C)` is invariant, so PCA **never shrinks** the cloud — it redistributes the fixed total into as few directions as the data allows. Micro-check (2026-10-07): `λ = (99, 1)` compresses to `k = 1` at 1% loss; `λ = (50, 50)` — the same total of 100 — loses 50%.

This is also the high-dimensional regime described by the [[Curse of Dimensionality]]: pairwise distances concentrate (the max/min ratio approaches 1), which is exactly the "no dominant direction" world PCA needs to *not* be in.

## Silent failures

Both consumers of `order` fail quietly instead of loudly:

- `components_ = vecs[:, order[:k]]` — without the reversal this keeps the **smallest**-λ directions: no error, just the least interesting axes.
- `transform = (X - mean_) @ components_` — projects onto those wrong axes.

The code runs; only the numbers are wrong. That is why the layout detectors carry more weight than "the call succeeded".

## Why "variance = importance" is an assumption

Ranking by λ treats variance as importance. That choice is **optimal for reconstruction** — k dimensions chosen this way minimize mean squared error — but it is an assumption about usefulness, and the assumption can fail: a low-variance direction may be the one that matters (the standard counterexample flagged in this track's lesson plan for CP6, where the assumption is contrasted with its limits).

## Kernel PCA — nonlinear manifolds and the lifting trick (2026-10-20)

Linear PCA finds orthogonal linear hyperplanes of maximum variance. When data lies on a **nonlinear manifold** (such as two concentric rings or a Swiss roll), any linear projection collapses distinct structures onto each other into overlapping intervals.

1. **Problem:** Concentric circles in $\mathbb{R}^2$ cannot be separated by any line or linear projection. In 2D, the radial geometry prevents linear separation; standard PCA projects along straight axes, crushing the inner and outer circles into overlapping segments.
2. **Where from / Mechanism (The Kernel Trick):** Lift data points $x \in \mathbb{R}^d$ into a higher-dimensional feature space $\mathcal{H}$ via a nonlinear mapping $\phi(x)$. For 2D concentric rings, mapping $(x_1, x_2) \mapsto (x_1, x_2, z = x_1^2 + x_2^2)$ places the inner ring at low height and the outer ring at high height on a paraboloid, allowing a horizontal linear hyperplane to cleanly separate them along the vertical axis. The **kernel trick** enables computing inner products in $\mathcal{H}$ without explicitly evaluating $\phi(x)$:
   $$K_{ij} = k(x_i, x_j) = \langle \phi(x_i), \phi(x_j) \rangle$$
   For an RBF (Radial Basis Function) kernel:
   $$k(x, x') = \exp(-\gamma \|x - x'\|^2)$$
   which corresponds to an infinite-dimensional feature space.
3. **Matrix Dimension Contrast ($d \times d$ vs $n \times n$):**
   - **Standard PCA** diagonalizes the $d \times d$ covariance matrix $C = \frac{1}{n-1} X_c^\top X_c$. For $n = 5000, d = 2$, $C$ is $2 \times 2$.
   - **Kernel PCA** diagonalizes the $n \times n$ pairwise similarity Gram matrix $K$. For $n = 5000, d = 2$, $K$ is $5000 \times 5000$. Computational cost shifts from feature dimension $d$ to sample size $n$ ($O(n^2)$ memory, $O(n^3)$ eigendecomposition).
4. **Boundary Conditions & the Pre-image Problem:**
   - The kernel function $k$ must satisfy **Mercer's condition** (positive semi-definiteness).
   - In feature space, centering must be performed on the Gram matrix $K$ implicitly ($\tilde{K} = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n = (I - \mathbf{1}_n) K (I - \mathbf{1}_n)$, where $\mathbf{1}_n$ is the $n \times n$ matrix with entries $1/n$).
   - The **pre-image problem**: while projecting a point into low-dimensional kernel coordinates is straightforward via training similarities, reconstructing an input-space vector $\hat{x} \in \mathbb{R}^d$ from a feature-space point $\phi(x)$ is generally ill-posed because an arbitrary vector in $\mathcal{H}$ may have no exact pre-image in input space.
5. **Contrast with t-SNE / UMAP:**
   - t-SNE and UMAP optimize low-dimensional coordinates directly via gradient descent on pairwise probabilities/fuzzy simplicial sets, which makes projecting out-of-sample test points ill-defined or expensive without re-optimizing.
   - Kernel PCA provides an analytical out-of-sample projection operator: a new test point $x^*$ is projected onto the $k$-th eigenvector by evaluating kernel similarities against all training points:
     $$y_k(x^*) = \frac{1}{\sqrt{\lambda_k}} \sum_{i=1}^n \alpha_{k, i} k(x_i, x^*)$$

### Feature-space centering and RBF shift-cancellation (Hidden Piece 1 sealed 2026-10-21)

1. **Problem (Why input-space centering fails):** In standard PCA, centering simply subtracts the input mean $\mu = \frac{1}{n}\sum_{i=1}^n x_i$. However, for distance-based shift-invariant kernels like the Gaussian RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$, uniform translation by any shift vector $c$ cancels identically in pairwise differences:
   $$\|(x_i - c) - (x_j - c)\|^2 = \|x_i - x_j\|^2$$
   Hence, centering raw features in $\mathbb{R}^d$ leaves the kernel matrix $K$ completely unchanged and completely fails to center the lifted points $\phi(x)$ in feature space $\mathcal{H}$ around $\mu_\phi = \frac{1}{n}\sum_{i=1}^n \phi(x_i)$.
2. **Where from / Double-Centering Formula:** Because $\phi(x)$ can be infinite-dimensional and is never explicitly computed, centering must be carried out directly on the $n \times n$ Gram matrix $K$. Centered features $\tilde{\phi}(x_i) = \phi(x_i) - \mu_\phi$ define centered kernel entries $\tilde{K}_{ij} = \langle \tilde{\phi}(x_i), \tilde{\phi}(x_j) \rangle = \langle \phi(x_i) - \frac{1}{n}\sum_{k=1}^n \phi(x_k), \phi(x_j) - \frac{1}{n}\sum_{l=1}^n \phi(x_l) \rangle$. Expanding the inner product yields the matrix identity:
   $$\tilde{K} = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n = (I - \mathbf{1}_n) K (I - \mathbf{1}_n)$$
   where $\mathbf{1}_n$ is the $n \times n$ matrix with all entries equal to $1/n$ ($\mathbf{1}_n = \frac{1}{n}\mathbf{1}\mathbf{1}^\top$). Double-centering subtracts row means, subtracts column means, and adds back the grand mean.
3. **Conditions & Cost:** Requires the full $n \times n$ Gram matrix ($O(n^2)$ space, $O(n^2)$ operations for centering). Out-of-sample test projection requires asymmetric centering against training column/row means.

## Open questions

- **Round cloud (equal eigenvalues) — sealed 2026-10-07:** `λI` ⇒ every direction is an eigenvector, the λ ranking is a total tie, the axes are arbitrary, the scree is flat, and a 95% target cannot drop a single bar. The verdict: PCA's compression power needs unequal spread (shape, not size).
- **Curse of dimensionality — sealed 2026-10-07:** distance concentration (distances become *more alike*, not smaller) and the fixed trace pie (`Σλ = trace(C)` invariant under rotation). See [[Curse of Dimensionality]].
- **`n == d` — sealed 2026-10-05:** both `vecs` and `Xc` then read `d×d`, so the shape detector alone cannot separate them — the resolution is to inspect what the array *holds* (`Xp`'s rows are data points, `V`'s columns are directions; the learner's own repair: "rows hold data points, hence nxk").
- **Kernel PCA hidden steps (CP6 mini 1/3 in-progress):** Hidden Piece 1 (centering the $n \times n$ Gram matrix $K$ in feature space via $(I - \mathbf{1}_n) K (I - \mathbf{1}_n)$ and RBF shift-cancellation) **sealed 2026-10-21**. Still open to unpack on resume: Hidden Piece 2 (why eigenvectors of centered $\tilde{K}$ act as coordinates, and the $1/\sqrt{\lambda}$ scaling factor) followed by Hidden Piece 3 (pre-image problem with a small 3-point toy walkthrough).

## Field notes

The learner's own phrasings (2026-10-03):

- "eigenvalue ranking is what remains untouched. the pair that flip sign are the signed projected coordinates and the axis direction."
- "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square."
- Repairs locked by the exit ticket: `np.cov`'s default is rows-as-variables (`rowvar=True`), `rowvar=False` is for points-in-rows; detector phrase "shape has `n` ⇒ points possible; all-`d` ⇒ directions only".

The learner's own words (2026-10-05, CP2 practice):

- "rows hold data points, hence nxk" — the locating-question self-repair that also sealed the `n == d` edge.
- Slips confessed and repaired in-session: "divided by 3" (the divisor), "any number of the minor diagonal is the variance" (off-diagonal vs variance), and a kept fraction of `1 − λ2/λ1` (the top λ treated as the pie).

The learner's own words (2026-10-07, CP3 minis 4–5 + practice):

- "i'd expect it to be big since in terms of reconstruction, the cloud falls short by a lot" (the anomaly-detection elicitation).
- "i would conclude it is an anomaly/outlier. its error comes from the fact that it is far off from the learned subspace."
- "PCA lives and dies on whether the spread is irregular or not. in this case it is regular spread hence no 'minor directions' for PCA to chop off."
- "PCA just cuts a slice of the cake but doesnt make the cake as a whole smaller." — the shape-vs-size framing, sharpened with the fixed trace pie.
- "the scree is a bunch of bars of equal height of 100."
- Repairs locked in CP3: bar **heights** vs bar **positions** on a scree (k is the position you choose; the heights are the λ menu); distances **concentrate** (more alike) rather than shrink.
- The tutor's own mid-practice mis-steer is recorded on the lesson side: the practice scree's "35" was called the third bar and the elbow pushed to `k = 2`; a fact-check receipt refuted it (35 is the fourth bar, keep the bars before the flat zone ⇒ `k = 3`) and it was retracted openly — the learner's bend-locating instinct had been right.

The learner's own words (2026-10-08, the anomaly-detector tangent):

- "a big residual tells me the point is an outlier as compared to the normal data" — accepted, sharpened: outlier-ness here is about *shape* (a mismatch with the learned subspace), not distance from the crowd.
- "whether big or small, it's still in the dropped subspace" — the puzzle the **unit-vs-signal** split dissolved: being in the residual subspace is the unit, the *length* is the signal.
- The two guiding rounds of the tangent, kept as the pair of detector phrases: **shape fit lives across, depth lives along**; **directions get dropped, points never do**.

The learner's own understanding (2026-10-21, CP6 mini 1 pause exit ticket X1):

- Pairwise differences cancel uniform shifts ($\|(x_i - \mu) - (x_j - \mu)\| = \|x_i - x_j\|$), rendering input-space centering ineffective for RBF kernels.
- Feature-space centering must be performed directly on $K$ via double-centering: $\tilde{K} = (I - \mathbf{1}_n) K (I - \mathbf{1}_n) = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n$.

## My understanding

> **status=learner-note** — the learner's words, verbatim from the 2026-10-20 and 2026-10-21 sessions (CP6 mini 1), never rewritten. The annotations around them are the tutor's and the source's.

**Kernel PCA lifting intuition for 2D concentric circles (Rung 3 own-words statement, 2026-10-20):**

> "it couldnt because you cant seperate concentric circles in 2D since there is no line you could draw that would seperate them. mapping to a non linear coordinate helps use to \"pull one out of the other\" by adding a new coordinate which wil put them at different heights thereby truly seperating them."

*Source framing (annotation, not a rewrite):* "Pull one out of the other" captures the dimension-lifting geometry cleanly — lifting $(x_1, x_2)$ onto a paraboloid $z = x_1^2 + x_2^2$ maps the radial coordinate into height, transforming non-linear concentricity into linear vertical separability.

**Paraboloid height coordinate (Rung 2 hint response, 2026-10-20):**

> "1. for the inner ring is sits at (1,1,z) and the outer sits at (3,3,z). 2. i think they end up as seperate points along the vertical axis"

*Source framing:* Confirms that lifting to 3D via height $z$ aligns the two concentric rings at different levels along the vertical axis.

**Pacing & comprehension reflection before /pause (2026-10-20):**

> "that kinda works. it is better than before but i think we will need to slow down a bit on it for the next time. i feel like there is a lot of \"hidden stuff\" i should know when reading some of what you just said but i dont really know. plus some parts still are fuzzy for me. /pause"

*Tutor note:* Paused at Checkpoint 6/6, mini 1/3 per learner request. Next session will slow down and unpack the hidden mechanics step-by-step with a 3-point toy walkthrough.

**Pause exit ticket X1 response & hidden-steps note (2026-10-20):**

> "1. it fails beause there is no line in 2d that can seperate them. lifting them into a non linear coordinate puts them at different heights thereby truly seperating them. sure 2. standard pca decomposes into 2x2 while kernel pca decomposes into 5000 x 5000. sure\nfor hidden stuff, i think basically all of it."

*Source framing:* The geometric intuition and matrix dimensions ($d \times d = 2 \times 2$ vs $n \times n = 5000 \times 5000$) are exact. The "hidden stuff" (centering $K$ in feature space, why eigenvectors of $K$ act as coordinates, $1/\sqrt{\lambda}$ scaling factor, and the pre-image problem) will be unpacked in detail.

**Kernel PCA centering in feature space & double-centering (Pause exit ticket X1, 2026-10-21):**

> "understanding that RBF differences cancel input shifts and centering requires double-centering the kernel matrix via $(I - \mathbf{1}_n) K (I - \mathbf{1}_n)$."

*Source framing (annotation, not a rewrite):* For an RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$, uniform translation in input space cancels in the Euclidean norm $\|(x_i - c) - (x_j - c)\| = \|x_i - x_j\|$, leaving the Gram matrix $K$ identical. Centering must be performed directly on $K$ in feature space using the projection operator $(I - \mathbf{1}_n) K (I - \mathbf{1}_n) = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n$, subtracting row/column means and adding back the grand mean.


