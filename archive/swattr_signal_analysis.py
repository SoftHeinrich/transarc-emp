#!/usr/bin/env python3
"""
Deep signal analysis: What distinguishes TP from FP, and FN from TN in SAD-SAM?

For every possible (element, sentence) pair, compute features and compare
distributions across TP/FP/FN/TN categories.
"""

import csv
import re
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import statistics

BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
RESULTS = "/mnt/hostshare/ardoco-home/transarc-emp/results"

PROJECTS = {
    "mediastore": {"text": "text_2016/mediastore.txt", "model": "model_2016/pcm/ms.repository", "gold": "goldstandards/goldstandard_sad_2016-sam_2016.csv"},
    "teastore": {"text": "text_2020/teastore.txt", "model": "model_2020/pcm/teastore.repository", "gold": "goldstandards/goldstandard_sad_2020-sam_2020.csv"},
    "teammates": {"text": "text_2021/teammates.txt", "model": "model_2021/pcm/teammates.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "jabref": {"text": "text_2021/jabref.txt", "model": "model_2021/pcm/jabref.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "bigbluebutton": {"text": "text_2021/bigbluebutton.txt", "model": "model_2021/pcm/bbb.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
}


def parse_pcm_model(repo_path):
    """Extract component/interface names and IDs."""
    tree = ET.parse(repo_path)
    root = tree.getroot()
    elements = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        eid = elem.get('id')
        ename = elem.get('entityName')
        if eid and ename:
            xsi_type = elem.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
            if tag == 'components__Repository':
                elements[eid] = {'name': ename, 'type': 'Component'}
            elif tag == 'interfaces__Repository':
                elements[eid] = {'name': ename, 'type': 'Interface'}
    return elements


def load_sentences(text_path):
    sentences = {}
    with open(text_path, 'r') as f:
        for i, line in enumerate(f, 1):
            sentences[i] = line.strip()
    return sentences


def load_csv_links(path):
    links = set()
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


# ──────────────────────── Feature Functions ────────────────────────

def tokenize(text):
    """Simple word tokenization."""
    return re.findall(r'[A-Za-z0-9]+', text.lower())


def camel_split(name):
    """Split camelCase/PascalCase into words."""
    parts = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\b)', name)
    return [p.lower() for p in parts if p]


def compute_name_variants(name):
    """Generate name variants for matching."""
    variants = set()
    variants.add(name.lower())
    # camelCase split
    parts = camel_split(name)
    if parts:
        variants.add(' '.join(parts))
        variants.add(''.join(parts))
        # Each individual word
        for p in parts:
            if len(p) > 2:
                variants.add(p)
    # Handle hyphens/spaces
    variants.add(name.lower().replace('-', ' '))
    variants.add(name.lower().replace(' ', ''))
    # Remove common suffixes
    for suffix in ['component', 'service', 'module', 'adapter', 'provider', 'management']:
        stripped = name.lower().replace(suffix, '').strip()
        if stripped and len(stripped) > 2:
            variants.add(stripped)
    return variants


def exact_name_in_sentence(name, text):
    """Check if exact model element name appears in sentence."""
    return name.lower() in text.lower()


def partial_name_in_sentence(name, text):
    """Check if any significant word from name appears in sentence."""
    parts = camel_split(name)
    text_lower = text.lower()
    matches = 0
    for p in parts:
        if len(p) > 2 and p in text_lower:
            matches += 1
    return matches, len(parts) if parts else 1


def fuzzy_name_match(name, text):
    """Best fuzzy match ratio of name against any word window in text."""
    name_lower = name.lower()
    text_lower = text.lower()
    words = text_lower.split()
    best = 0
    # Try sliding windows of various sizes
    name_word_count = len(name.split())
    for window_size in range(1, min(name_word_count + 2, len(words) + 1)):
        for i in range(len(words) - window_size + 1):
            window = ' '.join(words[i:i+window_size])
            ratio = SequenceMatcher(None, name_lower, window).ratio()
            best = max(best, ratio)
    return best


def sentence_starts_with_pronoun(text):
    """Check if sentence starts with a pronoun (coreference signal)."""
    pronouns = ['it ', 'its ', 'they ', 'their ', 'this ', 'these ', 'that ', 'those ',
                'he ', 'she ', 'the component ', 'the module ', 'the service ']
    text_lower = text.lower().strip()
    return any(text_lower.startswith(p) for p in pronouns)


def sentence_has_component_keyword(text):
    """Check if sentence has architecture keywords."""
    keywords = ['component', 'module', 'service', 'server', 'client', 'package',
                'subsystem', 'layer', 'tier', 'framework', 'library', 'plugin']
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def sentence_has_behavioral_keyword(text):
    """Check for behavioral/action keywords."""
    keywords = ['provides', 'handles', 'manages', 'processes', 'sends', 'receives',
                'creates', 'stores', 'fetches', 'queries', 'executes', 'contains',
                'implements', 'uses', 'calls', 'forwards', 'responsible']
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def count_element_mentions_in_sentence(text, all_elements):
    """Count how many different model elements are mentioned in this sentence."""
    count = 0
    for eid, info in all_elements.items():
        if exact_name_in_sentence(info['name'], text):
            count += 1
    return count


def get_section_context(sentences, snum, all_elements):
    """
    Determine what 'section' a sentence belongs to by looking for the nearest
    preceding sentence that introduces a component.
    Returns (nearest_element_id, distance) or (None, -1).
    """
    # Look backwards for the nearest sentence that explicitly names a component as subject
    for dist in range(1, min(snum, 20)):
        prev_snum = snum - dist
        if prev_snum < 1:
            break
        prev_text = sentences.get(prev_snum, '')
        # Check if previous sentence introduces a component
        for eid, info in all_elements.items():
            name = info['name']
            # Component is the sentence subject (appears early)
            first_50 = prev_text[:min(50, len(prev_text))].lower()
            if name.lower() in first_50 or ' '.join(camel_split(name)) in first_50:
                return eid, dist
    return None, -1


def get_paragraph_block(sentences, snum):
    """
    Identify paragraph blocks: consecutive sentences likely about the same topic.
    Look for empty lines or major topic shifts.
    """
    # Simple heuristic: find the nearest "introducing" sentence (names a component)
    # and group consecutive sentences
    return snum  # placeholder


def sentence_relative_position(snum, total_sentences):
    """Relative position in document (0 to 1)."""
    return snum / total_sentences


def word_overlap_with_name(name, text):
    """Compute Jaccard overlap between name words and sentence words."""
    name_words = set(camel_split(name))
    sent_words = set(tokenize(text))
    if not name_words or not sent_words:
        return 0.0
    return len(name_words & sent_words) / len(name_words | sent_words)


# ──────────────────────── Main Analysis ────────────────────────

def compute_features(eid, snum, model_elements, sentences, all_gold, all_result):
    """Compute all features for a (element, sentence) pair."""
    info = model_elements[eid]
    name = info['name']
    etype = info['type']
    text = sentences.get(snum, '')

    # Name matching features
    exact_match = exact_name_in_sentence(name, text)
    partial_matches, total_parts = partial_name_in_sentence(name, text)
    partial_ratio = partial_matches / total_parts if total_parts > 0 else 0
    fuzzy_score = fuzzy_name_match(name, text)
    jaccard = word_overlap_with_name(name, text)

    # Check variant matching
    variants = compute_name_variants(name)
    any_variant_match = any(v in text.lower() for v in variants if len(v) > 2)

    # Where does name appear in sentence?
    name_position = -1
    name_lower = name.lower()
    text_lower = text.lower()
    idx = text_lower.find(name_lower)
    if idx >= 0:
        name_position = idx / len(text) if text else -1
    else:
        # Try camel-split version
        spaced = ' '.join(camel_split(name))
        idx = text_lower.find(spaced)
        if idx >= 0:
            name_position = idx / len(text) if text else -1

    # Name appears as subject (in first 30% of sentence)?
    name_is_subject = name_position >= 0 and name_position < 0.3

    # Sentence features
    sent_len = len(text.split())
    starts_pronoun = sentence_starts_with_pronoun(text)
    arch_keywords = sentence_has_component_keyword(text)
    behav_keywords = sentence_has_behavioral_keyword(text)
    n_elements_mentioned = count_element_mentions_in_sentence(text, model_elements)

    # Context features
    section_eid, section_dist = get_section_context(sentences, snum, model_elements)
    in_own_section = (section_eid == eid)  # The nearest introducing element is this one
    section_distance = section_dist

    # Relative position
    rel_pos = sentence_relative_position(snum, len(sentences))

    # Element-level features
    gold_links_for_element = sum(1 for (e, s) in all_gold if e == eid)
    result_links_for_element = sum(1 for (e, s) in all_result if e == eid)
    gold_links_for_sentence = sum(1 for (e, s) in all_gold if s == snum)

    # Preceding/following sentence context
    prev_text = sentences.get(snum - 1, '')
    next_text = sentences.get(snum + 1, '')
    name_in_prev = exact_name_in_sentence(name, prev_text) or any(v in prev_text.lower() for v in variants if len(v) > 2)
    name_in_next = exact_name_in_sentence(name, next_text) or any(v in next_text.lower() for v in variants if len(v) > 2)

    # Does the element appear anywhere in a ±3 window?
    name_in_window = False
    for offset in range(-3, 4):
        if offset == 0:
            continue
        nearby = sentences.get(snum + offset, '')
        if exact_name_in_sentence(name, nearby):
            name_in_window = True
            break

    return {
        # Name matching
        'exact_match': exact_match,
        'any_variant_match': any_variant_match,
        'partial_ratio': partial_ratio,
        'fuzzy_score': fuzzy_score,
        'jaccard': jaccard,
        'name_position': name_position,
        'name_is_subject': name_is_subject,
        # Sentence
        'sent_len': sent_len,
        'starts_pronoun': starts_pronoun,
        'arch_keywords': arch_keywords,
        'behav_keywords': behav_keywords,
        'n_elements_mentioned': n_elements_mentioned,
        'rel_pos': rel_pos,
        # Context
        'in_own_section': in_own_section,
        'section_distance': section_distance,
        'name_in_prev': name_in_prev,
        'name_in_next': name_in_next,
        'name_in_window': name_in_window,
        # Element
        'element_type': etype,
        'gold_links_for_element': gold_links_for_element,
        'gold_links_for_sentence': gold_links_for_sentence,
    }


def analyze_all():
    """Run analysis across all projects."""

    all_records = []  # (project, eid, snum, category, features)

    for project_name, config in PROJECTS.items():
        bench_dir = os.path.join(BENCHMARK, project_name)
        result_dir = os.path.join(RESULTS, project_name, "sad-sam")

        model_elements = parse_pcm_model(os.path.join(bench_dir, config['model']))
        sentences = load_sentences(os.path.join(bench_dir, config['text']))
        gold = load_csv_links(os.path.join(bench_dir, config['gold']))
        result = load_csv_links(os.path.join(result_dir, f"sadSamTlr_{project_name}.csv"))

        # Only consider component/interface IDs (not internal actions etc.)
        element_ids = list(model_elements.keys())

        for eid in element_ids:
            for snum in sentences:
                pair = (eid, snum)
                in_gold = pair in gold
                in_result = pair in result

                if in_gold and in_result:
                    cat = 'TP'
                elif not in_gold and in_result:
                    cat = 'FP'
                elif in_gold and not in_result:
                    cat = 'FN'
                else:
                    cat = 'TN'

                features = compute_features(eid, snum, model_elements, sentences, gold, result)
                features['project'] = project_name
                features['element_name'] = model_elements[eid]['name']
                features['sentence_num'] = snum
                features['sentence_text'] = sentences[snum][:200]
                features['category'] = cat

                all_records.append(features)

    return all_records


def print_signal_comparison(records):
    """Compare feature distributions across categories."""

    cats = {'TP': [], 'FP': [], 'FN': [], 'TN': []}
    for r in records:
        cats[r['category']].append(r)

    print(f"Total pairs: {len(records)}")
    print(f"  TP={len(cats['TP'])}, FP={len(cats['FP'])}, FN={len(cats['FN'])}, TN={len(cats['TN'])}")
    print()

    # ──────────────────────── TP vs FP ────────────────────────
    print("=" * 90)
    print("SIGNAL ANALYSIS: TP vs FP (what distinguishes true links from false links?)")
    print("=" * 90)
    print(f"(TP={len(cats['TP'])}, FP={len(cats['FP'])})")

    numeric_features = [
        'exact_match', 'any_variant_match', 'partial_ratio', 'fuzzy_score', 'jaccard',
        'name_position', 'name_is_subject', 'sent_len', 'starts_pronoun',
        'arch_keywords', 'behav_keywords', 'n_elements_mentioned', 'rel_pos',
        'in_own_section', 'section_distance', 'name_in_prev', 'name_in_next',
        'name_in_window', 'gold_links_for_element', 'gold_links_for_sentence',
    ]

    def safe_mean(vals):
        return statistics.mean(vals) if vals else 0

    def safe_median(vals):
        return statistics.median(vals) if vals else 0

    def rate(vals):
        """For boolean features, compute rate of True."""
        return sum(1 for v in vals if v) / len(vals) if vals else 0

    print(f"\n{'Feature':<28} {'TP mean':>10} {'FP mean':>10} {'Δ(TP-FP)':>10} {'TP med':>10} {'FP med':>10} {'Signal?':>8}")
    print("-" * 90)

    for feat in numeric_features:
        tp_vals = [r[feat] for r in cats['TP'] if r[feat] is not None and r[feat] != -1]
        fp_vals = [r[feat] for r in cats['FP'] if r[feat] is not None and r[feat] != -1]

        if isinstance(tp_vals[0] if tp_vals else 0, bool):
            tp_m = rate(tp_vals)
            fp_m = rate(fp_vals)
            tp_med = tp_m
            fp_med = fp_m
        else:
            tp_m = safe_mean(tp_vals)
            fp_m = safe_mean(fp_vals)
            tp_med = safe_median(tp_vals)
            fp_med = safe_median(fp_vals)

        delta = tp_m - fp_m
        signal = "***" if abs(delta) > 0.2 else "**" if abs(delta) > 0.1 else "*" if abs(delta) > 0.05 else ""
        print(f"  {feat:<26} {tp_m:>10.3f} {fp_m:>10.3f} {delta:>+10.3f} {tp_med:>10.3f} {fp_med:>10.3f} {signal:>8}")

    # Element type breakdown
    print(f"\n  Element type distribution:")
    for cat_name in ['TP', 'FP']:
        type_counts = Counter(r['element_type'] for r in cats[cat_name])
        total = len(cats[cat_name])
        print(f"    {cat_name}: {dict(type_counts)} (Component rate: {type_counts.get('Component',0)/total:.3f})")

    # ──────────────────────── FN vs TN ────────────────────────
    print()
    print("=" * 90)
    print("SIGNAL ANALYSIS: FN vs TN (what makes missed links look like non-links?)")
    print("=" * 90)
    print(f"(FN={len(cats['FN'])}, TN={len(cats['TN'])})")

    print(f"\n{'Feature':<28} {'FN mean':>10} {'TN mean':>10} {'Δ(FN-TN)':>10} {'FN med':>10} {'TN med':>10} {'Signal?':>8}")
    print("-" * 90)

    for feat in numeric_features:
        fn_vals = [r[feat] for r in cats['FN'] if r[feat] is not None and r[feat] != -1]
        tn_vals = [r[feat] for r in cats['TN'] if r[feat] is not None and r[feat] != -1]

        if isinstance(fn_vals[0] if fn_vals else 0, bool):
            fn_m = rate(fn_vals)
            tn_m = rate(tn_vals)
            fn_med = fn_m
            tn_med = tn_m
        else:
            fn_m = safe_mean(fn_vals)
            tn_m = safe_mean(tn_vals)
            fn_med = safe_median(fn_vals)
            tn_med = safe_median(tn_vals)

        delta = fn_m - tn_m
        signal = "***" if abs(delta) > 0.2 else "**" if abs(delta) > 0.1 else "*" if abs(delta) > 0.05 else ""
        print(f"  {feat:<26} {fn_m:>10.3f} {tn_m:>10.3f} {delta:>+10.3f} {fn_med:>10.3f} {tn_med:>10.3f} {signal:>8}")

    # ──────────────────────── TP vs FP detailed breakdowns ────────────────────────
    print()
    print("=" * 90)
    print("DETAILED SIGNAL BREAKDOWNS")
    print("=" * 90)

    # 1. exact_match crosstab
    print("\n--- 1. Exact name match crosstab ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        matched = sum(1 for r in cats[cat_name] if r['exact_match'])
        total = len(cats[cat_name])
        pct = matched / total * 100 if total else 0
        print(f"  {cat_name}: {matched}/{total} ({pct:.1f}%) have exact name match")

    # 2. Section membership
    print("\n--- 2. In own section (nearest introducing sentence is for this element) ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        in_sec = sum(1 for r in cats[cat_name] if r['in_own_section'])
        total = len(cats[cat_name])
        pct = in_sec / total * 100 if total else 0
        print(f"  {cat_name}: {in_sec}/{total} ({pct:.1f}%) in own section")

    # 3. Pronoun starts
    print("\n--- 3. Starts with pronoun/demonstrative ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        pron = sum(1 for r in cats[cat_name] if r['starts_pronoun'])
        total = len(cats[cat_name])
        pct = pron / total * 100 if total else 0
        print(f"  {cat_name}: {pron}/{total} ({pct:.1f}%)")

    # 4. Name in adjacent sentences
    print("\n--- 4. Name appears in ±1 adjacent sentence ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        adj = sum(1 for r in cats[cat_name] if r['name_in_prev'] or r['name_in_next'])
        total = len(cats[cat_name])
        pct = adj / total * 100 if total else 0
        print(f"  {cat_name}: {adj}/{total} ({pct:.1f}%)")

    # 5. Name in ±3 window
    print("\n--- 5. Name appears in ±3 window ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        win = sum(1 for r in cats[cat_name] if r['name_in_window'])
        total = len(cats[cat_name])
        pct = win / total * 100 if total else 0
        print(f"  {cat_name}: {win}/{total} ({pct:.1f}%)")

    # 6. Combination: exact_match + in_own_section
    print("\n--- 6. Combo: exact match AND in own section ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        combo = sum(1 for r in cats[cat_name] if r['exact_match'] and r['in_own_section'])
        total = len(cats[cat_name])
        pct = combo / total * 100 if total else 0
        print(f"  {cat_name}: {combo}/{total} ({pct:.1f}%)")

    # 7. Combination: exact_match but NOT in_own_section
    print("\n--- 7. Exact match but NOT in own section ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        combo = sum(1 for r in cats[cat_name] if r['exact_match'] and not r['in_own_section'])
        total = len(cats[cat_name])
        pct = combo / total * 100 if total else 0
        print(f"  {cat_name}: {combo}/{total} ({pct:.1f}%)")

    # 8. Gold links for the sentence (how "traceable" is this sentence?)
    print("\n--- 8. Gold links for sentence (how traceable is the sentence?) ---")
    for cat_name in ['TP', 'FP', 'FN', 'TN']:
        vals = [r['gold_links_for_sentence'] for r in cats[cat_name]]
        print(f"  {cat_name}: mean={safe_mean(vals):.2f}, median={safe_median(vals):.1f}")

    # ──────────────────────── Per-project signal ────────────────────────
    print()
    print("=" * 90)
    print("PER-PROJECT TP vs FP ANALYSIS")
    print("=" * 90)

    for proj in PROJECTS:
        proj_tp = [r for r in cats['TP'] if r['project'] == proj]
        proj_fp = [r for r in cats['FP'] if r['project'] == proj]
        if not proj_fp:
            print(f"\n  {proj}: No FPs!")
            continue

        print(f"\n  {proj} (TP={len(proj_tp)}, FP={len(proj_fp)}):")

        # Key distinguishing features
        tp_exact = rate([r['exact_match'] for r in proj_tp])
        fp_exact = rate([r['exact_match'] for r in proj_fp])
        tp_section = rate([r['in_own_section'] for r in proj_tp])
        fp_section = rate([r['in_own_section'] for r in proj_fp])
        tp_subj = rate([r['name_is_subject'] for r in proj_tp])
        fp_subj = rate([r['name_is_subject'] for r in proj_fp])
        tp_pronoun = rate([r['starts_pronoun'] for r in proj_tp])
        fp_pronoun = rate([r['starts_pronoun'] for r in proj_fp])
        tp_gold_sent = safe_mean([r['gold_links_for_sentence'] for r in proj_tp])
        fp_gold_sent = safe_mean([r['gold_links_for_sentence'] for r in proj_fp])
        tp_window = rate([r['name_in_window'] for r in proj_tp])
        fp_window = rate([r['name_in_window'] for r in proj_fp])

        print(f"    exact_match:    TP={tp_exact:.3f}  FP={fp_exact:.3f}  Δ={tp_exact-fp_exact:+.3f}")
        print(f"    in_own_section: TP={tp_section:.3f}  FP={fp_section:.3f}  Δ={tp_section-fp_section:+.3f}")
        print(f"    name_is_subject:TP={tp_subj:.3f}  FP={fp_subj:.3f}  Δ={tp_subj-fp_subj:+.3f}")
        print(f"    starts_pronoun: TP={tp_pronoun:.3f}  FP={fp_pronoun:.3f}  Δ={tp_pronoun-fp_pronoun:+.3f}")
        print(f"    gold_for_sent:  TP={tp_gold_sent:.2f}   FP={fp_gold_sent:.2f}   Δ={tp_gold_sent-fp_gold_sent:+.2f}")
        print(f"    name_in_window: TP={tp_window:.3f}  FP={fp_window:.3f}  Δ={tp_window-fp_window:+.3f}")

        # Show each FP with its distinguishing features
        print(f"\n    Individual FPs:")
        for r in proj_fp:
            print(f"      {r['element_name']} → S{r['sentence_num']}: "
                  f"exact={r['exact_match']}, section={r['in_own_section']}, "
                  f"subject={r['name_is_subject']}, pronoun={r['starts_pronoun']}, "
                  f"window={r['name_in_window']}, gold_sent={r['gold_links_for_sentence']}")
            print(f"        \"{r['sentence_text'][:120]}\"")

    # ──────────────────────── Deep FP categorization ────────────────────────
    print()
    print("=" * 90)
    print("FP CATEGORIZATION: Why is each FP not a TP?")
    print("=" * 90)

    fp_categories = Counter()
    for r in cats['FP']:
        # Try to categorize the FP
        text_lower = r['sentence_text'].lower()
        name_lower = r['element_name'].lower()

        # Package description pattern
        pkg_patterns = ['package overview', 'package contains', '.api ', '.core ',
                       '.util ', '.entity ', '.cases ', '.pageobjects ',
                       'contains helpers', 'contains classes', 'contains test',
                       'contains custom', 'contains data', 'contains utility']
        is_pkg_desc = any(p in text_lower for p in pkg_patterns)

        # Negative statement
        is_negative = 'not a ' in text_lower or 'is not ' in text_lower

        # Cross-reference (mentions element in context of another)
        if r['n_elements_mentioned'] > 1 and r['gold_links_for_sentence'] > 0:
            category = 'cross_reference'
        elif is_pkg_desc:
            category = 'package_description'
        elif is_negative:
            category = 'negative_statement'
        elif not r['in_own_section'] and r['exact_match']:
            category = 'out_of_section_mention'
        elif r['gold_links_for_sentence'] == 0:
            category = 'non_traceable_sentence'
        else:
            category = 'wrong_element_assigned'

        fp_categories[category] += 1
        r['fp_category'] = category

    print(f"\n  FP categories ({len(cats['FP'])} total):")
    for cat, count in fp_categories.most_common():
        pct = count / len(cats['FP']) * 100
        print(f"    {cat}: {count} ({pct:.1f}%)")

    # Show examples for each category
    for cat in fp_categories:
        examples = [r for r in cats['FP'] if r.get('fp_category') == cat][:3]
        print(f"\n    Examples of '{cat}':")
        for r in examples:
            print(f"      [{r['project']}] {r['element_name']} → S{r['sentence_num']}")
            print(f"        \"{r['sentence_text'][:120]}\"")

    # ──────────────────────── Deep FN categorization ────────────────────────
    print()
    print("=" * 90)
    print("FN CATEGORIZATION: Why did SWATTR miss each FN?")
    print("=" * 90)

    fn_categories = Counter()
    for r in cats['FN']:
        if r['exact_match']:
            if r['in_own_section']:
                category = 'exact_match_in_section_MISSED'
            else:
                category = 'exact_match_out_of_section'
        elif r['any_variant_match']:
            category = 'variant_match_only'
        elif r['starts_pronoun'] or r['name_in_prev']:
            category = 'coreference_needed'
        elif r['name_in_window']:
            category = 'nearby_context'
        else:
            category = 'no_lexical_signal'

        fn_categories[category] += 1
        r['fn_category'] = category

    print(f"\n  FN categories ({len(cats['FN'])} total):")
    for cat, count in fn_categories.most_common():
        pct = count / len(cats['FN']) * 100
        print(f"    {cat}: {count} ({pct:.1f}%)")

    for cat in fn_categories:
        examples = [r for r in cats['FN'] if r.get('fn_category') == cat][:3]
        print(f"\n    Examples of '{cat}':")
        for r in examples:
            print(f"      [{r['project']}] {r['element_name']} → S{r['sentence_num']}")
            print(f"        \"{r['sentence_text'][:120]}\"")

    # ──────────────────────── Discriminative power summary ────────────────────────
    print()
    print("=" * 90)
    print("DISCRIMINATIVE POWER SUMMARY")
    print("=" * 90)

    # For TP vs FP: compute how well each feature separates them
    print("\n  TP vs FP — Best discriminating features:")
    positive = cats['TP'] + cats['FP']
    feature_disc = []
    for feat in numeric_features:
        tp_vals = [1 if r[feat] else 0 for r in cats['TP']] if isinstance(cats['TP'][0][feat], bool) else [r[feat] for r in cats['TP'] if r[feat] is not None and r[feat] != -1]
        fp_vals = [1 if r[feat] else 0 for r in cats['FP']] if isinstance(cats['FP'][0][feat], bool) else [r[feat] for r in cats['FP'] if r[feat] is not None and r[feat] != -1]

        tp_m = safe_mean(tp_vals)
        fp_m = safe_mean(fp_vals)
        # Effect size (Cohen's d approximation)
        tp_std = statistics.stdev(tp_vals) if len(tp_vals) > 1 else 0.001
        fp_std = statistics.stdev(fp_vals) if len(fp_vals) > 1 else 0.001
        pooled_std = ((tp_std**2 + fp_std**2) / 2) ** 0.5
        cohens_d = (tp_m - fp_m) / pooled_std if pooled_std > 0 else 0
        feature_disc.append((feat, cohens_d, tp_m, fp_m))

    feature_disc.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\n  {'Feature':<28} {'Cohen d':>8} {'TP mean':>8} {'FP mean':>8} {'Direction':>12}")
    for feat, d, tp_m, fp_m in feature_disc:
        direction = "TP>FP" if d > 0 else "FP>TP"
        stars = "***" if abs(d) > 0.8 else "**" if abs(d) > 0.5 else "*" if abs(d) > 0.2 else ""
        print(f"  {feat:<28} {d:>+8.3f} {tp_m:>8.3f} {fp_m:>8.3f} {direction:>10} {stars}")

    # For FN vs TN
    print("\n  FN vs TN — Best discriminating features:")
    feature_disc2 = []
    for feat in numeric_features:
        fn_vals = [1 if r[feat] else 0 for r in cats['FN']] if isinstance(cats['FN'][0][feat], bool) else [r[feat] for r in cats['FN'] if r[feat] is not None and r[feat] != -1]
        tn_vals = [1 if r[feat] else 0 for r in cats['TN']] if isinstance(cats['TN'][0][feat], bool) else [r[feat] for r in cats['TN'] if r[feat] is not None and r[feat] != -1]

        fn_m = safe_mean(fn_vals)
        tn_m = safe_mean(tn_vals)
        fn_std = statistics.stdev(fn_vals) if len(fn_vals) > 1 else 0.001
        tn_std = statistics.stdev(tn_vals) if len(tn_vals) > 1 else 0.001
        pooled_std = ((fn_std**2 + tn_std**2) / 2) ** 0.5
        cohens_d = (fn_m - tn_m) / pooled_std if pooled_std > 0 else 0
        feature_disc2.append((feat, cohens_d, fn_m, tn_m))

    feature_disc2.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\n  {'Feature':<28} {'Cohen d':>8} {'FN mean':>8} {'TN mean':>8} {'Direction':>12}")
    for feat, d, fn_m, tn_m in feature_disc2:
        direction = "FN>TN" if d > 0 else "TN>FN"
        stars = "***" if abs(d) > 0.8 else "**" if abs(d) > 0.5 else "*" if abs(d) > 0.2 else ""
        print(f"  {feat:<28} {d:>+8.3f} {fn_m:>8.3f} {tn_m:>8.3f} {direction:>10} {stars}")

    # ──────────────────────── Conditional probability analysis ────────────────────────
    print()
    print("=" * 90)
    print("CONDITIONAL PROBABILITIES (P(TP|feature), P(FP|feature), etc.)")
    print("=" * 90)

    # Among all SWATTR positives (TP+FP), what's P(TP | feature)?
    positives = cats['TP'] + cats['FP']
    print(f"\n  Among SWATTR positives ({len(positives)} = {len(cats['TP'])} TP + {len(cats['FP'])} FP):")

    conditions = [
        ('exact_match=True', lambda r: r['exact_match']),
        ('exact_match=False', lambda r: not r['exact_match']),
        ('in_own_section=True', lambda r: r['in_own_section']),
        ('in_own_section=False', lambda r: not r['in_own_section']),
        ('name_is_subject=True', lambda r: r['name_is_subject']),
        ('starts_pronoun=True', lambda r: r['starts_pronoun']),
        ('gold_for_sent>0', lambda r: r['gold_links_for_sentence'] > 0),
        ('gold_for_sent=0', lambda r: r['gold_links_for_sentence'] == 0),
        ('n_elements_mentioned>1', lambda r: r['n_elements_mentioned'] > 1),
        ('name_in_window=True', lambda r: r['name_in_window']),
        ('exact+section', lambda r: r['exact_match'] and r['in_own_section']),
        ('exact+NOT_section', lambda r: r['exact_match'] and not r['in_own_section']),
        ('exact+subject', lambda r: r['exact_match'] and r['name_is_subject']),
        ('exact+NOT_subject', lambda r: r['exact_match'] and not r['name_is_subject']),
    ]

    print(f"\n  {'Condition':<30} {'N':>5} {'P(TP)':>8} {'P(FP)':>8} {'TP':>5} {'FP':>5}")
    print("  " + "-" * 70)
    for cond_name, cond_fn in conditions:
        matching = [r for r in positives if cond_fn(r)]
        if not matching:
            continue
        tp_count = sum(1 for r in matching if r['category'] == 'TP')
        fp_count = sum(1 for r in matching if r['category'] == 'FP')
        n = len(matching)
        print(f"  {cond_name:<30} {n:>5} {tp_count/n:>8.3f} {fp_count/n:>8.3f} {tp_count:>5} {fp_count:>5}")

    # Among all gold positives (TP+FN), what helps SWATTR find them?
    gold_positives = cats['TP'] + cats['FN']
    print(f"\n  Among gold positives ({len(gold_positives)} = {len(cats['TP'])} TP + {len(cats['FN'])} FN):")

    conditions2 = [
        ('exact_match=True', lambda r: r['exact_match']),
        ('exact_match=False', lambda r: not r['exact_match']),
        ('any_variant=True', lambda r: r['any_variant_match']),
        ('any_variant=False', lambda r: not r['any_variant_match']),
        ('in_own_section=True', lambda r: r['in_own_section']),
        ('in_own_section=False', lambda r: not r['in_own_section']),
        ('name_is_subject=True', lambda r: r['name_is_subject']),
        ('starts_pronoun=True', lambda r: r['starts_pronoun']),
        ('name_in_window=True', lambda r: r['name_in_window']),
        ('name_in_window=False', lambda r: not r['name_in_window']),
        ('exact+section', lambda r: r['exact_match'] and r['in_own_section']),
        ('exact+NOT_section', lambda r: r['exact_match'] and not r['in_own_section']),
        ('NO_exact+section', lambda r: not r['exact_match'] and r['in_own_section']),
        ('NO_exact+NO_section', lambda r: not r['exact_match'] and not r['in_own_section']),
    ]

    print(f"\n  {'Condition':<30} {'N':>5} {'P(TP)':>8} {'P(FN)':>8} {'TP':>5} {'FN':>5}")
    print("  " + "-" * 70)
    for cond_name, cond_fn in conditions2:
        matching = [r for r in gold_positives if cond_fn(r)]
        if not matching:
            continue
        tp_count = sum(1 for r in matching if r['category'] == 'TP')
        fn_count = sum(1 for r in matching if r['category'] == 'FN')
        n = len(matching)
        print(f"  {cond_name:<30} {n:>5} {tp_count/n:>8.3f} {fn_count/n:>8.3f} {tp_count:>5} {fn_count:>5}")


if __name__ == '__main__':
    records = analyze_all()
    print_signal_comparison(records)
