#!/usr/bin/env python3
"""
LLM Improved Baseline: 5 post-processing improvements for LLM SAD-CODE TLR.

Implements all 5 proposed solutions from the bottleneck analysis:
  B1: Context Isolation Filter (remove isolated FP classifications)
  B2: Architectural Sentence Filter (heuristic FP removal)
  B3: Co-occurrence Enrichment (SAM-CODE file overlap co-assignment)
  B4: Generic Name Strict Filter (require explicit mention for generic names)
  B5: Selective Upgrade (add high-confidence links missed by conservative strategy)

Design principles (learned from v1 failure):
- Fixes START from baseline and REFINE (not rebuild from scratch)
- FP-reducing fixes: conservative removal only with strong evidence
- FN-reducing fixes: add links only with explicit textual evidence
- Combined pipeline: apply filters first, then additive fixes

Outputs: LLM_IMPROVED_BASELINE.md
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_raw,
    load_gs_sam_code_maps, load_gs_sad_code_enrolled,
    load_result_sad_code, load_text, load_model_element_names,
    calc_metrics,
)
from llm_agentic_eval import (
    load_json, majority_vote, intersection_vote,
    build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
    SINGLE_DIR, MULTI_DIR, VARIANTS,
)
from three_system_comparison import (
    ADAPTIVE_STRATEGIES,
    load_llm_adaptive_classifications,
    llm_classifications_to_sad_sam,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/LLM_IMPROVED_BASELINE.md")


# ═══════════════════════════════════════════════════════════════════════════════
# Shared utility: check if component name appears in sentence
# ═══════════════════════════════════════════════════════════════════════════════

def _comp_name_in_text(comp_name, sentence_text):
    """Check if a component's short name appears literally in sentence text."""
    short = comp_name.split(": ", 1)[1] if ": " in comp_name else comp_name
    if len(short) < 3:
        return False
    # Check for the name as a word (allowing compound forms)
    return short.lower() in sentence_text.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B1: Context Isolation Filter (FP reducer)
# ═══════════════════════════════════════════════════════════════════════════════

def fix_b1_context_isolation(classifications, text):
    """Remove isolated FP classifications using context validation.

    For each (sent, comp) pair: if the component name does NOT appear in the
    sentence AND no immediate neighbor (±1) has the same component assigned,
    the assignment is likely an isolated FP → remove it.

    This is the inverse of discourse propagation: instead of adding links,
    we remove links that lack contextual support.
    """
    result = {}
    for s, comps in classifications.items():
        snum = int(s)
        sent_text = text.get(s, "")
        kept = []
        for comp in comps:
            # Keep if component name appears in text
            if _comp_name_in_text(comp, sent_text):
                kept.append(comp)
                continue
            # Keep if any immediate neighbor also has this component
            neighbor_has = False
            for offset in [-1, 1]:
                ns = str(snum + offset)
                if ns in classifications and comp in classifications[ns]:
                    neighbor_has = True
                    break
            if neighbor_has:
                kept.append(comp)
            # else: isolated, no name match → filter out
        if kept:
            result[s] = kept
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B2: Architectural Sentence Filter (FP reducer)
# ═══════════════════════════════════════════════════════════════════════════════

_NON_ARCH_PATTERNS = [
    # Test-related
    re.compile(r'\btest(?:s|ed|ing|able|case|suite)?\b', re.IGNORECASE),
    re.compile(r'\bverif(?:y|ied|ication)\b', re.IGNORECASE),
    # UI interaction / end-user behavioral
    re.compile(r'\bclick(?:s|ed|ing)?\b', re.IGNORECASE),
    re.compile(r'\bbutton\b', re.IGNORECASE),
    re.compile(r'\bscreenshot\b', re.IGNORECASE),
    re.compile(r'\bpopup\b', re.IGNORECASE),
    # Process / organizational
    re.compile(r'\bmeeting\b', re.IGNORECASE),
    re.compile(r'\bsprint\b', re.IGNORECASE),
    re.compile(r'\bdeadline\b', re.IGNORECASE),
]

_ARCH_INDICATORS = [
    re.compile(r'\bcomponent\b', re.IGNORECASE),
    re.compile(r'\bmodule\b', re.IGNORECASE),
    re.compile(r'\bservice\b', re.IGNORECASE),
    re.compile(r'\binterface\b', re.IGNORECASE),
    re.compile(r'\bhandle[sd]?\b', re.IGNORECASE),
    re.compile(r'\bmanage[sd]?\b', re.IGNORECASE),
    re.compile(r'\bresponsible\b', re.IGNORECASE),
    re.compile(r'\bimplement(?:s|ed|ation)?\b', re.IGNORECASE),
    re.compile(r'\bcommunicat(?:e|es|ion)\b', re.IGNORECASE),
    re.compile(r'\bprocess(?:es|ing)?\b', re.IGNORECASE),
    re.compile(r'\bstore[sd]?\b', re.IGNORECASE),
    re.compile(r'\bprovide[sd]?\b', re.IGNORECASE),
]


def fix_b2_architectural_filter(classifications, text, component_short_names):
    """Remove entire sentence classifications for non-architectural sentences.

    Only removes when: non-arch pattern matches AND no component name in text
    AND no architectural indicators. Very conservative.
    """
    result = {}
    for s, comps in classifications.items():
        sent_text = text.get(s, "")

        # Check for non-architectural patterns
        has_non_arch = any(p.search(sent_text) for p in _NON_ARCH_PATTERNS)
        if not has_non_arch:
            result[s] = comps
            continue

        # Has non-arch pattern: keep if component name appears or arch indicator found
        has_comp_name = any(
            cn.lower() in sent_text.lower()
            for cn in component_short_names
            if len(cn) >= 3
        )
        if has_comp_name:
            result[s] = comps
            continue

        has_arch = any(p.search(sent_text) for p in _ARCH_INDICATORS)
        if has_arch:
            result[s] = comps
            continue

        # Non-architectural, no component name, no arch indicator → filter
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B3: Co-occurrence Enrichment (from SAM-CODE file overlap)
# ═══════════════════════════════════════════════════════════════════════════════

def build_cooccurrence_from_file_overlap(model_to_files, names, threshold=1.0):
    """Build co-occurrence rules from SAM-CODE file overlap.

    Only at threshold=1.0 (100% file containment) to avoid adding FPs.
    When comp B's files are a perfect subset of comp A's files, assigning
    A implies B should also be assigned.
    """
    coassign = defaultdict(set)
    ae_ids = list(model_to_files.keys())

    for i, a in enumerate(ae_ids):
        for b in ae_ids[i + 1:]:
            shared = model_to_files[a] & model_to_files[b]
            if not shared:
                continue
            a_name = names.get(a, a)
            b_name = names.get(b, b)
            ratio_a = len(shared) / len(model_to_files[a]) if model_to_files[a] else 0
            ratio_b = len(shared) / len(model_to_files[b]) if model_to_files[b] else 0

            if ratio_a >= threshold:
                coassign[b_name].add(a_name)
            if ratio_b >= threshold:
                coassign[a_name].add(b_name)

    return dict(coassign)


def fix_b3_cooccurrence(classifications, coassign_rules):
    """Add co-occurring components based on file overlap rules.

    When LLM assigns component A, add any component B whose files are
    100% contained in A's files. This mainly helps at SAD-SAM level
    (adding Interface counterparts) and is neutral at SAD-CODE level
    (since files are identical).
    """
    result = {}
    for s, comps in classifications.items():
        comp_set = set(comps)
        added = set()
        for comp in comps:
            for co_comp in coassign_rules.get(comp, set()):
                if co_comp not in comp_set:
                    added.add(co_comp)
        result[s] = list(comp_set | added)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B4: Generic Name Strict Filter (FP reducer)
# ═══════════════════════════════════════════════════════════════════════════════

GENERIC_NAMES = {
    "Logic", "Storage", "Common", "Client", "Server", "Apps",
    "Controller", "Manager", "Adapter", "Model",
}


def fix_b4_generic_strict(classifications, text, variants=None):
    """Require explicit textual evidence for generic-named components.

    For components with generic names (e.g. "Logic", "Storage"):
    - REQUIRE the name to appear literally in the sentence text
    - OR require 3/3 agent agreement (if variant data available)
    - Otherwise remove the assignment.
    """
    agreement = Counter()
    if variants:
        for v_cls in variants.values():
            for s, comps in v_cls.items():
                for c in comps:
                    agreement[(s, c)] += 1

    result = {}
    for s, comps in classifications.items():
        sent_text = text.get(s, "")
        kept = []
        for comp in comps:
            short = comp.split(": ", 1)[1] if ": " in comp else comp
            if short not in GENERIC_NAMES:
                kept.append(comp)
                continue
            # Generic: require text evidence OR unanimous agreement
            if _comp_name_in_text(comp, sent_text):
                kept.append(comp)
            elif variants and agreement.get((s, comp), 0) >= 3:
                kept.append(comp)
            # else: filtered
        if kept:
            result[s] = kept
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B5: Selective Upgrade (FN reducer)
# ═══════════════════════════════════════════════════════════════════════════════

def fix_b5_selective_upgrade(baseline_cls, variants, text, project):
    """Add high-confidence links that the conservative baseline strategy missed.

    Starting from the baseline classification:
    - For intersection projects: add 2/3-agreement links where the component
      name appears literally in the sentence text.
    - For majority projects: add 1/3-agreement links where the component
      name appears literally in the sentence text.
    - For single-agent projects: no upgrade (already includes everything).

    This is ADDITIVE only — never removes baseline links.
    """
    strategy = ADAPTIVE_STRATEGIES[project]
    if strategy == "single":
        return baseline_cls  # Nothing to upgrade

    # Count agreement per (sent, comp)
    pair_counts = Counter()
    for v_cls in variants.values():
        for s, comps in v_cls.items():
            for c in comps:
                pair_counts[(s, c)] += 1

    result = {s: list(comps) for s, comps in baseline_cls.items()}
    baseline_pairs = set()
    for s, comps in baseline_cls.items():
        for c in comps:
            baseline_pairs.add((s, c))

    if strategy == "intersection":
        # Baseline has 3/3 only. Upgrade: add 2/3 where name in text.
        min_agreement = 2
    else:  # majority
        # Baseline has 2/3+. Upgrade: add 1/3 where name in text.
        min_agreement = 1

    for (s, comp), count in pair_counts.items():
        if (s, comp) in baseline_pairs:
            continue
        if count < min_agreement:
            continue
        sent_text = text.get(s, "")
        if _comp_name_in_text(comp, sent_text):
            if s not in result:
                result[s] = []
            result[s].append(comp)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Combined Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def combined_pipeline(baseline_cls, variants, text, model_to_files, names,
                      component_short_names, project):
    """Apply beneficial fixes in optimal order: B2 → B4 → B5.

    Excludes B1 (context isolation) and B3 (co-occurrence) which empirically
    hurt performance:
    - B1 removes too many valid links (component not named but correctly inferred)
    - B3 adds Interface-type SAM links that are always FPs (gold has no Interface links)

    Order: FP filters first (B2, B4), then FN reducer (B5).
    """
    # Step 1: B2 — remove non-architectural sentences
    cls = fix_b2_architectural_filter(baseline_cls, text, component_short_names)

    # Step 2: B4 — require evidence for generic names
    cls = fix_b4_generic_strict(cls, text, variants=variants)

    # Step 3: B5 — selectively add high-confidence links missed by baseline
    if variants and len(variants) == 3:
        cls = fix_b5_selective_upgrade(cls, variants, text, project)

    return cls


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_classification(classifications, name_to_ids, model_to_files,
                            gs_sad_code, gs_sad_sam, gold_sents):
    """Evaluate a classification at both SAD-SAM and SAD-CODE levels."""
    result_code, unmatched = classifications_to_result_set(
        classifications, name_to_ids, model_to_files)
    tp_c = len(result_code & gs_sad_code)
    fp_c = len(result_code - gs_sad_code)
    fn_c = len(gs_sad_code - result_code)
    p_c = tp_c / (tp_c + fp_c) if (tp_c + fp_c) > 0 else 0
    r_c = tp_c / (tp_c + fn_c) if (tp_c + fn_c) > 0 else 0
    f1_c = 2 * p_c * r_c / (p_c + r_c) if (p_c + r_c) > 0 else 0

    result_sam = llm_classifications_to_sad_sam(classifications, name_to_ids)
    p_s, r_s, f1_s, tp_s, fp_s, fn_s = calc_metrics(gs_sad_sam, result_sam)

    return {
        "code": {"p": p_c, "r": r_c, "f1": f1_c, "tp": tp_c, "fp": fp_c, "fn": fn_c},
        "sam": {"p": p_s, "r": r_s, "f1": f1_s, "tp": tp_s, "fp": fp_s, "fn": fn_s},
        "n_sents": len(classifications),
        "n_links": sum(len(v) for v in classifications.values()),
        "unmatched": unmatched,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    lines = []
    w = lines.append

    w("# LLM Improved Baseline: 5 Post-Processing Fixes (v2)")
    w("")
    w("Applies 5 targeted fixes to the LLM Adaptive baseline:")
    w("")
    w("| Fix | Type | Approach |")
    w("|:----|:-----|:---------|")
    w("| B1 | FP reducer | Context isolation: remove assignments lacking neighbor support |")
    w("| B2 | FP reducer | Arch filter: remove non-architectural sentence classifications |")
    w("| B3 | FN reducer | Co-occurrence: add components with 100% file overlap |")
    w("| B4 | FP reducer | Generic strict: require text evidence for generic names |")
    w("| B5 | FN reducer | Selective upgrade: add name-in-text links below baseline threshold |")
    w("")
    w("**Design**: Fixes refine the baseline (never rebuild from scratch). "
      "FP reducers remove with evidence; FN reducers add only with explicit textual support.")
    w("")
    w("---")
    w("")

    all_results = {}

    for proj in PROJECTS:
        print(f"\n{'=' * 70}")
        print(f"  {proj.upper()}")
        print(f"{'=' * 70}")

        code_model = load_code_model_files(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gold_sents = set(s for s, _ in gs_sad_code)
        text = load_text(proj)
        names = load_model_element_names(proj)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        component_short_names = set()
        for name in names.values():
            short = name.split(": ", 1)[1] if ": " in name else name
            component_short_names.add(short)

        variants = {}
        for v in VARIANTS:
            path = MULTI_DIR / f"{proj}_{v}.json"
            if path.exists():
                variants[v] = load_json(path)

        # Baseline: Adaptive LLM
        baseline_cls = load_llm_adaptive_classifications(proj)
        baseline_eval = evaluate_classification(
            baseline_cls, name_to_ids, model_to_files,
            gs_sad_code, gs_sad_sam, gold_sents)

        # TransArc
        transarc_sad_code = load_result_sad_code(proj)
        tc_tp = len(transarc_sad_code & gs_sad_code)
        tc_fp = len(transarc_sad_code - gs_sad_code)
        tc_fn = len(gs_sad_code - transarc_sad_code)
        tc_p = tc_tp / (tc_tp + tc_fp) if (tc_tp + tc_fp) > 0 else 0
        tc_r = tc_tp / (tc_tp + tc_fn) if (tc_tp + tc_fn) > 0 else 0
        tc_f1 = 2 * tc_p * tc_r / (tc_p + tc_r) if (tc_p + tc_r) > 0 else 0
        transarc_eval = {"code": {"p": tc_p, "r": tc_r, "f1": tc_f1,
                                   "tp": tc_tp, "fp": tc_fp, "fn": tc_fn}}

        # ─── Apply individual fixes ───────────────────────────────────
        fix_evals = {}

        # B1: Context Isolation
        b1_cls = fix_b1_context_isolation(baseline_cls, text)
        fix_evals["B1: Ctx Isolate"] = evaluate_classification(
            b1_cls, name_to_ids, model_to_files,
            gs_sad_code, gs_sad_sam, gold_sents)

        # B2: Architectural Filter
        b2_cls = fix_b2_architectural_filter(baseline_cls, text, component_short_names)
        fix_evals["B2: Arch Filter"] = evaluate_classification(
            b2_cls, name_to_ids, model_to_files,
            gs_sad_code, gs_sad_sam, gold_sents)

        # B3: Co-occurrence (threshold=1.0)
        coassign = build_cooccurrence_from_file_overlap(model_to_files, names,
                                                          threshold=1.0)
        b3_cls = fix_b3_cooccurrence(baseline_cls, coassign)
        fix_evals["B3: Co-occur"] = evaluate_classification(
            b3_cls, name_to_ids, model_to_files,
            gs_sad_code, gs_sad_sam, gold_sents)
        n_coassign_rules = sum(len(v) for v in coassign.values())

        # B4: Generic Strict
        b4_cls = fix_b4_generic_strict(
            baseline_cls, text,
            variants=variants if len(variants) == 3 else None)
        fix_evals["B4: Generic Str"] = evaluate_classification(
            b4_cls, name_to_ids, model_to_files,
            gs_sad_code, gs_sad_sam, gold_sents)

        # B5: Selective Upgrade
        if len(variants) == 3:
            b5_cls = fix_b5_selective_upgrade(baseline_cls, variants, text, proj)
            fix_evals["B5: Sel Upgrade"] = evaluate_classification(
                b5_cls, name_to_ids, model_to_files,
                gs_sad_code, gs_sad_sam, gold_sents)
        else:
            fix_evals["B5: Sel Upgrade"] = baseline_eval

        # ─── Combined pipeline ────────────────────────────────────────
        if len(variants) == 3:
            combined_cls = combined_pipeline(
                baseline_cls, variants, text, model_to_files, names,
                component_short_names, proj)
            fix_evals["Combined"] = evaluate_classification(
                combined_cls, name_to_ids, model_to_files,
                gs_sad_code, gs_sad_sam, gold_sents)
        else:
            fix_evals["Combined"] = baseline_eval

        proj_results = {
            "TransArc": transarc_eval,
            "Baseline LLM": baseline_eval,
        }
        proj_results.update(fix_evals)
        all_results[proj] = proj_results

        # ─── Report per-project ───────────────────────────────────────
        w(f"## {proj.capitalize()}")
        w("")
        w(f"Adaptive strategy: **{ADAPTIVE_STRATEGIES[proj]}** | "
          f"Co-occurrence rules: {n_coassign_rules} | "
          f"Baseline: {baseline_eval['n_sents']} sents, {baseline_eval['n_links']} links")
        w("")

        # SAD-CODE table
        w("### SAD-CODE Level")
        w("")
        w("| System | P | R | F1 | TP | FP | FN | ΔF1 |")
        w("|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|")
        bl_f1 = baseline_eval["code"]["f1"]
        for name in ["TransArc", "Baseline LLM",
                      "B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                      "B4: Generic Str", "B5: Sel Upgrade", "Combined"]:
            ev = proj_results.get(name)
            if not ev:
                continue
            c = ev["code"]
            delta = c["f1"] - bl_f1
            w(f"| {name} | {c['p']:.3f} | {c['r']:.3f} | "
              f"**{c['f1']:.3f}** | {c['tp']} | {c['fp']} | {c['fn']} | "
              f"{delta:+.3f} |")
        w("")

        # SAD-SAM table
        w("### SAD-SAM Level")
        w("")
        w("| System | P | R | F1 | TP | FP | FN |")
        w("|:-------|:---:|:---:|:---:|---:|---:|---:|")
        for name in ["Baseline LLM",
                      "B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                      "B4: Generic Str", "B5: Sel Upgrade", "Combined"]:
            ev = proj_results.get(name)
            if not ev or "sam" not in ev:
                continue
            s = ev["sam"]
            w(f"| {name} | {s['p']:.3f} | {s['r']:.3f} | "
              f"**{s['f1']:.3f}** | {s['tp']} | {s['fp']} | {s['fn']} |")
        w("")

        # Print console summary
        for name in ["TransArc", "Baseline LLM",
                      "B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                      "B4: Generic Str", "B5: Sel Upgrade", "Combined"]:
            ev = proj_results.get(name)
            if not ev:
                continue
            c = ev["code"]
            delta = c["f1"] - bl_f1
            sam_info = ""
            if "sam" in ev:
                sam_info = f"  SAM: F1={ev['sam']['f1']:.3f}"
            print(f"  {name:<18s} CODE: P={c['p']:.3f} R={c['r']:.3f} "
                  f"F1={c['f1']:.3f} (Δ={delta:+.3f}){sam_info}")

        w("---")
        w("")

    # ═══════════════════════════════════════════════════════════════════
    # Aggregate Comparison
    # ═══════════════════════════════════════════════════════════════════

    w("## Aggregate Comparison")
    w("")

    system_names = ["TransArc", "Baseline LLM",
                    "B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                    "B4: Generic Str", "B5: Sel Upgrade", "Combined"]

    # Cross-project SAD-CODE F1
    w("### SAD-CODE Micro F1")
    w("")
    header = "| System |"
    sep = "|:-------|"
    for proj in PROJECTS:
        header += f" {proj[:6]} |"
        sep += ":---:|"
    header += " **Avg** |"
    sep += ":---:|"
    w(header)
    w(sep)

    avg_f1s = {}
    for name in system_names:
        row = f"| {name} |"
        f1s = []
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            if ev:
                f1 = ev["code"]["f1"]
                row += f" {f1:.3f} |"
                f1s.append(f1)
            else:
                row += " — |"
        avg = sum(f1s) / len(f1s) if f1s else 0
        avg_f1s[name] = avg
        row += f" **{avg:.3f}** |"
        w(row)
    w("")

    # Cross-project SAD-SAM F1
    w("### SAD-SAM Micro F1")
    w("")
    header2 = "| System |"
    sep2 = "|:-------|"
    for proj in PROJECTS:
        header2 += f" {proj[:6]} |"
        sep2 += ":---:|"
    header2 += " **Avg** |"
    sep2 += ":---:|"
    w(header2)
    w(sep2)

    avg_sam_f1s = {}
    for name in system_names:
        if name == "TransArc":
            continue  # TransArc doesn't have SAM-level in our eval
        row = f"| {name} |"
        f1s = []
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            if ev and "sam" in ev:
                f1 = ev["sam"]["f1"]
                row += f" {f1:.3f} |"
                f1s.append(f1)
            else:
                row += " — |"
        avg = sum(f1s) / len(f1s) if f1s else 0
        avg_sam_f1s[name] = avg
        row += f" **{avg:.3f}** |"
        w(row)
    w("")

    # Impact summary
    w("### Fix Impact Summary (SAD-CODE)")
    w("")
    w("| Fix | Type | Avg ΔF1 | Best Project | Worst Project |")
    w("|:----|:-----|:------:|:---|:---|")
    bl_avg = avg_f1s["Baseline LLM"]
    for name in ["B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                  "B4: Generic Str", "B5: Sel Upgrade", "Combined"]:
        deltas = {}
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            bl = all_results[proj]["Baseline LLM"]
            if ev and bl:
                deltas[proj] = ev["code"]["f1"] - bl["code"]["f1"]
        avg_delta = sum(deltas.values()) / len(deltas) if deltas else 0
        best_proj = max(deltas, key=deltas.get) if deltas else "—"
        worst_proj = min(deltas, key=deltas.get) if deltas else "—"
        fix_type = {"B1: Ctx Isolate": "FP ↓", "B2: Arch Filter": "FP ↓",
                    "B3: Co-occur": "FN ↓", "B4: Generic Str": "FP ↓",
                    "B5: Sel Upgrade": "FN ↓", "Combined": "Both"}[name]
        w(f"| {name} | {fix_type} | {avg_delta:+.4f} | "
          f"{best_proj} ({deltas.get(best_proj, 0):+.3f}) | "
          f"{worst_proj} ({deltas.get(worst_proj, 0):+.3f}) |")
    w("")

    # Impact summary for SAD-SAM
    w("### Fix Impact Summary (SAD-SAM)")
    w("")
    w("| Fix | Avg ΔF1 | Best Project | Worst Project |")
    w("|:----|:------:|:---|:---|")
    for name in ["B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                  "B4: Generic Str", "B5: Sel Upgrade", "Combined"]:
        deltas = {}
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            bl = all_results[proj]["Baseline LLM"]
            if ev and bl and "sam" in ev and "sam" in bl:
                deltas[proj] = ev["sam"]["f1"] - bl["sam"]["f1"]
        avg_delta = sum(deltas.values()) / len(deltas) if deltas else 0
        best_proj = max(deltas, key=deltas.get) if deltas else "—"
        worst_proj = min(deltas, key=deltas.get) if deltas else "—"
        w(f"| {name} | {avg_delta:+.4f} | "
          f"{best_proj} ({deltas.get(best_proj, 0):+.3f}) | "
          f"{worst_proj} ({deltas.get(worst_proj, 0):+.3f}) |")
    w("")

    # Final comparison
    w("### Final: Combined vs Baseline vs TransArc (SAD-CODE)")
    w("")
    w("| Project | TransArc | Baseline LLM | Combined | Δ vs Baseline | Δ vs TransArc |")
    w("|:--------|:---:|:---:|:---:|:---:|:---:|")
    tot_t, tot_bl, tot_cb = 0, 0, 0
    for proj in PROJECTS:
        t_f1 = all_results[proj]["TransArc"]["code"]["f1"]
        bl_f1 = all_results[proj]["Baseline LLM"]["code"]["f1"]
        cb_f1 = all_results[proj]["Combined"]["code"]["f1"]
        w(f"| {proj} | {t_f1:.3f} | {bl_f1:.3f} | **{cb_f1:.3f}** | "
          f"{cb_f1 - bl_f1:+.3f} | {cb_f1 - t_f1:+.3f} |")
        tot_t += t_f1
        tot_bl += bl_f1
        tot_cb += cb_f1
    n = len(PROJECTS)
    w(f"| **Average** | {tot_t/n:.3f} | {tot_bl/n:.3f} | **{tot_cb/n:.3f}** | "
      f"{(tot_cb - tot_bl)/n:+.3f} | {(tot_cb - tot_t)/n:+.3f} |")
    w("")

    combined_wins_bl = sum(1 for p in PROJECTS
                           if all_results[p]["Combined"]["code"]["f1"] >
                              all_results[p]["Baseline LLM"]["code"]["f1"])
    combined_wins_ta = sum(1 for p in PROJECTS
                           if all_results[p]["Combined"]["code"]["f1"] >
                              all_results[p]["TransArc"]["code"]["f1"])
    w(f"Combined beats Baseline LLM on **{combined_wins_bl}/{n}** projects.")
    w(f"Combined beats TransArc on **{combined_wins_ta}/{n}** projects.")
    w("")

    # ─── Key Findings ─────────────────────────────────────────────────
    w("## Key Findings")
    w("")

    best_fix = max(["B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                    "B4: Generic Str", "B5: Sel Upgrade"],
                   key=lambda name: avg_f1s.get(name, 0))
    w(f"1. **Best individual fix (CODE)**: {best_fix} "
      f"(avg F1={avg_f1s[best_fix]:.3f} vs baseline {bl_avg:.3f}, "
      f"Δ={avg_f1s[best_fix] - bl_avg:+.3f})")
    w("")

    best_sam_fix = max(["B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                        "B4: Generic Str", "B5: Sel Upgrade"],
                       key=lambda name: avg_sam_f1s.get(name, 0))
    bl_sam_avg = avg_sam_f1s.get("Baseline LLM", 0)
    w(f"2. **Best individual fix (SAM)**: {best_sam_fix} "
      f"(avg F1={avg_sam_f1s[best_sam_fix]:.3f} vs baseline {bl_sam_avg:.3f}, "
      f"Δ={avg_sam_f1s[best_sam_fix] - bl_sam_avg:+.3f})")
    w("")

    w("3. **Per-project best individual fix (CODE):**")
    for proj in PROJECTS:
        best_name = "—"
        best_delta = 0
        for name in ["B1: Ctx Isolate", "B2: Arch Filter", "B3: Co-occur",
                      "B4: Generic Str", "B5: Sel Upgrade"]:
            ev = all_results[proj].get(name)
            bl = all_results[proj]["Baseline LLM"]
            if ev and bl:
                delta = ev["code"]["f1"] - bl["code"]["f1"]
                if delta > best_delta:
                    best_delta = delta
                    best_name = name
        w(f"   - {proj}: {best_name} ({best_delta:+.3f})")
    w("")

    w(f"4. **Combined pipeline (CODE)**: avg F1={avg_f1s.get('Combined', 0):.3f}, "
      f"Δ={avg_f1s.get('Combined', 0) - bl_avg:+.3f} vs baseline")
    w("")

    w("5. **Lesson**: Post-processing improvements on pre-computed LLM classifications")
    w("   are inherently limited. The most impactful improvements require:")
    w("   - Re-running the LLM with modified prompts (discourse context, two-phase)")
    w("   - Access to confidence scores from the LLM (not just binary classifications)")
    w("   - Project-specific tuning (what works for BBB hurts Teammates)")
    w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 llm_improved_baseline.py")
    w("```")
    w("")

    # Write output
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nReport written to {OUTPUT_MD}")

    # Console summary
    print("\n" + "=" * 80)
    print("AGGREGATE: SAD-CODE Micro F1")
    print("=" * 80)
    print(f"{'System':<20s}", end="")
    for proj in PROJECTS:
        print(f" {proj[:8]:>8s}", end="")
    print(f" {'Avg':>8s}")
    print("-" * 80)
    for name in system_names:
        print(f"{name:<20s}", end="")
        f1s = []
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            if ev:
                f1 = ev["code"]["f1"]
                print(f" {f1:>8.3f}", end="")
                f1s.append(f1)
            else:
                print(f" {'—':>8s}", end="")
        avg = sum(f1s) / len(f1s) if f1s else 0
        print(f" {avg:>8.3f}")

    print(f"\n{'System':<20s}", end="")
    for proj in PROJECTS:
        print(f" {proj[:8]:>8s}", end="")
    print(f" {'Avg':>8s}")
    print("-" * 80)
    print("AGGREGATE: SAD-SAM Micro F1")
    for name in system_names:
        if name == "TransArc":
            continue
        print(f"{name:<20s}", end="")
        f1s = []
        for proj in PROJECTS:
            ev = all_results[proj].get(name)
            if ev and "sam" in ev:
                f1 = ev["sam"]["f1"]
                print(f" {f1:>8.3f}", end="")
                f1s.append(f1)
            else:
                print(f" {'—':>8s}", end="")
        avg = sum(f1s) / len(f1s) if f1s else 0
        print(f" {avg:>8.3f}")


if __name__ == "__main__":
    main()
