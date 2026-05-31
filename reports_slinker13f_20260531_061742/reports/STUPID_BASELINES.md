# Stupid Baselines: Why Micro-Averaged F1 Is Insufficient

This analysis implements trivially simple (and meaningless) baselines that exploit
**enrollment inflation** and **component-size skew** in the dataset to achieve
surprisingly high micro-averaged F1 on SAD-CODE trace link recovery. Each baseline
is then evaluated with holistic metrics to expose the gap between F1 and actual utility.

## Baseline Definitions

| ID | Name | Description | Oracle? |
|----|------|-------------|---------|
| B0 | **TransArc** | Actual system (reference) | No |
| B1 | **Link-All** | Every gold sentence x every code file (trivial R=100%) | No* |
| B2 | **Majority-1** | Every sentence x files of the SINGLE largest component | No |
| B3 | **Majority-2** | Every sentence x files of the TWO largest components | No |
| B4 | **Random** | Random links, same count as TransArc output | No |
| B5 | **Oracle-Top3** | Only predict for 3 sentences with most gold links, link to all files | Yes |
| B6 | **Keyword-Grep** | If sentence contains component name substring, link to its files | No |

\* B1 uses the set of gold sentences (which sentences have any trace link) but not the actual links.
  B2/B3 use component sizes from the (public) code model and SAM-CODE gold.
  B5 uses oracle knowledge of which sentences have the most gold links.

## Mediastore

Gold standard: **59** enrolled links from **25** sentences to **15** code files (code model: 97 files)

### Standard Metrics (Micro-Averaged)

| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |
|----------|-----------|-----------|--------|--------|----------|
| B0: TransArc | 26 | 0.962 | 0.424 | **0.588** | 0.760 |
| B1: Link-All | 2,425 | 0.024 | 1.000 | **0.048** | 0.048 |
| B2: Majority-1 | 400 | 0.000 | 0.000 | **0.000** | 0.000 |
| B3: Majority-2 | 550 | 0.000 | 0.000 | **0.000** | 0.000 |
| B4: Random | 26 | 0.000 | 0.000 | **0.000** | 0.000 |
| B5: Oracle-Top3 | 291 | 0.055 | 0.271 | **0.091** | 0.075 |
| B6: Keyword-Grep | 25 | 1.000 | 0.424 | **0.595** | 0.760 |

### Holistic Metrics Comparison

| Baseline | Sent Coverage | Usefulness | Noise | Query Success | Wasted Effort | Overwhelm | Code Pollution |
|----------|-------------|-----------|-------|-------------|-------------|-----------|---------------|
| B0: TransArc | 0.640 (16/25) | 0.941 | 0.059 | 0.941 | 0.04 | 1.0x | 0.000 |
| B1: Link-All | 1.000 (25/25) | 0.000 | 0.976 | 1.000 | 40.10 | 48.5x | 0.845 |
| B2: Majority-1 | 0.000 (0/25) | 0.000 | 1.000 | 0.000 | inf | 8.0x | 1.000 |
| B3: Majority-2 | 0.000 (0/25) | 0.000 | 1.000 | 0.000 | inf | 11.0x | 1.000 |
| B4: Random | 0.000 (0/25) | 0.000 | 1.000 | 0.000 | inf | 1.0x | 0.857 |
| B5: Oracle-Top3 | 0.120 (3/25) | 0.000 | 0.945 | 1.000 | 17.19 | 16.2x | 0.845 |
| B6: Keyword-Grep | 0.640 (16/25) | 1.000 | 0.000 | 1.000 | 0.00 | 1.0x | 0.000 |

### Distribution Metrics

| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | Code Reachability | Orphan Rate |
|----------|-----------|-------------|---------------|-----------------|------------|
| B0: TransArc | 0.386 | 0.000 | 0.960 | 0.667 | 0.267 |
| B1: Link-All | 0.000 | 0.020 | 1.000 | 1.000 | 0.000 |
| B2: Majority-1 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| B3: Majority-2 | 0.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| B4: Random | 0.000 | 0.000 | 1.000 | 0.000 | 0.800 |
| B5: Oracle-Top3 | 0.880 | 0.000 | 1.000 | 0.400 | 0.000 |
| B6: Keyword-Grep | 0.386 | 0.000 | 0.960 | 0.667 | 0.333 |

## Teastore

Gold standard: **707** enrolled links from **23** sentences to **145** code files (code model: 205 files)

### Standard Metrics (Micro-Averaged)

| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |
|----------|-----------|-----------|--------|--------|----------|
| B0: TransArc | 501 | 1.000 | 0.709 | **0.829** | 0.821 |
| B1: Link-All | 4,715 | 0.150 | 1.000 | **0.261** | 0.261 |
| B2: Majority-1 | 1,472 | 0.217 | 0.453 | **0.294** | 0.201 |
| B3: Majority-2 | 2,162 | 0.231 | 0.707 | **0.349** | 0.302 |
| B4: Random | 501 | 0.148 | 0.105 | **0.123** | 0.116 |
| B5: Oracle-Top3 | 615 | 0.405 | 0.352 | **0.377** | 0.197 |
| B6: Keyword-Grep | 245 | 1.000 | 0.347 | **0.515** | 0.711 |

### Holistic Metrics Comparison

| Baseline | Sent Coverage | Usefulness | Noise | Query Success | Wasted Effort | Overwhelm | Code Pollution |
|----------|-------------|-----------|-------|-------------|-------------|-----------|---------------|
| B0: TransArc | 0.696 (16/23) | 1.000 | 0.000 | 1.000 | 0.00 | 1.0x | 0.000 |
| B1: Link-All | 1.000 (23/23) | 0.000 | 0.850 | 1.000 | 5.67 | 10.8x | 0.293 |
| B2: Majority-1 | 0.217 (5/23) | 0.217 | 0.783 | 0.217 | 3.60 | 3.4x | 0.000 |
| B3: Majority-2 | 0.478 (11/23) | 0.217 | 0.769 | 0.478 | 3.32 | 4.9x | 0.000 |
| B4: Random | 0.739 (17/23) | 0.000 | 0.861 | 0.739 | 5.77 | 1.1x | 0.298 |
| B5: Oracle-Top3 | 0.130 (3/23) | 0.000 | 0.595 | 1.000 | 1.47 | 2.5x | 0.293 |
| B6: Keyword-Grep | 0.652 (15/23) | 1.000 | 0.000 | 1.000 | 0.00 | 1.0x | 0.000 |

### Distribution Metrics

| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | Code Reachability | Orphan Rate |
|----------|-----------|-------------|---------------|-----------------|------------|
| B0: TransArc | 0.304 | 0.000 | 1.000 | 1.000 | 0.000 |
| B1: Link-All | 0.000 | 0.048 | 1.000 | 1.000 | 0.000 |
| B2: Majority-1 | 0.796 | 0.000 | 0.870 | 0.441 | 0.559 |
| B3: Majority-2 | 0.554 | 0.000 | 0.826 | 0.648 | 0.352 |
| B4: Random | 0.457 | 0.000 | 0.261 | 0.434 | 0.076 |
| B5: Oracle-Top3 | 0.870 | 0.000 | 1.000 | 0.572 | 0.000 |
| B6: Keyword-Grep | 0.443 | 0.000 | 0.870 | 0.559 | 0.441 |

## Teammates

Gold standard: **8097** enrolled links from **92** sentences to **828** code files (code model: 833 files)

### Standard Metrics (Micro-Averaged)

| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |
|----------|-----------|-----------|--------|--------|----------|
| B0: TransArc | 9,702 | 0.753 | 0.902 | **0.821** | 0.688 |
| B1: Link-All | 76,636 | 0.106 | 1.000 | **0.191** | 0.191 |
| B2: Majority-1 | 32,016 | 0.113 | 0.447 | **0.181** | 0.158 |
| B3: Majority-2 | 32,016 | 0.113 | 0.447 | **0.181** | 0.158 |
| B4: Random | 9,702 | 0.110 | 0.132 | **0.120** | 0.107 |
| B5: Oracle-Top3 | 2,499 | 0.659 | 0.203 | **0.311** | 0.062 |
| B6: Keyword-Grep | 6,456 | 0.637 | 0.508 | **0.565** | 0.592 |

### Holistic Metrics Comparison

| Baseline | Sent Coverage | Usefulness | Noise | Query Success | Wasted Effort | Overwhelm | Code Pollution |
|----------|-------------|-----------|-------|-------------|-------------|-----------|---------------|
| B0: TransArc | 0.598 (55/92) | 0.692 | 0.299 | 0.846 | 0.33 | 1.0x | 0.000 |
| B1: Link-All | 1.000 (92/92) | 0.033 | 0.894 | 1.000 | 8.46 | 14.1x | 0.006 |
| B2: Majority-1 | 0.293 (27/92) | 0.098 | 0.887 | 0.293 | 7.84 | 5.9x | 0.000 |
| B3: Majority-2 | 0.293 (27/92) | 0.098 | 0.887 | 0.293 | 7.84 | 5.9x | 0.000 |
| B4: Random | 0.728 (67/92) | 0.022 | 0.891 | 0.728 | 8.08 | 2.1x | 0.006 |
| B5: Oracle-Top3 | 0.033 (3/92) | 1.000 | 0.341 | 1.000 | 0.52 | 2.0x | 0.006 |
| B6: Keyword-Grep | 0.565 (52/92) | 0.500 | 0.505 | 0.634 | 0.57 | 1.0x | 0.000 |

### Distribution Metrics

| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | Code Reachability | Orphan Rate |
|----------|-----------|-------------|---------------|-----------------|------------|
| B0: TransArc | 0.405 | 0.000 | 0.957 | 0.976 | 0.024 |
| B1: Link-All | 0.000 | 0.003 | 1.000 | 1.000 | 0.000 |
| B2: Majority-1 | 0.734 | 0.000 | 0.924 | 0.420 | 0.580 |
| B3: Majority-2 | 0.734 | 0.000 | 0.924 | 0.420 | 0.580 |
| B4: Random | 0.412 | 0.000 | 0.272 | 0.732 | 0.000 |
| B5: Oracle-Top3 | 0.967 | 0.000 | 1.000 | 0.976 | 0.000 |
| B6: Keyword-Grep | 0.486 | 0.000 | 0.891 | 0.556 | 0.444 |

## Bigbluebutton

Gold standard: **1529** enrolled links from **45** sentences to **252** code files (code model: 551 files)

### Standard Metrics (Micro-Averaged)

| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |
|----------|-----------|-----------|--------|--------|----------|
| B0: TransArc | 1,569 | 0.820 | 0.842 | **0.831** | 0.823 |
| B1: Link-All | 24,795 | 0.061 | 0.993 | **0.115** | 0.115 |
| B2: Majority-1 | 4,230 | 0.173 | 0.479 | **0.254** | 0.169 |
| B3: Majority-2 | 4,230 | 0.173 | 0.479 | **0.254** | 0.169 |
| B4: Random | 1,569 | 0.066 | 0.067 | **0.066** | 0.065 |
| B5: Oracle-Top3 | 1,653 | 0.196 | 0.212 | **0.204** | 0.099 |
| B6: Keyword-Grep | 2,663 | 0.550 | 0.958 | **0.699** | 0.839 |

### Holistic Metrics Comparison

| Baseline | Sent Coverage | Usefulness | Noise | Query Success | Wasted Effort | Overwhelm | Code Pollution |
|----------|-------------|-----------|-------|-------------|-------------|-----------|---------------|
| B0: TransArc | 0.822 (37/45) | 0.902 | 0.211 | 0.902 | 0.22 | 1.0x | 0.066 |
| B1: Link-All | 1.000 (45/45) | 0.000 | 0.939 | 1.000 | 15.32 | 34.4x | 0.546 |
| B2: Majority-1 | 0.178 (8/45) | 0.178 | 0.827 | 0.178 | 4.78 | 5.9x | 0.000 |
| B3: Majority-2 | 0.178 (8/45) | 0.178 | 0.827 | 0.178 | 4.78 | 5.9x | 0.000 |
| B4: Random | 0.711 (32/45) | 0.000 | 0.937 | 0.711 | 14.23 | 1.9x | 0.542 |
| B5: Oracle-Top3 | 0.067 (3/45) | 0.000 | 0.804 | 1.000 | 4.10 | 5.0x | 0.546 |
| B6: Keyword-Grep | 0.956 (43/45) | 0.500 | 0.451 | 0.717 | 0.82 | 1.0x | 0.049 |

### Distribution Metrics

| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | Code Reachability | Orphan Rate |
|----------|-----------|-------------|---------------|-----------------|------------|
| B0: TransArc | 0.219 | 0.176 | 0.844 | 0.956 | 0.044 |
| B1: Link-All | 0.012 | 0.033 | 0.778 | 0.992 | 0.008 |
| B2: Majority-1 | 0.831 | 0.000 | 0.911 | 0.373 | 0.627 |
| B3: Majority-2 | 0.831 | 0.000 | 0.911 | 0.373 | 0.627 |
| B4: Random | 0.488 | 0.000 | 0.289 | 0.317 | 0.048 |
| B5: Oracle-Top3 | 0.933 | 0.000 | 0.956 | 0.552 | 0.008 |
| B6: Keyword-Grep | 0.048 | 0.306 | 0.956 | 1.000 | 0.000 |

## Jabref

Gold standard: **8268** enrolled links from **10** sentences to **1955** code files (code model: 1998 files)

### Standard Metrics (Micro-Averaged)

| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |
|----------|-----------|-----------|--------|--------|----------|
| B0: TransArc | 9,262 | 0.893 | 1.000 | **0.943** | 0.957 |
| B1: Link-All | 19,980 | 0.414 | 1.000 | **0.585** | 0.585 |
| B2: Majority-1 | 9,720 | 0.400 | 0.470 | **0.432** | 0.293 |
| B3: Majority-2 | 16,790 | 0.400 | 0.812 | **0.536** | 0.419 |
| B4: Random | 9,262 | 0.414 | 0.464 | **0.437** | 0.444 |
| B5: Oracle-Top3 | 5,994 | 0.965 | 0.700 | **0.812** | 0.458 |
| B6: Keyword-Grep | 9,258 | 0.893 | 1.000 | **0.944** | 0.957 |

### Holistic Metrics Comparison

| Baseline | Sent Coverage | Usefulness | Noise | Query Success | Wasted Effort | Overwhelm | Code Pollution |
|----------|-------------|-----------|-------|-------------|-------------|-----------|---------------|
| B0: TransArc | 1.000 (10/10) | 0.900 | 0.082 | 1.000 | 0.12 | 1.0x | 0.001 |
| B1: Link-All | 1.000 (10/10) | 0.400 | 0.586 | 1.000 | 1.42 | 5.4x | 0.022 |
| B2: Majority-1 | 0.400 (4/10) | 0.400 | 0.600 | 0.400 | 1.50 | 2.6x | 0.000 |
| B3: Majority-2 | 0.500 (5/10) | 0.400 | 0.600 | 0.500 | 1.50 | 4.5x | 0.000 |
| B4: Random | 1.000 (10/10) | 0.400 | 0.585 | 1.000 | 1.42 | 2.5x | 0.022 |
| B5: Oracle-Top3 | 0.300 (3/10) | 1.000 | 0.035 | 1.000 | 0.04 | 1.0x | 0.022 |
| B6: Keyword-Grep | 1.000 (10/10) | 0.900 | 0.082 | 1.000 | 0.12 | 1.0x | 0.000 |

### Distribution Metrics

| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | Code Reachability | Orphan Rate |
|----------|-----------|-------------|---------------|-----------------|------------|
| B0: TransArc | 0.000 | 0.663 | 1.000 | 1.000 | 0.000 |
| B1: Link-All | 0.000 | 0.013 | 1.000 | 1.000 | 0.000 |
| B2: Majority-1 | 0.638 | 0.000 | 0.600 | 0.497 | 0.503 |
| B3: Majority-2 | 0.519 | 0.000 | 0.600 | 0.859 | 0.141 |
| B4: Random | 0.026 | 0.014 | 0.000 | 0.917 | 0.001 |
| B5: Oracle-Top3 | 0.700 | 0.000 | 1.000 | 0.987 | 0.000 |
| B6: Keyword-Grep | 0.000 | 0.664 | 1.000 | 1.000 | 0.000 |

## Cross-Project Summary: F1 vs Holistic Quality

This table shows each baseline's **micro F1** alongside the **macro F1** and key holistic
metrics across all projects. High micro F1 with low macro F1 or low holistic scores
indicates a baseline that games the enrollment-based metric without providing real value.

| Baseline | Avg Micro F1 | Avg Macro F1 | Gap | Avg Coverage | Avg Usefulness | Avg Noise |
|----------|------------|------------|-----|------------|--------------|-----------|
| B0: TransArc | 0.803 | 0.810 | -0.007 | 0.751 | 0.887 | 0.130 |
| B1: Link-All | 0.240 | 0.240 | +0.000 | 1.000 | 0.087 | 0.849 |
| B2: Majority-1 | 0.232 | 0.164 | +0.068 | 0.218 | 0.179 | 0.819 |
| B3: Majority-2 | 0.264 | 0.210 | +0.054 | 0.290 | 0.179 | 0.817 |
| B4: Random | 0.149 | 0.146 | +0.003 | 0.636 | 0.084 | 0.855 |
| B5: Oracle-Top3 | 0.359 | 0.178 | +0.180 | 0.130 | 0.400 | 0.544 |
| B6: Keyword-Grep | 0.664 | 0.772 | -0.108 | 0.763 | 0.780 | 0.208 |

### Per-Project Micro F1 Comparison

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref |
|----------|---------|---------|---------|---------|---------|
| B0: TransArc | 0.588 | 0.829 | 0.821 | 0.831 | 0.943 |
| B1: Link-All | 0.048 | 0.261 | 0.191 | 0.115 | 0.585 |
| B2: Majority-1 | 0.000 | 0.294 | 0.181 | 0.254 | 0.432 |
| B3: Majority-2 | 0.000 | 0.349 | 0.181 | 0.254 | 0.536 |
| B4: Random | 0.000 | 0.123 | 0.120 | 0.066 | 0.437 |
| B5: Oracle-Top3 | 0.091 | 0.377 | 0.311 | 0.204 | 0.812 |
| B6: Keyword-Grep | 0.595 | 0.515 | 0.565 | 0.699 | 0.944 |

### Per-Project Macro F1 Comparison

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref |
|----------|---------|---------|---------|---------|---------|
| B0: TransArc | 0.760 | 0.821 | 0.688 | 0.823 | 0.957 |
| B1: Link-All | 0.048 | 0.261 | 0.191 | 0.115 | 0.585 |
| B2: Majority-1 | 0.000 | 0.201 | 0.158 | 0.169 | 0.293 |
| B3: Majority-2 | 0.000 | 0.302 | 0.158 | 0.169 | 0.419 |
| B4: Random | 0.000 | 0.116 | 0.107 | 0.065 | 0.444 |
| B5: Oracle-Top3 | 0.075 | 0.197 | 0.062 | 0.099 | 0.458 |
| B6: Keyword-Grep | 0.760 | 0.711 | 0.592 | 0.839 | 0.957 |

## Key Insights: Why These Baselines Expose Metric Weakness

### Insight 1: Majority-1 Can Match or Exceed TransArc on Micro F1

The Majority-1 baseline links every sentence to all files of the single largest
component. It requires zero NLP, zero model understanding — just counting files in directories.

- **mediastore**: Majority-1 F1=0.000 vs TransArc F1=0.588 (Δ=-0.588)
- **teastore**: Majority-1 F1=0.294 vs TransArc F1=0.829 (Δ=-0.536)
- **teammates**: Majority-1 F1=0.181 vs TransArc F1=0.821 (Δ=-0.640)
- **bigbluebutton**: Majority-1 F1=0.254 vs TransArc F1=0.831 (Δ=-0.577)
- **jabref**: Majority-1 F1=0.432 vs TransArc F1=0.943 (Δ=-0.511)

### Insight 2: Micro F1 vs Macro F1 Gap Reveals Gaming

A large gap between micro and macro F1 means the baseline exploits enrollment inflation.
The micro metric is dominated by large components; macro gives equal weight per sentence.

- **teastore B5: Oracle-Top3**: Micro F1=0.377, Macro F1=0.197 (gap=0.179)
- **teammates B5: Oracle-Top3**: Micro F1=0.311, Macro F1=0.062 (gap=0.249)
- **bigbluebutton B5: Oracle-Top3**: Micro F1=0.204, Macro F1=0.099 (gap=0.105)
- **jabref B2: Majority-1**: Micro F1=0.432, Macro F1=0.293 (gap=0.140)
- **jabref B3: Majority-2**: Micro F1=0.536, Macro F1=0.419 (gap=0.117)
- **jabref B5: Oracle-Top3**: Micro F1=0.812, Macro F1=0.458 (gap=0.354)

### Insight 3: Sentence Coverage Exposes Uselessness

A developer queries individual sentences. Sentence coverage measures what fraction
of sentences return any useful result. Stupid baselines often have 100% coverage
(because they link everything) but terrible usefulness and noise:

- **mediastore**: TransArc usefulness=0.941 noise=0.059 vs Link-All usefulness=0.000 noise=0.976 vs Majority-1 usefulness=0.000 noise=1.000
- **teastore**: TransArc usefulness=1.000 noise=0.000 vs Link-All usefulness=0.000 noise=0.850 vs Majority-1 usefulness=0.217 noise=0.783
- **teammates**: TransArc usefulness=0.692 noise=0.299 vs Link-All usefulness=0.033 noise=0.894 vs Majority-1 usefulness=0.098 noise=0.887
- **bigbluebutton**: TransArc usefulness=0.902 noise=0.211 vs Link-All usefulness=0.000 noise=0.939 vs Majority-1 usefulness=0.178 noise=0.827
- **jabref**: TransArc usefulness=0.900 noise=0.082 vs Link-All usefulness=0.400 noise=0.586 vs Majority-1 usefulness=0.400 noise=0.600

### Insight 4: Wasted Effort is the Developer's Real Cost

Wasted effort = FP/TP — how many wrong files a developer must sift through per correct one.
A system with F1=0.800 and wasted effort=50 is far less useful than F1=0.600 with wasted effort=0.1.

- **mediastore B0: TransArc**: F1=0.588, Wasted Effort=0.0
- **mediastore B2: Majority-1**: F1=0.000, Wasted Effort=inf
- **mediastore B1: Link-All**: F1=0.048, Wasted Effort=40.1
- **teastore B0: TransArc**: F1=0.829, Wasted Effort=0.0
- **teastore B2: Majority-1**: F1=0.294, Wasted Effort=3.6
- **teastore B1: Link-All**: F1=0.261, Wasted Effort=5.7
- **teammates B0: TransArc**: F1=0.821, Wasted Effort=0.3
- **teammates B2: Majority-1**: F1=0.181, Wasted Effort=7.8
- **teammates B1: Link-All**: F1=0.191, Wasted Effort=8.5
- **bigbluebutton B0: TransArc**: F1=0.831, Wasted Effort=0.2
- **bigbluebutton B2: Majority-1**: F1=0.254, Wasted Effort=4.8
- **bigbluebutton B1: Link-All**: F1=0.115, Wasted Effort=15.3
- **jabref B0: TransArc**: F1=0.943, Wasted Effort=0.1
- **jabref B2: Majority-1**: F1=0.432, Wasted Effort=1.5
- **jabref B1: Link-All**: F1=0.585, Wasted Effort=1.4

### Insight 5: Keyword-Grep — A Trivial Baseline That Reveals Distribution Bias

The Keyword-Grep baseline uses no NLP — just checks if a sentence contains a component
name as a substring (e.g., 'logic' or 'database'). Its performance reveals how much of the
apparent quality comes from trivial pattern matching on component names:

- **mediastore**: Keyword-Grep F1=0.595 vs TransArc F1=0.588
- **teastore**: Keyword-Grep F1=0.515 vs TransArc F1=0.829
- **teammates**: Keyword-Grep F1=0.565 vs TransArc F1=0.821
- **bigbluebutton**: Keyword-Grep F1=0.699 vs TransArc F1=0.831
- **jabref**: Keyword-Grep F1=0.944 vs TransArc F1=0.943

### Insight 6: Oracle-Top3 Shows Single-Sentence Dominance

By predicting links only for the 3 sentences with the most gold links (and linking them
to all files), we see how much of the gold standard mass is concentrated in a few sentences:

- **mediastore**: 3 sentences capture 16 / 59 gold links = 27.1%. Oracle-Top3 F1=0.091
- **teastore**: 3 sentences capture 249 / 707 gold links = 35.2%. Oracle-Top3 F1=0.377
- **teammates**: 3 sentences capture 1646 / 8097 gold links = 20.3%. Oracle-Top3 F1=0.311
- **bigbluebutton**: 3 sentences capture 324 / 1529 gold links = 21.2%. Oracle-Top3 F1=0.204
- **jabref**: 3 sentences capture 5787 / 8268 gold links = 70.0%. Oracle-Top3 F1=0.812

## Conclusion

**Micro-averaged F1 on enrollment-based gold standards is easily gamed by trivial baselines.**

The Majority-1 baseline — which requires zero NLP, zero architecture understanding, and
can be implemented in 3 lines of code — achieves competitive or even superior micro F1 to
TransArc on some projects. This is because:

1. **Enrollment inflation**: One directory entry expands to hundreds of file-level links,
   so getting one large component right/wrong dominates the metric
2. **Component-size skew**: Most gold links belong to 1-2 large components, so always
   predicting the largest component captures a disproportionate share of TPs
3. **Sentence-file asymmetry**: A few sentences map to thousands of files, so getting
   those sentences right inflates micro F1 while 40% of sentences can have zero recall

**Holistic metrics expose these baselines as useless:**

- Sentence **usefulness** drops dramatically (majority of sentences get wrong results)
- **Noise** becomes extreme (developers see mostly wrong files)
- **Wasted effort** explodes (dozens of wrong files per correct one)
- **Macro F1** collapses (equal weight per sentence reveals the truth)
- **Code pollution** increases (many spurious code files in output)

This demonstrates that **comprehensive evaluation requires multiple complementary metrics**,
not just micro-averaged P/R/F1.

