# TransArc vs V24: Comprehensive Metric Comparison

Two-system comparison using our full metric suite at SAD-SAM and SAD-CODE levels.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)
- **V24**: LLM linker with hybrid batch/union judge (SAD-SAM), projected through **gold SAM-CODE** for SAD-CODE

V24 is a SAD-SAM linker; its SAD-CODE result is composed transitively via gold SAM-CODE.
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
| SAD-SAM | V24| 0.879 | 0.935 | 0.906 | 29 | 4 | 2 |
| SAD-SAM | **Δ (V24−T)** | -0.066 | +0.387 | **+0.212** | +12 | +3 | -12 |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V24| 0.803 | 0.898 | 0.848 | 53 | 13 | 6 |
| SAD-CODE | **Δ (V24−T)** | -0.159 | +0.475 | **+0.260** | +28 | +12 | -28 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.711 | 0.773 |
| SAD-SAM | V24| 0.902 | 0.965 |
| SAD-SAM | **Δ** | **+0.191** | +0.191 |
| SAD-CODE | TransArc | 0.633 | 0.712 |
| SAD-CODE | V24| 0.845 | 0.946 |
| SAD-CODE | **Δ** | **+0.212** | +0.234 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.556 | 0.574 | 0.556 | 0.593 | 0.407 |
| SAD-SAM | V24 | 0.815 | 0.907 | 0.926 | 0.889 | 0.000 |
| SAD-CODE | TransArc | 0.600 | 0.613 | 0.600 | 0.640 | 0.360 |
| SAD-CODE | V24 | 0.800 | 0.867 | 0.920 | 0.840 | 0.040 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.574 |
| SAD-SAM | V24| 0.907 |
| SAD-SAM | **Δ** | **+0.333** |
| SAD-CODE | TransArc | 0.613 |
| SAD-CODE | V24| 0.859 |
| SAD-CODE | **Δ** | **+0.245** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.588 | 0.739 | +0.151 |
| V24| 0.848 | 0.897 | +0.049 |
| **Δ (V24−T)** | **+0.260** | **+0.157** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.148 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | 0.516 |
| V24| 0.848 | 0.821 |
| **Δ** | **+0.260** | **+0.305** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.778 | 0.700 | 0.875 |
| SAD-SAM | V24| 0.889 | 1.000 | 0.800 |
| SAD-CODE | TransArc | 0.762 | 0.640 | 0.941 |
| SAD-CODE | V24| 0.896 | 0.960 | 0.840 |

### Enrollment Debiasing

| Metric | TransArc | V24| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.588 | 0.848 | +0.260 |
| IDF-Weighted F1 | 0.657 | 0.866 | +0.210 |
| Component-Macro F1 | 0.661 | 0.906 | +0.245 |
| PDR F1 | 0.641 | 0.862 | +0.221 |

---

## Teastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V24| 0.963 | 0.963 | 0.963 | 26 | 1 | 1 |
| SAD-SAM | **Δ (V24−T)** | -0.037 | +0.222 | **+0.112** | +6 | +1 | -6 |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V24| 0.993 | 0.973 | 0.983 | 688 | 5 | 19 |
| SAD-CODE | **Δ (V24−T)** | -0.007 | +0.264 | **+0.153** | +187 | +5 | -187 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.857 | 0.870 |
| SAD-SAM | V24| 0.962 | 0.981 |
| SAD-SAM | **Δ** | **+0.105** | +0.110 |
| SAD-CODE | TransArc | 0.828 | 0.854 |
| SAD-CODE | V24| 0.981 | 0.986 |
| SAD-CODE | **Δ** | **+0.153** | +0.132 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-SAM | V24 | 0.957 | 0.957 | 0.957 | 0.957 | 0.043 |
| SAD-CODE | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-CODE | V24 | 0.957 | 0.957 | 0.957 | 0.957 | 0.043 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.696 |
| SAD-SAM | V24| 0.957 |
| SAD-SAM | **Δ** | **+0.261** |
| SAD-CODE | TransArc | 0.696 |
| SAD-CODE | V24| 0.957 |
| SAD-CODE | **Δ** | **+0.261** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.829 | 0.851 | +0.022 |
| V24| 0.983 | 0.963 | -0.020 |
| **Δ (V24−T)** | **+0.153** | **+0.112** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.120 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | 0.806 |
| V24| 0.983 | 0.981 |
| **Δ** | **+0.153** | **+0.174** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 1.000 | 1.000 |
| SAD-SAM | V24| 0.909 | 1.000 | 0.833 |
| SAD-CODE | TransArc | 0.821 | 0.696 | 1.000 |
| SAD-CODE | V24| 0.957 | 0.957 | 0.957 |

### Enrollment Debiasing

| Metric | TransArc | V24| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.829 | 0.983 | +0.153 |
| IDF-Weighted F1 | 0.836 | 0.984 | +0.148 |
| Component-Macro F1 | 0.839 | 0.972 | +0.133 |
| PDR F1 | 0.830 | 0.983 | +0.154 |

---

## Teammates

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V24| 0.838 | 1.000 | 0.912 | 57 | 11 | 0 |
| SAD-SAM | **Δ (V24−T)** | +0.233 | +0.140 | **+0.202** | +8 | -21 | -8 |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V24| 0.849 | 0.810 | 0.829 | 6559 | 1163 | 1538 |
| SAD-CODE | **Δ (V24−T)** | +0.096 | -0.092 | **+0.008** | -748 | -1232 | +748 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.714 | 0.924 |
| SAD-SAM | V24| 0.914 | 0.998 |
| SAD-SAM | **Δ** | **+0.199** | +0.074 |
| SAD-CODE | TransArc | 0.814 | 0.943 |
| SAD-CODE | V24| 0.821 | 0.901 |
| SAD-CODE | **Δ** | **+0.006** | -0.042 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.756 | 0.800 | 0.822 | 0.778 | 0.133 |
| SAD-SAM | V24 | 0.956 | 0.978 | 1.000 | 0.956 | 0.000 |
| SAD-CODE | TransArc | 0.370 | 0.493 | 0.554 | 0.413 | 0.391 |
| SAD-CODE | V24 | 0.391 | 0.461 | 0.424 | 0.446 | 0.511 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.800 |
| SAD-SAM | V24| 1.000 |
| SAD-SAM | **Δ** | **+0.200** |
| SAD-CODE | TransArc | 0.514 |
| SAD-CODE | V24| 0.466 |
| SAD-CODE | **Δ** | **-0.048** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.821 | 0.624 | -0.197 |
| V24| 0.829 | 0.641 | -0.188 |
| **Δ (V24−T)** | **+0.008** | **+0.018** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.055 | Oracle F1: 0.881

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | 0.927 |
| V24| 0.829 | 0.937 |
| **Δ** | **+0.008** | **+0.010** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.222 | 1.000 | 0.125 |
| SAD-SAM | V24| 0.400 | 1.000 | 0.250 |
| SAD-CODE | TransArc | 0.591 | 0.598 | 0.585 |
| SAD-CODE | V24| 0.608 | 0.489 | 0.804 |

### Enrollment Debiasing

| Metric | TransArc | V24| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.821 | 0.829 | +0.008 |
| IDF-Weighted F1 | 0.817 | 0.828 | +0.012 |
| Component-Macro F1 | 0.723 | 0.784 | +0.062 |
| PDR F1 | 0.819 | 0.827 | +0.008 |

---

## Bigbluebutton

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V24| 0.868 | 0.952 | 0.908 | 59 | 9 | 3 |
| SAD-SAM | **Δ (V24−T)** | -0.030 | +0.242 | **+0.115** | +15 | +4 | -15 |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V24| 0.778 | 0.979 | 0.867 | 1497 | 428 | 32 |
| SAD-CODE | **Δ (V24−T)** | -0.043 | +0.137 | **+0.036** | +210 | +146 | -210 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.792 | 0.853 |
| SAD-SAM | V24| 0.905 | 0.973 |
| SAD-SAM | **Δ** | **+0.113** | +0.120 |
| SAD-CODE | TransArc | 0.820 | 0.915 |
| SAD-CODE | V24| 0.863 | 0.980 |
| SAD-CODE | **Δ** | **+0.044** | +0.065 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.604 | 0.712 | 0.646 | 0.750 | 0.188 |
| SAD-SAM | V24 | 0.854 | 0.920 | 0.938 | 0.875 | 0.021 |
| SAD-CODE | TransArc | 0.156 | 0.675 | 0.667 | 0.244 | 0.178 |
| SAD-CODE | V24 | 0.867 | 0.932 | 0.933 | 0.889 | 0.022 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.709 |
| SAD-SAM | V24| 0.916 |
| SAD-SAM | **Δ** | **+0.207** |
| SAD-CODE | TransArc | 0.725 |
| SAD-CODE | V24| 1.082 |
| SAD-CODE | **Δ** | **+0.357** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.831 | 0.347 | -0.484 |
| V24| 0.867 | 0.907 | +0.040 |
| **Δ (V24−T)** | **+0.036** | **+0.560** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.054 | Oracle F1: 0.968

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | 0.850 |
| V24| 0.867 | 0.890 |
| **Δ** | **+0.036** | **+0.039** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.842 | 1.000 | 0.727 |
| SAD-SAM | V24| 0.778 | 1.000 | 0.636 |
| SAD-CODE | TransArc | 0.405 | 0.822 | 0.268 |
| SAD-CODE | V24| 0.880 | 0.978 | 0.800 |

### Enrollment Debiasing

| Metric | TransArc | V24| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.831 | 0.867 | +0.036 |
| IDF-Weighted F1 | 0.860 | 0.829 | -0.031 |
| Component-Macro F1 | 0.863 | 0.902 | +0.039 |
| PDR F1 | 0.757 | 0.837 | +0.080 |

---

## Jabref

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V24| 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | **Δ (V24−T)** | +0.000 | +0.000 | **+0.000** | +0 | +0 | +0 |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V24| 0.893 | 1.000 | 0.944 | 8268 | 990 | 0 |
| SAD-CODE | **Δ (V24−T)** | +0.000 | +0.000 | **+0.000** | +0 | -4 | +0 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.933 | 0.983 |
| SAD-SAM | V24| 0.933 | 0.983 |
| SAD-SAM | **Δ** | **+0.000** | +0.000 |
| SAD-CODE | TransArc | 0.917 | 0.971 |
| SAD-CODE | V24| 0.917 | 0.971 |
| SAD-CODE | **Δ** | **+0.000** | +0.000 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | V24 | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-CODE | TransArc | 0.500 | 0.918 | 1.000 | 0.500 | 0.000 |
| SAD-CODE | V24 | 0.800 | 0.918 | 1.000 | 0.800 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.950 |
| SAD-SAM | V24| 0.950 |
| SAD-SAM | **Δ** | **+0.000** |
| SAD-CODE | TransArc | 0.935 |
| SAD-CODE | V24| 0.937 |
| SAD-CODE | **Δ** | **+0.002** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.943 | 0.857 | -0.086 |
| V24| 0.944 | 0.947 | +0.004 |
| **Δ (V24−T)** | **+0.000** | **+0.090** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.335 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | 0.915 |
| V24| 0.944 | 0.915 |
| **Δ** | **+0.000** | **+0.000** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.750 | 1.000 | 0.600 |
| SAD-SAM | V24| 0.750 | 1.000 | 0.600 |
| SAD-CODE | TransArc | 0.667 | 1.000 | 0.500 |
| SAD-CODE | V24| 0.889 | 1.000 | 0.800 |

### Enrollment Debiasing

| Metric | TransArc | V24| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.943 | 0.944 | +0.000 |
| IDF-Weighted F1 | 0.941 | 0.941 | +0.000 |
| Component-Macro F1 | 0.948 | 0.948 | +0.000 |
| PDR F1 | 0.943 | 0.943 | +0.000 |

---

## Cross-Project Summary

### SAD-SAM F1

| Project | TransArc | V24| Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.694 | 0.906 | +0.212 | V24 |
| teastore | 0.851 | 0.963 | +0.112 | V24 |
| teammates | 0.710 | 0.912 | +0.202 | V24 |
| bigbluebutton | 0.793 | 0.908 | +0.115 | V24 |
| jabref | 0.947 | 0.947 | +0.000 | Tie |
| **Average** | **0.799** | **0.927** | **+0.128** | **V24** |

### SAD-CODE F1

| Project | TransArc | V24| Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.588 | 0.848 | +0.260 | V24 |
| teastore | 0.829 | 0.983 | +0.153 | V24 |
| teammates | 0.821 | 0.829 | +0.008 | V24 |
| bigbluebutton | 0.831 | 0.867 | +0.036 | V24 |
| jabref | 0.943 | 0.944 | +0.000 | Tie |
| **Average** | **0.803** | **0.894** | **+0.092** | **V24** |

### All Metrics: Average Across Projects

| Metric | Level | TransArc | V24| Δ | Winner |
|:--|:--|:---:|:---:|:---:|:--|
| F1 | SAD-SAM | 0.799 | 0.927 | +0.128 | V24 |
| F1 | SAD-CODE | 0.803 | 0.894 | +0.092 | V24 |
| MCC | SAD-SAM | 0.801 | 0.923 | +0.122 | V24 |
| MCC | SAD-CODE | 0.802 | 0.885 | +0.083 | V24 |
| EMR | SAD-SAM | 0.682 | 0.876 | +0.194 | V24 |
| EMR | SAD-CODE | 0.464 | 0.763 | +0.299 | V24 |
| MAP | SAD-SAM | 0.746 | 0.946 | +0.200 | V24 |
| MAP | SAD-CODE | 0.697 | 0.860 | +0.163 | V24 |
| ACF1 | SAD-CODE | 0.684 | 0.871 | +0.187 | V24 |
| NDG | SAD-CODE | 0.803 | 0.909 | +0.106 | V24 |
| HUS | SAD-SAM | 0.718 | 0.745 | +0.027 | V24 |
| HUS | SAD-CODE | 0.649 | 0.846 | +0.197 | V24 |
| IDF F1 | SAD-CODE | 0.822 | 0.890 | +0.068 | V24 |
| Macro F1 | SAD-CODE | 0.807 | 0.902 | +0.096 | V24 |
| PDR F1 | SAD-CODE | 0.798 | 0.891 | +0.093 | V24 |

**Score: V24wins 15, TransArc wins 0, Ties 0** (across 15 metrics)

### Per-Project Wins (SAD-CODE metrics only)

| Project | TransArc Wins | V24Wins | Ties |
|:--|:---:|:---:|:---:|
| mediastore | 0 | 10 | 0 |
| teastore | 0 | 10 | 0 |
| teammates | 1 | 9 | 0 |
| bigbluebutton | 1 | 9 | 0 |
| jabref | 0 | 3 | 7 |
| **Total** | **2** | **41** | **7** |

---

## Key Findings

1. **SAD-SAM**: V24avg F1 = 0.927 vs TransArc 0.799 (Δ=+0.128)
2. **SAD-CODE** (standard): V24avg F1 = 0.894 vs TransArc 0.803 (Δ=+0.092)
3. **SAD-CODE** (debiased macro): V24= 0.902 vs TransArc 0.807 (Δ=+0.096)
4. **MCC SAD-SAM**: V24= 0.923 vs TransArc 0.801 (Δ=+0.122)

**SAD-SAM project wins**: V244/5, TransArc 0/5
**SAD-CODE project wins**: V244/5, TransArc 0/5

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 transarc_vs_v24_comparison.py
```

