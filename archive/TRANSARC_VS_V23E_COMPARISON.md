# TransArc vs V23e: Comprehensive Metric Comparison

Two-system comparison using our full metric suite at SAD-SAM and SAD-CODE levels.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)
- **V23e**: LLM linker with hybrid batch/union judge (SAD-SAM), projected through **gold SAM-CODE** for SAD-CODE

V23e is a SAD-SAM linker; its SAD-CODE result is composed transitively via gold SAM-CODE.
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
| SAD-SAM | V23e| 0.882 | 0.968 | 0.923 | 30 | 4 | 1 |
| SAD-SAM | **Δ (V23e−T)** | -0.062 | +0.419 | **+0.229** | +13 | +3 | -13 |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V23e| 0.814 | 0.966 | 0.884 | 57 | 13 | 2 |
| SAD-CODE | **Δ (V23e−T)** | -0.147 | +0.542 | **+0.295** | +32 | +12 | -32 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.711 | 0.773 |
| SAD-SAM | V23e| 0.920 | 0.981 |
| SAD-SAM | **Δ** | **+0.210** | +0.207 |
| SAD-CODE | TransArc | 0.633 | 0.712 |
| SAD-CODE | V23e| 0.884 | 0.980 |
| SAD-CODE | **Δ** | **+0.251** | +0.268 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.556 | 0.574 | 0.556 | 0.593 | 0.407 |
| SAD-SAM | V23e | 0.852 | 0.926 | 0.963 | 0.889 | 0.000 |
| SAD-CODE | TransArc | 0.600 | 0.613 | 0.600 | 0.640 | 0.360 |
| SAD-CODE | V23e | 0.840 | 0.907 | 0.960 | 0.880 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.574 |
| SAD-SAM | V23e| 0.926 |
| SAD-SAM | **Δ** | **+0.352** |
| SAD-CODE | TransArc | 0.613 |
| SAD-CODE | V23e| 0.899 |
| SAD-CODE | **Δ** | **+0.285** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.588 | 0.739 | +0.151 |
| V23e| 0.884 | 0.915 | +0.032 |
| **Δ (V23e−T)** | **+0.295** | **+0.176** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.148 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | 0.516 |
| V23e| 0.884 | 0.863 |
| **Δ** | **+0.295** | **+0.347** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.778 | 0.700 | 0.875 |
| SAD-SAM | V23e| 0.889 | 1.000 | 0.800 |
| SAD-CODE | TransArc | 0.762 | 0.640 | 0.941 |
| SAD-CODE | V23e| 0.917 | 1.000 | 0.846 |

### Enrollment Debiasing

| Metric | TransArc | V23e| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.588 | 0.884 | +0.295 |
| IDF-Weighted F1 | 0.657 | 0.895 | +0.238 |
| Component-Macro F1 | 0.661 | 0.920 | +0.260 |
| PDR F1 | 0.641 | 0.893 | +0.252 |

---

## Teastore

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V23e| 1.000 | 1.000 | 1.000 | 27 | 0 | 0 |
| SAD-SAM | **Δ (V23e−T)** | +0.000 | +0.259 | **+0.149** | +7 | +0 | -7 |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V23e| 1.000 | 1.000 | 1.000 | 707 | 0 | 0 |
| SAD-CODE | **Δ (V23e−T)** | +0.000 | +0.291 | **+0.171** | +206 | +0 | -206 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.857 | 0.870 |
| SAD-SAM | V23e| 1.000 | 1.000 |
| SAD-SAM | **Δ** | **+0.143** | +0.130 |
| SAD-CODE | TransArc | 0.828 | 0.854 |
| SAD-CODE | V23e| 1.000 | 1.000 |
| SAD-CODE | **Δ** | **+0.172** | +0.146 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-SAM | V23e | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| SAD-CODE | TransArc | 0.696 | 0.696 | 0.696 | 0.696 | 0.304 |
| SAD-CODE | V23e | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.696 |
| SAD-SAM | V23e| 1.000 |
| SAD-SAM | **Δ** | **+0.304** |
| SAD-CODE | TransArc | 0.696 |
| SAD-CODE | V23e| 1.000 |
| SAD-CODE | **Δ** | **+0.304** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.829 | 0.851 | +0.022 |
| V23e| 1.000 | 1.000 | +0.000 |
| **Δ (V23e−T)** | **+0.171** | **+0.149** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.120 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | 0.806 |
| V23e| 1.000 | 1.000 |
| **Δ** | **+0.171** | **+0.194** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 1.000 | 1.000 |
| SAD-SAM | V23e| 1.000 | 1.000 | 1.000 |
| SAD-CODE | TransArc | 0.821 | 0.696 | 1.000 |
| SAD-CODE | V23e| 1.000 | 1.000 | 1.000 |

### Enrollment Debiasing

| Metric | TransArc | V23e| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.829 | 1.000 | +0.171 |
| IDF-Weighted F1 | 0.836 | 1.000 | +0.164 |
| Component-Macro F1 | 0.839 | 1.000 | +0.161 |
| PDR F1 | 0.830 | 1.000 | +0.170 |

---

## Teammates

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V23e| 0.875 | 0.982 | 0.926 | 56 | 8 | 1 |
| SAD-SAM | **Δ (V23e−T)** | +0.270 | +0.123 | **+0.215** | +7 | -24 | -7 |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V23e| 0.939 | 0.801 | 0.865 | 6486 | 422 | 1611 |
| SAD-CODE | **Δ (V23e−T)** | +0.186 | -0.101 | **+0.043** | -821 | -1973 | +821 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.714 | 0.924 |
| SAD-SAM | V23e| 0.926 | 0.990 |
| SAD-SAM | **Δ** | **+0.211** | +0.066 |
| SAD-CODE | TransArc | 0.814 | 0.943 |
| SAD-CODE | V23e| 0.861 | 0.899 |
| SAD-CODE | **Δ** | **+0.047** | -0.044 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.756 | 0.800 | 0.822 | 0.778 | 0.133 |
| SAD-SAM | V23e | 0.933 | 0.956 | 0.978 | 0.933 | 0.022 |
| SAD-CODE | TransArc | 0.370 | 0.493 | 0.554 | 0.413 | 0.391 |
| SAD-CODE | V23e | 0.380 | 0.447 | 0.402 | 0.435 | 0.533 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.800 |
| SAD-SAM | V23e| 0.967 |
| SAD-SAM | **Δ** | **+0.167** |
| SAD-CODE | TransArc | 0.514 |
| SAD-CODE | V23e| 0.450 |
| SAD-CODE | **Δ** | **-0.064** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.821 | 0.624 | -0.197 |
| V23e| 0.865 | 0.642 | -0.222 |
| **Δ (V23e−T)** | **+0.043** | **+0.018** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.055 | Oracle F1: 0.881

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | 0.927 |
| V23e| 0.865 | 0.980 |
| **Δ** | **+0.043** | **+0.053** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.222 | 1.000 | 0.125 |
| SAD-SAM | V23e| 0.667 | 1.000 | 0.500 |
| SAD-CODE | TransArc | 0.591 | 0.598 | 0.585 |
| SAD-CODE | V23e| 0.603 | 0.467 | 0.851 |

### Enrollment Debiasing

| Metric | TransArc | V23e| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.821 | 0.865 | +0.043 |
| IDF-Weighted F1 | 0.817 | 0.864 | +0.047 |
| Component-Macro F1 | 0.723 | 0.791 | +0.069 |
| PDR F1 | 0.819 | 0.862 | +0.043 |

---

## Bigbluebutton

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V23e| 0.896 | 0.968 | 0.930 | 60 | 7 | 2 |
| SAD-SAM | **Δ (V23e−T)** | -0.002 | +0.258 | **+0.137** | +16 | +2 | -16 |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V23e| 0.874 | 0.990 | 0.928 | 1513 | 218 | 16 |
| SAD-CODE | **Δ (V23e−T)** | +0.054 | +0.148 | **+0.097** | +226 | -64 | -226 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.792 | 0.853 |
| SAD-SAM | V23e| 0.929 | 0.982 |
| SAD-SAM | **Δ** | **+0.136** | +0.128 |
| SAD-CODE | TransArc | 0.820 | 0.915 |
| SAD-CODE | V23e| 0.925 | 0.990 |
| SAD-CODE | **Δ** | **+0.106** | +0.075 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.604 | 0.712 | 0.646 | 0.750 | 0.188 |
| SAD-SAM | V23e | 0.854 | 0.925 | 0.958 | 0.875 | 0.021 |
| SAD-CODE | TransArc | 0.156 | 0.675 | 0.667 | 0.244 | 0.178 |
| SAD-CODE | V23e | 0.911 | 0.953 | 0.978 | 0.911 | 0.022 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.709 |
| SAD-SAM | V23e| 0.925 |
| SAD-SAM | **Δ** | **+0.215** |
| SAD-CODE | TransArc | 0.725 |
| SAD-CODE | V23e| 1.124 |
| SAD-CODE | **Δ** | **+0.398** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.831 | 0.347 | -0.484 |
| V23e| 0.928 | 0.934 | +0.005 |
| **Δ (V23e−T)** | **+0.097** | **+0.587** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.059 | Oracle F1: 0.968

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | 0.850 |
| V23e| 0.928 | 0.957 |
| **Δ** | **+0.097** | **+0.107** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.842 | 1.000 | 0.727 |
| SAD-SAM | V23e| 0.706 | 1.000 | 0.545 |
| SAD-CODE | TransArc | 0.405 | 0.822 | 0.268 |
| SAD-CODE | V23e| 0.912 | 0.978 | 0.854 |

### Enrollment Debiasing

| Metric | TransArc | V23e| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.831 | 0.928 | +0.097 |
| IDF-Weighted F1 | 0.860 | 0.921 | +0.062 |
| Component-Macro F1 | 0.863 | 0.933 | +0.070 |
| PDR F1 | 0.757 | 0.924 | +0.167 |

---

## Jabref

### Standard P/R/F1

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V23e| 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | **Δ (V23e−T)** | +0.000 | +0.000 | **+0.000** | +0 | +0 | +0 |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V23e| 0.893 | 1.000 | 0.944 | 8268 | 990 | 0 |
| SAD-CODE | **Δ (V23e−T)** | +0.000 | +0.000 | **+0.000** | +0 | -4 | +0 |

### N1: MCC (Matthews Correlation Coefficient)

| Level | System | MCC | Bal.Acc |
|:--|:--|:---:|:---:|
| SAD-SAM | TransArc | 0.933 | 0.983 |
| SAD-SAM | V23e| 0.933 | 0.983 |
| SAD-SAM | **Δ** | **+0.000** | +0.000 |
| SAD-CODE | TransArc | 0.917 | 0.971 |
| SAD-CODE | V23e| 0.917 | 0.971 |
| SAD-CODE | **Δ** | **+0.000** | +0.000 |

### N2: EMR (Exact Match Ratio)

| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-SAM | V23e | 0.800 | 0.900 | 1.000 | 0.800 | 0.000 |
| SAD-CODE | TransArc | 0.500 | 0.918 | 1.000 | 0.500 | 0.000 |
| SAD-CODE | V23e | 0.800 | 0.918 | 1.000 | 0.800 | 0.000 |

### N3: MAP (Mean Average Precision)

| Level | System | MAP |
|:--|:--|:---:|
| SAD-SAM | TransArc | 0.950 |
| SAD-SAM | V23e| 0.950 |
| SAD-SAM | **Δ** | **+0.000** |
| SAD-CODE | TransArc | 0.935 |
| SAD-CODE | V23e| 0.937 |
| SAD-CODE | **Δ** | **+0.002** |

### N4: ACF1 (Amplification-Corrected F1)

| System | Std F1 | ACF1 | Shift |
|:--|:---:|:---:|:---:|
| TransArc | 0.943 | 0.857 | -0.086 |
| V23e| 0.944 | 0.947 | +0.004 |
| **Δ (V23e−T)** | **+0.000** | **+0.090** | |

### N5: NDG (Normalized Difficulty Gap)

Random F1: 0.335 | Oracle F1: 1.000

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | 0.915 |
| V23e| 0.944 | 0.915 |
| **Δ** | **+0.000** | **+0.000** |

### N6: HUS (Holistic Usefulness Score)

| Level | System | HUS | Coverage | Purity |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.750 | 1.000 | 0.600 |
| SAD-SAM | V23e| 0.750 | 1.000 | 0.600 |
| SAD-CODE | TransArc | 0.667 | 1.000 | 0.500 |
| SAD-CODE | V23e| 0.889 | 1.000 | 0.800 |

### Enrollment Debiasing

| Metric | TransArc | V23e| Δ |
|:--|:---:|:---:|:---:|
| Standard F1 | 0.943 | 0.944 | +0.000 |
| IDF-Weighted F1 | 0.941 | 0.941 | +0.000 |
| Component-Macro F1 | 0.948 | 0.948 | +0.000 |
| PDR F1 | 0.943 | 0.943 | +0.000 |

---

## Cross-Project Summary

### SAD-SAM F1

| Project | TransArc | V23e| Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.694 | 0.923 | +0.229 | V23e |
| teastore | 0.851 | 1.000 | +0.149 | V23e |
| teammates | 0.710 | 0.926 | +0.215 | V23e |
| bigbluebutton | 0.793 | 0.930 | +0.137 | V23e |
| jabref | 0.947 | 0.947 | +0.000 | Tie |
| **Average** | **0.799** | **0.945** | **+0.146** | **V23e** |

### SAD-CODE F1

| Project | TransArc | V23e| Δ | Winner |
|:--|:---:|:---:|:---:|:--|
| mediastore | 0.588 | 0.884 | +0.295 | V23e |
| teastore | 0.829 | 1.000 | +0.171 | V23e |
| teammates | 0.821 | 0.865 | +0.043 | V23e |
| bigbluebutton | 0.831 | 0.928 | +0.097 | V23e |
| jabref | 0.943 | 0.944 | +0.000 | Tie |
| **Average** | **0.803** | **0.924** | **+0.121** | **V23e** |

### All Metrics: Average Across Projects

| Metric | Level | TransArc | V23e| Δ | Winner |
|:--|:--|:---:|:---:|:---:|:--|
| F1 | SAD-SAM | 0.799 | 0.945 | +0.146 | V23e |
| F1 | SAD-CODE | 0.803 | 0.924 | +0.121 | V23e |
| MCC | SAD-SAM | 0.801 | 0.941 | +0.140 | V23e |
| MCC | SAD-CODE | 0.802 | 0.917 | +0.115 | V23e |
| EMR | SAD-SAM | 0.682 | 0.888 | +0.206 | V23e |
| EMR | SAD-CODE | 0.464 | 0.786 | +0.322 | V23e |
| MAP | SAD-SAM | 0.746 | 0.953 | +0.208 | V23e |
| MAP | SAD-CODE | 0.697 | 0.882 | +0.185 | V23e |
| ACF1 | SAD-CODE | 0.684 | 0.888 | +0.204 | V23e |
| NDG | SAD-CODE | 0.803 | 0.943 | +0.140 | V23e |
| HUS | SAD-SAM | 0.718 | 0.802 | +0.084 | V23e |
| HUS | SAD-CODE | 0.649 | 0.864 | +0.215 | V23e |
| IDF F1 | SAD-CODE | 0.822 | 0.924 | +0.102 | V23e |
| Macro F1 | SAD-CODE | 0.807 | 0.919 | +0.112 | V23e |
| PDR F1 | SAD-CODE | 0.798 | 0.925 | +0.127 | V23e |

**Score: V23ewins 15, TransArc wins 0, Ties 0** (across 15 metrics)

### Per-Project Wins (SAD-CODE metrics only)

| Project | TransArc Wins | V23eWins | Ties |
|:--|:---:|:---:|:---:|
| mediastore | 0 | 10 | 0 |
| teastore | 0 | 10 | 0 |
| teammates | 1 | 9 | 0 |
| bigbluebutton | 0 | 10 | 0 |
| jabref | 0 | 3 | 7 |
| **Total** | **1** | **42** | **7** |

---

## Key Findings

1. **SAD-SAM**: V23eavg F1 = 0.945 vs TransArc 0.799 (Δ=+0.146)
2. **SAD-CODE** (standard): V23eavg F1 = 0.924 vs TransArc 0.803 (Δ=+0.121)
3. **SAD-CODE** (debiased macro): V23e= 0.919 vs TransArc 0.807 (Δ=+0.112)
4. **MCC SAD-SAM**: V23e= 0.941 vs TransArc 0.801 (Δ=+0.140)

**SAD-SAM project wins**: V23e4/5, TransArc 0/5
**SAD-CODE project wins**: V23e4/5, TransArc 0/5

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 transarc_vs_v23e_comparison.py
```

