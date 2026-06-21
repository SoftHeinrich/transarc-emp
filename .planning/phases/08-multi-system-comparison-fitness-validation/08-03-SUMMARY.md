---
phase: 08-multi-system-comparison-fitness-validation
plan: 03
subsystem: testing
tags: [metric-fitness, scorecard, component-suite, trivial-baselines, oracle-anchors, determinism, python-stdlib]

# Dependency graph
requires:
  - phase: 08-multi-system-comparison-fitness-validation (08-01)
    provides: pinned ARTEMIS_LOCAL source so the scorecard's artemis column inputs are reproducible
  - phase: 07-suite-universe-reconciliation
    provides: frozen universe split (micro/macro/gap shared gold∪result; min_comp/pct_missed gold-only) the scorecard scores as-defined
provides:
  - "src/bias/metric_fitness.py — standalone numeric fitness scorecard scoring 5 suite columns on 4 axes at both levels + a data-derived verdict-derivation function"
  - "reports/METRIC_FITNESS.csv — 10 data rows (5 columns × 2 levels) of separation/validity/stability/degeneracy + per-column verdict, 4-dp, deterministic"
  - "reports/METRIC_FITNESS.md — per-axis scorecard tables, one-line data-derived verdict, honesty note (D-07), and the quantified SC4 artemis long-tail finding"
affects: [phase-09-paper-integration, CMP-05, eval.tex-ch2]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scorecard mirrors check_component_suite.py standalone shape (sys.path.insert src/lib then src/bias; per-level loop; OK lines; report+CSV)"
    - "Trivial floor + real systems scored by the IDENTICAL suite path (collapse → component_suite); no new F1 math"
    - "Verdict DERIVED by a function from computed axis scores (separation ≥ median AND degeneracy ≥ median), not hardcoded"
    - "PYTHONHASHSEED-independent determinism: pre-sort set inputs to seeded RNG and key-sort dict inputs to order-sensitive library anchors"

key-files:
  created:
    - src/bias/metric_fitness.py
    - reports/METRIC_FITNESS.csv
    - reports/METRIC_FITNESS.md
  modified: []

key-decisions:
  - "Separation = mean(real 3 systems) − mean(rq2 Random+Top-3 floor) margin per column; gap uses |gap| skew magnitude, pct_missed oriented as coverage 1−pct_missed"
  - "Validity = oracle-ceiling headroom over the rq2 random→oracle band for F1-scaled columns (micro/macro/min_comp); gap/pct_missed report the oriented real mean as an interpreted bound (not an F1 comparison)"
  - "Stability = cross-project pstdev pooled over the 3 real systems; degeneracy = cross-system spread of per-system column means (small = degenerate)"
  - "sad-model separation is scored against the sad-code trivial floor (rq2 floor is file-level only) — scoping stated in the report (D-08)"
  - "Determinism fixed by sorting RNG/anchor inputs in metric_fitness.py only — the rq2 Random/Top-3 generators and compute_random_f1/compute_oracle_f1 are reused verbatim (D-01)"

patterns-established:
  - "Pattern 1: data-derived verdict via derive_verdict() consuming the CSV axis scores — headline/diagnostic emerges from median thresholds, with an explicit honesty note when the data contradicts the expected verdict"
  - "Pattern 2: reproducibility hardening for reused stochastic/order-sensitive helpers by stabilizing their INPUTS (sorted sequences/dicts) without editing the helper"

requirements-completed: [CMP-04]

# Metrics
duration: ~35min
completed: 2026-06-21
---

# Phase 8 Plan 03: Metric Fitness Scorecard Summary

**Standalone numeric scorecard scoring micro/macro/gap/min_comp/pct_missed on separation/validity/stability/degeneracy at both levels, with a data-derived verdict (headline = micro, macro, min_comp; diagnostic = gap, pct_missed) and the quantified artemis long-tail-abandonment finding — deterministic across runs.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 2
- **Files modified:** 3 (1 script + 2 reports)

## Accomplishments
- `src/bias/metric_fitness.py`: a stdlib-only scorecard that reuses `component_suite` (real systems), the rq2 `Random`/`Top-3` trivial floor, and the `compute_oracle_f1`/`compute_random_f1` anchors — adding NO new F1 math (only `calc_metrics` via the imports).
- Four numeric axes per (level × column): separation (real-vs-trivial margin, D-03), validity (oracle-ceiling headroom), stability (cross-project pstdev), degeneracy (cross-system spread).
- `derive_verdict()` ranks columns HEADLINE vs DIAGNOSTIC purely from the computed scores (separation ≥ median AND degeneracy ≥ median, pooled over both levels) — not a hardcoded string.
- SC4 artemis long-tail finding reproduced + quantified under the gold-only tail definition; the cited AVG min_comp/pct_missed match the committed COMPONENT_SUITE CSVs exactly.
- Byte-identical CSV across runs (and across 5 fresh PYTHONHASHSEED-randomized processes).

## Task Commits

1. **Task 1: Author metric_fitness.py (four axes, both levels)** - `e998aea` (feat)
2. **Task 2: Run scorecard — data-derived verdict + artemis tail + determinism fix** - `f9d140b` (fix)

_Note: Task 1 carries tdd="true" but this is stdlib-only research code with no test framework; per the manual-mode brief, the plan's own `<verify>` automated blocks (METRIC_FITNESS_AUTHORED / SCORECARD_GREEN_AND_DETERMINISTIC) are the validation — no separate RED test file was authored._

## Files Created/Modified
- `src/bias/metric_fitness.py` - The scorecard: floor/anchor builders, four axis functions, `derive_verdict()`, CSV/MD writers.
- `reports/METRIC_FITNESS.csv` - 10 data rows (micro/macro/gap/min_comp/pct_missed × sad-model/sad-code) of the four axis scores + verdict.
- `reports/METRIC_FITNESS.md` - Per-axis tables, the one-line data-derived verdict, the honesty note, and the SC4 artemis tail table.

## Verdict (data-derived) and honesty

- **Verdict the script emitted:** headline columns = `micro`, `macro`, `min_comp`; diagnostic columns = `gap`, `pct_missed`.
- **vs the milestone's expected verdict** (headline = macro + tail; diagnostic = micro/gap): **PARTIAL MATCH with one explicit contradiction.**
  - Matches: `macro` is headline; `min_comp` (the tail) is headline; `gap` is diagnostic.
  - Contradicts: `micro` ALSO ranks headline (not diagnostic). The data shows micro separates real-from-trivial and discriminates systems on par with macro — pooled separation micro 0.5279 vs macro 0.6200 (a 0.092 gap on separation only), degeneracy/stability within 0.05. The honesty note states this: the micro-vs-macro aggregation contrast is **second-order**, consistent with the Phase-7 reconciliation; the report does NOT oversell macro as the sole headline.
  - `pct_missed` lands diagnostic (low separation + low cross-system spread), while its sibling tail column `min_comp` is the single most discriminating column (degeneracy 0.3307, far above the others).
- The verdict is internally consistent with the CSV: headline columns are exactly the ones above the separation-median (0.4579) AND degeneracy-median (0.0728); both criteria agree.

## SC4 — artemis long-tail abandonment (quantified)

| level | artemis AVG min_comp | artemis AVG pct_missed | projects with min_comp=0 |
|---|---|---|---|
| sad-code | 0.3455 | 0.0533 | bigbluebutton, jabref |
| sad-model | 0.2788 | 0.0832 | teammates, bigbluebutton, jabref |

These AVG values match the artemis AVG rows of `reports/COMPONENT_SUITE_sad-code.csv` (min_comp=0.3455, pct_missed=0.0533) and `reports/COMPONENT_SUITE_sad-model.csv` (min_comp=0.2788, pct_missed=0.0832) — confirmed by reading both committed CSVs. The scorecard reads the same suite, so the tail finding is reproduced, not re-derived.

## Decisions Made
- Numeric axis rubric chosen at executor discretion (D-13): margin / oracle-band-headroom / pstdev / cross-system spread, with `gap`/`pct_missed` oriented so "higher = real beats trivial."
- The verdict thresholds are per-column medians of the pooled axis scores so the split is intrinsic to the data, not an external cutoff.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Non-deterministic scorecard CSV across runs**
- **Found during:** Task 2 (running the scorecard; the determinism `<verify>` failed).
- **Issue:** The first run produced a CSV that differed from the second. Root cause was PYTHONHASHSEED-dependent set/dict iteration order feeding two reused helpers: (a) `baseline_random_same_size` does `random.choice(list(all_code_files))`, so `random.seed(42)` alone did NOT make the Random floor reproducible across processes; (b) `compute_random_f1` builds a file→component map by last-writer-wins over `gold_sam_code_map.items()`, and for files shared by several components (e.g. 7 such files in teastore) the iteration order shifted the validity anchor by ~1e-3.
- **Fix:** In `metric_fitness.py` only — pass SORTED `code_files`/`gold_sents` sequences to the rq2 baseline generators, and pass a key-sorted `gold_sam_code_map` into the rq2 anchor functions. This stabilizes the inputs; the rq2 generators and `compute_random_f1`/`compute_oracle_f1` are reused verbatim (no new baseline, no new F1 math, D-01 honored). The library modules were NOT edited.
- **Files modified:** src/bias/metric_fitness.py
- **Verification:** 5 fresh default-`PYTHONHASHSEED` processes now produce 1 unique CSV md5; the plan's determinism `<verify>` prints SCORECARD_GREEN_AND_DETERMINISTIC.
- **Committed in:** f9d140b (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The fix was required for the plan's own determinism acceptance criterion. It only re-orders inputs to reused helpers — no scope creep, no new baseline, no metric-math reimplementation. The known carry-over "NDG non-determinism in compute_random_f1" (08-CONTEXT deferred) is sidestepped at the scorecard boundary, not fixed in the library.

## Issues Encountered
- The two-stage non-determinism (Random floor, then validity anchor) surfaced sequentially: fixing the floor first revealed the residual anchor drift. Both were isolated with per-component cross-process reproduction tests and fixed by input-ordering. Resolved.

## Self-Check: PASSED

- Files exist: `src/bias/metric_fitness.py`, `reports/METRIC_FITNESS.csv`, `reports/METRIC_FITNESS.md`, `08-03-SUMMARY.md` — all FOUND.
- Commits exist: `e998aea` (Task 1), `f9d140b` (Task 2) — both FOUND.
- Protected files untouched: `component_suite.py`, `rq2_trivial_baselines.py`, `.planning/ROADMAP.md` — CLEAN (`.planning/STATE.md` left to the orchestrator).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CMP-04 satisfied: the numeric scorecard + data-derived verdict + quantified artemis tail are ready for Phase 9 (CMP-05) paper integration into eval.tex Ch2.
- The honesty finding (micro ≈ macro is second-order; min_comp is the discriminating tail column; pct_missed is diagnostic) should be carried verbatim into the paper prose rather than restating the expected macro-only headline.

---
*Phase: 08-multi-system-comparison-fitness-validation*
*Completed: 2026-06-21*
