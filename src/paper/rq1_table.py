#!/usr/bin/env python3
"""Two-backend RQ1 wide-table generator (sad-sam + sad-code).

Implements REQ-V263-02 (D-02, D-03). See
agent-linker/.planning/phases/43-replay-s-linker19-checkpoints-for-paper-rq1-rq4-eval/43-CONTEXT.md.

D-02: This script lives in evaluation/ (transarc-emp/src/paper/) and is
      stdlib-only. It REUSES `compute_sad_sam_row` / `compute_sad_code_row` /
      `build_avg_row` from `metrics_api.py` — no metric math is reimplemented
      here. Nothing from `agent-linker/src/llm_sad_sam/` is imported.

D-03: One wide LaTeX table per task with two column groups (Claude | GPT-5.4)
      and 6 data rows (5 projects + 1 Macro). Claude is the left column group.

Inputs:
    --csv-root <PATH>      default /mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3
                           (with /mnt/hostshare/ardoco-home/agent-linker/approach/...
                           tried as a fallback, since `approach/` is a symlink lens)
    --tex-out-dir <PATH>   default /mnt/hostshare/ardoco-home/agent-linker/writing/working/tables
    --task {sad-sam,sad-code,both}   default both

The per-backend CSVs land under
    <csv-root>/<backend>/<project>/{sad-sam.csv,sad-code.csv}
where <backend> ∈ {claude, openai} and <project> ∈ metrics_api.PROJECTS.
Plan 02 emits both CSV schemas; this script bridges them to the legacy schema
that `transarc_error_analysis.load_result_sad_*` expects.

Bridge strategy (no edits to metrics_api / transarc_error_analysis):
    1. For each backend, materialise a temp results tree at
       <temp>/<project>/{sad-sam,sad-code}/{sadSamTlr_<p>.csv,sadCodeTlr_<p>.csv}.
    2. Monkey-patch `transarc_error_analysis.RESULTS` to point at <temp>.
    3. Loop projects -> compute_sad_sam_row / compute_sad_code_row, accumulate
       rows, then build_avg_row to get the Macro row.
    4. Restore RESULTS in a try/finally and clean up <temp>.

Output: two TeX files
    <tex-out-dir>/metrics_sad-sam.tex
    <tex-out-dir>/metrics_sad-code.tex
each containing `\\begin{table}` ... `\\end{table}` with `\\label{tab:metrics-sad-sam}`
or `\\label{tab:metrics-sad-code}` and a source-note footer pointing at the
Plan 02 CSVs (data lineage).
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import tempfile
from pathlib import Path

# ── Stdlib-only imports above. The three imports below are SIBLING modules
# inside transarc-emp/src/{lib,paper}/ (NOT third-party). Per CLAUDE.md the
# transarc-emp project pins itself to "Python 3 (stdlib only)", so these
# in-repo siblings are fair game.

_HERE = Path(__file__).resolve().parent             # transarc-emp/src/paper
_SRC = _HERE.parent                                 # transarc-emp/src
sys.path.insert(0, str(_SRC / "lib"))
sys.path.insert(0, str(_SRC / "paper"))

import metrics_api                                  # noqa: E402  (sys.path setup above)
import transarc_error_analysis                      # noqa: E402
import generate_tables                              # noqa: E402  (for render_table)


# ── Constants ─────────────────────────────────────────────────────────────────

BACKENDS = ("claude", "openai")
BACKEND_LABEL = {"claude": "Claude", "openai": "GPT-5.4"}

# Per-task subset of the unified SCHEMA's numeric columns. sad-sam has no
# file/weighted F1 (no enrollment); sad-code has no link/sentence F1 and no MAP
# per metrics_api SCHEMA. Order matches LATEX_HEADER for stable rendering.
SAD_SAM_COLS = ["link_f1", "sentence_f1", "mcc", "map", "acf1", "ndg", "hus"]
SAD_CODE_COLS = [
    "link_f1", "sentence_f1", "decision_f1", "component_f1",
    "file_f1", "weighted_f1", "mcc", "map", "acf1", "ndg", "hus",
]

# Display labels for the second header row (per-metric), taken from
# metrics_api.LATEX_HEADER so macro names like `\fone` round-trip verbatim.
def _metric_label(col):
    """Return the LATEX_HEADER cell for a SCHEMA column name."""
    idx = metrics_api.SCHEMA.index(col)
    return metrics_api.LATEX_HEADER[idx]


# ── CSV-root resolution (handles the `approach/` symlink lens) ────────────────

def _resolve_csv_root(arg_csv_root: str) -> Path:
    """Return the first existing csv-root, walking the approach/ symlink lens."""
    candidates = [
        Path(arg_csv_root),
        # If the caller passed `.../approach/results/v2.6.3`, the symlink-free
        # location is `.../results/v2.6.3`. If they passed the symlink-free
        # path, try the symlink lens as a fallback. Both should resolve to the
        # same inode when symlinks exist.
        Path(arg_csv_root.replace("/approach/results/", "/results/")),
        Path(arg_csv_root.replace("/results/", "/approach/results/")),
    ]
    seen = set()
    for c in candidates:
        rc = c.resolve()
        if rc in seen:
            continue
        seen.add(rc)
        if c.is_dir():
            return c
    raise SystemExit(
        f"ERROR: --csv-root {arg_csv_root} not found (also tried symlink-lens "
        f"variants); did Plan 02 run? Expected layout: "
        f"<csv-root>/<backend>/<project>/sad-{{sam,code}}.csv"
    )


# ── Per-backend results-tree materialisation ──────────────────────────────────

def _materialise_backend_results_tree(csv_root: Path, backend: str) -> Path:
    """Build a temp tree mirroring transarc_error_analysis.RESULTS layout.

    Source: <csv-root>/<backend>/<project>/{sad-sam.csv,sad-code.csv}
    Dest:   <temp>/<project>/sad-sam/sadSamTlr_<project>.csv     (passthrough)
            <temp>/<project>/sad-code/sadCodeTlr_<project>.csv   (column rename)

    Plan 02's sad-sam.csv columns (modelElementID, sentence, source) are a
    superset of the legacy schema (modelElementID, sentence) — csv.DictReader
    in load_result_sad_sam_standalone ignores extras, so we can copy directly.

    Plan 02's sad-code.csv columns (sentence, codeID) need rename to the legacy
    schema (modelElementID, codeId) since load_result_sad_code reads those
    exact field names. The semantic mapping is fixed: legacy `modelElementID`
    in the sad-code result holds the SENTENCE string (see the function
    docstring in transarc_error_analysis.load_result_sad_code).
    """
    temp = Path(tempfile.mkdtemp(prefix=f"rq1_table_{backend}_"))
    src_backend = csv_root / backend
    if not src_backend.is_dir():
        raise SystemExit(
            f"ERROR: backend dir {src_backend} not found under csv-root."
        )

    for project in metrics_api.PROJECTS:
        proj_src = src_backend / project
        if not proj_src.is_dir():
            print(
                f"WARNING: no Plan 02 outputs for {backend}/{project}; "
                f"compute_*_row will warn and skip", file=sys.stderr,
            )
            continue

        # sad-sam: pure copy (column names already compatible).
        src_sam = proj_src / "sad-sam.csv"
        dst_sam = temp / project / "sad-sam" / f"sadSamTlr_{project}.csv"
        dst_sam.parent.mkdir(parents=True, exist_ok=True)
        if src_sam.is_file():
            shutil.copy2(src_sam, dst_sam)

        # sad-code: rename columns to the legacy schema.
        src_code = proj_src / "sad-code.csv"
        dst_code = temp / project / "sad-code" / f"sadCodeTlr_{project}.csv"
        dst_code.parent.mkdir(parents=True, exist_ok=True)
        if src_code.is_file():
            with src_code.open(newline="") as fin, dst_code.open(
                "w", newline=""
            ) as fout:
                reader = csv.DictReader(fin)
                writer = csv.writer(fout)
                writer.writerow(["modelElementID", "codeId"])
                for row in reader:
                    writer.writerow([row["sentence"], row["codeID"]])
    return temp


# ── Per-backend row computation (reuses metrics_api primitives verbatim) ──────

def _run_backend_rows(task: str, csv_root: Path, backend: str):
    """Return (project_rows, macro_row) for one backend via metrics_api."""
    compute = (
        metrics_api.compute_sad_sam_row
        if task == "sad-sam"
        else metrics_api.compute_sad_code_row
    )

    temp_results = _materialise_backend_results_tree(csv_root, backend)
    original_results = transarc_error_analysis.RESULTS
    rows = []
    try:
        transarc_error_analysis.RESULTS = temp_results
        for project in metrics_api.PROJECTS:
            row = compute(project)
            if row is not None:
                rows.append(row)
    finally:
        transarc_error_analysis.RESULTS = original_results
        shutil.rmtree(temp_results, ignore_errors=True)

    macro = metrics_api.build_avg_row(rows)
    macro["project"] = "Macro"
    return rows, macro


# ── Wide-row composition (Claude || GPT-5.4) ──────────────────────────────────

def build_two_backend_rows(task: str, csv_root: Path):
    """Return a list of wide rows: 5 projects + Macro, with both backends.

    Each entry is a dict with key "project" plus per-(backend, metric) keys
    of the form f"{BACKEND_LABEL[backend]}.{col}".
    """
    per_backend = {}
    for backend in BACKENDS:
        rows, macro = _run_backend_rows(task, csv_root, backend)
        per_backend[backend] = {r["project"]: r for r in rows}
        per_backend[backend]["Macro"] = macro

    project_order = list(metrics_api.PROJECTS) + ["Macro"]
    cols = SAD_SAM_COLS if task == "sad-sam" else SAD_CODE_COLS

    wide_rows = []
    for project in project_order:
        wide = {"project": project}
        for backend in BACKENDS:
            src = per_backend[backend].get(project)
            for c in cols:
                key = f"{BACKEND_LABEL[backend]}.{c}"
                if src is None:
                    wide[key] = metrics_api.NA
                else:
                    wide[key] = src.get(c, metrics_api.NA)
        wide_rows.append(wide)
    return wide_rows


# ── LaTeX rendering ──────────────────────────────────────────────────────────

def _project_display(name):
    """Pretty-print a metrics_api project name for the LaTeX Project column."""
    mapping = {
        "mediastore": "MediaStore",
        "teastore": "TeaStore",
        "teammates": "TeaMmates",
        "bigbluebutton": "BigBlueButton",
        "jabref": "JabRef",
        "Macro": "Macro",
    }
    return mapping.get(name, name)


def _render_wide_table(task: str, wide_rows, csv_root: Path) -> str:
    """Render the two-backend wide table for `task` to a LaTeX string."""
    cols = SAD_SAM_COLS if task == "sad-sam" else SAD_CODE_COLS
    K = len(cols)

    # Two-row header: top groups, bottom per-metric. We assemble both rows
    # ourselves and concatenate them; generate_tables.render_table only emits
    # one header line, so we splice the second header row in by overriding the
    # `header_override` value with a multi-line string fragment.
    top_cells = (
        ["Project"]
        + ["\\multicolumn{%d}{c}{%s}" % (K, BACKEND_LABEL[b]) for b in BACKENDS]
    )
    bottom_cells = ["{}"] + [_metric_label(c) for c in cols] * len(BACKENDS)

    # render_table only emits a single header line. We emit our own table
    # body and reuse latex_escape + colspec helpers from generate_tables
    # rather than copying them.
    total_cols = 1 + K * len(BACKENDS)
    align = "l" + "r" * (total_cols - 1)

    caption = {
        "sad-sam": (
            "Doc-to-model link-level metrics for \\approach{} across two "
            "backends. Macro row is the unweighted mean across the five "
            "projects."
        ),
        "sad-code": (
            "Doc-to-code metrics for \\approach{} composed with the SAM-code "
            "mapping, across two backends. Macro row is the unweighted mean "
            "across the five projects."
        ),
    }[task]
    label = "tab:metrics-sad-sam" if task == "sad-sam" else "tab:metrics-sad-code"

    # Source-note footer with data lineage.
    note = (
        "Source: \\texttt{approach/results/v2.6.3/<backend>/<project>/"
        "%s.csv} (Plan 02 replay of s\\_linker19 phase\\_cache pickles; "
        "zero LLM calls)."
    ) % task

    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        "  \\caption{%s}" % caption,
        "  \\label{%s}" % label,
        "  \\begin{tabular}{%s}" % align,
        r"    \toprule",
        "    " + " & ".join(top_cells) + r" \\",
        # cmidrule under each backend group (visual separation).
        "    \\cmidrule(lr){2-%d} \\cmidrule(lr){%d-%d}" % (
            1 + K, 2 + K, 1 + 2 * K,
        ),
        "    " + " & ".join(bottom_cells) + r" \\",
        r"    \midrule",
    ]
    for row in wide_rows:
        cells = [_project_display(row["project"])]
        for backend in BACKENDS:
            for c in cols:
                v = row[f"{BACKEND_LABEL[backend]}.{c}"]
                if v == metrics_api.NA or v is None:
                    cells.append(metrics_api.NA_TEX)
                else:
                    cells.append(metrics_api._fmt(v))
        lines.append("    " + " & ".join(cells) + r" \\")
    lines.append(r"    \bottomrule")
    lines.append(r"  \end{tabular}")
    lines.append("  \\par\\smallskip\\footnotesize %s" % note)
    lines.append(r"\end{table}")
    return "\n".join(lines) + "\n"


def write_two_backend_tex(task: str, wide_rows, tex_out_dir: Path, csv_root: Path) -> Path:
    """Render `wide_rows` for `task` and write to <tex_out_dir>/metrics_<task>.tex."""
    tex_out_dir.mkdir(parents=True, exist_ok=True)
    content = _render_wide_table(task, wide_rows, csv_root)
    out = tex_out_dir / f"metrics_{task}.tex"
    out.write_text(content, encoding="utf-8")
    return out


# ── Entry point ───────────────────────────────────────────────────────────────

DEFAULT_CSV_ROOT = "/mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3"
DEFAULT_TEX_OUT_DIR = "/mnt/hostshare/ardoco-home/agent-linker/writing/working/tables"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate the two-backend RQ1 wide LaTeX tables "
            "(metrics_sad-sam.tex, metrics_sad-code.tex) from Plan 02 "
            "per-backend CSVs. Implements REQ-V263-02 (D-02 + D-03)."
        )
    )
    parser.add_argument(
        "--task", choices=["sad-sam", "sad-code", "both"], default="both",
        help="Which RQ1 task table to produce (default: both).",
    )
    parser.add_argument(
        "--csv-root", default=DEFAULT_CSV_ROOT,
        help=(
            "Root of the Plan 02 CSV tree "
            "(default: %(default)s; symlink-lens variants tried as fallback)."
        ),
    )
    parser.add_argument(
        "--tex-out-dir", default=DEFAULT_TEX_OUT_DIR,
        help="Directory to write the populated TeX tables (default: %(default)s).",
    )
    args = parser.parse_args()

    csv_root = _resolve_csv_root(args.csv_root)
    tex_out_dir = Path(args.tex_out_dir)

    tasks = ["sad-sam", "sad-code"] if args.task == "both" else [args.task]
    for task in tasks:
        wide_rows = build_two_backend_rows(task, csv_root)
        tex_path = write_two_backend_tex(task, wide_rows, tex_out_dir, csv_root)
        print(
            "[rq1-table] task=%s backends=%s projects=%d wrote=%s"
            % (task, ",".join(BACKENDS), len(wide_rows), tex_path)
        )


if __name__ == "__main__":
    main()
