# Component-Centric Metric Suite — Level-Agnostic (macro/micro unification)

Source: `src/bias/component_suite.py`. Reuses `calc_metrics` only (no new F1 math).
Reproduce: `python3 src/bias/component_suite.py` → `reports/COMPONENT_SUITE_sad-model.csv`
+ `reports/COMPONENT_SUITE_sad-code.csv`.

Systems compared: **swattr/transarc** (ARDoCo heuristic SAD-SAM; at doc-to-code =
SWATTR ⋈ ArCoTL), **s20linker** (agent-linker s_linker20; doc-to-code composed
through ArCoTL SAM-CODE), **artemis** (TAAS25 LLM SOTA; direct doc-to-code).

## The suite

For each system at a granularity, on (sentence, component) pairs:

| metric | definition | role |
|---|---|---|
| `micro` | pooled (sentence, component) F1 (= link F1 at SAD-SAM) | anchor |
| `macro` | per-component F1, unweighted mean | headline |
| `gap` | `micro − macro` — signed indicator of the skew regime | diagnostic |
| `min_comp` | worst single-component F1 | tail |
| `pct_missed` | fraction of components scored exactly 0 | coverage |
| `gold_gini` | Gini of gold #sentences-per-component (descriptor, not a score) | context |

The suite "exploits the unequal sentence↔component distribution" and applies at
**both** doc-to-model and doc-to-code.

## ⚠ Reconciled component universe (and what it corrected)

Two legacy per-component-F1 definitions disagreed on the universe:
`evaluation_critique._compute_component_f1` (micro) keeps files with **no**
SAM-CODE mapping as their own singleton component (`{b}` fallback);
`rq2_trivial_baselines.per_component_macro_f1` (macro) **drops** them (`()`).
Comparing those two is not apples-to-apples.

This suite computes micro **and** macro on the **same mapped-only universe**.
Effect at doc-to-code:

| | legacy (mismatched) | reconciled |
|---|---|---|
| swattr/transarc avg gap | −0.099 | **−0.019** |
| bigbluebutton swattr gap | −0.31 | **−0.05** |

**A large part of the apparent "enrollment-inflation gap" was a universe-mismatch
artifact, not aggregation.** Once reconciled, the micro/macro *aggregation* effect
is modest at both levels. Note: suite-`micro` therefore differs from the paper's
current headline `component_f1` (which uses the `{b}`-fallback micro) — e.g.
swattr/transarc avg micro 0.795 here vs 0.714 in `reports/metrics_sad-code.csv`.
Here 0.714 is the `{b}`-fallback micro on the *same* (default `results/`) source —
matching the paper headline `component_f1` ≈ 0.7143 — not the older standalone
`reports/metrics_sad-code.csv` (which reports 0.732 from a different result source).
Reconciling `metrics_api` to one universe is tracked as project work (CMP-02).

## Results — doc-to-model (mild natural skew)

| system | micro | macro | gap | min_comp | pct_missed |
|---|---|---|---|---|---|
| s20linker | 0.889 | 0.875 | +0.014 | **0.580** | 0.017 |
| artemis | 0.835 | 0.813 | +0.022 | **0.279** | 0.083 |
| swattr/transarc | 0.799 | 0.793 | +0.006 | **0.482** | 0.060 |

gold_gini ≈ 0.27 (busiest component carries 6–15 sentences vs median 3–5).

## Results — doc-to-code (enrollment skew, reconciled)

| system | micro | macro | gap | min_comp | pct_missed |
|---|---|---|---|---|---|
| s20linker | 0.858 | 0.852 | +0.006 | **0.546** | 0.018 |
| artemis | 0.799 | 0.788 | +0.011 | **0.345** | 0.053 |
| swattr/transarc | 0.795 | 0.813 | −0.019 | **0.544** | 0.060 |

## Findings

1. **micro/macro aggregation is a second-order effect once the universe is
   reconciled.** Per-project gaps stay within ±0.07; averages within ±0.02 at both
   levels. The previously-dramatic gaps mixed aggregation with the universe
   mismatch above. The `gap`'s *sign* still fingerprints the skew regime
   (slightly positive at doc-to-model, slightly negative at doc-to-code where
   enrollment over-weights big components in micro), but its magnitude is small.

2. **Tail coverage is the first-order, level-stable discriminator — and it indicts
   artemis.** At *both* levels artemis has by far the worst `min_comp`
   (0.345 / 0.279) and scores `min_comp = 0` on bigbluebutton and jabref: the LLM
   nails popular components and **abandons the long tail**. By `micro`/link F1
   artemis looks competitive (2nd); by worst-component coverage it is last. The
   heuristic SWATTR is more *uniform* across components despite a lower headline.
   `micro` and `macro` both hide this; only the tail half of the suite catches it.

3. **The suite generalizes across granularities.** Same five columns, coherent
   narrative at both levels. What shifts is which column carries the signal:
   the (small) `gap` leans negative under enrollment at doc-to-code, while tail
   coverage does the discriminating at both levels. "Unify macro and micro" lands
   as: **macro = headline, gap = skew-regime indicator, min/pct_missed = tail
   coverage, micro = anchor/gap term** — one object, two levels.

## Caveats / open items

- Reconcile `metrics_api.compute_sad_code_metrics` (and the paper headline) to the
  single mapped-only universe, or document the two definitions explicitly.
- swattr ≡ transarc at doc-to-code in this repo (SWATTR ⋈ ArCoTL); reported as one
  column. The live contrast is heuristic (uniform) vs LLM (peaky-but-leaky).
- External result roots (`agent-linker/`, `sota/recovered-links/`) must be present;
  absent systems are skipped with a warning.
