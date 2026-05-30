# Phase 3: Paper - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Restructure `writing/eval.tex` to match the two-pillar structure:
- **Ch1 = TransArc empirical study** (NEW, full chapter).
- **Ch2 = Benchmark bias** (merge the two EXISTING chapters — "Distributional
  Inequality in the ARDoCo Benchmark" + "Comprehensive Evaluation Metrics for
  SAD-CODE Traceability" — into one).

Plus a **table-generation script** that emits LaTeX tables from the retained
reports/results data (reproducible, not hand-typed). Out of scope: new analysis,
changing pillar scripts, full PDF compilation.
</domain>

<decisions>
## Implementation Decisions

### LaTeX compile (SC4 reframed by user)
- **No `pdflatex` compile required** — no local toolchain; chapters are authored
  into a larger external paper. eval.tex is a fragment (starts with
  `\documentclass` + custom macros + chapters; has NO `\begin{document}`).
- Verification = **structural validation only**: balanced `\begin{}`/`\end{}`
  environments, balanced braces, every `\ref`/`\cref` has a matching `\label`,
  every `\input{}` target exists.

### Tables from data via script (user's primary ask)
- Add a stdlib-only Python script that reads the retained `reports/` data (and/or
  re-derives from `src/lib` loaders) and writes LaTeX table files into
  `writing/tables/*.tex`. Chapters `\input{tables/<name>}` these.
- Script location: `src/paper/generate_tables.py` (new Pillar-neutral tooling dir).
- Must follow CLAUDE.md: stdlib only, no benchmark-derived word lists.

### Ch1 scope (user chose "Full chapter from all reports")
- Full chapter covering: SAD-SAM bottleneck, error amplification/cascade,
  SAD-SAM actual contribution + TP-gain, SAM-CODE cascade, and the S12C/S12E
  vs TransArc comparison.
- Sources (retained reports): `TRANSARC_EMPIRICAL_STUDY.md` (814 ln),
  `SAD_SAM_ACTUAL_CONTRIBUTION.md` (527), `SAD_SAM_TP_GAIN_STUDY.md` (576),
  `SAM_CODE_CASCADE.md` (259), `reports/S12C_VS_TRANSARC.csv`.

### Ch2 merge
- Combine the two current chapters into ONE "Benchmark bias" chapter: the
  Distributional Inequality material becomes the bias/enrollment-critique
  sections; the Comprehensive Metrics material becomes the proposed-metrics
  sections (baselines, F1 variants, enrollment-corrected metrics, protocol).
- Preserve all existing content/macros; only restructure chapter nesting.

### Traceability (SC3)
- Every table/figure/quantitative claim must trace to a retained script or report.
  Prefer `\input{}` of generated tables so the data lineage is explicit.

### Claude's Discretion
- Exact section ordering within Ch1; table set chosen for the generator; prose phrasing.
</decisions>

<code_context>
## Existing Code Insights

### Current eval.tex (990 lines, fragment)
- Preamble: `report` class + amsmath, booktabs, longtable, siunitx, hyperref,
  cleveref, etc. Macros: `\sadsam`, `\samcode`, `\sadcode` (textsc + xspace).
  NOTE: `\fone`, `\acfone` are USED but their `\newcommand` defs are NOT in the
  first lines — verify/define them if missing (else structural validation flags
  undefined-but-used is fine; only `\ref`/`\label`/`\input` are checked).
- Ch A `\chapter{Distributional Inequality in the ARDoCo Benchmark}` (line 28):
  sections Enrollment Inflation, Block Correlation, Error Amplification Asymmetry,
  Component-Size/Gold Skew, Cross-Project Incomparability, Ranking Instability,
  Summary of Inequality.
- Ch B `\chapter{Comprehensive Evaluation Metrics for \sadcode Traceability}`
  (line 379): F1 Variants, Classification Quality, Enrollment-Corrected,
  Sentence/Code-Centric, Bridge, Practical Utility, Component Coverage,
  Cascade-Weighted, Full Dashboard, Assessment, Recommended Protocol.

### Pillar scripts (data sources for the generator)
- `src/transarc/*.py` (4) + `src/bias/*.py` (9) + `src/lib/` loaders.
- Reports in `reports/` regenerate deterministically (Phase 2 confirmed).

### Environment caveat (CRITICAL for this phase)
- Hostshare mount intermittently CORRUPTS file reads (injects stale/hallucinated
  text, doubles lines, truncates). The Read tool failed entirely on eval.tex;
  clean reads require `sed -n 'A,Bp' file` with `dangerouslyDisableSandbox: true`.
  The Write tool is reliable. RULE: read in small `sed` slices (sandbox off),
  re-read once if output looks odd, and verify every Write by reading the file
  back. NEVER author edits from a read that contains "(truncated)" or repeated
  lines.
</code_context>

<specifics>
## Specific Ideas

- Generated tables live in `writing/tables/`; chapters `\input{tables/<name>}`.
- Keep the existing Ch2 content intact — restructure, don't rewrite.
</specifics>

<deferred>
## Deferred Ideas

- Actual `pdflatex` PDF build (no toolchain; external larger paper handles it).
- Bibliography/citations integration with the larger paper.
</deferred>
