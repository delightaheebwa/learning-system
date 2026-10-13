<!-- provenance: status=synthesis | source=Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap.md (umap-learn docs) + 2026-10-13 - dimensionality-reduction - umap-paper.md (McInnes & Healy 2018, ArXiv 1802.03426) + 2026-10-13 - dimensionality-reduction - umap-faq.md + 2026-10-13 - dimensionality-reduction - rohit.md (Rohit P1 L10) | verified-by=— | date=2026-10-13 | learner-note block: the "## My understanding" section is the learner's verbatim note (learner-note; two statements as of 2026-10-13) -->

# UMAP (Dimensionality Reduction)

> **Type:** concept · **Track:** AIEFS · **Source:** umap-learn documentation (umap-learn.readthedocs.io) + McInnes & Healy, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction* (ArXiv 1802.03426, 2018) + the umap-learn FAQ + Rohit P1 L10 (Dimensionality Reduction) · **Lang:** Python (`umap-learn`)
> **Insight:** UMAP assumes the data lies **uniformly on a locally connected Riemannian manifold with a locally constant metric**; from those assumptions it models the manifold as a *fuzzy topological structure* built patch by patch, and the embedding is the low-dimensional arrangement whose fuzzy structure best matches.
> Related: [[t-SNE (Dimensionality Reduction)]], [[Curse of Dimensionality]], [[PCA (Dimensionality Reduction)]], [[Perplexity]]

## The three assumptions (the docs, verbatim)

The umap-learn docs open with "The algorithm is founded on three assumptions about the data":

1. "The data is uniformly distributed on Riemannian manifold;"
2. "The Riemannian metric is locally constant (or can be approximated as such);"
3. "The manifold is locally connected."

and then: "From these assumptions it is possible to model the manifold with a fuzzy topological structure. The embedding is found by searching for a low dimensional projection of the data that has the closest possible equivalent fuzzy topological structure."

The name spells the recipe out: **U**niform **M**anifold **A**pproximation and **P**rojection. The docs also file it as a technique "that can be used for visualisation similarly to t-SNE, but also for general non-linear dimension reduction" — a wider remit than t-SNE's visualization-first pitch.

**Where the uniformity assumption comes from (paper).** Uniform spread on its own manifold is not something real data supplies, and the paper says as much: for theoretical reasons it is *beneficial* to assume it, and even without the assumption results "are only valid in the limit of infinite data", while "in practice, finite real world data is rarely so nicely behaved." The move is to *choose* a metric instead of inheriting the ambient one — assuming "the manifold has a Riemannian metric not inherited from the ambient space, we can find a metric such that the data is approximately uniformly distributed with regard to that metric." Uniformity is then a consequence of the metric choice, not a claim about the data as given.

## Manifold = a local property, not a dimension count

A manifold is defined by what a **small enough patch** looks like, not by the size of the whole object or by how folded it is:

- a straight line is a perfectly good 1-D manifold and a flat plane a 2-D one — degenerate cases where the surface is flat everywhere;
- an unrolled, flat sheet counts as a manifold too, so *folding* is not what makes something a manifold (the Swiss roll is a manifold because of its local structure, not because it is rolled);
- the defining property is that every sufficiently small patch looks like ordinary flat space (locally Euclidean) — and "locally constant metric" is the same statement in metric language.

That is why the local-connectivity and local-metric assumptions are the load-bearing ones: they only have to hold *patch by patch*.

## The mechanism: patches → glue → match

The paper's high-level construction: "UMAP uses local manifold approximations and patches together their local fuzzy simplicial set representations to construct a topological representation of the high dimensional data", and then "optimizes the layout of the data representation in the low dimensional space, to minimize the cross-entropy between the two topological representations." Read as three moves:

1. **Patch.** Each point's neighbourhood is a small connected patch of the manifold. Inside a patch the metric is (approximately) constant, so distances there are honest and the patch can be summarised locally.
2. **Glue.** Patches share neighbours, so their fuzzy representations overlap and merge into **one** global fuzzy structure for the whole data set. This is what *locally connected* buys: without connections there is nothing to sew.
3. **Match.** Build the same kind of fuzzy structure for a candidate low-dimensional layout, and score the mismatch; the embedding is the layout "that has the closest possible equivalent fuzzy topological structure."

"Manifold learning" is therefore a local-to-global construction: learn the surface patch by patch, then glue. Rohit's L10 says the same thing in one line — UMAP "builds a weighted graph in high-dimensional space (the 'fuzzy topological representation') and then finds a low-dimensional layout that preserves this graph as well as possible."

## Stitching needs continuity, not distinctness

Two patches are glued **where they share** — the overlap *is* the stitching. Two patches with zero overlap cannot be sewn honestly, which is exactly the **locally connected** assumption. What breaks at the extreme is the next section.

## ⚠️ The random-k-NN pull-together failure mode ("How UMAP can go wrong")

The FAQ's own failure page: if a point is maximally far from every other point (it shares no feature with anything under the chosen distance function), then "UMAPs assumption of all points lying on a connected manifold can lead us astray":

- "From this points perspective all other points are equally valid nearest neighbours so its k-nearest neighbour query will return a random selection of neighbours all at this maximal distance."
- The local kernel says a point should be maximally similar to its nearest neighbour — and here all `k` candidates sit at that same maximal distance, so "they will all be considered maximally similar".
- The optimizer then tries "to pull all these randomly selected points together". Add enough such points and the whole embedding is dragged into one blob, destroying the structure the map was meant to show.

The guard is `disconnection_distance`: it will "cut any edge with a distance greater than the value passed in". It defaults to `None`, which resolves to "the maximal value for any of our supported bounded metrics and otherwise set to `np.inf`". Cutting those edges disconnects the manifold, so the orphan point starts where it was initialised and is pushed away from everything else. When vertices do end up disconnected the library throws a warning, and `umap.utils.disconnected_vertices()` lists them (usable as a filter before retraining or plotting).

## Contrast with t-SNE (the global-structure disagreement is still open)

t-SNE states **no** data assumptions: it matches pairwise neighbour probabilities non-parametrically (see [[t-SNE (Dimensionality Reduction)]]). UMAP's three assumptions are what let it claim more — Rohit's L10 headline is "UMAP: faster, better global structure", and his comparison table files UMAP under "Local + some global structure", while the FAQ frames global structure as a goal the failure mode above can break rather than a guarantee. **The ⚠️ Rohit-vs-FAQ disagreement is queued for CP5 mini 4;** this page does not resolve it yet.

## Queued for this concept

Still to come in L10's CP5/CP6 (the fresh 2026-10-13 Scout digest is audited PASS):

- **`n_neighbors`** (CP5 mini 2) — the local↔global dial: the docs say low values "force UMAP to concentrate on very local structure (potentially to the detriment of the big picture)" and large values look at "larger neighborhoods of each point ... losing fine detail structure for the sake of getting the broader of the data". At `n_neighbors=2` UMAP "merely glues together small chains" and leaves singletons; by `20` there is "a fairly good overall view of the data"; at `200` the overall structure is "well captured, but at the loss of some of the finer local structure". Default 15.
- **`min_dist`** (CP5 mini 3) — "how tightly UMAP is allowed to pack points together"; low values give clumpier embeddings, larger values preserve the broad topological structure instead. Default 0.1.
- **CP5 mini 4** — the global-structure claim and the ⚠️ Rohit-vs-FAQ contradiction.
- **CP5 mini 5** — the pipeline (PCA → UMAP → HDBSCAN) and the centering-only vs standardize decision.
- **CP6** — kernel PCA (RBF) and the "high variance = important" contradiction (Rohit's definition vs Shlens's assumption that can fail).

## Open questions

- How much of the "global structure" claim survives the failure mode above, and under what tuning? (CP5 mini 4 — the ⚠️ Rohit-vs-FAQ contradiction.)
- How the local connectivity of each patch is chosen in code, and what it changes. Not yet read.

## My understanding

> **status=learner-note** — the learner's words, verbatim from the 2026-10-13 session (CP5 mini 1), never rewritten. The annotations around them are the tutor's and the source's.

**The elicitation prior (before the mini was taught):**

> "i think for data to lie on a manifold it means it lies in an area of the plot whereby there are many folds(like our swiss roll example). i think the assumption you have to make is that each layer of the fold is a plane"

**Source framing (annotation, not a rewrite):** the second sentence is the idea — "each layer of the fold is a plane" is local flatness — and the session carried it forward as the patch picture. The first sentence's *frame* is what slipped: folding is not what makes something a manifold (an unrolled flat sheet is one too), and a manifold is defined by its local structure, not by being an area with folds.

**The State-rung statements (both partial, both corrected in the same turn):**

> "1. A manifold is simply whatever shape is of dimension 2D or higher. 2. There must be no sharing of points hence there must be distinct neighborhoods."

**Annotations (not rewrites):** (1) a manifold is not a dimension count — a straight line is a 1-D manifold and a flat plane a 2-D one; what defines it is that every sufficiently small patch looks like ordinary flat space. (2) stitching runs on **sharing, not distinctness** — patches are glued where they overlap, and the failure the docs name is the opposite extreme: a point whose nearest neighbours are all maximally far gets a *random* set of k-NN, all treated as maximally similar, which the optimizer then drags together.

## Field notes

- "Learn the surface patch by patch, then glue" is the working one-liner for manifold learning as taught here.
- The 2026-10-13 exit ticket (3/3, all `sure`) landed the three load-bearing pieces: local flatness as the definition, patch → glue → match as the mechanism, and the random-k-NN pull-together failure with `disconnection_distance` as the guard.
- Two guiding questions were spent on the mini (UMAP had no independence evidence on record); both State-rung attempts were generations the learner made himself.
- Standing learner rule (2026-10-05): practices are paper walks or graded MCQ batches; no code writes as a learning-system task.

## Open questions (carried by the lesson)

- CP5 minis 2–5 and CP6 as listed above; then the final cumulative quiz + Feynman explain-back.
