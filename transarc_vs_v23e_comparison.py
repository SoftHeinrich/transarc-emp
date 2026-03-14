#!/usr/bin/env python3
"""
TransArc vs V23e Comprehensive Comparison

Compares TransArc (traditional transitive pipeline) against V23e (LLM linker
with hybrid batch/union judge) using our full suite of metrics:

**Standard**: P/R/F1 at SAD-SAM and SAD-CODE levels
**N1**: MCC (Matthews Correlation Coefficient)
**N2**: EMR (Exact Match Ratio) — per-entity set accuracy
**N3**: MAP (Mean Average Precision) — ranking quality
**N4**: ACF1 (Amplification-Corrected F1) — de-biased for enrollment
**N5**: NDG (Normalized Difficulty Gap) — effort above random toward oracle
**N6**: HUS (Holistic Usefulness Score) — combined noise/coverage/usefulness
**Debiasing**: IDF-weighted F1, Component-Macro F1, PDR F1

V23e is a SAD-SAM linker; its SAD-CODE result is composed via gold SAM-CODE.

Outputs: TRANSARC_VS_V23E_COMPARISON.md
"""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_raw,
    load_gs_sam_code_maps, load_gs_sad_code_enrolled,
    load_result_sad_code, load_transarc_intermediate_sad_sam,
    load_text, load_model_element_names, calc_metrics,
)

from new_metrics_analysis import (
    compute_mcc, compute_emr, compute_map, compute_acf1,
    compute_random_f1, compute_oracle_f1, compute_ndg, compute_hus,
    compose_sad_code, transarc_sad_sam_as_ranked,
)

from three_system_comparison import (
    compute_idf_weighted_f1,
    compute_component_macro_f1,
    compute_pdr_f1,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/TRANSARC_VS_V23E_COMPARISON.md")

V23E_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/ablation_results")


# ─── V23e data loaders ───────────────────────────────────────────────────────

def load_v23e_sad_sam(project):
    """Load V23e SAD-SAM links as set of (modelElementID, sentence_str)."""
    path = V23E_DIR / f"v23e_{project}_links.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["component_id"], row["sentence"]))
    return links


def load_v23e_sad_sam_with_confidence(project):
    """Load V23e links with confidence for MAP computation."""
    path = V23E_DIR / f"v23e_{project}_links.csv"
    links = []
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.append((row["sentence"], row["component_id"], float(row["confidence"])))
    return links


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    lines = []
    w = lines.append

    w("# TransArc vs V23e: Comprehensive Metric Comparison")
    w("")
    w("Two-system comparison using our full metric suite at SAD-SAM and SAD-CODE levels.")
    w("")
    w("**Systems:**")
    w("- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)")
    w("- **V23e**: LLM linker with hybrid batch/union judge (SAD-SAM), projected through **gold SAM-CODE** for SAD-CODE")
    w("")
    w("V23e is a SAD-SAM linker; its SAD-CODE result is composed transitively via gold SAM-CODE.")
    w("TransArc produces SAD-CODE directly via its own SAM-CODE pipeline.")
    w("")
    w("**Metrics:**")
    w("- Standard P/R/F1, MCC (N1), EMR (N2), MAP (N3), ACF1 (N4), NDG (N5), HUS (N6)")
    w("- Debiasing: IDF-weighted F1, Component-Macro F1, PDR F1")
    w("")
    w("---")
    w("")

    # Storage for cross-project aggregation
    agg = {
        "std_sam": {"t": [], "v": []},
        "std_code": {"t": [], "v": []},
        "n1_sam": {"t": [], "v": []},
        "n1_code": {"t": [], "v": []},
        "n2_sam": {"t": [], "v": []},
        "n2_code": {"t": [], "v": []},
        "n3_sam": {"t": [], "v": []},
        "n3_code": {"t": [], "v": []},
        "n4": {"t": [], "v": []},
        "n5": {"t": [], "v": []},
        "n6_sam": {"t": [], "v": []},
        "n6_code": {"t": [], "v": []},
        "idf": {"t": [], "v": []},
        "macro": {"t": [], "v": []},
        "pdr": {"t": [], "v": []},
    }

    per_proj = {}

    for proj in PROJECTS:
        w(f"## {proj.capitalize()}")
        w("")

        # ─── Load shared data ────────────────────────────────────────
        code_model = load_code_model_files(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sad_sam_maps = load_gs_sad_sam_maps(proj)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        text = load_text(proj)
        model_names = load_model_element_names(proj)

        all_sents = set(text.keys())
        all_comps = set(model_names.keys())

        # ─── TransArc ────────────────────────────────────────────────
        transarc_sad_sam = load_transarc_intermediate_sad_sam(proj)
        transarc_sad_code = load_result_sad_code(proj)

        # ─── V23e─────────────────────────────────────────────────────
        v23e_sad_sam = load_v23e_sad_sam(proj)
        v23e_ranked = load_v23e_sad_sam_with_confidence(proj)
        v23e_sad_code = compose_sad_code(v23e_sad_sam, gs_sam_code_map)

        # ─── All code files (for MCC universe) ───────────────────────
        all_code_files = set()
        for comp, files in gs_sam_code_map.items():
            all_code_files |= files
        for _, f in transarc_sad_code:
            all_code_files.add(f)
        for _, f in v23e_sad_code:
            all_code_files.add(f)

        # ═════════════════════════════════════════════════════════════
        # Standard P/R/F1
        # ═════════════════════════════════════════════════════════════
        t_p, t_r, t_f1, t_tp, t_fp, t_fn = calc_metrics(gs_sad_sam, transarc_sad_sam)
        v_p, v_r, v_f1, v_tp, v_fp, v_fn = calc_metrics(gs_sad_sam, v23e_sad_sam)

        tc_p, tc_r, tc_f1, tc_tp, tc_fp, tc_fn = calc_metrics(gs_sad_code, transarc_sad_code)
        vc_p, vc_r, vc_f1, vc_tp, vc_fp, vc_fn = calc_metrics(gs_sad_code, v23e_sad_code)

        agg["std_sam"]["t"].append(t_f1); agg["std_sam"]["v"].append(v_f1)
        agg["std_code"]["t"].append(tc_f1); agg["std_code"]["v"].append(vc_f1)

        w("### Standard P/R/F1")
        w("")
        w("| Level | System | P | R | F1 | TP | FP | FN |")
        w("|:--|:--|:---:|:---:|:---:|---:|---:|---:|")
        w(f"| SAD-SAM | TransArc | {t_p:.3f} | {t_r:.3f} | {t_f1:.3f} | {t_tp} | {t_fp} | {t_fn} |")
        w(f"| SAD-SAM | V23e| {v_p:.3f} | {v_r:.3f} | {v_f1:.3f} | {v_tp} | {v_fp} | {v_fn} |")
        w(f"| SAD-SAM | **Δ (V23e−T)** | {v_p-t_p:+.3f} | {v_r-t_r:+.3f} | **{v_f1-t_f1:+.3f}** | {v_tp-t_tp:+d} | {v_fp-t_fp:+d} | {v_fn-t_fn:+d} |")
        w(f"| SAD-CODE | TransArc | {tc_p:.3f} | {tc_r:.3f} | {tc_f1:.3f} | {tc_tp} | {tc_fp} | {tc_fn} |")
        w(f"| SAD-CODE | V23e| {vc_p:.3f} | {vc_r:.3f} | {vc_f1:.3f} | {vc_tp} | {vc_fp} | {vc_fn} |")
        w(f"| SAD-CODE | **Δ (V23e−T)** | {vc_p-tc_p:+.3f} | {vc_r-tc_r:+.3f} | **{vc_f1-tc_f1:+.3f}** | {vc_tp-tc_tp:+d} | {vc_fp-tc_fp:+d} | {vc_fn-tc_fn:+d} |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N1: MCC
        # ═════════════════════════════════════════════════════════════
        n1_t = compute_mcc(gs_sad_sam, transarc_sad_sam, all_sents, all_comps)
        n1_v = compute_mcc(gs_sad_sam, v23e_sad_sam, all_sents, all_comps)

        n1c_t = compute_mcc(gs_sad_code, transarc_sad_code, all_sents, all_code_files)
        n1c_v = compute_mcc(gs_sad_code, v23e_sad_code, all_sents, all_code_files)

        agg["n1_sam"]["t"].append(n1_t["mcc"]); agg["n1_sam"]["v"].append(n1_v["mcc"])
        agg["n1_code"]["t"].append(n1c_t["mcc"]); agg["n1_code"]["v"].append(n1c_v["mcc"])

        w("### N1: MCC (Matthews Correlation Coefficient)")
        w("")
        w("| Level | System | MCC | Bal.Acc |")
        w("|:--|:--|:---:|:---:|")
        w(f"| SAD-SAM | TransArc | {n1_t['mcc']:.3f} | {n1_t['balanced_accuracy']:.3f} |")
        w(f"| SAD-SAM | V23e| {n1_v['mcc']:.3f} | {n1_v['balanced_accuracy']:.3f} |")
        w(f"| SAD-SAM | **Δ** | **{n1_v['mcc']-n1_t['mcc']:+.3f}** | {n1_v['balanced_accuracy']-n1_t['balanced_accuracy']:+.3f} |")
        w(f"| SAD-CODE | TransArc | {n1c_t['mcc']:.3f} | {n1c_t['balanced_accuracy']:.3f} |")
        w(f"| SAD-CODE | V23e| {n1c_v['mcc']:.3f} | {n1c_v['balanced_accuracy']:.3f} |")
        w(f"| SAD-CODE | **Δ** | **{n1c_v['mcc']-n1c_t['mcc']:+.3f}** | {n1c_v['balanced_accuracy']-n1c_t['balanced_accuracy']:+.3f} |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N2: EMR (Exact Match Ratio)
        # ═════════════════════════════════════════════════════════════
        n2_t = compute_emr(gs_sad_sam, transarc_sad_sam)
        n2_v = compute_emr(gs_sad_sam, v23e_sad_sam)

        gs_code_flip = {(c, s) for s, c in gs_sad_code}
        tr_code_flip = {(c, s) for s, c in transarc_sad_code}
        v23e_code_flip = {(c, s) for s, c in v23e_sad_code}
        n2c_t = compute_emr(gs_code_flip, tr_code_flip)
        n2c_v = compute_emr(gs_code_flip, v23e_code_flip)

        agg["n2_sam"]["t"].append(n2_t["emr"]); agg["n2_sam"]["v"].append(n2_v["emr"])
        agg["n2_code"]["t"].append(n2c_t["emr"]); agg["n2_code"]["v"].append(n2c_v["emr"])

        w("### N2: EMR (Exact Match Ratio)")
        w("")
        w("| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |")
        w("|:--|:--|:---:|:---:|:---:|:---:|:---:|")
        for level, label, data in [
            ("SAD-SAM", "TransArc", n2_t), ("SAD-SAM", "V23e", n2_v),
            ("SAD-CODE", "TransArc", n2c_t), ("SAD-CODE", "V23e", n2c_v),
        ]:
            w(f"| {level} | {label} | {data['emr']:.3f} | {data['jaccard_mean']:.3f} | "
              f"{data['superset_rate']:.3f} | {data['subset_rate']:.3f} | {data['zero_pred_rate']:.3f} |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N3: MAP (Mean Average Precision)
        # ═════════════════════════════════════════════════════════════
        transarc_ranked = transarc_sad_sam_as_ranked(transarc_sad_sam)
        n3_t = compute_map(gs_sad_sam, transarc_ranked)
        n3_v = compute_map(gs_sad_sam, v23e_ranked)

        # SAD-CODE level MAP
        gs_code_flip_map = {(c, s) for s, c in gs_sad_code}
        transarc_code_ranked = [(s, c, 0.5) for s, c in transarc_sad_code]
        v23e_code_ranked = []
        for sent, comp_id, conf in v23e_ranked:
            for code_path in gs_sam_code_map.get(comp_id, set()):
                v23e_code_ranked.append((sent, code_path, conf))
        n3c_t = compute_map(gs_code_flip_map, transarc_code_ranked)
        n3c_v = compute_map(gs_code_flip_map, v23e_code_ranked)

        agg["n3_sam"]["t"].append(n3_t["map"]); agg["n3_sam"]["v"].append(n3_v["map"])
        agg["n3_code"]["t"].append(n3c_t["map"]); agg["n3_code"]["v"].append(n3c_v["map"])

        w("### N3: MAP (Mean Average Precision)")
        w("")
        w("| Level | System | MAP |")
        w("|:--|:--|:---:|")
        w(f"| SAD-SAM | TransArc | {n3_t['map']:.3f} |")
        w(f"| SAD-SAM | V23e| {n3_v['map']:.3f} |")
        w(f"| SAD-SAM | **Δ** | **{n3_v['map']-n3_t['map']:+.3f}** |")
        w(f"| SAD-CODE | TransArc | {n3c_t['map']:.3f} |")
        w(f"| SAD-CODE | V23e| {n3c_v['map']:.3f} |")
        w(f"| SAD-CODE | **Δ** | **{n3c_v['map']-n3c_t['map']:+.3f}** |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N4: ACF1 (Amplification-Corrected F1)
        # ═════════════════════════════════════════════════════════════
        n4_t = compute_acf1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        n4_v = compute_acf1(gs_sad_code, v23e_sad_code, gs_sam_code_map)

        agg["n4"]["t"].append(n4_t["acf1"]); agg["n4"]["v"].append(n4_v["acf1"])

        w("### N4: ACF1 (Amplification-Corrected F1)")
        w("")
        w("| System | Std F1 | ACF1 | Shift |")
        w("|:--|:---:|:---:|:---:|")
        w(f"| TransArc | {tc_f1:.3f} | {n4_t['acf1']:.3f} | {n4_t['acf1']-tc_f1:+.3f} |")
        w(f"| V23e| {vc_f1:.3f} | {n4_v['acf1']:.3f} | {n4_v['acf1']-vc_f1:+.3f} |")
        w(f"| **Δ (V23e−T)** | **{vc_f1-tc_f1:+.3f}** | **{n4_v['acf1']-n4_t['acf1']:+.3f}** | |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N5: NDG (Normalized Difficulty Gap)
        # ═════════════════════════════════════════════════════════════
        random_f1 = compute_random_f1(gs_sad_code, len(all_sents), len(all_comps), gs_sam_code_map)
        oracle_f1, _ = compute_oracle_f1(gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)

        ndg_t = compute_ndg(tc_f1, random_f1, oracle_f1)
        ndg_v = compute_ndg(vc_f1, random_f1, oracle_f1)

        agg["n5"]["t"].append(ndg_t); agg["n5"]["v"].append(ndg_v)

        w("### N5: NDG (Normalized Difficulty Gap)")
        w("")
        w(f"Random F1: {random_f1:.3f} | Oracle F1: {oracle_f1:.3f}")
        w("")
        w("| System | F1 | NDG |")
        w("|:--|:---:|:---:|")
        w(f"| TransArc | {tc_f1:.3f} | {ndg_t:.3f} |")
        w(f"| V23e| {vc_f1:.3f} | {ndg_v:.3f} |")
        w(f"| **Δ** | **{vc_f1-tc_f1:+.3f}** | **{ndg_v-ndg_t:+.3f}** |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # N6: HUS (Holistic Usefulness Score)
        # ═════════════════════════════════════════════════════════════
        n6_t = compute_hus(gs_sad_sam, transarc_sad_sam)
        n6_v = compute_hus(gs_sad_sam, v23e_sad_sam)

        n6c_t = compute_hus(gs_sad_code, transarc_sad_code)
        n6c_v = compute_hus(gs_sad_code, v23e_sad_code)

        agg["n6_sam"]["t"].append(n6_t["hus"]); agg["n6_sam"]["v"].append(n6_v["hus"])
        agg["n6_code"]["t"].append(n6c_t["hus"]); agg["n6_code"]["v"].append(n6c_v["hus"])

        w("### N6: HUS (Holistic Usefulness Score)")
        w("")
        w("| Level | System | HUS | Coverage | Purity |")
        w("|:--|:--|:---:|:---:|:---:|")
        w(f"| SAD-SAM | TransArc | {n6_t['hus']:.3f} | {n6_t['coverage']:.3f} | {n6_t['purity']:.3f} |")
        w(f"| SAD-SAM | V23e| {n6_v['hus']:.3f} | {n6_v['coverage']:.3f} | {n6_v['purity']:.3f} |")
        w(f"| SAD-CODE | TransArc | {n6c_t['hus']:.3f} | {n6c_t['coverage']:.3f} | {n6c_t['purity']:.3f} |")
        w(f"| SAD-CODE | V23e| {n6c_v['hus']:.3f} | {n6c_v['coverage']:.3f} | {n6c_v['purity']:.3f} |")
        w("")

        # ═════════════════════════════════════════════════════════════
        # Enrollment Debiasing Metrics
        # ═════════════════════════════════════════════════════════════
        idf_t = compute_idf_weighted_f1(gs_sad_code, transarc_sad_code, code_model)
        idf_v = compute_idf_weighted_f1(gs_sad_code, v23e_sad_code, code_model)
        macro_t = compute_component_macro_f1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        macro_v = compute_component_macro_f1(gs_sad_code, v23e_sad_code, gs_sam_code_map)
        pdr_t = compute_pdr_f1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        pdr_v = compute_pdr_f1(gs_sad_code, v23e_sad_code, gs_sam_code_map)

        agg["idf"]["t"].append(idf_t); agg["idf"]["v"].append(idf_v)
        agg["macro"]["t"].append(macro_t); agg["macro"]["v"].append(macro_v)
        agg["pdr"]["t"].append(pdr_t); agg["pdr"]["v"].append(pdr_v)

        w("### Enrollment Debiasing")
        w("")
        w("| Metric | TransArc | V23e| Δ |")
        w("|:--|:---:|:---:|:---:|")
        w(f"| Standard F1 | {tc_f1:.3f} | {vc_f1:.3f} | {vc_f1-tc_f1:+.3f} |")
        w(f"| IDF-Weighted F1 | {idf_t:.3f} | {idf_v:.3f} | {idf_v-idf_t:+.3f} |")
        w(f"| Component-Macro F1 | {macro_t:.3f} | {macro_v:.3f} | {macro_v-macro_t:+.3f} |")
        w(f"| PDR F1 | {pdr_t:.3f} | {pdr_v:.3f} | {pdr_v-pdr_t:+.3f} |")
        w("")

        per_proj[proj] = {
            "t_sam": (t_p, t_r, t_f1), "v_sam": (v_p, v_r, v_f1),
            "t_code": (tc_p, tc_r, tc_f1), "v_code": (vc_p, vc_r, vc_f1),
        }

        w("---")
        w("")

    # ═════════════════════════════════════════════════════════════════════════
    # Cross-Project Summary Tables
    # ═════════════════════════════════════════════════════════════════════════
    w("## Cross-Project Summary")
    w("")

    # ─── SAD-SAM F1 ───────────────────────────────────────────────
    w("### SAD-SAM F1")
    w("")
    w("| Project | TransArc | V23e| Δ | Winner |")
    w("|:--|:---:|:---:|:---:|:--|")
    for i, proj in enumerate(PROJECTS):
        tf = agg["std_sam"]["t"][i]
        vf = agg["std_sam"]["v"][i]
        delta = vf - tf
        winner = "V23e" if delta > 0.005 else ("TransArc" if delta < -0.005 else "Tie")
        w(f"| {proj} | {tf:.3f} | {vf:.3f} | {delta:+.3f} | {winner} |")
    avg_t = sum(agg["std_sam"]["t"]) / len(PROJECTS)
    avg_v = sum(agg["std_sam"]["v"]) / len(PROJECTS)
    w(f"| **Average** | **{avg_t:.3f}** | **{avg_v:.3f}** | **{avg_v-avg_t:+.3f}** | {'**V23e**' if avg_v > avg_t else '**TransArc**'} |")
    w("")

    # ─── SAD-CODE F1 ──────────────────────────────────────────────
    w("### SAD-CODE F1")
    w("")
    w("| Project | TransArc | V23e| Δ | Winner |")
    w("|:--|:---:|:---:|:---:|:--|")
    for i, proj in enumerate(PROJECTS):
        tf = agg["std_code"]["t"][i]
        vf = agg["std_code"]["v"][i]
        delta = vf - tf
        winner = "V23e" if delta > 0.005 else ("TransArc" if delta < -0.005 else "Tie")
        w(f"| {proj} | {tf:.3f} | {vf:.3f} | {delta:+.3f} | {winner} |")
    avg_t = sum(agg["std_code"]["t"]) / len(PROJECTS)
    avg_v = sum(agg["std_code"]["v"]) / len(PROJECTS)
    w(f"| **Average** | **{avg_t:.3f}** | **{avg_v:.3f}** | **{avg_v-avg_t:+.3f}** | {'**V23e**' if avg_v > avg_t else '**TransArc**'} |")
    w("")

    # ─── All Metrics Cross-Project ────────────────────────────────
    w("### All Metrics: Average Across Projects")
    w("")
    w("| Metric | Level | TransArc | V23e| Δ | Winner |")
    w("|:--|:--|:---:|:---:|:---:|:--|")

    metric_rows = [
        ("F1", "SAD-SAM", "std_sam"),
        ("F1", "SAD-CODE", "std_code"),
        ("MCC", "SAD-SAM", "n1_sam"),
        ("MCC", "SAD-CODE", "n1_code"),
        ("EMR", "SAD-SAM", "n2_sam"),
        ("EMR", "SAD-CODE", "n2_code"),
        ("MAP", "SAD-SAM", "n3_sam"),
        ("MAP", "SAD-CODE", "n3_code"),
        ("ACF1", "SAD-CODE", "n4"),
        ("NDG", "SAD-CODE", "n5"),
        ("HUS", "SAD-SAM", "n6_sam"),
        ("HUS", "SAD-CODE", "n6_code"),
        ("IDF F1", "SAD-CODE", "idf"),
        ("Macro F1", "SAD-CODE", "macro"),
        ("PDR F1", "SAD-CODE", "pdr"),
    ]

    wins = {"t": 0, "v": 0, "tie": 0}
    for label, level, key in metric_rows:
        avg_t = sum(agg[key]["t"]) / len(PROJECTS)
        avg_v = sum(agg[key]["v"]) / len(PROJECTS)
        delta = avg_v - avg_t
        if delta > 0.005:
            winner = "V23e"
            wins["v"] += 1
        elif delta < -0.005:
            winner = "TransArc"
            wins["t"] += 1
        else:
            winner = "Tie"
            wins["tie"] += 1
        w(f"| {label} | {level} | {avg_t:.3f} | {avg_v:.3f} | {delta:+.3f} | {winner} |")
    w("")

    w(f"**Score: V23ewins {wins['v']}, TransArc wins {wins['t']}, Ties {wins['tie']}** "
      f"(across {len(metric_rows)} metrics)")
    w("")

    # ─── Per-project wins breakdown ───────────────────────────────
    w("### Per-Project Wins (SAD-CODE metrics only)")
    w("")
    w("| Project | TransArc Wins | V23eWins | Ties |")
    w("|:--|:---:|:---:|:---:|")

    code_keys = ["std_code", "n1_code", "n2_code", "n3_code", "n4", "n5", "n6_code", "idf", "macro", "pdr"]
    total_tw = 0; total_vw = 0; total_tie = 0
    for i, proj in enumerate(PROJECTS):
        tw = vw = tie = 0
        for key in code_keys:
            tv = agg[key]["t"][i]
            vv = agg[key]["v"][i]
            d = vv - tv
            if d > 0.005:
                vw += 1
            elif d < -0.005:
                tw += 1
            else:
                tie += 1
        w(f"| {proj} | {tw} | {vw} | {tie} |")
        total_tw += tw; total_vw += vw; total_tie += tie
    w(f"| **Total** | **{total_tw}** | **{total_vw}** | **{total_tie}** |")
    w("")

    # ─── Key Findings ─────────────────────────────────────────────
    w("---")
    w("")
    w("## Key Findings")
    w("")

    # Compute some key stats
    sam_avg_t = sum(agg["std_sam"]["t"]) / len(PROJECTS)
    sam_avg_v = sum(agg["std_sam"]["v"]) / len(PROJECTS)
    code_avg_t = sum(agg["std_code"]["t"]) / len(PROJECTS)
    code_avg_v = sum(agg["std_code"]["v"]) / len(PROJECTS)
    macro_avg_t = sum(agg["macro"]["t"]) / len(PROJECTS)
    macro_avg_v = sum(agg["macro"]["v"]) / len(PROJECTS)
    mcc_sam_t = sum(agg["n1_sam"]["t"]) / len(PROJECTS)
    mcc_sam_v = sum(agg["n1_sam"]["v"]) / len(PROJECTS)

    w(f"1. **SAD-SAM**: V23eavg F1 = {sam_avg_v:.3f} vs TransArc {sam_avg_t:.3f} "
      f"(Δ={sam_avg_v-sam_avg_t:+.3f})")
    w(f"2. **SAD-CODE** (standard): V23eavg F1 = {code_avg_v:.3f} vs TransArc {code_avg_t:.3f} "
      f"(Δ={code_avg_v-code_avg_t:+.3f})")
    w(f"3. **SAD-CODE** (debiased macro): V23e= {macro_avg_v:.3f} vs TransArc {macro_avg_t:.3f} "
      f"(Δ={macro_avg_v-macro_avg_t:+.3f})")
    w(f"4. **MCC SAD-SAM**: V23e= {mcc_sam_v:.3f} vs TransArc {mcc_sam_t:.3f} "
      f"(Δ={mcc_sam_v-mcc_sam_t:+.3f})")
    w("")

    # Per-project winner tally for SAD-SAM
    sam_wins = {"t": 0, "v": 0}
    for i in range(len(PROJECTS)):
        if agg["std_sam"]["v"][i] > agg["std_sam"]["t"][i] + 0.005:
            sam_wins["v"] += 1
        elif agg["std_sam"]["t"][i] > agg["std_sam"]["v"][i] + 0.005:
            sam_wins["t"] += 1

    code_wins = {"t": 0, "v": 0}
    for i in range(len(PROJECTS)):
        if agg["std_code"]["v"][i] > agg["std_code"]["t"][i] + 0.005:
            code_wins["v"] += 1
        elif agg["std_code"]["t"][i] > agg["std_code"]["v"][i] + 0.005:
            code_wins["t"] += 1

    w(f"**SAD-SAM project wins**: V23e{sam_wins['v']}/{len(PROJECTS)}, "
      f"TransArc {sam_wins['t']}/{len(PROJECTS)}")
    w(f"**SAD-CODE project wins**: V23e{code_wins['v']}/{len(PROJECTS)}, "
      f"TransArc {code_wins['t']}/{len(PROJECTS)}")
    w("")

    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 transarc_vs_v23e_comparison.py")
    w("```")
    w("")

    # Write
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Written to {OUTPUT_MD}")

    # Quick stdout summary
    print(f"\n{'='*70}")
    print("QUICK SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'Metric':<25} {'Level':<10} {'TransArc':>10} {'V23e':>10} {'Δ':>10}")
    print("-" * 65)
    for label, level, key in metric_rows:
        at = sum(agg[key]["t"]) / len(PROJECTS)
        av = sum(agg[key]["v"]) / len(PROJECTS)
        print(f"{label:<25} {level:<10} {at:>10.3f} {av:>10.3f} {av-at:>+10.3f}")
    print(f"\nV23e wins: {wins['v']} | TransArc wins: {wins['t']} | Ties: {wins['tie']}")


if __name__ == "__main__":
    main()
