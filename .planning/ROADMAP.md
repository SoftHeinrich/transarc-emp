# Roadmap: TransArc-EMP

## Milestones

- ✅ **v1.0 Two-Pillar Refactor** — Phases 1-3 (shipped 2026-05-30) — see [archive](milestones/v1.0-ROADMAP.md)
- 🚧 **v1.1 Metrics Toolkit & Converged-Metric Motivation** — Phases 4-6 (in progress)

## Phases

<details>
<summary>✅ v1.0 Two-Pillar Refactor (Phases 1-3) — SHIPPED 2026-05-30</summary>

- [x] Phase 1: Reorganize (1/1 plans) — completed 2026-05-30
- [x] Phase 2: Verify (1/1 plans) — completed 2026-05-30
- [x] Phase 3: Paper (1/1 plans) — completed 2026-05-30

Narrowed the workspace to two pillars (`src/transarc/`, `src/bias/`, shared `src/lib/`),
verified both run reproducibly, and restructured `writing/eval.tex` into Ch1=TransArc
study + Ch2=Benchmark bias with a data-driven table generator (`src/paper/generate_tables.py`).

</details>

### v1.1 Metrics Toolkit & Converged-Metric Motivation (Phases 4-6)

- [x] **Phase 4: Metrics API** - Ingest TransArc-format sad-sam/sad-code results, compute the full metric set, emit CSV + LaTeX.
- [x] **Phase 5: Consequences Study & Converged Metrics** - Quantify how misleading F1 harms both tasks and propose one converged evaluation story (extends Pillar 2).
- [ ] **Phase 6: Handoff Docs** - Top-level two-pillar README + per-pillar run/reproduce instructions.

## Phase Details

### Phase 4: Metrics API
**Goal**: A user can point a stdlib-only API at a TransArc-format results file (sad-sam or sad-code) and get the full metric set out as both CSV and a ready-to-paste LaTeX table.
**Depends on**: Phase 3 (Pillar 2 metric code in `src/bias` + `src/lib`)
**Requirements**: MTR-01, MTR-02, MTR-03, MTR-04, MTR-05
**Success Criteria** (what must be TRUE):
  1. Running the API on a TransArc-format **sad-sam** results file produces a computed metric set for all benchmark projects (MTR-01).
  2. Running the API on a TransArc-format **sad-code** results file applies gold-standard enrollment and produces a computed metric set for all benchmark projects (MTR-02).
  3. The emitted metric set includes File, Decision, and Component P/R/F1 plus the proposed alternative metrics, computed by reusing `src/lib` + `src/bias` with no benchmark-derived word lists (MTR-03).
  4. The API writes a CSV (Excel-openable, stdlib `csv` only — no `.xlsx`) with one row per project covering the whole run in a single sheet (MTR-04).
  5. The API writes a LaTeX table of the same metrics that can be pasted into the paper without hand-editing (MTR-05).
**Plans**: 1 plan

Plans:
- [x] 04-01-PLAN.md — Build src/lib/metrics_api.py: stdlib CLI computing the unified metric set for sad-sam + sad-code, emitting reports/metrics_<task>.csv and writing/tables/metrics_<task>.tex by reusing existing functions.

### Phase 5: Consequences Study & Converged Metrics
**Goal**: A motivation analysis shows, with numbers, how misleading F1 distorts BOTH SAD-SAM (pure F1) and SAD-CODE (file-level enrollment F1), and proposes a converged metric framework giving the two tasks one coherent evaluation story — written up as a Pillar 2 paper section.
**Depends on**: Phase 4 (the metrics API output is available as evidence for the study)
**Requirements**: STUDY-01, STUDY-02, STUDY-03, STUDY-04
**Success Criteria** (what must be TRUE):
  1. An analysis quantifies what the headline **SAD-SAM pure F1** hides or distorts, output to a `reports/` artifact (STUDY-01).
  2. An analysis quantifies the misleading consequences of **SAD-CODE file-level (enrollment) F1**, consolidating prior bias findings (e.g. the JabRef File 0.943 → Decision 0.394 flip) as motivation evidence (STUDY-02).
  3. A **converged metric framework** is proposed and documented that applies one common evaluation story across both SAD-SAM and SAD-CODE (STUDY-03).
  4. The consequences findings + converged-metrics proposal are written into the paper as a motivation section extending Ch2 (Benchmark bias), citing only retained scripts/reports — `writing/eval.tex` still validates structurally and tables regenerate (STUDY-04).
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md — Build src/bias/consequences_study.py (stdlib): read the two Phase-4 metrics CSVs, emit reports/CONSEQUENCES_STUDY.md with SAD-SAM pure-F1 consequences (STUDY-01), consolidated SAD-CODE file-level consequences (STUDY-02), and the converged Decision+Component framework (STUDY-03).
- [x] 05-02-PLAN.md — Add t_consequences + t_converged_framework builders to src/paper/generate_tables.py and write the new Ch2 motivation section + converged-framework protocol extension into writing/eval.tex (STUDY-04).

### Phase 6: Handoff Docs
**Goal**: A new reader can open the repo, understand the two-pillar structure, and regenerate either pillar's reports from scratch by following written instructions.
**Depends on**: Phase 5 (docs describe the final layout including the Phase 4 metrics API and Phase 5 study)
**Requirements**: DOC-01, DOC-02
**Success Criteria** (what must be TRUE):
  1. A top-level README maps the two pillars — what each pillar is, and where its code, reports, and paper chapter live (DOC-01).
  2. Each pillar has run/reproduce instructions a reader can follow to regenerate that pillar's reports from scratch (DOC-02).
  3. The instructions cover the new metrics API (Phase 4) and the consequences study (Phase 5), so the documented commands match the shipped scripts.
**Plans**: 1 plan

Plans:
- [ ] 06-01-PLAN.md — Write top-level README.md: two-pillar map table (DOC-01) + per-pillar reproduce sections from the verified script→output map (DOC-02), covering the Phase-4 metrics API and Phase-5 consequences study; spot-validate one representative command per pillar.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Reorganize | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 2. Verify | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 3. Paper | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 4. Metrics API | v1.1 | 1/1 | ✓ Complete | 2026-05-30 |
| 5. Consequences Study & Converged Metrics | v1.1 | 2/2 | ✓ Complete | 2026-05-30 |
| 6. Handoff Docs | v1.1 | 0/1 | Not started | - |
