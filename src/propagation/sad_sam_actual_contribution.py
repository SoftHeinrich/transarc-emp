#!/usr/bin/env python3
"""
SAD-SAM Actual Contribution Analysis

For every SAD-SAM intermediate link (M, S), trace forward through the actual
TransArc pipeline to count the real SAD-CODE links it produced.

Every TransArc output link (S, C) exists because some intermediate SAD-SAM
link (M, S) was composed with some intermediate SAM-CODE link (M, C).
This script attributes each actual SAD-CODE output link back to its SAD-SAM
source(s) and counts the real TPs and FPs each SAD-SAM link produced.
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw, load_gs_sad_code_enrolled,
    load_result_sad_code,
    load_transarc_intermediate_maps,
    load_model_element_names, load_text,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/SAD_SAM_ACTUAL_CONTRIBUTION.md")


def analyze_project(proj):
    code_model = load_code_model_files(proj)
    texts = load_text(proj)
    names = load_model_element_names(proj)

    # Gold standards (enrolled)
    gs_sad_sam = load_gs_sad_sam(proj)
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)

    # Actual TransArc output
    transarc_output = load_result_sad_code(proj)
    transarc_tps = transarc_output & gs_sad_code
    transarc_fps = transarc_output - gs_sad_code

    # Intermediate maps
    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(proj)

    # ─── Attribute each actual SAD-CODE link to its SAD-SAM source(s) ─────

    # For each transarc output link (S, C), find bridging M(s)
    # where (M, S) in intermediate SAD-SAM AND (M, C) in intermediate SAM-CODE
    sad_sam_to_sad_code_tps = defaultdict(set)  # (M, S) -> set of (S, C) TPs
    sad_sam_to_sad_code_fps = defaultdict(set)  # (M, S) -> set of (S, C) FPs

    for (s, c) in transarc_output:
        models_for_s = sent_to_models.get(s, set())
        models_for_c = code_to_models.get(c, set())
        bridges = models_for_s & models_for_c

        is_tp = (s, c) in gs_sad_code

        for m in bridges:
            key = (m, s)
            if is_tp:
                sad_sam_to_sad_code_tps[key].add((s, c))
            else:
                sad_sam_to_sad_code_fps[key].add((s, c))

    # ─── Build per-SAD-SAM-link summary ───────────────────────────────

    # All intermediate SAD-SAM links
    all_sad_sam_links = set()
    for s, models in sent_to_models.items():
        for m in models:
            all_sad_sam_links.add((m, s))

    rows = []
    for (m, s) in all_sad_sam_links:
        is_sad_sam_tp = (m, s) in gs_sad_sam
        produced_tps = sad_sam_to_sad_code_tps.get((m, s), set())
        produced_fps = sad_sam_to_sad_code_fps.get((m, s), set())

        rows.append({
            "model": m,
            "sentence": s,
            "model_name": names.get(m, m),
            "sentence_text": texts.get(s, "<unknown>"),
            "sad_sam_status": "TP" if is_sad_sam_tp else "FP",
            "sad_code_tps": len(produced_tps),
            "sad_code_fps": len(produced_fps),
            "sad_code_total": len(produced_tps) + len(produced_fps),
            "tp_links": produced_tps,
            "fp_links": produced_fps,
        })

    return rows, {
        "transarc_tps": len(transarc_tps),
        "transarc_fps": len(transarc_fps),
        "transarc_total": len(transarc_output),
        "sad_sam_tps": sum(1 for r in rows if r["sad_sam_status"] == "TP"),
        "sad_sam_fps": sum(1 for r in rows if r["sad_sam_status"] == "FP"),
        "gs_sad_code_size": len(gs_sad_code),
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# SAD-SAM Actual Contribution to SAD-CODE Output")
    out()
    out("Every TransArc output link (S, C) was produced by composing an intermediate")
    out("SAD-SAM link (M, S) with an intermediate SAM-CODE link (M, C). This study")
    out("traces each **actual** SAD-CODE output link back to its SAD-SAM source and")
    out("counts the real TPs and FPs each SAD-SAM link produced.")
    out()
    out("A single SAD-CODE link may be attributed to multiple SAD-SAM links if")
    out("multiple bridging model elements exist. Counts reflect actual attribution.")
    out()

    all_results = {}
    for proj in PROJECTS:
        rows, stats = analyze_project(proj)
        all_results[proj] = (rows, stats)

    # ─── Overview ─────────────────────────────────────────────────────

    out("## Overview")
    out()
    out("| Project | SAD-SAM TPs | SAD-SAM FPs | SAD-CODE TPs | SAD-CODE FPs | SAD-CODE Total |")
    out("|---------|------------|------------|-------------|-------------|---------------|")
    for proj in PROJECTS:
        _, stats = all_results[proj]
        out(f"| {proj} | {stats['sad_sam_tps']} | {stats['sad_sam_fps']} | "
            f"{stats['transarc_tps']} | {stats['transarc_fps']} | {stats['transarc_total']} |")
    out()

    # ─── Per-project: Full ranked table ───────────────────────────────

    for proj in PROJECTS:
        rows, stats = all_results[proj]
        names = load_model_element_names(proj)
        texts = load_text(proj)

        out(f"## {proj.upper()}")
        out()
        out(f"TransArc output: {stats['transarc_tps']} TPs + {stats['transarc_fps']} FPs = "
            f"{stats['transarc_total']} total | Gold: {stats['gs_sad_code_size']}")
        out()

        # ── Table 1: SAD-SAM TPs ranked by SAD-CODE TPs produced ──

        tp_rows = [r for r in rows if r["sad_sam_status"] == "TP"]
        tp_rows.sort(key=lambda r: r["sad_code_tps"], reverse=True)

        out(f"### SAD-SAM TPs → Actual SAD-CODE Links Produced ({len(tp_rows)} links)")
        out()
        out("| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |")
        out("|------|--------------|------|---------------|-------------|-------------|-------|")

        for i, r in enumerate(tp_rows, 1):
            st = r["sentence_text"][:65] + ("..." if len(r["sentence_text"]) > 65 else "")
            out(f"| {i} | {r['model_name']} | {r['sentence']} | {st} | "
                f"**{r['sad_code_tps']}** | {r['sad_code_fps']} | {r['sad_code_total']} |")

        # Totals
        sum_tps = sum(r["sad_code_tps"] for r in tp_rows)
        sum_fps = sum(r["sad_code_fps"] for r in tp_rows)
        out(f"| | **TOTAL** | | | **{sum_tps}** | **{sum_fps}** | **{sum_tps + sum_fps}** |")
        out()

        # ── Table 2: SAD-SAM FPs ranked by SAD-CODE FPs produced ──

        fp_rows = [r for r in rows if r["sad_sam_status"] == "FP"]
        fp_rows.sort(key=lambda r: r["sad_code_fps"], reverse=True)

        if fp_rows:
            out(f"### SAD-SAM FPs → Actual SAD-CODE Links Produced ({len(fp_rows)} links)")
            out()
            out("| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |")
            out("|------|--------------|------|---------------|-------------|-------------|-------|")

            for i, r in enumerate(fp_rows, 1):
                st = r["sentence_text"][:65] + ("..." if len(r["sentence_text"]) > 65 else "")
                out(f"| {i} | {r['model_name']} | {r['sentence']} | {st} | "
                    f"{r['sad_code_tps']} | **{r['sad_code_fps']}** | {r['sad_code_total']} |")

            sum_tps = sum(r["sad_code_tps"] for r in fp_rows)
            sum_fps = sum(r["sad_code_fps"] for r in fp_rows)
            out(f"| | **TOTAL** | | | **{sum_tps}** | **{sum_fps}** | **{sum_tps + sum_fps}** |")
            out()
        else:
            out(f"### SAD-SAM FPs → No SAD-SAM FPs in this project")
            out()

        # ── Summary per model element ──

        model_agg = defaultdict(lambda: {"name": "", "tp_links": 0, "tp_tps": 0, "tp_fps": 0,
                                          "fp_links": 0, "fp_tps": 0, "fp_fps": 0})
        for r in rows:
            m = model_agg[r["model"]]
            m["name"] = r["model_name"]
            if r["sad_sam_status"] == "TP":
                m["tp_links"] += 1
                m["tp_tps"] += r["sad_code_tps"]
                m["tp_fps"] += r["sad_code_fps"]
            else:
                m["fp_links"] += 1
                m["fp_tps"] += r["sad_code_tps"]
                m["fp_fps"] += r["sad_code_fps"]

        out(f"### Per-Model-Element Summary")
        out()
        out("| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |")
        out("|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|")

        sorted_models = sorted(model_agg.items(),
                               key=lambda kv: kv[1]["tp_tps"] - kv[1]["fp_fps"],
                               reverse=True)

        for m_id, m in sorted_models:
            net = (m["tp_tps"] + m["fp_tps"]) - (m["tp_fps"] + m["fp_fps"])
            out(f"| {m['name']} | {m['tp_links']} | {m['tp_tps']} | {m['tp_fps']} | "
                f"{m['fp_links']} | {m['fp_tps']} | {m['fp_fps']} | {net:+d} |")

        out()

    # ─── Cross-project: Top SAD-SAM TPs ───────────────────────────────

    out("## Cross-Project Ranking: SAD-SAM TPs by Actual SAD-CODE TPs Produced")
    out()

    all_tp_rows = []
    for proj in PROJECTS:
        rows, _ = all_results[proj]
        for r in rows:
            if r["sad_sam_status"] == "TP":
                all_tp_rows.append((proj, r))

    all_tp_rows.sort(key=lambda t: t[1]["sad_code_tps"], reverse=True)

    out("| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |")
    out("|------|---------|--------------|------|---------------|-------------|-------------|")

    for i, (proj, r) in enumerate(all_tp_rows[:40], 1):
        st = r["sentence_text"][:55] + ("..." if len(r["sentence_text"]) > 55 else "")
        out(f"| {i} | {proj} | {r['model_name']} | {r['sentence']} | {st} | "
            f"**{r['sad_code_tps']}** | {r['sad_code_fps']} |")

    out()

    # ─── Cross-project: Top SAD-SAM FPs ───────────────────────────────

    out("## Cross-Project Ranking: SAD-SAM FPs by Actual SAD-CODE FPs Produced")
    out()

    all_fp_rows = []
    for proj in PROJECTS:
        rows, _ = all_results[proj]
        for r in rows:
            if r["sad_sam_status"] == "FP":
                all_fp_rows.append((proj, r))

    all_fp_rows.sort(key=lambda t: t[1]["sad_code_fps"], reverse=True)

    if all_fp_rows:
        out("| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |")
        out("|------|---------|--------------|------|---------------|-------------|-------------|")

        for i, (proj, r) in enumerate(all_fp_rows[:40], 1):
            st = r["sentence_text"][:55] + ("..." if len(r["sentence_text"]) > 55 else "")
            out(f"| {i} | {proj} | {r['model_name']} | {r['sentence']} | {st} | "
                f"{r['sad_code_tps']} | **{r['sad_code_fps']}** |")

        out()
    else:
        out("No SAD-SAM FPs across any project.")
        out()

    # ─── Efficiency analysis ──────────────────────────────────────────

    out("## SAD-SAM Link Efficiency")
    out()
    out("What fraction of SAD-CODE output from each SAD-SAM link is correct?")
    out()

    out("### SAD-SAM TPs: Precision of SAD-CODE Output")
    out()
    out("| Project | SAD-SAM TP | Model Element | Sent | Total Produced | TPs | FPs | Precision |")
    out("|---------|-----------|--------------|------|---------------|-----|-----|-----------|")

    # Show the least precise SAD-SAM TPs (those producing the most FPs relative to TPs)
    low_prec = []
    for proj in PROJECTS:
        rows, _ = all_results[proj]
        for r in rows:
            if r["sad_sam_status"] == "TP" and r["sad_code_total"] > 0:
                prec = r["sad_code_tps"] / r["sad_code_total"]
                low_prec.append((proj, r, prec))

    low_prec.sort(key=lambda t: t[2])

    for proj, r, prec in low_prec[:20]:
        st = r["sentence_text"][:50] + ("..." if len(r["sentence_text"]) > 50 else "")
        out(f"| {proj} | ({r['model_name']}, S{r['sentence']}) | {r['model_name']} | {r['sentence']} | "
            f"{r['sad_code_total']} | {r['sad_code_tps']} | {r['sad_code_fps']} | {prec:.3f} |")

    out()

    # ─── Write report ─────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
