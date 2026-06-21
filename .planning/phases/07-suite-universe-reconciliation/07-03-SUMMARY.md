---
phase: 07-suite-universe-reconciliation
plan: 03
subsystem: testing
tags: [component-suite, equivalence-oracle, determinism-check, reproducibility-gate, stdlib, mapped-only-universe]

# Dependency graph
requires:
  - phase: 07-suite-universe-reconciliation (plan 01, CMP-01)
    provides: finalized component_suite (micro/macro on shared gold∪result mapped-only universe); full 5-project committed COMPONENT_SUITE_{sad-code,sad-model}.csv
  - phase: 07-suite-universe-reconciliation (plan 02, CMP-02)
    provides: mapped-only component_f1 single source of truth (metrics_api headline == suite micro); per_component_macro_f1 (oracle target B) left UNCHANGED
provides:
  - src/bias/check_component_suite.py — one standalone command (equivalence oracle + determinism check), exit 0 = both guarantees hold
  - equivalence oracle binding component_suite.component_suite() macro to rq2_trivial_baselines.per_component_macro_f1 to 1e-9 (sad-code, every present system, all 5 projects)
  - determinism gate proving the committed COMPONENT_SUITE_{level}.csv regenerate byte-identical for present-system rows at both levels (temp-only regen, reports/ untouched)
affects: [08-fitness-scorecard, 09-paper-prose, component-suite, reproducibility]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Standalone reproducibility check modeled on mini-src/check.py: per-(system/project) loop, TOL=1e-9, SKIP/OK/FAIL lines, failures counter, sys.exit(1)"
    - "Equivalence oracle re-derives file-level gold + file_to_comps itself (replicating _code_inputs internals exactly) — does NOT assume _code_inputs exposes them"
    - "Determinism check regenerates to tempfile.mkdtemp() by monkeypatching component_suite.REPORTS in try/finally; never writes the real reports/ dir; diff scoped to present-system rows (D-09)"

key-files:
  created:
    - src/bias/check_component_suite.py
  modified: []

key-decisions:
  - "Oracle macro side built via component_suite._code_inputs(proj) for (gold_sc, collapse), with enrolled + file_to_comps rebuilt separately from the same transarc_error_analysis loaders — the 1e-9 assertion catches any drift between the two reconstructions (it found exactly 0.0 delta)"
  - "swattr/transarc treated as an always-on assertion: an empty sad-code link set for it is a FAIL, not a SKIP (T-07-03-03 — silent skip hiding a regression); only external systems (s20linker/artemis) skip-with-notice when absent"
  - "Determinism diff keyed by (project, system_label) including AVG rows; present systems = labels appearing in the regenerated temp CSV; absent committed rows skip-with-notice (D-09 present-system scope)"
  - "CSV equality compared on the written 4-dp string rows (same write_csv formatting) — the determinism notion is identical committed file content for present-system rows"

patterns-established:
  - "Pattern 1: reproducibility gate is a single python3 invocation returning a pass/fail exit code (D-05), not a --check flag and not two scripts"
  - "Pattern 2: an independent macro reference (per_component_macro_f1) pins the suite headline; sad-code only because sad-model would reuse the suite math and be circular (D-06)"

requirements-completed: [CMP-06]

# Metrics
duration: ~20min
completed: 2026-06-21
---

# Phase 7 Plan 03: Component Suite Reproducibility Gate (CMP-06) Summary

**One standalone `src/bias/check_component_suite.py` that binds the suite headline `macro` to the independent `per_component_macro_f1` oracle (0.0 delta, 1e-9 tol, all 15 present-system × project cells at sad-code) and proves the committed `COMPONENT_SUITE_{level}.csv` regenerate byte-identically via a temp-only run — exits 0, leaves `reports/` untouched.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-06-21
- **Tasks:** 2 (both complete)
- **Files modified:** 1 created, 0 modified

## Accomplishments
- **Equivalence oracle (D-06):** for every present system in `component_suite.SYSTEMS` (swattr/transarc always; s20linker + artemis present here) at sad-code across all 5 projects, `component_suite.component_suite(gold_sc, result_sc)['macro']` equals `rq2_trivial_baselines.per_component_macro_f1(enrolled, links, file_to_comps)` to within 1e-9 — measured delta is exactly `0.00e+00` on all 15 cells.
- **Determinism check (D-07/D-09):** regenerates both levels into a `tempfile.mkdtemp()` dir (by monkeypatching `component_suite.REPORTS`, restored in `finally`) and diffs the committed `reports/COMPONENT_SUITE_{sad-code,sad-model}.csv` for present-system rows (incl. AVG) — clean for all 36 rows (3 systems × {5 projects + AVG} × 2 levels).
- **Non-mutating:** running the check leaves `reports/COMPONENT_SUITE_*.csv` untouched (`git status --short` empty); no temp dirs leaked (`shutil.rmtree` in `finally`).
- **Stdlib-only + reuse:** imports only `csv`/`shutil`/`sys`/`tempfile`/`collections`/`pathlib` plus the project modules (`component_suite`, `rq2_trivial_baselines`, `transarc_error_analysis`); adds **no new F1 math** — every score flows through the imported suite/oracle functions.

## Task Commits

Manual mode — the orchestrator performs all git commits; no per-task hashes were created by this executor. Work is staged in the working tree at `/mnt/hostshare/ardoco-home/transarc-emp` as a single new untracked file `src/bias/check_component_suite.py`.

1. **Task 1: Author `check_component_suite.py` (equivalence oracle + determinism check)** — created `src/bias/check_component_suite.py` (depth-2 + `sys.path.insert` to `src/lib`, `mini-src/check.py` shape). Verify `SCRIPT_OK` (ast.parse + grep 1e-9/tempfile/per_component_macro_f1) passed.
2. **Task 2: Run green + prove non-mutating** — `python3 src/bias/check_component_suite.py` exits 0 with PASS, no FAIL lines; `git status` on the two committed CSVs empty. Verify `CHECK_GREEN_AND_CLEAN` passed.

## Files Created/Modified

### Created
- `src/bias/check_component_suite.py` — standalone CMP-06 reproducibility gate. PART 1 equivalence oracle (sad-code, suite-macro == `per_component_macro_f1`, TOL=1e-9, swattr/transarc always asserted, external systems skip-when-absent). PART 2 determinism check (regenerate both levels to a temp dir, diff committed CSVs scoped to present-system rows, restore `component_suite.REPORTS`).

### Modified
- None. **Do-not-modify list honored:** `component_suite.py`, `rq2_trivial_baselines.py`, `evaluation_critique.py`, `metrics_api.py`, the committed CSVs, and all 07-01/07-02 files are untouched (`git status --short --untracked-files=no` is empty).

## Decisions Made
- **Oracle input reconstruction (anticipated by the plan-check):** `_code_inputs(proj)` returns only `(gold_sc, collapse)` — not the file-level `enrolled` gold or `file_to_comps` that `per_component_macro_f1` needs. The check rebuilds both in `_oracle_file_inputs(proj)` by replicating `_code_inputs`' internals exactly (`load_code_model_files` → `load_model_element_names` → `enroll_gold_standard(load_gs_sam_code_raw(...))` → `file_to_comps`; `load_gs_sad_code_enrolled` → file-level gold). The 1e-9 assertion validates the rebuild matches what the suite collapses internally — it does (delta 0.0), confirming both oracle sides share one mapped-only universe (D-10).
- **Always-on assertion (T-07-03-03):** an empty sad-code link set for `swattr_transarc` is a FAIL (not a SKIP) so a real regression in the in-repo deterministic system cannot hide behind a skip; only external roots (s20linker/artemis) skip-with-notice.
- **Determinism equality on formatted CSV rows:** both committed and regenerated CSVs are written by the same `write_csv` 4-dp formatting, so identical committed file content for present-system rows is the determinism notion; comparison is keyed by `(project, system_label)` and includes AVG rows.

## Deviations from Plan

None — plan executed exactly as written. The file-level oracle-input reconstruction was explicitly mandated by the plan's `<action>` and plan-check note (`_code_inputs` does not expose `enrolled`/`file_to_comps`), so rebuilding them is in-scope, not a deviation. No auto-fixes (Rules 1–3) were triggered; no architectural question (Rule 4) arose.

## Issues Encountered
None. The oracle passed on the first run with an exact `0.00e+00` delta on all 15 cells (no universe-rebuild debugging was needed), and the determinism diff was clean on the first run for all 36 present-system rows.

## User Setup Required
None — no external service configuration required. (All three external result roots — `agent-linker/results/ablation_results`, `sota/recovered-links/doc-code`, `results_artemis_gpt54` — are present in this environment, so all 3 systems are exercised; the skip-with-notice path is implemented and ready for environments where a root is absent.)

## Verification Results

| Gate | Command | Result |
|------|---------|--------|
| Task 1 syntax + required tokens | `ast.parse` + grep `1e-9` / `tempfile` / `per_component_macro_f1` | PASS (`SCRIPT_OK`) |
| Task 1 stdlib-only imports | `grep -nE "^\s*import \|^\s*from "` | PASS (csv/shutil/sys/tempfile/collections/pathlib + project modules only) |
| Task 1 rebuilds file-level oracle inputs | grep `load_gs_sad_code_enrolled` / `enroll_gold_standard` | PASS |
| Task 1 imports both oracle targets | grep `component_suite.component_suite` + `per_component_macro_f1` | PASS |
| Task 2 oracle holds (suite-macro == per_component_macro_f1, 1e-9, all 5 projects, all present systems) | `python3 src/bias/check_component_suite.py` | PASS (15 OK, every \|delta\|=0.00e+00) |
| Task 2 determinism diff clean (both levels, present-system rows) | same run | PASS (36 OK, 0 FAIL) |
| Task 2 exit 0 + PASS line, no FAIL | same run | PASS (EXIT_CODE=0) |
| Task 2 committed CSVs untouched | `git status --short reports/COMPONENT_SUITE_*.csv` | PASS (empty) → `CHECK_GREEN_AND_CLEAN` |
| Scope: only new script added | `git status --short --untracked-files=no` | PASS (empty); suite/oracle/metrics_api/CSVs unedited |
| No temp dir leaked | `ls /tmp/component_suite_det_*` | PASS (none) |

## Self-Check: PASSED
- `src/bias/check_component_suite.py` — FOUND.
- No per-task commit hashes to verify (manual mode; orchestrator owns git). The single deliverable is the new script, present and passing.

## Next Phase Readiness
- CMP-06 satisfied → ROADMAP Phase 7 SC2 (equivalence oracle asserts suite-macro == `per_component_macro_f1`) and SC4 (re-running regenerates the committed CSVs deterministically) are both demonstrably met by `python3 src/bias/check_component_suite.py` (exit 0).
- Phase 8 (fitness scorecard / multi-system comparison) can build on a suite whose headline `macro` is independently pinned and whose committed CSVs are provably regenerable.
- The check is environment-portable: where an external root is absent it skip-with-notices instead of failing (D-09), while swattr/transarc always re-asserts.

---
*Phase: 07-suite-universe-reconciliation*
*Completed: 2026-06-21*
