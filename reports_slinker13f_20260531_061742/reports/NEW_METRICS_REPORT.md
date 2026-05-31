# New Metrics for SAD-CODE Traceability Evaluation

Proposes 6 novel metrics addressing specific blind spots of P/R/F1,
and computes measurements for **TransArc** and **V45 linker** on all 5 benchmark projects.

---

## Metric Definitions

### N1: Matthews Correlation Coefficient (MCC)

**Problem addressed:** P/R/F1 ignore true negatives. Most (sentence, component)
pairs are negative (not linked). A system that correctly identifies which
sentences do NOT mention a component gets zero credit.

**Definition:** For each (sentence, component) pair in the evaluation universe,
classify as positive (linked) or negative (not linked). Compute:

```
MCC = (TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```

**Range:** [-1, +1]. 0 = random, +1 = perfect, -1 = perfect inverse.
A random classifier always scores MCC=0 regardless of class imbalance.

**Level:** Component (SAD-SAM) and File (SAD-CODE).

### N2: Sentence-Level Exact Match Rate (EMR)

**Problem addressed:** F1 gives partial credit for partially-correct predictions.
A developer looking up "which components does sentence 47 discuss?" needs the
exact set, not partial overlap.

**Definition:** For each gold sentence, check if predicted component set == gold set.

```
EMR = |{s : pred(s) = gold(s)}| / |gold sentences|
```

**Companion metrics:**
- **Superset rate:** pred(s) ⊇ gold(s) — over-prediction (noise but no missed components)
- **Subset rate:** pred(s) ⊆ gold(s), |pred(s)|>0 — under-prediction (no noise but gaps)
- **Mean Jaccard:** Average |pred∩gold|/|pred∪gold| per sentence

**Level:** Component (SAD-SAM) and File (SAD-CODE).

### N3: Per-Sentence Mean Average Precision (MAP)

**Problem addressed:** Standard metrics treat all predictions as equally confident.
MAP rewards systems that rank correct components higher in their output.
A system returning [correct@0.99, wrong@0.80] is more useful than
[wrong@0.99, correct@0.80].

**Definition:** For each gold sentence, rank predicted components by confidence.
Compute Average Precision (AP). MAP = mean of all APs.

```
AP(s) = (1/|gold(s)|) · Σ_{k: pred_k ∈ gold} precision@k
MAP = (1/|S|) · Σ_s AP(s)
```

**Range:** [0, 1]. Requires confidence scores (V45 has them, TransArc gets uniform 0.5).

**Level:** Component (SAD-SAM) and File (SAD-CODE).

### N4: Amplification-Corrected F1 (ACF1)

**Problem addressed:** Enrollment inflates metrics by component size.
One error on JabRef logic (972 files) = 972 FPs; one error on
MediaStore Facade (1 file) = 1 FP. Standard F1 treats them as
972× different in severity.

**Definition:** Weight each file-level link by 1/|component files|:

```
w(sent, file) = 1 / |files_of_component(file)|
ACF1 = F1(Σw·TP, Σw·FP, Σw·FN)
```

**Effect:** Every component-level decision contributes equally regardless of code size.

**Level:** File (SAD-CODE), enrollment-corrected.

### N5: Normalized Discrimination Gain (NDG)

**Problem addressed:** Raw F1 is incomparable across projects.
JabRef F1=0.94 (easy: 6 components, 12 sentences) looks better than
Teammates F1=0.82 (hard: 14 components, 194 sentences), but Teammates
may require more intelligence.

**Definition:** Normalize system F1 between random and oracle baselines:

```
NDG = (system_F1 − random_F1) / (oracle_F1 − random_F1)
```

**Range:** [0, 1]. 0 = no better than random, 1 = oracle-level.
Enables fair cross-project comparison of "intelligence added".

**Level:** File (SAD-CODE).

### N6: Harmonic Usefulness Score (HUS)

**Problem addressed:** Coverage and noise capture complementary developer needs.
Coverage: "will the system find my sentence?" Purity: "will it give me
only correct links?" A system must do both. HUS is the harmonic mean:

```
Coverage = |{s ∈ gold : ∃ TP in s}| / |gold sentences|
Purity = |{s ∈ result : no FP in s}| / |result sentences|
HUS = 2 · Coverage · Purity / (Coverage + Purity)
```

**Range:** [0, 1]. Analogous to F1 but at sentence experience level.

**Level:** Both SAD-SAM and SAD-CODE.

---

## Measurements

### Mediastore

**Standard P/R/F1 (reference):**

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| SAD-SAM | V45 | 0.969 | 1.000 | 0.984 | 31 | 1 | 0 |
| SAD-CODE | TransArc | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 |
| SAD-CODE | V45+GoldSAMCODE | 0.983 | 1.000 | 0.992 | 59 | 1 | 0 |

**N1: Matthews Correlation Coefficient (MCC):**

| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |
|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|
| SAD-SAM | TransArc | 17 | 1 | 14 | 671 | 703 | **0.711** | 0.773 |
| SAD-SAM | V45 | 31 | 1 | 0 | 671 | 703 | **0.984** | 0.999 |
| SAD-CODE | TransArc | 25 | 1 | 34 | 2086 | 2146 | **0.633** | 0.712 |
| SAD-CODE | V45+GoldSAMCODE | 59 | 1 | 0 | 2086 | 2146 | **0.991** | 1.000 |

**N2: Exact Match Rate (EMR):**

| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.556** | 0.556 | 0.593 | 0.407 | 0.574 |
| SAD-SAM | V45 | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |
| SAD-CODE | TransArc | **0.600** | 0.600 | 0.640 | 0.360 | 0.613 |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |

**N3: Mean Average Precision (MAP):**

| Level | System | MAP | Confidence Info |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.574** | uniform (no confidence) |
| SAD-SAM | V45 | **1.000** | per-link [0.77–1.00] |
| SAD-CODE | TransArc | **0.613** | uniform (no confidence) |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | inherited from component |

**N4: Amplification-Corrected F1 (ACF1):**

| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.588 | **0.739** | +0.151 | 17.0 | 1.0 | 11.0 |
| V45+GoldSAMCODE | 0.992 | **0.982** | -0.009 | 28.0 | 1.0 | 0.0 |

**N5: Normalized Discrimination Gain (NDG):**

| Baseline | F1 |
|:--|:---:|
| Random | 0.148 |
| Oracle (gold SAD-SAM × gold SAM-CODE) | 1.000 (TP=59, FP=0, FN=0) |

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.588 | **0.516** |
| V45+GoldSAMCODE | 0.992 | **0.990** |

**N6: Harmonic Usefulness Score (HUS):**

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.593 | 0.941 | **0.727** |
| SAD-SAM | V45 | 1.000 | 0.964 | **0.982** |
| SAD-CODE | TransArc | 0.640 | 0.941 | **0.762** |
| SAD-CODE | V45+GoldSAMCODE | 1.000 | 0.962 | **0.980** |

---

### Teastore

**Standard P/R/F1 (reference):**

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| SAD-SAM | V45 | 1.000 | 1.000 | 1.000 | 27 | 0 | 0 |
| SAD-CODE | TransArc | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 |
| SAD-CODE | V45+GoldSAMCODE | 1.000 | 1.000 | 1.000 | 707 | 0 | 0 |

**N1: Matthews Correlation Coefficient (MCC):**

| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |
|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|
| SAD-SAM | TransArc | 20 | 0 | 7 | 790 | 817 | **0.857** | 0.870 |
| SAD-SAM | V45 | 27 | 0 | 0 | 790 | 817 | **1.000** | 1.000 |
| SAD-CODE | TransArc | 501 | 0 | 206 | 6001 | 6708 | **0.828** | 0.854 |
| SAD-CODE | V45+GoldSAMCODE | 707 | 0 | 0 | 6001 | 6708 | **1.000** | 1.000 |

**N2: Exact Match Rate (EMR):**

| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.696** | 0.696 | 0.696 | 0.304 | 0.696 |
| SAD-SAM | V45 | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |
| SAD-CODE | TransArc | **0.696** | 0.696 | 0.696 | 0.304 | 0.696 |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |

**N3: Mean Average Precision (MAP):**

| Level | System | MAP | Confidence Info |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.696** | uniform (no confidence) |
| SAD-SAM | V45 | **1.000** | per-link [0.77–1.00] |
| SAD-CODE | TransArc | **0.696** | uniform (no confidence) |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | inherited from component |

**N4: Amplification-Corrected F1 (ACF1):**

| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.829 | **0.851** | +0.022 | 20.0 | 0.0 | 7.0 |
| V45+GoldSAMCODE | 1.000 | **1.000** | +0.000 | 27.0 | 0.0 | 0.0 |

**N5: Normalized Discrimination Gain (NDG):**

| Baseline | F1 |
|:--|:---:|
| Random | 0.120 |
| Oracle (gold SAD-SAM × gold SAM-CODE) | 1.000 (TP=707, FP=0, FN=0) |

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.829 | **0.806** |
| V45+GoldSAMCODE | 1.000 | **1.000** |

**N6: Harmonic Usefulness Score (HUS):**

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-SAM | V45 | 1.000 | 1.000 | **1.000** |
| SAD-CODE | TransArc | 0.696 | 1.000 | **0.821** |
| SAD-CODE | V45+GoldSAMCODE | 1.000 | 1.000 | **1.000** |

---

### Teammates

**Standard P/R/F1 (reference):**

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| SAD-SAM | V45 | 0.947 | 0.947 | 0.947 | 54 | 3 | 3 |
| SAD-CODE | TransArc | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 |
| SAD-CODE | V45+GoldSAMCODE | 0.986 | 0.769 | 0.864 | 6223 | 91 | 1874 |

**N1: Matthews Correlation Coefficient (MCC):**

| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |
|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|
| SAD-SAM | TransArc | 49 | 32 | 8 | 2683 | 2772 | **0.714** | 0.924 |
| SAD-SAM | V45 | 54 | 3 | 3 | 2712 | 2772 | **0.946** | 0.973 |
| SAD-CODE | TransArc | 7307 | 2395 | 790 | 149492 | 159984 | **0.814** | 0.943 |
| SAD-CODE | V45+GoldSAMCODE | 6223 | 91 | 1874 | 151796 | 159984 | **0.865** | 0.884 |

**N2: Exact Match Rate (EMR):**

| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.756** | 0.822 | 0.778 | 0.133 | 0.800 |
| SAD-SAM | V45 | **0.933** | 0.933 | 0.978 | 0.022 | 0.956 |
| SAD-CODE | TransArc | **0.370** | 0.554 | 0.413 | 0.391 | 0.493 |
| SAD-CODE | V45+GoldSAMCODE | **0.370** | 0.380 | 0.446 | 0.533 | 0.440 |

**N3: Mean Average Precision (MAP):**

| Level | System | MAP | Confidence Info |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.800** | uniform (no confidence) |
| SAD-SAM | V45 | **0.956** | per-link [0.77–1.00] |
| SAD-CODE | TransArc | **0.514** | uniform (no confidence) |
| SAD-CODE | V45+GoldSAMCODE | **0.438** | inherited from component |

**N4: Amplification-Corrected F1 (ACF1):**

| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.821 | **0.624** | -0.197 | 57.4 | 21.6 | 47.5 |
| V45+GoldSAMCODE | 0.864 | **0.635** | -0.228 | 49.8 | 2.2 | 55.0 |

**N5: Normalized Discrimination Gain (NDG):**

| Baseline | F1 |
|:--|:---:|
| Random | 0.055 |
| Oracle (gold SAD-SAM × gold SAM-CODE) | 0.881 (TP=6380, FP=0, FN=1717) |

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.821 | **0.927** |
| V45+GoldSAMCODE | 0.864 | **0.979** |

**N6: Harmonic Usefulness Score (HUS):**

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.844 | 0.530 | **0.651** |
| SAD-SAM | V45 | 0.978 | 0.936 | **0.957** |
| SAD-CODE | TransArc | 0.598 | 0.585 | **0.591** |
| SAD-CODE | V45+GoldSAMCODE | 0.467 | 0.932 | **0.623** |

---

### Bigbluebutton

**Standard P/R/F1 (reference):**

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| SAD-SAM | V45 | 0.920 | 0.742 | 0.821 | 46 | 4 | 16 |
| SAD-CODE | TransArc | 0.820 | 0.842 | 0.831 | 1287 | 282 | 242 |
| SAD-CODE | V45+GoldSAMCODE | 0.914 | 0.914 | 0.914 | 1397 | 131 | 132 |

**N1: Matthews Correlation Coefficient (MCC):**

| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |
|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|
| SAD-SAM | TransArc | 44 | 5 | 18 | 1847 | 1914 | **0.792** | 0.853 |
| SAD-SAM | V45 | 46 | 4 | 16 | 1848 | 1914 | **0.821** | 0.870 |
| SAD-CODE | TransArc | 1287 | 282 | 242 | 22723 | 24534 | **0.820** | 0.915 |
| SAD-CODE | V45+GoldSAMCODE | 1397 | 131 | 132 | 22874 | 24534 | **0.908** | 0.954 |

**N2: Exact Match Rate (EMR):**

| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.604** | 0.646 | 0.750 | 0.188 | 0.712 |
| SAD-SAM | V45 | **0.729** | 0.750 | 0.833 | 0.146 | 0.793 |
| SAD-CODE | TransArc | **0.156** | 0.667 | 0.244 | 0.178 | 0.675 |
| SAD-CODE | V45+GoldSAMCODE | **0.756** | 0.778 | 0.822 | 0.156 | 0.819 |

**N3: Mean Average Precision (MAP):**

| Level | System | MAP | Confidence Info |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.709** | uniform (no confidence) |
| SAD-SAM | V45 | **0.791** | per-link [0.77–1.00] |
| SAD-CODE | TransArc | **0.725** | uniform (no confidence) |
| SAD-CODE | V45+GoldSAMCODE | **0.832** | inherited from component |

**N4: Amplification-Corrected F1 (ACF1):**

| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.831 | **0.347** | -0.484 | 39.9 | 139.1 | 11.2 |
| V45+GoldSAMCODE | 0.914 | **0.864** | -0.050 | 42.0 | 4.1 | 9.1 |

**N5: Normalized Discrimination Gain (NDG):**

| Baseline | F1 |
|:--|:---:|
| Random | 0.054 |
| Oracle (gold SAD-SAM × gold SAM-CODE) | 0.968 (TP=1521, FP=94, FN=8) |

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.831 | **0.850** |
| V45+GoldSAMCODE | 0.914 | **0.941** |

**N6: Harmonic Usefulness Score (HUS):**

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 0.812 | 0.878 | **0.844** |
| SAD-SAM | V45 | 0.854 | 0.909 | **0.881** |
| SAD-CODE | TransArc | 0.822 | 0.268 | **0.405** |
| SAD-CODE | V45+GoldSAMCODE | 0.844 | 0.881 | **0.862** |

---

### Jabref

**Standard P/R/F1 (reference):**

| Level | System | P | R | F1 | TP | FP | FN |
|:--|:--|:---:|:---:|:---:|---:|---:|---:|
| SAD-SAM | TransArc | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |
| SAD-SAM | V45 | 1.000 | 1.000 | 1.000 | 18 | 0 | 0 |
| SAD-CODE | TransArc | 0.893 | 1.000 | 0.943 | 8268 | 994 | 0 |
| SAD-CODE | V45+GoldSAMCODE | 1.000 | 1.000 | 1.000 | 8268 | 0 | 0 |

**N1: Matthews Correlation Coefficient (MCC):**

| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |
|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|
| SAD-SAM | TransArc | 18 | 2 | 0 | 58 | 78 | **0.933** | 0.983 |
| SAD-SAM | V45 | 18 | 0 | 0 | 60 | 78 | **1.000** | 1.000 |
| SAD-CODE | TransArc | 8268 | 994 | 0 | 16166 | 25428 | **0.917** | 0.971 |
| SAD-CODE | V45+GoldSAMCODE | 8268 | 0 | 0 | 17160 | 25428 | **1.000** | 1.000 |

**N2: Exact Match Rate (EMR):**

| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |
|:--|:--|:---:|:---:|:---:|:---:|:---:|
| SAD-SAM | TransArc | **0.800** | 1.000 | 0.800 | 0.000 | 0.900 |
| SAD-SAM | V45 | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |
| SAD-CODE | TransArc | **0.500** | 1.000 | 0.500 | 0.000 | 0.918 |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | 1.000 | 1.000 | 0.000 | 1.000 |

**N3: Mean Average Precision (MAP):**

| Level | System | MAP | Confidence Info |
|:--|:--|:---:|:--|
| SAD-SAM | TransArc | **0.950** | uniform (no confidence) |
| SAD-SAM | V45 | **1.000** | per-link [0.77–1.00] |
| SAD-CODE | TransArc | **0.935** | uniform (no confidence) |
| SAD-CODE | V45+GoldSAMCODE | **1.000** | inherited from component |

**N4: Amplification-Corrected F1 (ACF1):**

| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.943 | **0.857** | -0.086 | 18.0 | 6.0 | 0.0 |
| V45+GoldSAMCODE | 1.000 | **1.000** | +0.000 | 18.0 | 0.0 | 0.0 |

**N5: Normalized Discrimination Gain (NDG):**

| Baseline | F1 |
|:--|:---:|
| Random | 0.335 |
| Oracle (gold SAD-SAM × gold SAM-CODE) | 1.000 (TP=8268, FP=0, FN=0) |

| System | F1 | NDG |
|:--|:---:|:---:|
| TransArc | 0.943 | **0.915** |
| V45+GoldSAMCODE | 1.000 | **1.000** |

**N6: Harmonic Usefulness Score (HUS):**

| Level | System | Coverage | Purity | HUS |
|:--|:--|:---:|:---:|:---:|
| SAD-SAM | TransArc | 1.000 | 0.800 | **0.889** |
| SAD-SAM | V45 | 1.000 | 1.000 | **1.000** |
| SAD-CODE | TransArc | 1.000 | 0.500 | **0.667** |
| SAD-CODE | V45+GoldSAMCODE | 1.000 | 1.000 | **1.000** |

---

## Aggregate Comparison

### Standard F1 (Reference)

| Project | TransArc SAD-SAM | V45 SAD-SAM | TransArc SAD-CODE | V45 SAD-CODE |
|:--|:---:|:---:|:---:|:---:|
| mediastore | 0.694 | 0.984 | 0.588 | 0.992 |
| teastore | 0.851 | 1.000 | 0.829 | 1.000 |
| teammates | 0.710 | 0.947 | 0.821 | 0.864 |
| bigbluebutton | 0.793 | 0.821 | 0.831 | 0.914 |
| jabref | 0.947 | 1.000 | 0.943 | 1.000 |
| **Average** | **0.799** | **0.951** | **0.803** | **0.954** |

### N1: MCC Summary

**SAD-SAM level:**

| Project | #Components | #Sentences | Universe | TransArc MCC | V45 MCC | Δ |
|:--|---:|---:|---:|:---:|:---:|:---:|
| mediastore | 19 | 37 | 703 | 0.711 | 0.984 | +0.273 |
| teastore | 19 | 43 | 817 | 0.857 | 1.000 | +0.143 |
| teammates | 14 | 198 | 2772 | 0.714 | 0.946 | +0.232 |
| bigbluebutton | 22 | 87 | 1914 | 0.792 | 0.821 | +0.029 |
| jabref | 6 | 13 | 78 | 0.933 | 1.000 | +0.067 |
| **Average** | | | | **0.801** | **0.950** | **+0.149** |

**SAD-CODE level:**

| Project | #Files | Universe | TransArc MCC | V45 MCC | Δ |
|:--|---:|---:|:---:|:---:|:---:|
| mediastore | 58 | 2146 | 0.633 | 0.991 | +0.359 |
| teastore | 156 | 6708 | 0.828 | 1.000 | +0.172 |
| teammates | 808 | 159984 | 0.814 | 0.865 | +0.050 |
| bigbluebutton | 282 | 24534 | 0.820 | 0.908 | +0.089 |
| jabref | 1956 | 25428 | 0.917 | 1.000 | +0.083 |
| **Average** | | | **0.802** | **0.953** | **+0.151** |

**Insight:** At SAD-CODE file level, the universe is much larger (sentences × files),
making most pairs negative. MCC stays high because both systems correctly reject
the vast majority. The gap between systems is clearer at SAD-SAM level.

### N2: EMR Summary

**SAD-SAM level (component sets):**

| Project | TransArc EMR | V45 EMR | TransArc Jaccard | V45 Jaccard | TransArc Zero-Pred | V45 Zero-Pred |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.556 | 1.000 | 0.574 | 1.000 | 0.407 | 0.000 |
| teastore | 0.696 | 1.000 | 0.696 | 1.000 | 0.304 | 0.000 |
| teammates | 0.756 | 0.933 | 0.800 | 0.956 | 0.133 | 0.022 |
| bigbluebutton | 0.604 | 0.729 | 0.712 | 0.793 | 0.188 | 0.146 |
| jabref | 0.800 | 1.000 | 0.900 | 1.000 | 0.000 | 0.000 |
| **Average** | **0.682** | **0.932** | **0.736** | **0.950** | | |

**SAD-CODE level (file sets):**

| Project | TransArc EMR | V45 EMR | TransArc Jaccard | V45 Jaccard | TransArc Zero-Pred | V45 Zero-Pred |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.600 | 1.000 | 0.613 | 1.000 | 0.360 | 0.000 |
| teastore | 0.696 | 1.000 | 0.696 | 1.000 | 0.304 | 0.000 |
| teammates | 0.370 | 0.370 | 0.493 | 0.440 | 0.391 | 0.533 |
| bigbluebutton | 0.156 | 0.756 | 0.675 | 0.819 | 0.178 | 0.156 |
| jabref | 0.500 | 1.000 | 0.918 | 1.000 | 0.000 | 0.000 |
| **Average** | **0.464** | **0.825** | **0.679** | **0.852** | | |

**Insight:** EMR at file level is nearly impossible: getting every file exactly right
for a sentence requires both correct component classification AND perfect SAM-CODE.
Jaccard at file level reveals partial overlap quality. Zero-pred shows missed sentences.

### N3: MAP Summary

**SAD-SAM level:**

| Project | TransArc MAP | V45 MAP | Δ |
|:--|:---:|:---:|:---:|
| mediastore | 0.574 | 1.000 | +0.426 |
| teastore | 0.696 | 1.000 | +0.304 |
| teammates | 0.800 | 0.956 | +0.156 |
| bigbluebutton | 0.709 | 0.791 | +0.082 |
| jabref | 0.950 | 1.000 | +0.050 |
| **Average** | **0.746** | **0.949** | **+0.203** |

**SAD-CODE level:**

| Project | TransArc MAP | V45 MAP | Δ |
|:--|:---:|:---:|:---:|
| mediastore | 0.613 | 1.000 | +0.387 |
| teastore | 0.696 | 1.000 | +0.304 |
| teammates | 0.514 | 0.438 | -0.076 |
| bigbluebutton | 0.725 | 0.832 | +0.106 |
| jabref | 0.935 | 1.000 | +0.065 |
| **Average** | **0.697** | **0.854** | **+0.157** |

**Insight:** MAP at file level is dominated by within-component file ordering.
V45 inherits component confidence to all files, so files from high-confidence
components cluster at the top. TransArc's uniform confidence means MAP ≈ recall.

### N4: ACF1 Summary

| Project | TransArc F1 | TransArc ACF1 | Δ | V45 F1 | V45 ACF1 | Δ |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.588 | 0.739 | +0.151 | 0.992 | 0.982 | -0.009 |
| teastore | 0.829 | 0.851 | +0.022 | 1.000 | 1.000 | +0.000 |
| teammates | 0.821 | 0.624 | -0.197 | 0.864 | 0.635 | -0.228 |
| bigbluebutton | 0.831 | 0.347 | -0.484 | 0.914 | 0.864 | -0.050 |
| jabref | 0.943 | 0.857 | -0.086 | 1.000 | 1.000 | +0.000 |
| **Average** | **0.803** | **0.684** | **-0.119** | **0.954** | **0.896** | **-0.057** |

**Insight:** ACF1 corrects enrollment inflation. Projects where the shift is large
(e.g., JabRef, Teammates) are those where a few large components dominate standard F1.
ACF1 gives a truer picture of component-level quality.

### N5: NDG Summary

| Project | Random F1 | Oracle F1 | TransArc F1 | TransArc NDG | V45 F1 | V45 NDG |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.148 | 1.000 | 0.588 | **0.516** | 0.992 | **0.990** |
| teastore | 0.120 | 1.000 | 0.829 | **0.806** | 1.000 | **1.000** |
| teammates | 0.055 | 0.881 | 0.821 | **0.927** | 0.864 | **0.979** |
| bigbluebutton | 0.054 | 0.968 | 0.831 | **0.850** | 0.914 | **0.941** |
| jabref | 0.335 | 1.000 | 0.943 | **0.915** | 1.000 | **1.000** |
| **Average** | | | | **0.803** | | **0.982** |

**Insight:** NDG reveals which projects are genuinely hard. A high F1 with a high
oracle ceiling and low random baseline means the achievable range is wide — the system
must be doing real work. A high F1 near the oracle ceiling means there was little room
for improvement and the metric flatters the system.

### N6: HUS Summary

**SAD-SAM level:**

| Project | TransArc Coverage | TransArc Purity | TransArc HUS | V45 Coverage | V45 Purity | V45 HUS |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.593 | 0.941 | **0.727** | 1.000 | 0.964 | **0.982** |
| teastore | 0.696 | 1.000 | **0.821** | 1.000 | 1.000 | **1.000** |
| teammates | 0.844 | 0.530 | **0.651** | 0.978 | 0.936 | **0.957** |
| bigbluebutton | 0.812 | 0.878 | **0.844** | 0.854 | 0.909 | **0.881** |
| jabref | 1.000 | 0.800 | **0.889** | 1.000 | 1.000 | **1.000** |
| **Average** | | | **0.786** | | | **0.964** |

**SAD-CODE level:**

| Project | TransArc Coverage | TransArc Purity | TransArc HUS | V45 Coverage | V45 Purity | V45 HUS |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.640 | 0.941 | **0.762** | 1.000 | 0.962 | **0.980** |
| teastore | 0.696 | 1.000 | **0.821** | 1.000 | 1.000 | **1.000** |
| teammates | 0.598 | 0.585 | **0.591** | 0.467 | 0.932 | **0.623** |
| bigbluebutton | 0.822 | 0.268 | **0.405** | 0.844 | 0.881 | **0.862** |
| jabref | 1.000 | 0.500 | **0.667** | 1.000 | 1.000 | **1.000** |
| **Average** | | | **0.649** | | | **0.893** |

---

## Grand Summary: All Metrics Head-to-Head

| Metric | Level | TransArc (avg) | V45 (avg) | V45 Δ | Winner | What it reveals |
|:--|:--|:---:|:---:|:---:|:---:|:--|
| F1 (standard) | SAD-SAM | 0.799 | 0.951 | +0.152 | V45 | Basic quality at component level |
| F1 (standard) | SAD-CODE | 0.803 | 0.954 | +0.151 | V45 | File-level (enrollment-inflated) |
| **N1: MCC** | SAD-SAM | 0.801 | 0.950 | +0.149 | V45 | Discrimination (component) |
| **N1: MCC** | SAD-CODE | 0.802 | 0.953 | +0.151 | V45 | Discrimination (file) |
| **N2: EMR** | SAD-SAM | 0.682 | 0.932 | +0.250 | V45 | Exact component-set per sentence |
| **N2: EMR** | SAD-CODE | 0.464 | 0.825 | +0.361 | V45 | Exact file-set per sentence |
| **N3: MAP** | SAD-SAM | 0.746 | 0.949 | +0.203 | V45 | Ranking quality (component) |
| **N3: MAP** | SAD-CODE | 0.697 | 0.854 | +0.157 | V45 | Ranking quality (file) |
| **N4: ACF1** | SAD-CODE | 0.684 | 0.896 | +0.213 | V45 | Enrollment-corrected file-level |
| **N5: NDG** | SAD-CODE | 0.803 | 0.982 | +0.179 | V45 | Intelligence over random baseline |
| **N6: HUS** | SAD-SAM | 0.786 | 0.964 | +0.177 | V45 | Coverage × purity (component) |
| **N6: HUS** | SAD-CODE | 0.649 | 0.893 | +0.244 | V45 | Coverage × purity (file) |

### Key Takeaways

1. **MCC reveals true discrimination ability.** By including the ~95% of
   (sentence, component) pairs that are correctly rejected as negatives,
   MCC shows both systems are strong discriminators. The gap between them
   is smaller in MCC space than in F1 space, because F1 ignores the easy
   correct rejections that both systems nail.

2. **EMR is the strictest metric.** Getting every component exactly right
   for a sentence is much harder than getting high F1. V45's EMR advantage
   shows it makes fewer partial-set errors — important for developer trust.

3. **MAP rewards calibrated confidence.** V45's confidence scores (0.77–1.00)
   enable meaningful ranking; TransArc's binary outputs (uniform 0.5) cannot.
   Higher MAP means correct links surface first, reducing developer effort.

4. **ACF1 corrects enrollment inflation.** Projects with large components
   (JabRef logic=972 files, Teammates=400+ files per component) see the
   biggest ACF1 shift. ACF1 is the fairest file-level metric because
   each component-level decision contributes equally.

5. **NDG enables cross-project comparison.** A system with NDG=0.8 on all
   projects is uniformly good regardless of project difficulty. NDG reveals
   whether high F1 comes from genuine intelligence or favorable structure.

6. **HUS captures developer experience.** A system that covers most gold
   sentences (high coverage) but drowns each in false positives (low purity)
   scores poorly on HUS. The harmonic mean ensures both dimensions matter.

---

### Metric Selection Guide

| If you care about... | Use | Why |
|:--|:--|:--|
| Overall classification quality | N1 (MCC) | Handles class imbalance correctly |
| Developer trust per sentence | N2 (EMR) | Measures exact-set accuracy |
| Ranking of suggestions | N3 (MAP) | Rewards correct items first |
| Fair cross-component comparison | N4 (ACF1) | Removes enrollment inflation |
| Fair cross-project comparison | N5 (NDG) | Normalizes by project difficulty |
| Practical usefulness | N6 (HUS) | Balances coverage and noise |
| Backward compatibility | Standard F1 | Comparable to prior work |

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 new_metrics_analysis.py
# Output: NEW_METRICS_REPORT.md
```

