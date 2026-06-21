---
phase: 07-suite-universe-reconciliation
plan: 02
subsystem: metrics
tags: [component-f1, mapped-only-universe, metrics_api, reconciliation, latex-tables, stdlib]

# Dependency graph
requires:
  - phase: 07-suite-universe-reconciliation (plan 01, CMP-01)
    provides: finalized component_suite (micro/macro on shared gold∪result mapped-only universe); COMPONENT_SUITE_sad-code.csv micro = 0.7949 swattr/transarc AVG
provides:
  - mapped-only component universe as the single source of truth for headline component_f1 (D-01)
  - metrics_api component_f1 == component_suite micro for swattr/transarc by construction (1e-6)
  - regenerated CSV/MD/LaTeX artifacts (D-03) carrying the mapped-only number
  - reports/COMPONENT_UNIVERSE_RECONCILIATION.md (old→new delta + supersession ledger, D-02/D-04)
  - banner-marked superseded markdown reports + Phase-9 deferral flags (eval.tex + external alinker-paper)
affects: [08-fitness-scorecard, 09-paper-prose, component-f1, eval.tex]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-component F1 = mapped-only micro over (sentence, component) pairs; files with no SAM-CODE mapping are dropped (no {b} fallback); only calc_metrics primitive"
    - "Non-destructive supersession: generator-regen OR prepend banner 'superseded by mapped-only universe (v1.2)' OR ledger-classify; never silent delete/overwrite"

key-files:
  created:
    - reports/COMPONENT_UNIVERSE_RECONCILIATION.md
  modified:
    - src/bias/evaluation_critique.py
    - mini-src/metrics.py
    - reports/metrics_sad-code.csv
    - writing/tables/metrics_sad-code.tex
    - writing/tables/consequences.tex
    - writing/tables/converged_framework.tex
    - reports/SADCODE_S11_S13F_VS_TRANSARC.csv
    - reports/SADCODE_COMPARISON.md
    - reports/rq1/transarc_sad-code.csv
    - reports/rq1/artemis_sad-code.csv
    - reports/rq1/lissa_sad-code.csv
    - reports/EVALUATION_CRITIQUE.md
    - reports/RQ2_METRIC_REDUNDANCY.md
    - reports/CONSEQUENCES_STUDY.md
    - reports/EXTREME_BASELINES.md

key-decisions:
  - "D-01 realized: dropped the {b} singleton fallback in BOTH _compute_component_f1 (canonical) and mini-src/metrics.py to_comp (keeps mini-src/check.py green)"
  - "Headline metrics_sad-code.csv component_f1 AVG: 0.732 (stale artemis-source, old def) -> 0.795 (bundled TransArc result, mapped-only def); definition shift on the SAME transarc result is 0.714 -> 0.795 (matches ROADMAP)"
  - "Repopulated stale-empty reports/metrics_sad-sam.csv (Rule 3 blocking fix) so generate_tables.py exits 0; incidental sad-sam refresh documented in reconciliation §4 (NOT D-01)"
  - "s12c_four_level.tex + S12C_VS_TRANSARC.csv ledger-classified as SUPERSEDED (independent s12c pipeline), not regenerated, not in-file-bannered"

patterns-established:
  - "Pattern 1: mapped-only component universe is canonical for component_f1 across suite, metrics_api, and mini-src"
  - "Pattern 2: supersession ledger in reports/COMPONENT_UNIVERSE_RECONCILIATION.md accounts for every stale-number hit"

requirements-completed: [CMP-02]

# Metrics
duration: ~35min
completed: 2026-06-21
---

# Phase 7 Plan 02: Component Universe Reconciliation (CMP-02) Summary

**Dropped the `{b}` singleton fallback so the headline SAD-CODE `component_f1` is the mapped-only micro number (swattr/transarc AVG 0.714 → 0.795), equal to `component_suite` micro by construction; regenerated every in-repo CSV/MD/LaTeX artifact and banner/ledger-classified the rest.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-06-21
- **Tasks:** 3 (all complete)
- **Files modified:** 24 in-repo (1 created)

## Accomplishments
- `_compute_component_f1` (`src/bias/evaluation_critique.py`) now drops files with no SAM-CODE mapping — the headline `component_f1` is the mapped-only micro and matches `component_suite` micro for swattr/transarc to 1e-6 across all 5 projects (automated assertion passes).
- Identical drop applied to `mini-src/metrics.py` `to_comp`; `mini-src/check.py` still PASSES (mini == canon to 1e-9 on every panel cell, both tasks).
- Regenerated all definition-fed artifacts (D-03): `metrics_sad-code.csv` (AVG component_f1 0.732 → 0.795), `metrics_sad-code.tex`, `consequences.tex` & `converged_framework.tex` (0.714 gone), the `SADCODE_*` comparison CSV/MD, and the rq1 sad-code panels.
- Recorded the measured old→new delta and a complete supersession ledger in `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`; banner-marked 4 markdown reports; flagged `writing/eval.tex` (in-repo) and the external alinker-paper repo for Phase 9 without touching them.

## Task Commits

Manual mode — the orchestrator performs all git commits; no per-task hashes were created by this executor. Work is staged in the working tree at `/mnt/hostshare/ardoco-home/transarc-emp`.

1. **Task 1: Drop {b} fallback in both component_f1 impls** — `src/bias/evaluation_critique.py`, `mini-src/metrics.py` (TDD: RED baseline showed teammates/bbb/jabref mismatch; GREEN after edit).
2. **Task 2: Regenerate definition-fed CSV/MD/LaTeX artifacts** — via `metrics_api.py --task sad-code`, `sadcode_comparison.py`, `rq1_panels.py`, `generate_tables.py` (in order).
3. **Task 3: Discovery grep + delta record + supersession ledger + banners** — `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` + 4 banner-marked reports.

## Files Created/Modified

### Created
- `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` — old→new delta + full supersession ledger + Phase-9 flags.

### Modified — code (D-01)
- `src/bias/evaluation_critique.py` — `_compute_component_f1`: removed both `if not comps:` singleton-fallback branches (mapped-only).
- `mini-src/metrics.py` — `to_comp`: removed the per-file `else: out.add((s,c))` fallback (keeps `mini-src/check.py` green).

### Modified — REGENERATED to mapped-only value (D-03)
- `reports/metrics_sad-code.csv` (component_f1 AVG 0.732 → 0.795)
- `writing/tables/metrics_sad-code.tex` (Component F1 AVG → 0.795)
- `writing/tables/consequences.tex` (sad-code Component F1 AVG 0.714 → 0.795)
- `writing/tables/converged_framework.tex` (sad-code Component F1 0.714 → 0.795)
- `reports/SADCODE_S11_S13F_VS_TRANSARC.csv` (transarc_component_f1 AVG 0.7143 → 0.7949)
- `reports/SADCODE_COMPARISON.md`
- `reports/rq1/transarc_sad-code.csv` (component_f1 AVG 0.7143 → 0.7949)
- `reports/rq1/artemis_sad-code.csv` (0.7324 → 0.7995)
- `reports/rq1/lissa_sad-code.csv` (0.2097 → 0.2976)
- `reports/rq1/lissa-gpt4omini_sad-code.csv` (component_f1 AVG 0.1941 → 0.2811; file_f1 unchanged — pure D-01)
- `reports/rq1/aalinker-claude_sad-code.csv`, `reports/rq1/aalinker-openai_sad-code.csv` (component_f1 + incidental stale-result file-level refresh — see Deviations)

### Modified — SUPERSEDED via prepended banner
- `reports/EVALUATION_CRITIQUE.md`, `reports/RQ2_METRIC_REDUNDANCY.md`, `reports/CONSEQUENCES_STUDY.md`, `reports/EXTREME_BASELINES.md` — banner `superseded by mapped-only universe (v1.2)` prepended; original content intact.

### Modified — incidental SAD-SAM refresh (Rule 3 blocking fix, NOT D-01)
- `reports/metrics_sad-sam.csv`, `writing/tables/metrics_sad-sam.tex`, `reports/rq1/aalinker-claude_sad-sam.csv`, `reports/rq1/aalinker-openai_sad-sam.csv`

### Ledger-only SUPERSEDED (NOT modified — independent s12c pipeline)
- `reports/S12C_VS_TRANSARC.csv` (`ta_comp_F1` MACRO_AVG = 71.4), `writing/tables/s12c_four_level.tex` (Average Component 0.714) — rewritten byte-identical by `generate_tables.py`.

### NOT modified — Phase-9 deferred (flagged in ledger)
- `writing/eval.tex` (in-repo prose, the only deliberately-unedited in-repo stale-number file) and the **external** alinker-paper repo prose.

## Decisions Made
- **Definition change, not source archaeology (D-02):** the old standalone `metrics_sad-code.csv` 0.732 was a stale artemis-sourced/old-def value; re-running the generator against the bundled TransArc result with mapped-only gives 0.795 in one step. The apples-to-apples definition shift on the same transarc result is 0.714 → 0.795 (matches the ROADMAP expectation exactly, = `component_suite` micro).
- **s12c ledger-only:** its component number flows from the independent `s12c_sadcode_comparison.py` `compute_component`, not from `_compute_component_f1`, so it does not move; recorded as superseded (no in-file banner, since `generate_tables.py` rewrites the .tex byte-identical).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Repopulated stale-empty `reports/metrics_sad-sam.csv` to unblock `generate_tables.py`**
- **Found during:** Task 2 (step 4, `generate_tables.py`)
- **Issue:** The committed `reports/metrics_sad-sam.csv` was a stale placeholder containing only an em-dash `Average` row. `generate_tables.py` `t_converged_framework`/`t_consequences` crashed with `ValueError: could not convert string to float: '—'`. The plan's own Task-2 verify requires `generate_tables.py` to exit 0 — impossible against an empty SAD-SAM CSV.
- **Fix:** Ran `python3 src/lib/metrics_api.py --task sad-sam` (its own generator) to repopulate from the bundled `results/` tree — generator-based regeneration, not a silent overwrite, consistent with D-02 and CLAUDE.md "keep reports consistent with the script that produces them." Restores the populated state the committed SAD-SAM table rows were already built from.
- **Files modified:** `reports/metrics_sad-sam.csv`, `writing/tables/metrics_sad-sam.tex`
- **Verification:** `generate_tables.py` now exits 0; `consequences.tex`/`converged_framework.tex` regenerate cleanly with no 0.714.
- **Side effect:** SAD-SAM `component_f1` is unchanged (collapses onto link F1); SAD-SAM Sentence F1 in `consequences.tex` refreshed to current bundled values (AVG 0.875 → 0.825). Documented in reconciliation §4.

**2. [Rule 3 - Blocking, incidental] `rq1_panels.py` re-aligned stale agent-linker (`aalinker-*`) panels to current bundled results**
- **Found during:** Task 2 (step 3, mandated `rq1_panels.py` which "writes EVERY system")
- **Issue:** The committed `aalinker-claude_*`/`aalinker-openai_*` panels (both tasks) were stale vs. the current bundled agent-linker results; their SAD-SAM panels have no `component_f1` column yet still shifted, and their SAD-CODE file-level metrics shifted — proving the change is independent of D-01.
- **Fix:** Kept the regenerated (consistent) outputs rather than re-staling them; documented in reconciliation §4.
- **Files modified:** `reports/rq1/aalinker-claude_sad-sam.csv`, `aalinker-openai_sad-sam.csv`, `aalinker-claude_sad-code.csv`, `aalinker-openai_sad-code.csv`
- **Verification:** Generator output is deterministic for these files across re-runs (only NDG columns elsewhere wiggle).

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking/incidental, surfaced by the plan-mandated generators re-aligning pre-existing stale SAD-SAM artifacts). No D-01 scope creep — SAD-SAM `component_f1` is unchanged by the definition edit.
**Impact on plan:** All CMP-02 gates pass. The incidental SAD-SAM refresh was necessary to satisfy the plan's own Task-2 verify (`generate_tables.py` exit 0) and is fully traceable in the reconciliation ledger.

## Issues Encountered
- **Pre-existing inconsistency:** the committed `metrics_sad-code.csv` (artemis-source, 0.732) and `consequences.tex` (transarc-source, 0.714) were already out of sync before this plan; the regeneration brings both onto the single bundled-TransArc + mapped-only source of truth (0.795).
- **Pre-existing NDG non-determinism (deferred, out of scope):** `reports/SADCODE_S11_S13F_VS_TRANSARC.csv` is not byte-identical across runs — only the `*_ndg` columns wiggle (RNG in `compute_random_f1`, an explicit Phase-7 deferred carry-over). All `component_f1` columns are deterministic. Logged in reconciliation §5; not fixed (SCOPE BOUNDARY).

## Verification Results

| Gate | Command | Result |
|------|---------|--------|
| Task 1 fallback removed | `! grep -nE "if not comps" src/bias/evaluation_critique.py` | PASS |
| Task 1 mini==canon | `python3 mini-src/check.py` | PASS (exit 0) |
| Task 1 suite micro == metrics_api cf1 (1e-6, all 5 proj) | inline assertion | PASS (`DEF_MINI_RECON_OK`) |
| Task 2 regen + no stale headline | plan Task-2 verify | PASS (`REGEN_OK`) |
| consequences.tex / converged_framework.tex no 0.714 | `grep` | PASS |
| metrics_sad-code.csv AVG not 0.732 (= 0.795) | `grep` | PASS |
| rq2_trivial_baselines.py untouched (07-03 oracle) | `git diff --stat` | PASS (empty) |
| Task 3 banners + ledger | plan Task-3 verify | PASS (`SUPERSEDE_OK`) |
| Every discovery-grep hit accounted for | accounting audit | PASS (15/15 in ledger) |
| eval.tex + external repo untouched | `git status` | PASS |

## Next Phase Readiness
- CMP-02 satisfied: mapped-only universe is the single source of truth; suite micro == metrics_api component_f1 by construction; delta recorded.
- Phase 8 (fitness scorecard / multi-system comparison) can build on the reconciled numbers.
- Phase 9 must rewrite `writing/eval.tex` Component-level prose (still cites 0.648/0.574/0.880/0.714) and the external alinker-paper headline prose — both flagged in the reconciliation ledger.

---
*Phase: 07-suite-universe-reconciliation*
*Completed: 2026-06-21*
