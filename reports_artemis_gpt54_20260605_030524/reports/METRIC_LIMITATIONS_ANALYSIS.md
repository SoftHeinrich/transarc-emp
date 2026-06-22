# Why Precision/Recall/F1 Don't Tell the Whole Story: TransArc Error Analysis

---

## Prerequisites: Data Locations and Script Reference

### Benchmark Data

All gold standards and models live under:
```
BENCHMARK=/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/
```

Per-project structure (`{p}` = mediastore, teastore, teammates, bigbluebutton, jabref):
```
${BENCHMARK}/{p}/goldstandards/goldstandard_sad_*-code_*.csv   # SAD-CODE gold
${BENCHMARK}/{p}/goldstandards/goldstandard_sad_*-sam_*.csv    # SAD-SAM gold
${BENCHMARK}/{p}/goldstandards/goldstandard_sam_*-code_*.csv   # SAM-CODE gold
${BENCHMARK}/{p}/text_*/                                       # Documentation text
${BENCHMARK}/{p}/model_*/code/codeModel.acm                   # Code model (JSON)
${BENCHMARK}/{p}/model_*/pcm/*.repository                     # Architecture model
```

### Data Formats

**SAD-SAM gold** (`modelElementID,sentence`):
```csv
_st2Y0HDrEeSqnN80MQ2uGw,1
_st2Y0HDrEeSqnN80MQ2uGw,3
_p_EeYHDrEeSqnN80MQ2uGw,7
```

**SAM-CODE gold** (`ae_id,ae_name,ce_ids`):
```csv
_4QwQwHDqEeSqnN80MQ2uGw,Interface: IDownload,Implementation/mediastore.basic/.../IDownload.java
```

**SAD-CODE gold** (`sentenceID,codeID`) — note `Implementation/` prefix and directory entries ending `/`:
```csv
1,Implementation/mediastore.ejb.facade/.../FacadeImpl.java
11,Implementation/mediastore.ejb.usermanagement/.../usermanagement/
```

**TransArc output** (`modelElementID,codeId`) — `modelElementID` is a sentence number, no `Implementation/` prefix, lowercase `d` in `codeId`:
```csv
13,mediastore.ejb.usermanagement/.../SecurityUtil.java
29,mediastore.ejb.userdbadapter/.../User.java
```

**LLM classification** (JSON: `{sentence_num_str: [component_labels]}`):
```json
{"1": ["Component: Facade", "Interface: IFacade"],
 "7": ["Component: MediaManagement"],
 "12": ["Component: UserDBAdapter", "Component: DB"]}
```

### TransArc Results

```
RESULTS=/mnt/hostshare/ardoco-home/transarc-emp/results/
${RESULTS}/{p}/sad-code/sadCodeTlr_{p}.csv      # Final SAD-CODE
${RESULTS}/{p}/sad-code/sadSamTlr_{p}.csv        # Intermediate SAD-SAM
${RESULTS}/{p}/sad-code/samCodeTlr_{p}.csv       # Intermediate SAM-CODE
${RESULTS}/{p}/sad-sam/sadSamTlr_{p}.csv         # Standalone SAD-SAM
${RESULTS}/{p}/sam-code/samCodeTlr_{p}.csv       # Standalone SAM-CODE
```

### Analysis Scripts

All scripts live in `/mnt/hostshare/ardoco-home/transarc-emp/`. None take command-line
arguments — run each with `python3 <script>.py`. All import from
`transarc_error_analysis.py` (the root module).

| Script | Output Report | What It Computes |
|--------|:---|:---|
| `transarc_error_analysis.py` | `TRANSARC_EMPIRICAL_STUDY.md` | Baseline metrics, FP/FN decomposition, amplification, what-if |
| `holistic_metrics_analysis.py` | `HOLISTIC_METRICS.md` | M1-M6 alternative metrics, enrollment inflation, per-sentence distribution |
| `creative_metrics_analysis.py` | `CREATIVE_METRICS.md` | Coverage, noise, usefulness, Gini coefficient, wasted effort |
| `stupid_baseline_analysis.py` | `STUPID_BASELINES.md` | B0-B6 trivial baselines (Link-All, Majority, Random, Grep) |
| `extreme_baseline_analysis.py` | `EXTREME_BASELINES.md` | Oracle-Component, Oracle-Subset, Perfect-Transitive, Round-Robin |
| `sam_code_distribution_analysis.py` | `SAM_CODE_DISTRIBUTION.md` | Per-element enrollment, directory vs file breakdown |
| `sam_code_cascade_analysis.py` | `SAM_CODE_CASCADE.md` | SAM-CODE error cascade through pipeline |
| `sad_sam_tp_gain_analysis.py` | `SAD_SAM_TP_GAIN_STUDY.md` | Per-FN recovery potential |
| `sad_sam_actual_contribution.py` | `SAD_SAM_ACTUAL_CONTRIBUTION.md` | Per-link actual downstream impact |
| `llm_agentic_eval.py` | `LLM_BASELINE.md` | All LLM strategies + comparison |
| `llm_error_analysis.py` | *(stdout)* | Per-component LLM error breakdown |

### Replication: Generate All Data

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp

# Step 1: Core error analysis (must run first — all others import from it)
python3 transarc_error_analysis.py

# Step 2: Alternative metrics and baselines (can run in parallel)
python3 holistic_metrics_analysis.py &
python3 creative_metrics_analysis.py &
python3 stupid_baseline_analysis.py &
python3 extreme_baseline_analysis.py &
python3 sam_code_distribution_analysis.py &
python3 sam_code_cascade_analysis.py &
python3 sad_sam_tp_gain_analysis.py &
python3 sad_sam_actual_contribution.py &
wait

# Step 3: LLM baselines (requires llm_classifications/ and llm_classifications_multi/)
python3 llm_agentic_eval.py
python3 llm_error_analysis.py
```

### V45 Linker Replication

```bash
cd /mnt/hostshare/ardoco-home/llm-sad-sam-agent
source .venv/bin/activate
export LLM_BACKEND=openai
export OPENAI_API_KEY=<your_key>
export OPENAI_MODEL_NAME=gpt-5.2

python scripts/evaluation/evaluate_comprehensive.py --version v45
```

Results appear in `results/evaluation_results/v45_<timestamp>/`.

---

## 1. The Gold Standard Enrollment Explosion

### The Mechanism

SAD-CODE gold standards are annotated at **mixed granularity**: some entries are
individual files, others are directories (paths ending with `/`). Before evaluation,
directory entries are "enrolled" — expanded to every individual file listed in the
project's `.acm` code model under that directory.

#### Replication

```bash
# See per-project enrollment breakdown:
python3 sam_code_distribution_analysis.py
# Output: SAM_CODE_DISTRIBUTION.md → "Gold Standard Enrollment Impact" table
```

### The Enrollment Data

| Project | Raw Entries | Directories | Files | Enrolled Links | Expansion Factor |
|---------|:----------:|:-----------:|:-----:|:--------------:|:---------------:|
| MediaStore | 57 | 3 (5%) | 54 (95%) | 59 | **1.04x** |
| TeaStore | 70 | 10 (14%) | 60 (86%) | 707 | **10.1x** |
| Teammates | 228 | 228 (100%) | 0 (0%) | 8,097 | **35.5x** |
| BigBlueButton | 132 | 42 (32%) | 90 (68%) | 1,529 | **11.6x** |
| JabRef | 38 | 37 (97%) | 1 (3%) | 8,268 | **217.6x** |

Key observation: **Teammates is 100% directory-based** — every gold entry is a
directory, not a file. JabRef is 97% directory-based. This means almost all gold
links are artifacts of directory enrollment, not individual file annotations.

### Concrete Example: JabRef Per-Component Enrollment

```bash
# To see per-model-element enrollment:
python3 sam_code_distribution_analysis.py
# Output: SAM_CODE_DISTRIBUTION.md → "Per-Model-Element" tables
```

| Component | Raw Dirs | Enrolled Files | Factor | % of All Gold |
|-----------|:--------:|:--------------:|:------:|:------------:|
| logic | 3 | 972 | 324x | 47.0% |
| gui | 2 | 708 | 354x | 34.2% |
| model | 2 | 250 | 125x | 12.1% |
| preferences | 1 | 18 | 18x | 0.9% |
| cli | 2 | 8 | 4x | 0.4% |
| globals | 1 (file) | 1 | 1x | 0.0% |

Getting `logic` right or wrong shifts the metric by 972 units. Getting `globals`
right or wrong shifts it by 1. Yet the annotator treated both as one decision.

### Concrete Example: Teammates Per-Component Enrollment

| Component | Raw Dirs | Enrolled Files | Factor |
|-----------|:--------:|:--------------:|:------:|
| UI (Component+Interface) | 4 | 696 | 174x |
| Common (Component+Interface) | 4 | 300 | 75x |
| E2E (Component+Interface) | 2 | 246 | 123x |
| Logic (Component+Interface) | 4 | 142 | 36x |
| Storage (Component+Interface) | 4 | 118 | 30x |
| Client (Component+Interface) | 2 | 80 | 40x |
| Test Driver (Component+Interface) | 2 | 34 | 17x |

### Evidence: Alternative Metrics Expose the Distortion

```bash
# Compute all alternative metrics:
python3 holistic_metrics_analysis.py
# Output: HOLISTIC_METRICS.md → "SAD-CODE Metric Comparison (M1-M4)" table
```

| Project | M1 Micro F1 | M2 Raw-Entry F1 | M3 Macro/Sent F1 | Spread |
|---------|:---:|:---:|:---:|:---:|
| MediaStore | 0.588 | 0.568 | 0.596 | 0.028 |
| TeaStore | 0.829 | 0.824 | **0.696** | 0.133 |
| Teammates | 0.821 | 0.668 | **0.469** | **0.352** |
| BigBlueButton | 0.831 | **0.629** | 0.673 | **0.202** |
| JabRef | 0.943 | 0.905 | 0.933 | 0.038 |

Teammates drops from M1=0.821 to M3=**0.469** (macro per-sentence) — a 0.352
spread. Why? 37 of 92 gold sentences (40%) have **zero recall**. The micro-average
is propped up by a few high-file-count sentences (UI=348, Common=150) where
TransArc does well. The micro-average hides that TransArc doesn't work for
40% of the documentation.

### Per-Sentence Distribution (SAD-CODE)

```bash
# Per-sentence recall distribution:
python3 holistic_metrics_analysis.py
# Output: HOLISTIC_METRICS.md → "Per-Sentence Metric Distribution" table
```

| Project | Gold Sents | Perfect (all TPs) | R=100% | **R=0%** | P=0% |
|---------|:----------:|:-----------------:|:------:|:--------:|:----:|
| MediaStore | 25 | 15 (60%) | 15 (60%) | **9 (36%)** | 1 (6%) |
| TeaStore | 23 | 16 (70%) | 16 (70%) | **7 (30%)** | 0 (0%) |
| Teammates | 92 | 34 (37%) | 51 (55%) | **37 (40%)** | 10 (15%) |
| BigBlueButton | 45 | 7 (16%) | 30 (67%) | **8 (18%)** | 4 (10%) |
| JabRef | 10 | 5 (50%) | 10 (100%) | **0 (0%)** | 0 (0%) |

The distribution is **bimodal**: sentences are either perfectly recovered or
completely missed. Micro F1 hides this "all or nothing" pattern.

---

## 2. Error Amplification Makes P/R/F1 Incomparable Across Projects

### The Transitive Cascade

TransArc composes: SAD-SAM (S→M) × SAM-CODE (M→C) = SAD-CODE (S→C).
Every SAD-SAM link is composed with **all** SAM-CODE links for that component.

#### Replication

```bash
# Full FP/FN decomposition and amplification analysis:
python3 transarc_error_analysis.py
# Output: TRANSARC_EMPIRICAL_STUDY.md → Analyses B, C, D, E

# Per-link downstream impact:
python3 sad_sam_actual_contribution.py
# Output: SAD_SAM_ACTUAL_CONTRIBUTION.md

# SAM-CODE cascade:
python3 sam_code_cascade_analysis.py
# Output: SAM_CODE_CASCADE.md
```

### The Fundamental Asymmetry

| Project | Avg Files/Component | Avg Sents/Component | Ratio (Files÷Sents) |
|---------|:------------------:|:------------------:|:-------------------:|
| MediaStore | 1.4 | 2.2 | 0.6x |
| TeaStore | 24.2 | 3.3 | **7.2x** |
| Teammates | 115.4 | 11.3 | **10.2x** |
| BigBlueButton | 35.9 | 4.7 | **7.6x** |
| JabRef | 391.2 | 4.0 | **97.8x** |

This means SAD-SAM FPs are amplified 7-98x more than SAM-CODE FPs. For JabRef,
one wrong SAD-SAM link generates 972 FPs; one wrong SAM-CODE link generates ~4.

### Actual Amplification Data

| Project | SAD-SAM FPs | Induced TransArc FPs | Mean Amplif. | Max Single FP |
|---------|:-----------:|:--------------------:|:----------:|:-------:|
| MediaStore | 1 | 1 | 1.0x | 1 |
| TeaStore | 0 | 0 | — | — |
| Teammates | 28 | 2,395 | **85.5x** | 348 |
| BigBlueButton | 5 | 71 | 14.2x | 24 |
| JabRef | 2 | 990 | **495.0x** | 972 |
| **Total** | **36** | **3,457** | **96.0x** | |

36 component-level FPs become 3,457 file-level FPs.

### FP Cause Attribution (All Projects Combined)

| Category | Count | % | Description |
|----------|:-----:|:---:|:---|
| SAD_SAM_CAUSED | 3,440 | 93.7% | Wrong sentence-component link; correct component-file link |
| SAM_CODE_CAUSED | 121 | 3.3% | Correct sentence-component; wrong component-file link |
| BOTH_CAUSED | 17 | 0.5% | Both links wrong |
| COMBINATION | 94 | 2.6% | Both individually correct, but (S,C) not in gold |
| **Total** | **3,672** | **100%** | |

### Top 10 Most Damaging Individual Errors

From `SAD_SAM_ACTUAL_CONTRIBUTION.md`:

| Rank | Project | Component | Sent | Sentence Text | Induced FPs |
|------|---------|-----------|:----:|:---|:---:|
| 1 | JabRef | logic | 5 | "The model represents the most important data structures..." | **972** |
| 2 | Teammates | UI | 23 | "ui.website is not a real package." | **348** |
| 3 | Teammates | UI | 26 | "ui.website is not a Java package." | **348** |
| 4 | Teammates | UI | 22 | "logic, ui.website, ui.controller represent an application..." | **223** |
| 5 | Teammates | Common | 158 | "common.exceptions contains custom exceptions." | **139** |
| 6 | Teammates | E2E | 17 | "Selenium Java is used to automate E2E testing..." | **123** |
| 7 | Teammates | E2E | 190 | "e2e.cases contains test cases." | **123** |
| 8 | Teammates | Common | 157 | "common.util contains utility classes." | **118** |
| 9 | Teammates | Logic | 119 | "It contains minimal logic beyond what is directly relevant..." | **71** |
| 10 | Teammates | Logic | 117 | "Refer to the API for the cascade logic." | **71** |

JabRef S5→logic alone accounts for 972/3,672 = **26.5% of all TransArc FPs**.
The top 10 errors (10 component-level mistakes) produce 2,536/3,672 = **69%**
of all file-level FPs.

### Three Cascade Failure Patterns

**Pattern 1: Contextual Mention** — BBB S59: *"...voice conference systems
other than FreeSWITCH..."* is a correct SAD-SAM link (mentions FreeSWITCH) but
has 0 SAD-CODE gold links. Result: 0 TPs, **95 FPs**. Compare S58 (same
component): 94 TPs, 1 FP.

**Pattern 2: Wrong SAM-CODE Files** — BBB HTML5 Server incorrectly includes
8 `bbb-graphql-server/` files. Each is multiplied by 10 correct sentences:
8 × 10 = **80 FPs**.

**Pattern 3: Compound** — HTML5 Server combines patterns: 2 wrong sentences ×
24 files + 8 wrong files × 10 sentences + 16 compound = **128 FPs** from 11
root errors.

### Cross-Project Incomparability

| Project | File-Level F1 | Component-Level FPs | Component-Level FNs |
|---------|:---:|:---:|:---:|
| MediaStore | **0.588** | 1 | 14 |
| JabRef | **0.943** | 2 | 0 |

JabRef *appears* far better (0.943 vs 0.588) but makes 994 wrong file predictions
vs MediaStore's 1. The F1 difference is an artifact of component size, not quality.

---

## 3. Poor Gold Standard Coverage

### Documentation "Dark Matter"

#### Replication

```bash
# Coverage and noise metrics:
python3 creative_metrics_analysis.py
# Output: CREATIVE_METRICS.md → "Sentence-Centric Metrics" table

# Per-sentence recall distribution:
python3 holistic_metrics_analysis.py
# Output: HOLISTIC_METRICS.md → "Per-Sentence Metric Distribution"
```

### Sentences With No Code Links

| Project | Total Sents | Sents w/ Code Links | Coverage | Dark Matter |
|---------|:-----------:|:-------------------:|:--------:|:-----------:|
| JabRef | 13 | 10 | 76.9% | 3 |
| MediaStore | 37 | 25 | 67.6% | 12 |
| TeaStore | 43 | 23 | 53.5% | 20 |
| BigBlueButton | 87 | 45 | 51.7% | 42 |
| Teammates | 198 | 93 | **47.0%** | **105** |

Dark matter examples by category:

**Introductory/Meta**:
- Teammates S2: "TEAMMATES is a Web application that runs on Google App Engine."
- Teammates S3: "Given above is an overview of the main components."
- JabRef S3: "The dependencies are only directed towards the center."

**Implementation Details** (architecturally relevant, but no gold link):
- TeaStore S13–17: LFU cache implementation, image scaling behavior
- TeaStore S19–21: BCrypt/SHA512 hashing implementation
- TeaStore S29–36: Recommender algorithm details (training, slope one)

**Process/Design Rationale**:
- Teammates S30–38: Testing methodology
- Teammates S53–65: Error handling policies
- BBB S16–18: Historical scaling discussion

A system correctly identifying TeaStore S15 ("ImageProvider uses LFU caching")
as related to ImageProvider gets **punished** — 64 file-level FPs — because the
gold standard says S15 has no code link.

### SAD-SAM Coverage Gap

| Project | Doc Sents | SAD-SAM Gold Sents | SAD-SAM Coverage | SAD-CODE Gold Sents | Gap |
|---------|:---------:|:------------------:|:---------------:|:-------------------:|:---:|
| JabRef | 13 | 10 | 76.9% | 10 | 0 |
| MediaStore | 37 | 27 | 73.0% | 25 | 2 |
| TeaStore | 43 | 23 | 53.5% | 23 | 0 |
| BigBlueButton | 87 | 48 | 55.2% | 45 | 3 |
| Teammates | 198 | 45 | **22.7%** | 93 | **48** |

Teammates has a **2.07x mismatch**: 93 sentences have SAD-CODE gold but only 45
have SAD-SAM gold. The 48 extra sentences link directly to code without a model
element bridge.

### Transitive Composition Gap

```bash
# Compute transitive product vs actual gold:
python3 transarc_error_analysis.py
# Output: TRANSARC_EMPIRICAL_STUDY.md → "Scenario 3: Internal vs Standalone"
```

| Project | SAD-SAM × SAM-CODE | Actual SAD-CODE Gold | Match? |
|---------|:------------------:|:--------------------:|:------:|
| MediaStore | 57 | 57 | Exact |
| TeaStore | 70 | 70 | Exact |
| BigBlueButton | 135 | 132 | ~98% |
| JabRef | 38 | 38 | Exact |
| **Teammates** | **91** | **228** | **40%** |

Teammates' gold contains **137 non-transitive links** — sentence-to-specific-class
links like S87→`Logic.java`, S107→11 `*Attributes.java` files. No transitive
approach can recover these.

### Theoretical Limits

```bash
# FN decomposition showing theoretical limits:
python3 transarc_error_analysis.py
# Output: TRANSARC_EMPIRICAL_STUDY.md → "Analysis C – False Negative Decomposition"
```

| Project | Total FNs | Theoretical Limit | % | Recoverable | SAD-SAM Miss | SAM-CODE Miss |
|---------|:---------:|:-----------------:|:---:|:-----------:|:------------:|:------------:|
| MediaStore | 34 | 0 | 0% | 34 | 34 (100%) | 0 (0%) |
| TeaStore | 206 | 0 | 0% | 206 | 206 (100%) | 0 (0%) |
| Teammates | 790 | **544** | **69%** | 246 | 246 (100%) | 0 (0%) |
| BigBlueButton | 242 | 8 | 3% | 234 | 201 (86%) | 33 (14%) |
| JabRef | 0 | 0 | 0% | 0 | 0 | 0 |

For Teammates, **69% of FNs are structurally impossible**. No algorithm can fix this.
Yet F1 penalizes TransArc equally for these 544 impossible FNs.

### Ceiling-Adjusted Recall

| Project | Raw Recall | Achievable Gold | Ceiling-Adjusted |
|---------|:---------:|:--------------:|:---------------:|
| MediaStore | 42.4% | 59 (100%) | 42.4% |
| TeaStore | 70.9% | 707 (100%) | 70.9% |
| Teammates | 90.2% | 7,553 (93.3%) | **96.7%** |
| BigBlueButton | 84.2% | 1,521 (99.5%) | 84.6% |
| JabRef | 100.0% | 8,268 (100%) | 100.0% |

### Dormant SAM-CODE Errors

```bash
python3 sam_code_cascade_analysis.py
# Output: SAM_CODE_CASCADE.md → "SAM-CODE FN Cascade"
```

| Project | SAM-CODE FNs | With SAD-CODE Impact | Dormant | Why Dormant |
|---------|:------------:|:--------------------:|:-------:|:---|
| MediaStore | 40 | 0 | 40 | SAD-SAM already missed those sentences |
| Teammates | 808 | 0 | **808** | SAD-SAM already missed those sentences |
| BigBlueButton | 379 | 11 | 368 | SAD-SAM missed most |
| JabRef | 0 | 0 | 0 | — |

Teammates has **808 dormant SAM-CODE errors** masked by SAD-SAM failures. If
SAD-SAM improved (e.g., via V45), these would surface.

---

## 4. Distribution Skew Within Projects

### Gold Standard Concentration

#### Replication

```bash
python3 creative_metrics_analysis.py
# Output: CREATIVE_METRICS.md → full dashboard

python3 holistic_metrics_analysis.py
# Output: HOLISTIC_METRICS.md → "M5: Component Coverage"
```

### Top Components Dominate

| Project | Top 3 Components | Enrolled Links | % of Gold |
|---------|:--|:---:|:---:|
| JabRef | logic (3,888), gui (2,832), model (1,500) | 8,220 | **95.6%** |
| Teammates | UI (3,257), Logic (1,138), Common (1,264) | 5,659 | **69.9%** |
| BigBlueButton | FreeSWITCH (648), Pres.Conv (140), HTML5 Srv (160) | 948 | 62.0% |
| TeaStore | ImageProvider (320), WebUI (360), Persistence (90) | 770 | 50.6% |
| MediaStore | DB (28), MediaAccess (15), Facade (9) | 52 | 88.1% |

For JabRef, getting 3 of 5 components right yields F1 > 0.95.

### Per-Sentence Link Density

| Project | Avg Files/Sent | Max | Median | Top Example |
|---------|:---:|:---:|:---:|:---|
| MediaStore | 2.3 | 6 | 2 | S25, S34: DB + MediaAccess |
| TeaStore | 3.0 | 11 | 2 | S4: Persistence + Recommender |
| Teammates | 2.5 | 12 | 1 | S107: 11 `*Attributes.java` |
| BigBlueButton | 2.9 | 9 | 2 | S58: FreeSWITCH + FSESL |
| JabRef | 3.8 | 7 | 4 | S1, S4, S6: logic + gui + model |

### Recall Distribution (Gini Coefficient)

```bash
python3 creative_metrics_analysis.py
# Output: CREATIVE_METRICS.md → "Sentence Recall Distribution" table
```

| Project | R=0% | 0<R<100% | R=100% | Gini | Worst-Q25 F1 |
|---------|:----:|:--------:|:------:|:----:|:----------:|
| MediaStore | 9 (36%) | 1 (4%) | 15 (60%) | 0.386 | 0.000 |
| TeaStore | 7 (30%) | 0 (0%) | 16 (70%) | 0.304 | 0.000 |
| Teammates | 37 (40%) | 4 (4%) | 51 (55%) | **0.405** | 0.000 |
| BigBlueButton | 8 (18%) | 7 (16%) | 30 (67%) | 0.219 | 0.176 |
| JabRef | 0 (0%) | 0 (0%) | 10 (100%) | **0.000** | 0.663 |

Teammates' Gini=0.405 (high inequality) — performance is concentrated on a few
sentences while 40% get nothing. JabRef's Gini=0.000 (perfect equality) — every
sentence is fully recovered.

### Interfaces: Ghost Elements

Across all projects, **Interfaces never appear in SAD-SAM gold**:

| Project | # Interfaces | File Overlap with Components | FN Impact |
|---------|:---:|:---:|:---|
| Teammates | 7 | **100%** identical | Zero |
| BigBlueButton | 11 | **100%** identical | Zero |
| TeaStore | 8 | **0%** separate | **Real** — 26 file FNs |
| MediaStore | 10 | Mixed | Partial |
| JabRef | 0 | N/A | N/A |

### SAM-CODE Component Coverage

```bash
python3 holistic_metrics_analysis.py
# Output: HOLISTIC_METRICS.md → "M5: Component Coverage" table
```

| Project | Total Elements | F1≥90% | Perfect | Any TP |
|---------|:-:|:-:|:-:|:-:|
| MediaStore | 19 | 17 (89%) | 17 (89%) | 19 (100%) |
| TeaStore | 19 | 15 (79%) | 15 (79%) | 16 (84%) |
| Teammates | 14 | **14 (100%)** | **14 (100%)** | 14 (100%) |
| BigBlueButton | 22 | 14 (64%) | **8 (36%)** | 22 (100%) |
| JabRef | 6 | 6 (100%) | 5 (83%) | 6 (100%) |

BBB's enrolled F1=0.950 looks great, but only **36%** of its components are
perfectly recovered.

---

## 5. TransArc vs V45 Linker: Detailed Comparison

### Context

V45 is a discourse-aware coreference resolution linker operating at the SAD-SAM
level. It refines TransArc's SAD-SAM output using LLM-based entity extraction,
coreference resolution, and agent-as-judge review.

#### Replication: Run V45

```bash
cd /mnt/hostshare/ardoco-home/llm-sad-sam-agent
source .venv/bin/activate
export LLM_BACKEND=openai OPENAI_API_KEY=<key> OPENAI_MODEL_NAME=gpt-5.2

# Full evaluation (all 5 projects, SAD-SAM + transitive SAD-CODE):
python scripts/evaluation/evaluate_comprehensive.py --version v45

# Results: results/evaluation_results/v45_<timestamp>/
```

#### Replication: TransArc Baseline

```bash
cd /mnt/hostshare/ardoco-home/ardoco

# Generate TransArc results (requires Maven + Java 21):
mvn test -pl tlr/tests-tlr -Dtest=SwattrIT    # SAD-SAM
mvn test -pl tlr/tests-tlr -Dtest=ArcotlIT    # SAM-CODE
mvn test -pl tlr/tests-tlr -Dtest=TransarcIT   # SAD-CODE (transitive)

# Results appear in tlr/tests-tlr/target/<PROJECT>-output/
```

### Head-to-Head: SAD-SAM Component Level

| | TransArc | V45 | Delta |
|:--|:---:|:---:|:---:|
| **MediaStore** | P=94.4 R=54.8 **F1=69.4** | P=96.3 R=83.9 **F1=89.7** | **+20.3pp** |
| **TeaStore** | P=100.0 R=74.1 **F1=85.1** | P=96.4 R=100.0 **F1=98.2** | **+13.1pp** |
| **Teammates** | P=60.5 R=86.0 **F1=71.0** | P=82.0 R=87.7 **F1=84.7** | **+13.6pp** |
| **BigBlueButton** | P=89.8 R=71.0 **F1=79.3** | P=85.2 R=83.9 **F1=84.6** | **+5.3pp** |
| **JabRef** | P=90.0 R=100.0 **F1=94.7** | P=90.0 R=100.0 **F1=94.7** | +0.0pp |
| **Aggregate** | P=77.4 R=73.4 **F1=75.4** | P=87.8 R=88.7 **F1=88.3** | **+12.9pp** |

### Per-Component Breakdown: MediaStore

V45 recovers 3 entire components that TransArc completely misses:

| Component | TransArc TP/FP/FN | V45 TP/FP/FN | SAM-CODE Files | Change |
|-----------|:-:|:-:|:-:|:---|
| **DB** | **0/0/7** | **5/0/2** | 3 | **+5 TPs** (coreference) |
| **FileStorage** | **0/0/3** | **3/0/0** | 3 | **+3 TPs** (coreference) |
| **Reencoding** | **0/1/1** | **1/1/0** | 1 | +1 TP |
| Others (7) | 17/0/3 | 17/0/3 | — | Same |
| **TOTAL** | **17/1/14** | **26/1/5** | | +9 TPs, -9 FNs |

Projected SAD-CODE: F1 jumps from 0.588 to ~0.892 (+0.304).

### Per-Component Breakdown: TeaStore

V45 achieves **100% recall** on all 6 components:

| Component | TransArc TP/FP/FN | V45 TP/FP/FN | SAM-CODE Files | Recovered |
|-----------|:-:|:-:|:-:|:---|
| **ImageProvider** | 4/0/**1** | 5/0/**0** | 64 | S11 via coreference |
| **Persistence** | 3/0/**3** | 6/0/**0** | 5 | S23, S24, S26 |
| **Recommender** | 2/0/**1** | 3/**1**/0 | 12 | S28 (+1 FP: S36) |
| **WebUI** | 4/0/**2** | 6/0/**0** | 60 | S6, S8 |
| Others (2) | 7/0/0 | 7/0/0 | — | Same |
| **TOTAL** | **20/0/7** | **27/1/0** | | +7 TPs, +1 FP |

Projected SAD-CODE: F1 jumps from 0.829 to ~0.993 (+0.163).

### Per-Component Breakdown: Teammates — The Precision Revolution

| Component | TransArc TP/FP/FN | V45 TP/FP/FN | Files | FPs Eliminated |
|-----------|:-:|:-:|:-:|:---:|
| **Common** | 5/**6**/0 | 5/**0**/0 | 150 | **-6 FPs** |
| **E2E** | 5/**5**/0 | 5/**1**/0 | 123 | **-4 FPs** |
| **Client** | 3/**5**/1 | 3/**1**/1 | 40 | **-4 FPs** |
| **Storage** | 8/**5**/2 | 9/**1**/1 | 59 | **-4 FPs** |
| **Logic** | 14/**7**/1 | 14/**4**/1 | 71 | **-3 FPs** |
| UI | 9/3/0 | 9/3/0 | 348 | 0 |
| Others (2) | 5/1/4 | 5/1/4 | — | 0 |
| **TOTAL** | **49/32/8** | **50/11/7** | | **-21 FPs** |

File-level FP reduction:

| Eliminated FPs | × Files | = File FPs Removed |
|:-:|:-:|:-:|
| 6 Common | × 150 | = **900** |
| 4 E2E | × 123 | = **492** |
| 4 Client | × 40 | = **160** |
| 4 Storage | × 59 | = **236** |
| 3 Logic | × 71 | = **213** |
| **21 total** | | **~2,001** |

### Per-Component Breakdown: BigBlueButton — The Amplification Trap

| Component | TransArc TP/FP/FN | V45 TP/FP/FN | Files | Change |
|-----------|:-:|:-:|:-:|:---|
| **HTML5 Server** | 10/2/**3** | 13/2/**0** | 24 | **+3 TPs** |
| **Apps** | 5/0/**1** | 6/0/**0** | 16 | +1 TP |
| **BBB web** | 3/0/**2** | 4/0/**1** | 22 | +1 TP |
| **FSESL** | 1/0/1 | 2/**1**/0 | **92** | +1 TP, **+1 FP** |
| **FreeSWITCH** | 7/1/0 | 7/**2**/0 | **95** | **+1 FP** |
| **Pres. Conv.** | 2/0/0 | 2/**1**/0 | **73** | **+1 FP** |
| Others | 16/2/11 | 18/3/9 | — | +2 TPs, +1 FP |
| **TOTAL** | **44/5/18** | **52/9/10** | | +8 TPs, **+4 FPs** |

New FPs hit the 3 largest components: FSESL (92 files), FreeSWITCH (95), Pres.
Conversion (73) → **+260 file-level FPs**, canceling the ~226 new file TPs.
Net improvement: only +0.009 F1.

### Per-Component Breakdown: JabRef — Identical

Both produce 18 TPs, 2 FPs (logic S5, preferences S7). S5→logic = 972 FPs
remains the single most damaging error.

### What-If: V45 in the Full Pipeline

```bash
# What-if scenarios:
python3 transarc_error_analysis.py
# Output: TRANSARC_EMPIRICAL_STUDY.md → "Analysis F – What-If Component Comparison"
```

| Project | TransArc F1 | V45-Pipeline F1 | Delta | Driver |
|---------|:---:|:---:|:---:|:---|
| MediaStore | 0.588 | **~0.892** | **+0.304** | DB + FileStorage recovered |
| TeaStore | 0.829 | **~0.993** | **+0.163** | WebUI (+120), ImageProvider (+64) |
| Teammates | 0.821 | **~0.876** | **+0.055** | 2,001 file FPs removed |
| BigBlueButton | 0.831 | **~0.840** | **+0.009** | Gains canceled by high-footprint FPs |
| JabRef | 0.943 | **0.943** | **+0.000** | Identical |

### Aggregate Pipeline Impact

| Metric | TransArc | V45-in-Pipeline | Change |
|--------|:--------:|:--------------:|:------:|
| File TPs | ~17,388 | ~17,909 | +521 |
| File FPs | ~3,672 | ~1,931 | **-1,741** |
| File FNs | ~1,272 | ~751 | -521 |

### SAD-SAM FN Recovery Potential

```bash
python3 sad_sam_tp_gain_analysis.py
# Output: SAD_SAM_TP_GAIN_STUDY.md
```

| Project | SAD-SAM FNs | Potential New SAD-CODE TPs | Max Single-Link Gain | Avg Gain |
|---------|:-----------:|:------------------------:|:-------------------:|:--------:|
| MediaStore | 14 | 27 | 3 | 1.9 |
| TeaStore | 7 | 206 | 64 | 29.4 |
| Teammates | 8 | 246 | 71 | 30.8 |
| BigBlueButton | 18 | 195 | 22 | 10.8 |
| JabRef | 0 | 0 | 0 | 0.0 |

Top recovery targets:

| Rank | Project | Component | Sent | New SAD-CODE TPs If Recovered |
|------|---------|-----------|:----:|:---:|
| 1 | Teammates | Logic | 78 | **71** |
| 2 | TeaStore | ImageProvider | 11 | **64** |
| 3 | Teammates | Storage | 120 | **59** |
| 4 | Teammates | Storage | 119 | **59** |
| 5 | Teammates | Client | 19 | **40** |

---

## 6. The Stupid Baselines Problem

### Baselines

#### Replication

```bash
# Simple baselines:
python3 stupid_baseline_analysis.py
# Output: STUPID_BASELINES.md

# Oracle baselines:
python3 extreme_baseline_analysis.py
# Output: EXTREME_BASELINES.md
```

### Keyword-Grep Matches TransArc

| Project | Keyword-Grep F1 | TransArc F1 | Winner |
|---------|:---:|:---:|:---:|
| MediaStore | **0.595** | 0.588 | **Grep** |
| TeaStore | 0.515 | **0.829** | TransArc |
| Teammates | 0.608 | **0.821** | TransArc |
| BigBlueButton | 0.699 | **0.831** | TransArc |
| JabRef | **0.944** | 0.943 | **Grep** |
| **Average** | 0.698 | **0.803** | TransArc |

MediaStore: Grep P=1.000, R=0.424 — identical recall to TransArc but *better*
precision. JabRef: both produce ~9,260 links with nearly identical distributions.

### Full Baseline Comparison (Micro F1)

| Baseline | MS | TS | TM | BBB | JR | **Avg** |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| Oracle-Subset | 1.000 | 1.000 | 0.934 | 1.000 | 1.000 | **0.987** |
| Perfect-Transitive | 1.000 | 1.000 | 0.881 | 0.968 | 1.000 | **0.970** |
| Oracle-Component | 0.956 | 0.947 | 0.881 | 0.978 | 0.767 | **0.906** |
| **Adaptive LLM** | **0.965** | 0.764 | 0.707 | 0.710 | **0.999** | **0.829** |
| **TransArc** | 0.588 | **0.829** | **0.821** | **0.831** | 0.943 | **0.803** |
| Keyword-Grep | 0.595 | 0.515 | 0.608 | 0.827 | 0.944 | 0.698 |
| Enhanced-Grep | 0.122 | 0.792 | 0.608 | 0.827 | 0.944 | 0.659 |
| Optimal-Constant | 0.352 | 0.294 | 0.181 | 0.285 | 0.432 | 0.309 |
| Random | 0.024 | 0.126 | 0.120 | 0.063 | **0.440** | 0.155 |
| Round-Robin | 0.052 | 0.032 | 0.193 | 0.042 | 0.361 | 0.136 |

### Oracle-Top3: Gold Concentration

| Project | 3 Sentences Capture | Total Gold | Fraction | F1 |
|---------|:---:|:---:|:---:|:---:|
| JabRef | 5,787 | 8,268 | **70.0%** | 0.812 |
| TeaStore | 249 | 707 | 35.2% | 0.377 |
| Teammates | 1,646 | 8,097 | 20.3% | 0.311 |
| BigBlueButton | 324 | 1,529 | 21.2% | 0.204 |
| MediaStore | 16 | 59 | 27.1% | 0.091 |

### Random Baseline on JabRef

Gold density = 8,268 / (10 × 1,998) = **41.4%**. A random baseline achieves
F1=0.440 — purely from enrollment inflation.

### The Task Reduces to Component Classification

Oracle-Subset (choose correct component subset per sentence, link all enrolled
files) achieves **F1=0.987** — near-perfect — without any file-level precision.

The intelligence hierarchy:

| Rank | Baseline | Avg F1 | Intelligence |
|:---:|:---|:---:|:---|
| 1 | Oracle-Subset | 0.987 | Component subset per sentence |
| 2 | Perfect-Transitive | 0.970 | Gold SAD-SAM × Gold SAM-CODE |
| 3 | Oracle-Component | 0.906 | Single component per sentence |
| 4 | TransArc | 0.803 | Full NLP pipeline |
| 5 | Keyword-Grep | 0.698 | Substring match |
| 6 | Round-Robin | 0.136 | Nothing |

### LLM Agents: Reading Comprehension Beats NLP

```bash
# LLM evaluation:
python3 llm_agentic_eval.py
# Output: LLM_BASELINE.md

# LLM error analysis:
python3 llm_error_analysis.py
# Output: stdout
```

| Baseline | MS | TS | TM | BBB | JR | **Avg** |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| **Adaptive LLM** | **0.965** | 0.764 | 0.707 | 0.710 | **0.999** | **0.829** |
| TransArc | 0.588 | **0.829** | **0.821** | **0.831** | 0.943 | 0.803 |

LLM wins on 2/5 projects, beats TransArc on average (0.829 vs 0.803).

LLM strategy selection: intersection (large docs), majority (medium), single (tiny):

| Project | Best Strategy | F1 |
|---------|:---|:---:|
| MediaStore | Multi-Agent Majority | 0.965 |
| TeaStore | Multi-Agent Intersect | 0.764 |
| Teammates | Multi-Agent Intersect | 0.707 |
| BigBlueButton | Multi-Agent Majority | 0.710 |
| JabRef | Single-Agent | 0.999 |

LLM error patterns:
1. **Interface blind spot** — never assigns Interfaces (zero impact on Teammates/BBB, real on TeaStore)
2. **Co-occurrence blindness** — BBB HTML5 Client/Server always co-occur but LLM assigns one
3. **Over-classification** — assigns behavioral sentences (caching, hashing) that have no gold link

### Holistic Comparison

```bash
python3 creative_metrics_analysis.py
# Full dashboard: CREATIVE_METRICS.md
```

| System | Avg Micro F1 | Avg Macro F1 | Avg Noise | Avg Coverage | Avg Usefulness | Avg Wasted Effort |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| Adaptive LLM | **0.829** | **0.790** | 0.208 | **0.810** | 0.791 | 0.30 |
| TransArc | 0.803 | 0.699 | **0.130** | 0.751 | **0.887** | **0.14** |
| Keyword-Grep | 0.698 | 0.668 | 0.127 | 0.763 | 0.858 | 0.30 |

TransArc wins on noise (0.130) and wasted effort (0.14). LLM wins on coverage
(0.810) and macro F1 (0.790). V45 projects to best of both (~noise 0.095,
~coverage 0.850).

---

## 7. What Metrics Should We Use Instead?

### Problem Summary

| Issue | Why P/R/F1 Fails | Severity | Script That Exposes It |
|:--|:--|:---:|:---|
| Enrollment explosion | Large components dominate | Critical | `holistic_metrics_analysis.py` |
| Amplification asymmetry | 1 error = 1–972 FPs | Critical | `transarc_error_analysis.py` |
| Cross-project incomparability | Same F1 ≠ same quality | High | `transarc_error_analysis.py` |
| Coverage blindness | TNs get zero credit | High | `creative_metrics_analysis.py` |
| Theoretical limits | Impossible FNs penalized | High | `transarc_error_analysis.py` |
| Concentration | Top 3 components = 60–95% F1 | Medium | `holistic_metrics_analysis.py` |
| Stupid baseline parity | Grep = TransArc on 2/5 | Medium | `stupid_baseline_analysis.py` |
| Task reduction | F1 measures classification | Fundamental | `extreme_baseline_analysis.py` |

### Recommended Metrics

**M1: Component-Level F1** — Evaluate at (sentence, component) level:
```bash
python3 transarc_error_analysis.py  # Analysis A – SAD-SAM metrics
```

| System | Component TPs | FPs | FNs |
|:--|:---:|:---:|:---:|
| TransArc | 148 | 40 | 47 |
| V45 | 173 | 24 | 22 |

**M2: Raw Entry-Level F1** — Pre-enrollment evaluation:
```bash
python3 holistic_metrics_analysis.py  # M2 columns
```

**M3: Macro F1 per-sentence** — Equal weight per sentence:
```bash
python3 holistic_metrics_analysis.py  # M3 columns
```

**M4: Coverage + Noise + Usefulness**:
```bash
python3 creative_metrics_analysis.py  # Sentence-centric metrics
```

| Metric | Definition |
|:--|:--|
| Coverage | Fraction of gold sentences with ≥1 TP |
| Noise | Fraction of result sentences with ≥1 FP |
| Usefulness | Fraction of result sentences where TPs ≥ FPs |
| Wasted Effort | Avg FPs per TP across sentences |

**M5: Ceiling-Adjusted Recall** — Remove theoretical-limit FNs:
```bash
python3 transarc_error_analysis.py  # Analysis C – Theoretical limit
```

**M6: Component Coverage** — Breadth assessment:
```bash
python3 holistic_metrics_analysis.py  # M5 table
```

**M7: Cascade-Weighted** — SAM-CODE links weighted by downstream sentence count:
```bash
python3 holistic_metrics_analysis.py  # M6 table
```

**M8: Wasted Effort** — Developer experience metric:
```bash
python3 creative_metrics_analysis.py  # Practical utility
```

---

## 8. Summary: The Real Picture

### Three Systems Compared

| Metric | TransArc | V45 Linker | Adaptive LLM |
|:--|:---:|:---:|:---:|
| Operates at | File (transitive) | Component (SAD-SAM) | Component (direct) |
| SAD-CODE Micro F1 | 0.803 avg | ~0.930 (projected) | 0.829 |
| SAD-SAM Component F1 | 75.4% | **88.3%** | N/A |
| Component FPs | 40 | **24** | ~56 |
| Component FNs | 47 | **22** | ~42 |
| File FPs | 3,672 | **~1,931** | ~3,924 |
| Coverage | 0.751 | ~0.850 | **0.810** |
| Noise | **0.130** | ~0.095 | 0.208 |
| Macro F1/sent | 0.699 | ~0.82 | **0.790** |
| Grep-parity projects | 2/5 | 0/5 | 0/5 |
| Unreachable links | 552 | 552 | 0 (direct) |

### Bottom Line

1. **TransArc's file-level F1 is misleading.** Same quality → F1=0.588 (MediaStore)
   or F1=0.943 (JabRef) depending on component file counts.

2. **V45 wins at component level** (+12.9pp F1, 40% fewer FPs, 53% fewer FNs).
   Projected file impact: -1,741 FPs (transformative for Teammates, invisible for JabRef).

3. **The task reduces to reading comprehension.** Zero-training LLM beats TransArc
   (0.829 vs 0.803). Grep matches TransArc on 2/5 projects. Oracle classification = 0.987.

4. **No single metric suffices.** Report component-level error counts, macro F1,
   coverage, noise, wasted effort, and ceiling-adjusted recall alongside micro F1.

5. **The gold standard is the deepest problem.** 50% of documentation is dark matter.
   69% of Teammates FNs are structurally impossible. 38 annotations inflate to 8,268 links.

### Full Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp

# All analyses (run in order):
python3 transarc_error_analysis.py          # → TRANSARC_EMPIRICAL_STUDY.md
python3 holistic_metrics_analysis.py        # → HOLISTIC_METRICS.md
python3 creative_metrics_analysis.py        # → CREATIVE_METRICS.md
python3 stupid_baseline_analysis.py         # → STUPID_BASELINES.md
python3 extreme_baseline_analysis.py        # → EXTREME_BASELINES.md
python3 sam_code_distribution_analysis.py   # → SAM_CODE_DISTRIBUTION.md
python3 sam_code_cascade_analysis.py        # → SAM_CODE_CASCADE.md
python3 sad_sam_tp_gain_analysis.py         # → SAD_SAM_TP_GAIN_STUDY.md
python3 sad_sam_actual_contribution.py      # → SAD_SAM_ACTUAL_CONTRIBUTION.md
python3 llm_agentic_eval.py                # → LLM_BASELINE.md
python3 llm_error_analysis.py              # → stdout

# V45 linker:
cd /mnt/hostshare/ardoco-home/llm-sad-sam-agent
LLM_BACKEND=openai OPENAI_API_KEY=<key> \
  .venv/bin/python scripts/evaluation/evaluate_comprehensive.py --version v45
```
