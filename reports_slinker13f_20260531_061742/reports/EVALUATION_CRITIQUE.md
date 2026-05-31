# Evaluation Critique: Why File-Level P/R/F1 Is Inadequate for SAD-CODE

*A deep investigation of how distributional biases in the ARDoCo benchmark render*
*standard file-level precision/recall/F1 misleading for the SAD-CODE traceability task.*

## Part 1: The Inflation Problem

File-level P/R/F1 treats every `(sentence, file)` pair as an equally-weighted,
independent data point. But the gold standard is authored at a coarser granularity:
annotators assign *directories* or *components* to sentences, and enrollment expands
these to individual files. This creates a fundamental mismatch between the number of
*decisions* being evaluated and the number of *data points* in the metric.

### 1.1 Annotator Decisions vs Enrolled File Links

| Project | Raw Decisions | Dir Entries | File Entries | Enrolled Links | Inflation | Effective n |
|---------|--------------|-------------|-------------|---------------|-----------|-------------|
| mediastore | 57 | 2 | 55 | 59 | 1.0x | ~57 |
| teastore | 70 | 43 | 27 | 707 | 10.1x | ~70 |
| teammates | 228 | 151 | 77 | 8,097 | 35.5x | ~228 |
| bigbluebutton | 132 | 116 | 16 | 1,529 | 11.6x | ~132 |
| jabref | 38 | 38 | 0 | 8,268 | 217.6x | ~38 |
| **Total** | **525** | | | **18,660** | **35.5x** | **~525** |

The file-level F1 appears to be computed over 18,660 data points, but it really reflects 
~525 annotator decisions. The statistical confidence implied by the sample size is illusory.

### 1.2 Expansion Distribution — How Unequal Are the Weights?

Each raw gold entry expands to a different number of file-level links.
A correct/incorrect raw entry thus generates a different number of TPs/FNs.

| Project | Min Expansion | Median | Max | Gini | Top-1 Entry Weight | Top-3 % of Gold |
|---------|--------------|--------|-----|------|-------------------|-----------------|
| mediastore | 1 | 1 | 2 | 0.033 | 3.4% | 8.5% |
| teastore | 1 | 4 | 38 | 0.598 | 5.4% | 16.1% |
| teammates | 1 | 17 | 235 | 0.656 | 2.9% | 8.7% |
| bigbluebutton | 1 | 5 | 70 | 0.581 | 4.6% | 13.0% |
| jabref | 3 | 65 | 642 | 0.568 | 7.8% | 23.3% |

**JabRef**: The single largest raw entry (one directory) produces 642 file-level links, 
which is 7.8% of the entire enrolled gold standard. 
Getting this one directory right/wrong dominates the entire F1 score.

### 1.3 Where Do True Positives and False Negatives Actually Come From?

| Project | Total TP | TP from Dirs | % | Total FN | FN from Dirs | % |
|---------|---------|-------------|---|---------|-------------|---|
| mediastore | 25 | 4 | 16% | 34 | 0 | 0% |
| teastore | 501 | 483 | 96% | 206 | 197 | 96% |
| teammates | 7,307 | 7,300 | 100% | 790 | 720 | 91% |
| bigbluebutton | 1,287 | 1,271 | 99% | 242 | 242 | 100% |
| jabref | 8,268 | 8,268 | 100% | 0 | 0 | 0% |
| **Total** | **17,388** | **17,326** | **100%** | **1,272** | **1,159** | **91%** |

**99.6% of all TPs** and **91.1% of all FNs** are artifacts of 
directory enrollment. The metric is overwhelmingly measuring directory-level decisions
while presenting itself as a file-level evaluation.

## Part 2: Block Correlation — Violation of Independence

P/R/F1 implicitly assumes each data point is independent. But enrollment creates
**blocks** of correlated entries: all files under one directory are either all correct
(if the system identifies the directory) or all missed (if it doesn't). These blocks
move together as units.

### 2.1 Block Homogeneity — Do enrolled files from the same raw entry share fate?

For each raw gold entry that expands to ≥2 files, we check: what fraction of its
enrolled files are TPs vs FNs? Perfect homogeneity (all TP or all FN) means the
directory-level decision completely determines file-level outcomes.

| Project | Blocks ≥2 | All-TP Blocks | All-FN Blocks | Mixed | Homogeneity |
|---------|----------|--------------|--------------|-------|-------------|
| mediastore | 2 | 2 | 0 | 0 | 100% |
| teastore | 43 | 31 | 12 | 0 | 100% |
| teammates | 149 | 130 | 19 | 0 | 100% |
| bigbluebutton | 107 | 79 | 24 | 4 | 96% |
| jabref | 38 | 38 | 0 | 0 | 100% |

High homogeneity confirms that file-level outcomes are determined by directory-level
decisions. The files within a block are not independent observations — they are
redundant copies of one decision.

### 2.2 Effective Sample Size

If blocks of size N count as N independent observations but are really 1 decision,
the effective sample size is much smaller than the enrolled link count.

| Project | Enrolled Links | Raw Decisions | Ratio | Implied 95% CI Width | Actual CI Width |
|---------|---------------|--------------|-------|---------------------|-----------------|
| mediastore | 59 | 57 | 1:1 | ±0.1256 | ±0.128 |
| teastore | 707 | 70 | 10:1 | ±0.0277 | ±0.088 |
| teammates | 8,097 | 228 | 36:1 | ±0.0083 | ±0.050 |
| bigbluebutton | 1,529 | 132 | 12:1 | ±0.0188 | ±0.064 |
| jabref | 8,268 | 38 | 218:1 | ±0.0050 | ±0.074 |

The 'implied' CI width (using enrolled count) is deceptively narrow. The 'actual' CI
width (using raw decision count) is much wider, reflecting the true uncertainty.

## Part 3: Metric Sensitivity — Single Decisions That Swing F1

We remove each raw gold entry one at a time and recompute F1.
This shows how much a single annotator decision controls the final score.

### 3.1 Most Influential Raw Entries (by |ΔF1| when excluded)

**mediastore** (baseline F1=0.5882):

| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |
|------|----------|---------------|------|-----|-----|--------|-----|
| 1 | 11 | `…/edu/kit/ipd/sdq/mediastore/ejb/usermanagement/` [DIR] | 2 | 2 | 0 | 0.5542 | -0.0340 |
| 2 | 13 | `…/edu/kit/ipd/sdq/mediastore/ejb/usermanagement/` [DIR] | 2 | 2 | 0 | 0.5542 | -0.0340 |
| 3 | 1 | `…t/ipd/sdq/mediastore/ejb/facade/FacadeImpl.java` [FILE] | 1 | 1 | 0 | 0.5714 | -0.0168 |
| 4 | 3 | `…t/ipd/sdq/mediastore/ejb/facade/FacadeImpl.java` [FILE] | 1 | 1 | 0 | 0.5714 | -0.0168 |
| 5 | 6 | `…t/ipd/sdq/mediastore/ejb/facade/FacadeImpl.java` [FILE] | 1 | 1 | 0 | 0.5714 | -0.0168 |

**teastore** (baseline F1=0.8295):

| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |
|------|----------|---------------|------|-----|-----|--------|-----|
| 1 | 2 | `…e/src/main/java/tools/descartes/teastore/image/` [DIR] | 38 | 38 | 0 | 0.7915 | -0.0380 |
| 2 | 7 | `…e/src/main/java/tools/descartes/teastore/image/` [DIR] | 38 | 38 | 0 | 0.7915 | -0.0380 |
| 3 | 10 | `…e/src/main/java/tools/descartes/teastore/image/` [DIR] | 38 | 38 | 0 | 0.7915 | -0.0380 |
| 4 | 12 | `…e/src/main/java/tools/descartes/teastore/image/` [DIR] | 38 | 38 | 0 | 0.7915 | -0.0380 |
| 5 | 11 | `…e/src/main/java/tools/descartes/teastore/image/` [DIR] | 38 | 0 | 38 | 0.8564 | +0.0269 |

**teammates** (baseline F1=0.8211):

| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |
|------|----------|---------------|------|-----|-----|--------|-----|
| 1 | 1 | `src/main/java/teammates/ui/` [DIR] | 235 | 235 | 0 | 0.8053 | -0.0158 |
| 2 | 4 | `src/main/java/teammates/ui/` [DIR] | 235 | 235 | 0 | 0.8053 | -0.0158 |
| 3 | 5 | `src/main/java/teammates/ui/` [DIR] | 235 | 235 | 0 | 0.8053 | -0.0158 |
| 4 | 7 | `src/main/java/teammates/ui/` [DIR] | 235 | 235 | 0 | 0.8053 | -0.0158 |
| 5 | 25 | `src/main/java/teammates/ui/` [DIR] | 235 | 235 | 0 | 0.8053 | -0.0158 |

**bigbluebutton** (baseline F1=0.8309):

| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |
|------|----------|---------------|------|-----|-----|--------|-----|
| 1 | 80 | `…b/src/main/java/org/bigbluebutton/presentation/` [DIR] | 70 | 70 | 0 | 0.8038 | -0.0270 |
| 2 | 81 | `…b/src/main/java/org/bigbluebutton/presentation/` [DIR] | 70 | 70 | 0 | 0.8038 | -0.0270 |
| 3 | 57 | `akka-bbb-fsesl/` [DIR] | 59 | 59 | 0 | 0.8082 | -0.0227 |
| 4 | 58 | `…esl/src/main/java/org/bigbluebutton/freeswitch/` [DIR] | 53 | 53 | 0 | 0.8105 | -0.0203 |
| 5 | 61 | `…esl/src/main/java/org/bigbluebutton/freeswitch/` [DIR] | 53 | 53 | 0 | 0.8105 | -0.0203 |

**jabref** (baseline F1=0.9433):

| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |
|------|----------|---------------|------|-----|-----|--------|-----|
| 1 | 1 | `src/main/java/org/jabref/gui/` [DIR] | 642 | 642 | 0 | 0.9031 | -0.0402 |
| 2 | 4 | `src/main/java/org/jabref/gui/` [DIR] | 642 | 642 | 0 | 0.9031 | -0.0402 |
| 3 | 6 | `src/main/java/org/jabref/gui/` [DIR] | 642 | 642 | 0 | 0.9031 | -0.0402 |
| 4 | 7 | `src/main/java/org/jabref/gui/` [DIR] | 642 | 642 | 0 | 0.9031 | -0.0402 |
| 5 | 1 | `src/main/java/org/jabref/logic/` [DIR] | 575 | 575 | 0 | 0.9075 | -0.0358 |

### 3.2 Aggregate Sensitivity

| Project | F1 | Max |ΔF1| | Mean |ΔF1| (top-5) | Entries where |ΔF1|>0.01 |
|---------|----|---------|--------------------|--------------------------|
| mediastore | 0.5882 | 0.0340 | 0.0237 | 23/57 |
| teastore | 0.8295 | 0.0380 | 0.0358 | 24/70 |
| teammates | 0.8211 | 0.0158 | 0.0158 | 9/226 |
| bigbluebutton | 0.8309 | 0.0270 | 0.0235 | 20/132 |
| jabref | 0.9433 | 0.0402 | 0.0393 | 18/38 |

## Part 4: SAM-CODE Concentration × Enrollment = Double Amplification

In the transitive pipeline (SAD→SAM→CODE), the SAM-CODE step maps each architectural
element (AE) to code files. A few AEs dominate the file counts (Finding 3 from the bias study).
Enrollment then expands directory entries, creating a **double amplification**:

1. **SAD-SAM**: One sentence links to K model elements (low fan-out, K≈1-2)
2. **SAM-CODE**: Each model element maps to N files (high fan-out, N=1–972)
3. **Enrollment**: Directory entries expand by M additional files

A single correct SAD-SAM link can thus generate K×N TPs at file level.
The file-level F1 is dominated by the few sentences that link to high-fan-out AEs.

### 4.1 Sentence Contribution Inequality

How many file-level gold links does each sentence contribute?

**mediastore**: 25/37 sentences linked, 59 enrolled links, Gini=0.331
  - Top-1 sentence: 6 links (10.2% of gold)
  - Top-3 sentences: 16 links (27.1%)
  - Sentences for ≥50% of gold: **7** out of 25

**teastore**: 23/43 sentences linked, 707 enrolled links, Gini=0.448
  - Top-1 sentence: 83 links (11.7% of gold)
  - Top-3 sentences: 249 links (35.2%)
  - Sentences for ≥50% of gold: **5** out of 23

**teammates**: 92/198 sentences linked, 8,097 enrolled links, Gini=0.645
  - Top-1 sentence: 808 links (10.0% of gold)
  - Top-3 sentences: 1,646 links (20.3%)
  - Sentences for ≥50% of gold: **11** out of 92

**bigbluebutton**: 45/87 sentences linked, 1,529 enrolled links, Gini=0.472
  - Top-1 sentence: 114 links (7.5% of gold)
  - Top-3 sentences: 326 links (21.3%)
  - Sentences for ≥50% of gold: **8** out of 45

**jabref**: 10/13 sentences linked, 8,268 enrolled links, Gini=0.527
  - Top-1 sentence: 1,929 links (23.3% of gold)
  - Top-3 sentences: 5,787 links (70.0%)
  - Sentences for ≥50% of gold: **3** out of 10

### 4.2 The Amplification Chain

For each project, trace how model element concentration flows through enrollment:

| Project | AEs in SAM-CODE | Top AE | Files for Top AE | Gold SAD-CODE Links via Top AE | % of Total Gold |
|---------|----------------|--------|-----------------|-------------------------------|----------------|
| mediastore | 19 | Interface: IDownload | 16 | 0 | 0.0% |
| teastore | 19 | Component: ImageProvider | 64 | 320 | 45.3% |
| teammates | 14 | Interface: UI | 348 | 3,622 | 44.7% |
| bigbluebutton | 22 | Interface: FreeSWITCH | 94 | 732 | 47.9% |
| jabref | 6 | Component: logic | 972 | 3,888 | 47.0% |

The top architectural element's files account for a large fraction of the SAD-CODE
gold standard. Getting this one component right/wrong dominates file-level F1.

## Part 5: Alternative Metrics and Their Disagreements

We compute F1 at four granularities for **four systems** — TransArc, V45, LLM,
and V87 — and show where they disagree:

1. **File-level F1** (standard): each `(sentence, file)` is one data point
2. **Decision-level F1**: each raw gold entry `(sentence, dir_or_file)` is one data point.
   A raw entry is a TP if ≥50% of its enrolled files are TPs.
3. **Component-level F1**: each `(sentence, component_name)` is one data point.
   Collapse code files back to their architectural component (via SAM-CODE gold).
4. **Weighted File F1**: each enrolled link weighted by 1/block_size, so one directory = one unit of weight.

**Systems:**
- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)
- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through ARCOTL SAM-CODE
- **LLM**: Zero-training meta-learning classifier, projected through gold SAM-CODE
- **V87-pc**: Few-shot meta-learning (10% gold, per-component strategy),
  projected through TransArc SAM-CODE — **aggregate F1 only** (no per-link data)

### 5.1 Decision-Level F1 (TransArc)

Treat each raw gold entry as a single binary decision. A raw entry is 'hit' (TP)
if the system returned at least 50% of its enrolled files; otherwise it's a miss (FN).
System results not matching any gold entry are FPs (counted per unique directory/file in result).

| Project | Dec. TP | Dec. FP | Dec. FN | Dec. P | Dec. R | Dec. F1 | File F1 | Δ |
|---------|--------|--------|--------|--------|--------|---------|---------|---|
| mediastore | 23 | 1 | 34 | 0.958 | 0.404 | 0.568 | 0.588 | -0.020 |
| teastore | 49 | 0 | 21 | 1.000 | 0.700 | 0.824 | 0.829 | -0.006 |
| teammates | 137 | 123 | 89 | 0.527 | 0.606 | 0.564 | 0.821 | -0.257 |
| bigbluebutton | 105 | 97 | 27 | 0.520 | 0.795 | 0.629 | 0.831 | -0.202 |
| jabref | 38 | 117 | 0 | 0.245 | 1.000 | 0.394 | 0.943 | -0.550 |

### 5.2 Component-Level F1 (TransArc)

Collapse file paths to architectural components using the SAM-CODE gold standard.
A `(sentence, component)` pair is the evaluation unit.

| Project | Comp. Gold | Comp. Result | Comp. P | Comp. R | Comp. F1 | File F1 | Δ |
|---------|-----------|-------------|---------|---------|----------|---------|---|
| mediastore | 35 | 18 | 0.944 | 0.486 | 0.642 | 0.588 | +0.053 |
| teastore | 58 | 41 | 1.000 | 0.707 | 0.828 | 0.829 | -0.001 |
| teammates | 262 | 158 | 0.861 | 0.519 | 0.648 | 0.821 | -0.173 |
| bigbluebutton | 158 | 274 | 0.453 | 0.785 | 0.574 | 0.831 | -0.257 |
| jabref | 22 | 28 | 0.786 | 1.000 | 0.880 | 0.943 | -0.063 |

### 5.3 Inverse-Expansion-Weighted F1 (TransArc)

Weight each enrolled link by `1/block_size`, so all files from one directory
collectively count as 1.0, not N separate data points.

| Project | W-TP | W-FP | W-FN | W-P | W-R | W-F1 | File F1 | Δ |
|---------|------|------|------|-----|-----|------|---------|---|
| mediastore | 23.0 | 1 | 34.0 | 0.958 | 0.404 | 0.568 | 0.588 | -0.020 |
| teastore | 49.0 | 0 | 21.0 | 1.000 | 0.700 | 0.824 | 0.829 | -0.006 |
| teammates | 135.8 | 123 | 88.7 | 0.525 | 0.605 | 0.562 | 0.821 | -0.259 |
| bigbluebutton | 102.9 | 97 | 27.3 | 0.515 | 0.790 | 0.623 | 0.831 | -0.207 |
| jabref | 38.0 | 117 | 0.0 | 0.245 | 1.000 | 0.394 | 0.943 | -0.550 |

### 5.4 Full Metric Comparison — All Systems

**File-level F1** (standard enrolled metric):

| Project | TransArc | V45 | LLM | V87-pc |
|---------|----------|-----|-----|--------|
| mediastore | 0.588 | 0.929 | 0.965 | 0.000 |
| teastore | 0.829 | 1.000 | 0.829 | 0.000 |
| teammates | 0.821 | 0.864 | 0.618 | 0.000 |
| bigbluebutton | 0.831 | 0.864 | 0.789 | 0.000 |
| jabref | 0.943 | 1.000 | 0.916 | 0.000 |
| **Average** | **0.803** | **0.931** | **0.823** | **0.000** |

**Decision-level F1** (one raw gold entry = one data point):

| Project | TransArc | V45 | LLM | V87-pc |
|---------|----------|-----|-----|--------|
| mediastore | 0.568 | 0.926 | 0.964 | N/A |
| teastore | 0.824 | 1.000 | 0.685 | N/A |
| teammates | 0.564 | 0.582 | 0.442 | N/A |
| bigbluebutton | 0.629 | 0.655 | 0.693 | N/A |
| jabref | 0.394 | 0.950 | 0.239 | N/A |
| **Average** | **0.596** | **0.822** | **0.604** | N/A |

**Component-level F1** (sentence × component pairs):

| Project | TransArc | V45 | LLM | V87-pc |
|---------|----------|-----|-----|--------|
| mediastore | 0.642 | 0.986 | 0.971 | N/A |
| teastore | 0.828 | 1.000 | 0.803 | N/A |
| teammates | 0.648 | 0.557 | 0.531 | N/A |
| bigbluebutton | 0.574 | 0.627 | 0.775 | N/A |
| jabref | 0.880 | 0.917 | 0.875 | N/A |
| **Average** | **0.714** | **0.817** | **0.791** | N/A |

**Weighted File F1** (1/block_size weighting):

| Project | TransArc | V45 | LLM | V87-pc |
|---------|----------|-----|-----|--------|
| mediastore | 0.568 | 0.926 | 0.964 | N/A |
| teastore | 0.824 | 1.000 | 0.685 | N/A |
| teammates | 0.562 | 0.579 | 0.442 | N/A |
| bigbluebutton | 0.623 | 0.650 | 0.689 | N/A |
| jabref | 0.394 | 0.950 | 0.239 | N/A |
| **Average** | **0.594** | **0.821** | **0.604** | N/A |

### 5.5 Per-System Summary (All Granularities)

**TransArc:**

| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |
|---------|---------|-------------|-------------|-------------|
| mediastore | 0.588 | 0.568 | 0.642 | 0.568 |
| teastore | 0.829 | 0.824 | 0.828 | 0.824 |
| teammates | 0.821 | 0.564 | 0.648 | 0.562 |
| bigbluebutton | 0.831 | 0.629 | 0.574 | 0.623 |
| jabref | 0.943 | 0.394 | 0.880 | 0.394 |
| **Average** | **0.803** | **0.596** | **0.714** | **0.594** |

**V45:**

| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |
|---------|---------|-------------|-------------|-------------|
| mediastore | 0.929 | 0.926 | 0.986 | 0.926 |
| teastore | 1.000 | 1.000 | 1.000 | 1.000 |
| teammates | 0.864 | 0.582 | 0.557 | 0.579 |
| bigbluebutton | 0.864 | 0.655 | 0.627 | 0.650 |
| jabref | 1.000 | 0.950 | 0.917 | 0.950 |
| **Average** | **0.931** | **0.822** | **0.817** | **0.821** |

**LLM (Meta-Learning):**

| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |
|---------|---------|-------------|-------------|-------------|
| mediastore | 0.965 | 0.964 | 0.971 | 0.964 |
| teastore | 0.829 | 0.685 | 0.803 | 0.685 |
| teammates | 0.618 | 0.442 | 0.531 | 0.442 |
| bigbluebutton | 0.789 | 0.693 | 0.775 | 0.689 |
| jabref | 0.916 | 0.239 | 0.875 | 0.239 |
| **Average** | **0.823** | **0.604** | **0.791** | **0.604** |

**V87 per-component** (aggregate file-level F1 only — no per-link data for alternative metrics):

| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |
|---------|---------|-------------|-------------|-------------|
| mediastore | 0.000 | N/A | N/A | N/A |
| teastore | 0.000 | N/A | N/A | N/A |
| teammates | 0.000 | N/A | N/A | N/A |
| bigbluebutton | 0.000 | N/A | N/A | N/A |
| jabref | 0.000 | N/A | N/A | N/A |
| **Average** | **0.000** | N/A | N/A | N/A |

### 5.6 System Comparison Instability — Which System Wins?

The central question: does the choice of metric change which system appears better?

**Average F1 across projects:**

| Metric | TransArc | V45 | LLM | V87-pc | Best |
|--------|----------|-----|-----|--------|------|
| File F1 | 0.803 | 0.931 | 0.823 | 0.000 | V45 |
| Decision F1 | 0.596 | 0.822 | 0.604 | N/A | V45 |
| Component F1 | 0.714 | 0.817 | 0.791 | N/A | V45 |
| Weighted F1 | 0.594 | 0.821 | 0.604 | N/A | V45 |

**Per-project winners (File F1):**

| Project | TransArc | V45 | LLM | V87-pc | Best |
|---------|----------|-----|-----|--------|------|
| mediastore | 0.588 | 0.929 | 0.965 | 0.000 | LLM |
| teastore | 0.829 | 1.000 | 0.829 | 0.000 | V45 |
| teammates | 0.821 | 0.864 | 0.618 | 0.000 | V45 |
| bigbluebutton | 0.831 | 0.864 | 0.789 | 0.000 | V45 |
| jabref | 0.943 | 1.000 | 0.916 | 0.000 | V45 |

**Per-project winners (Component F1) — most semantically meaningful:**

| Project | TransArc | V45 | LLM | Best |
|---------|----------|-----|-----|------|
| mediastore | 0.642 | 0.986 | 0.971 | V45 |
| teastore | 0.828 | 1.000 | 0.803 | V45 |
| teammates | 0.648 | 0.557 | 0.531 | TransArc |
| bigbluebutton | 0.574 | 0.627 | 0.775 | LLM |
| jabref | 0.880 | 0.917 | 0.875 | V45 |

**Winner flips across metric granularity (per project):**

Does the choice of metric change which system wins on a given project?
For each project, we check if the best system changes across File/Decision/Component/Weighted F1.

- **mediastore**: File→LLM, Dec→LLM, Comp→V45, Weighted→LLM
- **teammates**: File→V45, Dec→V45, Comp→TransArc, Weighted→V45
- **bigbluebutton**: File→V45, Dec→LLM, Comp→LLM, Weighted→LLM

**3/5** projects show a winner flip across metric granularities.

### 5.7 Project Ranking Disagreements (TransArc)

Do alternative metrics change the **ranking** of projects?

| Rank | File F1 | Decision F1 | Component F1 | Weighted F1 |
|------|---------|-------------|-------------|-------------|
| 1 | jabref | teastore | jabref | teastore |
| 2 | bigbluebutton | bigbluebutton | teastore | bigbluebutton |
| 3 | teastore | mediastore | teammates | mediastore |
| 4 | teammates | teammates | mediastore | teammates |
| 5 | mediastore | jabref | bigbluebutton | jabref |

Pairwise ranking disagreements (discordant pairs out of 10):
- File vs Decision: 6
- File vs Component: 3
- File vs Weighted: 6
- Decision vs Component: 7

## Part 6: Case Studies

### 6.1 JabRef: 38 Decisions Masquerading as 8,268 Data Points

JabRef has **zero** file-level gold entries — every single raw entry is a directory.
The 38 raw decisions expand to 8,268 enrolled links (217.6x).
The file-level F1 of 0.943 appears precise to 3 decimal places,
but it's really measuring ~38 binary decisions.

**The 5 most influential decisions:**

| Decision | Dir | Size | TPs | FNs | ΔF1 if excluded |
|----------|-----|------|-----|-----|----------------|
| S1→gui/ | src/main/java/org/jabref/gui/… | 642 | 642 | 0 | -0.0402 |
| S4→gui/ | src/main/java/org/jabref/gui/… | 642 | 642 | 0 | -0.0402 |
| S6→gui/ | src/main/java/org/jabref/gui/… | 642 | 642 | 0 | -0.0402 |
| S7→gui/ | src/main/java/org/jabref/gui/… | 642 | 642 | 0 | -0.0402 |
| S1→logic/ | src/main/java/org/jabref/logic/… | 575 | 575 | 0 | -0.0358 |

The top-5 decisions collectively account for |ΔF1| sum = 0.197.
The remaining 33 decisions have much smaller influence.

### 6.2 Teammates: Interface/Component Overlap Doubles the Counting

| Base Name | Component Files | Interface Files | Overlap | Overlap % |
|-----------|----------------|----------------|---------|-----------|
| Client | 40 | 40 | 40 | 100% |
| Common | 150 | 150 | 150 | 100% |
| E2E | 123 | 123 | 123 | 100% |
| Logic | 71 | 71 | 71 | 100% |
| Storage | 59 | 59 | 59 | 100% |
| Test Driver | 17 | 17 | 17 | 100% |
| UI | 348 | 348 | 348 | 100% |

Every Component-Interface pair shares **100% of files** in Teammates.
This means each sentence→component assignment is effectively counted twice
at the file level (once via the Component, once via the Interface).
This is an artifact of the architecture model, not a reflection of system quality.

### 6.3 Cross-Project Incomparability

| Property | MediaStore | JabRef | Ratio |
|----------|-----------|--------|-------|
| Raw gold entries | 57 | 38 | 0.7x |
| Enrolled links | 59 | 8,268 | 140x |
| Enrollment ratio | 1.0x | 217.6x | |
| File-level F1 | 0.588 | 0.943 | |
| % TP from dirs | 16% | 100% | |

MediaStore's F1 measures 57 file-level decisions (mostly actual files).
JabRef's F1 measures 8,268 enrolled links derived from 38 directory decisions.
Averaging these F1 scores gives JabRef 140x more weight in the aggregate, despite
having fewer actual decisions. A macro-average across projects treats them equally,
but the file-level F1 itself gives massively different weight to different projects.

## Part 7: Synthesis — The Case Against File-Level P/R/F1

### Three Biases, One Conclusion

| Bias | Mechanism | Effect on File-Level F1 |
|------|-----------|------------------------|
| **SAD-SAM Long-Tail** | Few model elements have many links; most have few or none (UME) | Systems are tested mainly on popular elements; rare elements barely affect the score |
| **Enrollment Amplification** | Directories expand to 1–642 files each | One annotator decision becomes hundreds of data points; metric precision is illusory |
| **SAM-CODE Concentration** | Top-3 AEs hold 43–99% of all SAM-CODE links | Getting 3 components right/wrong dominates the entire evaluation |

### The Compound Effect

These biases don't just add — they **multiply**:

1. A sentence links to a popular model element (SAD-SAM long-tail)
2. That model element maps to hundreds of code files (SAM-CODE concentration)
3. Those files came from directory enrollment (enrollment amplification)

**Result**: One correct sentence→component association generates hundreds of file-level TPs.
One incorrect association generates hundreds of file-level FPs.
The file-level F1 score is dominated by a handful of high-impact decisions
while appearing to be a fine-grained, statistically robust evaluation.

### What File-Level F1 Actually Measures

- **18,660 data points** are derived from **525 decisions** (36:1 inflation)
- **100%** of TPs come from directory enrollment
- Removing the **single** most influential raw entry per project swings F1 by up to **4 percentage points**
- Block homogeneity is near 100%: files within a directory block are not independent observations
- Alternative metrics (decision-level, component-level, weighted) disagree with file-level rankings

### System Comparison Depends on Metric Granularity

The choice of evaluation metric changes which system appears better.
We compare all four systems (TransArc, V45, LLM, V87-pc) across metrics:

| Metric | TransArc | V45 | LLM | V87-pc | Best |
|--------|----------|-----|-----|--------|------|
| File F1 | 0.803 | 0.931 | 0.823 | 0.000 | V45 |
| Decision F1 | 0.596 | 0.822 | 0.604 | N/A | V45 |
| Component F1 | 0.714 | 0.817 | 0.791 | N/A | V45 |
| Weighted F1 | 0.594 | 0.821 | 0.604 | N/A | V45 |

In **3/5** projects, changing the metric granularity flips which system wins.
This means that claims like 'System A outperforms System B' are not robust —
they depend on the (arbitrary) choice of evaluation granularity.

### Recommendations

1. **Report multiple granularities**: Always report decision-level and component-level
   metrics alongside file-level metrics. If they disagree, investigate why.

2. **Weight by inverse expansion**: Use `1/block_size` weights so each annotator
   decision contributes equally to the score, regardless of how many files a directory contains.

3. **Report raw decision counts**: State how many independent gold standard decisions
   underlie the metric, not just the enrolled link count.

4. **Beware cross-project averages**: Projects with high enrollment expansion
   (JabRef: 218x) dominate any micro-average. Use macro-averages over projects,
   and report per-project metrics prominently.

5. **Consider component-level evaluation for SAD-CODE**: Since SAD-CODE is effectively
   'which components is this sentence about?', evaluating at the component level
   is more semantically meaningful than the file level.

6. **Sensitivity analysis**: For any new approach, report the F1 sensitivity to the
   top-5 most influential raw entries. If removing one entry changes F1 by >0.02,
   the result is fragile.

7. **Be skeptical of system comparisons**: If the winner changes depending on whether
   you measure at file, decision, or component level, the performance difference
   is likely within the noise of the evaluation methodology.

