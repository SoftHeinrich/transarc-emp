# RQ2 doc-to-model — non-leaky Top-3 ranking comparison (R1 vs R2)

Companion to `RQ2_DOC_TO_MODEL_PRESTUDY.md`. The original doc-to-model Top-3 baseline ranks components by **gold-link count**, which leaks the answer. This report re-runs Top-3 with two non-leaky rankings and compares them to the leaky R0 (reference) and Random.

**Rankings.**

- **R0 — Gold-link count (LEAKY, reference only).** Top-3 = the 3 components with the most gold (sentence, component) links.
- **R1 — File count.** Top-3 = the 3 components with the most enrolled files in the architecture model (built from the SAM-CODE gold standard, used as a public component-structure inventory — no SAD-SAM gold used).
- **R2 — Name frequency in the doc.** Top-3 = the 3 components whose display names appear in the most distinct doc sentences. Matching rule: case-insensitive substring match of the lowercased display name (after the `"<TypeTag>: "` prefix is stripped, if present); each sentence contributes at most 1 to a component's score; components whose normalized display name is shorter than 3 characters are filtered out.
- **Random.** `random.Random(42)`; samples (sentence, component) pairs uniformly from `gold_sents x all_components` until the prediction count matches the gold link count.

For all 3 ranking-based predictions (R0, R1, R2), the prediction rule is identical: for every **gold sentence** (sentence with >= 1 gold link) predict the chosen 3 components. Sentences with no gold links are not predicted on (matches the existing pre-study so numbers are directly comparable).

## 1. Per-baseline metrics

### 1.1 Random

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.065 | 0.074 | 0.088 | 0.048 | 0.333 | **0.122** |
| Per-component F1 (macro) | 0.047 | 0.038 | 0.053 | 0.018 | 0.265 | **0.084** |
| Per-sentence F1 (macro) | 0.074 | 0.051 | 0.068 | 0.038 | 0.287 | **0.104** |
| Sentence coverage | 0.074 | 0.087 | 0.111 | 0.062 | 0.600 | **0.187** |
| Noise rate | 0.913 | 0.956 | 0.889 | 0.946 | 0.607 | **0.862** |

### 1.2 R0 (gold-link count, leaky)

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.286 | 0.354 | 0.354 | 0.330 | 0.583 | **0.381** |
| Per-component F1 (macro) | 0.098 | 0.197 | 0.150 | 0.103 | 0.379 | **0.185** |
| Per-sentence F1 (macro) | 0.274 | 0.352 | 0.338 | 0.314 | 0.530 | **0.362** |
| Sentence coverage | 0.519 | 0.739 | 0.644 | 0.542 | 0.700 | **0.629** |
| Noise rate | 0.802 | 0.754 | 0.748 | 0.764 | 0.533 | **0.720** |

### 1.3 R1 (file count)

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.125 | 0.354 | 0.094 | 0.087 | 0.583 | **0.249** |
| Per-component F1 (macro) | 0.034 | 0.197 | 0.033 | 0.028 | 0.379 | **0.134** |
| Per-sentence F1 (macro) | 0.119 | 0.339 | 0.089 | 0.088 | 0.530 | **0.233** |
| Sentence coverage | 0.259 | 0.609 | 0.200 | 0.188 | 0.700 | **0.391** |
| Noise rate | 0.914 | 0.754 | 0.933 | 0.938 | 0.533 | **0.814** |

### 1.4 R2 (name freq in doc)

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref | **macro mean** |
|---|---|---|---|---|---|---|
| Micro F1 (sentence, component) | 0.214 | 0.229 | 0.156 | 0.204 | 0.583 | **0.277** |
| Per-component F1 (macro) | 0.077 | 0.110 | 0.050 | 0.059 | 0.379 | **0.135** |
| Per-sentence F1 (macro) | 0.211 | 0.226 | 0.149 | 0.197 | 0.530 | **0.263** |
| Sentence coverage | 0.444 | 0.478 | 0.333 | 0.417 | 0.700 | **0.475** |
| Noise rate | 0.852 | 0.841 | 0.889 | 0.854 | 0.533 | **0.794** |

## 2. Head-to-head: micro F1 (all baselines)

| Project | Random | R0 (leaky) | R1 (file count) | R2 (name freq) |
|---|---|---|---|---|
| mediastore | 0.065 | 0.286 | 0.125 | 0.214 |
| teastore | 0.074 | 0.354 | 0.354 | 0.229 |
| teammates | 0.088 | 0.354 | 0.094 | 0.156 |
| bigbluebutton | 0.048 | 0.330 | 0.087 | 0.204 |
| jabref | 0.333 | 0.583 | 0.583 | 0.583 |
| **macro mean** | **0.122** | **0.381** | **0.249** | **0.277** |

### 2b. Same head-to-head — per-component macro F1

| Project | Random | R0 (leaky) | R1 (file count) | R2 (name freq) |
|---|---|---|---|---|
| mediastore | 0.047 | 0.098 | 0.034 | 0.077 |
| teastore | 0.038 | 0.197 | 0.197 | 0.110 |
| teammates | 0.053 | 0.150 | 0.033 | 0.050 |
| bigbluebutton | 0.018 | 0.103 | 0.028 | 0.059 |
| jabref | 0.265 | 0.379 | 0.379 | 0.379 |
| **macro mean** | **0.084** | **0.185** | **0.134** | **0.135** |

### 2c. Same head-to-head — sentence coverage

| Project | Random | R0 (leaky) | R1 (file count) | R2 (name freq) |
|---|---|---|---|---|
| mediastore | 0.074 | 0.519 | 0.259 | 0.444 |
| teastore | 0.087 | 0.739 | 0.609 | 0.478 |
| teammates | 0.111 | 0.644 | 0.200 | 0.333 |
| bigbluebutton | 0.062 | 0.542 | 0.188 | 0.417 |
| jabref | 0.600 | 0.700 | 0.700 | 0.700 |
| **macro mean** | **0.187** | **0.629** | **0.391** | **0.475** |

## 3. Diagnostic — selected Top-3 components per ranking

Each cell lists the 3 selected components for the given (project, ranking). Format: ``display_name (rank_score)``. Score = gold-link count for R0, enrolled file count for R1, in-doc name-frequency (sentences-with-substring) for R2.

### 3.1 mediastore

| Ranking | Pick #1 | Pick #2 | Pick #3 |
|---|---|---|---|
| R0 (gold-link count) | db (7) | mediaaccess (5) | mediamanagement (4) |
| R1 (file count) | idownload (16) | imediaaccess (6) | db (4) |
| R2 (name freq in doc) | mediaaccess (3) | mediamanagement (3) | facade (3) |

### 3.2 teastore

| Ranking | Pick #1 | Pick #2 | Pick #3 |
|---|---|---|---|
| R0 (gold-link count) | webui (6) | persistence (6) | registry (5) |
| R1 (file count) | imageprovider (64) | persistence (30) | webui (19) |
| R2 (name freq in doc) | registry (5) | webui (4) | persistence (3) |

### 3.3 teammates

| Ranking | Pick #1 | Pick #2 | Pick #3 |
|---|---|---|---|
| R0 (gold-link count) | logic (15) | storage (10) | ui (9) |
| R1 (file count) | ui (348) | ui (348) | common (150) |
| R2 (name freq in doc) | logic (22) | logic (22) | storage (14) |

### 3.4 bigbluebutton

| Ranking | Pick #1 | Pick #2 | Pick #3 |
|---|---|---|---|
| R0 (gold-link count) | html5 client (14) | html5 server (13) | freeswitch (7) |
| R1 (file count) | freeswitch (94) | freeswitch (94) | fsesl (92) |
| R2 (name freq in doc) | freeswitch (8) | freeswitch (8) | html5 client (5) |

### 3.5 jabref

| Ranking | Pick #1 | Pick #2 | Pick #3 |
|---|---|---|---|
| R0 (gold-link count) | model (6) | gui (4) | logic (4) |
| R1 (file count) | logic (972) | gui (707) | model (250) |
| R2 (name freq in doc) | model (6) | logic (5) | gui (4) |

## 4. Set overlap with R0 (leaky reference)

How many of R1's / R2's Top-3 picks are also in R0's Top-3? If |R1 ∩ R0| is consistently 3/3, file count is essentially equivalent to gold-link count as a ranking signal and R1 is the simpler swap. If the overlap is low, R1 picks may differ enough that the inflation pattern shifts.

| Project | |R1 ∩ R0| / 3 | |R2 ∩ R0| / 3 | |R1 ∩ R2| / 3 |
|---|---|---|---|
| mediastore | 1/3 | 2/3 | 0/3 |
| teastore | 2/3 | 2/3 | 1/3 |
| teammates | 1/3 | 1/3 | 0/3 |
| bigbluebutton | 1/3 | 2/3 | 2/3 |
| jabref | 3/3 | 3/3 | 3/3 |
| **mean** | **1.60/3** | **2.00/3** | **1.20/3** |

## 5. Verdict

**Q1 — Does R1 (file count) still expose the popularity-skew bias?** R1 mean micro F1 = **0.249** vs Random **0.122** (2.0x). Yes — it inflates Top-3 well above Random.

**Q2 — Does R2 (name frequency) still expose it?** R2 mean micro F1 = **0.277** vs Random **0.122** (2.3x). Yes — R2 also inflates Top-3 above Random.

**Q3 — Which is closer to R0 (leaky reference, 0.381)?** R1 sits at **0.249** (|R1-R0| = 0.133); R2 sits at **0.277** (|R2-R0| = 0.104). **R2** is closer to R0 in macro mean micro F1.

**Q4 — Overlap with R0's picks.** Mean |R1 ∩ R0| = **1.60/3**, mean |R2 ∩ R0| = **2.00/3**. R1 differs noticeably from R0 — R2 may be a better proxy for the leaky baseline.

**Q5 — Final recommendation.** **Use R1 (file count).** Both R1 and R2 expose the bias; R1 is the simpler, leak-free choice and aligns with the doc-to-code pre-study's signal source. R2 can be cited in a footnote as a secondary check.

---

Script: `src/bias/rq2_doc_to_model_ranking_compare.py`. Reproduce: `python3 src/bias/rq2_doc_to_model_ranking_compare.py`.
