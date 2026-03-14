#!/usr/bin/env python3
"""
Deep Error Analysis of LLM Adaptive Component Classification.

Goes beyond surface-level FP/FN counts to understand:
1. Per-agent disagreement analysis (where do v1/v2/v3 diverge?)
2. Confusion matrix (which components get confused with which?)
3. Error taxonomy (WHY does each error happen?)
4. Gold standard quality (are FPs actually debatable?)
5. TransArc comparison (do both systems fail on same sentences?)
6. Amplification chains (component error → file-level impact)
7. Sentence difficulty ranking
8. Strategy impact analysis (what happens under each strategy?)

Outputs: LLM_DEEP_ERROR_ANALYSIS.md
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_maps, load_gs_sad_code_enrolled,
    load_result_sad_code, load_transarc_intermediate_sad_sam,
    load_text, load_model_element_names, calc_metrics,
)
from llm_agentic_eval import (
    load_json, majority_vote, intersection_vote,
    build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
    SINGLE_DIR, MULTI_DIR, VARIANTS,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/LLM_DEEP_ERROR_ANALYSIS.md")

ADAPTIVE_STRATEGIES = {
    "mediastore": "majority",
    "teastore": "intersection",
    "teammates": "intersection",
    "bigbluebutton": "majority",
    "jabref": "single",
}


def load_all_strategies(proj):
    """Load all strategy outputs for a project."""
    variants = {}
    for v in VARIANTS:
        path = MULTI_DIR / f"{proj}_{v}.json"
        if path.exists():
            variants[v] = load_json(path)

    results = {}
    # Single agent
    try:
        results["single"] = load_json(SINGLE_DIR / f"{proj}.json")
    except FileNotFoundError:
        pass

    if len(variants) == 3:
        results["majority"] = majority_vote(variants)
        results["intersection"] = intersection_vote(variants)

    results["variants"] = variants
    return results


def gold_sad_code_to_component_level(gs_sad_code, model_to_files, names):
    """Convert file-level gold to component-level per sentence."""
    file_to_comps = defaultdict(set)
    for ae_id, files in model_to_files.items():
        comp_name = names.get(ae_id, ae_id)
        for f in files:
            file_to_comps[f].add(comp_name)

    sent_comps = defaultdict(set)
    for s, f in gs_sad_code:
        for comp in file_to_comps.get(f, set()):
            sent_comps[s].add(comp)
    return dict(sent_comps)


def classify_error(sent_text, fp_comp, gold_comps, proj):
    """Classify an FP error into a category."""
    comp_lower = fp_comp.lower()
    text_lower = sent_text.lower()

    # Interface blind spot
    if fp_comp.startswith("Interface:"):
        return "interface_fn"
    if "interface:" in comp_lower:
        return "interface_fp"

    # Check if there's a matching component/interface pair
    if fp_comp.startswith("Component:"):
        base_name = fp_comp.replace("Component: ", "")
        interface_name = f"Interface: {base_name}"
        if interface_name in gold_comps:
            return "comp_assigned_but_interface_gold"

    # Behavioral description (no gold at all for this sentence)
    if not gold_comps:
        return "behavioral_overclassification"

    # Component name appears in text but wrong assignment
    comp_short = fp_comp.split(": ", 1)[1] if ": " in fp_comp else fp_comp
    words = [w.lower() for w in comp_short.replace("-", " ").replace("_", " ").split() if len(w) >= 3]
    if any(w in text_lower for w in words):
        return "keyword_triggered"

    return "semantic_confusion"


def main():
    lines = []
    w = lines.append

    w("# Deep Error Analysis: LLM Adaptive Component Classification")
    w("")
    w("---")
    w("")

    # Global tallies
    global_error_types = Counter()
    global_fp_file_impact = Counter()
    global_fn_file_impact = Counter()
    all_project_data = {}

    for proj in PROJECTS:
        w(f"## {proj.capitalize()}")
        w("")

        # ─── Load data ──────────────────────────────────────────────
        code_model = load_code_model_files(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        text = load_text(proj)
        names = load_model_element_names(proj)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        # TransArc data
        transarc_sad_sam = load_transarc_intermediate_sad_sam(proj)
        transarc_sad_code = load_result_sad_code(proj)

        # Gold at component level
        gold_comp = gold_sad_code_to_component_level(gs_sad_code, model_to_files, names)
        gold_sents = set(s for s, _ in gs_sad_code)

        # Load all strategies
        strategies = load_all_strategies(proj)
        adaptive_key = ADAPTIVE_STRATEGIES[proj]
        adaptive_cls = strategies[adaptive_key]

        # TransArc at component level
        transarc_comp = defaultdict(set)
        for comp_id, sent in transarc_sad_sam:
            comp_name = names.get(comp_id, comp_id)
            transarc_comp[sent].add(comp_name)

        # LLM at component level
        llm_comp = defaultdict(set)
        for s, comp_names in adaptive_cls.items():
            for c in comp_names:
                llm_comp[s].add(c)

        # ─── 1. Strategy Comparison ─────────────────────────────────
        w("### 1. Strategy Comparison")
        w("")
        w("| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |")
        w("|:--|---:|---:|---:|---:|:---:|")

        for strat_name in ["single", "majority", "intersection"]:
            if strat_name not in strategies:
                continue
            cls = strategies[strat_name]
            strat_comp = defaultdict(set)
            for s, comp_names in cls.items():
                for c in comp_names:
                    strat_comp[s].add(c)

            s_tp = s_fp = s_fn = 0
            for s in gold_sents | set(strat_comp.keys()):
                g = gold_comp.get(s, set())
                p = strat_comp.get(s, set())
                s_tp += len(g & p)
                s_fp += len(p - g)
                s_fn += len(g - p)

            # File-level
            result_set, _ = classifications_to_result_set(cls, name_to_ids, model_to_files)
            _, _, f1, _, _, _ = calc_metrics(gs_sad_code, result_set)
            marker = " **" if strat_name == adaptive_key else ""
            w(f"| {strat_name}{marker} | {len(cls)} | {s_tp} | {s_fp} | {s_fn} | {f1:.3f} |")
        w("")

        # ─── 2. Per-Agent Disagreement Analysis ─────────────────────
        w("### 2. Per-Agent Disagreement")
        w("")
        variants = strategies.get("variants", {})
        if len(variants) == 3:
            # Build per-sentence agreement map
            agent_predictions = {}
            for v_name, v_cls in variants.items():
                for s, comps in v_cls.items():
                    for c in comps:
                        agent_predictions.setdefault((s, c), set()).add(v_name)

            agree_3 = 0  # all 3 agree
            agree_2 = 0  # 2/3 agree
            agree_1 = 0  # only 1
            disagree_details = []

            for (s, c), agents in agent_predictions.items():
                gold_c = gold_comp.get(s, set())
                is_gold = c in gold_c
                if len(agents) == 3:
                    agree_3 += 1
                elif len(agents) == 2:
                    agree_2 += 1
                    if not is_gold:
                        disagree_details.append((s, c, len(agents), "FP", agents))
                    else:
                        disagree_details.append((s, c, len(agents), "TP-partial", agents))
                else:
                    agree_1 += 1
                    if is_gold:
                        disagree_details.append((s, c, len(agents), "FN-risk", agents))

            total = agree_3 + agree_2 + agree_1
            w(f"- All 3 agree: {agree_3} ({agree_3/max(1,total)*100:.1f}%)")
            w(f"- 2/3 agree: {agree_2} ({agree_2/max(1,total)*100:.1f}%)")
            w(f"- Only 1: {agree_1} ({agree_1/max(1,total)*100:.1f}%)")
            w("")

            # Impact of voting threshold
            # What does intersection lose that majority keeps?
            majority_set = set()
            intersection_set = set()
            for (s, c), agents in agent_predictions.items():
                if len(agents) >= 2:
                    majority_set.add((s, c))
                if len(agents) == 3:
                    intersection_set.add((s, c))

            lost_by_intersection = majority_set - intersection_set
            lost_tp = 0
            lost_fp = 0
            for s, c in lost_by_intersection:
                if c in gold_comp.get(s, set()):
                    lost_tp += 1
                else:
                    lost_fp += 1

            w(f"**Intersection vs Majority:** Intersection drops {len(lost_by_intersection)} pairs "
              f"({lost_tp} TPs lost, {lost_fp} FPs removed)")
            tp_fp_ratio = lost_fp / max(1, lost_tp)
            w(f"FP/TP removal ratio: {tp_fp_ratio:.2f} (>{1:.0f} means intersection helps)")
            w("")

            # Gold links only predicted by 1 agent (would be lost by both majority and intersection)
            gold_only_1 = []
            all_gold_pairs = set()
            for s, comps in gold_comp.items():
                for c in comps:
                    all_gold_pairs.add((s, c))
            for s, c in all_gold_pairs:
                agents = agent_predictions.get((s, c), set())
                if len(agents) <= 1:
                    gold_only_1.append((s, c, agents))

            w(f"**Gold links predicted by ≤1 agent:** {len(gold_only_1)}/{len(all_gold_pairs)} "
              f"({len(gold_only_1)/max(1,len(all_gold_pairs))*100:.1f}%) — irretrievable by voting")
            if gold_only_1[:5]:
                w("")
                w("| Sent | Component | Agents | Sentence Text |")
                w("|---:|:--|:--|:--|")
                for s, c, agents in sorted(gold_only_1, key=lambda x: int(x[0]))[:10]:
                    agent_str = ",".join(sorted(agents)) if agents else "none"
                    txt = text.get(s, "")[:80] + ("..." if len(text.get(s, "")) > 80 else "")
                    w(f"| {s} | {c} | {agent_str} | {txt} |")
            w("")

        # ─── 3. Error Taxonomy ──────────────────────────────────────
        w("### 3. Error Taxonomy")
        w("")
        error_types = Counter()
        error_examples = defaultdict(list)

        all_eval_sents = sorted(gold_sents | set(llm_comp.keys()), key=lambda x: int(x))

        for s in all_eval_sents:
            g = gold_comp.get(s, set())
            p = llm_comp.get(s, set())
            fp_comps = p - g
            fn_comps = g - p

            sent_text = text.get(s, "")

            for c in fp_comps:
                err_type = classify_error(sent_text, c, g, proj)
                error_types[err_type] += 1
                # Count file impact
                ae_ids = name_to_ids.get(c, set())
                fp_files = set()
                for ae_id in ae_ids:
                    fp_files |= model_to_files.get(ae_id, set())
                gold_files = set(f for ss, f in gs_sad_code if ss == s)
                fp_files -= gold_files
                if len(error_examples[err_type]) < 3:
                    error_examples[err_type].append({
                        "sent": s, "comp": c, "gold": sorted(g),
                        "text": sent_text[:100], "file_impact": len(fp_files)
                    })

            for c in fn_comps:
                if c.startswith("Interface:"):
                    # Check if matching Component was assigned
                    base = c.replace("Interface: ", "")
                    if f"Component: {base}" in p:
                        error_types["interface_covered_by_component"] += 1
                    else:
                        error_types["interface_missed_entirely"] += 1
                elif s not in llm_comp or not llm_comp[s]:
                    error_types["sentence_not_classified"] += 1
                else:
                    error_types["component_missed"] += 1

        global_error_types += error_types

        w("| Error Type | Count | Description |")
        w("|:--|---:|:--|")
        type_descriptions = {
            "behavioral_overclassification": "Sentence has no gold links but LLM assigns a component",
            "keyword_triggered": "Component name keyword appears in text, triggers wrong assignment",
            "semantic_confusion": "LLM infers wrong component from context (no keyword match)",
            "interface_covered_by_component": "Interface FN but matching Component was assigned (no file impact)",
            "interface_missed_entirely": "Interface FN and no matching Component either",
            "sentence_not_classified": "Gold sentence not classified at all by LLM",
            "component_missed": "Component FN (sentence classified but this component missed)",
        }
        for err_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            desc = type_descriptions.get(err_type, err_type)
            w(f"| {err_type} | {count} | {desc} |")
        w("")

        # Show examples for each FP type
        for err_type in ["behavioral_overclassification", "keyword_triggered", "semantic_confusion"]:
            examples = error_examples.get(err_type, [])
            if examples:
                w(f"**{err_type} examples:**")
                w("")
                for ex in examples:
                    w(f"- Sent {ex['sent']}: assigned `{ex['comp']}`, gold={ex['gold']}, "
                      f"file impact={ex['file_impact']}")
                    w(f"  > {ex['text']}...")
                w("")

        # ─── 4. Confusion Matrix ────────────────────────────────────
        w("### 4. Component Confusion Matrix")
        w("")

        # For each FP, what was the gold and what was wrongly assigned?
        confusion = Counter()  # (gold_comp, wrongly_assigned) → count
        fp_no_gold = Counter()  # wrongly_assigned → count (when sentence has no gold)

        for s in all_eval_sents:
            g = gold_comp.get(s, set())
            p = llm_comp.get(s, set())
            fps = p - g
            if not fps:
                continue
            if not g:
                for c in fps:
                    fp_no_gold[c] += 1
            else:
                for fp_c in fps:
                    for gold_c in g:
                        confusion[(gold_c, fp_c)] += 1

        if confusion:
            w("**When gold has components, LLM wrongly adds:**")
            w("")
            w("| Gold Component | Wrongly Assigned | Count |")
            w("|:--|:--|---:|")
            for (gold_c, wrong_c), count in sorted(confusion.items(), key=lambda x: -x[1])[:15]:
                w(f"| {gold_c} | {wrong_c} | {count} |")
            w("")

        if fp_no_gold:
            w("**Sentence has no gold, LLM assigns:**")
            w("")
            w("| Wrongly Assigned | Count |")
            w("|:--|---:|")
            for comp, count in sorted(fp_no_gold.items(), key=lambda x: -x[1])[:10]:
                w(f"| {comp} | {count} |")
            w("")

        # ─── 5. TransArc vs LLM Error Overlap ──────────────────────
        w("### 5. TransArc vs LLM: Error Overlap")
        w("")

        # Find sentences where both fail, only one fails, etc.
        both_correct = 0
        llm_only_correct = 0
        transarc_only_correct = 0
        both_wrong = 0
        llm_fp_only = 0
        transarc_fp_only = 0

        for s in gold_sents:
            g = gold_comp.get(s, set())
            l = llm_comp.get(s, set())
            t = transarc_comp.get(s, set())

            l_correct = (l & g) == g and not (l - g)  # exact match
            t_correct = (t & g) == g and not (t - g)

            if l_correct and t_correct:
                both_correct += 1
            elif l_correct and not t_correct:
                llm_only_correct += 1
            elif not l_correct and t_correct:
                transarc_only_correct += 1
            else:
                both_wrong += 1

        total_gold = len(gold_sents)
        w(f"| Category | Count | % |")
        w(f"|:--|---:|:---:|")
        w(f"| Both exactly correct | {both_correct} | {both_correct/max(1,total_gold)*100:.1f}% |")
        w(f"| LLM correct, TransArc wrong | {llm_only_correct} | {llm_only_correct/max(1,total_gold)*100:.1f}% |")
        w(f"| TransArc correct, LLM wrong | {transarc_only_correct} | {transarc_only_correct/max(1,total_gold)*100:.1f}% |")
        w(f"| Both wrong | {both_wrong} | {both_wrong/max(1,total_gold)*100:.1f}% |")
        w("")

        # Complementarity: if we could combine, how many sentences could we get right?
        combo_correct = both_correct + llm_only_correct + transarc_only_correct
        w(f"**Complementarity:** If we took the better answer per sentence, "
          f"{combo_correct}/{total_gold} ({combo_correct/max(1,total_gold)*100:.1f}%) would be exact-match correct "
          f"(vs LLM={both_correct+llm_only_correct}, TransArc={both_correct+transarc_only_correct})")
        w("")

        # Shared FP components (both systems assign same wrong component)
        shared_fps = Counter()
        for s in all_eval_sents:
            g = gold_comp.get(s, set())
            l_fp = llm_comp.get(s, set()) - g
            t_fp = transarc_comp.get(s, set()) - g
            for c in l_fp & t_fp:
                shared_fps[c] += 1

        if shared_fps:
            w("**Shared FP components (both systems assign wrong):**")
            w("")
            for c, count in sorted(shared_fps.items(), key=lambda x: -x[1])[:5]:
                w(f"- `{c}`: {count} sentences")
            w("")

        # ─── 6. Sentence Difficulty Ranking ─────────────────────────
        w("### 6. Hardest Sentences")
        w("")

        sent_difficulty = []
        for s in gold_sents:
            g = gold_comp.get(s, set())
            l = llm_comp.get(s, set())
            t = transarc_comp.get(s, set())

            l_tp = len(g & l); l_fp = len(l - g); l_fn = len(g - l)
            t_tp = len(g & t); t_fp = len(t - g); t_fn = len(g - t)

            # Difficulty score: number of errors across both systems
            difficulty = l_fp + l_fn + t_fp + t_fn
            if difficulty > 0:
                sent_difficulty.append((s, g, l, t, difficulty, l_fp, l_fn, t_fp, t_fn))

        sent_difficulty.sort(key=lambda x: -x[4])

        w(f"Top 10 hardest sentences (most errors across LLM + TransArc):")
        w("")
        w("| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |")
        w("|---:|---:|---:|---:|---:|---:|:--|")
        for s, g, l, t, diff, lfp, lfn, tfp, tfn in sent_difficulty[:10]:
            txt = text.get(s, "")[:60] + "..."
            w(f"| {s} | {len(g)} | {lfp} | {lfn} | {tfp} | {tfn} | {txt} |")
        w("")

        # ─── 7. Amplification Analysis ──────────────────────────────
        w("### 7. Error Amplification")
        w("")

        # For each component, compute amplification factor
        comp_sizes = {}
        for ae_id, files in model_to_files.items():
            comp_name = names.get(ae_id, ae_id)
            comp_sizes[comp_name] = len(files)

        w("| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |")
        w("|:--|---:|---:|---:|---:|---:|---:|---:|")

        comp_fp = Counter()
        comp_fn = Counter()
        comp_fp_files = Counter()
        comp_fn_files = Counter()

        for s in all_eval_sents:
            g = gold_comp.get(s, set())
            p = llm_comp.get(s, set())
            for c in p - g:
                comp_fp[c] += 1
                ae_ids = name_to_ids.get(c, set())
                fp_f = set()
                for ae_id in ae_ids:
                    fp_f |= model_to_files.get(ae_id, set())
                gold_f = set(f for ss, f in gs_sad_code if ss == s)
                fp_f -= gold_f
                comp_fp_files[c] += len(fp_f)
            for c in g - p:
                comp_fn[c] += 1
                ae_ids = name_to_ids.get(c, set())
                fn_f = set()
                for ae_id in ae_ids:
                    fn_f |= model_to_files.get(ae_id, set())
                gold_f = set(f for ss, f in gs_sad_code if ss == s)
                fn_f &= gold_f
                comp_fn_files[c] += len(fn_f)

        all_comps_with_errors = sorted(set(comp_fp.keys()) | set(comp_fn.keys()))
        for c in all_comps_with_errors:
            n_files = comp_sizes.get(c, 0)
            fp = comp_fp[c]
            fp_f = comp_fp_files[c]
            fn = comp_fn[c]
            fn_f = comp_fn_files[c]
            amp_fp = f"{fp_f/max(1,fp):.1f}" if fp > 0 else "—"
            amp_fn = f"{fn_f/max(1,fn):.1f}" if fn > 0 else "—"
            if fp > 0 or fn > 0:
                w(f"| {c} | {n_files} | {fp} | {fp_f} | {amp_fp}x | {fn} | {fn_f} | {amp_fn}x |")
        w("")

        # ─── 8. Gold Standard Quality Check ─────────────────────────
        w("### 8. Gold Standard Quality Check")
        w("")
        w("FP sentences where the LLM's assignment seems reasonable:")
        w("")

        debatable = []
        for s in all_eval_sents:
            g = gold_comp.get(s, set())
            p = llm_comp.get(s, set())
            fps = p - g
            if not fps:
                continue
            sent_text = text.get(s, "")
            for c in fps:
                comp_short = c.split(": ", 1)[1] if ": " in c else c
                words = [w.lower() for w in comp_short.replace("-", " ").replace("_", " ").split()
                         if len(w) >= 3]
                # Check if component name explicitly mentioned in sentence
                if any(w in sent_text.lower() for w in words):
                    debatable.append((s, c, g, sent_text))

        if debatable:
            w("| Sent | LLM Assigned (FP) | Gold Components | Sentence Text |")
            w("|---:|:--|:--|:--|")
            for s, c, g, txt in debatable[:15]:
                txt_short = txt[:80] + ("..." if len(txt) > 80 else "")
                w(f"| {s} | {c} | {sorted(g)} | {txt_short} |")
        else:
            w("No debatable FPs found.")
        w("")

        # Store for global summary
        all_project_data[proj] = {
            "error_types": error_types,
            "both_correct": both_correct,
            "llm_only": llm_only_correct,
            "ta_only": transarc_only_correct,
            "both_wrong": both_wrong,
            "total_gold": total_gold,
            "comp_fp": dict(comp_fp),
            "comp_fn": dict(comp_fn),
            "comp_fp_files": dict(comp_fp_files),
            "comp_fn_files": dict(comp_fn_files),
        }

        w("---")
        w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Cross-Project Summary
    # ═══════════════════════════════════════════════════════════════════════
    w("## Cross-Project Summary")
    w("")

    # ─── Error type distribution ─────────────────────────────────
    w("### Error Type Distribution (all projects)")
    w("")
    w("| Error Type | Total | % of All Errors |")
    w("|:--|---:|:---:|")
    total_errors = sum(global_error_types.values())
    for err_type, count in sorted(global_error_types.items(), key=lambda x: -x[1]):
        pct = count / max(1, total_errors) * 100
        w(f"| {err_type} | {count} | {pct:.1f}% |")
    w(f"| **Total** | **{total_errors}** | |")
    w("")

    # ─── Complementarity across projects ─────────────────────────
    w("### TransArc vs LLM Complementarity")
    w("")
    w("| Project | Both OK | LLM Only | TransArc Only | Both Wrong | Combo Ceiling |")
    w("|:--|---:|---:|---:|---:|:---:|")
    total_bc = total_lo = total_to = total_bw = total_g = 0
    for proj in PROJECTS:
        d = all_project_data[proj]
        combo = d["both_correct"] + d["llm_only"] + d["ta_only"]
        pct = combo / max(1, d["total_gold"]) * 100
        w(f"| {proj} | {d['both_correct']} | {d['llm_only']} | {d['ta_only']} | {d['both_wrong']} | {pct:.1f}% |")
        total_bc += d["both_correct"]
        total_lo += d["llm_only"]
        total_to += d["ta_only"]
        total_bw += d["both_wrong"]
        total_g += d["total_gold"]
    combo_total = total_bc + total_lo + total_to
    w(f"| **Total** | {total_bc} | {total_lo} | {total_to} | {total_bw} | {combo_total/max(1,total_g)*100:.1f}% |")
    w("")

    w("**Insight:** The two systems are partially complementary. An oracle combiner "
      f"that picks the better system per sentence would achieve {combo_total/max(1,total_g)*100:.1f}% "
      f"exact-match accuracy (vs LLM alone: {(total_bc+total_lo)/max(1,total_g)*100:.1f}%, "
      f"TransArc alone: {(total_bc+total_to)/max(1,total_g)*100:.1f}%).")
    w("")

    # ─── Top error sources by file impact ────────────────────────
    w("### Top Error Sources by File Impact")
    w("")
    all_comp_fp_files = Counter()
    all_comp_fn_files = Counter()
    for proj in PROJECTS:
        d = all_project_data[proj]
        for c, v in d["comp_fp_files"].items():
            all_comp_fp_files[f"{proj}:{c}"] += v
        for c, v in d["comp_fn_files"].items():
            all_comp_fn_files[f"{proj}:{c}"] += v

    w("**Largest FP sources (file-level):**")
    w("")
    w("| Project:Component | File FPs | Comp FPs |")
    w("|:--|---:|---:|")
    for key, v in sorted(all_comp_fp_files.items(), key=lambda x: -x[1])[:10]:
        proj_name, comp = key.split(":", 1)
        comp_fp_count = all_project_data[proj_name]["comp_fp"].get(comp, 0)
        w(f"| {key} | {v} | {comp_fp_count} |")
    w("")

    w("**Largest FN sources (file-level):**")
    w("")
    w("| Project:Component | File FNs | Comp FNs |")
    w("|:--|---:|---:|")
    for key, v in sorted(all_comp_fn_files.items(), key=lambda x: -x[1])[:10]:
        proj_name, comp = key.split(":", 1)
        comp_fn_count = all_project_data[proj_name]["comp_fn"].get(comp, 0)
        w(f"| {key} | {v} | {comp_fn_count} |")
    w("")

    # ─── Actionable recommendations ──────────────────────────────
    w("### Actionable Recommendations")
    w("")

    # Based on error type distribution
    top_error = global_error_types.most_common(3)
    w("Based on error frequency analysis:")
    w("")
    for i, (err_type, count) in enumerate(top_error, 1):
        pct = count / max(1, total_errors) * 100
        if err_type == "interface_covered_by_component":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): No action needed — "
              f"Interface FNs where Component was correctly assigned have zero file impact "
              f"(files fully overlap). This is a gold standard artifact, not a real error.")
        elif err_type == "behavioral_overclassification":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): Add a relevance filter — "
              f"these sentences describe component behavior but have no code trace links. "
              f"A pre-classification step asking 'does this sentence describe code-traceable "
              f"architecture?' would filter these.")
        elif err_type == "component_missed":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): Improve recall — "
              f"the intersection strategy is too aggressive for projects with many components. "
              f"Consider adaptive threshold: use majority for >15 components.")
        elif err_type == "sentence_not_classified":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): Coverage gap — "
              f"gold sentences that no agent classifies. These may be implicit references "
              f"that require coreference resolution or context window expansion.")
        elif err_type == "keyword_triggered":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): False keyword matches — "
              f"component name appears in text but refers to concept, not component. "
              f"Add disambiguation: 'Does this sentence reference the {'{'}component{'}'} "
              f"software component, or just the general concept?'")
        elif err_type == "interface_missed_entirely":
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%): Interface-aware prompting — "
              f"include Interface names in all agent prompts, not just Component names.")
        else:
            w(f"{i}. **{err_type}** ({count}, {pct:.0f}%)")
    w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 llm_deep_error_analysis.py")
    w("# Output: LLM_DEEP_ERROR_ANALYSIS.md")
    w("```")

    # ─── Write output ────────────────────────────────────────────
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWritten to {OUTPUT_MD}")

    # Console summary
    print("\n" + "=" * 80)
    print("ERROR TYPE DISTRIBUTION (all projects)")
    print("=" * 80)
    for err_type, count in sorted(global_error_types.items(), key=lambda x: -x[1]):
        pct = count / max(1, total_errors) * 100
        print(f"  {err_type:<45} {count:>4} ({pct:.1f}%)")

    print(f"\nCOMPLEMENTARITY (LLM + TransArc oracle combiner):")
    print(f"  Both correct:      {total_bc:>4}")
    print(f"  LLM only correct:  {total_lo:>4}")
    print(f"  TransArc only:     {total_to:>4}")
    print(f"  Both wrong:        {total_bw:>4}")
    print(f"  Combo ceiling:     {combo_total/max(1,total_g)*100:.1f}%")


if __name__ == "__main__":
    main()
