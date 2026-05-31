---
quick_id: 20260531-sadsam-metrics-comparator
status: complete
---

# Quick Task: SAD-SAM multi-level metrics comparator

## Goal
Mirror the SAD-CODE comparator (`src/transarc/s12c_sadcode_comparison.py`) for the
SAD-SAM stage, comparing **s_linker11**, **s_linker13f**, and **TransArc/ARDoCo-standalone**.

## Key design finding (grounds the metric choice)
SAD-SAM gold = atomic `(modelElementID, sentence)` pairs. No directory enrollment.
Therefore the 4 SAD-CODE levels (file/decision/component/weighted) **all collapse to
pair-level** — verified: 0 duplicate component-names in any project's SAM gold, so even
component-collapse is a 1:1 relabel. This collapse is itself evidence for the Ch2
benchmark-bias narrative (multi-level divergence is a SAD-CODE enrollment artifact).

## Levels computed
1. **Pair-level** — exact `(component_id, sentence)` match (canonical).
2. **Sentence-coverage** — sentence TP if it has ≥1 correct link (orthogonal recall view).
3. **Element-coverage** — model element TP if it has ≥1 correct link (architecture-side coverage).
4. **Collapse proof** — component-level F1, shown to equal pair-level empirically.

## Approach (revised)
Reuse the existing architecture-aware suite, don't hand-roll. Refactored
`compute_sad_sam_metrics(proj, res)` and `compute_sad_code_metrics(proj, res)` out
of the `*_row` fns in `src/lib/metrics_api.py` (single source of truth), then drive
them per system. Full suite per task:
- SAD-SAM: link / sentence / component F1 + MCC + MAP + HUS (file/decision/weighted collapse).
- SAD-CODE: file / decision / component / weighted F1 + ACF1 + MCC + NDG + HUS (levels diverge).

s11/s13f SAD-CODE = their SAD-SAM × ARCOTL SAM-CODE standalone (same composition as s12c).

## Outputs
- `src/transarc/sadsam_comparison.py` → `reports/SADSAM_COMPARISON.md` + `reports/SADSAM_S11_S13F_VS_TRANSARC.csv`
- `src/transarc/sadcode_comparison.py` → `reports/SADCODE_COMPARISON.md` + `reports/SADCODE_S11_S13F_VS_TRANSARC.csv`

## Results (avg)
- SAD-SAM Link F1: TransArc 0.799 / s11 0.937 / s13f 0.951
- SAD-CODE File F1: TransArc 0.803 / s11 0.902 / s13f 0.931
- Both linkers beat TransArc on every metric, both tasks; s13f best.

## Done
1. ✅ Refactored metrics_api (regression: both CLIs still pass).
2. ✅ Wrote + ran both comparators; sanity-checked (TransArc matches known values).
3. ✅ Updated STATE.md + PLAN.md. → gitwk.
