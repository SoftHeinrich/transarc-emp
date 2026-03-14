#!/usr/bin/env python3
"""
LLM Baseline Failure Mode Analysis

For each project, loads the adaptive LLM classification and gold SAD-SAM,
computes SAD-SAM FPs/FNs, categorizes each error, shows sentence text,
and analyzes document structure.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, load_text, load_gs_sad_sam, load_model_element_names,
    load_gs_sad_sam_maps, TEXT_FILES,
)
from three_system_comparison import (
    load_llm_adaptive_classifications, llm_classifications_to_sad_sam,
    ADAPTIVE_STRATEGIES,
)
from llm_agentic_eval import build_name_to_id_map


def main():
    print("=" * 100)
    print("LLM BASELINE FAILURE MODE ANALYSIS")
    print("=" * 100)
    print()

    # Global accumulators
    global_fn_categories = defaultdict(int)
    global_fp_categories = defaultdict(int)
    global_fn_total = 0
    global_fp_total = 0

    for proj in PROJECTS:
        print()
        print("#" * 100)
        print(f"#  PROJECT: {proj.upper()}")
        print(f"#  Adaptive strategy: {ADAPTIVE_STRATEGIES[proj]}")
        print("#" * 100)
        print()

        # ─── Load data ────────────────────────────────────────────────────
        text = load_text(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_s2m, gs_m2s = load_gs_sad_sam_maps(proj)
        model_names = load_model_element_names(proj)
        name_to_ids = build_name_to_id_map(proj)

        # Build reverse: id -> name
        id_to_name = {}
        for ae_id, ae_name in model_names.items():
            id_to_name[ae_id] = ae_name

        # Load LLM adaptive classifications
        llm_cls = load_llm_adaptive_classifications(proj)
        llm_sad_sam = llm_classifications_to_sad_sam(llm_cls, name_to_ids)

        # ─── Compute TP/FP/FN ─────────────────────────────────────────────
        tp_set = gs_sad_sam & llm_sad_sam
        fp_set = llm_sad_sam - gs_sad_sam
        fn_set = gs_sad_sam - llm_sad_sam

        print(f"Gold SAD-SAM links: {len(gs_sad_sam)}")
        print(f"LLM SAD-SAM links:  {len(llm_sad_sam)}")
        print(f"  TP: {len(tp_set)}")
        print(f"  FP: {len(fp_set)}")
        print(f"  FN: {len(fn_set)}")
        p = len(tp_set) / len(llm_sad_sam) if llm_sad_sam else 0
        r = len(tp_set) / len(gs_sad_sam) if gs_sad_sam else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        print(f"  P: {p:.3f}  R: {r:.3f}  F1: {f1:.3f}")
        print()

        # ─── Build helper maps ────────────────────────────────────────────
        # LLM: sentence -> set of component names assigned
        llm_sent_to_comps = defaultdict(set)
        for sent_num, comp_names in llm_cls.items():
            for cn in comp_names:
                llm_sent_to_comps[sent_num].add(cn)

        # LLM: sentence -> set of model element IDs assigned
        llm_sent_to_ids = defaultdict(set)
        for ae_id, sent in llm_sad_sam:
            llm_sent_to_ids[sent].add(ae_id)

        # Gold: sentence -> set of model element IDs
        gold_sent_to_ids = defaultdict(set)
        for ae_id, sent in gs_sad_sam:
            gold_sent_to_ids[sent].add(ae_id)

        # All component names (from SAM-CODE gold)
        all_component_names = set(model_names.values())

        # ─── Categorize FNs ───────────────────────────────────────────────
        # Group FNs by sentence
        fn_by_sent = defaultdict(set)  # sent -> set of missed model element IDs
        for ae_id, sent in fn_set:
            fn_by_sent[sent].add(ae_id)

        fn_implicit = []      # (a) no component name appears in text
        fn_explicit_miss = [] # (b) component name IS in text but LLM missed it
        fn_multi_miss = []    # (c) multiple gold comps, LLM got some but not all

        print("=" * 80)
        print("FALSE NEGATIVES (Missed gold links)")
        print("=" * 80)
        print()

        for sent in sorted(fn_by_sent.keys(), key=lambda s: int(s)):
            missed_ids = fn_by_sent[sent]
            sent_text = text.get(sent, "<unknown>")

            gold_ids_for_sent = gold_sent_to_ids[sent]
            llm_ids_for_sent = llm_sent_to_ids.get(sent, set())

            # Names
            missed_names = [id_to_name.get(m, m) for m in missed_ids]
            gold_names = [id_to_name.get(m, m) for m in gold_ids_for_sent]
            llm_names = list(llm_sent_to_comps.get(sent, set()))

            # Check if this is a multi-component miss (LLM got some but not all)
            found_some = bool(llm_ids_for_sent & gold_ids_for_sent)

            # Check if any missed component name appears explicitly in the text
            sent_lower = sent_text.lower()
            explicit_in_text = []
            implicit_refs = []
            for mid in missed_ids:
                mname = id_to_name.get(mid, "")
                # Extract the short name (after "Component: " or "Interface: ")
                short_name = mname.split(": ", 1)[1] if ": " in mname else mname
                # Check various forms
                name_variants = [short_name.lower()]
                # Also try splitting on camelCase/hyphens
                parts = re.findall(r'[A-Z][a-z]+|[a-z]+', short_name)
                if len(parts) > 1:
                    name_variants.append(" ".join(p.lower() for p in parts))
                # Check if any variant appears in text
                found_in_text = False
                for variant in name_variants:
                    if variant in sent_lower and len(variant) >= 3:
                        found_in_text = True
                        break
                if found_in_text:
                    explicit_in_text.append((mid, mname, short_name))
                else:
                    implicit_refs.append((mid, mname, short_name))

            # Categorize
            if found_some:
                category = "MULTI_COMP_MISS"
                fn_multi_miss.append((sent, missed_ids, gold_ids_for_sent, llm_ids_for_sent))
            elif explicit_in_text:
                category = "EXPLICIT_MISS"
                fn_explicit_miss.append((sent, missed_ids, explicit_in_text))
            else:
                category = "IMPLICIT_REF"
                fn_implicit.append((sent, missed_ids, implicit_refs))

            # Also check if some missed are explicit and some implicit
            # (for mixed cases, classify based on primary)
            if not found_some and explicit_in_text and implicit_refs:
                category = "EXPLICIT_MISS"  # At least some names are in text

            print(f"  Sentence {sent}: \"{sent_text}\"")
            print(f"    Category: {category}")
            print(f"    Gold components: {gold_names}")
            print(f"    LLM assigned:   {llm_names if llm_names else '<none>'}")
            print(f"    Missed:         {missed_names}")
            if explicit_in_text:
                print(f"    Names in text:  {[x[2] for x in explicit_in_text]}")
            if implicit_refs:
                print(f"    Implicit refs:  {[x[2] for x in implicit_refs]}")
            print()

        print(f"\n  FN Summary:")
        print(f"    (a) IMPLICIT_REF (no component name in text):      {len(fn_implicit)}")
        print(f"    (b) EXPLICIT_MISS (name in text, LLM missed):      {len(fn_explicit_miss)}")
        print(f"    (c) MULTI_COMP_MISS (got some, missed others):     {len(fn_multi_miss)}")
        print(f"    Total FN sentences: {len(fn_by_sent)}")
        print(f"    Total FN links:     {len(fn_set)}")
        print()

        # ─── Categorize FPs ───────────────────────────────────────────────
        # Group FPs by sentence
        fp_by_sent = defaultdict(set)  # sent -> set of wrong model element IDs
        for ae_id, sent in fp_set:
            fp_by_sent[sent].add(ae_id)

        fp_no_gold = []        # (a) sentence has NO gold components at all
        fp_wrong_comp = []     # (b) sentence has gold but LLM assigned different ones
        fp_over_assign = []    # (c) gold comps are a subset of LLM, extra ones are FPs

        print("=" * 80)
        print("FALSE POSITIVES (Wrong LLM links)")
        print("=" * 80)
        print()

        for sent in sorted(fp_by_sent.keys(), key=lambda s: int(s)):
            wrong_ids = fp_by_sent[sent]
            sent_text = text.get(sent, "<unknown>")

            gold_ids_for_sent = gold_sent_to_ids.get(sent, set())
            llm_ids_for_sent = llm_sent_to_ids.get(sent, set())

            wrong_names = [id_to_name.get(m, m) for m in wrong_ids]
            gold_names = [id_to_name.get(m, m) for m in gold_ids_for_sent]
            llm_names = list(llm_sent_to_comps.get(sent, set()))

            if not gold_ids_for_sent:
                category = "NO_GOLD_LINKS"
                fp_no_gold.append((sent, wrong_ids))
            elif gold_ids_for_sent <= llm_ids_for_sent:
                # Gold is a subset of LLM -> over-assignment
                category = "OVER_ASSIGNMENT"
                fp_over_assign.append((sent, wrong_ids, gold_ids_for_sent))
            else:
                category = "WRONG_COMPONENT"
                fp_wrong_comp.append((sent, wrong_ids, gold_ids_for_sent))

            print(f"  Sentence {sent}: \"{sent_text}\"")
            print(f"    Category: {category}")
            print(f"    Gold components: {gold_names if gold_names else '<none>'}")
            print(f"    LLM assigned:   {llm_names}")
            print(f"    Wrong (FP):     {wrong_names}")
            print()

        print(f"\n  FP Summary:")
        print(f"    (a) NO_GOLD_LINKS (sentence has no gold):          {len(fp_no_gold)}")
        print(f"    (b) WRONG_COMPONENT (has gold, LLM got different): {len(fp_wrong_comp)}")
        print(f"    (c) OVER_ASSIGNMENT (gold subset, extras are FP):  {len(fp_over_assign)}")
        print(f"    Total FP sentences: {len(fp_by_sent)}")
        print(f"    Total FP links:     {len(fp_set)}")
        print()

        # ─── Update global accumulators ───────────────────────────────────
        global_fn_categories["implicit_ref"] += len(fn_implicit)
        global_fn_categories["explicit_miss"] += len(fn_explicit_miss)
        global_fn_categories["multi_comp_miss"] += len(fn_multi_miss)
        global_fp_categories["no_gold_links"] += len(fp_no_gold)
        global_fp_categories["wrong_component"] += len(fp_wrong_comp)
        global_fp_categories["over_assignment"] += len(fp_over_assign)
        global_fn_total += len(fn_set)
        global_fp_total += len(fp_set)

        # ─── Document structure analysis ──────────────────────────────────
        print("=" * 80)
        print("DOCUMENT STRUCTURE ANALYSIS")
        print("=" * 80)
        print()

        text_path = TEXT_FILES[proj]
        with open(text_path) as f:
            lines = f.readlines()

        total_lines = len(lines)
        print(f"  Total sentences/lines: {total_lines}")

        # Detect potential headers: short lines, lines with all caps,
        # numbered sections, lines ending with colon
        headers = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            is_header = False
            reason = ""

            # Short line (< 60 chars) that doesn't end with period
            if len(stripped) < 60 and not stripped.endswith('.') and not stripped.endswith(','):
                is_header = True
                reason = "short_no_period"

            # All uppercase
            if stripped.upper() == stripped and len(stripped) > 3 and stripped.isalpha():
                is_header = True
                reason = "ALL_CAPS"

            # Numbered section: starts with digit + dot
            if re.match(r'^\d+\.', stripped):
                is_header = True
                reason = "numbered_section"

            # Contains only a few words (title-like)
            words = stripped.split()
            if 1 <= len(words) <= 5 and not stripped.endswith('.'):
                is_header = True
                reason = "title_like"

            if is_header:
                # Check if this line has gold links
                has_gold = str(i) in gold_sent_to_ids
                has_llm = str(i) in llm_sent_to_ids
                gold_comps = [id_to_name.get(m, m) for m in gold_sent_to_ids.get(str(i), set())]
                llm_comps = list(llm_sent_to_comps.get(str(i), set()))
                headers.append((i, stripped, reason, has_gold, has_llm, gold_comps, llm_comps))

        print(f"\n  Detected potential headers/section markers ({len(headers)}):")
        print()
        for line_num, line_text, reason, has_gold, has_llm, gold_comps, llm_comps in headers:
            gold_mark = f" GOLD:{gold_comps}" if has_gold else ""
            llm_mark = f" LLM:{llm_comps}" if has_llm else ""
            print(f"    Line {line_num:3d} [{reason:18s}]: \"{line_text[:80]}\"{gold_mark}{llm_mark}")

        # Summary: how many gold-linked lines are "headers"?
        header_line_nums = set(h[0] for h in headers)
        gold_sents_set = set(gold_sent_to_ids.keys())
        gold_in_headers = set(str(h) for h in header_line_nums) & gold_sents_set
        print(f"\n  Gold-linked sentences that are headers: {len(gold_in_headers)}/{len(gold_sents_set)}")

        # FN sentences that are headers
        fn_sents_set = set(fn_by_sent.keys())
        fn_in_headers = set(str(h) for h in header_line_nums) & fn_sents_set
        print(f"  FN sentences that are headers: {len(fn_in_headers)}/{len(fn_sents_set)}")

        # FP sentences that are headers
        fp_sents_set = set(fp_by_sent.keys())
        fp_in_headers = set(str(h) for h in header_line_nums) & fp_sents_set
        print(f"  FP sentences that are headers: {len(fp_in_headers)}/{len(fp_sents_set)}")
        print()

        # ─── Component coverage analysis ─────────────────────────────────
        print("=" * 80)
        print("COMPONENT COVERAGE ANALYSIS")
        print("=" * 80)
        print()

        # Which components does the gold standard link to?
        gold_comp_ids = set()
        for ae_id, sent in gs_sad_sam:
            gold_comp_ids.add(ae_id)

        # Which components does the LLM assign?
        llm_comp_ids = set()
        for ae_id, sent in llm_sad_sam:
            llm_comp_ids.add(ae_id)

        # Components in gold but not in LLM (missed entirely)
        gold_only = gold_comp_ids - llm_comp_ids
        llm_only = llm_comp_ids - gold_comp_ids
        both = gold_comp_ids & llm_comp_ids

        print(f"  Components in gold:  {len(gold_comp_ids)}")
        print(f"  Components in LLM:   {len(llm_comp_ids)}")
        print(f"  Components in both:  {len(both)}")
        print()

        if gold_only:
            print(f"  Components in GOLD but NOT in LLM ({len(gold_only)}):")
            for cid in sorted(gold_only, key=lambda x: id_to_name.get(x, x)):
                cname = id_to_name.get(cid, cid)
                n_gold = len([1 for mid, s in gs_sad_sam if mid == cid])
                print(f"    - {cname} ({n_gold} gold links)")

        if llm_only:
            print(f"  Components in LLM but NOT in gold ({len(llm_only)}):")
            for cid in sorted(llm_only, key=lambda x: id_to_name.get(x, x)):
                cname = id_to_name.get(cid, cid)
                n_llm = len([1 for mid, s in llm_sad_sam if mid == cid])
                print(f"    - {cname} ({n_llm} LLM links)")

        print()

        # Per-component P/R/F1
        print("  Per-component P/R/F1:")
        print(f"    {'Component':<35s}  {'Gold':>5s}  {'LLM':>5s}  {'TP':>4s}  {'FP':>4s}  {'FN':>4s}  {'P':>6s}  {'R':>6s}  {'F1':>6s}")
        print("    " + "-" * 95)

        all_comp_ids = gold_comp_ids | llm_comp_ids
        for cid in sorted(all_comp_ids, key=lambda x: id_to_name.get(x, x)):
            cname = id_to_name.get(cid, cid)
            gold_links = set(s for mid, s in gs_sad_sam if mid == cid)
            llm_links = set(s for mid, s in llm_sad_sam if mid == cid)
            tp = len(gold_links & llm_links)
            fp = len(llm_links - gold_links)
            fn = len(gold_links - llm_links)
            cp = tp / (tp + fp) if (tp + fp) > 0 else 0
            cr = tp / (tp + fn) if (tp + fn) > 0 else 0
            cf1 = 2 * cp * cr / (cp + cr) if (cp + cr) > 0 else 0
            print(f"    {cname:<35s}  {len(gold_links):>5d}  {len(llm_links):>5d}  {tp:>4d}  {fp:>4d}  {fn:>4d}  {cp:>6.3f}  {cr:>6.3f}  {cf1:>6.3f}")

        print()

        # ─── Interface vs Component analysis ─────────────────────────────
        interface_ids = set(cid for cid in all_comp_ids
                          if id_to_name.get(cid, "").startswith("Interface:"))
        component_ids = set(cid for cid in all_comp_ids
                           if id_to_name.get(cid, "").startswith("Component:"))

        if interface_ids:
            iface_gold = sum(1 for mid, s in gs_sad_sam if mid in interface_ids)
            iface_llm = sum(1 for mid, s in llm_sad_sam if mid in interface_ids)
            iface_tp = len(set((mid, s) for mid, s in tp_set if mid in interface_ids))
            iface_fp = len(set((mid, s) for mid, s in fp_set if mid in interface_ids))
            iface_fn = len(set((mid, s) for mid, s in fn_set if mid in interface_ids))
            print(f"  Interface links: Gold={iface_gold}, LLM={iface_llm}, TP={iface_tp}, FP={iface_fp}, FN={iface_fn}")
        if component_ids:
            comp_gold = sum(1 for mid, s in gs_sad_sam if mid in component_ids)
            comp_llm = sum(1 for mid, s in llm_sad_sam if mid in component_ids)
            comp_tp = len(set((mid, s) for mid, s in tp_set if mid in component_ids))
            comp_fp = len(set((mid, s) for mid, s in fp_set if mid in component_ids))
            comp_fn = len(set((mid, s) for mid, s in fn_set if mid in component_ids))
            print(f"  Component links: Gold={comp_gold}, LLM={comp_llm}, TP={comp_tp}, FP={comp_fp}, FN={comp_fn}")
        print()

    # ═══════════════════════════════════════════════════════════════════════════
    # Global Summary
    # ═══════════════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("GLOBAL SUMMARY ACROSS ALL PROJECTS")
    print("=" * 100)
    print()

    total_fn_sents = sum(global_fn_categories.values())
    total_fp_sents = sum(global_fp_categories.values())

    print(f"FN Categories (by sentence, {total_fn_sents} total unique FN sentences):")
    print(f"  (a) IMPLICIT_REF:    {global_fn_categories['implicit_ref']:>4d}  "
          f"({global_fn_categories['implicit_ref']/total_fn_sents*100:.1f}%)")
    print(f"  (b) EXPLICIT_MISS:   {global_fn_categories['explicit_miss']:>4d}  "
          f"({global_fn_categories['explicit_miss']/total_fn_sents*100:.1f}%)")
    print(f"  (c) MULTI_COMP_MISS: {global_fn_categories['multi_comp_miss']:>4d}  "
          f"({global_fn_categories['multi_comp_miss']/total_fn_sents*100:.1f}%)")
    print(f"  Total FN links:      {global_fn_total}")
    print()

    print(f"FP Categories (by sentence, {total_fp_sents} total unique FP sentences):")
    print(f"  (a) NO_GOLD_LINKS:   {global_fp_categories['no_gold_links']:>4d}  "
          f"({global_fp_categories['no_gold_links']/total_fp_sents*100:.1f}%)")
    print(f"  (b) WRONG_COMPONENT: {global_fp_categories['wrong_component']:>4d}  "
          f"({global_fp_categories['wrong_component']/total_fp_sents*100:.1f}%)")
    print(f"  (c) OVER_ASSIGNMENT: {global_fp_categories['over_assignment']:>4d}  "
          f"({global_fp_categories['over_assignment']/total_fp_sents*100:.1f}%)")
    print(f"  Total FP links:      {global_fp_total}")
    print()


if __name__ == "__main__":
    main()
