# Roadmap: TransArc-EMP

## Overview

This refactor milestone narrows a sprawled research workspace down to two pillars — the TransArc empirical study and the benchmark bias analysis — then verifies both pillars reproduce cleanly, and finally restructures the LaTeX paper to match. Work flows in one direction: reorganize first, verify second, write paper third. Nothing moves back upstream.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Reorganize** - Move scripts/reports into the two-pillar structure and archive out-of-scope work
- [x] **Phase 2: Verify** - Confirm both pillars run end-to-end and all imports/paths are intact after the moves
- [x] **Phase 3: Paper** - Restructure eval.tex to match the two-pillar structure (Ch1=TransArc, Ch2=Bias)

## Phase Details

### Phase 1: Reorganize
**Goal**: The workspace is structured as two explicit pillars with out-of-scope work moved to archive
**Depends on**: Nothing (first phase)
**Requirements**: SCOPE-01, SCOPE-02, SCOPE-03, SCOPE-04, SCOPE-05, ARCH-01, ARCH-02, ARCH-03, ARCH-04
**Success Criteria** (what must be TRUE):
  1. `src/` tree has a clear Pillar 1 grouping (transarc_error_analysis, propagation/*) and Pillar 2 grouping (bias/*, evaluation_critique, baselines, proposed-metrics scripts)
  2. `s12c_sadcode_comparison.py` and `reports/S12C_VS_TRANSARC.csv` are co-located with Pillar 1 material
  3. `src/annotation/` is empty or gone and both annotation scripts live under `archive/`
  4. `reports/ANNOTATION_CONVENTION.md` and any other gray reports live under `archive/`
  5. No retained script contains an import referencing an archived path, and no retained report links to archived work
**Plans**: 1 plan
  - [ ] 01-01-PLAN.md — Move-only reorg: assemble src/transarc/ (Pillar 1), expand src/bias/ (Pillar 2), archive annotation scripts + report, static import/reference checks

### Phase 2: Verify
**Goal**: Both retained pillars run reproducibly — every script executes and regenerates its report with paths intact
**Depends on**: Phase 1
**Requirements**: REPRO-01, REPRO-02, REPRO-03
**Success Criteria** (what must be TRUE):
  1. `python3` on every Pillar 1 script completes without import errors or path failures and writes its report to `reports/`
  2. `python3` on every Pillar 2 script completes without import errors or path failures and writes its report to `reports/`
  3. The shared `src/lib/` data-loader layer is importable by scripts in both pillars (no broken `sys.path` references)
**Plans**: TBD

### Phase 3: Paper
**Goal**: `writing/eval.tex` is restructured as Ch1=TransArc empirical study, Ch2=Benchmark bias, compiles cleanly, and every claim traces to a retained artifact
**Depends on**: Phase 2
**Requirements**: PAPER-01, PAPER-02, PAPER-03, PAPER-04
**Success Criteria** (what must be TRUE):
  1. Chapter 1 of eval.tex covers the TransArc empirical study (SAD-SAM bottleneck, error amplification, cascade analysis, s12c comparison)
  2. Chapter 2 of eval.tex covers benchmark bias (distributional inequality, enrollment inflation, metric critique, baselines, proposed metrics) — merging current Distributional Inequality and Comprehensive Metrics chapters into one
  3. Every figure, table, and quantitative claim in the two chapters can be traced to a specific retained script or report in `reports/`
  4. LaTeX tables are generated from data/results via a script (reproducible, not hand-typed); `eval.tex` passes structural validation (balanced environments/braces, resolved `\ref`/`\label`). Full `pdflatex` compile is out of scope per user (no local toolchain; chapters are authored into a larger external paper).
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Reorganize | 0/1 | Not started | - |
| 2. Verify | 0/TBD | Not started | - |
| 3. Paper | 0/TBD | Not started | - |
