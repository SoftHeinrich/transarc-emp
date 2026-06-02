---
quick_id: 260602-q6u
status: complete
date: 2026-06-02
---

# Metrics Correctness Audit — Summary

## Verdict: ISSUES FOUND

Ten distinct issues were found ranging from dead code (INFO) through API inconsistencies (WARNING) to one correctness concern (WARNING) that could produce misleading NDG values. No issues were found that produce outright incorrect final metric values when the code is run in its primary entry point (`new_metrics_analysis.py`). The `metrics_api.py` secondary entry point has two divergences from the reference implementation that make NDG and MCC values differ from the `new_metrics_analysis.py` numbers.

---

## Findings

### [INFO] Dead variable `comp_sent_count` in `compute_random_f1`
**File:** `src/lib/new_metrics_analysis.py:349`
**Issue:** `comp_sent_count = defaultdict(set)` is assigned but never read. Likewise `gold_by_sent` on line 350 is populated (lines 351-352) but its values are never subsequently used — `comp_sents` (line 361) is the variable actually used for per-component sentence counting.
**Impact:** No correctness impact. Minor code clarity issue — the variables left over from an earlier design suggest the code was partially refactored.

---

### [INFO] Dead parameter `n_components` in `compute_random_f1`
**File:** `src/lib/new_metrics_analysis.py:342`
**Issue:** The function signature is `compute_random_f1(gold_sad_code, n_sentences, n_components, gold_sam_code_map)`. The parameter `n_components` is accepted but never referenced inside the function body. The actual loop iterates over `gold_sam_code_map.items()`, which implicitly covers all components.
**Impact:** No correctness impact. All callers pass a value (`n_comps` or `n_components`) that is silently ignored. The parameter creates a misleading API surface.

---

### [WARNING] `n_sentences` inconsistency between `new_metrics_analysis.py` and `metrics_api.py` — NDG values will differ
**File:** `src/lib/new_metrics_analysis.py:785` vs `src/lib/metrics_api.py:235`
**Issue:** `compute_random_f1` divides by `n_sentences` to estimate the per-component prediction probability `p`. In `new_metrics_analysis.py`, this is `len(all_sents)` derived from `load_text(proj)` — the total number of sentences in the documentation file (e.g., 59 for mediastore). In `metrics_api.py`, it is `len({s for (s, _c) in enrolled})` — the number of distinct sentences that appear in the enrolled gold standard (a strictly smaller number, e.g., ~14 for mediastore based on known gold sizes).

Using the smaller denominator makes `p` larger than it should be, inflating the expected TP/FP counts, and thereby inflating `random_f1`. A higher `random_f1` lowers NDG for systems performing above that baseline. The magnitude of the discrepancy depends on the project: for mediastore (59 total vs ~14 linked), `p` is ~4x too large.

**Impact:** NDG values produced by `metrics_api.py` are numerically different from those produced by `new_metrics_analysis.py` for the same project. Neither is necessarily "wrong" as a design choice (the enrolled-sentences denominator could be argued as the evaluation domain), but the inconsistency means the two outputs are not directly comparable and the discrepancy is undocumented.

---

### [WARNING] MCC `all_files` universe in `metrics_api.py` excludes result-only files, risking negative `tn`
**File:** `src/lib/metrics_api.py:248`
**Issue:**
```python
all_files = set().union(*gs_sam_code_map.values()) if gs_sam_code_map else set()
row["mcc"] = compute_mcc(enrolled, res, all_sents, all_files)["mcc"]
```
`all_files` is built from gold SAM-CODE map values only. If `res` (the system result) contains file paths not in `all_files`, those links are counted as `fp` in `compute_mcc` but are not in the universe, so `tn = universe_size - tp - fp - fn` can go negative. A negative `tn` corrupts the MCC formula.

By contrast, `new_metrics_analysis.py` (lines 688-695) explicitly augments `all_code_files` with result paths:
```python
for _, f in transarc_sad_code:
    all_code_files.add(f)
for _, f in v45_sad_code:
    all_code_files.add(f)
```

**Impact:** For the standard TransArc result (where all result files are already in the gold SAM-CODE map), this is not a problem in practice. However, when `compute_sad_code_metrics` is called with an arbitrary external result set (e.g., an LLM linker output) that includes files outside the gold SAM-CODE map, `tn` can go negative, producing a corrupt MCC value. This is a latent correctness bug for non-TransArc callers.

---

### [WARNING] `sentence_f1` in `metrics_api.py` undercounts false positives at sentence level
**File:** `src/lib/metrics_api.py:146-152`
**Issue:**
```python
pred_correct_sentences = {
    s for s in res_by_s
    if gold_by_s.get(s) and (gold_by_s[s] & res_by_s[s])
}
gold_S = {(s, "*") for s in gold_by_s}
res_S = {(s, "*") for s in res_by_s if s in pred_correct_sentences}
```
`res_S` includes only sentences that have at least one TP component. A sentence predicted by the system but not in the gold at all (`res_by_s[s]` populated, but `gold_by_s.get(s)` is falsy) is excluded from `res_S`. It is also not in `gold_S`. So it produces no FP in `calc_metrics(gold_S, res_S)`.

Concretely: if the system predicts components for sentence 42 but sentence 42 has no gold links at all, this sentence contributes zero to FP (and zero to precision denominator). The metric effectively ignores pure-FP sentences entirely.

**Impact:** `sentence_f1` precision is overstated for systems that hallucinate links for gold-negative sentences. This is a design-level question — the docstring says "a sentence is a TP iff its gold and predicted component sets share ≥1 component", which could justify excluding gold-negative sentences. But it is not documented that gold-negative predicted sentences are also excluded from the FP count, and this differs from standard retrieval precision.

---

### [INFO] MAP with uniform confidence is not equivalent to recall (but close)
**File:** `src/lib/new_metrics_analysis.py:258-260`, comment at line 973
**Issue:** The code comment says "TransArc's uniform confidence means MAP ≈ recall." This is approximately true but not exact. With uniform confidence (all 0.5), Python's `sort(reverse=True)` is stable — ties are resolved by insertion order into the list, which comes from set iteration order. Set iteration order in CPython is implementation-defined (though deterministic within a run). For a sentence with K gold components and M total predicted components, AP depends on where the K gold components land in the arbitrary tie-breaking order.

In the best case (all gold comps first), AP = 1.0. In the worst case (all gold comps last), AP < 1.0. The average AP with random tie-breaking converges to something slightly different from recall for multi-component sentences.

**Impact:** Low. For single-component sentences (the common case in SAD-SAM), MAP = recall exactly when the component is present. The approximation comment is essentially correct in practice, but the claim that MAP is recall is technically inaccurate.

---

### [INFO] `compute_ndg` can return negative values; docs claim [0,1]
**File:** `src/lib/new_metrics_analysis.py:401-406`
**Issue:**
```python
def compute_ndg(system_f1, random_f1, oracle_f1):
    denom = oracle_f1 - random_f1
    if denom <= 0:
        return 1.0 if system_f1 >= oracle_f1 else 0.0
    return (system_f1 - random_f1) / denom
```
If `system_f1 < random_f1` (system is worse than random), the return value is negative. The metric definition section in the script (line 585) states range [0, 1]. No clamping is applied.

**Impact:** If a system underperforms the random baseline, the reported NDG will be negative. Whether this is a bug or intentional feature depends on interpretation. A value of NDG = −0.2 is meaningful (worse than random), but it violates the stated [0, 1] range. Users reading the "Range: [0, 1]" documentation will be surprised by negative values. The clamping in the `denom <= 0` special case handles oracle ≤ random but not the case where `system < random`.

---

### [WARNING] ACF1 multi-component files get minimum weight (largest component)
**File:** `src/lib/new_metrics_analysis.py:293-295`
**Issue:**
```python
w = 1.0 / n if n > 0 else 1.0
if f not in file_to_weight or w < file_to_weight[f]:
    file_to_weight[f] = w
```
When a file belongs to multiple components of different sizes, the code assigns the minimum weight (`1/max_N`), i.e., the weight corresponding to the largest component. The comment says "use minimum weight". This means a file shared between a small component (1 file) and a large component (972 files) gets weight 1/972 instead of 1/1.

**Impact:** Whether this is correct depends on the intended semantics. If the goal is "each component-level decision contributes equally", then for a file in two components of sizes N1 and N2, a correct prediction is simultaneously a correct prediction for both components. Assigning weight 1/max(N1,N2) under-weights the small-component contribution. Assigning weight 1/min(N1,N2) over-weights the large-component contribution. Neither is clearly correct for multi-membership files; this is a design ambiguity. The choice of minimum weight (largest denominator) appears deliberately conservative, but it is not documented as a deliberate design decision.

**Note:** In practice, the ARDoCo SAM-CODE gold standard rarely has files belonging to multiple components (the exception is Teammates/BBB where Interface and Component share files). The real-world impact is limited to those two projects.

---

### [INFO] `_compute_decision_f1` FP approximation: FPs counted per directory, not per file
**File:** `src/bias/evaluation_critique.py:613-621`
**Issue:** Decision-level FP counting groups FP files into (sentence, parent_directory) buckets, so all FP files in the same directory for a sentence count as one FP. This is the intended approximation (FPs at directory level = one wrong decision), but the approximation breaks down when a system produces FPs in multiple distinct directories (each counts separately) versus producing FPs that span files in the same directory (count as one). The asymmetry with TP counting (where a raw entry needs ≥50% file coverage) creates a precision metric that is not cleanly dual to the recall metric.
**Impact:** Low. The metric is clearly documented as an approximation. It does not produce outright incorrect results; it is a design choice with known limitations.

---

### [INFO] `build_avg_row` correctly handles all-NA columns
**File:** `src/lib/metrics_api.py:261-266`
**Issue (non-issue, confirmed correct):** When all rows have `NA` for a column, `vals = []` and `avg[col] = NA` (since `len(vals) == 0` triggers the `else NA` branch). This is correct behavior.
**Impact:** None. This specific concern from the audit checklist is implemented correctly.

---

### [INFO] `component_f1` ID-to-name fallback could theoretically cause collisions
**File:** `src/lib/metrics_api.py:155-156`
**Issue:**
```python
gold_C = {(names.get(c, c), s) for (c, s) in gold}
res_C = {(names.get(c, c), s) for (c, s) in res}
```
If a component ID has no entry in `names` (the SAM-CODE gold `ae_name` column), the raw ID is used as the name. Two different IDs without name entries would not collide (they use their distinct IDs). Two different IDs that map to the same name would collapse to a single component, which is intentional (the docstring says "so synonymous ids collapse").
**Impact:** None in practice. The SAM-CODE gold standard contains `ae_name` for all entries in the benchmark projects.

---

## Per-Metric Verdict

| Metric | Implementation file | Verdict |
|--------|---------------------|---------|
| MCC (SAD-SAM) | `compute_mcc` in `new_metrics_analysis.py` | CORRECT |
| MCC (SAD-CODE) in `new_metrics_analysis.py` | includes result-only files in universe | CORRECT |
| MCC (SAD-CODE) in `metrics_api.py` | excludes result-only files from universe | WARNING (latent bug for external result sets) |
| EMR | `compute_emr` | CORRECT |
| MAP | `compute_map` | CORRECT (formula) |
| MAP uniform baseline | `transarc_sad_sam_as_ranked` | INFO (comment slightly overstates equivalence to recall) |
| ACF1 | `compute_acf1` | WARNING (multi-membership weight policy undocumented; conservative choice) |
| NDG | `compute_ndg` | INFO (can return negative; contradicts stated [0,1] range) |
| NDG `random_f1` baseline | `compute_random_f1` | WARNING (`n_sentences` meaning differs between callers) |
| HUS | `compute_hus` | CORRECT |
| HUS call sites | `metrics_api.py` | CORRECT (SAD-SAM flips, SAD-CODE passes directly) |
| Sentence F1 | `metrics_api.py:compute_sad_sam_metrics` | WARNING (gold-negative predicted sentences excluded from FP count) |
| Component F1 | `metrics_api.py:compute_sad_sam_metrics` | CORRECT |
| Decision F1 | `_compute_decision_f1` | CORRECT (approximation by design) |
| Weighted F1 | `_compute_weighted_f1` | CORRECT |
| `build_avg_row` | `metrics_api.py` | CORRECT |
| `calc_metrics` | `transarc_error_analysis.py` | CORRECT |

---

## Code Quality

### Dead code in `compute_random_f1`
Two variables are allocated and populated but never consumed: `comp_sent_count` (line 349) and `gold_by_sent` (lines 350-352). The loop that builds `gold_by_sent` iterates over `gold_sad_code` identically to the loop that builds `comp_sents` (lines 361-365), making it redundant. These should be removed to avoid confusion.

### `n_components` parameter misleads callers
The parameter is in the function signature with a descriptive name, suggesting it influences the result. It does not. The function's docstring does not mention that this parameter is unused.

### `compute_random_f1` floating-point non-determinism
The inner loop `sum(1 for s, c in gold_sad_code if c in files)` iterates over a set (`gold_sad_code`). Python sets have deterministic iteration order within a single run but not across runs in older Python versions (< 3.7). In Python 3.7+, dicts are ordered, but sets are not guaranteed stable across process restarts. The final result is a float sum over a fixed set of components, which is stable within a single run. Cross-run determinism is practically fine for this analysis, but technically not guaranteed if `gold_sad_code` contains elements with hash randomization.

### `enroll_gold_standard` vs `enroll_with_provenance` dual implementations
`transarc_error_analysis.py` has `enroll_gold_standard` (simple set expansion) and `evaluation_critique.py` has `enroll_with_provenance` (provenance tracking). These should produce identical enrolled sets. `metrics_api.py` calls `enroll_with_provenance` for SAD-CODE (for provenance-based decision/weighted F1) but uses `enroll_gold_standard`-based loaders for NDG's oracle (via `load_gs_sad_sam_maps`). This is correct by design (different callers need different levels of provenance), but the dual code paths are a maintenance risk if enrollment logic changes.

### No division-by-zero guards where expected
All identified division points (`len(gold)`, `len(result)`, `(tp+fp)`, `(prec+rec)`, etc.) are properly guarded. No unguarded division-by-zero found.

---

## Conclusion

The core metric math is correct in `new_metrics_analysis.py`. The six metrics (MCC, EMR, MAP, ACF1, NDG, HUS) implement their formulas correctly. The main issues are:

1. **Actionable inconsistency**: `metrics_api.py` uses `n_sentences = enrolled-linked sentences only` while `new_metrics_analysis.py` uses `n_sentences = total text sentences` when computing the NDG random baseline. This produces different NDG values for the same project from the two scripts. One of these needs to be adopted as the canonical definition and the other aligned to it.

2. **Latent correctness bug**: MCC in `metrics_api.py` does not add result-only files to the universe, which can yield negative `tn` if an external caller passes result links to files outside the gold SAM-CODE map. For the standard TransArc result this does not trigger.

3. **Undocumented FP exclusion**: `sentence_f1` silently ignores gold-negative sentences predicted by the system, overstating precision. This should be documented as a design decision or fixed to count those as FPs.

4. **Dead code**: Two unused variables in `compute_random_f1` and one unused parameter.

None of the published report numbers (`NEW_METRICS_REPORT.md`) are affected by issues 2 or 3, since `new_metrics_analysis.py` handles MCC correctly and `sentence_f1` is only in `metrics_api.py`. Issue 1 means NDG values from `metrics_api.py` will differ from `new_metrics_analysis.py` by a project-specific amount.
