# TransArc vs V22: Comprehensive Metric Comparison

Two-system comparison using our full metric suite at SAD-SAM and SAD-CODE levels.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)
- **V22**: 10-phase LLM linker (SAD-SAM), projected through **gold SAM-CODE** for SAD-CODE

V22 is a SAD-SAM linker; its SAD-CODE result is composed transitively via gold SAM-CODE.
TransArc produces SAD-CODE directly via its own SAM-CODE pipeline.

**Metrics:**
- Standard P/R/F1, MCC (N1), EMR (N2), MAP (N3), ACF1 (N4), NDG (N5), HUS (N6)
- Debiasing: IDF-weighted F1, Component-Macro F1, PDR F1

---

## Mediastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| SAD-SAM | V22 | 0.938 | 0.968 | 0.952 | 30 | 2 | 1 |
| SAD-SAM | **Δ (V22−T)** | -0.007 | +0.419 | **+0.259** | +13 | +1 | -13 |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V22 | 0.965 | 0.932 | 0.948 | 55 | 2 | 4 |
| SAD-CODE | **Δ (V22−T)** | +0.003 | +0.508 | **+0.360** | +30 | +1 | -30 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.711 | 0.773 |
| SAD-SAM | V22 | 0.950 | 0.982 |
| SAD-SAM | **Δ** | **+0.239** | +0.209 |
| SAD-CODE | TransArc | 0.633 | 0.712 |
| SAD-CODE | V22 | 0.947 | 0.966 |
| SAD-CODE | **Δ** | **+0.314** | +0.254 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.556 | 0.574 | 0.556 | 0.593 | 0.407 |
| SAD-SAM | V22 | 0.963 | 0.981 | 0.963 | 1.000 | 0.000 |
| SAD-CODE | TransArc | 0.600 | 0.613 | 0.600 | 0.640 | 0.360 |
| SAD-CODE | V22 | 0.960 | 0.960 | 0.960 | 0.960 | 0.040 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.574 |
| SAD-SAM | V22 | 0.981 |
| SAD-SAM | **Δ** | **+0.407** |
| SAD-CODE | TransArc | 0.613 |
| SAD-CODE | V22 | 0.960 |
| SAD-CODE | **Δ** | **+0.347** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.588 | 0.739 | +0.151 |
| V22 | 0.948 | 0.947 | -0.001 |
| **Δ (V22−T)** | **+0.360** | **+0.208** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.124 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | 0.530 |
| V22 | 0.948 | 0.941 |
| **Δ** | **+0.360** | **+0.411** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.778 | 0.700 | 0.875 |
| SAD-SAM | V22 | 0.947 | 1.000 | 0.900 |
| SAD-CODE | TransArc | 0.762 | 0.640 | 0.941 |
| SAD-CODE | V22 | 0.941 | 0.960 | 0.923 |

### Enrollment Debiasing

| Metric | TransArc | V22 | Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.588 | 0.948 | +0.360 |
| IDF-Weighted F1 | 0.657 | 0.943 | +0.287 |
| Component-Macro F1 | 0.661 | 0.935 | +0.274 |
| PDR F1 | 0.641 | 0.951 | +0.310 |

---

## Teastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V22 | 0.964 | 1.000 | 0.982 | 27 | 1 | 0 |
| SAD-SAM | **Δ (V22−T)** | -0.036 | +0.259 | **+0.131** | +7 | +1 | -7 |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V22 | 0.981 | 1.000 | 0.990 | 707 | 14 | 0 |
| SAD-CODE | **Δ (V22−T)** | -0.019 | +0.291 | **+0.161** | +206 | +14 | -206 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.857 | 0.870 |
| SAD-SAM | V22 | 0.981 | 0.999 |
| SAD-SAM | **Δ** | **+0.124** | +0.129 |
| SAD-CODE | TransArc | 0.828 | 0.854 |
| SAD-CODE | V22 | 0.989 | 0.999 |
| SAD-CODE | **Δ** | **+0.161** | +0.145 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-SAM | V22 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-CODE | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-CODE | V22 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.696 |
| SAD-SAM | V22 | 1.000 |
| SAD-SAM | **Δ** | **+0.304** |
| SAD-CODE | TransArc | 0.696 |
| SAD-CODE | V22 | 1.000 |
| SAD-CODE | **Δ** | **+0.304** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.829 | 0.851 | +0.022 |
| V22 | 0.990 | 0.982 | -0.008 |
| **Δ (V22−T)** | **+0.161** | **+0.131** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.120 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | 0.806 |
| V22 | 0.990 | 0.989 |
| **Δ** | **+0.161** | **+0.183** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 1.000 | 1.000 |
| SAD-SAM | V22 | 0.909 | 1.000 | 0.833 |
| SAD-CODE | TransArc | 0.821 | 0.696 | 1.000 |
| SAD-CODE | V22 | 0.979 | 1.000 | 0.958 |

### Enrollment Debiasing

| Metric | TransArc | V22 | Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.829 | 0.990 | +0.161 |
| IDF-Weighted F1 | 0.836 | 0.988 | +0.152 |
| Component-Macro F1 | 0.839 | 0.967 | +0.128 |
| PDR F1 | 0.830 | 0.990 | +0.161 |

---

## Teammates

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V22 | 0.758 | 0.877 | 0.813 | 50 | 16 | 7 |
| SAD-SAM | **Δ (V22−T)** | +0.153 | +0.018 | **+0.103** | +1 | -16 | -1 |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V22 | 0.798 | 0.763 | 0.780 | 6174 | 1567 | 1923 |
| SAD-CODE | **Δ (V22−T)** | +0.044 | -0.140 | **-0.041** | -1133 | -828 | +1133 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.714 | 0.924 |
| SAD-SAM | V22 | 0.811 | 0.936 |
| SAD-SAM | **Δ** | **+0.097** | +0.012 |
| SAD-CODE | TransArc | 0.814 | 0.943 |
| SAD-CODE | V22 | 0.768 | 0.876 |
| SAD-CODE | **Δ** | **-0.046** | -0.067 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.756 | 0.800 | 0.822 | 0.778 | 0.133 |
| SAD-SAM | V22 | 0.800 | 0.830 | 0.844 | 0.800 | 0.089 |
| SAD-CODE | TransArc | 0.370 | 0.493 | 0.554 | 0.413 | 0.391 |
| SAD-CODE | V22 | 0.337 | 0.405 | 0.359 | 0.391 | 0.554 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.800 |
| SAD-SAM | V22 | 0.839 |
| SAD-SAM | **Δ** | **+0.039** |
| SAD-CODE | TransArc | 0.514 |
| SAD-CODE | V22 | 0.402 |
| SAD-CODE | **Δ** | **-0.112** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.821 | 0.624 | -0.197 |
| V22 | 0.780 | 0.576 | -0.204 |
| **Δ (V22−T)** | **-0.041** | **-0.048** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.055 | Oracle F1: 0.881

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | 0.927 |
| V22 | 0.780 | 0.877 |
| **Δ** | **-0.041** | **-0.050** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.222 | 1.000 | 0.125 |
| SAD-SAM | V22 | 0.400 | 1.000 | 0.250 |
| SAD-CODE | TransArc | 0.591 | 0.598 | 0.585 |
| SAD-CODE | V22 | 0.526 | 0.424 | 0.692 |

### Enrollment Debiasing

| Metric | TransArc | V22 | Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.821 | 0.780 | -0.041 |
| IDF-Weighted F1 | 0.817 | 0.782 | -0.035 |
| Component-Macro F1 | 0.723 | 0.723 | +0.001 |
| PDR F1 | 0.819 | 0.778 | -0.042 |

---

## Bigbluebutton

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V22 | 0.768 | 0.855 | 0.809 | 53 | 16 | 9 |
| SAD-SAM | **Δ (V22−T)** | -0.130 | +0.145 | **+0.016** | +9 | +11 | -9 |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V22 | 0.829 | 0.969 | 0.894 | 1481 | 305 | 48 |
| SAD-CODE | **Δ (V22−T)** | +0.009 | +0.127 | **+0.063** | +194 | +23 | -194 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.792 | 0.853 |
| SAD-SAM | V22 | 0.804 | 0.923 |
| SAD-SAM | **Δ** | **+0.011** | +0.070 |
| SAD-CODE | TransArc | 0.820 | 0.915 |
| SAD-CODE | V22 | 0.889 | 0.978 |
| SAD-CODE | **Δ** | **+0.069** | +0.063 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.604 | 0.712 | 0.646 | 0.750 | 0.188 |
| SAD-SAM | V22 | 0.708 | 0.842 | 0.812 | 0.854 | 0.042 |
| SAD-CODE | TransArc | 0.156 | 0.675 | 0.667 | 0.244 | 0.178 |
| SAD-CODE | V22 | 0.867 | 0.921 | 0.933 | 0.889 | 0.044 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.709 |
| SAD-SAM | V22 | 0.856 |
| SAD-SAM | **Δ** | **+0.146** |
| SAD-CODE | TransArc | 0.725 |
| SAD-CODE | V22 | 0.971 |
| SAD-CODE | **Δ** | **+0.246** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.831 | 0.347 | -0.484 |
| V22 | 0.894 | 0.841 | -0.052 |
| **Δ (V22−T)** | **+0.063** | **+0.495** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.059 | Oracle F1: 0.968

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | 0.850 |
| V22 | 0.894 | 0.919 |
| **Δ** | **+0.063** | **+0.069** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.842 | 1.000 | 0.727 |
| SAD-SAM | V22 | 0.737 | 1.000 | 0.583 |
| SAD-CODE | TransArc | 0.405 | 0.822 | 0.268 |
| SAD-CODE | V22 | 0.817 | 0.956 | 0.714 |

### Enrollment Debiasing

| Metric | TransArc | V22 | Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.831 | 0.894 | +0.063 |
| IDF-Weighted F1 | 0.860 | 0.921 | +0.061 |
| Component-Macro F1 | 0.863 | 0.909 | +0.046 |
| PDR F1 | 0.757 | 0.910 | +0.153 |

---

## Jabref

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V22 | 0.857 | 1.000 | 0.923 | 18 | 3 | 0 |
| SAD-SAM | **Δ (V22−T)** | -0.043 | +0.000 | **-0.024** | +0 | +1 | +0 |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V22 | 0.870 | 1.000 | 0.930 | 8268 | 1240 | 0 |
| SAD-CODE | **Δ (V22−T)** | -0.023 | +0.000 | **-0.013** | +0 | +246 | +0 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.933 | 0.983 |
| SAD-SAM | V22 | 0.902 | 0.975 |
| SAD-SAM | **Δ** | **-0.030** | -0.008 |
| SAD-CODE | TransArc | 0.917 | 0.971 |
| SAD-CODE | V22 | 0.898 | 0.964 |
| SAD-CODE | **Δ** | **-0.019** | -0.007 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | V22 | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-CODE | TransArc | 0.500 | 0.918 | 1.000 | 0.500 | 0.000 |
| SAD-CODE | V22 | 0.800 | 0.918 | 1.000 | 0.800 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.950 |
| SAD-SAM | V22 | 0.950 |
| SAD-SAM | **Δ** | **+0.000** |
| SAD-CODE | TransArc | 0.935 |
| SAD-CODE | V22 | 0.937 |
| SAD-CODE | **Δ** | **+0.002** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.943 | 0.857 | -0.086 |
| V22 | 0.930 | 0.923 | -0.007 |
| **Δ (V22−T)** | **-0.013** | **+0.066** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.335 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | 0.915 |
| V22 | 0.930 | 0.895 |
| **Δ** | **-0.013** | **-0.020** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.750 | 1.000 | 0.600 |
| SAD-SAM | V22 | 0.571 | 1.000 | 0.400 |
| SAD-CODE | TransArc | 0.667 | 1.000 | 0.500 |
| SAD-CODE | V22 | 0.842 | 1.000 | 0.727 |

### Enrollment Debiasing

| Metric | TransArc | V22 | Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.943 | 0.930 | -0.013 |
| IDF-Weighted F1 | 0.941 | 0.930 | -0.011 |
| Component-Macro F1 | 0.948 | 0.935 | -0.013 |
| PDR F1 | 0.943 | 0.930 | -0.013 |

---

## Cross-Project Summary

### SAD-SAM F1

| Project | TransArc | V22 | Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.694 | 0.952 | +0.259 | V22 |
| teastore | 0.851 | 0.982 | +0.131 | V22 |
| teammates | 0.710 | 0.813 | +0.103 | V22 |
| bigbluebutton | 0.793 | 0.809 | +0.016 | V22 |
| jabref | 0.947 | 0.923 | -0.024 | TransArc |
| **Average** | **0.799** | **0.896** | **+0.097** | **V22** |

### SAD-CODE F1

| Project | TransArc | V22 | Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.588 | 0.948 | +0.360 | V22 |
| teastore | 0.829 | 0.990 | +0.161 | V22 |
| teammates | 0.821 | 0.780 | -0.041 | TransArc |
| bigbluebutton | 0.831 | 0.894 | +0.063 | V22 |
| jabref | 0.943 | 0.930 | -0.013 | TransArc |
| **Average** | **0.803** | **0.908** | **+0.106** | **V22** |

### All Metrics: Average Across Projects

| Metric | Level | TransArc | V22 | Δ | Winner |
|:--|:--|:---:|:---:|:---:|:--|
| F1 | SAD-SAM | 0.799 | 0.896 | +0.097 | V22 |
| F1 | SAD-CODE | 0.803 | 0.908 | +0.106 | V22 |
| MCC | SAD-SAM | 0.801 | 0.890 | +0.088 | V22 |
| MCC | SAD-CODE | 0.802 | 0.898 | +0.096 | V22 |
| EMR | SAD-SAM | 0.682 | 0.854 | +0.172 | V22 |
| EMR | SAD-CODE | 0.464 | 0.793 | +0.329 | V22 |
| MAP | SAD-SAM | 0.746 | 0.925 | +0.179 | V22 |
| MAP | SAD-CODE | 0.697 | 0.854 | +0.157 | V22 |
| ACF1 | SAD-CODE | 0.684 | 0.854 | +0.170 | V22 |
| NDG | SAD-CODE | 0.805 | 0.924 | +0.119 | V22 |
| HUS | SAD-SAM | 0.718 | 0.713 | -0.005 | TransArc |
| HUS | SAD-CODE | 0.649 | 0.821 | +0.172 | V22 |
| IDF F1 | SAD-CODE | 0.822 | 0.913 | +0.091 | V22 |
| Macro F1 | SAD-CODE | 0.807 | 0.894 | +0.087 | V22 |
| PDR F1 | SAD-CODE | 0.798 | 0.912 | +0.114 | V22 |

**Score: V22 wins 14, TransArc wins 1, Ties 0** (across 15 metrics)

### Per-Project Wins (SAD-CODE metrics only)

| Project | TransArc Wins | V22 Wins | Ties |
|:--|:---:|:---:|:---:|
| mediastore | 0 | 10 | 0 |
| teastore | 0 | 10 | 0 |
| teammates | 9 | 0 | 1 |
| bigbluebutton | 0 | 10 | 0 |
| jabref | 6 | 3 | 1 |
| **Total** | **15** | **33** | **2** |

---

## Key Findings

1. **SAD-SAM**: V22 avg F1 = 0.896 vs TransArc 0.799 (Δ=+0.097)
2. **SAD-CODE** (standard): V22 avg F1 = 0.908 vs TransArc 0.803 (Δ=+0.106)
3. **SAD-CODE** (debiased macro): V22 = 0.894 vs TransArc 0.807 (Δ=+0.087)
4. **MCC SAD-SAM**: V22 = 0.890 vs TransArc 0.801 (Δ=+0.088)

**SAD-SAM project wins**: V22 4/5, TransArc 1/5
**SAD-CODE project wins**: V22 3/5, TransArc 2/5

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 transarc_vs_v22_comparison.py
```

