# SWATTR (SAD-SAM) TP vs FP Feature Analysis

Can we distinguish SWATTR true positives from false positives using
externally observable features? This analysis extracts a feature vector
for each SWATTR link and tests separability.

## 1. Data Overview

Total links analyzed: **188** (148 TPs, 40 FPs)

| Project | TPs | FPs | Total | FP Rate |
|---------|-----|-----|-------|---------|
| mediastore | 17 | 1 | 18 | 5.6% |
| teastore | 20 | 0 | 20 | 0.0% |
| teammates | 49 | 32 | 81 | 39.5% |
| bigbluebutton | 44 | 5 | 49 | 10.2% |
| jabref | 18 | 2 | 20 | 10.0% |

## 2. Feature Distributions: TP vs FP

Mean values and Cohen's d effect size for each feature.
Cohen's d: |d|<0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, >0.8 large.

| Feature | TP Mean | FP Mean | Cohen's d | Direction |
|---------|---------|---------|-----------|-----------|
| best_camel_ratio | 0.924 | 0.920 | +0.025 | TP > FP |
| best_word_ratio | 0.889 | 0.904 | -0.088 | FP > TP |
| camel_word_fraction | 0.946 | 0.925 | +0.105 | TP > FP |
| elem_is_interface | 0.000 | 0.000 | +0.000 | = |
| elem_name_length | 7.899 | 6.200 | +0.445 | TP > FP |
| elem_name_word_count | 1.250 | 1.250 | +0.000 | = |
| exact_name_match | 0.872 | 0.875 | -0.010 | FP > TP |
| gold_elem_fanout | 6.824 | 7.725 | -0.216 | FP > TP |
| gold_sent_fanout | 1.716 | 0.275 | +1.175 | TP > FP |
| jaccard_similarity | 0.117 | 0.107 | +0.078 | TP > FP |
| name_word_fraction | 0.919 | 0.925 | -0.025 | FP > TP |
| result_elem_fanout | 7.642 | 11.525 | -0.697 | FP > TP |
| result_sent_fanout | 1.696 | 1.275 | +0.347 | TP > FP |
| sent_is_first_quarter | 0.365 | 0.200 | +0.352 | TP > FP |
| sent_is_last_quarter | 0.216 | 0.425 | -0.482 | FP > TP |
| sent_length | 102.723 | 81.450 | +0.473 | TP > FP |
| sent_position_norm | 0.440 | 0.613 | -0.556 | FP > TP |
| sent_word_count | 16.122 | 12.825 | +0.440 | TP > FP |

**Top features by |Cohen's d|:**

- `gold_sent_fanout`: d=+1.175 (large)
- `result_elem_fanout`: d=-0.697 (medium)
- `sent_position_norm`: d=-0.556 (medium)
- `sent_is_last_quarter`: d=-0.482 (small)
- `sent_length`: d=+0.473 (small)

## 3. Per-Project Feature Separability

Cohen's d for top features per project:

| Project | `gold_sent_fanout` | `result_elem_fanout` | `sent_position_norm` | `sent_is_last_quarter` | `sent_length` | `elem_name_length` |
|---------|---------|---------|---------|---------|---------|---------|
| mediastore | N/A | N/A | N/A | N/A | N/A | N/A |
| teastore | N/A | N/A | N/A | N/A | N/A | N/A |
| teammates | +1.20 | +0.10 | -0.72 | -0.52 | +0.86 | -0.03 |
| bigbluebutton | +0.62 | -0.69 | +0.06 | -0.28 | -0.59 | -0.16 |
| jabref | +1.43 | +0.40 | -0.13 | +0.45 | +0.18 | -1.19 |

## 4. Classification Experiments

Can a classifier distinguish TPs from FPs? Using stratified 5-fold CV.

### All features (incl. oracle gold fanout)

| Classifier | Accuracy | AUC-ROC |
|------------|----------|---------|
| Majority baseline | 0.787 | 0.500 |
| Logistic Regression | 0.931 | 0.960 |
| Random Forest | 0.941 | 0.937 |

**RF Feature Importances (top 8):**

- `gold_sent_fanout`: 0.388 ######################################
- `result_elem_fanout`: 0.119 ###########
- `sent_length`: 0.087 ########
- `sent_position_norm`: 0.075 #######
- `sent_word_count`: 0.075 #######
- `jaccard_similarity`: 0.064 ######
- `gold_elem_fanout`: 0.049 ####
- `result_sent_fanout`: 0.043 ####

**LR Coefficients (top 8, positive = predicts TP):**

- `gold_sent_fanout`: +3.935
- `result_sent_fanout`: -2.911
- `result_elem_fanout`: -1.321
- `gold_elem_fanout`: +0.887
- `sent_position_norm`: -0.638
- `best_word_ratio`: -0.624
- `elem_name_word_count`: -0.599
- `jaccard_similarity`: +0.432

### Fair features (no gold, has result fanout)

| Classifier | Accuracy | AUC-ROC |
|------------|----------|---------|
| Majority baseline | 0.787 | 0.500 |
| Logistic Regression | 0.702 | 0.751 |
| Random Forest | 0.809 | 0.713 |

**RF Feature Importances (top 8):**

- `result_elem_fanout`: 0.211 #####################
- `sent_length`: 0.179 #################
- `sent_position_norm`: 0.144 ##############
- `sent_word_count`: 0.126 ############
- `jaccard_similarity`: 0.109 ##########
- `elem_name_length`: 0.084 ########
- `result_sent_fanout`: 0.035 ###
- `best_word_ratio`: 0.022 ##

**LR Coefficients (top 8, positive = predicts TP):**

- `elem_name_word_count`: -0.887
- `sent_position_norm`: -0.809
- `best_word_ratio`: -0.789
- `elem_name_length`: +0.676
- `result_elem_fanout`: -0.638
- `sent_word_count`: +0.543
- `jaccard_similarity`: +0.468
- `camel_word_fraction`: +0.425

### External-only (no gold, no result fanout)

| Classifier | Accuracy | AUC-ROC |
|------------|----------|---------|
| Majority baseline | 0.787 | 0.500 |
| Logistic Regression | 0.660 | 0.706 |
| Random Forest | 0.809 | 0.713 |

**RF Feature Importances (top 8):**

- `sent_length`: 0.207 ####################
- `sent_position_norm`: 0.196 ###################
- `sent_word_count`: 0.157 ###############
- `elem_name_length`: 0.152 ###############
- `jaccard_similarity`: 0.132 #############
- `best_word_ratio`: 0.037 ###
- `best_camel_ratio`: 0.027 ##
- `sent_is_first_quarter`: 0.022 ##

**LR Coefficients (top 8, positive = predicts TP):**

- `elem_name_word_count`: -1.002
- `elem_name_length`: +0.926
- `best_word_ratio`: -0.789
- `sent_position_norm`: -0.762
- `jaccard_similarity`: +0.688
- `sent_word_count`: +0.590
- `camel_word_fraction`: +0.398
- `best_camel_ratio`: -0.236

## 5. Leave-One-Project-Out Cross-Validation

Tests generalization: train on 4 projects, predict on held-out project.
Using external-only features (no oracle info).

| Held-out Project | n_TP | n_FP | LR Acc | LR AUC | RF Acc | RF AUC |
|------------------|------|------|--------|--------|--------|--------|
| mediastore | 17 | 1 | 1.000 | 1.000 | 0.889 | 0.824 |
| teastore | 20 | 0 | N/A (single class) | N/A | N/A | N/A |
| teammates | 49 | 32 | 0.593 | 0.474 | 0.605 | 0.372 |
| bigbluebutton | 44 | 5 | 0.429 | 0.391 | 0.735 | 0.370 |
| jabref | 18 | 2 | 0.600 | 0.292 | 0.900 | 0.250 |

## 6. FP Inspection: What Do False Positives Look Like?

All FP links with key features:

### mediastore (1 FPs)

| Sent# | Element | Exact Match | Name Frac | Best Ratio | Sentence (truncated) |
|-------|---------|-------------|-----------|------------|---------------------|
| 37 | Reencoding | 0 | 0.00 | 0.89 | However, a download can cause re-encoding of the audio file.... |

### teammates (32 FPs)

| Sent# | Element | Exact Match | Name Frac | Best Ratio | Sentence (truncated) |
|-------|---------|-------------|-----------|------------|---------------------|
| 131 | Storage | 1 | 1.00 | 1.00 | storage.api provides the API of the component to be accessed... |
| 79 | Logic | 1 | 1.00 | 1.00 | Managing relationships between entities, e.g. cascade logic ... |
| 158 | Common | 1 | 1.00 | 1.00 | common.exceptions contains custom exceptions.... |
| 130 | Storage | 1 | 1.00 | 1.00 | Package overview contains storage.api, storage.entity, stora... |
| 117 | Logic | 1 | 1.00 | 1.00 | Refer to the API for the cascade logic.... |
| 22 | Logic | 1 | 1.00 | 1.00 | logic, ui.website, ui.controller represent an application of... |
| 127 | Common | 1 | 1.00 | 1.00 | These datatransfer classes are in common.datatransfer packag... |
| 189 | E2E | 1 | 1.00 | 0.50 | e2e.pageobjects contains abstractions of the pages as they a... |
| 173 | Test Driver | 1 | 1.00 | 0.95 | x.testdriver contains component test cases for testing the t... |
| 132 | Storage | 1 | 1.00 | 1.00 | storage.entity contains classes that represent persistable e... |
| 196 | Client | 1 | 1.00 | 1.00 | client.util contains helpers needed for client scripts.... |
| 156 | Common | 1 | 1.00 | 1.00 | Package overview contains common.util, common.exceptions, co... |
| 23 | UI | 1 | 1.00 | 1.00 | ui.website is not a real package.... |
| 157 | Common | 1 | 1.00 | 1.00 | common.util contains utility classes.... |
| 133 | Storage | 1 | 1.00 | 1.00 | storage.search contains classes for dealing with searching a... |
| 85 | Logic | 1 | 1.00 | 1.00 | logic.api provides the API of the component to be accessed b... |
| 119 | Logic | 1 | 1.00 | 1.00 | It contains minimal logic beyond what is directly relevant t... |
| 188 | E2E | 1 | 1.00 | 0.50 | e2e.util contains helpers needed for running E2E tests.... |
| 190 | E2E | 1 | 1.00 | 0.50 | e2e.cases contains test cases.... |
| 159 | Common | 1 | 1.00 | 1.00 | common.datatransfer contains data transfer objects.... |
| 160 | Common | 1 | 1.00 | 1.00 | common.datatransfer package contains lightweight data transf... |
| 86 | Logic | 1 | 1.00 | 1.00 | logic.core contains the core logic of the system.... |
| 125 | Storage | 1 | 1.00 | 1.00 | Classes in the storage.entity package are not visible outsid... |
| 4 | Client | 1 | 1.00 | 1.00 | The UI Browser seen by users consists of Web pages containin... |
| 195 | Client | 1 | 1.00 | 1.00 | Package overview contains client.util, client.remoteapi, cli... |
| 17 | E2E | 1 | 1.00 | 0.50 | Selenium Java is used to automate E2E testing with actual We... |
| 84 | Logic | 1 | 1.00 | 1.00 | Package overview contains logic.api, logic.core.... |
| 26 | UI | 1 | 1.00 | 1.00 | ui.website is not a Java package.... |
| 187 | E2E | 1 | 1.00 | 0.50 | Package overview contains e2e.util, e2e.pageobjects, e2e.cas... |
| 22 | UI | 1 | 1.00 | 1.00 | logic, ui.website, ui.controller represent an application of... |
| 198 | Client | 1 | 1.00 | 1.00 | client.scripts scripts that deal with the back end data for ... |
| 197 | Client | 1 | 1.00 | 1.00 | client.remoteapi classes needed to connect to the back end d... |

### bigbluebutton (5 FPs)

| Sent# | Element | Exact Match | Name Frac | Best Ratio | Sentence (truncated) |
|-------|---------|-------------|-----------|------------|---------------------|
| 68 | HTML5 Server | 0 | 0.50 | 0.67 | Kurento Media Server KMS is a media server that implements b... |
| 74 | WebRTC-SFU | 0 | 0.50 | 0.75 | WebRTC provides the user with high-quality audio with lower ... |
| 18 | HTML5 Server | 0 | 0.50 | 0.67 | Because nodejs was running on a single CPU core, having a 16... |
| 60 | FreeSWITCH | 1 | 1.00 | 1.00 | Communication between apps and FreeSWITCH Event Socket Layer... |
| 5 | WebRTC-SFU | 0 | 0.50 | 0.75 | The HTML5 client is a single page, responsive web applicatio... |

### jabref (2 FPs)

| Sent# | Element | Exact Match | Name Frac | Best Ratio | Sentence (truncated) |
|-------|---------|-------------|-----------|------------|---------------------|
| 5 | logic | 1 | 1.00 | 1.00 | The model represents the most important data structures (Bib... |
| 7 | preferences | 1 | 1.00 | 1.00 | Only the gui knows the user and his preferences and can inte... |

## 7. False Negative Analysis

What gold links did SWATTR miss? Features of FNs vs TPs.

| Feature | TP Mean | FN Mean | Cohen's d | Interpretation |
|---------|---------|---------|-----------|----------------|
| best_camel_ratio | 0.924 | 0.632 | +1.495 | TPs higher |
| best_word_ratio | 0.889 | 0.502 | +2.216 | TPs higher |
| camel_word_fraction | 0.946 | 0.223 | +3.179 | TPs higher |
| elem_is_interface | 0.000 | 0.000 | +0.000 |  |
| elem_name_length | 7.899 | 8.340 | -0.111 |  |
| elem_name_word_count | 1.250 | 1.340 | -0.203 |  |
| exact_name_match | 0.872 | 0.021 | +2.821 | TPs higher |
| gold_elem_fanout | 6.824 | 7.851 | -0.247 |  |
| gold_sent_fanout | 1.716 | 1.383 | +0.276 |  |
| jaccard_similarity | 0.117 | 0.021 | +0.741 | TPs higher |
| name_word_fraction | 0.919 | 0.191 | +2.771 | TPs higher |
| result_elem_fanout | 7.642 | 4.000 | +0.678 | TPs higher |
| result_sent_fanout | 1.696 | 0.298 | +1.158 | TPs higher |
| sent_is_first_quarter | 0.365 | 0.277 | +0.185 |  |
| sent_is_last_quarter | 0.216 | 0.298 | -0.192 |  |
| sent_length | 102.723 | 102.468 | +0.006 |  |
| sent_position_norm | 0.440 | 0.552 | -0.367 |  |
| sent_word_count | 16.122 | 16.660 | -0.071 |  |

Total FNs: **47** across all projects

**FN breakdown by project:**

- **mediastore**: 14 FNs
  - S25 x MediaAccess: exact=0, name_frac=0.00, best_ratio=0.73
  - S32 x DB: exact=0, name_frac=0.00, best_ratio=0.40
  - S23 x DB: exact=0, name_frac=0.00, best_ratio=0.40
  - S20 x Reencoding: exact=0, name_frac=0.00, best_ratio=0.74
  - S36 x ?: exact=0, name_frac=0.00, best_ratio=0.29
  - ... and 9 more
- **teastore**: 7 FNs
  - S26 x Persistence: exact=0, name_frac=0.00, best_ratio=0.31
  - S23 x Persistence: exact=0, name_frac=0.00, best_ratio=0.53
  - S8 x WebUI: exact=0, name_frac=0.00, best_ratio=0.57
  - S6 x WebUI: exact=0, name_frac=0.00, best_ratio=0.31
  - S28 x Recommender: exact=0, name_frac=0.00, best_ratio=0.47
  - ... and 2 more
- **teammates**: 8 FNs
  - S78 x Logic: exact=0, name_frac=0.00, best_ratio=0.43
  - S120 x Storage: exact=0, name_frac=0.00, best_ratio=0.40
  - S119 x Storage: exact=0, name_frac=0.00, best_ratio=0.44
  - S19 x Client: exact=0, name_frac=0.00, best_ratio=0.50
  - S141 x ?: exact=0, name_frac=0.00, best_ratio=0.22
  - ... and 3 more
- **bigbluebutton**: 18 FNs
  - S79 x HTML5 Client: exact=0, name_frac=0.50, best_ratio=0.67
  - S10 x HTML5 Client: exact=0, name_frac=0.50, best_ratio=0.67
  - S19 x HTML5 Client: exact=0, name_frac=1.00, best_ratio=0.63
  - S11 x HTML5 Client: exact=0, name_frac=0.50, best_ratio=0.67
  - S69 x ?: exact=0, name_frac=0.00, best_ratio=0.33
  - ... and 13 more

## 8. Synthesis

### Verdict: **MODERATELY SEPARABLE**

- External-only RF AUC: **0.713**
- All-features RF AUC: **0.937**

Meaningful signal exists (AUC 0.7-0.8). A classifier could identify some FPs but at the cost of also removing TPs.

### Key Findings

1. **Most discriminative features** (by effect size):
   - `gold_sent_fanout` (d=+1.175)
   - `result_elem_fanout` (d=-0.697)
   - `sent_position_norm` (d=-0.556)

2. **Name-matching features alone**: AUC = 0.668

3. **Implications for SWATTR improvement**:

   Some FPs are systematically distinguishable from TPs.
   The most useful features for a post-hoc filter would be:
   - `gold_sent_fanout`
   - `result_elem_fanout`
   - `sent_position_norm`

