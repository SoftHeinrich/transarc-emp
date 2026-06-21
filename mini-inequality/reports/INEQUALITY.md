# Trace-Link Data-Inequality — Gold Benchmark Distribution

> Self-contained, stdlib-only, **gold/benchmark only** (no system results). Reproduces the inequality tables of `writing/eval.tex` Chapter 1 and self-checks against their frozen literals.

## Per-sentence gold concentration — Gini 0.331 (MediaStore) → 0.645 (peak)

The per-sentence enrolled sad-code link distribution is heavily right-skewed (eval.tex `tab:sent_gini`).

| project | sent_n | sent_min | sent_median | sent_max | sent_gini | sent_top3_pct |
|---|---|---|---|---|---|---|
| mediastore | 25 | 1 | 2 | 6 | 0.331 | 27.119 |
| teastore | 23 | 5 | 19 | 83 | 0.448 | 35.219 |
| teammates | 92 | 1 | 59.000 | 808 | 0.645 | 20.329 |
| bigbluebutton | 45 | 3 | 16 | 114 | 0.472 | 21.321 |
| jabref | 10 | 8 | 478.500 | 1929 | 0.527 | 69.993 |

## Enrollment expansion — 525 raw decisions → 18,660 enrolled file links (35.5× avg, up to 217.6× on JabRef)

Directory-level gold entries are enrolled to every file beneath them (eval.tex `tab:enrollment`), inflating a few hundred decisions into tens of thousands of file-level points.

| project | raw | dir_entries | dir_pct | enrolled | factor |
|---|---|---|---|---|---|
| mediastore | 57 | 2 | 3.509 | 59 | 1.035 |
| teastore | 70 | 43 | 61.429 | 707 | 10.100 |
| teammates | 228 | 151 | 66.228 | 8097 | 35.513 |
| bigbluebutton | 132 | 116 | 87.879 | 1529 | 11.583 |
| jabref | 38 | 38 | 100.000 | 8268 | 217.579 |

## Structural component→file amplification — files-per-component Gini 0.400 → 0.694; one component decision expands to up to 972 file pairs

The dataset-intrinsic amplification driver is the SAM-CODE files-per-architectural-element fan-out (eval.tex `tab:samcode_skew`): a single component-level decision structurally maps to up to 972 code files (JabRef `logic` = 972, Teammates `ui` = 348). Aggregate amplification equals the enrollment factor. This is a GOLD property — NO system results are used. (eval.tex `tab:amplification`, the TransArc actual-error cascade 36→3,457, is a system-specific quantity and is intentionally excluded from this gold-only study.)

| project | aes | enrolled | min | median | max | gini | top3_conc_pct | mean_fanout |
|---|---|---|---|---|---|---|---|---|
| mediastore | 19 | 60 | 1 | 3 | 16 | 0.400 | 43.333 | 3.158 |
| teastore | 19 | 164 | 1 | 2 | 64 | 0.694 | 68.902 | 8.632 |
| teammates | 14 | 1616 | 17 | 71.000 | 348 | 0.452 | 52.351 | 115.429 |
| bigbluebutton | 22 | 730 | 3 | 16.000 | 94 | 0.513 | 38.356 | 33.182 |
| jabref | 6 | 1956 | 1 | 134.000 | 972 | 0.612 | 98.620 | 326.000 |

**Structural amplification potential (gold):**

| project | n_components | mean_fanout | max_fanout | enrollment_factor |
|---|---|---|---|---|
| mediastore | 19 | 3.158 | 16 | 1.035 |
| teastore | 19 | 8.632 | 64 | 10.100 |
| teammates | 14 | 115.429 | 348 | 35.513 |
| bigbluebutton | 22 | 33.182 | 94 | 11.583 |
| jabref | 6 | 326.000 | 972 | 217.579 |

## Per-component & per-sentence concentration (supplementary skew)

Per-component #sentences inequality, sad-sam side (eval.tex `gold_gini` analogue):

| project | n_components | sent_min | sent_median | sent_max | comp_sent_gini | top1_pct | top3_pct |
|---|---|---|---|---|---|---|---|
| mediastore | 10 | 1 | 3.000 | 7 | 0.306 | 22.581 | 51.613 |
| teastore | 6 | 2 | 5.000 | 6 | 0.179 | 22.222 | 62.963 |
| teammates | 8 | 4 | 5.000 | 15 | 0.261 | 26.316 | 59.649 |
| bigbluebutton | 11 | 2 | 4 | 14 | 0.370 | 22.581 | 54.839 |
| jabref | 5 | 2 | 4 | 6 | 0.222 | 33.333 | 77.778 |

## Sanity check

Status: **PASS ✓** — every reproduced number agrees with the frozen `writing/eval.tex` literals (tolerance: Gini ≤ 0.005, integer counts exact). No system results were read; the engine is stdlib-only and self-contained.

