---
quick_id: 260602-qwd
slug: investigate-3-warnings-from-metrics-audi
description: "Investigate 3 warnings from metrics audit — are they real bugs?"
date: 2026-06-02
status: planned
must_haves:
  truths:
    - Each warning classified as BUG (wrong output), DESIGN (intentional but undocumented), or FALSE ALARM
    - Concrete evidence: actual values or code traces, not just "could happen"
  artifacts:
    - .planning/quick/260602-qwd-investigate-3-warnings-from-metrics-audi/260602-qwd-SUMMARY.md
  key_links:
    - src/lib/metrics_api.py
    - src/lib/new_metrics_analysis.py
    - .planning/quick/260602-q6u-run-code-quality-review-audit-does-the-m/260602-q6u-SUMMARY.md
---

# Quick Task 260602-qwd: Investigate 3 Warnings

From audit 260602-q6u. Three WARNINGs need deeper investigation to determine if
they produce wrong output in practice, or are acceptable design choices.

## Warning 1: NDG `n_sentences` inconsistency

**Location:** `src/lib/metrics_api.py:235` vs `src/lib/new_metrics_analysis.py:785`

**Claim:** `metrics_api.py` uses `len({s for (s, _c) in enrolled})` (enrolled-linked
sentences only) as `n_sentences`, while `new_metrics_analysis.py` uses `len(all_sents)`
(total text sentences from `load_text()`). This makes `p` larger in metrics_api,
inflating `random_f1`, and depressing NDG.

**Investigate:**
1. For each of the 5 projects, compute both sentence counts: total text vs enrolled-linked.
   Use the actual benchmark data — read `load_text` result and count enrolled SAD-CODE gold sentences.
2. For a concrete project (e.g. mediastore), compute what `random_f1` would be with
   each denominator. How much does NDG actually change?
3. Which is the semantically correct denominator? The random model predicts over
   ALL sentences in the document, not just gold-linked ones. So total text sentences
   is the correct denominator for a document-level random baseline.
4. Verdict: BUG in metrics_api.py, or intentional scoping to the evaluation domain?

**Data needed:**
- `PROJECTS` list and `load_text(proj)` sentence count per project
- `load_gs_sad_code_enrolled(proj, code_model)` to count distinct enrolled sentences
- Check if NDG values in existing reports came from `new_metrics_analysis.py` or
  `metrics_api.py`

## Warning 2: MCC `all_files` latent bug in `metrics_api.py`

**Location:** `src/lib/metrics_api.py:248`

**Claim:** `all_files = set().union(*gs_sam_code_map.values())` excludes result-only
files from the universe, so if `res` has FP files outside the gold SAM-CODE map,
`tn = universe_size - tp - fp - fn` goes negative, corrupting MCC.

**Investigate:**
1. Check if the comparison scripts (sadsam_comparison.py, sadcode_comparison.py) pass
   result links that could contain out-of-gold files.
2. Check `load_result_sad_code` — does it normalize paths? Do result paths always
   match gold SAM-CODE map paths (after normalization)?
3. Check `load_gs_sam_code_maps` — are ALL possible result file paths guaranteed to
   be in `gs_sam_code_map.values()`?
4. If s11/s13f results are used via `compute_sad_code_metrics`, do they stay within
   the gold file universe?
5. Verdict: TRIGGERED in practice (real bug), or only theoretical for exotic inputs?

## Warning 3: `sentence_f1` FP undercount

**Location:** `src/lib/metrics_api.py:146-152`

**Claim:** Gold-negative sentences predicted by the system are excluded from `res_S`
AND `gold_S`, so they contribute zero FP. This overstates precision for systems that
predict links for sentences that have no gold entries at all.

**Investigate:**
1. Does TransArc ever predict links for sentences with no gold SAD-SAM entries?
   Check one project (e.g. mediastore): are all sentences in the TransArc SAD-SAM
   result also present in the gold SAD-SAM?
2. Does s11/s13f ever predict links for gold-negative sentences? This matters more
   for LLM-based linkers.
3. What is the standard definition of sentence-level F1 in IR? Should FP-only
   predicted sentences count as FPs?
4. Compute the actual difference for mediastore: sentence_f1 with and without
   counting gold-negative FP sentences.
5. Verdict: BUG (wrong precision), DESIGN (acceptable approximation), or
   IRRELEVANT (never triggered in practice for these systems)?

## Output

Write `260602-qwd-SUMMARY.md` with:
- For each warning: evidence, concrete numbers, final verdict (BUG/DESIGN/FALSE ALARM)
- Overall: which issues should be fixed vs documented
