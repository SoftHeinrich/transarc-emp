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
"""

import csv
import math
import sys
import argparse
from collections import defaultdict
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────
# metrics_api.py lives IN src/lib, so the self-import target is `parent`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transarc_error_analysis import (
    PROJECTS, RESULTS, calc_metrics,
    load_code_model_files,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_maps,
    load_result_sad_sam_standalone,
    load_result_sad_code, load_text, load_model_element_names,
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
from generate_tables import render_table, write_table

# ── Paths (hardcoded-absolute-path convention) ────────────────────────────────
REPORTS = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports")

# ── Unified column schema (superset across both tasks) ────────────────────────
SCHEMA = [
    "project", "link_f1", "sentence_f1", "decision_f1", "component_f1",
    "file_f1", "weighted_f1", "mcc", "map", "acf1", "ndg", "hus",
]
NUMERIC_COLS = SCHEMA[1:]  # everything except "project"

NA = "—"      # em dash — CSV inapplicable cells
NA_TEX = "--"      # LaTeX inapplicable cells

# LaTeX display header (contains \fone macros → must use header_override).
LATEX_HEADER = [
    "Project", "Link \\fone", "Sentence \\fone", "Decision \\fone",
    "Component \\fone", "File \\fone", "Weighted \\fone",
    "MCC", "MAP", "ACF1", "NDG", "HUS",
]


def _fmt(v):
    """Format a numeric value to 3 decimals; pass NA / strings through."""
    if isinstance(v, (int, float)):
        return f"{v:.3f}"
    return v


def select_projects(args):
    """Return the list of projects to process, validating --project."""
    if args.project:
        if args.project not in PROJECTS:
            print(f"ERROR: unknown project '{args.project}' "
                  f"(expected one of {PROJECTS})", file=sys.stderr)
            sys.exit(2)
        return [args.project]
    return list(PROJECTS)


# ── Placeholder computations (replaced in Tasks 2 and 3) ──────────────────────

def compute_sad_sam_row(proj):
    """Compute the SAD-SAM metric row for the standalone (TransArc) result.

    SAD-SAM has NO files and NO enrollment — work directly on
    (modelElementID, sentence) pairs. The evaluation_critique `_compute_*`
    helpers are NOT used here (they require enrollment maps that do not
    exist for sad-sam). Returns None (skip + warn) if the results file is
    absent.
    """
    res = load_result_sad_sam_standalone(proj)         # set() if file absent
    if not res:
        print(f"WARNING: no sad-sam results for {proj}, skipping",
              file=sys.stderr)
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
    pred_correct_sentences = {
        s for s in res_by_s
        if gold_by_s.get(s) and (gold_by_s[s] & res_by_s[s])
    }
    gold_S = {(s, "*") for s in gold_by_s}
    res_S = {(s, "*") for s in res_by_s if s in pred_correct_sentences}
    row["sentence_f1"] = calc_metrics(gold_S, res_S)[2]

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


def compute_sad_code_row(proj):
    """Compute the SAD-CODE metric row for the standalone (TransArc) result.

    Reuses the evaluation_critique granularity helpers verbatim (the
    part5_alternative_metrics caller idiom is the exact reference). Returns
    None (skip + warn) if the results file is absent.
    """
    res = load_result_sad_code(proj)                   # set() if file absent
    if not res:
        print(f"WARNING: no sad-code results for {proj}, skipping",
              file=sys.stderr)
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

    # Alt metrics (sad-code).
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)  # model_id -> set(files)
    row["acf1"] = compute_acf1(enrolled, res, gs_sam_code_map)["acf1"]

    # NDG = (system_f1 - random_f1) / (oracle_f1 - random_f1).
    system_f1 = file_f1
    n_sentences = len({s for (s, _c) in enrolled})
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
    args = parser.parse_args()

    task = args.task
    projects = select_projects(args)
    compute = compute_sad_sam_row if task == "sad-sam" else compute_sad_code_row

    rows = []
    for proj in projects:
        row = compute(proj)
        if row is not None:
            rows.append(row)

    if not rows:
        print(f"WARNING: no results found for any project on task {task}; "
              f"writing header + empty Average only.", file=sys.stderr)

    avg_row = build_avg_row(rows)
    csv_path = write_csv(task, rows, avg_row)
    tex_path = write_latex(task, rows, avg_row)

    print(f"[metrics-api] task={task} projects={len(rows)} "
          f"csv={csv_path} tex={tex_path}")


if __name__ == "__main__":
    main()
