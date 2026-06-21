---
phase: 08-multi-system-comparison-fitness-validation
plan: 01
subsystem: infra
tags: [provenance, reproducibility, artemis, component-suite, version-control]

# Dependency graph
requires:
  - phase: 07-suite-universe-reconciliation
    provides: component_suite.py loaders + reconciled universe split (ARTEMIS_LOCAL / ARTEMIS_DOC_CODE path contract)
provides:
  - "results_artemis_gpt54/ canonical ARTEMIS_LOCAL sad-code links source committed under version control (25 files, 5 projects)"
  - "reports/ARTEMIS_PROVENANCE.md authoritative-source ledger naming canonical vs external vs secondary/superseded artemis dirs"
affects: [08-02-comparison, 08-03-scorecard]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Provenance ledger pins canonical data source under VC + documents secondary dirs non-destructively"]

key-files:
  created:
    - reports/ARTEMIS_PROVENANCE.md
  modified:
    - results_artemis_gpt54/

key-decisions:
  - "Pinned results_artemis_gpt54/ as canonical ARTEMIS_LOCAL (D-10); secondary dirs documented-as-superseded, never deleted (CLAUDE.md non-destructive)"
  - "ARTEMIS_DOC_CODE (sota/recovered-links/doc-code) stays external/unvendored with skip-with-notice (D-08)"

patterns-established:
  - "Authoritative-source ledger: name what the code reads (ARTEMIS_LOCAL/_artemis_model), mark derived snapshots secondary, keep external roots unvendored"

requirements-completed: [CMP-03]

# Metrics
duration: 2min
completed: 2026-06-21
---

# Phase 8 Plan 01: Artemis Provenance Pin Summary

**Committed the canonical `results_artemis_gpt54/` ARTEMIS_LOCAL sad-code links source (25 files, 5 projects) under version control and wrote `reports/ARTEMIS_PROVENANCE.md` naming it authoritative — making the suite's artemis rows bit-for-bit reproducible and resolving the D-10 untracked-dir ambiguity.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-06-21T22:07:30Z
- **Completed:** 2026-06-21T22:09:16Z
- **Tasks:** 2
- **Files modified:** 26 (25 data files committed + 1 ledger created)

## Accomplishments
- Pinned the only artemis links input (`results_artemis_gpt54/`, the `ARTEMIS_LOCAL` path read by `component_suite._artemis_model` at `<proj>/sad-code/sadSamTlr_<proj>.csv`) under git — was previously untracked, so a fresh clone could not reproduce the artemis sad-code rows. Now 25 files across mediastore/teastore/teammates/bigbluebutton/jabref are tracked.
- Wrote `reports/ARTEMIS_PROVENANCE.md`: a three-entry ledger marking `results_artemis_gpt54/` AUTHORITATIVE, `ARTEMIS_DOC_CODE` (doc-code) EXTERNAL/unvendored, and `reports_artemis_gpt54_20260605_030524/` + `paper-result/` SECONDARY/SUPERSEDED (never read by the suite, documented not deleted).
- Discharged 08-CONTEXT D-10 (canonical-source provenance) — the reproducibility prerequisite that unblocks 08-02 (comparison) and 08-03 (scorecard) determinism claims.

## Task Commits

Each task was committed atomically:

1. **Task 1: Commit the canonical artemis source (results_artemis_gpt54/)** - `ec14244` (feat) — 25 files, 23426 insertions
2. **Task 2: Write reports/ARTEMIS_PROVENANCE.md (authoritative-source ledger)** - `9fc5da8` (docs) — 1 file, 68 insertions

_Plan-metadata commit (this SUMMARY) is made separately; STATE.md/ROADMAP.md are owned by the orchestrator (manual mode)._

## Files Created/Modified
- `results_artemis_gpt54/` - Canonical ARTEMIS_LOCAL source; 25 CSVs across 5 projects (each `<proj>/sad-code/{sadSamTlr,sadCodeTlr,samCodeTlr}_<proj>.csv` + `sad-sam/` + `sam-code/`). `_artemis_model` reads `sad-code/sadSamTlr_<proj>.csv`. Pure VC pin — no content changed.
- `reports/ARTEMIS_PROVENANCE.md` - Authoritative-source ledger (canonical vs external vs secondary/superseded), consistent with `component_suite.py` constants and `COMPONENT_SUITE.md` skip-with-notice narrative.

## Decisions Made
- None beyond the plan — followed D-10 (pin canonical) and D-08 (skip-with-notice for external doc-code) as specified. The ledger paths were transcribed directly from the verified `component_suite.py` constants (`ARTEMIS_LOCAL`, `ARTEMIS_DOC_CODE`, `_artemis_model`, `_artemis_code`).

## Deviations from Plan

None - plan executed exactly as written. No source code changed; no new dependencies; both verify sentinels passed on first run.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The artemis input is now pinned under version control with a written provenance ledger — 08-02 (multi-system comparison) and 08-03 (fitness scorecard) can now assert deterministic regeneration of the present-system (artemis) rows.
- Secondary dirs (`reports_artemis_gpt54_20260605_030524/`, `paper-result/`) and `reports/RESULTS_INDEX.md` remain UNTRACKED by design (documented-secondary, not vendored).
- The external `ARTEMIS_DOC_CODE` doc-code root stays unvendored (present today; skip-with-notice if ever absent).

## Self-Check: PASSED
- FOUND: results_artemis_gpt54/ (25 files tracked via git ls-files)
- FOUND: reports/ARTEMIS_PROVENANCE.md
- FOUND: commit ec14244 (Task 1)
- FOUND: commit 9fc5da8 (Task 2)
- Task 1 <verify>: ARTEMIS_LOCAL_PINNED
- Task 2 <verify>: PROVENANCE_LEDGER_OK

---
*Phase: 08-multi-system-comparison-fitness-validation*
*Completed: 2026-06-21*
