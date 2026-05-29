# Architecture

**Analysis Date:** 2026-05-29

## Pattern Overview

**Overall:** Multi-stage empirical evaluation pipeline analyzing error propagation from intermediate TLR stages (SAD-SAM, SAM-CODE) to final SAD-CODE composition with bias critique and alternative metrics.

**Key Characteristics:**
- Input: Gold standards + benchmark code models + ARDoCo/TransArc results (sad-sam, sam-code, sad-code)
- Processing: Load, normalize, enroll, compute metrics, decompose errors, analyze distributions
- Output: Markdown reports documenting performance, bias, error propagation, metric limitations
- Modular: Reusable infrastructure shared across analysis scripts via `transarc_error_analysis.py`
- Investigative depth: Baseline metrics → root cause analysis → bias studies → metric critique → alternative metrics

## Layers

**Data Infrastructure Layer:**
- Purpose: Load and normalize benchmark datasets, code models, and ARDoCo/TransArc results
- Location: `src/lib/transarc_error_analysis.py` (lines 1–342)
- Contains: 
  - Path definitions (BENCHMARK, RESULTS, gold standard files, ACM code models, text files)
  - Loaders: `load_code_model_files()`, `load_gs_sad_sam()`, `load_gs_sam_code_raw()`, `load_gs_sad_code_raw()`, `load_result_sad_code()`, etc.
  - Helpers: `normalize_path()`, `enroll_gold_standard()`, `load_text()`, `load_model_element_names()`
  - Metric computation: `calc_metrics(gold, result)` → (precision, recall, f1, tp, fp, fn)
  - Intermediate maps: `load_transarc_intermediate_maps()` → (sent→models, model→codes, model→sents, code→models)
- Depends on: ARDoCo benchmark directory structure, TransArc results CSV files
- Used by: All analysis scripts in src/evaluation/, src/bias/, src/propagation/, src/annotation/

**Evaluation & Metrics Layer:**
- Purpose: Compute baseline metrics and implement alternative metric schemes
- Location: `src/lib/transarc_error_analysis.py` (lines 316–342 — analysis_a), `src/evaluation/*.py`
- Contains: 
  - Standard micro-averaged F1 (file-level, post-enrollment)
  - Component-level F1 (unique model → set of codes)
  - Decision-level F1 (raw gold entries, no enrollment)
  - Extreme baselines: Oracle-Component, Round-Robin, Random, Popularity
- Depends on: Data infrastructure layer
- Used by: Report generation, bias studies, critique

**Error Propagation & Root Cause Layer:**
- Purpose: Trace false positives and false negatives back to component causes in intermediate stages
- Location: `src/lib/transarc_error_analysis.py` (lines 349–400+, Analysis B/C), `src/propagation/*.py`
- Contains: 
  - FP classification: SAD_SAM_CAUSED, SAM_CODE_CAUSED, BOTH_CAUSED, COMBINATION_ERROR
  - TP gain analysis: for each SAD-SAM FN, compute hypothetical SAD-CODE TP gain
  - Cascade analysis: for each SAM-CODE link, trace its impact on SAD-CODE
  - Contribution ranking: model elements by actual TPs produced / FPs amplified
- Depends on: Data infrastructure, intermediate maps, metrics
- Used by: Prioritization of improvement areas, error understanding

**Bias & Distribution Analysis Layer:**
- Purpose: Quantify distributional properties and their impact on evaluation metrics
- Location: `src/bias/*.py`
- Contains: 
  - Gini coefficient (concentration measure)
  - Enrollment amplification factors (raw entries → enrolled files)
  - Position bias (early vs. late sentences/models)
  - Long-tail identification (top-N concentration)
  - File-level vs. decision-level metric disagreement
- Depends on: Data infrastructure layer, metrics layer
- Used by: Metric critique, alternative metric justification

**Document Analysis Layer:**
- Purpose: Extract document structure, component names, and sentence metadata from benchmark
- Location: `src/annotation/*.py`
- Contains: Text parsing, model element name resolution, document structure patterns, annotation convention discovery
- Depends on: Data infrastructure layer, benchmark text and model files
- Used by: Understanding annotation conventions, document-driven bias

## Data Flow

**Gold Standard Loading & Enrollment:**

```
benchmark/{project}/goldstandards/
  ├── goldstandard_sad_*-sam_*.csv  → load_gs_sad_sam() → set(modelElementID, sentence)
  ├── goldstandard_sam_*-code_*.csv → load_gs_sam_code_raw() → set(ae_id, code_path_raw)
  │                                      ↓
  │                                  enroll_gold_standard(code_model_files)
  │                                      ↓
  │                                  set(ae_id, code_path_enrolled)
  └── goldstandard_sad_*-code_*.csv → load_gs_sad_code_raw() → set(sentenceID, code_path_raw)
                                           ↓
                                       enroll_gold_standard()
                                           ↓
                                       set(sentenceID, code_path_enrolled)
```

**Code Model Parsing:**

```
benchmark/{project}/model_*/code/codeModel.acm (JSON)
  ↓
load_code_model_files() 
  ↓
Extract CodeCompilationUnit items, build set of normalized file paths
  ↓
Used for: (1) Enrollment expansion, (2) Normalization validation
```

**TransArc Result Loading:**

```
results/{project}/
  ├── sad-sam/sadSamTlr_{project}.csv      → load_result_sad_sam_standalone()
  ├── sam-code/samCodeTlr_{project}.csv    → load_result_sam_code_standalone()
  └── sad-code/
      ├── sadCodeTlr_{project}.csv         → load_result_sad_code() [final]
      ├── sadSamTlr_{project}.csv          → load_transarc_intermediate_sad_sam()
      └── samCodeTlr_{project}.csv         → load_transarc_intermediate_sam_code()
```

**Metrics Computation Pipeline:**

```
gold (set of links)  ┐
                     ├─→ calc_metrics() ─→ (precision, recall, f1, tp, fp, fn)
result (set of links)┘

For each project & task:
  1. Load gold standard (enroll if needed)
  2. Load result set
  3. Compute TP = gold ∩ result
  4. Compute FP = result - gold, FN = gold - result
  5. Calculate P = |TP| / |result|, R = |TP| / |gold|, F1 = 2PR / (P+R)
```

**Error Decomposition Flow (Analysis B):**

```
For each FP (S, C) in transarc_result - gs_sad_code:
  ├─ Find bridging models: M where (M, S) in intermediate_sad_sam
  │                              and (M, C) in intermediate_sam_code
  │
  ├─ Check correctness of components:
  │  ├─ Is (M, S) in gs_sad_sam? 
  │  │  ├─ YES: SAD-SAM correct, (M, C) error source
  │  │  └─ NO:  SAD-SAM wrong
  │  └─ Is (M, C) in gs_sam_code_enrolled?
  │     ├─ YES: SAM-CODE correct, (M, S) error source
  │     └─ NO:  SAM-CODE wrong
  │
  └─ Classify: SAD_SAM_CAUSED | SAM_CODE_CAUSED | BOTH_CAUSED | COMBINATION_ERROR
```

**Report Generation:**

```
Analysis scripts iterate over PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]
  │
  ├─ Load all data for project
  ├─ Compute findings (metrics, errors, distributions)
  ├─ Format as Markdown:
  │   - Summary tables (P/R/F1 for all projects)
  │   - Detailed analysis (top errors, distributions, insights)
  │   - Annotated examples (specific links, explanations)
  │
  └─ Write to reports/{ANALYSIS_NAME}.md
```

**State Management:**
- Immutable: Gold standards, code model, benchmark text (read-only from `/mnt/hostshare/ardoco-home/ardoco/`)
- Transient: All intermediate sets loaded on-demand per script execution
- Persistent: Final reports written to `/mnt/hostshare/ardoco-home/transarc-emp/reports/` as Markdown
- No inter-script state — each analysis script is self-contained

## Key Abstractions

**TraceLink Sets:**
- Purpose: Represent TLR results as Python sets of tuples for efficient boolean operations
- Formats:
  - SAD-SAM: `set((modelElementID: str, sentence: str))` — ~500–1000 links per project
  - SAM-CODE: `set((ae_id: str, code_path: str))` — ~200–5000 links per project (pre-enrollment)
  - SAD-CODE: `set((sentenceID: str, code_path: str))` — ~59–8268 links per project (post-enrollment)
- Operations: Intersection (∩), difference (-), union (∪), membership testing
- Pattern: All loaders normalize paths and return frozen sets; empty set if file missing

**Enrollment:**
- Purpose: Convert directory-level gold entries (`path/to/dir/`) to file-level entries using code model
- Algorithm: 
  ```
  for (id, path) in gold:
      if path.endswith("/"):
          for file in code_model if file.startswith(path):
              enrolled.add((id, file))
      else:
          enrolled.add((id, path))
  ```
- Inflation factors:
  - MediaStore: 1.0× (mostly file-level, 57 raw → 59 enrolled)
  - TeaStore: 10.1× (70 raw → 707 enrolled)
  - Teammates: 35.5× (228 raw → 8,097 enrolled)
  - BBB: 11.6× (132 raw → 1,529 enrolled)
  - JabRef: 217.6× (38 raw → 8,268 enrolled, 100% directory entries)
- Impact: Single raw entry can swing F1 by 0.01–0.04 pp (JabRef top entry = 972 files = 47% of gold)

**Intermediate Maps:**
- Purpose: Trace error sources through multi-stage pipeline
- Data structure:
  ```python
  sent_to_models: dict[sentenceID: str → set[modelElementID: str]]
  model_to_codes: dict[modelElementID: str → set[codePath: str]]
  model_to_sents: dict[modelElementID: str → set[sentenceID: str]]
  code_to_models: dict[codePath: str → set[modelElementID: str]]
  ```
- Built from: TransArc intermediate CSV files (same output as standalone sad-sam/sam-code, but generated as part of sad-code pipeline)
- Used for: FP decomposition (find bridging M for link (S,C)), TP gain estimation, cascade analysis

**FP Classification (dataclass):**
- Purpose: Categorize false positives by root cause for prioritization
- Fields:
  - `sad_sam_caused`: [(S, C, M, reason)] — SAD-SAM error, SAM-CODE correct
  - `sam_code_caused`: [(S, C, M, reason)] — SAD-SAM correct, SAM-CODE error
  - `both_caused`: [(S, C, M)] — Both components wrong
  - `combination_error`: [(S, C, M, reason)] — Each component correct separately, but composition is wrong
- Used by: Error amplification analysis, prioritization (SAD-SAM errors amplify ~85–972×)

**Path Normalization:**
- Purpose: Ensure consistent path representation across gold standards and results
- Pattern: Strip `Implementation/` prefix if present (appears in gold standards, not in intermediate results)
- Examples:
  - `Implementation/src/main/java/Foo.java` → `src/main/java/Foo.java`
  - `src/main/java/Foo.java` → `src/main/java/Foo.java` (unchanged)

## Entry Points

**Primary Analysis:**
- Location: `src/lib/transarc_error_analysis.py`
- Execution: `python3 src/lib/transarc_error_analysis.py` (optional main block)
- Responsibilities: 
  - Define all paths, constants, loaders, metrics
  - Export functions for use by other scripts
  - If run directly, execute Analysis A (baseline metrics) and Analysis B (FP decomposition)
  - Write `TRANSARC_EMPIRICAL_STUDY.md` to `reports/`

**Evaluation Scripts:**
- `src/evaluation/evaluation_critique.py`: Compare file-level vs. decision-level vs. component-level F1, show metric misleadingness
  - Output: `reports/EVALUATION_CRITIQUE.md`
  - Key finding: File-level rankings disagree with decision-level rankings (JabRef: 0.943 file F1 → 0.394 decision F1)
  
- `src/evaluation/extreme_baseline_analysis.py`: Implement 7 naive baselines (Oracle-Component, Oracle-SAM-CODE, Round-Robin, Random, Most-Popular, etc.)
  - Output: `reports/EXTREME_BASELINES.md`
  - Shows what baselines can achieve without learning

- `src/evaluation/s12c_sadcode_comparison.py`: Compare TransArc (sad-code) vs. S12C baseline
  - Output: `reports/S12C_VS_TRANSARC.csv`

**Bias Analysis Scripts:**
- `src/bias/benchmark_bias_study.py`: Gini analysis, position bias, exploitability via popularity baselines
  - Output: `reports/BENCHMARK_BIAS_STUDY.md`
  - Key finding: Gini coefficient 0.95–1.0 (extreme concentration); top-1 AE = 45% of SAD-CODE gold

- `src/bias/enrollment_distortion_analysis.py`: Impact of enrollment amplification on metric interpretation
  - Output: `reports/ENROLLMENT_DISTORTION_ANALYSIS.md`

- `src/bias/sam_code_distribution_analysis.py`: SAM-CODE link distribution (per-model concentration)
  - Output: `reports/SAM_CODE_DISTRIBUTION.md`

**Propagation Analysis Scripts:**
- `src/propagation/sad_sam_actual_contribution.py`: For each SAD-SAM TP, count how many SAD-CODE TPs it produces
  - Output: `reports/SAD_SAM_ACTUAL_CONTRIBUTION.md`
  - Key finding: SAD-SAM FNs account for 93.7% of SAD-CODE FPs; error amplification 1–972×

- `src/propagation/sad_sam_tp_gain_analysis.py`: For each SAD-SAM FN, compute potential SAD-CODE TP gain
  - Output: `reports/SAD_SAM_TP_GAIN_STUDY.md`
  - Shows which SAD-SAM FNs, if recovered, would provide largest SAD-CODE improvement

- `src/propagation/sam_code_cascade_analysis.py`: Trace each SAM-CODE link through pipeline to measure SAD-CODE impact
  - Output: `reports/SAM_CODE_CASCADE.md`

**Annotation Analysis Scripts:**
- `src/annotation/doc_structure_analysis_v2.py`: Extract document structure patterns, component names, aliases
  - Output: `reports/ANNOTATION_CONVENTION.md`

- `src/annotation/reverse_engineer_convention.py`: Discover labeling conventions from gold standards
  - Used for: Understanding how annotators decided what sentences to annotate

## Error Handling

**Strategy:** Defensive data loading with existence checks and empty set fallbacks

**Patterns:**
- Missing result files: `if not path.exists(): return set()` — Allows standalone task evaluation (e.g., evaluate sad-sam without results for sad-code)
- CSV parsing robustness: 
  - Optional column fallback: `row.get("ce_ids") or row.get("ce_id")` — Handle naming variants (teams uses ce_id singular, others plural)
  - Sentence-ID consistency: Convert to string universally (input CSVs use both int and string)
- Path normalization: Applied to ALL loaded paths (gold, results, intermediate) to ensure comparison validity
- Enrollment boundary: Exact `path.endswith("/")` check for directory markers
- Bridging validation: If FP (S,C) has no bridging M, classify as `combination_error` with reason `"no_bridge"` (should not occur with valid intermediates)
- Division by zero: All metric calculations guard against empty result sets (`if result else 0`)

## Cross-Cutting Concerns

**Logging:**
- Print to stdout with structured sections (Analysis A, B, C, etc.)
- Key metrics summarized at script end with 3–4 decimal places
- Findings compiled into Markdown table format for report inclusion

**Validation:**
- Expected values from Java test files: `EXPECTED` dict in `src/lib/transarc_error_analysis.py` (lines 71–93)
- Baseline comparison: "WARNING: {task}/{project}: actual >= expected" flagged if violated
- File existence validation in all loaders; graceful degradation if missing

**Configuration:**
- Hard-coded absolute paths using `Path` objects (environment-independent)
- Project list: `PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]`
- Gold standard mapping: Static dict per task (`GS_SAD_SAM`, `GS_SAM_CODE`, `GS_SAD_CODE`)

**Path Handling:**
- All paths normalized with `normalize_path()` to strip "Implementation/" prefix
- Benchmark paths: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/{project}/`
- Results paths: `/mnt/hostshare/ardoco-home/transarc-emp/results/{project}/{task}/`
- Reports output: `/mnt/hostshare/ardoco-home/transarc-emp/reports/`

---

*Architecture analysis: 2026-05-29*
