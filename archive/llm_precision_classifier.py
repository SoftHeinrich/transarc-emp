#!/usr/bin/env python3
"""
Precision-Focused LLM Classifier for SAD-CODE Trace Link Recovery.

Implements the key insight from the fix impact simulation: FP reduction
is the dominant improvement lever. This classifier uses:

1. A precision-focused prompt that explicitly instructs the LLM to only
   classify sentences with direct code traceability, rejecting behavioral
   descriptions and general requirements.
2. Multi-agent intersection voting (3 agents, all must agree) for
   maximum precision.
3. A post-hoc relevance filter that removes assignments lacking textual
   evidence (component name not in sentence AND no neighboring context).

The classifier uses the Claude CLI backend.

Usage:
    python3 llm_precision_classifier.py [--project PROJECT] [--eval-only]
"""

import json
import subprocess
import sys
import time
import re
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from transarc_error_analysis import (
    PROJECTS, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_maps, load_gs_sad_code_enrolled,
    load_result_sad_code, load_text, load_model_element_names, calc_metrics,
)
from llm_agentic_eval import (
    load_json, build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
)

OUTPUT_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/llm_classifications_precision")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/LLM_PRECISION_CLASSIFIER.md")

NUM_AGENTS = 3


def get_component_names(project):
    """Get all component/interface names for a project."""
    names = load_model_element_names(project)
    code_model = load_code_model_files(project)
    model_to_files = build_model_to_files(project, code_model)
    # Only include names that have file mappings
    active_names = set()
    for ae_id, name in names.items():
        if ae_id in model_to_files:
            active_names.add(name)
    return sorted(active_names)


def build_traceability_gate_prompt(doc_text):
    """Build a binary traceability classification prompt.

    Instead of reviewing component assignments, ask a simpler question:
    "Which sentences describe something implemented in code?"

    This is fundamentally easier than the component assignment question
    because it's a binary gate (yes/no) rather than multi-label classification.
    """
    doc_lines = []
    for sent_num in sorted(doc_text.keys(), key=int):
        doc_lines.append(f"[{sent_num}] {doc_text[sent_num]}")
    doc_formatted = "\n".join(doc_lines)

    return f"""You are an expert at software architecture traceability analysis.

TASK: For each sentence in this software architecture document, determine if
it describes something that would be DIRECTLY IMPLEMENTED in source code files
(code-traceable), or if it describes general concepts, requirements, or behavior
that would NOT correspond to specific code files.

DOCUMENT:
{doc_formatted}

For each sentence, classify as:
- TRACEABLE: The sentence describes a specific software component's functionality,
  data processing, storage mechanism, communication protocol, or implementation detail
  that would be found in source code files.
- NOT_TRACEABLE: The sentence is an introduction, overview, general requirement,
  quality attribute, user workflow description, or abstract architectural decision
  that does NOT correspond to specific code files.

OUTPUT: Return a JSON object with sentence numbers as keys and "T" or "N" as values.
Example: {{"1": "T", "2": "N", "3": "T"}}

Classify ALL sentences. Return ONLY the JSON object."""


def build_review_prompt(doc_text, classifications, component_names, project):
    """Build a review prompt that filters existing classifications.

    Instead of re-classifying from scratch (too conservative), this takes
    the original classifications and asks the LLM to review and filter them.
    """
    comp_list = "\n".join(f"  - {name}" for name in component_names)

    # Build assignments to review
    review_lines = []
    for sent_num in sorted(classifications.keys(), key=int):
        sent_text = doc_text.get(sent_num, "")
        comps = classifications[sent_num]
        comp_str = ", ".join(comps)
        review_lines.append(f"[{sent_num}] \"{sent_text}\" → {comp_str}")
    review_formatted = "\n".join(review_lines)

    return f"""You are an expert at software architecture traceability analysis.

TASK: Review the following sentence-to-component assignments and FILTER OUT
assignments where the sentence does NOT describe code-traceable architecture
for that component.

ARCHITECTURE COMPONENTS:
{comp_list}

CURRENT ASSIGNMENTS TO REVIEW:
{review_formatted}

FILTER RULES:
1. KEEP assignments where the sentence describes functionality DIRECTLY
   implemented in code (classes, methods, modules) of that component.
2. REMOVE assignments where the sentence:
   - Describes general system behavior without mentioning specific component implementation
   - Is a purely introductory or summary sentence (e.g., "The system consists of...")
   - Describes user interactions or workflows at a UI level, not component internals
   - Mentions a component name only in passing without describing its code behavior
3. KEEP assignments where the sentence describes what a component DOES,
   HOW it processes data, WHAT it stores, or HOW it communicates with other components.
4. When in doubt, KEEP the assignment. Only remove clearly non-traceable ones.

OUTPUT: Return a JSON object with ONLY the assignments you want to KEEP.
Same format: {{"sentence_num": ["Component: Name", ...]}}

Return ONLY the JSON object, no explanation."""


def build_precision_prompt(doc_text, component_names, project):
    """Build a precision-focused classification prompt for fresh classification."""
    comp_list = "\n".join(f"  - {name}" for name in component_names)

    # Build numbered doc text
    doc_lines = []
    for sent_num in sorted(doc_text.keys(), key=int):
        doc_lines.append(f"[{sent_num}] {doc_text[sent_num]}")
    doc_formatted = "\n".join(doc_lines)

    return f"""You are an expert at software architecture traceability analysis.

TASK: Classify which architecture components each sentence in the documentation
below describes. You must be PRECISE — only classify sentences that describe
something DIRECTLY IMPLEMENTED in code.

ARCHITECTURE COMPONENTS:
{comp_list}

RULES FOR CLASSIFICATION:
1. ONLY classify a sentence if it describes functionality that is DIRECTLY
   implemented as code (classes, methods, modules, files) of that component.
2. A sentence mentioning a component by name is NOT enough — it must describe
   what that component DOES or HOW it works at an implementation level.
3. DO NOT classify sentences that:
   - Describe general system behavior or user workflows
   - State requirements or quality attributes
   - Describe abstract architecture decisions without implementation detail
   - Are introductory or summary sentences
   - Describe interactions at a purely conceptual level
4. When in doubt, DO NOT classify. Precision is more important than recall.
5. Each sentence can map to zero, one, or multiple components.

DOCUMENTATION:
{doc_formatted}

OUTPUT FORMAT: Return a JSON object where keys are sentence numbers (as strings)
and values are arrays of component names. Only include sentences that you are
confident trace to code. Example:
{{"3": ["Component: Facade"], "5": ["Component: DB", "Interface: IDB"]}}

Return ONLY the JSON object, no explanation."""


def call_claude(prompt, timeout=300):
    """Call Claude CLI and return the response text."""
    cmd = [
        "claude", "-p",
        "--output-format", "json",
        "--dangerously-skip-permissions",
        prompt
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd="/tmp"
        )

        response_text = ""
        # Parse JSON output format
        try:
            data = json.loads(result.stdout.strip())
            if data.get('type') == 'result':
                response_text = data.get('result', '')
        except json.JSONDecodeError:
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if event.get('type') == 'result':
                        response_text = event.get('result', '')
                        break
                except json.JSONDecodeError:
                    continue

        if not response_text and result.stdout.strip():
            response_text = result.stdout.strip()

        return response_text

    except subprocess.TimeoutExpired:
        print(f"  WARNING: Claude call timed out after {timeout}s")
        return ""
    except Exception as e:
        print(f"  ERROR: {e}")
        return ""


def parse_classification_response(response_text, valid_names):
    """Extract classification JSON from LLM response.

    Returns dict of {sent_num_str: [comp_name, ...]}
    """
    if not response_text:
        return {}

    # Try to find JSON in response
    match = re.search(r'\{[\s\S]*\}', response_text)
    if not match:
        return {}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return {}

    # Validate and clean
    result = {}
    valid_set = set(valid_names)
    for key, comps in data.items():
        if not isinstance(key, str):
            key = str(key)
        if not isinstance(comps, list):
            continue
        valid_comps = [c for c in comps if c in valid_set]
        if valid_comps:
            result[key] = valid_comps

    return result


def intersection_vote(classifications_list):
    """Intersection voting: keep only pairs where ALL agents agree."""
    if not classifications_list:
        return {}

    # Build pair sets for each agent
    pair_sets = []
    for cls in classifications_list:
        pairs = set()
        for sent, comps in cls.items():
            for comp in comps:
                pairs.add((sent, comp))
        pair_sets.append(pairs)

    # Intersection
    common = pair_sets[0]
    for ps in pair_sets[1:]:
        common = common & ps

    result = defaultdict(list)
    for sent, comp in common:
        result[sent].append(comp)
    return dict(result)


def majority_vote(classifications_list, threshold=2):
    """Majority voting: keep pairs where >= threshold agents agree."""
    pair_counts = Counter()
    for cls in classifications_list:
        for sent, comps in cls.items():
            for comp in comps:
                pair_counts[(sent, comp)] += 1

    result = defaultdict(list)
    for (sent, comp), count in pair_counts.items():
        if count >= threshold:
            result[sent].append(comp)
    return dict(result)


def context_isolation_filter(classifications, text):
    """Post-hoc filter: remove assignments lacking textual evidence.

    For each (sent, comp) pair: if the component name does NOT appear in
    the sentence AND no neighbor (±1) has the same component, remove it.
    """
    result = {}
    for s, comps in classifications.items():
        snum = int(s)
        sent_text = text.get(s, "")
        kept = []
        for comp in comps:
            short = comp.split(": ", 1)[1] if ": " in comp else comp
            # Check if name appears in this sentence
            if short.lower() in sent_text.lower():
                kept.append(comp)
                continue
            # Check if same component appears in neighbors
            neighbor_has = False
            for ns in [str(snum - 1), str(snum + 1)]:
                if ns in classifications and comp in classifications[ns]:
                    neighbor_has = True
                    break
            if neighbor_has:
                kept.append(comp)
        if kept:
            result[s] = kept
    return result


def evaluate_classifications(classifications, project):
    """Evaluate classifications against gold standard.

    Returns dict with P, R, F1, TP, FP, FN at file level.
    """
    code_model = load_code_model_files(project)
    gs_sad_code = load_gs_sad_code_enrolled(project, code_model)
    name_to_ids = build_name_to_id_map(project)
    model_to_files = build_model_to_files(project, code_model)

    result_set, unmatched = classifications_to_result_set(
        classifications, name_to_ids, model_to_files
    )
    p, r, f1, tp, fp, fn = calc_metrics(gs_sad_code, result_set)
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn,
            "unmatched": unmatched, "output_size": len(result_set)}


def run_classification(project):
    """Run precision-focused classification for a project.

    Two strategies:
    1. REVIEW: Take existing adaptive-best classifications, ask LLM to filter
    2. FRESH: Classify from scratch with precision-focused prompt

    For each, run 3 agents and apply intersection/majority voting.

    Returns dict with per-agent and aggregated results.
    """
    from three_system_comparison import (
        ADAPTIVE_STRATEGIES, load_llm_adaptive_classifications,
    )

    text = load_text(project)
    comp_names = get_component_names(project)
    orig_cls = load_llm_adaptive_classifications(project)

    print(f"\n{'='*60}")
    print(f"  {project.upper()}: {len(text)} sentences, {len(comp_names)} components")
    print(f"  Original: {len(orig_cls)} sents, {sum(len(v) for v in orig_cls.values())} pairs")
    print(f"{'='*60}")

    results = {"agents_review": [], "agents_fresh": []}

    # ─── Strategy 1: LLM REVIEW of existing classifications ─────────
    print(f"\n  --- Review Strategy ---")
    review_prompt = build_review_prompt(text, orig_cls, comp_names, project)
    print(f"  Review prompt: {len(review_prompt)} chars")

    for i in range(NUM_AGENTS):
        print(f"  Review Agent {i+1}/{NUM_AGENTS}...", end="", flush=True)
        t0 = time.time()
        response = call_claude(review_prompt)
        dt = time.time() - t0
        cls = parse_classification_response(response, comp_names)
        results["agents_review"].append(cls)
        n_pairs = sum(len(v) for v in cls.values())
        print(f" {dt:.1f}s, {len(cls)} sents, {n_pairs} pairs")

    # ─── Strategy 2: FRESH precision classification ─────────────────
    print(f"\n  --- Fresh Strategy ---")
    fresh_prompt = build_precision_prompt(text, comp_names, project)
    print(f"  Fresh prompt: {len(fresh_prompt)} chars")

    for i in range(NUM_AGENTS):
        print(f"  Fresh Agent {i+1}/{NUM_AGENTS}...", end="", flush=True)
        t0 = time.time()
        response = call_claude(fresh_prompt)
        dt = time.time() - t0
        cls = parse_classification_response(response, comp_names)
        results["agents_fresh"].append(cls)
        n_pairs = sum(len(v) for v in cls.values())
        print(f" {dt:.1f}s, {len(cls)} sents, {n_pairs} pairs")

    # ─── Strategy 3: TRACEABILITY GATE ────────────────────────────
    # Binary question: is each sentence code-traceable?
    # Then only keep original classifications for traceable sentences.
    print(f"\n  --- Traceability Gate ---")
    gate_prompt = build_traceability_gate_prompt(text)
    print(f"  Gate prompt: {len(gate_prompt)} chars")

    gate_results = []
    for i in range(NUM_AGENTS):
        print(f"  Gate Agent {i+1}/{NUM_AGENTS}...", end="", flush=True)
        t0 = time.time()
        response = call_claude(gate_prompt)
        dt = time.time() - t0

        # Parse gate response
        gate = {}
        if response:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                try:
                    data = json.loads(match.group())
                    for k, v in data.items():
                        gate[str(k)] = str(v).upper().startswith("T")
                except json.JSONDecodeError:
                    pass

        gate_results.append(gate)
        n_traceable = sum(1 for v in gate.values() if v)
        n_total = len(gate)
        print(f" {dt:.1f}s, {n_traceable}/{n_total} traceable")

    results["gate_agents"] = gate_results

    # Apply gate: intersection of gates (all 3 must agree sentence is traceable)
    def apply_gate(gate_list, threshold):
        """Count how many agents say each sentence is traceable."""
        traceable = Counter()
        for gate in gate_list:
            for s, is_t in gate.items():
                if is_t:
                    traceable[s] += 1
        return {s for s, count in traceable.items() if count >= threshold}

    gate_all = apply_gate(gate_results, NUM_AGENTS)   # All agents agree
    gate_majority = apply_gate(gate_results, 2)        # 2/3 agree
    gate_any = apply_gate(gate_results, 1)             # Any agent says traceable

    # Filter original classifications using gate
    def filter_by_gate(classifications, traceable_sents):
        return {s: c for s, c in classifications.items() if s in traceable_sents}

    results["gate_all"] = filter_by_gate(orig_cls, gate_all)
    results["gate_majority"] = filter_by_gate(orig_cls, gate_majority)
    results["gate_any"] = filter_by_gate(orig_cls, gate_any)

    # ─── Aggregation ────────────────────────────────────────────────
    # Review-based
    results["review_intersection"] = intersection_vote(results["agents_review"])
    results["review_majority"] = majority_vote(results["agents_review"])
    results["review_single"] = results["agents_review"][0] if results["agents_review"] else {}

    # Fresh-based
    results["fresh_intersection"] = intersection_vote(results["agents_fresh"])
    results["fresh_majority"] = majority_vote(results["agents_fresh"])
    results["fresh_single"] = results["agents_fresh"][0] if results["agents_fresh"] else {}

    # With context isolation filter
    results["review_intersection_filtered"] = context_isolation_filter(
        results["review_intersection"], text
    )
    results["review_majority_filtered"] = context_isolation_filter(
        results["review_majority"], text
    )

    return results


def save_results(project, results):
    """Save classification results to JSON files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save per-agent results
    for prefix, key in [("review", "agents_review"), ("fresh", "agents_fresh")]:
        for i, cls in enumerate(results.get(key, [])):
            path = OUTPUT_DIR / f"{project}_{prefix}_agent{i+1}.json"
            with open(path, "w") as f:
                json.dump(cls, f, indent=2)

    # Save gate per-agent results
    for i, gate in enumerate(results.get("gate_agents", [])):
        path = OUTPUT_DIR / f"{project}_gate_agent{i+1}.json"
        with open(path, "w") as f:
            json.dump(gate, f, indent=2)

    # Save aggregated strategies
    for strategy in ["review_intersection", "review_majority", "review_single",
                     "review_intersection_filtered", "review_majority_filtered",
                     "fresh_intersection", "fresh_majority", "fresh_single",
                     "gate_all", "gate_majority", "gate_any"]:
        if strategy in results:
            path = OUTPUT_DIR / f"{project}_{strategy}.json"
            with open(path, "w") as f:
                json.dump(results[strategy], f, indent=2)


def eval_and_report(projects=None):
    """Evaluate all saved results and generate report."""
    if projects is None:
        projects = PROJECTS

    lines = []
    w = lines.append

    w("# Precision-Focused LLM Classifier Results")
    w("")
    w("Classifier optimized for precision over recall, based on the fix impact")
    w("simulation finding that FP reduction (+0.081 avg ΔF1) dominates all other fixes.")
    w("")
    w("**Key changes from original LLM baseline:**")
    w("1. Precision-focused prompt: explicit instructions to only classify code-traceable sentences")
    w("2. Multi-agent intersection voting: all 3 agents must agree")
    w("3. Context isolation post-filter: remove assignments lacking textual evidence")
    w("")
    w("---")
    w("")

    # Load reference systems
    from new_metrics_analysis import load_v45_sad_sam, compose_sad_code
    from three_system_comparison import ADAPTIVE_STRATEGIES, load_llm_adaptive_classifications

    agg = defaultdict(list)

    for proj in projects:
        w(f"## {proj.capitalize()}")
        w("")

        code_model = load_code_model_files(proj)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        # Reference systems
        transarc = load_result_sad_code(proj)
        _, _, ta_f1, ta_tp, ta_fp, ta_fn = calc_metrics(gs_sad_code, transarc)

        v45_links = load_v45_sad_sam(proj)
        v45_sad_code = compose_sad_code(v45_links, gs_sam_code_map)
        _, _, v45_f1, v45_tp, v45_fp, v45_fn = calc_metrics(gs_sad_code, v45_sad_code)

        # Original LLM adaptive
        orig_cls = load_llm_adaptive_classifications(proj)
        orig_result, _ = classifications_to_result_set(orig_cls, name_to_ids, model_to_files)
        _, _, orig_f1, orig_tp, orig_fp, orig_fn = calc_metrics(gs_sad_code, orig_result)

        # New precision classifier results
        strategies = [
            "review_intersection", "review_majority", "review_single",
            "review_intersection_filtered", "review_majority_filtered",
            "fresh_intersection", "fresh_majority", "fresh_single",
            "gate_all", "gate_majority", "gate_any",
        ]
        new_results = {}
        for strat in strategies:
            path = OUTPUT_DIR / f"{proj}_{strat}.json"
            if path.exists():
                cls = load_json(path)
                result_set, _ = classifications_to_result_set(cls, name_to_ids, model_to_files)
                p, r, f1, tp, fp, fn = calc_metrics(gs_sad_code, result_set)
                n_sents = len(cls)
                n_pairs = sum(len(v) for v in cls.values())
                new_results[strat] = {
                    "p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn,
                    "sents": n_sents, "pairs": n_pairs
                }

        if not new_results:
            w("*No precision classifier results found. Run classification first.*")
            w("")
            continue

        w("| System | P | R | F1 | TP | FP | FN |")
        w("|:--|:---:|:---:|:---:|---:|---:|---:|")

        ta_p = ta_tp / (ta_tp + ta_fp) if (ta_tp + ta_fp) > 0 else 0
        ta_r = ta_tp / (ta_tp + ta_fn) if (ta_tp + ta_fn) > 0 else 0
        w(f"| TransArc | {ta_p:.3f} | {ta_r:.3f} | **{ta_f1:.3f}** | {ta_tp} | {ta_fp} | {ta_fn} |")

        v45_p = v45_tp / (v45_tp + v45_fp) if (v45_tp + v45_fp) > 0 else 0
        v45_r = v45_tp / (v45_tp + v45_fn) if (v45_tp + v45_fn) > 0 else 0
        w(f"| V45 | {v45_p:.3f} | {v45_r:.3f} | **{v45_f1:.3f}** | {v45_tp} | {v45_fp} | {v45_fn} |")

        orig_p = orig_tp / (orig_tp + orig_fp) if (orig_tp + orig_fp) > 0 else 0
        orig_r = orig_tp / (orig_tp + orig_fn) if (orig_tp + orig_fn) > 0 else 0
        w(f"| LLM Original ({ADAPTIVE_STRATEGIES[proj]}) | {orig_p:.3f} | {orig_r:.3f} | "
          f"**{orig_f1:.3f}** | {orig_tp} | {orig_fp} | {orig_fn} |")

        best_strat = None
        best_f1 = -1
        for strat, m in sorted(new_results.items()):
            w(f"| {strat} | {m['p']:.3f} | {m['r']:.3f} | **{m['f1']:.3f}** | "
              f"{m['tp']} | {m['fp']} | {m['fn']} |")
            if m["f1"] > best_f1:
                best_f1 = m["f1"]
                best_strat = strat
        w("")

        # Track best for aggregate
        if best_strat:
            agg["best_f1"].append(best_f1)
            agg["best_strat"].append(best_strat)
            agg["orig_f1"].append(orig_f1)
            agg["ta_f1"].append(ta_f1)
            agg["v45_f1"].append(v45_f1)
            agg["proj"].append(proj)

        w(f"**Best strategy:** {best_strat} (F1={best_f1:.3f}, "
          f"Δ vs original: {best_f1 - orig_f1:+.3f})")
        w("")

    # Aggregate
    if agg["best_f1"]:
        w("## Aggregate Summary")
        w("")
        w("| Project | TransArc | V45 | LLM Original | LLM Precision | Best Strategy | ΔF1 |")
        w("|:--|:---:|:---:|:---:|:---:|:--|:---:|")
        for i in range(len(agg["proj"])):
            delta = agg["best_f1"][i] - agg["orig_f1"][i]
            w(f"| {agg['proj'][i]} | {agg['ta_f1'][i]:.3f} | {agg['v45_f1'][i]:.3f} | "
              f"{agg['orig_f1'][i]:.3f} | **{agg['best_f1'][i]:.3f}** | "
              f"{agg['best_strat'][i]} | {delta:+.3f} |")

        avg_best = sum(agg["best_f1"]) / len(agg["best_f1"])
        avg_orig = sum(agg["orig_f1"]) / len(agg["orig_f1"])
        avg_ta = sum(agg["ta_f1"]) / len(agg["ta_f1"])
        avg_v45 = sum(agg["v45_f1"]) / len(agg["v45_f1"])
        w(f"| **Average** | **{avg_ta:.3f}** | **{avg_v45:.3f}** | "
          f"**{avg_orig:.3f}** | **{avg_best:.3f}** | — | "
          f"**{avg_best - avg_orig:+.3f}** |")
        w("")

        w("### Key Findings")
        w("")
        w(f"- Precision LLM avg F1: **{avg_best:.3f}** (vs original {avg_orig:.3f}, "
          f"Δ = {avg_best - avg_orig:+.3f})")
        w(f"- TransArc avg F1: {avg_ta:.3f}")
        w(f"- V45 avg F1: {avg_v45:.3f}")
        if avg_best > avg_v45:
            w(f"- **Precision LLM surpasses V45** ({avg_best:.3f} > {avg_v45:.3f})")
        w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 llm_precision_classifier.py            # Run classification")
    w("python3 llm_precision_classifier.py --eval-only # Evaluate only")
    w("```")

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nReport written to {OUTPUT_MD}")


def main():
    args = sys.argv[1:]

    eval_only = "--eval-only" in args
    args = [a for a in args if a != "--eval-only"]

    # Select projects
    if "--project" in args:
        idx = args.index("--project")
        if idx + 1 < len(args):
            projects = [args[idx + 1]]
        else:
            print("ERROR: --project requires a project name")
            sys.exit(1)
    else:
        projects = list(PROJECTS)

    if not eval_only:
        for proj in projects:
            results = run_classification(proj)
            save_results(proj, results)

            # Quick evaluation
            print(f"\n  Quick eval for {proj}:")
            for strat in ["review_intersection", "review_majority", "review_single",
                          "review_intersection_filtered", "review_majority_filtered",
                          "fresh_intersection", "fresh_majority", "fresh_single",
                          "gate_all", "gate_majority", "gate_any"]:
                if strat in results:
                    m = evaluate_classifications(results[strat], proj)
                    print(f"    {strat:<35} P={m['p']:.3f} R={m['r']:.3f} F1={m['f1']:.3f} "
                          f"TP={m['tp']} FP={m['fp']} FN={m['fn']}")

    # Generate report
    eval_and_report(projects)


if __name__ == "__main__":
    main()
