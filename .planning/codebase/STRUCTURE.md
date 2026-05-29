# Codebase Structure

**Analysis Date:** 2026-05-29

## Directory Layout

```
transarc-emp/
├── src/                        # Analysis source code organized by phase
│   ├── lib/                    # Shared infrastructure
│   │   └── transarc_error_analysis.py    # Data loaders, metrics, common analysis functions
│   ├── evaluation/             # Metric adequacy & baseline analysis
│   ├── bias/                   # Distributional analysis and long-tail studies
│   ├── propagation/            # Error propagation & component-level impact
│   └── annotation/             # Document structure & naming conventions
├── results/                    # ARDoCo TransArc results per project
│   ├── mediastore/
│   ├── teastore/
│   ├── teammates/
│   ├── bigbluebutton/
│   └── jabref/
│       ├── sad-sam/            # SAD-SAM task results
│       │   └── sadSamTlr_*.csv
│       ├── sam-code/           # SAM-CODE task results
│       │   └── samCodeTlr_*.csv
│       └── sad-code/           # SAD-CODE task results (TransArc)
│           ├── sadCodeTlr_*.csv       # Final output
│           ├── sadSamTlr_*.csv        # Intermediate SAD-SAM
│           └── samCodeTlr_*.csv       # Intermediate SAM-CODE
├── reports/                    # Analysis output (Markdown files)
│   ├── TRANSARC_EMPIRICAL_STUDY.md
│   ├── BENCHMARK_BIAS_STUDY.md
│   ├── EVALUATION_CRITIQUE.md
│   ├── SAD_SAM_TP_GAIN_STUDY.md
│   ├── EXTREME_BASELINES.md
│   └── [10+ other analysis reports]
├── writing/                    # Paper / documentation
│   └── eval.tex                # LaTeX evaluation chapter
├── archive/                    # Previous experiments & ablations (not active)
│   ├── llm_classifications/    # LLM-based baseline results
│   ├── swattr_*/               # SWATTR variants & comparisons
│   ├── llm_*/                  # LLM baseline experiments
│   └── sentence_classification/ # Sentence-level classification attempts
├── .planning/                  # Generated architecture docs
│   └── codebase/              # This directory
├── .git/                       # Version control
├── .gitignore                 # Excludes results/, archive/
└── bench-paper.pdf            # Background reference material
```

## Directory Purposes

**src/ (Analysis Source Code)**
- Purpose: Python scripts implementing analysis pipelines
- Contains: Main analysis entry points, shared infrastructure, specialized analysis modules
- Key files: `src/lib/transarc_error_analysis.py` (foundational data loaders and metric calculation)

**src/lib/ (Shared Infrastructure)**
- Purpose: Centralized data loading, metric computation, common utilities
- Contains: 
  - Path constants to ARDoCo benchmark and results directories
  - Gold standard loaders (SAD-SAM, SAM-CODE, SAD-CODE raw and enrolled)
  - Result loaders (standalone and intermediate TransArc results)
  - Enrollment logic (directory expansion using `.acm` code model)
  - Metric calculation (`calc_metrics` returns P/R/F1/TP/FP/FN)
  - Expected value thresholds from Java test files
- Key files: `src/lib/transarc_error_analysis.py`

**src/evaluation/ (Metric Adequacy & Baseline Analysis)**
- Purpose: Analyze evaluation methodology, implement baseline systems
- Contains:
  - `evaluation_critique.py` — Why file-level F1 is misleading; decision-level vs file-level metrics
  - `extreme_baseline_analysis.py` — 7 naive baselines (Oracle-Component, Round-Robin, Optimal-Constant, etc.)
  - `creative_metrics_analysis.py` — Alternative metrics (component-level F1, sentence-centric metrics)
  - `s12c_sadcode_comparison.py` — Compare project-level S12C vs TransArc performance
  - `holistic_metrics_analysis.py` — Metrics beyond P/R/F1 (sentence coverage, component concentration)
  - `stupid_baseline_analysis.py` — Minimally intelligent baselines (keyword grep, popularity-based)

**src/bias/ (Distributional Analysis)**
- Purpose: Quantify dataset bias, long-tail effects, exploitability
- Contains:
  - `benchmark_bias_study.py` — Gini coefficient, position bias, long-tail distribution analysis
  - `enrollment_distortion_analysis.py` — How enrollment amplification distorts metrics
  - `enrollment_bias_analysis.py` — Directory-level vs file-level bias measurement
  - `sam_code_distribution_analysis.py` — SAM-CODE concentration across projects
- Focus: Showing where dataset bias enables naive baselines to succeed

**src/propagation/ (Error Propagation & Impact)**
- Purpose: Trace errors back to source stages, compute component-level impact
- Contains:
  - `sad_sam_tp_gain_analysis.py` — If we recovered this SAD-SAM FN, how many SAD-CODE TPs would we gain?
  - `sad_sam_actual_contribution.py` — Current SAD-SAM TP contribution to SAD-CODE results
  - `sam_code_cascade_analysis.py` — How SAM-CODE errors propagate to SAD-CODE FPs/FNs
- Focus: Bottleneck identification and fix impact simulation

**src/annotation/ (Document Structure Analysis)**
- Purpose: Extract metadata, naming conventions, and structural patterns
- Contains:
  - `doc_structure_analysis_v2.py` — Resolve all model element names, identify sections and aliases
  - `reverse_engineer_convention.py` — Infer annotation labeling convention from gold standards
- Focus: Understanding document bias and gold standard construction

**results/ (ARDoCo TransArc Results)**
- Purpose: Store computed traceability links per project and task
- Contains: One subdirectory per project (mediastore, teastore, teammates, bigbluebutton, jabref)
- Structure per project:
  - `sad-sam/sadSamTlr_{project}.csv` — Standalone SAD-SAM task output (columns: modelElementID, sentence)
  - `sam-code/samCodeTlr_{project}.csv` — Standalone SAM-CODE task output (columns: sentenceID, codeID)
  - `sad-code/sadCodeTlr_{project}.csv` — Final TransArc SAD-CODE output (columns: modelElementID, codeId)
  - `sad-code/sadSamTlr_{project}.csv` — Intermediate SAD-SAM within TransArc pipeline
  - `sad-code/samCodeTlr_{project}.csv` — Intermediate SAM-CODE within TransArc pipeline
- Naming: File format: `{TaskName}Tlr_{project}.csv` (camelCase task, snake_case project)
- Column differences:
  - SAD-SAM: `modelElementID` (UUID), `sentence` (text string)
  - SAM-CODE: `sentenceID` (model element ID in standalone; sentence number in transitive), `codeID` (file path without `Implementation/` prefix)
  - SAD-CODE: `modelElementID` (sentence number as string), `codeId` (file path, note lowercase 'd')

**reports/ (Analysis Output)**
- Purpose: Markdown documents containing analysis results and findings
- Contains: 14+ analysis reports (see list below)
- Format: Structured Markdown with tables, sections, annotated examples
- Audience: Researchers analyzing TransArc performance and data properties
- Key reports:
  - `TRANSARC_EMPIRICAL_STUDY.md` — Primary baseline metrics and error decomposition
  - `BENCHMARK_BIAS_STUDY.md` — Distributional analysis and exploitability
  - `EVALUATION_CRITIQUE.md` — Why file-level metrics are misleading
  - `EXTREME_BASELINES.md` — Oracle and naive baselines showing dataset exploitation
  - `SAD_SAM_TP_GAIN_STUDY.md` — Component-level impact analysis
  - `SAM_CODE_CASCADE.md` — Error propagation through transitive composition
  - Plus: `ANNOTATION_CONVENTION.md`, `CREATIVE_METRICS.md`, `HOLISTIC_METRICS.md`, `NEW_METRICS_REPORT.md`, etc.

**writing/ (Paper & Documentation)**
- Purpose: LaTeX source for research paper evaluation section
- Contains: `eval.tex` — Two-chapter structure for empirical study results
- Status: Integration target for reports via extracted findings

**archive/ (Archived Experiments)**
- Purpose: Historical variants, ablations, and previous approaches (not active)
- Contains: ~50 scripts organized by approach (LLM baselines, SWATTR variants, sentence classification)
- Status: Reference only; code in src/ supersedes these implementations
- Notable subdirectories:
  - `llm_classifications/` — LLM-based SAD-SAM baseline results
  - `llm_classifications_improved/` — Meta-learning approach with per-project analysis
  - `llm_cache_swattr/` — LLM call cache for reproducibility
  - `sentence_classification/` — Sentence-level component assignment experiments
- Reports: `LLM_BASELINE.md`, `FOUR_SYSTEM_COMPARISON.md`, `SWATTR_LLM_FEWSHOT.md`, etc.

## Key File Locations

**Entry Points (Executable Scripts):**
- `src/lib/transarc_error_analysis.py` — Primary analysis: metrics, error decomposition, report generation
- `src/evaluation/evaluation_critique.py` — Metric adequacy analysis
- `src/bias/benchmark_bias_study.py` — Distributional analysis
- `src/propagation/sad_sam_tp_gain_analysis.py` — Component-level impact
- `src/evaluation/extreme_baseline_analysis.py` — Baseline implementations

**Infrastructure / Shared Code:**
- `src/lib/transarc_error_analysis.py` — Core data loaders, shared by all analysis scripts
  - `BENCHMARK` path: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark`
  - `RESULTS` path: `/mnt/hostshare/ardoco-home/transarc-emp/results`
  - Functions: `load_gs_sad_sam`, `load_gs_sam_code_raw`, `load_gs_sad_code_enrolled`, `load_result_sad_code`, `calc_metrics`, `normalize_path`, `enroll_gold_standard`, etc.

**Configuration & Constants:**
- `src/lib/transarc_error_analysis.py` lines 20-93:
  - Project list: `PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]`
  - Gold standard paths: `GS_SAD_SAM`, `GS_SAM_CODE`, `GS_SAD_CODE` (dicts mapping project → CSV path)
  - Code model paths: `ACM_FILES` (dicts mapping project → `.acm` file path)
  - Text paths: `TEXT_FILES` (dicts mapping project → `.txt` file path)
  - Expected values: `EXPECTED` (nested dicts with P/R/F1 thresholds from Java tests)

**Result Directory Structure:**
- Golden paths hardcoded in loaders:
  - `results/{project}/sad-sam/sadSamTlr_{project}.csv`
  - `results/{project}/sam-code/samCodeTlr_{project}.csv`
  - `results/{project}/sad-code/sadCodeTlr_{project}.csv` (final output)
  - `results/{project}/sad-code/sadSamTlr_{project}.csv` (intermediate)
  - `results/{project}/sad-code/samCodeTlr_{project}.csv` (intermediate)

**Gold Standard Paths (ARDoCo Benchmark):**
- `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/{project}/goldstandards/`
  - `goldstandard_sad_*-sam_*.csv` (SAD-SAM gold)
  - `goldstandard_sam_*-code_*.csv` (SAM-CODE gold)
  - `goldstandard_sad_*-code_*.csv` (SAD-CODE gold)
- Code models:
  - `{project}/model_*/code/codeModel.acm` (`.acm` JSON format)
- Documentation:
  - `{project}/text_*/` → `.txt` file (one sentence per line)

## Naming Conventions

**Files:**
- Analysis scripts: `{analysis_type}_{detail}.py` (e.g., `benchmark_bias_study.py`, `sad_sam_tp_gain_analysis.py`)
- Result CSVs: `{TaskType}Tlr_{project}.csv` (e.g., `sadSamTlr_mediastore.csv`, `samCodeTlr_teastore.csv`)
- Reports: `UPPERCASE_WITH_UNDERSCORES.md` (e.g., `BENCHMARK_BIAS_STUDY.md`, `SAD_SAM_TP_GAIN_STUDY.md`)
- Archived scripts: grouped by technique (llm_*/swattr_*), with version suffixes where applicable

**Directories:**
- Task-specific: `sad-sam/`, `sam-code/`, `sad-code/` (use hyphens)
- Analysis phases: `evaluation/`, `bias/`, `propagation/`, `annotation/` (lowercase, single-purpose)
- Data: `results/`, `reports/`, `archive/` (lowercase, content type)

**Variables & Functions:**
- Set/dict naming: `gs_{task}` (gold), `result_{task}` (predicted), `{entity}_to_{other}` (mappings)
  - Examples: `gs_sad_sam`, `result_sad_code`, `sent_to_models`, `model_to_codes`
- Loader naming: `load_{entity_type}_{variant}` (load_gs_sad_sam, load_result_sad_code)
- Function naming: snake_case (e.g., `calc_metrics`, `normalize_path`, `enroll_gold_standard`)

**CSV Columns:**
- SAD-SAM: `modelElementID`, `sentence`
- SAM-CODE: `ae_id`, `ae_name`, `ce_ids` (or `ce_id` for teammates)
- SAD-CODE: `sentenceID`, `codeID` (or `modelElementID`, `codeId` in TransArc output)
- Note: TransArc output uses `codeId` (lowercase 'd'), differs from input `codeID`

## Where to Add New Code

**New Analysis Script (experiment phase):**
- Create: `src/{phase}/{analysis_name}.py` where phase ∈ {evaluation, bias, propagation, annotation}
- Import infrastructure: `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))`
- Then: `from transarc_error_analysis import BENCHMARK, RESULTS, PROJECTS, load_gs_*, load_result_*, calc_metrics, normalize_path, etc.`
- Output: Write Markdown report to `reports/{REPORT_NAME}.md`
- Example: `src/evaluation/creative_metrics_analysis.py` implements three new metrics, writes `reports/CREATIVE_METRICS.md`

**New Evaluation Metric:**
- Add to `src/lib/transarc_error_analysis.py`:
  - New function: `def compute_{metric_name}(gold, result, ...): ...`
  - Call from analysis scripts that need it
  - Document return value and interpretation
- Example: Line 296-309 shows `calc_metrics(gold, result)` returning 6-tuple (P, R, F1, TP, FP, FN)

**New Baseline Implementation:**
- Add to `src/evaluation/extreme_baseline_analysis.py` (or create new file in src/evaluation/)
- Signature: Function that takes project, code_model, gs_sad_code, returns `set((sentenceID, codePath))`
- Call `calc_metrics(gs_sad_code, result_set)` to compute P/R/F1
- Add to results table in report Markdown
- Example: Lines 66-150 show 7 baselines with metric computation and aggregation

**New Data Import:**
- If new result type: Add loader to `src/lib/transarc_error_analysis.py`
  - Signature: `def load_{entity}_{variant}(project): ... → set() or dict()`
  - Call `normalize_path()` on all file paths
  - Handle optional columns with `.get()` fallback
- Example: Lines 199-232 show loaders for SAD-SAM, SAM-CODE, SAD-CODE results

**Archived Experiments:**
- Move completed/obsolete scripts to `archive/{category}/` (e.g., `archive/llm_*/`, `archive/swattr_*/`)
- Create README in archive subdirectory documenting approach and findings
- Keep main src/ tree clean for active analysis

## Special Directories

**results/ (Generated Output from ARDoCo)**
- Purpose: Store TransArc execution results per project/task
- Generated: By ARDoCo TransArc implementation (external to this codebase)
- Committed: Yes, benchmarks for empirical study
- Accessed by: All loaders in `src/lib/transarc_error_analysis.py` via hardcoded paths

**reports/ (Generated Analysis Documents)**
- Purpose: Store human-readable Markdown reports of empirical findings
- Generated: By scripts in src/ (e.g., `python3 src/lib/transarc_error_analysis.py > reports/TRANSARC_EMPIRICAL_STUDY.md`)
- Committed: Yes, part of research record
- Format: Markdown with tables, sections, code examples, annotated trace examples

**archive/ (Historical Artifacts)**
- Purpose: Keep record of previous approaches and ablations
- Generated: Previous versions of analysis scripts, LLM classification attempts, etc.
- Committed: Yes, for reproducibility and methodology transparency
- Ignored by active pipeline: Scripts here do not affect current src/ analysis

**.planning/codebase/ (Architecture Documentation)**
- Purpose: GSD agent-generated codebase maps for future execution
- Generated: By `/gsd-map-codebase` agent on-demand
- Committed: Yes (may be checked in for reference)
- Format: Markdown; consumed by `/gsd-plan-phase` and `/gsd-execute-phase`

---

*Structure analysis: 2026-05-29*
