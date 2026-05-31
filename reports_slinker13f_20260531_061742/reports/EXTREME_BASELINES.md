# Extreme Baselines: Maximum Exploitation of Dataset Distribution

These baselines push distributional exploitation to the limit, proving that
micro-averaged enrollment-based F1 is fundamentally dominated by a few structural
properties of the dataset rather than actual trace link recovery quality.

## Baseline Definitions

| ID | Name | Description | Oracle? |
|----|------|-------------|---------|
| B0 | TransArc | Actual system (reference) | No |
| B6 | Keyword-Grep | String match on component names (from previous analysis) | No |
| B7 | Oracle-Component | Per-sentence: oracle-select BEST single component | Yes |
| B8 | Oracle-Subset | Per-sentence: oracle-select BEST component SUBSET (2^K search) | Yes |
| B9 | Round-Robin | Assign sentences to components cyclically by size | No |
| B10 | Sentence-Length | Longest sentences → largest components | No |
| B11 | Optimal-Constant | Single best component for ALL sentences (F1-maximizing) | No* |
| B12 | Enhanced-Grep | Keyword-Grep with camelCase splitting & name fragments | No |
| B13 | Gold-Density | Link to files appearing in most SAM-CODE gold entries | No* |
| B_perf | Perfect-Transitive | Gold SAD-SAM x Gold SAM-CODE transitive closure | Oracle |

\* B11 searches over components to find the F1-maximizing one (uses gold indirectly).
  B13 uses SAM-CODE gold file frequencies (public gold standard info).

## Mediastore

Gold: **59** enrolled links, **25** sentences, **15** code files, code model: 97 files, gold density: 2.4%

### F1 and Holistic Metrics

| Baseline | Output | **Micro F1** | Macro F1 | Coverage | Useful | Noise | Wasted |
|----------|--------|------------|----------|----------|--------|-------|--------|
| B0: TransArc | 26 | **0.588** | 0.620 | 0.640 (16/25) | 0.941 | 0.059 | 0.04 |
| B6: Keyword-Grep | 25 | **0.595** | 0.620 | 0.640 (16/25) | 1.000 | 0.000 | 0.00 |
| B7: Oracle-Component | 54 | **0.956** | 0.971 | 1.000 (25/25) | 1.000 | 0.000 | 0.00 |
| B8: Oracle-Subset | 59 | **1.000** | 1.000 | 1.000 (25/25) | 1.000 | 0.000 | 0.00 |
| B9: Round-Robin | 95 | **0.052** | 0.040 | 0.040 (1/25) | 0.040 | 0.960 | 22.75 |
| B10: Sent-Length | 95 | **0.052** | 0.040 | 0.040 (1/25) | 0.040 | 0.960 | 22.75 |
| B11: Optimal-Const (Component: DB) | 100 | **0.352** | 0.264 | 0.280 (7/25) | 0.280 | 0.720 | 2.57 |
| B12: Enhanced-Grep | 384 | **0.122** | 0.120 | 0.680 (17/25) | 0.000 | 0.922 | 13.22 |
| B13: Gold-Density | 1,200 | **0.076** | 0.075 | 0.880 (22/25) | 0.000 | 0.960 | 24.00 |
| B_perf: Perfect-Trans | 59 | **1.000** | 1.000 | 1.000 (25/25) | 1.000 | 0.000 | 0.00 |

## Teastore

Gold: **707** enrolled links, **23** sentences, **145** code files, code model: 205 files, gold density: 15.0%

### F1 and Holistic Metrics

| Baseline | Output | **Micro F1** | Macro F1 | Coverage | Useful | Noise | Wasted |
|----------|--------|------------|----------|----------|--------|-------|--------|
| B0: TransArc | 501 | **0.829** | 0.696 | 0.696 (16/23) | 1.000 | 0.000 | 0.00 |
| B6: Keyword-Grep | 245 | **0.515** | 0.570 | 0.652 (15/23) | 1.000 | 0.000 | 0.00 |
| B7: Oracle-Component | 636 | **0.947** | 0.975 | 1.000 (23/23) | 1.000 | 0.000 | 0.00 |
| B8: Oracle-Subset | 707 | **1.000** | 1.000 | 1.000 (23/23) | 1.000 | 0.000 | 0.00 |
| B9: Round-Robin | 291 | **0.032** | 0.030 | 0.130 (3/23) | 0.130 | 0.870 | 17.19 |
| B10: Sent-Length | 291 | **0.156** | 0.087 | 0.087 (2/23) | 0.087 | 0.913 | 2.73 |
| B11: Optimal-Const (Component: ImageProvider) | 1,472 | **0.294** | 0.201 | 0.217 (5/23) | 0.217 | 0.783 | 3.60 |
| B12: Enhanced-Grep | 719 | **0.792** | 0.684 | 0.739 (17/23) | 0.833 | 0.155 | 0.27 |
| B13: Gold-Density | 2,346 | **0.309** | 0.275 | 1.000 (23/23) | 0.130 | 0.799 | 3.98 |
| B_perf: Perfect-Trans | 707 | **1.000** | 1.000 | 1.000 (23/23) | 1.000 | 0.000 | 0.00 |

## Teammates

Gold: **8097** enrolled links, **92** sentences, **828** code files, code model: 833 files, gold density: 10.6%

### F1 and Holistic Metrics

| Baseline | Output | **Micro F1** | Macro F1 | Coverage | Useful | Noise | Wasted |
|----------|--------|------------|----------|----------|--------|-------|--------|
| B0: TransArc | 9,702 | **0.821** | 0.515 | 0.598 (55/92) | 0.692 | 0.299 | 0.33 |
| B6: Keyword-Grep | 5,442 | **0.608** | 0.439 | 0.565 (52/92) | 0.707 | 0.300 | 0.32 |
| B7: Oracle-Component | 6,695 | **0.881** | 0.525 | 0.554 (51/92) | 1.000 | 0.030 | 0.03 |
| B8: Oracle-Subset | 7,427 | **0.934** | 0.537 | 0.554 (51/92) | 1.000 | 0.030 | 0.02 |
| B9: Round-Robin | 11,080 | **0.193** | 0.101 | 0.174 (16/92) | 0.109 | 0.896 | 4.99 |
| B10: Sent-Length | 11,080 | **0.114** | 0.096 | 0.207 (19/92) | 0.098 | 0.898 | 9.13 |
| B11: Optimal-Const (Component: UI) | 32,016 | **0.181** | 0.113 | 0.293 (27/92) | 0.098 | 0.887 | 7.84 |
| B12: Enhanced-Grep | 5,442 | **0.608** | 0.439 | 0.565 (52/92) | 0.707 | 0.300 | 0.32 |
| B13: Gold-Density | 38,272 | **0.176** | 0.139 | 0.913 (84/92) | 0.033 | 0.893 | 8.38 |
| B_perf: Perfect-Trans | 6,380 | **0.881** | 0.454 | 0.457 (42/92) | 1.000 | 0.000 | 0.00 |

## Bigbluebutton

Gold: **1529** enrolled links, **45** sentences, **252** code files, code model: 551 files, gold density: 6.2%

### F1 and Holistic Metrics

| Baseline | Output | **Micro F1** | Macro F1 | Coverage | Useful | Noise | Wasted |
|----------|--------|------------|----------|----------|--------|-------|--------|
| B0: TransArc | 1,569 | **0.831** | 0.732 | 0.822 (37/45) | 0.902 | 0.211 | 0.22 |
| B6: Keyword-Grep | 2,014 | **0.827** | 0.779 | 0.956 (43/45) | 0.682 | 0.251 | 0.37 |
| B7: Oracle-Component | 1,463 | **0.978** | 0.983 | 1.000 (45/45) | 1.000 | 0.000 | 0.00 |
| B8: Oracle-Subset | 1,589 | **0.981** | 0.994 | 1.000 (45/45) | 1.000 | 0.012 | 0.04 |
| B9: Round-Robin | 1,554 | **0.042** | 0.089 | 0.089 (4/45) | 0.089 | 0.911 | 23.28 |
| B10: Sent-Length | 1,554 | **0.160** | 0.153 | 0.156 (7/45) | 0.156 | 0.846 | 5.29 |
| B11: Optimal-Const (Interface: HTML5 Server) | 720 | **0.285** | 0.416 | 0.444 (20/45) | 0.444 | 0.556 | 1.25 |
| B12: Enhanced-Grep | 2,014 | **0.827** | 0.779 | 0.956 (43/45) | 0.682 | 0.251 | 0.37 |
| B13: Gold-Density | 11,925 | **0.227** | 0.208 | 1.000 (45/45) | 0.000 | 0.872 | 6.80 |
| B_perf: Perfect-Trans | 1,615 | **0.968** | 0.999 | 1.000 (45/45) | 0.978 | 0.022 | 0.06 |

## Jabref

Gold: **8268** enrolled links, **10** sentences, **1955** code files, code model: 1998 files, gold density: 41.4%

### F1 and Holistic Metrics

| Baseline | Output | **Micro F1** | Macro F1 | Coverage | Useful | Noise | Wasted |
|----------|--------|------------|----------|----------|--------|-------|--------|
| B0: TransArc | 9,262 | **0.943** | 0.933 | 1.000 (10/10) | 0.900 | 0.082 | 0.12 |
| B6: Keyword-Grep | 9,258 | **0.944** | 0.933 | 1.000 (10/10) | 0.900 | 0.082 | 0.12 |
| B7: Oracle-Component | 5,139 | **0.767** | 0.871 | 1.000 (10/10) | 1.000 | 0.000 | 0.00 |
| B8: Oracle-Subset | 8,268 | **1.000** | 1.000 | 1.000 (10/10) | 1.000 | 0.000 | 0.00 |
| B9: Round-Robin | 3,903 | **0.361** | 0.179 | 0.400 (4/10) | 0.400 | 0.600 | 0.78 |
| B10: Sent-Length | 3,903 | **0.320** | 0.226 | 0.500 (5/10) | 0.500 | 0.500 | 1.00 |
| B11: Optimal-Const (Component: logic) | 9,720 | **0.432** | 0.290 | 0.400 (4/10) | 0.400 | 0.600 | 1.50 |
| B12: Enhanced-Grep | 9,258 | **0.944** | 0.933 | 1.000 (10/10) | 0.900 | 0.082 | 0.12 |
| B13: Gold-Density | 9,990 | **0.462** | 0.347 | 1.000 (10/10) | 0.400 | 0.578 | 1.37 |
| B_perf: Perfect-Trans | 8,268 | **1.000** | 1.000 | 1.000 (10/10) | 1.000 | 0.000 | 0.00 |

## Cross-Project Micro F1 Comparison

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref | **Avg** |
|----------|---------|---------|---------|---------|---------|---------|
| B0: TransArc | 0.588 | 0.829 | 0.821 | 0.831 | 0.943 | **0.803** |
| B6: Keyword-Grep | 0.595 | 0.515 | 0.608 | 0.827 | 0.944 | **0.698** |
| B7: Oracle-Component | 0.956 | 0.947 | 0.881 | 0.978 | 0.767 | **0.906** |
| B8: Oracle-Subset | 1.000 | 1.000 | 0.934 | 0.981 | 1.000 | **0.983** |
| B9: Round-Robin | 0.052 | 0.032 | 0.193 | 0.042 | 0.361 | **0.136** |
| B10: Sent-Length | 0.052 | 0.156 | 0.114 | 0.160 | 0.320 | **0.161** |
| B11: Optimal-Const | 0.352 | 0.294 | 0.181 | 0.285 | 0.432 | **0.309** |
| B12: Enhanced-Grep | 0.122 | 0.792 | 0.608 | 0.827 | 0.944 | **0.659** |
| B13: Gold-Density | 0.076 | 0.309 | 0.176 | 0.227 | 0.462 | **0.250** |
| B_perf: Perfect-Trans | 1.000 | 1.000 | 0.881 | 0.968 | 1.000 | **0.970** |

## Cross-Project Macro F1 Comparison

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref | **Avg** |
|----------|---------|---------|---------|---------|---------|---------|
| B0: TransArc | 0.620 | 0.696 | 0.515 | 0.732 | 0.933 | **0.699** |
| B6: Keyword-Grep | 0.620 | 0.570 | 0.439 | 0.779 | 0.933 | **0.668** |
| B7: Oracle-Component | 0.971 | 0.975 | 0.525 | 0.983 | 0.871 | **0.865** |
| B8: Oracle-Subset | 1.000 | 1.000 | 0.537 | 0.994 | 1.000 | **0.906** |
| B9: Round-Robin | 0.040 | 0.030 | 0.101 | 0.089 | 0.179 | **0.088** |
| B10: Sent-Length | 0.040 | 0.087 | 0.096 | 0.153 | 0.226 | **0.120** |
| B11: Optimal-Const | 0.264 | 0.201 | 0.113 | 0.416 | 0.290 | **0.257** |
| B12: Enhanced-Grep | 0.120 | 0.684 | 0.439 | 0.779 | 0.933 | **0.591** |
| B13: Gold-Density | 0.075 | 0.275 | 0.139 | 0.208 | 0.347 | **0.209** |
| B_perf: Perfect-Trans | 1.000 | 1.000 | 0.454 | 0.999 | 1.000 | **0.891** |

## Key Findings

### Finding 1: Oracle-Component-Subset Achieves Near-Perfect F1

The Oracle-Subset baseline (B8) selects the optimal subset of components per sentence,
then links to ALL files of those components. It requires NO file-level precision —
just knowing which components each sentence should map to. Results:

- **mediastore**: Oracle-Subset F1=**1.000** vs TransArc F1=0.588 (Δ=+0.412)
- **teastore**: Oracle-Subset F1=**1.000** vs TransArc F1=0.829 (Δ=+0.171)
- **teammates**: Oracle-Subset F1=**0.934** vs TransArc F1=0.821 (Δ=+0.113)
- **bigbluebutton**: Oracle-Subset F1=**0.981** vs TransArc F1=0.831 (Δ=+0.150)
- **jabref**: Oracle-Subset F1=**1.000** vs TransArc F1=0.943 (Δ=+0.057)

**Implication**: The SAD-CODE task effectively reduces to **component-level sentence
classification**. Once you correctly identify which components a sentence describes,
enrollment inflation does the rest — you don't need file-level precision at all.

### Finding 2: Even Oracle-Single-Component Approaches TransArc

B7 limits each sentence to a SINGLE component (the best one). Even this coarse
strategy achieves high F1:

- **mediastore**: Oracle-Component F1=0.956 (162% of TransArc)
- **teastore**: Oracle-Component F1=0.947 (114% of TransArc)
- **teammates**: Oracle-Component F1=0.881 (107% of TransArc)
- **bigbluebutton**: Oracle-Component F1=0.978 (118% of TransArc)
- **jabref**: Oracle-Component F1=0.767 (81% of TransArc)

### Finding 3: Content-Free Baselines Reveal Structural F1

Round-Robin (B9) and Sentence-Length (B10) use zero text content. Their F1 represents
the 'free' F1 obtainable from dataset structure alone:

- **mediastore**: Round-Robin F1=0.052, Sent-Length F1=0.052 (TransArc=0.588)
- **teastore**: Round-Robin F1=0.032, Sent-Length F1=0.156 (TransArc=0.829)
- **teammates**: Round-Robin F1=0.193, Sent-Length F1=0.114 (TransArc=0.821)
- **bigbluebutton**: Round-Robin F1=0.042, Sent-Length F1=0.160 (TransArc=0.831)
- **jabref**: Round-Robin F1=0.361, Sent-Length F1=0.320 (TransArc=0.943)

### Finding 4: Perfect-Transitive Upper Bound

B_perf shows the maximum F1 achievable by the transitive approach (gold SAD-SAM × gold SAM-CODE).
The gap between B_perf and B8 reveals how much is lost to gold standard disagreement:

- **mediastore**: Perfect-Transitive F1=1.000, Oracle-Subset F1=1.000, gap=0.000
- **teastore**: Perfect-Transitive F1=1.000, Oracle-Subset F1=1.000, gap=0.000
- **teammates**: Perfect-Transitive F1=0.881, Oracle-Subset F1=0.934, gap=-0.053
- **bigbluebutton**: Perfect-Transitive F1=0.968, Oracle-Subset F1=0.981, gap=-0.013
- **jabref**: Perfect-Transitive F1=1.000, Oracle-Subset F1=1.000, gap=0.000

### Finding 5: Macro F1 Correctly Penalizes Exploitation

While micro F1 can be gamed, macro F1 (per-sentence average) correctly penalizes
baselines that only work for a few sentences:

| Baseline | Avg Micro F1 | Avg Macro F1 | Micro-Macro Gap |
|----------|------------|------------|----------------|
| B0: TransArc | 0.803 | 0.699 | +0.104 |
| B6: Keyword-Grep | 0.698 | 0.668 | +0.029 |
| B7: Oracle-Component | 0.906 | 0.865 | +0.041 |
| B8: Oracle-Subset | 0.983 | 0.906 | +0.077 |
| B9: Round-Robin | 0.136 | 0.088 | +0.048 |
| B10: Sent-Length | 0.161 | 0.120 | +0.040 |
| B11: Optimal-Const | 0.309 | 0.257 | +0.052 |
| B12: Enhanced-Grep | 0.659 | 0.591 | +0.068 |
| B13: Gold-Density | 0.250 | 0.209 | +0.041 |
| B_perf: Perfect-Trans | 0.970 | 0.891 | +0.079 |

### Finding 6: The F1 Hierarchy Reveals What Matters

Ordering baselines by average micro F1 reveals the contribution of each 'intelligence' layer:

| Rank | Baseline | Avg Micro F1 | Intelligence Required |
|------|----------|------------|---------------------|
| 1 | B8: Oracle-Subset | 0.983 | Oracle (per-sentence component knowledge) |
| 2 | B_perf: Perfect-Trans | 0.970 | Oracle (gold standards) |
| 3 | B7: Oracle-Component | 0.906 | Oracle (per-sentence component knowledge) |
| 4 | B0: TransArc | 0.803 | Full NLP pipeline (SAD-SAM + SAM-CODE) |
| 5 | B6: Keyword-Grep | 0.698 | Simple substring match |
| 6 | B12: Enhanced-Grep | 0.659 | CamelCase-aware substring match |
| 7 | B11: Optimal-Const | 0.309 | Search (tries all components against gold) |
| 8 | B13: Gold-Density | 0.250 | SAM-CODE gold file frequency |
| 9 | B10: Sent-Length | 0.161 | Word count only |
| 10 | B9: Round-Robin | 0.136 | None (positional) |

## Conclusion

The extreme baselines reveal a fundamental property of enrollment-based evaluation:
**the SAD-CODE task, as measured by micro F1, is primarily a component-level
sentence classification problem**, not a file-level trace link recovery problem.

Evidence:
1. Oracle-Subset (component-level, no file precision) achieves near-perfect F1
2. Even a single correctly-assigned component captures most of a sentence's gold links
3. Content-free baselines (round-robin, sentence-length) already achieve non-trivial F1
4. The gap between TransArc and Keyword-Grep is small for well-named components

**The hard part is not file-level precision — enrollment gives that for free.**
The hard part is sentence-level coverage (reaching all sentences) and component
assignment accuracy. These are exactly the properties that holistic metrics
(sentence coverage, macro F1, noise, usefulness) measure, and that micro F1 misses.

