# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-30)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** Phase 1 — Reorganize

## Current Position

Phase: 1 of 3 (Reorganize)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-05-30 — Roadmap created

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Scoping]: Keep only TransArc empirical study + benchmark bias as active pillars
- [Scoping]: SWATTR FP filter stays archived (intervention/tool, not a study)
- [Scoping]: s12c comparison moves into Pillar 1 (TransArc study evidence)
- [Scoping]: Proposed-metrics + baselines fold into Pillar 2 (benchmark bias chapter)
- [Paper]: Paper restructures to Ch1=TransArc + Ch2=Bias (merge Distributional + Metrics chapters)

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 1 moves must preserve `sys.path.insert` import paths in all retained scripts — verify during Phase 2.
- `src/lib/new_metrics_analysis.py` role needs clarification: it is listed under Pillar 2 proposed-metrics scope (SCOPE-05) but lives in `src/lib/`; Phase 1 plan should decide whether to move it or leave it in lib.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Documentation | DOC-01: Top-level README (two-pillar map) | v2 deferred | Roadmap creation |
| Documentation | DOC-02: Per-pillar run/reproduce instructions | v2 deferred | Roadmap creation |

## Session Continuity

Last session: 2026-05-30
Stopped at: Roadmap and state files created; no plans written yet
Resume file: None
