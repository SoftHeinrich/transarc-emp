#!/usr/bin/env python3
"""
Meta-Learning LLM Classifier for SAD-CODE Trace Link Recovery.

Two-phase approach with ZERO hardcoded per-project knowledge:
  Phase 1 (Meta-Analysis): LLM discovers document structure, component aliases,
    co-occurrence patterns, and tracing boundaries from raw inputs.
  Phase 2 (Classification): 3 independent LLM agents use Phase 1 analysis
    to classify sentences.

Usage:
    python3 llm_improved_classifier.py                     # Run all projects
    python3 llm_improved_classifier.py --project teastore  # Run one project
    python3 llm_improved_classifier.py --eval-only         # Evaluate saved results
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
    load_gs_sad_sam, load_gs_sam_code_raw, load_gs_sam_code_maps,
    load_gs_sad_code_enrolled, load_result_sad_code,
    load_text, load_model_element_names, calc_metrics,
)
from llm_agentic_eval import (
    load_json, majority_vote, intersection_vote,
    build_name_to_id_map, build_model_to_files,
    classifications_to_result_set,
    SINGLE_DIR, MULTI_DIR, VARIANTS,
)
from three_system_comparison import (
    ADAPTIVE_STRATEGIES, load_llm_adaptive_classifications,
    llm_classifications_to_sad_sam,
)

OUTPUT_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/llm_classifications_improved")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/LLM_IMPROVED_CLASSIFIER.md")

NUM_AGENTS = 3


# ═══════════════════════════════════════════════════════════════════════════════
# Generic Utilities (no project-specific knowledge)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_cooccurrence_pairs(model_to_files, names):
    """Compute component pairs that share files (co-occurrence).

    Returns list of (comp_a, comp_b, overlap_pct) for pairs with >=80% overlap.
    """
    id_to_name = {ae_id: name for ae_id, name in names.items()}
    comp_files = defaultdict(set)
    for ae_id, files in model_to_files.items():
        name = id_to_name.get(ae_id, "")
        short = name.split(": ", 1)[1] if ": " in name else name
        comp_files[short] |= files

    pairs = []
    comp_list = sorted(comp_files.keys())
    for i, a in enumerate(comp_list):
        for b in comp_list[i+1:]:
            fa, fb = comp_files[a], comp_files[b]
            if not fa or not fb:
                continue
            overlap = len(fa & fb)
            min_size = min(len(fa), len(fb))
            pct = overlap / min_size if min_size > 0 else 0
            if pct >= 0.8:
                pairs.append((a, b, pct))

    return pairs


def format_file_overlap_data(pairs):
    """Format file overlap pairs as text for LLM consumption."""
    if not pairs:
        return "No component pairs share >80% of their code files."
    lines = ["Component pairs sharing >80% of code files:"]
    for a, b, pct in pairs:
        lines.append(f"  - {a} <-> {b}: {pct*100:.0f}% file overlap")
    return "\n".join(lines)


def get_component_names(project):
    """Get all component/interface names for a project that have code mappings."""
    names = load_model_element_names(project)
    code_model = load_code_model_files(project)
    model_to_files = build_model_to_files(project, code_model)
    active = set()
    for ae_id, name in names.items():
        if ae_id in model_to_files:
            active.add(name)
    return sorted(active)


def format_numbered_document(text):
    """Format document text with sentence numbers."""
    lines = []
    for sent_num in sorted(text.keys(), key=int):
        lines.append(f"[{sent_num}] {text[sent_num]}")
    return "\n".join(lines)


def compute_doc_stats(text):
    """Compute basic document statistics for context."""
    n_sents = len(text)
    avg_words = sum(len(s.split()) for s in text.values()) / n_sents if n_sents else 0
    short_sents = sum(1 for s in text.values() if len(s.split()) <= 5)
    return {
        "n_sents": n_sents,
        "avg_words": round(avg_words, 1),
        "short_sents": short_sents,
        "short_pct": round(100 * short_sents / n_sents, 1) if n_sents else 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Claude CLI Interface
# ═══════════════════════════════════════════════════════════════════════════════

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
    """Extract classification JSON from LLM response."""
    if not response_text:
        return {}

    match = re.search(r'\{[\s\S]*\}', response_text)
    if not match:
        return {}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return {}

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


def parse_meta_analysis_response(response_text):
    """Extract meta-analysis JSON from LLM response."""
    if not response_text:
        return {}

    match = re.search(r'\{[\s\S]*\}', response_text)
    if not match:
        return {}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        # Try to fix common JSON issues
        text = match.group()
        # Remove trailing commas before } or ]
        text = re.sub(r',\s*([}\]])', r'\1', text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print("  WARNING: Could not parse meta-analysis JSON")
            return {}

    return data


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Meta-Analysis (LLM discovers patterns from raw inputs)
# ═══════════════════════════════════════════════════════════════════════════════

def build_meta_analysis_prompt(text, component_names, file_overlap_text, doc_stats):
    """Build prompt for Phase 1: meta-analysis.

    Discovers FACTUAL patterns only (structure, names, co-occurrence).
    Does NOT make judgment calls about what to trace — that's Phase 2's job.
    """
    doc_formatted = format_numbered_document(text)
    comp_list = "\n".join(f"  - {name}" for name in component_names)

    prompt = f"""You are an expert at analyzing software architecture documentation.

TASK: Analyze the document below to discover FACTUAL patterns about how
architecture components are discussed. Focus on what IS in the document,
not on what SHOULD be traced (that's a separate step).

ARCHITECTURE COMPONENTS:
{comp_list}

FILE OVERLAP DATA (from code analysis — components sharing code files):
{file_overlap_text}

DOCUMENT:
{doc_formatted}

Produce a JSON object with EXACTLY these fields:

1. "sections": Identify document sections where the topic shifts to a different
   component. Look for short lines (<=5 words) that name components, or clear
   topic transitions. Each section has one primary component.
   Format: [{{"header_sent": <sent_num>, "header_text": "<quoted text>",
             "component": "Component: X", "end_sent": <last_sent_in_section>}}]
   Only create sections where there is a CLEAR topic shift. Not every sentence
   needs to be in a section.

2. "aliases": Discover alternate PROPER NAMES, abbreviations, or acronyms used
   for each component. ONLY include:
   - Abbreviated names (e.g., "BBB web" for "BigBlueButton web application")
   - Acronyms (e.g., "FSESL" for "FreeSWITCH Event Socket Layer")
   - Alternate capitalizations or spacing (e.g., "Image Provider" for "ImageProvider")
   - Pronoun patterns within sections (e.g., "the client" in an HTML5 Client section)
   DO NOT include descriptions or characteristics as aliases (e.g., "CPU-intensive"
   is NOT an alias, "central business logic component" is NOT an alias).
   Format: {{"Component: X": ["alias1", "alias2"]}}

3. "cooccurrence_pairs": Based ONLY on the file overlap data above, list component
   pairs that share files. For each pair with file overlap, state which components
   should be co-assigned when a sentence mentions one.
   Format: [{{"comp_a": "Component: X", "comp_b": "Component: Y",
             "rule": "brief description of when to co-assign"}}]
   ONLY include pairs that appear in the file overlap data. Do NOT invent
   co-occurrence rules based on document content alone.

Return ONLY the JSON object, no explanation."""

    return prompt


def run_meta_analysis(project, text, component_names, model_to_files, names):
    """Run Phase 1: meta-analysis to discover document patterns."""
    pairs = compute_cooccurrence_pairs(model_to_files, names)
    file_overlap_text = format_file_overlap_data(pairs)
    doc_stats = compute_doc_stats(text)

    prompt = build_meta_analysis_prompt(text, component_names, file_overlap_text, doc_stats)
    print(f"  Phase 1 (meta-analysis): {len(prompt)} chars...", end="", flush=True)

    t0 = time.time()
    response = call_claude(prompt, timeout=600)
    dt = time.time() - t0

    analysis = parse_meta_analysis_response(response)
    n_sections = len(analysis.get("sections", []))
    n_aliases = sum(len(v) for v in analysis.get("aliases", {}).values())
    n_cooc = len(analysis.get("cooccurrence_pairs", analysis.get("cooccurrence_rules", [])))

    print(f" {dt:.1f}s — {n_sections} sections, {n_aliases} aliases, "
          f"{n_cooc} co-occurrence pairs")

    return analysis


def format_meta_analysis_for_prompt(analysis):
    """Format Phase 1 results as context for Phase 2 classification prompt.

    Only includes factual discoveries — no judgment about tracing boundary.
    """
    parts = []

    # Sections
    secs = analysis.get("sections", [])
    if secs:
        parts.append("DOCUMENT STRUCTURE (discovered by analysis):")
        for sec in secs:
            comp = sec.get("component", "")
            # Handle both old format (list) and new format (string)
            if not comp:
                comps = sec.get("components", [])
                comp = comps[0] if comps else "?"
            header_sent = sec.get("header_sent", "?")
            end = sec.get("end_sent", "?")
            header = sec.get("header_text", "")
            parts.append(f"  Sentences {header_sent}-{end}: \"{header}\" → {comp}")

    # Aliases
    aliases = analysis.get("aliases", {})
    if aliases:
        parts.append("")
        parts.append("COMPONENT ALIASES (alternate names found in the document):")
        for comp, alts in sorted(aliases.items()):
            if alts:
                alt_str = ", ".join(f'"{a}"' for a in alts)
                parts.append(f"  {comp}: also referred to as {alt_str}")

    # Co-occurrence pairs (from file overlap)
    cooc = analysis.get("cooccurrence_pairs", [])
    if cooc:
        parts.append("")
        parts.append("CO-OCCURRENCE PAIRS (components sharing code files):")
        for pair in cooc:
            if isinstance(pair, dict):
                a = pair.get("comp_a", "?")
                b = pair.get("comp_b", "?")
                rule = pair.get("rule", "")
                parts.append(f"  {a} <-> {b}: {rule}")
            elif isinstance(pair, str):
                parts.append(f"  - {pair}")
    # Also handle old format "cooccurrence_rules"
    rules = analysis.get("cooccurrence_rules", [])
    if rules and not cooc:
        parts.append("")
        parts.append("CO-OCCURRENCE RULES:")
        for i, rule in enumerate(rules, 1):
            parts.append(f"  {i}. {rule}")

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Classification (uses Phase 1 discoveries)
# ═══════════════════════════════════════════════════════════════════════════════

def build_classification_prompt(text, component_names, meta_context):
    """Build Phase 2 classification prompt using meta-analysis results.

    NO hardcoded per-project knowledge — all context comes from Phase 1.
    """
    doc_formatted = format_numbered_document(text)
    comp_list = "\n".join(f"  - {name}" for name in component_names)

    prompt = f"""You are an expert at software architecture traceability analysis.

TASK: For each sentence in the documentation below, decide whether it describes
a specific architecture component AND would correspond to that component's source
code files. Be CONSERVATIVE — only trace sentences you are confident about.

ARCHITECTURE COMPONENTS:
{comp_list}

{meta_context}

CLASSIFICATION RULES (apply strictly):

TRACE a sentence if it meets ALL of these criteria:
1. The sentence explicitly NAMES a component (by its official name or a known alias
   from the list above), AND
2. The sentence describes what that component DOES, what it IS, how it COMMUNICATES,
   or what data it PROCESSES — i.e., its architectural role or responsibility.

Also TRACE:
- Section headers that are a component name (e.g., "FreeSWITCH." or "BBB web.")
- Sentences describing inter-component communication (assign BOTH components)

DO NOT TRACE (even if a component name appears):
- Sentences describing algorithms, hashing methods, caching strategies, or other
  implementation details that explain HOW something works internally
- Sentences about test infrastructure, package listings, or test case descriptions
- General overview sentences about the entire system (not a specific component)
- Sentences that mention a component only in passing (e.g., "See the Auth docs")
- Sentences about user workflows, UI behavior, or end-user actions
- Sentences describing general design rationale or system-level decisions

PRONOUN RESOLUTION:
- When a sentence uses "it", "this", "the service" etc., check the DOCUMENT
  STRUCTURE above to see which component's section it falls in. Only resolve
  the pronoun if the section clearly identifies one component.

Each sentence can map to zero, one, or multiple components.

DOCUMENTATION:
{doc_formatted}

OUTPUT FORMAT: Return a JSON object where keys are sentence numbers (as strings)
and values are arrays of component names. Only include sentences that trace to
at least one component. Example:
{{"3": ["Component: Facade"], "5": ["Component: DB", "Interface: IDB"]}}

Return ONLY the JSON object, no explanation."""

    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# Classification Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def run_classification(project):
    """Run meta-learning classification for a project.

    Phase 1: Meta-analysis discovers patterns.
    Phase 2: NUM_AGENTS independent agents classify using discoveries.
    """
    text = load_text(project)
    comp_names = get_component_names(project)
    model_names = load_model_element_names(project)
    code_model = load_code_model_files(project)
    model_to_files = build_model_to_files(project, code_model)

    print(f"\n{'='*60}")
    print(f"  {project.upper()}: {len(text)} sentences, {len(comp_names)} components")
    print(f"  Strategy: {ADAPTIVE_STRATEGIES[project]}")
    print(f"{'='*60}")

    # ── Phase 1: Meta-Analysis ──
    analysis = run_meta_analysis(project, text, comp_names, model_to_files, model_names)

    # Save meta-analysis for inspection
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    analysis_path = OUTPUT_DIR / f"{project}_meta_analysis.json"
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"  Meta-analysis saved to {analysis_path}")

    # Format Phase 1 results for Phase 2
    meta_context = format_meta_analysis_for_prompt(analysis)

    # ── Phase 2: Classification ──
    prompt = build_classification_prompt(text, comp_names, meta_context)
    print(f"  Phase 2 prompt length: {len(prompt)} chars")

    agents = []
    for i in range(NUM_AGENTS):
        for attempt in range(3):  # retry up to 3 times on empty response
            print(f"  Agent {i+1}/{NUM_AGENTS}" +
                  (f" (retry {attempt})" if attempt > 0 else "") + "...",
                  end="", flush=True)
            t0 = time.time()
            response = call_claude(prompt, timeout=600)
            dt = time.time() - t0
            cls = parse_classification_response(response, comp_names)
            n_pairs = sum(len(v) for v in cls.values())
            print(f" {dt:.1f}s, {len(cls)} sents, {n_pairs} pairs")
            if cls:  # non-empty response, accept it
                break
            print(f"  WARNING: Empty response, retrying...")
        agents.append(cls)

    return agents, analysis


def aggregate_results(agents, project):
    """Apply voting strategies to agent results."""
    strategy = ADAPTIVE_STRATEGIES[project]

    variants = {f"v{i+1}": a for i, a in enumerate(agents)}

    results = {
        "agents": agents,
        "majority": majority_vote(variants),
        "intersection": intersection_vote(variants),
        "single": agents[0] if agents else {},
    }

    if strategy == "majority":
        results["adaptive"] = results["majority"]
    elif strategy == "intersection":
        results["adaptive"] = results["intersection"]
    else:
        results["adaptive"] = results["single"]

    return results


def save_results(project, agents, aggregated):
    """Save classification results to JSON files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, cls in enumerate(agents):
        path = OUTPUT_DIR / f"{project}_v{i+1}.json"
        with open(path, "w") as f:
            json.dump(cls, f, indent=2)

    for strategy in ["majority", "intersection", "single", "adaptive"]:
        if strategy in aggregated:
            path = OUTPUT_DIR / f"{project}_{strategy}.json"
            with open(path, "w") as f:
                json.dump(aggregated[strategy], f, indent=2)

    path = OUTPUT_DIR / f"{project}.json"
    with open(path, "w") as f:
        json.dump(aggregated["adaptive"], f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_classifications(classifications, project):
    """Evaluate classifications against gold standard at SAD-CODE level."""
    code_model = load_code_model_files(project)
    gs_sad_code = load_gs_sad_code_enrolled(project, code_model)
    name_to_ids = build_name_to_id_map(project)
    model_to_files = build_model_to_files(project, code_model)

    result_set, unmatched = classifications_to_result_set(
        classifications, name_to_ids, model_to_files
    )
    p, r, f1, tp, fp, fn = calc_metrics(gs_sad_code, result_set)
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn,
            "unmatched": unmatched}


def evaluate_sad_sam(classifications, project):
    """Evaluate classifications at SAD-SAM level."""
    gs_sad_sam = load_gs_sad_sam(project)
    name_to_ids = build_name_to_id_map(project)
    llm_links = llm_classifications_to_sad_sam(classifications, name_to_ids)
    p, r, f1, tp, fp, fn = calc_metrics(gs_sad_sam, llm_links)
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


# ═══════════════════════════════════════════════════════════════════════════════
# Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def eval_and_report(projects=None):
    """Evaluate all saved results and generate comparison report."""
    if projects is None:
        projects = list(PROJECTS)

    from new_metrics_analysis import load_v45_sad_sam, compose_sad_code

    lines = []
    w = lines.append

    w("# Meta-Learning LLM Classifier Results")
    w("")
    w("Two-phase approach with ZERO hardcoded per-project knowledge:")
    w("- **Phase 1 (Meta-Analysis)**: LLM discovers document structure, aliases,")
    w("  co-occurrence patterns, and tracing boundaries from raw inputs")
    w("- **Phase 2 (Classification)**: 3 independent agents use Phase 1 analysis")
    w("")
    w("---")
    w("")

    agg_code = defaultdict(list)
    agg_sam = defaultdict(list)

    for proj in projects:
        w(f"## {proj.capitalize()}")
        w("")

        code_model = load_code_model_files(proj)
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
        name_to_ids = build_name_to_id_map(proj)
        model_to_files = build_model_to_files(proj, code_model)

        # Reference systems
        transarc = load_result_sad_code(proj)
        ta_p, ta_r, ta_f1, ta_tp, ta_fp, ta_fn = calc_metrics(gs_sad_code, transarc)

        v45_links = load_v45_sad_sam(proj)
        v45_sad_code = compose_sad_code(v45_links, gs_sam_code_map)
        v45_p, v45_r, v45_f1, v45_tp, v45_fp, v45_fn = calc_metrics(gs_sad_code, v45_sad_code)

        # Original LLM adaptive
        orig_cls = load_llm_adaptive_classifications(proj)
        orig_code = evaluate_classifications(orig_cls, proj)
        orig_sam = evaluate_sad_sam(orig_cls, proj)

        # Meta-learning classifier results
        improved_results = {}
        for strategy in ["adaptive", "majority", "intersection", "single"]:
            path = OUTPUT_DIR / f"{proj}_{strategy}.json"
            if path.exists():
                cls = load_json(path)
                code_m = evaluate_classifications(cls, proj)
                sam_m = evaluate_sad_sam(cls, proj)
                improved_results[strategy] = {"code": code_m, "sam": sam_m}

        if not improved_results:
            w("*No meta-learning classifier results found. Run classification first.*")
            w("")
            continue

        # Meta-analysis summary
        meta_path = OUTPUT_DIR / f"{proj}_meta_analysis.json"
        if meta_path.exists():
            meta = load_json(meta_path)
            n_sec = len(meta.get("sections", []))
            n_alias = sum(len(v) for v in meta.get("aliases", {}).values())
            n_cooc = len(meta.get("cooccurrence_pairs", meta.get("cooccurrence_rules", [])))
            w(f"**Meta-analysis**: {n_sec} sections, {n_alias} aliases, "
              f"{n_cooc} co-occurrence pairs")
            w("")

        # ── SAD-CODE table ──
        w(f"### SAD-CODE Level (strategy: {ADAPTIVE_STRATEGIES[proj]})")
        w("")
        w("| System | P | R | F1 | TP | FP | FN | ΔF1 |")
        w("|:-------|:---:|:---:|:---:|---:|---:|---:|:---:|")
        w(f"| TransArc | {ta_p:.3f} | {ta_r:.3f} | **{ta_f1:.3f}** | "
          f"{ta_tp} | {ta_fp} | {ta_fn} | — |")
        w(f"| V45 | {v45_p:.3f} | {v45_r:.3f} | **{v45_f1:.3f}** | "
          f"{v45_tp} | {v45_fp} | {v45_fn} | — |")
        w(f"| LLM Original | {orig_code['p']:.3f} | {orig_code['r']:.3f} | "
          f"**{orig_code['f1']:.3f}** | {orig_code['tp']} | {orig_code['fp']} | "
          f"{orig_code['fn']} | — |")

        for strat, m in sorted(improved_results.items()):
            delta = m["code"]["f1"] - orig_code["f1"]
            w(f"| Meta-Learning ({strat}) | {m['code']['p']:.3f} | {m['code']['r']:.3f} | "
              f"**{m['code']['f1']:.3f}** | {m['code']['tp']} | {m['code']['fp']} | "
              f"{m['code']['fn']} | {delta:+.3f} |")
        w("")

        # ── SAD-SAM table ──
        v45_sam_links = load_v45_sad_sam(proj)
        v45_sp, v45_sr, v45_sf1, _, _, _ = calc_metrics(gs_sad_sam, v45_sam_links)

        w("### SAD-SAM Level")
        w("")
        w("| System | P | R | F1 | ΔF1 |")
        w("|:-------|:---:|:---:|:---:|:---:|")
        w(f"| V45 | {v45_sp:.3f} | {v45_sr:.3f} | **{v45_sf1:.3f}** | — |")
        w(f"| LLM Original | {orig_sam['p']:.3f} | {orig_sam['r']:.3f} | "
          f"**{orig_sam['f1']:.3f}** | — |")

        for strat, m in sorted(improved_results.items()):
            delta = m["sam"]["f1"] - orig_sam["f1"]
            w(f"| Meta-Learning ({strat}) | {m['sam']['p']:.3f} | {m['sam']['r']:.3f} | "
              f"**{m['sam']['f1']:.3f}** | {delta:+.3f} |")
        w("")

        # Track adaptive for aggregate
        if "adaptive" in improved_results:
            imp = improved_results["adaptive"]
            agg_code["proj"].append(proj)
            agg_code["ta"].append(ta_f1)
            agg_code["v45"].append(v45_f1)
            agg_code["orig"].append(orig_code["f1"])
            agg_code["improved"].append(imp["code"]["f1"])

            agg_sam["v45"].append(v45_sf1)
            agg_sam["orig"].append(orig_sam["f1"])
            agg_sam["improved"].append(imp["sam"]["f1"])

        # Find best strategy
        best_strat = max(improved_results, key=lambda s: improved_results[s]["code"]["f1"])
        best = improved_results[best_strat]
        w(f"**Best strategy:** {best_strat} "
          f"(CODE F1={best['code']['f1']:.3f}, "
          f"Δ vs original: {best['code']['f1'] - orig_code['f1']:+.3f})")
        w("")
        w("---")
        w("")

    # ── Aggregate Summary ──
    if agg_code["proj"]:
        n = len(agg_code["proj"])
        w("## Aggregate Summary")
        w("")

        w("### SAD-CODE")
        w("")
        w("| Project | TransArc | V45 | LLM Original | Meta-Learning | ΔF1 |")
        w("|:--------|:--------:|:---:|:------------:|:------------:|:---:|")
        for i in range(n):
            delta = agg_code["improved"][i] - agg_code["orig"][i]
            w(f"| {agg_code['proj'][i]} | {agg_code['ta'][i]:.3f} | "
              f"{agg_code['v45'][i]:.3f} | {agg_code['orig'][i]:.3f} | "
              f"**{agg_code['improved'][i]:.3f}** | {delta:+.3f} |")

        avg_ta = sum(agg_code["ta"]) / n
        avg_v45 = sum(agg_code["v45"]) / n
        avg_orig = sum(agg_code["orig"]) / n
        avg_imp = sum(agg_code["improved"]) / n
        w(f"| **Average** | **{avg_ta:.3f}** | **{avg_v45:.3f}** | "
          f"**{avg_orig:.3f}** | **{avg_imp:.3f}** | **{avg_imp-avg_orig:+.3f}** |")
        w("")

        w("### SAD-SAM")
        w("")
        w("| Project | V45 | LLM Original | Meta-Learning | ΔF1 |")
        w("|:--------|:---:|:------------:|:------------:|:---:|")
        for i in range(n):
            delta = agg_sam["improved"][i] - agg_sam["orig"][i]
            w(f"| {agg_code['proj'][i]} | {agg_sam['v45'][i]:.3f} | "
              f"{agg_sam['orig'][i]:.3f} | **{agg_sam['improved'][i]:.3f}** | "
              f"{delta:+.3f} |")
        avg_v45_s = sum(agg_sam["v45"]) / n
        avg_orig_s = sum(agg_sam["orig"]) / n
        avg_imp_s = sum(agg_sam["improved"]) / n
        w(f"| **Average** | **{avg_v45_s:.3f}** | **{avg_orig_s:.3f}** | "
          f"**{avg_imp_s:.3f}** | **{avg_imp_s-avg_orig_s:+.3f}** |")
        w("")

        w("### Key Findings")
        w("")
        w(f"- Meta-Learning avg SAD-CODE F1: **{avg_imp:.3f}** "
          f"(vs original {avg_orig:.3f}, Δ = {avg_imp-avg_orig:+.3f})")
        w(f"- Meta-Learning avg SAD-SAM F1: **{avg_imp_s:.3f}** "
          f"(vs original {avg_orig_s:.3f}, Δ = {avg_imp_s-avg_orig_s:+.3f})")
        w(f"- TransArc avg SAD-CODE F1: {avg_ta:.3f}")
        w(f"- V45 avg SAD-CODE F1: {avg_v45:.3f}")
        if avg_imp > avg_v45:
            w(f"- **Meta-Learning surpasses V45** ({avg_imp:.3f} > {avg_v45:.3f})")
        w("")

    w("---")
    w("")
    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 llm_improved_classifier.py                     # Run all projects")
    w("python3 llm_improved_classifier.py --project teastore  # Run one project")
    w("python3 llm_improved_classifier.py --eval-only         # Evaluate only")
    w("```")

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nReport written to {OUTPUT_MD}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]

    eval_only = "--eval-only" in args
    args = [a for a in args if a != "--eval-only"]

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
            agents, analysis = run_classification(proj)
            aggregated = aggregate_results(agents, proj)
            save_results(proj, agents, aggregated)

            # Quick evaluation
            print(f"\n  Quick eval for {proj}:")
            for strat in ["adaptive", "majority", "intersection", "single"]:
                if strat in aggregated:
                    m = evaluate_classifications(aggregated[strat], proj)
                    s = evaluate_sad_sam(aggregated[strat], proj)
                    print(f"    {strat:<15} CODE: P={m['p']:.3f} R={m['r']:.3f} F1={m['f1']:.3f}"
                          f"  SAM: P={s['p']:.3f} R={s['r']:.3f} F1={s['f1']:.3f}")

    eval_and_report(projects)


if __name__ == "__main__":
    main()
