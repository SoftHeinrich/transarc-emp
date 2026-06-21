#!/usr/bin/env python3
"""Unified metrics-reporting API for ARDoCo TransArc evaluation.

A stdlib-only CLI that ingests TransArc-format results for a ``sad-sam`` or
``sad-code`` run, computes the full unified metric set for ALL benchmark
projects by REUSING existing functions (zero reimplementation), and emits both
a wide CSV (``reports/metrics_<task>.csv``) and a ready-to-paste booktabs LaTeX
table (``writing/tables/metrics_<task>.tex``).

Reused primitives (no metric math is implemented here):
  - ``transarc_error_analysis``: PROJECTS, loaders, ``calc_metrics``
  - ``evaluation_critique``: ``_compute_decision_f1`` / ``_compute_component_f1`` /
    ``_compute_weighted_f1`` (SAD-CODE only)
  - ``new_metrics_analysis``: ``compute_mcc`` / ``compute_map`` / ``compute_acf1`` /
    ``compute_ndg`` / ``compute_hus``
  - ``generate_tables``: ``render_table`` / ``write_table``

Run:  python3 src/lib/metrics_api.py --task sad-sam
      python3 src/lib/metrics_api.py --task sad-code [--project jabref]

      # Score arbitrarily-named result CSVs (e.g. agent-linker link exports)
      # from a configurable location. Result columns are auto-detected, so both
      # the TransArc dialect (modelElementID,sentence) and the agent-linker
      # dialect (sentence,component_id,...) are accepted:
      python3 src/lib/metrics_api.py --task sad-sam \
          --results-dir /path/to/run --reports-dir /tmp/out \
          --result-pattern 's_linker20_union_{project}_links.csv'

Paths are configurable (no hardcoded input/output): --results-dir /
--result-pattern / --reports-dir / --tables-dir CLI flags, or the
$TRANSARC_RESULTS_DIR / $TRANSARC_REPORTS_DIR / $TRANSARC_TABLES_DIR env vars,
all defaulting to the bundled transarc-emp tree. When --reports-dir is set and
--tables-dir is not, the .tex follows --reports-dir so one-off scoring runs
never overwrite the committed writing/tables/ artifacts.
"""

import csv
import math
import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────
# metrics_api.py lives IN src/lib, so the self-import target is `parent`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
# Module handle (not a value import) so the input-results root is read as
# `_tea.RESULTS` at CALL time — this keeps both --results-dir AND the existing
# monkeypatch in src/paper/rq1_table.py (transarc_error_analysis.RESULTS = ...)
# working. Result-file READING now lives here (column-tolerant); the metric
# MATH still comes entirely from the shared lib below.
import transarc_error_analysis as _tea
from transarc_error_analysis import (
    PROJECTS, calc_metrics, normalize_path,
    load_code_model_files,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_maps,
    load_text, load_model_element_names,
)
from new_metrics_analysis import (
    compute_mcc, compute_map, compute_acf1, compute_random_f1,
    compute_oracle_f1, compute_ndg, compute_hus, transarc_sad_sam_as_ranked,
)

# bias/ and paper/ are siblings of the lib dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bias"))
from evaluation_critique import (
    _compute_decision_f1, _compute_component_f1, _compute_weighted_f1,
    load_sad_code_raw_with_provenance, enroll_with_provenance,
    load_sam_code_enrolled,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "paper"))
import generate_tables as _gt   # module handle so --tables-dir can rebind _gt.OUT
from generate_tables import render_table, write_table

# ── Paths (configurable: env var → CLI flag → bundled default) ────────────────
# Input results root: default is the bundled transarc-emp/results tree, read at
# call time as _tea.RESULTS. Override with --results-dir or $TRANSARC_RESULTS_DIR,
# optionally combined with --result-pattern to point at arbitrarily-named CSVs
# (e.g. agent-linker's "s_linker20_union_{project}_links.csv").
# Output reports dir: override with --reports-dir or $TRANSARC_REPORTS_DIR.
_DEFAULT_REPORTS = "/mnt/hostshare/ardoco-home/transarc-emp/reports"
REPORTS = Path(os.environ.get("TRANSARC_REPORTS_DIR", _DEFAULT_REPORTS))

# Column-name candidates so result CSVs in either dialect are accepted:
#   TransArc style     → sad-sam : modelElementID, sentence
#                        sad-code: modelElementID (holds the sentence id), codeId
#   agent-linker style → sad-sam : sentence, component_id, component_name, ...
_SADSAM_COMPONENT_KEYS = ("modelElementID", "component_id", "componentId")
_SADSAM_SENTENCE_KEYS = ("sentence",)
_SADCODE_SENTENCE_KEYS = ("modelElementID", "sentence")
_SADCODE_CODE_KEYS = ("codeId", "codeID", "code_path")

# ── Unified column schema (superset across both tasks) ────────────────────────
# sentence_coverage / noise_rate added 2026-06-05 as part of the paper's RQ2
# primary panel ([[project-paper-metric-choices]]). They were previously defined
# in src/bias/rq2_metric_redundancy.py; inlined here so metrics_api stays the
# single source of truth.
SCHEMA = [
    "project", "link_f1", "sentence_f1", "decision_f1", "component_f1",
    "file_f1", "weighted_f1", "sentence_coverage", "noise_rate",
    "mcc", "map", "acf1", "ndg", "hus",
]
NUMERIC_COLS = SCHEMA[1:]  # everything except "project"

# Paper's chosen primary metric panel for RQ2 on doc-to-code, after the
# 2026-06-05 redundancy cut ([[project-paper-metric-choices]]):
#   file_f1 (reference), component_f1   (size-blind aggregation contrast)
#   sentence_coverage, noise_rate       (developer view)
# Decision F1 was dropped 2026-06-05 — file_f1 + component_f1 already cover the
# enrolment-inflation contrast, and decision_f1 added another granularity axis
# without independent rank signal beyond per-component F1.
# HUS and NDG are appendix-only — both shadowed on this benchmark
# (ρ >= 0.85 with metrics already in the main panel; 0 system-pair reversals
# beyond what the main panel produces). See reports/RQ2_METRIC_REDUNDANCY.md.
PAPER_MAIN_PANEL_SADCODE = [
    "file_f1", "component_f1",
    "sentence_coverage", "noise_rate",
]
PAPER_APPENDIX_SADCODE = ["hus", "ndg"]
# For sad-sam, per-component F1 collapses onto link F1 (ρ = +1.00, 0/189
# reversals — no enrolment), so the main panel is link F1, sentence coverage,
# and noise rate; HUS and per-sentence F1 are appendix-only.
PAPER_MAIN_PANEL_SADSAM = ["link_f1", "sentence_coverage", "noise_rate"]
PAPER_APPENDIX_SADSAM = ["sentence_f1", "hus"]

NA = "—"      # em dash — CSV inapplicable cells
NA_TEX = "--"      # LaTeX inapplicable cells

# LaTeX display header (contains \fone macros → must use header_override).
LATEX_HEADER = [
    "Project", "Link \\fone", "Sentence \\fone", "Decision \\fone",
    "Component \\fone", "File \\fone", "Weighted \\fone",
    "Sent.\\ cov.", "Noise (\\(\\downarrow\\))",
    "MCC", "MAP", "ACF1", "NDG", "HUS",
]


def _fmt(v):
    """Format a numeric value to 3 decimals; pass NA / strings through."""
    if isinstance(v, (int, float)):
        return f"{v:.3f}"
    return v


def _sentence_coverage(gold_by_s, res_by_s):
    """Fraction of gold sentences with at least one correct prediction.

    Both args are sentence -> set[target] dicts (target is component-id for
    sad-sam, code-path for sad-code; the metric is target-agnostic). Mirrors
    src/bias/rq2_metric_redundancy.py::sentence_coverage on the same inputs.
    """
    if not gold_by_s:
        return 0.0
    covered = sum(
        1 for s in gold_by_s if gold_by_s[s] & res_by_s.get(s, set())
    )
    return covered / len(gold_by_s)


def _noise_rate(gold_by_s, res_by_s):
    """Mean FP/(TP+FP) across predicted sentences; lower is better.

    Sentences with zero predictions are skipped (no purity to measure).
    Mirrors src/bias/rq2_metric_redundancy.py::noise_rate.
    """
    vals = []
    for s, r in res_by_s.items():
        g = gold_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        if tp + fp > 0:
            vals.append(fp / (tp + fp))
    return sum(vals) / len(vals) if vals else 0.0


def select_projects(args):
    """Return the list of projects to process, validating --project."""
    if args.project:
        if args.project not in PROJECTS:
            print(f"ERROR: unknown project '{args.project}' "
                  f"(expected one of {PROJECTS})", file=sys.stderr)
            sys.exit(2)
        return [args.project]
    return list(PROJECTS)


# ── Column-tolerant, path-configurable result loading ─────────────────────────

def _cell(row, keys):
    """First non-empty value among `keys` in a csv.DictReader row, else None."""
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None


def _unquote(s):
    """Strip one layer of matching surrounding quotes. Guards against IDE run
    configs / parameter fields that pass a quoted value literally — a real
    shell would strip these, so e.g. --result-pattern 's_..._{project}.csv'
    must not arrive with the quotes baked into the filename."""
    if s and len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _results_root(results_dir):
    """Resolve the results root: an explicit --results-dir wins; otherwise read
    the live transarc_error_analysis.RESULTS so the rq1_table monkeypatch (and
    the bundled default) keep working."""
    return Path(results_dir) if results_dir is not None else Path(_tea.RESULTS)


def _result_path(proj, results_dir, result_pattern, subdir, tlr_prefix):
    """Locate a result CSV. With --result-pattern, join `pattern.format(project=)`
    onto the root; otherwise use the default TransArc layout
    ``<root>/<project>/<subdir>/<tlr_prefix>_<project>.csv``."""
    root = _results_root(results_dir)
    if result_pattern:
        return root / result_pattern.format(project=proj)
    return root / proj / subdir / f"{tlr_prefix}_{proj}.csv"


def load_sad_sam_result(path):
    """Read a SAD-SAM result CSV → set[(component_id, sentence)], accepting both
    the TransArc and agent-linker column dialects. Empty set if file absent."""
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            comp = _cell(row, _SADSAM_COMPONENT_KEYS)
            sent = _cell(row, _SADSAM_SENTENCE_KEYS)
            if comp and sent:
                links.add((comp, sent))
    return links


def load_sad_code_result(path):
    """Read a SAD-CODE result CSV → set[(sentence, code_path)], accepting both
    column dialects. Empty set if file absent."""
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            sent = _cell(row, _SADCODE_SENTENCE_KEYS)
            code = _cell(row, _SADCODE_CODE_KEYS)
            if sent and code:
                links.add((sent, normalize_path(code)))
    return links


# ── Per-project metric rows ───────────────────────────────────────────────────

def compute_sad_sam_row(proj, results_dir=None, result_pattern=None):
    """Compute the SAD-SAM metric row for a standalone result CSV.

    SAD-SAM has NO files and NO enrollment — work directly on
    (modelElementID, sentence) pairs. The evaluation_critique `_compute_*`
    helpers are NOT used here (they require enrollment maps that do not exist
    for sad-sam). Reads the default TransArc layout unless `results_dir` /
    `result_pattern` redirect it (column dialect is auto-detected). Returns
    None (skip + warn) if the results file is absent.
    """
    path = _result_path(proj, results_dir, result_pattern, "sad-sam", "sadSamTlr")
    res = load_sad_sam_result(path)                     # set() if file absent
    if not res:
        print(f"WARNING: no sad-sam results for {proj} (looked in {path}), "
              f"skipping", file=sys.stderr)
        return None
    return compute_sad_sam_metrics(proj, res)


def compute_sad_sam_metrics(proj, res):
    """Compute the full SAD-SAM metric suite for an arbitrary result set.

    Single source of truth for SAD-SAM metrics — used both by the standalone
    metrics CLI (``compute_sad_sam_row``) and by multi-system comparators that
    pass e.g. an LLM linker's links. ``res`` is a set[(modelElementID,
    sentence)]. Returns the row dict (caller may overwrite "project").
    """
    gold = load_gs_sad_sam(proj)                       # set[(modelElementID, sentence)]

    text = load_text(proj)
    names = load_model_element_names(proj)             # modelElementID -> component name
    all_sents = set(text.keys())
    all_comps = set(names.keys())

    row = {"project": proj}

    # link_f1 = decision_f1 for sad-sam (every pair is one human decision,
    # zero enrollment inflation).
    _, _, link_f1, *_ = calc_metrics(gold, res)
    row["link_f1"] = link_f1
    row["decision_f1"] = link_f1

    # sentence_f1: a sentence is a TP iff its gold and predicted component
    # sets share at least one component. Build sentence-level link sets, then
    # reuse calc_metrics (only the set transform is inline, sanctioned by
    # CONTEXT "all granularities are built by transforming the link set").
    gold_by_s = defaultdict(set)
    res_by_s = defaultdict(set)
    for c, s in gold:
        gold_by_s[s].add(c)
    for c, s in res:
        res_by_s[s].add(c)
    gold_S = {(s, "*") for s in gold_by_s}
    res_S = {(s, "*") for s in res_by_s}
    row["sentence_f1"] = calc_metrics(gold_S, res_S)[2]

    # Sentence coverage / noise rate (paper RQ2 main panel — see
    # project-paper-metric-choices). Both operate on sentence -> set[component]
    # dicts that we already built above for sentence_f1.
    row["sentence_coverage"] = _sentence_coverage(gold_by_s, res_by_s)
    row["noise_rate"] = _noise_rate(gold_by_s, res_by_s)

    # component_f1: map ids to component names so synonymous ids collapse.
    gold_C = {(names.get(c, c), s) for (c, s) in gold}
    res_C = {(names.get(c, c), s) for (c, s) in res}
    row["component_f1"] = calc_metrics(gold_C, res_C)[2]

    # MCC over the (sentence × component) universe.
    row["mcc"] = compute_mcc(gold, res, all_sents, all_comps)["mcc"]

    # MAP: TransArc has no per-link confidence → uniform 0.5 ranking.
    ranked = transarc_sad_sam_as_ranked(res)
    row["map"] = compute_map(gold, ranked)["map"]

    # HUS: compute_hus groups by element [0]; sad-sam pairs are
    # (component, sentence) so flip to group by sentence.
    gold_flip = {(s, c) for (c, s) in gold}
    res_flip = {(s, c) for (c, s) in res}
    row["hus"] = compute_hus(gold_flip, res_flip)["hus"]

    # N/A: require enrollment / gold_sam_code_map which sad-sam lacks.
    row["file_f1"] = NA
    row["weighted_f1"] = NA
    row["acf1"] = NA
    row["ndg"] = NA
    return row


def compute_sad_code_row(proj, results_dir=None, result_pattern=None):
    """Compute the SAD-CODE metric row for a standalone result CSV.

    Reuses the evaluation_critique granularity helpers verbatim (the
    part5_alternative_metrics caller idiom is the exact reference). Reads the
    default TransArc layout unless `results_dir` / `result_pattern` redirect it
    (column dialect is auto-detected). Returns None (skip + warn) if the
    results file is absent.
    """
    path = _result_path(proj, results_dir, result_pattern, "sad-code", "sadCodeTlr")
    res = load_sad_code_result(path)                    # set() if file absent
    if not res:
        print(f"WARNING: no sad-code results for {proj} (looked in {path}), "
              f"skipping", file=sys.stderr)
        return None
    return compute_sad_code_metrics(proj, res)


def compute_sad_code_metrics(proj, res):
    """Compute the full SAD-CODE metric suite for an arbitrary result set.

    Single source of truth for SAD-CODE metrics — used both by the standalone
    metrics CLI (``compute_sad_code_row``) and by multi-system comparators that
    pass e.g. a composed (LLM-linker × ARCOTL) SAD-CODE result. ``res`` is a
    set[(sentence_str, code_path)]. Returns the row dict (caller may overwrite
    "project").
    """
    code_model = load_code_model_files(proj)

    # Provenance maps from raw gold (matching the part5 caller). Use the
    # provenance-tracked `enrolled` for ALL granularity calls so they agree.
    raw_entries = load_sad_code_raw_with_provenance(proj)
    enrolled, raw_to_enrolled, enrolled_to_raw = enroll_with_provenance(
        raw_entries, code_model)

    # file -> {component_name} map (caller idiom).
    names = load_model_element_names(proj)
    sam_enrolled = load_sam_code_enrolled(proj, code_model)   # (ae_id, file_path)
    file_to_comps = defaultdict(set)
    for ae, fp in sam_enrolled:
        file_to_comps[fp].add(names.get(ae, ae))

    row = {"project": proj}

    # Four granularities (reuse verbatim).
    _, _, file_f1, *_ = calc_metrics(enrolled, res)
    row["file_f1"] = file_f1
    row["decision_f1"] = _compute_decision_f1(enrolled, res, raw_to_enrolled)["f1"]
    row["component_f1"] = _compute_component_f1(enrolled, res, file_to_comps)["f1"]
    row["weighted_f1"] = _compute_weighted_f1(
        enrolled, res, enrolled_to_raw, raw_to_enrolled)["f1"]

    # Sentence coverage / noise rate (paper RQ2 main panel). sad-code pairs
    # are already in (sentence, code-path) order, so group by [0] directly.
    gold_by_s = defaultdict(set)
    res_by_s = defaultdict(set)
    for s, f in enrolled:
        gold_by_s[s].add(f)
    for s, f in res:
        res_by_s[s].add(f)
    row["sentence_coverage"] = _sentence_coverage(gold_by_s, res_by_s)
    row["noise_rate"] = _noise_rate(gold_by_s, res_by_s)

    # Alt metrics (sad-code).
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)  # model_id -> set(files)
    row["acf1"] = compute_acf1(enrolled, res, gs_sam_code_map)["acf1"]

    # NDG = (system_f1 - random_f1) / (oracle_f1 - random_f1).
    system_f1 = file_f1
    n_sentences = len(load_text(proj))
    n_components = len(gs_sam_code_map)
    # compute_random_f1 returns a BARE FLOAT (not a tuple) — do not subscript.
    random_f1 = compute_random_f1(enrolled, n_sentences, n_components, gs_sam_code_map)
    sad_sam_maps = load_gs_sad_sam_maps(proj)
    oracle_f1, _ = compute_oracle_f1(enrolled, gs_sam_code_map, sad_sam_maps)
    row["ndg"] = compute_ndg(system_f1, random_f1, oracle_f1)

    # HUS: sad-code links are (sentence, code) → groups by sentence, no flip.
    row["hus"] = compute_hus(enrolled, res)["hus"]

    # MCC over the (sentence × code-file) universe.
    all_sents = {s for (s, _c) in enrolled}
    all_files = set().union(*gs_sam_code_map.values()) if gs_sam_code_map else set()
    row["mcc"] = compute_mcc(enrolled, res, all_sents, all_files)["mcc"]

    # N/A: link/sentence are sad-sam-only granularities; MAP is sad-sam only
    # here (CONTEXT: MAP at sad-code is optional → omitted).
    row["link_f1"] = NA
    row["sentence_f1"] = NA
    row["map"] = NA
    return row


# ── Aggregation + emitters ────────────────────────────────────────────────────

def build_avg_row(rows):
    """Build the Average row: mean of numeric cells per column, NA otherwise."""
    avg = {"project": "Average"}
    for col in NUMERIC_COLS:
        vals = [r[col] for r in rows if isinstance(r[col], (int, float))]
        avg[col] = sum(vals) / len(vals) if vals else NA
    return avg


def write_csv(task, rows, avg_row):
    out_csv = REPORTS / f"metrics_{task}.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(SCHEMA)
        for row in rows:
            w.writerow([_fmt(row[col]) if col != "project" else row[col]
                        for col in SCHEMA])
        w.writerow([_fmt(avg_row[col]) if col != "project" else avg_row[col]
                    for col in SCHEMA])
    return out_csv


def write_latex(task, rows, avg_row):
    data_rows = []
    for row in list(rows) + [avg_row]:
        cells = [row["project"]]
        for c in NUMERIC_COLS:
            cells.append(_fmt(row[c]) if row[c] != NA else NA_TEX)
        data_rows.append(cells)
    content = render_table(
        [LATEX_HEADER] + data_rows,
        caption="Unified metric set for the %s task." % task,
        label="tab:metrics-%s" % task,
        note="Source: reports/metrics\\_%s.csv." % task,
        header_override=LATEX_HEADER,
    )
    return write_table(f"metrics_{task}", content)


def main():
    parser = argparse.ArgumentParser(
        description="Unified metrics-reporting API for sad-sam / sad-code runs.")
    parser.add_argument("--task", required=True,
                        choices=["sad-sam", "sad-code"],
                        help="Evaluation task to report metrics for.")
    parser.add_argument("--project", default=None,
                        help="Optional single-project filter (default: all).")
    parser.add_argument("--results-dir", default=None,
                        help="Root directory holding the result CSVs to score "
                             "(default: $TRANSARC_RESULTS_DIR, else the bundled "
                             "transarc-emp/results tree).")
    parser.add_argument("--result-pattern", default=None,
                        help="Filename pattern relative to --results-dir with a "
                             "{project} placeholder, e.g. "
                             "'s_linker20_union_{project}_links.csv'. When omitted, "
                             "the default TransArc layout "
                             "<project>/<task>/<Tlr>_<project>.csv is used. Result "
                             "columns are auto-detected (modelElementID|component_id).")
    parser.add_argument("--reports-dir", default=None,
                        help="Output directory for metrics_<task>.csv (default: "
                             "$TRANSARC_REPORTS_DIR, else the bundled "
                             "transarc-emp/reports).")
    parser.add_argument("--tables-dir", default=None,
                        help="Output directory for the LaTeX metrics_<task>.tex "
                             "(default: $TRANSARC_TABLES_DIR; else follows "
                             "--reports-dir when that is set; else the bundled "
                             "writing/tables — so one-off scoring runs do not "
                             "overwrite the committed paper tables).")
    args = parser.parse_args()

    # Tolerate values pasted with surrounding quotes (IDE run configs etc.).
    for _a in ("results_dir", "result_pattern", "reports_dir", "tables_dir"):
        _v = getattr(args, _a)
        if _v is not None:
            setattr(args, _a, _unquote(_v))

    global REPORTS
    if args.reports_dir:
        REPORTS = Path(args.reports_dir)
    REPORTS.mkdir(parents=True, exist_ok=True)

    # LaTeX output: explicit --tables-dir / env wins; else follow --reports-dir
    # when that was overridden; else leave generate_tables.OUT at its default.
    reports_overridden = bool(args.reports_dir or os.environ.get("TRANSARC_REPORTS_DIR"))
    tables_dir = args.tables_dir or os.environ.get("TRANSARC_TABLES_DIR")
    if not tables_dir and reports_overridden:
        tables_dir = str(REPORTS)
    if tables_dir:
        _gt.OUT = Path(tables_dir)

    results_dir_arg = args.results_dir or os.environ.get("TRANSARC_RESULTS_DIR")
    results_dir = Path(results_dir_arg) if results_dir_arg else None

    task = args.task
    projects = select_projects(args)
    compute = compute_sad_sam_row if task == "sad-sam" else compute_sad_code_row

    rows = []
    for proj in projects:
        row = compute(proj, results_dir, args.result_pattern)
        if row is not None:
            rows.append(row)

    if not rows:
        print(f"WARNING: no results found for any project on task {task}; "
              f"writing header + empty Average only.", file=sys.stderr)

    avg_row = build_avg_row(rows)
    csv_path = write_csv(task, rows, avg_row)
    tex_path = write_latex(task, rows, avg_row)

    print(f"[metrics-api] task={task} projects={len(rows)} "
          f"results_dir={_results_root(results_dir)} "
          f"csv={csv_path} tex={tex_path}")


if __name__ == "__main__":
    main()
