#!/usr/bin/env python3
"""
SAM-CODE Error Cascade & Holistic Pipeline Analysis

Traces every SAM-CODE link (TP/FP/FN) forward through the TransArc pipeline
to measure its actual impact on SAD-CODE output. Then combines with SAD-SAM
error contributions for a holistic per-model-element view of the full pipeline.

Key question: for each SAM-CODE link (M, C), how many actual SAD-CODE
TPs and FPs did it produce? And how does this combine with SAD-SAM errors
per model element?
"""

from collections import defaultdict
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw,
    load_gs_sad_code_enrolled,
    load_result_sad_code,
    load_transarc_intermediate_maps,
    load_transarc_intermediate_sad_sam,
    load_transarc_intermediate_sam_code,
    load_model_element_names, load_text,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/SAM_CODE_CASCADE.md")


def analyze_project(proj):
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)
    texts = load_text(proj)

    # Gold standards
    gs_sad_sam = load_gs_sad_sam(proj)
    gs_sam_code_raw = load_gs_sam_code_raw(proj)
    gs_sam_code = enroll_gold_standard(gs_sam_code_raw, code_model)
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)

    # TransArc output and intermediates
    transarc_output = load_result_sad_code(proj)
    transarc_tps = transarc_output & gs_sad_code
    transarc_fps = transarc_output - gs_sad_code
    transarc_fns = gs_sad_code - transarc_output

    int_sad_sam = load_transarc_intermediate_sad_sam(proj)
    int_sam_code = load_transarc_intermediate_sam_code(proj)

    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(proj)

    # ─── SAM-CODE link classification ────────────────────────────────
    sam_code_tps = int_sam_code & gs_sam_code
    sam_code_fps = int_sam_code - gs_sam_code
    sam_code_fns = gs_sam_code - int_sam_code

    # ─── SAD-SAM link classification ─────────────────────────────────
    sad_sam_tps = int_sad_sam & gs_sad_sam
    sad_sam_fps = int_sad_sam - gs_sad_sam

    # ═══ FORWARD TRACE: SAM-CODE → SAD-CODE ══════════════════════════
    #
    # Every TransArc output link (S, C) was produced by composing
    # intermediate SAD-SAM (M, S) with intermediate SAM-CODE (M, C).
    # For each SAM-CODE link (M, C), find all SAD-SAM links (M, S)
    # that produced output links (S, C).

    # For each intermediate SAM-CODE link, count actual SAD-CODE output
    sam_code_link_to_output_tps = defaultdict(set)  # (M,C) -> set of (S,C) TPs
    sam_code_link_to_output_fps = defaultdict(set)  # (M,C) -> set of (S,C) FPs

    for (s, c) in transarc_output:
        models_for_s = sent_to_models.get(s, set())
        models_for_c = code_to_models.get(c, set())
        bridges = models_for_s & models_for_c

        is_tp = (s, c) in gs_sad_code

        for m in bridges:
            key = (m, c)
            if is_tp:
                sam_code_link_to_output_tps[key].add((s, c))
            else:
                sam_code_link_to_output_fps[key].add((s, c))

    # ═══ FORWARD TRACE: SAM-CODE FN → SAD-CODE FN ═══════════════════
    #
    # For each SAM-CODE FN (M, C_missed), how many gold SAD-CODE links
    # (S, C_missed) are FNs where M is the bridging element?
    # i.e., SAD-SAM correctly found (M, S) but SAM-CODE missed (M, C_missed)

    sam_code_fn_to_sad_code_fns = defaultdict(set)  # (M,C) -> set of (S,C) FNs

    # Gold SAD-SAM maps for checking which sentences link to which models
    gs_sad_sam_s2m = defaultdict(set)
    gs_sad_sam_m2s = defaultdict(set)
    for m, s in gs_sad_sam:
        gs_sad_sam_s2m[s].add(m)
        gs_sad_sam_m2s[m].add(s)

    for (s, c) in transarc_fns:
        # Find gold bridging models for this FN
        gold_models_for_s = gs_sad_sam_s2m.get(s, set())
        gold_sam_code_models_for_c = set(m for m, cp in gs_sam_code if cp == c)
        gold_bridges = gold_models_for_s & gold_sam_code_models_for_c

        for m in gold_bridges:
            # Did TransArc find this model for this sentence?
            transarc_models_for_s = sent_to_models.get(s, set())
            if m in transarc_models_for_s:
                # SAD-SAM found the right model, but SAM-CODE missed the code
                if (m, c) not in int_sam_code:
                    sam_code_fn_to_sad_code_fns[(m, c)].add((s, c))

    # ═══ BUILD PER-SAM-CODE-LINK TABLE ═══════════════════════════════

    sam_code_rows = []
    for (m, c) in int_sam_code:
        is_tp = (m, c) in gs_sam_code
        produced_tps = sam_code_link_to_output_tps.get((m, c), set())
        produced_fps = sam_code_link_to_output_fps.get((m, c), set())
        sam_code_rows.append({
            "model": m,
            "code": c,
            "model_name": names.get(m, m),
            "status": "TP" if is_tp else "FP",
            "sad_code_tps": len(produced_tps),
            "sad_code_fps": len(produced_fps),
            "sad_code_total": len(produced_tps) + len(produced_fps),
        })

    # SAM-CODE FN rows
    sam_code_fn_rows = []
    for (m, c) in sam_code_fns:
        caused_fns = sam_code_fn_to_sad_code_fns.get((m, c), set())
        sam_code_fn_rows.append({
            "model": m,
            "code": c,
            "model_name": names.get(m, m),
            "sad_code_fns_caused": len(caused_fns),
            "fn_links": caused_fns,
        })

    # ═══ HOLISTIC PER-MODEL-ELEMENT VIEW ═════════════════════════════
    #
    # For each model element M, aggregate:
    # - SAD-SAM side: how many SAD-SAM TPs/FPs, and what SAD-CODE output they produce
    # - SAM-CODE side: how many SAM-CODE TPs/FPs/FNs, and what SAD-CODE output they produce
    # - Combined: total SAD-CODE TPs/FPs/FNs attributable to this M

    model_holistic = {}

    # All model elements that appear in any intermediate
    all_models = set()
    for m, _ in int_sad_sam:
        all_models.add(m)
    for m, _ in int_sam_code:
        all_models.add(m)
    # Also include models from gold that might be missed entirely
    for m, _ in gs_sad_sam:
        all_models.add(m)
    for m, _ in gs_sam_code:
        all_models.add(m)

    for m in all_models:
        # SAD-SAM links for this model
        m_sad_sam_links = [(mm, s) for (mm, s) in int_sad_sam if mm == m]
        m_sad_sam_tp_count = sum(1 for link in m_sad_sam_links if link in gs_sad_sam)
        m_sad_sam_fp_count = sum(1 for link in m_sad_sam_links if link not in gs_sad_sam)

        # SAM-CODE links for this model
        m_sam_code_links = [(mm, c) for (mm, c) in int_sam_code if mm == m]
        m_sam_code_tp_count = sum(1 for link in m_sam_code_links if link in gs_sam_code)
        m_sam_code_fp_count = sum(1 for link in m_sam_code_links if link not in gs_sam_code)
        m_sam_code_fn_links = [(mm, c) for (mm, c) in sam_code_fns if mm == m]
        m_sam_code_fn_count = len(m_sam_code_fn_links)

        # Gold footprint
        m_gs_sad_sam_sents = set(s for mm, s in gs_sad_sam if mm == m)
        m_gs_sam_code_files = set(c for mm, c in gs_sam_code if mm == m)

        # TransArc output via this model
        m_sents = model_to_sents.get(m, set())
        m_codes = model_to_codes.get(m, set())

        # Actual SAD-CODE output through this model
        m_sad_code_tps = 0
        m_sad_code_fps = 0
        for s in m_sents:
            for c in m_codes:
                if (s, c) in transarc_output:
                    if (s, c) in gs_sad_code:
                        m_sad_code_tps += 1
                    else:
                        m_sad_code_fps += 1

        # SAD-CODE FNs attributable to this model (via SAM-CODE FNs)
        m_sad_code_fns_from_sam_code = sum(
            len(sam_code_fn_to_sad_code_fns.get((m, c), set()))
            for _, c in m_sam_code_fn_links
        )

        # Classify SAD-CODE FPs through this model by root cause
        m_fp_from_sad_sam = 0  # SAD-SAM wrong, SAM-CODE right
        m_fp_from_sam_code = 0  # SAD-SAM right, SAM-CODE wrong
        m_fp_from_both = 0  # both wrong
        m_fp_from_combo = 0  # both right individually, combo wrong

        for s in m_sents:
            for c in m_codes:
                if (s, c) in transarc_fps:
                    sad_sam_ok = (m, s) in gs_sad_sam
                    sam_code_ok = (m, c) in gs_sam_code
                    if not sad_sam_ok and not sam_code_ok:
                        m_fp_from_both += 1
                    elif not sad_sam_ok:
                        m_fp_from_sad_sam += 1
                    elif not sam_code_ok:
                        m_fp_from_sam_code += 1
                    else:
                        m_fp_from_combo += 1

        model_holistic[m] = {
            "name": names.get(m, m),
            "sad_sam_tps": m_sad_sam_tp_count,
            "sad_sam_fps": m_sad_sam_fp_count,
            "sam_code_tps": m_sam_code_tp_count,
            "sam_code_fps": m_sam_code_fp_count,
            "sam_code_fns": m_sam_code_fn_count,
            "gs_sents": len(m_gs_sad_sam_sents),
            "gs_files": len(m_gs_sam_code_files),
            "int_sents": len(m_sents),
            "int_files": len(m_codes),
            "sad_code_tps": m_sad_code_tps,
            "sad_code_fps": m_sad_code_fps,
            "sad_code_fns_from_sam_code": m_sad_code_fns_from_sam_code,
            "fp_from_sad_sam": m_fp_from_sad_sam,
            "fp_from_sam_code": m_fp_from_sam_code,
            "fp_from_both": m_fp_from_both,
            "fp_from_combo": m_fp_from_combo,
        }

    return {
        "sam_code_rows": sam_code_rows,
        "sam_code_fn_rows": sam_code_fn_rows,
        "model_holistic": model_holistic,
        "stats": {
            "transarc_tps": len(transarc_tps),
            "transarc_fps": len(transarc_fps),
            "transarc_fns": len(transarc_fns),
            "transarc_total": len(transarc_output),
            "int_sam_code_tps": len(sam_code_tps),
            "int_sam_code_fps": len(sam_code_fps),
            "int_sam_code_fns": len(sam_code_fns),
            "int_sad_sam_tps": len(sad_sam_tps),
            "int_sad_sam_fps": len(sad_sam_fps),
        },
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# SAM-CODE Error Cascade & Holistic Pipeline Analysis")
    out()

    all_results = {}
    for proj in PROJECTS:
        all_results[proj] = analyze_project(proj)

    # ═══ 1. SAM-CODE FP CASCADE ══════════════════════════════════════

    out("## 1. SAM-CODE FP Cascade: Each Wrong File × Number of Sentences")
    out()
    out("Every SAM-CODE FP (M, C_wrong) is composed with all intermediate SAD-SAM")
    out("sentences for M, producing |sentences(M)| SAD-CODE links — most of which are FPs.")
    out()

    out("### SAM-CODE FPs Ranked by Induced SAD-CODE FPs")
    out()
    out("| Rank | Project | Model Element | Wrong Code File | SAD-SAM Sents | →SAD-CODE TPs | →SAD-CODE FPs | Total |")
    out("|------|---------|--------------|----------------|---------------|-------------|-------------|-------|")

    all_fp_rows = []
    for proj in PROJECTS:
        for r in all_results[proj]["sam_code_rows"]:
            if r["status"] == "FP":
                all_fp_rows.append((proj, r))

    all_fp_rows.sort(key=lambda t: t[1]["sad_code_fps"], reverse=True)

    for i, (proj, r) in enumerate(all_fp_rows[:30], 1):
        parts = r["code"].split("/")
        code_short = "/".join(parts[-2:]) if len(parts) >= 2 else r["code"]
        h = all_results[proj]["model_holistic"][r["model"]]
        out(f"| {i} | {proj} | {r['model_name']} | `{code_short}` | "
            f"{h['int_sents']} | {r['sad_code_tps']} | **{r['sad_code_fps']}** | {r['sad_code_total']} |")

    out()

    # Summary
    out("### SAM-CODE FP Cascade Summary")
    out()
    out("| Project | SAM-CODE FPs | Total Induced SAD-CODE FPs | Avg Amplification (sents/FP) | SAD-CODE FPs from SAM-CODE | % of All TransArc FPs |")
    out("|---------|-------------|---------------------------|------------------------------|--------------------------|---------------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        fp_rows = [x for x in r["sam_code_rows"] if x["status"] == "FP"]
        sc_fps = len(fp_rows)
        total_induced_fps = sum(x["sad_code_fps"] for x in fp_rows)
        total_induced_tps = sum(x["sad_code_tps"] for x in fp_rows)
        avg_amp = total_induced_fps / sc_fps if sc_fps else 0
        total_transarc_fps = r["stats"]["transarc_fps"]
        pct = total_induced_fps / total_transarc_fps * 100 if total_transarc_fps else 0
        out(f"| {proj} | {sc_fps} | {total_induced_fps} | {avg_amp:.1f} | {total_induced_fps} | {pct:.1f}% |")

    out()

    # ═══ 2. SAM-CODE FN CASCADE ══════════════════════════════════════

    out("## 2. SAM-CODE FN Cascade: Each Missed File × Number of Sentences")
    out()
    out("Every SAM-CODE FN (M, C_missed) means sentences correctly linked to M via")
    out("SAD-SAM cannot reach C_missed. The missed code file causes SAD-CODE FNs")
    out("for all sentences that should link to it.")
    out()

    out("### SAM-CODE FNs Ranked by Caused SAD-CODE FNs")
    out()
    out("| Rank | Project | Model Element | Missed Code File | Caused SAD-CODE FNs |")
    out("|------|---------|--------------|-----------------|-------------------|")

    all_fn_cascade = []
    for proj in PROJECTS:
        for r in all_results[proj]["sam_code_fn_rows"]:
            if r["sad_code_fns_caused"] > 0:
                all_fn_cascade.append((proj, r))

    all_fn_cascade.sort(key=lambda t: t[1]["sad_code_fns_caused"], reverse=True)

    for i, (proj, r) in enumerate(all_fn_cascade[:30], 1):
        parts = r["code"].split("/")
        code_short = "/".join(parts[-2:]) if len(parts) >= 2 else r["code"]
        out(f"| {i} | {proj} | {r['model_name']} | `{code_short}` | **{r['sad_code_fns_caused']}** |")

    if not all_fn_cascade:
        out("| — | — | — | — | No SAM-CODE FNs caused SAD-CODE FNs |")

    out()

    # Summary
    out("### SAM-CODE FN Cascade Summary")
    out()
    out("| Project | SAM-CODE FNs | With SAD-CODE Impact | Total Caused SAD-CODE FNs | % of All TransArc FNs |")
    out("|---------|-------------|---------------------|--------------------------|--------------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        fn_rows = r["sam_code_fn_rows"]
        total_fns = len(fn_rows)
        with_impact = sum(1 for x in fn_rows if x["sad_code_fns_caused"] > 0)
        total_caused = sum(x["sad_code_fns_caused"] for x in fn_rows)
        total_transarc_fns = r["stats"]["transarc_fns"]
        pct = total_caused / total_transarc_fns * 100 if total_transarc_fns else 0
        out(f"| {proj} | {total_fns} | {with_impact} | {total_caused} | {pct:.1f}% |")

    out()

    # ═══ 3. SAM-CODE TP CASCADE ══════════════════════════════════════

    out("## 3. SAM-CODE TP Value: Each Correct File × Number of Sentences")
    out()
    out("Each SAM-CODE TP (M, C_correct) is composed with all SAD-SAM sentences for M.")
    out("With correct SAD-SAM links this produces TPs; with wrong SAD-SAM links, FPs.")
    out()

    out("### SAM-CODE TPs Ranked by SAD-CODE TPs Produced (Top 20)")
    out()
    out("| Rank | Project | Model Element | Correct Code File | →SAD-CODE TPs | →SAD-CODE FPs | Precision |")
    out("|------|---------|--------------|------------------|-------------|-------------|-----------|")

    all_tp_rows = []
    for proj in PROJECTS:
        for r in all_results[proj]["sam_code_rows"]:
            if r["status"] == "TP":
                all_tp_rows.append((proj, r))

    all_tp_rows.sort(key=lambda t: t[1]["sad_code_tps"], reverse=True)

    for i, (proj, r) in enumerate(all_tp_rows[:20], 1):
        parts = r["code"].split("/")
        code_short = "/".join(parts[-2:]) if len(parts) >= 2 else r["code"]
        prec = r["sad_code_tps"] / r["sad_code_total"] if r["sad_code_total"] else 0
        out(f"| {i} | {proj} | {r['model_name']} | `{code_short}` | "
            f"**{r['sad_code_tps']}** | {r['sad_code_fps']} | {prec:.3f} |")

    out()

    # Show SAM-CODE TPs that produce mostly FPs (low precision through cascade)
    out("### SAM-CODE TPs with Lowest Cascade Precision (correct file, but most SAD-CODE output is wrong)")
    out()
    out("| Project | Model Element | Correct Code File | →SAD-CODE TPs | →SAD-CODE FPs | Precision | Root Cause |")
    out("|---------|--------------|------------------|-------------|-------------|-----------|-----------|")

    low_prec = []
    for proj in PROJECTS:
        for r in all_results[proj]["sam_code_rows"]:
            if r["status"] == "TP" and r["sad_code_total"] > 0:
                prec = r["sad_code_tps"] / r["sad_code_total"]
                if prec < 0.8 and r["sad_code_fps"] > 0:
                    low_prec.append((proj, r, prec))

    low_prec.sort(key=lambda t: t[2])

    for proj, r, prec in low_prec[:15]:
        parts = r["code"].split("/")
        code_short = "/".join(parts[-2:]) if len(parts) >= 2 else r["code"]
        h = all_results[proj]["model_holistic"][r["model"]]
        # Root cause: FPs come from SAD-SAM FPs linking wrong sentences to this model
        cause = f"{h['sad_sam_fps']} SAD-SAM FPs for {r['model_name']}"
        out(f"| {proj} | {r['model_name']} | `{code_short}` | "
            f"{r['sad_code_tps']} | {r['sad_code_fps']} | {prec:.3f} | {cause} |")

    if not low_prec:
        out("| — | — | All SAM-CODE TPs have cascade precision >= 0.8 | — | — | — | — |")

    out()

    # ═══ 4. HOLISTIC PER-MODEL-ELEMENT VIEW ══════════════════════════

    out("## 4. Holistic Per-Model-Element Pipeline View")
    out()
    out("For each model element M, the combined effect of SAD-SAM and SAM-CODE")
    out("errors on the final SAD-CODE output. Shows how errors from both components")
    out("compound through the transitive composition.")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        h = r["model_holistic"]
        names = load_model_element_names(proj)

        out(f"### {proj.upper()}")
        out()
        out(f"TransArc output: {r['stats']['transarc_tps']} TPs + {r['stats']['transarc_fps']} FPs = "
            f"{r['stats']['transarc_total']} | FNs: {r['stats']['transarc_fns']}")
        out()
        out("| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |")
        out("|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|")

        sorted_models = sorted(
            [(m, d) for m, d in h.items() if d["int_sents"] > 0 or d["int_files"] > 0],
            key=lambda kv: kv[1]["sad_code_tps"] + kv[1]["sad_code_fps"],
            reverse=True
        )

        total_tps = 0
        total_fps_ss = 0
        total_fps_sc = 0
        total_fps_both = 0
        total_fps_combo = 0
        total_fns_sc = 0

        for m, d in sorted_models:
            gs_cross = d["gs_sents"] * d["gs_files"]
            total_tps += d["sad_code_tps"]
            total_fps_ss += d["fp_from_sad_sam"]
            total_fps_sc += d["fp_from_sam_code"]
            total_fps_both += d["fp_from_both"]
            total_fps_combo += d["fp_from_combo"]
            total_fns_sc += d["sad_code_fns_from_sam_code"]
            out(f"| {d['name']} | {gs_cross} | {d['int_sents']} | {d['int_files']} | "
                f"**{d['sad_code_tps']}** | {d['fp_from_sad_sam']} | {d['fp_from_sam_code']} | "
                f"{d['fp_from_both']} | {d['fp_from_combo']} | {d['sad_code_fns_from_sam_code']} |")

        total_fps = total_fps_ss + total_fps_sc + total_fps_both + total_fps_combo
        out(f"| **TOTAL** | | | | **{total_tps}** | **{total_fps_ss}** | **{total_fps_sc}** | "
            f"**{total_fps_both}** | **{total_fps_combo}** | **{total_fns_sc}** |")
        out()

    # ═══ 5. CROSS-CUTTING: ERROR INTERACTION MATRIX ══════════════════

    out("## 5. Error Interaction: How SAD-SAM and SAM-CODE Errors Compound")
    out()
    out("The transitive product means errors multiply: |FPs| = |SAD-SAM FP sents| × |SAM-CODE files| + |SAD-SAM sents| × |SAM-CODE FP files|.")
    out("This section quantifies how the two error sources interact per model element.")
    out()

    out("### Per-Model Error Budget")
    out()
    out("For each model element with errors, decompose the total SAD-CODE output:")
    out()
    out("| Project | Model Element | SS TPs × SC TPs → | SS TPs × SC FPs → | SS FPs × SC TPs → | SS FPs × SC FPs → | Total Output |")
    out("|---------|--------------|-------------------|-------------------|-------------------|-------------------|-------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        h = r["model_holistic"]
        names = load_model_element_names(proj)

        for m, d in sorted(h.items(), key=lambda kv: kv[1]["sad_code_fps"], reverse=True):
            if d["sad_code_fps"] == 0 and d["sad_code_fns_from_sam_code"] == 0:
                continue
            if d["int_sents"] == 0 and d["int_files"] == 0:
                continue

            # Decompose: for each output link (S,C) through M, classify by
            # whether (M,S) is SAD-SAM TP/FP and (M,C) is SAM-CODE TP/FP
            tp_tp = 0  # both correct → could be TP or combo FP
            tp_fp = 0  # SAD-SAM correct, SAM-CODE wrong → SAM-CODE-caused FP
            fp_tp = 0  # SAD-SAM wrong, SAM-CODE correct → SAD-SAM-caused FP
            fp_fp = 0  # both wrong → both-caused FP

            sents = r["model_holistic"][m]["int_sents"]
            files = r["model_holistic"][m]["int_files"]

            # We already have the breakdown in holistic:
            tp_tp = d["sad_code_tps"] + d["fp_from_combo"]  # correct components, output may be TP or combo FP
            tp_fp = d["fp_from_sam_code"]
            fp_tp = d["fp_from_sad_sam"]
            fp_fp = d["fp_from_both"]

            total = tp_tp + tp_fp + fp_tp + fp_fp
            if total == 0:
                continue

            out(f"| {proj} | {d['name']} | {tp_tp} ({tp_tp/total*100:.0f}%) | "
                f"{tp_fp} ({tp_fp/total*100:.0f}%) | {fp_tp} ({fp_tp/total*100:.0f}%) | "
                f"{fp_fp} ({fp_fp/total*100:.0f}%) | {total} |")

    out()

    # ═══ 6. CASCADE AMPLIFICATION COMPARISON ═════════════════════════

    out("## 6. Amplification Comparison: SAD-SAM vs SAM-CODE")
    out()
    out("How does the amplification factor compare between the two error sources?")
    out("- SAD-SAM FP amplification = number of SAM-CODE files for that model element")
    out("- SAM-CODE FP amplification = number of SAD-SAM sentences for that model element")
    out()

    out("| Project | Component | SAD-SAM FPs | ×Files | =SAD-CODE FPs | SAM-CODE FPs | ×Sents | =SAD-CODE FPs |")
    out("|---------|----------|------------|--------|-------------|-------------|--------|-------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        h = r["model_holistic"]

        for m, d in sorted(h.items(), key=lambda kv: kv[1]["sad_code_fps"], reverse=True):
            if d["sad_code_fps"] == 0:
                continue
            sad_sam_fp_induced = d["fp_from_sad_sam"] + d["fp_from_both"]
            sam_code_fp_induced = d["fp_from_sam_code"] + d["fp_from_both"]
            out(f"| {proj} | {d['name']} | {d['sad_sam_fps']} | ×{d['int_files']} | "
                f"{sad_sam_fp_induced} | {d['sam_code_fps']} | ×{d['int_sents']} | "
                f"{sam_code_fp_induced} |")

    out()

    # ═══ 7. AGGREGATE CROSS-PROJECT SUMMARY ══════════════════════════

    out("## 7. Cross-Project Error Source Summary")
    out()

    total_tps = 0
    total_fps = 0
    total_fps_ss = 0
    total_fps_sc = 0
    total_fps_both = 0
    total_fps_combo = 0
    total_fns_sc = 0
    total_fns_all = 0

    out("| Project | SAD-CODE TPs | FPs (SAD-SAM) | FPs (SAM-CODE) | FPs (Both) | FPs (Combo) | FNs from SC | Total FNs |")
    out("|---------|------------|-------------|-------------|-----------|-----------|-----------|----------|")

    for proj in PROJECTS:
        r = all_results[proj]
        h = r["model_holistic"]
        p_tps = sum(d["sad_code_tps"] for d in h.values())
        p_fps_ss = sum(d["fp_from_sad_sam"] for d in h.values())
        p_fps_sc = sum(d["fp_from_sam_code"] for d in h.values())
        p_fps_both = sum(d["fp_from_both"] for d in h.values())
        p_fps_combo = sum(d["fp_from_combo"] for d in h.values())
        p_fns_sc = sum(d["sad_code_fns_from_sam_code"] for d in h.values())
        p_fns_all = r["stats"]["transarc_fns"]

        total_tps += p_tps
        total_fps += p_fps_ss + p_fps_sc + p_fps_both + p_fps_combo
        total_fps_ss += p_fps_ss
        total_fps_sc += p_fps_sc
        total_fps_both += p_fps_both
        total_fps_combo += p_fps_combo
        total_fns_sc += p_fns_sc
        total_fns_all += p_fns_all

        out(f"| {proj} | {p_tps} | {p_fps_ss} | {p_fps_sc} | {p_fps_both} | {p_fps_combo} | {p_fns_sc} | {p_fns_all} |")

    out(f"| **TOTAL** | **{total_tps}** | **{total_fps_ss}** | **{total_fps_sc}** | "
        f"**{total_fps_both}** | **{total_fps_combo}** | **{total_fns_sc}** | **{total_fns_all}** |")
    out()

    # Percentage breakdown
    if total_fps > 0:
        out(f"**FP attribution**: SAD-SAM caused {total_fps_ss}/{total_fps} ({total_fps_ss/total_fps*100:.1f}%), "
            f"SAM-CODE caused {total_fps_sc}/{total_fps} ({total_fps_sc/total_fps*100:.1f}%), "
            f"Both {total_fps_both}/{total_fps} ({total_fps_both/total_fps*100:.1f}%), "
            f"Combination {total_fps_combo}/{total_fps} ({total_fps_combo/total_fps*100:.1f}%)")
        out()

    if total_fns_all > 0:
        out(f"**FN attribution**: SAM-CODE FNs caused {total_fns_sc}/{total_fns_all} ({total_fns_sc/total_fns_all*100:.1f}%) of TransArc FNs. "
            f"The remaining {total_fns_all - total_fns_sc} ({(total_fns_all - total_fns_sc)/total_fns_all*100:.1f}%) are from SAD-SAM misses or theoretical limits.")
        out()

    out("### Key Insight: The Asymmetry of Error Sources")
    out()
    out("SAD-SAM errors dominate because of a fundamental asymmetry in the transitive product:")
    out()
    out("- A SAD-SAM FP for model M gets multiplied by ALL SAM-CODE files for M")
    out("- A SAM-CODE FP for model M gets multiplied by ALL SAD-SAM sentences for M")
    out()
    out("Since SAM-CODE footprints (files per model element) are typically much larger")
    out("than SAD-SAM footprints (sentences per model element), SAD-SAM FPs amplify more.")
    out()

    out("| Project | Avg Files/Model | Avg Sents/Model | Ratio (Files/Sents) |")
    out("|---------|----------------|----------------|-------------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        h = r["model_holistic"]
        active = [(m, d) for m, d in h.items() if d["int_sents"] > 0 and d["int_files"] > 0]
        if not active:
            continue
        avg_files = sum(d["int_files"] for _, d in active) / len(active)
        avg_sents = sum(d["int_sents"] for _, d in active) / len(active)
        ratio = avg_files / avg_sents if avg_sents else 0
        out(f"| {proj} | {avg_files:.1f} | {avg_sents:.1f} | {ratio:.1f}x |")

    out()
    out("This ratio explains why SAD-SAM errors cause ~94% of TransArc FPs:")
    out("each SAD-SAM FP is amplified by the (larger) file count, while each")
    out("SAM-CODE FP is amplified by the (smaller) sentence count.")
    out()

    # ─── Write report ────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
