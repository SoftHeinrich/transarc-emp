# Three-System Comparison: TransArc vs V45 vs LLM Adaptive

Unified evaluation of 3 systems across 6 new metrics (N1-N6)
at both SAD-SAM and SAD-CODE levels, plus enrollment debiasing metrics.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)
- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through gold SAM-CODE
- **LLM Adaptive**: Zero-training LLM classifier (best strategy per project),
  projected through gold SAM-CODE

| Project | LLM Strategy |
|:--|:--|
| mediastore | majority |
| teastore | intersection |
| teammates | intersection |
| bigbluebutton | majority |
| jabref | single |

---

## Mediastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| SAD-SAM | V45 | 0.963 | 0.839 | 0.897 | 26 | 1 | 5 |
| SAD-SAM | LLM Adaptive | 1.000 | 0.871 | 0.931 | 27 | 0 | 4 |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V45 | 0.979 | 0.780 | 0.868 | 46 | 1 | 13 |
| SAD-CODE | LLM Adaptive | 1.000 | 0.932 | 0.965 | 55 | 0 | 4 |

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.711** | 0.773 | 17 | 1 | 14 | 671 |
| SAD-SAM | V45 | **0.894** | 0.919 | 26 | 1 | 5 | 671 |
| SAD-SAM | LLM | **0.930** | 0.935 | 27 | 0 | 4 | 672 |
| SAD-CODE | TransArc | **0.633** | 0.712 | 25 | 1 | 34 | 2086 |
| SAD-CODE | V45 | **0.871** | 0.890 | 46 | 1 | 13 | 2086 |
| SAD-CODE | LLM | **0.965** | 0.966 | 55 | 0 | 4 | 2087 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.556** | 0.574 | 0.556 | 0.593 | 0.407 |
| SAD-SAM | V45 | **0.815** | 0.852 | 0.815 | 0.889 | 0.111 |
| SAD-SAM | LLM | **0.889** | 0.889 | 0.889 | 0.889 | 0.111 |
| SAD-CODE | TransArc | **0.600** | 0.613 | 0.600 | 0.640 | 0.360 |
| SAD-CODE | V45 | **0.800** | 0.827 | 0.800 | 0.840 | 0.160 |
| SAD-CODE | LLM | **0.960** | 0.960 | 0.960 | 0.960 | 0.040 |

### N3: MAP

| Level | System | MAP | Note |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.574** | uniform conf |
| SAD-SAM | V45 | **0.852** | per-link conf |
| SAD-SAM | LLM | **0.889** | uniform conf |
| SAD-CODE | TransArc | **0.613** | uniform conf |
| SAD-CODE | V45 | **0.827** | inherited conf |
| SAD-CODE | LLM | **0.960** | uniform conf |

### N4: ACF1

| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.588 | **0.739** | +0.151 | 17.0 | 1.0 | 11.0 |
| V45 | 0.868 | **0.885** | +0.017 | 23.0 | 1.0 | 5.0 |
| LLM | 0.965 | **0.982** | +0.017 | 27.0 | 0.0 | 1.0 |

### N5: NDG

Random F1: 0.148 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | **0.516** |
| V45 | 0.868 | **0.845** |
| LLM | 0.965 | **0.959** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.593 | 0.941 | **0.727** |
| SAD-SAM | V45 | 0.889 | 0.960 | **0.923** |
| SAD-SAM | LLM | 0.889 | 1.000 | **0.941** |
| SAD-CODE | TransArc | 0.640 | 0.941 | **0.762** |
| SAD-CODE | V45 | 0.840 | 0.955 | **0.894** |
| SAD-CODE | LLM | 0.960 | 1.000 | **0.980** |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.588 | 0.868 | 0.965 |
| IDF-Weighted F1 | 0.657 | 0.879 | 0.972 |
| Component-Macro F1 | 0.661 | 0.894 | 0.985 |
| Popularity-Debiased F1 | 0.641 | 0.872 | 0.970 |
| N4: ACF1 | 0.739 | 0.885 | 0.982 |

---

## Teastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V45 | 0.964 | 1.000 | 0.982 | 27 | 1 | 0 |
| SAD-SAM | LLM Adaptive | 0.676 | 0.926 | 0.781 | 25 | 12 | 2 |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V45 | 0.981 | 1.000 | 0.990 | 707 | 14 | 0 |
| SAD-CODE | LLM Adaptive | 0.632 | 0.966 | 0.764 | 683 | 397 | 24 |

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.857** | 0.870 | 20 | 0 | 7 | 790 |
| SAD-SAM | V45 | **0.981** | 0.999 | 27 | 1 | 0 | 789 |
| SAD-SAM | LLM | **0.783** | 0.955 | 25 | 12 | 2 | 778 |
| SAD-CODE | TransArc | **0.828** | 0.854 | 501 | 0 | 206 | 6001 |
| SAD-CODE | V45 | **0.989** | 0.999 | 707 | 14 | 0 | 5987 |
| SAD-CODE | LLM | **0.752** | 0.950 | 683 | 397 | 24 | 5604 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.696** | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-SAM | V45 | **1.000** | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-SAM | LLM | **0.913** | 0.913 | 0.913 | 0.913 | 0.087 |
| SAD-CODE | TransArc | **0.696** | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-CODE | V45 | **1.000** | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-CODE | LLM | **0.913** | 0.913 | 0.913 | 0.913 | 0.087 |

### N3: MAP

| Level | System | MAP | Note |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.696** | uniform conf |
| SAD-SAM | V45 | **1.000** | per-link conf |
| SAD-SAM | LLM | **0.913** | uniform conf |
| SAD-CODE | TransArc | **0.696** | uniform conf |
| SAD-CODE | V45 | **1.000** | inherited conf |
| SAD-CODE | LLM | **0.913** | uniform conf |

### N4: ACF1

| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.829 | **0.851** | +0.022 | 20.0 | 0.0 | 7.0 |
| V45 | 0.990 | **0.982** | -0.008 | 27.0 | 1.0 | 0.0 |
| LLM | 0.764 | **0.781** | +0.017 | 25.0 | 12.0 | 2.0 |

### N5: NDG

Random F1: 0.120 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | **0.806** |
| V45 | 0.990 | **0.989** |
| LLM | 0.764 | **0.732** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-SAM | V45 | 1.000 | 0.958 | **0.979** |
| SAD-SAM | LLM | 0.913 | 0.636 | **0.750** |
| SAD-CODE | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-CODE | V45 | 1.000 | 0.958 | **0.979** |
| SAD-CODE | LLM | 0.913 | 0.636 | **0.750** |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.829 | 0.990 | 0.764 |
| IDF-Weighted F1 | 0.836 | 0.988 | 0.754 |
| Component-Macro F1 | 0.839 | 0.967 | 0.783 |
| Popularity-Debiased F1 | 0.830 | 0.990 | 0.764 |
| N4: ACF1 | 0.851 | 0.982 | 0.781 |

---

## Teammates

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V45 | 0.820 | 0.877 | 0.847 | 50 | 11 | 7 |
| SAD-SAM | LLM Adaptive | 0.625 | 0.789 | 0.698 | 45 | 27 | 12 |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V45 | 0.803 | 0.770 | 0.786 | 6235 | 1525 | 1862 |
| SAD-CODE | LLM Adaptive | 0.656 | 0.766 | 0.707 | 6205 | 3257 | 1892 |

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.714** | 0.924 | 49 | 32 | 8 | 2683 |
| SAD-SAM | V45 | **0.845** | 0.937 | 50 | 11 | 7 | 2704 |
| SAD-SAM | LLM | **0.696** | 0.890 | 45 | 27 | 12 | 2688 |
| SAD-CODE | TransArc | **0.814** | 0.943 | 7307 | 2395 | 790 | 149492 |
| SAD-CODE | V45 | **0.775** | 0.880 | 6235 | 1525 | 1862 | 150362 |
| SAD-CODE | LLM | **0.692** | 0.872 | 6205 | 3257 | 1892 | 148630 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.756** | 0.800 | 0.822 | 0.778 | 0.133 |
| SAD-SAM | V45 | **0.778** | 0.822 | 0.844 | 0.800 | 0.133 |
| SAD-SAM | LLM | **0.622** | 0.730 | 0.733 | 0.711 | 0.156 |
| SAD-CODE | TransArc | **0.370** | 0.493 | 0.554 | 0.413 | 0.391 |
| SAD-CODE | V45 | **0.337** | 0.404 | 0.359 | 0.391 | 0.576 |
| SAD-CODE | LLM | **0.283** | 0.406 | 0.391 | 0.359 | 0.500 |

### N3: MAP

| Level | System | MAP | Note |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.800** | uniform conf |
| SAD-SAM | V45 | **0.833** | per-link conf |
| SAD-SAM | LLM | **0.750** | uniform conf |
| SAD-CODE | TransArc | **0.514** | uniform conf |
| SAD-CODE | V45 | **0.402** | inherited conf |
| SAD-CODE | LLM | **0.406** | uniform conf |

### N4: ACF1

| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.821 | **0.624** | -0.197 | 57.4 | 21.6 | 47.5 |
| V45 | 0.786 | **0.593** | -0.193 | 48.6 | 10.4 | 56.2 |
| LLM | 0.707 | **0.535** | -0.171 | 47.3 | 24.7 | 57.5 |

### N5: NDG

Random F1: 0.055 | Oracle F1: 0.881

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | **0.927** |
| V45 | 0.786 | **0.885** |
| LLM | 0.707 | **0.789** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.844 | 0.530 | **0.651** |
| SAD-SAM | V45 | 0.867 | 0.766 | **0.813** |
| SAD-SAM | LLM | 0.844 | 0.552 | **0.667** |
| SAD-CODE | TransArc | 0.598 | 0.585 | **0.591** |
| SAD-CODE | V45 | 0.424 | 0.766 | **0.546** |
| SAD-CODE | LLM | 0.467 | 0.569 | **0.513** |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.821 | 0.786 | 0.707 |
| IDF-Weighted F1 | 0.817 | 0.784 | 0.706 |
| Component-Macro F1 | 0.723 | 0.717 | 0.643 |
| Popularity-Debiased F1 | 0.819 | 0.784 | 0.705 |
| N4: ACF1 | 0.624 | 0.593 | 0.535 |

---

## Bigbluebutton

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V45 | 0.852 | 0.839 | 0.846 | 52 | 9 | 10 |
| SAD-SAM | LLM Adaptive | 0.642 | 0.548 | 0.591 | 34 | 19 | 28 |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V45 | 0.817 | 0.947 | 0.877 | 1448 | 325 | 81 |
| SAD-CODE | LLM Adaptive | 0.656 | 0.772 | 0.710 | 1181 | 618 | 348 |

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.792** | 0.853 | 44 | 5 | 18 | 1847 |
| SAD-SAM | V45 | **0.840** | 0.917 | 52 | 9 | 10 | 1843 |
| SAD-SAM | LLM | **0.581** | 0.769 | 34 | 19 | 28 | 1833 |
| SAD-CODE | TransArc | **0.820** | 0.915 | 1287 | 282 | 242 | 22723 |
| SAD-CODE | V45 | **0.871** | 0.966 | 1448 | 325 | 81 | 22680 |
| SAD-CODE | LLM | **0.691** | 0.873 | 1181 | 618 | 348 | 22387 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.604** | 0.712 | 0.646 | 0.750 | 0.188 |
| SAD-SAM | V45 | **0.708** | 0.832 | 0.792 | 0.854 | 0.062 |
| SAD-SAM | LLM | **0.479** | 0.569 | 0.542 | 0.562 | 0.250 |
| SAD-CODE | TransArc | **0.156** | 0.675 | 0.667 | 0.244 | 0.178 |
| SAD-CODE | V45 | **0.867** | 0.910 | 0.911 | 0.889 | 0.067 |
| SAD-CODE | LLM | **0.600** | 0.644 | 0.644 | 0.622 | 0.222 |

### N3: MAP

| Level | System | MAP | Note |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.709** | uniform conf |
| SAD-SAM | V45 | **0.866** | per-link conf |
| SAD-SAM | LLM | **0.591** | uniform conf |
| SAD-CODE | TransArc | **0.725** | uniform conf |
| SAD-CODE | V45 | **0.974** | inherited conf |
| SAD-CODE | LLM | **0.651** | uniform conf |

### N4: ACF1

| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.831 | **0.347** | -0.484 | 39.9 | 139.1 | 11.2 |
| V45 | 0.877 | **0.886** | +0.009 | 47.0 | 8.1 | 4.0 |
| LLM | 0.710 | **0.673** | -0.037 | 34.0 | 16.1 | 17.0 |

### N5: NDG

Random F1: 0.059 | Oracle F1: 0.968

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | **0.850** |
| V45 | 0.877 | **0.900** |
| LLM | 0.710 | **0.716** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.812 | 0.878 | **0.844** |
| SAD-SAM | V45 | 0.938 | 0.820 | **0.875** |
| SAD-SAM | LLM | 0.667 | 0.600 | **0.632** |
| SAD-CODE | TransArc | 0.822 | 0.268 | **0.405** |
| SAD-CODE | V45 | 0.933 | 0.816 | **0.871** |
| SAD-CODE | LLM | 0.711 | 0.622 | **0.664** |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.831 | 0.877 | 0.710 |
| IDF-Weighted F1 | 0.860 | 0.876 | 0.665 |
| Component-Macro F1 | 0.863 | 0.901 | 0.700 |
| Popularity-Debiased F1 | 0.757 | 0.874 | 0.660 |
| N4: ACF1 | 0.347 | 0.886 | 0.673 |

---

## Jabref

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V45 | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | LLM Adaptive | 0.947 | 1.000 | 0.973 | 18 | 1 | 0 |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V45 | 0.893 | 1.000 | 0.944 | 8268 | 990 | 0 |
| SAD-CODE | LLM Adaptive | 0.998 | 1.000 | 0.999 | 8268 | 18 | 0 |

### N1: MCC

| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |
|:--|:--|:---:|:---:|---:|---:|---:|---:|
| SAD-SAM | TransArc | **0.933** | 0.983 | 18 | 2 | 0 | 58 |
| SAD-SAM | V45 | **0.933** | 0.983 | 18 | 2 | 0 | 58 |
| SAD-SAM | LLM | **0.965** | 0.992 | 18 | 1 | 0 | 59 |
| SAD-CODE | TransArc | **0.917** | 0.971 | 8268 | 994 | 0 | 16166 |
| SAD-CODE | V45 | **0.917** | 0.971 | 8268 | 990 | 0 | 16170 |
| SAD-CODE | LLM | **0.998** | 0.999 | 8268 | 18 | 0 | 17142 |

### N2: EMR

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.800** | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | V45 | **0.800** | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | LLM | **0.900** | 0.950 | 1.000 | 0.900 | 0.000 |
| SAD-CODE | TransArc | **0.500** | 0.918 | 1.000 | 0.500 | 0.000 |
| SAD-CODE | V45 | **0.800** | 0.918 | 1.000 | 0.800 | 0.000 |
| SAD-CODE | LLM | **0.900** | 0.998 | 1.000 | 0.900 | 0.000 |

### N3: MAP

| Level | System | MAP | Note |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.950** | uniform conf |
| SAD-SAM | V45 | **0.950** | per-link conf |
| SAD-SAM | LLM | **0.950** | uniform conf |
| SAD-CODE | TransArc | **0.935** | uniform conf |
| SAD-CODE | V45 | **0.933** | inherited conf |
| SAD-CODE | LLM | **0.994** | uniform conf |

### N4: ACF1

| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.943 | **0.857** | -0.086 | 18.0 | 6.0 | 0.0 |
| V45 | 0.944 | **0.947** | +0.004 | 18.0 | 2.0 | 0.0 |
| LLM | 0.999 | **0.973** | -0.026 | 18.0 | 1.0 | 0.0 |

### N5: NDG

Random F1: 0.335 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | **0.915** |
| V45 | 0.944 | **0.915** |
| LLM | 0.999 | **0.998** |

### N6: HUS

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 0.800 | **0.889** |
| SAD-SAM | V45 | 1.000 | 0.800 | **0.889** |
| SAD-SAM | LLM | 1.000 | 0.900 | **0.947** |
| SAD-CODE | TransArc | 1.000 | 0.500 | **0.667** |
| SAD-CODE | V45 | 1.000 | 0.800 | **0.889** |
| SAD-CODE | LLM | 1.000 | 0.900 | **0.947** |

### Enrollment Debiasing

| Metric | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.943 | 0.944 | 0.999 |
| IDF-Weighted F1 | 0.941 | 0.941 | 0.998 |
| Component-Macro F1 | 0.948 | 0.948 | 0.967 |
| Popularity-Debiased F1 | 0.943 | 0.943 | 0.999 |
| N4: ACF1 | 0.857 | 0.947 | 0.973 |

---

## Aggregate Comparison

### Standard F1

| Project | | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.694 | 0.897 | 0.931 | LLM |
| | CODE | 0.588 | 0.868 | 0.965 | LLM |
| teastore | SAM | 0.851 | 0.982 | 0.781 | V45 |
| | CODE | 0.829 | 0.990 | 0.764 | V45 |
| teammates | SAM | 0.710 | 0.847 | 0.698 | V45 |
| | CODE | 0.821 | 0.786 | 0.707 | TransArc |
| bigbluebutton | SAM | 0.793 | 0.846 | 0.591 | V45 |
| | CODE | 0.831 | 0.877 | 0.710 | V45 |
| jabref | SAM | 0.947 | 0.947 | 0.973 | LLM |
| | CODE | 0.943 | 0.944 | 0.999 | LLM |
| **Average** | SAM | **0.799** | **0.904** | **0.795** | **V45** |
| | CODE | **0.803** | **0.893** | **0.829** | **V45** |

### N1: MCC

| Project | Level | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.711 | 0.894 | 0.930 | LLM |
| | CODE | 0.633 | 0.871 | 0.965 | LLM |
| teastore | SAM | 0.857 | 0.981 | 0.783 | V45 |
| | CODE | 0.828 | 0.989 | 0.752 | V45 |
| teammates | SAM | 0.714 | 0.845 | 0.696 | V45 |
| | CODE | 0.814 | 0.775 | 0.692 | TransArc |
| bigbluebutton | SAM | 0.792 | 0.840 | 0.581 | V45 |
| | CODE | 0.820 | 0.871 | 0.691 | V45 |
| jabref | SAM | 0.933 | 0.933 | 0.965 | LLM |
| | CODE | 0.917 | 0.917 | 0.998 | LLM |
| **Average** | SAM | **0.801** | **0.899** | **0.791** | **V45** |
| | CODE | **0.802** | **0.885** | **0.820** | **V45** |

### N2: EMR

| Project | Level | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.556 | 0.815 | 0.889 | LLM |
| | CODE | 0.600 | 0.800 | 0.960 | LLM |
| teastore | SAM | 0.696 | 1.000 | 0.913 | V45 |
| | CODE | 0.696 | 1.000 | 0.913 | V45 |
| teammates | SAM | 0.756 | 0.778 | 0.622 | V45 |
| | CODE | 0.370 | 0.337 | 0.283 | TransArc |
| bigbluebutton | SAM | 0.604 | 0.708 | 0.479 | V45 |
| | CODE | 0.156 | 0.867 | 0.600 | V45 |
| jabref | SAM | 0.800 | 0.800 | 0.900 | LLM |
| | CODE | 0.500 | 0.800 | 0.900 | LLM |
| **Average** | SAM | **0.682** | **0.820** | **0.761** | **V45** |
| | CODE | **0.464** | **0.761** | **0.731** | **V45** |

### N3: MAP

| Project | Level | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.574 | 0.852 | 0.889 | LLM |
| | CODE | 0.613 | 0.827 | 0.960 | LLM |
| teastore | SAM | 0.696 | 1.000 | 0.913 | V45 |
| | CODE | 0.696 | 1.000 | 0.913 | V45 |
| teammates | SAM | 0.800 | 0.833 | 0.750 | V45 |
| | CODE | 0.514 | 0.402 | 0.406 | TransArc |
| bigbluebutton | SAM | 0.709 | 0.866 | 0.591 | V45 |
| | CODE | 0.725 | 0.974 | 0.651 | V45 |
| jabref | SAM | 0.950 | 0.950 | 0.950 | TransArc |
| | CODE | 0.935 | 0.933 | 0.994 | LLM |
| **Average** | SAM | **0.746** | **0.900** | **0.819** | **V45** |
| | CODE | **0.697** | **0.827** | **0.785** | **V45** |

### N4: ACF1 (Enrollment-Corrected)

| Project | TransArc | V45 | LLM | Best |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.739 | 0.885 | 0.982 | LLM |
| teastore | 0.851 | 0.982 | 0.781 | V45 |
| teammates | 0.624 | 0.593 | 0.535 | TransArc |
| bigbluebutton | 0.347 | 0.886 | 0.673 | V45 |
| jabref | 0.857 | 0.947 | 0.973 | LLM |
| **Average** | **0.684** | **0.859** | **0.789** | **V45** |

### N5: NDG (Difficulty-Normalized)

| Project | Random | Oracle | TransArc | V45 | LLM | Best |
|:--|:---:|:---:|:---:|:---:|:---:|:--|
| mediastore | 0.148 | 1.000 | 0.516 | 0.845 | 0.959 | LLM |
| teastore | 0.120 | 1.000 | 0.806 | 0.989 | 0.732 | V45 |
| teammates | 0.055 | 0.881 | 0.927 | 0.885 | 0.789 | TransArc |
| bigbluebutton | 0.059 | 0.968 | 0.850 | 0.900 | 0.716 | V45 |
| jabref | 0.335 | 1.000 | 0.915 | 0.915 | 0.998 | LLM |
| **Average** | | | **0.803** | **0.907** | **0.839** | **V45** |

### N6: HUS

| Project | Level | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | SAM | 0.727 | 0.923 | 0.941 | LLM |
| | CODE | 0.762 | 0.894 | 0.980 | LLM |
| teastore | SAM | 0.821 | 0.979 | 0.750 | V45 |
| | CODE | 0.821 | 0.979 | 0.750 | V45 |
| teammates | SAM | 0.651 | 0.813 | 0.667 | V45 |
| | CODE | 0.591 | 0.546 | 0.513 | TransArc |
| bigbluebutton | SAM | 0.844 | 0.875 | 0.632 | V45 |
| | CODE | 0.405 | 0.871 | 0.664 | V45 |
| jabref | SAM | 0.889 | 0.889 | 0.947 | LLM |
| | CODE | 0.667 | 0.889 | 0.947 | LLM |
| **Average** | SAM | **0.786** | **0.896** | **0.788** | **V45** |
| | CODE | **0.649** | **0.836** | **0.771** | **V45** |

### Enrollment Debiasing Summary

| Project | Metric | TransArc | V45 | LLM | Best |
|:--|:--|:---:|:---:|:---:|:--|
| mediastore | Std F1 | 0.588 | 0.868 | 0.965 | LLM |
|  | IDF-F1 | 0.657 | 0.879 | 0.972 | LLM |
|  | Macro-F1 | 0.661 | 0.894 | 0.985 | LLM |
|  | PDR-F1 | 0.641 | 0.872 | 0.970 | LLM |
|  | ACF1 | 0.739 | 0.885 | 0.982 | LLM |
| teastore | Std F1 | 0.829 | 0.990 | 0.764 | V45 |
|  | IDF-F1 | 0.836 | 0.988 | 0.754 | V45 |
|  | Macro-F1 | 0.839 | 0.967 | 0.783 | V45 |
|  | PDR-F1 | 0.830 | 0.990 | 0.764 | V45 |
|  | ACF1 | 0.851 | 0.982 | 0.781 | V45 |
| teammates | Std F1 | 0.821 | 0.786 | 0.707 | TransArc |
|  | IDF-F1 | 0.817 | 0.784 | 0.706 | TransArc |
|  | Macro-F1 | 0.723 | 0.717 | 0.643 | TransArc |
|  | PDR-F1 | 0.819 | 0.784 | 0.705 | TransArc |
|  | ACF1 | 0.624 | 0.593 | 0.535 | TransArc |
| bigbluebutton | Std F1 | 0.831 | 0.877 | 0.710 | V45 |
|  | IDF-F1 | 0.860 | 0.876 | 0.665 | V45 |
|  | Macro-F1 | 0.863 | 0.901 | 0.700 | V45 |
|  | PDR-F1 | 0.757 | 0.874 | 0.660 | V45 |
|  | ACF1 | 0.347 | 0.886 | 0.673 | V45 |
| jabref | Std F1 | 0.943 | 0.944 | 0.999 | LLM |
|  | IDF-F1 | 0.941 | 0.941 | 0.998 | LLM |
|  | Macro-F1 | 0.948 | 0.948 | 0.967 | LLM |
|  | PDR-F1 | 0.943 | 0.943 | 0.999 | LLM |
|  | ACF1 | 0.857 | 0.947 | 0.973 | LLM |

**Averages across projects:**

| Metric | TransArc | V45 | LLM | Best |
|:--|:---:|:---:|:---:|:--|
| Standard F1 | 0.803 | 0.893 | 0.829 | V45 |
| IDF-Weighted | 0.822 | 0.893 | 0.819 | V45 |
| Component-Macro | 0.807 | 0.885 | 0.815 | V45 |
| PDR | 0.798 | 0.893 | 0.820 | V45 |
| ACF1 | 0.684 | 0.859 | 0.789 | V45 |

---

## Grand Summary

| Metric | Level | TransArc | V45 | LLM | Best | V45-T Δ | LLM-T Δ |
|:--|:--|:---:|:---:|:---:|:--|:---:|:---:|
| F1 (standard) | SAM | 0.799 | 0.904 | 0.795 | V45 | +0.105 | -0.004 |
| F1 (standard) | CODE | 0.803 | 0.893 | 0.829 | V45 | +0.090 | +0.026 |
| **N1: MCC** | SAM | 0.801 | 0.899 | 0.791 | V45 | +0.097 | -0.011 |
| **N1: MCC** | CODE | 0.802 | 0.885 | 0.820 | V45 | +0.082 | +0.017 |
| **N2: EMR** | SAM | 0.682 | 0.820 | 0.761 | V45 | +0.138 | +0.078 |
| **N2: EMR** | CODE | 0.464 | 0.761 | 0.731 | V45 | +0.297 | +0.267 |
| **N3: MAP** | SAM | 0.746 | 0.900 | 0.819 | V45 | +0.154 | +0.073 |
| **N3: MAP** | CODE | 0.697 | 0.827 | 0.785 | V45 | +0.130 | +0.088 |
| **N4: ACF1** | CODE | 0.684 | 0.859 | 0.789 | V45 | +0.175 | +0.105 |
| **N5: NDG** | CODE | 0.803 | 0.907 | 0.839 | V45 | +0.104 | +0.036 |
| **N6: HUS** | SAM | 0.786 | 0.896 | 0.788 | V45 | +0.109 | +0.001 |
| **N6: HUS** | CODE | 0.649 | 0.836 | 0.771 | V45 | +0.187 | +0.122 |
| IDF-Weighted F1 | CODE | 0.822 | 0.893 | 0.819 | V45 | +0.072 | -0.003 |
| Component-Macro F1 | CODE | 0.807 | 0.885 | 0.815 | V45 | +0.079 | +0.009 |
| PDR F1 | CODE | 0.798 | 0.893 | 0.820 | V45 | +0.095 | +0.022 |

### Per-Project Win Count (across all metrics)

Count of (metric, level) combinations where each system scores highest:

| Project | TransArc | V45 | LLM |
|:--|:---:|:---:|:---:|
| mediastore | 0 | 0 | 12 |
| teastore | 0 | 12 | 0 |
| teammates | 7 | 5 | 0 |
| bigbluebutton | 0 | 12 | 0 |
| jabref | 1 | 0 | 11 |
| **Total** | **8** | **29** | **23** |

### Key Findings

1. **Overall winner: V45** — best on 15/15 aggregate metrics (TransArc: 0, V45: 15, LLM: 0)

2. **LLM vs TransArc:**
   - LLM wins on 11 metrics: F1 (standard) (CODE): 0.829 vs 0.803; N1: MCC (CODE): 0.820 vs 0.802; N2: EMR (SAM): 0.761 vs 0.682
   - TransArc wins on 1 metrics: N1: MCC (SAM): 0.801 vs 0.791

3. **Most discriminating metric: n2_code** — spread of 0.297 between best and worst system

4. **Debiasing impact:** PDR F1 deflates all systems vs Standard F1:
   - TransArc: 0.803 → 0.798 (-0.005)
   - V45: 0.893 → 0.893 (-0.000)
   - LLM: 0.829 → 0.820 (-0.009)

5. **Per-project breakdown:**
   - mediastore: LLM dominates (12/12 metrics)
   - teastore: V45 dominates (12/12 metrics)
   - teammates: TransArc dominates (7/12 metrics)
   - bigbluebutton: V45 dominates (12/12 metrics)
   - jabref: LLM dominates (11/12 metrics)

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 three_system_comparison.py
# Output: THREE_SYSTEM_COMPARISON.md
```

