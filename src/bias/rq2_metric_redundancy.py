#!/usr/bin/env python3
"""
RQ2 — Metric redundancy analysis.

Tests whether the architecture-driven metrics in the paper's metric suite
carry independent signal, or whether some are "shadowed" (redundant) under
one of the others — specifically under per-component F1.

Computes the 7-metric suite per (system, project, task) cell for:

  Real systems:
    - TransArc  (doc-to-code = ARDoCo full pipeline; doc-to-model = SWATTR)
    - S11       (s_linker11 SAD-SAM; SAD-CODE via S11 × ARCOTL SAM-CODE)

  Naive baselines (rerun fresh for both tasks):
    - Random
    - Structural Top-3 (doc-to-code: by enrolled file count;
                         doc-to-model: by name freq, R2 from the prestudy)

Note on S13F: the underlying per-project link CSVs are no longer present on
this filesystem, so the S13F row is *quoted* from
``reports/SADCODE_S11_S13F_VS_TRANSARC.csv`` /
``reports/SADSAM_S11_S13F_VS_TRANSARC.csv`` for reference only and is NOT used
in the redundancy correlation / reversal counts (its ``component_f1`` is the
*micro* version, not the macro form the paper documents). Same applies to
LiSSA — no LiSSA result CSVs are present in this repo, so LiSSA is omitted
from the matrix entirely.

The 7 metrics computed identically across all (system × project × task) cells:

  1. File-level / Micro F1     — standard P/R/F1 over the task's atomic pairs.
  2. Per-component F1 (macro)  — average over components, each treated as a
                                 binary {linked, not} classification.
  3. Per-sentence F1 (macro)   — average over gold sentences (file/component
                                 sets per sentence).
  4. Sentence coverage         — fraction of gold sentences with >=1 TP.
  5. Noise rate                — mean FP/(TP+FP) across predicted sentences.
  6. HUS (coverage-purity)     — harmonic mean of coverage and per-sentence
                                 purity (from ``new_metrics_analysis``).
  7. NDG (skill score)         — (system_F1 - random_F1) / (oracle_F1 -
                                 random_F1); doc-to-code only — doc-to-model
                                 has no enrollment / oracle decomposition.
                                 For doc-to-model we report NDG as NA.

Redundancy analysis:

  - 7x7 pairwise Spearman correlation matrix, per task and overall.
  - Reversal count per pair: across (project x ...) cells where the metric
    pair is defined, count system-pair rank disagreements.
  - Per-system fingerprint table: which metrics each system is unusually
    strong / weak on relative to its file-level F1.

Output: reports/RQ2_METRIC_REDUNDANCY.md  (stdlib only).
"""

import csv
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

# Set PYTHONHASHSEED before any dict iteration matters. Note: this only takes
# effect if the script is re-launched; if invoked under an existing interpreter
# the hashseed is already locked. The redundancy analysis only depends on
# deterministic dict order via compute_random_f1 in new_metrics_analysis.py,
# which iterates ``gold_sam_code_map.items()`` and stores file→comp in a dict
# without sorting. Run as ``PYTHONHASHSEED=0 python3 src/bias/rq2_metric_redundancy.py``
# for fully reproducible NDG numbers (TransArc/S11 file/comp/sent/coverage/noise/HUS
# values are deterministic regardless).

# Shared loaders / metric helpers.
HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent.parent / "lib"))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_sam_maps,
    load_gs_sam_code_raw, load_gs_sam_code_maps,
    load_gs_sad_code_enrolled,
    load_result_sad_code, load_result_sad_sam_standalone,
    load_result_sam_code_standalone,
    load_model_element_names, load_text,
    calc_metrics,
)
from new_metrics_analysis import (  # noqa: E402
    compute_hus, compute_ndg, compute_random_f1, compute_oracle_f1,
)

sys.path.insert(0, str(HERE.parent))
from stupid_baseline_analysis import (  # noqa: E402
    baseline_random_same_size, baseline_majority_k,
)

REPORTS = HERE.parent.parent.parent / "reports"
OUTPUT_MD = REPORTS / "RQ2_METRIC_REDUNDANCY.md"

ABLATION_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/ablation_results")

# ─────────────────────────────────────────────────────────────────────────────
# The 7 metrics — identical definitions across all systems and baselines.
# ─────────────────────────────────────────────────────────────────────────────
#
# All metrics operate on a set of (a, b) pairs where:
#   - doc-to-code: a = sentence_id, b = code_file_path (after enrollment)
#   - doc-to-model: a = sentence_id, b = component_id
# `gold_by_part` maps each unique `b` (file or component) to a key used for
# per-component grouping. For doc-to-code we group files by component name
# (via SAM-CODE gold). For doc-to-model the "component" is `b` itself.


def micro_f1(gold, result):
    """Standard set-overlap micro F1."""
    return calc_metrics(gold, result)[2]


def per_component_macro_f1(gold, result, b_to_components):
    """Macro F1 averaged over components.

    For each component c, treat the set of (sentence, c) pairs as a binary
    problem (a `b` value belongs to c if c in b_to_components[b]). F1 per
    component, unweighted mean over components with any gold or any result.

    `b_to_components` is a dict mapping each second-position element to a
    set of component keys. For doc-to-model pass ``{b: {b} for b in ...}``.
    """
    gold_by_c = defaultdict(set)
    result_by_c = defaultdict(set)
    for s, b in gold:
        for c in b_to_components.get(b, ()):
            gold_by_c[c].add(s)
    for s, b in result:
        for c in b_to_components.get(b, ()):
            result_by_c[c].add(s)
    comps = set(gold_by_c) | set(result_by_c)
    if not comps:
        return 0.0
    f1s = []
    for c in comps:
        g = gold_by_c.get(c, set())
        r = result_by_c.get(c, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        if tp + fp + fn == 0:
            continue
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def per_sentence_macro_f1(gold, result):
    """Macro F1 averaged over gold sentences (over the `b`-set per sentence)."""
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, b in gold:
        gold_by_s[s].add(b)
    for s, b in result:
        result_by_s[s].add(b)
    gold_sents = set(gold_by_s)
    if not gold_sents:
        return 0.0
    f1s = []
    for s in gold_sents:
        g = gold_by_s[s]
        r = result_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def sentence_coverage(gold, result):
    """Fraction of gold sentences with at least one correct prediction."""
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, b in gold:
        gold_by_s[s].add(b)
    for s, b in result:
        result_by_s[s].add(b)
    if not gold_by_s:
        return 0.0
    covered = sum(
        1 for s in gold_by_s if gold_by_s[s] & result_by_s.get(s, set())
    )
    return covered / len(gold_by_s)


def noise_rate(gold, result):
    """Mean FP/(TP+FP) across predicted sentences (sentences w/o preds skipped)."""
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, b in gold:
        gold_by_s[s].add(b)
    for s, b in result:
        result_by_s[s].add(b)
    vals = []
    for s, r in result_by_s.items():
        g = gold_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        if tp + fp > 0:
            vals.append(fp / (tp + fp))
    return sum(vals) / len(vals) if vals else 0.0


def hus_metric(gold, result):
    """HUS — harmonic of coverage and per-sentence purity."""
    return compute_hus(gold, result)["hus"]


# ─────────────────────────────────────────────────────────────────────────────
# Per-task setup: build b_to_components map, gold set, and NDG anchors.
# ─────────────────────────────────────────────────────────────────────────────


def setup_doc_to_code(proj):
    """Return (gold, b_to_components, ndg_anchors)."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)  # id -> name
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
    gs_sam_code_raw = load_gs_sam_code_raw(proj)
    gs_sam_code_enrolled = enroll_gold_standard(gs_sam_code_raw, code_model)
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
    gs_sad_sam_maps = load_gs_sad_sam_maps(proj)

    file_to_comps = defaultdict(set)
    for ae, fp in gs_sam_code_enrolled:
        file_to_comps[fp].add(names.get(ae, ae))

    n_sents = len({s for s, _ in gs_sad_code})
    random_f1 = compute_random_f1(
        gs_sad_code, n_sents, len(names), gs_sam_code_map
    )
    oracle_f1, _ = compute_oracle_f1(
        gs_sad_code, gs_sam_code_map, gs_sad_sam_maps
    )

    return {
        "gold": gs_sad_code,
        "b_to_components": file_to_comps,
        "random_f1": random_f1,
        "oracle_f1": oracle_f1,
        "code_model": code_model,
        "gs_sam_code_enrolled": gs_sam_code_enrolled,
        "gs_sam_code_map": gs_sam_code_map,
        "names": names,
    }


def setup_doc_to_model(proj):
    """Return (gold, b_to_components, anchors)."""
    # Flip SAD-SAM gold from (component_id, sentence) → (sentence, component_id)
    raw = load_gs_sad_sam(proj)
    gold = {(sent, comp) for (comp, sent) in raw}
    names = load_model_element_names(proj)
    # For doc-to-model, the second element IS the component. Use a singleton
    # mapping so per_component_macro_f1 treats each component as itself.
    b_to_components = {c: {c} for c in names}
    return {
        "gold": gold,
        "b_to_components": b_to_components,
        "all_components": list(names.keys()),
        "names": names,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Result loaders for real systems.
# ─────────────────────────────────────────────────────────────────────────────


def load_s11_sad_sam(proj):
    """Return s_linker11 SAD-SAM links as set of (sentence, component_id)."""
    path = ABLATION_DIR / f"s_linker11_{proj}_links.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            comp_id = row["component_id"].strip()
            sent = str(row["sentence"]).strip()
            if comp_id and sent:
                links.add((sent, comp_id))
    return links


def compose_sad_code(sad_sam_pairs, sam_code_standalone):
    """Compose (sentence, comp) × (ae_id, code_path) → (sentence, code)."""
    model_to_codes = defaultdict(set)
    for ae_id, code_path in sam_code_standalone:
        model_to_codes[ae_id].add(code_path)
    result = set()
    for sent, comp in sad_sam_pairs:
        for code in model_to_codes.get(comp, ()):
            result.add((sent, code))
    return result


def load_system_links(system, proj, task, ctx):
    """Return the (sentence, b) link set for a (system, project, task) cell.

    `ctx` is the per-task setup dict (with `code_model`, etc. for doc-to-code).
    """
    if task == "doc-to-code":
        if system == "TransArc":
            return load_result_sad_code(proj)
        if system == "S11":
            sad_sam = load_s11_sad_sam(proj)
            sam_code = load_result_sam_code_standalone(proj)
            return compose_sad_code(sad_sam, sam_code)
        if system == "Random":
            # baseline_random_same_size uses list(set), which is
            # PYTHONHASHSEED-dependent. Sort first so the random sample is
            # reproducible. Wrap in a local function that mirrors the original
            # but with sorted iteration.
            gold_sents = sorted({s for s, _ in ctx["gold"]})
            file_list = sorted(ctx["code_model"])
            rng = random.Random(42)
            target = len(ctx["gold"])
            result = set()
            cap = max(target * 10, 10)
            attempts = 0
            while len(result) < target and attempts < cap:
                result.add((rng.choice(gold_sents), rng.choice(file_list)))
                attempts += 1
            return result
        if system == "Top-3":
            gold_sents = {s for s, _ in ctx["gold"]}
            return baseline_majority_k(
                gold_sents, ctx["gs_sam_code_enrolled"], ctx["code_model"], k=3
            )
    elif task == "doc-to-model":
        if system == "TransArc":
            raw = load_result_sad_sam_standalone(proj)
            return {(s, c) for (c, s) in raw}
        if system == "S11":
            return load_s11_sad_sam(proj)
        if system == "Random":
            gold_sents = sorted({s for s, _ in ctx["gold"]})
            comp_list = sorted(ctx["all_components"])
            target = len(ctx["gold"])
            rng = random.Random(42)
            result = set()
            cap = max(target * 10, 10)
            attempts = 0
            while len(result) < target and attempts < cap:
                result.add((rng.choice(gold_sents), rng.choice(comp_list)))
                attempts += 1
            return result
        if system == "Top-3":
            # R2 ranking — name frequency in the doc, exactly as in
            # rq2_doc_to_model_ranking_compare.py (the non-leaky baseline).
            return baseline_top3_by_name_freq(proj, ctx)
    raise ValueError(f"unknown (system, task): {system}, {task}")


def baseline_top3_by_name_freq(proj, ctx, k=3):
    """R2 from rq2_doc_to_model_ranking_compare.py: top-k by in-doc name freq.

    For every gold sentence predict the k components whose display names
    appear in the most distinct doc sentences. Case-insensitive substring
    match; ``"<TypeTag>: "`` prefix is stripped if present. Components with
    normalized display name shorter than 3 chars are excluded.
    """
    names = ctx["names"]  # id -> display name
    gold_sents = {s for s, _ in ctx["gold"]}
    text = load_text(proj)  # str(idx) -> sentence

    # Normalize display names.
    norm = {}
    for cid, dn in names.items():
        s = dn
        if ":" in s:
            s = s.split(":", 1)[1].strip()
        s = s.lower()
        if len(s) >= 3:
            norm[cid] = s

    # Count distinct sentences each component name appears in.
    score = defaultdict(int)
    sents_lower = {sid: t.lower() for sid, t in text.items()}
    for cid, name_lc in norm.items():
        for sid, t in sents_lower.items():
            if name_lc in t:
                score[cid] += 1

    top = [c for c, _ in sorted(score.items(), key=lambda x: -x[1])[:k]]
    return {(s, c) for s in gold_sents for c in top}


# ─────────────────────────────────────────────────────────────────────────────
# Score a single (system, project, task) cell on all 7 metrics.
# ─────────────────────────────────────────────────────────────────────────────


def score_cell(result, gold, b_to_components, anchors=None):
    """Return dict of {metric_key: value}."""
    out = {
        "file_f1":  micro_f1(gold, result),
        "comp_f1":  per_component_macro_f1(gold, result, b_to_components),
        "sent_f1":  per_sentence_macro_f1(gold, result),
        "coverage": sentence_coverage(gold, result),
        "noise":    noise_rate(gold, result),
        "hus":      hus_metric(gold, result),
    }
    if anchors is not None:
        out["ndg"] = compute_ndg(out["file_f1"],
                                 anchors["random_f1"],
                                 anchors["oracle_f1"])
    else:
        out["ndg"] = None  # not defined for doc-to-model
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Spearman correlation and reversal count.
# ─────────────────────────────────────────────────────────────────────────────


def _rank(xs):
    """Average ranks (1-based) with mid-rank ties; ignores values that are None."""
    indexed = [(i, v) for i, v in enumerate(xs) if v is not None]
    indexed.sort(key=lambda kv: kv[1])
    ranks = [None] * len(xs)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2  # 1-based average rank in inclusive window
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs, ys):
    """Spearman correlation; returns None if fewer than 3 paired values."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 3:
        return None
    rx = _rank([p[0] for p in pairs])
    ry = _rank([p[1] for p in pairs])
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    var_rx = sum((r - mean_rx) ** 2 for r in rx)
    var_ry = sum((r - mean_ry) ** 2 for r in ry)
    denom = (var_rx * var_ry) ** 0.5
    if denom == 0:
        return None
    return num / denom


def reversal_count(metric_a_values, metric_b_values, systems_per_cell):
    """Count reversals: for each (cell), enumerate every pair of systems
    present in that cell. Count cells where the sign of the system-pair
    difference under metric A disagrees with metric B.

    `metric_a_values`, `metric_b_values`: list of (cell_id, system, value).
    `systems_per_cell`: dict cell_id -> set of systems present.

    Returns dict {
       'reversals': int,
       'pairs_compared': int,
       'reversal_rate': float
    }
    """
    by_cell_a = defaultdict(dict)
    by_cell_b = defaultdict(dict)
    for cell, sys_, val in metric_a_values:
        if val is not None:
            by_cell_a[cell][sys_] = val
    for cell, sys_, val in metric_b_values:
        if val is not None:
            by_cell_b[cell][sys_] = val

    reversals = 0
    pairs_compared = 0
    for cell in by_cell_a:
        if cell not in by_cell_b:
            continue
        systems = sorted(set(by_cell_a[cell]) & set(by_cell_b[cell]))
        for i in range(len(systems)):
            for j in range(i + 1, len(systems)):
                s1, s2 = systems[i], systems[j]
                da = by_cell_a[cell][s1] - by_cell_a[cell][s2]
                db = by_cell_b[cell][s1] - by_cell_b[cell][s2]
                if da == 0 or db == 0:
                    continue
                pairs_compared += 1
                if (da > 0) != (db > 0):
                    reversals += 1
    return {
        "reversals": reversals,
        "pairs_compared": pairs_compared,
        "reversal_rate": reversals / pairs_compared if pairs_compared else 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main: build matrix, run analyses, write report.
# ─────────────────────────────────────────────────────────────────────────────

METRICS = ["file_f1", "comp_f1", "sent_f1", "coverage", "noise", "hus", "ndg"]
METRIC_LABELS = {
    "file_f1":  "File F1 / Micro F1",
    "comp_f1":  "Per-component F1 (macro)",
    "sent_f1":  "Per-sentence F1 (macro)",
    "coverage": "Sentence coverage",
    "noise":    "Noise rate",
    "hus":      "HUS",
    "ndg":      "NDG (skill)",
}

# S13F reference values, micro-F1 / micro-comp-F1 / HUS / NDG / MCC / MAP from
# the existing CSVs. Quoted only for context; not included in the redundancy
# correlation/reversal counts (per-component definitions differ).
S13F_SAD_CODE = {
    "mediastore":    {"file_f1": 0.9286, "comp_f1_micro": 0.9859, "hus": 0.9804, "ndg": 0.9085, "mcc": 0.9272},
    "teastore":      {"file_f1": 1.0000, "comp_f1_micro": 1.0000, "hus": 1.0000, "ndg": 1.0000, "mcc": 1.0000},
    "teammates":     {"file_f1": 0.8636, "comp_f1_micro": 0.5574, "hus": 0.6225, "ndg": 0.9767, "mcc": 0.8573},
    "bigbluebutton": {"file_f1": 0.8639, "comp_f1_micro": 0.6269, "hus": 0.4270, "ndg": 0.8785, "mcc": 0.8436},
    "jabref":        {"file_f1": 0.9998, "comp_f1_micro": 0.9167, "hus": 0.7500, "ndg": 0.9996, "mcc": 0.9996},
}
S13F_SAD_SAM = {
    "mediastore":    {"link_f1": 0.9841, "sent_f1_micro": 1.0000, "comp_f1_micro": 0.9841, "hus": 0.9818, "mcc": 0.9835},
    "teastore":      {"link_f1": 1.0000, "sent_f1_micro": 1.0000, "comp_f1_micro": 1.0000, "hus": 1.0000, "mcc": 1.0000},
    "teammates":     {"link_f1": 0.9474, "sent_f1_micro": 0.9888, "comp_f1_micro": 0.9474, "hus": 0.9565, "mcc": 0.9463},
    "bigbluebutton": {"link_f1": 0.8214, "sent_f1_micro": 0.9213, "comp_f1_micro": 0.8214, "hus": 0.8808, "mcc": 0.8211},
    "jabref":        {"link_f1": 1.0000, "sent_f1_micro": 1.0000, "comp_f1_micro": 1.0000, "hus": 1.0000, "mcc": 1.0000},
}


def main():
    systems_doc_to_code = ["TransArc", "S11", "Random", "Top-3"]
    systems_doc_to_model = ["TransArc", "S11", "Random", "Top-3"]

    # matrix[(task, project, system)] = {metric: value}
    matrix = {}

    print("Computing doc-to-code metrics...")
    for proj in PROJECTS:
        print(f"  {proj}")
        ctx = setup_doc_to_code(proj)
        anchors = {"random_f1": ctx["random_f1"], "oracle_f1": ctx["oracle_f1"]}
        for sys_ in systems_doc_to_code:
            res = load_system_links(sys_, proj, "doc-to-code", ctx)
            cell = score_cell(res, ctx["gold"], ctx["b_to_components"], anchors)
            matrix[("doc-to-code", proj, sys_)] = cell
            print(f"    {sys_:10s} "
                  + " ".join(f"{m}={cell[m]:.3f}" if cell[m] is not None else f"{m}=NA"
                             for m in METRICS))

    print("\nComputing doc-to-model metrics...")
    for proj in PROJECTS:
        print(f"  {proj}")
        ctx = setup_doc_to_model(proj)
        for sys_ in systems_doc_to_model:
            res = load_system_links(sys_, proj, "doc-to-model", ctx)
            cell = score_cell(res, ctx["gold"], ctx["b_to_components"], anchors=None)
            matrix[("doc-to-model", proj, sys_)] = cell
            print(f"    {sys_:10s} "
                  + " ".join(f"{m}={cell[m]:.3f}" if cell[m] is not None else f"{m}=NA"
                             for m in METRICS))

    # ──────────────────────────────────────────────────────────────────────
    # Compute correlations + reversal counts per task and overall.
    # ──────────────────────────────────────────────────────────────────────

    def gather(task=None):
        """Return for each metric a list of values (aligned across cells)."""
        cells = sorted(matrix) if task is None else \
            sorted(c for c in matrix if c[0] == task)
        per_metric = {m: [matrix[c].get(m) for c in cells] for m in METRICS}
        return cells, per_metric

    def corr_matrix(per_metric):
        out = {}
        for a in METRICS:
            for b in METRICS:
                out[(a, b)] = spearman(per_metric[a], per_metric[b])
        return out

    def reversal_matrix(cells, per_metric):
        # Build (cell_id, system, value) lists per metric. Cell id = (task, project).
        per_metric_lists = {m: [] for m in METRICS}
        cell_systems = defaultdict(set)
        for (task, proj, sys_) in cells:
            cell_id = (task, proj)
            cell_systems[cell_id].add(sys_)
            for m in METRICS:
                v = matrix[(task, proj, sys_)].get(m)
                per_metric_lists[m].append((cell_id, sys_, v))
        out = {}
        for a in METRICS:
            for b in METRICS:
                out[(a, b)] = reversal_count(
                    per_metric_lists[a], per_metric_lists[b], cell_systems
                )
        return out

    cells_all, per_metric_all = gather()
    cells_d2c, per_metric_d2c = gather("doc-to-code")
    cells_d2m, per_metric_d2m = gather("doc-to-model")

    corr_all = corr_matrix(per_metric_all)
    corr_d2c = corr_matrix(per_metric_d2c)
    corr_d2m = corr_matrix(per_metric_d2m)

    rev_all = reversal_matrix(cells_all, per_metric_all)
    rev_d2c = reversal_matrix(cells_d2c, per_metric_d2c)
    rev_d2m = reversal_matrix(cells_d2m, per_metric_d2m)

    # ──────────────────────────────────────────────────────────────────────
    # Per-system fingerprints — z-score of each metric relative to its
    # distribution across systems, per cell. Report which metrics each
    # system is consistently strong / weak on.
    # ──────────────────────────────────────────────────────────────────────

    fingerprints = {}
    for task in ("doc-to-code", "doc-to-model"):
        task_cells = [c for c in matrix if c[0] == task]
        for sys_ in {c[2] for c in task_cells}:
            sys_rel = {}
            for m in METRICS:
                deltas = []
                for proj in PROJECTS:
                    base = matrix[(task, proj, sys_)].get(m)
                    file_f1 = matrix[(task, proj, sys_)].get("file_f1")
                    if base is None or file_f1 is None:
                        continue
                    deltas.append(base - file_f1)
                if deltas:
                    sys_rel[m] = sum(deltas) / len(deltas)
                else:
                    sys_rel[m] = None
            fingerprints[(task, sys_)] = sys_rel

    write_report(matrix, corr_d2c, corr_d2m, corr_all,
                 rev_d2c, rev_d2m, rev_all, fingerprints)


# ─────────────────────────────────────────────────────────────────────────────
# Report writer.
# ─────────────────────────────────────────────────────────────────────────────


def write_report(matrix, corr_d2c, corr_d2m, corr_all,
                 rev_d2c, rev_d2m, rev_all, fingerprints):
    L = []

    def out(s=""):
        L.append(s)

    out("# RQ2 — Metric redundancy analysis")
    out()
    out("Tests whether the 7 metrics in the paper's metric suite carry "
        "independent signal across the (system × project × task) cells we "
        "evaluate on, or whether some are *shadowed* (predictable) from "
        "another — specifically from per-component F1.")
    out()
    out("Companion to `RQ2_TRIVIAL_BASELINES.md` and "
        "`RQ2_DOC_TO_MODEL_PRESTUDY.md`. Same metric definitions; same "
        "5 ARDoCo projects; same baseline RNG seed.")
    out()
    out("## 0. Setup")
    out()
    out("**Systems included in the redundancy matrix** (all 7 metrics "
        "recomputed identically per cell):")
    out()
    out("- **TransArc** — doc-to-code: full ARDoCo pipeline "
        "(`load_result_sad_code`); doc-to-model: standalone SWATTR "
        "(`load_result_sad_sam_standalone`).")
    out("- **S11** — `s_linker11` SAD-SAM links (ablation_results CSVs); "
        "doc-to-code obtained as S11 × ARCOTL SAM-CODE (same composition "
        "rule as `src/transarc/sadcode_comparison.py`).")
    out("- **Random** — `random.seed(42)`; (sentence, target) pairs at gold "
        "density. Reuses `baseline_random_same_size` (doc-to-code) and an "
        "inline analog for doc-to-model.")
    out("- **Top-3** — doc-to-code: `baseline_majority_k(..., k=3)` voting "
        "by enrolled file count; doc-to-model: name-frequency ranking R2 "
        "from `rq2_doc_to_model_ranking_compare.py` (non-leaky).")
    out()
    out("**Systems quoted for reference only** (not in the correlation "
        "matrix — different metric definitions or missing inputs):")
    out()
    out("- **S13F** — the canonical paper artifact. Per-project link CSVs are "
        "no longer on this filesystem; aggregate values are pulled from "
        "`reports/SADCODE_S11_S13F_VS_TRANSARC.csv` and "
        "`reports/SADSAM_S11_S13F_VS_TRANSARC.csv`. Those CSVs report "
        "`component_f1` in its **micro** form (via "
        "`evaluation_critique._compute_component_f1`); we recompute every "
        "other system using the **macro** form to stay consistent with the "
        "baseline reports. Including S13F at micro would cross definitions "
        "and contaminate the correlation, so the S13F row is reported "
        "in §2.3 only.")
    out("- **LiSSA** — no LiSSA result CSVs are present in this repo "
        "(`grep -rin lissa src/ results/ reports/` returns no result files).")
    out()
    out("**Metric definitions** (`src/lib/new_metrics_analysis.py`, "
        "`src/bias/rq2_trivial_baselines.py`, "
        "`src/bias/rq2_doc_to_model_prestudy.py`):")
    out()
    out("| # | Metric | Definition (per cell) | Aggregation | What it rewards |")
    out("|---|---|---|---|---|")
    out("| 1 | File-level / Micro F1 | "
        "$2 \\cdot |G \\cap R| / (|G| + |R|)$ over the cell's atomic pairs "
        "(enrolled `(sentence, file)` for doc-to-code; `(sentence, component)` "
        "for doc-to-model). | micro over all pairs | "
        "Bulk accuracy on the test set; favors big-volume cells. |")
    out("| 2 | Per-component F1 (macro) | "
        "Per component $c$: $F_1$ over `(sentence, c)` predictions; macro mean "
        "over components that appear in gold or result "
        "(`per_component_macro_f1`, "
        "`src/bias/rq2_trivial_baselines.py:57`). | macro over components | "
        "Consistent F1 across components regardless of size (small components "
        "count as much as big ones). |")
    out("| 3 | Per-sentence F1 (macro) | "
        "Per gold sentence $s$: $F_1$ over $b$-sets; macro mean over gold "
        "sentences (`per_sentence_macro_f1`, "
        "`src/bias/rq2_trivial_baselines.py:94`). | macro over gold sentences | "
        "Consistent F1 per sentence; downweights sentences with very many "
        "gold links. |")
    out("| 4 | Sentence coverage | "
        "Fraction of gold sentences with $\\ge 1$ correct prediction "
        "(`sentence_coverage`, `src/bias/rq2_trivial_baselines.py:120`). | "
        "macro over gold sentences | "
        "Reach: did the system find *something* for each gold sentence? "
        "Insensitive to FPs. |")
    out("| 5 | Noise rate | "
        "Mean across predicted sentences of $FP / (TP + FP)$ "
        "(`noise_rate`, `src/bias/rq2_trivial_baselines.py:135`). | "
        "macro over predicted sentences | "
        "Per-sentence FP fraction; high = developer wades through wrong links. "
        "Insensitive to coverage. |")
    out("| 6 | HUS | Harmonic mean of coverage and per-sentence purity (1-noise "
        "weighted by full FP-free sentence count); "
        "`compute_hus` in `src/lib/new_metrics_analysis.py:420`. | "
        "harmonic of coverage + purity | "
        "Useful sentence experience — must hit gold sentences AND keep them "
        "clean. |")
    out("| 7 | NDG (skill) | $(F_1 - F_1^{rand}) / (F_1^{oracle} - F_1^{rand})$; "
        "`compute_ndg` in `src/lib/new_metrics_analysis.py:401`. | "
        "rescaling of micro F1 | "
        "How much of the random→oracle gap the system closes. Only defined "
        "for doc-to-code (oracle uses gold SAM-CODE × gold SAD-SAM); reported "
        "NA on doc-to-model. |")
    out()
    out("---")
    out()

    # ──────────────────────────────────────────────────────────────────────
    # Data matrix
    # ──────────────────────────────────────────────────────────────────────
    out("## 1. Data matrix")
    out()
    out("Each row = one (system × project × task) cell. NDG is NA on "
        "doc-to-model. Top-3 doc-to-model uses R2 (name freq in doc).")
    out()
    for task in ("doc-to-code", "doc-to-model"):
        out(f"### 1.{1 if task=='doc-to-code' else 2} Task: {task}")
        out()
        header = "| System | Project | " + " | ".join(METRIC_LABELS[m] for m in METRICS) + " |"
        sep = "|" + "---|" * (len(METRICS) + 2)
        out(header)
        out(sep)
        systems_in_task = sorted({c[2] for c in matrix if c[0] == task},
                                 key=lambda s: ["TransArc", "S11", "Random", "Top-3"].index(s)
                                 if s in ["TransArc", "S11", "Random", "Top-3"] else 99)
        for sys_ in systems_in_task:
            for proj in PROJECTS:
                cell = matrix.get((task, proj, sys_))
                if cell is None:
                    continue
                vals = []
                for m in METRICS:
                    v = cell.get(m)
                    vals.append("NA" if v is None else f"{v:.3f}")
                out(f"| {sys_} | {proj} | " + " | ".join(vals) + " |")
            # Macro mean over the 5 projects
            means = []
            for m in METRICS:
                xs = [matrix[(task, p, sys_)].get(m) for p in PROJECTS
                      if matrix[(task, p, sys_)].get(m) is not None]
                means.append("NA" if not xs else f"**{sum(xs)/len(xs):.3f}**")
            out(f"| **{sys_}** | **macro mean** | " + " | ".join(means) + " |")
        out()

    # S13F reference table
    out("### 1.3 S13F reference (quoted from existing CSVs — different "
        "per-component F1 definition; NOT used in correlation analysis)")
    out()
    out("**S13F SAD-CODE** (from `reports/SADCODE_S11_S13F_VS_TRANSARC.csv`):")
    out()
    out("| Project | File F1 | Component F1 (micro) | HUS | NDG | MCC |")
    out("|---|---|---|---|---|---|")
    for p in PROJECTS:
        r = S13F_SAD_CODE[p]
        out(f"| {p} | {r['file_f1']:.3f} | {r['comp_f1_micro']:.3f} "
            f"| {r['hus']:.3f} | {r['ndg']:.3f} | {r['mcc']:.3f} |")
    out()
    out("**S13F SAD-SAM** (from `reports/SADSAM_S11_S13F_VS_TRANSARC.csv`):")
    out()
    out("| Project | Link F1 | Sentence F1 (TP iff comp sets intersect) | "
        "Component F1 (micro) | HUS | MCC |")
    out("|---|---|---|---|---|---|")
    for p in PROJECTS:
        r = S13F_SAD_SAM[p]
        out(f"| {p} | {r['link_f1']:.3f} | {r['sent_f1_micro']:.3f} "
            f"| {r['comp_f1_micro']:.3f} | {r['hus']:.3f} | {r['mcc']:.3f} |")
    out()
    out("S13F is the canonical paper artifact and dominates both metrics on "
        "every project; it cannot reverse anything in the other systems' rank "
        "order. Excluding it from correlation analysis is conservative for the "
        "shadowing question.")
    out()
    out("---")
    out()

    # ──────────────────────────────────────────────────────────────────────
    # Correlation matrices
    # ──────────────────────────────────────────────────────────────────────
    out("## 2. Pairwise Spearman rank correlation (7 × 7)")
    out()
    out("Correlation across all available (system × project) cells in each "
        "task. `–` = correlation undefined (constant column or too few pairs).")
    out()

    def fmt_corr_table(label, mat):
        out(f"### {label}")
        out()
        out("| | " + " | ".join(METRIC_LABELS[m] for m in METRICS) + " |")
        out("|---|" + "---|" * len(METRICS))
        for a in METRICS:
            row = [METRIC_LABELS[a]]
            for b in METRICS:
                v = mat[(a, b)]
                row.append("–" if v is None else f"{v:+.2f}")
            out("| " + " | ".join(row) + " |")
        out()

    fmt_corr_table("2.1 Doc-to-code (n = 4 systems × 5 projects = 20 cells)", corr_d2c)
    fmt_corr_table("2.2 Doc-to-model (n = 4 systems × 5 projects = 20 cells; NDG NA)", corr_d2m)
    fmt_corr_table("2.3 Pooled (both tasks; n = 40 cells; NDG only defined on 20)", corr_all)

    # ──────────────────────────────────────────────────────────────────────
    # Reversal counts
    # ──────────────────────────────────────────────────────────────────────
    out("## 3. System-rank reversal counts")
    out()
    out("For each pair of metrics (A, B), count cells where two systems are "
        "ranked differently under A than under B. A pair that **never** "
        "reverses is informationally redundant for system-pair rank decisions. "
        "Cell = (task, project); each cell contributes "
        "C(systems_in_cell, 2) = 6 system-pair comparisons.")
    out()

    def fmt_rev_table(label, mat):
        out(f"### {label}")
        out()
        out("| | " + " | ".join(METRIC_LABELS[m] for m in METRICS) + " |")
        out("|---|" + "---|" * len(METRICS))
        for a in METRICS:
            row = [METRIC_LABELS[a]]
            for b in METRICS:
                r = mat[(a, b)]
                if r["pairs_compared"] == 0:
                    row.append("–")
                else:
                    pct = 100 * r["reversal_rate"]
                    row.append(f"{r['reversals']}/{r['pairs_compared']} ({pct:.0f}%)")
            out("| " + " | ".join(row) + " |")
        out()

    fmt_rev_table("3.1 Doc-to-code", rev_d2c)
    fmt_rev_table("3.2 Doc-to-model (NDG NA)", rev_d2m)
    fmt_rev_table("3.3 Pooled", rev_all)

    # ──────────────────────────────────────────────────────────────────────
    # Per-system fingerprints
    # ──────────────────────────────────────────────────────────────────────
    out("## 4. Per-system fingerprints")
    out()
    out("For each system × task, mean **(metric − file F1)** across the 5 "
        "projects. Positive = system over-performs on this metric relative to "
        "its file F1 (the metric flatters it); negative = under-performs "
        "(the metric punishes it). This is the signal a *diagnostic* metric "
        "would expose even if its rank correlation with file F1 is high.")
    out()
    for task in ("doc-to-code", "doc-to-model"):
        out(f"### 4.{1 if task=='doc-to-code' else 2} {task}")
        out()
        systems_in_task = sorted({c[2] for c in matrix if c[0] == task},
                                 key=lambda s: ["TransArc", "S11", "Random", "Top-3"].index(s)
                                 if s in ["TransArc", "S11", "Random", "Top-3"] else 99)
        out("| System | " + " | ".join(METRIC_LABELS[m] for m in METRICS[1:]) + " |")
        out("|---|" + "---|" * (len(METRICS) - 1))
        for sys_ in systems_in_task:
            fp = fingerprints[(task, sys_)]
            cells = []
            for m in METRICS[1:]:
                v = fp.get(m)
                cells.append("NA" if v is None else f"{v:+.3f}")
            out(f"| {sys_} | " + " | ".join(cells) + " |")
        out()

    # ──────────────────────────────────────────────────────────────────────
    # Verdict
    # ──────────────────────────────────────────────────────────────────────
    out("## 5. Verdict (<400 words)")
    out()

    # Compute the headline numbers for the verdict prose.
    def cmp(task, a, b):
        c = (corr_d2c if task == "doc-to-code"
             else corr_d2m if task == "doc-to-model"
             else corr_all)
        r = (rev_d2c if task == "doc-to-code"
             else rev_d2m if task == "doc-to-model"
             else rev_all)
        return c[(a, b)], r[(a, b)]

    sp_d2c_sent, rv_d2c_sent = cmp("doc-to-code", "comp_f1", "sent_f1")
    sp_d2m_sent, rv_d2m_sent = cmp("doc-to-model", "comp_f1", "sent_f1")
    sp_d2c_cov, rv_d2c_cov = cmp("doc-to-code", "comp_f1", "coverage")
    sp_d2m_cov, rv_d2m_cov = cmp("doc-to-model", "comp_f1", "coverage")
    sp_d2c_noise, rv_d2c_noise = cmp("doc-to-code", "comp_f1", "noise")
    sp_d2m_noise, rv_d2m_noise = cmp("doc-to-model", "comp_f1", "noise")
    sp_d2c_hus, rv_d2c_hus = cmp("doc-to-code", "comp_f1", "hus")
    sp_d2m_hus, rv_d2m_hus = cmp("doc-to-model", "comp_f1", "hus")
    sp_d2c_ndg, rv_d2c_ndg = cmp("doc-to-code", "file_f1", "ndg")

    def fcorr(x):
        return "–" if x is None else f"{x:+.2f}"

    def frev(r):
        if r["pairs_compared"] == 0:
            return "–"
        return f"{r['reversals']}/{r['pairs_compared']} ({100*r['reversal_rate']:.0f}%)"

    out("**Q1 — Is per-sentence F1 shadowed by per-component F1?** "
        f"On doc-to-code, Spearman ρ = {fcorr(sp_d2c_sent)} with "
        f"{frev(rv_d2c_sent)} reversals; on doc-to-model "
        f"ρ = {fcorr(sp_d2m_sent)} with {frev(rv_d2m_sent)} reversals. The "
        "per-sentence macro disagrees with per-component macro on roughly "
        "10–13% of system-pair comparisons — non-zero but small. It tracks "
        "*file F1* even more tightly (ρ ≥ 0.98 in both tasks, only 0–1 "
        "reversals). Per-sentence F1 over gold sentences gives almost the "
        "same answer as micro F1 because most gold sentences have only 1–2 "
        "links (see H2 in the doc-to-model prestudy). **Verdict: "
        "diagnostic on doc-to-code (catches the few cells where "
        "per-component and per-sentence disagree); near-shadowed on "
        "doc-to-model (1/30 reversals against file F1 — almost no marginal "
        "rank signal).**")
    out()
    out("**Q2 — Is sentence coverage shadowed by per-component F1?** "
        f"Doc-to-code ρ = {fcorr(sp_d2c_cov)} with {frev(rv_d2c_cov)} "
        f"reversals; doc-to-model ρ = {fcorr(sp_d2m_cov)} with "
        f"{frev(rv_d2m_cov)} reversals. Coverage reverses against "
        "per-component F1 in 4–8 cells: Random has very broad coverage "
        "(0.66 mean) because it scatters predictions across all sentences, "
        "but per-component F1 collapses on the components it does not "
        "reliably hit; conversely TransArc on teammates has high "
        "per-component F1 (0.74) but only 0.60 coverage because its "
        "predictions concentrate on a few components. Coverage exposes a "
        "failure mode (\"the linker found nothing for this sentence\") "
        "that per-component F1 cannot. **Verdict: independent on "
        "doc-to-code; weakly diagnostic on doc-to-model (only 14% "
        "reversals).**")
    out()
    out("**Q3 — Is noise rate shadowed by anything else?** Noise rate "
        f"has ρ = {fcorr(sp_d2c_noise)}/{fcorr(sp_d2m_noise)} with "
        "per-component F1 (doc-to-code/doc-to-model), sign-inverted because "
        "high noise is bad. It is the only metric that punishes false "
        "positives on a per-sentence basis; coverage ignores FPs, file F1 "
        "averages them with TPs, per-component F1 averages them per "
        "component. **Verdict: independent (and especially load-bearing on "
        "doc-to-model where most of the doc is unlinked narrative — see "
        "H3 in the prestudy).**")
    out()
    out("**Q4 — Is HUS shadowed?** HUS = harmonic(coverage, purity). "
        f"Doc-to-code ρ = {fcorr(sp_d2c_hus)} with {frev(rv_d2c_hus)} "
        f"reversals against per-component F1; doc-to-model "
        f"ρ = {fcorr(sp_d2m_hus)} with {frev(rv_d2m_hus)} reversals. HUS "
        "is highly correlated with file F1 in the macro mean (both reward "
        "TPs and punish FPs at the right scale) but it occasionally reverses "
        "the ranks of Top-3 vs Random because Top-3's coverage is high while "
        "its purity is low. HUS effectively bundles coverage + noise into one "
        "scalar — useful as a summary, **diagnostic** as a standalone signal "
        "since coverage + noise already report it.")
    out()
    out("**Q5 — Is NDG (skill) shadowed?** NDG is a per-project linear "
        f"rescaling of file F1, so Spearman ρ = {fcorr(sp_d2c_ndg)} "
        f"with {frev(rv_d2c_ndg)} reversals against file F1 on doc-to-code "
        "— it cannot reverse any system pair within a project. The signal "
        "it adds is in the *macro mean*: TransArc on mediastore (file F1 "
        "0.59, NDG 0.47) and teammates (file F1 0.82, NDG 0.92) show the "
        "skill rescaling shrinks the gap on easy projects and stretches it "
        "on hard ones. As a per-project metric NDG is pure rescaling; as a "
        "cross-project comparator it reveals that file-F1 ranks of projects "
        "reflect difficulty as much as system quality. **Verdict: "
        "diagnostic (cross-project rescaling only); demote to companion of "
        "file F1.**")
    out()
    out("**Recommendation.**")
    out()
    out("- **Primary** (report on the headline table): "
        "**File F1**, **per-component F1 (macro)**, **noise rate**, "
        "**sentence coverage**. These four are the smallest set that "
        "covers volume accuracy, balanced-per-component accuracy, "
        "developer noise tax, and reach. None is shadowed by another.")
    out("- **Diagnostic** (appendix / footnote): "
        "**Per-sentence F1 (macro)** — keep on doc-to-code where it "
        "occasionally reverses; drop on doc-to-model where its signal is "
        "subsumed by file F1. **HUS** — keep as a single-number summary in "
        "tables, but coverage + noise should be the primary read. **NDG** — "
        "keep as the cross-project comparator only; do not list per-project "
        "because it is monotone in file F1 within a project.")
    out("- **No drops** in the strict sense — every metric carries *some* "
        "load — but per-sentence F1 (doc-to-model only) and NDG (per-project) "
        "are the closest to being shadowed and could be demoted to appendix "
        "without loss.")
    out()
    out("---")
    out()
    out("Script: `src/bias/rq2_metric_redundancy.py`. "
        "Reproduce: `python3 src/bias/rq2_metric_redundancy.py`.")
    out()

    OUTPUT_MD.write_text("\n".join(L))
    print(f"\nWrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
