---
plan: 03-01
phase: 3
title: "Restructure eval.tex into Ch1=TransArc + Ch2=Bias; generate tables from data"
status: complete
date: 2026-05-30
---

# Summary: Phase 3 Paper — Plan 03-01

Restructured `writing/eval.tex` to the two-pillar structure and added a
data-driven LaTeX table generator. Authored via a subagent (content/reads/writes),
verified + committed inline by the orchestrator (mount makes subagent git unsafe).

## Deliverables

| File | What |
|------|------|
| `writing/ch1_transarc.tex` (new) | Ch1 "The TransArc Empirical Study" (`\label{ch:transarc}`), `\input` by eval.tex |
| `writing/eval.tex` (edited) | `\input{ch1_transarc}` after `\begin{document}`; two former chapters merged into one Ch2 "Benchmark Bias and Evaluation Metrics" (`\label{ch:bias}`), former chapter titles demoted to `\section` |
| `src/paper/generate_tables.py` (new) | Stdlib-only generator; parses retained `reports/*.md` + `S12C_VS_TRANSARC.csv` → booktabs LaTeX |
| `writing/tables/*.tex` (10, generated) | transarc_overview, sadsam_contribution, sadsam_tp_gain, sadsam_coverage, error_amplification, fp_attribution, samcode_cascade, theoretical_limit, s12c_four_level (Ch1); dashboard (Ch2) |

## Ch1 Content (full, numbers traced to reports)

- **SAD-SAM bottleneck**: 93.7% of all TransArc FPs attributed to SAD-SAM stage
  (vs 3.3% SAM-CODE) — `reports/TRANSARC_EMPIRICAL_STUDY.md`, `fp_attribution` table.
- **Error amplification**: enrollment amplifies one upstream FP into 1–3 orders of
  magnitude of file-level FPs (e.g. JabRef single-decision 972-file blowup;
  Teammates mean ~85.5×) — `error_amplification` table.
- **SAD-SAM contribution + TP-gain** — `SAD_SAM_ACTUAL_CONTRIBUTION.md`,
  `SAD_SAM_TP_GAIN_STUDY.md`.
- **SAM-CODE cascade** — `SAM_CODE_CASCADE.md`.
- **S12C/S12E vs TransArc** four-level comparison — `reports/S12C_VS_TRANSARC.csv`.

## Requirements Covered

PAPER-01 (Ch1=TransArc), PAPER-02 (Ch2=Bias, two chapters merged),
PAPER-03 (every table traces to a retained script/report via the generator),
PAPER-04 (reframed: structural validation passes; no pdflatex per user).

## Notes / Deviations

- **SC4 reframed by user**: no local LaTeX toolchain and chapters feed a larger
  external paper, so the milestone target is a data-driven table generator +
  structural validation, not a `pdflatex` PDF build. ROADMAP SC4 updated accordingly.
- **eval.tex is a full standalone document** (`\begin{document}`, macros
  `\fone`/`\acfone`/`\transarc` predefined) — my earlier "fragment" reading was a
  hostshare-mount read corruption; the subagent read it clean and preserved structure.
- Generator is `from __future__ import annotations` + csv/re/pathlib only; no
  benchmark-derived word lists (project/column names are opaque data read from reports).
