# Roadmap: TransArc-EMP

## Milestones

- ✅ **v1.0 Two-Pillar Refactor** — Phases 1-3 (shipped 2026-05-30) — see [archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Metrics Toolkit & Converged-Metric Motivation** — Phases 4-6 (shipped 2026-05-31) — see [archive](milestones/v1.1-ROADMAP.md)
- 🚧 **v1.2 Component-Centric Metric Suite** — Phases 7-9 (active, defined 2026-06-21) — see [roadmap](milestones/v1.2-ROADMAP.md)

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

<details>
<summary>✅ v1.1 Metrics Toolkit & Converged-Metric Motivation (Phases 4-6) — SHIPPED 2026-05-31</summary>

- [x] Phase 4: Metrics API (1/1 plans) — completed 2026-05-30
- [x] Phase 5: Consequences Study & Converged Metrics (2/2 plans) — completed 2026-05-30
- [x] Phase 6: Handoff Docs (1/1 plans) — completed 2026-05-31

Shipped `src/lib/metrics_api.py` (stdlib metric set → CSV + LaTeX), corrected the SAD-SAM
metric framing (link/sentence/component, no enrollment), `src/bias/consequences_study.py`
+ `reports/CONSEQUENCES_STUDY.md`, a converged Decision+Component framework written into
`eval.tex` Ch2, and a top-level two-pillar `README.md`. Full detail: [archive](milestones/v1.1-ROADMAP.md).

</details>

## Active — v1.2 Component-Centric Metric Suite (Phases 7-9)

- [ ] Phase 7: Suite & Universe Reconciliation — CMP-01, CMP-02, CMP-06
- [ ] Phase 8: Multi-System Comparison & Fitness Validation — CMP-03, CMP-04
- [ ] Phase 9: Paper Integration — CMP-05

Foundation delivered in the 2026-06-21 explore session: `src/bias/component_suite.py`,
`reports/COMPONENT_SUITE*.{md,csv}`. Next: `/gsd-discuss-phase 7` → `/gsd-plan-phase 7`.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Reorganize | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 2. Verify | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 3. Paper | v1.0 | 1/1 | ✓ Complete | 2026-05-30 |
| 4. Metrics API | v1.1 | 1/1 | ✓ Complete | 2026-05-30 |
| 5. Consequences Study & Converged Metrics | v1.1 | 2/2 | ✓ Complete | 2026-05-30 |
| 6. Handoff Docs | v1.1 | 1/1 | ✓ Complete | 2026-05-31 |
| 7. Suite & Universe Reconciliation | v1.2 | 0/? | ◌ Planned | — |
| 8. Multi-System Comparison & Fitness Validation | v1.2 | 0/? | ◌ Planned | — |
| 9. Paper Integration | v1.2 | 0/? | ◌ Planned | — |
