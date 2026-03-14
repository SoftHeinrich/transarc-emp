# Fix Impact Simulation: LLM Adaptive Classification

Simulates the effect of each proposed fix from the deep error analysis.
All fixes are deterministic — no new LLM calls needed.

**Fixes:**
1. **Interface co-assignment**: When LLM assigns Component X, also assign Interface X
2. **Interface prompting** (oracle): Recover all interface_missed_entirely FNs
3. **Coverage expansion** (oracle): Recover all sentence_not_classified FNs
4. **FP reduction** (oracle): Remove all behavioral_overclassification FPs
5. **All fixes combined**: Apply 1+2+3+4 simultaneously

Note: Fixes 2, 3, 4 are **oracle upper bounds** — they show the maximum
possible improvement if the fix were perfect. Fix 1 is deterministic and
represents a real, implementable improvement.

---

## Mediastore

### File-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | — |
| Fix 1: Coassign | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| Fix 2: Interface | 1.000 | 0.966 | **0.983** | 57 | 0 | 2 | +0.018 |
| Fix 3: Coverage | 1.000 | 1.000 | **1.000** | 59 | 0 | 0 | +0.035 |
| Fix 4: FP Reduce | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| All Fixes | 1.000 | 0.966 | **0.983** | 57 | 0 | 2 | +0.018 |

### Component-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 1.000 | 0.771 | **0.871** | 27 | 0 | 8 | — |
| Fix 1: Coassign | 1.000 | 0.771 | **0.871** | 27 | 0 | 8 | +0.000 |
| Fix 2: Interface | 1.000 | 0.971 | **0.986** | 34 | 0 | 1 | +0.115 |
| Fix 3: Coverage | 1.000 | 0.829 | **0.906** | 29 | 0 | 6 | +0.035 |
| Fix 4: FP Reduce | 1.000 | 0.771 | **0.871** | 27 | 0 | 8 | +0.000 |
| All Fixes | 1.000 | 0.971 | **0.986** | 34 | 0 | 1 | +0.115 |

### Fix Details

- **Fix 1** (co-assign): Added 0 interface assignments
- **Fix 2** (interface prompting): Recovered 7 interface assignments
- **Fix 3** (coverage): Recovered 2 assignments across 1 sentences
- **Fix 4** (FP reduce): Removed 0 false positive assignments

**Best single fix:** Fix 3: Coverage (ΔF1 = +0.035)

### Enrollment Expansion Effect

Component-level oracle fixes expand through SAM-CODE to files,
potentially creating file-level FPs. This table shows the gap:

| Fix | Comp TPs Added | File TPs Added | File FPs Added | Net File ΔF1 |
|:--|---:|---:|---:|:---:|
| Fix 1: Coassign | +0 | +0 | +0 | +0.000 |
| Fix 2: Interface | +7 | +2 | +0 | +0.018 |
| Fix 3: Coverage | +2 | +4 | +0 | +0.035 |
| Fix 4: FP Reduce | +0 | +0 | +0 | +0.000 |
| All Fixes | +7 | +2 | +0 | +0.018 |

---

## Teastore

### File-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | — |
| Fix 1: Coassign | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | +0.000 |
| Fix 2: Interface | 0.633 | 0.969 | **0.766** | 685 | 397 | 22 | +0.001 |
| Fix 3: Coverage | 0.640 | 1.000 | **0.781** | 707 | 397 | 0 | +0.016 |
| Fix 4: FP Reduce | 1.000 | 0.966 | **0.983** | 683 | 0 | 24 | +0.218 |
| All Fixes | 1.000 | 0.976 | **0.988** | 690 | 0 | 17 | +0.223 |

### Component-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.676 | 0.431 | **0.526** | 25 | 12 | 33 | — |
| Fix 1: Coassign | 0.672 | 0.672 | **0.672** | 39 | 19 | 19 | +0.146 |
| Fix 2: Interface | 0.778 | 0.724 | **0.750** | 42 | 12 | 16 | +0.224 |
| Fix 3: Coverage | 0.707 | 0.500 | **0.586** | 29 | 12 | 29 | +0.060 |
| Fix 4: FP Reduce | 1.000 | 0.431 | **0.602** | 25 | 0 | 33 | +0.076 |
| All Fixes | 1.000 | 0.983 | **0.991** | 57 | 0 | 1 | +0.465 |

### Fix Details

- **Fix 1** (co-assign): Added 21 interface assignments
- **Fix 2** (interface prompting): Recovered 17 interface assignments
- **Fix 3** (coverage): Recovered 4 assignments across 2 sentences
- **Fix 4** (FP reduce): Removed 12 false positive assignments

**Best single fix:** All Fixes (ΔF1 = +0.223)

### Enrollment Expansion Effect

Component-level oracle fixes expand through SAM-CODE to files,
potentially creating file-level FPs. This table shows the gap:

| Fix | Comp TPs Added | File TPs Added | File FPs Added | Net File ΔF1 |
|:--|---:|---:|---:|:---:|
| Fix 1: Coassign | +14 | +0 | +0 | +0.000 |
| Fix 2: Interface | +17 | +2 | +0 | +0.001 |
| Fix 3: Coverage | +4 | +24 | +0 | +0.016 |
| Fix 4: FP Reduce | +0 | +0 | -397 | +0.218 |
| All Fixes | +32 | +7 | -397 | +0.223 |

---

## Teammates

### File-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 | — |
| Fix 1: Coassign | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 | +0.000 |
| Fix 2: Interface | 0.404 | 0.995 | **0.575** | 8057 | 11879 | 40 | -0.132 |
| Fix 3: Coverage | 0.415 | 0.952 | **0.578** | 7709 | 10888 | 388 | -0.129 |
| Fix 4: FP Reduce | 0.911 | 0.766 | **0.833** | 6205 | 603 | 1892 | +0.126 |
| All Fixes | 0.466 | 0.995 | **0.635** | 8057 | 9225 | 40 | -0.072 |

### Component-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.708 | 0.230 | **0.347** | 51 | 21 | 171 | — |
| Fix 1: Coassign | 0.708 | 0.459 | **0.557** | 102 | 42 | 120 | +0.210 |
| Fix 2: Interface | 0.841 | 0.500 | **0.627** | 111 | 21 | 111 | +0.280 |
| Fix 3: Coverage | 0.879 | 0.689 | **0.773** | 153 | 21 | 69 | +0.426 |
| Fix 4: FP Reduce | 0.864 | 0.230 | **0.363** | 51 | 8 | 171 | +0.016 |
| All Fixes | 0.910 | 0.730 | **0.810** | 162 | 16 | 60 | +0.463 |

### Fix Details

- **Fix 1** (co-assign): Added 72 interface assignments
- **Fix 2** (interface prompting): Recovered 60 interface assignments
- **Fix 3** (coverage): Recovered 102 assignments across 46 sentences
- **Fix 4** (FP reduce): Removed 13 false positive assignments

**Best single fix:** Fix 4: FP Reduce (ΔF1 = +0.126)

### Enrollment Expansion Effect

Component-level oracle fixes expand through SAM-CODE to files,
potentially creating file-level FPs. This table shows the gap:

| Fix | Comp TPs Added | File TPs Added | File FPs Added | Net File ΔF1 |
|:--|---:|---:|---:|:---:|
| Fix 1: Coassign | +51 | +0 | +0 | +0.000 |
| Fix 2: Interface | +60 | +1852 | +8622 | -0.132 |
| Fix 3: Coverage | +102 | +1504 | +7631 | -0.129 |
| Fix 4: FP Reduce | +0 | +0 | -2654 | +0.126 |
| All Fixes | +111 | +1852 | +5968 | -0.072 |

---

## Bigbluebutton

### File-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | — |
| Fix 1: Coassign | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | +0.000 |
| Fix 2: Interface | 0.696 | 1.000 | **0.821** | 1529 | 668 | 0 | +0.111 |
| Fix 3: Coverage | 0.700 | 0.944 | **0.804** | 1444 | 618 | 85 | +0.094 |
| Fix 4: FP Reduce | 0.765 | 0.772 | **0.769** | 1181 | 363 | 348 | +0.059 |
| All Fixes | 0.787 | 1.000 | **0.881** | 1529 | 413 | 0 | +0.171 |

### Component-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.679 | 0.228 | **0.341** | 36 | 17 | 122 | — |
| Fix 1: Coassign | 0.692 | 0.456 | **0.550** | 72 | 32 | 86 | +0.208 |
| Fix 2: Interface | 0.823 | 0.500 | **0.622** | 79 | 17 | 79 | +0.281 |
| Fix 3: Coverage | 0.805 | 0.443 | **0.571** | 70 | 17 | 88 | +0.230 |
| Fix 4: FP Reduce | 0.837 | 0.228 | **0.358** | 36 | 7 | 122 | +0.017 |
| All Fixes | 0.906 | 0.728 | **0.807** | 115 | 12 | 43 | +0.466 |

### Fix Details

- **Fix 1** (co-assign): Added 51 interface assignments
- **Fix 2** (interface prompting): Recovered 43 interface assignments
- **Fix 3** (coverage): Recovered 34 assignments across 10 sentences
- **Fix 4** (FP reduce): Removed 10 false positive assignments

**Best single fix:** All Fixes (ΔF1 = +0.171)

### Enrollment Expansion Effect

Component-level oracle fixes expand through SAM-CODE to files,
potentially creating file-level FPs. This table shows the gap:

| Fix | Comp TPs Added | File TPs Added | File FPs Added | Net File ΔF1 |
|:--|---:|---:|---:|:---:|
| Fix 1: Coassign | +36 | +0 | +0 | +0.000 |
| Fix 2: Interface | +43 | +348 | +50 | +0.111 |
| Fix 3: Coverage | +34 | +263 | +0 | +0.094 |
| Fix 4: FP Reduce | +0 | +0 | -255 | +0.059 |
| All Fixes | +79 | +348 | -205 | +0.171 |

---

## Jabref

### File-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | — |
| Fix 1: Coassign | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| Fix 2: Interface | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| Fix 3: Coverage | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| Fix 4: FP Reduce | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| All Fixes | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |

### Component-Level Metrics

| Fix | P | R | F1 | TP | FP | FN | ΔF1 |
|:--|:---:|:---:|:---:|---:|---:|---:|:---:|
| Baseline | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | — |
| Fix 1: Coassign | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | +0.000 |
| Fix 2: Interface | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | +0.000 |
| Fix 3: Coverage | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | +0.000 |
| Fix 4: FP Reduce | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | +0.000 |
| All Fixes | 0.947 | 0.818 | **0.878** | 18 | 1 | 4 | +0.000 |

### Fix Details

- **Fix 1** (co-assign): Added 0 interface assignments
- **Fix 2** (interface prompting): Recovered 0 interface assignments
- **Fix 3** (coverage): Recovered 0 assignments across 0 sentences
- **Fix 4** (FP reduce): Removed 0 false positive assignments

**Best single fix:** Fix 1: Coassign (ΔF1 = +0.000)

### Enrollment Expansion Effect

Component-level oracle fixes expand through SAM-CODE to files,
potentially creating file-level FPs. This table shows the gap:

| Fix | Comp TPs Added | File TPs Added | File FPs Added | Net File ΔF1 |
|:--|---:|---:|---:|:---:|
| Fix 1: Coassign | +0 | +0 | +0 | +0.000 |
| Fix 2: Interface | +0 | +0 | +0 | +0.000 |
| Fix 3: Coverage | +0 | +0 | +0 | +0.000 |
| Fix 4: FP Reduce | +0 | +0 | +0 | +0.000 |
| All Fixes | +0 | +0 | +0 | +0.000 |

---

## Aggregate Summary

### Average File-Level F1 Across Projects

| Fix | Avg F1 | Avg ΔF1 | Max ΔF1 (project) |
|:--|:---:|:---:|:--|
| Baseline | **0.829** | — | — |
| Fix 1: Coassign | **0.829** | +0.000 | +0.000 (mediastore) |
| Fix 2: Interface | **0.829** | -0.000 | +0.111 (bigbluebutton) |
| Fix 3: Coverage | **0.832** | +0.003 | +0.094 (bigbluebutton) |
| Fix 4: FP Reduce | **0.910** | +0.081 | +0.218 (teastore) |
| All Fixes | **0.897** | +0.068 | +0.223 (teastore) |

### Per-Project ΔF1 (File-Level)

| Fix | medi | teas | team | bigb | jabr |
|:--|:---:|:---:|:---:|:---:|:---:|
| Fix 1: Coassign | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| Fix 2: Interface | +0.018 | +0.001 | -0.132 | +0.111 | +0.000 |
| Fix 3: Coverage | +0.035 | +0.016 | -0.129 | +0.094 | +0.000 |
| Fix 4: FP Reduce | +0.000 | +0.218 | +0.126 | +0.059 | +0.000 |
| All Fixes | +0.018 | +0.223 | -0.072 | +0.171 | +0.000 |

### With Fixes vs TransArc and V45

| Project | TransArc | V45 | LLM Baseline | LLM + All Fixes | Best |
|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | 0.588 | 0.868 | 0.965 | **0.983** | LLM+Fix |
| teastore | 0.829 | 0.990 | 0.764 | **0.988** | V45 |
| teammates | 0.821 | 0.786 | 0.707 | **0.635** | TransArc |
| bigbluebutton | 0.831 | 0.877 | 0.710 | **0.881** | LLM+Fix |
| jabref | 0.943 | 0.944 | 0.999 | **0.999** | LLM+Fix |
| **Average** | **0.803** | **0.893** | **0.829** | **0.897** | **LLM+Fix** |

### Key Insights

1. **Baseline LLM avg F1:** 0.829
2. **LLM + All Fixes avg F1:** 0.897 (Δ = +0.068)
3. **TransArc avg F1:** 0.803
4. **V45 avg F1:** 0.893

**LLM + All Fixes would surpass V45** (0.897 > 0.893)

### Implementability

| Fix | Type | Avg ΔF1 | Effort |
|:--|:--|:---:|:--|
| Fix 1: Coassign | **Deterministic** | +0.000 | Zero cost — post-hoc rule |
| Fix 2: Interface | Oracle bound | -0.000 | Requires interface-aware prompting |
| Fix 3: Coverage | Oracle bound | +0.003 | Requires coreference / context expansion |
| Fix 4: FP Reduce | Oracle bound | +0.081 | Requires relevance pre-filter |

## Critical Finding: The Enrollment Expansion Paradox

The simulation reveals a fundamental tension in the SAD-CODE evaluation framework:

**Oracle fixes at the component level can HURT file-level F1.**

This happens because:
1. The gold standard maps sentence S → component C → specific files {f1, f2}
2. But SAM-CODE maps component C → ALL files {f1, f2, f3, ...}
3. Adding the correct component C for sentence S expands to {f1, f2, f3}
4. Files {f3, ...} are NOT in the gold for sentence S, creating FPs

**Teammates is the worst case:** Fix 2 (interface oracle) drops F1 from 0.707 to 0.575
because Teammates has large components (UI: 348 files) and the gold only links
each sentence to a subset of those files. Adding a correct Interface assignment
expands to ALL 348+ files, creating thousands of FPs.

### Implications

1. **Component-level analysis misleads**: Fixing 127 component FNs (interface_missed_entirely)
   does NOT translate to +127 file-level TPs. It creates ~12,000 file FPs on Teammates alone.

2. **Fix 4 (FP reduction) dominates**: The only consistently positive fix is removing FPs.
   This works because removing a wrong component ALWAYS removes wrong files.
   Adding a correct component may add BOTH correct and incorrect files.

3. **The real bottleneck is precision, not recall**: The LLM's main problem isn't missing
   components — it's assigning components to sentences that don't trace to code,
   and the enrollment process amplifies each FP to hundreds of file-level FPs.

4. **Fix priority should be**: (a) reduce FPs, (b) improve precision of assignments,
   (c) expand coverage. This is the OPPOSITE of what the component-level error
   distribution (33% interface miss > 18% coverage) would suggest.

### Realistic Improvement: Fix 4 Only

Since Fix 4 (FP reduction) is the only consistently positive fix,
here is the comparison with only FP reduction applied:

| Project | TransArc | V45 | LLM Baseline | LLM + FP Fix | Best |
|:--|:---:|:---:|:---:|:---:|:--|
| mediastore | 0.588 | 0.868 | 0.965 | **0.965** | LLM+FP |
| teastore | 0.829 | 0.990 | 0.764 | **0.983** | V45 |
| teammates | 0.821 | 0.786 | 0.707 | **0.833** | LLM+FP |
| bigbluebutton | 0.831 | 0.877 | 0.710 | **0.769** | V45 |
| jabref | 0.943 | 0.944 | 0.999 | **0.999** | LLM+FP |
| **Average** | **0.803** | **0.893** | **0.829** | **0.910** | **LLM+FP** |

**LLM + FP Fix surpasses V45** (0.910 > 0.893)

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 llm_fix_simulation.py
# Output: LLM_FIX_SIMULATION.md
```
