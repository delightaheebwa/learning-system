# t-SNE (Dimensionality Reduction)

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L10 (Dimensionality Reduction) + Wattenberg, Viégas & Johnson, *How to Use t-SNE Effectively*, Distill 2016 · **Lang:** Python (`sklearn.manifold.TSNE`)
> **Insight:** t-SNE maps high-dimensional data into 2D/3D by **preserving which points are near each other** — it builds a probability distribution over point *pairs* (near = high, far = low) and searches for an arrangement whose pair distribution matches it.
> Related: [[PCA (Dimensionality Reduction)]], [[Curse of Dimensionality]], [[Perplexity]], [[KL Divergence]], [[Covariance and correlation]]

## The goal, in the source's words

Rohit, Phase 1 L10: t-SNE "maps high-dimensional data to 2D (or 3D) while preserving which points are near each other." The pitch is explicitly about **neighbourhoods, not distances**: "Points that were neighbors in 784 dimensions stay neighbors in 2D."

Two properties the lesson source states outright:

- **Non-linear.** It "can unfold complex manifolds that PCA cannot." Standard PCA finds linear subspaces — rotate the coordinate system, drop axes — so a curved manifold (a rolled sheet, the classic Swiss roll) has no single linear cut that exposes its structure.
- **For visualization, not preprocessing.** The source's comparison table files t-SNE under "publication-quality 2D plots / local neighborhoods", and its glossary line is "Good for visualization, not for preprocessing."

## The mechanism — and whose mechanism it is

**The pair-probability mechanism is Rohit's, not Distill's.** The construction, as the lesson source gives it: "in the original space, compute a probability distribution over pairs of points based on their distances. Near points get high probability. Far points get low probability. Then find a 2D arrangement where the same probability distribution holds."

So the algorithm has two halves: (1) a high-dimensional pair distribution `P` built from distances, with neighbours carrying high mass; (2) a low-dimensional pair distribution `Q` over the 2D coordinates, plus a search for the coordinates that make `Q` look like `P`. The name expands to *t-Distributed Stochastic Neighbor Embedding*; the details of the low-dimensional kernel and of the objective that scores the `P`-vs-`Q` match are the later CP4 minis (they connect to [[KL Divergence]]), not this page.

**Attribution note (2026-10-08).** An earlier draft of this track credited the probability framing to Distill. That was wrong: the framing above is already in Rohit's lesson text. Distill's distinctive contribution is the **interpretation-caution layer** documented in its own section below.

## Why a linear squash invents false neighbours (CP4 mini 1, 2026-10-08)

The failure mode that motivates a non-linear method, as derived in this track:

- A linear projection can only **shrink or preserve** pairwise distances; it can never enlarge them.
- So a straight squash of a curved manifold never **tears true neighbours apart** — the sheet's local pairs stay close in the shadow.
- But it does **collapse distinct regions onto each other**: the two layers of a rolled sheet land on top of one another, so points that were far apart in the original space become apparent neighbours. These are **false neighbours**.
- The learner's own phrasing: "non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case." The flattened picture is a **smeared shadow** of the sheet, not the unrolled sheet.

That asymmetry — never tear, but often merge — is the precise sense in which PCA "cannot" show a manifold's structure, and it is the property t-SNE's pair-distribution match is built to defend.

## The interpretation-caution layer (Distill 2016)

Distill's essay is a catalogue of ways to misread a t-SNE picture. The headline cautions:

- **Cluster sizes mean nothing.** t-SNE "naturally expands dense clusters, and contracts sparse ones, evening out cluster sizes" — density equalisation is **by design**, not an ordinary distance distortion. Two Gaussians, one 10× more dispersed than the other, come out looking about the same size.
- **Distances between clusters may mean anything or nothing.** "The basic message is that distances between well-separated clusters in a t-SNE plot may mean nothing." Global geometry comes through only at the right perplexity, and the right value is data-dependent: in the essay's three-Gaussian example, perplexity 50 read the geometry well, lower values made the clusters look equidistant, and with 200 points per cluster *none* of the trial perplexities recovered it.
- **Random noise looks structured at low perplexity.** On 500 points drawn from a unit Gaussian in 100 dimensions, the perplexity-2 plot "seems to show dramatic clusters" — pure artifact. The same example doubles as a win: the perplexity-30 plot's oddly even density is a truthful statement about high-dimensional Gaussians, more accurate than a linear projection could be.
- **Stopping early invents shapes.** Non-converged runs give "seemingly 1-dimensional and even pointlike images" of the clusters; "if you see a t-SNE plot with strange 'pinched' shapes, chances are the process was stopped too early." Runs may also differ wildly — in the trefoil-knot example, three of five perplexity-2 runs introduced artificial breaks, while five perplexity-50 runs were visually identical up to symmetry. Stochasticity is a reading hazard, not just a nuisance.
- **Density equalisation distorts shape subtly even when it works.** Long parallel clusters come out slightly bowed outward, because the middles are denser and get magnified relative to the ends; contained clusters are exaggerated in size.
- **For topology, use several plots.** Low and high perplexity can tell different stories about containment or connectedness, and the essay's own recommendation is to analyse multiple perplexities.

## ⚠️ Sources disagree on cluster distances

- **Rohit (unconditional):** "Distances between clusters in the output are not meaningful. Only the clusters themselves are."
- **Distill (conditional):** distances between well-separated clusters "may mean nothing" — *at arbitrary perplexity*. In their three-Gaussian example, perplexity 50 did give a good sense of the global geometry; low perplexity flattened the clusters to looking equidistant.

**Resolution carried in this track:** Rohit's blanket rule is the **safe default**; Distill's "distances can be read if the perplexity is tuned" is the **fragile exception**. Both hold at their own scope — the unconditional claim is what to believe unless you have deliberately tuned perplexity and verified the picture is stable on your own data. It stays flagged as a live contradiction until CP4 mini 4 teaches it.

## Perplexity (the knob) — opening, not yet taught here

Both sources describe perplexity as the neighbour-count knob. Rohit: it "controls how many neighbors to consider (typical range: 5-50)". Distill calls it "a guess about the number of close neighbors each point has" and quotes the original paper's "typical values are between 5 and 50", then adds two refinements: the effect "is more nuanced than that" — "getting the most from t-SNE may mean analyzing multiple plots with different perplexities" — and it should stay **smaller than the number of points** (the essay was edited to correct implementations that misbehave otherwise).

The bridge to this track's existing math — perplexity as `2^H` applied to the neighbour distribution (see [[Perplexity]]) — is **CP4 mini 2**; this page records the source facts and leaves that derivation open.

## Other flags from the source

- **Stochastic:** "Different runs produce different layouts."
- **Slow:** `O(n²)` pairwise by default; the source's table says "Slow (< 10k samples ideal)".
- **UMAP has the analogous knob:** `n_neighbors`, "similar to perplexity" — CP5.

## Open questions

- **Perplexity as `2^H`** on the neighbour distribution (and the name-collision with [[Perplexity]]'s uniform yardstick) — **CP4 mini 2**.
- **The objective:** how the mismatch between `P` and `Q` is scored, which direction the divergence runs, and why that asymmetry matters — **CP4 mini 3**, bridging to [[KL Divergence]].
- **The Rohit-vs-Distill contradiction** above — currently resolved as safe-default vs fragile-exception; to be taught and stress-tested at **CP4 mini 4**.
- **How much of the t-SNE fix is the objective and how much is redefining "neighbourhood" locally?** Raised on [[Curse of Dimensionality]] and still open; CP4–CP5.

## Field notes

- "non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case" — the CP4 mini 1 elicitation landing, in the learner's own words.
- "flat 2D plane; neighbors stay neighbors" — the first prediction (right about the flatten, wrong about the neighbours), which set up the two guiding questions.
- Check-back confirmed the "why now": PCA's squash blurs the neighbourhood pattern; t-SNE's job is defending it, with failure modes of its own to be named before trusting any picture.
