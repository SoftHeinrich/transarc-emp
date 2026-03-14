#!/usr/bin/env python3
"""
Four-System Comparison: TransArc vs V45 vs LLM Adaptive vs V87
on all 6 new metrics (N1-N6) at both SAD-SAM and SAD-CODE levels,
plus enrollment debiasing metrics.

V87 has only aggregate P/R/F1 (no per-link data), so metrics requiring
per-link data (N2, N3, N4, N6, debiasing) are marked N/A for V87.
V87 SAD-SAM metrics are holdout-only (10% few-shot) — not directly
comparable to full-gold evaluations of the other 3 systems.

Outputs: FOUR_SYSTEM_COMPARISON.md
"""

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
    load_v45_sad_sam, load_v45_sad_sam_with_confidence,
    compose_sad_code, transarc_sad_sam_as_ranked,
)

from llm_agentic_eval import (
    load_json, majority_vote, intersection_vote,
    build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
    SINGLE_DIR, MULTI_DIR, VARIANTS,
)

# Reuse LLM loading from three_system_comparison
from three_system_comparison import (
    ADAPTIVE_STRATEGIES,
    load_llm_adaptive_classifications,
    llm_classifications_to_sad_sam,
    compute_idf_weighted_f1,
    compute_component_macro_f1,
    compute_pdr_f1,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/FOUR_SYSTEM_COMPARISON.md")

V87_JSON = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-agent/results/evaluation_results/v87_pilot_20260207_213531.json")


# ─── V87 data loading ───────────────────────────────────────────────────────

def load_v87_best_per_project():
    """Load V87 pilot results, pick best strategy per project by SAD-Code F1.

    Returns dict: project -> {strategy, SAD-SAM: {P,R,F1}, SAD-Code: {P,R,F1}, n_links, n_fp}
    """
    with open(V87_JSON) as f:
        rows = json.load(f)

    best = {}
    for entry in rows:
        ds = entry["dataset"]
        f1 = entry["SAD-Code"]["F1"]
        if ds not in best or f1 > best[ds]["SAD-Code"]["F1"]:
            best[ds] = entry
    return best


def reconstruct_tp_fp_fn(p, r, gold_size):
    """Reconstruct TP, FP, FN from precision, recall, and gold set size."""
    tp = round(r * gold_size)
    fp = round(tp / p - tp) if p > 0 else 0
    fn = gold_size - tp
    return tp, fp, fn


def compute_mcc_from_counts(tp, fp, fn, universe_size):
    """Compute MCC from TP/FP/FN/universe."""
    tn = universe_size - tp - fp - fn
    numer = tp * tn - fp * fn
    denom_sq = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    denom = math.sqrt(denom_sq) if denom_sq > 0 else 1
    return numer / denom, tn


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    lines = []
    w = lines.append

    v87_data = load_v87_best_per_project()

    w("# Four-System Comparison: TransArc vs V45 vs LLM vs V87")
    w("")
    w("Unified evaluation of 4 systems across 6 new metrics (N1-N6)")
    w("at both SAD-SAM and SAD-CODE levels, plus enrollment debiasing metrics.")
    w("")
    w("**Systems:**")
    w("- **TransArc**: Traditional transitive pipeline (SAD-SAM x SAM-CODE)")
    w("- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through gold SAM-CODE")
    w("- **LLM Adaptive**: Zero-training LLM classifier (best strategy per project),")
    w("  projected through gold SAM-CODE")
    w("- **V87**: Few-shot meta-learning linker (10% gold SAD-SAM as training),")
    w("  projected through TransArc SAM-CODE (not gold)")
    w("")
    w("**Important caveats for V87:**")
    w("1. V87 uses **10% of gold SAD-SAM links as few-shot training** — not zero-shot")
    w("2. V87 SAD-SAM metrics are **holdout-only** (90% test split) — not full-gold")
    w("3. V87 SAD-CODE projection uses **TransArc SAM-CODE** (may have errors),")
    w("   while V45 and LLM use **gold SAM-CODE** (oracle)")
    w("4. V87 only has **aggregate P/R/F1** — N2, N3, N4, N6, debiasing are N/A")
    w("")
    w("| Project | LLM Strategy | V87 Strategy |")
    w("|:--|:--|:--|")
    for proj in PROJECTS:
        v87s = v87_data[proj]["strategy"]
        w(f"| {proj} | {ADAPTIVE_STRATEGIES[proj]} | {v87s} |")
    w("")
    w("---")
    w("")

    # Storage for aggregates
    all_std = {}
    all_n1 = {}; all_n1c = {}
    all_n2 = {}; all_n2c = {}
    all_n3 = {}; all_n3c = {}
    all_n4 = {}
    all_n5 = {}
    all_n6s = {}; all_n6c = {}
    all_debias = {}

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

        # ─── TransArc ───────────────────────────────────────────────
        transarc_sad_sam = load_transarc_intermediate_sad_sam(proj)
        transarc_sad_code = load_result_sad_code(proj)

        # ─── V45 ────────────────────────────────────────────────────
        v45_sad_sam = load_v45_sad_sam(proj)
        v45_ranked = load_v45_sad_sam_with_confidence(proj)
        v45_sad_code = compose_sad_code(v45_sad_sam, gs_sam_code_map)

        # ─── LLM Adaptive ──────────────────────────────────────────
        llm_cls = load_llm_adaptive_classifications(proj)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)
        llm_sad_sam = llm_classifications_to_sad_sam(llm_cls, name_to_ids)
        llm_sad_code, _ = classifications_to_result_set(llm_cls, name_to_ids, model_to_files)

        # ─── V87 (aggregate only) ──────────────────────────────────
        v87 = v87_data[proj]
        v87_p_c = v87["SAD-Code"]["P"]
        v87_r_c = v87["SAD-Code"]["R"]
        v87_f1_c = v87["SAD-Code"]["F1"]
        v87_p_s = v87["SAD-SAM"]["P"]
        v87_r_s = v87["SAD-SAM"]["R"]
        v87_f1_s = v87["SAD-SAM"]["F1"]

        # Reconstruct SAD-CODE TP/FP/FN
        v87_tp_c, v87_fp_c, v87_fn_c = reconstruct_tp_fp_fn(v87_p_c, v87_r_c, len(gs_sad_code))

        # ─── Standard F1 ────────────────────────────────────────────
        t_p, t_r, t_f1, t_tp, t_fp, t_fn = calc_metrics(gs_sad_sam, transarc_sad_sam)
        v_p, v_r, v_f1, v_tp, v_fp, v_fn = calc_metrics(gs_sad_sam, v45_sad_sam)
        l_p, l_r, l_f1, l_tp, l_fp, l_fn = calc_metrics(gs_sad_sam, llm_sad_sam)

        tc_p, tc_r, tc_f1, tc_tp, tc_fp, tc_fn = calc_metrics(gs_sad_code, transarc_sad_code)
        vc_p, vc_r, vc_f1, vc_tp, vc_fp, vc_fn = calc_metrics(gs_sad_code, v45_sad_code)
        lc_p, lc_r, lc_f1, lc_tp, lc_fp, lc_fn = calc_metrics(gs_sad_code, llm_sad_code)

        all_std[proj] = {
            "t_sam": (t_p, t_r, t_f1), "v_sam": (v_p, v_r, v_f1), "l_sam": (l_p, l_r, l_f1),
            "t_code": (tc_p, tc_r, tc_f1), "v_code": (vc_p, vc_r, vc_f1), "l_code": (lc_p, lc_r, lc_f1),
            "v87_sam": (v87_p_s, v87_r_s, v87_f1_s),
            "v87_code": (v87_p_c, v87_r_c, v87_f1_c),
        }

        w("### Standard P/R/F1")
        w("")
        w("| Level | System | P | R | F1 | TP | FP | FN |")
        w("|:--|:--|:---:|:---:|:---:|---:|---:|---:|")
        w(f"| SAD-SAM | TransArc | {t_p:.3f} | {t_r:.3f} | {t_f1:.3f} | {t_tp} | {t_fp} | {t_fn} |")
        w(f"| SAD-SAM | V45 | {v_p:.3f} | {v_r:.3f} | {v_f1:.3f} | {v_tp} | {v_fp} | {v_fn} |")
        w(f"| SAD-SAM | LLM | {l_p:.3f} | {l_r:.3f} | {l_f1:.3f} | {l_tp} | {l_fp} | {l_fn} |")
        w(f"| SAD-SAM | V87 * | {v87_p_s:.3f} | {v87_r_s:.3f} | {v87_f1_s:.3f} | — | — | — |")
        w(f"| SAD-CODE | TransArc | {tc_p:.3f} | {tc_r:.3f} | {tc_f1:.3f} | {tc_tp} | {tc_fp} | {tc_fn} |")
        w(f"| SAD-CODE | V45 | {vc_p:.3f} | {vc_r:.3f} | {vc_f1:.3f} | {vc_tp} | {vc_fp} | {vc_fn} |")
        w(f"| SAD-CODE | LLM | {lc_p:.3f} | {lc_r:.3f} | {lc_f1:.3f} | {lc_tp} | {lc_fp} | {lc_fn} |")
        w(f"| SAD-CODE | V87 | {v87_p_c:.3f} | {v87_r_c:.3f} | {v87_f1_c:.3f} | {v87_tp_c} | {v87_fp_c} | {v87_fn_c} |")
        w("")
        w("\\* V87 SAD-SAM: holdout-only (10% train split), not full-gold")
        w("")

        # ─── N1: MCC ────────────────────────────────────────────────
        n1_t = compute_mcc(gs_sad_sam, transarc_sad_sam, all_sents, all_comps)
        n1_v = compute_mcc(gs_sad_sam, v45_sad_sam, all_sents, all_comps)
        n1_l = compute_mcc(gs_sad_sam, llm_sad_sam, all_sents, all_comps)
        all_n1[proj] = {"t": n1_t, "v": n1_v, "l": n1_l}

        # SAD-CODE level
        all_code_files = set()
        for comp, files in gs_sam_code_map.items():
            all_code_files |= files
        for _, f in transarc_sad_code:
            all_code_files.add(f)
        for _, f in v45_sad_code:
            all_code_files.add(f)
        for _, f in llm_sad_code:
            all_code_files.add(f)

        code_universe = len(all_sents) * len(all_code_files)

        n1c_t = compute_mcc(gs_sad_code, transarc_sad_code, all_sents, all_code_files)
        n1c_v = compute_mcc(gs_sad_code, v45_sad_code, all_sents, all_code_files)
        n1c_l = compute_mcc(gs_sad_code, llm_sad_code, all_sents, all_code_files)

        # V87 MCC from reconstructed counts
        v87_mcc_c, v87_tn_c = compute_mcc_from_counts(v87_tp_c, v87_fp_c, v87_fn_c, code_universe)
        all_n1c[proj] = {"t": n1c_t, "v": n1c_v, "l": n1c_l, "v87_mcc": v87_mcc_c}

        w("### N1: MCC")
        w("")
        w("| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |")
        w("|:--|:--|:---:|:---:|---:|---:|---:|---:|")
        for label, data in [("TransArc", n1_t), ("V45", n1_v), ("LLM", n1_l)]:
            w(f"| SAD-SAM | {label} | **{data['mcc']:.3f}** | {data['balanced_accuracy']:.3f} | {data['tp']} | {data['fp']} | {data['fn']} | {data['tn']} |")
        w(f"| SAD-SAM | V87 | N/A | N/A | — | — | — | — |")
        for label, data in [("TransArc", n1c_t), ("V45", n1c_v), ("LLM", n1c_l)]:
            w(f"| SAD-CODE | {label} | **{data['mcc']:.3f}** | {data['balanced_accuracy']:.3f} | {data['tp']} | {data['fp']} | {data['fn']} | {data['tn']} |")
        w(f"| SAD-CODE | V87 | **{v87_mcc_c:.3f}** | — | {v87_tp_c} | {v87_fp_c} | {v87_fn_c} | {v87_tn_c} |")
        w("")

        # ─── N2: EMR ────────────────────────────────────────────────
        n2_t = compute_emr(gs_sad_sam, transarc_sad_sam)
        n2_v = compute_emr(gs_sad_sam, v45_sad_sam)
        n2_l = compute_emr(gs_sad_sam, llm_sad_sam)
        all_n2[proj] = {"t": n2_t, "v": n2_v, "l": n2_l}

        gs_code_flip = {(c, s) for s, c in gs_sad_code}
        tr_code_flip = {(c, s) for s, c in transarc_sad_code}
        v45_code_flip = {(c, s) for s, c in v45_sad_code}
        llm_code_flip = {(c, s) for s, c in llm_sad_code}
        n2c_t = compute_emr(gs_code_flip, tr_code_flip)
        n2c_v = compute_emr(gs_code_flip, v45_code_flip)
        n2c_l = compute_emr(gs_code_flip, llm_code_flip)
        all_n2c[proj] = {"t": n2c_t, "v": n2c_v, "l": n2c_l}

        w("### N2: EMR")
        w("")
        w("| Level | System | EMR | Jaccard | Superset | Subset | Zero-Pred |")
        w("|:--|:--|:---:|:---:|:---:|:---:|:---:|")
        for level, label, data in [
            ("SAD-SAM", "TransArc", n2_t), ("SAD-SAM", "V45", n2_v), ("SAD-SAM", "LLM", n2_l),
            ("SAD-CODE", "TransArc", n2c_t), ("SAD-CODE", "V45", n2c_v), ("SAD-CODE", "LLM", n2c_l),
        ]:
            w(f"| {level} | {label} | **{data['emr']:.3f}** | {data['jaccard_mean']:.3f} | {data['superset_rate']:.3f} | {data['subset_rate']:.3f} | {data['zero_pred_rate']:.3f} |")
        w(f"| SAD-SAM | V87 | N/A | N/A | N/A | N/A | N/A |")
        w(f"| SAD-CODE | V87 | N/A | N/A | N/A | N/A | N/A |")
        w("")

        # ─── N3: MAP ────────────────────────────────────────────────
        transarc_ranked = transarc_sad_sam_as_ranked(transarc_sad_sam)
        llm_ranked_sam = [(sent, comp, 0.5) for comp, sent in llm_sad_sam]
        n3_t = compute_map(gs_sad_sam, transarc_ranked)
        n3_v = compute_map(gs_sad_sam, v45_ranked)
        n3_l = compute_map(gs_sad_sam, llm_ranked_sam)
        all_n3[proj] = {"t": n3_t, "v": n3_v, "l": n3_l}

        gs_code_flip_map = {(c, s) for s, c in gs_sad_code}
        transarc_code_ranked = [(s, c, 0.5) for s, c in transarc_sad_code]
        llm_code_ranked = [(s, c, 0.5) for s, c in llm_sad_code]
        v45_code_ranked = []
        for sent, comp_id, conf in v45_ranked:
            for code_path in gs_sam_code_map.get(comp_id, set()):
                v45_code_ranked.append((sent, code_path, conf))
        n3c_t = compute_map(gs_code_flip_map, transarc_code_ranked)
        n3c_v = compute_map(gs_code_flip_map, v45_code_ranked)
        n3c_l = compute_map(gs_code_flip_map, llm_code_ranked)
        all_n3c[proj] = {"t": n3c_t, "v": n3c_v, "l": n3c_l}

        w("### N3: MAP")
        w("")
        w("| Level | System | MAP |")
        w("|:--|:--|:---:|")
        for level, label, data in [
            ("SAD-SAM", "TransArc", n3_t), ("SAD-SAM", "V45", n3_v), ("SAD-SAM", "LLM", n3_l),
            ("SAD-CODE", "TransArc", n3c_t), ("SAD-CODE", "V45", n3c_v), ("SAD-CODE", "LLM", n3c_l),
        ]:
            w(f"| {level} | {label} | **{data['map']:.3f}** |")
        w(f"| both | V87 | N/A |")
        w("")

        # ─── N4: ACF1 ───────────────────────────────────────────────
        n4_t = compute_acf1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        n4_v = compute_acf1(gs_sad_code, v45_sad_code, gs_sam_code_map)
        n4_l = compute_acf1(gs_sad_code, llm_sad_code, gs_sam_code_map)
        all_n4[proj] = {"t": n4_t, "v": n4_v, "l": n4_l}

        w("### N4: ACF1")
        w("")
        w("| System | Std F1 | ACF1 | Shift |")
        w("|:--|:---:|:---:|:---:|")
        for label, std_f1, data in [
            ("TransArc", tc_f1, n4_t), ("V45", vc_f1, n4_v), ("LLM", lc_f1, n4_l),
        ]:
            w(f"| {label} | {std_f1:.3f} | **{data['acf1']:.3f}** | {data['acf1']-std_f1:+.3f} |")
        w(f"| V87 | {v87_f1_c:.3f} | N/A | N/A |")
        w("")

        # ─── N5: NDG ────────────────────────────────────────────────
        n_sents = len(all_sents)
        random_f1 = compute_random_f1(gs_sad_code, n_sents, len(all_comps), gs_sam_code_map)
        oracle_f1, oracle_links = compute_oracle_f1(gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)

        ndg_t = compute_ndg(tc_f1, random_f1, oracle_f1)
        ndg_v = compute_ndg(vc_f1, random_f1, oracle_f1)
        ndg_l = compute_ndg(lc_f1, random_f1, oracle_f1)
        ndg_87 = compute_ndg(v87_f1_c, random_f1, oracle_f1)
        all_n5[proj] = {"t": ndg_t, "v": ndg_v, "l": ndg_l, "v87": ndg_87,
                        "random_f1": random_f1, "oracle_f1": oracle_f1}

        w("### N5: NDG")
        w("")
        w(f"Random F1: {random_f1:.3f} | Oracle F1: {oracle_f1:.3f}")
        w("")
        w("| System | F1 | NDG |")
        w("|:--|:---:|:---:|")
        w(f"| TransArc | {tc_f1:.3f} | **{ndg_t:.3f}** |")
        w(f"| V45 | {vc_f1:.3f} | **{ndg_v:.3f}** |")
        w(f"| LLM | {lc_f1:.3f} | **{ndg_l:.3f}** |")
        w(f"| V87 | {v87_f1_c:.3f} | **{ndg_87:.3f}** |")
        w("")

        # ─── N6: HUS ────────────────────────────────────────────────
        gs_sam_sf = {(s, m) for m, s in gs_sad_sam}
        tr_sam_sf = {(s, m) for m, s in transarc_sad_sam}
        v45_sam_sf = {(s, m) for m, s in v45_sad_sam}
        llm_sam_sf = {(s, m) for m, s in llm_sad_sam}

        n6s_t = compute_hus(gs_sam_sf, tr_sam_sf)
        n6s_v = compute_hus(gs_sam_sf, v45_sam_sf)
        n6s_l = compute_hus(gs_sam_sf, llm_sam_sf)
        all_n6s[proj] = {"t": n6s_t, "v": n6s_v, "l": n6s_l}

        n6c_t = compute_hus(gs_sad_code, transarc_sad_code)
        n6c_v = compute_hus(gs_sad_code, v45_sad_code)
        n6c_l = compute_hus(gs_sad_code, llm_sad_code)
        all_n6c[proj] = {"t": n6c_t, "v": n6c_v, "l": n6c_l}

        w("### N6: HUS")
        w("")
        w("| Level | System | Coverage | Purity | HUS |")
        w("|:--|:--|:---:|:---:|:---:|")
        for level, label, data in [
            ("SAD-SAM", "TransArc", n6s_t), ("SAD-SAM", "V45", n6s_v), ("SAD-SAM", "LLM", n6s_l),
            ("SAD-CODE", "TransArc", n6c_t), ("SAD-CODE", "V45", n6c_v), ("SAD-CODE", "LLM", n6c_l),
        ]:
            w(f"| {level} | {label} | {data['coverage']:.3f} | {data['purity']:.3f} | **{data['hus']:.3f}** |")
        w(f"| both | V87 | N/A | N/A | N/A |")
        w("")

        # ─── Debiasing ──────────────────────────────────────────────
        idf_t = compute_idf_weighted_f1(gs_sad_code, transarc_sad_code, code_model)
        idf_v = compute_idf_weighted_f1(gs_sad_code, v45_sad_code, code_model)
        idf_l = compute_idf_weighted_f1(gs_sad_code, llm_sad_code, code_model)
        macro_t = compute_component_macro_f1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        macro_v = compute_component_macro_f1(gs_sad_code, v45_sad_code, gs_sam_code_map)
        macro_l = compute_component_macro_f1(gs_sad_code, llm_sad_code, gs_sam_code_map)
        pdr_t = compute_pdr_f1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        pdr_v = compute_pdr_f1(gs_sad_code, v45_sad_code, gs_sam_code_map)
        pdr_l = compute_pdr_f1(gs_sad_code, llm_sad_code, gs_sam_code_map)

        all_debias[proj] = {
            "idf": {"t": idf_t, "v": idf_v, "l": idf_l},
            "macro": {"t": macro_t, "v": macro_v, "l": macro_l},
            "pdr": {"t": pdr_t, "v": pdr_v, "l": pdr_l},
        }

        w("### Enrollment Debiasing")
        w("")
        w("| Metric | TransArc | V45 | LLM | V87 |")
        w("|:--|:---:|:---:|:---:|:---:|")
        w(f"| Standard F1 | {tc_f1:.3f} | {vc_f1:.3f} | {lc_f1:.3f} | {v87_f1_c:.3f} |")
        w(f"| IDF-Weighted F1 | {idf_t:.3f} | {idf_v:.3f} | {idf_l:.3f} | N/A |")
        w(f"| Component-Macro F1 | {macro_t:.3f} | {macro_v:.3f} | {macro_l:.3f} | N/A |")
        w(f"| PDR F1 | {pdr_t:.3f} | {pdr_v:.3f} | {pdr_l:.3f} | N/A |")
        w(f"| ACF1 | {n4_t['acf1']:.3f} | {n4_v['acf1']:.3f} | {n4_l['acf1']:.3f} | N/A |")
        w("")
        w("---")
        w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Aggregate Tables
    # ═══════════════════════════════════════════════════════════════════════
    n = len(PROJECTS)
    w("## Aggregate Comparison")
    w("")

    def best4(t, v, l, m87, m87_valid=True):
        vals = {"TransArc": t, "V45": v, "LLM": l}
        if m87_valid:
            vals["V87"] = m87
        return max(vals, key=vals.get)

    def na(v, fmt=".3f"):
        return f"{v:{fmt}}" if v is not None else "N/A"

    # ─── Standard F1 ─────────────────────────────────────────────
    w("### Standard F1")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    st = {"ts": 0, "vs": 0, "ls": 0, "m87s": 0, "tc": 0, "vc": 0, "lc": 0, "m87c": 0}
    for proj in PROJECTS:
        s = all_std[proj]
        ts, vs, ls = s["t_sam"][2], s["v_sam"][2], s["l_sam"][2]
        m87s = s["v87_sam"][2]
        tc, vc, lc = s["t_code"][2], s["v_code"][2], s["l_code"][2]
        m87c = s["v87_code"][2]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {m87s:.3f}* | {best4(ts, vs, ls, m87s)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {m87c:.3f} | {best4(tc, vc, lc, m87c)} |")
        st["ts"] += ts; st["vs"] += vs; st["ls"] += ls; st["m87s"] += m87s
        st["tc"] += tc; st["vc"] += vc; st["lc"] += lc; st["m87c"] += m87c
    w(f"| **Average** | SAM | **{st['ts']/n:.3f}** | **{st['vs']/n:.3f}** | **{st['ls']/n:.3f}** | **{st['m87s']/n:.3f}*** | |")
    w(f"| | CODE | **{st['tc']/n:.3f}** | **{st['vc']/n:.3f}** | **{st['lc']/n:.3f}** | **{st['m87c']/n:.3f}** | |")
    w("")
    w("\\* holdout-only (not full-gold)")
    w("")

    # ─── N1: MCC ─────────────────────────────────────────────────
    w("### N1: MCC")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    s1 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0, "m87c": 0}
    for proj in PROJECTS:
        ts = all_n1[proj]["t"]["mcc"]; vs = all_n1[proj]["v"]["mcc"]; ls = all_n1[proj]["l"]["mcc"]
        tc = all_n1c[proj]["t"]["mcc"]; vc = all_n1c[proj]["v"]["mcc"]; lc = all_n1c[proj]["l"]["mcc"]
        m87c = all_n1c[proj]["v87_mcc"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | N/A | {best4(ts, vs, ls, 0, False)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {m87c:.3f} | {best4(tc, vc, lc, m87c)} |")
        s1["ts"] += ts; s1["vs"] += vs; s1["ls"] += ls
        s1["tc"] += tc; s1["vc"] += vc; s1["lc"] += lc; s1["m87c"] += m87c
    w(f"| **Average** | SAM | **{s1['ts']/n:.3f}** | **{s1['vs']/n:.3f}** | **{s1['ls']/n:.3f}** | N/A | |")
    w(f"| | CODE | **{s1['tc']/n:.3f}** | **{s1['vc']/n:.3f}** | **{s1['lc']/n:.3f}** | **{s1['m87c']/n:.3f}** | |")
    w("")

    # ─── N2: EMR ─────────────────────────────────────────────────
    w("### N2: EMR")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    s2 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n2[proj]["t"]["emr"]; vs = all_n2[proj]["v"]["emr"]; ls = all_n2[proj]["l"]["emr"]
        tc = all_n2c[proj]["t"]["emr"]; vc = all_n2c[proj]["v"]["emr"]; lc = all_n2c[proj]["l"]["emr"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | N/A | {best4(ts, vs, ls, 0, False)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | N/A | {best4(tc, vc, lc, 0, False)} |")
        s2["ts"] += ts; s2["vs"] += vs; s2["ls"] += ls
        s2["tc"] += tc; s2["vc"] += vc; s2["lc"] += lc
    w(f"| **Average** | SAM | **{s2['ts']/n:.3f}** | **{s2['vs']/n:.3f}** | **{s2['ls']/n:.3f}** | N/A | |")
    w(f"| | CODE | **{s2['tc']/n:.3f}** | **{s2['vc']/n:.3f}** | **{s2['lc']/n:.3f}** | N/A | |")
    w("")

    # ─── N3: MAP ─────────────────────────────────────────────────
    w("### N3: MAP")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    s3 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n3[proj]["t"]["map"]; vs = all_n3[proj]["v"]["map"]; ls = all_n3[proj]["l"]["map"]
        tc = all_n3c[proj]["t"]["map"]; vc = all_n3c[proj]["v"]["map"]; lc = all_n3c[proj]["l"]["map"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | N/A | {best4(ts, vs, ls, 0, False)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | N/A | {best4(tc, vc, lc, 0, False)} |")
        s3["ts"] += ts; s3["vs"] += vs; s3["ls"] += ls
        s3["tc"] += tc; s3["vc"] += vc; s3["lc"] += lc
    w(f"| **Average** | SAM | **{s3['ts']/n:.3f}** | **{s3['vs']/n:.3f}** | **{s3['ls']/n:.3f}** | N/A | |")
    w(f"| | CODE | **{s3['tc']/n:.3f}** | **{s3['vc']/n:.3f}** | **{s3['lc']/n:.3f}** | N/A | |")
    w("")

    # ─── N4: ACF1 ────────────────────────────────────────────────
    w("### N4: ACF1")
    w("")
    w("| Project | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:---:|:---:|:---:|:---:|:--|")
    s4 = {"t": 0, "v": 0, "l": 0}
    for proj in PROJECTS:
        t = all_n4[proj]["t"]["acf1"]; v = all_n4[proj]["v"]["acf1"]; l = all_n4[proj]["l"]["acf1"]
        w(f"| {proj} | {t:.3f} | {v:.3f} | {l:.3f} | N/A | {best4(t, v, l, 0, False)} |")
        s4["t"] += t; s4["v"] += v; s4["l"] += l
    w(f"| **Average** | **{s4['t']/n:.3f}** | **{s4['v']/n:.3f}** | **{s4['l']/n:.3f}** | N/A | |")
    w("")

    # ─── N5: NDG ─────────────────────────────────────────────────
    w("### N5: NDG")
    w("")
    w("| Project | Random | Oracle | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|:--|")
    s5 = {"t": 0, "v": 0, "l": 0, "m87": 0}
    for proj in PROJECTS:
        d = all_n5[proj]
        w(f"| {proj} | {d['random_f1']:.3f} | {d['oracle_f1']:.3f} | {d['t']:.3f} | {d['v']:.3f} | {d['l']:.3f} | {d['v87']:.3f} | {best4(d['t'], d['v'], d['l'], d['v87'])} |")
        s5["t"] += d["t"]; s5["v"] += d["v"]; s5["l"] += d["l"]; s5["m87"] += d["v87"]
    w(f"| **Average** | | | **{s5['t']/n:.3f}** | **{s5['v']/n:.3f}** | **{s5['l']/n:.3f}** | **{s5['m87']/n:.3f}** | |")
    w("")

    # ─── N6: HUS ─────────────────────────────────────────────────
    w("### N6: HUS")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    s6 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n6s[proj]["t"]["hus"]; vs = all_n6s[proj]["v"]["hus"]; ls = all_n6s[proj]["l"]["hus"]
        tc = all_n6c[proj]["t"]["hus"]; vc = all_n6c[proj]["v"]["hus"]; lc = all_n6c[proj]["l"]["hus"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | N/A | {best4(ts, vs, ls, 0, False)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | N/A | {best4(tc, vc, lc, 0, False)} |")
        s6["ts"] += ts; s6["vs"] += vs; s6["ls"] += ls
        s6["tc"] += tc; s6["vc"] += vc; s6["lc"] += lc
    w(f"| **Average** | SAM | **{s6['ts']/n:.3f}** | **{s6['vs']/n:.3f}** | **{s6['ls']/n:.3f}** | N/A | |")
    w(f"| | CODE | **{s6['tc']/n:.3f}** | **{s6['vc']/n:.3f}** | **{s6['lc']/n:.3f}** | N/A | |")
    w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Grand Summary
    # ═══════════════════════════════════════════════════════════════════════
    w("---")
    w("")
    w("## Grand Summary")
    w("")

    avgs = {}
    avgs["f1_sam"] = (st["ts"]/n, st["vs"]/n, st["ls"]/n, st["m87s"]/n)
    avgs["f1_code"] = (st["tc"]/n, st["vc"]/n, st["lc"]/n, st["m87c"]/n)
    avgs["n1_sam"] = (s1["ts"]/n, s1["vs"]/n, s1["ls"]/n, None)
    avgs["n1_code"] = (s1["tc"]/n, s1["vc"]/n, s1["lc"]/n, s1["m87c"]/n)
    avgs["n2_sam"] = (s2["ts"]/n, s2["vs"]/n, s2["ls"]/n, None)
    avgs["n2_code"] = (s2["tc"]/n, s2["vc"]/n, s2["lc"]/n, None)
    avgs["n3_sam"] = (s3["ts"]/n, s3["vs"]/n, s3["ls"]/n, None)
    avgs["n3_code"] = (s3["tc"]/n, s3["vc"]/n, s3["lc"]/n, None)
    avgs["n4"] = (s4["t"]/n, s4["v"]/n, s4["l"]/n, None)
    avgs["n5"] = (s5["t"]/n, s5["v"]/n, s5["l"]/n, s5["m87"]/n)
    avgs["n6_sam"] = (s6["ts"]/n, s6["vs"]/n, s6["ls"]/n, None)
    avgs["n6_code"] = (s6["tc"]/n, s6["vc"]/n, s6["lc"]/n, None)

    for mk in ["idf", "macro", "pdr"]:
        t_a = sum(all_debias[p][mk]["t"] for p in PROJECTS) / n
        v_a = sum(all_debias[p][mk]["v"] for p in PROJECTS) / n
        l_a = sum(all_debias[p][mk]["l"] for p in PROJECTS) / n
        avgs[mk] = (t_a, v_a, l_a, None)

    rows_def = [
        ("F1 (standard)", "SAM", "f1_sam"),
        ("F1 (standard)", "CODE", "f1_code"),
        ("**N1: MCC**", "SAM", "n1_sam"),
        ("**N1: MCC**", "CODE", "n1_code"),
        ("**N2: EMR**", "SAM", "n2_sam"),
        ("**N2: EMR**", "CODE", "n2_code"),
        ("**N3: MAP**", "SAM", "n3_sam"),
        ("**N3: MAP**", "CODE", "n3_code"),
        ("**N4: ACF1**", "CODE", "n4"),
        ("**N5: NDG**", "CODE", "n5"),
        ("**N6: HUS**", "SAM", "n6_sam"),
        ("**N6: HUS**", "CODE", "n6_code"),
        ("IDF-Weighted F1", "CODE", "idf"),
        ("Component-Macro F1", "CODE", "macro"),
        ("PDR F1", "CODE", "pdr"),
    ]

    w("| Metric | Level | TransArc | V45 | LLM | V87 | Best (all) |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")

    for label, level, key in rows_def:
        t, v, l, m87 = avgs[key]
        v87_str = f"{m87:.3f}" if m87 is not None else "N/A"
        has_v87 = m87 is not None
        b = best4(t, v, l, m87 if m87 else 0, has_v87)
        note = ""
        if key == "f1_sam":
            v87_str += "*"
            note = ""
        w(f"| {label} | {level} | {t:.3f} | {v:.3f} | {l:.3f} | {v87_str} | {b} |")
    w("")
    w("\\* holdout-only, not directly comparable")
    w("")

    # ─── Computable metrics head-to-head (only where V87 has data) ──
    w("### V87 Head-to-Head (computable metrics only)")
    w("")
    w("Metrics where V87 has data for fair comparison:")
    w("")
    w("| Metric | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:---:|:---:|:---:|:---:|:--|")
    computable = [
        ("F1 SAD-CODE", avgs["f1_code"]),
        ("N1: MCC CODE", avgs["n1_code"]),
        ("N5: NDG", avgs["n5"]),
    ]
    for label, (t, v, l, m87) in computable:
        b = best4(t, v, l, m87)
        w(f"| {label} | {t:.3f} | {v:.3f} | {l:.3f} | {m87:.3f} | {b} |")
    w("")

    # Per-project detail for computable metrics
    w("**Per-project for computable metrics:**")
    w("")
    w("| Project | Metric | TransArc | V45 | LLM | V87 | Best |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")
    for proj in PROJECTS:
        s = all_std[proj]
        tc = s["t_code"][2]; vc = s["v_code"][2]; lc = s["l_code"][2]; m87c = s["v87_code"][2]
        w(f"| {proj} | F1 CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {m87c:.3f} | {best4(tc, vc, lc, m87c)} |")
        tc = all_n1c[proj]["t"]["mcc"]; vc = all_n1c[proj]["v"]["mcc"]; lc = all_n1c[proj]["l"]["mcc"]; m87c = all_n1c[proj]["v87_mcc"]
        w(f"| | MCC CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {m87c:.3f} | {best4(tc, vc, lc, m87c)} |")
        d = all_n5[proj]
        w(f"| | NDG | {d['t']:.3f} | {d['v']:.3f} | {d['l']:.3f} | {d['v87']:.3f} | {best4(d['t'], d['v'], d['l'], d['v87'])} |")
    w("")

    # ─── Key Findings ────────────────────────────────────────────
    w("### Key Findings")
    w("")

    # Count V87 wins on computable metrics per project
    v87_wins = 0
    v87_total = 0
    for proj in PROJECTS:
        for t_val, v_val, l_val, m87_val in [
            (all_std[proj]["t_code"][2], all_std[proj]["v_code"][2], all_std[proj]["l_code"][2], all_std[proj]["v87_code"][2]),
            (all_n1c[proj]["t"]["mcc"], all_n1c[proj]["v"]["mcc"], all_n1c[proj]["l"]["mcc"], all_n1c[proj]["v87_mcc"]),
            (all_n5[proj]["t"], all_n5[proj]["v"], all_n5[proj]["l"], all_n5[proj]["v87"]),
        ]:
            v87_total += 1
            if best4(t_val, v_val, l_val, m87_val) == "V87":
                v87_wins += 1

    w(f"1. **V87 wins {v87_wins}/{v87_total} computable metric-project combinations**")
    w(f"   (F1-CODE + MCC-CODE + NDG across 5 projects)")
    w("")

    # V87 vs TransArc on computable metrics
    v87_beats_t = 0
    t_beats_v87 = 0
    for proj in PROJECTS:
        for t_val, m87_val in [
            (all_std[proj]["t_code"][2], all_std[proj]["v87_code"][2]),
            (all_n1c[proj]["t"]["mcc"], all_n1c[proj]["v87_mcc"]),
            (all_n5[proj]["t"], all_n5[proj]["v87"]),
        ]:
            if m87_val > t_val + 0.005:
                v87_beats_t += 1
            elif t_val > m87_val + 0.005:
                t_beats_v87 += 1

    w(f"2. **V87 vs TransArc**: V87 wins {v87_beats_t}/{v87_total}, TransArc wins {t_beats_v87}/{v87_total}")
    w(f"   Note: V87 uses 10% gold SAD-SAM + TransArc SAM-CODE; TransArc is fully automatic")
    w("")

    # Avg computable metrics
    f1c = avgs["f1_code"]
    mcc_c = avgs["n1_code"]
    ndg = avgs["n5"]
    w("3. **Average computable metrics:**")
    w(f"   - F1 CODE: TransArc={f1c[0]:.3f}, V45={f1c[1]:.3f}, LLM={f1c[2]:.3f}, V87={f1c[3]:.3f}")
    w(f"   - MCC CODE: TransArc={mcc_c[0]:.3f}, V45={mcc_c[1]:.3f}, LLM={mcc_c[2]:.3f}, V87={mcc_c[3]:.3f}")
    w(f"   - NDG: TransArc={ndg[0]:.3f}, V45={ndg[1]:.3f}, LLM={ndg[2]:.3f}, V87={ndg[3]:.3f}")
    w("")

    w("4. **Fair comparison caveat**: V87 has structural advantages (few-shot training)")
    w("   and disadvantages (TransArc SAM-CODE vs gold SAM-CODE) that make direct")
    w("   comparison imperfect. Metrics requiring per-link data (N2-N4, N6) would")
    w("   provide a more complete picture but are unavailable for V87.")
    w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 four_system_comparison.py")
    w("# Output: FOUR_SYSTEM_COMPARISON.md")
    w("```")

    # ─── Write output ────────────────────────────────────────────
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWritten to {OUTPUT_MD}")

    # ─── Console summary ─────────────────────────────────────────
    print("\n" + "=" * 90)
    print("GRAND SUMMARY: Four-System Comparison")
    print("=" * 90)
    print(f"\n{'Metric':<25} {'Level':<6} {'TransArc':>10} {'V45':>10} {'LLM':>10} {'V87':>10} {'Best':<10}")
    print("-" * 85)
    for label, level, key in rows_def:
        clean = label.replace("**", "")
        t, v, l, m87 = avgs[key]
        v87_str = f"{m87:10.3f}" if m87 is not None else "       N/A"
        has_v87 = m87 is not None
        b = best4(t, v, l, m87 if m87 else 0, has_v87)
        print(f"{clean:<25} {level:<6} {t:>10.3f} {v:>10.3f} {l:>10.3f} {v87_str} {b:<10}")

    # V87 computable metrics head-to-head
    print(f"\nV87 computable metrics (F1-CODE, MCC-CODE, NDG):")
    print(f"  V87 wins: {v87_wins}/{v87_total} project-metric combinations")
    print(f"  V87 vs TransArc: {v87_beats_t} wins, {t_beats_v87} losses")


if __name__ == "__main__":
    main()
