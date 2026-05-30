---
phase: 05-consequences-study-converged-metrics
plan: 01
subsystem: bias-analysis
tags: [consequences, sad-sam, sad-code, converged-metrics, stdlib, report]
requires:
  - reports/metrics_sad-sam.csv
  - reports/metrics_sad-code.csv
provides:
  - src/bias/consequences_study.py
  - reports/CONSEQUENCES_STUDY.md
affects:
  - Phase-5 Plan-02 paper write-up (cites CONSEQUENCES_STUDY.md anchors)
tech-stack:
  added: []
  patterns:
    - "out() markdown accumulator (single final write) from evaluation_critique.py"
    - "csv.DictReader load_metrics_csv(task) -> (rows_by_project, avg_row); read Average row, never recompute"
    - "em-dash N/A handling via num() helper; headline-vs-honest delta differencing"
key-files:
  created:
    - src/bias/consequences_study.py
    - reports/CONSEQUENCES_STUDY.md
  modified: []
decisions:
  - "Read the literal Average row from each CSV (F1 as 0-1 decimals) — no division by 100, no recomputed averages"
  - "Only Δ columns are computed; every absolute number is read from the CSVs (STUDY-02 no-recompute mandate)"
  - "SAD-SAM link−decision Δ framed as 0.000 (headline already at decision granularity); its distortion is the sentence/quality gap, not enrollment"
metrics:
  duration_minutes: 8
  completed: 2026-05-30
  tasks: 2
  files: 2
---

# Phase 5 Plan 01: Consequences Study & Converged Metrics Summary

Stdlib-only `consequences_study.py` reads both Phase-4 metrics CSVs and emits `reports/CONSEQUENCES_STUDY.md` — a three-section motivation report (SAD-SAM pure-F1 disagreement, SAD-CODE file-level enrollment distortion, and the converged Decision+Component axis) whose every absolute number is read, not recomputed.

## What Was Built

- **`src/bias/consequences_study.py`** (271 lines, stdlib only: `csv`, `pathlib.Path`). Helpers `load_metrics_csv(task)` (returns `(rows_by_project, avg_row)`), `num()` (em-dash → None), `fmt()`, `delta()`. Three section functions plus an `out()`-accumulator `main()`.
  - `part_sad_sam` (STUDY-01): per-project pipe table Link/Sentence/Component/MCC/MAP/HUS + computed Link−Sentence Δ, Average row read from CSV. Prose flags teammates (sentence 0.916 vs link 0.710, ~0.206 understatement) and the MCC/MAP/HUS quality divergence.
  - `part_sad_code` (STUDY-02): per-project File/Decision/Component + File−Decision Δ table; consolidates the JabRef ranking flip (File 0.943 #1 → Decision 0.394 #5) and avg File 0.803 / Decision 0.596 / Component 0.714, explicitly citing `EVALUATION_CRITIQUE.md` + `BENCHMARK_BIAS_STUDY.md` with NO recomputation.
  - `part_converged` (STUDY-03): maps both tasks to the Decision+Component axis, a 2-row comparison table (SAD-SAM headline link 0.799; SAD-CODE headline file 0.803, decision 0.596, Δ 0.207), a ranking-disagreement count, and an extend-not-replace recommendation.
- **`reports/CONSEQUENCES_STUDY.md`** — generated artifact, three `##` sections matching STUDY-01/02/03.

## Verification

- `python3 src/bias/consequences_study.py` exits 0 and regenerates the report.
- All required anchors present in the report: `0.394`, `0.943`, `0.916`, `0.803`, `0.596`, `0.714`, `0.207`.
- Imports are stdlib only (`csv`, `pathlib.Path`); `grep transarc_error_analysis` returns nothing.
- Report contains a SAD-SAM table (Link + Sentence columns), a SAD-CODE table (File + Decision columns), and a converged table (Decision + Component columns).

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new security-relevant surface. Script reads two committed local CSVs and writes one hardcoded-absolute-path markdown file under `reports/` (matches the plan threat model T-05-01/02/03 dispositions). T-05-02 mitigation satisfied: no benchmark-derived word lists; project names are opaque CSV ordering data.

## Known Stubs

None. The report is fully wired to live CSV data; no placeholders.

## Self-Check: PASSED

- FOUND: src/bias/consequences_study.py
- FOUND: reports/CONSEQUENCES_STUDY.md
- FOUND commit: dd2cdbc (feat 05-01 SAD-SAM + SAD-CODE sections)
- FOUND commit: c88df5c (feat 05-01 converged framework section)
