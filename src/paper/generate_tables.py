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
    """Return every Markdown table as a list of cell-rows (separator dropped)."""
    tables: list[list[list[str]]] = []
    cur: list[list[str]] = []
    for line in md_text.split("\n"):
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and not _is_sep(s):
            cur.append(_split_row(s))
        else:
            if len(cur) >= 2:
                tables.append(cur)
            cur = []
    if len(cur) >= 2:
        tables.append(cur)
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


def render_table(rows, caption, label, note=None, header_override=None):
    header = header_override if header_override is not None else rows[0]
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
        "    " + " & ".join(latex_escape(c) for c in header) + r" \\",
        r"    \midrule",
    ]
    for row in data:
        row = list(row) + [""] * (ncols - len(row))
        out.append("    " + " & ".join(latex_escape(c) for c in row[:ncols]) + r" \\")
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
            label="tab:dashboard",
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
    ]
    written = [b() for b in builders]
    for p in written:
        print("WROTE", p.relative_to(ROOT))
    print("TOTAL", len(written))


if __name__ == "__main__":
    main()
