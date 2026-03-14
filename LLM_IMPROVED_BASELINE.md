# LLM Improved Baseline: 5 Post-Processing Fixes (v2)

Applies 5 targeted fixes to the LLM Adaptive baseline:

| Fix | Type | Approach |
|:----|:-----|:---------|
| B1 | FP reducer | Context isolation: remove assignments lacking neighbor support |
| B2 | FP reducer | Arch filter: remove non-architectural sentence classifications |
| B3 | FN reducer | Co-occurrence: add components with 100% file overlap |
| B4 | FP reducer | Generic strict: require text evidence for generic names |
| B5 | FN reducer | Selective upgrade: add name-in-text links below baseline threshold |

**Design**: Fixes refine the baseline (never rebuild from scratch). FP reducers remove with evidence; FN reducers add only with explicit textual support.

---

## Mediastore

Adaptive strategy: **majority** | Co-occurrence rules: 1 | Baseline: 24 sents, 27 links

### SAD-CODE Level

| System | P | R | F1 | TP | FP | FN | ΔF1 |
|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|
| TransArc | 0.962 | 0.424 | **0.588** | 25 | 1 | 34 | -0.377 |
| Baseline LLM | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| B1: Ctx Isolate | 1.000 | 0.847 | **0.917** | 50 | 0 | 9 | -0.047 |
| B2: Arch Filter | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| B3: Co-occur | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| B4: Generic Str | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| B5: Sel Upgrade | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |
| Combined | 1.000 | 0.932 | **0.965** | 55 | 0 | 4 | +0.000 |

### SAD-SAM Level

| System | P | R | F1 | TP | FP | FN |
|:-------|:---:|:---:|:---:|---:|---:|---:|
| Baseline LLM | 1.000 | 0.871 | **0.931** | 27 | 0 | 4 |
| B1: Ctx Isolate | 1.000 | 0.806 | **0.893** | 25 | 0 | 6 |
| B2: Arch Filter | 1.000 | 0.871 | **0.931** | 27 | 0 | 4 |
| B3: Co-occur | 0.818 | 0.871 | **0.844** | 27 | 6 | 4 |
| B4: Generic Str | 1.000 | 0.871 | **0.931** | 27 | 0 | 4 |
| B5: Sel Upgrade | 1.000 | 0.871 | **0.931** | 27 | 0 | 4 |
| Combined | 1.000 | 0.871 | **0.931** | 27 | 0 | 4 |

---

## Teastore

Adaptive strategy: **intersection** | Co-occurrence rules: 9 | Baseline: 33 sents, 37 links

### SAD-CODE Level

| System | P | R | F1 | TP | FP | FN | ΔF1 |
|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|
| TransArc | 1.000 | 0.709 | **0.829** | 501 | 0 | 206 | +0.065 |
| Baseline LLM | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | +0.000 |
| B1: Ctx Isolate | 0.583 | 0.785 | **0.669** | 555 | 397 | 152 | -0.095 |
| B2: Arch Filter | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | +0.000 |
| B3: Co-occur | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | +0.000 |
| B4: Generic Str | 0.632 | 0.966 | **0.764** | 683 | 397 | 24 | +0.000 |
| B5: Sel Upgrade | 0.634 | 0.973 | **0.768** | 688 | 397 | 19 | +0.003 |
| Combined | 0.634 | 0.973 | **0.768** | 688 | 397 | 19 | +0.003 |

### SAD-SAM Level

| System | P | R | F1 | TP | FP | FN |
|:-------|:---:|:---:|:---:|---:|---:|---:|
| Baseline LLM | 0.676 | 0.926 | **0.781** | 25 | 12 | 2 |
| B1: Ctx Isolate | 0.657 | 0.852 | **0.742** | 23 | 12 | 4 |
| B2: Arch Filter | 0.676 | 0.926 | **0.781** | 25 | 12 | 2 |
| B3: Co-occur | 0.321 | 0.926 | **0.476** | 25 | 53 | 2 |
| B4: Generic Str | 0.676 | 0.926 | **0.781** | 25 | 12 | 2 |
| B5: Sel Upgrade | 0.684 | 0.963 | **0.800** | 26 | 12 | 1 |
| Combined | 0.684 | 0.963 | **0.800** | 26 | 12 | 1 |

---

## Teammates

Adaptive strategy: **intersection** | Co-occurrence rules: 14 | Baseline: 58 sents, 72 links

### SAD-CODE Level

| System | P | R | F1 | TP | FP | FN | ΔF1 |
|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|
| TransArc | 0.753 | 0.902 | **0.821** | 7307 | 2395 | 790 | +0.114 |
| Baseline LLM | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 | +0.000 |
| B1: Ctx Isolate | 0.601 | 0.592 | **0.597** | 4796 | 3186 | 3301 | -0.110 |
| B2: Arch Filter | 0.667 | 0.766 | **0.713** | 6205 | 3100 | 1892 | +0.006 |
| B3: Co-occur | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 | +0.000 |
| B4: Generic Str | 0.656 | 0.766 | **0.707** | 6205 | 3257 | 1892 | +0.000 |
| B5: Sel Upgrade | 0.629 | 0.899 | **0.740** | 7281 | 4294 | 816 | +0.033 |
| Combined | 0.638 | 0.899 | **0.746** | 7281 | 4137 | 816 | +0.039 |

### SAD-SAM Level

| System | P | R | F1 | TP | FP | FN |
|:-------|:---:|:---:|:---:|---:|---:|---:|
| Baseline LLM | 0.625 | 0.789 | **0.698** | 45 | 27 | 12 |
| B1: Ctx Isolate | 0.606 | 0.702 | **0.650** | 40 | 26 | 17 |
| B2: Arch Filter | 0.652 | 0.789 | **0.714** | 45 | 24 | 12 |
| B3: Co-occur | 0.312 | 0.789 | **0.448** | 45 | 99 | 12 |
| B4: Generic Str | 0.625 | 0.789 | **0.698** | 45 | 27 | 12 |
| B5: Sel Upgrade | 0.511 | 0.842 | **0.636** | 48 | 46 | 9 |
| Combined | 0.527 | 0.842 | **0.649** | 48 | 43 | 9 |

---

## Bigbluebutton

Adaptive strategy: **majority** | Co-occurrence rules: 30 | Baseline: 45 sents, 53 links

### SAD-CODE Level

| System | P | R | F1 | TP | FP | FN | ΔF1 |
|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|
| TransArc | 0.820 | 0.842 | **0.831** | 1287 | 282 | 242 | +0.121 |
| Baseline LLM | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | +0.000 |
| B1: Ctx Isolate | 0.681 | 0.724 | **0.702** | 1107 | 519 | 422 | -0.008 |
| B2: Arch Filter | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | +0.000 |
| B3: Co-occur | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | +0.000 |
| B4: Generic Str | 0.656 | 0.772 | **0.710** | 1181 | 618 | 348 | +0.000 |
| B5: Sel Upgrade | 0.656 | 0.888 | **0.754** | 1357 | 712 | 172 | +0.045 |
| Combined | 0.656 | 0.888 | **0.754** | 1357 | 712 | 172 | +0.045 |

### SAD-SAM Level

| System | P | R | F1 | TP | FP | FN |
|:-------|:---:|:---:|:---:|---:|---:|---:|
| Baseline LLM | 0.642 | 0.548 | **0.591** | 34 | 19 | 28 |
| B1: Ctx Isolate | 0.674 | 0.500 | **0.574** | 31 | 15 | 31 |
| B2: Arch Filter | 0.642 | 0.548 | **0.591** | 34 | 19 | 28 |
| B3: Co-occur | 0.268 | 0.597 | **0.370** | 37 | 101 | 25 |
| B4: Generic Str | 0.642 | 0.548 | **0.591** | 34 | 19 | 28 |
| B5: Sel Upgrade | 0.678 | 0.645 | **0.661** | 40 | 19 | 22 |
| Combined | 0.678 | 0.645 | **0.661** | 40 | 19 | 22 |

---

## Jabref

Adaptive strategy: **single** | Co-occurrence rules: 1 | Baseline: 10 sents, 19 links

### SAD-CODE Level

| System | P | R | F1 | TP | FP | FN | ΔF1 |
|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|
| TransArc | 0.893 | 1.000 | **0.943** | 8268 | 994 | 0 | -0.056 |
| Baseline LLM | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| B1: Ctx Isolate | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| B2: Arch Filter | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| B3: Co-occur | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| B4: Generic Str | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| B5: Sel Upgrade | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |
| Combined | 0.998 | 1.000 | **0.999** | 8268 | 18 | 0 | +0.000 |

### SAD-SAM Level

| System | P | R | F1 | TP | FP | FN |
|:-------|:---:|:---:|:---:|---:|---:|---:|
| Baseline LLM | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |
| B1: Ctx Isolate | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |
| B2: Arch Filter | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |
| B3: Co-occur | 0.783 | 1.000 | **0.878** | 18 | 5 | 0 |
| B4: Generic Str | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |
| B5: Sel Upgrade | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |
| Combined | 0.947 | 1.000 | **0.973** | 18 | 1 | 0 |

---

## Aggregate Comparison

### SAD-CODE Micro F1

| System | medias | teasto | teamma | bigblu | jabref | **Avg** |
|:-------|:---:|:---:|:---:|:---:|:---:|:---:|
| TransArc | 0.588 | 0.829 | 0.821 | 0.831 | 0.943 | **0.803** |
| Baseline LLM | 0.965 | 0.764 | 0.707 | 0.710 | 0.999 | **0.829** |
| B1: Ctx Isolate | 0.917 | 0.669 | 0.597 | 0.702 | 0.999 | **0.777** |
| B2: Arch Filter | 0.965 | 0.764 | 0.713 | 0.710 | 0.999 | **0.830** |
| B3: Co-occur | 0.965 | 0.764 | 0.707 | 0.710 | 0.999 | **0.829** |
| B4: Generic Str | 0.965 | 0.764 | 0.707 | 0.710 | 0.999 | **0.829** |
| B5: Sel Upgrade | 0.965 | 0.768 | 0.740 | 0.754 | 0.999 | **0.845** |
| Combined | 0.965 | 0.768 | 0.746 | 0.754 | 0.999 | **0.846** |

### SAD-SAM Micro F1

| System | medias | teasto | teamma | bigblu | jabref | **Avg** |
|:-------|:---:|:---:|:---:|:---:|:---:|:---:|
| Baseline LLM | 0.931 | 0.781 | 0.698 | 0.591 | 0.973 | **0.795** |
| B1: Ctx Isolate | 0.893 | 0.742 | 0.650 | 0.574 | 0.973 | **0.766** |
| B2: Arch Filter | 0.931 | 0.781 | 0.714 | 0.591 | 0.973 | **0.798** |
| B3: Co-occur | 0.844 | 0.476 | 0.448 | 0.370 | 0.878 | **0.603** |
| B4: Generic Str | 0.931 | 0.781 | 0.698 | 0.591 | 0.973 | **0.795** |
| B5: Sel Upgrade | 0.931 | 0.800 | 0.636 | 0.661 | 0.973 | **0.800** |
| Combined | 0.931 | 0.800 | 0.649 | 0.661 | 0.973 | **0.803** |

### Fix Impact Summary (SAD-CODE)

| Fix | Type | Avg ΔF1 | Best Project | Worst Project |
|:----|:-----|:------:|:---|:---|
| B1: Ctx Isolate | FP ↓ | -0.0522 | jabref (+0.000) | teammates (-0.110) |
| B2: Arch Filter | FP ↓ | +0.0013 | teammates (+0.006) | mediastore (+0.000) |
| B3: Co-occur | FN ↓ | +0.0000 | mediastore (+0.000) | mediastore (+0.000) |
| B4: Generic Str | FP ↓ | +0.0000 | mediastore (+0.000) | mediastore (+0.000) |
| B5: Sel Upgrade | FN ↓ | +0.0163 | bigbluebutton (+0.045) | mediastore (+0.000) |
| Combined | Both | +0.0175 | bigbluebutton (+0.045) | mediastore (+0.000) |

### Fix Impact Summary (SAD-SAM)

| Fix | Avg ΔF1 | Best Project | Worst Project |
|:----|:------:|:---|:---|
| B1: Ctx Isolate | -0.0284 | jabref (+0.000) | teammates (-0.047) |
| B2: Arch Filter | +0.0033 | teammates (+0.017) | mediastore (+0.000) |
| B3: Co-occur | -0.1917 | mediastore (-0.087) | teastore (-0.305) |
| B4: Generic Str | +0.0000 | mediastore (+0.000) | mediastore (+0.000) |
| B5: Sel Upgrade | +0.0053 | bigbluebutton (+0.070) | teammates (-0.062) |
| Combined | +0.0079 | bigbluebutton (+0.070) | teammates (-0.049) |

### Final: Combined vs Baseline vs TransArc (SAD-CODE)

| Project | TransArc | Baseline LLM | Combined | Δ vs Baseline | Δ vs TransArc |
|:--------|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.588 | 0.965 | **0.965** | +0.000 | +0.377 |
| teastore | 0.829 | 0.764 | **0.768** | +0.003 | -0.062 |
| teammates | 0.821 | 0.707 | **0.746** | +0.039 | -0.075 |
| bigbluebutton | 0.831 | 0.710 | **0.754** | +0.045 | -0.077 |
| jabref | 0.943 | 0.999 | **0.999** | +0.000 | +0.056 |
| **Average** | 0.803 | 0.829 | **0.846** | +0.017 | +0.044 |

Combined beats Baseline LLM on **3/5** projects.
Combined beats TransArc on **2/5** projects.

## Key Findings

1. **Best individual fix (CODE)**: B5: Sel Upgrade (avg F1=0.845 vs baseline 0.829, Δ=+0.016)

2. **Best individual fix (SAM)**: B5: Sel Upgrade (avg F1=0.800 vs baseline 0.795, Δ=+0.005)

3. **Per-project best individual fix (CODE):**
   - mediastore: — (+0.000)
   - teastore: B5: Sel Upgrade (+0.003)
   - teammates: B5: Sel Upgrade (+0.033)
   - bigbluebutton: B5: Sel Upgrade (+0.045)
   - jabref: — (+0.000)

4. **Combined pipeline (CODE)**: avg F1=0.846, Δ=+0.017 vs baseline

5. **Lesson**: Post-processing improvements on pre-computed LLM classifications
   are inherently limited. The most impactful improvements require:
   - Re-running the LLM with modified prompts (discourse context, two-phase)
   - Access to confidence scores from the LLM (not just binary classifications)
   - Project-specific tuning (what works for BBB hurts Teammates)

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 llm_improved_baseline.py
```

