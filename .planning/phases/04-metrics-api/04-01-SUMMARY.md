---
phase: 04-metrics-api
plan: 01
subsystem: metrics
tags: [metrics, csv, latex, booktabs, sad-sam, sad-code, mcc, map, acf1, ndg, hus, stdlib]

# Dependency graph
requires:
  - phase: v1.0 (Pillar 1 + Pillar 2)
    provides: transarc_error_analysis loaders + calc_metrics, evaluation_critique granularity helpers, new_metrics_analysis alt metrics, generate_tables LaTeX helpers
provides:
  - "Single reproducible metrics-reporting entry point: src/lib/metrics_api.py --task {sad-sam,sad-code}"
  - "Wide per-project CSV (reports/metrics_<task>.csv) + booktabs LaTeX table (writing/tables/metrics_<task>.tex)"
  - "Unified 12-column metric schema with task-appropriate N/A cells"
affects: [phase-05-consequences-study, paper-eval-tex]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "argparse CLI surface (first in src/): required --task choices + validated --project"
    - "Compose four sibling modules via three sys.path.insert hops (lib/bias/paper)"
    - "Unified column superset with em-dash N/A cells per task asymmetry"
    - "Zero metric-math reimplementation — every value flows from an imported function"

key-files:
  created:
    - src/lib/metrics_api.py
    - reports/metrics_sad-sam.csv
    - reports/metrics_sad-code.csv
    - writing/tables/metrics_sad-sam.tex
    - writing/tables/metrics_sad-code.tex
  modified: []

key-decisions:
  - "MAP omitted for sad-code (CONTEXT: optional there) → set to N/A, keeping schema uniform"
  - "Provenance enrolled set (enroll_with_provenance) used for ALL four sad-code granularity calls so they agree"
  - "sentence_f1 for sad-sam built via shared-component set transform + calc_metrics (no new metric math)"

patterns-established:
  - "Pattern: reuse-only metrics aggregation — transform link sets, call existing primitives, never reimplement"
  - "Pattern: task asymmetry enforced in code — sad-sam path never touches evaluation_critique _compute_* helpers"

requirements-completed: [MTR-01, MTR-02, MTR-03, MTR-04, MTR-05]

# Metrics
duration: ~15min
completed: 2026-05-30
---

# Phase 4 Plan 01: Metrics API Summary

**Stdlib-only `metrics_api.py` CLI that reuses existing primitives to emit a unified sad-sam / sad-code metric set (link/sentence/decision/component/file/weighted F1 + MCC/MAP/ACF1/NDG/HUS) as a wide CSV and a booktabs LaTeX table, reproducing every already-published reference value exactly.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-05-30T16:48:44Z
- **Tasks:** 3
- **Files modified:** 5 (1 source created, 4 generated artifacts)

## Accomplishments
- `src/lib/metrics_api.py`: a single reproducible metrics entry point composing four existing modules with zero metric-math reimplementation.
- SAD-SAM row: link=decision, sentence, component F1 + MCC/MAP/HUS; file/weighted/ACF1/NDG correctly marked N/A (no enrollment). All alt-metric values match `reports/NEW_METRICS_REPORT.md` exactly (MCC, MAP, HUS summaries).
- SAD-CODE row: file/decision/component/weighted F1 + MCC/ACF1/NDG/HUS via verbatim reuse of `evaluation_critique` provenance helpers; jabref File 0.943 / Decision 0.394 reproduce `reports/EVALUATION_CRITIQUE.md`.
- Missing per-project results file → stderr WARNING + skip, exit 0 (T-04-01 mitigation). `--project` validated against PROJECTS allow-list (T-04-03).

## Task Commits

1. **Task 1: CLI skeleton, imports, schema, CSV+LaTeX emitters** - `bcdbc24` (feat)
2. **Task 2: sad-sam metric row (link/sentence/component + MCC/MAP/HUS)** - `25e679c` (feat)
3. **Task 3: sad-code metric row (file/decision/component/weighted + MCC/ACF1/NDG/HUS)** - `0f11b74` (feat)

## Files Created/Modified
- `src/lib/metrics_api.py` - stdlib-only CLI computing the unified metric set for sad-sam/sad-code, emitting CSV + LaTeX.
- `reports/metrics_sad-sam.csv` - wide sad-sam metrics, 5 project rows + Average.
- `reports/metrics_sad-code.csv` - wide sad-code metrics, 5 project rows + Average.
- `writing/tables/metrics_sad-sam.tex` - booktabs LaTeX table (sad-sam).
- `writing/tables/metrics_sad-code.tex` - booktabs LaTeX table (sad-code).

## Verification Highlights
- `--task sad-sam` and `--task sad-code` both exit 0, writing 7-row CSVs (header + 5 projects + Average) and booktabs `.tex` tables containing `tabular` + `\fone` macros.
- Reference parity: sad-sam MCC (mediastore 0.711, jabref 0.933), MAP (jabref 0.950), HUS (mediastore 0.727, jabref 0.889) all match NEW_METRICS_REPORT.md; sad-code jabref File 0.943 / Decision 0.394 match EVALUATION_CRITIQUE.md; sad-code ACF1 mediastore 0.739, HUS mediastore 0.762/jabref 0.667 match.
- No leakage: zero benchmark-derived word lists; no `_compute_*` helper called inside the sad-sam path; no metric math redefined locally.

## Decisions Made
- **MAP set to N/A for sad-code** — CONTEXT flagged sad-code MAP as optional; omitting it (rather than computing a redundant file-ordering MAP) keeps the unified schema clean. Resolved a `KeyError: 'map'` in `build_avg_row` (Rule 3: blocking) by explicitly assigning `row["map"] = NA`.
- **Single consistent `enrolled` variable** — used the provenance-tracked `enrolled` from `enroll_with_provenance` for all four sad-code granularity calls (matching the part5 caller), so file/decision/component/weighted agree.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] sad-code row omitted the `map` schema key**
- **Found during:** Task 3 (sad-code row implementation)
- **Issue:** `compute_sad_code_row` did not set `row["map"]`; `build_avg_row` iterates `NUMERIC_COLS` (which includes `map`) and raised `KeyError: 'map'`. CONTEXT specifies MAP is optional/inapplicable for sad-code.
- **Fix:** Added `row["map"] = NA` to the sad-code N/A block.
- **Files modified:** src/lib/metrics_api.py
- **Verification:** `--task sad-code` full + single-project runs exit 0; CSV `map` column shows `—` for sad-code.
- **Committed in:** `0f11b74` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for the sad-code path to run; no scope creep. The plan's schema-completeness contract (every SCHEMA column keyed) was the implicit requirement.

## Issues Encountered
- Single-project runs (`--project jabref`) overwrite the full-run CSV (same output path). Expected behavior, not a bug — regenerated the full sad-code/sad-sam CSVs after the single-project verification so committed artifacts reflect all 5 projects.

## User Setup Required
None - offline stdlib script, local file I/O only.

## Next Phase Readiness
- Phase 5 (consequences study) can consume `reports/metrics_<task>.csv` and `writing/tables/metrics_<task>.tex` directly as evidence, avoiding duplicate metric computation (STATE concern resolved).
- sam-code task remains deferred (out of scope this milestone).

## Self-Check: PASSED

All 5 created artifacts + SUMMARY.md exist; all 3 task commits (bcdbc24, 25e679c, 0f11b74) present in git history.

---
*Phase: 04-metrics-api*
*Completed: 2026-05-30*
