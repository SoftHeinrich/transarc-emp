#!/usr/bin/env python3
"""
Holistic Evaluation Metrics Analysis

Problems with current enrollment-based P/R/F1:
1. Enrollment inflation: one directory entry → hundreds of file-level links
2. Non-uniform weighting: JabRef/logic (972 files) has 972x the influence of globals (1 file)
3. Granularity mismatch: annotators wrote directory-level, evaluation is file-level
4. Cascade blindness: SAM-CODE metrics don't reflect downstream SAD-CODE impact

This script computes alternative metrics and compares them to current ones.
"""

import math
from collections import defaultdict
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw,
    load_gs_sad_code_enrolled, load_gs_sad_code_raw,
    load_result_sad_code,
    load_result_sam_code_standalone,
    load_transarc_intermediate_sam_code,
    load_transarc_intermediate_maps,
    load_model_element_names, load_text,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/HOLISTIC_METRICS.md")


def f1(p, r):
    return 2 * p * r / (p + r) if (p + r) > 0 else 0


def analyze_sam_code(proj):
    """Compute all metric variants for SAM-CODE."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)

    gs_raw = load_gs_sam_code_raw(proj)
    gs_enrolled = enroll_gold_standard(gs_raw, code_model)
    result = load_result_sam_code_standalone(proj)
    internal = load_transarc_intermediate_sam_code(proj)

    # ─── M1: Current enrolled file-level P/R/F1 (micro) ─────────────
    p1, r1, f1_1, tp1, fp1, fn1 = calc_metrics(gs_enrolled, result)

    # ─── M2: Raw entry-level (pre-enrollment) P/R/F1 ────────────────
    # Match result links back to raw gold entries.
    # A raw entry (M, dir/) is considered a TP if the result contains
    # at least one (M, file) where file starts with dir.
    # A raw entry (M, file) is TP if (M, file) is in result.
    # FPs: result links that don't match any raw entry.

    raw_tps = set()
    raw_fns = set()
    result_explained = set()  # result links that match a raw gold entry

    for (m, path) in gs_raw:
        if path.endswith("/"):
            # Directory entry: TP if any file in result matches
            matched = False
            for (rm, rc) in result:
                if rm == m and rc.startswith(path):
                    matched = True
                    result_explained.add((rm, rc))
            if matched:
                raw_tps.add((m, path))
            else:
                raw_fns.add((m, path))
        else:
            # File entry: exact match
            if (m, path) in result:
                raw_tps.add((m, path))
                result_explained.add((m, path))
            else:
                raw_fns.add((m, path))

    raw_fps = result - result_explained  # result links not explained by any raw entry
    # But we need to be careful: a raw directory entry "explains" many result links.
    # Raw FPs = unique raw entries in result not matching any gold entry.
    # Group result FPs by model element + directory to count unique "raw-level" FPs.
    raw_fp_entries = set()
    for (m, c) in raw_fps:
        # Find what directory this file belongs to (use first 3 path segments as approx)
        parts = c.split("/")
        if len(parts) >= 3:
            dir_prefix = "/".join(parts[:3]) + "/"
        else:
            dir_prefix = c
        raw_fp_entries.add((m, dir_prefix))

    p2 = len(raw_tps) / (len(raw_tps) + len(raw_fp_entries)) if (len(raw_tps) + len(raw_fp_entries)) > 0 else 0
    r2 = len(raw_tps) / len(gs_raw) if gs_raw else 0
    f1_2 = f1(p2, r2)

    # ─── M3: Macro-averaged per-model-element P/R/F1 ────────────────
    # Compute P/R/F1 per model element, then average.

    all_model_ids = set(m for m, _ in gs_enrolled) | set(m for m, _ in result)
    per_me_metrics = []

    for m in all_model_ids:
        gold_m = set(c for mm, c in gs_enrolled if mm == m)
        result_m = set(c for mm, c in result if mm == m)
        if not gold_m and not result_m:
            continue
        tp_m = gold_m & result_m
        fp_m = result_m - gold_m
        fn_m = gold_m - result_m
        p_m = len(tp_m) / len(result_m) if result_m else 0
        r_m = len(tp_m) / len(gold_m) if gold_m else 0
        f1_m = f1(p_m, r_m)
        per_me_metrics.append({
            "id": m, "name": names.get(m, m),
            "gold": len(gold_m), "result": len(result_m),
            "tp": len(tp_m), "fp": len(fp_m), "fn": len(fn_m),
            "p": p_m, "r": r_m, "f1": f1_m,
        })

    macro_p = sum(d["p"] for d in per_me_metrics) / len(per_me_metrics) if per_me_metrics else 0
    macro_r = sum(d["r"] for d in per_me_metrics) / len(per_me_metrics) if per_me_metrics else 0
    macro_f1 = sum(d["f1"] for d in per_me_metrics) / len(per_me_metrics) if per_me_metrics else 0

    # ─── M4: Enrollment-weighted P/R/F1 ─────────────────────────────
    # Weight each enrolled link inversely by its enrollment factor.
    # A TP from a 972-file directory counts 1/972; a single-file TP counts 1.

    # Build map: enrolled file -> raw entry -> enrollment count
    raw_to_enrolled_count = {}
    for (m, path) in gs_raw:
        if path.endswith("/"):
            count = sum(1 for f in code_model if f.startswith(path))
        else:
            count = 1
        raw_to_enrolled_count[(m, path)] = max(count, 1)

    # Map each enrolled gold link to its weight
    enrolled_weights = {}
    for (m, c) in gs_enrolled:
        # Find which raw entry this came from
        for (rm, rp) in gs_raw:
            if rm == m:
                if rp.endswith("/") and c.startswith(rp):
                    enrolled_weights[(m, c)] = 1.0 / raw_to_enrolled_count[(rm, rp)]
                    break
                elif rp == c:
                    enrolled_weights[(m, c)] = 1.0
                    break

    # Weighted TP/FP/FN
    weighted_tp = sum(enrolled_weights.get((m, c), 1.0) for (m, c) in (gs_enrolled & result))
    weighted_fn = sum(enrolled_weights.get((m, c), 1.0) for (m, c) in (gs_enrolled - result))
    # For FPs, weight = 1/estimated enrollment of target directory
    weighted_fp = 0
    for (m, c) in (result - gs_enrolled):
        # Find if this matches a directory pattern of the model element
        # Approximate: use 1.0 (conservative)
        weighted_fp += 1.0  # FPs don't have enrollment weights; count as-is

    # Normalize: total weighted gold = sum of weights for all gold entries
    total_weighted_gold = sum(enrolled_weights.get(k, 1.0) for k in gs_enrolled)
    total_weighted_result = weighted_tp + weighted_fp

    p4 = weighted_tp / total_weighted_result if total_weighted_result > 0 else 0
    r4 = weighted_tp / total_weighted_gold if total_weighted_gold > 0 else 0
    f1_4 = f1(p4, r4)

    # ─── M5: Component coverage metrics ─────────────────────────────
    # For each model element: binary (any correct file?) and threshold (>50% recall?)
    n_components = len(per_me_metrics)
    n_any_tp = sum(1 for d in per_me_metrics if d["tp"] > 0)
    n_perfect = sum(1 for d in per_me_metrics if d["gold"] > 0 and d["tp"] == d["gold"] and d["fp"] == 0)
    n_recall_50 = sum(1 for d in per_me_metrics if d["r"] >= 0.5)
    n_recall_90 = sum(1 for d in per_me_metrics if d["r"] >= 0.9)
    n_prec_90 = sum(1 for d in per_me_metrics if d["p"] >= 0.9)
    n_f1_90 = sum(1 for d in per_me_metrics if d["f1"] >= 0.9)

    # ─── M6: Cascade-weighted metrics (for TransArc context) ────────
    # Weight each SAM-CODE link by the number of SAD-SAM sentences for that model element
    # This captures downstream SAD-CODE impact.

    gs_sad_sam = load_gs_sad_sam(proj)
    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(proj)

    # Count sentences per model element in intermediate SAD-SAM
    sents_per_model = defaultdict(int)
    for m, sents in model_to_sents.items():
        sents_per_model[m] = len(sents)

    # Weight each internal SAM-CODE link by sentence count
    gs_sam_code_enrolled = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
    int_sam_code = internal

    cascade_tp_weight = 0
    cascade_fp_weight = 0
    cascade_fn_weight = 0

    for (m, c) in int_sam_code:
        w = sents_per_model.get(m, 0)
        if (m, c) in gs_sam_code_enrolled:
            cascade_tp_weight += w
        else:
            cascade_fp_weight += w

    for (m, c) in (gs_sam_code_enrolled - int_sam_code):
        w = sents_per_model.get(m, 0)
        cascade_fn_weight += w

    total_cascade_result = cascade_tp_weight + cascade_fp_weight
    total_cascade_gold = cascade_tp_weight + cascade_fn_weight

    p6 = cascade_tp_weight / total_cascade_result if total_cascade_result > 0 else 0
    r6 = cascade_tp_weight / total_cascade_gold if total_cascade_gold > 0 else 0
    f1_6 = f1(p6, r6)

    return {
        "M1_micro": {"p": p1, "r": r1, "f1": f1_1, "tp": tp1, "fp": fp1, "fn": fn1},
        "M2_raw": {"p": p2, "r": r2, "f1": f1_2,
                    "tp": len(raw_tps), "fp": len(raw_fp_entries), "fn": len(raw_fns),
                    "raw_gold": len(gs_raw)},
        "M3_macro": {"p": macro_p, "r": macro_r, "f1": macro_f1,
                     "per_me": per_me_metrics},
        "M4_weighted": {"p": p4, "r": r4, "f1": f1_4,
                        "weighted_tp": weighted_tp, "weighted_fp": weighted_fp,
                        "weighted_fn": weighted_fn,
                        "total_weighted_gold": total_weighted_gold},
        "M5_coverage": {"n_components": n_components,
                        "any_tp": n_any_tp, "perfect": n_perfect,
                        "recall_50": n_recall_50, "recall_90": n_recall_90,
                        "prec_90": n_prec_90, "f1_90": n_f1_90},
        "M6_cascade": {"p": p6, "r": r6, "f1": f1_6,
                       "cascade_tp": cascade_tp_weight,
                       "cascade_fp": cascade_fp_weight,
                       "cascade_fn": cascade_fn_weight},
    }


def analyze_sad_code(proj):
    """Compute metric variants for SAD-CODE (TransArc)."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)

    gs_raw = load_gs_sad_code_raw(proj)
    gs_enrolled = load_gs_sad_code_enrolled(proj, code_model)
    result = load_result_sad_code(proj)

    # M1: Current enrolled micro P/R/F1
    p1, r1, f1_1, tp1, fp1, fn1 = calc_metrics(gs_enrolled, result)

    # M2: Raw entry-level
    raw_tps = set()
    raw_fns = set()
    result_explained = set()

    for (s, path) in gs_raw:
        if path.endswith("/"):
            matched = False
            for (rs, rc) in result:
                if rs == s and rc.startswith(path):
                    matched = True
                    result_explained.add((rs, rc))
            if matched:
                raw_tps.add((s, path))
            else:
                raw_fns.add((s, path))
        else:
            if (s, path) in result:
                raw_tps.add((s, path))
                result_explained.add((s, path))
            else:
                raw_fns.add((s, path))

    raw_fps = result - result_explained
    raw_fp_entries = set()
    for (s, c) in raw_fps:
        parts = c.split("/")
        if len(parts) >= 3:
            dir_prefix = "/".join(parts[:3]) + "/"
        else:
            dir_prefix = c
        raw_fp_entries.add((s, dir_prefix))

    p2 = len(raw_tps) / (len(raw_tps) + len(raw_fp_entries)) if (len(raw_tps) + len(raw_fp_entries)) > 0 else 0
    r2 = len(raw_tps) / len(gs_raw) if gs_raw else 0
    f1_2 = f1(p2, r2)

    # M3: Macro-averaged per-sentence P/R/F1
    all_sents = set(s for s, _ in gs_enrolled) | set(s for s, _ in result)
    per_sent_metrics = []

    for s in all_sents:
        gold_s = set(c for ss, c in gs_enrolled if ss == s)
        result_s = set(c for ss, c in result if ss == s)
        if not gold_s and not result_s:
            continue
        tp_s = gold_s & result_s
        fp_s = result_s - gold_s
        fn_s = gold_s - result_s
        p_s = len(tp_s) / len(result_s) if result_s else 0
        r_s = len(tp_s) / len(gold_s) if gold_s else 0
        f1_s = f1(p_s, r_s)
        per_sent_metrics.append({
            "sent": s, "gold": len(gold_s), "result": len(result_s),
            "tp": len(tp_s), "fp": len(fp_s), "fn": len(fn_s),
            "p": p_s, "r": r_s, "f1": f1_s,
        })

    macro_p = sum(d["p"] for d in per_sent_metrics) / len(per_sent_metrics) if per_sent_metrics else 0
    macro_r = sum(d["r"] for d in per_sent_metrics) / len(per_sent_metrics) if per_sent_metrics else 0
    macro_f1 = sum(d["f1"] for d in per_sent_metrics) / len(per_sent_metrics) if per_sent_metrics else 0

    # M4: Enrollment-weighted
    raw_to_enrolled_count = {}
    for (s, path) in gs_raw:
        if path.endswith("/"):
            count = sum(1 for f in code_model if f.startswith(path))
        else:
            count = 1
        raw_to_enrolled_count[(s, path)] = max(count, 1)

    enrolled_weights = {}
    for (s, c) in gs_enrolled:
        for (rs, rp) in gs_raw:
            if rs == s:
                if rp.endswith("/") and c.startswith(rp):
                    enrolled_weights[(s, c)] = 1.0 / raw_to_enrolled_count[(rs, rp)]
                    break
                elif rp == c:
                    enrolled_weights[(s, c)] = 1.0
                    break

    weighted_tp = sum(enrolled_weights.get(k, 1.0) for k in (gs_enrolled & result))
    weighted_fn = sum(enrolled_weights.get(k, 1.0) for k in (gs_enrolled - result))
    weighted_fp = len(result - gs_enrolled) * 1.0

    total_weighted_gold = sum(enrolled_weights.get(k, 1.0) for k in gs_enrolled)
    total_weighted_result = weighted_tp + weighted_fp

    p4 = weighted_tp / total_weighted_result if total_weighted_result > 0 else 0
    r4 = weighted_tp / total_weighted_gold if total_weighted_gold > 0 else 0
    f1_4 = f1(p4, r4)

    return {
        "M1_micro": {"p": p1, "r": r1, "f1": f1_1, "tp": tp1, "fp": fp1, "fn": fn1},
        "M2_raw": {"p": p2, "r": r2, "f1": f1_2,
                    "tp": len(raw_tps), "fp": len(raw_fp_entries), "fn": len(raw_fns),
                    "raw_gold": len(gs_raw)},
        "M3_macro": {"p": macro_p, "r": macro_r, "f1": macro_f1,
                     "n_sents": len(per_sent_metrics),
                     "per_sent": per_sent_metrics},
        "M4_weighted": {"p": p4, "r": r4, "f1": f1_4},
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# Holistic Evaluation Metrics: Beyond Enrollment-Based P/R/F1")
    out()
    out("## Problems with Current Evaluation")
    out()
    out("The current evaluation computes micro-averaged P/R/F1 on enrolled (file-level) gold standards.")
    out("This creates systematic distortions:")
    out()
    out("1. **Enrollment inflation**: A single directory entry `src/main/java/org/jabref/logic/` expands")
    out("   to 972 file-level links. Getting one directory right/wrong shifts metrics by 972 units.")
    out("2. **Non-uniform weighting**: JabRef/logic (972 files) has 972× the influence of globals (1 file).")
    out("   A single error in `logic` matters 972× more than an error in `globals`.")
    out("3. **Granularity mismatch**: Annotators wrote directory-level entries, but evaluation is file-level.")
    out("   The tool is really doing component→directory mapping, but we measure file-level accuracy.")
    out("4. **Cascade blindness**: SAM-CODE P/R/F1 ignores downstream impact. A SAM-CODE FP for a model")
    out("   element with 20 SAD-SAM sentences causes 20× more SAD-CODE FPs than one with 1 sentence.")
    out()

    # ═══ SAM-CODE METRICS COMPARISON ═════════════════════════════════

    out("## SAM-CODE Metric Comparison")
    out()

    sam_code_results = {}
    for proj in PROJECTS:
        sam_code_results[proj] = analyze_sam_code(proj)

    # M1 vs M2 vs M3 vs M4
    out("### M1: Current Micro-Averaged (Enrolled) vs M2: Raw Entry-Level vs M3: Macro-Averaged vs M4: Enrollment-Weighted")
    out()
    out("| Project | M1 Micro P | M1 R | M1 F1 | M2 Raw P | M2 R | M2 F1 | M3 Macro P | M3 R | M3 F1 | M4 Wt P | M4 R | M4 F1 |")
    out("|---------|----------|------|-------|---------|------|-------|-----------|------|-------|--------|------|-------|")

    for proj in PROJECTS:
        r = sam_code_results[proj]
        m1 = r["M1_micro"]
        m2 = r["M2_raw"]
        m3 = r["M3_macro"]
        m4 = r["M4_weighted"]
        out(f"| {proj} | {m1['p']:.3f} | {m1['r']:.3f} | {m1['f1']:.3f} | "
            f"{m2['p']:.3f} | {m2['r']:.3f} | {m2['f1']:.3f} | "
            f"{m3['p']:.3f} | {m3['r']:.3f} | {m3['f1']:.3f} | "
            f"{m4['p']:.3f} | {m4['r']:.3f} | {m4['f1']:.3f} |")

    out()

    # Show how enrollment inflates
    out("### Enrollment Inflation: Raw vs Enrolled Gold Size")
    out()
    out("| Project | Raw Gold Entries | Enrolled Gold Links | Inflation Factor | M1 F1 (Enrolled) | M2 F1 (Raw) | Δ |")
    out("|---------|----------------|--------------------|-----------------|-----------------|-----------|----|")

    for proj in PROJECTS:
        r = sam_code_results[proj]
        raw_n = r["M2_raw"]["raw_gold"]
        enrolled_n = r["M1_micro"]["tp"] + r["M1_micro"]["fn"]
        factor = enrolled_n / raw_n if raw_n > 0 else 0
        delta = r["M2_raw"]["f1"] - r["M1_micro"]["f1"]
        out(f"| {proj} | {raw_n} | {enrolled_n} | {factor:.1f}x | "
            f"{r['M1_micro']['f1']:.3f} | {r['M2_raw']['f1']:.3f} | {delta:+.3f} |")

    out()

    # M5: Component coverage
    out("### M5: Component Coverage Metrics")
    out()
    out("| Project | Components | Any TP | Perfect | R≥50% | R≥90% | P≥90% | F1≥90% |")
    out("|---------|-----------|--------|---------|-------|-------|-------|--------|")

    for proj in PROJECTS:
        m5 = sam_code_results[proj]["M5_coverage"]
        n = m5["n_components"]
        out(f"| {proj} | {n} | {m5['any_tp']}/{n} ({m5['any_tp']/n*100:.0f}%) | "
            f"{m5['perfect']}/{n} ({m5['perfect']/n*100:.0f}%) | "
            f"{m5['recall_50']}/{n} ({m5['recall_50']/n*100:.0f}%) | "
            f"{m5['recall_90']}/{n} ({m5['recall_90']/n*100:.0f}%) | "
            f"{m5['prec_90']}/{n} ({m5['prec_90']/n*100:.0f}%) | "
            f"{m5['f1_90']}/{n} ({m5['f1_90']/n*100:.0f}%) |")

    out()

    # M6: Cascade-weighted
    out("### M6: Cascade-Weighted SAM-CODE Metrics (weighted by downstream sentence count)")
    out()
    out("Each SAM-CODE link is weighted by the number of SAD-SAM sentences for its model element,")
    out("reflecting its actual impact on the TransArc output.")
    out()
    out("| Project | M1 Micro F1 | M6 Cascade P | M6 R | M6 F1 | Δ F1 |")
    out("|---------|-----------|-----------|------|-------|------|")

    for proj in PROJECTS:
        r = sam_code_results[proj]
        m1 = r["M1_micro"]
        m6 = r["M6_cascade"]
        delta = m6["f1"] - m1["f1"]
        out(f"| {proj} | {m1['f1']:.3f} | {m6['p']:.3f} | {m6['r']:.3f} | {m6['f1']:.3f} | {delta:+.3f} |")

    out()

    # ═══ SAD-CODE METRICS COMPARISON ═════════════════════════════════

    out("## SAD-CODE (TransArc) Metric Comparison")
    out()

    sad_code_results = {}
    for proj in PROJECTS:
        sad_code_results[proj] = analyze_sad_code(proj)

    out("### M1: Current Micro (Enrolled) vs M2: Raw Entry-Level vs M3: Macro (per-sentence) vs M4: Enrollment-Weighted")
    out()
    out("| Project | M1 Micro P | M1 R | M1 F1 | M2 Raw P | M2 R | M2 F1 | M3 Macro P | M3 R | M3 F1 | M4 Wt P | M4 R | M4 F1 |")
    out("|---------|----------|------|-------|---------|------|-------|-----------|------|-------|--------|------|-------|")

    for proj in PROJECTS:
        r = sad_code_results[proj]
        m1 = r["M1_micro"]
        m2 = r["M2_raw"]
        m3 = r["M3_macro"]
        m4 = r["M4_weighted"]
        out(f"| {proj} | {m1['p']:.3f} | {m1['r']:.3f} | {m1['f1']:.3f} | "
            f"{m2['p']:.3f} | {m2['r']:.3f} | {m2['f1']:.3f} | "
            f"{m3['p']:.3f} | {m3['r']:.3f} | {m3['f1']:.3f} | "
            f"{m4['p']:.3f} | {m4['r']:.3f} | {m4['f1']:.3f} |")

    out()

    # Enrollment inflation for SAD-CODE
    out("### SAD-CODE Enrollment Inflation")
    out()
    out("| Project | Raw Gold | Enrolled Gold | Factor | M1 F1 | M2 F1 | Δ |")
    out("|---------|---------|-------------|--------|-------|-------|----|")

    for proj in PROJECTS:
        r = sad_code_results[proj]
        raw_n = r["M2_raw"]["raw_gold"]
        enrolled_n = r["M1_micro"]["tp"] + r["M1_micro"]["fn"]
        factor = enrolled_n / raw_n if raw_n > 0 else 0
        delta = r["M2_raw"]["f1"] - r["M1_micro"]["f1"]
        out(f"| {proj} | {raw_n} | {enrolled_n} | {factor:.1f}x | "
            f"{r['M1_micro']['f1']:.3f} | {r['M2_raw']['f1']:.3f} | {delta:+.3f} |")

    out()

    # ═══ PER-SENTENCE ANALYSIS FOR SAD-CODE ══════════════════════════

    out("### Per-Sentence Metric Distribution (SAD-CODE)")
    out()
    out("How do individual sentence-level metrics distribute? Are there sentences with")
    out("perfect results and sentences with zero recall?")
    out()

    for proj in PROJECTS:
        r = sad_code_results[proj]
        per_sent = r["M3_macro"]["per_sent"]
        if not per_sent:
            continue

        n = len(per_sent)
        n_perfect = sum(1 for d in per_sent if d["gold"] > 0 and d["tp"] == d["gold"] and d["fp"] == 0)
        n_zero_recall = sum(1 for d in per_sent if d["gold"] > 0 and d["r"] == 0)
        n_zero_prec = sum(1 for d in per_sent if d["result"] > 0 and d["p"] == 0)
        n_recall_100 = sum(1 for d in per_sent if d["gold"] > 0 and d["r"] == 1.0)
        n_with_gold = sum(1 for d in per_sent if d["gold"] > 0)
        n_with_result = sum(1 for d in per_sent if d["result"] > 0)

        out(f"**{proj}** ({n} sentences involved):")
        out(f"- Perfect (TP=Gold, FP=0): {n_perfect}/{n_with_gold} ({n_perfect/n_with_gold*100:.0f}%)")
        out(f"- Recall=100%: {n_recall_100}/{n_with_gold} ({n_recall_100/n_with_gold*100:.0f}%)")
        out(f"- Recall=0% (all gold links missed): {n_zero_recall}/{n_with_gold} ({n_zero_recall/n_with_gold*100:.0f}%)")
        if n_with_result > 0:
            out(f"- Precision=0% (all result links wrong): {n_zero_prec}/{n_with_result} ({n_zero_prec/n_with_result*100:.0f}%)")

        # Show worst sentences
        worst = sorted([d for d in per_sent if d["gold"] > 0], key=lambda d: d["f1"])
        if worst:
            texts = load_text(proj)
            out(f"- Worst 3 sentences by F1:")
            for d in worst[:3]:
                st = texts.get(d["sent"], "?")[:70]
                out(f"  - S{d['sent']}: F1={d['f1']:.3f} (TP={d['tp']}, FP={d['fp']}, FN={d['fn']}, Gold={d['gold']}) \"{st}...\"")
        out()

    # ═══ SUMMARY: WHICH METRICS REVEAL WHAT ══════════════════════════

    out("## Summary: What Each Metric Reveals")
    out()
    out("| Metric | What It Measures | What It Hides | Best For |")
    out("|--------|-----------------|--------------|----------|")
    out("| **M1**: Micro P/R/F1 (enrolled) | File-level accuracy after enrollment | Large-component bias; one directory dominates | Comparing to prior work (standard metric) |")
    out("| **M2**: Raw entry-level P/R/F1 | Accuracy at annotation granularity | File-level errors within correct directories | Understanding annotator-level performance |")
    out("| **M3**: Macro-averaged P/R/F1 | Equal weight per model element (SAM-CODE) or per sentence (SAD-CODE) | Overall volume of correct links | Identifying weak spots; fairness across elements |")
    out("| **M4**: Enrollment-weighted P/R/F1 | Each raw gold entry counts equally regardless of expansion | Absolute file-level counts | Removing enrollment bias from P/R/F1 |")
    out("| **M5**: Component coverage | What fraction of components are well-served | Severity of errors per component | Quick assessment of breadth |")
    out("| **M6**: Cascade-weighted P/R/F1 | Downstream TransArc impact per SAM-CODE link | Standalone SAM-CODE quality | Optimizing for end-to-end pipeline performance |")
    out()

    out("### Key Revelations from Alternative Metrics")
    out()

    # Compare where metrics diverge most
    out("**Where metrics diverge most:**")
    out()
    for proj in PROJECTS:
        sc = sam_code_results[proj]
        m1_f1 = sc["M1_micro"]["f1"]
        m2_f1 = sc["M2_raw"]["f1"]
        m3_f1 = sc["M3_macro"]["f1"]
        metrics = {"M1_micro": m1_f1, "M2_raw": m2_f1, "M3_macro": m3_f1}
        max_m = max(metrics, key=metrics.get)
        min_m = min(metrics, key=metrics.get)
        spread = metrics[max_m] - metrics[min_m]
        if spread > 0.01:
            out(f"- **{proj} SAM-CODE**: M1={m1_f1:.3f}, M2={m2_f1:.3f}, M3={m3_f1:.3f} "
                f"(spread={spread:.3f}, highest={max_m}, lowest={min_m})")

    for proj in PROJECTS:
        sc = sad_code_results[proj]
        m1_f1 = sc["M1_micro"]["f1"]
        m2_f1 = sc["M2_raw"]["f1"]
        m3_f1 = sc["M3_macro"]["f1"]
        metrics = {"M1_micro": m1_f1, "M2_raw": m2_f1, "M3_macro": m3_f1}
        max_m = max(metrics, key=metrics.get)
        min_m = min(metrics, key=metrics.get)
        spread = metrics[max_m] - metrics[min_m]
        if spread > 0.05:
            out(f"- **{proj} SAD-CODE**: M1={m1_f1:.3f}, M2={m2_f1:.3f}, M3={m3_f1:.3f} "
                f"(spread={spread:.3f}, highest={max_m}, lowest={min_m})")

    out()

    out("### Recommendation")
    out()
    out("No single metric captures the full picture. We recommend reporting:")
    out()
    out("1. **M1 (micro enrolled)** for backward compatibility with prior work")
    out("2. **M3 (macro per-element/per-sentence)** to reveal performance on under-represented components")
    out("3. **M5 (component coverage)** for a quick breadth assessment")
    out("4. **M6 (cascade-weighted)** when evaluating SAM-CODE in the TransArc pipeline context")
    out()
    out("M2 (raw entry-level) and M4 (enrollment-weighted) are recommended when enrollment")
    out("inflation is suspected to bias results. For projects with >10x enrollment factor")
    out("(TeaStore, Teammates, BigBlueButton, JabRef), these metrics provide a more honest assessment.")
    out()

    # ─── Write report ────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
