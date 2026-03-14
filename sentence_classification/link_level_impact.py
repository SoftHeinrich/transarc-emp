#!/usr/bin/env python3
"""
Link-level impact analysis: what happens to SWATTR's P/R/F1 when we filter
pkg_code sentences from its output?

Operates at the (modelElementID, sentence) link level, not sentence level.
"""

import csv
import os
import re
import json

BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
RESULTS = "/mnt/hostshare/ardoco-home/transarc-emp/results"
DATA_DIR = "/mnt/hostshare/ardoco-home/transarc-emp/sentence_classification"

PROJECTS = {
    "mediastore": {"gold": "goldstandards/goldstandard_sad_2016-sam_2016.csv"},
    "teastore": {"gold": "goldstandards/goldstandard_sad_2020-sam_2020.csv"},
    "teammates": {"gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "jabref": {"gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "bigbluebutton": {"gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
}


def load_links(path):
    links = set()
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def load_annotations():
    with open(os.path.join(DATA_DIR, "annotated_sentences.json")) as f:
        rows = json.load(f)
    # Build label lookup: (project, sentence_num) → label
    labels = {}
    for r in rows:
        labels[(r['project'], r['sentence_num'])] = r['label']
    return labels


def rule_classifier_v2(text):
    text_s = text.strip()
    text_l = text_s.lower()
    if 'package overview' in text_l:
        return 'pkg_code'
    if re.match(r'^[a-z][a-z0-9]*\.[a-z]', text_s):
        return 'pkg_code'
    if re.search(r'\bx\.[a-z]\S*\s+contains\b', text_l):
        return 'pkg_code'
    if re.match(r'^sub-?packages?\s+contains', text_s, re.IGNORECASE):
        return 'pkg_code'
    if re.search(r'is not a (real |Java )?package', text_s):
        return 'pkg_code'
    if re.search(r'\b[a-z][a-z0-9]*\.[a-z][a-z0-9]*\b', text_s) and len(text_s.split()) <= 10 and 'contains' in text_l:
        return 'pkg_code'
    if re.search(r'classes in the \S+\.\S+ package', text_l):
        return 'pkg_code'
    if re.search(r'(conceptual|virtual|logical) package', text_l):
        return 'pkg_code'
    return 'not_pkg'


def load_sentences(project):
    """Load sentences for a project."""
    dirs = {
        "mediastore": "text_2016/mediastore.txt",
        "teastore": "text_2020/teastore.txt",
        "teammates": "text_2021/teammates.txt",
        "jabref": "text_2021/jabref.txt",
        "bigbluebutton": "text_2021/bigbluebutton.txt",
    }
    path = os.path.join(BENCHMARK, project, dirs[project])
    sents = {}
    with open(path) as f:
        for i, line in enumerate(f, 1):
            sents[i] = line.strip()
    return sents


def main():
    labels = load_annotations()

    print("=" * 90)
    print("LINK-LEVEL IMPACT: pkg_code Filter on SWATTR SAD-SAM")
    print("=" * 90)

    total_tp_before = total_fp_before = total_fn_before = 0
    total_tp_after = total_fp_after = total_fn_after = 0

    for project, config in PROJECTS.items():
        gold = load_links(os.path.join(BENCHMARK, project, config['gold']))
        result = load_links(os.path.join(RESULTS, project, "sad-sam", f"sadSamTlr_{project}.csv"))
        sents = load_sentences(project)

        # Identify pkg_code sentences
        pkg_sents = set()
        for snum, text in sents.items():
            if rule_classifier_v2(text) == 'pkg_code':
                pkg_sents.add(snum)

        # Before filter
        tp_before = gold & result
        fp_before = result - gold
        fn_before = gold - result

        # After filter: remove links to pkg_code sentences from result
        filtered_result = {(eid, snum) for (eid, snum) in result if snum not in pkg_sents}

        tp_after = gold & filtered_result
        fp_after = filtered_result - gold
        fn_after = gold - filtered_result

        p_b = len(tp_before) / len(result) if result else 0
        r_b = len(tp_before) / len(gold) if gold else 0
        f1_b = 2*p_b*r_b/(p_b+r_b) if (p_b+r_b) > 0 else 0

        p_a = len(tp_after) / len(filtered_result) if filtered_result else 0
        r_a = len(tp_after) / len(gold) if gold else 0
        f1_a = 2*p_a*r_a/(p_a+r_a) if (p_a+r_a) > 0 else 0

        links_removed = len(result) - len(filtered_result)
        tp_lost = len(tp_before) - len(tp_after)
        fp_removed = len(fp_before) - len(fp_after)

        print(f"\n  {project}:")
        print(f"    pkg_code sentences: {len(pkg_sents)}")
        print(f"    Links removed: {links_removed} ({tp_lost} TP lost, {fp_removed} FP removed)")
        print(f"    Before: TP={len(tp_before)}, FP={len(fp_before)}, FN={len(fn_before)}, "
              f"P={p_b:.3f}, R={r_b:.3f}, F1={f1_b:.3f}")
        print(f"    After:  TP={len(tp_after)}, FP={len(fp_after)}, FN={len(fn_after)}, "
              f"P={p_a:.3f}, R={r_a:.3f}, F1={f1_a:.3f}")
        print(f"    ΔP={p_a-p_b:+.3f}, ΔR={r_a-r_b:+.3f}, ΔF1={f1_a-f1_b:+.3f}")

        # Show lost TPs
        if tp_lost > 0:
            lost_links = tp_before - tp_after
            print(f"    Lost TP links ({tp_lost}):")
            for eid, snum in sorted(lost_links, key=lambda x: x[1]):
                print(f"      ({eid[:20]}..., S{snum}): \"{sents[snum][:80]}\"")
                # Check: is this element still linked from other sentences?
                remaining = [s for (e, s) in tp_after if e == eid]
                print(f"        Element still has {len(remaining)} TP links: S{sorted(remaining)[:5]}")

        total_tp_before += len(tp_before)
        total_fp_before += len(fp_before)
        total_fn_before += len(fn_before)
        total_tp_after += len(tp_after)
        total_fp_after += len(fp_after)
        total_fn_after += len(fn_after)

    # Aggregate
    print(f"\n{'='*90}")
    print("AGGREGATE (micro-average)")
    p_b = total_tp_before / (total_tp_before + total_fp_before)
    r_b = total_tp_before / (total_tp_before + total_fn_before)
    f1_b = 2*p_b*r_b/(p_b+r_b)

    p_a = total_tp_after / (total_tp_after + total_fp_after)
    r_a = total_tp_after / (total_tp_after + total_fn_after)
    f1_a = 2*p_a*r_a/(p_a+r_a)

    print(f"\n  Before: TP={total_tp_before}, FP={total_fp_before}, FN={total_fn_before}, "
          f"P={p_b:.3f}, R={r_b:.3f}, F1={f1_b:.3f}")
    print(f"  After:  TP={total_tp_after}, FP={total_fp_after}, FN={total_fn_after}, "
          f"P={p_a:.3f}, R={r_a:.3f}, F1={f1_a:.3f}")
    print(f"  ΔP={p_a-p_b:+.3f}, ΔR={r_a-r_b:+.3f}, ΔF1={f1_a-f1_b:+.3f}")

    # Also compute macro-average
    print(f"\n  Macro-average F1 change:")
    macro_f1_before = 0
    macro_f1_after = 0
    for project, config in PROJECTS.items():
        gold = load_links(os.path.join(BENCHMARK, project, config['gold']))
        result = load_links(os.path.join(RESULTS, project, "sad-sam", f"sadSamTlr_{project}.csv"))
        sents = load_sentences(project)

        pkg_sents = {snum for snum, text in sents.items() if rule_classifier_v2(text) == 'pkg_code'}
        filtered = {(eid, snum) for (eid, snum) in result if snum not in pkg_sents}

        tp_b = len(gold & result)
        fp_b = len(result - gold)
        tp_a = len(gold & filtered)
        fp_a = len(filtered - gold)
        fn = len(gold - result)
        fn_a = len(gold - filtered)

        p_b = tp_b/(tp_b+fp_b) if (tp_b+fp_b) > 0 else 0
        r_b = tp_b/(tp_b+fn) if (tp_b+fn) > 0 else 0
        f1_b = 2*p_b*r_b/(p_b+r_b) if (p_b+r_b) > 0 else 0

        p_a = tp_a/(tp_a+fp_a) if (tp_a+fp_a) > 0 else 0
        r_a = tp_a/(tp_a+fn_a) if (tp_a+fn_a) > 0 else 0
        f1_a = 2*p_a*r_a/(p_a+r_a) if (p_a+r_a) > 0 else 0

        macro_f1_before += f1_b
        macro_f1_after += f1_a
        print(f"    {project}: F1 {f1_b:.3f} → {f1_a:.3f} (Δ={f1_a-f1_b:+.3f})")

    macro_f1_before /= 5
    macro_f1_after /= 5
    print(f"\n  Macro-avg F1: {macro_f1_before:.3f} → {macro_f1_after:.3f} (Δ={macro_f1_after-macro_f1_before:+.3f})")


if __name__ == '__main__':
    main()
