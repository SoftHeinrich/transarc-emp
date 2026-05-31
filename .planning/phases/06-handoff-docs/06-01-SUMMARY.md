---
phase: 06-handoff-docs
plan: 01
subsystem: docs
tags: [readme, handoff, reproducibility, two-pillar, markdown]

# Dependency graph
requires:
  - phase: 04-metrics-api
    provides: "metrics_api.py CLI (--task sad-sam|sad-code -> reports/metrics_*.csv + writing/tables/metrics_*.tex)"
  - phase: 05-consequences-study
    provides: "consequences_study.py reading metrics_*.csv -> reports/CONSEQUENCES_STUDY.md"
provides:
  - "Top-level README.md mapping the two pillars (DOC-01)"
  - "Per-pillar reproduce sections with verified script->output commands (DOC-02)"
  - "Documented prerequisites: Python 3 stdlib-only, external benchmark path, pdflatex limitation"
affects: [milestone-handoff, future-onboarding]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Handoff README: pillar-map table + per-pillar reproduce tables linking commands to verified outputs"]

key-files:
  created: [README.md]
  modified: []

key-decisions:
  - "Listed transarc_error_analysis.py under src/lib/ (its real location) while presenting it as the Pillar 1 study entrypoint"
  - "Documented enrollment_distortion_analysis.py as a supporting/intermediate (stdout-only) script rather than omitting it"
  - "Ordered Pillar 2 reproduce: standalone scripts -> metrics_api -> consequences_study, so the CSV dependency is satisfied"

patterns-established:
  - "Reproduce tables map each command verbatim to its OUTPUT_MD/OUTPUT_CSV path (single source of truth = verified script->output map)"

requirements-completed: [DOC-01, DOC-02]

# Metrics
duration: 8min
completed: 2026-05-31
---

# Phase 6 Plan 01: Handoff Docs Summary

**Top-level README.md mapping the TransArc-EMP two pillars (empirical study + benchmark bias) with verified per-pillar reproduce commands, prerequisites, and CLAUDE.md links.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-31T01:51:00Z
- **Completed:** 2026-05-31T01:59:20Z
- **Tasks:** 2
- **Files modified:** 1 (README.md created)

## Accomplishments

- Created `README.md` (94 lines) at the repo root with a `## Two Pillars` map table (Pillar | Code dirs | Key scripts | Output reports | Paper chapter) satisfying DOC-01.
- Added `## Pillar 1 — Reproduce` and `## Pillar 2 — Reproduce` sections with each command mapped verbatim to its verified output, satisfying DOC-02; Pillar 2 ordered so `metrics_api.py` runs before `consequences_study.py` (CSV dependency).
- Documented prerequisites (Python 3 stdlib-only, external benchmark path, pdflatex-unavailable limitation) and linked to `[CLAUDE.md](CLAUDE.md)` + `[../CLAUDE.md](../CLAUDE.md)` without duplicating their content.
- Spot-validated one representative command per pillar (Task 2): both run clean and produce their named outputs; the documented commands match exactly, so no README correction was needed.

## Task Commits

1. **Task 1: Write top-level README.md (pillar map + per-pillar reproduce sections)** - `181a4de` (docs)
2. **Task 2: Spot-validate one representative reproduce command per pillar** - no new commit (validation only; README confirmed accurate, no edit needed)

**Plan metadata:** (final docs commit — SUMMARY/STATE/ROADMAP)

## Files Created/Modified

- `README.md` - Top-level handoff README: intro, prerequisites, two-pillar map table, Pillar 1 + Pillar 2 reproduce tables, Paper section.

## Decisions Made

- `transarc_error_analysis.py` documented at its real path `src/lib/` while framed as the Pillar 1 study entrypoint (matches verified map; deferred rename to `data_loaders.py` not assumed).
- `enrollment_distortion_analysis.py` listed as a supporting/intermediate stdout-only script (Claude's discretion per CONTEXT) rather than omitted.
- Pillar 2 reproduce order enforces the metrics_api -> consequences_study dependency.

## Deviations from Plan

None - plan executed exactly as written. The script->output map matched live behavior; all scripts confirmed via reads before documenting.

## Spot-Validation Detail (Task 2)

- **Pillar 2 representative:** `python3 src/lib/metrics_api.py --task sad-sam` exited 0 and produced `reports/metrics_sad-sam.csv` + `writing/tables/metrics_sad-sam.tex` (regenerated identically — no diff).
- **Pillar 1 representative:** `python3 src/transarc/s12c_sadcode_comparison.py` exited 0 and produced `reports/S12C_VS_TRANSARC.csv`.
- The S12C CSV regeneration differed only in the `wt` (weighted) columns at the 1st decimal (e.g. 51.2 -> 51.7), the same set-iteration non-determinism already deferred for `src/lib/new_metrics_analysis.py` (STATE Deferred Items). This is a pre-existing upstream source concern, NOT a Task-2 deliverable. The incidental regeneration was reverted (`git checkout -- reports/S12C_VS_TRANSARC.csv`); only README.md was committed as the deliverable.

## Issues Encountered

None. Hostshare git stat-cache refreshed with `git update-index --refresh` before each status check per project memory; no corruption observed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DOC-01 and DOC-02 complete; workspace is handoff-ready with a top-level README.
- This is the final plan of Phase 6 and the v1.1 milestone's last planned phase — milestone completion (`/gsd-complete-milestone`) is the next step.

## Self-Check: PASSED

- FOUND: README.md (repo root)
- FOUND: .planning/phases/06-handoff-docs/06-01-SUMMARY.md
- FOUND: commit 181a4de
- archive/README.md UNCHANGED

---
*Phase: 06-handoff-docs*
*Completed: 2026-05-31*
