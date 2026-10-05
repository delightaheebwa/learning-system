# PCA (Dimensionality Reduction)

> Related: [[Covariance and correlation]], [[Variance is Non-Negative (PSD Covariance)]], [[PCA Sign Ambiguity (svd_flip)]], [[Linear Algebra Intuition]], [[Matrix Transformations]]

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

## Silent failures

Both consumers of `order` fail quietly instead of loudly:

- `components_ = vecs[:, order[:k]]` — without the reversal this keeps the **smallest**-λ directions: no error, just the least interesting axes.
- `transform = (X - mean_) @ components_` — projects onto those wrong axes.

The code runs; only the numbers are wrong. That is why the layout detectors carry more weight than "the call succeeded".

## Why "variance = importance" is an assumption

Ranking by λ treats variance as importance. That choice is **optimal for reconstruction** — k dimensions chosen this way minimize mean squared error — but it is an assumption about usefulness, and the assumption can fail: a low-variance direction may be the one that matters (the standard counterexample flagged in this track's lesson plan for CP6, where the assumption is contrasted with its limits).

## Open questions

- **Round cloud (equal eigenvalues):** when λ1 = λ2 there is no unique "long axis" — the *subspace* is determined, not the individual directions. Pocketed for CP3.
- **Curse of dimensionality:** distance concentration is still unexplained in this track; surfaces at CP3.
- **`n == d` — sealed 2026-10-05:** both `vecs` and `Xc` then read `d×d`, so the shape detector alone cannot separate them — the resolution is to inspect what the array *holds* (`Xp`'s rows are data points, `V`'s columns are directions; the learner's own repair: "rows hold data points, hence nxk").

## Field notes

The learner's own phrasings (2026-10-03):

- "eigenvalue ranking is what remains untouched. the pair that flip sign are the signed projected coordinates and the axis direction."
- "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square."
- Repairs locked by the exit ticket: `np.cov`'s default is rows-as-variables (`rowvar=True`), `rowvar=False` is for points-in-rows; detector phrase "shape has `n` ⇒ points possible; all-`d` ⇒ directions only".

The learner's own words (2026-10-05, CP2 practice):

- "rows hold data points, hence nxk" — the locating-question self-repair that also sealed the `n == d` edge.
- Slips confessed and repaired in-session: "divided by 3" (the divisor), "any number of the minor diagonal is the variance" (off-diagonal vs variance), and a kept fraction of `1 − λ2/λ1` (the top λ treated as the pie).
