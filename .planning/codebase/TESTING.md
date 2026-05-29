# Testing Patterns

**Analysis Date:** 2026-05-29

## Test Framework & Validation Approach

**Philosophy:**
This is an empirical evaluation research codebase with no traditional unit test framework (pytest, unittest). Instead, validation happens through:
1. **Baseline metric verification** - Results checked against expected thresholds from Java test files
2. **Variance testing** - Stochastic LLM outputs sampled multiple times to measure stability
3. **Leakage testing** - Checking whether solutions overgeneralize or fit benchmark specifics
4. **Artifact comparison** - Cross-validating intermediate outputs through the transitive pipeline
5. **Consistency assertions** - Runtime checks that computed metrics sum correctly

## Baseline Metric Verification

**Location:** `src/lib/transarc_error_analysis.py` (lines 70-93, 662-677)

**Expected thresholds:** Hard-coded from Java test files (minimum performance targets):

```python
EXPECTED = {
    "sad-sam": {
        "mediastore": (0.940, 0.548, 0.69),   # (precision, recall, f1)
        "teastore": (0.999, 0.74, 0.85),
        "teammates": (0.60, 0.859, 0.709),
        "bigbluebutton": (0.897, 0.709, 0.79),
        "jabref": (0.899, 0.999, 0.946),
    },
    "sam-code": {...},
    "sad-code": {...},
}
```

**Run Command:**
```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 src/lib/transarc_error_analysis.py
```

**Validation Logic:**
```python
# Baseline Verification (lines 662-677)
all_pass = True
for task in ["sad-sam", "sam-code", "sad-code"]:
    for proj in PROJECTS:
        p, r, f1, tp, fp, fn, gs, rs = baseline[(task, proj)]
        ep, er, ef1 = EXPECTED[task][proj]
        if p < ep - 0.01 or r < er - 0.01 or f1 < ef1 - 0.01:
            out(f"- WARNING: {task}/{proj}: P={p:.3f} (exp>={ep:.3f}), ...")
            all_pass = False
        # Verify consistency: TP + FP = |result|, TP + FN = |gold|
        assert tp + fp == rs, f"{task}/{proj}: TP+FP={tp+fp} != result={rs}"
        assert tp + fn == gs, f"{task}/{proj}: TP+FN={tp+fn} != gold={gs}"

if all_pass:
    out("All 15 runs meet or exceed expected thresholds.")
```

**Test Plan:**
- [x] All 15 task×project combinations produce metrics >= expected values
- [x] TP + FP = result set size (no counting errors)
- [x] TP + FN = gold standard size (gold standard consistency)
- [x] FP/FN/TP categories sum to reported totals across all analyses

## Variance Testing

**Purpose:** Measure stochastic variability in LLM-based filter reasoning (SWATTR).

**Location:** `archive/swattr_variance_test.py` (legacy validation script)

**Test Design:**
- Run the same LLM prompt 5 independent times with different cache keys
- Measure how many FPs are caught (killed) and TPs are accidentally killed
- Track per-project consistency across runs

**Run Command:**
```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 archive/swattr_variance_test.py
```

**Output Structure:**
```
Data: <n_tp> TPs + <n_fp> FPs = <total> links
Running 5 independent trials...

=== Run 1/5 ===
  mediastore: <count> links... <fp_caught> NO_LINK
  ...

Run  FPs caught    TPs killed   Net
1    <fp>/<total>  <tp>/<total>  +<net>
2    <fp>/<total>  <tp>/<total>  +<net>
...
Mean <avg_fp>     <avg_tp>      +<avg_net>
Std  <std_fp>     <std_tp>      <std_net>
```

**Pass Criteria:**
- Mean FP catch rate is stable (std deviation < 1-2 FPs across 5 runs)
- TP kill rate is minimal (mean < 1 per 5 runs, ideally 0)
- Per-project consistency maintained across runs (same items failed/passed)

**Example Results (from memory):**
- v23 generic reasoning guide: mean 38.0 FPs caught (std=0.71), 0.2 TPs killed (std=0.45)
- Shows robust filtering without recall degradation

## Leakage Testing

**Purpose:** Detect if analysis uses benchmark-specific knowledge that would invalidate generalization.

**Location:** `archive/swattr_fn_leakage_test.py`

**Test Design:**
- Apply LLM reasoning guide to gold standard False Negatives (SWATTR misses)
- If guide classifies FNs as "NO_LINK", it's too aggressive and would hurt recall
- Also test on ALL gold standard links to show complete picture

**Run Command:**
```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 archive/swattr_fn_leakage_test.py
```

**Validation Logic:**
```python
# Load gold standard + SWATTR results
gold = load_gs_sad_sam(proj)
result = load_result_sad_sam(proj)  # SWATTR output

# Separate into TPs, FPs, FNs
tp_set = gold & result       # Correctly found
fp_set = result - gold        # Wrongly added
fn_set = gold - result        # Wrongly missed

# Apply reasoning guide to FNs
for (model_id, sent_num) in fn_set:
    # If guide votes "NO_LINK", that's a false negative leak
    # (correct link rejected)
```

**Pass Criteria:**
- FN kill rate = 0 (or near-zero: no correct links rejected)
- No bias against any specific project or component type
- Shows analysis is generalizable, not overfitting to benchmark labels

## Pipeline Consistency Checks

**Purpose:** Verify that intermediate transitive compositions are mathematically consistent.

**Location:** `src/lib/transarc_error_analysis.py` (lines 315-342, 592-597)

**Analysis F: What-If Component Comparison** (lines 550-597)

Computes three scenarios to validate pipeline:

1. **Perfect SAD-SAM + Actual SAM-CODE:**
   - Use gold standard SAD-SAM links
   - Compose with actual intermediate SAM-CODE results
   - Expect better F1 than actual TransArc output

2. **Actual SAD-SAM + Perfect SAM-CODE:**
   - Use actual intermediate SAD-SAM results
   - Compose with gold SAM-CODE links
   - Expect better F1 than actual TransArc output

3. **Internal vs Standalone SAM-CODE:**
   - Compare TransArc-internal SAM-CODE intermediates
   - vs standalone ARCOTL SAM-CODE execution
   - Should show minimal delta (verifies composition consistency)

**Implementation:**
```python
# Perfect SAD-SAM scenario
perfect_sad_sam_result = set()
for sent, models in gs_sad_sam_s2m.items():
    for m in models:
        codes = model_to_codes_int.get(m, set())  # From intermediates
        for c in codes:
            perfect_sad_sam_result.add((sent, c))

p1, r1, f1_1, tp1, fp1, fn1 = calc_metrics(gs_sad_code_enrolled, perfect_sad_sam_result)
# Verify: F1_1 >= actual_f1 (oracle shows upper bound)
```

**Pass Criteria:**
- Perfect SAD-SAM F1 > actual F1 (improving component gives gains)
- Perfect SAM-CODE F1 > actual F1 (validates both components matter)
- Internal SAM-CODE ≈ Standalone SAM-CODE (within 1-3% delta)
- Delta magnitudes show which component limits performance

## Error Decomposition Consistency

**Location:** `src/lib/transarc_error_analysis.py` (lines 316-412, 426-488)

**Analysis B: FP Classification** (lines 349-411)

Ensures all false positives are classified into exactly one category:

```python
@dataclass
class FPClassification:
    sad_sam_caused: list       # SAD-SAM wrong, SAM-CODE correct
    sam_code_caused: list      # SAD-SAM correct, SAM-CODE wrong
    both_caused: list          # Both components wrong
    combination_error: list    # Both correct but combination invalid

# Verify coverage
n_ss = len(cls.sad_sam_caused)
n_sc = len(cls.sam_code_caused)
n_both = len(cls.both_caused)
n_comb = len(cls.combination_error)
total = n_ss + n_sc + n_both + n_comb
assert total == total_fp, f"{proj}: categories sum={total} != total_fp={total_fp}"
```

**Analysis C: FN Classification** (lines 418-488)

Similarly exhaustive classification of false negatives:

```python
@dataclass
class FNClassification:
    theoretical_limit: list     # No transitive path in gold
    sad_sam_miss: list          # TransArc missed SAD-SAM
    sam_code_miss: list         # Correct model, SAM-CODE missed code
    both_miss: list             # Both components contributed

assert total == total_fn, f"{proj}: categories sum={total} != total_fn={total_fn}"
```

**Pass Criteria:**
- Every FP classified into exactly one category (sum = total FP count)
- Every FN classified into exactly one category (sum = total FN count)
- No overlaps or uncounted items
- Categories report in run output match markdown tables

## Cross-Project Comparison Testing

**Location:** `src/evaluation/evaluation_critique.py`, `src/bias/benchmark_bias_study.py`

**Test Design:**
- Load results from 5 projects: mediastore, teastore, teammates, bigbluebutton, jabref
- Compute metrics at multiple granularities (decision-level, file-level, component-level)
- Verify ranking consistency across metrics (e.g., JabRef should not rank differently)
- Detect distributional biases that inflate/deflate apparent performance

**Run Command:**
```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 src/evaluation/evaluation_critique.py
```

**Output:** Comprehensive markdown report with tables comparing:
- File-level P/R/F1 vs Decision-level P/R/F1 (reveals enrollment inflation)
- Per-project ranking by different metrics
- Long-tail concentration (Gini coefficient, entropy, top-3 concentration)

**Pass Criteria:**
- File-level and decision-level metrics show different rankings (JabRef case study)
- Gini coefficients reveal high inequality in link distribution
- Enrollment expansion documented with actual counts
- No anomalous outliers (single project with drastically different properties)

## Test Data Integrity Checks

**Pattern:** All data loading functions validate paths and structure:

**Location:** `src/lib/transarc_error_analysis.py` (lines 104-195)

```python
def load_code_model_files(project):
    """Load all file paths from the .acm code model."""
    acm_file = ACM_FILES[project]  # Constant dict at module top
    files = set()
    with open(acm_file) as f:
        data = json.load(f)
    repo = data.get("codeItemRepository", {}).get("repository", {})
    for item in repo.values():
        if item.get("type") == "CodeCompilationUnit":
            # Extract and validate structure
            path_elements = item.get("pathElements", [])
            name = item.get("name", "")
            ext = item.get("extension", "")
            if path_elements and name:
                full_path = "/".join(path_elements) + "/" + name
                if ext:
                    full_path += "." + ext
                files.add(normalize_path(full_path))
    return files
```

**Validation:**
- File existence checked before reading (`.exists()`)
- CSV column names validated via `DictReader`
- Path normalization applied consistently (`normalize_path()`)
- JSON structure validated with `.get()` with defaults
- Empty collections returned gracefully on missing files

## Test Coverage Gaps & Known Limitations

**Not tested:**
- Unit-level function tests (pure Python functions assumed correct if outputs match)
- LLM response parsing edge cases (handled with broad except clauses)
- Filesystem I/O errors beyond file-not-found
- Memory/performance on larger datasets
- Parallelization/concurrency (all scripts run sequentially)

**Manual validation needed:**
- New dataset added to benchmark: verify enrollment expansion matches new code model
- SWATTR algorithm changes: re-baseline with Java tests
- LLM model changes: re-run variance tests, leakage tests

---

*Testing analysis: 2026-05-29*
