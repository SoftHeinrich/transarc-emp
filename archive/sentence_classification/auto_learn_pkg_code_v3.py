#!/usr/bin/env python3
"""
Generalizable pkg_code detection v3: regex preprocessing → pattern clustering → LLM.

Approach:
  1. Preprocess: identify internal-punctuation types in tokens (dot, hyphen, etc.)
  2. For each punct type, check: does it cluster at sentence-initial position?
     (A token with internal dots at sentence START is anomalous in English)
  3. Cluster = bimodal position distribution → use as seeds
  4. LLM learns concept from seeds → classifies remaining sentences

The regex patterns (dot, camelCase, etc.) are general preprocessing —
they exist in ANY software documentation. The LEARNING is which
patterns indicate a distinct sentence category.
"""

import json
import os
import re
import subprocess
import hashlib
from collections import Counter

DATA_DIR = "/mnt/hostshare/ardoco-home/transarc-emp/sentence_classification"
BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
CACHE_DIR = os.path.join(DATA_DIR, "llm_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

PROJECTS = {
    "mediastore": "text_2016/mediastore.txt",
    "teastore":   "text_2020/teastore.txt",
    "teammates":  "text_2021/teammates.txt",
    "jabref":     "text_2021/jabref.txt",
    "bigbluebutton": "text_2021/bigbluebutton.txt",
}


def load_sentences(project):
    path = os.path.join(BENCHMARK, project, PROJECTS[project])
    sents = {}
    with open(path) as f:
        for i, line in enumerate(f, 1):
            sents[i] = line.strip()
    return sents


def load_gold():
    with open(os.path.join(DATA_DIR, "annotated_sentences.json")) as f:
        rows = json.load(f)
    return {(r['project'], r['sentence_num']): r['label'] for r in rows}


def call_sonnet(prompt, cache_key=None, max_retries=3):
    if cache_key:
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.txt")
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return f.read()
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["claude", "--print", "--model", "sonnet"],
                input=prompt, capture_output=True, text=True, timeout=180,
                env={**os.environ, "CLAUDECODE": ""},
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                if cache_key:
                    with open(cache_path, 'w') as f:
                        f.write(text)
                return text
        except subprocess.TimeoutExpired:
            print(f"    Timeout on attempt {attempt+1}")
    return ""


# ============================================================================
# PHASE 1: Regex Preprocessing — General Token Pattern Extraction
# ============================================================================

# General token patterns that exist in any software documentation.
# These are not domain-specific — they detect syntactic features.
TOKEN_PATTERNS = {
    'dot':      lambda t: '.' in t.strip('.,;:!?()'),          # internal dot: a.b
    'camel':    lambda t: bool(re.search(r'[a-z][A-Z]', t)),   # camelCase
    'hyphen':   lambda t: '-' in t.strip('-'),                   # internal hyphen: a-b
    'slash':    lambda t: '/' in t,                              # internal slash: a/b
    'colon':    lambda t: '::' in t,                             # C++ namespace: a::b
    'under':    lambda t: '_' in t,                              # snake_case
    'allcaps':  lambda t: len(t) >= 2 and t.isupper(),          # ACRONYM
    'mixed':    lambda t: bool(re.match(r'[A-Z][a-z]+[A-Z]', t)),  # PascalCase multi
}


def extract_token_features(text):
    """Extract which patterns each token matches."""
    tokens = text.split()
    features = []
    for i, tok in enumerate(tokens):
        tok_clean = tok.strip('.,;:!?()"\'[]{}')
        if not tok_clean:
            continue
        matched = set()
        for name, fn in TOKEN_PATTERNS.items():
            if fn(tok_clean):
                matched.add(name)
        features.append({
            'pos': i,
            'token': tok_clean,
            'patterns': matched,
            'is_first': i == 0,
            'starts_lower': tok_clean[0].islower() if tok_clean else False,
        })
    return features


# ============================================================================
# PHASE 1b: Per-Project Pattern Clustering
# ============================================================================

def discover_anomalous_patterns(sents):
    """For each token pattern, check if it creates a sentence-initial cluster.

    A pattern is "anomalous at start" if:
    - It appears at sentence position 0 in some sentences
    - Those sentences form a distinct group (many sentences start this way)
    - Starting with this pattern is unusual in English (lowercase start)

    Returns: dict of pattern_name → set of sentence numbers
    """
    # For each pattern: which sentences have it at position 0?
    pattern_at_start = {name: set() for name in TOKEN_PATTERNS}
    # Also: which sentences have it at position 0 AND start lowercase?
    pattern_at_start_lower = {name: set() for name in TOKEN_PATTERNS}
    # And: count per sentence (for density-based detection)
    pattern_counts = {name: {} for name in TOKEN_PATTERNS}

    for snum, text in sents.items():
        features = extract_token_features(text)
        if not features:
            continue

        # Check first token
        first = features[0]
        for pat in first['patterns']:
            pattern_at_start[pat].add(snum)
            if first['starts_lower']:
                pattern_at_start_lower[pat].add(snum)

        # Count per sentence
        for pat_name in TOKEN_PATTERNS:
            count = sum(1 for f in features if pat_name in f['patterns'])
            if count > 0:
                pattern_counts[pat_name][snum] = count

    return pattern_at_start, pattern_at_start_lower, pattern_counts


def find_seed_pattern(sents, pat_at_start, pat_at_start_lower, pat_counts):
    """Find the best pattern that creates a bimodal cluster.

    Strategy:
    - For each pattern, count sentences where it appears at start + lowercase
    - The best pattern has the most such sentences while being < 20% of total
    - Also check: does high-density (3+ tokens) create a cluster?
    """
    n = len(sents)
    best_pattern = None
    best_seeds = set()
    best_score = 0

    for pat_name in TOKEN_PATTERNS:
        # Strategy A: sentence starts with lowercase + pattern
        # This is the STRONGEST signal: two anomalies combined
        # (lowercase sentence start + code-like first token)
        start_lower = pat_at_start_lower[pat_name]
        if len(start_lower) >= 5 and len(start_lower) / n < 0.25:
            score = len(start_lower) * 3  # high weight: dual anomaly
            if score > best_score:
                best_score = score
                best_pattern = f"{pat_name}_at_start_lower"
                best_seeds = start_lower

        # Strategy B: high density (3+ pattern tokens per sentence)
        # Weaker signal — needs larger cluster to be trusted
        high_density = {snum for snum, count in pat_counts[pat_name].items()
                        if count >= 3}
        if len(high_density) >= 5 and len(high_density) / n < 0.10:
            combined = start_lower | high_density
            score = len(combined)
            if score > best_score:
                best_score = score
                best_pattern = f"{pat_name}_combined"
                best_seeds = combined

    return best_pattern, best_seeds


# ============================================================================
# PHASE 2: Template Discovery (co-occurrence with seeds)
# ============================================================================

def discover_templates(sents, seeds):
    """Find repeated sentence prefixes that co-occur with seeds."""
    snums = sorted(sents.keys())
    prefix_counts = Counter()
    prefix_sents = {}

    for snum in snums:
        words = sents[snum].split()
        for n in (2, 3):
            if len(words) >= n:
                prefix = ' '.join(words[:n])
                prefix_counts[prefix] += 1
                prefix_sents.setdefault(prefix, []).append(snum)

    templates = set()
    for prefix, count in prefix_counts.items():
        if count < 3:
            continue
        snum_list = prefix_sents[prefix]
        followers = sum(1 for snum in snum_list
                       if any((snum + off) in seeds for off in range(1, 4)))
        if followers >= count * 0.5:
            for snum in snum_list:
                templates.add(snum)

    return templates


# ============================================================================
# PHASE 3: LLM Concept Learning + Classification
# ============================================================================

def llm_learn_and_classify(project, sentences, seed_snums):
    seed_texts = [f"  S{s}: {sentences[s]}" for s in sorted(seed_snums)]

    nearby = []
    for snum in sorted(seed_snums):
        for offset in (-2, -1, 1, 2):
            n = snum + offset
            if n in sentences and n not in seed_snums:
                nearby.append(f"  S{n}: {sentences[n]}")
    nearby = list(dict.fromkeys(nearby))[:15]

    learn_prompt = f"""I detected syntactically unusual sentences in a software architecture document.
These "seed" sentences were flagged because they contain tokens with unusual character patterns
(like internal dots, special identifiers, or uncommon token structures) at prominent positions.

Seed sentences:
{chr(10).join(seed_texts[:20])}

Neighboring non-seed sentences for contrast:
{chr(10).join(nearby)}

In 2-3 sentences: What concept do these seeds share? What PURPOSE do they serve?"""

    concept_key = hashlib.md5(f"v3_concept_{project}_{len(seed_snums)}".encode()).hexdigest()[:16]
    concept = call_sonnet(learn_prompt, concept_key)

    sent_list = [f"S{s}: {sentences[s]}" for s in sorted(sentences.keys())]

    classify_prompt = f"""Classify sentences in a software architecture document.

Discovered concept:
{concept}

Example sentences (seeds):
{chr(10).join(seed_texts[:20])}

Include sentences serving the SAME PURPOSE as seeds, even with different syntax
(pronouns, mid-sentence references, headers for seed-like content).
Be CONSERVATIVE: exclude sentences that merely mention similar words in different context.

SENTENCES:
{chr(10).join(sent_list)}

Return ONLY a JSON array of sentence numbers: [1, 2, 3, ...]"""

    classify_key = hashlib.md5(f"v3_classify_{project}_{len(seed_snums)}".encode()).hexdigest()[:16]
    response = call_sonnet(classify_prompt, classify_key)

    classified = []
    try:
        match = re.search(r'\[[\d,\s]+\]', response)
        if match:
            classified = json.loads(match.group())
    except (json.JSONDecodeError, ValueError):
        pass

    return concept, classified


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate(predicted, gold_pkg):
    tp = predicted & gold_pkg
    fp = predicted - gold_pkg
    fn = gold_pkg - predicted
    p = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    r = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
    return {'tp': len(tp), 'fp': len(fp), 'fn': len(fn), 'p': p, 'r': r, 'f1': f1,
            'tp_set': tp, 'fp_set': fp, 'fn_set': fn}


# ============================================================================
# MAIN
# ============================================================================

def main():
    gold = load_gold()
    gold_pkg = {k for k, v in gold.items() if v == 'pkg_code'}

    print("=" * 90)
    print("AUTO-LEARN v3: Regex Preprocessing → Pattern Clustering → LLM")
    print("=" * 90)

    all_predicted = set()

    for project in PROJECTS:
        sents = load_sentences(project)
        proj_gold = {snum for (p, snum) in gold_pkg if p == project}

        print(f"\n{'='*90}")
        print(f"PROJECT: {project} ({len(sents)} sentences, {len(proj_gold)} gold)")
        print(f"{'='*90}")

        # Phase 1: Extract patterns
        pat_at_start, pat_at_start_lower, pat_counts = discover_anomalous_patterns(sents)

        print("\n  Token pattern distribution:")
        for pat_name in TOKEN_PATTERNS:
            n_any = len(pat_counts[pat_name])
            n_start = len(pat_at_start[pat_name])
            n_start_lower = len(pat_at_start_lower[pat_name])
            n_high = sum(1 for c in pat_counts[pat_name].values() if c >= 3)
            if n_any > 0:
                print(f"    {pat_name:10s}: {n_any:3d} sentences, "
                      f"{n_start:2d} at start, "
                      f"{n_start_lower:2d} at start+lowercase, "
                      f"{n_high:2d} high-density(3+)")

        # Find best seed pattern
        best_pat, seeds = find_seed_pattern(sents, pat_at_start, pat_at_start_lower, pat_counts)

        if not seeds:
            print(f"\n  No anomalous pattern cluster found → skip")
            continue

        # Template discovery
        templates = discover_templates(sents, seeds)
        seeds = seeds | templates

        print(f"\n  Best pattern: {best_pat}")
        print(f"  Seeds: {len(seeds)} (+ {len(templates)} from templates)")

        # Show seeds
        for snum in sorted(seeds)[:10]:
            print(f"    S{snum}: {sents[snum][:80]}")
        if len(seeds) > 10:
            print(f"    ... and {len(seeds)-10} more")

        # Phase 1 eval
        phase1_pred = {(project, snum) for snum in seeds}
        p1 = evaluate(phase1_pred, gold_pkg)
        print(f"\n  Phase 1+templates: TP={p1['tp']}, FP={p1['fp']}, "
              f"FN={len(proj_gold) - p1['tp']}")

        # Phase 2+3: LLM
        print(f"\n  Phase 2+3: LLM concept learning + classification...")
        concept, classified = llm_learn_and_classify(project, sents, seeds)
        print(f"    Concept: {concept[:120]}...")
        print(f"    LLM classified: {len(classified)} sentences")

        final = seeds | set(classified)
        for snum in sorted(final):
            all_predicted.add((project, snum))

        # Per-project eval
        proj_pred = {(project, snum) for snum in final}
        proj_res = evaluate(proj_pred, gold_pkg)
        print(f"\n  Final: TP={proj_res['tp']}, FP={proj_res['fp']}, FN={proj_res['fn']}, "
              f"P={proj_res['p']:.3f}, R={proj_res['r']:.3f}, F1={proj_res['f1']:.3f}")

        if proj_res['fp'] > 0:
            for key in sorted(proj_res['fp_set']):
                label = gold.get(key, '?')
                print(f"    FP: S{key[1]} ({label}): {sents[key[1]][:80]}")
        if proj_res['fn'] > 0:
            for key in sorted(proj_res['fn_set'], key=lambda x: x[1]):
                if key[1] in sents:
                    print(f"    FN: S{key[1]}: {sents[key[1]][:80]}")

    # Overall
    print(f"\n{'='*90}")
    print("OVERALL RESULTS")
    print(f"{'='*90}")

    result = evaluate(all_predicted, gold_pkg)
    print(f"\n  TP={result['tp']}, FP={result['fp']}, FN={result['fn']}")
    print(f"  P={result['p']:.3f}, R={result['r']:.3f}, F1={result['f1']:.3f}")

    if result['fp'] > 0:
        print(f"\n  FPs:")
        for key in sorted(result['fp_set']):
            label = gold.get(key, '?')
            all_s = load_sentences(key[0])
            print(f"    [{key[0]}] S{key[1]} ({label}): {all_s[key[1]][:80]}")
    if result['fn'] > 0:
        print(f"\n  FNs:")
        for key in sorted(result['fn_set'], key=lambda x: x[1]):
            all_s = load_sentences(key[0])
            print(f"    [{key[0]}] S{key[1]}: {all_s[key[1]][:80]}")

    print(f"\n{'='*90}")
    print("COMPARISON")
    print(f"{'='*90}")
    print(f"""
  Approach                              P      R      F1
  ─────────────────────────────────────────────────────────
  Rule V2 (8 manual regexes)         1.000  1.000  1.000
  Auto-discover (engineered features)1.000  0.949  0.974
  LLM zero-shot                      0.971  0.872  0.919
  LLM meta-learning                  0.949  0.949  0.949
  v1: Engineered seeds + LLM         1.000  0.949  0.974
  ─────────────────────────────────────────────────────────
  v3: Regex preprocess + learn + LLM {result['p']:.3f}  {result['r']:.3f}  {result['f1']:.3f}

  Preprocessing: general regex patterns (dot, camel, hyphen, etc.)
  Learning: which pattern + position creates a bimodal cluster
  Generalization: LLM learns concept from discovered seeds
""")


if __name__ == '__main__':
    main()
