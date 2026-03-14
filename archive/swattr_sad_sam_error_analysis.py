#!/usr/bin/env python3
"""
Error analysis of SWATTR SAD-SAM results vs gold standard.
Identifies patterns in false positives and false negatives.
"""

import csv
import re
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
RESULTS = "/mnt/hostshare/ardoco-home/transarc-emp/results"

PROJECTS = {
    "mediastore": {"text": "text_2016/mediastore.txt", "model": "model_2016/pcm/ms.repository", "gold": "goldstandards/goldstandard_sad_2016-sam_2016.csv", "ume": "goldstandards/goldstandard_sad_2016-sam_2016_UME.csv"},
    "teastore": {"text": "text_2020/teastore.txt", "model": "model_2020/pcm/teastore.repository", "gold": "goldstandards/goldstandard_sad_2020-sam_2020.csv", "ume": "goldstandards/goldstandard_sad_2020-sam_2020_UME.csv"},
    "teammates": {"text": "text_2021/teammates.txt", "model": "model_2021/pcm/teammates.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv", "ume": "goldstandards/goldstandard_sad_2021-sam_2021_UME.csv"},
    "jabref": {"text": "text_2021/jabref.txt", "model": "model_2021/pcm/jabref.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv", "ume": "goldstandards/goldstandard_sad_2021-sam_2021_UME.csv"},
    "bigbluebutton": {"text": "text_2021/bigbluebutton.txt", "model": "model_2021/pcm/bbb.repository", "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv", "ume": "goldstandards/goldstandard_sad_2021-sam_2021_UME.csv"},
}


def parse_pcm_model(repo_path):
    """Extract component/interface names and IDs from PCM .repository file."""
    tree = ET.parse(repo_path)
    root = tree.getroot()

    elements = {}
    # Namespace handling
    ns = {}
    for attr, val in root.attrib.items():
        if attr.startswith('{'):
            continue

    # Find all components and interfaces
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        eid = elem.get('id')
        ename = elem.get('entityName')

        if eid and ename:
            etype = None
            xsi_type = elem.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')

            if tag == 'components__Repository':
                if 'BasicComponent' in xsi_type or 'CompositeComponent' in xsi_type:
                    etype = 'Component'
                else:
                    etype = 'Component'
            elif tag == 'interfaces__Repository':
                etype = 'Interface'

            if etype:
                elements[eid] = {'name': ename, 'type': etype}

    return elements


def load_sentences(text_path):
    """Load sentences from text file (1-indexed)."""
    sentences = {}
    with open(text_path, 'r') as f:
        for i, line in enumerate(f, 1):
            sentences[i] = line.strip()
    return sentences


def load_gold(gold_path):
    """Load gold standard as set of (modelElementID, sentence) tuples."""
    links = set()
    with open(gold_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def load_result(result_path):
    """Load SWATTR result as set of (modelElementID, sentence) tuples."""
    links = set()
    with open(result_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def load_ume(ume_path):
    """Load undocumented model elements."""
    ume_ids = set()
    if not os.path.exists(ume_path):
        return ume_ids
    with open(ume_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ume_ids.add(row['missingModelElementID'])
    return ume_ids


def classify_sentence(text):
    """Classify a sentence by its content type."""
    text_lower = text.lower()

    # Structural/architectural
    if any(kw in text_lower for kw in ['component', 'module', 'service', 'server', 'client', 'tier', 'layer', 'subsystem']):
        return 'structural'
    # Behavioral/functional
    if any(kw in text_lower for kw in ['request', 'process', 'send', 'receive', 'forward', 'fetch', 'store', 'create', 'delete', 'update', 'query', 'execute']):
        return 'behavioral'
    # Data/storage
    if any(kw in text_lower for kw in ['database', 'storage', 'data', 'file', 'persist', 'cache']):
        return 'data'
    # Communication
    if any(kw in text_lower for kw in ['api', 'interface', 'protocol', 'rest', 'http', 'message', 'communicate']):
        return 'communication'
    # User-facing
    if any(kw in text_lower for kw in ['user', 'login', 'authentication', 'registration', 'page', 'website', 'browse', 'upload', 'download']):
        return 'user-facing'
    return 'other'


def find_component_mentions(text, model_elements):
    """Find which model elements are mentioned in a sentence."""
    mentioned = []
    text_lower = text.lower()
    for eid, info in model_elements.items():
        name = info['name']
        # Try exact match and common variations
        name_lower = name.lower()
        # Split camelCase
        words = re.findall(r'[A-Z][a-z]+|[a-z]+', name)
        name_spaced = ' '.join(words).lower()

        if name_lower in text_lower or name_spaced in text_lower:
            mentioned.append((eid, name))
    return mentioned


def analyze_project(project_name, config):
    """Analyze SAD-SAM errors for a single project."""
    bench_dir = os.path.join(BENCHMARK, project_name)
    result_dir = os.path.join(RESULTS, project_name, "sad-sam")

    # Load data
    model_elements = parse_pcm_model(os.path.join(bench_dir, config['model']))
    sentences = load_sentences(os.path.join(bench_dir, config['text']))
    gold = load_gold(os.path.join(bench_dir, config['gold']))

    result_file = os.path.join(result_dir, f"sadSamTlr_{project_name}.csv")
    result = load_result(result_file)

    ume = load_ume(os.path.join(bench_dir, config['ume']))

    # Compute sets
    tp = gold & result
    fp = result - gold
    fn = gold - result

    precision = len(tp) / len(result) if result else 0
    recall = len(tp) / len(gold) if gold else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n{'='*80}")
    print(f"PROJECT: {project_name.upper()}")
    print(f"{'='*80}")
    print(f"Model elements: {len(model_elements)} ({sum(1 for v in model_elements.values() if v['type']=='Component')} Components, {sum(1 for v in model_elements.values() if v['type']=='Interface')} Interfaces)")
    print(f"Sentences: {len(sentences)}")
    print(f"Gold links: {len(gold)}, Result links: {len(result)}")
    print(f"TP={len(tp)}, FP={len(fp)}, FN={len(fn)}")
    print(f"Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")

    # --- FALSE POSITIVE ANALYSIS ---
    print(f"\n--- FALSE POSITIVES ({len(fp)}) ---")

    fp_by_element = defaultdict(list)
    fp_by_sentence = defaultdict(list)
    fp_element_types = Counter()
    fp_sentence_types = Counter()

    for eid, snum in fp:
        ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
        etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
        stext = sentences.get(snum, 'UNKNOWN')

        fp_by_element[f"{ename} ({etype})"].append(snum)
        fp_by_sentence[snum].append(f"{ename} ({etype})")
        fp_element_types[etype] += 1
        fp_sentence_types[classify_sentence(stext)] += 1

    if fp:
        print(f"\n  FP by element type: {dict(fp_element_types)}")
        print(f"  FP by sentence category: {dict(fp_sentence_types)}")

        print(f"\n  FP by model element:")
        for elem, snums in sorted(fp_by_element.items(), key=lambda x: -len(x[1])):
            print(f"    {elem}: sentences {sorted(snums)}")

        print(f"\n  FP details (element → sentence):")
        for eid, snum in sorted(fp, key=lambda x: x[1]):
            ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
            etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
            stext = sentences.get(snum, 'UNKNOWN')
            # Check if element IS mentioned in sentence
            mentioned = find_component_mentions(stext, {eid: model_elements[eid]}) if eid in model_elements else []
            mention_flag = "MENTIONED" if mentioned else "NOT_MENTIONED"
            # Check if gold has this element at all
            gold_sents_for_elem = sorted([s for (e, s) in gold if e == eid])
            # Check if gold has this sentence at all
            gold_elems_for_sent = [(e, model_elements.get(e, {}).get('name', '?')) for (e, s) in gold if s == snum]
            print(f"    FP: {ename} ({etype}) → S{snum} [{mention_flag}]")
            print(f"         \"{stext[:120]}...\"" if len(stext) > 120 else f"         \"{stext}\"")
            print(f"         Gold for this element: sentences {gold_sents_for_elem}")
            print(f"         Gold for this sentence: {gold_elems_for_sent}")

    # --- FALSE NEGATIVE ANALYSIS ---
    print(f"\n--- FALSE NEGATIVES ({len(fn)}) ---")

    fn_by_element = defaultdict(list)
    fn_by_sentence = defaultdict(list)
    fn_element_types = Counter()
    fn_sentence_types = Counter()

    for eid, snum in fn:
        ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
        etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
        stext = sentences.get(snum, 'UNKNOWN')

        fn_by_element[f"{ename} ({etype})"].append(snum)
        fn_by_sentence[snum].append(f"{ename} ({etype})")
        fn_element_types[etype] += 1
        fn_sentence_types[classify_sentence(stext)] += 1

    if fn:
        print(f"\n  FN by element type: {dict(fn_element_types)}")
        print(f"  FN by sentence category: {dict(fn_sentence_types)}")

        print(f"\n  FN by model element:")
        for elem, snums in sorted(fn_by_element.items(), key=lambda x: -len(x[1])):
            print(f"    {elem}: sentences {sorted(snums)}")

        print(f"\n  FN details (element → sentence):")
        for eid, snum in sorted(fn, key=lambda x: x[1]):
            ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
            etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
            stext = sentences.get(snum, 'UNKNOWN')
            mentioned = find_component_mentions(stext, {eid: model_elements[eid]}) if eid in model_elements else []
            mention_flag = "MENTIONED" if mentioned else "NOT_MENTIONED"
            # Check if result has this element at all
            result_sents_for_elem = sorted([s for (e, s) in result if e == eid])
            # Check if result has this sentence at all
            result_elems_for_sent = [(e, model_elements.get(e, {}).get('name', '?')) for (e, s) in result if s == snum]
            print(f"    FN: {ename} ({etype}) → S{snum} [{mention_flag}]")
            print(f"         \"{stext[:120]}...\"" if len(stext) > 120 else f"         \"{stext}\"")
            print(f"         SWATTR found for this element: sentences {result_sents_for_elem}")
            print(f"         SWATTR found for this sentence: {result_elems_for_sent}")

    # --- PATTERN ANALYSIS ---
    print(f"\n--- PATTERN ANALYSIS ---")

    # 1. Elements completely missed (all gold links are FN)
    gold_by_element = defaultdict(set)
    result_by_element = defaultdict(set)
    for eid, snum in gold:
        gold_by_element[eid].add(snum)
    for eid, snum in result:
        result_by_element[eid].add(snum)

    completely_missed = []
    partially_missed = []
    for eid in gold_by_element:
        gold_sents = gold_by_element[eid]
        result_sents = result_by_element.get(eid, set())
        hit_sents = gold_sents & result_sents
        miss_sents = gold_sents - result_sents
        if len(hit_sents) == 0:
            completely_missed.append((eid, gold_sents))
        elif len(miss_sents) > 0:
            partially_missed.append((eid, hit_sents, miss_sents))

    if completely_missed:
        print(f"\n  Completely missed elements ({len(completely_missed)}):")
        for eid, sents in completely_missed:
            ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
            etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
            is_ume = eid in ume
            print(f"    {ename} ({etype}): {len(sents)} gold links missed{' [UME]' if is_ume else ''}")

    if partially_missed:
        print(f"\n  Partially missed elements ({len(partially_missed)}):")
        for eid, hits, misses in partially_missed:
            ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
            etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
            print(f"    {ename} ({etype}): found {len(hits)}/{len(hits)+len(misses)} gold links, missed S{sorted(misses)}")

    # 2. Elements with only FPs (not in gold at all)
    spurious_elements = []
    for eid in result_by_element:
        if eid not in gold_by_element:
            spurious_elements.append((eid, result_by_element[eid]))

    if spurious_elements:
        print(f"\n  Spurious elements (FP-only, {len(spurious_elements)}):")
        for eid, sents in spurious_elements:
            ename = model_elements.get(eid, {}).get('name', 'UNKNOWN')
            etype = model_elements.get(eid, {}).get('type', 'UNKNOWN')
            print(f"    {ename} ({etype}): {len(sents)} FP links")

    # 3. Sentence-level analysis
    gold_by_sentence = defaultdict(set)
    result_by_sentence = defaultdict(set)
    for eid, snum in gold:
        gold_by_sentence[snum].add(eid)
    for eid, snum in result:
        result_by_sentence[snum].add(eid)

    # Sentences in gold but completely missed
    missed_sentences = [s for s in gold_by_sentence if s not in result_by_sentence]
    if missed_sentences:
        print(f"\n  Sentences completely missed ({len(missed_sentences)}):")
        for snum in sorted(missed_sentences):
            stext = sentences.get(snum, '?')
            gold_elems = [model_elements.get(e, {}).get('name', '?') for e in gold_by_sentence[snum]]
            print(f"    S{snum}: gold={gold_elems}")
            print(f"         \"{stext[:120]}\"")

    # Sentences with only FPs (not in gold)
    spurious_sentences = [s for s in result_by_sentence if s not in gold_by_sentence]
    if spurious_sentences:
        print(f"\n  Spurious sentences (FP-only, {len(spurious_sentences)}):")
        for snum in sorted(spurious_sentences):
            stext = sentences.get(snum, '?')
            result_elems = [model_elements.get(e, {}).get('name', '?') for e in result_by_sentence[snum]]
            print(f"    S{snum}: result={result_elems}")
            print(f"         \"{stext[:120]}\"")

    # 4. Check mention patterns
    fp_mentioned = sum(1 for eid, snum in fp if find_component_mentions(sentences.get(snum, ''), {eid: model_elements[eid]}) if eid in model_elements)
    fp_not_mentioned = len(fp) - fp_mentioned
    fn_mentioned = sum(1 for eid, snum in fn if find_component_mentions(sentences.get(snum, ''), {eid: model_elements[eid]}) if eid in model_elements)
    fn_not_mentioned = len(fn) - fn_mentioned

    print(f"\n  Name mention patterns:")
    print(f"    FP: {fp_mentioned} with name mentioned, {fp_not_mentioned} without")
    print(f"    FN: {fn_mentioned} with name mentioned, {fn_not_mentioned} without")

    return {
        'project': project_name,
        'tp': len(tp), 'fp': len(fp), 'fn': len(fn),
        'precision': precision, 'recall': recall, 'f1': f1,
        'gold_count': len(gold), 'result_count': len(result),
        'model_elements': len(model_elements),
        'sentences': len(sentences),
        'fp_set': fp, 'fn_set': fn, 'tp_set': tp,
        'model': model_elements, 'sents': sentences,
    }


def cross_project_analysis(results):
    """Analyze patterns across all projects."""
    print(f"\n\n{'='*80}")
    print("CROSS-PROJECT ANALYSIS")
    print(f"{'='*80}")

    # Summary table
    print(f"\n{'Project':<15} {'Gold':>5} {'Result':>6} {'TP':>4} {'FP':>4} {'FN':>4} {'P':>6} {'R':>6} {'F1':>6}")
    print("-" * 65)
    total_tp = total_fp = total_fn = total_gold = total_result = 0
    for r in results:
        print(f"{r['project']:<15} {r['gold_count']:>5} {r['result_count']:>6} {r['tp']:>4} {r['fp']:>4} {r['fn']:>4} {r['precision']:>6.3f} {r['recall']:>6.3f} {r['f1']:>6.3f}")
        total_tp += r['tp']
        total_fp += r['fp']
        total_fn += r['fn']
        total_gold += r['gold_count']
        total_result += r['result_count']

    macro_p = sum(r['precision'] for r in results) / len(results)
    macro_r = sum(r['recall'] for r in results) / len(results)
    macro_f1 = sum(r['f1'] for r in results) / len(results)
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0
    print("-" * 65)
    print(f"{'Macro avg':<15} {total_gold:>5} {total_result:>6} {total_tp:>4} {total_fp:>4} {total_fn:>4} {macro_p:>6.3f} {macro_r:>6.3f} {macro_f1:>6.3f}")
    print(f"{'Micro avg':<15} {'':>5} {'':>6} {'':>4} {'':>4} {'':>4} {micro_p:>6.3f} {micro_r:>6.3f} {micro_f1:>6.3f}")

    # FP/FN pattern aggregation
    print("\n--- AGGREGATE FP PATTERNS ---")

    all_fp_mention = 0
    all_fp_no_mention = 0
    all_fn_mention = 0
    all_fn_no_mention = 0

    fp_element_type_total = Counter()
    fn_element_type_total = Counter()

    for r in results:
        model = r['model']
        sents = r['sents']
        for eid, snum in r['fp_set']:
            etype = model.get(eid, {}).get('type', 'UNKNOWN')
            fp_element_type_total[etype] += 1
            if eid in model and find_component_mentions(sents.get(snum, ''), {eid: model[eid]}):
                all_fp_mention += 1
            else:
                all_fp_no_mention += 1

        for eid, snum in r['fn_set']:
            etype = model.get(eid, {}).get('type', 'UNKNOWN')
            fn_element_type_total[etype] += 1
            if eid in model and find_component_mentions(sents.get(snum, ''), {eid: model[eid]}):
                all_fn_mention += 1
            else:
                all_fn_no_mention += 1

    print(f"  FP by element type: {dict(fp_element_type_total)}")
    print(f"  FP name mentioned: {all_fp_mention}, not mentioned: {all_fp_no_mention}")
    print(f"\n  FN by element type: {dict(fn_element_type_total)}")
    print(f"  FN name mentioned: {all_fn_mention}, not mentioned: {all_fn_no_mention}")

    # Common FP patterns
    print("\n--- COMMON ERROR PATTERNS ---")

    # Pattern: Wrong element assigned to sentence (FP element + FN element on same sentence)
    print("\n  1. Wrong assignment (FP+FN on same sentence = confusion):")
    for r in results:
        model = r['model']
        fp_sents = defaultdict(set)
        fn_sents = defaultdict(set)
        for eid, snum in r['fp_set']:
            fp_sents[snum].add(eid)
        for eid, snum in r['fn_set']:
            fn_sents[snum].add(eid)

        confused_sents = set(fp_sents.keys()) & set(fn_sents.keys())
        if confused_sents:
            print(f"\n    {r['project']}:")
            for snum in sorted(confused_sents):
                fp_names = [model.get(e, {}).get('name', '?') for e in fp_sents[snum]]
                fn_names = [model.get(e, {}).get('name', '?') for e in fn_sents[snum]]
                print(f"      S{snum}: SWATTR assigned {fp_names} instead of {fn_names}")

    # Pattern: Over-linking (element gets too many sentences)
    print("\n  2. Over-linking (element linked to more sentences than gold):")
    for r in results:
        model = r['model']
        gold_by_elem = defaultdict(set)
        result_by_elem = defaultdict(set)
        for eid, snum in r['tp_set'] | r['fn_set']:
            gold_by_elem[eid].add(snum)
        for eid, snum in r['tp_set'] | r['fp_set']:
            result_by_elem[eid].add(snum)

        overlinked = []
        for eid in result_by_elem:
            if len(result_by_elem[eid]) > len(gold_by_elem.get(eid, set())) + 1:  # >1 extra
                overlinked.append((eid, len(result_by_elem[eid]), len(gold_by_elem.get(eid, set()))))

        if overlinked:
            print(f"\n    {r['project']}:")
            for eid, res_count, gold_count in overlinked:
                ename = model.get(eid, {}).get('name', '?')
                print(f"      {ename}: {res_count} result links vs {gold_count} gold links")

    # Pattern: Under-linking (element gets fewer sentences than gold)
    print("\n  3. Under-linking (element linked to fewer sentences than gold):")
    for r in results:
        model = r['model']
        gold_by_elem = defaultdict(set)
        result_by_elem = defaultdict(set)
        for eid, snum in r['tp_set'] | r['fn_set']:
            gold_by_elem[eid].add(snum)
        for eid, snum in r['tp_set'] | r['fp_set']:
            result_by_elem[eid].add(snum)

        underlinked = []
        for eid in gold_by_elem:
            gold_count = len(gold_by_elem[eid])
            res_count = len(result_by_elem.get(eid, set()))
            if gold_count > res_count + 1:  # >1 missing
                underlinked.append((eid, res_count, gold_count))

        if underlinked:
            print(f"\n    {r['project']}:")
            for eid, res_count, gold_count in underlinked:
                ename = model.get(eid, {}).get('name', '?')
                print(f"      {ename}: {res_count} result links vs {gold_count} gold links (missing {gold_count - res_count})")


def main():
    all_results = []
    for project_name, config in PROJECTS.items():
        result = analyze_project(project_name, config)
        all_results.append(result)

    cross_project_analysis(all_results)


if __name__ == '__main__':
    main()
