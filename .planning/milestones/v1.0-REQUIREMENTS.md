# Requirements: TransArc-EMP

**Defined:** 2026-05-30
**Core Value:** The two retained pillars (TransArc empirical study + benchmark bias analysis) must stay reproducible, and their reports/paper chapters must remain consistent with the code that produced them.

## v1 Requirements

Requirements for this refactor milestone. Each maps to a roadmap phase.

### Scope (codebase reorganization)

- [ ] **SCOPE-01**: TransArc empirical study scripts (`transarc_error_analysis`, `propagation/*`) and their reports are grouped as Pillar 1
- [ ] **SCOPE-02**: `s12c_sadcode_comparison.py` and `reports/S12C_VS_TRANSARC.csv` are moved into Pillar 1 (TransArc study)
- [ ] **SCOPE-03**: Benchmark bias scripts (`bias/*`, `evaluation_critique`) and their reports are grouped as Pillar 2
- [ ] **SCOPE-04**: Baseline scripts/reports (`stupid_baseline_analysis`, `extreme_baseline_analysis`, STUPID_BASELINES, EXTREME_BASELINES) are folded into Pillar 2
- [ ] **SCOPE-05**: Proposed-metrics scripts/reports (`holistic_metrics_analysis`, `creative_metrics_analysis`, `new_metrics_analysis`, HOLISTIC/CREATIVE/NEW_METRICS, METRIC_LIMITATIONS) are folded into Pillar 2

### Archive (out-of-scope removal)

- [ ] **ARCH-01**: `src/annotation/*` (`doc_structure_analysis_v2`, `reverse_engineer_convention`) is moved to `archive/`
- [ ] **ARCH-02**: SWATTR-dependent and remaining gray reports (e.g. `ANNOTATION_CONVENTION.md`) are moved to `archive/`
- [ ] **ARCH-03**: SWATTR FP filter work remains in `archive/` (untouched, confirmed not referenced by retained code)
- [ ] **ARCH-04**: No retained script or report references archived/out-of-scope code (no broken imports or dangling links)

### Reproducibility

- [ ] **REPRO-01**: Shared data-loader layer in `src/lib` works for both pillars after the move (imports/paths intact)
- [ ] **REPRO-02**: Every retained Pillar 1 script runs end-to-end and regenerates its report
- [ ] **REPRO-03**: Every retained Pillar 2 script runs end-to-end and regenerates its report

### Paper alignment

- [ ] **PAPER-01**: `writing/eval.tex` Chapter 1 is the TransArc empirical study (new chapter)
- [ ] **PAPER-02**: `writing/eval.tex` Chapter 2 is Benchmark bias — current Distributional Inequality + Comprehensive Metrics chapters merged into one
- [ ] **PAPER-03**: Every claim/figure/table in the two chapters traces to a retained script or report (no references to archived work)
- [ ] **PAPER-04**: `writing/eval.tex` compiles standalone after restructure

## v2 Requirements

Deferred. Tracked but not in this milestone.

### Documentation

- **DOC-01**: Top-level README mapping the two-pillar structure and how to reproduce each
- **DOC-02**: Per-pillar run/reproduce instructions

## Out of Scope

| Feature | Reason |
|---------|--------|
| SWATTR FP filter (as active pillar) | Intervention/tool, not an analytical study; LLM machinery; stays in archive |
| LLM agentic / precision / improved classifiers | Prior exploration, already archived; outside the two pillars |
| LLM ablation linkers (`llm-sad-sam-v45`, S-Linker variants) | External dependency; only the s12c result comparison is retained, not the linkers |
| Annotation-convention reverse-engineering | Supports archived SWATTR work; not a pillar output |
| New analyses / new research | This is a consolidation/refactor milestone, not new research |
| Deleting archived work | Archival is non-destructive (`git mv` into `archive/`), nothing is deleted |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCOPE-01 | Phase 1 | Pending |
| SCOPE-02 | Phase 1 | Pending |
| SCOPE-03 | Phase 1 | Pending |
| SCOPE-04 | Phase 1 | Pending |
| SCOPE-05 | Phase 1 | Pending |
| ARCH-01 | Phase 1 | Pending |
| ARCH-02 | Phase 1 | Pending |
| ARCH-03 | Phase 1 | Pending |
| ARCH-04 | Phase 1 | Pending |
| REPRO-01 | Phase 2 | Pending |
| REPRO-02 | Phase 2 | Pending |
| REPRO-03 | Phase 2 | Pending |
| PAPER-01 | Phase 3 | Pending |
| PAPER-02 | Phase 3 | Pending |
| PAPER-03 | Phase 3 | Pending |
| PAPER-04 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-30*
*Last updated: 2026-05-30 — traceability populated by roadmapper*
