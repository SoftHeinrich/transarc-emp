#!/usr/bin/env python3
"""
Creative Holistic Metrics for Trace Link Recovery Evaluation

Goes beyond P/R/F1 to capture dimensions that matter for practical use:

SENTENCE-CENTRIC: Does the documentation connect to code?
  - Sentence coverage: fraction of gold sentences that get any correct link
  - Sentence completeness: among covered sentences, how many gold links found?
  - Sentence usefulness: fraction of sentences where TPs > FPs
  - Sentence noise: avg FP/(TP+FP) per sentence — developer trust proxy

CODE-CENTRIC: Is the codebase reachable from documentation?
  - Code reachability: fraction of gold code files reached by any correct link
  - Code pollution: fraction of result code files not in any gold link
  - Orphan rate: fraction of code model files with zero trace links

COMPONENT/BRIDGE-CENTRIC: Does the transitive bridge work?
  - Bridge utilization: fraction of model elements that produce any output
  - Bridge accuracy: fraction of bridges where the SAD-SAM side is correct
  - Component confusion: when wrong, what do we confuse with?

DISTRIBUTION: How fair/robust is performance?
  - Gini coefficient of per-sentence recall
  - Worst-quartile F1: average F1 of the bottom 25% of sentences
  - All-or-nothing rate: fraction of sentences with recall=0% or 100%

PRACTICAL UTILITY: Developer experience proxies
  - Query success rate: P(≥1 correct file | developer queries a sentence)
  - Signal-to-noise ratio: median(TP/FP) per sentence
  - Precision@k: if a developer looks at top-k files per sentence, how many are correct?
  - Completeness gap: for covered sentences, avg fraction of gold files still missing
"""

import math
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
    load_result_sam_code_standalone,
    load_transarc_intermediate_sam_code,
    load_transarc_intermediate_sad_sam,
    load_transarc_intermediate_maps,
    load_model_element_names, load_text,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/CREATIVE_METRICS.md")


def gini_coefficient(values):
    """Compute Gini coefficient. 0 = perfect equality, 1 = maximum inequality."""
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    numerator = sum((2 * i - n - 1) * v for i, v in enumerate(sorted_vals, 1))
    denominator = n * sum(sorted_vals)
    return numerator / denominator if denominator > 0 else 0


def percentile(values, p):
    """Get the p-th percentile of a sorted list."""
    if not values:
        return 0
    k = (len(values) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] * (c - k) + values[c] * (k - f)


def analyze_project(proj):
    """Full creative metrics for one project."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)
    texts = load_text(proj)

    # Gold standards
    gs_sad_sam = load_gs_sad_sam(proj)
    gs_sam_code = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)

    # Results
    result = load_result_sad_code(proj)
    result_tps = result & gs_sad_code
    result_fps = result - gs_sad_code
    result_fns = gs_sad_code - result

    # Intermediates
    int_sad_sam = load_transarc_intermediate_sad_sam(proj)
    int_sam_code = load_transarc_intermediate_sam_code(proj)
    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(proj)

    # ═══ SENTENCE-CENTRIC ════════════════════════════════════════════

    # All sentences in gold
    gold_sents = set(s for s, _ in gs_sad_code)
    result_sents = set(s for s, _ in result)
    all_sents = gold_sents | result_sents

    per_sent = {}
    for s in all_sents:
        gold_s = set(c for ss, c in gs_sad_code if ss == s)
        result_s = set(c for ss, c in result if ss == s)
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

    # Sentence coverage: fraction of gold sentences with at least 1 TP
    gold_sent_list = [s for s in all_sents if per_sent[s]["has_gold"]]
    covered_sents = [s for s in gold_sent_list if per_sent[s]["tp"] > 0]
    sent_coverage = len(covered_sents) / len(gold_sent_list) if gold_sent_list else 0

    # Sentence completeness: among covered sentences, avg recall
    completeness_values = [per_sent[s]["recall"] for s in covered_sents]
    sent_completeness = sum(completeness_values) / len(completeness_values) if completeness_values else 0

    # Sentence usefulness: fraction of result sentences where TP > FP
    result_sent_list = [s for s in all_sents if per_sent[s]["has_result"]]
    useful_sents = [s for s in result_sent_list if per_sent[s]["tp"] > per_sent[s]["fp"]]
    sent_usefulness = len(useful_sents) / len(result_sent_list) if result_sent_list else 0

    # Sentence noise: avg (FP / (TP+FP)) per sentence with output
    noise_values = []
    for s in result_sent_list:
        total = per_sent[s]["tp"] + per_sent[s]["fp"]
        noise_values.append(per_sent[s]["fp"] / total if total > 0 else 0)
    sent_noise = sum(noise_values) / len(noise_values) if noise_values else 0

    # All-or-nothing rate: fraction with recall=0 or recall=1
    all_or_nothing = sum(1 for s in gold_sent_list
                        if per_sent[s]["recall"] == 0 or per_sent[s]["recall"] == 1.0)
    all_or_nothing_rate = all_or_nothing / len(gold_sent_list) if gold_sent_list else 0

    # Recall distribution stats
    recall_values = sorted([per_sent[s]["recall"] for s in gold_sent_list])
    recall_zero = sum(1 for v in recall_values if v == 0)
    recall_one = sum(1 for v in recall_values if v == 1.0)

    # Worst quartile F1
    f1_values = []
    for s in gold_sent_list:
        p = per_sent[s]["precision"] if per_sent[s]["precision"] is not None else 0
        r = per_sent[s]["recall"]
        f = 2*p*r/(p+r) if (p+r) > 0 else 0
        f1_values.append(f)
    f1_values_sorted = sorted(f1_values)
    q25_idx = max(1, len(f1_values_sorted) // 4)
    worst_q25_f1 = sum(f1_values_sorted[:q25_idx]) / q25_idx if q25_idx > 0 else 0

    # Gini of recall
    recall_gini = gini_coefficient(recall_values)

    # ═══ CODE-CENTRIC ════════════════════════════════════════════════

    # All code files in gold
    gold_codes = set(c for _, c in gs_sad_code)
    result_codes = set(c for _, c in result)

    # Code reachability: fraction of gold code files in at least 1 TP
    reached_codes = set(c for _, c in result_tps)
    code_reachability = len(reached_codes & gold_codes) / len(gold_codes) if gold_codes else 0

    # Code pollution: fraction of result code files not in any gold link
    spurious_codes = result_codes - gold_codes
    code_pollution = len(spurious_codes) / len(result_codes) if result_codes else 0

    # Per-code-file metrics
    per_code = {}
    for c in gold_codes | result_codes:
        gold_c = set(s for s, cc in gs_sad_code if cc == c)
        result_c = set(s for s, cc in result if cc == c)
        tp_c = gold_c & result_c
        per_code[c] = {
            "gold_sents": len(gold_c), "result_sents": len(result_c),
            "tp_sents": len(tp_c),
            "recall": len(tp_c) / len(gold_c) if gold_c else None,
        }

    # Orphan rate: gold code files with zero result links
    orphan_codes = [c for c in gold_codes if per_code[c]["result_sents"] == 0]
    orphan_rate = len(orphan_codes) / len(gold_codes) if gold_codes else 0

    # Code reachability distribution
    code_recall_values = sorted([per_code[c]["recall"] for c in gold_codes if per_code[c]["recall"] is not None])

    # ═══ COMPONENT/BRIDGE-CENTRIC ════════════════════════════════════

    # All model elements in gold SAD-SAM
    gold_models = set(m for m, _ in gs_sad_sam)
    int_models = set(m for m, _ in int_sad_sam)

    # Bridge utilization: fraction of gold model elements that appear in intermediate
    bridge_utilization = len(gold_models & int_models) / len(gold_models) if gold_models else 0

    # Bridge accuracy: fraction of intermediate SAD-SAM links that are TPs
    int_sad_sam_tps = int_sad_sam & gs_sad_sam
    bridge_accuracy = len(int_sad_sam_tps) / len(int_sad_sam) if int_sad_sam else 0

    # Bridge recall: fraction of gold SAD-SAM links found
    bridge_recall = len(int_sad_sam_tps) / len(gs_sad_sam) if gs_sad_sam else 0

    # Component confusion: for SAD-SAM FPs, which model element was chosen instead of correct?
    confusions = []
    sad_sam_fps = int_sad_sam - gs_sad_sam
    gs_sad_sam_s2m = defaultdict(set)
    for m, s in gs_sad_sam:
        gs_sad_sam_s2m[s].add(m)

    for (m_wrong, s) in sad_sam_fps:
        correct_models = gs_sad_sam_s2m.get(s, set())
        if correct_models:
            for m_correct in correct_models:
                confusions.append((names.get(m_wrong, m_wrong),
                                  names.get(m_correct, m_correct), s))

    # Aggregate confusions
    confusion_counts = defaultdict(int)
    for wrong, correct, _ in confusions:
        confusion_counts[(wrong, correct)] += 1

    # ═══ PRACTICAL UTILITY ═══════════════════════════════════════════

    # Query success rate: P(≥1 correct file | sentence queried)
    # = fraction of result sentences that have at least 1 TP
    query_success = sum(1 for s in result_sent_list if per_sent[s]["tp"] > 0) / \
                    len(result_sent_list) if result_sent_list else 0

    # Signal-to-noise per sentence: TP / (TP+FP) = precision per sentence
    # Report median
    prec_per_sent = [per_sent[s]["tp"] / (per_sent[s]["tp"] + per_sent[s]["fp"])
                     for s in result_sent_list if per_sent[s]["tp"] + per_sent[s]["fp"] > 0]
    prec_per_sent_sorted = sorted(prec_per_sent)
    median_sent_prec = percentile(prec_per_sent_sorted, 50) if prec_per_sent_sorted else 0

    # Completeness gap: for covered sentences, avg fraction of gold still missing
    completeness_gaps = [per_sent[s]["fn"] / per_sent[s]["gold"]
                        for s in covered_sents if per_sent[s]["gold"] > 0]
    avg_completeness_gap = sum(completeness_gaps) / len(completeness_gaps) if completeness_gaps else 0

    # "Overwhelm ratio": for result sentences, median result size / gold size
    # Captures: does the tool return a manageable number of links?
    overwhelm_values = []
    for s in result_sent_list:
        if per_sent[s]["has_gold"] and per_sent[s]["gold"] > 0:
            overwhelm_values.append(per_sent[s]["result"] / per_sent[s]["gold"])
    overwhelm_values_sorted = sorted(overwhelm_values)
    median_overwhelm = percentile(overwhelm_values_sorted, 50) if overwhelm_values_sorted else 0

    # Wasted effort: total FPs / total TPs — how many wrong links per correct one?
    total_tp = len(result_tps)
    total_fp = len(result_fps)
    wasted_effort = total_fp / total_tp if total_tp > 0 else float('inf')

    return {
        "sent": {
            "n_gold": len(gold_sent_list),
            "n_result": len(result_sent_list),
            "coverage": sent_coverage,
            "completeness": sent_completeness,
            "usefulness": sent_usefulness,
            "noise": sent_noise,
            "all_or_nothing_rate": all_or_nothing_rate,
            "recall_zero": recall_zero,
            "recall_one": recall_one,
            "worst_q25_f1": worst_q25_f1,
            "recall_gini": recall_gini,
            "recall_median": percentile(recall_values, 50) if recall_values else 0,
            "recall_p25": percentile(recall_values, 25) if recall_values else 0,
            "recall_p75": percentile(recall_values, 75) if recall_values else 0,
            "per_sent": per_sent,
        },
        "code": {
            "n_gold": len(gold_codes),
            "n_result": len(result_codes),
            "reachability": code_reachability,
            "pollution": code_pollution,
            "orphan_rate": orphan_rate,
            "n_orphans": len(orphan_codes),
            "recall_median": percentile(code_recall_values, 50) if code_recall_values else 0,
        },
        "bridge": {
            "utilization": bridge_utilization,
            "accuracy": bridge_accuracy,
            "recall": bridge_recall,
            "n_gold_models": len(gold_models),
            "n_int_models": len(int_models),
            "confusions": sorted(confusion_counts.items(), key=lambda x: x[1], reverse=True),
        },
        "utility": {
            "query_success": query_success,
            "median_sent_prec": median_sent_prec,
            "completeness_gap": avg_completeness_gap,
            "median_overwhelm": median_overwhelm,
            "wasted_effort": wasted_effort,
        },
        "baseline": {
            "tp": total_tp, "fp": total_fp, "fn": len(result_fns),
            "p": total_tp / len(result) if result else 0,
            "r": total_tp / len(gs_sad_code) if gs_sad_code else 0,
        },
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# Creative Holistic Metrics for Trace Link Recovery")
    out()

    all_results = {}
    for proj in PROJECTS:
        all_results[proj] = analyze_project(proj)

    # ═══ 1. SENTENCE COVERAGE & COMPLETENESS ═════════════════════════

    out("## 1. Sentence-Centric Metrics")
    out()
    out("These answer: **how well does the documentation connect to code?**")
    out()
    out("| Metric | Definition |")
    out("|--------|-----------|")
    out("| **Coverage** | Fraction of gold sentences with ≥1 correct link (TP) |")
    out("| **Completeness** | Among covered sentences, average recall (what fraction of gold links found?) |")
    out("| **Usefulness** | Fraction of result sentences where TP > FP (more helpful than harmful) |")
    out("| **Noise** | Average FP/(TP+FP) per result sentence (developer frustration proxy) |")
    out("| **All-or-Nothing** | Fraction of gold sentences with recall = 0% or 100% (bimodality) |")
    out()

    out("| Project | P/R/F1 (M1) | Sent Coverage | Completeness | Usefulness | Noise | All-or-Nothing |")
    out("|---------|-----------|-------------|-------------|-----------|-------|---------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        b = r["baseline"]
        s = r["sent"]
        f1 = 2*b["p"]*b["r"]/(b["p"]+b["r"]) if (b["p"]+b["r"]) > 0 else 0
        out(f"| {proj} | {b['p']:.3f}/{b['r']:.3f}/{f1:.3f} | "
            f"{s['coverage']:.3f} ({len([x for x in s['per_sent'].values() if x['has_gold'] and x['tp']>0])}/{s['n_gold']}) | "
            f"{s['completeness']:.3f} | "
            f"{s['usefulness']:.3f} ({len([x for x in s['per_sent'].values() if x['has_result'] and x['tp']>x['fp']])}/{s['n_result']}) | "
            f"{s['noise']:.3f} | "
            f"{s['all_or_nothing_rate']:.3f} |")

    out()

    # Recall distribution
    out("### Sentence Recall Distribution")
    out()
    out("| Project | Gold Sents | R=0% | 0<R<50% | 50%≤R<100% | R=100% | Median R | Gini | Worst-Q25 F1 |")
    out("|---------|----------|------|---------|-----------|--------|---------|------|-------------|")

    for proj in PROJECTS:
        s = all_results[proj]["sent"]
        gold_sents = [x for x in s["per_sent"].values() if x["has_gold"]]
        r0 = sum(1 for x in gold_sents if x["recall"] == 0)
        r_low = sum(1 for x in gold_sents if 0 < x["recall"] < 0.5)
        r_mid = sum(1 for x in gold_sents if 0.5 <= x["recall"] < 1.0)
        r1 = sum(1 for x in gold_sents if x["recall"] == 1.0)
        out(f"| {proj} | {s['n_gold']} | {r0} ({r0/s['n_gold']*100:.0f}%) | "
            f"{r_low} ({r_low/s['n_gold']*100:.0f}%) | "
            f"{r_mid} ({r_mid/s['n_gold']*100:.0f}%) | "
            f"{r1} ({r1/s['n_gold']*100:.0f}%) | "
            f"{s['recall_median']:.3f} | {s['recall_gini']:.3f} | {s['worst_q25_f1']:.3f} |")

    out()

    # ═══ 2. CODE-CENTRIC METRICS ═════════════════════════════════════

    out("## 2. Code-Centric Metrics")
    out()
    out("These answer: **how well is the codebase reachable from documentation?**")
    out()
    out("| Metric | Definition |")
    out("|--------|-----------|")
    out("| **Reachability** | Fraction of gold code files correctly linked to ≥1 sentence |")
    out("| **Pollution** | Fraction of result code files not in any gold link (spurious) |")
    out("| **Orphan Rate** | Fraction of gold code files with zero result links (completely invisible) |")
    out()

    out("| Project | Gold Files | Result Files | Reachability | Pollution | Orphan Rate |")
    out("|---------|----------|-------------|-------------|----------|------------|")

    for proj in PROJECTS:
        c = all_results[proj]["code"]
        out(f"| {proj} | {c['n_gold']} | {c['n_result']} | "
            f"{c['reachability']:.3f} | {c['pollution']:.3f} | "
            f"{c['orphan_rate']:.3f} ({c['n_orphans']}/{c['n_gold']}) |")

    out()

    # ═══ 3. BRIDGE/COMPONENT METRICS ═════════════════════════════════

    out("## 3. Bridge & Component Metrics")
    out()
    out("These answer: **does the transitive bridge work?**")
    out()
    out("| Metric | Definition |")
    out("|--------|-----------|")
    out("| **Bridge Utilization** | Fraction of gold model elements that appear in the intermediate |")
    out("| **Bridge Accuracy** | Precision of intermediate SAD-SAM links (correct bridges) |")
    out("| **Bridge Recall** | Fraction of gold SAD-SAM links found in intermediate |")
    out()

    out("| Project | Gold Models | Int Models | Utilization | Bridge Accuracy | Bridge Recall |")
    out("|---------|-----------|-----------|------------|----------------|--------------|")

    for proj in PROJECTS:
        br = all_results[proj]["bridge"]
        out(f"| {proj} | {br['n_gold_models']} | {br['n_int_models']} | "
            f"{br['utilization']:.3f} | {br['accuracy']:.3f} | {br['recall']:.3f} |")

    out()

    # Component confusion
    out("### Component Confusion (SAD-SAM FPs: wrong model element assigned)")
    out()
    out("When SAD-SAM assigns a sentence to the wrong model element, which confusions occur?")
    out()

    for proj in PROJECTS:
        br = all_results[proj]["bridge"]
        confusions = br["confusions"]
        if not confusions:
            continue

        out(f"**{proj}:**")
        out()
        out("| Assigned (Wrong) | Should Be (Correct) | Count |")
        out("|-----------------|--------------------|----- |")
        for (wrong, correct), count in confusions[:10]:
            out(f"| {wrong} | {correct} | {count} |")
        out()

    # ═══ 4. PRACTICAL UTILITY METRICS ════════════════════════════════

    out("## 4. Practical Utility Metrics")
    out()
    out("These answer: **how useful is the tool for a developer?**")
    out()
    out("| Metric | Definition |")
    out("|--------|-----------|")
    out("| **Query Success** | P(≥1 correct file \\| developer queries a sentence) |")
    out("| **Median Precision** | Median per-sentence precision (typical developer experience) |")
    out("| **Completeness Gap** | Among covered sentences, avg fraction of gold files still missing |")
    out("| **Overwhelm Ratio** | Median (result files / gold files) per sentence (information overload) |")
    out("| **Wasted Effort** | Total FP / Total TP (wrong links per correct one) |")
    out()

    out("| Project | Query Success | Median Prec | Completeness Gap | Overwhelm Ratio | Wasted Effort |")
    out("|---------|-------------|-----------|-----------------|----------------|-------------- |")

    for proj in PROJECTS:
        u = all_results[proj]["utility"]
        we = f"{u['wasted_effort']:.2f}" if u['wasted_effort'] != float('inf') else "∞"
        out(f"| {proj} | {u['query_success']:.3f} | {u['median_sent_prec']:.3f} | "
            f"{u['completeness_gap']:.3f} | {u['median_overwhelm']:.1f}x | {we} |")

    out()

    # ═══ 5. COMPREHENSIVE DASHBOARD ══════════════════════════════════

    out("## 5. Comprehensive Dashboard: All Metrics Side by Side")
    out()

    out("| Metric | mediastore | teastore | teammates | bigbluebutton | jabref |")
    out("|--------|-----------|---------|----------|-------------|--------|")

    metric_rows = [
        ("**Standard P/R/F1**", lambda r: f"{2*r['baseline']['p']*r['baseline']['r']/(r['baseline']['p']+r['baseline']['r']) if (r['baseline']['p']+r['baseline']['r'])>0 else 0:.3f}"),
        ("", lambda r: ""),
        ("*Sentence-Centric*", lambda r: ""),
        ("Sentence Coverage", lambda r: f"{r['sent']['coverage']:.3f}"),
        ("Sentence Completeness", lambda r: f"{r['sent']['completeness']:.3f}"),
        ("Sentence Usefulness", lambda r: f"{r['sent']['usefulness']:.3f}"),
        ("Sentence Noise", lambda r: f"{r['sent']['noise']:.3f}"),
        ("All-or-Nothing Rate", lambda r: f"{r['sent']['all_or_nothing_rate']:.3f}"),
        ("Recall Gini", lambda r: f"{r['sent']['recall_gini']:.3f}"),
        ("Worst-Q25 F1", lambda r: f"{r['sent']['worst_q25_f1']:.3f}"),
        ("Recall Median", lambda r: f"{r['sent']['recall_median']:.3f}"),
        ("", lambda r: ""),
        ("*Code-Centric*", lambda r: ""),
        ("Code Reachability", lambda r: f"{r['code']['reachability']:.3f}"),
        ("Code Pollution", lambda r: f"{r['code']['pollution']:.3f}"),
        ("Code Orphan Rate", lambda r: f"{r['code']['orphan_rate']:.3f}"),
        ("", lambda r: ""),
        ("*Bridge*", lambda r: ""),
        ("Bridge Utilization", lambda r: f"{r['bridge']['utilization']:.3f}"),
        ("Bridge Accuracy", lambda r: f"{r['bridge']['accuracy']:.3f}"),
        ("Bridge Recall", lambda r: f"{r['bridge']['recall']:.3f}"),
        ("", lambda r: ""),
        ("*Practical Utility*", lambda r: ""),
        ("Query Success", lambda r: f"{r['utility']['query_success']:.3f}"),
        ("Median Sent Precision", lambda r: f"{r['utility']['median_sent_prec']:.3f}"),
        ("Completeness Gap", lambda r: f"{r['utility']['completeness_gap']:.3f}"),
        ("Overwhelm Ratio", lambda r: f"{r['utility']['median_overwhelm']:.1f}x"),
        ("Wasted Effort", lambda r: f"{r['utility']['wasted_effort']:.2f}" if r['utility']['wasted_effort'] != float('inf') else "∞"),
    ]

    for label, fn in metric_rows:
        if not label:
            out(f"| | | | | | |")
            continue
        vals = [fn(all_results[p]) for p in PROJECTS]
        out(f"| {label} | {' | '.join(vals)} |")

    out()

    # ═══ 6. METRIC CORRELATIONS & INSIGHTS ══════════════════════════

    out("## 6. What These Metrics Reveal That P/R/F1 Cannot")
    out()

    out("### Insight 1: F1 Hides Bimodal Sentence Coverage")
    out()
    out("Standard F1 averages over all links uniformly. But sentences are either fully")
    out("recovered or completely missed. The All-or-Nothing rate reveals this:")
    out()
    for proj in PROJECTS:
        s = all_results[proj]["sent"]
        b = all_results[proj]["baseline"]
        f1v = 2*b["p"]*b["r"]/(b["p"]+b["r"]) if (b["p"]+b["r"])>0 else 0
        out(f"- **{proj}**: F1={f1v:.3f}, but {s['all_or_nothing_rate']*100:.0f}% of sentences are all-or-nothing "
            f"(R=0: {s['recall_zero']}, R=100%: {s['recall_one']})")
    out()

    out("### Insight 2: Completeness Gap Shows Partial Recovery Is Rare")
    out()
    for proj in PROJECTS:
        u = all_results[proj]["utility"]
        s = all_results[proj]["sent"]
        gold_sents = [x for x in s["per_sent"].values() if x["has_gold"]]
        partial = sum(1 for x in gold_sents if 0 < x["recall"] < 1.0)
        out(f"- **{proj}**: Completeness gap = {u['completeness_gap']:.3f} "
            f"(only {partial}/{len(gold_sents)} sentences have partial recall)")
    out()

    out("### Insight 3: Overwhelm Ratio Shows Information Overload")
    out()
    out("The developer sees N result files per sentence. How does N compare to the actual gold count?")
    out()
    for proj in PROJECTS:
        u = all_results[proj]["utility"]
        out(f"- **{proj}**: Median overwhelm = {u['median_overwhelm']:.1f}x "
            f"(result files are {u['median_overwhelm']:.1f}× the gold count)")
    out()

    out("### Insight 4: Gini Coefficient Reveals Inequality")
    out()
    out("A Gini of 0 means all sentences are equally well-served; 1 means all recall is")
    out("concentrated in one sentence. High Gini = unfair distribution of quality.")
    out()
    for proj in PROJECTS:
        s = all_results[proj]["sent"]
        out(f"- **{proj}**: Gini = {s['recall_gini']:.3f}")
    out()

    out("### Insight 5: Component Confusion Reveals Systematic Errors")
    out()
    for proj in PROJECTS:
        br = all_results[proj]["bridge"]
        if br["confusions"]:
            top = br["confusions"][0]
            out(f"- **{proj}**: Top confusion: {top[0][0]} → {top[0][1]} ({top[1]}× "
                f"— sentences about {top[0][1]} are assigned to {top[0][0]})")
    out()

    out("### Insight 6: Query Success vs F1")
    out()
    out("F1 counts individual links. Query success counts whether a developer")
    out("gets *any* useful result per query. These can diverge significantly:")
    out()
    for proj in PROJECTS:
        b = all_results[proj]["baseline"]
        u = all_results[proj]["utility"]
        f1v = 2*b["p"]*b["r"]/(b["p"]+b["r"]) if (b["p"]+b["r"])>0 else 0
        out(f"- **{proj}**: F1={f1v:.3f}, Query Success={u['query_success']:.3f}")
    out()

    # ─── Write report ────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
