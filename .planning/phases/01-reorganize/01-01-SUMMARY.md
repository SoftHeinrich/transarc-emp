---
plan: 01-01
phase: 1
title: "Move-only reorg into two pillars + archive"
status: complete
date: 2026-05-30
---

# Summary: Phase 1 Reorganize — Plan 01-01

Move-only `git mv` reorganization into two pillars + archive. Zero code edits
(depth-2 preserved, every `sys.path.insert(parent.parent/"lib")` still resolves).

## Tasks Completed

1. **Assemble Pillar 1 (`src/transarc/`)** — `git mv` of 3 propagation scripts +
   s12c_sadcode_comparison.py (tracked since b1407e1) into new `src/transarc/`.
   Removed empty `src/propagation/`. Commit `refactor(01): assemble Pillar 1`.
2. **Expand Pillar 2 (`src/bias/`) + archive** — `git mv` of 5 evaluation scripts
   into existing `src/bias/`; `git mv` of annotation pair + ANNOTATION_CONVENTION.md
   into `archive/`. Removed empty src dirs. Commit `refactor(01): expand Pillar 2`.
3. **Static verification** — all checks pass (see Verification).

## Final Structure

```
src/
  transarc/  (4 .py)  sad_sam_actual_contribution, sad_sam_tp_gain_analysis,
                      sam_code_cascade_analysis, s12c_sadcode_comparison
  bias/      (9 .py)  benchmark_bias_study, enrollment_bias_analysis,
                      enrollment_distortion_analysis, sam_code_distribution_analysis
                      (original 4) + evaluation_critique, creative_metrics_analysis,
                      holistic_metrics_analysis, extreme_baseline_analysis,
                      stupid_baseline_analysis (moved 5)
  lib/       (2 .py)  transarc_error_analysis (loaders), new_metrics_analysis (UNCHANGED)
archive/             + doc_structure_analysis_v2.py, reverse_engineer_convention.py,
                       ANNOTATION_CONVENTION.md
reports/             flat; S12C_VS_TRANSARC.csv intact
```

## Verification Results (Task 3)

| Check | Result |
|-------|--------|
| src/transarc/ .py count | 4 ✓ |
| src/bias/ .py count | 9 (4+5) ✓ |
| src/lib unchanged (loader + new_metrics) | ✓ |
| No retained script imports archived module | grep=0 ✓ |
| No retained report links ANNOTATION_CONVENTION | grep=0 ✓ |
| No swattr refs in src/ | grep=0 ✓ |
| reports/S12C_VS_TRANSARC.csv intact | ✓ |
| Depth-2 preserved (sys.path.insert in pillar scripts) | 13/13 ✓ |
| src/evaluation, src/propagation, src/annotation removed | ✓ |
| Working tree clean | ✓ |

## Requirements Covered

SCOPE-01, SCOPE-02, SCOPE-03, SCOPE-04, SCOPE-05, ARCH-01, ARCH-02, ARCH-03, ARCH-04.

## Deviations / Notes

- **s12c handling**: plan noted s12c might be untracked; it was tracked (b1407e1),
  so used `git mv` (history-preserving) as the plan's NOTE directed.
- **Environment**: hostshare mount caused flaky git output and one orphaned subagent
  commit (planner's plan commit 348d25e dangled → plan re-committed as 4326729).
  All Phase 1 git ops were run inline in the main context, serialized, with
  `git update-index --refresh` + ground-truth checks after each step to avoid races.
- An empty `src/evaluation/` dir lingered after the first `rm -rf` (mount glitch);
  removed in a follow-up. No tracked files affected.
- REPRO-01/02/03 (actually running scripts) deferred to Phase 2 per plan guardrail.
