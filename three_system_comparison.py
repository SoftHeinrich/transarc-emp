#!/usr/bin/env python3
"""
Three-System Comparison: TransArc vs V45 vs LLM Adaptive Best
on all 6 new metrics (N1-N6) at both SAD-SAM and SAD-CODE levels,
plus enrollment debiasing metrics.

Outputs: THREE_SYSTEM_COMPARISON.md
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

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/THREE_SYSTEM_COMPARISON.md")

# ─── LLM Adaptive Strategy per project ──────────────────────────────────────

ADAPTIVE_STRATEGIES = {
    "mediastore": "majority",
    "teastore": "intersection",
    "teammates": "intersection",
    "bigbluebutton": "majority",
    "jabref": "single",
}


def load_llm_adaptive_classifications(project):
    """Load the adaptive-best LLM classification for a project.

    Returns dict of {sent_num_str: [comp_name, ...]}
    """
    strategy = ADAPTIVE_STRATEGIES[project]

    if strategy == "single":
        return load_json(SINGLE_DIR / f"{project}.json")

    # Load 3 variants for voting
    variants = {}
    for v in VARIANTS:
        path = MULTI_DIR / f"{project}_{v}.json"
        if path.exists():
            variants[v] = load_json(path)

    if len(variants) != 3:
        raise ValueError(f"Expected 3 variants for {project}, got {len(variants)}")

    if strategy == "majority":
        return majority_vote(variants)
    elif strategy == "intersection":
        return intersection_vote(variants)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def llm_classifications_to_sad_sam(classifications, name_to_ids):
    """Convert LLM classifications to SAD-SAM links: set of (model_element_id, sentence_str).

    Args:
        classifications: {sent_num_str: [comp_name, ...]}
        name_to_ids: {comp_name: set(ae_id)}

    Returns:
        set of (model_element_id, sentence_str)
    """
    links = set()
    for sent_num, comp_names in classifications.items():
        for comp_name in comp_names:
            ae_ids = name_to_ids.get(comp_name, set())
            for ae_id in ae_ids:
                links.add((ae_id, sent_num))
    return links


# ─── Enrollment debiasing (from enrollment_bias_analysis.py) ─────────────────

def compute_idf_weighted_f1(gold_sad_code, result_sad_code, code_model_files):
    """IDF-weighted F1: weight each file by log(N/df) where df = times file appears in gold."""
    file_df = defaultdict(int)
    for sent, code in gold_sad_code:
        file_df[code] += 1
    N = len(set(s for s, _ in gold_sad_code))  # total gold sentences

    def idf(f):
        df = file_df.get(f, 0)
        if df == 0:
            return 1.0
        return math.log(1 + N / df)

    tp_set = gold_sad_code & result_sad_code
    fp_set = result_sad_code - gold_sad_code
    fn_set = gold_sad_code - result_sad_code

    w_tp = sum(idf(c) for _, c in tp_set)
    w_fp = sum(idf(c) for _, c in fp_set)
    w_fn = sum(idf(c) for _, c in fn_set)

    w_prec = w_tp / (w_tp + w_fp) if (w_tp + w_fp) > 0 else 0
    w_rec = w_tp / (w_tp + w_fn) if (w_tp + w_fn) > 0 else 0
    f1 = 2 * w_prec * w_rec / (w_prec + w_rec) if (w_prec + w_rec) > 0 else 0
    return f1


def compute_component_macro_f1(gold_sad_code, result_sad_code, sam_code_map):
    """Component-Macro F1: compute F1 per component, then average."""
    # Build file → component mapping
    file_to_comps = defaultdict(set)
    for comp, files in sam_code_map.items():
        for f in files:
            file_to_comps[f].add(comp)

    # Group gold and result by component
    gold_by_comp = defaultdict(set)
    result_by_comp = defaultdict(set)
    for sent, code in gold_sad_code:
        for comp in file_to_comps.get(code, {"unknown"}):
            gold_by_comp[comp].add((sent, code))
    for sent, code in result_sad_code:
        for comp in file_to_comps.get(code, {"unknown"}):
            result_by_comp[comp].add((sent, code))

    f1s = []
    for comp in gold_by_comp:
        g = gold_by_comp[comp]
        r = result_by_comp.get(comp, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * rec / (p + rec) if (p + rec) > 0 else 0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0


def compute_pdr_f1(gold_sad_code, result_sad_code, sam_code_map):
    """Popularity-Debiased F1: weight each file link by 1/popularity.

    popularity(file) = number of components that map to this file.
    """
    file_popularity = defaultdict(int)
    for comp, files in sam_code_map.items():
        for f in files:
            file_popularity[f] += 1

    tp_set = gold_sad_code & result_sad_code
    fp_set = result_sad_code - gold_sad_code
    fn_set = gold_sad_code - result_sad_code

    def weighted_sum(link_set):
        total = 0.0
        for sent, code in link_set:
            pop = file_popularity.get(code, 1)
            total += 1.0 / pop
        return total

    w_tp = weighted_sum(tp_set)
    w_fp = weighted_sum(fp_set)
    w_fn = weighted_sum(fn_set)

    w_prec = w_tp / (w_tp + w_fp) if (w_tp + w_fp) > 0 else 0
    w_rec = w_tp / (w_tp + w_fn) if (w_tp + w_fn) > 0 else 0
    f1 = 2 * w_prec * w_rec / (w_prec + w_rec) if (w_prec + w_rec) > 0 else 0
    return f1


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    lines = []
    w = lines.append

    w("# Three-System Comparison: TransArc vs V45 vs LLM Adaptive")
    w("")
    w("Unified evaluation of 3 systems across 6 new metrics (N1-N6)")
    w("at both SAD-SAM and SAD-CODE levels, plus enrollment debiasing metrics.")
    w("")
    w("**Systems:**")
    w("- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)")
    w("- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through gold SAM-CODE")
    w("- **LLM Adaptive**: Zero-training LLM classifier (best strategy per project),")
    w("  projected through gold SAM-CODE")
    w("")
    w("| Project | LLM Strategy |")
    w("|:--|:--|")
    for proj in PROJECTS:
        w(f"| {proj} | {ADAPTIVE_STRATEGIES[proj]} |")
    w("")
    w("---")
    w("")

    # Storage for aggregates
    all_std = {}       # standard F1
    all_n1 = {}        # MCC at SAD-SAM
    all_n1c = {}       # MCC at SAD-CODE
    all_n2 = {}        # EMR at SAD-SAM
    all_n2c = {}       # EMR at SAD-CODE
    all_n3 = {}        # MAP at SAD-SAM
    all_n3c = {}       # MAP at SAD-CODE
    all_n4 = {}        # ACF1
    all_n5 = {}        # NDG
    all_n6s = {}       # HUS at SAD-SAM
    all_n6c = {}       # HUS at SAD-CODE
    all_debias = {}    # debiasing metrics

    for proj in PROJECTS:
        w(f"## {proj.capitalize()}")
        w("")

        # ─── Load shared data ────────────────────────────────────────────
        code_model = load_code_model_files(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sad_sam_maps = load_gs_sad_sam_maps(proj)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        text = load_text(proj)
        model_names = load_model_element_names(proj)

        all_sents = set(text.keys())
        all_comps = set(model_names.keys())

        # ─── TransArc data ───────────────────────────────────────────────
        transarc_sad_sam = load_transarc_intermediate_sad_sam(proj)
        transarc_sad_code = load_result_sad_code(proj)

        # ─── V45 data ───────────────────────────────────────────────────
        v45_sad_sam = load_v45_sad_sam(proj)
        v45_ranked = load_v45_sad_sam_with_confidence(proj)
        v45_sad_code = compose_sad_code(v45_sad_sam, gs_sam_code_map)

        # ─── LLM Adaptive data ──────────────────────────────────────────
        llm_cls = load_llm_adaptive_classifications(proj)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        llm_sad_sam = llm_classifications_to_sad_sam(llm_cls, name_to_ids)
        llm_sad_code, _ = classifications_to_result_set(llm_cls, name_to_ids, model_to_files)

        # ─── Standard F1 ────────────────────────────────────────────────
        t_p, t_r, t_f1, t_tp, t_fp, t_fn = calc_metrics(gs_sad_sam, transarc_sad_sam)
        v_p, v_r, v_f1, v_tp, v_fp, v_fn = calc_metrics(gs_sad_sam, v45_sad_sam)
        l_p, l_r, l_f1, l_tp, l_fp, l_fn = calc_metrics(gs_sad_sam, llm_sad_sam)

        tc_p, tc_r, tc_f1, tc_tp, tc_fp, tc_fn = calc_metrics(gs_sad_code, transarc_sad_code)
        vc_p, vc_r, vc_f1, vc_tp, vc_fp, vc_fn = calc_metrics(gs_sad_code, v45_sad_code)
        lc_p, lc_r, lc_f1, lc_tp, lc_fp, lc_fn = calc_metrics(gs_sad_code, llm_sad_code)

        all_std[proj] = {
            "t_sam": (t_p, t_r, t_f1), "v_sam": (v_p, v_r, v_f1), "l_sam": (l_p, l_r, l_f1),
            "t_code": (tc_p, tc_r, tc_f1), "v_code": (vc_p, vc_r, vc_f1), "l_code": (lc_p, lc_r, lc_f1),
        }

        w("### Standard P/R/F1")
        w("")
        w("| Level | System | P | R | F1 | TP | FP | FN |")
        w("|:--|:--|:---:|:---:|:---:|---:|---:|---:|")
        w(f"| SAD-SAM | TransArc | {t_p:.3f} | {t_r:.3f} | {t_f1:.3f} | {t_tp} | {t_fp} | {t_fn} |")
        w(f"| SAD-SAM | V45 | {v_p:.3f} | {v_r:.3f} | {v_f1:.3f} | {v_tp} | {v_fp} | {v_fn} |")
        w(f"| SAD-SAM | LLM Adaptive | {l_p:.3f} | {l_r:.3f} | {l_f1:.3f} | {l_tp} | {l_fp} | {l_fn} |")
        w(f"| SAD-CODE | TransArc | {tc_p:.3f} | {tc_r:.3f} | {tc_f1:.3f} | {tc_tp} | {tc_fp} | {tc_fn} |")
        w(f"| SAD-CODE | V45 | {vc_p:.3f} | {vc_r:.3f} | {vc_f1:.3f} | {vc_tp} | {vc_fp} | {vc_fn} |")
        w(f"| SAD-CODE | LLM Adaptive | {lc_p:.3f} | {lc_r:.3f} | {lc_f1:.3f} | {lc_tp} | {lc_fp} | {lc_fn} |")
        w("")

        # ─── N1: MCC ────────────────────────────────────────────────────
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

        n1c_t = compute_mcc(gs_sad_code, transarc_sad_code, all_sents, all_code_files)
        n1c_v = compute_mcc(gs_sad_code, v45_sad_code, all_sents, all_code_files)
        n1c_l = compute_mcc(gs_sad_code, llm_sad_code, all_sents, all_code_files)
        all_n1c[proj] = {"t": n1c_t, "v": n1c_v, "l": n1c_l}

        w("### N1: MCC")
        w("")
        w("| Level | System | MCC | Bal.Acc | TP | FP | FN | TN |")
        w("|:--|:--|:---:|:---:|---:|---:|---:|---:|")
        for level, label, data in [
            ("SAD-SAM", "TransArc", n1_t), ("SAD-SAM", "V45", n1_v), ("SAD-SAM", "LLM", n1_l),
            ("SAD-CODE", "TransArc", n1c_t), ("SAD-CODE", "V45", n1c_v), ("SAD-CODE", "LLM", n1c_l),
        ]:
            w(f"| {level} | {label} | **{data['mcc']:.3f}** | {data['balanced_accuracy']:.3f} | {data['tp']} | {data['fp']} | {data['fn']} | {data['tn']} |")
        w("")

        # ─── N2: EMR ────────────────────────────────────────────────────
        n2_t = compute_emr(gs_sad_sam, transarc_sad_sam)
        n2_v = compute_emr(gs_sad_sam, v45_sad_sam)
        n2_l = compute_emr(gs_sad_sam, llm_sad_sam)
        all_n2[proj] = {"t": n2_t, "v": n2_v, "l": n2_l}

        # SAD-CODE level (flip tuples)
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
        w("")

        # ─── N3: MAP ────────────────────────────────────────────────────
        transarc_ranked = transarc_sad_sam_as_ranked(transarc_sad_sam)
        llm_ranked_sam = [(sent, comp, 0.5) for comp, sent in llm_sad_sam]  # uniform
        n3_t = compute_map(gs_sad_sam, transarc_ranked)
        n3_v = compute_map(gs_sad_sam, v45_ranked)
        n3_l = compute_map(gs_sad_sam, llm_ranked_sam)
        all_n3[proj] = {"t": n3_t, "v": n3_v, "l": n3_l}

        # SAD-CODE level (flip gold)
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
        w("| Level | System | MAP | Note |")
        w("|:--|:--|:---:|:--|")
        w(f"| SAD-SAM | TransArc | **{n3_t['map']:.3f}** | uniform conf |")
        w(f"| SAD-SAM | V45 | **{n3_v['map']:.3f}** | per-link conf |")
        w(f"| SAD-SAM | LLM | **{n3_l['map']:.3f}** | uniform conf |")
        w(f"| SAD-CODE | TransArc | **{n3c_t['map']:.3f}** | uniform conf |")
        w(f"| SAD-CODE | V45 | **{n3c_v['map']:.3f}** | inherited conf |")
        w(f"| SAD-CODE | LLM | **{n3c_l['map']:.3f}** | uniform conf |")
        w("")

        # ─── N4: ACF1 ───────────────────────────────────────────────────
        n4_t = compute_acf1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        n4_v = compute_acf1(gs_sad_code, v45_sad_code, gs_sam_code_map)
        n4_l = compute_acf1(gs_sad_code, llm_sad_code, gs_sam_code_map)
        all_n4[proj] = {"t": n4_t, "v": n4_v, "l": n4_l}

        w("### N4: ACF1")
        w("")
        w("| System | Std F1 | ACF1 | Shift | w-TP | w-FP | w-FN |")
        w("|:--|:---:|:---:|:---:|---:|---:|---:|")
        for label, std_f1, data in [
            ("TransArc", tc_f1, n4_t), ("V45", vc_f1, n4_v), ("LLM", lc_f1, n4_l),
        ]:
            w(f"| {label} | {std_f1:.3f} | **{data['acf1']:.3f}** | {data['acf1']-std_f1:+.3f} | {data['weighted_tp']:.1f} | {data['weighted_fp']:.1f} | {data['weighted_fn']:.1f} |")
        w("")

        # ─── N5: NDG ────────────────────────────────────────────────────
        n_sents = len(all_sents)
        random_f1 = compute_random_f1(gs_sad_code, n_sents, len(all_comps), gs_sam_code_map)
        oracle_f1, oracle_links = compute_oracle_f1(gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)

        ndg_t = compute_ndg(tc_f1, random_f1, oracle_f1)
        ndg_v = compute_ndg(vc_f1, random_f1, oracle_f1)
        ndg_l = compute_ndg(lc_f1, random_f1, oracle_f1)
        all_n5[proj] = {"t": ndg_t, "v": ndg_v, "l": ndg_l,
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
        w("")

        # ─── N6: HUS ────────────────────────────────────────────────────
        # SAD-SAM (sentence-first format)
        gs_sam_sf = {(s, m) for m, s in gs_sad_sam}
        tr_sam_sf = {(s, m) for m, s in transarc_sad_sam}
        v45_sam_sf = {(s, m) for m, s in v45_sad_sam}
        llm_sam_sf = {(s, m) for m, s in llm_sad_sam}

        n6s_t = compute_hus(gs_sam_sf, tr_sam_sf)
        n6s_v = compute_hus(gs_sam_sf, v45_sam_sf)
        n6s_l = compute_hus(gs_sam_sf, llm_sam_sf)
        all_n6s[proj] = {"t": n6s_t, "v": n6s_v, "l": n6s_l}

        # SAD-CODE
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
        w("")

        # ─── Enrollment Debiasing ───────────────────────────────────────
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
            "std": {"t": tc_f1, "v": vc_f1, "l": lc_f1},
        }

        w("### Enrollment Debiasing")
        w("")
        w("| Metric | TransArc | V45 | LLM |")
        w("|:--|:---:|:---:|:---:|")
        w(f"| Standard F1 | {tc_f1:.3f} | {vc_f1:.3f} | {lc_f1:.3f} |")
        w(f"| IDF-Weighted F1 | {idf_t:.3f} | {idf_v:.3f} | {idf_l:.3f} |")
        w(f"| Component-Macro F1 | {macro_t:.3f} | {macro_v:.3f} | {macro_l:.3f} |")
        w(f"| Popularity-Debiased F1 | {pdr_t:.3f} | {pdr_v:.3f} | {pdr_l:.3f} |")
        w(f"| N4: ACF1 | {n4_t['acf1']:.3f} | {n4_v['acf1']:.3f} | {n4_l['acf1']:.3f} |")
        w("")
        w("---")
        w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Aggregate Comparison Tables
    # ═══════════════════════════════════════════════════════════════════════
    w("## Aggregate Comparison")
    w("")
    n = len(PROJECTS)

    def best3(t, v, l):
        """Return label of best value."""
        vals = {"TransArc": t, "V45": v, "LLM": l}
        return max(vals, key=vals.get)

    # ─── Standard F1 ─────────────────────────────────────────────────
    w("### Standard F1")
    w("")
    w("| Project | | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    sums = {"t_sam": 0, "v_sam": 0, "l_sam": 0, "t_code": 0, "v_code": 0, "l_code": 0}
    for proj in PROJECTS:
        s = all_std[proj]
        ts, vs, ls = s["t_sam"][2], s["v_sam"][2], s["l_sam"][2]
        tc, vc, lc = s["t_code"][2], s["v_code"][2], s["l_code"][2]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {best3(ts, vs, ls)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {best3(tc, vc, lc)} |")
        sums["t_sam"] += ts; sums["v_sam"] += vs; sums["l_sam"] += ls
        sums["t_code"] += tc; sums["v_code"] += vc; sums["l_code"] += lc
    w(f"| **Average** | SAM | **{sums['t_sam']/n:.3f}** | **{sums['v_sam']/n:.3f}** | **{sums['l_sam']/n:.3f}** | **{best3(sums['t_sam'], sums['v_sam'], sums['l_sam'])}** |")
    w(f"| | CODE | **{sums['t_code']/n:.3f}** | **{sums['v_code']/n:.3f}** | **{sums['l_code']/n:.3f}** | **{best3(sums['t_code'], sums['v_code'], sums['l_code'])}** |")
    w("")

    # ─── N1: MCC ─────────────────────────────────────────────────────
    w("### N1: MCC")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    s1 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n1[proj]["t"]["mcc"]; vs = all_n1[proj]["v"]["mcc"]; ls = all_n1[proj]["l"]["mcc"]
        tc = all_n1c[proj]["t"]["mcc"]; vc = all_n1c[proj]["v"]["mcc"]; lc = all_n1c[proj]["l"]["mcc"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {best3(ts, vs, ls)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {best3(tc, vc, lc)} |")
        s1["ts"] += ts; s1["vs"] += vs; s1["ls"] += ls
        s1["tc"] += tc; s1["vc"] += vc; s1["lc"] += lc
    w(f"| **Average** | SAM | **{s1['ts']/n:.3f}** | **{s1['vs']/n:.3f}** | **{s1['ls']/n:.3f}** | **{best3(s1['ts'], s1['vs'], s1['ls'])}** |")
    w(f"| | CODE | **{s1['tc']/n:.3f}** | **{s1['vc']/n:.3f}** | **{s1['lc']/n:.3f}** | **{best3(s1['tc'], s1['vc'], s1['lc'])}** |")
    w("")

    # ─── N2: EMR ─────────────────────────────────────────────────────
    w("### N2: EMR")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    s2 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n2[proj]["t"]["emr"]; vs = all_n2[proj]["v"]["emr"]; ls = all_n2[proj]["l"]["emr"]
        tc = all_n2c[proj]["t"]["emr"]; vc = all_n2c[proj]["v"]["emr"]; lc = all_n2c[proj]["l"]["emr"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {best3(ts, vs, ls)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {best3(tc, vc, lc)} |")
        s2["ts"] += ts; s2["vs"] += vs; s2["ls"] += ls
        s2["tc"] += tc; s2["vc"] += vc; s2["lc"] += lc
    w(f"| **Average** | SAM | **{s2['ts']/n:.3f}** | **{s2['vs']/n:.3f}** | **{s2['ls']/n:.3f}** | **{best3(s2['ts'], s2['vs'], s2['ls'])}** |")
    w(f"| | CODE | **{s2['tc']/n:.3f}** | **{s2['vc']/n:.3f}** | **{s2['lc']/n:.3f}** | **{best3(s2['tc'], s2['vc'], s2['lc'])}** |")
    w("")

    # ─── N3: MAP ─────────────────────────────────────────────────────
    w("### N3: MAP")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    s3 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n3[proj]["t"]["map"]; vs = all_n3[proj]["v"]["map"]; ls = all_n3[proj]["l"]["map"]
        tc = all_n3c[proj]["t"]["map"]; vc = all_n3c[proj]["v"]["map"]; lc = all_n3c[proj]["l"]["map"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {best3(ts, vs, ls)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {best3(tc, vc, lc)} |")
        s3["ts"] += ts; s3["vs"] += vs; s3["ls"] += ls
        s3["tc"] += tc; s3["vc"] += vc; s3["lc"] += lc
    w(f"| **Average** | SAM | **{s3['ts']/n:.3f}** | **{s3['vs']/n:.3f}** | **{s3['ls']/n:.3f}** | **{best3(s3['ts'], s3['vs'], s3['ls'])}** |")
    w(f"| | CODE | **{s3['tc']/n:.3f}** | **{s3['vc']/n:.3f}** | **{s3['lc']/n:.3f}** | **{best3(s3['tc'], s3['vc'], s3['lc'])}** |")
    w("")

    # ─── N4: ACF1 ────────────────────────────────────────────────────
    w("### N4: ACF1 (Enrollment-Corrected)")
    w("")
    w("| Project | TransArc | V45 | LLM | Best |")
    w("|:--|:---:|:---:|:---:|:--|")
    s4 = {"t": 0, "v": 0, "l": 0}
    for proj in PROJECTS:
        t = all_n4[proj]["t"]["acf1"]; v = all_n4[proj]["v"]["acf1"]; l = all_n4[proj]["l"]["acf1"]
        w(f"| {proj} | {t:.3f} | {v:.3f} | {l:.3f} | {best3(t, v, l)} |")
        s4["t"] += t; s4["v"] += v; s4["l"] += l
    w(f"| **Average** | **{s4['t']/n:.3f}** | **{s4['v']/n:.3f}** | **{s4['l']/n:.3f}** | **{best3(s4['t'], s4['v'], s4['l'])}** |")
    w("")

    # ─── N5: NDG ─────────────────────────────────────────────────────
    w("### N5: NDG (Difficulty-Normalized)")
    w("")
    w("| Project | Random | Oracle | TransArc | V45 | LLM | Best |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:--|")
    s5 = {"t": 0, "v": 0, "l": 0}
    for proj in PROJECTS:
        d = all_n5[proj]
        w(f"| {proj} | {d['random_f1']:.3f} | {d['oracle_f1']:.3f} | {d['t']:.3f} | {d['v']:.3f} | {d['l']:.3f} | {best3(d['t'], d['v'], d['l'])} |")
        s5["t"] += d["t"]; s5["v"] += d["v"]; s5["l"] += d["l"]
    w(f"| **Average** | | | **{s5['t']/n:.3f}** | **{s5['v']/n:.3f}** | **{s5['l']/n:.3f}** | **{best3(s5['t'], s5['v'], s5['l'])}** |")
    w("")

    # ─── N6: HUS ─────────────────────────────────────────────────────
    w("### N6: HUS")
    w("")
    w("| Project | Level | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    s6 = {"ts": 0, "vs": 0, "ls": 0, "tc": 0, "vc": 0, "lc": 0}
    for proj in PROJECTS:
        ts = all_n6s[proj]["t"]["hus"]; vs = all_n6s[proj]["v"]["hus"]; ls = all_n6s[proj]["l"]["hus"]
        tc = all_n6c[proj]["t"]["hus"]; vc = all_n6c[proj]["v"]["hus"]; lc = all_n6c[proj]["l"]["hus"]
        w(f"| {proj} | SAM | {ts:.3f} | {vs:.3f} | {ls:.3f} | {best3(ts, vs, ls)} |")
        w(f"| | CODE | {tc:.3f} | {vc:.3f} | {lc:.3f} | {best3(tc, vc, lc)} |")
        s6["ts"] += ts; s6["vs"] += vs; s6["ls"] += ls
        s6["tc"] += tc; s6["vc"] += vc; s6["lc"] += lc
    w(f"| **Average** | SAM | **{s6['ts']/n:.3f}** | **{s6['vs']/n:.3f}** | **{s6['ls']/n:.3f}** | **{best3(s6['ts'], s6['vs'], s6['ls'])}** |")
    w(f"| | CODE | **{s6['tc']/n:.3f}** | **{s6['vc']/n:.3f}** | **{s6['lc']/n:.3f}** | **{best3(s6['tc'], s6['vc'], s6['lc'])}** |")
    w("")

    # ─── Debiasing summary ───────────────────────────────────────────
    w("### Enrollment Debiasing Summary")
    w("")
    w("| Project | Metric | TransArc | V45 | LLM | Best |")
    w("|:--|:--|:---:|:---:|:---:|:--|")
    sd = {"std_t": 0, "std_v": 0, "std_l": 0,
          "idf_t": 0, "idf_v": 0, "idf_l": 0,
          "macro_t": 0, "macro_v": 0, "macro_l": 0,
          "pdr_t": 0, "pdr_v": 0, "pdr_l": 0,
          "acf1_t": 0, "acf1_v": 0, "acf1_l": 0}
    for proj in PROJECTS:
        d = all_debias[proj]
        n4d = all_n4[proj]
        rows = [
            ("Std F1", d["std"]["t"], d["std"]["v"], d["std"]["l"]),
            ("IDF-F1", d["idf"]["t"], d["idf"]["v"], d["idf"]["l"]),
            ("Macro-F1", d["macro"]["t"], d["macro"]["v"], d["macro"]["l"]),
            ("PDR-F1", d["pdr"]["t"], d["pdr"]["v"], d["pdr"]["l"]),
            ("ACF1", n4d["t"]["acf1"], n4d["v"]["acf1"], n4d["l"]["acf1"]),
        ]
        for i, (label, t, v, l) in enumerate(rows):
            proj_col = proj if i == 0 else ""
            w(f"| {proj_col} | {label} | {t:.3f} | {v:.3f} | {l:.3f} | {best3(t, v, l)} |")
            sd[f"{label.lower().replace('-', '_').replace(' ', '_')}_t"] = sd.get(f"{label.lower().replace('-', '_').replace(' ', '_')}_t", 0)

    # Compute debiasing averages
    w("")
    w("**Averages across projects:**")
    w("")
    w("| Metric | TransArc | V45 | LLM | Best |")
    w("|:--|:---:|:---:|:---:|:--|")
    for metric_key, metric_label in [("std", "Standard F1"), ("idf", "IDF-Weighted"), ("macro", "Component-Macro"), ("pdr", "PDR")]:
        t_avg = sum(all_debias[p][metric_key]["t"] for p in PROJECTS) / n
        v_avg = sum(all_debias[p][metric_key]["v"] for p in PROJECTS) / n
        l_avg = sum(all_debias[p][metric_key]["l"] for p in PROJECTS) / n
        w(f"| {metric_label} | {t_avg:.3f} | {v_avg:.3f} | {l_avg:.3f} | {best3(t_avg, v_avg, l_avg)} |")
    t_avg_acf1 = s4["t"] / n; v_avg_acf1 = s4["v"] / n; l_avg_acf1 = s4["l"] / n
    w(f"| ACF1 | {t_avg_acf1:.3f} | {v_avg_acf1:.3f} | {l_avg_acf1:.3f} | {best3(t_avg_acf1, v_avg_acf1, l_avg_acf1)} |")
    w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Grand Summary
    # ═══════════════════════════════════════════════════════════════════════
    w("---")
    w("")
    w("## Grand Summary")
    w("")

    # Compute all averages
    avgs = {}
    avgs["f1_sam"] = (sums["t_sam"]/n, sums["v_sam"]/n, sums["l_sam"]/n)
    avgs["f1_code"] = (sums["t_code"]/n, sums["v_code"]/n, sums["l_code"]/n)
    avgs["n1_sam"] = (s1["ts"]/n, s1["vs"]/n, s1["ls"]/n)
    avgs["n1_code"] = (s1["tc"]/n, s1["vc"]/n, s1["lc"]/n)
    avgs["n2_sam"] = (s2["ts"]/n, s2["vs"]/n, s2["ls"]/n)
    avgs["n2_code"] = (s2["tc"]/n, s2["vc"]/n, s2["lc"]/n)
    avgs["n3_sam"] = (s3["ts"]/n, s3["vs"]/n, s3["ls"]/n)
    avgs["n3_code"] = (s3["tc"]/n, s3["vc"]/n, s3["lc"]/n)
    avgs["n4"] = (s4["t"]/n, s4["v"]/n, s4["l"]/n)
    avgs["n5"] = (s5["t"]/n, s5["v"]/n, s5["l"]/n)
    avgs["n6_sam"] = (s6["ts"]/n, s6["vs"]/n, s6["ls"]/n)
    avgs["n6_code"] = (s6["tc"]/n, s6["vc"]/n, s6["lc"]/n)

    # Debiasing averages
    for mk in ["idf", "macro", "pdr"]:
        t_a = sum(all_debias[p][mk]["t"] for p in PROJECTS) / n
        v_a = sum(all_debias[p][mk]["v"] for p in PROJECTS) / n
        l_a = sum(all_debias[p][mk]["l"] for p in PROJECTS) / n
        avgs[mk] = (t_a, v_a, l_a)

    w("| Metric | Level | TransArc | V45 | LLM | Best | V45-T Δ | LLM-T Δ |")
    w("|:--|:--|:---:|:---:|:---:|:--|:---:|:---:|")

    rows = [
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

    for label, level, key in rows:
        t, v, l = avgs[key]
        b = best3(t, v, l)
        w(f"| {label} | {level} | {t:.3f} | {v:.3f} | {l:.3f} | {b} | {v-t:+.3f} | {l-t:+.3f} |")
    w("")

    # ─── Win/Loss table ──────────────────────────────────────────────
    w("### Per-Project Win Count (across all metrics)")
    w("")
    w("Count of (metric, level) combinations where each system scores highest:")
    w("")
    wins = {"TransArc": 0, "V45": 0, "LLM": 0}
    per_proj_wins = {p: {"TransArc": 0, "V45": 0, "LLM": 0} for p in PROJECTS}

    # Collect per-project per-metric winner
    for proj in PROJECTS:
        entries = [
            all_std[proj]["t_sam"][2], all_std[proj]["v_sam"][2], all_std[proj]["l_sam"][2],
            all_std[proj]["t_code"][2], all_std[proj]["v_code"][2], all_std[proj]["l_code"][2],
            all_n1[proj]["t"]["mcc"], all_n1[proj]["v"]["mcc"], all_n1[proj]["l"]["mcc"],
            all_n1c[proj]["t"]["mcc"], all_n1c[proj]["v"]["mcc"], all_n1c[proj]["l"]["mcc"],
            all_n2[proj]["t"]["emr"], all_n2[proj]["v"]["emr"], all_n2[proj]["l"]["emr"],
            all_n2c[proj]["t"]["emr"], all_n2c[proj]["v"]["emr"], all_n2c[proj]["l"]["emr"],
            all_n3[proj]["t"]["map"], all_n3[proj]["v"]["map"], all_n3[proj]["l"]["map"],
            all_n3c[proj]["t"]["map"], all_n3c[proj]["v"]["map"], all_n3c[proj]["l"]["map"],
            all_n4[proj]["t"]["acf1"], all_n4[proj]["v"]["acf1"], all_n4[proj]["l"]["acf1"],
            all_n5[proj]["t"], all_n5[proj]["v"], all_n5[proj]["l"],
            all_n6s[proj]["t"]["hus"], all_n6s[proj]["v"]["hus"], all_n6s[proj]["l"]["hus"],
            all_n6c[proj]["t"]["hus"], all_n6c[proj]["v"]["hus"], all_n6c[proj]["l"]["hus"],
        ]
        # Each group of 3 = (t, v, l) for one metric
        for i in range(0, len(entries), 3):
            t_val, v_val, l_val = entries[i], entries[i+1], entries[i+2]
            b = best3(t_val, v_val, l_val)
            wins[b] += 1
            per_proj_wins[proj][b] += 1

    w("| Project | TransArc | V45 | LLM |")
    w("|:--|:---:|:---:|:---:|")
    for proj in PROJECTS:
        pw = per_proj_wins[proj]
        w(f"| {proj} | {pw['TransArc']} | {pw['V45']} | {pw['LLM']} |")
    w(f"| **Total** | **{wins['TransArc']}** | **{wins['V45']}** | **{wins['LLM']}** |")
    w("")

    # ─── Key Findings ────────────────────────────────────────────────
    w("### Key Findings")
    w("")

    # Determine overall rankings
    # Count which system is best on average across all metrics
    avg_rankings = {"TransArc": 0, "V45": 0, "LLM": 0}
    for key in avgs:
        t, v, l = avgs[key]
        b = best3(t, v, l)
        avg_rankings[b] += 1

    w(f"1. **Overall winner: {max(avg_rankings, key=avg_rankings.get)}** — "
      f"best on {max(avg_rankings.values())}/{len(avgs)} aggregate metrics "
      f"(TransArc: {avg_rankings['TransArc']}, V45: {avg_rankings['V45']}, LLM: {avg_rankings['LLM']})")
    w("")

    # Find where LLM beats TransArc
    llm_beats_transarc = []
    llm_loses_transarc = []
    for label, level, key in rows:
        t, v, l = avgs[key]
        clean_label = label.replace("**", "")
        if l > t + 0.005:
            llm_beats_transarc.append(f"{clean_label} ({level}): {l:.3f} vs {t:.3f}")
        elif t > l + 0.005:
            llm_loses_transarc.append(f"{clean_label} ({level}): {t:.3f} vs {l:.3f}")

    w("2. **LLM vs TransArc:**")
    if llm_beats_transarc:
        w(f"   - LLM wins on {len(llm_beats_transarc)} metrics: {'; '.join(llm_beats_transarc[:3])}")
    if llm_loses_transarc:
        w(f"   - TransArc wins on {len(llm_loses_transarc)} metrics: {'; '.join(llm_loses_transarc[:3])}")
    w("")

    # Find most discriminating metric
    max_spread_key = max(avgs, key=lambda k: max(avgs[k]) - min(avgs[k]))
    t, v, l = avgs[max_spread_key]
    spread = max(t, v, l) - min(t, v, l)
    w(f"3. **Most discriminating metric: {max_spread_key}** — "
      f"spread of {spread:.3f} between best and worst system")
    w("")

    # Debiasing impact
    std_t, std_v, std_l = avgs["f1_code"]
    pdr_t, pdr_v, pdr_l = avgs["pdr"]
    w(f"4. **Debiasing impact:** PDR F1 deflates all systems vs Standard F1:")
    w(f"   - TransArc: {std_t:.3f} → {pdr_t:.3f} ({pdr_t-std_t:+.3f})")
    w(f"   - V45: {std_v:.3f} → {pdr_v:.3f} ({pdr_v-std_v:+.3f})")
    w(f"   - LLM: {std_l:.3f} → {pdr_l:.3f} ({pdr_l-std_l:+.3f})")
    w("")

    # Per-project insights
    w("5. **Per-project breakdown:**")
    for proj in PROJECTS:
        pw = per_proj_wins[proj]
        dom = max(pw, key=pw.get)
        w(f"   - {proj}: {dom} dominates ({pw[dom]}/{sum(pw.values())} metrics)")
    w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 three_system_comparison.py")
    w("# Output: THREE_SYSTEM_COMPARISON.md")
    w("```")
    w("")

    # ─── Write output ────────────────────────────────────────────────
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWritten to {OUTPUT_MD}")

    # ─── Console summary ─────────────────────────────────────────────
    print("\n" + "=" * 85)
    print("GRAND SUMMARY: Three-System Comparison")
    print("=" * 85)
    print(f"\n{'Metric':<25} {'Level':<6} {'TransArc':>10} {'V45':>10} {'LLM':>10} {'Best':<10}")
    print("-" * 75)
    for label, level, key in rows:
        clean = label.replace("**", "")
        t, v, l = avgs[key]
        b = best3(t, v, l)
        print(f"{clean:<25} {level:<6} {t:>10.3f} {v:>10.3f} {l:>10.3f} {b:<10}")

    print(f"\nPer-project wins: TransArc={wins['TransArc']}, V45={wins['V45']}, LLM={wins['LLM']}")


if __name__ == "__main__":
    main()
