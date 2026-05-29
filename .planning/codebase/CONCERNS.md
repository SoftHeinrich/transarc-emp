# Codebase Concerns

**Analysis Date:** 2026-05-29

## Evaluation Validity & Metric Concerns

### File-Level vs Decision-Level Metric Divergence (Critical)

**Issue:** File-level P/R/F1 (standard metric) fundamentally misrepresents system performance due to enrollment inflation and non-uniform weighting.

**Files:** 
- `src/evaluation/evaluation_critique.py`
- `src/evaluation/holistic_metrics_analysis.py`
- `src/bias/enrollment_distortion_analysis.py`

**Impact:** 
- File-level F1 and Decision-level F1 disagree on system rankings in 6/10 pairwise comparisons (e.g., JabRef: File F1=0.943 ranked #1, Decision F1=0.394 ranked #5)
- Component F1 (0.714 avg) differs from File F1 (0.803 avg) by ~0.09 points
- Enrollment inflates 525 raw gold decisions into 18,660 file-level entries (36x factor)
- Block homogeneity is 96-100%: files within directory blocks are NOT independent observations

**Root Cause:** 
- SAD-CODE gold is annotated at mixed granularity (directories + files)
- Expansion of one directory entry to hundreds of files creates massive weighting bias
- Micro-averaged P/R/F1 treats each enrolled link equally, ignoring annotation intent
- Single directory addition can swing F1 by up to 4 percentage points

**Recommendation:**
- Report metrics at multiple levels: file-level, decision-level (50% enrollment rule), and component-level
- For research claims, use decision-level or component-level metrics as primary measurement
- Document metric granularity clearly in all papers/reports
- Avoid claims of "best" system without specifying metric level

---

### Enrollment Block Homogeneity & Statistical Independence (High)

**Issue:** Files expanded from the same directory are highly correlated. Block-level aggregation shows 99.6% of true positives come from directory entries, violating statistical independence.

**Files:** `src/evaluation/evaluation_critique.py` (lines 55-87)

**Impact:**
- Block homogeneity 96-100% across projects means 96-100% of files within a directory block have identical gold status (TP/FP)
- File-level micro-averaging treats correlated outcomes as independent, inflating effective sample size
- Confidence intervals computed via standard P/R/F1 formulas are invalid (width is ~5-10x too narrow)
- Top architecture element accounts for 40-50% of SAD-CODE gold in 4/5 projects

**Evidence:**
- Teammates & BigBlueButton: Interface and Component files have 100% overlap (zero separation possible)
- TeaStore: Interfaces have separate files (0% block homogeneity), causing massive enrollment divergence from Components
- Single top AE (e.g., JabRef "logic") drives 45% of all gold links

**Recommendation:**
- Report confidence intervals at decision/component level, not file level
- For projects with high block homogeneity (Teammates, BigBlueButton), acknowledge evaluation limited to component-level granularity
- Test file-level variance via bootstrap resampling at block level (not individual files)

---

### Enrollment Paradox: Adding Correct Answers Hurts Metrics (High)

**Issue:** File-level F1 DECREASES when correct component-level decisions are "enrolled" (expanded to individual files), creating inverted incentives.

**Files:** `src/bias/enrollment_bias_analysis.py`

**Impact:**
- Teammates: Adding 60 correct Interface assignments (oracle-verified) creates +8,622 new enrolled file-level entries but only ~732 are actually links → net ΔF1 = -0.132
- When component-level precision is fixed, file-level F1 varies inversely with directory size
- Suggests metric is measuring "ability to avoid large directories" rather than "correctness of traceability"

**Example:**
```
Baseline: F1=0.821
+ Add 60 correct Interface assignments via enrollment
= F1=0.689
Result: Metrics DECREASED despite oracle correctness
```

**Recommendation:**
- Never use file-level F1 to evaluate component-level correctness
- For enrollment-heavy projects (TeaStore: 10.1x, Teammates: 36.8x), weight by decision count, not file count
- Include "oracle enrollment" test case in evaluation suite: verify metrics remain stable when oracle correct links are added

---

## Benchmark Leakage Risks

### Hardcoded Project Knowledge in Analysis Scripts (Medium)

**Issue:** Some analysis and development scripts contain hardcoded project-specific mappings or examples that could conflate with benchmark data.

**Files:**
- `src/annotation/reverse_engineer_convention.py` (loads all benchmarks to reverse-engineer rules)
- Archive scripts with LLM examples (e.g., `archive/llm_improved_classifier.py`, `archive/swattr_llm_fewshot.py`)

**Risk:**
- If these mappings or LLM few-shot examples are derived from benchmark analysis, they constitute benchmark leakage
- Reverse engineering the "annotation convention" by examining gold standard distribution is sound research, but results must not be hardcoded into production linkers
- Hardcoded component names, aliases, or example sentences from benchmark projects would invalidate external validity

**Current Safeguards:**
- `src/` scripts are analysis/evaluation only, not used in `ardoco/` pipeline
- Archive scripts explicitly noted as exploratory/archived
- Core message in CLAUDE.md: "Never hardcode word lists derived from benchmark datasets"

**Recommendation:**
- Keep analysis scripts in `src/` and `archive/` strictly separated from pipeline code
- If developing new linkers, use `src/annotation/` outputs (e.g., discovered section structure) only for generic patterns, never hardcoded values
- Document any benchmark-derived knowledge transfer as a research limitation

---

## Reproducibility & Non-Determinism

### LLM Agent Inconsistency (High)

**Issue:** OpenAI API calls have ~15% failure rate (random 0-result responses), requiring retry logic that may not be uniform across scripts.

**Files:**
- `archive/llm_classifications_improved/` (meta-analysis outputs)
- Archive LLM evaluation scripts reference this issue in comments

**Impact:**
- Results computed via LLM vary across runs due to API instability, not algorithmic changes
- 5-run variance study showed means differ (e.g., SWATTR FP filter: mean=38.0, std=0.71, range 37-39)
- Variance studies helpful for stability assessment but complicate replication

**Reproducibility Threat:**
- Exact replication of archived LLM results requires storing API responses (not done)
- Regenerating results requires OpenAI API access and will produce different random samples
- No random seed control for LLM sampling temperature

**Recommendation:**
- Document all LLM-based results as "approximate" or "point estimates"
- For future work: cache all LLM API responses with versioning
- Store random seed, temperature, model version with each LLM experiment
- If claiming improvements via LLM, run at least 5 independent trials and report mean ± std

---

### Random Seed Inconsistency (Medium)

**Issue:** Random sampling scripts use hardcoded `random.seed(42)` but this only controls Python's `random` module, not numpy or other libraries.

**Files:**
- `src/evaluation/stupid_baseline_analysis.py` (line 45)
- `src/evaluation/extreme_baseline_analysis.py` (line 53)

**Impact:**
- If scripts are refactored to use numpy random (e.g., `numpy.random.choice`), results will diverge without code change
- Reported baseline numbers rely on specific random state but no explicit documentation of what's seeded

**Recommendation:**
- Use `numpy.random.seed(42)` in addition to `random.seed(42)` if numpy is imported
- Add comment documenting which RNG modules are seeded in each script
- If refactoring, update seed setup code and re-verify baselines match previous runs

---

## Code Organization & Maintenance

### Large Monolithic Scripts (Medium)

**Issue:** Several analysis scripts exceed 1,200 lines with minimal function decomposition, making testing and reuse difficult.

**Files:**
- `src/lib/transarc_error_analysis.py` (1,186 lines)
- `src/lib/new_metrics_analysis.py` (1,183 lines)
- `src/evaluation/evaluation_critique.py` (1,325 lines)

**Impact:**
- Functions like `analysis_a()`, `analysis_b()`, `analysis_c()` in `transarc_error_analysis.py` perform multiple distinct analyses with mixed output formats
- Difficult to unit test individual analysis components
- Code reuse limited (copy-paste of similar metric computations across scripts)
- Changes to shared logic ripple across all scripts

**Example (lines 316-548):** Five separate analysis functions, each with its own data loading, filtering, and reporting logic.

**Recommendation:**
- Extract shared metric computation into dedicated module: `src/lib/metrics.py`
- Create abstract `Analysis` base class with consistent reporting interface
- Add unit tests for core metrics (Gini, F1, enrollment logic) in `src/tests/`
- Refactor `transarc_error_analysis.py` as composition of smaller analysis functions

---

### Scattered Metric Implementations (Medium)

**Issue:** P/R/F1 calculation and variant metrics (Gini, percentile, holistic scores) are reimplemented across files rather than centralized.

**Files:**
- `src/lib/transarc_error_analysis.py` (lines 296-315: `calc_metrics()`)
- `src/evaluation/holistic_metrics_analysis.py` (lines 36-40: `f1()`)
- `src/evaluation/stupid_baseline_analysis.py` (lines 52-71: `gini_coefficient()`, `percentile()`)
- `src/evaluation/creative_metrics_analysis.py` (lines 58-79: similar implementations)
- `src/bias/benchmark_bias_study.py` (lines 67-122: `gini_coefficient()`, `shannon_entropy()`)

**Impact:**
- Metric definition inconsistencies across files (e.g., Gini coefficient formula varies slightly)
- Bug fixes only applied to one implementation, others remain outdated
- Hard to verify metric correctness when implementations are scattered
- Floating-point precision differences between files

**Recommendation:**
- Create `src/lib/metrics.py` with centralized implementations of all metrics
- Functions to include: `calc_metrics()`, `gini_coefficient()`, `shannon_entropy()`, `percentile()`, `f1()`
- Add docstring with formula and edge-case handling
- Import consistently: `from src.lib.metrics import calc_metrics, gini_coefficient, ...`
- Add unit tests for each metric against known values

---

## Data Loading & Path Handling

### Hardcoded Absolute Paths (Medium)

**Issue:** All scripts use hardcoded absolute paths to benchmark, results, and output directories. Projects cannot be moved or run from different environments without editing scripts.

**Files:**
- `src/lib/transarc_error_analysis.py` (lines 20-68)
- `src/evaluation/evaluation_critique.py` (line 35)
- `src/bias/benchmark_bias_study.py` (line 33)
- Nearly all scripts in `src/`

**Examples:**
```python
BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/STUPID_BASELINES.md")
```

**Impact:**
- Scripts fail immediately if project is moved or mounted at different path
- Running in different environment (e.g., Docker container, different machine) requires editing multiple files
- CI/CD pipelines would need to hard-code paths or set environment variables

**Recommendation:**
- Create `src/lib/config.py` with configurable paths:
  ```python
  from pathlib import Path
  import os
  
  PROJECT_ROOT = Path(os.getenv("TRANSARC_EMP_ROOT", "/mnt/hostshare/ardoco-home/transarc-emp"))
  ARDOCO_ROOT = Path(os.getenv("ARDOCO_ROOT", "/mnt/hostshare/ardoco-home/ardoco"))
  
  BENCHMARK = ARDOCO_ROOT / "core/tests-base/src/main/resources/benchmark"
  RESULTS = PROJECT_ROOT / "results"
  ```
- Update all scripts to import from `config.py` instead of defining paths locally
- Document environment variables in README

---

### Path Normalization Edge Cases (Low)

**Issue:** Path normalization (removing `Implementation/` prefix) is inconsistent across loaders.

**Files:**
- `src/lib/transarc_error_analysis.py` (lines 97-101: `normalize_path()`)
- Used in multiple loaders: `load_gs_sad_code_raw()`, `load_gs_sam_code_raw()`, `enroll_gold_standard()`

**Risk:**
- If gold standard format changes (e.g., prefix becomes `Model/` instead), all loaders break silently
- No validation that prefix was actually present before stripping
- Could silently discard important path information in future datasets

**Example:**
```python
def normalize_path(path):
    if path.startswith("Implementation/"):
        path = path[len("Implementation/"):]
    return path
```

**Recommendation:**
- Add validation flag: `assert path.startswith("Implementation/"), f"Unexpected path format: {path}"`
- If legitimate paths don't have prefix, split into separate functions: `normalize_gold_path()` vs `normalize_result_path()`
- Add unit test for both prefixed and non-prefixed inputs

---

## Analysis Gaps & Incomplete Coverage

### Precision-Centric Evaluation Missing (Medium)

**Issue:** Most analysis focuses on recall and F1. Component-level precision breakdown is sparse, particularly for false positive root causes.

**Files:**
- `src/lib/transarc_error_analysis.py` (lines 357-418: `FPClassification` dataclass and `analysis_b()`)
- `archive/llm_precision_classifier.py` (abandoned precision improvement approach)

**Gap:**
- FP classification exists but is secondary to FN analysis
- No per-model-element precision breakdown (only aggregate FP counts)
- No analysis of "precision drift" — which components have unexpectedly high FP rates?

**Impact:**
- For component improvement, hard to prioritize: is precision loss driven by 1 problematic component or distributed?
- Recommender prioritization uses TP/FP ratios but not per-component precision bias

**Recommendation:**
- Add `per_component_precision_breakdown()` function in `metrics.py`
- For each model element, compute TP / (TP + FP) and rank by precision deficit
- Include in main empirical study report
- Correlate component precision with documentation word count or ambiguity metrics

---

### Test Coverage Gaps (Low)

**Issue:** No unit test infrastructure exists for metric implementations or data loading functions.

**Files:** No `tests/` directory in `src/`

**Risk:**
- Metric implementations (Gini, F1, enrollment) are untested
- Data loading functions (`load_gs_sad_sam()`, `enroll_gold_standard()`) have no regression tests
- Refactoring metrics is high-risk without automated verification

**Recommendation:**
- Create `src/tests/` with `pytest` configuration
- Add test fixtures for small mock datasets (2-3 projects with simplified gold standards)
- Test cases:
  - `test_calc_metrics()` — verify P/R/F1 against hand-calculated values
  - `test_enroll_gold_standard()` — test directory expansion with mocked .acm files
  - `test_normalize_path()` — test edge cases (missing prefix, empty string, nested paths)
  - `test_gini_coefficient()` — test against known inequal distributions (e.g., [1,1,1,7] should give ~0.5)

---

## Documentation & Clarity

### Evaluation Critique Findings Not Centralized (Medium)

**Issue:** Fundamental findings about metric validity (enrollment inflation, block homogeneity, metric divergence) are scattered across separate reports with no synthesis.

**Files:**
- `src/evaluation/evaluation_critique.py` → `reports/EVALUATION_CRITIQUE.md`
- `src/bias/enrollment_distortion_analysis.py` → `reports/ENROLLMENT_DISTORTION_ANALYSIS.md`
- `src/bias/benchmark_bias_study.py` → `reports/BENCHMARK_BIAS_STUDY.md`
- Key findings in memory notes, not in source code comments

**Impact:**
- Readers of individual reports may not understand full scope of metric invalidity
- Scripts don't reference each other, making it hard to understand dependency chain
- Future researchers may rediscover same issues

**Recommendation:**
- Add docstring summary to `src/evaluation/evaluation_critique.py`:
  ```python
  """
  THIS SCRIPT IDENTIFIES FUNDAMENTAL METRIC VALIDITY ISSUES.
  
  Key findings:
  - File-level P/R/F1 disagrees with decision-level P/R/F1 in 60% of pairwise rankings
  - Enrollment inflation (36x for Teammates) creates non-independent observations
  - Adding correct links can DECREASE file-level F1 (enrollment paradox)
  
  Related: benchmark_bias_study.py (distributional properties)
  
  See EVALUATION_CRITIQUE.md for full analysis.
  """
  ```
- Create `reports/METRIC_VALIDITY_SUMMARY.md` synthesizing all three reports
- Link from main project README

---

### Archive Directory Lacks Clear Retention Policy (Low)

**Issue:** `archive/` contains 30+ exploratory scripts and reports with no retention policy or curation notes.

**Files:** `archive/` (multiple scripts, some with duplicative functionality)

**Impact:**
- Unclear which results are stable vs experimental
- Replication scripts (e.g., `four_system_comparison.py`) are archived but may be relevant for future work
- Disk space used by old LLM cache (`llm_cache_swattr/` 2.3GB)

**Examples of potential duplicates:**
- `llm_baseline_eval.py` (17KB), `llm_agentic_eval.py` (17KB), `llm_improved_baseline.py` (17KB)
- `swattr_variance_test.py`, `swattr_extended_variance.py`, `swattr_quick_variance.py`

**Recommendation:**
- Create `ARCHIVE_MANIFEST.md` documenting:
  - Script purpose and date written
  - Whether results are published, exploratory, or superseded
  - Successor if replaced by newer analysis
  - Key findings worth preserving
- Move clearly superseded scripts to `archive/superseded/` with brief note
- Delete LLM cache directories if not needed for replication
- Example entry:
  ```markdown
  ### llm_baseline_eval.py (Feb 7, 2026)
  - **Status**: Exploreded, superseded by llm_agentic_eval.py (multi-agent version)
  - **Key finding**: Adaptive LLM baseline (0.829 F1) beats TransArc (0.803)
  - **Result location**: archive/LLM_BASELINE.md
  ```

---

## Transitive Composition Concerns

### Intermediate Output Format Inconsistency (Medium)

**Issue:** SAD-SAM and SAM-CODE intermediate outputs use different key naming and formats, creating composition complexity.

**Files:**
- `src/lib/transarc_error_analysis.py` (lines 235-285: loader functions)
- `src/propagation/sam_code_cascade_analysis.py` (lines 56-92: composition logic)

**Specific Issues:**
- SAD-SAM intermediate: `(modelElementID, sentence)` — sentence is full text string
- SAM-CODE intermediate: `(ae_id, codeID)` — matches SAD-SAM's model element IDs
- But `sentence` vs `ae_id` naming is inconsistent with TransArc result: `(modelElementID=sentence_number, codeId)`

**Composition Challenge:**
- To compose SAD-SAM × SAM-CODE, need to match model elements (works)
- But intermediate is raw sentences, not sentence IDs, forcing string-based matching
- TransArc result switches to sentence IDs, requiring re-lookup

**Impact:**
- Composition code is error-prone (string matching instead of ID matching)
- Hard to trace which intermediate links produced which output links
- Intermediate format differs from final output format unnecessarily

**Recommendation:**
- Standardize intermediate outputs to use sentence IDs (integers) not strings
- Modify SAD-SAM loader: output `(model_id, sentence_id, sentence_text)` triples
- Update composition: match on `(model_id, sentence_id)` pairs, carry sentence_text for debugging only
- Add round-trip test: verify that intermediate SAD-SAM×SAM-CODE composed equals actual TransArc output

---

## Summary Table: Issue Priority

| Issue | Severity | Scope | Recommended Action |
|-------|----------|-------|-------------------|
| File-level vs decision-level metric divergence | Critical | Evaluation | Report metrics at multiple levels; revise paper claims |
| Enrollment block homogeneity | High | Evaluation | Test at decision/component level; adjust confidence intervals |
| Enrollment paradox (correct links hurt F1) | High | Evaluation | Acknowledge metric invalidity; weight by decision count |
| LLM agent non-determinism | High | Reproducibility | Document as approximate; cache LLM responses in future |
| Hardcoded absolute paths | Medium | Maintenance | Refactor to config.py with environment variables |
| Large monolithic scripts (1000+ lines) | Medium | Maintenance | Extract shared logic; add unit tests |
| Scattered metric implementations | Medium | Maintenance | Centralize in metrics.py; add docstrings |
| Evaluation critique findings scattered | Medium | Documentation | Create synthesis report; add cross-references |
| Precision analysis underdeveloped | Medium | Analysis | Add per-component precision breakdown |
| Path normalization edge cases | Low | Robustness | Add validation and unit tests |
| Random seed inconsistency | Low | Reproducibility | Use numpy.seed() in addition to random.seed() |
| Test coverage gaps | Low | Testing | Add pytest suite for metrics and loaders |
| Archive curation lacking | Low | Maintenance | Create ARCHIVE_MANIFEST.md; delete stale caches |
| Intermediate format inconsistency | Medium | Code Quality | Standardize to sentence IDs; add composition test |

---

*Concerns audit: 2026-05-29*
