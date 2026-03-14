# Four-System Comparison: TransArc vs V45 vs LLM vs V87

Unified evaluation of 4 systems across 6 new metrics (N1-N6)
at both SAD-SAM and SAD-CODE levels, plus enrollment debiasing metrics.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM x SAM-CODE)
- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through gold SAM-CODE
- **LLM Adaptive**: Zero-training LLM classifier (best strategy per project),
  projected through gold SAM-CODE
- **V87**: Few-shot meta-learning linker (10% gold SAD-SAM as training),
  projected through TransArc SAM-CODE (not gold)

**Important caveats for V87:**
1. V87 uses **10% of gold SAD-SAM links as few-shot training** — not zero-shot
2. V87 SAD-SAM metrics are **holdout-only** (90% test split) — not full-gold
3. V87 SAD-CODE projection uses **TransArc SAM-CODE** (may have errors),
   while V45 and LLM use **gold SAM-CODE** (oracle)
4. V87 only has **aggregate P/R/F1** — N2, N3, N4, N6, debiasing are N/A

| Project | LLM Strategy | V87 Strategy |
|:--|:--|:--|
| mediastore | majority | per_component |
| teastore | intersection | per_component |
| teammates | intersection | link_level |
| bigbluebutton | majority | per_sentence |
| jabref | single | per_sentence |

---

## Mediastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| SAD-SAM | V45 | 0.963 | 0.839 | 0.897 | 26 | 1 | 5 |
| SAD-SAM | LLM | 1.000 | 0.871 | 0.931 | 27 | 0 | 4 |
| SAD-SAM | V87 * | 0.957 | 0.917 | 0.936 | — | — | — |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V45 | 0.979 | 0.780 | 0.868 | 46 | 1 | 13 |
| SAD-CODE | LLM | 1.000 | 0.932 | 0.965 | 55 | 0 | 4 |
| SAD-CODE | V87 | 0.981 | 0.881 | 0.929 | 52 | 1 | 7 |

\* V87 SAD-SAM: holdout-only (10% train split), not full-gold

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.711** | 0.773 | 17 | 1 | 14 | 671 |
| SAD-SAM | V45 | **0.894** | 0.919 | 26 | 1 | 5 | 671 |
| SAD-SAM | LLM | **0.930** | 0.935 | 27 | 0 | 4 | 672 |
| SAD-SAM | V87 | N/A | N/A | — | — | — | — |
| SAD-CODE | TransArc | **0.633** | 0.712 | 25 | 1 | 34 | 2086 |
| SAD-CODE | V45 | **0.871** | 0.890 | 46 | 1 | 13 | 2086 |
| SAD-CODE | LLM | **0.965** | 0.966 | 55 | 0 | 4 | 2087 |
| SAD-CODE | V87 | **0.928** | — | 52 | 1 | 7 | 2086 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.556** | 0.574 | 0.556 | 0.593 | 0.407 |
| SAD-SAM | V45 | **0.815** | 0.852 | 0.815 | 0.889 | 0.111 |
| SAD-SAM | LLM | **0.889** | 0.889 | 0.889 | 0.889 | 0.111 |
| SAD-CODE | TransArc | **0.600** | 0.613 | 0.600 | 0.640 | 0.360 |
| SAD-CODE | V45 | **0.800** | 0.827 | 0.800 | 0.840 | 0.160 |
| SAD-CODE | LLM | **0.960** | 0.960 | 0.960 | 0.960 | 0.040 |
| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |
| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |

### N3: MAP

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | **0.574** |
| SAD-SAM | V45 | **0.852** |
| SAD-SAM | LLM | **0.889** |
| SAD-CODE | TransArc | **0.613** |
| SAD-CODE | V45 | **0.827** |
| SAD-CODE | LLM | **0.960** |
| both | V87 | N/A |

### N4: ACF1

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.588 | **0.739** | +0.151 |
| V45 | 0.868 | **0.885** | +0.017 |
| LLM | 0.965 | **0.982** | +0.017 |
| V87 | 0.929 | N/A | N/A |

### N5: NDG

Random F1: 0.148 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | **0.516** |
| V45 | 0.868 | **0.845** |
| LLM | 0.965 | **0.959** |
| V87 | 0.929 | **0.916** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.593 | 0.941 | **0.727** |
| SAD-SAM | V45 | 0.889 | 0.960 | **0.923** |
| SAD-SAM | LLM | 0.889 | 1.000 | **0.941** |
| SAD-CODE | TransArc | 0.640 | 0.941 | **0.762** |
| SAD-CODE | V45 | 0.840 | 0.955 | **0.894** |
| SAD-CODE | LLM | 0.960 | 1.000 | **0.980** |
| both | V87 | N/A | N/A | N/A |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM | V87 |
|:--|:---:|:---:|:---:|:---:|
| Standard F1 | 0.588 | 0.868 | 0.965 | 0.929 |
| IDF-Weighted F1 | 0.657 | 0.879 | 0.972 | N/A |
| Component-Macro F1 | 0.661 | 0.894 | 0.985 | N/A |
| PDR F1 | 0.641 | 0.872 | 0.970 | N/A |
| ACF1 | 0.739 | 0.885 | 0.982 | N/A |

---

## Teastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V45 | 0.964 | 1.000 | 0.982 | 27 | 1 | 0 |
| SAD-SAM | LLM | 0.676 | 0.926 | 0.781 | 25 | 12 | 2 |
| SAD-SAM | V87 * | 0.769 | 0.952 | 0.851 | — | — | — |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V45 | 0.981 | 1.000 | 0.990 | 707 | 14 | 0 |
| SAD-CODE | LLM | 0.632 | 0.966 | 0.764 | 683 | 397 | 24 |
| SAD-CODE | V87 | 0.895 | 0.973 | 0.932 | 688 | 81 | 19 |

\* V87 SAD-SAM: holdout-only (10% train split), not full-gold

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.857** | 0.870 | 20 | 0 | 7 | 790 |
| SAD-SAM | V45 | **0.981** | 0.999 | 27 | 1 | 0 | 789 |
| SAD-SAM | LLM | **0.783** | 0.955 | 25 | 12 | 2 | 778 |
| SAD-SAM | V87 | N/A | N/A | — | — | — | — |
| SAD-CODE | TransArc | **0.828** | 0.854 | 501 | 0 | 206 | 6001 |
| SAD-CODE | V45 | **0.989** | 0.999 | 707 | 14 | 0 | 5987 |
| SAD-CODE | LLM | **0.752** | 0.950 | 683 | 397 | 24 | 5604 |
| SAD-CODE | V87 | **0.925** | — | 688 | 81 | 19 | 5920 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.696** | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-SAM | V45 | **1.000** | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-SAM | LLM | **0.913** | 0.913 | 0.913 | 0.913 | 0.087 |
| SAD-CODE | TransArc | **0.696** | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-CODE | V45 | **1.000** | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-CODE | LLM | **0.913** | 0.913 | 0.913 | 0.913 | 0.087 |
| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |
| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |

### N3: MAP

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | **0.696** |
| SAD-SAM | V45 | **1.000** |
| SAD-SAM | LLM | **0.913** |
| SAD-CODE | TransArc | **0.696** |
| SAD-CODE | V45 | **1.000** |
| SAD-CODE | LLM | **0.913** |
| both | V87 | N/A |

### N4: ACF1

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.829 | **0.851** | +0.022 |
| V45 | 0.990 | **0.982** | -0.008 |
| LLM | 0.764 | **0.781** | +0.017 |
| V87 | 0.932 | N/A | N/A |

### N5: NDG

Random F1: 0.120 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | **0.806** |
| V45 | 0.990 | **0.989** |
| LLM | 0.764 | **0.732** |
| V87 | 0.932 | **0.923** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-SAM | V45 | 1.000 | 0.958 | **0.979** |
| SAD-SAM | LLM | 0.913 | 0.636 | **0.750** |
| SAD-CODE | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-CODE | V45 | 1.000 | 0.958 | **0.979** |
| SAD-CODE | LLM | 0.913 | 0.636 | **0.750** |
| both | V87 | N/A | N/A | N/A |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM | V87 |
|:--|:---:|:---:|:---:|:---:|
| Standard F1 | 0.829 | 0.990 | 0.764 | 0.932 |
| IDF-Weighted F1 | 0.836 | 0.988 | 0.754 | N/A |
| Component-Macro F1 | 0.839 | 0.967 | 0.783 | N/A |
| PDR F1 | 0.830 | 0.990 | 0.764 | N/A |
| ACF1 | 0.851 | 0.982 | 0.781 | N/A |

---

## Teammates

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V45 | 0.820 | 0.877 | 0.847 | 50 | 11 | 7 |
| SAD-SAM | LLM | 0.625 | 0.789 | 0.698 | 45 | 27 | 12 |
| SAD-SAM | V87 * | 0.860 | 0.843 | 0.851 | — | — | — |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V45 | 0.803 | 0.770 | 0.786 | 6235 | 1525 | 1862 |
| SAD-CODE | LLM | 0.656 | 0.766 | 0.707 | 6205 | 3257 | 1892 |
| SAD-CODE | V87 | 0.935 | 0.747 | 0.830 | 6046 | 422 | 2051 |

\* V87 SAD-SAM: holdout-only (10% train split), not full-gold

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.714** | 0.924 | 49 | 32 | 8 | 2683 |
| SAD-SAM | V45 | **0.845** | 0.937 | 50 | 11 | 7 | 2704 |
| SAD-SAM | LLM | **0.696** | 0.890 | 45 | 27 | 12 | 2688 |
| SAD-SAM | V87 | N/A | N/A | — | — | — | — |
| SAD-CODE | TransArc | **0.814** | 0.943 | 7307 | 2395 | 790 | 149492 |
| SAD-CODE | V45 | **0.775** | 0.880 | 6235 | 1525 | 1862 | 150362 |
| SAD-CODE | LLM | **0.692** | 0.872 | 6205 | 3257 | 1892 | 148630 |
| SAD-CODE | V87 | **0.828** | — | 6046 | 422 | 2051 | 151465 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.756** | 0.800 | 0.822 | 0.778 | 0.133 |
| SAD-SAM | V45 | **0.778** | 0.822 | 0.844 | 0.800 | 0.133 |
| SAD-SAM | LLM | **0.622** | 0.730 | 0.733 | 0.711 | 0.156 |
| SAD-CODE | TransArc | **0.370** | 0.493 | 0.554 | 0.413 | 0.391 |
| SAD-CODE | V45 | **0.337** | 0.404 | 0.359 | 0.391 | 0.576 |
| SAD-CODE | LLM | **0.283** | 0.406 | 0.391 | 0.359 | 0.500 |
| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |
| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |

### N3: MAP

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | **0.800** |
| SAD-SAM | V45 | **0.833** |
| SAD-SAM | LLM | **0.750** |
| SAD-CODE | TransArc | **0.514** |
| SAD-CODE | V45 | **0.402** |
| SAD-CODE | LLM | **0.406** |
| both | V87 | N/A |

### N4: ACF1

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.821 | **0.624** | -0.197 |
| V45 | 0.786 | **0.593** | -0.193 |
| LLM | 0.707 | **0.535** | -0.171 |
| V87 | 0.830 | N/A | N/A |

### N5: NDG

Random F1: 0.055 | Oracle F1: 0.881

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | **0.927** |
| V45 | 0.786 | **0.885** |
| LLM | 0.707 | **0.789** |
| V87 | 0.830 | **0.938** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.844 | 0.530 | **0.651** |
| SAD-SAM | V45 | 0.867 | 0.766 | **0.813** |
| SAD-SAM | LLM | 0.844 | 0.552 | **0.667** |
| SAD-CODE | TransArc | 0.598 | 0.585 | **0.591** |
| SAD-CODE | V45 | 0.424 | 0.766 | **0.546** |
| SAD-CODE | LLM | 0.467 | 0.569 | **0.513** |
| both | V87 | N/A | N/A | N/A |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM | V87 |
|:--|:---:|:---:|:---:|:---:|
| Standard F1 | 0.821 | 0.786 | 0.707 | 0.830 |
| IDF-Weighted F1 | 0.817 | 0.784 | 0.706 | N/A |
| Component-Macro F1 | 0.723 | 0.717 | 0.643 | N/A |
| PDR F1 | 0.819 | 0.784 | 0.705 | N/A |
| ACF1 | 0.624 | 0.593 | 0.535 | N/A |

---

## Bigbluebutton

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V45 | 0.852 | 0.839 | 0.846 | 52 | 9 | 10 |
| SAD-SAM | LLM | 0.642 | 0.548 | 0.591 | 34 | 19 | 28 |
| SAD-SAM | V87 * | 0.786 | 0.880 | 0.830 | — | — | — |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V45 | 0.817 | 0.947 | 0.877 | 1448 | 325 | 81 |
| SAD-CODE | LLM | 0.656 | 0.772 | 0.710 | 1181 | 618 | 348 |
| SAD-CODE | V87 | 0.734 | 0.927 | 0.820 | 1418 | 513 | 111 |

\* V87 SAD-SAM: holdout-only (10% train split), not full-gold

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.792** | 0.853 | 44 | 5 | 18 | 1847 |
| SAD-SAM | V45 | **0.840** | 0.917 | 52 | 9 | 10 | 1843 |
| SAD-SAM | LLM | **0.581** | 0.769 | 34 | 19 | 28 | 1833 |
| SAD-SAM | V87 | N/A | N/A | — | — | — | — |
| SAD-CODE | TransArc | **0.820** | 0.915 | 1287 | 282 | 242 | 22723 |
| SAD-CODE | V45 | **0.871** | 0.966 | 1448 | 325 | 81 | 22680 |
| SAD-CODE | LLM | **0.691** | 0.873 | 1181 | 618 | 348 | 22387 |
| SAD-CODE | V87 | **0.813** | — | 1418 | 513 | 111 | 22492 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.604** | 0.712 | 0.646 | 0.750 | 0.188 |
| SAD-SAM | V45 | **0.708** | 0.832 | 0.792 | 0.854 | 0.062 |
| SAD-SAM | LLM | **0.479** | 0.569 | 0.542 | 0.562 | 0.250 |
| SAD-CODE | TransArc | **0.156** | 0.675 | 0.667 | 0.244 | 0.178 |
| SAD-CODE | V45 | **0.867** | 0.910 | 0.911 | 0.889 | 0.067 |
| SAD-CODE | LLM | **0.600** | 0.644 | 0.644 | 0.622 | 0.222 |
| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |
| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |

### N3: MAP

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | **0.709** |
| SAD-SAM | V45 | **0.866** |
| SAD-SAM | LLM | **0.591** |
| SAD-CODE | TransArc | **0.725** |
| SAD-CODE | V45 | **0.974** |
| SAD-CODE | LLM | **0.651** |
| both | V87 | N/A |

### N4: ACF1

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.831 | **0.347** | -0.484 |
| V45 | 0.877 | **0.886** | +0.009 |
| LLM | 0.710 | **0.673** | -0.037 |
| V87 | 0.820 | N/A | N/A |

### N5: NDG

Random F1: 0.059 | Oracle F1: 0.968

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | **0.850** |
| V45 | 0.877 | **0.900** |
| LLM | 0.710 | **0.716** |
| V87 | 0.820 | **0.837** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.812 | 0.878 | **0.844** |
| SAD-SAM | V45 | 0.938 | 0.820 | **0.875** |
| SAD-SAM | LLM | 0.667 | 0.600 | **0.632** |
| SAD-CODE | TransArc | 0.822 | 0.268 | **0.405** |
| SAD-CODE | V45 | 0.933 | 0.816 | **0.871** |
| SAD-CODE | LLM | 0.711 | 0.622 | **0.664** |
| both | V87 | N/A | N/A | N/A |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM | V87 |
|:--|:---:|:---:|:---:|:---:|
| Standard F1 | 0.831 | 0.877 | 0.710 | 0.820 |
| IDF-Weighted F1 | 0.860 | 0.876 | 0.665 | N/A |
| Component-Macro F1 | 0.863 | 0.901 | 0.700 | N/A |
| PDR F1 | 0.757 | 0.874 | 0.660 | N/A |
| ACF1 | 0.347 | 0.886 | 0.673 | N/A |

---

## Jabref

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V45 | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | LLM | 0.947 | 1.000 | 0.973 | 18 | 1 | 0 |
| SAD-SAM | V87 * | 0.882 | 1.000 | 0.938 | — | — | — |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V45 | 0.893 | 1.000 | 0.944 | 8268 | 990 | 0 |
| SAD-CODE | LLM | 0.998 | 1.000 | 0.999 | 8268 | 18 | 0 |
| SAD-CODE | V87 | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |

\* V87 SAD-SAM: holdout-only (10% train split), not full-gold

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.933** | 0.983 | 18 | 2 | 0 | 58 |
| SAD-SAM | V45 | **0.933** | 0.983 | 18 | 2 | 0 | 58 |
| SAD-SAM | LLM | **0.965** | 0.992 | 18 | 1 | 0 | 59 |
| SAD-SAM | V87 | N/A | N/A | — | — | — | — |
| SAD-CODE | TransArc | **0.917** | 0.971 | 8268 | 994 | 0 | 16166 |
| SAD-CODE | V45 | **0.917** | 0.971 | 8268 | 990 | 0 | 16170 |
| SAD-CODE | LLM | **0.998** | 0.999 | 8268 | 18 | 0 | 17142 |
| SAD-CODE | V87 | **0.917** | — | 8268 | 994 | 0 | 16166 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.800** | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | V45 | **0.800** | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | LLM | **0.900** | 0.950 | 1.000 | 0.900 | 0.000 |
| SAD-CODE | TransArc | **0.500** | 0.918 | 1.000 | 0.500 | 0.000 |
| SAD-CODE | V45 | **0.800** | 0.918 | 1.000 | 0.800 | 0.000 |
| SAD-CODE | LLM | **0.900** | 0.998 | 1.000 | 0.900 | 0.000 |
| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |
| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |

### N3: MAP

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | **0.950** |
| SAD-SAM | V45 | **0.950** |
| SAD-SAM | LLM | **0.950** |
| SAD-CODE | TransArc | **0.935** |
| SAD-CODE | V45 | **0.933** |
| SAD-CODE | LLM | **0.994** |
| both | V87 | N/A |

### N4: ACF1

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.943 | **0.857** | -0.086 |
| V45 | 0.944 | **0.947** | +0.004 |
| LLM | 0.999 | **0.973** | -0.026 |
| V87 | 0.943 | N/A | N/A |

### N5: NDG

Random F1: 0.335 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | **0.915** |
| V45 | 0.944 | **0.915** |
| LLM | 0.999 | **0.998** |
| V87 | 0.943 | **0.915** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 0.800 | **0.889** |
| SAD-SAM | V45 | 1.000 | 0.800 | **0.889** |
| SAD-SAM | LLM | 1.000 | 0.900 | **0.947** |
| SAD-CODE | TransArc | 1.000 | 0.500 | **0.667** |
| SAD-CODE | V45 | 1.000 | 0.800 | **0.889** |
| SAD-CODE | LLM | 1.000 | 0.900 | **0.947** |
| both | V87 | N/A | N/A | N/A |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM | V87 |
|:--|:---:|:---:|:---:|:---:|
| Standard F1 | 0.943 | 0.944 | 0.999 | 0.943 |
| IDF-Weighted F1 | 0.941 | 0.941 | 0.998 | N/A |
| Component-Macro F1 | 0.948 | 0.948 | 0.967 | N/A |
| PDR F1 | 0.943 | 0.943 | 0.999 | N/A |
| ACF1 | 0.857 | 0.947 | 0.973 | N/A |

---

## Aggregate Comparison

### Standard F1

| Project | Level | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.694 | 0.897 | 0.931 | 0.936* | V87 |
| | CODE | 0.588 | 0.868 | 0.965 | 0.929 | LLM |
| teastore | SAM | 0.851 | 0.982 | 0.781 | 0.851* | V45 |
| | CODE | 0.829 | 0.990 | 0.764 | 0.932 | V45 |
| teammates | SAM | 0.710 | 0.847 | 0.698 | 0.851* | V87 |
| | CODE | 0.821 | 0.786 | 0.707 | 0.830 | V87 |
| bigbluebutton | SAM | 0.793 | 0.846 | 0.591 | 0.830* | V45 |
| | CODE | 0.831 | 0.877 | 0.710 | 0.820 | V45 |
| jabref | SAM | 0.947 | 0.947 | 0.973 | 0.938* | LLM |
| | CODE | 0.943 | 0.944 | 0.999 | 0.943 | LLM |
| **Average** | SAM | **0.799** | **0.904** | **0.795** | **0.881*** | |
| | CODE | **0.803** | **0.893** | **0.829** | **0.891** | |

\* holdout-only (not full-gold)

### N1: MCC

| Project | Level | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.711 | 0.894 | 0.930 | N/A | LLM |
| | CODE | 0.633 | 0.871 | 0.965 | 0.928 | LLM |
| teastore | SAM | 0.857 | 0.981 | 0.783 | N/A | V45 |
| | CODE | 0.828 | 0.989 | 0.752 | 0.925 | V45 |
| teammates | SAM | 0.714 | 0.845 | 0.696 | N/A | V45 |
| | CODE | 0.814 | 0.775 | 0.692 | 0.828 | V87 |
| bigbluebutton | SAM | 0.792 | 0.840 | 0.581 | N/A | V45 |
| | CODE | 0.820 | 0.871 | 0.691 | 0.813 | V45 |
| jabref | SAM | 0.933 | 0.933 | 0.965 | N/A | LLM |
| | CODE | 0.917 | 0.917 | 0.998 | 0.917 | LLM |
| **Average** | SAM | **0.801** | **0.899** | **0.791** | N/A | |
| | CODE | **0.802** | **0.885** | **0.820** | **0.882** | |

### N2: EMR

| Project | Level | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.556 | 0.815 | 0.889 | N/A | LLM |
| | CODE | 0.600 | 0.800 | 0.960 | N/A | LLM |
| teastore | SAM | 0.696 | 1.000 | 0.913 | N/A | V45 |
| | CODE | 0.696 | 1.000 | 0.913 | N/A | V45 |
| teammates | SAM | 0.756 | 0.778 | 0.622 | N/A | V45 |
| | CODE | 0.370 | 0.337 | 0.283 | N/A | TransArc |
| bigbluebutton | SAM | 0.604 | 0.708 | 0.479 | N/A | V45 |
| | CODE | 0.156 | 0.867 | 0.600 | N/A | V45 |
| jabref | SAM | 0.800 | 0.800 | 0.900 | N/A | LLM |
| | CODE | 0.500 | 0.800 | 0.900 | N/A | LLM |
| **Average** | SAM | **0.682** | **0.820** | **0.761** | N/A | |
| | CODE | **0.464** | **0.761** | **0.731** | N/A | |

### N3: MAP

| Project | Level | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.574 | 0.852 | 0.889 | N/A | LLM |
| | CODE | 0.613 | 0.827 | 0.960 | N/A | LLM |
| teastore | SAM | 0.696 | 1.000 | 0.913 | N/A | V45 |
| | CODE | 0.696 | 1.000 | 0.913 | N/A | V45 |
| teammates | SAM | 0.800 | 0.833 | 0.750 | N/A | V45 |
| | CODE | 0.514 | 0.402 | 0.406 | N/A | TransArc |
| bigbluebutton | SAM | 0.709 | 0.866 | 0.591 | N/A | V45 |
| | CODE | 0.725 | 0.974 | 0.651 | N/A | V45 |
| jabref | SAM | 0.950 | 0.950 | 0.950 | N/A | TransArc |
| | CODE | 0.935 | 0.933 | 0.994 | N/A | LLM |
| **Average** | SAM | **0.746** | **0.900** | **0.819** | N/A | |
| | CODE | **0.697** | **0.827** | **0.785** | N/A | |

### N4: ACF1

| Project | TransArc | V45 | LLM | V87 | Best |
|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | 0.739 | 0.885 | 0.982 | N/A | LLM |
| teastore | 0.851 | 0.982 | 0.781 | N/A | V45 |
| teammates | 0.624 | 0.593 | 0.535 | N/A | TransArc |
| bigbluebutton | 0.347 | 0.886 | 0.673 | N/A | V45 |
| jabref | 0.857 | 0.947 | 0.973 | N/A | LLM |
| **Average** | **0.684** | **0.859** | **0.789** | N/A | |

### N5: NDG

| Project | Random | Oracle | TransArc | V45 | LLM | V87 | Best |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|:--|
| mediastore | 0.148 | 1.000 | 0.516 | 0.845 | 0.959 | 0.916 | LLM |
| teastore | 0.120 | 1.000 | 0.806 | 0.989 | 0.732 | 0.923 | V45 |
| teammates | 0.055 | 0.881 | 0.927 | 0.885 | 0.789 | 0.938 | V87 |
| bigbluebutton | 0.059 | 0.968 | 0.850 | 0.900 | 0.716 | 0.837 | V45 |
| jabref | 0.335 | 1.000 | 0.915 | 0.915 | 0.998 | 0.915 | LLM |
| **Average** | | | **0.803** | **0.907** | **0.839** | **0.906** | |

### N6: HUS

| Project | Level | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.727 | 0.923 | 0.941 | N/A | LLM |
| | CODE | 0.762 | 0.894 | 0.980 | N/A | LLM |
| teastore | SAM | 0.821 | 0.979 | 0.750 | N/A | V45 |
| | CODE | 0.821 | 0.979 | 0.750 | N/A | V45 |
| teammates | SAM | 0.651 | 0.813 | 0.667 | N/A | V45 |
| | CODE | 0.591 | 0.546 | 0.513 | N/A | TransArc |
| bigbluebutton | SAM | 0.844 | 0.875 | 0.632 | N/A | V45 |
| | CODE | 0.405 | 0.871 | 0.664 | N/A | V45 |
| jabref | SAM | 0.889 | 0.889 | 0.947 | N/A | LLM |
| | CODE | 0.667 | 0.889 | 0.947 | N/A | LLM |
| **Average** | SAM | **0.786** | **0.896** | **0.788** | N/A | |
| | CODE | **0.649** | **0.836** | **0.771** | N/A | |

---

## Grand Summary

| Metric | Level | TransArc | V45 | LLM | V87 | Best (all) |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| F1 (standard) | SAM | 0.799 | 0.904 | 0.795 | 0.881* | V45 |
| F1 (standard) | CODE | 0.803 | 0.893 | 0.829 | 0.891 | V45 |
| **N1: MCC** | SAM | 0.801 | 0.899 | 0.791 | N/A | V45 |
| **N1: MCC** | CODE | 0.802 | 0.885 | 0.820 | 0.882 | V45 |
| **N2: EMR** | SAM | 0.682 | 0.820 | 0.761 | N/A | V45 |
| **N2: EMR** | CODE | 0.464 | 0.761 | 0.731 | N/A | V45 |
| **N3: MAP** | SAM | 0.746 | 0.900 | 0.819 | N/A | V45 |
| **N3: MAP** | CODE | 0.697 | 0.827 | 0.785 | N/A | V45 |
| **N4: ACF1** | CODE | 0.684 | 0.859 | 0.789 | N/A | V45 |
| **N5: NDG** | CODE | 0.803 | 0.907 | 0.839 | 0.906 | V45 |
| **N6: HUS** | SAM | 0.786 | 0.896 | 0.788 | N/A | V45 |
| **N6: HUS** | CODE | 0.649 | 0.836 | 0.771 | N/A | V45 |
| IDF-Weighted F1 | CODE | 0.822 | 0.893 | 0.819 | N/A | V45 |
| Component-Macro F1 | CODE | 0.807 | 0.885 | 0.815 | N/A | V45 |
| PDR F1 | CODE | 0.798 | 0.893 | 0.820 | N/A | V45 |

\* holdout-only, not directly comparable

### V87 Head-to-Head (computable metrics only)

Metrics where V87 has data for fair comparison:

| Metric | TransArc | V45 | LLM | V87 | Best |
|:--|:---:|:---:|:---:|:---:|:--|
| F1 SAD-CODE | 0.803 | 0.893 | 0.829 | 0.891 | V45 |
| N1: MCC CODE | 0.802 | 0.885 | 0.820 | 0.882 | V45 |
| N5: NDG | 0.803 | 0.907 | 0.839 | 0.906 | V45 |

**Per-project for computable metrics:**

| Project | Metric | TransArc | V45 | LLM | V87 | Best |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | F1 CODE | 0.588 | 0.868 | 0.965 | 0.929 | LLM |
| | MCC CODE | 0.633 | 0.871 | 0.965 | 0.928 | LLM |
| | NDG | 0.516 | 0.845 | 0.959 | 0.916 | LLM |
| teastore | F1 CODE | 0.829 | 0.990 | 0.764 | 0.932 | V45 |
| | MCC CODE | 0.828 | 0.989 | 0.752 | 0.925 | V45 |
| | NDG | 0.806 | 0.989 | 0.732 | 0.923 | V45 |
| teammates | F1 CODE | 0.821 | 0.786 | 0.707 | 0.830 | V87 |
| | MCC CODE | 0.814 | 0.775 | 0.692 | 0.828 | V87 |
| | NDG | 0.927 | 0.885 | 0.789 | 0.938 | V87 |
| bigbluebutton | F1 CODE | 0.831 | 0.877 | 0.710 | 0.820 | V45 |
| | MCC CODE | 0.820 | 0.871 | 0.691 | 0.813 | V45 |
| | NDG | 0.850 | 0.900 | 0.716 | 0.837 | V45 |
| jabref | F1 CODE | 0.943 | 0.944 | 0.999 | 0.943 | LLM |
| | MCC CODE | 0.917 | 0.917 | 0.998 | 0.917 | LLM |
| | NDG | 0.915 | 0.915 | 0.998 | 0.915 | LLM |

### Key Findings

1. **V87 wins 3/15 computable metric-project combinations**
   (F1-CODE + MCC-CODE + NDG across 5 projects)

2. **V87 vs TransArc**: V87 wins 9/15, TransArc wins 3/15
   Note: V87 uses 10% gold SAD-SAM + TransArc SAM-CODE; TransArc is fully automatic

3. **Average computable metrics:**
   - F1 CODE: TransArc=0.803, V45=0.893, LLM=0.829, V87=0.891
   - MCC CODE: TransArc=0.802, V45=0.885, LLM=0.820, V87=0.882
   - NDG: TransArc=0.803, V45=0.907, LLM=0.839, V87=0.906

4. **Fair comparison caveat**: V87 has structural advantages (few-shot training)
   and disadvantages (TransArc SAM-CODE vs gold SAM-CODE) that make direct
   comparison imperfect. Metrics requiring per-link data (N2-N4, N6) would
   provide a more complete picture but are unavailable for V87.

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 four_system_comparison.py
# Output: FOUR_SYSTEM_COMPARISON.md
```
