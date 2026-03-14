#!/usr/bin/env python3
"""
Document Structure Analysis for ARDoCo Benchmark Projects

Analyzes each project's documentation text file for structural patterns:
- Short lines that might be section headers
- Lines containing component names
- Gold sentence clustering
- Proximity of gold sentences to headers and component name mentions
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

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


def load_text(project):
    """Returns list of (line_number, text) tuples, 1-indexed."""
    lines = []
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            lines.append((i, line.strip()))
    return lines


def load_gs_sad_sam(project):
    """Returns dict: sentence_num_str -> set of modelElementIDs."""
    sent_to_models = defaultdict(set)
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            sent_to_models[row["sentence"]].add(row["modelElementID"])
    return dict(sent_to_models)


def load_model_element_names(project):
    """Returns dict: model_element_id -> name."""
    names = {}
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            names[row["ae_id"]] = row["ae_name"]
    return names


def extract_short_names(names_dict):
    """Extract short names from model element names by splitting on ': '."""
    short_names = set()
    for full_name in set(names_dict.values()):
        if ": " in full_name:
            short = full_name.split(": ", 1)[1]
            short_names.add(short)
        else:
            short_names.add(full_name)
    return short_names


def is_short_line(text, max_words=10):
    """Check if a line has fewer than max_words words."""
    return len(text.split()) < max_words


def find_component_mentions(text, short_names):
    """Find which component short names appear in a line of text (case-insensitive)."""
    found = []
    text_lower = text.lower()
    for name in short_names:
        # Use word boundary matching for short names to avoid false positives
        # For multi-word names, also try without spaces
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(name)
    return found


def find_clusters(gold_sentences, total_lines):
    """Find clusters of consecutive gold sentences (gap <= 1 non-gold line)."""
    sorted_sents = sorted(gold_sentences)
    if not sorted_sents:
        return []

    clusters = []
    current_cluster = [sorted_sents[0]]

    for i in range(1, len(sorted_sents)):
        if sorted_sents[i] - sorted_sents[i-1] <= 2:  # gap of at most 1 non-gold line
            current_cluster.append(sorted_sents[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_sents[i]]
    clusters.append(current_cluster)

    return clusters


def analyze_project(project):
    """Full structural analysis for one project."""
    lines = load_text(project)
    gs = load_gs_sad_sam(project)
    names = load_model_element_names(project)
    short_names = extract_short_names(names)

    gold_sentences = set(int(s) for s in gs.keys())
    total_lines = len(lines)

    # Build reverse mapping: model_id -> short_name
    id_to_short = {}
    for mid, full_name in names.items():
        if ": " in full_name:
            id_to_short[mid] = full_name.split(": ", 1)[1]
        else:
            id_to_short[mid] = full_name

    print(f"\n{'='*80}")
    print(f"PROJECT: {project.upper()}")
    print(f"{'='*80}")
    print(f"Total lines: {total_lines}")
    print(f"Gold sentences: {len(gold_sentences)} (unique sentence numbers)")
    print(f"Gold links: {sum(len(v) for v in gs.values())} (sentence-model pairs)")
    print(f"Component short names ({len(short_names)}): {sorted(short_names)}")

    # ─── Identify structural features per line ────────────────────────────────

    short_line_nums = set()
    component_mention_lines = {}  # line_num -> [component names]

    print(f"\n--- Line-by-line analysis ---")
    print(f"{'Line':>4} {'Gold':>4} {'Short':>5} {'CompMentions':<40} Text")
    print(f"{'-'*4} {'-'*4} {'-'*5} {'-'*40} {'-'*50}")

    for line_num, text in lines:
        is_gold = line_num in gold_sentences
        is_short = is_short_line(text)
        mentions = find_component_mentions(text, short_names)

        if is_short:
            short_line_nums.add(line_num)
        if mentions:
            component_mention_lines[line_num] = mentions

        # Only print lines that are interesting: gold, short, or have component mentions
        if is_gold or is_short or mentions:
            gold_marker = "GOLD" if is_gold else ""
            short_marker = "SHORT" if is_short else ""
            mention_str = ", ".join(mentions) if mentions else ""

            # For gold lines, show which model elements they're linked to
            if is_gold:
                model_names = [id_to_short.get(mid, mid[:15]) for mid in gs[str(line_num)]]
                gold_marker = f"GOLD({', '.join(model_names)})"

            text_preview = text[:80] + ("..." if len(text) > 80 else "")
            print(f"{line_num:>4} {gold_marker:<30} {short_marker:<5} {mention_str:<40} {text_preview}")

    # ─── Gold sentence clusters ───────────────────────────────────────────────

    clusters = find_clusters(sorted(gold_sentences), total_lines)
    print(f"\n--- Gold sentence clusters (gap <= 1 non-gold line) ---")
    print(f"Number of clusters: {len(clusters)}")
    for i, cluster in enumerate(clusters, 1):
        # Find nearby component mentions for this cluster
        cluster_start = min(cluster) - 3
        cluster_end = max(cluster) + 3
        nearby_mentions = set()
        for ln in range(max(1, cluster_start), min(total_lines, cluster_end) + 1):
            if ln in component_mention_lines:
                for name in component_mention_lines[ln]:
                    nearby_mentions.add(name)

        # What model elements does this cluster cover?
        cluster_models = set()
        for s in cluster:
            if str(s) in gs:
                for mid in gs[str(s)]:
                    cluster_models.add(id_to_short.get(mid, mid[:15]))

        print(f"  Cluster {i}: sentences {cluster} (size={len(cluster)})")
        print(f"    Model elements: {sorted(cluster_models)}")
        print(f"    Nearby component mentions (+-3): {sorted(nearby_mentions)}")

    # ─── Proximity analysis: gold sentences near headers ──────────────────────

    print(f"\n--- Proximity analysis ---")

    # For each gold sentence, check if there's a short line (potential header) within +-3
    gold_near_header = 0
    gold_near_component_mention = 0
    gold_with_component_in_sentence = 0
    gold_near_component_contextual = 0  # component mentioned within +-3 lines

    for sent_num in sorted(gold_sentences):
        near_header = False
        near_mention = False
        in_sentence = False

        # Check the sentence itself for component mentions
        sent_text = ""
        for ln, text in lines:
            if ln == sent_num:
                sent_text = text
                break

        in_sentence_mentions = find_component_mentions(sent_text, short_names)
        if in_sentence_mentions:
            in_sentence = True
            gold_with_component_in_sentence += 1

        # Check +-3 lines
        for delta in range(-3, 4):
            check_line = sent_num + delta
            if check_line < 1 or check_line > total_lines:
                continue
            if delta == 0:
                continue

            if check_line in short_line_nums:
                near_header = True
            if check_line in component_mention_lines:
                near_mention = True

        if near_header:
            gold_near_header += 1
        if near_mention or in_sentence:
            gold_near_component_contextual += 1

    print(f"Gold sentences with component name IN the sentence: {gold_with_component_in_sentence}/{len(gold_sentences)} ({gold_with_component_in_sentence/len(gold_sentences)*100:.1f}%)")
    print(f"Gold sentences near a short line (potential header) within +-3: {gold_near_header}/{len(gold_sentences)} ({gold_near_header/len(gold_sentences)*100:.1f}%)")
    print(f"Gold sentences with component mention within +-3 lines (or in sentence): {gold_near_component_contextual}/{len(gold_sentences)} ({gold_near_component_contextual/len(gold_sentences)*100:.1f}%)")

    # ─── Non-gold sentences with component mentions ───────────────────────────

    non_gold_with_mentions = 0
    non_gold_total = total_lines - len(gold_sentences)
    for line_num, text in lines:
        if line_num not in gold_sentences:
            mentions = find_component_mentions(text, short_names)
            if mentions:
                non_gold_with_mentions += 1

    print(f"\nNon-gold sentences with component mentions: {non_gold_with_mentions}/{non_gold_total} ({non_gold_with_mentions/non_gold_total*100:.1f}%)")
    print(f"Gold sentences with component mentions: {gold_with_component_in_sentence}/{len(gold_sentences)} ({gold_with_component_in_sentence/len(gold_sentences)*100:.1f}%)")

    # ─── Which model elements' gold sentences DON'T have that component mentioned nearby? ──

    print(f"\n--- Per-model-element: sentences with/without contextual component mention ---")

    # For each model element, check each of its gold sentences
    model_to_sents = defaultdict(set)
    for sent_str, mids in gs.items():
        for mid in mids:
            model_to_sents[mid].add(int(sent_str))

    for mid in sorted(model_to_sents.keys(), key=lambda x: id_to_short.get(x, x)):
        short_name = id_to_short.get(mid, mid)
        sents = sorted(model_to_sents[mid])

        with_mention = 0
        without_mention = []
        for s in sents:
            # Check if short_name appears in +-3 lines
            found = False
            for delta in range(-3, 4):
                check_line = s + delta
                if check_line < 1 or check_line > total_lines:
                    continue
                for ln, text in lines:
                    if ln == check_line:
                        if re.search(r'\b' + re.escape(short_name.lower()) + r'\b', text.lower()):
                            found = True
                        break
            if found:
                with_mention += 1
            else:
                without_mention.append(s)

        pct = with_mention / len(sents) * 100 if sents else 0
        if without_mention:
            print(f"  {short_name:<30} {with_mention}/{len(sents)} ({pct:.0f}%) with own name nearby. Missing: sentences {without_mention}")
        else:
            print(f"  {short_name:<30} {with_mention}/{len(sents)} ({pct:.0f}%) with own name nearby. ALL covered.")

    # ─── Section structure detection ──────────────────────────────────────────

    print(f"\n--- Potential section headers (short lines < 10 words) ---")
    for line_num, text in lines:
        if is_short_line(text) and len(text.split()) <= 8:
            # Count gold sentences between this header and the next header
            next_header = total_lines + 1
            for ln2, text2 in lines:
                if ln2 > line_num and is_short_line(text2) and len(text2.split()) <= 8:
                    next_header = ln2
                    break

            gold_in_section = [s for s in gold_sentences if line_num <= s < next_header]
            print(f"  Line {line_num}: \"{text}\" -> {len(gold_in_section)} gold sentences until next header")

    return {
        "total_lines": total_lines,
        "gold_sentences": len(gold_sentences),
        "gold_links": sum(len(v) for v in gs.values()),
        "short_names": short_names,
        "num_clusters": len(clusters),
        "gold_with_component_in_sentence": gold_with_component_in_sentence,
        "gold_near_header": gold_near_header,
        "gold_near_component_contextual": gold_near_component_contextual,
        "non_gold_with_mentions": non_gold_with_mentions,
        "non_gold_total": non_gold_total,
    }


def main():
    all_results = {}
    for project in PROJECTS:
        all_results[project] = analyze_project(project)

    # ─── Cross-project summary ────────────────────────────────────────────────

    print(f"\n{'='*80}")
    print(f"CROSS-PROJECT SUMMARY")
    print(f"{'='*80}")

    print(f"\n{'Project':<15} {'Lines':>5} {'Gold':>5} {'Links':>5} {'Clusters':>8} {'InSent':>8} {'NearHdr':>8} {'NearComp':>9} {'NonGold':>8}")
    print(f"{'-'*15} {'-'*5} {'-'*5} {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*9} {'-'*8}")

    for project in PROJECTS:
        r = all_results[project]
        gs = r["gold_sentences"]
        print(f"{project:<15} {r['total_lines']:>5} {gs:>5} {r['gold_links']:>5} {r['num_clusters']:>8} "
              f"{r['gold_with_component_in_sentence']:>4}/{gs:<3} {r['gold_near_header']:>4}/{gs:<3} "
              f"{r['gold_near_component_contextual']:>5}/{gs:<3} {r['non_gold_with_mentions']:>4}/{r['non_gold_total']:<3}")

    print(f"\nColumn meanings:")
    print(f"  InSent   = gold sentences with a component name IN the sentence text")
    print(f"  NearHdr  = gold sentences with a short line (potential header) within +-3 lines")
    print(f"  NearComp = gold sentences with ANY component mention within +-3 lines (including in-sentence)")
    print(f"  NonGold  = non-gold sentences that mention a component name")

    # ─── Impact assessment ────────────────────────────────────────────────────

    print(f"\n--- Impact Assessment for Document-Structure-Aware Classification ---")
    print()

    total_gold = sum(r["gold_sentences"] for r in all_results.values())
    total_near_comp = sum(r["gold_near_component_contextual"] for r in all_results.values())
    total_in_sent = sum(r["gold_with_component_in_sentence"] for r in all_results.values())
    total_non_gold_mentions = sum(r["non_gold_with_mentions"] for r in all_results.values())
    total_non_gold = sum(r["non_gold_total"] for r in all_results.values())

    print(f"Across all projects:")
    print(f"  Gold sentences with component in sentence: {total_in_sent}/{total_gold} ({total_in_sent/total_gold*100:.1f}%)")
    print(f"  Gold sentences with component within +-3:  {total_near_comp}/{total_gold} ({total_near_comp/total_gold*100:.1f}%)")
    print(f"  Non-gold sentences mentioning components:  {total_non_gold_mentions}/{total_non_gold} ({total_non_gold_mentions/total_non_gold*100:.1f}%)")

    print()
    print(f"Key finding: A structure-aware classifier that uses component name proximity")
    print(f"within +-3 lines could potentially provide signal for {total_near_comp}/{total_gold} ({total_near_comp/total_gold*100:.1f}%) of gold sentences.")

    gap = total_gold - total_near_comp
    print(f"However, {gap}/{total_gold} ({gap/total_gold*100:.1f}%) gold sentences have NO nearby component mention,")
    print(f"meaning structure alone is insufficient for these cases.")

    print(f"\nFalse-positive risk: {total_non_gold_mentions}/{total_non_gold} ({total_non_gold_mentions/total_non_gold*100:.1f}%)")
    print(f"of non-gold sentences also mention component names, indicating that")
    print(f"component name presence alone is not sufficient for classification.")


if __name__ == "__main__":
    main()
