---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Component-Centric Metric Suite
status: Phase 8 context gathered (08-CONTEXT.md). Next `/gsd-plan-phase 8`.
stopped_at: Phase 8 discuss complete — 4 areas resolved (no new baselines; real comparators = 3 paper systems; numeric fitness scorecard in new metric_fitness.py; data-derived verdict; skip-with-notice + both levels + swattr≡transarc + pinned artemis provenance)
last_updated: "2026-06-21T21:35:07.000Z"
last_activity: 2026-06-21 -- Phase 8 discuss-phase (context + discussion-log committed 11d6418)
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 33
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** v1.2 Component-Centric Metric Suite — defined; foundation delivered this session. Next: `/gsd-discuss-phase 7` → `/gsd-plan-phase 7`.

## Current Position

Milestone: v1.2 — Component-Centric Metric Suite (defined 2026-06-21)
Phase: 8 — Multi-System Comparison & Fitness Validation ◐ CONTEXT GATHERED (2026-06-21); Phase 7 ✓ COMPLETE
Plan: none yet — 08-CONTEXT.md ready, next `/gsd-plan-phase 8`
Status: Phase 8 discuss complete. Decisions (08-CONTEXT.md): (1) no new synthetic baselines — rq2 Random/Top-3 = trivial floor, real comparators = 3 paper systems only (swattr/transarc, s20linker/s20union, artemis), legacy s11/s13f/s12c excluded; (2) numeric fitness scorecard in NEW src/bias/metric_fitness.py → reports/METRIC_FITNESS.{md,csv} scoring columns on separation/validity/stability/degeneracy; (3) data-derived verdict (don't oversell micro-vs-macro); (4) skip-with-notice + both levels + swattr≡transarc one column + pin results_artemis_gpt54 provenance.
Last activity: 2026-06-21

Progress: [███░░░░░░░] 33% (1/3 phases) — Phase 7 complete; Phase 8 context gathered; Phases 8-9 remain

### Phase 7 deliverables (committed e2f93c5 / 55202a9 / 70287e0)
- `src/bias/component_suite.py` finalized; `reports/COMPONENT_SUITE_{sad-code,sad-model}.csv` regenerated (swattr/transarc AVG micro 0.7949 / macro 0.8134).
- `metrics_api` headline `component_f1` reconciled to mapped-only via dropping the `{b}` fallback (evaluation_critique.py + mini-src/metrics.py); AVG 0.732→0.795; delta + supersession ledger in `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`.
- `src/bias/check_component_suite.py` — equivalence oracle (suite-macro == per_component_macro_f1, all 15 cells |delta|=0) + temp-dir determinism diff (36/36).
- WARNING follow-up: regenerating the stale `metrics_sad-sam.csv` placeholder moved Pillar-1 SAD-SAM Sentence F1 (teammates 0.916→0.703 / avg 0.875→0.825) into `consequences.tex` — human should confirm before Phase 9 (CMP-05). Possibly related to the known sentence_f1 gold-negative-FP bug.

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

Last session: 2026-06-21T21:35:07.000Z
Stopped at: Phase 8 context gathered (discuss-phase complete). Next `/gsd-plan-phase 8`.
Resume file: .planning/phases/08-multi-system-comparison-fitness-validation/08-CONTEXT.md

**Phase 8 discuss complete.** Ran `/gsd-discuss-phase 8` manually (no gsd-sdk).
4 gray areas resolved → 08-CONTEXT.md + 08-DISCUSSION-LOG.md committed `11d6418`.
Locked: no new synthetic baselines (real comparators = 3 paper systems only);
numeric fitness scorecard in NEW `src/bias/metric_fitness.py` → `reports/METRIC_FITNESS.{md,csv}`
(separation/validity/stability/degeneracy); data-derived verdict; skip-with-notice +
both levels + swattr≡transarc + pinned `results_artemis_gpt54` provenance.
Next: `/gsd-plan-phase 8`.

**Phase 7 complete.** Planned (3 plans, plan-check PASS after 1 revision), executed
sequentially (manual mode — no gsd-sdk), and verified (gsd-verifier, status passed;
SC1–SC4 all PASS). Commits: 07-01 `e2f93c5`, 07-02 `55202a9`, 07-03 `70287e0`.

OPEN ITEMS for next session:
1. **SAD-SAM Sentence F1 review (WARNING):** 07-02 refreshed the stale `metrics_sad-sam.csv`
   placeholder, moving teammates Sentence F1 0.916→0.703 (avg 0.875→0.825) into
   `consequences.tex`. Confirm these Pillar-1 numbers (possible link to the known
   `sentence_f1` gold-negative-FP bug) before Phase 9 / any paper use.
2. **Branch:** working branch is `gsd/mini-data-inequality`; all v1.2 Phase 7 work
   (context 0b59a9a + plans + execution) lives here, NOT on master. Decide whether to
   migrate v1.2 to master/a v1.2 branch before continuing.
3. `writing/eval.tex` prose still cites old numbers — deliberate Phase-9 (CMP-05) deferral.
4. **Phase 8 provenance (D-10):** untracked `results_artemis_gpt54/`,
   `reports_artemis_gpt54_*/`, `paper-result/` must be resolved (commit/pin the
   canonical artemis source) before the scorecard's determinism/regen claim can hold.
