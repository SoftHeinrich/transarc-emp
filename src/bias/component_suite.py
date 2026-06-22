#!/usr/bin/env python3
"""Level-agnostic component-centric metric suite (macro/micro unification).

Motivation
----------
Per-component F1 has two coexisting aggregations that can *disagree in direction*
(see reports/RQ2_METRIC_REDUNDANCY.md and the bigbluebutton sign-flip):

  * MICRO  — pool every (sentence, component) pair into one P/R/F1. Volume-weighted
             (a component referenced by many sentences counts many times). At
             SAD-SAM this is exactly link F1.
  * MACRO  — F1 per component, then unweighted mean. Size-blind.

This module unifies them into ONE suite that "exploits the unequal sentence<->
component distribution" and applies at BOTH granularities:

  micro       reuse: pooled (sentence, component) F1                     [anchor]
  macro       reuse: per-component mean F1                               [headline]
  gap         micro - macro  -- signed indicator of the skew regime
  min_comp    worst single GOLD-component F1                             [tail]
  pct_missed  fraction of GOLD components scored exactly 0               [coverage]
  gold_gini   Gini of the GOLD #sentences-per-component (a descriptor,
              NOT a score) -- explains *why* gap/tail carry signal

Universe split (Phase 7, D-10 / D-11)
-------------------------------------
The HEADLINE pair (``micro`` / ``macro`` / ``gap``) is computed on the SHARED
gold∪result mapped-only component universe -- this keeps ``micro`` = link F1 at
SAD-SAM and keeps ``macro`` equal to ``rq2_trivial_baselines.per_component_macro_f1``
(the 07-03 equivalence oracle). The TAIL pair (``min_comp`` / ``pct_missed``) is
GOLD-ONLY: it measures coverage of REAL components, so a result-only
(false-positive) component scoring 0 does NOT count as "missed" or "min".

Empirically (5 ARDoCo projects):
  * doc-to-code  -- directory enrollment manufactures large skew -> the GAP
                    dominates (e.g. bigbluebutton micro .574 vs macro .883).
  * doc-to-model -- mild natural skew -> the gap is quiet, but TAIL coverage
                    (min_comp / pct_missed) dominates and reorders systems
                    (LLM linkers nail popular components, abandon the long tail).

Reconciled universe (fixes a latent trap)
------------------------------------------
The two legacy definitions did not even agree on the component universe:
``evaluation_critique._compute_component_f1`` (micro) falls back to the file path
as its own component for files with no SAM-CODE mapping (``{b}``), while
``rq2_trivial_baselines.per_component_macro_f1`` drops them (``()``). Comparing
those two is not apples-to-apples. This suite computes micro AND macro on the
SAME mapped-only universe so the gap reflects aggregation alone. (Suite-micro can
therefore differ slightly from the legacy headline micro on projects with
unmapped gold files.)

Metric math is reused: only ``calc_metrics`` (set-overlap P/R/F1) is called; the
suite adds no new F1 formula -- macro/min/pct_missed are aggregations over a list
of per-component ``calc_metrics`` F1s.

Run
---
    python3 src/bias/component_suite.py                  # both levels, all systems
    python3 src/bias/component_suite.py --level sad-code
    python3 src/bias/component_suite.py --level sad-model --project jabref
"""

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS, calc_metrics, normalize_path,
    load_code_model_files, load_model_element_names,
    load_gs_sad_sam, load_result_sad_sam_standalone,
    load_gs_sad_code_enrolled, load_gs_sam_code_raw, enroll_gold_standard,
    load_result_sad_code, load_result_sam_code_standalone,
)

REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"

# ── External system-result roots (guarded; absent => system skipped) ──────────
# Roots live as siblings of this repo under the ardoco-home workspace. Default
# the prefix to that workspace (repo's parent dir) and allow override via the
# ARDOCO_HOME env var so the suite is portable across machines.
ARDOCO_HOME = Path(os.environ.get("ARDOCO_HOME", Path(__file__).resolve().parents[3]))
# s20linker == the v45 LLM SAD-SAM pipeline (s_linker20 lineage). Its per-sentence
# component links live in the v45 evaluation_results dir as ``<prefix>_<proj>_links.csv``
# (schema: sentence,component_id,component_name,...). Override dir/prefix via env:
#   S20_LINKS_DIR    (default: llm-sad-sam-v45/results/evaluation_results)
#   S20_LINKS_PREFIX (default: "v45"; set "agent" for the adaptive-agent variant)
AGENT_LINKER = Path(os.environ.get(
    "S20_LINKS_DIR",
    ARDOCO_HOME / "llm-sad-sam-v45" / "results" / "evaluation_results"))
S20_PREFIX = os.environ.get("S20_LINKS_PREFIX", "v45")
ARTEMIS_DOC_CODE = ARDOCO_HOME / "sota-recovered-links" / "doc-code"
ARTEMIS_MODEL_DOC = ARDOCO_HOME / "sota-recovered-links" / "model-doc"

SUITE_COLS = ["micro", "macro", "gap", "min_comp", "pct_missed", "gold_gini"]


# ── Result loaders (column-tolerant) ──────────────────────────────────────────

def _read_pairs(path, a_keys, b_keys):
    """Read a CSV into a set of (a, b) string pairs over the first present keys."""
    out = set()
    if not path.exists():
        return out
    with open(path) as f:
        for row in csv.DictReader(f):
            a = _first(row, a_keys)
            b = _first(row, b_keys)
            if a and b:
                out.add((a, b))
    return out


def _first(row, keys):
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


def _compose_sad_code(sad_sam_links, sam_code_standalone):
    """SAD-SAM (comp_id, sentence) x ARCOTL SAM-CODE -> SAD-CODE (sentence, code)."""
    model_to_codes = defaultdict(set)
    for ae_id, code_path in sam_code_standalone:
        model_to_codes[ae_id].add(code_path)
    out = set()
    for ae_id, sentence in sad_sam_links:
        for code in model_to_codes.get(ae_id, ()):
            out.add((sentence, code))
    return out


# Registry: key -> {label, model(proj)->set(comp_id,sent), code(proj)->set(sent,code)}
def _swattr_model(p):
    return load_result_sad_sam_standalone(p)


def _swattr_code(p):
    return load_result_sad_code(p)


def _s20_model(p):
    return {(c, s) for c, s in _read_pairs(
        AGENT_LINKER / f"{S20_PREFIX}_{p}_links.csv",
        a_keys=("component_id", "modelElementID"), b_keys=("sentence",))}


def _s20_code(p):
    return _compose_sad_code(_s20_model(p), load_result_sam_code_standalone(p))


def _artemis_model(p):
    # model-doc CSV schema: sentence_id,target_id (target_id = model element id).
    # _model_inputs.collapse expects (comp_id, sentence) -> a=target_id, b=sentence_id.
    return _read_pairs(ARTEMIS_MODEL_DOC / f"artemis-{p}-gpt-5.4.csv",
                       a_keys=("target_id", "modelElementID", "component_id"),
                       b_keys=("sentence_id", "sentence"))


def _artemis_code(p):
    raw = _read_pairs(ARTEMIS_DOC_CODE / f"artemis-{p}-gpt-5.4.csv",
                      a_keys=("sentence_id", "sentence"), b_keys=("target_id", "codeId", "codeID"))
    return {(s, normalize_path(c)) for s, c in raw}


SYSTEMS = [
    # key,            label,              model loader,    code loader
    ("swattr_transarc", "swattr/transarc", _swattr_model, _swattr_code),
    ("s20linker",       "s20linker",       _s20_model,    _s20_code),
    ("artemis",         "artemis",         _artemis_model, _artemis_code),
]


# ── Suite math (single source of truth; reuses calc_metrics only) ─────────────

def _gini(values):
    xs = sorted(values)
    n = len(xs)
    if n == 0 or sum(xs) == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * sum(xs)) - (n + 1) / n


def component_suite(gold_sc, result_sc):
    """Compute the component suite from already-collapsed (sentence, component) sets.

    micro pools all pairs; macro aggregates per-component F1 over the SHARED
    gold∪result universe (D-10); min_comp/pct_missed aggregate per-component F1
    over the GOLD-ONLY universe (D-11). gold_gini describes the gold
    #sentences-per-component skew. Every score flows through ``calc_metrics`` --
    the suite adds no new F1 formula.
    """
    micro = calc_metrics(gold_sc, result_sc)[2]

    gold_by_c, res_by_c = defaultdict(set), defaultdict(set)
    for s, c in gold_sc:
        gold_by_c[c].add(s)
    for s, c in result_sc:
        res_by_c[c].add(s)

    def _comp_score(c):
        # Per-component F1 via the sole F1 primitive (calc_metrics) -- no new math.
        g = {(s, c) for s in gold_by_c.get(c, set())}
        r = {(s, c) for s in res_by_c.get(c, set())}
        return calc_metrics(g, r)[2]

    # Headline pair: SHARED gold∪result mapped-only universe (D-10) -> macro / gap.
    per_comp = [_comp_score(c) for c in set(gold_by_c) | set(res_by_c)]
    # Tail/coverage pair: GOLD-ONLY universe (D-11) -> min_comp / pct_missed.
    # A real gold component with no result still counts as missed/min; a
    # result-only (FP) component no longer pollutes the tail.
    per_comp_gold = [_comp_score(c) for c in set(gold_by_c)]

    macro = sum(per_comp) / len(per_comp) if per_comp else 0.0
    # min() is order-independent, so min_comp tie handling is immaterial: the
    # worst F1 value (not the component identity) is what is reported.
    min_comp = min(per_comp_gold) if per_comp_gold else 0.0
    pct_missed = (sum(1 for x in per_comp_gold if x == 0.0) / len(per_comp_gold)
                  if per_comp_gold else 0.0)
    gold_gini = _gini([len(v) for v in gold_by_c.values()])

    return {"micro": micro, "macro": macro, "gap": micro - macro,
            "min_comp": min_comp, "pct_missed": pct_missed, "gold_gini": gold_gini}


# ── Per-level collapse to (sentence, component) ───────────────────────────────

def _model_inputs(proj):
    """doc-to-model: gold + a collapse(links)->(sentence, comp_name)."""
    names = load_model_element_names(proj)
    gold = {(s, names.get(c, c)) for c, s in load_gs_sad_sam(proj)}

    def collapse(links):  # links: set[(comp_id, sentence)]
        return {(s, names.get(c, c)) for c, s in links}

    return gold, collapse


def _code_inputs(proj):
    """doc-to-code: enrolled gold + a collapse(links)->(sentence, comp_name).

    Reconciled universe: a (sentence, file) pair contributes one
    (sentence, component) pair per mapped component; files with NO SAM-CODE
    component are DROPPED (same rule for gold and result, so micro/macro align).
    """
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)
    sam_enrolled = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
    file_to_comps = defaultdict(set)
    for ae, fp in sam_enrolled:
        file_to_comps[fp].add(names.get(ae, ae))

    enrolled = load_gs_sad_code_enrolled(proj, code_model)  # set[(sentence, file)]

    def collapse(links):  # links: set[(sentence, file)]
        out = set()
        for s, f in links:
            for comp in file_to_comps.get(f, ()):
                out.add((s, comp))
        return out

    gold = collapse(enrolled)
    return gold, collapse


LEVELS = {
    "sad-model": (_model_inputs, lambda key, m, c: m),
    "sad-code":  (_code_inputs,  lambda key, m, c: c),
}


# ── Driver ────────────────────────────────────────────────────────────────────

def run_level(level, projects):
    build_inputs, pick_loader = LEVELS[level]
    rows = []  # (project, system_key, system_label, metrics)
    for proj in projects:
        gold, collapse = build_inputs(proj)
        for key, label, mloader, cloader in SYSTEMS:
            loader = pick_loader(key, mloader, cloader)
            links = loader(proj)
            if not links:
                _warn_skip(level, label, proj)
                continue
            result_sc = collapse(links)
            rows.append((proj, key, label, component_suite(gold, result_sc)))
    return rows


def _warn_skip(level, label, proj):
    # Standardized absent/empty-external-root notice (stderr; WARNING: prefix).
    print(f"WARNING: no {level} result links for system={label} project={proj} "
          f"(absent or empty external root); skipping", file=sys.stderr)


def averages(rows):
    by_sys = defaultdict(lambda: defaultdict(list))
    labels = {}
    for proj, key, label, m in rows:
        labels[key] = label
        for c in SUITE_COLS:
            by_sys[key][c].append(m[c])
    out = []
    for key, cols in by_sys.items():
        avg = {c: sum(cols[c]) / len(cols[c]) for c in SUITE_COLS}
        out.append((key, labels[key], avg))
    return out


def _fmt(v):
    return f"{v:+.3f}" if v < 0 else f"{v:.3f}"


def write_csv(level, rows, avg):
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"COMPONENT_SUITE_{level}.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "system"] + SUITE_COLS)
        for proj, _key, label, m in rows:
            w.writerow([proj, label] + [f"{m[c]:.4f}" for c in SUITE_COLS])
        for _key, label, m in avg:
            w.writerow(["AVG", label] + [f"{m[c]:.4f}" for c in SUITE_COLS])
    return out


def print_table(level, avg):
    print(f"\n=== {level} — average over projects ===")
    print(f"{'system':18}" + "".join(f"{c:>11}" for c in SUITE_COLS))
    for _key, label, m in avg:
        print(f"{label:18}" + "".join(f"{_fmt(m[c]):>11}" for c in SUITE_COLS))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--level", choices=["sad-model", "sad-code", "both"],
                    default="both",
                    help="granularity to run: 'sad-model' (doc-to-model), "
                         "'sad-code' (doc-to-code), or 'both' (default).")
    ap.add_argument("--project", default=None,
                    help="restrict to a single project (one of PROJECTS); default "
                         "= all projects. NOTE: a single-project run still writes "
                         "the same COMPONENT_SUITE_<level>.csv and therefore "
                         "OVERWRITES the full committed file -- run with no "
                         "--project to regenerate the authoritative committed CSVs.")
    args = ap.parse_args()

    projects = [args.project] if args.project else list(PROJECTS)
    if args.project and args.project not in PROJECTS:
        sys.exit(f"unknown project {args.project!r}; expected one of {PROJECTS}")

    levels = ["sad-model", "sad-code"] if args.level == "both" else [args.level]
    for level in levels:
        rows = run_level(level, projects)
        avg = averages(rows)
        csv_path = write_csv(level, rows, avg)
        print_table(level, avg)
        print(f"[component-suite] level={level} rows={len(rows)} csv={csv_path}")


if __name__ == "__main__":
    main()
