---
phase: 05-consequences-study-converged-metrics
plan: 02
subsystem: paper
tags: [paper, latex, booktabs, generate-tables, eval-tex, converged-metrics]
requires:
  - reports/metrics_sad-sam.csv
  - reports/metrics_sad-code.csv
  - reports/CONSEQUENCES_STUDY.md
  - src/paper/generate_tables.py (render_table/write_table helpers)
provides:
  - writing/tables/consequences.tex (headline-vs-honest, both tasks)
  - writing/tables/converged_framework.tex (converged Decision+Component axis)
  - eval.tex Ch2 motivation section sec:eval:misleading-both
  - eval.tex sec:eval:protocol converged-axis extension
affects:
  - writing/eval.tex
tech-stack:
  added: []
  patterns:
    - "CSV-backed booktabs builders single-sourced from Phase-4 metrics_*.csv"
    - "render_table raw_cols param for macro-bearing data cells"
key-files:
  created:
    - writing/tables/consequences.tex
    - writing/tables/converged_framework.tex
  modified:
    - src/paper/generate_tables.py
    - writing/eval.tex
decisions:
  - "render_table gained raw_cols= to emit macro-bearing data cells verbatim (Task column \\sadsam/\\sadcode)"
metrics:
  duration: 6m
  completed: 2026-05-30
  tasks: 2
  files: 4
---

# Phase 5 Plan 02: Consequences Study as Paper Material Summary

Added two CSV-backed booktabs table generators (`t_consequences`, `t_converged_framework`) to `generate_tables.py` and wove them into `eval.tex` as a new Chapter-2 motivation section on misleading \fone across both tasks plus a converged Decision+Component protocol extension — single-sourced from the Phase-4 metrics CSVs, structurally validated without pdflatex.

## What Was Built

**Task 1 — table builders (commit a0ef389):**
- `_load_metrics(task)` + `_fmt_dec(v)` helpers reading the 0–1-decimal `metrics_sad-sam.csv` / `metrics_sad-code.csv` (existing `_load_csv`/`_fmt_f1`/`CSV_FILE` left untouched). `_fmt_dec` maps the em-dash N/A cell to `--` and formats with `%.3f` (no `/100`).
- `t_consequences()` — one table, both tasks: SAD-SAM block (headline = link \fone) then SAD-CODE block (headline = file \fone, sentence \fone → `--`), 5 projects + Average row each, read in CSV order.
- `t_converged_framework()` — 2-row average-only table with computed Headline−Decision deltas (SAD-SAM 0.000, SAD-CODE 0.207).
- Both registered in `main()` builders list under the Chapter-2 comment after `t_dashboard`. `TOTAL` is now 12 (was 10).

**Task 2 — eval.tex (commit 1d5e526):**
- New `\section{Misleading \fone Across Both Tasks}` / `\label{sec:eval:misleading-both}` after `sec:comprehensive-metrics`, with `\Cref{tab:consequences}` and `\input{tables/consequences}`. Covers the Teammates 0.916-vs-0.710 sentence/link gap and the JabRef file-0.943/decision-0.394 reordering.
- `sec:eval:protocol` extended with `\paragraph{A converged axis for both tasks.}` + `\Cref{tab:converged-framework}` + `\input{tables/converged_framework}` after the existing (unmodified) enumerate. Frames decision+component \fone as a layer atop the corrected metrics.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `\sadsam`/`\sadcode` macros in data cells were mangled by `latex_escape`**
- **Found during:** Task 1 (first generator run)
- **Issue:** The plan specified `\\sadsam`/`\\sadcode` macros in the Task data column, but `render_table` escapes ALL data cells (only the header gets `header_override`). The macros came out as `\textbackslash{}sadsam`, which would render as literal text `\sadsam` in the PDF instead of expanding to "SAD-SAM" — a correctness bug in the generated artifact.
- **Fix:** Added an optional `raw_cols=` parameter to `render_table` (set of 0-based column indices whose data cells are emitted verbatim), and passed `raw_cols=[0]` from both new builders. Header behavior, `_fmt_f1`, and all existing builders are unaffected (default `raw_cols=None`).
- **Files modified:** `src/paper/generate_tables.py`
- **Verification:** `grep -c textbackslash` on both generated tables now returns 0; macros emit as `\sadsam &`/`\sadcode &`.
- **Commit:** a0ef389 (folded into the Task 1 commit)

## Authentication Gates

None.

## Verification

- `python3 src/paper/generate_tables.py` exits 0, prints `TOTAL 12`, writes both new `.tex` files.
- `consequences.tex`: valid booktabs float; contains `\toprule`/`\bottomrule`/`\fone`, `0.394`, `0.916`, `0.943`; SAD-CODE sentence column is `--`; no `\textbackslash`.
- `converged_framework.tex`: contains `tab:converged-framework`, `$\Delta$`, deltas `0.000` (SAD-SAM) and `0.207` (SAD-CODE); no `\textbackslash`.
- `eval.tex`: one `\begin{document}` / one `\end{document}` (last line); `sec:comprehensive-metrics` and `sec:eval:f1` preserved; new `\label{sec:eval:misleading-both}`; both `\Cref{tab:...}` precede their `\input`; all `\Cref` targets have matching `\label` in the generated tables.
- Source-notes cite only retained material (`reports/metrics_*.csv`, `reports/CONSEQUENCES_STUDY.md`, `reports/EVALUATION_CRITIQUE.md`).

## Known Stubs

None.

## Threat Flags

None — filesystem-only generator over committed CSVs; no new trust-boundary surface.

## Self-Check: PASSED

All created/modified files present; both task commits (a0ef389, 1d5e526) found in git log.
