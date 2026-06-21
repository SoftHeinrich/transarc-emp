#!/usr/bin/env python3
"""Minimal metrics for ARDoCo doc-to-code / doc-to-model trace-link recovery.

A single, self-contained, stdlib-only reimplementation that computes ONLY the
paper's non-redundant *primary panel* — no MCC/MAP/ACF1/NDG/HUS/decision-F1/
weighted-F1/sentence-F1 (the redundancy analysis in
``reports/RQ2_METRIC_REDUNDANCY.md`` showed those are shadowed: Spearman
rho >= 0.85 with a kept metric and ~0 system-pair rank reversals).

Primary panel
-------------
    sad-code (doc-to-code) : file P/R/F1, per-component F1, sentence coverage,
                             noise rate
    sad-sam  (doc-to-model): link P/R/F1, sentence coverage, noise rate
                             (per-component F1 collapses onto link F1 with no
                             enrolment, so it is dropped)

This file deliberately does NOT import the existing ``src/`` modules
(``transarc_error_analysis``, ``evaluation_critique``, ``new_metrics_analysis``,
``generate_tables``). Every value it prints matches
``metrics_api.compute_sad_*_metrics`` for the same input set — verified in
``mini-src/check.py`` — but the whole computation lives here in ~250 lines.

Definitions are taken verbatim from ``src/lib/metrics_api.py``:
  * per-component F1 is the **micro** form (one P/R/F1 over all
    (sentence, component) pairs), matching the paper headline
    ``reports/SADCODE_S11_S13F_VS_TRANSARC.csv``.
  * sentence coverage = fraction of gold sentences with >=1 *correct* hit.
  * noise rate = mean over *predicted* sentences of FP/(TP+FP); lower is better.

Usage
-----
    python3 mini-src/metrics.py --task sad-code
    python3 mini-src/metrics.py --task sad-sam --project jabref
    python3 mini-src/metrics.py --task sad-code \
        --results-dir /path/to/run \
        --result-pattern 's_linker20_union_{project}_links.csv' \
        --csv /tmp/panel.csv

Result CSV columns are auto-detected, so both the TransArc dialect
(modelElementID, codeId / sentence) and the agent-linker dialect
(sentence, component_id, ...) are accepted.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# ── Benchmark layout (mirrors src/lib/transarc_error_analysis.py) ─────────────
# Defaults are derived from this file's location rather than hardcoded:
#   <ardoco-home>/transarc-emp/mini-src/metrics.py  →  parents[2] is ardoco-home.
# Env vars still override for out-of-tree benchmark / result roots.
_ARDOCO_HOME = Path(__file__).resolve().parents[2]
BENCHMARK = Path(os.environ.get(
    "TRANSARC_BENCHMARK",
    _ARDOCO_HOME / "ardoco/core/tests-base/src/main/resources/benchmark",
))
DEFAULT_RESULTS = Path(os.environ.get(
    "TRANSARC_RESULTS_DIR",
    _ARDOCO_HOME / "transarc-emp/results",
))

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]

GS_SAD_SAM = {
    "mediastore":    "mediastore/goldstandards/goldstandard_sad_2016-sam_2016.csv",
    "teastore":      "teastore/goldstandards/goldstandard_sad_2020-sam_2020.csv",
    "teammates":     "teammates/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "bigbluebutton": "bigbluebutton/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "jabref":        "jabref/goldstandards/goldstandard_sad_2021-sam_2021.csv",
}
GS_SAM_CODE = {
    "mediastore":    "mediastore/goldstandards/goldstandard_sam_2016-code_2016.csv",
    "teastore":      "teastore/goldstandards/goldstandard_sam_2020-code_2022.csv",
    "teammates":     "teammates/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "bigbluebutton": "bigbluebutton/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "jabref":        "jabref/goldstandards/goldstandard_sam_2021-code_2023.csv",
}
GS_SAD_CODE = {
    "mediastore":    "mediastore/goldstandards/goldstandard_sad_2016-code_2016.csv",
    "teastore":      "teastore/goldstandards/goldstandard_sad_2020-code_2022.csv",
    "teammates":     "teammates/goldstandards/goldstandard_sad_2021-code_2023.csv",
    "bigbluebutton": "bigbluebutton/goldstandards/goldstandard_sad_2021-code_2023.csv",
    "jabref":        "jabref/goldstandards/goldstandard_sad_2021-code_2023.csv",
}
ACM_FILES = {
    "mediastore":    "mediastore/model_2016/code/codeModel.acm",
    "teastore":      "teastore/model_2022/code/codeModel.acm",
    "teammates":     "teammates/model_2023/code/codeModel.acm",
    "bigbluebutton": "bigbluebutton/model_2023/code/codeModel.acm",
    "jabref":        "jabref/model_2023/code/codeModel.acm",
}

# Column-name candidates so result CSVs in every dialect are accepted:
#   - TransArc / legacy : modelElementID, codeId / sentence
#   - agent-linker      : sentence, component_id, codeID, ...
#   - recovered-links   : sentence_id, target_id (sota/recovered-links/*; the
#                         normalized SOTA-baseline dump — target_id is the PCM
#                         element id for sad-sam and the code file path for
#                         sad-code). Probed first-non-empty, so adding these is
#                         additive: files lacking the column are unaffected.
_SADSAM_COMPONENT_KEYS = ("modelElementID", "component_id", "componentId", "target_id")
_SADSAM_SENTENCE_KEYS = ("sentence", "sentence_id")
_SADCODE_SENTENCE_KEYS = ("modelElementID", "sentence", "sentence_id")
_SADCODE_CODE_KEYS = ("codeId", "codeID", "code_path", "target_id")


# ── Core metric primitives ────────────────────────────────────────────────────

def prf(gold, res):
    """(precision, recall, f1) treating gold/res as sets of links."""
    if not res:
        return 0.0, 0.0, 0.0
    tp = len(gold & res)
    precision = tp / len(res)
    recall = tp / len(gold) if gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if precision + recall > 0 else 0.0)
    return precision, recall, f1


def sentence_coverage(gold_by_s, res_by_s):
    """Fraction of gold sentences with >=1 correct prediction."""
    if not gold_by_s:
        return 0.0
    covered = sum(1 for s in gold_by_s if gold_by_s[s] & res_by_s.get(s, set()))
    return covered / len(gold_by_s)


def noise_rate(gold_by_s, res_by_s):
    """Mean FP/(TP+FP) across predicted sentences; lower is better."""
    vals = []
    for s, r in res_by_s.items():
        g = gold_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        if tp + fp > 0:
            vals.append(fp / (tp + fp))
    return sum(vals) / len(vals) if vals else 0.0


def normalize_path(path):
    """Drop the leading 'Implementation/' segment used in the gold standard."""
    prefix = "Implementation/"
    return path[len(prefix):] if path.startswith(prefix) else path


def enroll(gold, code_files):
    """Expand directory-level gold entries (trailing '/') to individual files."""
    enrolled = set()
    for gid, gpath in gold:
        if gpath.endswith("/"):
            for fp in code_files:
                if fp.startswith(gpath):
                    enrolled.add((gid, fp))
        else:
            enrolled.add((gid, gpath))
    return enrolled


# ── Loaders ───────────────────────────────────────────────────────────────────

def _cell(row, keys):
    """First non-empty value among `keys` in a DictReader row, else None."""
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


def load_code_model_files(project):
    """All compilation-unit paths from the .acm code model (normalized)."""
    files = set()
    with open(BENCHMARK / ACM_FILES[project]) as f:
        data = json.load(f)
    repo = data.get("codeItemRepository", {}).get("repository", {})
    for item in repo.values():
        if item.get("type") != "CodeCompilationUnit":
            continue
        parts, name, ext = (item.get("pathElements", []),
                            item.get("name", ""), item.get("extension", ""))
        if parts and name:
            full = "/".join(parts) + "/" + name + (f".{ext}" if ext else "")
            files.add(normalize_path(full))
    return files


def load_gs_sad_sam(project):
    """set[(modelElementID, sentence)]."""
    with open(BENCHMARK / GS_SAD_SAM[project]) as f:
        return {(r["modelElementID"], r["sentence"]) for r in csv.DictReader(f)}


def load_gs_sad_code_raw(project):
    """set[(sentenceID, normalized_path)] — pre-enrolment."""
    with open(BENCHMARK / GS_SAD_CODE[project]) as f:
        return {(r["sentenceID"], normalize_path(r["codeID"]))
                for r in csv.DictReader(f)}


def load_file_to_comps(project, code_files):
    """file_path -> {component_name}, from the enrolled SAM-CODE gold."""
    names, raw = {}, set()
    with open(BENCHMARK / GS_SAM_CODE[project]) as f:
        for r in csv.DictReader(f):
            names[r["ae_id"]] = r["ae_name"]
            raw.add((r["ae_id"], normalize_path(r.get("ce_ids") or r.get("ce_id"))))
    file_to_comps = defaultdict(set)
    for ae, fp in enroll(raw, code_files):
        file_to_comps[fp].add(names.get(ae, ae))
    return file_to_comps


def load_result(path, task):
    """Read a result CSV into a link set, auto-detecting the column dialect.

    sad-code -> set[(sentence, normalized_path)]
    sad-sam  -> set[(component_id, sentence)]
    Empty set if the file is absent.
    """
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            if task == "sad-code":
                s = _cell(row, _SADCODE_SENTENCE_KEYS)
                c = _cell(row, _SADCODE_CODE_KEYS)
                if s and c:
                    links.add((s, normalize_path(c)))
            else:
                c = _cell(row, _SADSAM_COMPONENT_KEYS)
                s = _cell(row, _SADSAM_SENTENCE_KEYS)
                if c and s:
                    links.add((c, s))
    return links


def result_path(project, results_dir, result_pattern):
    """Default TransArc layout, or `result_pattern.format(project=...)`."""
    root = Path(results_dir) if results_dir else DEFAULT_RESULTS
    if result_pattern:
        return root / result_pattern.format(project=project)
    sub, prefix = (("sad-code", "sadCodeTlr") if _TASK == "sad-code"
                   else ("sad-sam", "sadSamTlr"))
    return root / project / sub / f"{prefix}_{project}.csv"


# ── Per-project metric rows ───────────────────────────────────────────────────

def compute_sad_code(project, res):
    """Primary panel for one doc-to-code result set."""
    code_files = load_code_model_files(project)
    gold = enroll(load_gs_sad_code_raw(project), code_files)
    file_to_comps = load_file_to_comps(project, code_files)

    fp_, fr_, ff1 = prf(gold, res)

    def to_comp(pairs):
        # Mapped-only universe (v1.2, D-01): files with NO SAM-CODE component
        # are DROPPED -- no `(s, c)` singleton fallback -- matching the canonical
        # metrics_api._compute_component_f1 so mini-src/check.py stays green.
        out = set()
        for s, c in pairs:
            for comp in file_to_comps.get(c, ()):
                out.add((s, comp))
        return out
    comp_f1 = prf(to_comp(gold), to_comp(res))[2]

    gold_by_s, res_by_s = defaultdict(set), defaultdict(set)
    for s, c in gold:
        gold_by_s[s].add(c)
    for s, c in res:
        res_by_s[s].add(c)

    return {
        "project": project,
        "file_p": fp_, "file_r": fr_, "file_f1": ff1,
        "component_f1": comp_f1,
        "sentence_coverage": sentence_coverage(gold_by_s, res_by_s),
        "noise_rate": noise_rate(gold_by_s, res_by_s),
    }


def compute_sad_sam(project, res):
    """Primary panel for one doc-to-model result set."""
    gold = load_gs_sad_sam(project)
    lp, lr, lf1 = prf(gold, res)

    gold_by_s, res_by_s = defaultdict(set), defaultdict(set)
    for c, s in gold:
        gold_by_s[s].add(c)
    for c, s in res:
        res_by_s[s].add(c)

    return {
        "project": project,
        "link_p": lp, "link_r": lr, "link_f1": lf1,
        "sentence_coverage": sentence_coverage(gold_by_s, res_by_s),
        "noise_rate": noise_rate(gold_by_s, res_by_s),
    }


# ── CLI / output ──────────────────────────────────────────────────────────────

PANELS = {
    "sad-code": ["file_p", "file_r", "file_f1", "component_f1",
                 "sentence_coverage", "noise_rate"],
    "sad-sam":  ["link_p", "link_r", "link_f1",
                 "sentence_coverage", "noise_rate"],
}
HEADERS = {
    "file_p": "file_P", "file_r": "file_R", "file_f1": "file_F1",
    "link_p": "link_P", "link_r": "link_R", "link_f1": "link_F1",
    "component_f1": "comp_F1", "sentence_coverage": "sent_cov",
    "noise_rate": "noise",
}

_TASK = "sad-code"   # set in main(); read by result_path()


def average_row(rows, cols):
    avg = {"project": "Average"}
    for c in cols:
        avg[c] = sum(r[c] for r in rows) / len(rows) if rows else 0.0
    return avg


def print_table(task, rows):
    cols = PANELS[task]
    w = max(13, max((len(r["project"]) for r in rows), default=7) + 1)
    head = "project".ljust(w) + "".join(HEADERS[c].rjust(10) for c in cols)
    print(head)
    print("-" * len(head))
    for r in rows:
        line = r["project"].ljust(w) + "".join(f"{r[c]:10.4f}" for c in cols)
        print(line)
    if rows:
        avg = average_row(rows, cols)
        print("-" * len(head))
        print(avg["project"].ljust(w) + "".join(f"{avg[c]:10.4f}" for c in cols))


def write_csv(task, rows, path):
    cols = PANELS[task]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project"] + cols)
        for r in list(rows) + ([average_row(rows, cols)] if rows else []):
            w.writerow([r["project"]] + [f"{r[c]:.4f}" for c in cols])


def main():
    global _TASK
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True, choices=["sad-code", "sad-sam"])
    ap.add_argument("--project", default=None,
                    help="single project (default: all five)")
    ap.add_argument("--results-dir", default=None,
                    help="root holding result CSVs (default: bundled results/)")
    ap.add_argument("--result-pattern", default=None,
                    help="filename pattern with {project}, relative to --results-dir")
    ap.add_argument("--csv", default=None, help="also write the panel to this CSV")
    args = ap.parse_args()
    _TASK = args.task

    if args.project and args.project not in PROJECTS:
        ap.error(f"unknown project {args.project!r}; expected one of {PROJECTS}")
    projects = [args.project] if args.project else PROJECTS
    compute = compute_sad_code if args.task == "sad-code" else compute_sad_sam

    rows = []
    for proj in projects:
        path = result_path(proj, args.results_dir, args.result_pattern)
        res = load_result(path, args.task)
        if not res:
            print(f"WARNING: no {args.task} results for {proj} "
                  f"(looked in {path}), skipping", file=sys.stderr)
            continue
        rows.append(compute(proj, res))

    print_table(args.task, rows)
    if args.csv:
        write_csv(args.task, rows, args.csv)
        print(f"\n[mini-metrics] wrote {args.csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
