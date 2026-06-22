# RQ2 pre-study: Doc-to-model (SAD-SAM) bias check and trivial baselines

Companion to `RQ2_TRIVIAL_BASELINES.md`. The doc-to-code pre-study showed file-level micro F1 is dominated by enrollment inflation, block correlation, and gold concentration. Doc-to-model gold links are sentence -> architecture component (no enrollment, one human decision per link), so those exact biases do not carry over. This report tests three candidate biases that might still motivate the bias-corrected metric suite on doc-to-model.

Bias hypotheses tested:

- **H1 — Component popularity skew.** A few popular components attract most sentence-link mass, so any 'always vote popular' baseline can fool micro F1.
- **H2 — Sentence-link asymmetry.** A handful of sentences link to many components while most link to 0 or 1; micro F1 hides this.
- **H3 — Narrative / referential split.** Many doc sentences contain no gold links at all; sentence-level evaluation needs to know that.

## 1. Per-project gold standard characterisation

### 1a. Basic counts

| Project | # gold links | # components | # doc sentences | # gold sentences |
|---|---|---|---|---|
| mediastore | 31 | 19 | 37 | 27 |
| teastore | 27 | 19 | 43 | 23 |
| teammates | 57 | 14 | 198 | 45 |
| bigbluebutton | 62 | 22 | 87 | 48 |
| jabref | 18 | 6 | 13 | 10 |

### 1b. H1 — Component popularity skew

| Project | Top-3 component share | Max single-component share | Gini (over all components) |
|---|---|---|---|
| mediastore | 0.516 | 0.226 | 0.680 |
| teastore | 0.630 | 0.222 | 0.741 |
| teammates | 0.596 | 0.263 | 0.635 |
| bigbluebutton | 0.548 | 0.226 | 0.713 |
| jabref | 0.778 | 0.333 | 0.352 |

### 1c. H2 — Links per sentence (gold sentences only)

| Project | p50 | p90 | p99 | max | Share of gold sentences with >=5 links |
|---|---|---|---|---|---|
| mediastore | 1.0 | 2.0 | 2.0 | 2 | 0.000 |
| teastore | 1.0 | 2.0 | 2.0 | 2 | 0.000 |
| teammates | 1.0 | 2.0 | 4.8 | 7 | 0.022 |
| bigbluebutton | 1.0 | 2.0 | 3.0 | 3 | 0.000 |
| jabref | 1.5 | 3.0 | 3.0 | 3 | 0.000 |

### 1d. H3 — Narrative / referential split

| Project | Fraction of doc sentences with no gold links |
|---|---|
| mediastore | 0.270 |
| teastore | 0.465 |
| teammates | 0.773 |
| bigbluebutton | 0.448 |
| jabref | 0.231 |

## 2. Trivial baselines

- **Random**: `random.Random(42)`; samples (sentence, component) pairs uniformly from gold-sentences x all-components until the prediction count matches the gold link count.
- **Top-3**: every gold sentence linked to the 3 components with the most gold links overall in the project. (Different from the doc-to-code Top-3 which voted by enrolled file count — file count does not exist here.)

### 2.1 Random

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.065 | 0.074 | 0.088 | 0.048 | 0.333 | **0.122** |
| Per-component F1 (macro) | 0.047 | 0.038 | 0.053 | 0.018 | 0.265 | **0.084** |
| Per-sentence F1 (macro) | 0.074 | 0.051 | 0.068 | 0.038 | 0.287 | **0.104** |
| Sentence coverage | 0.074 | 0.087 | 0.111 | 0.062 | 0.600 | **0.187** |
| Noise rate | 0.913 | 0.956 | 0.889 | 0.946 | 0.607 | **0.862** |

### 2.2 Top-3

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.286 | 0.354 | 0.354 | 0.330 | 0.583 | **0.381** |
| Per-component F1 (macro) | 0.098 | 0.197 | 0.150 | 0.103 | 0.379 | **0.185** |
| Per-sentence F1 (macro) | 0.274 | 0.352 | 0.338 | 0.314 | 0.530 | **0.362** |
| Sentence coverage | 0.519 | 0.739 | 0.644 | 0.542 | 0.700 | **0.629** |
| Noise rate | 0.802 | 0.754 | 0.748 | 0.764 | 0.533 | **0.720** |

### 2.3 Head-to-head (Random vs Top-3)

| Project | Random micro_F1 | Top-3 micro_F1 | Random comp_F1 | Top-3 comp_F1 | Random coverage | Top-3 coverage |
|---|---|---|---|---|---|---|
| mediastore | 0.065 | 0.286 | 0.047 | 0.098 | 0.074 | 0.519 |
| teastore | 0.074 | 0.354 | 0.038 | 0.197 | 0.087 | 0.739 |
| teammates | 0.088 | 0.354 | 0.053 | 0.150 | 0.111 | 0.644 |
| bigbluebutton | 0.048 | 0.330 | 0.018 | 0.103 | 0.062 | 0.542 |
| jabref | 0.333 | 0.583 | 0.265 | 0.379 | 0.600 | 0.700 |
| **macro mean** | **0.122** | **0.381** | **0.084** | **0.185** | **0.187** | **0.629** |

### 2.4 Prediction sizes per baseline

| Project | |gold| | |random pred| | |top-3 pred| |
|---|---|---|---|
| mediastore | 31 | 31 | 81 |
| teastore | 27 | 27 | 69 |
| teammates | 57 | 57 | 135 |
| bigbluebutton | 62 | 62 | 144 |
| jabref | 18 | 18 | 30 |

## 3. Verdict

**Q1 — Does H1 hold?** Yes, decisively. The top-3 components hold a mean **61%** of all gold links across the 5 projects (range 0.52-0.78), the single most popular component owns **25%** on average (range 0.22-0.33), and the component-mass Gini averages **0.62** (range 0.35-0.74). This is enough skew that voting for the 3 most popular components is a non-trivial baseline: Top-3 reaches **micro F1 0.38** on doc-to-model, **3.1x** the Random baseline (0.12). Without a per-component view this would look like real signal.

**Q2 — Does H2 hold?** Only weakly. The per-sentence link distribution is concentrated near 1-2 (p50=1 on every project, p90=2 on four of five), and only a single project (teammates) shows any sentences with >=5 gold links — mean share **0.4%**. So the per-sentence F1 macro generally does **not** tell a different story from micro F1 on doc-to-model; with maxes of 2-3 links per sentence there is little asymmetry for macro averaging to expose. This is the weakest of the three biases on this task.

**Q3 — Does H3 hold?** Yes — strongly, and surprisingly. Across the 5 projects, on average **44%** of doc sentences carry no gold link at all (range 0.23-0.77, with teammates at 0.77). Even on the smallest doc (jabref, 13 lines) 23% are unlinked. This means the per-sentence F1 macro restricted to gold sentences and sentence coverage / noise rate carry information that micro F1 obscures: systems can hit the gold sentences they choose, but most of the document is narrative they must learn to ignore. False positives on unlinked sentences are invisible to per-sentence macro F1 over gold sentences but show up immediately in the noise rate.

**Q4 — Does the doc-to-code reversal pattern repeat?** Partially — the sign flips at the component level on the easier projects. Macro mean micro F1 ranks **Top-3 (0.38) > Random (0.12)**, matching expectation, but per-component F1 macro is **0.19 vs 0.08** — still Top-3 ahead in mean, however the gap collapses sharply (Top-3 averages F1=0 on the 16-19 components it ignores, dragging the macro down). Sentence coverage actually agrees with micro F1 here: Top-3 (0.63) > Random (0.19), because hitting any of the 3 huge components covers many sentences. The cleanest reversal-style signal is therefore **noise rate**: Top-3 averages **0.72** wrong links per sentence (down from 0.86), but a real system that learns the top-3 trick still pays a heavy noise tax that micro F1 does not capture. The pattern is stronger on the larger / narrative-heavy projects (teammates, bigbluebutton) than on the smaller, densely-linked jabref.

**Q5 — Overall recommendation.** The metric suite does earn a (more modest) place on doc-to-model, motivated primarily by **H1** with strong support from **H3**. H1 is the main reason micro F1 alone is unsafe: a system that always votes for the 3 most popular components already gets micro F1 in the 0.29-0.58 range, indistinguishable from a real-but-weak linker. The per-component F1 macro, sentence coverage, and noise rate together discriminate trivial-popular from real linkers in a way micro F1 cannot. H3 (high narrative fraction) adds force to the noise rate, since most of the doc is not link-bearing and false positives there must be visible. H2 is too thin on this gold to justify per-sentence macro on its own; on doc-to-model the per-sentence macro is best framed as a side effect of needing sentence coverage / noise rate rather than as a standalone motivator. So: keep the suite, but cite **component popularity skew (H1) + narrative split (H3)** as the doc-to-model justification; do not reuse the doc-to-code enrollment / block-correlation arguments verbatim.

---

Script: `src/bias/rq2_doc_to_model_prestudy.py`. Reproduce: `python3 src/bias/rq2_doc_to_model_prestudy.py`.
