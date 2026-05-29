# Codebase Structure

**Analysis Date:** 2026-05-29

## Directory Layout

```
transarc-emp/
├── src/                        # Analysis source code organized by phase
│   ├── lib/                    # Shared infrastructure
│   │   ├── transarc_error_analysis.py    # Data loaders, metrics, common analysis functions
│   │   └── new_metrics_analysis.py       # Experimental metrics
│   ├── evaluation/             # Metric adequacy & baseline analysis
│   │   ├── evaluation_critique.py        # File-level vs decision-level metrics
│   │   ├── extreme_baseline_analysis.py  # 7 oracle & naive baselines
│   │   ├── s12c_sadcode_comparison.py    # TransArc vs S12C comparison
│   │   ├── creative_metrics_analysis.py  # Alternative metric schemes
│   │   ├── holistic_metrics_analysis.py  # Metrics beyond P/R/F1
│   │   └── stupid_baseline_analysis.py   # Keyword & popularity baselines
│   ├── bias/                   # Distributional analysis and long-tail studies
│   │   ├── benchmark_bias_study.py       # Gini, position bias, exploitability
│   │   ├── enrollment_distortion_analysis.py  # Enrollment amplification impact
│   │   ├── enrollment_bias_analysis.py   # Directory vs file-level bias
│   │   └── sam_code_distribution_analysis.py  # Per-model concentration
│   ├── propagation/            # Error propagation & component-level impact
│   │   ├── sad_sam_tp_gain_analysis.py   # FN→TP gain if SAD-SAM recovered
│   │   ├── sad_sam_actual_contribution.py # Current TP contribution per element
│   │   └── sam_code_cascade_analysis.py  # SAM-CODE impact on SAD-CODE
│   └── annotation/             # Document structure & naming conventions
│       ├── doc_structure_analysis_v2.py  # Model names, sections, aliases
│       └── reverse_engineer_convention.py # Labeling convention discovery
├── results/                    # ARDoCo TransArc results per project/task
│   ├── mediastore/
│   ├── teastore/
│   ├── teammates/
│   ├── bigbluebutton/
│   └── jabref/
│       ├── sad-sam/            # SAD-SAM task results
│       │   └── sadSamTlr_jabref.csv
│       ├── sam-code/           # SAM-CODE task results
│       │   └── samCodeTlr_jabref.csv
│       └── sad-code/           # SAD-CODE task results (TransArc composition)
│           ├── sadCodeTlr_jabref.csv    # Final SAD-CODE output
│           ├── sadSamTlr_jabref.csv     # Intermediate SAD-SAM
│           └── samCodeTlr_jabref.csv    # Intermediate SAM-CODE
├── reports/                    # Analysis output (Markdown files)
│   ├── TRANSARC_EMPIRICAL_STUDY.md                # Main baseline metrics
│   ├── BENCHMARK_BIAS_STUDY.md                    # Distributional analysis
│   ├── EVALUATION_CRITIQUE.md                     # Metric inadequacy
│   ├── SAD_SAM_ACTUAL_CONTRIBUTION.md             # Component impact
│   ├── SAD_SAM_TP_GAIN_STUDY.md                   # Recovery potential
│   ├── SAM_CODE_CASCADE.md                        # Error propagation
│   ├── EXTREME_BASELINES.md                       # Oracle/naive baselines
│   ├── ANNOTATION_CONVENTION.md                   # Document structure
│   ├── ENROLLMENT_BIAS_ANALYSIS.md                # Enrollment effects
│   ├── CREATIVE_METRICS.md                        # Alternative metrics
│   ├── HOLISTIC_METRICS.md                        # Beyond P/R/F1
│   ├── NEW_METRICS_REPORT.md                      # Additional schemes
│   ├── SAM_CODE_DISTRIBUTION.md                   # Model concentration
│   ├── STUPID_BASELINES.md                        # Keyword/popularity
│   ├── SUB_COMPONENT_ANALYSIS.md                  # Granularity studies
│   ├── METRIC_LIMITATIONS_ANALYSIS.md             # Metric critique
│   ├── S12C_VS_TRANSARC.csv                       # Project comparison data
│   └── .~lock.S12C_VS_TRANSARC.csv#               # File lock
├── writing/                    # Paper & documentation
│   └── eval.tex                # LaTeX evaluation chapters (2-chapter structure)
├── archive/                    # Previous experiments & ablations (inactive)
│   ├── llm_classifications/            # LLM classification results
│   ├── llm_classifications_improved/   # Meta-learning variants
│   ├── llm_classifications_multi/      # Multi-agent LLM
│   ├── llm_classifications_precision/  # Precision classifier
│   ├── llm_cache_swattr/               # LLM call cache
│   ├── sentence_classification/        # Sentence-level experiments
│   ├── llm_*.py                        # LLM baseline scripts (20+)
│   ├── swattr_*.py                     # SWATTR variants (15+)
│   ├── {THREE,FOUR}_SYSTEM_COMPARISON.md  # Multi-system comparisons
│   ├── LLM_BASELINE.md, LLM_IMPROVED_*.md # LLM reports
│   ├── SWATTR_*.md                     # SWATTR analysis reports
│   └── README.md                       # Archive documentation
├── .planning/                  # Generated architecture docs
│   └── codebase/              # GSD agent-generated codebase maps
│       ├── ARCHITECTURE.md
│       ├── STRUCTURE.md (this file)
│       ├── CONVENTIONS.md
│       ├── TESTING.md
│       ├── STACK.md
│       ├── INTEGRATIONS.md
│       └── CONCERNS.md
├── .git/                       # Git version control
├── .gitignore                  # Excludes: results/, archive/, .env
├── bench-paper.pdf             # Background reference material
└── .claude/                    # Claude Code cache
```

## Directory Purposes

**src/ (Analysis Source Code)**
- Purpose: Python scripts implementing empirical analysis pipelines
- Contains: Entry points for all analyses, shared infrastructure, specialized phases
- Key dependency: All scripts import from `src/lib/transarc_error_analysis.py`
- Execution: Run scripts directly with `python3 src/{phase}/{script}.py`

**src/lib/ (Shared Infrastructure)**
- Purpose: Centralized data loading, metric computation, common utilities
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/src/lib/`
- Contains:
  - `transarc_error_analysis.py` (55 KB, 1200+ lines):
    - Path constants: `BENCHMARK` (ARDoCo), `RESULTS` (TransArc), project list
    - Data loaders for gold standards and results (14+ functions)
    - Enrollment logic: expand directory-level gold entries to files
    - Metric calculation: `calc_metrics(gold, result)` → (P, R, F1, TP, FP, FN)
    - Error classification: `FPClassification` dataclass + Analysis B logic
    - Expected values from Java tests
    - Analysis functions: `analysis_a()`, `analysis_b()`, `analysis_c()`
  - `new_metrics_analysis.py` (56 KB): Experimental metric schemes (archived approach)
- Key exports:
  - Constants: `PROJECTS`, `BENCHMARK`, `RESULTS`, `GS_SAD_SAM`, `GS_SAM_CODE`, `GS_SAD_CODE`, `ACM_FILES`, `TEXT_FILES`, `EXPECTED`
  - Functions: `load_gs_sad_sam`, `load_result_sad_code`, `calc_metrics`, `normalize_path`, `enroll_gold_standard`

**src/evaluation/ (Metric Adequacy & Baseline Analysis)**
- Purpose: Analyze evaluation methodology, implement baselines, critique metrics
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/src/evaluation/`
- Scripts:
  - `evaluation_critique.py` (61 KB): Why file-level micro-F1 is misleading; compares file-level vs decision-level vs component-level metrics; shows ranking disagreements
    - Output: `reports/EVALUATION_CRITIQUE.md`
    - Key finding: JabRef file F1=0.943 (best) → decision F1=0.394 (worst)
  
  - `extreme_baseline_analysis.py` (28 KB): 7 naive baselines testing data exploitability
    - Baselines: Oracle-Component, Oracle-SAM-CODE, Round-Robin, Random, Most-Popular, Same-For-All, Frequency-Based
    - Output: `reports/EXTREME_BASELINES.md`
  
  - `s12c_sadcode_comparison.py` (14 KB): Compare TransArc (sad-code) vs S12C baseline per project
    - Output: `reports/S12C_VS_TRANSARC.csv`
  
  - `creative_metrics_analysis.py` (27 KB): Component-level F1, sentence coverage, concentration metrics
    - Output: `reports/CREATIVE_METRICS.md`
  
  - `holistic_metrics_analysis.py` (27 KB): Metrics beyond P/R/F1
    - Output: `reports/HOLISTIC_METRICS.md`
  
  - `stupid_baseline_analysis.py` (29 KB): Minimally intelligent baselines (keyword grep, popularity)
    - Output: `reports/STUPID_BASELINES.md`

**src/bias/ (Distributional Analysis)**
- Purpose: Quantify dataset bias, long-tail effects, metric exploitability
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/src/bias/`
- Scripts:
  - `benchmark_bias_study.py` (30 KB): Gini coefficient, position bias, long-tail identification
    - Analysis: Per-project distribution of gold entries; popularity baselines; long-tail concentration
    - Output: `reports/BENCHMARK_BIAS_STUDY.md`
    - Key finding: Gini 0.95–1.0 (extreme concentration); top-1 AE = 45% of SAD-CODE gold
  
  - `enrollment_distortion_analysis.py` (19 KB): How enrollment amplification (1–217× inflation) distorts metrics
    - Output: `reports/ENROLLMENT_DISTORTION_ANALYSIS.md`
  
  - `enrollment_bias_analysis.py` (19 KB): Directory-level vs file-level bias measurement
    - Output: `reports/ENROLLMENT_BIAS_ANALYSIS.md`
  
  - `sam_code_distribution_analysis.py` (30 KB): SAM-CODE concentration across projects per model element
    - Output: `reports/SAM_CODE_DISTRIBUTION.md`

**src/propagation/ (Error Propagation & Impact)**
- Purpose: Trace errors back to source stages, compute component-level impact
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/src/propagation/`
- Scripts:
  - `sad_sam_tp_gain_analysis.py` (36 KB): If we recovered this SAD-SAM FN, how many SAD-CODE TPs would we gain?
    - Analysis: Rank SAD-SAM FNs by potential impact; estimate maximum achievable F1
    - Output: `reports/SAD_SAM_TP_GAIN_STUDY.md`
    - Key finding: 95.4% of recoverable SAD-CODE FNs from SAD-SAM FNs; some FNs worth 1000+ TPs each
  
  - `sad_sam_actual_contribution.py` (41 KB): Current SAD-SAM TP contribution to SAD-CODE results
    - Analysis: For each SAD-SAM TP, count actual SAD-CODE TPs it produces; amplification factors
    - Output: `reports/SAD_SAM_ACTUAL_CONTRIBUTION.md`
    - Key finding: SAD-SAM FNs cause 93.7% of SAD-CODE FPs; error amplification 1–972×
  
  - `sam_code_cascade_analysis.py` (21 KB): Trace each SAM-CODE link through pipeline to measure SAD-CODE impact
    - Analysis: For each SAM-CODE TP/FP, compute its contribution to SAD-CODE; holistic view
    - Output: `reports/SAM_CODE_CASCADE.md`

**src/annotation/ (Document Structure Analysis)**
- Purpose: Extract metadata, naming conventions, and structural patterns
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/src/annotation/`
- Scripts:
  - `doc_structure_analysis_v2.py` (50 KB): Resolve all model element names; identify sections and aliases
    - Analysis: Map model element IDs to human-readable names; find document structure patterns
    - Output: `reports/ANNOTATION_CONVENTION.md`
  
  - `reverse_engineer_convention.py` (30 KB): Infer annotation labeling convention from gold standards
    - Analysis: Discover what annotators considered "relevant" (boundaries, inclusion criteria)
    - Helps understand gold standard construction bias

**results/ (ARDoCo TransArc Results)**
- Purpose: Store computed traceability links per project and task
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/results/`
- Structure:
  - One subdirectory per project: `mediastore/`, `teastore/`, `teammates/`, `bigbluebutton/`, `jabref/`
  - Each project has three task directories: `sad-sam/`, `sam-code/`, `sad-code/`
  - CSV files per task with results
- File naming: `{TaskType}Tlr_{project}.csv` (camelCase task, snake_case project)
  - Example: `sadSamTlr_mediastore.csv`, `samCodeTlr_teastore.csv`, `sadCodeTlr_jabref.csv`
- Column formats:
  - **SAD-SAM**: `modelElementID` (UUID), `sentence` (text string or index)
  - **SAM-CODE (standalone)**: `sentenceID` (model element ID), `codeID` (file path)
  - **SAM-CODE (intermediate in sad-code/)**: `sentenceID` (sentence number), `codeID` (file path)
  - **SAD-CODE**: `modelElementID` (sentence number as string), `codeId` (file path, note lowercase 'd')
- Accessed by: All loaders in `src/lib/transarc_error_analysis.py` via hardcoded paths

**reports/ (Analysis Output)**
- Purpose: Markdown documents containing analysis results and findings
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/reports/`
- Contains: 16 Markdown reports (see file list above) + 1 CSV comparison data file
- Format: Structured Markdown with tables, sections, annotated examples, rankings
- Audience: Researchers analyzing TransArc performance, data properties, and metric adequacy
- Key reports:
  - `TRANSARC_EMPIRICAL_STUDY.md` — Baseline metrics (P/R/F1), error decomposition per project
  - `BENCHMARK_BIAS_STUDY.md` — Distributional analysis, Gini coefficient, long-tail identification
  - `EVALUATION_CRITIQUE.md` — Why file-level metrics misleading, metric ranking disagreements
  - `EXTREME_BASELINES.md` — Oracle and naive baselines showing data exploitability limits
  - `SAD_SAM_TP_GAIN_STUDY.md` — Per-component SAD-SAM FN recovery potential
  - `SAM_CODE_CASCADE.md` — Error propagation through transitive composition
  - Plus: Bias analysis, annotation convention, creative/holistic metrics, comparisons

**writing/ (Paper & Documentation)**
- Purpose: LaTeX source for research paper evaluation section
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/writing/`
- Files:
  - `eval.tex` — Two-chapter structure:
    - Chapter 1: Distributional Inequality in the ARDoCo Benchmark
    - Chapter 2: Comprehensive Evaluation Metrics
  - Can be compiled standalone or `\input{eval}` from larger paper
  - Status: Integration target for findings from `reports/` via manual extraction

**archive/ (Archived Experiments)**
- Purpose: Historical variants, ablations, and previous approaches (reference only)
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/archive/`
- Contains: ~50 scripts and ~20 reports organized by approach
- Notable subdirectories:
  - `llm_classifications/` — LLM-based SAD-SAM baseline results (single-agent)
  - `llm_classifications_improved/` — Meta-learning approach with per-project analysis
  - `llm_classifications_multi/` — Multi-agent LLM variants
  - `llm_classifications_precision/` — Precision classifier experiments
  - `llm_cache_swattr/` — LLM call cache for reproducibility
  - `sentence_classification/` — Sentence-level component assignment experiments
- Notable reports: `LLM_BASELINE.md`, `FOUR_SYSTEM_COMPARISON.md`, `SWATTR_LLM_FEWSHOT.md`, etc.
- Status: Reference only; active analysis in `src/` supersedes these implementations

**.planning/codebase/ (Architecture Documentation)**
- Purpose: GSD agent-generated codebase maps for future execution by `/gsd-plan-phase` and `/gsd-execute-phase`
- Location: `/mnt/hostshare/ardoco-home/transarc-emp/.planning/codebase/`
- Files: Auto-generated Markdown docs
  - `ARCHITECTURE.md` — Data pipeline, error propagation, key abstractions
  - `STRUCTURE.md` — Directory layout, file locations, naming conventions (this file)
  - `CONVENTIONS.md` — Coding style, import organization, module design patterns
  - `TESTING.md` — Test patterns and infrastructure (if applicable)
  - `STACK.md` — Technology stack and runtimes
  - `INTEGRATIONS.md` — External integrations (ARDoCo, benchmark)
  - `CONCERNS.md` — Technical debt and known issues
- Format: Markdown; consumed by GSD planning/execution agents
- Generated: By `/gsd-map-codebase` agent on-demand

## Key File Locations

**Executable Entry Points (Analysis Scripts):**
- `src/lib/transarc_error_analysis.py` — Primary analysis: metrics, error decomposition
- `src/evaluation/evaluation_critique.py` — Metric adequacy (file vs decision vs component-level)
- `src/bias/benchmark_bias_study.py` — Distributional analysis (Gini, position bias)
- `src/propagation/sad_sam_tp_gain_analysis.py` — Component-level impact analysis
- `src/evaluation/extreme_baseline_analysis.py` — Baseline implementations
- `src/propagation/sad_sam_actual_contribution.py` — Current TP contribution per element
- `src/propagation/sam_code_cascade_analysis.py` — Error cascade analysis
- `src/annotation/doc_structure_analysis_v2.py` — Document structure patterns

**Shared Infrastructure:**
- `src/lib/transarc_error_analysis.py` (55 KB, ~1200 lines)
  - Exported by all analysis scripts via: `from transarc_error_analysis import BENCHMARK, RESULTS, PROJECTS, load_gs_*, load_result_*, calc_metrics, normalize_path, enroll_gold_standard`

**Configuration & Constants (src/lib/transarc_error_analysis.py):**
- Lines 20–26: `BENCHMARK`, `RESULTS` paths
- Lines 30–60: Gold standard file mappings (`GS_SAD_SAM`, `GS_SAM_CODE`, `GS_SAD_CODE`)
- Lines 54–60: Code model paths (`ACM_FILES`), text file paths (`TEXT_FILES`)
- Lines 26: `PROJECTS` = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]
- Lines 71–93: Expected values from Java tests (`EXPECTED` dict)

**Result Directory Paths (hardcoded in loaders):**
- Standalone SAD-SAM: `results/{project}/sad-sam/sadSamTlr_{project}.csv`
- Standalone SAM-CODE: `results/{project}/sam-code/samCodeTlr_{project}.csv`
- SAD-CODE final output: `results/{project}/sad-code/sadCodeTlr_{project}.csv`
- SAD-CODE intermediate SAD-SAM: `results/{project}/sad-code/sadSamTlr_{project}.csv`
- SAD-CODE intermediate SAM-CODE: `results/{project}/sad-code/samCodeTlr_{project}.csv`

**Gold Standard Paths (ARDoCo Benchmark):**
- Base: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
- Gold standards: `{project}/goldstandards/goldstandard_{task1}-{task2}_{year}.csv`
- Code models: `{project}/model_{year}/code/codeModel.acm` (JSON format)
- Documentation: `{project}/text_{year}/{project}.txt` (one sentence per line)

**Report Output Paths:**
- Base: `/mnt/hostshare/ardoco-home/transarc-emp/reports/`
- Format: `{ANALYSIS_NAME}.md` (uppercase with underscores)
- Example: `BENCHMARK_BIAS_STUDY.md`, `SAD_SAM_TP_GAIN_STUDY.md`, `TRANSARC_EMPIRICAL_STUDY.md`

## Naming Conventions

**Python Files:**
- Analysis scripts: `{topic}_{detail}.py` (snake_case, lowercase)
  - Examples: `benchmark_bias_study.py`, `sad_sam_tp_gain_analysis.py`, `extreme_baseline_analysis.py`
- Shared library: `transarc_error_analysis.py`, `new_metrics_analysis.py`
- Archived: Same pattern, organized in `archive/{category}/`

**Result CSV Files:**
- Format: `{TaskType}Tlr_{project}.csv` (camelCase task + Tlr, snake_case project)
- Examples:
  - `sadSamTlr_mediastore.csv` (SAD-SAM results)
  - `samCodeTlr_teastore.csv` (SAM-CODE results)
  - `sadCodeTlr_jabref.csv` (SAD-CODE results)

**Report Markdown Files:**
- Format: `UPPERCASE_WITH_UNDERSCORES.md`
- Examples: `BENCHMARK_BIAS_STUDY.md`, `SAD_SAM_TP_GAIN_STUDY.md`, `EVALUATION_CRITIQUE.md`

**Directories:**
- Task-specific: `sad-sam/`, `sam-code/`, `sad-code/` (lowercase with hyphens)
- Analysis phases: `evaluation/`, `bias/`, `propagation/`, `annotation/` (lowercase, single purpose)
- Data: `results/`, `reports/`, `archive/` (lowercase, content type)
- Internal: `.planning/`, `.git/`, `.claude/` (dotted, system use)

**Variables & Functions (Python):**
- Gold standard sets: `gs_{task}` (e.g., `gs_sad_sam`, `gs_sad_code_enrolled`)
- Result sets: `result_{task}` (e.g., `result_sad_code`)
- Mapping dicts: `{entity}_to_{other}` (e.g., `sent_to_models`, `model_to_codes`)
- Loaders: `load_{entity}_{variant}` (e.g., `load_gs_sad_sam()`, `load_result_sad_code()`)
- Helpers: snake_case (e.g., `calc_metrics()`, `normalize_path()`, `enroll_gold_standard()`)
- Analysis functions: `analysis_{letter}()` (e.g., `analysis_a()`, `analysis_b()`)

**CSV Column Names:**
- SAD-SAM gold: `modelElementID`, `sentence`
- SAM-CODE gold: `ae_id`, `ae_name`, `ce_ids` (or `ce_id` for teammates)
- SAD-CODE gold: `sentenceID`, `codeID`
- TransArc SAD-CODE output: `modelElementID`, `codeId` (note: `codeId` lowercase 'd', differs from input)

## Where to Add New Code

**New Analysis Script (experiment phase):**
1. Create: `src/{phase}/{analysis_name}.py` where phase ∈ {evaluation, bias, propagation, annotation}
2. Import infrastructure:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
   from transarc_error_analysis import (
       BENCHMARK, RESULTS, PROJECTS, 
       load_gs_sad_sam, load_result_sad_code, calc_metrics, normalize_path, etc.
   )
   ```
3. Iterate over `PROJECTS`, load data via exported functions
4. Write findings to: `reports/{ANALYSIS_NAME}.md` (use `OUTPUT_MD = Path(...)`constant)
5. Example: `src/evaluation/creative_metrics_analysis.py` lines 1–60 (imports and setup)

**New Evaluation Metric:**
1. Add function to `src/lib/transarc_error_analysis.py`:
   ```python
   def compute_{metric_name}(gold, result, ...):
       """Returns {return type}. Documentation."""
       ...
   ```
2. Export by adding to docstring or by being in module
3. Import and call from analysis scripts
4. Document return value and interpretation
5. Example: `calc_metrics(gold, result)` at line 296 returns 6-tuple (P, R, F1, TP, FP, FN)

**New Baseline Implementation:**
1. Add to `src/evaluation/extreme_baseline_analysis.py` or create new file in `src/evaluation/`
2. Function signature:
   ```python
   def {baseline_name}_baseline(project, code_model_files, gs_sad_code):
       """Returns set((sentenceID, codePath))."""
       ...
   ```
3. Call `calc_metrics(gs_sad_code, result_set)` to compute P/R/F1
4. Aggregate results in final report table
5. Example: Lines 66–100 show 3 baseline implementations with full metric computation

**New Data Import:**
1. If new result file type: Add loader to `src/lib/transarc_error_analysis.py`
   ```python
   def load_{entity}_{variant}(project):
       """Returns set() or dict(). Documentation."""
       path = RESULTS / project / "..." / f"{filename}_{project}.csv"
       ...
       return normalize_path(path)  # Applied to all paths
   ```
2. Handle optional columns with `.get()` fallback: `row.get("ce_ids") or row.get("ce_id")`
3. Test with at least one project
4. Example: Lines 199–232 show result loaders (`load_result_sad_code`, `load_transarc_intermediate_sad_sam`)

**Archived Experiments:**
1. When analysis complete or superseded: Move scripts to `archive/{category}/`
   - Categories: `llm_*/`, `swattr_*/`, etc.
2. Create README in archive subdirectory: Approach, findings, why superseded
3. Keep `src/` tree clean for active analysis only
4. Example: `archive/llm_improved_classifier.py` + `archive/LLM_IMPROVED_CLASSIFIER.md`

## Special Directories

**results/ (Generated Output from ARDoCo)**
- Purpose: Store TransArc execution results per project/task
- Generated: By ARDoCo TransArc implementation (external to this codebase)
- Committed: Yes, benchmarks for empirical study
- Size: ~1 MB total (1000–20000 links per project/task)
- Accessed by: All loaders in `src/lib/transarc_error_analysis.py`

**reports/ (Generated Analysis Documents)**
- Purpose: Store human-readable Markdown reports of empirical findings
- Generated: By scripts in `src/` (e.g., `python3 src/lib/transarc_error_analysis.py`)
- Committed: Yes, part of research record
- Size: ~500 KB total
- Format: Markdown with tables, sections, code examples, annotated trace examples

**archive/ (Historical Artifacts)**
- Purpose: Keep record of previous approaches and ablations
- Generated: Previous versions of analysis scripts, LLM classification attempts, etc.
- Committed: Yes, for reproducibility and methodology transparency
- Size: ~2 MB (50 scripts + 20 reports)
- Status: Inactive in current pipeline; for reference only

**.planning/codebase/ (Architecture Documentation)**
- Purpose: GSD agent-generated codebase maps for future execution
- Generated: By `/gsd-map-codebase` agent on-demand
- Committed: Optional (useful for next agent context)
- Format: Markdown; consumed by `/gsd-plan-phase` and `/gsd-execute-phase`
- Files: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, STACK.md, INTEGRATIONS.md, CONCERNS.md

---

*Structure analysis: 2026-05-29*
