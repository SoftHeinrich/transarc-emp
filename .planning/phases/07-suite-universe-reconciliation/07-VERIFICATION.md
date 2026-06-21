---
phase: 07-suite-universe-reconciliation
verified: 2026-06-21T00:00:00Z
status: passed
score: 4/4 success criteria verified (CMP-01/02/06 all satisfied)
mode: goal-backward (manual; gsd-sdk not invoked)
re_verification: false
success_criteria:
  - id: SC1
    text: "component_suite.py emits per-project + AVG CSV for sad-model and sad-code, reusing calc_metrics only"
    status: PASS
  - id: SC2
    text: "micro and macro on the same mapped-only universe; oracle asserts suite-macro == per_component_macro_f1"
    status: PASS
  - id: SC3
    text: "divergence from metrics_api headline component_f1 reconciled OR documented with the delta recorded"
    status: PASS
  - id: SC4
    text: "re-running the tool regenerates the committed CSVs deterministically"
    status: PASS
requirements:
  CMP-01: satisfied
  CMP-02: satisfied
  CMP-06: satisfied
concerns:
  - severity: warning
    item: "07-02 incidentally refreshed SAD-SAM (Pillar-1) numbers — consequences.tex Sentence F1 AVG 0.875->0.825 — to unblock generate_tables.py (em-dash placeholder crash). Acceptable in-scope blocking fix; flag for confirmation before Phase 9 paper integration since it touches the TransArc-study chapter, not the bias chapter under test."
  - severity: info
    item: "Pre-existing NDG non-determinism in reports/SADCODE_S11_S13F_VS_TRANSARC.csv (only *_ndg columns; RNG in compute_random_f1). component_f1 columns are deterministic; explicitly deferred (reconciliation §5). Not a CMP-02 concern."
  - severity: info
    item: "writing/eval.tex still cites old component numbers (0.648/0.574/0.880/0.714) — deliberately deferred to Phase 9 (CMP-05); confirmed untouched since Phase 5 commit."
---

# Phase 7: Suite & Universe Reconciliation — Verification Report

**Phase Goal:** The component suite is a finalized, tested, stdlib tool whose micro
and macro share one component universe, with the relationship to the existing
`metrics_api` headline `component_f1` resolved (reconciled or documented with the
numeric delta).

**Verified:** 2026-06-21 (manual mode — every check re-run independently; SUMMARY claims not trusted)
**Status:** passed
**Re-verification:** No — initial verification.

## Goal Achievement

The phase goal is **achieved**. All four ROADMAP success criteria were independently
re-run and pass. The suite is finalized and stdlib-only; micro and macro are computed
on one shared mapped-only universe; the `metrics_api` headline `component_f1` is both
*reconciled* (the `{b}` fallback was dropped so it equals suite-`micro` by construction)
*and* documented with the numeric delta; and the committed CSVs regenerate byte-identically.

### Success Criteria

| #   | Criterion | Status | Evidence |
| --- | --------- | ------ | -------- |
| SC1 | `python3 src/bias/component_suite.py [--level --project]` emits per-project + AVG CSV for `sad-model` and `sad-code`, reusing `calc_metrics` only | ✓ PASS | Ran with no args → exit 0; wrote `COMPONENT_SUITE_sad-code.csv` and `COMPONENT_SUITE_sad-model.csv`, each 15 data rows (5 projects × 3 systems) + 3 AVG rows. `--help` lists `--level`/`--project`. Imports are stdlib-only (`argparse, csv, sys, collections, pathlib`) + `transarc_error_analysis`. The only per-component F1 path is `_comp_score()` which delegates to `calc_metrics` — no new F1/precision/recall helper in the file. |
| SC2 | micro and macro on the same mapped-only universe; equivalence oracle asserts suite-macro == `per_component_macro_f1` | ✓ PASS | In `component_suite()`, both `micro` (pooled) and `macro` (per-component mean over `set(gold_by_c) \| set(res_by_c)`) derive from the same mapped-only collapsed (sentence, component) sets (`_code_inputs`/`_model_inputs` drop files with no SAM-CODE component). `check_component_suite.py` ran → exit 0; oracle binds `component_suite(...)['macro']` to `rq2_trivial_baselines.per_component_macro_f1` at sad-code across all 5 projects × 3 present systems = 15 cells, **every `|delta| = 0.00e+00`** at `TOL=1e-9`. |
| SC3 | Divergence from `metrics_api` headline `component_f1` (~0.795 vs old 0.714) reconciled in `metrics_api` OR documented with the delta recorded in `reports/` | ✓ PASS (reconciled **and** documented) | `{b}` singleton fallback removed from `_compute_component_f1` (`src/bias/evaluation_critique.py:631`) and mirror `to_comp` (`mini-src/metrics.py:264`); `grep "if not comps"` returns nothing. `reports/metrics_sad-code.csv` AVG `component_f1` = **0.795** and equals `COMPONENT_SUITE_sad-code.csv` swattr/transarc AVG `micro` (0.7949), matching per-project (0.642/0.828/0.716/0.832/0.957 ≡ 0.6415/0.8283/0.7158/0.8322/0.9565). `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` records the apples-to-apples delta **0.714 → 0.795** (matches ROADMAP), headline 0.732 → 0.795, per-project deltas, and a full supersession ledger. `mini-src/check.py` → exit 0 (mini == metrics_api on all component_f1 cells after the drop). |
| SC4 | Re-running the tool regenerates the committed CSVs deterministically | ✓ PASS | Ran `component_suite.py` twice: md5 of both CSVs identical across runs **and** byte-identical to the committed files (`git diff --stat` empty after both runs). `check_component_suite.py` PART 2 regenerates both levels into a temp dir and diffs the committed CSVs for present-system rows → 36/36 OK, 0 FAIL, `reports/` untouched. |

**Score:** 4/4 success criteria verified.

### Requirements Coverage

| Requirement | Source Plan | Verdict | Evidence |
| ----------- | ----------- | ------- | -------- |
| CMP-01 — Level-agnostic component suite tool | 07-01 | ✓ SATISFIED | `component_suite.py` computes `{micro, macro, gap, min_comp, pct_missed, gold_gini}` at both levels, `calc_metrics` is the sole F1 primitive, micro/macro on one shared mapped-only universe, tail (`min_comp`/`pct_missed`) gold-only, full per-project + AVG CSV emitted. Artemis long-tail finding holds: artemis has the worst `min_comp` AVG at both levels (0.3455 sad-code, 0.2788 sad-model) and highest `pct_missed`, re-confirmed in `COMPONENT_SUITE.md`. stdlib-only; no debt markers. |
| CMP-02 — Reconciled component universe | 07-02 | ✓ SATISFIED | micro/macro on same mapped-only universe (gap reflects aggregation alone); `{b}` fallback dropped in `metrics_api` so headline `component_f1` == suite `micro` by construction (asserted 1e-6 / mini 1e-9); numeric delta recorded in `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`. Reconciled, not merely documented. |
| CMP-06 — Reproducibility & equivalence oracle | 07-03 | ✓ SATISFIED | Standalone `src/bias/check_component_suite.py` — single command, exit 0 = both guarantees. Oracle (suite-macro == `per_component_macro_f1`, 1e-9, 15 cells, delta 0.0) + determinism gate (temp-only regen, committed CSVs byte-identical, `reports/` untouched). stdlib-only, no new F1 math. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `src/bias/component_suite.py` | shared-universe micro/macro, gold-only tail, argparse CLI, calc_metrics only | ✓ VERIFIED | `_comp_score` delegates to `calc_metrics`; `per_comp` over gold∪result (macro/gap), `per_comp_gold` over gold-only (min_comp/pct_missed); `--level`/`--project` CLI; committed & clean. |
| `reports/COMPONENT_SUITE_sad-code.csv` | 5 projects × 3 systems + AVG | ✓ VERIFIED | 15 data + 3 AVG rows; header `project,system,micro,macro,gap,min_comp,pct_missed,gold_gini`; regenerates byte-identical. |
| `reports/COMPONENT_SUITE_sad-model.csv` | 5 projects × 3 systems + AVG | ✓ VERIFIED | Same shape; regenerates byte-identical. |
| `reports/COMPONENT_SUITE.md` | gold-coverage framing + re-confirmed artemis tail | ✓ VERIFIED | "gold coverage of REAL components" framing present; artemis worst `min_comp` at both levels stated with numbers matching the CSV. |
| `src/bias/evaluation_critique.py` | `{b}` fallback removed | ✓ VERIFIED | `_compute_component_f1` mapped-only; no `if not comps` branch. |
| `mini-src/metrics.py` | `{b}` fallback removed, check stays green | ✓ VERIFIED | `to_comp` mapped-only; `mini-src/check.py` exit 0. |
| `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` | old→new delta + supersession ledger | ✓ VERIFIED | Records 0.714→0.795, 0.732→0.795, per-project deltas, full ledger (REGENERATED / SUPERSEDED(banner) / ledger-only / coincidental / Phase-9-deferred). |
| `src/bias/check_component_suite.py` | equivalence oracle + determinism check | ✓ VERIFIED | Exit 0; 15 oracle OK (delta 0.0), 36 determinism OK; stdlib-only. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `component_suite.component_suite()` | per-component F1 | `_comp_score` → `calc_metrics` | ✓ WIRED | No new F1 math; sole primitive is `calc_metrics`. |
| `component_suite` tail | gold-only universe | `per_comp_gold` over `set(gold_by_c)` | ✓ WIRED | `min_comp`/`pct_missed` derived from gold-only list. |
| `check_component_suite` | `rq2_trivial_baselines.per_component_macro_f1` | imported + asserted 1e-9 | ✓ WIRED | Function exists (`rq2_trivial_baselines.py:57`); delta 0.0 on all cells. |
| `metrics_api` headline `component_f1` | suite `micro` | mapped-only definition shared | ✓ WIRED | metrics_sad-code.csv AVG 0.795 ≡ suite swattr/transarc micro AVG 0.7949 (per-project too). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Suite runs both levels, writes CSVs | `python3 src/bias/component_suite.py` | exit 0; 2 CSVs, 15+3 rows each | ✓ PASS |
| Determinism (cross-run + vs committed) | run twice + `md5sum` + `git diff --stat` | md5 identical, diff empty | ✓ PASS |
| Oracle + determinism gate | `python3 src/bias/check_component_suite.py` | exit 0; 15 oracle OK (|delta|=0.0), 36 det OK | ✓ PASS |
| mini == metrics_api after `{b}` drop | `python3 mini-src/check.py` | exit 0; all panel cells OK | ✓ PASS |
| Reconciliation: headline == suite micro | inspect `metrics_sad-code.csv` AVG vs suite AVG | 0.795 == 0.7949 (per-project match) | ✓ PASS |

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| (none) | TODO/FIXME/XXX/HACK/TBD/placeholder scan of all 4 phase-7 source files | — | None found (the one `footgun` reference is intentional `--project` help text, not a debt marker). |

## SAD-SAM Side-Effect Assessment

**Verdict: acceptable in-scope blocking fix — flag for confirmation before Phase 9 (WARNING, non-blocking).**

The committed `reports/metrics_sad-sam.csv` was a stale em-dash placeholder
(`Average` row only) that crashed `src/paper/generate_tables.py`
(`ValueError: could not convert string to float: '—'`) in
`t_converged_framework`/`t_consequences`. The 07-02 plan's own Task-2 verify
requires `generate_tables.py` to exit 0, which is impossible against an empty
SAD-SAM CSV. 07-02 repopulated it via its own generator
(`python3 src/lib/metrics_api.py --task sad-sam`) — generator-based regeneration,
non-destructive, consistent with CLAUDE.md ("keep reports consistent with the
script that produces them") and the D-02 single-source-of-truth principle.

Why this does not threaten the Phase 7 goal:
- SAD-SAM `component_f1` collapses onto link F1 and is **unchanged** by the D-01
  definition edit — confirmed in `reconciliation §4` and by the fact that the
  agent-linker SAD-SAM panels (no `component_f1` column at all) also shifted,
  proving the movement is a stale-result re-alignment, not a CMP-02 effect.
- The change is fully traceable in the supersession ledger / reconciliation §4.

Why it warrants a follow-up flag (not a Phase 7 blocker):
- The refresh moved Pillar-1 SAD-SAM numbers that feed `writing/tables/consequences.tex`
  (SAD-SAM Sentence F1 AVG 0.875 → 0.825; the brief notes a teammates Sentence F1
  shift on the order of 0.916 → 0.703). Those numbers live in the **TransArc-study
  chapter (Ch1 / Pillar 1)**, which is *not* the subject of this milestone (Pillar 2
  / bias). Before Phase 9 paper integration, a human should confirm the refreshed
  SAD-SAM values are the intended current bundled-result numbers and not a silent
  regression in a Pillar-1 table.

This is recorded as a `warning` concern in the frontmatter — it does not reduce the
phase score.

## Concerns

1. **(WARNING)** SAD-SAM Pillar-1 refresh side effect — see assessment above. Confirm
   before Phase 9.
2. **(INFO)** Pre-existing NDG non-determinism in
   `reports/SADCODE_S11_S13F_VS_TRANSARC.csv` (only `*_ndg` columns wiggle via RNG in
   `compute_random_f1`). All `component_f1` columns — the CMP-02 concern — are
   deterministic. Explicitly deferred (reconciliation §5); not in Phase 7 scope.
3. **(INFO)** `writing/eval.tex` still cites old component numbers
   (0.648/0.574/0.880/0.714). Confirmed untouched since the Phase 5 commit — this is
   the deliberate Phase-9 (CMP-05) deferral, correctly flagged in the reconciliation
   ledger. Appropriate for this phase.

## Gaps Summary

No gaps. All four success criteria pass with independently re-run evidence, all three
requirements (CMP-01/02/06) are satisfied, all artifacts exist, are substantive, are
wired, and the data flows (numeric equalities verified). The non-destructive rule is
honored (4 superseded reports carry the `superseded by mapped-only universe (v1.2)`
banner; ledger accounts for the rest; `eval.tex` deferred to Phase 9). Phase work is
committed across 3 commits (`e2f93c5`, `55202a9`, `70287e0`) with a clean working tree.

The single WARNING (SAD-SAM Pillar-1 refresh) is an advisory follow-up for Phase 9, not
a blocker for the Phase 7 goal.

---

_Verified: 2026-06-21_
_Verifier: Claude (gsd-verifier, manual mode)_
