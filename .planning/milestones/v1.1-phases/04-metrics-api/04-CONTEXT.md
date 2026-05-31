# Phase 4: Metrics API - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

A stdlib-only API that ingests a TransArc-format results file for a **sad-sam** or
**sad-code** run and emits the full metric set as both a CSV (Excel-openable, all
benchmark projects in one sheet) and a ready-to-paste LaTeX table. It reuses existing
metric code in `src/lib` + `src/bias` with zero reimplementation and no
benchmark-derived word lists.

Covers MTR-01..MTR-05. Tasks limited to sad-sam + sad-code (no sam-code this milestone).
</domain>

<decisions>
## Implementation Decisions

### Invocation & CLI Surface
- Invoked as a run-script: `python3 src/lib/metrics_api.py --task sad-sam` (matches repo "run script per area" convention).
- Lives at `src/lib/metrics_api.py` — central, reuses lib loaders directly.
- Default input scope = ALL benchmark projects, read from `results/<project>/<task>/` (satisfies MTR-04 "all projects in one sheet"); optional `--project` filter.
- `--task {sad-sam,sad-code}` is a required flag.

### Output (CSV + LaTeX)
- CSV layout = **wide**: one row per project, columns = each metric, plus a mean/avg row.
- Output paths: CSV → `reports/`, LaTeX → `writing/tables/` (matches existing convention from `generate_tables.py`).
- LaTeX reuses `src/paper/generate_tables.py` helpers (`render_table`, `latex_escape`, `colspec`, `write_table`) — booktabs + caption + label.
- File names: `reports/metrics_<task>.csv` + `writing/tables/metrics_<task>.tex`.
- Skip a project + warn (continue) when its results file is missing — no hard error.

### Metric Set & Granularities (CORRECTED — see code_context)
- **Unified column schema with N/A cells**: one column superset across both tasks; granularities that do not apply to a task render as "—".
- **SAD-SAM granularities** (NO files — direct `(modelElementID, sentence)` pairs, no enrollment):
  - **Link/pair-level** — exact `(modelElementID, sentence)` match. Headline; equals decision-level (every pair is one human decision, zero enrollment inflation).
  - **Sentence-level** — sentence traced to correct component(s).
  - **Component-level** — aggregate by `modelElementID` (architecture component/interface).
  - Applicable alt metrics: **MCC**, **MAP** (ranked). ACF1/NDG/HUS are sad-code-only (require `gold_sam_code_map`) → N/A.
- **SAD-CODE granularities** (enrollment via `.acm` model):
  - **File-level** (enrolled) — the misleading headline.
  - **Decision-level** (raw, pre-enrollment) — the honest measure.
  - **Component-level**, **Weighted-level** (inverse-expansion-weighted).
  - Alt metrics: **ACF1, NDG, HUS, MCC**.
- **Convergence axis (feeds Phase 5 STUDY-03):** the common honest granularities across BOTH tasks are **Decision-level + Component-level**. For sad-sam decision==link (no inflation); for sad-code decision==raw pre-enrollment. Component-level aggregates both to architecture components → one coherent evaluation story.

### Reuse Strategy (non-negotiable)
- Import existing functions, no reimplementation:
  - `transarc_error_analysis.py`: `PROJECTS`, loaders, `calc_metrics`, `enroll_gold_standard`, `load_code_model_files`.
  - `evaluation_critique.py`: `_compute_decision_f1`, `_compute_component_f1`, `_compute_weighted_f1` (sad-code granularities).
  - `new_metrics_analysis.py`: `compute_mcc`, `compute_map`, `compute_acf1`, `compute_ndg`, `compute_hus`.
  - `generate_tables.py`: LaTeX render helpers.
- Zero benchmark-derived word lists (stopwords only) per workspace CLAUDE.md.

### Claude's Discretion
- Exact internal structure of the metric-row dataclass / dict and how the unified column superset is ordered.
- Whether to factor any reused helpers into `src/lib` if an import is awkward from `src/bias` (prefer import-as-is; refactor only if blocked).
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/lib/transarc_error_analysis.py` — `PROJECTS`, `BENCHMARK`, `RESULTS`, `calc_metrics(gold,result)->(p,r,f1,tp,fp,fn)`, `enroll_gold_standard`, `load_code_model_files`, gold/result loaders for sad-sam (`load_gs_sad_sam`, `load_result_sad_sam_standalone`) and sad-code (`load_gs_sad_code_enrolled`, `load_gs_sad_code_raw`, `load_result_sad_code`).
- `src/bias/evaluation_critique.py` — `_compute_decision_f1`, `_compute_component_f1`, `_compute_weighted_f1` (all SAD-CODE enrollment-based; need `raw_to_enrolled`, `file_to_comps`, `enrolled_to_raw` maps).
- `src/lib/new_metrics_analysis.py` — `compute_mcc(gold,result,all_sentences,all_components)`, `compute_map`, `compute_acf1`, `compute_ndg`, `compute_hus`.
- `src/paper/generate_tables.py` — `render_table(rows,caption,label,note,header_override)`, `latex_escape`, `colspec`, `write_table(name,content)` → `writing/tables/`.

### Established Patterns
- Scripts insert `src/lib` on `sys.path` and import shared loaders; outputs land in `reports/` (md/csv) and `writing/tables/` (tex).
- Hardcoded absolute paths to BENCHMARK/RESULTS/reports at module top.
- `calc_metrics` is exact-set P/R/F1; all granularities are built by transforming the link set then calling `calc_metrics`.

### Key Correction (why File≠universal)
- File/Decision/Component/Weighted granularities are SAD-CODE enrollment artifacts (directory gold entries expanded to files via `.acm`). SAD-SAM has none of these — it is link/sentence/component only. The API must NOT emit a File column for sad-sam.

### Integration Points
- New file `src/lib/metrics_api.py`; writes `reports/metrics_<task>.csv` and `writing/tables/metrics_<task>.tex`.
</code_context>

<specifics>
## Specific Ideas

- User explicitly flagged the original "File P/R/F1 for sad-sam" framing as wrong: "for sad-sam metrics, there is no file ... maybe sentence or component level?" — corrected to Link + Sentence + Component.
- Unified schema chosen so a future combined sheet (sad-sam + sad-code) is possible; inapplicable cells = "—".
</specifics>

<deferred>
## Deferred Ideas

- sam-code task metrics (out of scope this milestone).
- True `.xlsx` workbook (would add openpyxl; CSV keeps stdlib-only).
- Renaming `transarc_error_analysis.py` → `data_loaders.py`.
</deferred>
