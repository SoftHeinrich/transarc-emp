# Requirements: TransArc-EMP — Milestone v1.1

**Milestone:** v1.1 Metrics Toolkit & Converged-Metric Motivation
**Goal:** Ship a reproducible metrics-reporting API + a motivation study showing how misleading F1 harms BOTH SAD-SAM and SAD-CODE, and propose a converged metric framework that gives the two tasks one coherent evaluation story — while making the workspace handoff-ready.

## v1.1 Requirements

### Documentation
<!-- DOC-01/DOC-02 were defined and deferred in v1.0; activated this milestone. -->

- [x] **DOC-01
**: A top-level README maps the two pillars — what each pillar is, and where its code, reports, and paper chapter live.
- [x] **DOC-02
**: Each pillar has run/reproduce instructions — a reader can regenerate that pillar's reports from scratch by following them.

### Metrics API
<!-- Ingest TransArc-format linker results → all metrics → CSV + LaTeX. Stdlib only. Reuse src/lib + src/bias. Tasks: sad-sam + sad-code only. -->

- [x] **MTR-01
**: A user can point the API at a TransArc-format results file for a **sad-sam** run and get all metrics computed.
- [x] **MTR-02
**: A user can point the API at a TransArc-format results file for a **sad-code** run (with gold-standard enrollment) and get all metrics computed.
- [x] **MTR-03
**: The API computes the full metric set — File, Decision, and Component P/R/F1 plus the proposed alternative metrics — by reusing `src/lib` + `src/bias`, with no benchmark-derived word lists.
- [x] **MTR-04
**: The API emits the computed metrics as CSV (Excel-openable), covering all benchmark projects for the run in one sheet.
- [x] **MTR-05
**: The API emits a ready-to-paste LaTeX table of the same metrics.

### Consequences Study & Converged Metrics (Pillar 2 extension)
<!-- Motivation chapter: harm of misleading F1 for BOTH tasks → one converged story. -->

- [x] **STUDY-01
**: An analysis quantifies the misleading consequences of **SAD-SAM pure F1** — what the headline number hides or distorts.
- [x] **STUDY-02
**: An analysis quantifies the misleading consequences of **SAD-CODE file-level (enrollment) F1**, consolidating prior bias findings as motivation evidence.
- [x] **STUDY-03
**: A **converged metric framework** is proposed that applies one common evaluation story across both SAD-SAM and SAD-CODE.
- [x] **STUDY-04
**: The consequences findings + converged-metrics proposal are written up as a motivation section aligned to the paper (extends Ch2 Benchmark bias), citing only retained scripts/reports.

## Future Requirements (deferred)

- Rename `src/lib/transarc_error_analysis.py` → `data_loaders.py` (clarity cleanup; no functional change).
- Real `pdflatex` PDF build of `eval.tex` (no local LaTeX toolchain; chapters feed a larger external paper).
- Extend the metrics API to **sam-code** (this milestone scopes to sad-sam + sad-code).
- True `.xlsx` workbook output (would add an openpyxl dependency; CSV chosen to preserve stdlib-only).

## Out of Scope

- `.xlsx` via third-party library — breaks the stdlib-only constraint; CSV is the chosen Excel-openable format.
- New linker formats / generic ingestion adapters — the API ingests the existing TransArc output format only.
- sam-code metrics — excluded from this milestone's metric scope.
- Any benchmark-derived word lists in the API or study code (workspace CLAUDE.md leakage rule).

## Traceability

<!-- REQ-ID → Phase. -->

| REQ-ID | Phase |
|--------|-------|
| MTR-01 | Phase 4: Metrics API |
| MTR-02 | Phase 4: Metrics API |
| MTR-03 | Phase 4: Metrics API |
| MTR-04 | Phase 4: Metrics API |
| MTR-05 | Phase 4: Metrics API |
| STUDY-01 | Phase 5: Consequences Study & Converged Metrics |
| STUDY-02 | Phase 5: Consequences Study & Converged Metrics |
| STUDY-03 | Phase 5: Consequences Study & Converged Metrics |
| STUDY-04 | Phase 5: Consequences Study & Converged Metrics |
| DOC-01 | Phase 6: Handoff Docs |
| DOC-02 | Phase 6: Handoff Docs |

**Coverage:** 11/11 requirements mapped ✓
