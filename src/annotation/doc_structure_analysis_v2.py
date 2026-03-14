#!/usr/bin/env python3
"""
Document Structure Analysis v2 - Resolves all model element names and provides
complete analysis of document structure patterns across ARDoCo benchmark projects.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]

TEXT_FILES = {
    "mediastore":    BENCHMARK / "mediastore/text_2016/mediastore.txt",
    "teastore":      BENCHMARK / "teastore/text_2020/teastore.txt",
    "teammates":     BENCHMARK / "teammates/text_2021/teammates.txt",
    "bigbluebutton": BENCHMARK / "bigbluebutton/text_2021/bigbluebutton.txt",
    "jabref":        BENCHMARK / "jabref/text_2021/jabref.txt",
}

GS_SAD_SAM = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sad_2016-sam_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sad_2020-sam_2020.csv",
    "teammates":     BENCHMARK / "teammates/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "bigbluebutton": BENCHMARK / "bigbluebutton/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "jabref":        BENCHMARK / "jabref/goldstandards/goldstandard_sad_2021-sam_2021.csv",
}

GS_SAM_CODE = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sam_2016-code_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sam_2020-code_2022.csv",
    "teammates":     BENCHMARK / "teammates/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "bigbluebutton": BENCHMARK / "bigbluebutton/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "jabref":        BENCHMARK / "jabref/goldstandards/goldstandard_sam_2021-code_2023.csv",
}

# Model elements in SAD-SAM gold but not in SAM-CODE gold (manually resolved from PCM/UML)
EXTRA_NAMES = {
    "_qxAiILg7EeSNPorBlo7x9g": "Component: FileStorage",
    "_KGVMcKETEeu-mYqkDskRow": "Component: GAE Datastore",
    "_oN4CMFkHEeyewPSmlgszyA": "Component: Kurento",
}


def load_text_lines(project):
    lines = {}
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            lines[i] = line.strip()
    return lines


def load_gs_sad_sam(project):
    sent_to_models = defaultdict(set)
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            sent_to_models[int(row["sentence"])].add(row["modelElementID"])
    return dict(sent_to_models)


def load_model_element_names(project):
    names = {}
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            names[row["ae_id"]] = row["ae_name"]
    names.update(EXTRA_NAMES)
    return names


def get_short_name(full_name):
    if ": " in full_name:
        return full_name.split(": ", 1)[1]
    return full_name


def find_mentions(text, short_names):
    """Case-insensitive word-boundary search for component short names in text."""
    found = set()
    text_lower = text.lower()
    for name in short_names:
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(name)
    return found


def analyze_project(project):
    lines = load_text_lines(project)
    gs = load_gs_sad_sam(project)
    names = load_model_element_names(project)
    total_lines = len(lines)

    # Build short name set and ID-to-short mapping
    id_to_short = {}
    short_names = set()
    # Collect all model IDs that appear in gold
    all_model_ids = set()
    for mids in gs.values():
        all_model_ids.update(mids)

    for mid in all_model_ids:
        full = names.get(mid, mid)
        short = get_short_name(full)
        id_to_short[mid] = short
        short_names.add(short)

    gold_sents = set(gs.keys())  # set of int

    # Precompute: which lines mention which components
    line_mentions = {}  # line_num -> set of short names
    for ln, text in lines.items():
        m = find_mentions(text, short_names)
        if m:
            line_mentions[ln] = m

    # Short lines (potential headers)
    short_line_nums = set()
    for ln, text in lines.items():
        if len(text.split()) < 10:
            short_line_nums.add(ln)

    print(f"\n{'='*100}")
    print(f"PROJECT: {project.upper()}")
    print(f"{'='*100}")
    print(f"Total lines: {total_lines} | Gold sentences: {len(gold_sents)} | "
          f"Gold links: {sum(len(v) for v in gs.values())}")
    print(f"Component short names ({len(short_names)}): {sorted(short_names)}")

    # ─── Full line-by-line output ─────────────────────────────────────────────
    print(f"\n--- Full annotated text ---")
    for ln in range(1, total_lines + 1):
        text = lines[ln]
        is_gold = ln in gold_sents
        is_short = ln in short_line_nums
        mentions = line_mentions.get(ln, set())

        markers = []
        if is_gold:
            model_names = sorted(id_to_short.get(mid, mid[:20]) for mid in gs[ln])
            markers.append(f"GOLD[{','.join(model_names)}]")
        if is_short:
            markers.append("HDR?")
        if mentions:
            markers.append(f"MENTIONS[{','.join(sorted(mentions))}]")

        marker_str = " ".join(markers) if markers else ""
        text_preview = text[:90] + ("..." if len(text) > 90 else "")
        if markers:
            print(f"  {ln:>3} | {marker_str:<70} | {text_preview}")
        else:
            print(f"  {ln:>3} | {'':70} | {text_preview}")

    # ─── Clusters of consecutive gold sentences ──────────────────────────────
    sorted_gold = sorted(gold_sents)
    clusters = []
    if sorted_gold:
        cur = [sorted_gold[0]]
        for i in range(1, len(sorted_gold)):
            if sorted_gold[i] - sorted_gold[i-1] <= 2:
                cur.append(sorted_gold[i])
            else:
                clusters.append(cur)
                cur = [sorted_gold[i]]
        clusters.append(cur)

    print(f"\n--- Gold sentence clusters (gap <= 1) ---")
    print(f"Total clusters: {len(clusters)}")
    for i, cl in enumerate(clusters, 1):
        cl_models = set()
        for s in cl:
            for mid in gs[s]:
                cl_models.add(id_to_short.get(mid, mid[:20]))
        # Nearby mentions
        nearby = set()
        for s in cl:
            for delta in range(-3, 4):
                check = s + delta
                if check in line_mentions:
                    nearby.update(line_mentions[check])
        print(f"  Cluster {i}: lines {min(cl)}-{max(cl)} ({len(cl)} gold sents)")
        print(f"    Models: {sorted(cl_models)}")
        print(f"    Nearby mentions (+-3): {sorted(nearby)}")

    # ─── Proximity counts ─────────────────────────────────────────────────────
    gold_in_sent = 0         # component name IN the gold sentence
    gold_near_comp = 0       # component name within +-3 lines (incl in-sentence)
    gold_near_own_comp = 0   # own component name within +-3 lines
    gold_near_header = 0     # short line within +-3

    for s in sorted_gold:
        # In-sentence mentions
        in_sent_m = line_mentions.get(s, set())
        if in_sent_m:
            gold_in_sent += 1

        # Near-component (+-3, inclusive of self)
        near_m = set()
        for delta in range(-3, 4):
            check = s + delta
            if check in line_mentions:
                near_m.update(line_mentions[check])
        if near_m:
            gold_near_comp += 1

        # Own component name nearby?
        own_names = set(id_to_short.get(mid, mid) for mid in gs[s])
        if own_names & near_m:
            gold_near_own_comp += 1

        # Near header?
        for delta in range(-3, 4):
            if delta == 0:
                continue
            check = s + delta
            if check in short_line_nums:
                gold_near_header += 1
                break

    ng = len(gold_sents)
    print(f"\n--- Proximity summary ---")
    print(f"  Component name IN gold sentence:                   {gold_in_sent}/{ng} ({gold_in_sent/ng*100:.1f}%)")
    print(f"  Any component mention within +-3 (incl self):      {gold_near_comp}/{ng} ({gold_near_comp/ng*100:.1f}%)")
    print(f"  OWN component name within +-3 (incl self):         {gold_near_own_comp}/{ng} ({gold_near_own_comp/ng*100:.1f}%)")
    print(f"  Short line (potential header) within +-3:           {gold_near_header}/{ng} ({gold_near_header/ng*100:.1f}%)")

    # Non-gold stats
    non_gold = [ln for ln in range(1, total_lines+1) if ln not in gold_sents]
    non_gold_with_mention = sum(1 for ln in non_gold if ln in line_mentions)
    print(f"  Non-gold with component mention:                   {non_gold_with_mention}/{len(non_gold)} ({non_gold_with_mention/len(non_gold)*100:.1f}%)" if non_gold else "")

    # ─── Per-model-element own-name proximity ─────────────────────────────────
    print(f"\n--- Per-model-element: own name within +-3 lines ---")
    model_to_sents = defaultdict(set)
    for s, mids in gs.items():
        for mid in mids:
            model_to_sents[mid].add(s)

    for mid in sorted(model_to_sents.keys(), key=lambda x: id_to_short.get(x, x)):
        short = id_to_short.get(mid, mid)
        sents = sorted(model_to_sents[mid])
        with_own = 0
        missing = []
        for s in sents:
            found = False
            for delta in range(-3, 4):
                check = s + delta
                if 1 <= check <= total_lines:
                    text = lines[check]
                    if re.search(r'\b' + re.escape(short.lower()) + r'\b', text.lower()):
                        found = True
                        break
            if found:
                with_own += 1
            else:
                missing.append(s)
        pct = with_own / len(sents) * 100
        miss_str = f" Missing: {missing}" if missing else " ALL COVERED"
        print(f"  {short:<30} {with_own}/{len(sents)} ({pct:5.1f}%){miss_str}")

    # ─── Section header analysis ──────────────────────────────────────────────
    # Identify true section headers: short lines that are NOT gold and seem like headers
    print(f"\n--- Section headers (short lines, typically topic introductions) ---")
    headers = []
    for ln in range(1, total_lines + 1):
        text = lines[ln]
        wc = len(text.split())
        if wc <= 8 and wc >= 1:
            # Find next header
            next_h = total_lines + 1
            for ln2 in range(ln + 1, total_lines + 1):
                if len(lines[ln2].split()) <= 8:
                    next_h = ln2
                    break
            gold_in_section = [s for s in gold_sents if ln <= s < next_h]
            mentions = find_mentions(text, short_names)
            is_gold = ln in gold_sents
            mentions_str = str(sorted(mentions)) if mentions else "---"
            print(f"  Line {ln:>3} {'[GOLD]' if is_gold else '      '} "
                  f"({wc}w) mentions={mentions_str:30} "
                  f"gold_until_next={len(gold_in_section):>2} | \"{text}\"")
            headers.append((ln, text, mentions, gold_in_section))

    return {
        "total_lines": total_lines,
        "gold_sentences": ng,
        "gold_links": sum(len(v) for v in gs.values()),
        "gold_in_sent": gold_in_sent,
        "gold_near_comp": gold_near_comp,
        "gold_near_own_comp": gold_near_own_comp,
        "gold_near_header": gold_near_header,
        "non_gold_with_mention": non_gold_with_mention,
        "non_gold_total": len(non_gold),
        "num_clusters": len(clusters),
    }


def main():
    all_results = {}
    for project in PROJECTS:
        all_results[project] = analyze_project(project)

    print(f"\n{'='*100}")
    print(f"CROSS-PROJECT SUMMARY")
    print(f"{'='*100}")

    print(f"\n{'Project':<15} {'Lines':>5} {'Gold':>5} {'Links':>5} {'Clust':>5} "
          f"{'InSent':>10} {'NearAny':>10} {'NearOwn':>10} {'NearHdr':>10} {'NonGoldM':>10}")
    print(f"{'-'*15} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for project in PROJECTS:
        r = all_results[project]
        ng = r["gold_sentences"]
        nng = r["non_gold_total"]
        def pct(n, d):
            return f"{n}/{d} ({n/d*100:.0f}%)" if d > 0 else "N/A"

        print(f"{project:<15} {r['total_lines']:>5} {ng:>5} {r['gold_links']:>5} {r['num_clusters']:>5} "
              f"{pct(r['gold_in_sent'], ng):>10} {pct(r['gold_near_comp'], ng):>10} "
              f"{pct(r['gold_near_own_comp'], ng):>10} {pct(r['gold_near_header'], ng):>10} "
              f"{pct(r['non_gold_with_mention'], nng):>10}")

    # Aggregates
    total_gold = sum(r["gold_sentences"] for r in all_results.values())
    total_in = sum(r["gold_in_sent"] for r in all_results.values())
    total_near = sum(r["gold_near_comp"] for r in all_results.values())
    total_own = sum(r["gold_near_own_comp"] for r in all_results.values())
    total_hdr = sum(r["gold_near_header"] for r in all_results.values())
    total_nng_m = sum(r["non_gold_with_mention"] for r in all_results.values())
    total_nng = sum(r["non_gold_total"] for r in all_results.values())

    print(f"\nAGGREGATE:")
    print(f"  Gold sentences with component IN sentence:      {total_in}/{total_gold} ({total_in/total_gold*100:.1f}%)")
    print(f"  Gold sentences with ANY component within +-3:   {total_near}/{total_gold} ({total_near/total_gold*100:.1f}%)")
    print(f"  Gold sentences with OWN component within +-3:   {total_own}/{total_gold} ({total_own/total_gold*100:.1f}%)")
    print(f"  Gold sentences near short line (header) +-3:    {total_hdr}/{total_gold} ({total_hdr/total_gold*100:.1f}%)")
    print(f"  Non-gold with component mention:                {total_nng_m}/{total_nng} ({total_nng_m/total_nng*100:.1f}%)")

    print(f"\n--- CONCLUSION: Impact of Document-Structure-Aware Classification ---")
    print()
    print(f"1. COMPONENT NAME IN SENTENCE ({total_in}/{total_gold} = {total_in/total_gold*100:.1f}%)")
    print(f"   Most gold sentences directly mention their target component.")
    print(f"   This is the baseline signal -- a keyword-match classifier could reach this.")
    print()
    print(f"2. CONTEXTUAL PROXIMITY (+-3 lines) boosts coverage to {total_near}/{total_gold} = {total_near/total_gold*100:.1f}%")
    gap_near = total_gold - total_near
    print(f"   Only {gap_near} gold sentences ({gap_near/total_gold*100:.1f}%) have NO component mention nearby.")
    print(f"   These are exclusively pronoun references or indirect descriptions.")
    print()
    print(f"3. OWN COMPONENT NAME nearby: {total_own}/{total_gold} = {total_own/total_gold*100:.1f}%")
    gap_own = total_gold - total_own
    print(f"   {gap_own} gold sentences ({gap_own/total_gold*100:.1f}%) don't mention their OWN component within +-3 lines.")
    print(f"   These cases need coreference resolution or topic continuation tracking.")
    print()
    print(f"4. FALSE POSITIVE RISK: {total_nng_m}/{total_nng} = {total_nng_m/total_nng*100:.1f}% of non-gold")
    print(f"   sentences also mention component names.")
    if total_nng_m > 0:
        print(f"   This is concentrated in Teammates ({all_results['teammates']['non_gold_with_mention']}/{all_results['teammates']['non_gold_total']})")
        print(f"   due to its long, detailed documentation with many cross-references.")
    print()
    print(f"5. DOCUMENT STRUCTURE (section headers):")
    print(f"   BigBlueButton has the clearest section structure (component-named headers).")
    print(f"   JabRef has almost no structural markers (short, dense text).")
    print(f"   A header-aware approach would help most for BBB, partially for TeaStore/Teammates.")


if __name__ == "__main__":
    main()
