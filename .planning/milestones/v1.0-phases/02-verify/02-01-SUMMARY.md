---
plan: 02-01
phase: 2
title: "Run all 13 pillar scripts; confirm clean execution + report regeneration"
status: complete
date: 2026-05-30
---

# Summary: Phase 2 Verify — Plan 02-01

Ran all 13 retained pillar scripts from repo root after the Phase 1 reorg.

## Results

| Pillar | Scripts | Exit 0 |
|--------|---------|--------|
| 1 — TransArc (`src/transarc/`) | sad_sam_actual_contribution, sad_sam_tp_gain_analysis, sam_code_cascade_analysis, s12c_sadcode_comparison | 4/4 ✓ |
| 2 — Bias (`src/bias/`) | benchmark_bias_study, enrollment_bias_analysis, enrollment_distortion_analysis, sam_code_distribution_analysis, evaluation_critique, creative_metrics_analysis, holistic_metrics_analysis, extreme_baseline_analysis, stupid_baseline_analysis | 9/9 ✓ |

**Total: 13/13 exit 0. Zero failures.**

- No `ModuleNotFoundError` for `transarc_error_analysis` or `new_metrics_analysis` →
  shared `src/lib/` loader importable from both `src/transarc/` and `src/bias/`
  (REPRO-01 ✓). The depth-2 `parent.parent/lib` invariant held — no import edits needed.
- Reports regenerated **identically** (git diff = 0 on `reports/`) → outputs are
  deterministic/stable, confirming reproducibility (REPRO-02, REPRO-03 ✓).

## Requirements Covered

REPRO-01 (shared lib importable both pillars), REPRO-02 (Pillar 1 runs + reports),
REPRO-03 (Pillar 2 runs + reports).

## Notes

- Each script run with a 300s timeout; stdout+stderr captured to `/tmp/p2logs/<script>.log`.
- Inputs confirmed present: benchmark data (5 projects) at the ardoco tests-base path;
  in-repo `results/`. Mount stat-layer is flaky for shell `ls`/`test -d`, but real
  python file I/O succeeded for every script.
- Run inline in main context (subagent git ops race the index on this mount — learned
  in Phase 1).
- No analysis logic changed; no pre-existing failures encountered.
