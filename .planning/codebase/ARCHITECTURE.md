# Architecture

**Analysis Date:** 2026-05-29

## Pattern Overview

**Overall:** Multi-stage empirical evaluation pipeline with layered analysis

**Key Characteristics:**
- Input: Gold standards + benchmark code models + ARDoCo results (sad-sam, sam-code, sad-code)
- Processing: Load, normalize, enroll, compute metrics, decompose errors
- Output: Markdown reports documenting performance, bias, error propagation
- Modular: Reusable infrastructure shared across analysis scripts
- Extensible: New baselines and metrics can build on common loaders

## Layers

**Data Infrastructure Layer:**
- Purpose: Load and normalize benchmark datasets, code models, and ARDoCo results
- Location: `src/lib/transarc_error_analysis.py`
- Contains: Path definitions, loaders for gold standards and results, metric calculators, normalization helpers
- Depends on: ARDoCo benchmark directory structure, TransArc results directory
- Used by: All analysis scripts in src/evaluation/, src/bias/, src/propagation/, src/annotation/

**Evaluation & Analysis Layer:**
- Purpose: Compute metrics, identify performance bottlenecks, and analyze error distributions
- Location: `src/evaluation/` (evaluation_critique.py, extreme_baseline_analysis.py, s12c_sadcode_comparison.py, etc.)
- Contains: Metric computation, baseline implementations, distributional analysis
- Depends on: Data Infrastructure Layer
- Used by: Report generation

**Bias & Distribution Analysis Layer:**
- Purpose: Quantify distributional properties and their impact on evaluation metrics
- Location: `src/bias/` (benchmark_bias_study.py, enrollment_distortion_analysis.py, etc.)
- Contains: Gini analysis, enrollment amplification tracking, position bias measurement
- Depends on: Data Infrastructure Layer, Evaluation metrics
- Used by: Report generation and improvement planning

**Error Propagation Layer:**
- Purpose: Trace false positives and false negatives back to component causes in intermediate stages
- Location: `src/propagation/` (sad_sam_actual_contribution.py, sad_sam_tp_gain_analysis.py, sam_code_cascade_analysis.py)
- Contains: FP/FN decomposition, intermediate stage linking, contribution analysis
- Depends on: Data Infrastructure Layer, Transitive link composition
- Used by: Root cause analysis and prioritization

**Annotation & Metadata Layer:**
- Purpose: Extract document structure, component names, and sentence metadata from benchmark
- Location: `src/annotation/` (doc_structure_analysis_v2.py, reverse_engineer_convention.py)
- Contains: Text parsing, model element name resolution, document structure patterns
- Depends on: Data Infrastructure Layer, Benchmark text and model files
- Used by: Understanding annotation conventions and document bias

## Data Flow

**Core Evaluation Pipeline:**

1. **Load Benchmark & Results** (`load_*` functions in `src/lib/transarc_error_analysis.py`)
   - Gold standards (CSV): SAD-SAM (sentence→model), SAM-CODE (model→code), SAD-CODE (sentence→code)
   - Code model (`.acm` JSON): Complete file paths and structure
   - ARDoCo results (CSV): TransArc SAD-CODE output + intermediates (SAD-SAM, SAM-CODE)
   - Text file: One sentence per line, indexed by line number

2. **Normalize Paths** (`normalize_path`)
   - Strip "Implementation/" prefix from gold standards and intermediates
   - Ensure consistent path representation across all datasets

3. **Enroll Gold Standards** (`enroll_gold_standard`)
   - Expand directory-level entries (ending with "/") to individual files using code model
   - Creates comprehensive ground truth for file-level metrics
   - Essential for SAM-CODE and SAD-CODE metrics

4. **Compute Metrics** (`calc_metrics`)
   - TP: result ∩ gold
   - FP: result - gold
   - FN: gold - result
   - Precision, Recall, F1

5. **Decompose Errors** (Analysis B, C, etc.)
   - For each FP, trace via intermediates: (S, C) → {(M, S), (M, C)} → error source
   - For each FN, compute potential TP gain if intermediate recovered
   - Categorize by root cause: SAD-SAM vs SAM-CODE

6. **Generate Reports** (Markdown)
   - Summary tables: metrics for all projects/tasks
   - Detailed analysis: annotated examples, distributions, impact metrics
   - Written to `/mnt/hostshare/ardoco-home/transarc-emp/reports/{REPORT}.md`

**Intermediate Data Flow (TransArc SAD-CODE analysis):**

```
sad-sam.csv (gold)  ─────┐
                           │
sad-sam.csv (result) ──────├──→ Enroll ─────→ Join ─────→ Metrics
                           │
sam-code.csv (gold) ──────┘
```

**Error Propagation Flow:**

```
TransArc FP (S, C)
    ↓
Extract M from intermediates: M where (M, S) in intermediate SAD-SAM
    ↓
Check:
  - Is (M, S) in gold SAD-SAM? → SAD-SAM error
  - Is (M, C) in gold SAM-CODE? → SAM-CODE error
  - Both correct but (S, C) not in gold? → Combination error
```

**State Management:**
- Data stored as Python sets for O(1) membership testing
- Dictionaries for mapping (sentence→models, model→codes, etc.)
- Results validated against expected thresholds from Java test files
- No persistent state between scripts — each script loads fresh from disk

## Key Abstractions

**Enrollment:**
- Purpose: Convert directory-level gold entries to comprehensive file-level ground truth
- Examples: `src/lib/transarc_error_analysis.py` lines 124-134
- Pattern: Iterate directory entries, expand to all files in `.acm` code model, preserve original mapping

**Transitive Composition:**
- Purpose: Bridge SAD-CODE via intermediate SAD-SAM and SAM-CODE results
- Examples: `src/propagation/sad_sam_tp_gain_analysis.py` lines 62-80
- Pattern: (M,S)∈SAD-SAM ∧ (M,C)∈SAM-CODE ⟹ (S,C)∈SAD-CODE

**Error Categorization:**
- Purpose: Classify false positives by root cause
- Examples: `src/lib/transarc_error_analysis.py` lines 349-400
- Pattern: Categories: SAD_SAM_CAUSED, SAM_CODE_CAUSED, BOTH_CAUSED, COMBINATION_ERROR
- Used to quantify error amplification and impact per stage

**Distributional Analysis:**
- Purpose: Quantify dataset bias and exploitability
- Examples: `src/bias/benchmark_bias_study.py` lines 66-80 (Gini coefficient)
- Pattern: Concentration metrics (Gini, entropy, position), long-tail identification, baseline comparison

## Entry Points

**Standalone Analysis Scripts:**
- `src/lib/transarc_error_analysis.py`: Primary analysis producing `TRANSARC_EMPIRICAL_STUDY.md` and baseline metrics
  - Location: `src/lib/transarc_error_analysis.py` lines 312-400+
  - Triggers: Manual execution `python3 src/lib/transarc_error_analysis.py`
  - Responsibilities: Load all data, compute metrics for all projects/tasks, decompose FPs/FNs, generate report

- `src/evaluation/evaluation_critique.py`: Metric adequacy analysis producing `EVALUATION_CRITIQUE.md`
  - Location: `src/evaluation/evaluation_critique.py` lines 35-200+
  - Triggers: Manual execution `python3 src/evaluation/evaluation_critique.py`
  - Responsibilities: Compare file-level F1 vs decision-level F1, show metric misleadingness, alternative metrics

- `src/bias/benchmark_bias_study.py`: Distributional bias analysis producing `BENCHMARK_BIAS_STUDY.md`
  - Location: `src/bias/benchmark_bias_study.py` lines 30-100+
  - Triggers: Manual execution `python3 src/bias/benchmark_bias_study.py`
  - Responsibilities: Gini analysis, position bias, baseline exploitability, long-tail identification

- `src/propagation/sad_sam_tp_gain_analysis.py`: Component-level impact analysis producing `SAD_SAM_TP_GAIN_STUDY.md`
  - Location: `src/propagation/sad_sam_tp_gain_analysis.py` lines 39-80+
  - Triggers: Manual execution `python3 src/propagation/sad_sam_tp_gain_analysis.py`
  - Responsibilities: For each SAD-SAM FN, compute potential SAD-CODE TP gain; rank by impact

- `src/evaluation/extreme_baseline_analysis.py`: Baseline comparison producing `EXTREME_BASELINES.md`
  - Location: `src/evaluation/extreme_baseline_analysis.py` lines 1-64+
  - Triggers: Manual execution `python3 src/evaluation/extreme_baseline_analysis.py`
  - Responsibilities: Implement 7 naive baselines (Oracle-Component, Round-Robin, etc.), compute metrics

## Error Handling

**Strategy:** Defensive loading with existence checks and graceful fallbacks

**Patterns:**
- `if not path.exists(): return empty_set` — Missing results produce empty sets, metrics degrade gracefully
- CSV parsing with optional column fallback: `row.get("ce_ids") or row.get("ce_id")` — Handle naming variants
- Validation warnings in output: "WARNING: {task}/{project}: {metric} (exp>={threshold})" — Flag failing expected values
- No exceptions raised for missing intermediate files — allows standalone task evaluation

## Cross-Cutting Concerns

**Logging:** Print to stdout with structured sections (Analysis A, B, C, etc.), written to report Markdown

**Validation:** Expected values from Java test files (`EXPECTED` dict in `src/lib/transarc_error_analysis.py` lines 71-93) used to flag mismatches

**Configuration:** Hard-coded paths using `Path` objects, environment-independent via absolute paths to ARDoCo benchmark and TransArc results

**Path normalization:** All paths normalized with `normalize_path()` to strip "Implementation/" prefix, ensure consistent comparison across gold and results

---

*Architecture analysis: 2026-05-29*
