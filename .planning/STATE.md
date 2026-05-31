---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Metrics Toolkit & Converged-Metric Motivation
status: milestone_complete
stopped_at: Completed 06-01-PLAN.md
last_updated: "2026-05-31T01:59:59.243Z"
last_activity: 2026-05-31 -- Phase 6 (Handoff Docs) complete; v1.1 milestone done
progress:
  total_phases: 3
  completed_phases: 4
  total_plans: 4
  completed_plans: 4
  percent: 133
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-30)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** Phase 6 (Handoff Docs) complete — v1.1 milestone done

## Current Position

Phase: 06
Plan: Not started
Status: Milestone complete
Last activity: 2026-05-31

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 5
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 04 | 1 | - | - |
| 05 | 2 | - | - |
| 06 | 1 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 04 P01 | 15 | 3 tasks | 5 files |
| Phase 05 P01 | 8 | 2 tasks | 2 files |
| Phase 05 P02 | 6 | 2 tasks | 4 files |
| Phase 06 P01 | 8 | 2 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Scoping]: Stdlib-only preserved — Excel output is CSV, not `.xlsx` (no openpyxl, no requirements.txt)
- [Scoping]: Metrics API ingests the existing TransArc output format from `results/`; reuses `src/lib` + `src/bias`
- [Scoping]: Tasks limited to sad-sam + sad-code this milestone (no sam-code)
- [Scoping]: Consequences study + converged-metrics proposal extend Pillar 2 (benchmark bias)
- [Paper]: No local LaTeX toolchain — Phase 5 validates via table-gen + structural check, not pdflatex
- [04-01] Metrics API reuses existing primitives with zero metric-math reimplementation; sad-sam path never touches evaluation_critique _compute_* helpers (task asymmetry)
- [04-01] MAP is N/A for sad-code (optional there); unified 12-column schema with em-dash N/A cells per task
- render_table gained raw_cols= to emit macro-bearing data cells verbatim (Task column \sadsam/\sadcode) [05-02]
- [06-01] README documents transarc_error_analysis.py at its real src/lib/ path (deferred rename not assumed); enrollment_distortion_analysis.py listed as supporting/stdout-only; Pillar 2 reproduce order enforces metrics_api -> consequences_study CSV dependency

### Pending Todos

None yet.

### Blockers/Concerns

- `src/lib/new_metrics_analysis.py` is the likely home for the proposed alternative metrics the API must reuse (MTR-03) — Phase 4 plan should confirm its API surface before wrapping it.
- Phase 4 must compute the full metric set without any benchmark-derived word lists (CLAUDE.md leakage rule).
- Phase 5 should consume Phase 4 CSV/LaTeX output as evidence where possible to avoid duplicate metric computation.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Cleanup | Rename `src/lib/transarc_error_analysis.py` → `data_loaders.py` | Future | v1.1 roadmap |
| Paper | Real `pdflatex` PDF build of `eval.tex` | Future | v1.1 roadmap |
| Metrics | Extend metrics API to sam-code | Future | v1.1 roadmap |
| Metrics | True `.xlsx` workbook output (needs openpyxl) | Future | v1.1 roadmap |
| Metrics | NDG column non-deterministic in 2nd-3rd decimal (compute_random_f1 set-iteration order in src/lib/new_metrics_analysis.py) — reused verbatim, fix at source | Future | 04-01 exec |

## Session Continuity

Last session: 2026-05-31T01:59:20Z
Stopped at: Completed 06-01-PLAN.md
Resume file: None

**Milestone v1.1 complete:** all 3 phases (4 plans) done — next: `/gsd-complete-milestone`
