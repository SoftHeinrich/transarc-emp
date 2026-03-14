#!/usr/bin/env python3
"""
Error analysis of LLM component classifications vs gold standard.
Identifies:
1. Component-level FPs and FNs per sentence
2. File-level impact (how many file-level FPs/FNs each component error causes)
3. Patterns in errors (which components are confused)
4. Sentence text for misclassified sentences
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, load_code_model_files, enroll_gold_standard,
    load_gs_sam_code_raw, load_gs_sad_code_enrolled,
    load_model_element_names, load_text,
)
from llm_agentic_eval import (
    load_json, majority_vote, intersection_vote,
    build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
    SINGLE_DIR, MULTI_DIR, VARIANTS,
)
from extreme_baseline_analysis import compute_metrics


def reverse_map_gold_to_components(gs_sad_code, model_to_files, names):
    """For each sentence in gold, find which components' files are linked."""
    # Build file→component map
    file_to_comps = defaultdict(set)
    id_to_name = {ae_id: ae_name for ae_id, ae_name in names.items()}
    for ae_id, files in model_to_files.items():
        comp_name = id_to_name.get(ae_id, ae_id)
        for f in files:
            file_to_comps[f].add(comp_name)

    # For each sentence, which components have gold files?
    sent_gold_comps = defaultdict(set)
    sent_gold_files = defaultdict(set)
    for s, f in gs_sad_code:
        sent_gold_files[s].add(f)
        for comp in file_to_comps.get(f, set()):
            sent_gold_comps[s].add(comp)

    return dict(sent_gold_comps), dict(sent_gold_files), dict(file_to_comps)


def get_best_classification(proj, variants):
    """Get the best (adaptive) classification for a project."""
    # Strategy from the evaluation results
    best_strategy = {
        "mediastore": "majority",
        "teastore": "intersect",
        "teammates": "intersect",
        "bigbluebutton": "majority",
        "jabref": "single",
    }
    strat = best_strategy.get(proj, "majority")

    if strat == "single":
        return load_json(SINGLE_DIR / f"{proj}.json"), "Single-Agent"
    elif strat == "majority":
        return majority_vote(variants), "Multi-Agent Majority"
    elif strat == "intersect":
        return intersection_vote(variants), "Multi-Agent Intersect"


def main():
    focus_projects = ["teastore", "teammates", "bigbluebutton"]
    print("=" * 80)
    print("LLM COMPONENT CLASSIFICATION ERROR ANALYSIS")
    print("Focus: projects where TransArc beats LLM")
    print("=" * 80)

    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        names_raw = load_model_element_names(proj)
        text = load_text(proj)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gold_sents = set(s for s, _ in gs_sad_code)
        gold_sents_sorted = sorted(gold_sents)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        # Reverse map: gold files → components
        sent_gold_comps, sent_gold_files, file_to_comps = \
            reverse_map_gold_to_components(gs_sad_code, model_to_files, names_raw)

        # Get LLM classification (best strategy)
        variants = {}
        for v in VARIANTS:
            path = MULTI_DIR / f"{proj}_{v}.json"
            if path.exists():
                variants[v] = load_json(path)

        llm_cls, strat_name = get_best_classification(proj, variants)

        # Convert LLM to component-level per sentence
        llm_sent_comps = defaultdict(set)
        for s, comp_names in llm_cls.items():
            for c in comp_names:
                llm_sent_comps[s].add(c)

        # Also compute file-level result
        llm_result, unmatched = classifications_to_result_set(llm_cls, name_to_ids, model_to_files)
        metrics = compute_metrics(llm_result, gs_sad_code, gold_sents)

        print(f"\n{'='*80}")
        print(f"PROJECT: {proj.upper()} (strategy: {strat_name})")
        print(f"File-level: P={metrics['p']:.3f} R={metrics['r']:.3f} F1={metrics['f1']:.3f}")
        print(f"{'='*80}")

        # Component-level error analysis
        comp_fp_count = Counter()  # component → times it was wrongly assigned
        comp_fn_count = Counter()  # component → times it was missed
        comp_tp_count = Counter()  # component → times it was correctly assigned
        comp_fp_file_impact = Counter()  # component → total file-level FPs caused
        comp_fn_file_impact = Counter()  # component → total file-level FNs caused

        fp_sentences = []  # (sentence, wrongly_assigned_comps, gold_comps)
        fn_sentences = []  # (sentence, missed_comps, assigned_comps)

        all_sents = sorted(gold_sents | set(llm_sent_comps.keys()),
                          key=lambda x: int(x))

        for s in all_sents:
            gold_c = sent_gold_comps.get(s, set())
            llm_c = llm_sent_comps.get(s, set())

            # Component-level TP, FP, FN
            tp_comps = gold_c & llm_c
            fp_comps = llm_c - gold_c
            fn_comps = gold_c - llm_c

            for c in tp_comps:
                comp_tp_count[c] += 1

            for c in fp_comps:
                comp_fp_count[c] += 1
                # How many file-level FPs does this cause?
                ae_ids = name_to_ids.get(c, set())
                fp_files = set()
                for ae_id in ae_ids:
                    fp_files |= model_to_files.get(ae_id, set())
                # Remove files that are actually gold for this sentence
                fp_files -= sent_gold_files.get(s, set())
                comp_fp_file_impact[c] += len(fp_files)

            for c in fn_comps:
                comp_fn_count[c] += 1
                # How many file-level FNs does this cause?
                ae_ids = name_to_ids.get(c, set())
                fn_files = set()
                for ae_id in ae_ids:
                    fn_files |= model_to_files.get(ae_id, set())
                # Only count files that are actually gold for this sentence
                fn_files &= sent_gold_files.get(s, set())
                # Remove files covered by other assigned components
                covered_files = set()
                for other_c in tp_comps:
                    for ae_id in name_to_ids.get(other_c, set()):
                        covered_files |= model_to_files.get(ae_id, set())
                fn_files -= covered_files
                comp_fn_file_impact[c] += len(fn_files)

            if fp_comps:
                fp_sentences.append((s, fp_comps, gold_c))
            if fn_comps and s in gold_sents_sorted:
                fn_sentences.append((s, fn_comps, llm_c))

        # Report: Component confusion matrix
        all_comp_names = sorted(set(comp_fp_count.keys()) | set(comp_fn_count.keys())
                               | set(comp_tp_count.keys()))

        print(f"\n--- Component-Level Accuracy ---")
        print(f"{'Component':<45} {'TP':>4} {'FP':>4} {'FN':>4} {'FP-files':>9} {'FN-files':>9}")
        print("-" * 80)
        total_fp_files = 0
        total_fn_files = 0
        for c in sorted(all_comp_names):
            tp = comp_tp_count[c]
            fp = comp_fp_count[c]
            fn = comp_fn_count[c]
            fp_f = comp_fp_file_impact[c]
            fn_f = comp_fn_file_impact[c]
            total_fp_files += fp_f
            total_fn_files += fn_f
            if fp > 0 or fn > 0:
                print(f"  {c:<43} {tp:>4} {fp:>4} {fn:>4} {fp_f:>9} {fn_f:>9}")
        print(f"  {'TOTAL':<43} {'':>4} {sum(comp_fp_count.values()):>4} "
              f"{sum(comp_fn_count.values()):>4} {total_fp_files:>9} {total_fn_files:>9}")

        # Top FP sentences (most damaging)
        if proj in focus_projects:
            print(f"\n--- Top FP Sentences (wrong component assigned) ---")
            # Sort by file impact
            fp_with_impact = []
            for s, fp_comps, gold_c in fp_sentences:
                impact = sum(comp_fp_file_impact.get(c, 0) for c in fp_comps) // max(1, len(fp_sentences))
                fp_with_impact.append((s, fp_comps, gold_c, impact))
            fp_with_impact.sort(key=lambda x: -len(x[1]))

            for s, fp_comps, gold_c, _ in fp_with_impact[:15]:
                sent_text = text.get(s, "???")
                if len(sent_text) > 100:
                    sent_text = sent_text[:100] + "..."
                print(f"  Sent {s:>3}: WRONG={sorted(fp_comps)}")
                print(f"           GOLD ={sorted(gold_c)}")
                print(f"           TEXT: {sent_text}")

            print(f"\n--- Top FN Sentences (missed component) ---")
            fn_with_impact = []
            for s, fn_comps, assigned in fn_sentences:
                fn_with_impact.append((s, fn_comps, assigned))
            fn_with_impact.sort(key=lambda x: -len(x[1]))

            for s, fn_comps, assigned in fn_with_impact[:15]:
                sent_text = text.get(s, "???")
                if len(sent_text) > 100:
                    sent_text = sent_text[:100] + "..."
                print(f"  Sent {s:>3}: MISSED={sorted(fn_comps)}")
                print(f"           ASSIGNED={sorted(assigned)}")
                print(f"           TEXT: {sent_text}")

        # Summary stats
        print(f"\n--- Summary ---")
        print(f"  Gold sentences: {len(gold_sents_sorted)}")
        print(f"  LLM classified: {len(llm_cls)}")
        print(f"  Sentences with FP components: {len(fp_sentences)}")
        print(f"  Sentences with FN components: {len(fn_sentences)}")
        print(f"  Total component-level FPs: {sum(comp_fp_count.values())}")
        print(f"  Total component-level FNs: {sum(comp_fn_count.values())}")
        print(f"  Total file-level FPs caused: {total_fp_files}")
        print(f"  Total file-level FNs caused: {total_fn_files}")
        if unmatched:
            print(f"  Unmatched component names: {unmatched}")

        # Extra: which components have NO errors?
        perfect_comps = [c for c in all_comp_names
                        if comp_fp_count[c] == 0 and comp_fn_count[c] == 0]
        if perfect_comps:
            print(f"  Perfect components: {', '.join(sorted(perfect_comps))}")


if __name__ == "__main__":
    main()
