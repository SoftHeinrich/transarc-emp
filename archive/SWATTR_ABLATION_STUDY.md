# SWATTR Leave-One-Out Ablation Study

Generated: 2026-02-23 00:37

## Overview

This study tests whether SWATTR's default threshold values generalize across
benchmark projects by using leave-one-out cross-validation: for each held-out
test project, we find the optimal threshold on the remaining 4 training projects
and evaluate on the test project.

## Parameters Studied

| Parameter | Tier | Default | Sweep Values |
|-----------|------|---------|-------------|
| `jaroWinkler_SimilarityThreshold` | 1 | 0.9 | 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0 |
| `getMostRecommendedIByRef_MinProportion` | 1 | 0.5 | 0.3, 0.4, 0.5, 0.6, 0.7, 0.8 |
| `MappingCombinerInformant::minCosineSimilarity` | 2 | 0.4 | 0.2, 0.3, 0.4, 0.5, 0.6, 0.7 |

## jaroWinkler_SimilarityThreshold

**Tier 1** | Default: 0.9

### Parameter Sensitivity (F1 vs Threshold)

| Value | Med | Tea | Tmm | BBB | Jab | **Avg** |
|-------|------|------|------|------|------|--------|
| 0.7 | 0.265 | 0.524 | 0.316 | 0.600 | 0.818 | 0.505 |
| 0.75 | 0.439 | 0.645 | 0.436 | 0.655 | 0.947 | 0.624 |
| 0.8 | 0.500 | 0.727 | 0.566 | 0.742 | 0.947 | 0.697 |
| 0.85 | 0.531 | 0.784 | 0.590 | 0.746 | 0.947 | 0.720 |
| 0.9 | **0.694** | **0.851** | **0.710** | **0.793** | **0.947** | **0.799** |
| 0.95 | 0.694 | 0.826 | 0.710 | 0.762 | 0.947 | 0.788 |
| 1.0 | 0.694 | 0.826 | 0.710 | 0.762 | 0.947 | 0.788 |

### Detailed Metrics (P / R / F1)

**jaroWinkler_SimilarityThreshold = 0.7**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.163 | 0.710 | 0.265 | 22 | 113 | 9 |
| TEASTORE | 0.386 | 0.815 | 0.524 | 22 | 35 | 5 |
| TEAMMATES | 0.194 | 0.860 | 0.316 | 49 | 204 | 8 |
| BIGBLUEBUTTON | 0.621 | 0.581 | 0.600 | 36 | 22 | 26 |
| JABREF | 0.692 | 1.000 | 0.818 | 18 | 8 | 0 |

**jaroWinkler_SimilarityThreshold = 0.75**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.353 | 0.581 | 0.439 | 18 | 33 | 13 |
| TEASTORE | 0.571 | 0.741 | 0.645 | 20 | 15 | 7 |
| TEAMMATES | 0.292 | 0.860 | 0.436 | 49 | 119 | 8 |
| BIGBLUEBUTTON | 0.750 | 0.581 | 0.655 | 36 | 12 | 26 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**jaroWinkler_SimilarityThreshold = 0.8**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.439 | 0.581 | 0.500 | 18 | 23 | 13 |
| TEASTORE | 0.714 | 0.741 | 0.727 | 20 | 8 | 7 |
| TEAMMATES | 0.422 | 0.860 | 0.566 | 49 | 67 | 8 |
| BIGBLUEBUTTON | 0.700 | 0.790 | 0.742 | 49 | 21 | 13 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**jaroWinkler_SimilarityThreshold = 0.85**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.515 | 0.548 | 0.531 | 17 | 16 | 14 |
| TEASTORE | 0.833 | 0.741 | 0.784 | 20 | 4 | 7 |
| TEAMMATES | 0.450 | 0.860 | 0.590 | 49 | 60 | 8 |
| BIGBLUEBUTTON | 0.786 | 0.710 | 0.746 | 44 | 12 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**jaroWinkler_SimilarityThreshold = 0.9**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**jaroWinkler_SimilarityThreshold = 0.95**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.704 | 0.826 | 19 | 0 | 8 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.930 | 0.645 | 0.762 | 40 | 3 | 22 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**jaroWinkler_SimilarityThreshold = 1.0**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.704 | 0.826 | 19 | 0 | 8 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.930 | 0.645 | 0.762 | 40 | 3 | 22 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

### Leave-One-Out Cross-Validation

| Test Project | LOO-Optimal Value | LOO Train F1 | LOO Test F1 | Default Test F1 | Best-All Value | Best-All Test F1 | Gap (LOO - Default) |
|-------------|-------------------|-------------|-------------|-----------------|----------------|------------------|---------------------|
| MEDIASTORE | 0.9 | 0.825 | 0.694 | 0.694 | 0.9 | 0.694 | +0.000 |
| TEASTORE | 0.9 | 0.786 | 0.851 | 0.851 | 0.9 | 0.851 | +0.000 |
| TEAMMATES | 0.9 | 0.821 | 0.710 | 0.710 | 0.9 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.9 | 0.801 | 0.793 | 0.793 | 0.9 | 0.793 | +0.000 |
| JABREF | 0.9 | 0.762 | 0.947 | 0.947 | 0.9 | 0.947 | +0.000 |
| **Average** | - | - | **0.799** | **0.799** | - | - | **+0.000** |

### Interpretation

The default value (0.9) generalizes well — the LOO gap is negligible (+0.000).

## getMostRecommendedIByRef_MinProportion

**Tier 1** | Default: 0.5

### Parameter Sensitivity (F1 vs Threshold)

| Value | Med | Tea | Tmm | BBB | Jab | **Avg** |
|-------|------|------|------|------|------|--------|
| 0.3 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.4 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.5 | **0.694** | **0.851** | **0.710** | **0.793** | **0.947** | **0.799** |
| 0.6 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.7 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.8 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |

### Detailed Metrics (P / R / F1)

**getMostRecommendedIByRef_MinProportion = 0.3**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**getMostRecommendedIByRef_MinProportion = 0.4**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**getMostRecommendedIByRef_MinProportion = 0.5**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**getMostRecommendedIByRef_MinProportion = 0.6**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**getMostRecommendedIByRef_MinProportion = 0.7**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**getMostRecommendedIByRef_MinProportion = 0.8**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

### Leave-One-Out Cross-Validation

| Test Project | LOO-Optimal Value | LOO Train F1 | LOO Test F1 | Default Test F1 | Best-All Value | Best-All Test F1 | Gap (LOO - Default) |
|-------------|-------------------|-------------|-------------|-----------------|----------------|------------------|---------------------|
| MEDIASTORE | 0.3 | 0.825 | 0.694 | 0.694 | 0.3 | 0.694 | +0.000 |
| TEASTORE | 0.3 | 0.786 | 0.851 | 0.851 | 0.3 | 0.851 | +0.000 |
| TEAMMATES | 0.3 | 0.821 | 0.710 | 0.710 | 0.3 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.3 | 0.801 | 0.793 | 0.793 | 0.3 | 0.793 | +0.000 |
| JABREF | 0.3 | 0.762 | 0.947 | 0.947 | 0.3 | 0.947 | +0.000 |
| **Average** | - | - | **0.799** | **0.799** | - | - | **+0.000** |

### Interpretation

The default value (0.5) generalizes well — the LOO gap is negligible (+0.000).

## MappingCombinerInformant::minCosineSimilarity

**Tier 2** | Default: 0.4

### Parameter Sensitivity (F1 vs Threshold)

| Value | Med | Tea | Tmm | BBB | Jab | **Avg** |
|-------|------|------|------|------|------|--------|
| 0.2 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.3 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.4 | **0.694** | **0.851** | **0.710** | **0.793** | **0.947** | **0.799** |
| 0.5 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.6 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |
| 0.7 | 0.694 | 0.851 | 0.710 | 0.793 | 0.947 | 0.799 |

### Detailed Metrics (P / R / F1)

**MappingCombinerInformant::minCosineSimilarity = 0.2**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**MappingCombinerInformant::minCosineSimilarity = 0.3**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**MappingCombinerInformant::minCosineSimilarity = 0.4**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**MappingCombinerInformant::minCosineSimilarity = 0.5**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**MappingCombinerInformant::minCosineSimilarity = 0.6**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

**MappingCombinerInformant::minCosineSimilarity = 0.7**

| Project | P | R | F1 | TP | FP | FN |
|---------|---|---|----|----|----|----|
| MEDIASTORE | 0.944 | 0.548 | 0.694 | 17 | 1 | 14 |
| TEASTORE | 1.000 | 0.741 | 0.851 | 20 | 0 | 7 |
| TEAMMATES | 0.605 | 0.860 | 0.710 | 49 | 32 | 8 |
| BIGBLUEBUTTON | 0.898 | 0.710 | 0.793 | 44 | 5 | 18 |
| JABREF | 0.900 | 1.000 | 0.947 | 18 | 2 | 0 |

### Leave-One-Out Cross-Validation

| Test Project | LOO-Optimal Value | LOO Train F1 | LOO Test F1 | Default Test F1 | Best-All Value | Best-All Test F1 | Gap (LOO - Default) |
|-------------|-------------------|-------------|-------------|-----------------|----------------|------------------|---------------------|
| MEDIASTORE | 0.2 | 0.825 | 0.694 | 0.694 | 0.2 | 0.694 | +0.000 |
| TEASTORE | 0.2 | 0.786 | 0.851 | 0.851 | 0.2 | 0.851 | +0.000 |
| TEAMMATES | 0.2 | 0.821 | 0.710 | 0.710 | 0.2 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.2 | 0.801 | 0.793 | 0.793 | 0.2 | 0.793 | +0.000 |
| JABREF | 0.2 | 0.762 | 0.947 | 0.947 | 0.2 | 0.947 | +0.000 |
| **Average** | - | - | **0.799** | **0.799** | - | - | **+0.000** |

### Interpretation

The default value (0.4) generalizes well — the LOO gap is negligible (+0.000).

## Overall Summary

| Parameter | Default | Avg F1 (Default) | Avg F1 (LOO) | Generalization Gap |
|-----------|---------|------------------|-------------|-------------------|
| `jaroWinkler_SimilarityThreshold` | 0.9 | 0.799 | 0.799 | +0.000 |
| `getMostRecommendedIByRef_MinProportion` | 0.5 | 0.799 | 0.799 | +0.000 |
| `MappingCombinerInformant::minCosineSimilarity` | 0.4 | 0.799 | 0.799 | +0.000 |

## Best Per-Project Configuration

For each project, the parameter value that maximizes F1:

### jaroWinkler_SimilarityThreshold

| Project | Best Value | F1 | Default F1 | Delta |
|---------|-----------|-----|-----------|-------|
| MEDIASTORE | 0.9 | 0.694 | 0.694 | +0.000 |
| TEASTORE | 0.9 | 0.851 | 0.851 | +0.000 |
| TEAMMATES | 0.9 | 0.710 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.9 | 0.793 | 0.793 | +0.000 |
| JABREF | 0.75 | 0.947 | 0.947 | +0.000 |

### getMostRecommendedIByRef_MinProportion

| Project | Best Value | F1 | Default F1 | Delta |
|---------|-----------|-----|-----------|-------|
| MEDIASTORE | 0.3 | 0.694 | 0.694 | +0.000 |
| TEASTORE | 0.3 | 0.851 | 0.851 | +0.000 |
| TEAMMATES | 0.3 | 0.710 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.3 | 0.793 | 0.793 | +0.000 |
| JABREF | 0.3 | 0.947 | 0.947 | +0.000 |

### MappingCombinerInformant::minCosineSimilarity

| Project | Best Value | F1 | Default F1 | Delta |
|---------|-----------|-----|-----------|-------|
| MEDIASTORE | 0.2 | 0.694 | 0.694 | +0.000 |
| TEASTORE | 0.2 | 0.851 | 0.851 | +0.000 |
| TEAMMATES | 0.2 | 0.710 | 0.710 | +0.000 |
| BIGBLUEBUTTON | 0.2 | 0.793 | 0.793 | +0.000 |
| JABREF | 0.2 | 0.947 | 0.947 | +0.000 |
