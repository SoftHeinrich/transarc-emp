# TransArc-EMP

## What This Is

A research workspace of Python analysis scripts, generated reports, and a LaTeX paper studying ARDoCo's transitive Traceability Link Recovery (TransArc) and how its benchmark is evaluated. The v1.0 refactor narrowed the sprawled codebase down to **two pillars** — the *TransArc empirical study* and the *benchmark bias analysis* — and aligned the paper (`writing/eval.tex`) to match them. Audience: the researcher(s) authoring the larger ARDoCo evaluation paper.

## Core Value

The two retained pillars (TransArc empirical study + benchmark bias analysis) must remain reproducible and their reports/paper chapters must stay consistent with the code that produced them. If everything else is dropped, these two studies must still run and tell a coherent story.

## Current State

**Shipped v1.1 (2026-05-31) — Metrics Toolkit & Converged-Metric Motivation** (on top of v1.0 Two-Pillar Refactor). The workspace is organized as:
- `src/transarc/` (Pillar 1): SAD-SAM contribution, TP-gain, SAM-CODE cascade, S12C/S12E-vs-TransArc comparison.
- `src/bias/` (Pillar 2): enrollment-inflation critique, File/Decision/Component metrics, trivial/extreme baselines, proposed alternative metrics, **`consequences_study.py`** (v1.1).
- `src/lib/` (shared): `transarc_error_analysis.py` loaders + `new_metrics_analysis.py` + **`metrics_api.py`** (v1.1 stdlib metrics CLI).
- `src/paper/generate_tables.py`: stdlib table generator → `writing/tables/*.tex` (now 12 tables incl. consequences + converged-framework).
- `writing/eval.tex`: Ch1 = TransArc empirical study (`\input{ch1_transarc}`), Ch2 = Benchmark bias, now incl. `sec:eval:misleading-both` + converged-axis protocol extension.
- `README.md` (v1.1): top-level two-pillar map + per-pillar reproduce instructions.
- `archive/`: out-of-scope work, non-destructively retained.

All pillar scripts run clean and regenerate their reports deterministically (NDG/weighted columns jitter in low decimals — deferred source-level fix).

## Next Milestone

**🚧 v1.2 — Component-Centric Metric Suite (active, defined 2026-06-21).** A
level-agnostic component suite (`micro, macro, gap, min_comp, pct_missed,
gold_gini`) applying at BOTH doc-to-model and doc-to-code, a validated multi-system
comparison (swattr/transarc, s20linker, artemis), a paper section, and a fix for the
latent per-component-F1 universe inconsistency. Phases 7–9; see
`milestones/v1.2-ROADMAP.md`. Foundation delivered this session
(`src/bias/component_suite.py`, `reports/COMPONENT_SUITE*`). Next:
`/gsd-discuss-phase 7`.

Still-deferred carry-overs: NDG non-determinism in `compute_random_f1`; metrics API
→ **sam-code**; true `.xlsx` output (openpyxl); real `pdflatex` PDF build; rename
`transarc_error_analysis.py` → `data_loaders.py`.

## Requirements

### Validated

<!-- Pre-existing studies, plus v1.0 refactor deliverables. -->

- ✓ TransArc empirical study: error analysis, SAD-SAM bottleneck, error amplification/cascade — `src/transarc/*`, `reports/TRANSARC_EMPIRICAL_STUDY.md` + propagation reports
- ✓ Benchmark bias analysis: enrollment-inflation critique, File vs Decision vs Component F1, distribution analysis — `src/bias/*`, `reports/BENCHMARK_BIAS_STUDY.md`, `EVALUATION_CRITIQUE.md`
- ✓ Trivial/extreme baselines exposing F1 gameability — `src/bias/{stupid,extreme}_baseline_analysis.py`
- ✓ Proposed alternative metrics — `src/bias/{holistic,creative}_metrics_analysis.py`, `src/lib/new_metrics_analysis.py`
- ✓ Two-pillar reorganization of `src/` + non-destructive archival — v1.0 (Phase 1)
- ✓ s12c comparison co-located with Pillar 1 — v1.0 (Phase 1)
- ✓ Both pillars verified reproducible (13/13 scripts, reports regenerate) — v1.0 (Phase 2)
- ✓ `writing/eval.tex` restructured: Ch1 = TransArc study, Ch2 = Benchmark bias — v1.0 (Phase 3)
- ✓ Data-driven LaTeX table generation (`src/paper/generate_tables.py`) — v1.0 (Phase 3)
- ✓ Stdlib metrics API: TransArc-format sad-sam/sad-code → full per-task metric set → CSV + LaTeX (`src/lib/metrics_api.py`) — v1.1 (MTR-01..05)
- ✓ SAD-SAM pure-F1 + SAD-CODE file-level consequences study (`src/bias/consequences_study.py`, `reports/CONSEQUENCES_STUDY.md`) — v1.1 (STUDY-01/02)
- ✓ Converged metric framework (Decision + Component common axis), written into `eval.tex` Ch2 — v1.1 (STUDY-03/04)
- ✓ Top-level two-pillar README with per-pillar reproduce instructions (`README.md`) — v1.1 (DOC-01/02)

### Active

<!-- v1.2 Component-Centric Metric Suite (see milestones/v1.2-REQUIREMENTS.md). -->

- ◐ CMP-01 — Level-agnostic component suite tool (micro/macro/gap/min_comp/pct_missed/gold_gini) at sad-model + sad-code, reusing `calc_metrics` only → CSV (`src/bias/component_suite.py`) — *foundation delivered; harden in Phase 7*
- ☐ CMP-02 — Reconcile micro & macro onto one mapped-only universe; reconcile/document the `metrics_api` headline `component_f1` delta (Phase 7)
- ◐ CMP-03 — Multi-system, two-level comparison (swattr/transarc, s20linker, artemis) → `reports/COMPONENT_SUITE.md` — *foundation delivered; harden in Phase 8*
- ☐ CMP-04 — Metric fitness validation scorecard (separation/validity/stability/degeneracy); hardened baselines justify headline=macro+tail vs diagnostic=micro/gap (Phase 8)
- ☐ CMP-05 — Paper integration: suite + artemis long-tail finding + universe correction into `eval.tex` Ch2 with generated tables (Phase 9)
- ☐ CMP-06 — Reproducibility + equivalence oracle (suite-macro == `per_component_macro_f1`; deterministic regen) (Phase 7)

### Out of Scope

- SWATTR FP filter (LLM few-shot post-filter on SAD-SAM) — an *intervention/tool*, not an analytical study; stays in `archive/`
- LLM agentic baselines, precision classifier, improved/meta-learning classifiers — prior exploration, archived
- LLM ablation linkers (`llm-sad-sam-v45`, S-Linker variants) — external dependency; only the s12c *result comparison* is kept
- Annotation-convention reverse-engineering — supports the archived SWATTR work; archived
- `pdflatex` PDF build of eval.tex — chapters feed a larger external paper; no local toolchain (v1.0 SC4 reframed to table-gen + structural validation)

## Context

- **Brownfield**: codebase map at `.planning/codebase/` (ARCHITECTURE, STACK, STRUCTURE, CONVENTIONS, TESTING, CONCERNS, INTEGRATIONS).
- **Current layout**: `src/{transarc,bias,lib,paper}`, `reports/` (~17 markdown + CSV), `writing/{eval.tex,ch1_transarc.tex,tables/}`, `bench-paper.pdf`, `results/` (run outputs), `archive/` (prior work).
- **Shared data loaders**: both pillars import `src/lib/transarc_error_analysis.py` (PROJECTS, BENCHMARK, RESULTS, `load_code_model_files`, `enroll_gold_standard`, gold loaders). Depth-2 `src/<pillar>/x.py` keeps `sys.path.insert(parent.parent/"lib")` resolving.
- **Benchmark data** lives outside this repo at `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/` (5 projects: mediastore, teastore, teammates, bigbluebutton, jabref).
- **Key prior findings**: SAD-SAM is the primary TransArc bottleneck (93.7% of FPs); error amplification is extreme; file-level P/R/F1 is misleading (enrollment 36× inflation; JabRef ranking flips File F1 0.943 → Decision F1 0.394).
- **Environment**: repo on a hostshare mount with a flaky git stat-cache + intermittent read corruption — run git inline, `git update-index --refresh` before status, `sed` reads sandbox-off.
- **CLAUDE.md leakage rule**: no benchmark-derived word lists in any retained/LLM-touching code.

## Constraints

- **Tech stack**: Python 3 (stdlib only) analysis scripts; LaTeX (`report` class) for the paper. No build system beyond `python3 script.py`.
- **Reproducibility**: scripts read fixed benchmark paths + `results/`; moves must preserve relative imports (`sys.path.insert` to `src/lib`) and output paths into `reports/`.
- **Consistency**: paper chapters cite only retained scripts/reports; no orphaned references to archived work.
- **Non-destructive archival**: out-of-scope work moves to `archive/` via `git mv`, never deleted.
- **Git**: planning docs committed (`commit_docs: true`); reorganization via `git mv`.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep only TransArc empirical study + benchmark bias analysis | Two coherent analytical studies; everything else is intervention/exploration | ✓ Good (v1.0) |
| SWATTR FP filter stays archived | Prescriptive tool, not a study; LLM machinery | ✓ Good (v1.0) |
| Fold proposed-metrics + baselines into benchmark bias | Bias pillar = critique + baseline evidence + proposed metrics | ✓ Good (v1.0) |
| s12c comparison → TransArc study | Frames S12C/S12E-vs-TransArc as part of the empirical study | ✓ Good (v1.0) |
| Archive `annotation/*` + SWATTR-dependent scripts | Support archived/out-of-scope work, not pillar outputs | ✓ Good (v1.0) |
| Paper = TransArc + Bias chapters (merge old Distributional + Metrics into Bias) | Align paper structure exactly to the two pillars | ✓ Good (v1.0) |
| `new_metrics_analysis.py` stays in `src/lib` | Imported as a library by both pillars, not a standalone script | ✓ Good (v1.0) |
| Keep depth-2 `src/<pillar>/x.py` layout | Preserves `parent.parent/lib` import resolution with zero code edits | ✓ Good (v1.0) |
| Reframe paper SC4 (table-gen + structural validation, not pdflatex) | No local LaTeX toolchain; chapters feed a larger external paper | ✓ Good (v1.0) |
| SAD-SAM has no file/enrollment granularity (link/sentence/component only) | File/Decision/Component is a SAD-CODE enrollment construct; sad-sam pairs are direct, uninflated | ✓ Good (v1.1) |
| Converged metric = Decision + Component common axis (not a single composite), layered atop existing corrected metrics | Gives both tasks one honest evaluation story without discarding the v1.0 metric suite | ✓ Good (v1.1) |
| Metrics API reuses existing primitives, zero metric-math reimplementation | Guarantees numbers match published reports; cheaper to verify | ✓ Good (v1.1) |
| NDG/weighted column low-decimal non-determinism deferred | Root cause is set-iteration order in `compute_random_f1` (source-level); not goal-blocking | ⚠️ Revisit (v1.1) |
| Component suite computes micro & macro on ONE mapped-only universe | The two legacy defs disagreed (`_compute_component_f1` keeps unmapped files `{b}`; `per_component_macro_f1` drops `()`), inflating the apparent gap (bbb −0.31→−0.05) | 🚧 v1.2 (CMP-02) |
| Headline = macro + tail coverage; micro = anchor/gap term | Reconciled micro/macro aggregation is second-order; tail coverage (min_comp/pct_missed) is the level-stable discriminator | 🚧 v1.2 (CMP-04) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-21 — v1.2 milestone defined (Component-Centric Metric Suite); foundation delivered.*
