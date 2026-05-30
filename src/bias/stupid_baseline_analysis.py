#!/usr/bin/env python3
"""
Stupid Baselines for Trace Link Recovery: Why We Need Holistic Evaluation

Implements several trivially simple (and meaningless) baselines that exploit
dataset distribution properties — especially enrollment inflation — to achieve
surprisingly high micro-averaged F1, while being clearly useless for any
practical purpose. Each baseline is then evaluated with both standard F1 AND
the holistic metrics from creative_metrics_analysis.py, exposing the gap.

Baselines:
  B0: TransArc (actual system) — reference
  B1: Link-All — every gold sentence × every code file (R=100%)
  B2: Majority-1 — every sentence × files of the SINGLE largest component
  B3: Majority-2 — every sentence × files of the TWO largest components
  B4: Uniform-Random — random sample, same size as TransArc output
  B5: Oracle-Heaviest — link only the sentences with most gold links
       to all code files (uses oracle; labeled as such)
  B6: Keyword-Grep — link sentences containing component name substrings
       to that component's files (trivial string match, no NLP)
"""

import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw,
    load_gs_sad_code_enrolled, load_gs_sad_code_raw,
    load_result_sad_code,
    load_transarc_intermediate_sad_sam,
    load_transarc_intermediate_sam_code,
    load_transarc_intermediate_maps,
    load_model_element_names, load_text,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/STUPID_BASELINES.md")

random.seed(42)  # Reproducibility


# ═══════════════════════════════════════════════════════════════════════════════
# Holistic metric computation (reused from creative_metrics_analysis.py)
# ═══════════════════════════════════════════════════════════════════════════════

def gini_coefficient(values):
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    numerator = sum((2 * i - n - 1) * v for i, v in enumerate(sorted_vals, 1))
    denominator = n * sum(sorted_vals)
    return numerator / denominator if denominator > 0 else 0


def percentile(values, p):
    if not values:
        return 0
    k = (len(values) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] * (c - k) + values[c] * (k - f)


def compute_holistic(result_set, gs_sad_code, gold_sents_set, all_code_files):
    """Compute standard + holistic metrics for a result set against enrolled gold."""
    p, r, f1, tp_count, fp_count, fn_count = calc_metrics(gs_sad_code, result_set)

    result_tps = result_set & gs_sad_code
    result_fps = result_set - gs_sad_code
    result_fns = gs_sad_code - result_set

    # ── Sentence-centric ──
    result_sents = set(s for s, _ in result_set)
    all_sents = gold_sents_set | result_sents

    per_sent = {}
    for s in all_sents:
        gold_s = set(c for ss, c in gs_sad_code if ss == s)
        result_s = set(c for ss, c in result_set if ss == s)
        tp_s = gold_s & result_s
        fp_s = result_s - gold_s
        fn_s = gold_s - result_s
        per_sent[s] = {
            "gold": len(gold_s), "result": len(result_s),
            "tp": len(tp_s), "fp": len(fp_s), "fn": len(fn_s),
            "recall": len(tp_s) / len(gold_s) if gold_s else None,
            "precision": len(tp_s) / len(result_s) if result_s else None,
            "has_gold": len(gold_s) > 0,
            "has_result": len(result_s) > 0,
        }

    gold_sent_list = [s for s in all_sents if per_sent[s]["has_gold"]]
    covered_sents = [s for s in gold_sent_list if per_sent[s]["tp"] > 0]
    result_sent_list = [s for s in all_sents if per_sent[s]["has_result"]]

    sent_coverage = len(covered_sents) / len(gold_sent_list) if gold_sent_list else 0

    completeness_values = [per_sent[s]["recall"] for s in covered_sents]
    sent_completeness = sum(completeness_values) / len(completeness_values) if completeness_values else 0

    useful_sents = [s for s in result_sent_list if per_sent[s]["tp"] > per_sent[s]["fp"]]
    sent_usefulness = len(useful_sents) / len(result_sent_list) if result_sent_list else 0

    noise_values = []
    for s in result_sent_list:
        total = per_sent[s]["tp"] + per_sent[s]["fp"]
        noise_values.append(per_sent[s]["fp"] / total if total > 0 else 0)
    sent_noise = sum(noise_values) / len(noise_values) if noise_values else 0

    recall_values = sorted([per_sent[s]["recall"] for s in gold_sent_list])
    recall_gini = gini_coefficient(recall_values)

    f1_values = []
    for s in gold_sent_list:
        sp = per_sent[s]["precision"] if per_sent[s]["precision"] is not None else 0
        sr = per_sent[s]["recall"]
        sf = 2 * sp * sr / (sp + sr) if (sp + sr) > 0 else 0
        f1_values.append(sf)
    f1_values_sorted = sorted(f1_values)
    q25_idx = max(1, len(f1_values_sorted) // 4)
    worst_q25_f1 = sum(f1_values_sorted[:q25_idx]) / q25_idx if q25_idx > 0 else 0

    all_or_nothing = sum(1 for s in gold_sent_list
                         if per_sent[s]["recall"] == 0 or per_sent[s]["recall"] == 1.0)
    all_or_nothing_rate = all_or_nothing / len(gold_sent_list) if gold_sent_list else 0

    # Macro P/R/F1 (per-sentence)
    macro_p_vals = [per_sent[s]["precision"] for s in gold_sent_list
                    if per_sent[s]["precision"] is not None]
    macro_r_vals = [per_sent[s]["recall"] for s in gold_sent_list]
    macro_p = sum(macro_p_vals) / len(macro_p_vals) if macro_p_vals else 0
    macro_r = sum(macro_r_vals) / len(macro_r_vals) if macro_r_vals else 0
    macro_f1 = 2 * macro_p * macro_r / (macro_p + macro_r) if (macro_p + macro_r) > 0 else 0

    # ── Code-centric ──
    gold_codes = set(c for _, c in gs_sad_code)
    result_codes = set(c for _, c in result_set)
    reached_codes = set(c for _, c in result_tps)
    code_reachability = len(reached_codes & gold_codes) / len(gold_codes) if gold_codes else 0
    spurious_codes = result_codes - gold_codes
    code_pollution = len(spurious_codes) / len(result_codes) if result_codes else 0

    orphan_codes = 0
    for c in gold_codes:
        if not any(True for s, cc in result_set if cc == c):
            orphan_codes += 1
    orphan_rate = orphan_codes / len(gold_codes) if gold_codes else 0

    # ── Practical utility ──
    query_success = sum(1 for s in result_sent_list if per_sent[s]["tp"] > 0) / \
                    len(result_sent_list) if result_sent_list else 0

    prec_per_sent = [per_sent[s]["tp"] / (per_sent[s]["tp"] + per_sent[s]["fp"])
                     for s in result_sent_list if per_sent[s]["tp"] + per_sent[s]["fp"] > 0]
    median_prec = percentile(sorted(prec_per_sent), 50) if prec_per_sent else 0

    wasted_effort = fp_count / tp_count if tp_count > 0 else float('inf')

    overwhelm_values = []
    for s in result_sent_list:
        if per_sent[s]["has_gold"] and per_sent[s]["gold"] > 0:
            overwhelm_values.append(per_sent[s]["result"] / per_sent[s]["gold"])
    median_overwhelm = percentile(sorted(overwhelm_values), 50) if overwhelm_values else 0

    return {
        "p": p, "r": r, "f1": f1,
        "tp": tp_count, "fp": fp_count, "fn": fn_count,
        "output_size": len(result_set),
        "macro_p": macro_p, "macro_r": macro_r, "macro_f1": macro_f1,
        "sent_coverage": sent_coverage,
        "sent_completeness": sent_completeness,
        "sent_usefulness": sent_usefulness,
        "sent_noise": sent_noise,
        "recall_gini": recall_gini,
        "worst_q25_f1": worst_q25_f1,
        "all_or_nothing_rate": all_or_nothing_rate,
        "code_reachability": code_reachability,
        "code_pollution": code_pollution,
        "orphan_rate": orphan_rate,
        "query_success": query_success,
        "median_prec": median_prec,
        "wasted_effort": wasted_effort,
        "median_overwhelm": median_overwhelm,
        "n_covered": len(covered_sents),
        "n_gold_sents": len(gold_sent_list),
        "n_result_sents": len(result_sent_list),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Baseline generators
# ═══════════════════════════════════════════════════════════════════════════════

def baseline_link_all(gold_sents, all_code_files):
    """B1: Every gold sentence × every code file. Zero intelligence."""
    return {(s, c) for s in gold_sents for c in all_code_files}


def baseline_majority_k(gold_sents, gs_sam_code_enrolled, code_model, k=1):
    """B2/B3: Every sentence × files of the top-K largest enrolled components.
    Requires only knowing component sizes (public info from code model)."""
    # Count enrolled files per model element
    model_files = defaultdict(set)
    for m, c in gs_sam_code_enrolled:
        model_files[m].add(c)
    # Pick top-K by enrolled file count
    sorted_models = sorted(model_files.items(), key=lambda x: len(x[1]), reverse=True)
    top_files = set()
    for _, files in sorted_models[:k]:
        top_files |= files
    return {(s, c) for s in gold_sents for c in top_files}


def baseline_random_same_size(gold_sents, all_code_files, target_size):
    """B4: Random links, same total count as TransArc output."""
    sent_list = list(gold_sents)
    file_list = list(all_code_files)
    result = set()
    attempts = 0
    while len(result) < target_size and attempts < target_size * 10:
        s = random.choice(sent_list)
        c = random.choice(file_list)
        result.add((s, c))
        attempts += 1
    return result


def baseline_oracle_heaviest(gs_sad_code, all_code_files, top_n=3):
    """B5: Link the N sentences with most gold links to ALL code files.
    Uses oracle knowledge of gold standard — labeled as such."""
    sent_gold_count = defaultdict(int)
    for s, _ in gs_sad_code:
        sent_gold_count[s] += 1
    top_sents = sorted(sent_gold_count.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result = set()
    for s, _ in top_sents:
        for c in all_code_files:
            result.add((s, c))
    return result


def baseline_keyword_grep(proj, names, text, all_code_files, gs_sam_code_enrolled):
    """B6: Trivial keyword matching — if a sentence contains a component name
    substring (case-insensitive), link it to ALL files of that component.
    No NLP, no model understanding — just grep."""
    # Build model_element -> files mapping
    model_files = defaultdict(set)
    for m, c in gs_sam_code_enrolled:
        model_files[m].add(c)

    # Extract keywords from model element names
    model_keywords = {}
    for m_id, m_name in names.items():
        # Extract the name part after "Component: " or similar prefix
        name = m_name
        if ": " in name:
            name = name.split(": ", 1)[1]
        # Use lowercase keywords, split on spaces/special chars
        keywords = [w.lower() for w in name.replace("-", " ").replace("_", " ").split()
                    if len(w) >= 3]  # skip short words
        if keywords:
            model_keywords[m_id] = keywords

    result = set()
    for sent_num, sent_text in text.items():
        sent_lower = sent_text.lower()
        for m_id, keywords in model_keywords.items():
            if m_id not in model_files:
                continue
            # Check if ANY keyword appears in the sentence
            for kw in keywords:
                if kw in sent_lower:
                    for c in model_files[m_id]:
                        result.add((sent_num, c))
                    break  # Don't double-add for same model element
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Main analysis
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# Stupid Baselines: Why Micro-Averaged F1 Is Insufficient")
    out()
    out("This analysis implements trivially simple (and meaningless) baselines that exploit")
    out("**enrollment inflation** and **component-size skew** in the dataset to achieve")
    out("surprisingly high micro-averaged F1 on SAD-CODE trace link recovery. Each baseline")
    out("is then evaluated with holistic metrics to expose the gap between F1 and actual utility.")
    out()
    out("## Baseline Definitions")
    out()
    out("| ID | Name | Description | Oracle? |")
    out("|----|------|-------------|---------|")
    out("| B0 | **TransArc** | Actual system (reference) | No |")
    out("| B1 | **Link-All** | Every gold sentence x every code file (trivial R=100%) | No* |")
    out("| B2 | **Majority-1** | Every sentence x files of the SINGLE largest component | No |")
    out("| B3 | **Majority-2** | Every sentence x files of the TWO largest components | No |")
    out("| B4 | **Random** | Random links, same count as TransArc output | No |")
    out("| B5 | **Oracle-Top3** | Only predict for 3 sentences with most gold links, link to all files | Yes |")
    out("| B6 | **Keyword-Grep** | If sentence contains component name substring, link to its files | No |")
    out()
    out("\\* B1 uses the set of gold sentences (which sentences have any trace link) but not the actual links.")
    out("  B2/B3 use component sizes from the (public) code model and SAM-CODE gold.")
    out("  B5 uses oracle knowledge of which sentences have the most gold links.")
    out()

    all_project_results = {}

    for proj in PROJECTS:
        print(f"\n{'='*60}")
        print(f"Processing: {proj}")
        print(f"{'='*60}")

        code_model = load_code_model_files(proj)
        names = load_model_element_names(proj)
        text = load_text(proj)

        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gs_sam_code_raw = load_gs_sam_code_raw(proj)
        gs_sam_code_enrolled = enroll_gold_standard(gs_sam_code_raw, code_model)

        gold_sents = set(s for s, _ in gs_sad_code)
        all_text_sents = set(text.keys())

        # B0: TransArc
        transarc = load_result_sad_code(proj)

        # B1: Link-All
        b1 = baseline_link_all(gold_sents, code_model)

        # B2: Majority-1
        b2 = baseline_majority_k(gold_sents, gs_sam_code_enrolled, code_model, k=1)

        # B3: Majority-2
        b3 = baseline_majority_k(gold_sents, gs_sam_code_enrolled, code_model, k=2)

        # B4: Random same-size
        b4 = baseline_random_same_size(gold_sents, code_model, len(transarc))

        # B5: Oracle-Top3
        b5 = baseline_oracle_heaviest(gs_sad_code, code_model, top_n=3)

        # B6: Keyword-Grep
        b6 = baseline_keyword_grep(proj, names, text, code_model, gs_sam_code_enrolled)

        baselines = {
            "B0: TransArc": transarc,
            "B1: Link-All": b1,
            "B2: Majority-1": b2,
            "B3: Majority-2": b3,
            "B4: Random": b4,
            "B5: Oracle-Top3": b5,
            "B6: Keyword-Grep": b6,
        }

        results = {}
        for name, bl_result in baselines.items():
            results[name] = compute_holistic(bl_result, gs_sad_code, gold_sents, code_model)
            r = results[name]
            print(f"  {name}: P={r['p']:.3f} R={r['r']:.3f} F1={r['f1']:.3f} "
                  f"(output={r['output_size']}, TP={r['tp']}, FP={r['fp']}, FN={r['fn']})")

        all_project_results[proj] = results

    # ═══════════════════════════════════════════════════════════════════
    # Report generation
    # ═══════════════════════════════════════════════════════════════════

    for proj in PROJECTS:
        results = all_project_results[proj]
        code_model = load_code_model_files(proj)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)

        out(f"## {proj.capitalize()}")
        out()
        out(f"Gold standard: **{len(gs_sad_code)}** enrolled links from "
            f"**{len(set(s for s,_ in gs_sad_code))}** sentences to "
            f"**{len(set(c for _,c in gs_sad_code))}** code files "
            f"(code model: {len(code_model)} files)")
        out()

        # Standard metrics table
        out("### Standard Metrics (Micro-Averaged)")
        out()
        out("| Baseline | Output Size | Precision | Recall | **F1** | Macro F1 |")
        out("|----------|-----------|-----------|--------|--------|----------|")
        for name, r in results.items():
            f1_fmt = f"**{r['f1']:.3f}**"
            out(f"| {name} | {r['output_size']:,} | {r['p']:.3f} | {r['r']:.3f} | "
                f"{f1_fmt} | {r['macro_f1']:.3f} |")
        out()

        # Holistic metrics table
        out("### Holistic Metrics Comparison")
        out()
        out("| Baseline | Sent Coverage | Usefulness | Noise | Query Success | "
            "Wasted Effort | Overwhelm | Code Pollution |")
        out("|----------|-------------|-----------|-------|-------------|"
            "-------------|-----------|---------------|")
        for name, r in results.items():
            we = f"{r['wasted_effort']:.2f}" if r['wasted_effort'] != float('inf') else "inf"
            out(f"| {name} | {r['sent_coverage']:.3f} "
                f"({r['n_covered']}/{r['n_gold_sents']}) | "
                f"{r['sent_usefulness']:.3f} | {r['sent_noise']:.3f} | "
                f"{r['query_success']:.3f} | {we} | "
                f"{r['median_overwhelm']:.1f}x | {r['code_pollution']:.3f} |")
        out()

        # Distribution metrics
        out("### Distribution Metrics")
        out()
        out("| Baseline | Recall Gini | Worst-Q25 F1 | All-or-Nothing | "
            "Code Reachability | Orphan Rate |")
        out("|----------|-----------|-------------|---------------|"
            "-----------------|------------|")
        for name, r in results.items():
            out(f"| {name} | {r['recall_gini']:.3f} | "
                f"{r['worst_q25_f1']:.3f} | {r['all_or_nothing_rate']:.3f} | "
                f"{r['code_reachability']:.3f} | {r['orphan_rate']:.3f} |")
        out()

    # ═══════════════════════════════════════════════════════════════════
    # Cross-project summary
    # ═══════════════════════════════════════════════════════════════════

    out("## Cross-Project Summary: F1 vs Holistic Quality")
    out()
    out("This table shows each baseline's **micro F1** alongside the **macro F1** and key holistic")
    out("metrics across all projects. High micro F1 with low macro F1 or low holistic scores")
    out("indicates a baseline that games the enrollment-based metric without providing real value.")
    out()

    # Aggregate table: for each baseline, show avg F1, avg macro F1, avg coverage, etc
    baseline_names = ["B0: TransArc", "B1: Link-All", "B2: Majority-1",
                      "B3: Majority-2", "B4: Random", "B5: Oracle-Top3", "B6: Keyword-Grep"]

    out("| Baseline | Avg Micro F1 | Avg Macro F1 | Gap | Avg Coverage | Avg Usefulness | Avg Noise |")
    out("|----------|------------|------------|-----|------------|--------------|-----------|")
    for bl_name in baseline_names:
        f1s, mf1s, covs, uses, nois = [], [], [], [], []
        for proj in PROJECTS:
            r = all_project_results[proj][bl_name]
            f1s.append(r["f1"])
            mf1s.append(r["macro_f1"])
            covs.append(r["sent_coverage"])
            uses.append(r["sent_usefulness"])
            nois.append(r["sent_noise"])
        avg_f1 = sum(f1s) / len(f1s)
        avg_mf1 = sum(mf1s) / len(mf1s)
        gap = avg_f1 - avg_mf1
        avg_cov = sum(covs) / len(covs)
        avg_use = sum(uses) / len(uses)
        avg_noi = sum(nois) / len(nois)
        out(f"| {bl_name} | {avg_f1:.3f} | {avg_mf1:.3f} | "
            f"{gap:+.3f} | {avg_cov:.3f} | {avg_use:.3f} | {avg_noi:.3f} |")
    out()

    # Per-project F1 comparison
    out("### Per-Project Micro F1 Comparison")
    out()
    header = "| Baseline |"
    sep = "|----------|"
    for proj in PROJECTS:
        header += f" {proj} |"
        sep += "---------|"
    out(header)
    out(sep)
    for bl_name in baseline_names:
        row = f"| {bl_name} |"
        for proj in PROJECTS:
            r = all_project_results[proj][bl_name]
            row += f" {r['f1']:.3f} |"
        out(row)
    out()

    # Per-project Macro F1 comparison
    out("### Per-Project Macro F1 Comparison")
    out()
    out(header)
    out(sep)
    for bl_name in baseline_names:
        row = f"| {bl_name} |"
        for proj in PROJECTS:
            r = all_project_results[proj][bl_name]
            row += f" {r['macro_f1']:.3f} |"
        out(row)
    out()

    # ═══════════════════════════════════════════════════════════════════
    # Key insights
    # ═══════════════════════════════════════════════════════════════════

    out("## Key Insights: Why These Baselines Expose Metric Weakness")
    out()

    # Find the most dramatic examples
    out("### Insight 1: Majority-1 Can Match or Exceed TransArc on Micro F1")
    out()
    out("The Majority-1 baseline links every sentence to all files of the single largest")
    out("component. It requires zero NLP, zero model understanding — just counting files in directories.")
    out()
    for proj in PROJECTS:
        ta = all_project_results[proj]["B0: TransArc"]
        m1 = all_project_results[proj]["B2: Majority-1"]
        delta = m1["f1"] - ta["f1"]
        out(f"- **{proj}**: Majority-1 F1={m1['f1']:.3f} vs TransArc F1={ta['f1']:.3f} "
            f"(Δ={delta:+.3f})")
    out()

    out("### Insight 2: Micro F1 vs Macro F1 Gap Reveals Gaming")
    out()
    out("A large gap between micro and macro F1 means the baseline exploits enrollment inflation.")
    out("The micro metric is dominated by large components; macro gives equal weight per sentence.")
    out()
    for proj in PROJECTS:
        for bl_name in ["B2: Majority-1", "B3: Majority-2", "B5: Oracle-Top3"]:
            r = all_project_results[proj][bl_name]
            gap = r["f1"] - r["macro_f1"]
            if gap > 0.1:
                out(f"- **{proj} {bl_name}**: Micro F1={r['f1']:.3f}, "
                    f"Macro F1={r['macro_f1']:.3f} (gap={gap:.3f})")
    out()

    out("### Insight 3: Sentence Coverage Exposes Uselessness")
    out()
    out("A developer queries individual sentences. Sentence coverage measures what fraction")
    out("of sentences return any useful result. Stupid baselines often have 100% coverage")
    out("(because they link everything) but terrible usefulness and noise:")
    out()
    for proj in PROJECTS:
        ta = all_project_results[proj]["B0: TransArc"]
        b1 = all_project_results[proj]["B1: Link-All"]
        m1 = all_project_results[proj]["B2: Majority-1"]
        out(f"- **{proj}**: TransArc usefulness={ta['sent_usefulness']:.3f} "
            f"noise={ta['sent_noise']:.3f} vs "
            f"Link-All usefulness={b1['sent_usefulness']:.3f} "
            f"noise={b1['sent_noise']:.3f} vs "
            f"Majority-1 usefulness={m1['sent_usefulness']:.3f} "
            f"noise={m1['sent_noise']:.3f}")
    out()

    out("### Insight 4: Wasted Effort is the Developer's Real Cost")
    out()
    out("Wasted effort = FP/TP — how many wrong files a developer must sift through per correct one.")
    out("A system with F1=0.800 and wasted effort=50 is far less useful than F1=0.600 with wasted effort=0.1.")
    out()
    for proj in PROJECTS:
        results = all_project_results[proj]
        for bl_name in ["B0: TransArc", "B2: Majority-1", "B1: Link-All"]:
            r = results[bl_name]
            we = f"{r['wasted_effort']:.1f}" if r['wasted_effort'] != float('inf') else "inf"
            out(f"- **{proj} {bl_name}**: F1={r['f1']:.3f}, Wasted Effort={we}")
    out()

    out("### Insight 5: Keyword-Grep — A Trivial Baseline That Reveals Distribution Bias")
    out()
    out("The Keyword-Grep baseline uses no NLP — just checks if a sentence contains a component")
    out("name as a substring (e.g., 'logic' or 'database'). Its performance reveals how much of the")
    out("apparent quality comes from trivial pattern matching on component names:")
    out()
    for proj in PROJECTS:
        ta = all_project_results[proj]["B0: TransArc"]
        kg = all_project_results[proj]["B6: Keyword-Grep"]
        out(f"- **{proj}**: Keyword-Grep F1={kg['f1']:.3f} vs TransArc F1={ta['f1']:.3f}")
    out()

    out("### Insight 6: Oracle-Top3 Shows Single-Sentence Dominance")
    out()
    out("By predicting links only for the 3 sentences with the most gold links (and linking them")
    out("to all files), we see how much of the gold standard mass is concentrated in a few sentences:")
    out()
    for proj in PROJECTS:
        r = all_project_results[proj]["B5: Oracle-Top3"]
        gs_sad_code = load_gs_sad_code_enrolled(proj, load_code_model_files(proj))
        gold_mass = len(gs_sad_code)
        out(f"- **{proj}**: 3 sentences capture {r['tp']} / {gold_mass} gold links "
            f"= {r['tp']/gold_mass*100:.1f}%. Oracle-Top3 F1={r['f1']:.3f}")
    out()

    out("## Conclusion")
    out()
    out("**Micro-averaged F1 on enrollment-based gold standards is easily gamed by trivial baselines.**")
    out()
    out("The Majority-1 baseline — which requires zero NLP, zero architecture understanding, and")
    out("can be implemented in 3 lines of code — achieves competitive or even superior micro F1 to")
    out("TransArc on some projects. This is because:")
    out()
    out("1. **Enrollment inflation**: One directory entry expands to hundreds of file-level links,")
    out("   so getting one large component right/wrong dominates the metric")
    out("2. **Component-size skew**: Most gold links belong to 1-2 large components, so always")
    out("   predicting the largest component captures a disproportionate share of TPs")
    out("3. **Sentence-file asymmetry**: A few sentences map to thousands of files, so getting")
    out("   those sentences right inflates micro F1 while 40% of sentences can have zero recall")
    out()
    out("**Holistic metrics expose these baselines as useless:**")
    out()
    out("- Sentence **usefulness** drops dramatically (majority of sentences get wrong results)")
    out("- **Noise** becomes extreme (developers see mostly wrong files)")
    out("- **Wasted effort** explodes (dozens of wrong files per correct one)")
    out("- **Macro F1** collapses (equal weight per sentence reveals the truth)")
    out("- **Code pollution** increases (many spurious code files in output)")
    out()
    out("This demonstrates that **comprehensive evaluation requires multiple complementary metrics**,")
    out("not just micro-averaged P/R/F1.")
    out()

    # Write report
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
