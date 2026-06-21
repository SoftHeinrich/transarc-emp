---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Component-Centric Metric Suite
status: Phase 7 planned (3 plans, plan-check passed). Next `/gsd-execute-phase 7`.
stopped_at: Phase 7 planned — 07-01 (CMP-01), 07-02 (CMP-02), 07-03 (CMP-06); plan-check PASS after 1 revision
last_updated: "2026-06-21T15:20:17.000Z"
last_activity: 2026-06-21 -- Phase 7 plans authored (gsd-planner) + verified (gsd-plan-checker)
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 3
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** v1.2 Component-Centric Metric Suite — defined; foundation delivered this session. Next: `/gsd-discuss-phase 7` → `/gsd-plan-phase 7`.

## Current Position

Milestone: v1.2 — Component-Centric Metric Suite (defined 2026-06-21)
Phase: 7 — Suite & Universe Reconciliation (PLANNED — 3 plans, plan-check passed)
Plan: 07-01 (CMP-01), 07-02 (CMP-02), 07-03 (CMP-06) — wave 1: 07-01 ∥ 07-02; wave 2: 07-03
Status: Phase 7 plans authored + plan-checked (PASS after 1 revision closing the D-03/D-04 regen+banner gap). Plan docs NOT yet committed. Next `/gsd-execute-phase 7`.
Last activity: 2026-06-21

Progress: [░░░░░░░░░░] 0% (0/3 phases) — Phase 7 planned, not yet executed

### v1.2 foundation delivered this session (to be hardened/verified in Phases 7-9)

- `src/bias/component_suite.py` — level-agnostic suite (micro/macro/gap/min_comp/pct_missed/gold_gini), reconciled mapped-only universe, reuses `calc_metrics` only. [CMP-01, CMP-02 partial]
- `reports/COMPONENT_SUITE_{sad-model,sad-code}.csv` + `reports/COMPONENT_SUITE.md` — 3-system, 2-level comparison + universe-reconciliation note. [CMP-03 partial]
- Finding: micro/macro aggregation is second-order once universe-reconciled; tail coverage (min_comp/pct_missed) is the discriminator; artemis abandons the long tail. Memory: `component-suite-finding`.
- Open for Phases 7-9: reconcile/document `metrics_api` headline delta (CMP-02), equivalence oracle (CMP-06), hardened fitness scorecard (CMP-04), paper integration (CMP-05).

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
| 2026-06-02 | 260602-q6u | Code quality + metrics correctness audit. 10 issues found: 3 WARNINGs (NDG n_sentences inconsistency metrics_api vs new_metrics_analysis; latent MCC negative-tn if result has out-of-gold files; sentence_f1 undercounts FPs for gold-negative predicted sentences), 1 WARNING design (ACF1 multi-component weight policy undocumented), 1 INFO (NDG range documented [0,1] but can return negative), 4 INFO/dead-code (unused `comp_sent_count`, `gold_by_sent`, `n_components` param in compute_random_f1). Core math in new_metrics_analysis.py verified CORRECT. Published report numbers unaffected. See `.planning/quick/260602-q6u-*/SUMMARY.md`. |
| 2026-06-02 | 260602-qwd | Investigated 3 WARNINGs from prior audit with concrete data. W1=BUG: metrics_api NDG uses enrolled-sentence count (25–93) not total text (13–198), p inflated 1.3–2.1×, NDG systematically wrong in sadcode_comparison. W2=FALSE ALARM: TransArc result paths confirmed within gold SAM-CODE universe (mediastore verified 0/11 out-of-gold); structural argument holds for all callers. W3=BUG: sentence_f1 silently drops gold-negative FP sentences — teammates has 27/66 result sentences (41%) with no gold entry, precision overstated. Fixes specified in SUMMARY.md. |

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Cleanup | Rename `src/lib/transarc_error_analysis.py` → `data_loaders.py` | Future | v1.1 roadmap |
| Paper | Real `pdflatex` PDF build of `eval.tex` | Future | v1.1 roadmap |
| Metrics | Extend metrics API to sam-code | Future | v1.1 roadmap |
| Metrics | True `.xlsx` workbook output (needs openpyxl) | Future | v1.1 roadmap |
| Metrics | NDG column non-deterministic in 2nd-3rd decimal (compute_random_f1 set-iteration order in src/lib/new_metrics_analysis.py) — reused verbatim, fix at source | Future | 04-01 exec |

## Session Continuity

Last session: 2026-06-21T15:20:17.000Z
Stopped at: Phase 7 planned (3 plans) + plan-check PASS; plan docs uncommitted
Resume file: .planning/phases/07-suite-universe-reconciliation/07-01-PLAN.md

**Phase 7 planned.** 3 plans authored by gsd-planner, verified by gsd-plan-checker
(PASS after 1 revision — closed a D-03/D-04 gap where in-repo `writing/tables/*.tex`
and secondary reports kept the superseded `component_f1` 0.714/0.732 without regen or
banner). Plans: 07-01 (CMP-01 suite finalize), 07-02 (CMP-02 metrics_api mapped-only
reconciliation + artifact regen/banner), 07-03 (CMP-06 equivalence oracle + determinism).
Next: `/gsd-execute-phase 7` (wave 1: 07-01 ∥ 07-02; wave 2: 07-03).

NOTE — uncommitted + branch: plan docs (`07-0{1,2,3}-PLAN.md`) and the
`v1.2-ROADMAP.md`/STATE edits are NOT committed. Working branch is
`gsd/mini-data-inequality` (the v1.2 Phase 7 context commit 0b59a9a already lives here,
not on master). Decide commit target before `/gsd-execute-phase 7`.
