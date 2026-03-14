#!/usr/bin/env python3
"""
LLM-based pkg_code detection using Claude Sonnet via CLI subprocess.

Approaches:
  1. Zero-shot: ask Sonnet to classify each sentence (no examples)
  2. Zero-shot batch: send all sentences at once for efficiency
  3. Rule discovery: ask Sonnet to discover classification rules from text
  4. Rule discovery + apply: Sonnet discovers rules, we apply them programmatically
  5. Meta-learning: Sonnet analyzes document structure, then classifies
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

DATA_DIR = "/mnt/hostshare/ardoco-home/transarc-emp/sentence_classification"
BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
PROJECTS = ["mediastore", "teastore", "teammates", "jabref", "bigbluebutton"]

CACHE_DIR = os.path.join(DATA_DIR, "llm_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def load_dataset():
    with open(os.path.join(DATA_DIR, "annotated_sentences.json")) as f:
        return json.load(f)


def load_raw_sentences(project):
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


def call_sonnet(prompt, cache_key=None, max_retries=3):
    """Call Claude Sonnet via CLI subprocess."""
    if cache_key:
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)["response"]

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["claude", "--print", "--model", "sonnet"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "CLAUDECODE": ""},
            )
            response = result.stdout.strip()
            if response:
                if cache_key:
                    with open(cache_path, 'w') as f:
                        json.dump({"prompt_hash": cache_key, "response": response}, f)
                return response
            print(f"    [retry {attempt+1}] empty response", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"    [retry {attempt+1}] timeout", file=sys.stderr)
        except Exception as e:
            print(f"    [retry {attempt+1}] error: {e}", file=sys.stderr)
        time.sleep(2)

    return ""


def evaluate(predictions, rows, name, show_errors=True):
    tp = fp = fn = tn = 0
    fps = []
    fns = []

    for r in rows:
        true = r['label'] == 'pkg_code'
        pred = predictions.get((r['project'], r['sentence_num']), False)
        if true and pred: tp += 1
        elif not true and pred:
            fp += 1
            fps.append(r)
        elif true and not pred:
            fn += 1
            fns.append(r)
        else: tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    status = "PERFECT" if f1 >= 1.0 else f"gap={1.0-f1:.3f}"
    print(f"\n  {name}:")
    print(f"    TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"    P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}  [{status}]")

    if show_errors:
        if fps:
            print(f"    FPs ({len(fps)}):")
            for r in fps[:5]:
                print(f"      [{r['project']}] S{r['sentence_num']} ({r['label']}): \"{r['text'][:90]}\"")
            if len(fps) > 5:
                print(f"      ... and {len(fps)-5} more")
        if fns:
            print(f"    FNs ({len(fns)}):")
            for r in fns[:5]:
                print(f"      [{r['project']}] S{r['sentence_num']}: \"{r['text'][:90]}\"")
            if len(fns) > 5:
                print(f"      ... and {len(fns)-5} more")

    return tp, fp, fn, tn, f1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROACH 1: ZERO-SHOT BATCH CLASSIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def zero_shot_batch(project, sents):
    """Send all sentences for a project in one batch, ask Sonnet to classify."""
    sent_list = "\n".join(f"S{snum}: {text}" for snum, text in sorted(sents.items()))

    prompt = f"""You are classifying sentences from a software architecture document.

Task: For each sentence, determine if it describes **package/code structure** (e.g., package contents, sub-package listings, package hierarchies, code organization) versus **architectural description** (e.g., component responsibilities, interactions, data flow) or other content.

Label each sentence as either:
- "pkg_code" — describes package structure, code organization, file/class listings
- "other" — everything else (architecture, behavior, implementation, meta)

Return ONLY a JSON object mapping sentence IDs to labels. Example:
{{"S1": "other", "S2": "pkg_code", "S3": "other"}}

Sentences from project "{project}":
{sent_list}

Return the JSON object:"""

    cache_key = f"zeroshot_batch_{project}"
    response = call_sonnet(prompt, cache_key=cache_key)

    # Parse JSON from response
    predictions = {}
    try:
        # Try to find JSON in response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            for key, val in parsed.items():
                snum = int(re.search(r'\d+', key).group())
                predictions[(project, snum)] = (val == 'pkg_code')
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"    Parse error for {project}: {e}", file=sys.stderr)
        # Fallback: line-by-line parsing
        for line in response.split('\n'):
            m = re.search(r'S(\d+).*?(pkg_code|other)', line)
            if m:
                predictions[(project, int(m.group(1)))] = (m.group(2) == 'pkg_code')

    return predictions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROACH 2: RULE DISCOVERY — ask Sonnet to discover rules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def discover_rules(all_sents):
    """Ask Sonnet to analyze documents and discover classification rules."""

    # Collect sample sentences from all projects
    samples = []
    for project, sents in all_sents.items():
        for snum, text in sorted(sents.items()):
            samples.append(f"[{project}] S{snum}: {text}")

    # Send a representative subset (first 50 from teammates where pkg_code lives)
    teammates_sents = "\n".join(
        f"S{snum}: {text}"
        for snum, text in sorted(all_sents['teammates'].items())
        if snum <= 200
    )

    prompt = f"""You are analyzing a software architecture document to discover text patterns.

Some sentences describe **package/code structure** (package contents, sub-package listings, file organization). Others describe **architectural responsibilities** (what components do, how they interact).

Here are sentences from a software architecture document:

{teammates_sents}

Task: Examine these sentences and discover RULES (regex patterns, keyword tests, structural heuristics) that can reliably identify sentences describing package/code structure. The rules should:
1. Be implementable as Python regex or simple string tests
2. Have high precision (never misclassify architectural sentences as package)
3. Have high recall (catch all package-describing sentences)

Return your answer as a JSON list of rules, each with:
- "name": short descriptive name
- "type": "regex_match" (re.match), "regex_search" (re.search), or "keyword" (substring test)
- "pattern": the regex pattern or keyword string
- "case_insensitive": true/false
- "description": what this rule catches

Example:
[
  {{"name": "starts_with_dotted_name", "type": "regex_match", "pattern": "^[a-z][a-z0-9]*\\\\.[a-z]", "case_insensitive": false, "description": "Sentence starts with a Java-style package name"}}
]

Return ONLY the JSON list:"""

    cache_key = "rule_discovery_teammates"
    response = call_sonnet(prompt, cache_key=cache_key)

    # Parse rules
    rules = []
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            rules = json.loads(json_match.group())
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"  Rule parsing error: {e}", file=sys.stderr)

    return rules, response


def apply_discovered_rules(rules, all_sents):
    """Apply LLM-discovered rules to classify sentences."""
    predictions = {}

    for project, sents in all_sents.items():
        for snum, text in sents.items():
            text_s = text.strip()
            text_l = text_s.lower()
            matched = False

            for rule in rules:
                try:
                    pat = rule.get('pattern', '')
                    rtype = rule.get('type', '')
                    ci = rule.get('case_insensitive', False)
                    flags = re.IGNORECASE if ci else 0
                    target = text_l if ci else text_s

                    if rtype == 'regex_match':
                        if re.match(pat, target, flags):
                            matched = True
                            break
                    elif rtype == 'regex_search':
                        if re.search(pat, target, flags):
                            matched = True
                            break
                    elif rtype == 'keyword':
                        if pat.lower() in text_l:
                            matched = True
                            break
                except re.error:
                    pass  # skip invalid regex

            predictions[(project, snum)] = matched

    return predictions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROACH 3: META-LEARNING — Sonnet analyzes then classifies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def meta_learning_classify(project, sents):
    """Two-phase: Sonnet first discovers document structure, then classifies."""

    sent_list = "\n".join(f"S{snum}: {text}" for snum, text in sorted(sents.items()))

    prompt = f"""You are analyzing a software architecture document.

Phase 1 — ANALYZE the document structure:
Look at these sentences and identify which sections describe:
- Package structure (listing packages, sub-packages, what packages contain)
- Architectural design (component responsibilities, interactions)
- Implementation details (specific technologies, configurations)
- Meta information (references to diagrams, document structure)

Phase 2 — CLASSIFY each sentence:
For each sentence, output "pkg_code" if it describes package/code structure, or "other" for everything else.

A sentence is "pkg_code" if it:
- Lists package contents (e.g., "X contains Y, Z")
- Describes what is inside a package or sub-package
- States package hierarchies or organization
- References specific code packages by their dotted names (e.g., logic.api, storage.entity)
- Describes package properties (e.g., "X is not a real package", "X is a conceptual package")

A sentence is NOT "pkg_code" if it:
- Describes what a component DOES (responsibilities, behavior)
- Describes how components interact
- Mentions component names without describing their package structure

Sentences from project "{project}":
{sent_list}

Return ONLY a JSON object mapping sentence IDs to labels.
Example: {{"S1": "other", "S2": "pkg_code"}}

JSON:"""

    cache_key = f"metalearning_{project}"
    response = call_sonnet(prompt, cache_key=cache_key)

    predictions = {}
    try:
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            for key, val in parsed.items():
                snum = int(re.search(r'\d+', key).group())
                predictions[(project, snum)] = (val == 'pkg_code')
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"    Parse error for {project}: {e}", file=sys.stderr)
        for line in response.split('\n'):
            m = re.search(r'S(\d+).*?(pkg_code|other)', line)
            if m:
                predictions[(project, int(m.group(1)))] = (m.group(2) == 'pkg_code')

    return predictions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROACH 4: CROSS-PROJECT RULE TRANSFER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cross_project_rule_discovery(all_sents):
    """Ask Sonnet to analyze ALL projects, discover universal rules."""

    all_text = ""
    for project in PROJECTS:
        sents = all_sents[project]
        sample = "\n".join(f"  S{snum}: {text}" for snum, text in sorted(sents.items()) if snum <= 50)
        all_text += f"\n--- {project} (first 50 sentences) ---\n{sample}\n"

    prompt = f"""You are analyzing software architecture documents from 5 different projects to discover UNIVERSAL rules for identifying sentences that describe package/code structure.

Sample sentences from each project:
{all_text}

Task: Discover rules that work ACROSS ALL projects to identify "package/code structure" sentences. These are sentences that describe:
- Package contents ("X contains Y, Z")
- Sub-package hierarchies
- Code file/class organization
- Package properties ("X is not a real package")

NOT package/code structure:
- Component responsibilities ("X provides authentication")
- Component interactions ("X communicates with Y")
- Implementation details ("configured in web.xml")

Return a JSON list of universal rules:
[
  {{"name": "rule_name", "type": "regex_match"|"regex_search"|"keyword", "pattern": "...", "case_insensitive": true|false, "description": "..."}}
]

Focus on HIGH PRECISION rules. Better to miss some pkg_code sentences than to wrongly classify architectural sentences.

JSON list:"""

    cache_key = "crossproject_rules"
    response = call_sonnet(prompt, cache_key=cache_key)

    rules = []
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            rules = json.loads(json_match.group())
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"  Parse error: {e}", file=sys.stderr)

    return rules, response


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    rows = load_dataset()
    all_sents = {p: load_raw_sentences(p) for p in PROJECTS}

    print("=" * 90)
    print("LLM-BASED pkg_code DETECTION (Sonnet via CLI)")
    print("=" * 90)

    pkg_count = sum(1 for r in rows if r['label'] == 'pkg_code')
    print(f"\nDataset: {len(rows)} sentences, {pkg_count} pkg_code (all in Teammates)")

    results = []

    # ── Approach 1: Zero-shot batch ───────────────────────────────────
    print("\n" + "=" * 90)
    print("APPROACH 1: ZERO-SHOT BATCH CLASSIFICATION")
    print("=" * 90)

    preds_zs = {}
    for project in PROJECTS:
        print(f"  Classifying {project}...")
        p = zero_shot_batch(project, all_sents[project])
        preds_zs.update(p)
        classified = sum(1 for v in p.values() if v)
        print(f"    → {classified} classified as pkg_code")

    r1 = evaluate(preds_zs, rows, "Zero-shot batch")
    results.append(("Zero-shot batch", r1))

    # ── Approach 2: Rule discovery (single project) ───────────────────
    print("\n" + "=" * 90)
    print("APPROACH 2: RULE DISCOVERY (from Teammates)")
    print("=" * 90)

    rules_single, raw_response = discover_rules(all_sents)
    print(f"\n  Discovered {len(rules_single)} rules:")
    for rule in rules_single:
        print(f"    {rule.get('name', '?')}: {rule.get('type', '?')} / {rule.get('pattern', '?')[:60]}")
        print(f"      → {rule.get('description', '?')}")

    preds_rules = apply_discovered_rules(rules_single, all_sents)
    r2 = evaluate(preds_rules, rows, "LLM-discovered rules (single project)")
    results.append(("Rules (single)", r2))

    # ── Approach 3: Meta-learning classify ────────────────────────────
    print("\n" + "=" * 90)
    print("APPROACH 3: META-LEARNING (analyze then classify)")
    print("=" * 90)

    preds_ml = {}
    for project in PROJECTS:
        print(f"  Analyzing & classifying {project}...")
        p = meta_learning_classify(project, all_sents[project])
        preds_ml.update(p)
        classified = sum(1 for v in p.values() if v)
        print(f"    → {classified} classified as pkg_code")

    r3 = evaluate(preds_ml, rows, "Meta-learning (analyze + classify)")
    results.append(("Meta-learning", r3))

    # ── Approach 4: Cross-project rules ───────────────────────────────
    print("\n" + "=" * 90)
    print("APPROACH 4: CROSS-PROJECT RULE DISCOVERY")
    print("=" * 90)

    rules_cross, raw_cross = cross_project_rule_discovery(all_sents)
    print(f"\n  Discovered {len(rules_cross)} universal rules:")
    for rule in rules_cross:
        print(f"    {rule.get('name', '?')}: {rule.get('type', '?')} / {rule.get('pattern', '?')[:60]}")
        print(f"      → {rule.get('description', '?')}")

    preds_cross = apply_discovered_rules(rules_cross, all_sents)
    r4 = evaluate(preds_cross, rows, "Cross-project rules")
    results.append(("Cross-project rules", r4))

    # ── Summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)

    print(f"\n  {'Approach':<35} {'P':>6} {'R':>6} {'F1':>6} {'TP':>4} {'FP':>4} {'FN':>4}")
    print("  " + "─" * 75)

    # Add baselines
    print(f"  {'Rule V2 (human-crafted)':<35} {'1.000':>6} {'1.000':>6} {'1.000':>6} {'39':>4} {'0':>4} {'0':>4}")
    print(f"  {'Auto pipeline (34 hardcoded)':<35} {'1.000':>6} {'1.000':>6} {'1.000':>6} {'39':>4} {'0':>4} {'0':>4}")
    print("  " + "─" * 75)

    for name, (tp, fp, fn, tn, f1) in results:
        p = tp/(tp+fp) if (tp+fp) > 0 else 0
        r = tp/(tp+fn) if (tp+fn) > 0 else 0
        print(f"  {name:<35} {p:>6.3f} {r:>6.3f} {f1:>6.3f} {tp:>4} {fp:>4} {fn:>4}")

    # ── Show discovered rules for analysis ────────────────────────────
    print("\n" + "=" * 90)
    print("DISCOVERED RULES (for manual inspection)")
    print("=" * 90)

    print("\n  Single-project rules:")
    for rule in rules_single:
        print(f"    {json.dumps(rule, indent=2)[:200]}")

    print("\n  Cross-project rules:")
    for rule in rules_cross:
        print(f"    {json.dumps(rule, indent=2)[:200]}")


if __name__ == '__main__':
    main()
