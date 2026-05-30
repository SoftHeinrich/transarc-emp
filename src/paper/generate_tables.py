#!/usr/bin/env python3
"""Generate booktabs LaTeX tables for ``writing/eval.tex`` from retained reports.

Data lineage (SC3): every emitted table traces to a retained artifact under
``reports/``.  The script parses the Markdown tables already produced by the
Pillar-1 analysis scripts (deterministic regeneration confirmed in Phase 2) and
the ``S12C_VS_TRANSARC.csv`` four-level comparison, then converts them to
``\\begin{table}`` floats under ``writing/tables/``.

Stdlib only (csv, re, pathlib).  No benchmark-derived word lists: project and
column names are treated as opaque data read from the reports; the only literal
strings the script matches on are *structural* column-header fragments taken
from the report headers themselves (e.g. ``"precision"``, ``"amplification"``),
never domain vocabulary.

Run:  python3 src/paper/generate_tables.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
OUT = ROOT / "writing" / "tables"

REPORT_FILES = {
    "emp": REPORTS / "TRANSARC_EMPIRICAL_STUDY.md",
    "contrib": REPORTS / "SAD_SAM_ACTUAL_CONTRIBUTION.md",
    "tpgain": REPORTS / "SAD_SAM_TP_GAIN_STUDY.md",
    "cascade": REPORTS / "SAM_CODE_CASCADE.md",
}
CSV_FILE = REPORTS / "S12C_VS_TRANSARC.csv"


# ---------------------------------------------------------------------------
# Markdown-table parsing
# ---------------------------------------------------------------------------
def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_sep(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", line.strip()))


def extract_tables(md_text: str) -> list[list[list[str]]]:
    """Return every Markdown table as ``[header_row, data_row, ...]``.

    A GitHub-flavoured Markdown table is delimited by its ``|---|`` separator
    row: the pipe-line immediately *above* the separator is the header. Because
    the reports place consecutive tables with no blank line between them, we
    cannot rely on blank lines to split tables; instead each separator row
    starts a fresh table whose header is the line just before it. Pipe-lines
    after a table's data, up to the next separator, belong to the next table's
    header region.
    """
    lines = md_text.split("\n")
    is_pipe = [l.strip().startswith("|") and l.strip().endswith("|") for l in lines]
    tables: list[list[list[str]]] = []
    i = 0
    n = len(lines)
    while i < n:
        if is_pipe[i] and _is_sep(lines[i]):
            # header is the immediately-preceding pipe line
            header_idx = i - 1
            if header_idx < 0 or not is_pipe[header_idx]:
                i += 1
                continue
            rows = [_split_row(lines[header_idx])]
            j = i + 1
            while j < n and is_pipe[j] and not _is_sep(lines[j]):
                rows.append(_split_row(lines[j]))
                j += 1
            if len(rows) >= 2:
                tables.append(rows)
            i = j
        else:
            i += 1
    return tables


def find_table(report_key: str, header_keywords: list[str], min_rows: int = 2):
    """First table in a report whose header contains all ``header_keywords``.

    ``header_keywords`` are case-insensitive substrings of the report's own
    column headers -- a structural selector, not domain vocabulary.
    """
    md = REPORT_FILES[report_key].read_text(encoding="utf-8")
    for t in extract_tables(md):
        header = " ".join(t[0]).lower()
        if len(t) >= min_rows and all(k.lower() in header for k in header_keywords):
            return t
    raise SystemExit(
        "ERROR: no table matching %r in %s"
        % (header_keywords, REPORT_FILES[report_key].name)
    )


# ---------------------------------------------------------------------------
# Cell / LaTeX helpers
# ---------------------------------------------------------------------------
def clean_cell(cell: str) -> str:
    """Strip Markdown emphasis / code ticks before LaTeX escaping."""
    cell = cell.replace("**", "").replace("`", "")
    cell = cell.replace("→", r"$\rightarrow$").replace("×", r"$\times$")
    return cell.strip()


def latex_escape(cell: str) -> str:
    cell = clean_cell(cell)
    # protect already-formed math
    parts = re.split(r"(\$[^$]*\$)", cell)
    esc = []
    for i, p in enumerate(parts):
        if i % 2 == 1:  # inside $...$
            esc.append(p)
            continue
        p = p.replace("\\", r"\textbackslash{}")
        for ch in ("&", "%", "#", "_"):
            p = p.replace(ch, "\\" + ch)
        esc.append(p)
    return "".join(esc)


def colspec(header: list[str]) -> str:
    """Left-align the first (label) column, right-align numeric columns."""
    return "l" + "r" * (len(header) - 1)


def render_table(rows, caption, label, note=None, header_override=None, raw_cols=None):
    # header_override is hand-written LaTeX (may contain macros): emit verbatim.
    # Auto-derived headers come from the report and must be escaped.
    # raw_cols: 0-based column indices whose *data* cells are hand-written LaTeX
    # (may contain macros such as \sadsam) and must be emitted verbatim.
    raw = set(raw_cols or ())
    if header_override is not None:
        header = header_override
        header_cells = list(header)
    else:
        header = rows[0]
        header_cells = [latex_escape(c) for c in header]
    data = rows[1:]
    ncols = len(header)
    align = colspec(header)
    out = [
        r"\begin{table}[htbp]",
        r"  \centering",
        "  \\caption{%s}" % caption,
        "  \\label{%s}" % label,
        "  \\begin{tabular}{%s}" % align,
        r"    \toprule",
        "    " + " & ".join(header_cells) + r" \\",
        r"    \midrule",
    ]
    for row in data:
        row = list(row) + [""] * (ncols - len(row))
        cells = [c if i in raw else latex_escape(c) for i, c in enumerate(row[:ncols])]
        out.append("    " + " & ".join(cells) + r" \\")
    out.append(r"    \bottomrule")
    out.append(r"  \end{tabular}")
    if note:
        out.append("  \\par\\smallskip\\footnotesize %s" % note)
    out.append(r"\end{table}")
    return "\n".join(out) + "\n"


def write_table(name: str, content: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + ".tex")
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------
def t_transarc_overview():
    rows = find_table("emp", ["project", "precision", "recall", "f1"])
    return write_table(
        "transarc_overview",
        render_table(
            rows,
            caption=(
                "End-to-end \\sadcode (\\transarc) results per project: gold "
                "size, produced links, confusion counts, and \\fone (with the "
                "expected/threshold values reproduced from the TLR test suite)"
            ),
            label="tab:transarc-overview",
            note="Source: \\texttt{reports/TRANSARC\\_EMPIRICAL\\_STUDY.md}.",
        ),
    )


def t_sadsam_contribution():
    rows = find_table("contrib", ["sad-sam tps", "sad-code tps"])
    return write_table(
        "sadsam_contribution",
        render_table(
            rows,
            caption=(
                "Actual contribution of \\sadsam to \\transarc: the \\sadsam "
                "true/false positives that seed the transitive pipeline and the "
                "resulting \\sadcode links, per project"
            ),
            label="tab:sadsam-contribution",
            note="Source: \\texttt{reports/SAD\\_SAM\\_ACTUAL\\_CONTRIBUTION.md}.",
        ),
    )


def t_sadsam_tp_gain():
    rows = find_table("tpgain", ["sad-sam fns", "potential new"])
    return write_table(
        "sadsam_tp_gain",
        render_table(
            rows,
            caption=(
                "\\sadsam true-positive gain: \\sadcode true positives that "
                "would become recoverable if each \\sadsam false negative were "
                "fixed"
            ),
            label="tab:sadsam-tp-gain",
            note="Source: \\texttt{reports/SAD\\_SAM\\_TP\\_GAIN\\_STUDY.md}.",
        ),
    )


def t_sadsam_coverage():
    rows = find_table("tpgain", ["sad-code fns", "coverage"])
    return write_table(
        "sadsam_coverage",
        render_table(
            rows,
            caption=(
                "Recoverability of \\sadcode false negatives through \\sadsam "
                "false-negative recovery (upper bound on recall gain)"
            ),
            label="tab:sadsam-coverage",
            note="Source: \\texttt{reports/SAD\\_SAM\\_TP\\_GAIN\\_STUDY.md}.",
        ),
    )


def t_error_amplification():
    rows = find_table("emp", ["sad-sam fps", "induced transarc fps", "amplification"])
    # The report header repeats "Avg Amplification" for the two stages;
    # disambiguate so the LaTeX header is unambiguous.
    header = [
        "Project",
        "\\sadsam FPs",
        "Induced \\transarc FPs",
        "Amp. (\\sadsam)",
        "\\samcode FPs",
        "Induced \\transarc FPs",
        "Amp. (\\samcode)",
    ]
    return write_table(
        "error_amplification",
        render_table(
            rows,
            caption=(
                "Error amplification: each upstream false positive cascades into "
                "many \\transarc false positives. The mean amplification factor "
                "reaches 85.5 for Teammates and 495 for JabRef"
            ),
            label="tab:error-amplification",
            note="Source: \\texttt{reports/TRANSARC\\_EMPIRICAL\\_STUDY.md}.",
            header_override=header,
        ),
    )


def t_fp_attribution():
    rows = find_table("emp", ["category", "count", "percentage"])
    return write_table(
        "fp_attribution",
        render_table(
            rows,
            caption=(
                "Attribution of every \\transarc false positive to its causing "
                "stage: \\sadsam dominates with 93.7\\% of all false positives"
            ),
            label="tab:fp-attribution",
            note="Source: \\texttt{reports/TRANSARC\\_EMPIRICAL\\_STUDY.md}.",
        ),
    )


def t_samcode_cascade():
    rows = find_table(
        "cascade", ["sam-code fps", "induced sad-code fps", "amplification"]
    )
    header = [
        "Project",
        "\\samcode FPs",
        "Induced \\sadcode FPs",
        "Amp. (sents/FP)",
        "\\sadcode FPs from \\samcode",
        "\\% of all \\transarc FPs",
    ]
    return write_table(
        "samcode_cascade",
        render_table(
            rows,
            caption=(
                "\\samcode stage as the second link of the \\transarc cascade: "
                "\\samcode false positives and the \\sadcode false positives they "
                "induce, per project"
            ),
            label="tab:samcode-cascade",
            note="Source: \\texttt{reports/SAM\\_CODE\\_CASCADE.md}.",
            header_override=header,
        ),
    )


def t_theoretical_limit():
    rows = find_table("emp", ["theoretical limit", "unrecoverable"])
    return write_table(
        "theoretical_limit",
        render_table(
            rows,
            caption=(
                "Theoretical recall limit: \\sadcode gold links for which no "
                "transitive path exists even with a perfect upstream pipeline. "
                "Only Teammates (6.7\\%) and BigBlueButton (0.5\\%) are affected"
            ),
            label="tab:theoretical-limit",
            note="Source: \\texttt{reports/TRANSARC\\_EMPIRICAL\\_STUDY.md}.",
        ),
    )


# ---------------------------------------------------------------------------
# CSV-derived tables (S12C / S12E four-level comparison + dashboard)
# ---------------------------------------------------------------------------
def _load_csv():
    with CSV_FILE.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("dataset") and r["dataset"] != "MACRO_AVG"]
    return rows


def _fmt_f1(v: str) -> str:
    """CSV stores F1 as a percentage (e.g. 82.9); show as 0.829."""
    if v in ("", None):
        return "--"
    return "%.3f" % (float(v) / 100.0)


# ---------------------------------------------------------------------------
# Phase-4 metrics CSVs (already 0-1 decimals; include an ``Average`` row)
# ---------------------------------------------------------------------------
METRICS_CSV = {
    "sad-sam": REPORTS / "metrics_sad-sam.csv",
    "sad-code": REPORTS / "metrics_sad-code.csv",
}


def _load_metrics(task):
    with METRICS_CSV[task].open(encoding="utf-8") as f:
        return list(csv.DictReader(f))  # includes the Average row


def _fmt_dec(v):
    """metrics_*.csv stores F1 as a 0-1 decimal; em-dash = N/A."""
    if v in ("—", "", None):
        return "--"
    return "%.3f" % float(v)


def t_consequences():
    """STUDY-01/02: headline vs honest \\fone for BOTH tasks."""
    header = [
        "Task",
        "Project",
        "Headline \\fone",
        "Decision \\fone",
        "Component \\fone",
        "Sentence \\fone",
    ]
    data = []
    for r in _load_metrics("sad-sam"):
        data.append(
            [
                "\\sadsam",
                r["project"],
                _fmt_dec(r["link_f1"]),
                _fmt_dec(r["decision_f1"]),
                _fmt_dec(r["component_f1"]),
                _fmt_dec(r["sentence_f1"]),
            ]
        )
    for r in _load_metrics("sad-code"):
        data.append(
            [
                "\\sadcode",
                r["project"],
                _fmt_dec(r["file_f1"]),
                _fmt_dec(r["decision_f1"]),
                _fmt_dec(r["component_f1"]),
                _fmt_dec(r["sentence_f1"]),
            ]
        )
    caption = (
        "Headline versus honest \\fone for \\sadsam and \\sadcode: the headline "
        "metric (link for \\sadsam, file for \\sadcode) against decision-, "
        "component-, and sentence-level \\fone"
    )
    note = (
        "Source: \\texttt{reports/metrics\\_sad-sam.csv}, "
        "\\texttt{reports/metrics\\_sad-code.csv}, and "
        "\\texttt{reports/CONSEQUENCES\\_STUDY.md}. JabRef is best on file \\fone "
        "(0.943) yet worst on decision \\fone (0.394)."
    )
    return write_table(
        "consequences",
        render_table(
            [header] + data,
            caption=caption,
            label="tab:consequences",
            note=note,
            header_override=header,
            raw_cols=[0],  # Task column holds \sadsam / \sadcode macros
        ),
    )


def t_converged_framework():
    """STUDY-03: converged Decision+Component axis across both tasks."""
    sam_avg = next(r for r in _load_metrics("sad-sam") if r["project"] == "Average")
    code_avg = next(r for r in _load_metrics("sad-code") if r["project"] == "Average")
    sam_delta = "%.3f" % (float(sam_avg["link_f1"]) - float(sam_avg["decision_f1"]))
    code_delta = "%.3f" % (float(code_avg["file_f1"]) - float(code_avg["decision_f1"]))
    header = [
        "Task",
        "Headline metric",
        "Headline \\fone",
        "Decision \\fone",
        "Component \\fone",
        "Headline$-$Decision $\\Delta$",
    ]
    data = [
        [
            "\\sadsam",
            "link",
            _fmt_dec(sam_avg["link_f1"]),
            _fmt_dec(sam_avg["decision_f1"]),
            _fmt_dec(sam_avg["component_f1"]),
            sam_delta,
        ],
        [
            "\\sadcode",
            "file",
            _fmt_dec(code_avg["file_f1"]),
            _fmt_dec(code_avg["decision_f1"]),
            _fmt_dec(code_avg["component_f1"]),
            code_delta,
        ],
    ]
    caption = (
        "Converged evaluation axis: Decision- and Component-level \\fone as the "
        "common honest story across \\sadsam and \\sadcode (cross-project "
        "averages)"
    )
    note = (
        "Source: \\texttt{reports/metrics\\_sad-sam.csv}, "
        "\\texttt{reports/metrics\\_sad-code.csv}. The converged axis extends, "
        "not replaces, the corrected metrics in "
        "\\texttt{reports/EVALUATION\\_CRITIQUE.md}."
    )
    return write_table(
        "converged_framework",
        render_table(
            [header] + data,
            caption=caption,
            label="tab:converged-framework",
            note=note,
            header_override=header,
            raw_cols=[0],  # Task column holds \sadsam / \sadcode macros
        ),
    )


def t_s12c_four_level():
    rows = _load_csv()
    header = [
        "Project",
        "File \\fone",
        "Decision \\fone",
        "Component \\fone",
        "Weighted \\fone",
    ]
    data = []
    for r in rows:
        data.append(
            [
                r["dataset"],
                _fmt_f1(r["ta_file_F1"]),
                _fmt_f1(r["ta_dec_F1"]),
                _fmt_f1(r["ta_comp_F1"]),
                _fmt_f1(r["ta_wt_F1"]),
            ]
        )
    # cross-project average
    avg = ["Average"]
    for col in ("ta_file_F1", "ta_dec_F1", "ta_comp_F1", "ta_wt_F1"):
        vals = [float(r[col]) / 100.0 for r in rows if r.get(col)]
        avg.append("%.3f" % (sum(vals) / len(vals)))
    data.append(avg)
    note = (
        "Source: \\texttt{reports/S12C\\_VS\\_TRANSARC.csv} (\\transarc rows). "
        "Identical \\sadcode trace links scored at four aggregation levels. "
        "JabRef is best on File \\fone (0.943) yet worst on Decision \\fone "
        "(0.394), illustrating the ranking instability of file-level scoring."
    )
    return write_table(
        "s12c_four_level",
        render_table(
            [header] + data,
            caption=(
                "Four-level \\sadcode evaluation of \\transarc: file-, decision-, "
                "component-, and inverse-expansion-weighted \\fone"
            ),
            label="tab:s12c-four-level",
            note=note,
            header_override=header,
        ),
    )


def t_dashboard():
    """Ch2 dashboard: TransArc vs the S12C SAM-CODE oracle across levels."""
    rows = _load_csv()
    header = [
        "Project",
        "TA File \\fone",
        "TA Dec. \\fone",
        "S12C File \\fone",
        "S12C Dec. \\fone",
        "S12C Comp. \\fone",
    ]
    data = []
    for r in rows:
        data.append(
            [
                r["dataset"],
                _fmt_f1(r["ta_file_F1"]),
                _fmt_f1(r["ta_dec_F1"]),
                _fmt_f1(r["s12c_file_F1"]),
                _fmt_f1(r["s12c_dec_F1"]),
                _fmt_f1(r["s12c_comp_F1"]),
            ]
        )
    avg = ["Average"]
    for col in ("ta_file_F1", "ta_dec_F1", "s12c_file_F1", "s12c_dec_F1", "s12c_comp_F1"):
        vals = [float(r[col]) / 100.0 for r in rows if r.get(col)]
        avg.append("%.3f" % (sum(vals) / len(vals)))
    data.append(avg)
    note = (
        "Source: \\texttt{reports/S12C\\_VS\\_TRANSARC.csv}. ``TA'' = end-to-end "
        "\\transarc; ``S12C'' substitutes the oracle \\samcode link. The spread "
        "between File and Decision \\fone quantifies enrollment-inflation bias; "
        "the TA$\\to$S12C jump isolates the \\sadsam bottleneck."
    )
    return write_table(
        "dashboard",
        render_table(
            [header] + data,
            caption=(
                "Evaluation dashboard: \\transarc versus the \\samcode-oracle "
                "(S12C) variant, scored at multiple aggregation levels with "
                "cross-project averages"
            ),
            label="tab:transarc-dashboard",
            note=note,
            header_override=header,
        ),
    )


# ---------------------------------------------------------------------------
def main():
    builders = [
        # Chapter 1 (TransArc empirical study)
        t_transarc_overview,
        t_sadsam_contribution,
        t_sadsam_tp_gain,
        t_sadsam_coverage,
        t_error_amplification,
        t_fp_attribution,
        t_samcode_cascade,
        t_theoretical_limit,
        t_s12c_four_level,
        # Chapter 2 (Benchmark bias / metrics)
        t_dashboard,
        t_consequences,         # STUDY-01/02 headline-vs-honest, both tasks
        t_converged_framework,  # STUDY-03 converged Decision+Component
    ]
    written = [b() for b in builders]
    for p in written:
        print("WROTE", p.relative_to(ROOT))
    print("TOTAL", len(written))


if __name__ == "__main__":
    main()
