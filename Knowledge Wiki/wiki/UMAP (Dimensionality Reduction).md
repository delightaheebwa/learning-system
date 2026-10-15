<!-- provenance: status=synthesis | source=Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap.md (umap-learn docs) + 2026-10-13 - dimensionality-reduction - umap-params.md (Basic UMAP Parameters) + 2026-10-13 - dimensionality-reduction - umap-paper.md (McInnes & Healy 2018, ArXiv 1802.03426, Definition 11 / Algorithm 5) + 2026-10-13 - dimensionality-reduction - umap-faq.md + 2026-10-13 - dimensionality-reduction - rohit.md (Rohit P1 L10) | verified-by=— | date=2026-10-14 | learner-note block: the "## My understanding" section is the learner's verbatim note (learner-note; five statements as of 2026-10-14 — two from 2026-10-13, three appended 2026-10-14, nothing overwritten) -->

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

## The two dials

UMAP's two load-bearing knobs act on **different sides of the pipeline** — and the 2026-10-14 pause exit ticket showed that separation is not yet automatic: `n_neighbors` shapes the *input* graph, `min_dist` shapes only the *output* layout.

### `n_neighbors` — the INPUT-side dial (a hard integer)

The docs: `n_neighbors` "controls how UMAP balances local versus global structure in the data. It does this by constraining the size of the local neighborhood UMAP will look at when attempting to learn the manifold structure of the data. This means that low values of `n_neighbors` will force UMAP to concentrate on very local structure (potentially to the detriment of the big picture), while large values will push UMAP to look at larger neighborhoods of each point when estimating the manifold structure of the data, losing fine detail structure for the sake of getting the broader of the data." Default **15**; the docs sweep 2 → 200 on an 800-point colour cube.

- **A hard integer, one fixed list length for the whole run** — not a per-point soft count. That is the exact contrast with [[t-SNE (Dimensionality Reduction)|perplexity]]: perplexity is an *effective* number of neighbours (`Per(P_i) = 2^{H(P_i)}`) against **one user-set target shared by every point** (a non-integer such as 23.7 is legal on that knob), and what varies per point is the bell width `σ_i`, binary-searched until *that* point's `Per(P_i)` equals the target — while `n_neighbors` is a literal k handed to a k-NN query. Rohit's L10 files the knob as "how many neighbors define local structure (similar to perplexity). Higher values preserve more global structure" — the same *role*, a different *object*.
- **Why k carries the whole local↔global balance by itself:** each point gets a local chart of its k neighbours, and the charts are glued where they overlap. Small k ⇒ charts barely overlap ⇒ UMAP "merely glues together small chains" and, "due to the narrow/local view, fails to see how those connect together. It also leaves many different components (and even singleton points)" — "from a fine detail point of view the data is very disconnected and scattered throughout the space". Large k ⇒ charts overlap nearly everywhere ⇒ the map coheres, "but at the loss of some of the finer local structure (individual colors are no longer necessarily immediately near their closest color match)". There is **no separate global module** in the construction; nothing else gets to say what "global" means, so k is the only thing holding that end of the trade.
- **The anchor sweep (docs, k = 2 / 20 / 200):** at `n_neighbors=2` the "narrow/local view" fails to see how the chains connect; by `20` "we have a fairly good overall view of the data showing how the various colors interelate to each other over the whole dataset"; at `200` "the overall structure (blues, greens, and reds; high luminance versus low) is well captured, but at the loss of some of the finer local structure". The docs call this "the local/global tradeoff provided by `n_neighbors`".
- **The paper's version of the same dial:** n is "the local scale at which to approximate the manifold as roughly flat, with the manifold estimation averaging over the n neighbors. Manifold features that occur at a smaller scale than within the n nearest-neighbors of points will be lost"; smaller n "ensure[s] detailed manifold structure is accurately captured (at a loss of the 'big picture' view of the manifold)", larger n captures "large scale manifold structures, but at a loss of fine detail structure which will get averaged out in the local approximations", and "With smaller n values the manifold tends to be broken into many small connected components".
- **What the k neighbours normalise to:** the local kernel's cardinality is fixed, not just its list length — the paper sets `Σ_j exp(−max(0, d(x_i, x_j) − ρ_i)/σ_i) = log₂(k)`, with `ρ_i` the distance to the nearest neighbour (which "ensures that x_i connects to at least one other data point with an edge of weight 1; this is equivalent to the resulting fuzzy simplicial set being locally connected at x_i") and `σ_i` found by binary search (Algorithm 3). So k is also the patch's *membership mass*, fixed at `log₂(k)`.

### `min_dist` — the OUTPUT-side dial (the packing floor)

The docs: `min_dist` "controls how tightly UMAP is allowed to pack points together. It, quite literally, provides the minimum distance apart that points are allowed to be in the low dimensional representation." Default **0.1**; the docs sweep 0.0 → 0.99.

- **Output side, by the paper's own definition:** min-dist is "a hyperparameter directly affecting the output, as it controls the fuzzy simplicial set construction from the low dimensional representation. It acts in lieu of the distance to the nearest neighbor used to ensure local connectivity. In essence this determines how closely points can be packed together in the low dimensional representation" — and the paper calls it "an essentially aesthetic parameter, governing the appearance of the embedding".
- **The anchor sweep (docs, 0.0 → 0.99):** at `min_dist=0.0` "UMAP manages to find small connected components, clumps and strings in the data, and emphasises these features in the resulting embedding"; as the value rises "these structures are pushed apart into softer more general features, providing a better overarching view of the data at the loss of the more detailed topological structure". Low values give "clumpier embeddings" — useful "if you are interested in clustering, or in finer topological structure".
- **It never touches the graph.** The charts, their overlaps and any disconnected vertices are all settled on the input side, before the low-dimensional packing begins, so **a fragmented graph stays fragmented whatever `min_dist` is set to.** Fragmentation is a connectivity (`n_neighbors`) story, not a spacing story.
- **The floor arrives as a force curve, not a wall.** The paper defines the target membership `Ψ` piecewise — `1` if `‖x − y‖₂ ≤ min-dist`, otherwise `exp(−(‖x − y‖₂ − min-dist))` — and then fits a smooth, differentiable approximation `Φ(x, y) = (1 + a‖x − y‖₂^{2b})⁻¹`, "where a and b are chosen by non-linear least squares fitting against the curve Ψ"; Algorithm 5 then descends on `log Φ` ("Fit Φ from Ψ defined by min-dist"). Same shape as t-SNE's low-D side: a well that packs points down to the floor, with repulsion that fires below it.
- **⚠️ Sources disagree on how hard the floor is.** The docs are literal — "quite literally, provides the minimum distance apart that points are allowed to be" — while the paper's own optimisation only *penalises* sub-floor placements, because what is fitted is a smooth curve approximating a piecewise rule. **Resolution (taught 2026-10-14):** the practical reading is *the optimizer strongly resists packing points closer than `min_dist`*, and the mechanism is *a gradient penalty, not a hard constraint*. The two readings agree on the observable behaviour (0.0 ⇒ clumps and strings; larger values ⇒ structures spread "into softer more general features") and disagree only on the language of enforcement.

**The knob-crossing failure mode (2026-10-14 exit ticket).** The two dials are easy to swap under pressure: item X3 placed `min_dist` on the *input* side of the pipeline, and item X1 gave only the gain half of the `n_neighbors` trade. The separator is one sentence — *`min_dist` never touches the graph*: if the question is about charts, neighbours, connectivity or components, the dial is `n_neighbors`; if it is about packing, spacing or the look of the picture, it is `min_dist`.

## Contrast with t-SNE (the global-structure disagreement is still open)

t-SNE states **no** data assumptions: it matches pairwise neighbour probabilities non-parametrically (see [[t-SNE (Dimensionality Reduction)]]). UMAP's three assumptions are what let it claim more — Rohit's L10 headline is "UMAP: faster, better global structure", and his comparison table files UMAP under "Local + some global structure", while the FAQ frames global structure as a goal the failure mode above can break rather than a guarantee. **The ⚠️ Rohit-vs-FAQ disagreement is queued for CP5 mini 4;** this page does not resolve it yet.

## Queued for this concept

Still to come in L10's CP5/CP6:

- **CP5 mini 4 — the global-structure claim.** Rohit's L10 headline is "UMAP: faster, better global structure" and his comparison table files UMAP under "Local + some global structure"; the paper hedges it — UMAP "is competitive with t-SNE for visualization quality, and arguably preserves more of the global structure with superior run time performance" — and the FAQ frames it as a *goal* the failure mode above can break ("by preserving more global structure and creating meaningful separation between connected components of the manifold on which the data lies, UMAP offers more meaningful clusters"), not a guarantee. **The ⚠️ Rohit-vs-FAQ disagreement is queued for CP5 mini 4**; this page does not resolve it.
- **CP5 mini 5** — the pipeline (PCA → UMAP → HDBSCAN) and the centering-only vs standardize decision.
- **CP6** — kernel PCA (RBF) and the "high variance = important" contradiction (Rohit's definition vs Shlens's assumption that can fail).

The two dials above were taught and sealed on 2026-10-14 (CP5 minis 2–3), so they are **no longer queued** — their page sections are live.

## Open questions

- How much of the "global structure" claim survives the failure mode above, and under what tuning? (CP5 mini 4 — the ⚠️ Rohit-vs-FAQ contradiction, and the paper's own "arguably" hedge.)
- How the local connectivity of each patch is chosen in code, and what it changes — **partly answered 2026-10-14:** `ρ_i` is the distance to the nearest neighbour (so each point connects to at least one other with weight 1, i.e. local connectivity at that point) and `σ_i` is binary-searched until the patch's memberships sum to `log₂(k)` (paper Algorithms 2–3). Still unread: the `local_connectivity` / spectral-initialisation corner cases in code.

## My understanding

> **status=learner-note** — the learner's words, verbatim from the 2026-10-13 session (CP5 mini 1), never rewritten. The annotations around them are the tutor's and the source's.

**The elicitation prior (before the mini was taught):**

> "i think for data to lie on a manifold it means it lies in an area of the plot whereby there are many folds(like our swiss roll example). i think the assumption you have to make is that each layer of the fold is a plane"

**Source framing (annotation, not a rewrite):** the second sentence is the idea — "each layer of the fold is a plane" is local flatness — and the session carried it forward as the patch picture. The first sentence's *frame* is what slipped: folding is not what makes something a manifold (an unrolled flat sheet is one too), and a manifold is defined by its local structure, not by being an area with folds.

**The State-rung statements (both partial, both corrected in the same turn):**

> "1. A manifold is simply whatever shape is of dimension 2D or higher. 2. There must be no sharing of points hence there must be distinct neighborhoods."

**Annotations (not rewrites):** (1) a manifold is not a dimension count — a straight line is a 1-D manifold and a flat plane a 2-D one; what defines it is that every sufficiently small patch looks like ordinary flat space. (2) stitching runs on **sharing, not distinctness** — patches are glued where they overlap, and the failure the docs name is the opposite extreme: a point whose nearest neighbours are all maximally far gets a *random* set of k-NN, all treated as maximally similar, which the optimizer then drags together.

### 2026-10-14 — CP5 minis 2–3 (`n_neighbors` and `min_dist`)

> **status=learner-note** — three more of the learner's statements, verbatim from the 2026-10-14 session, **appended** (nothing from 2026-10-13 was altered). The annotations around them are the tutor's and the source's.

**The State-rung statement — the leaf analogy (`n_neighbors`):**

> "small patch chain produces a map that's like zooming into a leaf and seeing the fine detail of things like the stomata but you don't see how all that fine detail comes together to form the overall leaf structure while the big patch chain is like zooming out and seeing that same leaf from afar... you see the overall leaf structure but you can't see the fine detail that brings it together."

**Source framing (annotation, not a rewrite):** accepted as-is — both ends of the trade are right, and the "small patch chain" is the docs' own picture (at k = 2 UMAP "merely glues together small chains"). The session *extended* it rather than correcting it: k is each point's chart size, the charts' **overlap** is what glues the map, and there is no separate global module — which is why one number moves the picture from stomata-resolved to leaf-resolved.

**The State-rung statement — the box-packer analogy (`min_dist`):**

> "min_dist is the guy that tells you how tightly to pack those set of items in that box. the higher it is, then you are to pack the items with more spacing between them while the lower it is, then you are to pack the items with less spacing."

**Source framing (annotation, not a rewrite):** direction correct at both ends, and it uses the docs' own verb ("how tightly UMAP is allowed to pack points together"). One refinement taught in-session: the floor is **permissive** — points may pack down *to* it, never through it — and raising the value reshapes the whole attraction/repulsion curve, so the entire picture softens, not just the tightest pairs.

**The closing statement — the trigger:**

> "it kicks in when two points try to go lower than the floor in terms of distance between them."

**Source framing:** complete and correct, and checkable against the paper: what fires on sub-floor pairs is repulsion through the fitted `Φ`, not a hard wall (the ⚠️ disagreement above).

## Field notes

- "Learn the surface patch by patch, then glue" is the working one-liner for manifold learning as taught here.
- The 2026-10-13 exit ticket (3/3, all `sure`) landed the three load-bearing pieces: local flatness as the definition, patch → glue → match as the mechanism, and the random-k-NN pull-together failure with `disconnection_distance` as the guard.
- Two guiding questions were spent on the mini (UMAP had no independence evidence on record); both State-rung attempts were generations the learner made himself.
- Standing learner rule (2026-10-05): practices are paper walks or graded MCQ batches; no code writes as a learning-system task.
- The 2026-10-14 warm-up re-passed the mini-1 material 3/3, all `sure`, 0 hints (local flatness as the definition; patch → glue → match; the random maximally-similar k-NN pull-together ahead of `disconnection_distance`).
- The two dials were taught and sealed on 2026-10-14 (CP5 minis 2–3): `n_neighbors` with the leaf analogy, `min_dist` with the box-packer analogy and the closing trigger statement; two tie-downs passed 2/2 (0.0 removes the output-side floor; fragmentation is charts failing to overlap, not spacing).
- Two guiding questions were spent on mini 2 (still no independence evidence on record); mini 3 ran elicitation → tie-downs → idea → check-and-extend, with the learner generating both analogies himself.
- **Exit ticket 1/3, all `sure`, 0 hints** — X1 ✗ gains-only `n_neighbors` trade (the asked half omitted), X2 ✓ (charts stop overlapping ⇒ components and singletons float), X3 ✗ `min_dist` placed on the input side. Both fails are the **knob-crossing slip** firing twice in one batch; the learner banked the repair for a later warm-up, so the self-attribution is unelicited and the ledger row stays `active`.
- The ⚠️ docs-vs-paper reading of the floor was surfaced in-session and resolved to *strong resistance / gradient penalty* (see `## The two dials`).

## Open questions (carried by the lesson)

- CP5 mini 4 (the global-structure claim + the ⚠️ Rohit-vs-FAQ contradiction), CP5 mini 5 (the pipeline and the scaling decision) and CP6 (kernel PCA + the "high variance = important" contradiction); then the final cumulative quiz + Feynman explain-back.
- The banked X1/X3 repair — the knob-separation warm-up the learner asked to defer.
