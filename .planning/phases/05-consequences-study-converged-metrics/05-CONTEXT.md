# Phase 5: Consequences Study & Converged Metrics - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

A motivation analysis (Pillar 2 extension) that quantifies, with numbers, how a
misleading headline F1 distorts BOTH SAD-SAM (pure link F1) and SAD-CODE
(file-level enrollment F1), and proposes a converged metric framework giving the
two tasks one coherent evaluation story. Written up as a paper section extending
Chapter 2 (Benchmark bias) of `writing/eval.tex`.

Covers STUDY-01..STUDY-04. Reuses Phase-4 metrics outputs and existing Pillar 2
reports as evidence; cites only retained scripts/reports.
</domain>

<decisions>
## Implementation Decisions

### Analysis Approach & Evidence
- **STUDY-01 (SAD-SAM pure-F1 consequences — genuinely new):** Derive from Phase-4 `reports/metrics_sad-sam.csv` — the disagreement across link vs sentence vs component granularities plus MCC/MAP/HUS — supplemented by existing `SAD_SAM_ACTUAL_CONTRIBUTION.md`, `SAD_SAM_TP_GAIN_STUDY.md`, `METRIC_LIMITATIONS_ANALYSIS.md`. Show what the single SAD-SAM headline F1 hides/distorts.
- **STUDY-02 (SAD-CODE file-level consequences):** Consolidate existing findings from `EVALUATION_CRITIQUE.md` / `BENCHMARK_BIAS_STUDY.md` (enrollment inflation 35.5x, block homogeneity, ranking flips, JabRef File 0.943 → Decision 0.394) as motivation evidence — NO recomputation.
- **New script:** ONE `src/bias/consequences_study.py` that loads both Phase-4 metrics CSVs (`reports/metrics_sad-sam.csv`, `reports/metrics_sad-code.csv`) + reads existing reports, computes the cross-granularity disagreement evidence (e.g. headline-vs-honest deltas, ranking disagreements), and emits `reports/CONSEQUENCES_STUDY.md`.
- **Leakage guard (non-negotiable):** zero benchmark-derived word lists; stopwords only (none needed here — pure numeric analysis).

### Converged Metric Framework (STUDY-03)
- **Definition:** the common honest evaluation axis = **Decision-level + Component-level** applied to BOTH tasks.
  - SAD-SAM: decision == link (`(modelElementID, sentence)`, no enrollment inflation); component == aggregate by model element.
  - SAD-CODE: decision == raw pre-enrollment `(sentence, dir-or-file)`; component == aggregate by architecture component.
- **Presentation:** a comparison table — per task, headline F1 (file for sad-code, link for sad-sam) vs the converged decision+component F1 — showing the headline misleads while the converged view tells one coherent story. Reuse the Phase-4 metrics CSVs as the data source.
- **Position:** a unifying recommendation layered ATOP the existing Ch2 corrected metrics (ACF1, weighted, etc.), extending `sec:eval:protocol` — it does NOT replace existing metrics.

### Paper Write-up & Validation (STUDY-04)
- **Placement:** a new motivation section inside Chapter 2 of `writing/eval.tex` ("misleading F1 across BOTH tasks"), plus an extension to the evaluation protocol (`sec:eval:protocol`) presenting the converged framework. New `.tex` content authored directly into eval.tex (or an \input file consistent with the ch1_transarc.tex pattern).
- **Tables:** add generator function(s) to `src/paper/generate_tables.py` for the consequences + converged tables, emitting to `writing/tables/` (consistent with existing table pipeline).
- **Validation (no pdflatex toolchain):** structural check only — new \section/\label present, generated tables exist and are structurally valid (tabular/booktabs), \ref/\cref targets resolve, and citations reference only retained scripts/reports.
- **Citations scope:** cite only retained scripts/reports (per STUDY-04) — no references to archived/removed material.

### Claude's Discretion
- Exact section title/label names and ordering within Ch2.
- Whether the new prose goes inline in eval.tex or in a new \input file (follow ch1_transarc.tex precedent if split).
- Precise columns/shape of the consequences and converged tables.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase-4 outputs:** `reports/metrics_sad-sam.csv`, `reports/metrics_sad-code.csv` (link/sentence/component + MCC/MAP/HUS for sad-sam; file/decision/component/weighted + MCC/ACF1/NDG/HUS for sad-code) — the primary numeric evidence.
- **Pillar 2 reports:** `reports/EVALUATION_CRITIQUE.md`, `BENCHMARK_BIAS_STUDY.md`, `METRIC_LIMITATIONS_ANALYSIS.md`, `SAD_SAM_ACTUAL_CONTRIBUTION.md`, `SAD_SAM_TP_GAIN_STUDY.md`, `NEW_METRICS_REPORT.md`, `EXTREME_BASELINES.md`, `STUPID_BASELINES.md`, `HOLISTIC_METRICS.md`, `CREATIVE_METRICS.md`.
- **Bias scripts:** `src/bias/evaluation_critique.py` (decision/component/weighted F1 + part5 alt metrics + part7 synthesis), `src/bias/benchmark_bias_study.py`. `src/lib/transarc_error_analysis.py` loaders.
- **Paper pipeline:** `src/paper/generate_tables.py` (`render_table`, `latex_escape`, `colspec`, `write_table` → `writing/tables/`; `_load_csv` helper for CSV-backed tables — see `t_s12c_four_level`).
- **Paper:** `writing/eval.tex` — Ch1 = `\input{ch1_transarc}`; Ch2 "Benchmark Bias and Evaluation Metrics" with `sec:distributional-inequality` (enrollment/block/amplification/skew/incomparable/ranking) and `sec:comprehensive-metrics` (f1, classification, corrected, sentence, code, bridge, utility, component, cascade, dashboard, assessment, protocol). SAD-SAM currently appears only as the cascade SOURCE, not analyzed as a standalone-misleading metric.

### Established Patterns
- Reports are generated markdown in `reports/`; table generators in `generate_tables.py` read a report/CSV and write a `.tex` file in `writing/tables/`, then eval.tex `\input`s them.
- LaTeX macros already defined: `\sadsam`, `\sadcode`, `\samcode`, `\fone`, `\acfone`.

### Integration Points
- New: `src/bias/consequences_study.py` → `reports/CONSEQUENCES_STUDY.md`.
- New table generator(s) in `src/paper/generate_tables.py` → `writing/tables/*.tex`.
- New section(s) in `writing/eval.tex` Ch2 + extended `sec:eval:protocol`.
</code_context>

<specifics>
## Specific Ideas

- The Phase-4 convergence insight (logged in 04-CONTEXT) is the backbone of STUDY-03: decision+component is the common honest axis where sad-sam (no enrollment) and sad-code (de-enrolled) tell the same story.
- Concrete anchor numbers already validated: sad-code JabRef File 0.943 → Decision 0.394 (ranking flip); avg File 0.803 vs Decision 0.596 vs Component 0.714.
</specifics>

<deferred>
## Deferred Ideas

- Real pdflatex PDF build of eval.tex (no local toolchain).
- Extending the converged framework to sam-code (milestone scopes sad-sam + sad-code).
</deferred>
