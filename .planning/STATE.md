---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Component-Centric Metric Suite
status: milestone_complete
stopped_at: v1.2 milestone COMPLETE — audited (passed 6/6), shipped, phases archived to milestones/v1.2-phases/, lifecycle done. Branch pushed to origin.
last_updated: "2026-06-22T00:00:00.000Z"
last_activity: 2026-06-22 -- Phase 09 complete (CMP-05 paper integration, verification passed)
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 7
  completed_plans: 7
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Both retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.
**Current focus:** v1.2 Component-Centric Metric Suite — defined; foundation delivered this session. Next: `/gsd-discuss-phase 7` → `/gsd-plan-phase 7`.

## Current Position

Milestone: v1.2 — Component-Centric Metric Suite (defined 2026-06-21)
Phase: 9 — Paper Integration ✓ COMPLETE + VERIFIED (2026-06-22); Phases 7-8 ✓ COMPLETE
Plan: 09-01 complete (1/1); verification passed (3/3 SC)
Status: v1.2 milestone COMPLETE & SHIPPED (audit passed 6/6; phases archived; lifecycle done)
Last activity: 2026-06-22 -- v1.2 lifecycle: audit passed → shipped → cleanup (phases 7-9 archived)

Progress: [██████████] 100% (3/3 phases) — Phases 7-9 complete; all CMP-01…CMP-06 delivered

### Phase 9 deliverables (committed feat(09) 7111505 / docs(09) completion)

- **09-01 (CMP-05):** New `eval.tex` Ch2 §`sec:eval:component-suite` ("A Level-Agnostic
  Component Suite and the Long-Tail Discriminator") — suite-as-one-object (both
  granularities), universe-reconciliation correction (aggregation second-order;
  gap −0.099→−0.019 avg, headline component F1 0.714→0.795), tail-coverage discriminator
  (artemis competitive on micro but last on min_comp 0.279/0.345, abandons real gold
  components), fitness-scorecard verdict. Cites only retained scripts/reports.
- Two generated tables via `src/paper/generate_tables.py`: `tab:component-suite`
  (3 systems × 2 levels) + `tab:metric-fitness` (pooled verdict); byte-identical regen.
- New stdlib `src/paper/check_eval_structure.py` (SC3 gate; exit 0 — 69 labels/47 refs/
  15 inputs resolve) in place of pdflatex.
- **STATE open-item #1 RESOLVED:** the `sentence_f1` gold-negative-FP bug was already
  fixed in `b9a18f4` (2026-06-03); teammates SAD-SAM Sentence F1 0.703 / avg 0.825
  confirmed trustworthy (empirically reproduced; 40.9% pure-FP). Stale `eval.tex:417`
  prose re-anchored Teammates 0.916 → BigBlueButton 0.876 (matches metrics_sad-sam.csv).
- **Verification:** `09-VERIFICATION.md` — status PASSED, 3/3 SC; every numeric claim
  cross-checked against the committed CSVs; upstream metric scripts untouched.

### Phase 8 deliverables (committed ec14244+9fc5da8+69a7aab / 229c843 / e998aea+f9d140b+e8748b9)

- **08-01 (CMP-03 prereq):** Pinned the canonical artemis source `results_artemis_gpt54/` under
  version control (25 files, all 5 `sad-code/sadSamTlr_<proj>.csv` — the `ARTEMIS_LOCAL` path
  `component_suite._artemis_model` reads). `reports/ARTEMIS_PROVENANCE.md` names it canonical,
  keeps `ARTEMIS_DOC_CODE` external/unvendored, marks `reports_artemis_gpt54_*` + `paper-result/`
  documented-secondary (non-destructive, still on disk). Resolves D-10.
- **08-02 (CMP-03):** `reports/COMPONENT_SUITE_{sad-model,sad-code}.csv` regenerate deterministically
  over all 3 present systems × 2 levels (byte-identical 2nd run; clean diff vs Phase-7 committed —
  now reproducible because artemis is pinned). `reports/COMPONENT_SUITE.md` hardened: skip-with-notice
  policy (real `WARNING:` + the 3 guarded roots), swattr≡transarc note (D-12), provenance xref.
  Graceful-skip demonstrated (ARTEMIS_LOCAL→nonexistent emits the WARNING, present rows still returned).
- **08-03 (CMP-04):** NEW `src/bias/metric_fitness.py` — scores micro/macro/gap/min_comp/pct_missed on
  four axes (separation/validity/stability/degeneracy) × 2 levels vs the rq2 trivial floor (Random/Top-3,
  reused as-is — no new baselines) + oracle anchors → `reports/METRIC_FITNESS.{md,csv}`. **Data-derived
  verdict:** headline = micro/macro/min_comp; diagnostic = gap/pct_missed — honestly flags that `micro`
  ranks headline (micro/macro diverge only ~0.092 on separation; second-order, per the Phase-7
  reconciliation) rather than restating the expected "headline=macro+tail". SC4 artemis long-tail
  abandonment quantified (sad-code min_comp 0.3455 / pct_missed 0.0533; sad-model 0.2788 / 0.0832;
  min_comp=0 on bbb+jabref both levels, teammates sad-model) — matches the committed CSVs.
  Determinism hardened beyond the deferred NDG item: cross-`PYTHONHASHSEED` byte-identical (sorted
  sequences + key-sorted map; library modules unedited).
- **Verification:** `08-VERIFICATION.md` — status PASSED, 4/4 SC, all invariants green (stdlib-only;
  no new F1 math; non-destructive; `component_suite.py` + `rq2_trivial_baselines.py` unedited; Phase-7
  equivalence/determinism oracle still passes — no regression). One documented override: ROADMAP's
  literal "≥1 cleverer baseline" reinterpreted to the 3 real paper systems per locked D-01/D-02/D-03.

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
| 2026-06-25 | rq12-bigtable-csv | New `mini-src/rq12.py` (stdlib, imports `metrics.py`; no new metric math) sweeps the 4-system roster, macro-averages 5 projects, means the approach over 3 runs, and emits `reports/RQ12_BIGTABLE.csv` (every RQ1/RQ2 cell) + `reports/RQ2_PANEL.csv` (size-aware panel for **both** approach backends — GPT-5.4 and Claude/sonnet — deltas vs Artemis, and an `OUTDATED` row carrying the paper's stale .62/.71). RQ1 reproduces the paper exactly (3 dp); RQ2 SOTA tail (TransArc .54/.67/.75, Artemis .35/.47/.71) reproduces. Paper RQ2 approach .62/.71 marked OUTDATED (source run `v2.6.5_s20union_gpt_re_medium` + `/tmp/v265.py` deleted); live reproducible values GPT-5.4 .59/.78, Claude .69/.82 (file-F1 .875/.906). `check.py` PASS. See `.planning/quick/20260625-rq12-bigtable-csv/SUMMARY.md`. |

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Cleanup | Rename `src/lib/transarc_error_analysis.py` → `data_loaders.py` | Future | v1.1 roadmap |
| Paper | Real `pdflatex` PDF build of `eval.tex` | Future | v1.1 roadmap |
| Metrics | Extend metrics API to sam-code | Future | v1.1 roadmap |
| Metrics | True `.xlsx` workbook output (needs openpyxl) | Future | v1.1 roadmap |
| Metrics | NDG column non-deterministic in 2nd-3rd decimal (compute_random_f1 set-iteration order in src/lib/new_metrics_analysis.py) — reused verbatim, fix at source | Future | 04-01 exec |

## Session Continuity

Last session: 2026-06-22
Stopped at: Phase 9 complete + verified (1/1 plan, 3/3 SC PASS). ALL v1.2 phases done; running milestone lifecycle (audit → complete → cleanup).
Resume file: .planning/phases/09-paper-integration/09-VERIFICATION.md

**Phase 8 complete.** Executed manually (no gsd-sdk on PATH) sequentially on the main
working tree — worktree isolation deliberately disabled because of the environment's git
auto-commit/force-sync daemon. 3 plans (08-01 artemis pin / 08-02 suite hardening /
08-03 metric-fitness scorecard), each spot-checked, then gsd-verifier PASSED (4/4 SC).
CMP-03 + CMP-04 delivered. See "Phase 8 deliverables" above + 08-VERIFICATION.md.
Next: `/gsd-plan-phase 9` (CMP-05 paper integration).

**Phase 7 complete.** Planned (3 plans, plan-check PASS after 1 revision), executed
sequentially (manual mode — no gsd-sdk), and verified (gsd-verifier, status passed;
SC1–SC4 all PASS). Commits: 07-01 `e2f93c5`, 07-02 `55202a9`, 07-03 `70287e0`.

OPEN ITEMS:

1. **SAD-SAM Sentence F1 review — RESOLVED (2026-06-22, Phase 9 pre-work).** The
   `sentence_f1` gold-negative-FP bug was already fixed in `b9a18f4` (2026-06-03), before
   Phase 7; teammates 0.916→0.703 (avg 0.875→0.825) is the *corrected* standard-IR value,
   not a stale artifact. Empirically reproduced (27/66 = 40.9% teammates pure-FP; canonical
   `compute_sad_sam_metrics` matches 0.703/0.825; CSV + `metrics_sad-sam.tex` consistent).
   The one stale consequence — `eval.tex:417` prose on the buggy 0.916 — was re-anchored to
   BigBlueButton (0.876 vs link 0.793) in Phase 9. Trustworthy & paper-ready.

2. **Branch — DECIDED (2026-06-22):** stay on `gsd/mini-data-inequality` (carries all v1.2
   work). Branch/PR hygiene to be handled at ship time. Branch pushed to origin.

3. **`eval.tex` prose — DONE (Phase 9).** The new §`sec:eval:component-suite` folds in
   `reports/COMPONENT_SUITE.md`, `reports/METRIC_FITNESS.md` (data-derived verdict), and the
   universe-reconciliation correction; `reports/ARTEMIS_PROVENANCE.md` underpins the pinned
   artemis source. Stale Sentence-F1 example corrected (item #1).
4. **Phase 8 provenance (D-10): RESOLVED.** `results_artemis_gpt54/` pinned + committed (08-01);
   `reports/ARTEMIS_PROVENANCE.md` is the authoritative-source ledger. `reports_artemis_gpt54_*/`
   and `paper-result/` intentionally remain untracked (documented-secondary, non-destructive).
5. **Phase 9 wording (from 08-VERIFICATION):** the 08-03 SUMMARY's "micro ≈ macro second-order"
   prose is looser than the committed `reports/METRIC_FITNESS.md` (which correctly states micro/macro
   diverge ~0.092 on separation). Cite the ARTIFACT's wording in the paper, not the SUMMARY's.
