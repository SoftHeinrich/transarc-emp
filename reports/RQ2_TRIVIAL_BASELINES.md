# RQ2: Trivial Baselines Under File-Level F1 vs Bias-Corrected Metrics

Two trivial baselines computed on SAM-CODE-enrolled SAD-CODE gold for
the 5 ARDoCo benchmark projects:

- **Random**: `random.seed(42)`, samples `(sentence, file)` pairs at gold link density
  (total predictions ~= |gold|), reusing `baseline_random_same_size` from
  `src/bias/stupid_baseline_analysis.py`.
- **Top-3**: every sentence linked to the files of the 3 components with the most
  enrolled gold files in the project, reusing `baseline_majority_k(..., k=3)` from
  the same module.

Each baseline is scored on 7 metrics per project: file-level micro F1,
per-component F1 (macro), per-sentence F1 (macro), sentence coverage,
noise rate, HUS (`src/lib/new_metrics_analysis.py`), and NDG skill score
`(system_F1 - random_F1) / (oracle_F1 - random_F1)`.

## Random

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| File-level F1 (micro) | 0.017 | 0.154 | 0.106 | 0.067 | 0.407 | **0.150** |
| Per-component F1 (macro) | 0.023 | 0.127 | 0.280 | 0.263 | 0.468 | **0.232** |
| Per-sentence F1 (macro) | 0.013 | 0.133 | 0.071 | 0.058 | 0.299 | **0.115** |
| Sentence coverage | 0.040 | 0.870 | 0.717 | 0.822 | 1.000 | **0.690** |
| Noise rate | 0.978 | 0.844 | 0.895 | 0.934 | 0.593 | **0.849** |
| HUS | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **0.000** |
| NDG (skill score) | -0.260 | -0.089 | -0.017 | -0.045 | -0.050 | **-0.092** |

## Top-3

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| File-level F1 (micro) | 0.079 | 0.371 | 0.184 | 0.247 | 0.596 | **0.296** |
| Per-component F1 (macro) | 0.073 | 0.214 | 0.126 | 0.060 | 0.411 | **0.177** |
| Per-sentence F1 (macro) | 0.073 | 0.319 | 0.136 | 0.167 | 0.477 | **0.235** |
| Sentence coverage | 0.280 | 0.609 | 0.543 | 0.178 | 0.700 | **0.462** |
| Noise rate | 0.957 | 0.764 | 0.892 | 0.835 | 0.574 | **0.804** |
| HUS | 0.000 | 0.000 | 0.021 | 0.040 | 0.420 | **0.096** |
| NDG (skill score) | -0.180 | 0.191 | 0.086 | 0.164 | 0.285 | **0.109** |

## Head-to-head per metric (Random vs Top-3 vs SOTA reference)

SOTA reference = TransArc / s11 / s13f file-level F1 from
`reports/SADCODE_S11_S13F_VS_TRANSARC.csv` (the best of TransArc, S11, S13F per project).

| Project | Random file_F1 | Top-3 file_F1 | TransArc file_F1 | S11 file_F1 | S13F file_F1 |
|---|---|---|---|---|---|
| mediastore | 0.017 | 0.079 | 0.588 | 0.912 | 0.929 |
| teastore | 0.154 | 0.371 | 0.830 | 0.948 | 1.000 |
| teammates | 0.106 | 0.184 | 0.821 | 0.785 | 0.864 |
| bigbluebutton | 0.067 | 0.247 | 0.831 | 0.879 | 0.864 |
| jabref | 0.407 | 0.596 | 0.943 | 0.985 | 1.000 |
| **macro mean** | **0.150** | **0.296** | **0.803** | **0.902** | **0.931** |

## NDG anchors per project

| Project | random_f1 (analytic prior) | oracle_f1 (perfect transitive) | |gold| | |random pred| | |top-3 pred| |
|---|---|---|---|---|---|
| mediastore | 0.2197 | 1.0000 | 59 | 59 | 650 |
| teastore | 0.2235 | 1.0000 | 707 | 707 | 2,599 |
| teammates | 0.1186 | 0.8814 | 8,097 | 8,097 | 45,816 |
| bigbluebutton | 0.1053 | 0.9676 | 1,529 | 1,529 | 4,590 |
| jabref | 0.4350 | 1.0000 | 8,268 | 8,268 | 19,290 |

---

Script: `src/bias/rq2_trivial_baselines.py`. Reproduce: `python3 src/bias/rq2_trivial_baselines.py`.
