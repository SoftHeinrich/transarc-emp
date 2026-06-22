#!/usr/bin/env python3
"""
SAD-SAM TP Gain → SAD-CODE Impact Analysis

For each SAD-SAM gold link that TransArc currently misses (SAD-SAM FN),
compute how many new SAD-CODE true positives would be gained if that
single SAD-SAM link were recovered — using the *actual* intermediate
SAM-CODE results as the bridge.

Also analyzes existing SAD-SAM TPs: how many SAD-CODE TPs does each
one currently produce, and how many additional ones would it produce
if it were somehow lost.

Produces a ranked list per project and a cross-project summary.
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

# Reuse infrastructure from the main analysis
from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS, TEXT_FILES,
    GS_SAD_SAM, GS_SAM_CODE, GS_SAD_CODE, ACM_FILES,
    normalize_path, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_code_enrolled, load_gs_sam_code_raw,
    load_result_sad_sam_standalone, load_result_sad_code,
    load_transarc_intermediate_sam_code, load_transarc_intermediate_maps,
    load_model_element_names, load_text,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/SAD_SAM_TP_GAIN_STUDY.md")


def analyze_project(proj):
    """For a project, compute the SAD-CODE TP gain for each SAD-SAM FN,
    and the current SAD-CODE TP contribution of each SAD-SAM TP."""

    code_model = load_code_model_files(proj)
    texts = load_text(proj)
    names = load_model_element_names(proj)

    # Gold standards
    gs_sad_sam = load_gs_sad_sam(proj)  # set of (modelElementID, sentence)
    gs_sad_code_enrolled = load_gs_sad_code_enrolled(proj, code_model)

    # TransArc results
    result_sad_sam = load_result_sad_sam_standalone(proj)  # = intermediate SAD-SAM
    result_sad_code = load_result_sad_code(proj)

    # Intermediate SAM-CODE map: model -> set(code)
    _, model_to_codes_int, _, _ = load_transarc_intermediate_maps(proj)

    # Current SAD-CODE TPs and FNs
    sad_code_tps = result_sad_code & gs_sad_code_enrolled
    sad_code_fns = gs_sad_code_enrolled - result_sad_code

    # ─── Part 1: SAD-SAM FN → potential SAD-CODE TP gain ──────────────

    sad_sam_fns = gs_sad_sam - result_sad_sam  # missed gold SAD-SAM links

    fn_gains = []  # (model, sentence, new_tps, new_tp_links, would_also_produce_fps)

    for (m, s) in sad_sam_fns:
        # If we recovered this SAD-SAM link, we'd compose (M,S) with SAM-CODE
        # to get transitive links (S, C) for each C in model_to_codes_int[M]
        codes = model_to_codes_int.get(m, set())

        new_tps = []       # (s, c) that are gold SAD-CODE TPs we don't currently have
        new_fps = []       # (s, c) that are NOT in gold (would be new FPs)
        already_found = [] # (s, c) already in TransArc result

        for c in codes:
            link = (s, c)
            if link in sad_code_tps:
                already_found.append(link)
            elif link in sad_code_fns:
                new_tps.append(link)
            else:
                # Not in gold standard → this would be a new FP
                new_fps.append(link)

        fn_gains.append({
            "model": m,
            "sentence": s,
            "model_name": names.get(m, m),
            "sentence_text": texts.get(s, "<unknown>"),
            "new_tps": len(new_tps),
            "new_tp_links": new_tps,
            "new_fps": len(new_fps),
            "already_found": len(already_found),
            "total_codes": len(codes),
        })

    # Sort by new TPs descending
    fn_gains.sort(key=lambda x: x["new_tps"], reverse=True)

    # ─── Part 2: SAD-SAM TP → current SAD-CODE contribution ──────────

    sad_sam_tps = gs_sad_sam & result_sad_sam  # correctly found SAD-SAM links

    tp_contributions = []

    for (m, s) in sad_sam_tps:
        codes = model_to_codes_int.get(m, set())

        contributed_tps = []
        contributed_fps = []

        for c in codes:
            link = (s, c)
            if link in sad_code_tps:
                contributed_tps.append(link)
            elif link not in gs_sad_code_enrolled:
                contributed_fps.append(link)

        tp_contributions.append({
            "model": m,
            "sentence": s,
            "model_name": names.get(m, m),
            "sentence_text": texts.get(s, "<unknown>"),
            "contributed_tps": len(contributed_tps),
            "contributed_fps": len(contributed_fps),
            "total_codes": len(codes),
        })

    tp_contributions.sort(key=lambda x: x["contributed_tps"], reverse=True)

    return {
        "fn_gains": fn_gains,
        "tp_contributions": tp_contributions,
        "stats": {
            "sad_sam_gold": len(gs_sad_sam),
            "sad_sam_result": len(result_sad_sam),
            "sad_sam_tps": len(sad_sam_tps),
            "sad_sam_fns": len(sad_sam_fns),
            "sad_sam_fps": len(result_sad_sam - gs_sad_sam),
            "sad_code_gold": len(gs_sad_code_enrolled),
            "sad_code_result": len(result_sad_code),
            "sad_code_tps": len(sad_code_tps),
            "sad_code_fns": len(sad_code_fns),
        }
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# SAD-SAM TP Gain → SAD-CODE Impact Study")
    out()
    out("For each missed SAD-SAM gold link (a SAD-SAM FN), we ask: if TransArc had found")
    out("this link, how many **new SAD-CODE true positives** would it unlock?")
    out()
    out("The mechanism: a recovered SAD-SAM link (M, S) composes with the actual")
    out("intermediate SAM-CODE links for M to produce transitive links (S, C).")
    out("We check each (S, C) against the enrolled SAD-CODE gold standard.")
    out()

    all_results = {}
    for proj in PROJECTS:
        all_results[proj] = analyze_project(proj)

    # ─── Overview table ───────────────────────────────────────────────

    out("## Overview")
    out()
    out("| Project | SAD-SAM FNs | Total Potential New SAD-CODE TPs | Max Single-Link Gain | Avg Gain/FN |")
    out("|---------|-------------|--------------------------------|---------------------|-------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        fns = r["fn_gains"]
        total_gain = sum(x["new_tps"] for x in fns)
        max_gain = fns[0]["new_tps"] if fns else 0
        avg_gain = total_gain / len(fns) if fns else 0
        out(f"| {proj} | {len(fns)} | {total_gain} | {max_gain} | {avg_gain:.1f} |")

    out()

    # Context: how does total gain compare to current FNs?
    out("### Gain vs Current SAD-CODE FNs")
    out()
    out("| Project | SAD-CODE FNs | Recoverable via SAD-SAM FN Recovery | Coverage |")
    out("|---------|-------------|-------------------------------------|----------|")

    for proj in PROJECTS:
        r = all_results[proj]
        fns = r["fn_gains"]
        sad_code_fns = r["stats"]["sad_code_fns"]
        # Collect all unique new TP links
        all_new_tp_links = set()
        for x in fns:
            all_new_tp_links.update(x["new_tp_links"])
        coverage = len(all_new_tp_links) / sad_code_fns * 100 if sad_code_fns else 0
        out(f"| {proj} | {sad_code_fns} | {len(all_new_tp_links)} | {coverage:.1f}% |")

    out()

    # ─── Per-project ranked lists ─────────────────────────────────────

    out("## Per-Project Ranking: SAD-SAM FNs by Potential SAD-CODE TP Gain")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        fns = r["fn_gains"]
        stats = r["stats"]

        out(f"### {proj.upper()}")
        out()
        out(f"SAD-SAM: {stats['sad_sam_tps']} TP, {stats['sad_sam_fns']} FN, {stats['sad_sam_fps']} FP | "
            f"SAD-CODE: {stats['sad_code_tps']} TP, {stats['sad_code_fns']} FN")
        out()

        if not fns:
            out("No SAD-SAM FNs — all gold links are already recovered.")
            out()
            continue

        out("| Rank | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | Already Found | SAM-CODE Links |")
        out("|------|--------------|----------|----------------------|---------|---------|---------------|----------------|")

        for i, x in enumerate(fns, 1):
            sent_text = x["sentence_text"][:60] + ("..." if len(x["sentence_text"]) > 60 else "")
            out(f"| {i} | {x['model_name']} | {x['sentence']} | {sent_text} | **{x['new_tps']}** | {x['new_fps']} | {x['already_found']} | {x['total_codes']} |")

        out()

        # Summary stats for this project
        total_new_tps = sum(x["new_tps"] for x in fns)
        total_new_fps = sum(x["new_fps"] for x in fns)
        gain_zero = sum(1 for x in fns if x["new_tps"] == 0)

        out(f"**Summary**: {len(fns)} SAD-SAM FNs → {total_new_tps} potential new SAD-CODE TPs, "
            f"{total_new_fps} new FPs | {gain_zero} FNs with zero TP gain")
        out()

    # ─── Cross-project aggregate ranking ──────────────────────────────

    out("## Cross-Project Aggregate Ranking (Top 30)")
    out()
    out("All SAD-SAM FNs across all projects, ranked by potential SAD-CODE TP gain.")
    out()
    out("| Rank | Project | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | TP/FP Ratio |")
    out("|------|---------|--------------|----------|----------------------|---------|---------|-------------|")

    all_fns = []
    for proj in PROJECTS:
        for x in all_results[proj]["fn_gains"]:
            all_fns.append((proj, x))

    all_fns.sort(key=lambda t: t[1]["new_tps"], reverse=True)

    for i, (proj, x) in enumerate(all_fns[:30], 1):
        sent_text = x["sentence_text"][:55] + ("..." if len(x["sentence_text"]) > 55 else "")
        ratio = f"{x['new_tps']/x['new_fps']:.1f}" if x["new_fps"] > 0 else "inf"
        out(f"| {i} | {proj} | {x['model_name']} | {x['sentence']} | {sent_text} | **{x['new_tps']}** | {x['new_fps']} | {ratio} |")

    out()

    # ─── Existing SAD-SAM TPs: current contribution ──────────────────

    out("## Existing SAD-SAM TPs: Current SAD-CODE Contribution")
    out()
    out("How many SAD-CODE TPs does each existing SAD-SAM TP currently produce?")
    out("(If this SAD-SAM TP were lost, these SAD-CODE TPs would become FNs.)")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        tps = r["tp_contributions"]

        out(f"### {proj.upper()}")
        out()

        if not tps:
            out("No SAD-SAM TPs.")
            out()
            continue

        out("| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |")
        out("|------|--------------|----------|----------------------|-------------|-------------|----------------|")

        for i, x in enumerate(tps, 1):
            sent_text = x["sentence_text"][:60] + ("..." if len(x["sentence_text"]) > 60 else "")
            out(f"| {i} | {x['model_name']} | {x['sentence']} | {sent_text} | **{x['contributed_tps']}** | {x['contributed_fps']} | {x['total_codes']} |")

        out()

        total_tps = sum(x["contributed_tps"] for x in tps)
        total_fps = sum(x["contributed_fps"] for x in tps)
        out(f"**Summary**: {len(tps)} SAD-SAM TPs produce {total_tps} SAD-CODE TPs and {total_fps} SAD-CODE FPs")
        out()

    # ─── Model element analysis ───────────────────────────────────────

    out("## Model Element Impact Analysis")
    out()
    out("Which model elements have the highest total SAD-CODE impact (TPs gained + TPs lost)?")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        names = load_model_element_names(proj)

        # Aggregate by model element
        model_stats = defaultdict(lambda: {
            "name": "", "fn_new_tps": 0, "fn_new_fps": 0, "fn_count": 0,
            "tp_contributed_tps": 0, "tp_contributed_fps": 0, "tp_count": 0,
        })

        for x in r["fn_gains"]:
            ms = model_stats[x["model"]]
            ms["name"] = x["model_name"]
            ms["fn_new_tps"] += x["new_tps"]
            ms["fn_new_fps"] += x["new_fps"]
            ms["fn_count"] += 1

        for x in r["tp_contributions"]:
            ms = model_stats[x["model"]]
            ms["name"] = x["model_name"]
            ms["tp_contributed_tps"] += x["contributed_tps"]
            ms["tp_contributed_fps"] += x["contributed_fps"]
            ms["tp_count"] += 1

        if not model_stats:
            continue

        out(f"### {proj.upper()}")
        out()
        out("| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |")
        out("|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|")

        sorted_models = sorted(model_stats.items(),
                               key=lambda kv: kv[1]["fn_new_tps"] + kv[1]["tp_contributed_tps"],
                               reverse=True)

        for m_id, ms in sorted_models:
            total = ms["fn_new_tps"] + ms["tp_contributed_tps"]
            out(f"| {ms['name']} | {ms['tp_count']} | {ms['tp_contributed_tps']} | {ms['fn_count']} | {ms['fn_new_tps']} | {ms['fn_new_fps']} | {total} |")

        out()

    # ─── Diminishing returns: cumulative recovery ─────────────────────

    out("## Cumulative Recovery Curve")
    out()
    out("If we recover SAD-SAM FNs in order of highest TP gain, how does SAD-CODE recall improve?")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        fns = r["fn_gains"]
        stats = r["stats"]

        if not fns or stats["sad_code_fns"] == 0:
            continue

        out(f"### {proj.upper()}")
        out()
        out(f"Current SAD-CODE: TP={stats['sad_code_tps']}, FN={stats['sad_code_fns']}, "
            f"Gold={stats['sad_code_gold']}")
        out()

        out("| SAD-SAM FNs Recovered | Cumul. New TPs | New Recall | Recall Delta |")
        out("|----------------------|----------------|-----------|--------------|")

        cumul_tps = 0
        current_recall = stats["sad_code_tps"] / stats["sad_code_gold"]

        # Show milestones: 1, 2, 3, 5, 10, 25%, 50%, 75%, 100%
        milestones = {1, 2, 3, 5, 10}
        pct_milestones = {int(len(fns) * p) for p in [0.25, 0.5, 0.75, 1.0]}
        milestones.update(pct_milestones)
        milestones.add(len(fns))  # always show final

        # Track unique new TP links to avoid double-counting
        recovered_tp_links = set()

        for i, x in enumerate(fns, 1):
            for link in x["new_tp_links"]:
                recovered_tp_links.add(link)

            if i in milestones or i <= 5:
                new_total_tps = stats["sad_code_tps"] + len(recovered_tp_links)
                new_recall = new_total_tps / stats["sad_code_gold"]
                delta = new_recall - current_recall
                out(f"| {i}/{len(fns)} | {len(recovered_tp_links)} | {new_recall:.3f} | +{delta:.3f} |")

        out()

    # ─── Write report ─────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\n\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
