# Precision-Focused LLM Classifier Results

Classifier optimized for precision over recall, based on the fix impact
simulation finding that FP reduction (+0.081 avg ΔF1) dominates all other fixes.

**Key changes from original LLM baseline:**
1. Precision-focused prompt: explicit instructions to only classify code-traceable sentences
2. Multi-agent intersection voting: all 3 agents must agree
3. Context isolation post-filter: remove assignments lacking textual evidence

---

## Mediastore

| System | P | R | F1 | TP | FP | FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.962 | 0.424 | **0.588** | 25 | 1 | 34 |
| V45 | 0.979 | 0.780 | **0.868** | 46 | 1 | 13 |
| LLM Original (majority) | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| fresh_intersection | 1.000 | 0.814 | **0.897** | 48 | 0 | 11 |
| fresh_majority | 1.000 | 0.847 | **0.917** | 50 | 0 | 9 |
| fresh_single | 1.000 | 0.881 | **0.937** | 52 | 0 | 7 |
| gate_all | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| gate_any | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| gate_majority | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| review_intersection | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| review_intersection_filtered | 1.000 | 0.847 | **0.917** | 50 | 0 | 9 |
| review_majority | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |
| review_majority_filtered | 1.000 | 0.847 | **0.917** | 50 | 0 | 9 |
| review_single | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 |

**Best strategy:** gate_all (F1=0.965, Δ vs original: +0.000)

## Teastore

| System | P | R | F1 | TP | FP | FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 1.000 | 0.709 | **0.829** | 501 | 0 | 206 |
| V45 | 0.981 | 1.000 | **0.990** | 707 | 14 | 0 |
| LLM Original (intersection) | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 |
| fresh_intersection | 0.563 | 0.779 | **0.654** | 551 | 428 | 156 |
| fresh_majority | 0.562 | 0.801 | **0.660** | 566 | 442 | 141 |
| fresh_single | 0.590 | 0.870 | **0.703** | 615 | 428 | 92 |
| gate_all | 0.618 | 0.909 | **0.736** | 643 | 397 | 64 |
| gate_any | 0.618 | 0.909 | **0.736** | 643 | 397 | 64 |
| gate_majority | 0.618 | 0.909 | **0.736** | 643 | 397 | 64 |
| review_intersection | 0.629 | 0.952 | **0.757** | 673 | 397 | 34 |
| review_intersection_filtered | 0.579 | 0.771 | **0.661** | 545 | 397 | 162 |
| review_majority | 0.629 | 0.952 | **0.757** | 673 | 397 | 34 |
| review_majority_filtered | 0.579 | 0.771 | **0.661** | 545 | 397 | 162 |
| review_single | 0.629 | 0.952 | **0.757** | 673 | 397 | 34 |

**Best strategy:** review_intersection (F1=0.757, Δ vs original: -0.007)

## Teammates

| System | P | R | F1 | TP | FP | FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.753 | 0.902 | **0.821** | 7307 | 2395 | 790 |
| V45 | 0.803 | 0.770 | **0.786** | 6235 | 1525 | 1862 |
| LLM Original (intersection) | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 |
| fresh_intersection | 0.000 | 0.000 | **0.000** | 0 | 0 | 8097 |
| fresh_majority | 0.204 | 0.388 | **0.267** | 3138 | 12280 | 4959 |
| fresh_single | 0.000 | 0.000 | **0.000** | 0 | 0 | 8097 |
| gate_all | 0.646 | 0.486 | **0.555** | 3934 | 2154 | 4163 |
| gate_any | 0.646 | 0.486 | **0.555** | 3934 | 2154 | 4163 |
| gate_majority | 0.646 | 0.486 | **0.555** | 3934 | 2154 | 4163 |
| review_intersection | 0.607 | 0.621 | **0.614** | 5032 | 3257 | 3065 |
| review_intersection_filtered | 0.612 | 0.619 | **0.615** | 5015 | 3186 | 3082 |
| review_majority | 0.607 | 0.621 | **0.614** | 5032 | 3257 | 3065 |
| review_majority_filtered | 0.612 | 0.619 | **0.615** | 5015 | 3186 | 3082 |
| review_single | 0.607 | 0.621 | **0.614** | 5032 | 3257 | 3065 |

**Best strategy:** review_intersection_filtered (F1=0.615, Δ vs original: -0.091)

## Bigbluebutton

| System | P | R | F1 | TP | FP | FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.820 | 0.842 | **0.831** | 1287 | 282 | 242 |
| V45 | 0.817 | 0.947 | **0.877** | 1448 | 325 | 81 |
| LLM Original (majority) | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 |
| fresh_intersection | 0.506 | 0.422 | **0.460** | 645 | 630 | 884 |
| fresh_majority | 0.539 | 0.493 | **0.515** | 754 | 646 | 775 |
| fresh_single | 0.540 | 0.483 | **0.510** | 739 | 630 | 790 |
| gate_all | 0.558 | 0.510 | **0.533** | 780 | 618 | 749 |
| gate_any | 0.563 | 0.520 | **0.540** | 795 | 618 | 734 |
| gate_majority | 0.558 | 0.510 | **0.533** | 780 | 618 | 749 |
| review_intersection | 0.563 | 0.520 | **0.540** | 795 | 618 | 734 |
| review_intersection_filtered | 0.579 | 0.466 | **0.516** | 713 | 519 | 816 |
| review_majority | 0.563 | 0.520 | **0.540** | 795 | 618 | 734 |
| review_majority_filtered | 0.579 | 0.466 | **0.516** | 713 | 519 | 816 |
| review_single | 0.563 | 0.520 | **0.540** | 795 | 618 | 734 |

**Best strategy:** gate_any (F1=0.540, Δ vs original: -0.169)

## Jabref

| System | P | R | F1 | TP | FP | FN |
|:--|:---:|:---:|:---:|---:|---:|---:|
| TransArc | 0.893 | 1.000 | **0.943** | 8268 | 994 | 0 |
| V45 | 0.893 | 1.000 | **0.944** | 8268 | 990 | 0 |
| LLM Original (single) | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 |
| fresh_intersection | 1.000 | 0.267 | **0.421** | 2205 | 0 | 6063 |
| fresh_majority | 1.000 | 0.267 | **0.421** | 2205 | 0 | 6063 |
| fresh_single | 1.000 | 0.267 | **0.421** | 2205 | 0 | 6063 |
| gate_all | 1.000 | 0.533 | **0.696** | 4410 | 0 | 3858 |
| gate_any | 1.000 | 0.533 | **0.696** | 4410 | 0 | 3858 |
| gate_majority | 1.000 | 0.533 | **0.696** | 4410 | 0 | 3858 |
| review_intersection | 1.000 | 0.767 | **0.868** | 6339 | 0 | 1929 |
| review_intersection_filtered | 1.000 | 0.767 | **0.868** | 6339 | 0 | 1929 |
| review_majority | 1.000 | 0.767 | **0.868** | 6339 | 0 | 1929 |
| review_majority_filtered | 1.000 | 0.767 | **0.868** | 6339 | 0 | 1929 |
| review_single | 1.000 | 0.767 | **0.868** | 6339 | 0 | 1929 |

**Best strategy:** review_intersection (F1=0.868, Δ vs original: -0.131)

## Aggregate Summary

| Project | TransArc | V45 | LLM Original | LLM Precision | Best Strategy | ΔF1 |
|:--|:---:|:---:|:---:|:---:|:--|:---:|
| mediastore | 0.588 | 0.868 | 0.965 | **0.965** | gate_all | +0.000 |
| teastore | 0.829 | 0.990 | 0.764 | **0.757** | review_intersection | -0.007 |
| teammates | 0.821 | 0.786 | 0.707 | **0.615** | review_intersection_filtered | -0.091 |
| bigbluebutton | 0.831 | 0.877 | 0.710 | **0.540** | gate_any | -0.169 |
| jabref | 0.943 | 0.944 | 0.999 | **0.868** | review_intersection | -0.131 |
| **Average** | **0.803** | **0.893** | **0.829** | **0.749** | — | **-0.080** |

### Key Findings — Negative Result

**All three LLM-based FP reduction strategies hurt performance** (avg ΔF1 = -0.080):

| Strategy | Approach | Avg Best F1 | Δ vs Original |
|:--|:--|:---:|:---:|
| Fresh precision | Re-classify with precision prompt | ~0.65 | ~-0.18 |
| LLM review | Ask LLM to filter existing assignments | 0.749 | -0.080 |
| Traceability gate | Binary "is sentence code-traceable?" filter | ~0.70 | ~-0.13 |
| **Original LLM** | Adaptive multi-agent baseline | **0.829** | — |

### Why LLM Post-Hoc Filtering Fails

The fix impact simulation showed oracle FP reduction yields +0.081 avg ΔF1. However,
**all three LLM-based attempts to approximate this oracle failed** because the LLM
cannot distinguish TPs from FPs using text alone:

1. **FP sentences look equally code-traceable as TP sentences.** The LLM's false positives
   are sentences that ARE about architecture — they just have incorrect component assignments.
   A traceability gate passes them through because they genuinely describe implementation.

2. **Review removes TPs and FPs proportionally.** When asked to review its own assignments,
   the LLM keeps FPs (they "sound reasonable") while removing some TPs (which also sound
   reasonable but happen to be correct). Example:
   - BBB: Gate kept all 618 FPs unchanged, but reduced TPs from 1,181 to 780 (-34%)
   - Teammates: Gate reduced FPs by 34% but TPs by 37% — precision barely changed (0.656→0.646)

3. **The FP problem is assignment-level, not sentence-level.** Removing entire sentences
   is too coarse — a sentence can have both correct (TP) and incorrect (FP) component
   assignments simultaneously. Sentence-level filtering throws away both.

### Implication

The gap between oracle FP reduction (+0.081) and LLM-achievable FP reduction (-0.080) reveals
that **FP identification requires information not present in the documentation text**. Potential
approaches that might bridge this gap:

- **Code-aware classification**: Give the LLM access to actual code files to verify component boundaries
- **SAM-CODE model**: Use the architecture-to-code mapping to constrain which components are valid
  for sentences that mention specific code artifacts
- **Ensemble with TransArc**: TransArc has higher precision (0.820-1.000) — intersection of LLM
  and TransArc results could reduce FPs while retaining LLM's broader recall

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 llm_precision_classifier.py            # Run classification
python3 llm_precision_classifier.py --eval-only # Evaluate only
```
