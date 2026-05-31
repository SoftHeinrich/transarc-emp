# Phase 5: Consequences Study & Converged Metrics - Pattern Map

**Mapped:** 2026-05-30
**Files analyzed:** 3 (1 new, 2 modified)
**Analogs found:** 3 / 3 (all strong)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/bias/consequences_study.py` (NEW) | analysis script → report | transform (CSV in → markdown out) | `src/bias/evaluation_critique.py` (md `out()` writer) + `src/lib/metrics_api.py` (CSV-reader idiom) | exact (role) + role-match (CSV input) |
| `src/paper/generate_tables.py` (MODIFY) | paper table generator | transform (CSV → LaTeX) | `t_s12c_four_level` / `t_dashboard` (same file) + `metrics_api.write_latex` | exact |
| `writing/eval.tex` (MODIFY) | LaTeX paper source | document | existing Ch2 sections `sec:comprehensive-metrics` / `sec:eval:protocol` (same file) | exact |

---

## Pattern Assignments

### `src/bias/consequences_study.py` (NEW — analysis script, transform)

This is the only genuinely-new file. It has TWO complementary analogs: copy the
**markdown report writer** structure from `evaluation_critique.py` and the
**CSV-reading idiom** from `metrics_api.py`. It must consume the Phase-4 CSVs
(`reports/metrics_sad-sam.csv`, `reports/metrics_sad-code.csv`) rather than
recompute metrics — STUDY-02 explicitly says NO recomputation.

**Analog A — report writer:** `src/bias/evaluation_critique.py`

**Module header + stdlib imports + sys.path bootstrap** (lines 1-35) — copy verbatim shape (a `bias/` script imports lib loaders via `sys.path.insert(parent.parent/"lib")`). For Phase 5 the heavy `transarc_error_analysis` import block is likely UNNEEDED (pure CSV numeric analysis); keep only `csv`, `sys`, `pathlib.Path`, maybe `collections`:
```python
import csv
import sys
from collections import defaultdict
from pathlib import Path

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/EVALUATION_CRITIQUE.md")
```
For the new script: `OUTPUT_MD = Path(".../reports/CONSEQUENCES_STUDY.md")` (absolute-path convention, matches `metrics_api.REPORTS`).

**The `out()` accumulator + final write** (lines 1289-1321) — this is THE report-writing idiom to replicate. A local closure appends to `md_lines`, then one `open(...,"w")` write at the end:
```python
def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    out("# Evaluation Critique: ...")
    out()
    out("*A deep investigation ...*")
    out()

    all_data = part1_inflation(out)
    part2_block_correlation(out, all_data)
    ...
    part7_synthesis(out, all_data, ...)

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
        f.write("\n")
    print(f"\n\nReport written to {OUTPUT_MD}")
```

**Section-function signature + markdown-table emission** (`part7_synthesis`, lines 1152-1233) — each section is a function taking `out` (+ data) and emits markdown headers, prose, and pipe tables. Copy the table-row idiom and the "compute avg, find best, flag flips" pattern (directly reusable for STUDY-01 cross-granularity disagreement / STUDY-03 headline-vs-converged):
```python
def part7_synthesis(out, all_data, ...):
    out("## Part 7: Synthesis ...")
    out()
    out("| Metric | TransArc | V45 | LLM | V87-pc | Best |")
    out("|--------|----------|-----|-----|--------|------|")
    for label, ta_avg, v45_avg, llm_avg, v87_avg in [...]:
        vals = {"TransArc": ta_avg, ...}
        best = max(vals, key=vals.get)
        out(f"| {label} | {ta_avg:.3f} | ... | {best} |")
    out()
    # ranking-flip counter — reusable for "ranking disagreements" evidence
    flips = 0
    for proj in PROJECTS:
        winners = [...]
        if len(set(winners)) > 1:
            flips += 1
    out(f"In **{flips}/{n}** projects, changing the metric granularity flips which system wins.")
```

**Analog B — CSV reading of `reports/metrics_*.csv`:** `src/lib/metrics_api.py`

The Phase-4 CSV schema (header, then 5 project rows, then `Average` row; `—` em-dash marks N/A cells) is produced by `metrics_api.write_csv` (lines 247-257). Schema reference (lines 59-63):
```python
SCHEMA = [
    "project", "link_f1", "sentence_f1", "decision_f1", "component_f1",
    "file_f1", "weighted_f1", "mcc", "map", "acf1", "ndg", "hus",
]
NA = "—"   # CSV inapplicable cells
```
So the consumer reads with `csv.DictReader`, skips/handles the `Average` row, and parses numeric cells while treating `"—"` as N/A. The closest read idiom in the codebase is `evaluation_critique.load_sad_code_raw_with_provenance` (lines 57-60) and `generate_tables._load_csv` (below). Recommended consumer shape for the new script:
```python
REPORTS = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports")

def load_metrics_csv(task):
    """task in {'sad-sam','sad-code'}; returns (per_project_rows, avg_row)."""
    rows = []
    avg = None
    with (REPORTS / f"metrics_{task}.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["project"] == "Average":
                avg = r
            else:
                rows.append(r)
    return rows, avg

def num(v):
    return None if v in ("—", "", None) else float(v)
```

**Concrete anchor numbers (from CONTEXT specifics, already in the CSVs):**
sad-code JabRef File 0.943 → Decision 0.394 (ranking flip); avg File 0.803 vs Decision 0.596 vs Component 0.714. sad-sam Teammates sentence 0.916 vs link 0.710; avg link 0.799. These come straight from the two CSVs — the script derives "headline-vs-honest deltas" by differencing the headline column (file_f1 for sad-code, link_f1 for sad-sam) against the converged decision_f1 / component_f1 columns.

---

### `src/paper/generate_tables.py` (MODIFY — table generator, transform)

**Analog:** `t_s12c_four_level` (lines 353-397) and `t_dashboard` (lines 400-447) in the SAME file — the CSV-backed builder pattern. The executor ADDS new builder function(s) following this exact shape and REGISTERS them in `main()`.

**The CSV-backed builder pattern** (`t_s12c_four_level`, lines 353-397):
```python
def t_s12c_four_level():
    rows = _load_csv()
    header = [
        "Project", "File \\fone", "Decision \\fone",
        "Component \\fone", "Weighted \\fone",
    ]
    data = []
    for r in rows:
        data.append([r["dataset"], _fmt_f1(r["ta_file_F1"]), ...])
    # cross-project average row
    avg = ["Average"]
    for col in ("ta_file_F1", "ta_dec_F1", "ta_comp_F1", "ta_wt_F1"):
        vals = [float(r[col]) / 100.0 for r in rows if r.get(col)]
        avg.append("%.3f" % (sum(vals) / len(vals)))
    data.append(avg)
    return write_table(
        "s12c_four_level",
        render_table(
            [header] + data,
            caption="Four-level \\sadcode evaluation of \\transarc: ...",
            label="tab:s12c-four-level",
            note="Source: \\texttt{reports/S12C\\_VS\\_TRANSARC.csv} ...",
            header_override=header,   # REQUIRED when header contains \fone macros
        ),
    )
```

**CRITICAL idioms the executor must replicate:**
- `header_override=header` is MANDATORY whenever a column header contains a LaTeX macro (`\fone`, `\sadsam`, ...). Without it `render_table` runs `latex_escape` on the header and would mangle the backslash. See `render_table` lines 136-144.
- `_fmt_f1` (lines 346-350) divides by 100 because `S12C_VS_TRANSARC.csv` stores F1 as a percentage. **The Phase-4 `metrics_*.csv` files store F1 as a 0–1 decimal already** (e.g. `0.943`) — so the new builder must NOT divide by 100. Use a plain `"%.3f" % float(v)` formatter (or pass through), and treat the `"—"` em-dash as `"--"` (see `metrics_api.NA_TEX = "--"`, line 66, and its `write_latex` cell loop lines 260-266).
- The Phase-4 CSV already contains an `Average` row, so the new builder can read it directly instead of recomputing the average (unlike `_load_csv` which filters out `MACRO_AVG`).

**New `_load_csv`-style reader:** `_load_csv` (lines 339-343) is hardwired to `CSV_FILE = S12C_VS_TRANSARC.csv`. The new builder needs a parameterized reader for `reports/metrics_<task>.csv`. Add a sibling helper near line 339, e.g.:
```python
METRICS_CSV = {
    "sad-sam":  REPORTS / "metrics_sad-sam.csv",
    "sad-code": REPORTS / "metrics_sad-code.csv",
}
def _load_metrics(task):
    with METRICS_CSV[task].open(encoding="utf-8") as f:
        return list(csv.DictReader(f))   # includes the Average row
```
(`REPORTS`, `OUT`, `ROOT` already defined lines 28-30. `render_table`/`write_table` already imported in-file.)

**Registry — `main()`** (lines 451-469): every builder is a zero-arg function appended to the `builders` list, called once, and its returned `Path` printed. The executor MUST add the new builder(s) to this list under a Chapter-2 comment:
```python
def main():
    builders = [
        # Chapter 1 (TransArc empirical study)
        t_transarc_overview, ... t_s12c_four_level,
        # Chapter 2 (Benchmark bias / metrics)
        t_dashboard,
        t_consequences,        # NEW — STUDY-01/02 headline-vs-honest deltas
        t_converged_framework, # NEW — STUDY-03 converged decision+component table
    ]
    written = [b() for b in builders]
    for p in written:
        print("WROTE", p.relative_to(ROOT))
    print("TOTAL", len(written))
```

**Output target:** `write_table(name, content)` (lines 169-173) writes `writing/tables/<name>.tex`. New tables land beside the existing 12 (`writing/tables/*.tex`).

---

### `writing/eval.tex` (MODIFY — LaTeX document)

**Analog:** the existing Ch2 sections in the SAME file — `sec:comprehensive-metrics` (lines 389-401) for a new analysis/motivation section, and `sec:eval:protocol` (lines 986-1004) which the converged framework EXTENDS (not replaces).

**Macros available** (lines 16-21) — use these, never spell out task names:
```latex
\newcommand{\sadcode}{SAD-CODE\xspace}
\newcommand{\sadsam}{SAD-SAM\xspace}
\newcommand{\samcode}{SAM-CODE\xspace}
\newcommand{\transarc}{TransArc\xspace}
\newcommand{\fone}{F\textsubscript{1}\xspace}
\newcommand{\acfone}{ACF\textsubscript{1}\xspace}
```

**Section + label conventions** (lines 37-39, 389-391) — sections use `\section{...}` then `\label{sec:...}`; the Ch2 namespace is `sec:eval:*` (e.g. `sec:eval:f1`, `sec:eval:protocol`) and `sec:ineq:*` for the inequality chapter. New section labels should follow `sec:eval:<topic>` (Claude's discretion on exact name per CONTEXT line 42):
```latex
\section{Comprehensive Evaluation Metrics for \sadcode Traceability}
\label{sec:comprehensive-metrics}
\label{ch:eval}
```

**Cross-reference idiom:** `\Cref{tab:...}` / `\Cref{sec:...}` (cleveref, loaded line 14). Prose references the table by label, e.g. line 407:
```latex
\Cref{tab:s12c-four-level} shows how file-, decision-, component-, and weighted \fone disagree---and even reorder the projects---when applied to identical \sadcode trace links.
```

**Two ways tables enter the document — match the surrounding context:**
1. **`\input{tables/<name>}`** — the generated-table idiom, used throughout `ch1_transarc.tex` (e.g. `\input{tables/s12c_four_level}`, `\input{tables/dashboard}`). Use this for the NEW generated consequences/converged tables. Place the `\input` right after the prose that `\Cref`s it.
2. **Inline `\begin{table}...\end{table}`** — eval.tex Ch2 also hand-writes small tables inline (e.g. `tab:f1_variants` lines 449-465, `tab:enrollment` lines 57-78). Either is acceptable; prefer `\input{tables/...}` for anything generate_tables.py emits so the data stays single-sourced.

Note: in the current tree the generated tables `tab:s12c-four-level` and `tab:dashboard` are physically `\input` inside `ch1_transarc.tex`, while eval.tex Ch2 only `\Cref`s their labels. For Phase 5, place the new `\input{tables/...}` directly in the new eval.tex Ch2 section so the float and its discussion are co-located.

**Placement targets:**
- NEW motivation section "misleading \fone across BOTH tasks" → insert as a new `\section` within Ch2, logically after `sec:comprehensive-metrics` intro / alongside the inequality discussion. It introduces the SAD-SAM standalone-misleading angle (CONTEXT line 55: SAD-SAM currently appears only as the cascade source).
- Converged framework → EXTEND `sec:eval:protocol` (lines 986-1004). The existing `\begin{enumerate}` recommendation list (items 1-7) stays; add the converged decision+component recommendation atop it and `\input` the converged table. End-of-document is `\end{document}` at line 1007 — new protocol content goes BEFORE it.

**Citations scope (STUDY-04):** prose may reference only retained reports/scripts. Retained `reports/*.md` available for `\texttt{}` source-notes: `BENCHMARK_BIAS_STUDY`, `CREATIVE_METRICS`, `ENROLLMENT_BIAS_ANALYSIS`, `EVALUATION_CRITIQUE`, `EXTREME_BASELINES`, `HOLISTIC_METRICS`, `METRIC_LIMITATIONS_ANALYSIS`, `NEW_METRICS_REPORT`, `SAD_SAM_ACTUAL_CONTRIBUTION`, `SAD_SAM_TP_GAIN_STUDY`, `SAM_CODE_CASCADE`, `SAM_CODE_DISTRIBUTION`, `STUPID_BASELINES`, `SUB_COMPONENT_ANALYSIS`, `TRANSARC_EMPIRICAL_STUDY`, plus the NEW `CONSEQUENCES_STUDY.md`. There is NO `.bib`/`\cite` machinery in eval.tex — "citations" here means `\texttt{reports/...}` source-notes in table `note=` and prose, exactly as existing tables do (e.g. line 191 `note="Source: \\texttt{reports/TRANSARC\\_EMPIRICAL\\_STUDY.md}."`). Do not reference archived/removed material.

---

## Shared Patterns

### Stdlib-only + absolute paths
**Source:** `metrics_api.py` line 56, `evaluation_critique.py` line 35
**Apply to:** the new `consequences_study.py`
No third-party deps (csv, sys, pathlib, collections only). Output paths are hardcoded absolute under `/mnt/hostshare/ardoco-home/transarc-emp/reports/`.

### `render_table` / `write_table` / `header_override`
**Source:** `generate_tables.py` lines 136-173
**Apply to:** every new table builder
booktabs output (`\toprule`/`\midrule`/`\bottomrule`), `colspec` = left-align label col + right-align numerics, `header_override` mandatory for macro-bearing headers, `note=` for the `\texttt{reports/...}` source line.

### Markdown `out()` accumulator
**Source:** `evaluation_critique.py` lines 1289-1321
**Apply to:** `consequences_study.py`
Local closure appends to a `md_lines` list (also `print`s for console), single write at end.

### No benchmark leakage (NON-NEGOTIABLE)
**Source:** workspace + project CLAUDE.md; CONTEXT line 26
**Apply to:** ALL files
Zero benchmark-derived word lists — no component names, project-specific terms, synonym maps hardcoded. CONTEXT line 26 confirms NONE are needed here (pure numeric CSV analysis; stopwords only, and none required). Project NAMES read as opaque data from the CSV `project` column are fine (same stance as `generate_tables.py` lines 11-14: project/column names are opaque data read from reports, not vocabulary).

---

## No Analog Found

None. All three files map to strong in-repo analogs.

- The "converged metric framework" CONCEPT (STUDY-03) is new analysis, but its mechanics (read two CSVs, difference headline vs decision+component, emit md table + LaTeX table) are fully covered by the `evaluation_critique` writer + `generate_tables` builder + `metrics_api` CSV idioms above. No new infrastructure surface.

---

## Metadata

**Analog search scope:** `src/bias/`, `src/lib/`, `src/paper/`, `writing/`, `reports/`
**Files scanned:** evaluation_critique.py, metrics_api.py, generate_tables.py, new_metrics_analysis.py, eval.tex, ch1_transarc.tex; metrics_sad-sam.csv, metrics_sad-code.csv, S12C_VS_TRANSARC.csv
**Pattern extraction date:** 2026-05-30

## PATTERN MAPPING COMPLETE
