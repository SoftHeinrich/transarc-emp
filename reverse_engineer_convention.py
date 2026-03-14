#!/usr/bin/env python3
"""
Reverse-engineer the annotation convention from the gold standard data.

For each component, show:
  - Gold TP sentences (in gold, SWATTR found them)
  - SWATTR FP sentences (NOT in gold, but SWATTR linked them)
  - Gold FN sentences (in gold, but SWATTR missed them)
  - Sentences that mention the component name but are NOT in gold (unlinked mentions)

Goal: discover what rule distinguishes "linked mention" from "unlinked mention".
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]

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

TEXT_FILES = {
    "mediastore":    BENCHMARK / "mediastore/text_2016/mediastore.txt",
    "teastore":      BENCHMARK / "teastore/text_2020/teastore.txt",
    "teammates":     BENCHMARK / "teammates/text_2021/teammates.txt",
    "bigbluebutton": BENCHMARK / "bigbluebutton/text_2021/bigbluebutton.txt",
    "jabref":        BENCHMARK / "jabref/text_2021/jabref.txt",
}


def load_text(project):
    sentences = {}
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            sentences[str(i)] = line.strip()
    return sentences


def load_gs_sad_sam(project):
    links = set()
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_result_sad_sam(project):
    path = RESULTS / project / "sad-sam" / f"sadSamTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_model_element_info(project):
    info = {}
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            ae_id = row["ae_id"]
            ae_name = row["ae_name"]
            if ae_id not in info:
                if ae_name.startswith("Component: "):
                    info[ae_id] = {"name": ae_name[len("Component: "):], "type": "Component"}
                elif ae_name.startswith("Interface: "):
                    info[ae_id] = {"name": ae_name[len("Interface: "):], "type": "Interface"}
                else:
                    info[ae_id] = {"name": ae_name, "type": "Unknown"}
    return info


def find_mentions(text, name):
    """Check if component name appears in text (case-insensitive, word boundary)."""
    # Try exact match
    if re.search(r'\b' + re.escape(name.lower()) + r'\b', text.lower()):
        return "exact"
    # Try each word of multi-word name
    words = re.findall(r'[a-zA-Z]+', name)
    if len(words) > 1:
        found = sum(1 for w in words if re.search(r'\b' + re.escape(w.lower()) + r'\b', text.lower()))
        if found == len(words):
            return "all_words"
        elif found > 0:
            return f"partial({found}/{len(words)})"
    return None


def main():
    md = []
    def out(s=""):
        print(s)
        md.append(s)

    out("# Reverse-Engineering the SAD-SAM Annotation Convention")
    out()
    out("For each component, comparing GOLD-linked sentences vs unlinked-but-mentioning sentences.")
    out("Goal: discover what distinguishes a gold trace link from a mere mention.")
    out()

    # ── Per-project, per-component analysis ───────────────────────────────────

    all_gold_texts = []   # (project, component, sent_num, text, category)
    all_nogold_texts = [] # sentences that mention component but NOT in gold

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)
        total_sents = len(text)

        # Build gold maps
        gold_by_elem = defaultdict(set)
        for mid, snum in gold:
            gold_by_elem[mid].add(snum)

        result_by_elem = defaultdict(set)
        for mid, snum in result:
            result_by_elem[mid].add(snum)

        out(f"## {proj.upper()}")
        out()
        out(f"Documentation: {total_sents} sentences")
        out()

        # Get unique elements that appear in gold OR result
        all_elems = set()
        for mid, _ in gold:
            all_elems.add(mid)
        for mid, _ in result:
            all_elems.add(mid)

        for mid in sorted(all_elems):
            ei = elem_info.get(mid, {"name": "UNKNOWN", "type": "?"})
            name = ei["name"]

            gold_sents = gold_by_elem.get(mid, set())
            result_sents = result_by_elem.get(mid, set())

            tp_sents = gold_sents & result_sents
            fp_sents = result_sents - gold_sents
            fn_sents = gold_sents - result_sents

            # Find ALL sentences that mention this component (regardless of gold)
            mention_sents = {}
            for snum, stxt in text.items():
                m = find_mentions(stxt, name)
                if m:
                    mention_sents[snum] = m

            # Unlinked mentions: mention the name but NOT in gold
            unlinked = {s: mention_sents[s] for s in mention_sents if s not in gold_sents}

            # Only show components that have FPs or interesting unlinked mentions
            if not fp_sents and not unlinked:
                continue

            out(f"### {ei['type']}: {name} (`{mid[:12]}...`)")
            out()

            # Gold TPs
            if tp_sents:
                out(f"**Gold TPs** ({len(tp_sents)} sentences — in gold, SWATTR found):")
                out()
                for s in sorted(tp_sents, key=int):
                    out(f"- S{s}: `{text[s]}`")
                out()

            # Gold FNs
            if fn_sents:
                out(f"**Gold FNs** ({len(fn_sents)} sentences — in gold, SWATTR missed):")
                out()
                for s in sorted(fn_sents, key=int):
                    mention = find_mentions(text[s], name)
                    tag = f" [mention: {mention}]" if mention else " [NO mention]"
                    out(f"- S{s}: `{text[s]}`{tag}")
                out()

            # SWATTR FPs
            if fp_sents:
                out(f"**SWATTR FPs** ({len(fp_sents)} sentences — NOT in gold, SWATTR linked):")
                out()
                for s in sorted(fp_sents, key=int):
                    mention = find_mentions(text[s], name)
                    tag = f" [mention: {mention}]" if mention else " [NO mention]"
                    out(f"- S{s}: `{text[s]}`{tag}")
                out()

            # Unlinked mentions (NOT FPs — SWATTR also didn't link them)
            unlinked_not_fp = {s: m for s, m in unlinked.items() if s not in fp_sents}
            if unlinked_not_fp:
                out(f"**Unlinked mentions** ({len(unlinked_not_fp)} sentences — "
                    f"mention '{name}', NOT in gold, SWATTR also skipped):")
                out()
                for s in sorted(unlinked_not_fp, key=int):
                    out(f"- S{s} [{unlinked_not_fp[s]}]: `{text[s]}`")
                out()

            out("---")
            out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Pattern Analysis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Pattern Analysis: What Distinguishes Gold from Non-Gold?")
    out()

    # Collect stats across all projects
    gold_patterns = defaultdict(int)
    nongold_patterns = defaultdict(int)

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        gold_by_elem = defaultdict(set)
        for mid, snum in gold:
            gold_by_elem[mid].add(snum)

        for mid in set(m for m, _ in gold):
            ei = elem_info.get(mid, {"name": "UNKNOWN"})
            name = ei["name"]

            gold_sents = gold_by_elem[mid]

            for snum, stxt in text.items():
                mention = find_mentions(stxt, name)
                if not mention:
                    continue

                stxt_lower = stxt.lower()
                is_gold = snum in gold_sents
                target = gold_patterns if is_gold else nongold_patterns

                # Classify the sentence
                has_dotted_pkg = bool(re.search(r'\b\w+\.\w+\b', stxt))
                has_contains = bool(re.search(r'\bcontains?\b', stxt_lower))
                has_package = bool(re.search(r'\bpackage\b', stxt_lower))
                has_pkg_overview = bool(re.search(r'package overview', stxt_lower))
                is_role_desc = bool(re.search(
                    r'\b(responsible|manages?|handles?|provides?|processes?|'
                    r'retriev|delivers?|stores?|communicat|authenticat|serves?)\b',
                    stxt_lower))
                is_structural = bool(re.search(
                    r'\b(consists? of|composed of|contains? (?:\d+ |the following))\b',
                    stxt_lower))
                has_subpackage_desc = bool(re.search(
                    r'\b\w+\.\w+\s+(contains?|provides?|has|is)\b', stxt_lower))
                is_class_listing = bool(re.search(
                    r'\bcontains?\s+(classes|helpers?|utilities?|abstractions?|'
                    r'custom|data\s*transfer|test)\b', stxt_lower))
                word_count = len(stxt.split())
                is_short = word_count <= 8

                target["total"] += 1
                if has_dotted_pkg: target["has_dotted_pkg"] += 1
                if has_contains: target["has_contains"] += 1
                if has_package: target["has_package"] += 1
                if has_pkg_overview: target["has_pkg_overview"] += 1
                if is_role_desc: target["is_role_desc"] += 1
                if is_structural: target["is_structural"] += 1
                if has_subpackage_desc: target["has_subpackage_desc"] += 1
                if is_class_listing: target["is_class_listing"] += 1
                if is_short: target["is_short_≤8w"] += 1

    out("### Pattern frequency in Gold vs Non-Gold mentions")
    out()
    out("Sentences that **mention** the component name, split by whether they're in the gold standard.")
    out()
    out("| Pattern | Gold (n={}) | Non-Gold (n={}) | Gold Rate | Non-Gold Rate | Ratio |".format(
        gold_patterns["total"], nongold_patterns["total"]))
    out("|---------|-----------|--------------|-----------|---------------|-------|")

    for pat in ["has_dotted_pkg", "has_contains", "has_package", "has_pkg_overview",
                "is_role_desc", "is_structural", "has_subpackage_desc", "is_class_listing",
                "is_short_≤8w"]:
        gc = gold_patterns.get(pat, 0)
        nc = nongold_patterns.get(pat, 0)
        gr = gc / gold_patterns["total"] if gold_patterns["total"] > 0 else 0
        nr = nc / nongold_patterns["total"] if nongold_patterns["total"] > 0 else 0
        ratio = nr / gr if gr > 0 else float('inf')
        marker = " **" if ratio > 2 else ""
        out(f"| {pat} | {gc} ({gr:.0%}) | {nc} ({nr:.0%}) | {gr:.2f} | {nr:.2f} | {ratio:.2f}{marker} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Teammates Deep Dive
    # ═══════════════════════════════════════════════════════════════════════════

    out("## TEAMMATES Deep Dive: Section Structure")
    out()
    out("Teammates has 198 sentences. What sections do gold vs non-gold mentions fall in?")
    out()

    text = load_text("teammates")
    gold = load_gs_sad_sam("teammates")
    elem_info = load_model_element_info("teammates")

    gold_sents_all = set(s for _, s in gold)

    # Try to identify section boundaries by looking for patterns
    out("### Document structure (sentences with potential section markers):")
    out()
    for snum in sorted(text.keys(), key=int):
        stxt = text[snum]
        # Section markers: very short, title-like, or "Package overview"
        if (len(stxt.split()) <= 5 or
            stxt.startswith("Package overview") or
            re.match(r'^[A-Z][\w\s]+$', stxt.strip()) or
            "component" in stxt.lower()[:30]):
            in_gold = "GOLD" if snum in gold_sents_all else "    "
            out(f"  S{snum:>3s} [{in_gold}]: {stxt[:100]}")
    out()

    # Categorize sentence ranges
    out("### Gold link density by sentence range:")
    out()
    ranges = [(1, 30), (31, 60), (61, 90), (91, 120), (121, 150), (151, 180), (181, 198)]
    out("| Range | Total | Gold-linked | Density | Notes |")
    out("|-------|-------|-------------|---------|-------|")
    for lo, hi in ranges:
        total = hi - lo + 1
        gold_count = sum(1 for s in range(lo, hi+1) if str(s) in gold_sents_all)
        density = gold_count / total
        # Check what's in this range
        sample = text.get(str(lo), "")[:60]
        out(f"| S{lo}-S{hi} | {total} | {gold_count} | {density:.0%} | {sample}... |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Convention Hypothesis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Hypothesized Annotation Convention")
    out()

    # Test hypothesis: "Gold links are for sentences that describe WHAT a component does
    # (its architectural role), not HOW it's structured internally (package contents)"

    # For each SWATTR FP, categorize
    out("### Hypothesis: Gold = describes component's architectural ROLE")
    out("### Non-gold = describes component's internal STRUCTURE")
    out()

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        fps = result - gold
        if not fps:
            continue

        out(f"**{proj}** — {len(fps)} FPs:")
        out()
        for mid, snum in sorted(fps, key=lambda x: int(x[1])):
            ei = elem_info.get(mid, {"name": "?"})
            stxt = text.get(snum, "")

            # Classify
            stxt_lower = stxt.lower()
            if re.search(r'package overview|package\b.*\bcontains', stxt_lower):
                cat = "PKG_OVERVIEW"
            elif re.search(r'\b\w+\.\w+\s+(contains?|provides?|has|is)\b', stxt_lower):
                cat = "SUBPKG_DESC"
            elif re.search(r'\bcontains?\s+(classes|helpers?|util|abstract|custom|data)', stxt_lower):
                cat = "CLASS_LISTING"
            elif re.search(r'\bnot a (?:real |java )?package\b', stxt_lower):
                cat = "META_COMMENT"
            elif re.search(r'\brefer to\b', stxt_lower):
                cat = "CROSS_REF"
            elif re.search(r'\b(responsible|manages?|handles?|provides?\s+\w+\s+to|processes?)\b', stxt_lower):
                cat = "ROLE_DESC (unusual FP!)"
            else:
                cat = "OTHER"

            out(f"  - [{cat}] S{snum} × {ei['name']}: `{stxt[:90]}`")
        out()

    # Test hypothesis quantitatively: what % of FPs are structural/package descriptions?
    out("### FP Category Summary")
    out()

    cats = defaultdict(int)
    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        for mid, snum in (result - gold):
            stxt = text.get(snum, "").lower()
            if re.search(r'package overview|package\b.*\bcontains', stxt):
                cats["PKG_OVERVIEW"] += 1
            elif re.search(r'\b\w+\.\w+\s+(contains?|provides?|has|is)\b', stxt):
                cats["SUBPKG_DESC"] += 1
            elif re.search(r'\bcontains?\s+(classes|helpers?|util|abstract|custom|data)', stxt):
                cats["CLASS_LISTING"] += 1
            elif re.search(r'not a (?:real |java )?package', stxt):
                cats["META_COMMENT"] += 1
            elif re.search(r'\brefer to\b', stxt):
                cats["CROSS_REF"] += 1
            else:
                cats["OTHER"] += 1

    total_fps = sum(cats.values())
    out("| Category | Count | % of FPs |")
    out("|----------|-------|----------|")
    for cat in sorted(cats, key=cats.get, reverse=True):
        out(f"| {cat} | {cats[cat]} | {cats[cat]/total_fps:.0%} |")
    out(f"| **TOTAL** | **{total_fps}** | |")
    out()

    structural_total = sum(v for k, v in cats.items() if k != "OTHER")
    out(f"**Structural/package descriptions**: {structural_total}/{total_fps} = "
        f"{structural_total/total_fps:.0%} of all FPs")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Gold TP categorization — what DO they describe?
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Gold TP Sentence Types")
    out()
    out("What kind of sentences ARE in the gold standard?")
    out()

    tp_cats = defaultdict(lambda: defaultdict(int))

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        for mid, snum in gold:
            stxt = text.get(snum, "").lower()
            ei = elem_info.get(mid, {"name": "?"})

            if re.search(r'(responsible|manages?|handles?|processes?|authenticat|serves?)\b', stxt):
                tp_cats[proj]["role/behavior"] += 1
            elif re.search(r'(provides?|delivers?|retriev|sends?|receiv|loads?|stores?)\b', stxt):
                tp_cats[proj]["service/data_flow"] += 1
            elif re.search(r'(consists? of|composed|contains?.*(?:services?|component))\b', stxt):
                tp_cats[proj]["structural_overview"] += 1
            elif re.search(r'(communicat|connect|interact|between)\b', stxt):
                tp_cats[proj]["interaction"] += 1
            elif re.search(r'(is a|represents?|refers? to)\b', stxt):
                tp_cats[proj]["definition"] += 1
            else:
                tp_cats[proj]["other"] += 1

    all_cats = set()
    for proj_cats in tp_cats.values():
        all_cats |= set(proj_cats.keys())

    out("| Project | " + " | ".join(sorted(all_cats)) + " | Total |")
    out("|---------|" + "|".join("---" for _ in all_cats) + "|-------|")
    for proj in PROJECTS:
        vals = [str(tp_cats[proj].get(c, 0)) for c in sorted(all_cats)]
        total = sum(tp_cats[proj].values())
        out(f"| {proj} | " + " | ".join(vals) + f" | {total} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Synthesis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Reverse-Engineered Convention")
    out()
    out("Based on systematic comparison of gold vs non-gold mentions:")
    out()
    out("### The Rule")
    out()
    out("A sentence S is linked to component C if and only if:")
    out()
    out("1. **S mentions C** (by name, synonym, or clear reference)")
    out("2. **S describes C's architectural role, behavior, or interactions** —")
    out("   what C does in the system, what services it provides, what data it handles,")
    out("   how it communicates with other components.")
    out()
    out("A sentence is **NOT** linked even if it mentions C when:")
    out()
    out("- S describes C's **internal package structure** (sub-packages, directory layout)")
    out("- S **lists implementation classes** within C ('contains helpers/utilities/exceptions')")
    out("- S is a **package overview** header ('Package overview contains X.a, X.b, X.c')")
    out("- S is a **meta-comment** about C's implementation ('X.Y is not a Java package')")
    out("- S is a **cross-reference** ('Refer to the API for...')")
    out()
    out("### Abstraction Level Boundary")
    out()
    out("The boundary is between **architectural abstraction** and **implementation abstraction**:")
    out()
    out("- **Architectural**: 'The Storage component manages persistent data' → LINKED")
    out("- **Implementation**: 'storage.entity contains classes that represent persistable entities' → NOT LINKED")
    out()
    out("Both sentences are 'about' Storage, but at different abstraction levels.")
    out("The gold standard only traces at the architectural level.")
    out()

    with open(Path("/mnt/hostshare/ardoco-home/transarc-emp/ANNOTATION_CONVENTION.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nWritten to ANNOTATION_CONVENTION.md")


if __name__ == "__main__":
    main()
