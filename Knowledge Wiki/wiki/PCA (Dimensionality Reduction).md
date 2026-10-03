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
- **Slice detector:** `[::-1]` **reverses** (keeps every element, order flipped); `[:-1]` **drops the last**. `vals.argsort()[:, :-1]` is therefore a different, silently wrong object — descending λ is a reversal of the ascending order, not a truncation.

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
- **`n == d`:** both `vecs` and `Xc` then read `d×d`, so the shape detector alone cannot separate them (flagged at warm-up 2026-10-03, isomorphic re-check owed).

## Field notes

The learner's own phrasings (2026-10-03):

- "eigenvalue ranking is what remains untouched. the pair that flip sign are the signed projected coordinates and the axis direction."
- "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square."
- Repairs locked by the exit ticket: `np.cov`'s default is rows-as-variables (`rowvar=True`), `rowvar=False` is for points-in-rows; detector phrase "shape has `n` ⇒ points possible; all-`d` ⇒ directions only".
