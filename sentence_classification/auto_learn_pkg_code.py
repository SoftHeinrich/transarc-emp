#!/usr/bin/env python3
"""
Generalizable pkg_code detection: auto-discover seeds → LLM learns concept → LLM generalizes.

Pipeline:
  Phase 1: Zero-knowledge syntactic anomaly detection (finds seeds automatically)
  Phase 2: LLM reads seeds, infers the underlying concept
  Phase 3: LLM classifies ALL sentences using the learned concept

This is generalizable because:
  - Phase 1 works on any text (finds syntactically unusual sentences)
  - Phase 2/3 uses LLM understanding to go beyond surface patterns
  - No hardcoded "package", "contains", dot-regex, or Java knowledge
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
# PHASE 1: Zero-Knowledge Anomaly Detection (generalizable)
# ============================================================================

def detect_anomalies(sentences):
    """Find syntactically anomalous sentences using general text statistics.

    General anomaly signals (not Java-specific):
    - Sentence starts with lowercase (unusual in English prose)
    - First token contains non-alphabetic chars (dots, colons, slashes)
    - Sentence has unusually high density of non-word characters
    - Sentence has tokens with unusual character patterns
    """
    anomaly_scores = {}

    # Compute corpus-level statistics for calibration
    all_first_chars = []
    all_token_patterns = Counter()

    for snum, text in sentences.items():
        tokens = text.split()
        if not tokens:
            continue
        first_tok = tokens[0].rstrip('.,;:!?()')
        all_first_chars.append(first_tok[0] if first_tok else ' ')

        # Classify each token by its character pattern
        for tok in tokens:
            tok_clean = tok.strip('.,;:!?()"\'[]{}')
            if not tok_clean:
                continue
            pattern = classify_token(tok_clean)
            all_token_patterns[pattern] += 1

    # What fraction of sentences start with lowercase?
    total = len(all_first_chars)
    lower_frac = sum(1 for c in all_first_chars if c.islower()) / total

    # Compute per-sentence anomaly score
    for snum, text in sentences.items():
        tokens = text.split()
        if not tokens:
            anomaly_scores[snum] = 0
            continue

        score = 0
        first_tok = tokens[0].rstrip('.,;:!?()')

        # Signal 1: starts with lowercase
        if first_tok and first_tok[0].islower():
            score += 1

        # Signal 2: first token has internal punctuation (dots, colons, etc.)
        if first_tok and has_internal_punct(first_tok):
            score += 2

        # Signal 3: count tokens with unusual patterns (code-like)
        code_tokens = 0
        for tok in tokens:
            tok_clean = tok.strip('.,;:!?()"\'[]{}')
            if tok_clean and classify_token(tok_clean) == 'code_like':
                code_tokens += 1
        if code_tokens >= 1:
            score += 1
        if code_tokens >= 3:
            score += 2

        # Signal 4: sentence is short and dominated by code-like tokens
        if len(tokens) <= 12 and code_tokens >= len(tokens) * 0.3:
            score += 1

        anomaly_scores[snum] = score

    return anomaly_scores


def classify_token(tok):
    """Classify a token by character pattern — general, not Java-specific."""
    if not tok:
        return 'empty'
    # Pure word (letters only, or letters + apostrophe)
    if re.match(r"^[a-zA-Z]+'?[a-zA-Z]*$", tok):
        return 'word'
    # Number
    if re.match(r'^[\d,.]+$', tok):
        return 'number'
    # Mixed alphanumeric with internal punctuation (code-like)
    if re.search(r'[a-zA-Z]', tok) and re.search(r'[^a-zA-Z\s]', tok):
        # Has both letters and non-letter chars
        if re.search(r'[.:/\\]', tok):  # separator chars common in code
            return 'code_like'
        if tok[0].islower() and re.search(r'[A-Z]', tok[1:]):  # camelCase
            return 'code_like'
    return 'other'


def has_internal_punct(tok):
    """Check if token has internal punctuation (not just trailing)."""
    clean = tok.rstrip('.,;:!?()')
    # Internal dot, colon, slash, backslash
    return bool(re.search(r'[.:/\\]', clean[1:] if len(clean) > 1 else ''))


def find_seeds(anomaly_scores, threshold=None):
    """Find seeds by gap detection in anomaly score distribution.

    Key insight: require CONVERGENCE of multiple anomaly signals.
    A single signal (score=1) is noise (e.g., "e.g." or "React.js").
    Multiple signals (score>=3) mean the sentence is genuinely anomalous.

    We also look for a GAP in the distribution — bimodality indicates
    a real subpopulation, while unimodal means no real anomalies.
    """
    score_counts = Counter(anomaly_scores.values())
    max_score = max(anomaly_scores.values()) if anomaly_scores else 0

    if threshold is None:
        # Strategy: find bimodal gap
        # Scan from score=2 upward, find first gap (count=0 or very small)
        # followed by a cluster above

        best_threshold = None
        best_gap_quality = 0

        for t in range(2, max_score + 1):
            above = sum(score_counts.get(s, 0) for s in range(t, max_score + 1))
            if above == 0:
                continue

            # Check for gap: how empty is the range just below threshold?
            gap_width = 0
            for g in range(t - 1, 0, -1):
                if score_counts.get(g, 0) <= 1:
                    gap_width += 1
                else:
                    break

            # Quality = gap_width * seed_count / total
            # Prefer wide gaps with meaningful seed clusters
            total = sum(score_counts.values())
            quality = gap_width * above

            if quality > best_gap_quality:
                best_gap_quality = quality
                best_threshold = t

        threshold = best_threshold

    if threshold is None:
        # No clear bimodal structure → no confident seeds
        return set(), 0

    seeds = {snum for snum, score in anomaly_scores.items() if score >= threshold}
    return seeds, threshold


# ============================================================================
# PHASE 2: LLM Concept Learning from Seeds
# ============================================================================

def llm_learn_concept(project, sentences, seed_snums):
    """Show seeds to LLM, ask it to infer the underlying concept."""

    seed_texts = []
    non_seed_texts = []
    for snum in sorted(sentences.keys()):
        if snum in seed_snums:
            seed_texts.append(f"  [SEED] S{snum}: {sentences[snum]}")
        else:
            non_seed_texts.append(f"  S{snum}: {sentences[snum]}")

    # Sample some non-seeds for contrast (nearby for context)
    nearby_non_seeds = []
    for snum in seed_snums:
        for offset in (-2, -1, 1, 2):
            neighbor = snum + offset
            if neighbor in sentences and neighbor not in seed_snums:
                nearby_non_seeds.append(f"  [NON-SEED] S{neighbor}: {sentences[neighbor]}")

    # Deduplicate
    nearby_non_seeds = list(dict.fromkeys(nearby_non_seeds))[:20]

    prompt = f"""I automatically detected some syntactically unusual sentences in a software architecture document.
These "seed" sentences were flagged because they have unusual character patterns (e.g., starting with lowercase,
containing tokens with internal punctuation like dots/colons/slashes).

Here are the seed sentences:
{chr(10).join(seed_texts)}

Here are some neighboring non-seed sentences for contrast:
{chr(10).join(nearby_non_seeds)}

Analyze these seeds and answer:
1. What CONCEPT or CATEGORY do these seed sentences share? (Describe in 1-2 sentences)
2. What distinguishes them from the non-seed neighbors?
3. Are there likely OTHER sentences in the document that belong to the same category
   but were NOT detected because they lack the surface-level anomaly signals?
   (e.g., sentences that use pronouns to refer back, or describe the same topic in normal English syntax)

Be specific and concise. Focus on the PURPOSE of these sentences, not just their syntax."""

    cache_key = hashlib.md5(f"learn_concept_{project}_{sorted(seed_snums)}".encode()).hexdigest()[:16]
    return call_sonnet(prompt, cache_key)


# ============================================================================
# PHASE 3: LLM Classification Using Learned Concept
# ============================================================================

def llm_classify_with_concept(project, sentences, seed_snums, concept_description):
    """LLM classifies all sentences using the learned concept + seeds as examples."""

    seed_examples = []
    for snum in sorted(seed_snums):
        seed_examples.append(f"  S{snum}: {sentences[snum]}")

    # Build numbered sentence list
    sent_list = []
    for snum in sorted(sentences.keys()):
        sent_list.append(f"S{snum}: {sentences[snum]}")

    prompt = f"""You are classifying sentences in a software architecture document.

I automatically discovered a category of sentences. Here is what I learned about this category:

{concept_description}

Here are example sentences that belong to this category (automatically detected seeds):
{chr(10).join(seed_examples)}

Now classify ALL of the following sentences. A sentence belongs to this category if it serves
the same PURPOSE as the seeds — even if its syntax looks different (e.g., pronoun references,
different sentence structure, or the concept appears mid-sentence).

IMPORTANT: Be inclusive of sentences that serve the same purpose as the seeds, but conservative
about sentences that merely mention similar words in a different context.

SENTENCES:
{chr(10).join(sent_list)}

Return ONLY a JSON array of sentence numbers that belong to this category.
Example: [84, 85, 86, 130]

Return ONLY the JSON array, nothing else."""

    cache_key = hashlib.md5(f"classify_{project}_{sorted(seed_snums)}_v2".encode()).hexdigest()[:16]
    response = call_sonnet(prompt, cache_key)

    # Parse response
    try:
        # Find JSON array in response
        match = re.search(r'\[[\d,\s]+\]', response)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, ValueError):
        pass
    return []


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
    print("GENERALIZABLE pkg_code DETECTION: Auto-Discover → LLM Learn → LLM Classify")
    print("=" * 90)

    all_predicted = set()

    for project in PROJECTS:
        sentences = load_sentences(project)

        print(f"\n{'='*90}")
        print(f"PROJECT: {project} ({len(sentences)} sentences)")
        print(f"{'='*90}")

        # ── PHASE 1: Auto anomaly detection ───────────────────────────────
        print("\n  Phase 1: Anomaly detection...")
        scores = detect_anomalies(sentences)
        seeds, threshold = find_seeds(scores)

        print(f"    Threshold: {threshold}, Seeds found: {len(seeds)}")

        # Show score distribution
        score_dist = Counter(scores.values())
        for s in sorted(score_dist.keys()):
            marker = " ← threshold" if s == threshold else ""
            in_seed = sum(1 for sn in seeds if scores[sn] == s)
            print(f"      score={s}: {score_dist[s]:3d} sentences"
                  f" ({in_seed} seeds){marker}")

        if not seeds:
            print("    No seeds found → skip this project")
            continue

        # Show seeds
        print(f"\n    Seeds:")
        for snum in sorted(seeds):
            print(f"      S{snum} (score={scores[snum]}): {sentences[snum][:80]}")

        # Evaluate Phase 1 alone
        proj_gold = {snum for (p, s), v in gold.items()
                     if p == project and v == 'pkg_code' for snum in [s]}
        phase1_pred = {(project, snum) for snum in seeds}
        phase1_eval = evaluate(phase1_pred, gold_pkg)
        print(f"\n    Phase 1 result: TP={phase1_eval['tp']}, FP={phase1_eval['fp']}, "
              f"FN (within project)={len(proj_gold - {s for _, s in phase1_pred})}")

        # ── PHASE 2: LLM concept learning ─────────────────────────────────
        print("\n  Phase 2: LLM concept learning...")
        concept = llm_learn_concept(project, sentences, seeds)
        print(f"    Concept learned:")
        for line in concept.split('\n')[:10]:
            print(f"      {line}")

        # ── PHASE 3: LLM classification ───────────────────────────────────
        print("\n  Phase 3: LLM classification using learned concept...")
        classified = llm_classify_with_concept(project, sentences, seeds, concept)
        print(f"    LLM classified {len(classified)} sentences")

        # Union: seeds ∪ LLM (LLM may miss some seeds, seeds may have noise)
        # Strategy: trust seeds AND LLM
        final = set(classified) | seeds
        print(f"    Final (seeds ∪ LLM): {len(final)} sentences")

        for snum in sorted(final):
            proj_pred_key = (project, snum)
            all_predicted.add(proj_pred_key)

    # ── OVERALL EVALUATION ─────────────────────────────────────────────────

    print(f"\n{'='*90}")
    print("OVERALL RESULTS")
    print(f"{'='*90}")

    result = evaluate(all_predicted, gold_pkg)
    print(f"\n  TP={result['tp']}, FP={result['fp']}, FN={result['fn']}")
    print(f"  P={result['p']:.3f}, R={result['r']:.3f}, F1={result['f1']:.3f}")

    if result['fp'] > 0:
        print(f"\n  FPs ({result['fp']}):")
        all_sents = {}
        for proj in PROJECTS:
            for snum, text in load_sentences(proj).items():
                all_sents[(proj, snum)] = text
        for key in sorted(result['fp_set']):
            label = gold.get(key, '?')
            print(f"    [{key[0]}] S{key[1]} ({label}): {all_sents[key][:90]}")

    if result['fn'] > 0:
        print(f"\n  FNs ({result['fn']}):")
        all_sents = {}
        for proj in PROJECTS:
            for snum, text in load_sentences(proj).items():
                all_sents[(proj, snum)] = text
        for key in sorted(result['fn_set'], key=lambda x: x[1]):
            print(f"    [{key[0]}] S{key[1]}: {all_sents[key][:90]}")

    # ── COMPARISON ─────────────────────────────────────────────────────────

    print(f"\n{'='*90}")
    print("COMPARISON")
    print(f"{'='*90}")
    print(f"""
  Approach                              P      R      F1    Hardcoded
  ─────────────────────────────────────────────────────────────────────
  Rule V2 (manual)                   1.000  1.000  1.000    8 regexes
  Auto-discover only (prev script)   1.000  0.949  0.974    NOTHING (but Java-specific features)
  LLM zero-shot                      0.971  0.872  0.919    NOTHING
  LLM meta-learning                  0.949  0.949  0.949    NOTHING
  ─────────────────────────────────────────────────────────────────────
  This: Auto-seed → LLM learn        {result['p']:.3f}  {result['r']:.3f}  {result['f1']:.3f}    NOTHING (generalizable)

  Key difference: This pipeline is generalizable because:
  1. Phase 1 finds "unusual" sentences in ANY text (not just Java-dotted)
  2. Phase 2 asks LLM to understand WHY they're unusual (learns the concept)
  3. Phase 3 uses the concept to find sentences the syntax missed
""")


if __name__ == '__main__':
    main()
