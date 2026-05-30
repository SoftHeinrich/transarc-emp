# TransArc-EMP

## What This Is

A research workspace of Python analysis scripts, generated reports, and a LaTeX paper studying ARDoCo's transitive Traceability Link Recovery (TransArc) and how its benchmark is evaluated. The v1.0 refactor narrowed the sprawled codebase down to **two pillars** — the *TransArc empirical study* and the *benchmark bias analysis* — and aligned the paper (`writing/eval.tex`) to match them. Audience: the researcher(s) authoring the larger ARDoCo evaluation paper.

## Core Value

The two retained pillars (TransArc empirical study + benchmark bias analysis) must remain reproducible and their reports/paper chapters must stay consistent with the code that produced them. If everything else is dropped, these two studies must still run and tell a coherent story.

## Current State

**Shipped v1.0 (2026-05-30) — Two-Pillar Refactor.** The workspace is now organized as:
- `src/transarc/` (Pillar 1): SAD-SAM contribution, TP-gain, SAM-CODE cascade, S12C/S12E-vs-TransArc comparison.
- `src/bias/` (Pillar 2): enrollment-inflation critique, File/Decision/Component metrics, trivial/extreme baselines, proposed alternative metrics.
- `src/lib/` (shared): `transarc_error_analysis.py` loaders + `new_metrics_analysis.py` (serve both pillars).
- `src/paper/generate_tables.py`: stdlib table generator → `writing/tables/*.tex`.
- `writing/eval.tex`: Ch1 = TransArc empirical study (`\input{ch1_transarc}`), Ch2 = Benchmark bias.
- `archive/`: out-of-scope work (annotation, SWATTR, LLM exploration), non-destructively retained.

All 13 pillar scripts run clean and regenerate their reports deterministically.

## Current Milestone: v1.1 Metrics Toolkit & Converged-Metric Motivation

**Goal:** Ship a reproducible metrics-reporting API plus a motivation study showing how misleading F1 harms BOTH SAD-SAM and SAD-CODE, and propose a converged metric framework that gives the two tasks one coherent evaluation story — while making the workspace handoff-ready.

**Target features:**
- DOC-01: top-level README mapping the two pillars.
- DOC-02: per-pillar run/reproduce instructions.
- Metrics API: ingest TransArc-format linker results → compute all metrics (File/Decision/Component F1 + proposed alternatives) for **sad-sam** and **sad-code** → emit CSV (Excel-openable) + LaTeX table.
- Empirical consequences study: harm of misleading F1 for BOTH **SAD-SAM** (pure F1) and **SAD-CODE** (file-level enrollment F1), then propose **converged metrics** so the two tasks share one evaluation story (motivation chapter, extends Pillar 2).

**Key context:**
- Stdlib-only preserved — Excel output is **CSV**, not `.xlsx` (no openpyxl, no requirements.txt).
- Metrics API ingests the existing **TransArc output format** from `results/`; reuses `src/lib` + `src/bias` for metric computation.
- Tasks limited to **sad-sam + sad-code** (no sam-code this milestone).
- The consequences study + converged-metrics proposal extend Pillar 2 (benchmark bias).

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

### Active

<!-- Empty — next milestone defines new requirements via /gsd-new-milestone. -->

(none — v1.0 shipped; define next milestone's requirements with `/gsd-new-milestone`)

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
*Last updated: 2026-05-30 — v1.1 milestone started (Metrics Toolkit & Converged-Metric Motivation)*
