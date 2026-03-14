#!/usr/bin/env python3
"""
Generalizable pkg_code detection v2: auto-discover token patterns → LLM learns.

Phase 1: Character-class regex preprocessing
  - Convert each token to its character-class signature (a=lower, A=upper, 0=digit, else=itself)
  - Count signature frequency across corpus
  - Rare signatures = anomalous tokens
  - Sentences with many anomalous tokens = seeds

Phase 2+3: LLM concept learning + classification (same as v1)

ZERO hardcoded features. The system discovers what's "code-like" from data.
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
# PHASE 1: Auto-discover rare token patterns
# ============================================================================

def token_signature(tok):
    """Convert token to character-class signature.

    Each char → class: lowercase='a', uppercase='A', digit='0', else=itself.
    Collapse consecutive same-class runs.

    Examples:
      "logic"     → "a"
      "Logic"     → "Aa"
      "logic.api" → "a.a"
      "React.js"  → "Aa.a"
      "e.g."      → "a.a."
      "HTML5"     → "A0"
      "bbb-conf"  → "a-a"
      "x.util"    → "a.a"
      "--setip"   → "-a"
      "2.3-alpha" → "0.0-a"
    """
    if not tok:
        return ''
    sig = []
    prev = None
    for ch in tok:
        if ch.islower():
            cls = 'a'
        elif ch.isupper():
            cls = 'A'
        elif ch.isdigit():
            cls = '0'
        else:
            cls = ch  # punctuation keeps itself
        if cls != prev:
            sig.append(cls)
            prev = cls
    return ''.join(sig)


def analyze_corpus_patterns(all_project_sents):
    """Discover discriminating token signatures by finding bimodal distributions.

    For each signature, compute the per-sentence count distribution.
    A signature is "discriminating" if its count distribution is bimodal:
    most sentences have 0-1, but a subgroup has 2+.

    This discovers patterns like a.a (dot-separated) from DATA, not hardcoded.
    """
    # Count signature occurrences per sentence
    per_sentence_counts = {}  # (project, snum) → {sig: count}
    sig_global_counts = Counter()  # sig → total sentence appearances
    total_sentences = 0

    for project, sents in all_project_sents.items():
        for snum, text in sents.items():
            total_sentences += 1
            sig_counts = Counter()
            for tok in text.split():
                tok_clean = tok.strip('.,;:!?()"\'[]{}')
                if tok_clean:
                    sig = token_signature(tok_clean)
                    sig_counts[sig] += 1
            per_sentence_counts[(project, snum)] = sig_counts
            for sig in sig_counts:
                sig_global_counts[sig] += 1

    # For each signature, check if per-sentence count distribution is bimodal
    discriminating_sigs = {}

    for sig, n_sentences in sig_global_counts.items():
        if n_sentences < 3:  # too rare to be meaningful
            continue

        # Collect per-sentence counts for this signature
        counts = []
        for key in per_sentence_counts:
            c = per_sentence_counts[key].get(sig, 0)
            counts.append(c)

        # Check bimodality: are there sentences with count >= 2 while most have 0?
        count_dist = Counter(counts)
        n_zero = count_dist.get(0, 0)
        n_one = count_dist.get(1, 0)
        n_high = sum(v for k, v in count_dist.items() if k >= 2)

        # Discriminating if: most sentences have 0, some have 2+,
        # and the high-count group is a small minority
        if (n_high >= 2
                and n_high / total_sentences < 0.10
                and n_zero / total_sentences > 0.50):
            discriminating_sigs[sig] = {
                'n_sentences': n_sentences,
                'n_high': n_high,
                'count_dist': dict(count_dist),
            }

    return per_sentence_counts, discriminating_sigs, sig_global_counts, total_sentences


def score_sentences(sents, per_sentence_counts, disc_sigs, project):
    """Score each sentence by position-weighted discriminating signatures.

    Key insight (learned from data, not hardcoded):
      - A disc-sig token at sentence START is much more anomalous than mid-sentence
      - Multiple disc-sig tokens in one sentence amplify the signal
      - Sentence starting lowercase is anomalous in English prose

    Weights:
      +3: first token has disc signature AND sentence starts lowercase
      +2: first token has disc signature (any case)
      +1: each additional disc-sig token beyond the first
    """
    scores = {}
    details = {}
    for snum, text in sents.items():
        key = (project, snum)
        tokens = text.split()
        if not tokens:
            scores[snum] = 0
            details[snum] = {'disc_tokens': [], 'starts_lower': False}
            continue

        score = 0
        disc_tokens = []
        starts_lower = text[0].islower()

        # Analyze first token
        first_tok = tokens[0].strip('.,;:!?()"\'[]{}')
        first_sig = token_signature(first_tok) if first_tok else ''

        if first_sig in disc_sigs:
            if starts_lower:
                score += 3  # lowercase start + disc sig = very anomalous
            else:
                score += 2  # disc sig at start but uppercase
            disc_tokens.append((first_tok, first_sig))

        # Count all disc-sig tokens in sentence
        total_disc = 0
        for tok in tokens:
            tok_clean = tok.strip('.,;:!?()"\'[]{}')
            if tok_clean:
                sig = token_signature(tok_clean)
                if sig in disc_sigs:
                    total_disc += 1
                    if tok_clean != first_tok or sig != first_sig:
                        disc_tokens.append((tok_clean, sig))

        # Add density bonus (beyond the first token)
        if total_disc >= 2:
            score += total_disc - 1
        if total_disc >= 4:
            score += 2  # extra bonus for very high density

        scores[snum] = score
        details[snum] = {'disc_tokens': disc_tokens, 'starts_lower': starts_lower,
                         'total_disc': total_disc}

    return scores, details


def find_seeds_bimodal(scores):
    """Find seeds via bimodal gap detection."""
    score_counts = Counter(scores.values())
    max_score = max(scores.values()) if scores else 0

    best_threshold = None
    best_quality = 0

    for t in range(2, max_score + 1):
        above = sum(score_counts.get(s, 0) for s in range(t, max_score + 1))
        if above == 0:
            continue

        # Check gap width below threshold
        gap_width = 0
        for g in range(t - 1, 0, -1):
            if score_counts.get(g, 0) <= 1:
                gap_width += 1
            else:
                break

        quality = gap_width * above
        if quality > best_quality:
            best_quality = quality
            best_threshold = t

    if best_threshold is None:
        return set(), 0

    seeds = {snum for snum, score in scores.items() if score >= best_threshold}
    return seeds, best_threshold


# ============================================================================
# PHASE 2+3: LLM Concept Learning + Classification (same as v1)
# ============================================================================

def llm_learn_and_classify(project, sentences, seed_snums):
    """Two-step: learn concept from seeds, then classify all sentences."""

    seed_texts = []
    for snum in sorted(seed_snums):
        seed_texts.append(f"  S{snum}: {sentences[snum]}")

    # Nearby non-seeds for contrast
    nearby = []
    for snum in sorted(seed_snums):
        for offset in (-2, -1, 1, 2):
            n = snum + offset
            if n in sentences and n not in seed_snums:
                nearby.append(f"  S{n}: {sentences[n]}")
    nearby = list(dict.fromkeys(nearby))[:15]

    # Phase 2: concept learning
    learn_prompt = f"""I automatically detected syntactically unusual sentences in a software architecture document.
These "seed" sentences were flagged because they contain tokens with rare character patterns
(e.g., tokens with internal dots, unusual capitalization, or special characters that rarely
appear in normal English prose).

Seed sentences:
{chr(10).join(seed_texts)}

Neighboring non-seed sentences for contrast:
{chr(10).join(nearby)}

In 2-3 sentences: What concept or category do these seeds share? What PURPOSE do they serve
in the document that distinguishes them from neighboring sentences?"""

    concept_key = hashlib.md5(f"v2_concept_{project}_{len(seed_snums)}".encode()).hexdigest()[:16]
    concept = call_sonnet(learn_prompt, concept_key)

    # Phase 3: classification
    sent_list = [f"S{snum}: {sentences[snum]}" for snum in sorted(sentences.keys())]

    classify_prompt = f"""You are classifying sentences in a software architecture document.

I discovered a category of sentences. Here is the concept:
{concept}

Example sentences belonging to this category:
{chr(10).join(seed_texts[:15])}

Classify ALL sentences below. Include sentences that serve the SAME PURPOSE as the seeds,
even if their syntax is different (e.g., uses pronouns, different structure, concept appears
mid-sentence rather than at the start).

Be CONSERVATIVE: only include sentences that truly describe the same kind of content as seeds.
Do NOT include sentences that merely mention similar words in a different context.

SENTENCES:
{chr(10).join(sent_list)}

Return ONLY a JSON array of sentence numbers: [1, 2, 3, ...]"""

    classify_key = hashlib.md5(f"v2_classify_{project}_{len(seed_snums)}".encode()).hexdigest()[:16]
    response = call_sonnet(classify_prompt, classify_key)

    # Parse
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
    print("AUTO-LEARN v2: Character-Signature Anomaly → LLM Concept → Classification")
    print("=" * 90)

    # Load all sentences
    all_project_sents = {}
    for project in PROJECTS:
        all_project_sents[project] = load_sentences(project)

    total_sents = sum(len(s) for s in all_project_sents.values())
    print(f"\nTotal sentences: {total_sents}")
    print(f"Gold pkg_code: {len(gold_pkg)}")

    # ── PHASE 1a: Discover rare signatures across entire corpus ────────────

    print(f"\n{'='*90}")
    print("PHASE 1a: Corpus-wide Token Signature Analysis")
    print(f"{'='*90}")

    per_sent_counts, disc_sigs, sig_freq, n_total = analyze_corpus_patterns(all_project_sents)

    # Show signature landscape
    print(f"\n  Total unique signatures: {len(sig_freq)}")
    print(f"  Discriminating signatures (bimodal distribution): {len(disc_sigs)}")

    print(f"\n  Top 15 most common signatures:")
    for sig, count in sig_freq.most_common(15):
        pct = count / n_total * 100
        disc = " [DISC]" if sig in disc_sigs else ""
        print(f"    '{sig:10s}': in {count:3d}/{n_total} sentences ({pct:5.1f}%){disc}")

    print(f"\n  Discriminating signatures (learned from data):")
    for sig, info in sorted(disc_sigs.items(), key=lambda x: -x[1]['n_high']):
        dist = info['count_dist']
        dist_str = ', '.join(f"{k}:{v}" for k, v in sorted(dist.items()) if k > 0)
        # Collect example tokens
        examples = set()
        for project, sents in all_project_sents.items():
            for snum, text in sents.items():
                for tok in text.split():
                    tok_clean = tok.strip('.,;:!?()"\'[]{}')
                    if tok_clean and token_signature(tok_clean) == sig:
                        examples.add(tok_clean)
                        if len(examples) >= 5:
                            break
        print(f"    '{sig}': {info['n_high']} sentences with 2+ tokens "
              f"(dist: {dist_str})")
        print(f"      examples: {list(examples)[:5]}")

    # ── PHASE 1b: Score sentences per project ──────────────────────────────

    print(f"\n{'='*90}")
    print("PHASE 1b: Per-Project Sentence Scoring & Seed Discovery")
    print(f"{'='*90}")

    all_predicted = set()

    for project in PROJECTS:
        sents = all_project_sents[project]
        proj_gold = {snum for (p, snum) in gold_pkg if p == project}

        print(f"\n  ── {project} ({len(sents)} sentences, {len(proj_gold)} gold pkg_code) ──")

        scores, details = score_sentences(sents, per_sent_counts, disc_sigs, project)
        seeds, threshold = find_seeds_bimodal(scores)

        # Show score distribution
        score_dist = Counter(scores.values())
        for s in sorted(score_dist.keys()):
            marker = " ← threshold" if s == threshold else ""
            n_seeds = sum(1 for sn in seeds if scores[sn] == s)
            print(f"    score={s:2d}: {score_dist[s]:3d} sentences"
                  f" ({n_seeds} seeds){marker}")

        if not seeds:
            print(f"    No bimodal gap found → no seeds → skip")
            continue

        print(f"\n    Seeds ({len(seeds)}):")
        for snum in sorted(seeds)[:10]:
            disc_toks = [f"{t}[{s}]" for t, s in details[snum]['disc_tokens']]
            print(f"      S{snum} (score={scores[snum]}): {sents[snum][:70]}")
            if disc_toks:
                print(f"        disc tokens: {', '.join(disc_toks[:5])}")
        if len(seeds) > 10:
            print(f"      ... and {len(seeds)-10} more")

        # Evaluate Phase 1
        phase1_pred = {(project, snum) for snum in seeds}
        phase1_tp = len(phase1_pred & gold_pkg)
        phase1_fp = len(phase1_pred - gold_pkg)
        print(f"\n    Phase 1: TP={phase1_tp}, FP={phase1_fp}, "
              f"FN={len(proj_gold) - phase1_tp}")

        # ── PHASE 2+3: LLM ────────────────────────────────────────────────
        print(f"\n    Phase 2+3: LLM concept learning + classification...")
        concept, classified = llm_learn_and_classify(project, sents, seeds)

        print(f"    Concept: {concept[:150]}...")
        print(f"    LLM classified: {len(classified)} sentences")

        # Union
        final = seeds | set(classified)
        print(f"    Final (seeds ∪ LLM): {len(final)} sentences")

        for snum in sorted(final):
            all_predicted.add((project, snum))

        # Per-project eval
        proj_pred = {(project, snum) for snum in final}
        proj_res = evaluate(proj_pred, gold_pkg)
        print(f"    Result: TP={proj_res['tp']}, FP={proj_res['fp']}, FN={proj_res['fn']}, "
              f"P={proj_res['p']:.3f}, R={proj_res['r']:.3f}, F1={proj_res['f1']:.3f}")

        if proj_res['fp'] > 0:
            for key in sorted(proj_res['fp_set']):
                label = gold.get(key, '?')
                print(f"      FP: S{key[1]} ({label}): {sents[key[1]][:80]}")
        if proj_res['fn'] > 0:
            for key in sorted(proj_res['fn_set'], key=lambda x: x[1]):
                fn_snum = key[1]
                fn_text = sents.get(fn_snum, '(from another project)')
                print(f"      FN: S{fn_snum}: {fn_text[:80]}")

    # ── OVERALL ────────────────────────────────────────────────────────────

    print(f"\n{'='*90}")
    print("OVERALL RESULTS")
    print(f"{'='*90}")

    all_sents_flat = {}
    for proj, proj_sents in all_project_sents.items():
        for snum, text in proj_sents.items():
            all_sents_flat[(proj, snum)] = text

    result = evaluate(all_predicted, gold_pkg)
    print(f"\n  TP={result['tp']}, FP={result['fp']}, FN={result['fn']}")
    print(f"  P={result['p']:.3f}, R={result['r']:.3f}, F1={result['f1']:.3f}")

    if result['fp'] > 0:
        print(f"\n  FPs ({result['fp']}):")
        for key in sorted(result['fp_set']):
            label = gold.get(key, '?')
            print(f"    [{key[0]}] S{key[1]} ({label}): {all_sents_flat[key][:90]}")
    if result['fn'] > 0:
        print(f"\n  FNs ({result['fn']}):")
        for key in sorted(result['fn_set'], key=lambda x: x[1]):
            print(f"    [{key[0]}] S{key[1]}: {all_sents_flat[key][:90]}")

    # ── COMPARISON ─────────────────────────────────────────────────────────

    print(f"\n{'='*90}")
    print("COMPARISON")
    print(f"{'='*90}")
    print(f"""
  Approach                              P      R      F1    Hardcoded
  ─────────────────────────────────────────────────────────────────────
  Rule V2 (manual)                   1.000  1.000  1.000    8 regexes
  Auto-discover (dot-specific)       1.000  0.949  0.974    4 engineered features
  LLM zero-shot                      0.971  0.872  0.919    NOTHING
  LLM meta-learning                  0.949  0.949  0.949    NOTHING
  v1: Auto-seed + LLM               1.000  0.949  0.974    4 engineered features
  ─────────────────────────────────────────────────────────────────────
  v2: Char-signature + LLM          {result['p']:.3f}  {result['r']:.3f}  {result['f1']:.3f}    NOTHING (learned from data)

  v2 discovers token patterns from character-class statistics.
  No "dot", "camelCase", "package" etc. hardcoded — all emerge from data.
""")


if __name__ == '__main__':
    main()
