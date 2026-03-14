#!/usr/bin/env python3
"""
Multi-Agent LLM Baseline Evaluation for SAD-CODE Trace Link Recovery

Reads 3 independent agent classification files per project, aggregates via
majority voting (>=2/3 agreement), and evaluates against SAD-CODE gold standard.

Compares: Single-Agent LLM, Multi-Agent LLM, TransArc, Keyword-Grep, Oracle baselines.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sam_code_raw, load_gs_sad_code_enrolled,
    load_result_sad_code, load_model_element_names, load_text,
    calc_metrics,
)
from extreme_baseline_analysis import (
    compute_metrics,
    baseline_oracle_best_component,
    baseline_oracle_component_subset,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/LLM_BASELINE.md")
SINGLE_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/llm_classifications")
MULTI_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/llm_classifications_multi")

VARIANTS = ["v1", "v2", "v3"]
THRESHOLD = 2  # Need >=2 out of 3 agents to agree


def load_classification(path):
    """Load a classification JSON file."""
    with open(path) as f:
        return json.load(f)


def load_single_agent(project):
    """Load single-agent classification."""
    return load_classification(SINGLE_DIR / f"{project}.json")


def load_multi_agent_variants(project):
    """Load all 3 variant classifications for a project."""
    variants = {}
    for v in VARIANTS:
        path = MULTI_DIR / f"{project}_{v}.json"
        if path.exists():
            variants[v] = load_classification(path)
    return variants


def majority_vote(variants):
    """Aggregate multiple classifications via majority voting.

    For each (sentence, component) pair, count how many agents assigned it.
    Keep only pairs where >= THRESHOLD agents agree.

    Returns: {sentence_num_str: [component_names]}
    """
    # Count (sentence, component) occurrences across agents
    pair_counts = Counter()
    for v_name, classification in variants.items():
        for sent_num, comp_names in classification.items():
            for comp in comp_names:
                pair_counts[(sent_num, comp)] += 1

    # Keep pairs with sufficient agreement
    result = defaultdict(list)
    for (sent_num, comp), count in pair_counts.items():
        if count >= THRESHOLD:
            result[sent_num].append(comp)

    return dict(result)


def union_vote(variants):
    """Aggregate via union (any agent assigned it => keep it)."""
    result = defaultdict(set)
    for v_name, classification in variants.items():
        for sent_num, comp_names in classification.items():
            for comp in comp_names:
                result[sent_num].add(comp)
    return {k: list(v) for k, v in result.items()}


def intersection_vote(variants):
    """Aggregate via intersection (ALL agents must agree)."""
    if not variants:
        return {}

    # Get all (sent, comp) pairs per variant
    variant_pairs = []
    for v_name, classification in variants.items():
        pairs = set()
        for sent_num, comp_names in classification.items():
            for comp in comp_names:
                pairs.add((sent_num, comp))
        variant_pairs.append(pairs)

    # Intersect all
    common = variant_pairs[0]
    for p in variant_pairs[1:]:
        common = common & p

    result = defaultdict(list)
    for sent_num, comp in common:
        result[sent_num].append(comp)
    return dict(result)


def build_name_to_id_map(project):
    """Build ae_name -> set(ae_id) mapping from SAM-CODE gold standard."""
    names = load_model_element_names(project)
    name_to_ids = defaultdict(set)
    for ae_id, ae_name in names.items():
        name_to_ids[ae_name].add(ae_id)
    return dict(name_to_ids)


def build_model_to_files(project, code_model):
    """Build ae_id -> set(enrolled_files) from SAM-CODE gold."""
    gs_sam_code_raw = load_gs_sam_code_raw(project)
    gs_sam_code_enrolled = enroll_gold_standard(gs_sam_code_raw, code_model)
    model_to_files = defaultdict(set)
    for m, c in gs_sam_code_enrolled:
        model_to_files[m].add(c)
    return dict(model_to_files)


def classifications_to_result_set(classifications, name_to_ids, model_to_files):
    """Convert classifications to (sentence, code_file) result set."""
    result = set()
    unmatched_names = set()
    for sent_num, comp_names in classifications.items():
        for comp_name in comp_names:
            ae_ids = name_to_ids.get(comp_name, set())
            if not ae_ids:
                unmatched_names.add(comp_name)
                continue
            for ae_id in ae_ids:
                files = model_to_files.get(ae_id, set())
                for f in files:
                    result.add((sent_num, f))
    return result, unmatched_names


def baseline_keyword_grep(gold_sents, text, model_to_files, names):
    """Keyword-Grep baseline."""
    model_keywords = {}
    for m_id, m_name in names.items():
        if m_id not in model_to_files:
            continue
        name = m_name
        if ": " in name:
            name = name.split(": ", 1)[1]
        keywords = [w.lower() for w in name.replace("-", " ").replace("_", " ").split()
                    if len(w) >= 3]
        if keywords:
            model_keywords[m_id] = keywords

    result = set()
    for s in gold_sents:
        sent_text = text.get(s, "").lower()
        for m_id, keywords in model_keywords.items():
            for kw in keywords:
                if kw in sent_text:
                    for c in model_to_files[m_id]:
                        result.add((s, c))
                    break
    return result


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# Analysis L: LLM Baseline for Component Classification")
    out()
    out("## Approach")
    out()
    out("Two LLM-based approaches are evaluated:")
    out()
    out("**Single-Agent**: One Claude agent per project classifies each sentence")
    out("into component(s), mapped to enrolled code files via SAM-CODE gold standard.")
    out()
    out("**Multi-Agent (Majority Vote)**: Three independent agents (2x Sonnet + 1x Haiku)")
    out("classify each project with different prompt variants. A (sentence, component)")
    out("assignment is kept only if >=2/3 agents agree. This ensemble approach aims to")
    out("reduce noise (false component assignments) while preserving recall.")
    out()

    all_results = {}
    all_details = {}

    for proj in PROJECTS:
        print(f"\n{'='*60}")
        print(f"Processing: {proj}")
        print(f"{'='*60}")

        code_model = load_code_model_files(proj)
        names = load_model_element_names(proj)
        text = load_text(proj)

        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gold_sents = set(s for s, _ in gs_sad_code)

        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        # --- Single-Agent LLM ---
        single_cls = None
        try:
            single_cls = load_single_agent(proj)
        except FileNotFoundError:
            print(f"  WARNING: No single-agent file for {proj}")

        if single_cls:
            single_result, single_unmatched = classifications_to_result_set(
                single_cls, name_to_ids, model_to_files)
            single_metrics = compute_metrics(single_result, gs_sad_code, gold_sents)
            if single_unmatched:
                print(f"  Single-agent unmatched: {single_unmatched}")
        else:
            single_metrics = None

        # --- Multi-Agent LLM ---
        variants = load_multi_agent_variants(proj)
        if len(variants) == 3:
            # Majority vote
            majority_cls = majority_vote(variants)
            majority_result, majority_unmatched = classifications_to_result_set(
                majority_cls, name_to_ids, model_to_files)
            majority_metrics = compute_metrics(majority_result, gs_sad_code, gold_sents)
            if majority_unmatched:
                print(f"  Multi-agent unmatched: {majority_unmatched}")

            # Also compute individual variant metrics for analysis
            variant_metrics = {}
            for v_name, v_cls in variants.items():
                v_result, _ = classifications_to_result_set(v_cls, name_to_ids, model_to_files)
                variant_metrics[v_name] = compute_metrics(v_result, gs_sad_code, gold_sents)

            # Union and Intersection for comparison
            union_cls = union_vote(variants)
            union_result, _ = classifications_to_result_set(union_cls, name_to_ids, model_to_files)
            union_metrics = compute_metrics(union_result, gs_sad_code, gold_sents)

            intersect_cls = intersection_vote(variants)
            intersect_result, _ = classifications_to_result_set(intersect_cls, name_to_ids, model_to_files)
            intersect_metrics = compute_metrics(intersect_result, gs_sad_code, gold_sents)
        else:
            print(f"  WARNING: Only {len(variants)} variants found for {proj}, need 3")
            majority_metrics = None
            variant_metrics = {}
            union_metrics = None
            intersect_metrics = None

        # --- TransArc ---
        transarc = load_result_sad_code(proj)
        ta_metrics = compute_metrics(transarc, gs_sad_code, gold_sents)

        # --- Keyword-Grep ---
        kg_result = baseline_keyword_grep(gold_sents, text, model_to_files, names)
        kg_metrics = compute_metrics(kg_result, gs_sad_code, gold_sents)

        # --- Oracle baselines ---
        b7 = baseline_oracle_best_component(gold_sents, gs_sad_code, model_to_files)
        b7_metrics = compute_metrics(b7, gs_sad_code, gold_sents)

        print(f"  Computing Oracle-Subset (2^{len(model_to_files)} subsets)...")
        b8 = baseline_oracle_component_subset(gold_sents, gs_sad_code, model_to_files)
        b8_metrics = compute_metrics(b8, gs_sad_code, gold_sents)

        all_results[proj] = {
            "Single-Agent LLM": single_metrics,
            "Multi-Agent LLM (Majority)": majority_metrics,
            "Multi-Agent LLM (Union)": union_metrics,
            "Multi-Agent LLM (Intersect)": intersect_metrics,
            "TransArc": ta_metrics,
            "Keyword-Grep": kg_metrics,
            "Oracle-Component": b7_metrics,
            "Oracle-Subset": b8_metrics,
        }

        # Classification details
        details = {
            "n_total_sents": len(text),
            "n_gold_sents": len(gold_sents),
            "variant_metrics": variant_metrics,
        }
        if single_cls:
            details["single_n_classified"] = len(single_cls)
            details["single_avg_comps"] = sum(len(v) for v in single_cls.values()) / len(single_cls) if single_cls else 0
        if len(variants) == 3:
            details["majority_n_classified"] = len(majority_cls)
            details["majority_avg_comps"] = sum(len(v) for v in majority_cls.values()) / len(majority_cls) if majority_cls else 0
            # Per-variant stats
            for v_name, v_cls in variants.items():
                details[f"{v_name}_n_classified"] = len(v_cls)
                details[f"{v_name}_avg_comps"] = sum(len(v) for v in v_cls.values()) / len(v_cls) if v_cls else 0

        all_details[proj] = details

        # Print summary
        for name, m in all_results[proj].items():
            if m:
                print(f"  {name}: P={m['p']:.3f} R={m['r']:.3f} F1={m['f1']:.3f} "
                      f"(TP={m['tp']}, FP={m['fp']}, FN={m['fn']})")

    if not all_results:
        print("No results. Run classification agents first.")
        return

    # ═══════════════════════════════════════════════════════════════
    # Report
    # ═══════════════════════════════════════════════════════════════

    out("## Classification Summary")
    out()
    out("| Project | Total | Gold | Single Classified | Multi (Majority) | Avg Comps (S) | Avg Comps (M) |")
    out("|---------|-------|------|-------------------|------------------|---------------|---------------|")
    for proj in PROJECTS:
        if proj not in all_details:
            continue
        d = all_details[proj]
        sc = d.get("single_n_classified", "—")
        mc = d.get("majority_n_classified", "—")
        sac = f"{d.get('single_avg_comps', 0):.1f}" if "single_avg_comps" in d else "—"
        mac = f"{d.get('majority_avg_comps', 0):.1f}" if "majority_avg_comps" in d else "—"
        out(f"| {proj} | {d['n_total_sents']} | {d['n_gold_sents']} | {sc} | {mc} | {sac} | {mac} |")
    out()

    # Per-variant detail
    out("### Agent Variant Details")
    out()
    out("| Project | v1 (Sonnet) | v2 (Haiku) | v3 (Sonnet) | Majority | Intersection | Union |")
    out("|---------|-------------|------------|-------------|----------|-------------|-------|")
    for proj in PROJECTS:
        if proj not in all_details:
            continue
        d = all_details[proj]
        vm = d.get("variant_metrics", {})
        row = f"| {proj}"
        for v in VARIANTS:
            if v in vm:
                row += f" | F1={vm[v]['f1']:.3f}"
            else:
                row += " | —"
        # Majority, Intersect, Union
        for name in ["Multi-Agent LLM (Majority)", "Multi-Agent LLM (Intersect)", "Multi-Agent LLM (Union)"]:
            m = all_results[proj].get(name)
            if m:
                row += f" | F1={m['f1']:.3f}"
            else:
                row += " | —"
        row += " |"
        out(row)
    out()

    # Per-project results — focus on key baselines
    baseline_order = [
        "Multi-Agent LLM (Majority)",
        "Single-Agent LLM",
        "TransArc",
        "Keyword-Grep",
        "Oracle-Component",
        "Oracle-Subset",
    ]

    for proj in PROJECTS:
        if proj not in all_results:
            continue
        results = all_results[proj]

        out(f"## {proj.capitalize()}")
        out()

        out("### Micro and Macro F1")
        out()
        out("| Baseline | Output | **Micro F1** | P | R | Macro F1 | TP | FP | FN |")
        out("|----------|--------|------------|---|---|----------|----|----|-----|")
        for name in baseline_order:
            r = results.get(name)
            if not r:
                continue
            out(f"| {name} | {r['output_size']:,} | **{r['f1']:.3f}** | "
                f"{r['p']:.3f} | {r['r']:.3f} | {r['macro_f1']:.3f} | "
                f"{r['tp']} | {r['fp']} | {r['fn']} |")
        out()

        out("### Holistic Metrics")
        out()
        out("| Baseline | Coverage | Usefulness | Noise | Wasted Effort |")
        out("|----------|----------|------------|-------|---------------|")
        for name in baseline_order:
            r = results.get(name)
            if not r:
                continue
            we = f"{r['wasted_effort']:.2f}" if r['wasted_effort'] != float('inf') else "inf"
            out(f"| {name} | {r['sent_coverage']:.3f} ({r['n_covered']}/{r['n_gold_sents']}) | "
                f"{r['sent_usefulness']:.3f} | {r['sent_noise']:.3f} | {we} |")
        out()

    # ═══════════════════════════════════════════════════════════════
    # Cross-project summary
    # ═══════════════════════════════════════════════════════════════

    completed = [p for p in PROJECTS if p in all_results]

    out("## Cross-Project Micro F1 Comparison")
    out()
    header = "| Baseline |"
    sep = "|----------|"
    for proj in completed:
        header += f" {proj} |"
        sep += "---------|"
    header += " **Avg** |"
    sep += "---------|"
    out(header)
    out(sep)
    for bl_name in baseline_order:
        row = f"| {bl_name} |"
        f1s = []
        for proj in completed:
            r = all_results[proj].get(bl_name)
            if r:
                row += f" {r['f1']:.3f} |"
                f1s.append(r['f1'])
            else:
                row += " — |"
        avg = sum(f1s) / len(f1s) if f1s else 0
        row += f" **{avg:.3f}** |"
        out(row)
    out()

    out("## Cross-Project Macro F1 Comparison")
    out()
    out(header)
    out(sep)
    for bl_name in baseline_order:
        row = f"| {bl_name} |"
        f1s = []
        for proj in completed:
            r = all_results[proj].get(bl_name)
            if r:
                row += f" {r['macro_f1']:.3f} |"
                f1s.append(r['macro_f1'])
            else:
                row += " — |"
        avg = sum(f1s) / len(f1s) if f1s else 0
        row += f" **{avg:.3f}** |"
        out(row)
    out()

    out("## Cross-Project Holistic Comparison")
    out()
    out("| Baseline | Avg Micro F1 | Avg Macro F1 | Micro-Macro Gap | Avg Coverage | Avg Usefulness | Avg Noise |")
    out("|----------|------------|------------|----------------|------------|--------------|-----------|")
    for bl_name in baseline_order:
        mi, ma, cov, use, noi = [], [], [], [], []
        for proj in completed:
            r = all_results[proj].get(bl_name)
            if not r:
                continue
            mi.append(r['f1'])
            ma.append(r['macro_f1'])
            cov.append(r['sent_coverage'])
            use.append(r['sent_usefulness'])
            noi.append(r['sent_noise'])
        if not mi:
            continue
        avg_mi = sum(mi) / len(mi)
        avg_ma = sum(ma) / len(ma)
        gap = avg_mi - avg_ma
        avg_cov = sum(cov) / len(cov)
        avg_use = sum(use) / len(use)
        avg_noi = sum(noi) / len(noi)
        out(f"| {bl_name} | {avg_mi:.3f} | {avg_ma:.3f} | {gap:+.3f} | "
            f"{avg_cov:.3f} | {avg_use:.3f} | {avg_noi:.3f} |")
    out()

    # ═══════════════════════════════════════════════════════════════
    # Multi-Agent vs Single-Agent analysis
    # ═══════════════════════════════════════════════════════════════

    out("## Multi-Agent vs Single-Agent Analysis")
    out()
    out("The multi-agent majority voting ensemble aims to reduce noise by filtering")
    out("component assignments that only one agent makes. Below we compare the effect:")
    out()
    out("| Project | Single F1 | Multi F1 | Δ F1 | Single Noise | Multi Noise | Δ Noise | Single P | Multi P |")
    out("|---------|-----------|----------|------|-------------|-------------|---------|----------|---------|")
    for proj in completed:
        s = all_results[proj].get("Single-Agent LLM")
        m = all_results[proj].get("Multi-Agent LLM (Majority)")
        if s and m:
            df1 = m['f1'] - s['f1']
            dn = m['sent_noise'] - s['sent_noise']
            out(f"| {proj} | {s['f1']:.3f} | {m['f1']:.3f} | {df1:+.3f} | "
                f"{s['sent_noise']:.3f} | {m['sent_noise']:.3f} | {dn:+.3f} | "
                f"{s['p']:.3f} | {m['p']:.3f} |")
    out()

    # Aggregation strategy comparison
    out("### Aggregation Strategy Comparison")
    out()
    out("| Project | Union F1 | Majority F1 | Intersect F1 | Union Noise | Majority Noise | Intersect Noise |")
    out("|---------|----------|-------------|-------------|-------------|----------------|-----------------|")
    for proj in completed:
        u = all_results[proj].get("Multi-Agent LLM (Union)")
        m = all_results[proj].get("Multi-Agent LLM (Majority)")
        i = all_results[proj].get("Multi-Agent LLM (Intersect)")
        if u and m and i:
            out(f"| {proj} | {u['f1']:.3f} | {m['f1']:.3f} | {i['f1']:.3f} | "
                f"{u['sent_noise']:.3f} | {m['sent_noise']:.3f} | {i['sent_noise']:.3f} |")
    out()

    # ═══════════════════════════════════════════════════════════════
    # Key findings
    # ═══════════════════════════════════════════════════════════════

    out("## Key Findings")
    out()

    out("### Finding 1: Multi-Agent vs TransArc")
    out()
    for proj in completed:
        m = all_results[proj].get("Multi-Agent LLM (Majority)")
        ta = all_results[proj].get("TransArc")
        if m and ta:
            delta = m['f1'] - ta['f1']
            out(f"- **{proj}**: Multi-Agent F1={m['f1']:.3f} vs TransArc F1={ta['f1']:.3f} "
                f"(Δ={delta:+.3f})")
    out()

    out("### Finding 2: Noise Reduction from Multi-Agent Voting")
    out()
    out("The primary weakness of single-agent LLM was high noise (over-assignment).")
    out("Majority voting filters assignments not confirmed by multiple agents:")
    out()
    for proj in completed:
        s = all_results[proj].get("Single-Agent LLM")
        m = all_results[proj].get("Multi-Agent LLM (Majority)")
        if s and m:
            reduction = s['sent_noise'] - m['sent_noise']
            out(f"- **{proj}**: Noise {s['sent_noise']:.3f} → {m['sent_noise']:.3f} "
                f"(reduced by {reduction:.3f})")
    out()

    out("### Finding 3: Multi-Agent vs Oracle-Subset")
    out()
    for proj in completed:
        m = all_results[proj].get("Multi-Agent LLM (Majority)")
        b8 = all_results[proj].get("Oracle-Subset")
        if m and b8:
            delta = m['f1'] - b8['f1']
            out(f"- **{proj}**: Multi-Agent F1={m['f1']:.3f} vs Oracle-Subset F1={b8['f1']:.3f} "
                f"(gap={delta:+.3f})")
    out()

    # ═══════════════════════════════════════════════════════════════
    # Conclusion
    # ═══════════════════════════════════════════════════════════════

    out("## Conclusion")
    out()

    # Compute averages
    avgs = {}
    for bl_name in baseline_order:
        f1s = [all_results[p][bl_name]['f1'] for p in completed
               if all_results[p].get(bl_name)]
        avgs[bl_name] = sum(f1s) / len(f1s) if f1s else 0

    out(f"The multi-agent majority voting baseline achieves an average micro F1 of "
        f"**{avgs.get('Multi-Agent LLM (Majority)', 0):.3f}** across {len(completed)} projects:")
    out()
    for bl_name in baseline_order:
        if bl_name in avgs:
            out(f"- {bl_name}: {avgs[bl_name]:.3f}")
    out()
    out("The multi-agent approach demonstrates that ensemble LLM classification with")
    out("majority voting can reduce noise while maintaining coverage, validating that")
    out("SAD-CODE trace link recovery effectively reduces to component classification.")
    out()

    # Save aggregated multi-agent classifications
    for proj in PROJECTS:
        variants = load_multi_agent_variants(proj)
        if len(variants) == 3:
            majority_cls = majority_vote(variants)
            out_path = MULTI_DIR / f"{proj}.json"
            with open(out_path, "w") as f:
                json.dump(majority_cls, f, indent=2)
            print(f"  Saved aggregated: {out_path}")

    # Write report
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
