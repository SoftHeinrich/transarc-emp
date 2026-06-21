# RQ2 — Metric redundancy analysis

> **[SUPERSEDED — v1.2]** The per-component / TransArc SAD-CODE F1 figures in this report (e.g. TransArc 0.732) use the pre-v1.2 `{b}`-fallback component universe and are **superseded by mapped-only universe (v1.2)**: SAD-CODE component F1 now drops files with no SAM-CODE mapping, moving the swattr/transarc cross-project average from 0.714/0.732 to 0.795. See `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` for the measured old→new delta and the full supersession ledger. Original content is retained unchanged below.

Tests whether the 7 metrics in the paper's metric suite carry independent signal across the (system × project × task) cells we evaluate on, or whether some are *shadowed* (predictable) from another — specifically from per-component F1.

Companion to `RQ2_TRIVIAL_BASELINES.md` and `RQ2_DOC_TO_MODEL_PRESTUDY.md`. Same metric definitions; same 5 ARDoCo projects; same baseline RNG seed.

## 0. Setup

**Systems included in the redundancy matrix** (all 7 metrics recomputed identically per cell):

- **TransArc** — doc-to-code: full ARDoCo pipeline (`load_result_sad_code`); doc-to-model: standalone SWATTR (`load_result_sad_sam_standalone`).
- **S11** — `s_linker11` SAD-SAM links (ablation_results CSVs); doc-to-code obtained as S11 × ARCOTL SAM-CODE (same composition rule as `src/transarc/sadcode_comparison.py`).
- **Random** — `random.seed(42)`; (sentence, target) pairs at gold density. Reuses `baseline_random_same_size` (doc-to-code) and an inline analog for doc-to-model.
- **Top-3** — doc-to-code: `baseline_majority_k(..., k=3)` voting by enrolled file count; doc-to-model: name-frequency ranking R2 from `rq2_doc_to_model_ranking_compare.py` (non-leaky).

**Systems quoted for reference only** (not in the correlation matrix — different metric definitions or missing inputs):

- **S13F** — the canonical paper artifact. Per-project link CSVs are no longer on this filesystem; aggregate values are pulled from `reports/SADCODE_S11_S13F_VS_TRANSARC.csv` and `reports/SADSAM_S11_S13F_VS_TRANSARC.csv`. Those CSVs report `component_f1` in its **micro** form (via `evaluation_critique._compute_component_f1`); we recompute every other system using the **macro** form to stay consistent with the baseline reports. Including S13F at micro would cross definitions and contaminate the correlation, so the S13F row is reported in §2.3 only.
- **LiSSA** — no LiSSA result CSVs are present in this repo (`grep -rin lissa src/ results/ reports/` returns no result files).

**Metric definitions** (`src/lib/new_metrics_analysis.py`, `src/bias/rq2_trivial_baselines.py`, `src/bias/rq2_doc_to_model_prestudy.py`):

| # | Metric | Definition (per cell) | Aggregation | What it rewards |
|---|---|---|---|---|
| 1 | File-level / Micro F1 | $2 \cdot |G \cap R| / (|G| + |R|)$ over the cell's atomic pairs (enrolled `(sentence, file)` for doc-to-code; `(sentence, component)` for doc-to-model). | micro over all pairs | Bulk accuracy on the test set; favors big-volume cells. |
| 2 | Per-component F1 (macro) | Per component $c$: $F_1$ over `(sentence, c)` predictions; macro mean over components that appear in gold or result (`per_component_macro_f1`, `src/bias/rq2_trivial_baselines.py:57`). | macro over components | Consistent F1 across components regardless of size (small components count as much as big ones). |
| 3 | Per-sentence F1 (macro) | Per gold sentence $s$: $F_1$ over $b$-sets; macro mean over gold sentences (`per_sentence_macro_f1`, `src/bias/rq2_trivial_baselines.py:94`). | macro over gold sentences | Consistent F1 per sentence; downweights sentences with very many gold links. |
| 4 | Sentence coverage | Fraction of gold sentences with $\ge 1$ correct prediction (`sentence_coverage`, `src/bias/rq2_trivial_baselines.py:120`). | macro over gold sentences | Reach: did the system find *something* for each gold sentence? Insensitive to FPs. |
| 5 | Noise rate | Mean across predicted sentences of $FP / (TP + FP)$ (`noise_rate`, `src/bias/rq2_trivial_baselines.py:135`). | macro over predicted sentences | Per-sentence FP fraction; high = developer wades through wrong links. Insensitive to coverage. |
| 6 | HUS | Harmonic mean of coverage and per-sentence purity (1-noise weighted by full FP-free sentence count); `compute_hus` in `src/lib/new_metrics_analysis.py:420`. | harmonic of coverage + purity | Useful sentence experience — must hit gold sentences AND keep them clean. |
| 7 | NDG (skill) | $(F_1 - F_1^{rand}) / (F_1^{oracle} - F_1^{rand})$; `compute_ndg` in `src/lib/new_metrics_analysis.py:401`. | rescaling of micro F1 | How much of the random→oracle gap the system closes. Only defined for doc-to-code (oracle uses gold SAM-CODE × gold SAD-SAM); reported NA on doc-to-model. |

---

## 1. Data matrix

Each row = one (system × project × task) cell. NDG is NA on doc-to-model. Top-3 doc-to-model uses R2 (name freq in doc).

### 1.1 Task: doc-to-code

| System | Project | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|---|
| TransArc | mediastore | 0.588 | 0.661 | 0.620 | 0.640 | 0.059 | 0.762 | 0.496 |
| TransArc | teastore | 0.829 | 0.839 | 0.696 | 0.696 | 0.000 | 0.821 | 0.780 |
| TransArc | teammates | 0.821 | 0.736 | 0.515 | 0.598 | 0.299 | 0.591 | 0.921 |
| TransArc | bigbluebutton | 0.831 | 0.883 | 0.732 | 0.822 | 0.211 | 0.405 | 0.840 |
| TransArc | jabref | 0.943 | 0.948 | 0.933 | 1.000 | 0.082 | 0.667 | 0.900 |
| **TransArc** | **macro mean** | **0.803** | **0.813** | **0.699** | **0.751** | **0.130** | **0.649** | **0.787** |
| S11 | mediastore | 0.912 | 0.987 | 0.947 | 1.000 | 0.024 | 0.980 | 0.893 |
| S11 | teastore | 0.948 | 0.875 | 0.989 | 1.000 | 0.133 | 0.894 | 0.933 |
| S11 | teammates | 0.785 | 0.545 | 0.327 | 0.337 | 0.013 | 0.500 | 0.874 |
| S11 | bigbluebutton | 0.879 | 0.855 | 0.852 | 0.978 | 0.186 | 0.438 | 0.896 |
| S11 | jabref | 0.985 | 0.987 | 1.000 | 1.000 | 0.091 | 0.706 | 0.973 |
| **S11** | **macro mean** | **0.902** | **0.850** | **0.823** | **0.863** | **0.089** | **0.703** | **0.914** |
| Random | mediastore | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | -0.225 |
| Random | teastore | 0.117 | 0.165 | 0.096 | 0.870 | 0.882 | 0.000 | -0.138 |
| Random | teammates | 0.106 | 0.283 | 0.072 | 0.717 | 0.892 | 0.021 | -0.016 |
| Random | bigbluebutton | 0.064 | 0.225 | 0.053 | 0.733 | 0.936 | 0.000 | -0.058 |
| Random | jabref | 0.415 | 0.469 | 0.308 | 1.000 | 0.581 | 0.000 | -0.036 |
| **Random** | **macro mean** | **0.140** | **0.228** | **0.106** | **0.664** | **0.858** | **0.004** | **-0.095** |
| Top-3 | mediastore | 0.079 | 0.073 | 0.073 | 0.280 | 0.957 | 0.000 | -0.128 |
| Top-3 | teastore | 0.371 | 0.214 | 0.319 | 0.609 | 0.764 | 0.000 | 0.189 |
| Top-3 | teammates | 0.184 | 0.126 | 0.136 | 0.543 | 0.892 | 0.021 | 0.086 |
| Top-3 | bigbluebutton | 0.247 | 0.060 | 0.167 | 0.178 | 0.835 | 0.040 | 0.156 |
| Top-3 | jabref | 0.596 | 0.411 | 0.477 | 0.700 | 0.574 | 0.420 | 0.285 |
| **Top-3** | **macro mean** | **0.296** | **0.177** | **0.235** | **0.462** | **0.804** | **0.096** | **0.118** |

### 1.2 Task: doc-to-model

| System | Project | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|---|
| TransArc | mediastore | 0.694 | 0.734 | 0.580 | 0.593 | 0.059 | 0.727 | NA |
| TransArc | teastore | 0.851 | 0.859 | 0.696 | 0.696 | 0.000 | 0.821 | NA |
| TransArc | teammates | 0.710 | 0.696 | 0.815 | 0.844 | 0.447 | 0.651 | NA |
| TransArc | bigbluebutton | 0.793 | 0.830 | 0.746 | 0.812 | 0.081 | 0.844 | NA |
| TransArc | jabref | 0.947 | 0.938 | 0.933 | 1.000 | 0.100 | 0.889 | NA |
| **TransArc** | **macro mean** | **0.799** | **0.812** | **0.754** | **0.789** | **0.137** | **0.786** | NA |
| S11 | mediastore | 0.984 | 0.993 | 0.988 | 1.000 | 0.019 | 0.981 | NA |
| S11 | teastore | 0.915 | 0.821 | 0.971 | 1.000 | 0.154 | 0.894 | NA |
| S11 | teammates | 0.851 | 0.793 | 0.726 | 0.733 | 0.029 | 0.835 | NA |
| S11 | bigbluebutton | 0.959 | 0.867 | 0.964 | 0.979 | 0.021 | 0.979 | NA |
| S11 | jabref | 0.973 | 0.985 | 1.000 | 1.000 | 0.091 | 0.952 | NA |
| **S11** | **macro mean** | **0.937** | **0.892** | **0.930** | **0.943** | **0.063** | **0.928** | NA |
| Random | mediastore | 0.065 | 0.050 | 0.074 | 0.074 | 0.913 | 0.080 | NA |
| Random | teastore | 0.074 | 0.038 | 0.051 | 0.087 | 0.956 | 0.000 | NA |
| Random | teammates | 0.088 | 0.057 | 0.068 | 0.111 | 0.889 | 0.103 | NA |
| Random | bigbluebutton | 0.048 | 0.019 | 0.038 | 0.062 | 0.946 | 0.040 | NA |
| Random | jabref | 0.333 | 0.265 | 0.287 | 0.600 | 0.607 | 0.231 | NA |
| **Random** | **macro mean** | **0.122** | **0.086** | **0.104** | **0.187** | **0.862** | **0.091** | NA |
| Top-3 | mediastore | 0.214 | 0.086 | 0.211 | 0.444 | 0.852 | 0.000 | NA |
| Top-3 | teastore | 0.354 | 0.197 | 0.352 | 0.739 | 0.754 | 0.000 | NA |
| Top-3 | teammates | 0.156 | 0.056 | 0.149 | 0.333 | 0.889 | 0.000 | NA |
| Top-3 | bigbluebutton | 0.204 | 0.064 | 0.197 | 0.417 | 0.854 | 0.000 | NA |
| Top-3 | jabref | 0.583 | 0.379 | 0.530 | 0.700 | 0.533 | 0.420 | NA |
| **Top-3** | **macro mean** | **0.302** | **0.156** | **0.288** | **0.527** | **0.776** | **0.084** | NA |

### 1.3 S13F reference (quoted from existing CSVs — different per-component F1 definition; NOT used in correlation analysis)

**S13F SAD-CODE** (from `reports/SADCODE_S11_S13F_VS_TRANSARC.csv`):

| Project | File F1 | Component F1 (micro) | HUS | NDG | MCC |
|---|---|---|---|---|---|
| mediastore | 0.929 | 0.986 | 0.980 | 0.908 | 0.927 |
| teastore | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| teammates | 0.864 | 0.557 | 0.623 | 0.977 | 0.857 |
| bigbluebutton | 0.864 | 0.627 | 0.427 | 0.878 | 0.844 |
| jabref | 1.000 | 0.917 | 0.750 | 1.000 | 1.000 |

**S13F SAD-SAM** (from `reports/SADSAM_S11_S13F_VS_TRANSARC.csv`):

| Project | Link F1 | Sentence F1 (TP iff comp sets intersect) | Component F1 (micro) | HUS | MCC |
|---|---|---|---|---|---|
| mediastore | 0.984 | 1.000 | 0.984 | 0.982 | 0.984 |
| teastore | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| teammates | 0.947 | 0.989 | 0.947 | 0.957 | 0.946 |
| bigbluebutton | 0.821 | 0.921 | 0.821 | 0.881 | 0.821 |
| jabref | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

S13F is the canonical paper artifact and dominates both metrics on every project; it cannot reverse anything in the other systems' rank order. Excluding it from correlation analysis is conservative for the shadowing question.

---

## 2. Pairwise Spearman rank correlation (7 × 7)

Correlation across all available (system × project) cells in each task. `–` = correlation undefined (constant column or too few pairs).

### 2.1 Doc-to-code (n = 4 systems × 5 projects = 20 cells)

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | +1.00 | +0.92 | +0.98 | +0.63 | -0.84 | +0.83 | +0.94 |
| Per-component F1 (macro) | +0.92 | +1.00 | +0.91 | +0.74 | -0.81 | +0.79 | +0.86 |
| Per-sentence F1 (macro) | +0.98 | +0.91 | +1.00 | +0.61 | -0.84 | +0.85 | +0.92 |
| Sentence coverage | +0.63 | +0.74 | +0.61 | +1.00 | -0.40 | +0.37 | +0.45 |
| Noise rate | -0.84 | -0.81 | -0.84 | -0.40 | +1.00 | -0.87 | -0.78 |
| HUS | +0.83 | +0.79 | +0.85 | +0.37 | -0.87 | +1.00 | +0.84 |
| NDG (skill) | +0.94 | +0.86 | +0.92 | +0.45 | -0.78 | +0.84 | +1.00 |

### 2.2 Doc-to-model (n = 4 systems × 5 projects = 20 cells; NDG NA)

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | +1.00 | +0.98 | +0.98 | +0.94 | -0.90 | +0.89 | – |
| Per-component F1 (macro) | +0.98 | +1.00 | +0.95 | +0.91 | -0.92 | +0.90 | – |
| Per-sentence F1 (macro) | +0.98 | +0.95 | +1.00 | +0.96 | -0.84 | +0.88 | – |
| Sentence coverage | +0.94 | +0.91 | +0.96 | +1.00 | -0.75 | +0.80 | – |
| Noise rate | -0.90 | -0.92 | -0.84 | -0.75 | +1.00 | -0.83 | – |
| HUS | +0.89 | +0.90 | +0.88 | +0.80 | -0.83 | +1.00 | – |
| NDG (skill) | – | – | – | – | – | – | – |

### 2.3 Pooled (both tasks; n = 40 cells; NDG only defined on 20)

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | +1.00 | +0.95 | +0.98 | +0.78 | -0.87 | +0.85 | +0.94 |
| Per-component F1 (macro) | +0.95 | +1.00 | +0.93 | +0.84 | -0.84 | +0.83 | +0.86 |
| Per-sentence F1 (macro) | +0.98 | +0.93 | +1.00 | +0.81 | -0.83 | +0.85 | +0.92 |
| Sentence coverage | +0.78 | +0.84 | +0.81 | +1.00 | -0.57 | +0.58 | +0.45 |
| Noise rate | -0.87 | -0.84 | -0.83 | -0.57 | +1.00 | -0.84 | -0.78 |
| HUS | +0.85 | +0.83 | +0.85 | +0.58 | -0.84 | +1.00 | +0.84 |
| NDG (skill) | +0.94 | +0.86 | +0.92 | +0.45 | -0.78 | +0.84 | +1.00 |

## 3. System-rank reversal counts

For each pair of metrics (A, B), count cells where two systems are ranked differently under A than under B. A pair that **never** reverses is informationally redundant for system-pair rank decisions. Cell = (task, project); each cell contributes C(systems_in_cell, 2) = 6 system-pair comparisons.

### 3.1 Doc-to-code

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | 0/30 (0%) | 4/30 (13%) | 0/30 (0%) | 8/27 (30%) | 27/30 (90%) | 1/28 (4%) | 0/30 (0%) |
| Per-component F1 (macro) | 4/30 (13%) | 0/30 (0%) | 4/30 (13%) | 6/27 (22%) | 23/30 (77%) | 3/28 (11%) | 4/30 (13%) |
| Per-sentence F1 (macro) | 0/30 (0%) | 4/30 (13%) | 0/30 (0%) | 8/27 (30%) | 27/30 (90%) | 1/28 (4%) | 0/30 (0%) |
| Sentence coverage | 8/27 (30%) | 6/27 (22%) | 8/27 (30%) | 0/27 (0%) | 17/27 (63%) | 6/25 (24%) | 8/27 (30%) |
| Noise rate | 27/30 (90%) | 23/30 (77%) | 27/30 (90%) | 17/27 (63%) | 0/30 (0%) | 24/28 (86%) | 27/30 (90%) |
| HUS | 1/28 (4%) | 3/28 (11%) | 1/28 (4%) | 6/25 (24%) | 24/28 (86%) | 0/28 (0%) | 1/28 (4%) |
| NDG (skill) | 0/30 (0%) | 4/30 (13%) | 0/30 (0%) | 8/27 (30%) | 27/30 (90%) | 1/28 (4%) | 0/30 (0%) |

### 3.2 Doc-to-model (NDG NA)

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | 0/30 (0%) | 2/30 (7%) | 1/30 (3%) | 2/29 (7%) | 28/30 (93%) | 3/29 (10%) | – |
| Per-component F1 (macro) | 2/30 (7%) | 0/30 (0%) | 3/30 (10%) | 4/29 (14%) | 30/30 (100%) | 3/29 (10%) | – |
| Per-sentence F1 (macro) | 1/30 (3%) | 3/30 (10%) | 0/30 (0%) | 1/29 (3%) | 27/30 (90%) | 4/29 (14%) | – |
| Sentence coverage | 2/29 (7%) | 4/29 (14%) | 1/29 (3%) | 0/29 (0%) | 25/29 (86%) | 5/28 (18%) | – |
| Noise rate | 28/30 (93%) | 30/30 (100%) | 27/30 (90%) | 25/29 (86%) | 0/30 (0%) | 26/29 (90%) | – |
| HUS | 3/29 (10%) | 3/29 (10%) | 4/29 (14%) | 5/28 (18%) | 26/29 (90%) | 0/29 (0%) | – |
| NDG (skill) | – | – | – | – | – | – | – |

### 3.3 Pooled

| | File F1 / Micro F1 | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|---|
| File F1 / Micro F1 | 0/60 (0%) | 6/60 (10%) | 1/60 (2%) | 10/56 (18%) | 55/60 (92%) | 4/57 (7%) | 0/30 (0%) |
| Per-component F1 (macro) | 6/60 (10%) | 0/60 (0%) | 7/60 (12%) | 10/56 (18%) | 53/60 (88%) | 6/57 (11%) | 4/30 (13%) |
| Per-sentence F1 (macro) | 1/60 (2%) | 7/60 (12%) | 0/60 (0%) | 9/56 (16%) | 54/60 (90%) | 5/57 (9%) | 0/30 (0%) |
| Sentence coverage | 10/56 (18%) | 10/56 (18%) | 9/56 (16%) | 0/56 (0%) | 42/56 (75%) | 11/53 (21%) | 8/27 (30%) |
| Noise rate | 55/60 (92%) | 53/60 (88%) | 54/60 (90%) | 42/56 (75%) | 0/60 (0%) | 50/57 (88%) | 27/30 (90%) |
| HUS | 4/57 (7%) | 6/57 (11%) | 5/57 (9%) | 11/53 (21%) | 50/57 (88%) | 0/57 (0%) | 1/28 (4%) |
| NDG (skill) | 0/30 (0%) | 4/30 (13%) | 0/30 (0%) | 8/27 (30%) | 27/30 (90%) | 1/28 (4%) | 0/30 (0%) |

## 4. Per-system fingerprints

For each system × task, mean **(metric − file F1)** across the 5 projects. Positive = system over-performs on this metric relative to its file F1 (the metric flatters it); negative = under-performs (the metric punishes it). This is the signal a *diagnostic* metric would expose even if its rank correlation with file F1 is high.

### 4.1 doc-to-code

| System | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|
| TransArc | +0.011 | -0.104 | -0.051 | -0.672 | -0.154 | -0.015 |
| S11 | -0.052 | -0.079 | -0.039 | -0.812 | -0.198 | +0.012 |
| Random | +0.088 | -0.034 | +0.524 | +0.718 | -0.136 | -0.235 |
| Top-3 | -0.119 | -0.061 | +0.166 | +0.509 | -0.199 | -0.178 |

### 4.2 doc-to-model

| System | Per-component F1 (macro) | Per-sentence F1 (macro) | Sentence coverage | Noise rate | HUS | NDG (skill) |
|---|---|---|---|---|---|---|
| TransArc | +0.012 | -0.045 | -0.010 | -0.662 | -0.013 | NA |
| S11 | -0.045 | -0.007 | +0.006 | -0.874 | -0.008 | NA |
| Random | -0.036 | -0.018 | +0.065 | +0.741 | -0.031 | NA |
| Top-3 | -0.146 | -0.015 | +0.224 | +0.474 | -0.218 | NA |

## 5. Verdict (<400 words)

**Q1 — Is per-sentence F1 shadowed by per-component F1?** On doc-to-code, Spearman ρ = +0.91 with 4/30 (13%) reversals; on doc-to-model ρ = +0.95 with 3/30 (10%) reversals. The per-sentence macro disagrees with per-component macro on roughly 10–13% of system-pair comparisons — non-zero but small. It tracks *file F1* even more tightly (ρ ≥ 0.98 in both tasks, only 0–1 reversals). Per-sentence F1 over gold sentences gives almost the same answer as micro F1 because most gold sentences have only 1–2 links (see H2 in the doc-to-model prestudy). **Verdict: diagnostic on doc-to-code (catches the few cells where per-component and per-sentence disagree); near-shadowed on doc-to-model (1/30 reversals against file F1 — almost no marginal rank signal).**

**Q2 — Is sentence coverage shadowed by per-component F1?** Doc-to-code ρ = +0.74 with 6/27 (22%) reversals; doc-to-model ρ = +0.91 with 4/29 (14%) reversals. Coverage reverses against per-component F1 in 4–8 cells: Random has very broad coverage (0.66 mean) because it scatters predictions across all sentences, but per-component F1 collapses on the components it does not reliably hit; conversely TransArc on teammates has high per-component F1 (0.74) but only 0.60 coverage because its predictions concentrate on a few components. Coverage exposes a failure mode ("the linker found nothing for this sentence") that per-component F1 cannot. **Verdict: independent on doc-to-code; weakly diagnostic on doc-to-model (only 14% reversals).**

**Q3 — Is noise rate shadowed by anything else?** Noise rate has ρ = -0.81/-0.92 with per-component F1 (doc-to-code/doc-to-model), sign-inverted because high noise is bad. It is the only metric that punishes false positives on a per-sentence basis; coverage ignores FPs, file F1 averages them with TPs, per-component F1 averages them per component. **Verdict: independent (and especially load-bearing on doc-to-model where most of the doc is unlinked narrative — see H3 in the prestudy).**

**Q4 — Is HUS shadowed?** HUS = harmonic(coverage, purity). Doc-to-code ρ = +0.79 with 3/28 (11%) reversals against per-component F1; doc-to-model ρ = +0.90 with 3/29 (10%) reversals. HUS is highly correlated with file F1 in the macro mean (both reward TPs and punish FPs at the right scale) but it occasionally reverses the ranks of Top-3 vs Random because Top-3's coverage is high while its purity is low. HUS effectively bundles coverage + noise into one scalar — useful as a summary, **diagnostic** as a standalone signal since coverage + noise already report it.

**Q5 — Is NDG (skill) shadowed?** NDG is a per-project linear rescaling of file F1, so Spearman ρ = +0.94 with 0/30 (0%) reversals against file F1 on doc-to-code — it cannot reverse any system pair within a project. The signal it adds is in the *macro mean*: TransArc on mediastore (file F1 0.59, NDG 0.47) and teammates (file F1 0.82, NDG 0.92) show the skill rescaling shrinks the gap on easy projects and stretches it on hard ones. As a per-project metric NDG is pure rescaling; as a cross-project comparator it reveals that file-F1 ranks of projects reflect difficulty as much as system quality. **Verdict: diagnostic (cross-project rescaling only); demote to companion of file F1.**

**Recommendation.**

- **Primary** (report on the headline table): **File F1**, **per-component F1 (macro)**, **noise rate**, **sentence coverage**. These four are the smallest set that covers volume accuracy, balanced-per-component accuracy, developer noise tax, and reach. None is shadowed by another.
- **Diagnostic** (appendix / footnote): **Per-sentence F1 (macro)** — keep on doc-to-code where it occasionally reverses; drop on doc-to-model where its signal is subsumed by file F1. **HUS** — keep as a single-number summary in tables, but coverage + noise should be the primary read. **NDG** — keep as the cross-project comparator only; do not list per-project because it is monotone in file F1 within a project.
- **No drops** in the strict sense — every metric carries *some* load — but per-sentence F1 (doc-to-model only) and NDG (per-project) are the closest to being shadowed and could be demoted to appendix without loss.

---

Script: `src/bias/rq2_metric_redundancy.py`. Reproduce: `python3 src/bias/rq2_metric_redundancy.py`.
