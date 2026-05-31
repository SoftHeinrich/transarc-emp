---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Metrics Toolkit & Converged-Metric Motivation
status: milestone_archived
stopped_at: v1.1 shipped & archived (tag v1.1)
last_updated: "2026-05-31T00:00:00.000Z"
last_activity: 2026-05-31 -- v1.1 milestone archived; ready for next milestone
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 4
  completed_plans: 4
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-31)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** v1.1 shipped & archived — define the next milestone with `/gsd-new-milestone`

## Current Position

Milestone: v1.1 — shipped & archived (tag `v1.1`)
Phase: — (no active phase)
Plan: —
Status: Milestone archived — awaiting next milestone (`/gsd-new-milestone`)
Last activity: 2026-05-31

Progress: [██████████] 100% (3/3 phases, 4/4 plans)

## Performance Metrics

**Velocity (v1.1):**

- Total plans completed: 4
- Average duration: ~9 min/plan

**By Phase:**

| Phase | Plans | Tasks | Files | Duration |
|-------|-------|-------|-------|----------|
| 04 Metrics API | 1 | 3 | 5 | ~15 min |
| 05 Consequences & Converged | 2 | 4 | 6 | ~14 min |
| 06 Handoff Docs | 1 | 2 | 1 | ~8 min |

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

None — all v1.1 concerns resolved (metrics API reused `new_metrics_analysis.py`/`src/bias` with no leakage; Phase 5 consumed the Phase-4 CSVs as evidence). Remaining non-blocking debt tracked under Deferred Items.

## Quick Tasks Completed

| Date | Slug | Result |
|------|------|--------|
| 2026-05-31 | sadsam-metrics-comparator | Holistic s_linker11 / s_linker13f / TransArc comparison for **both** SAD-SAM and SAD-CODE, reusing the canonical suite. Refactored `metrics_api.compute_sad_sam_metrics(proj, res)` and `compute_sad_code_metrics(proj, res)` out of the `*_row` fns. New `src/transarc/sadsam_comparison.py` → `reports/SADSAM_COMPARISON.md`(+CSV); `src/transarc/sadcode_comparison.py` → `reports/SADCODE_COMPARISON.md`(+CSV). s11/s13f SAD-CODE composed (SAD-SAM × ARCOTL SAM-CODE, like s12c). Avg SAD-SAM Link F1: TransArc 0.799 / s11 0.937 / s13f 0.951. Avg SAD-CODE File F1: 0.803 / 0.902 / 0.931. Both linkers beat TransArc on every metric; s13f best. SAD-SAM levels collapse to Link F1 (no enrollment); SAD-CODE levels diverge (enrollment). |

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Cleanup | Rename `src/lib/transarc_error_analysis.py` → `data_loaders.py` | Future | v1.1 roadmap |
| Paper | Real `pdflatex` PDF build of `eval.tex` | Future | v1.1 roadmap |
| Metrics | Extend metrics API to sam-code | Future | v1.1 roadmap |
| Metrics | True `.xlsx` workbook output (needs openpyxl) | Future | v1.1 roadmap |
| Metrics | NDG column non-deterministic in 2nd-3rd decimal (compute_random_f1 set-iteration order in src/lib/new_metrics_analysis.py) — reused verbatim, fix at source | Future | 04-01 exec |

## Session Continuity

Last session: 2026-05-31
Stopped at: v1.1 milestone shipped, audited (PASSED 11/11), completed & archived; phases moved to `milestones/v1.1-phases/`; tag `v1.1` created (not pushed)
Resume file: None

**Milestone v1.1 DONE & ARCHIVED.** audit ✅ → complete ✅ → cleanup ✅. Next: `/gsd-new-milestone` (REQUIREMENTS.md git-rm'd, fresh for next cycle). Optional: `git push origin v1.1`.
