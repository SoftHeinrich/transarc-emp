# Phase 6: Handoff Docs - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

A top-level `README.md` that (a) maps the repo's two pillars — what each is and where
its code, reports, and paper chapter live (DOC-01) — and (b) gives per-pillar
run/reproduce instructions so a new reader can regenerate either pillar's reports
from scratch (DOC-02). Covers DOC-01, DOC-02. No code changes beyond the README
(and any small doc files); existing scripts already produce all reports.
</domain>

<decisions>
## Implementation Decisions

### README Structure & Mapping (DOC-01)
- **Single top-level `README.md`** at repo root. Per-pillar reproduce instructions are inline sections (not split into docs/).
- **Pillar mapping presented as a table**: each pillar → {code dirs, key scripts, output reports, paper chapter}.
- **Scope/audience:** a new researcher/reviewer. State prerequisites (Python 3, the external benchmark data path) and link to `CLAUDE.md`/`../CLAUDE.md` for deeper dev rules rather than duplicating them. Not a full tutorial.
- **Two pillars (from repo structure):**
  - **Pillar 1 — TransArc empirical study:** code `src/transarc/` + `src/lib/`; paper `writing/ch1_transarc.tex` (eval.tex Ch1).
  - **Pillar 2 — Benchmark bias & metrics:** code `src/bias/` + `src/lib/` + Phase-4/5 tooling (`src/lib/metrics_api.py`, `src/bias/consequences_study.py`, `src/paper/generate_tables.py`); paper `writing/eval.tex` Ch2.

### Reproduce Instructions & Validation (DOC-02)
- **Granularity:** per-pillar "regenerate reports" section listing each script → its output report/table, runnable top-to-bottom (e.g. `python3 src/<area>/<script>.py`).
- **Cover Phase 4/5 tooling:** document `metrics_api.py` (`--task sad-sam|sad-code` → `reports/metrics_*.csv` + `writing/tables/metrics_*.tex`), `consequences_study.py` (→ `reports/CONSEQUENCES_STUDY.md`), and `generate_tables.py` (→ `writing/tables/*.tex`, consumed by `eval.tex`).
- **Prerequisites documented:** external benchmark data path (`/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`) and stdlib-only (no `pip install`, no requirements.txt).
- **Validation (no pdflatex):** spot-run one representative script per pillar to confirm the documented command produces the named output; plus structural check that README has the pillar-map + both reproduce sections.

### Script → Output map (verified, for the reproduce sections)
- **Pillar 1 (transarc):** `transarc_error_analysis.py`→TRANSARC_EMPIRICAL_STUDY.md; `sad_sam_actual_contribution.py`→SAD_SAM_ACTUAL_CONTRIBUTION.md; `sad_sam_tp_gain_analysis.py`→SAD_SAM_TP_GAIN_STUDY.md; `sam_code_cascade_analysis.py`→SAM_CODE_CASCADE.md; `s12c_sadcode_comparison.py`→S12C_VS_TRANSARC.csv.
- **Pillar 2 (bias/metrics):** `benchmark_bias_study.py`→BENCHMARK_BIAS_STUDY.md; `evaluation_critique.py`→EVALUATION_CRITIQUE.md; `enrollment_bias_analysis.py`→ENROLLMENT_BIAS_ANALYSIS.md; `extreme_baseline_analysis.py`→EXTREME_BASELINES.md; `stupid_baseline_analysis.py`→STUPID_BASELINES.md; `holistic_metrics_analysis.py`→HOLISTIC_METRICS.md; `creative_metrics_analysis.py`→CREATIVE_METRICS.md; `sam_code_distribution_analysis.py`→SAM_CODE_DISTRIBUTION.md; `new_metrics_analysis.py`→NEW_METRICS_REPORT.md; `metrics_api.py`→metrics_*.csv/.tex; `consequences_study.py`→CONSEQUENCES_STUDY.md.
- **Paper:** `generate_tables.py`→writing/tables/*.tex (\input by eval.tex).

### Claude's Discretion
- Exact README section ordering, headings, and prose tone.
- Whether `enrollment_distortion_analysis.py` (intermediate, no clear single OUTPUT_MD) is listed as a supporting/intermediate script or omitted — planner/executor decides after reading it.
- Which specific script is the "representative" spot-run per pillar.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- All report-generating scripts already exist and run stdlib-only; outputs already present in `reports/` (19 files) and `writing/tables/`.
- `CLAUDE.md` (project) and `../CLAUDE.md` (workspace) already document build/eval/leakage rules — README links to them, does not duplicate.
- `archive/README.md` exists (archived material) — the new README is at repo ROOT and is separate.

### Established Patterns
- Run a script: `python3 src/<area>/<script>.py`; outputs land in `reports/` (md/csv) or `writing/tables/` (tex).
- Shared loaders in `src/lib` imported via sys.path insert.

### Integration Points
- New `README.md` at repo root (the only required new file).
</code_context>

<specifics>
## Specific Ideas

- The script→report map above is verified from the actual `OUTPUT_MD`/path constants in each script — reuse it verbatim for the reproduce tables.
- Two-pillar framing matches the project's stated v1.0 refactor (PROJECT.md / CLAUDE.md).
</specifics>

<deferred>
## Deferred Ideas

- Real pdflatex PDF build instructions (no local toolchain — note as a known limitation only).
- Renaming `src/lib/transarc_error_analysis.py` → `data_loaders.py` (deferred cleanup; README documents current name).
</deferred>
