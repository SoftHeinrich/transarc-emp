# TransArc-EMP

## What This Is

A research workspace of Python analysis scripts, generated reports, and a LaTeX paper studying ARDoCo's transitive Traceability Link Recovery (TransArc) and how its benchmark is evaluated. This refactor narrows the sprawled codebase down to **two pillars** — the *TransArc empirical study* and the *benchmark bias analysis* — and aligns the paper (`writing/eval.tex`) to match them. Audience: the researcher(s) authoring the larger ARDoCo evaluation paper.

## Core Value

The two retained pillars (TransArc empirical study + benchmark bias analysis) must remain reproducible and their reports/paper chapters must stay consistent with the code that produced them. If everything else is dropped, these two studies must still run and tell a coherent story.

## Requirements

### Validated

<!-- Inferred from existing code/reports — already built and relied upon. -->

- ✓ TransArc empirical study: error analysis, SAD-SAM bottleneck, error amplification/cascade — existing (`src/lib/transarc_error_analysis.py`, `src/propagation/*`, `reports/TRANSARC_EMPIRICAL_STUDY.md` + propagation reports)
- ✓ Benchmark bias analysis: enrollment-inflation critique, File vs Decision vs Component F1, distribution analysis — existing (`src/bias/*`, `src/evaluation/evaluation_critique.py`, `reports/BENCHMARK_BIAS_STUDY.md`, `EVALUATION_CRITIQUE.md`)
- ✓ Trivial/extreme baselines exposing F1 gameability — existing (`src/evaluation/stupid_baseline_analysis.py`, `extreme_baseline_analysis.py`)
- ✓ Proposed alternative metrics — existing (`src/evaluation/holistic_metrics_analysis.py`, `creative_metrics_analysis.py`, `src/lib/new_metrics_analysis.py`)
- ✓ Paper draft `writing/eval.tex` (currently 2 chapters: Distributional Inequality + Comprehensive Metrics)

### Active

<!-- This refactor milestone. -->

- [ ] Reorganize `src/` and `reports/` so only the two pillars are active: **Pillar 1 — TransArc empirical study**, **Pillar 2 — Benchmark bias analysis**
- [ ] Fold the proposed-metrics + baseline scripts/reports into Pillar 2 (benchmark bias)
- [ ] Move `src/evaluation/s12c_sadcode_comparison.py` (+ `reports/S12C_VS_TRANSARC.csv`) into Pillar 1 (TransArc study)
- [ ] Archive out-of-scope work: `src/annotation/*`, SWATTR-dependent scripts (`reverse_engineer_convention`), remaining gray reports (e.g. `ANNOTATION_CONVENTION.md`)
- [ ] Restructure `writing/eval.tex` → **Ch1 = TransArc empirical study (new)**, **Ch2 = Benchmark bias** (merge current Distributional Inequality + Comprehensive Metrics)
- [ ] Verify both pillars still run reproducibly after the move (imports/paths intact) and reports regenerate
- [ ] Ensure code and paper are consistent: every claim/figure in the two chapters traces to a retained script/report

### Out of Scope

- SWATTR FP filter (LLM few-shot post-filter on SAD-SAM) — an *intervention/tool*, not an analytical study; different artifact class, drags in LLM pipeline machinery; stays in `archive/`
- LLM agentic baselines, precision classifier, improved/meta-learning classifiers — prior exploration, already archived; not part of the two pillars
- LLM ablation linkers (`llm-sad-sam-v45`, S-Linker variants) — external dependency; only their *result comparison* (s12c) is kept as TransArc-study evidence, not the linkers themselves
- Annotation-convention reverse-engineering — supports the archived SWATTR work; not a study output
- Building new analyses/features — this is a consolidation/refactor milestone, not new research

## Context

- **Brownfield**: codebase map exists at `.planning/codebase/` (ARCHITECTURE, STACK, STRUCTURE, CONVENTIONS, TESTING, CONCERNS, INTEGRATIONS).
- **Current layout**: `src/` (annotation, bias, evaluation, lib, propagation), `reports/` (~17 markdown + CSV), `writing/eval.tex`, `bench-paper.pdf`, `results/` (run outputs), `archive/` (prior LLM + SWATTR work).
- **Shared data loaders**: pillar scripts import a shared module under `src/lib/` (PROJECTS, BENCHMARK, RESULTS, `load_code_model_files`, `enroll_gold_standard`, gold-standard loaders). Refactor must keep this shared layer working for both pillars.
- **Benchmark data** lives outside this repo at `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/` (5 projects: mediastore, teastore, teammates, bigbluebutton, jabref).
- **Key prior findings** (memory): SAD-SAM is the primary TransArc bottleneck; error amplification is extreme (mean 85.5×); file-level P/R/F1 is misleading (enrollment 36× inflation; JabRef ranking flips File F1 0.943 → Decision F1 0.394).
- **CLAUDE.md leakage rule**: no benchmark-derived word lists in any retained/LLM-touching code (relevant if SWATTR scripts are referenced).

## Constraints

- **Tech stack**: Python 3 analysis scripts; LaTeX (`report` class) for the paper. No build system beyond `python3 script.py`.
- **Reproducibility**: scripts read fixed benchmark paths + `results/`; moves must preserve relative imports (`sys.path.insert` to `src/lib`) and output paths into `reports/`.
- **Consistency**: paper chapters must cite only retained scripts/reports; no orphaned references to archived work.
- **Non-destructive archival**: out-of-scope work moves to `archive/`, not deleted (prior work uses `git mv` into `archive/`).
- **Git**: planning docs committed (`commit_docs: true`). Existing convention: reorganization commits via `git mv`.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep only TransArc empirical study + benchmark bias analysis | Two coherent analytical (descriptive) studies; everything else is intervention/exploration | — Pending |
| SWATTR FP filter stays archived | Prescriptive tool, not a study; different artifact class + LLM machinery | — Pending |
| Fold proposed-metrics + baselines into benchmark bias | Bias pillar = critique + baseline evidence + proposed metrics; coherent chapter | — Pending |
| s12c comparison → TransArc study | Frames S12C/S12E-vs-TransArc as part of the empirical study | — Pending |
| Archive `annotation/*` + SWATTR-dependent scripts | Support archived/out-of-scope work, not pillar outputs | — Pending |
| Paper = TransArc + Bias chapters (merge old Distributional + Metrics into Bias) | Align paper structure exactly to the two pillars | — Pending |

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
*Last updated: 2026-05-30 after initialization*
