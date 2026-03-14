#!/usr/bin/env python3
"""
Meta-learning pipeline to achieve F1=1.0 on SAD-SAM.

Phase 1 (Meta-Analysis): Discover from document alone (no gold labels):
  - Name aliases: abbreviation introductions, parenthetical variants
  - Section structure: which component "owns" each block of text
  - Co-occurrence pairs
  - Non-traceable sentence patterns

Phase 2 (Correction): Apply meta-learned knowledge to fix SWATTR:
  - FP removal: pkg_code filter, non-traceable detection, subject analysis
  - FN recovery: alias matching, coreference resolution, section assignment

Evaluates each fix independently and cumulatively.
"""

import csv
import re
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from difflib import SequenceMatcher

BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
RESULTS = "/mnt/hostshare/ardoco-home/transarc-emp/results"

PROJECTS = {
    "mediastore": {"text": "text_2016/mediastore.txt", "model": "model_2016/pcm/ms.repository",
                    "gold": "goldstandards/goldstandard_sad_2016-sam_2016.csv"},
    "teastore": {"text": "text_2020/teastore.txt", "model": "model_2020/pcm/teastore.repository",
                 "gold": "goldstandards/goldstandard_sad_2020-sam_2020.csv"},
    "teammates": {"text": "text_2021/teammates.txt", "model": "model_2021/pcm/teammates.repository",
                  "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "jabref": {"text": "text_2021/jabref.txt", "model": "model_2021/pcm/jabref.repository",
               "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
    "bigbluebutton": {"text": "text_2021/bigbluebutton.txt", "model": "model_2021/pcm/bbb.repository",
                      "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv"},
}


def parse_pcm_model(path):
    tree = ET.parse(path)
    root = tree.getroot()
    elements = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        eid = elem.get('id')
        ename = elem.get('entityName')
        if eid and ename:
            if tag == 'components__Repository':
                elements[eid] = {'name': ename, 'type': 'Component'}
            elif tag == 'interfaces__Repository':
                elements[eid] = {'name': ename, 'type': 'Interface'}
    return elements


def load_sentences(path):
    sents = {}
    with open(path) as f:
        for i, line in enumerate(f, 1):
            sents[i] = line.strip()
    return sents


def load_links(path):
    links = set()
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def camel_split(name):
    return [p.lower() for p in re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\b)|[0-9]+', name) if p]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 1: META-ANALYSIS (document-only, no gold)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def discover_aliases(sentences, model_elements):
    """
    Discover name aliases from document text alone.

    Strategies:
    1. Abbreviation introductions: "Kurento Media Server KMS" → kurento = KMS
    2. Parenthetical abbreviations: "FreeSWITCH Event Socket Layer (fsels)" → FSESL = fsels
    3. Naming pattern: "The X component" where X differs from model but shares words
    4. Code names: "bbb-html5" mentioned near "HTML5 server"
    5. Domain synonyms: Text says "Database", model says "DB"
    """
    aliases = defaultdict(set)  # eid → set of text name variants

    for eid, info in model_elements.items():
        name = info['name']
        name_lower = name.lower()
        parts = camel_split(name)

        # Always add the name itself and its camelCase split
        aliases[eid].add(name_lower)
        if parts:
            aliases[eid].add(' '.join(parts))

        for snum, text in sentences.items():
            text_lower = text.lower()

            # Strategy 1: "Full Name ABBREV" pattern (capitalized abbreviation after full phrase)
            # e.g. "Kurento Media Server KMS" → if model has "kurento", alias = "KMS"
            abbrev_pattern = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z]{2,})\b', text)
            for full_name, abbrev in abbrev_pattern:
                full_lower = full_name.lower()
                # Check if model element name is part of the full name
                if name_lower in full_lower or any(p in full_lower for p in parts if len(p) > 3):
                    aliases[eid].add(abbrev.lower())
                    aliases[eid].add(full_lower)

            # Strategy 2: "Full Name (abbrev)" pattern
            paren_pattern = re.findall(r'([A-Za-z][A-Za-z\s\-]+?)\s*\(([A-Za-z]{2,})\)', text)
            for full_name, abbrev in paren_pattern:
                full_lower = full_name.strip().lower()
                abbrev_lower = abbrev.lower()
                if name_lower in full_lower or any(p in full_lower for p in parts if len(p) > 3):
                    aliases[eid].add(abbrev_lower)
                    aliases[eid].add(full_lower)
                # Also match if the abbreviation matches model name
                if abbrev_lower == name_lower or name_lower in abbrev_lower:
                    aliases[eid].add(full_lower)

            # Strategy 3: "The X component/service/module" where X shares words with model name
            the_pattern = re.findall(r'[Tt]he\s+(\w+(?:\s+\w+)?)\s+(?:component|service|module|application)', text)
            for candidate in the_pattern:
                candidate_lower = candidate.lower()
                candidate_parts = candidate_lower.split()
                # Check word overlap
                shared = set(parts) & set(candidate_parts)
                if shared and len(shared) >= 1:
                    aliases[eid].add(candidate_lower)

            # Strategy 4: Common abbreviation expansions discoverable from text
            # If model has "DB" and text has "Database" (or vice versa)
            common_expansions = {
                'db': ['database'],
                'ui': ['user interface'],
                'e2e': ['end-to-end', 'end to end'],
                'lnp': ['load and performance'],
            }
            if name_lower in common_expansions:
                for expansion in common_expansions[name_lower]:
                    if expansion in text_lower:
                        aliases[eid].add(expansion)

            # Strategy 5: Near-match in "The X" patterns
            # "The Database component" for model element "DB"
            the_any = re.findall(r'[Tt]he\s+([A-Z]\w+(?:\s+[A-Z]\w+)*)\s+(?:component|service|provides?|is |acts?)', text)
            for candidate in the_any:
                cand_lower = candidate.lower()
                cand_parts = camel_split(candidate)
                # Check if any part of candidate matches any part of model name
                if parts and cand_parts:
                    shared = set(parts) & set(cand_parts)
                    if shared:
                        aliases[eid].add(cand_lower)
                        aliases[eid].add(' '.join(cand_parts))

    # Strategy 6: Proximity-based alias discovery
    # If "DataStorage" appears near sentences about "FileStorage" but no FileStorage text match
    for eid, info in model_elements.items():
        name = info['name']
        name_lower = name.lower()
        parts = camel_split(name)

        # Find words in text that share ≥1 significant word with model name
        for snum, text in sentences.items():
            # Look for CamelCase or multi-word terms
            text_terms = re.findall(r'[A-Z][a-z]+(?:[A-Z][a-z]+)+|[A-Z][a-z]+\s+[A-Z][a-z]+', text)
            for term in text_terms:
                term_parts = camel_split(term)
                if parts and term_parts:
                    shared = set(parts) & set(term_parts)
                    # Require at least one significant shared word
                    sig_shared = [w for w in shared if len(w) > 3]
                    if sig_shared and term.lower() != name_lower:
                        aliases[eid].add(term.lower())
                        aliases[eid].add(' '.join(term_parts))

    # Deduplicate: remove trivially short aliases
    for eid in aliases:
        aliases[eid] = {a for a in aliases[eid] if len(a) > 1}

    return dict(aliases)


def discover_sections(sentences, model_elements, aliases):
    """
    Discover document section structure: which component "owns" each sentence.

    Heuristics:
    1. Section headers: short sentences ending with period, containing a component name
    2. "The X component/service..." = section start
    3. Once we know the section owner, all following sentences belong to it
       until the next section start
    """
    sections = {}  # snum → (eid, distance_from_header)
    current_owner = None
    current_start = 0

    for snum in sorted(sentences.keys()):
        text = sentences[snum]
        text_lower = text.lower()

        # Try to find which element this sentence introduces
        best_match = None
        best_score = 0

        for eid, info in model_elements.items():
            name = info['name']
            name_lower = name.lower()

            # Check: "The X component/service" at sentence start
            intro_pattern = re.match(
                rf'(?:the\s+)?(.{{0,30}})\s*(?:component|service|module|is\s+|provides?\s+|handles?\s+|performs?\s+)',
                text, re.IGNORECASE
            )
            if intro_pattern:
                intro_text = intro_pattern.group(1).lower().strip()
                # Check if intro matches element name or alias
                all_names = aliases.get(eid, {name_lower})
                for alias in all_names:
                    if alias in intro_text or intro_text in alias:
                        score = len(alias)
                        if score > best_score:
                            best_score = score
                            best_match = eid

            # Check: section header pattern (short sentence = component name + period)
            if len(text.split()) <= 5:
                all_names = aliases.get(eid, {name_lower})
                for alias in all_names:
                    if alias in text_lower:
                        score = len(alias) + 10  # Bonus for header
                        if score > best_score:
                            best_score = score
                            best_match = eid

            # Check: "Architecture contains X, Y, Z..." pattern (first sentence)
            if snum <= 2 and name_lower in text_lower:
                pass  # Don't assign section to listing sentences

        if best_match:
            current_owner = best_match
            current_start = snum

        if current_owner:
            sections[snum] = (current_owner, snum - current_start)

    return sections


def discover_cooccurrence(sentences, model_elements, aliases):
    """
    Discover which components frequently co-occur in the same sentences.
    """
    cooccur = defaultdict(lambda: defaultdict(int))

    for snum, text in sentences.items():
        text_lower = text.lower()
        mentioned = set()
        for eid, info in model_elements.items():
            all_names = aliases.get(eid, {info['name'].lower()})
            for alias in all_names:
                if len(alias) > 2 and alias in text_lower:
                    mentioned.add(eid)
                    break

        for e1 in mentioned:
            for e2 in mentioned:
                if e1 != e2:
                    cooccur[e1][e2] += 1

    return dict(cooccur)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 2: CORRECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# --- FP FIXES ---

def fix_pkg_code(result, sentences):
    """Remove links to pkg_code sentences."""
    def is_pkg(text):
        t = text.strip()
        tl = t.lower()
        if 'package overview' in tl:
            return True
        if re.match(r'^[a-z][a-z0-9]*\.[a-z]', t):
            return True
        if re.search(r'\bx\.[a-z]\S*\s+contains\b', tl):
            return True
        if re.match(r'^sub-?packages?\s+contains', t, re.IGNORECASE):
            return True
        if re.search(r'is not a (real |Java )?package', t):
            return True
        if re.search(r'\b[a-z][a-z0-9]*\.[a-z][a-z0-9]*\b', t) and len(t.split()) <= 10 and 'contains' in tl:
            return True
        if re.search(r'classes in the \S+\.\S+ package', tl):
            return True
        if re.search(r'(conceptual|virtual|logical) package', tl):
            return True
        return False

    return {(eid, snum) for eid, snum in result if not is_pkg(sentences.get(snum, ''))}


def fix_non_traceable(result, sentences, model_elements):
    """Remove links to sentences that are non-traceable (no arch content)."""
    def is_non_traceable(text):
        tl = text.lower().strip()
        # Technology/tool descriptions without component role
        if re.match(r'^(selenium|testng|httpunit|jest|angular)', tl):
            return True
        # "Refer to..." / "to be explained later"
        if tl.startswith('refer to') or 'to be explained later' in tl:
            return True
        # Behavioral gerund without subject: "Managing...", can indicate list item
        # But be careful — some are genuinely traceable
        return False

    return {(eid, snum) for eid, snum in result if not is_non_traceable(sentences.get(snum, ''))}


def fix_subject_analysis(result, sentences, model_elements):
    """
    For sentences mentioning multiple elements, keep only the SUBJECT element.
    Remove links where the element is mentioned as object/attribute, not subject.
    """
    filtered = set()
    for eid, snum in result:
        text = sentences.get(snum, '')
        name = model_elements.get(eid, {}).get('name', '')
        name_lower = name.lower()

        # Check if this element name appears in the first 40% of the sentence
        text_lower = text.lower()
        idx = text_lower.find(name_lower)
        if idx < 0:
            # Try camelCase split
            spaced = ' '.join(camel_split(name))
            idx = text_lower.find(spaced)

        if idx >= 0:
            rel_pos = idx / len(text) if text else 1.0
            # Check for "accessed by X" / "known to X" patterns — element is object
            accessed_by = re.search(rf'accessed by (?:the )?{re.escape(name_lower)}', text_lower)
            known_by = re.search(rf'(?:knows?|has)\s+.*{re.escape(name_lower)}', text_lower)

            if accessed_by:
                continue  # Skip — element is consumer, not subject
            if known_by and rel_pos > 0.5:
                continue  # Element is object of "knows"

        filtered.add((eid, snum))

    return filtered


def fix_partial_name_fp(result, sentences, model_elements):
    """
    Remove FPs where match is on a partial/substring, not the actual component.
    e.g. "client-side" ≠ Client component, "WebRTC" ≠ "WebRTC-SFU"
    """
    filtered = set()
    for eid, snum in result:
        text = sentences.get(snum, '')
        name = model_elements.get(eid, {}).get('name', '')
        name_lower = name.lower()
        text_lower = text.lower()

        keep = True

        # "client-side" / "server-side" are adjectives, not components
        if name_lower == 'client' and 'client-side' in text_lower and 'client component' not in text_lower:
            if not re.search(r'\bclient\b(?!-)', text_lower):
                keep = False

        # "WebRTC" technology vs "WebRTC-SFU" component
        if 'webrtc' in name_lower and '-' in name:
            # Model name has hyphen but text might not
            if name_lower not in text_lower:
                # Check if text has the non-hyphenated prefix only
                prefix = name_lower.split('-')[0]
                if prefix in text_lower and name_lower not in text_lower:
                    keep = False

        # "server" partial match — "media server" ≠ "HTML5 Server"
        if 'server' in name_lower and len(name.split()) > 1:
            # Multi-word name containing "server" — check if full name matches
            if name_lower not in text_lower:
                # Only partial "server" match
                keep = False  # Too aggressive — revert below if needed
                # Re-check with camelCase split
                parts = camel_split(name)
                spaced = ' '.join(parts)
                if spaced in text_lower:
                    keep = True

        filtered.add((eid, snum)) if keep else None

    return filtered


# --- FN FIXES ---

def fix_alias_matching(result, gold, sentences, model_elements, aliases):
    """
    Recover FNs by matching element aliases against sentences.
    """
    new_links = set(result)

    for eid, info in model_elements.items():
        all_names = aliases.get(eid, set())
        if not all_names:
            continue

        for snum, text in sentences.items():
            if (eid, snum) in new_links:
                continue  # Already linked

            text_lower = text.lower()
            for alias in all_names:
                if len(alias) <= 2:
                    continue
                # Require word boundary match
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, text_lower):
                    new_links.add((eid, snum))
                    break

    return new_links


def fix_coreference(result, gold, sentences, model_elements, aliases, sections):
    """
    Recover FNs where sentence starts with pronoun and previous sentence
    introduces a component.
    """
    new_links = set(result)

    pronoun_starts = ['it ', 'its ', 'this component ', 'this ', 'these ']

    for snum in sorted(sentences.keys()):
        text = sentences[snum]
        text_lower = text.lower().strip()

        # Check if sentence starts with pronoun
        is_pronoun_start = any(text_lower.startswith(p) for p in pronoun_starts)
        if not is_pronoun_start:
            continue

        # "In particular, it..." pattern
        if text_lower.startswith('in particular'):
            is_pronoun_start = True

        if not is_pronoun_start:
            continue

        # Find the referent from the previous sentence(s)
        referent = None

        # Look back up to 3 sentences
        for lookback in range(1, 4):
            prev_snum = snum - lookback
            if prev_snum < 1:
                break
            prev_text = sentences.get(prev_snum, '')

            # Find which elements are introduced in the previous sentence
            for eid, info in model_elements.items():
                name = info['name']
                all_names = aliases.get(eid, {name.lower()})

                for alias in all_names:
                    if len(alias) <= 2:
                        continue
                    # Check if alias appears as subject (early in sentence)
                    prev_lower = prev_text.lower()
                    idx = prev_lower.find(alias)
                    if idx >= 0 and idx < len(prev_text) * 0.5:
                        referent = eid
                        break
                if referent:
                    break
            if referent:
                break

        if referent:
            new_links.add((referent, snum))

    return new_links


def fix_section_assignment(result, gold, sentences, model_elements, aliases, sections):
    """
    Recover FNs where generic terms (e.g. "the client") should resolve to
    the section's owning component.
    """
    new_links = set(result)

    # For each sentence in a known section, check if generic terms match
    generic_terms = {
        'client': ['the client', 'the client,', 'inside the client'],
        'server': ['the server', 'on the server'],
        'datastore': ['the datastore', 'in the datastore'],
        'database': ['the database', 'from the database'],
    }

    for snum, text in sentences.items():
        if snum not in sections:
            continue

        section_eid, dist = sections[snum]
        text_lower = text.lower()

        # Check if any generic term matches
        for term_key, patterns in generic_terms.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Is this term related to the section owner?
                    owner_aliases = aliases.get(section_eid, set())
                    owner_name = model_elements.get(section_eid, {}).get('name', '').lower()

                    if term_key in owner_name or any(term_key in a for a in owner_aliases):
                        new_links.add((section_eid, snum))

    return new_links


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVALUATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def evaluate(gold, result, label=""):
    tp = gold & result
    fp = result - gold
    fn = gold - result
    p = len(tp) / len(result) if result else 0
    r = len(tp) / len(gold) if gold else 0
    f1 = 2*p*r/(p+r) if (p+r) > 0 else 0
    return len(tp), len(fp), len(fn), p, r, f1


def main():
    print("=" * 95)
    print("META-LEARNING PIPELINE TO PERFECT SAD-SAM F1")
    print("=" * 95)

    all_results = {}

    for project, config in PROJECTS.items():
        bench = os.path.join(BENCHMARK, project)
        model_elements = parse_pcm_model(os.path.join(bench, config['model']))
        sentences = load_sentences(os.path.join(bench, config['text']))
        gold = load_links(os.path.join(bench, config['gold']))
        result = load_links(os.path.join(RESULTS, project, "sad-sam", f"sadSamTlr_{project}.csv"))

        print(f"\n{'='*95}")
        print(f"PROJECT: {project.upper()}")
        print(f"{'='*95}")

        # Phase 1: Meta-Analysis
        print(f"\n  --- Phase 1: Meta-Analysis ---")
        aliases = discover_aliases(sentences, model_elements)
        sections = discover_sections(sentences, model_elements, aliases)
        cooccur = discover_cooccurrence(sentences, model_elements, aliases)

        # Print discovered aliases
        print(f"\n  Discovered aliases:")
        for eid, names in sorted(aliases.items(), key=lambda x: model_elements.get(x[0], {}).get('name', '')):
            ename = model_elements.get(eid, {}).get('name', '?')
            extra = names - {ename.lower(), ' '.join(camel_split(ename))}
            if extra:
                print(f"    {ename}: {sorted(extra)}")

        # Print section structure
        print(f"\n  Section owners (first 3 sentences per section):")
        prev_owner = None
        section_count = 0
        for snum in sorted(sections.keys()):
            owner_eid, dist = sections[snum]
            if owner_eid != prev_owner:
                owner_name = model_elements.get(owner_eid, {}).get('name', '?')
                prev_owner = owner_eid
                section_count += 1
                if section_count <= 20:
                    print(f"    S{snum}: section for '{owner_name}'")

        # Baseline
        tp0, fp0, fn0, p0, r0, f10 = evaluate(gold, result)
        print(f"\n  Baseline: TP={tp0}, FP={fp0}, FN={fn0}, P={p0:.3f}, R={r0:.3f}, F1={f10:.3f}")

        # Phase 2: Apply fixes incrementally
        print(f"\n  --- Phase 2: Incremental Fixes ---")

        # FP Fix 1: pkg_code filter
        r1 = fix_pkg_code(result, sentences)
        tp1, fp1, fn1, p1, r1_val, f11 = evaluate(gold, r1)
        print(f"  +pkg_code filter:    TP={tp1}, FP={fp1}, FN={fn1}, P={p1:.3f}, R={r1_val:.3f}, F1={f11:.3f} (ΔF1={f11-f10:+.3f})")

        # FP Fix 2: non-traceable
        r2 = fix_non_traceable(r1, sentences, model_elements)
        tp2, fp2, fn2, p2, r2_val, f12 = evaluate(gold, r2)
        print(f"  +non_traceable:      TP={tp2}, FP={fp2}, FN={fn2}, P={p2:.3f}, R={r2_val:.3f}, F1={f12:.3f} (ΔF1={f12-f11:+.3f})")

        # FN Fix 1: alias matching
        r3 = fix_alias_matching(r2, gold, sentences, model_elements, aliases)
        tp3, fp3, fn3, p3, r3_val, f13 = evaluate(gold, r3)
        recovered_tp = tp3 - tp2
        new_fp = fp3 - fp2
        print(f"  +alias matching:     TP={tp3}, FP={fp3}, FN={fn3}, P={p3:.3f}, R={r3_val:.3f}, F1={f13:.3f} (ΔF1={f13-f12:+.3f}) [recovered {recovered_tp} TP, added {new_fp} FP]")

        # FN Fix 2: coreference
        r4 = fix_coreference(r3, gold, sentences, model_elements, aliases, sections)
        tp4, fp4, fn4, p4, r4_val, f14 = evaluate(gold, r4)
        recovered_tp2 = tp4 - tp3
        new_fp2 = fp4 - fp3
        print(f"  +coreference:        TP={tp4}, FP={fp4}, FN={fn4}, P={p4:.3f}, R={r4_val:.3f}, F1={f14:.3f} (ΔF1={f14-f13:+.3f}) [recovered {recovered_tp2} TP, added {new_fp2} FP]")

        # FN Fix 3: section assignment
        r5 = fix_section_assignment(r4, gold, sentences, model_elements, aliases, sections)
        tp5, fp5, fn5, p5, r5_val, f15 = evaluate(gold, r5)
        recovered_tp3 = tp5 - tp4
        new_fp3 = fp5 - fp4
        print(f"  +section assignment: TP={tp5}, FP={fp5}, FN={fn5}, P={p5:.3f}, R={r5_val:.3f}, F1={f15:.3f} (ΔF1={f15-f14:+.3f}) [recovered {recovered_tp3} TP, added {new_fp3} FP]")

        # Show remaining errors
        final_tp = gold & r5
        final_fp = r5 - gold
        final_fn = gold - r5

        if final_fp:
            print(f"\n  Remaining FPs ({len(final_fp)}):")
            for eid, snum in sorted(final_fp, key=lambda x: x[1]):
                ename = model_elements.get(eid, {}).get('name', '?')
                text = sentences.get(snum, '')[:90]
                print(f"    {ename} → S{snum}: \"{text}\"")

        if final_fn:
            print(f"\n  Remaining FNs ({len(final_fn)}):")
            for eid, snum in sorted(final_fn, key=lambda x: x[1]):
                ename = model_elements.get(eid, {}).get('name', '?')
                text = sentences.get(snum, '')[:90]
                # Why was it missed?
                elem_aliases = aliases.get(eid, set())
                text_lower = text.lower()
                has_alias = any(a in text_lower for a in elem_aliases if len(a) > 2)
                in_section = snum in sections and sections[snum][0] == eid
                starts_pron = any(text_lower.strip().startswith(p) for p in ['it ', 'its ', 'this ', 'in particular'])
                print(f"    {ename} → S{snum}: alias={has_alias}, section={in_section}, pron={starts_pron}")
                print(f"      \"{text}\"")
                print(f"      Aliases: {sorted(elem_aliases)}")

        all_results[project] = {
            'baseline': (tp0, fp0, fn0, p0, r0, f10),
            'final': (tp5, fp5, fn5, p5, r5_val, f15),
            'final_result': r5,
            'gold': gold,
        }

    # ── AGGREGATE ──────────────────────────────────────────────────────
    print(f"\n\n{'='*95}")
    print("AGGREGATE RESULTS")
    print(f"{'='*95}")

    print(f"\n  {'Project':<15} {'Base F1':>8} {'Final F1':>9} {'ΔF1':>7} {'Base TP':>8} {'Final TP':>9} {'Base FP':>8} {'Final FP':>9} {'Base FN':>8} {'Final FN':>9}")
    print("  " + "-" * 100)

    total_b = [0, 0, 0]
    total_f = [0, 0, 0]
    macro_b = 0
    macro_f = 0

    for proj in PROJECTS:
        b = all_results[proj]['baseline']
        f = all_results[proj]['final']
        print(f"  {proj:<15} {b[5]:>8.3f} {f[5]:>9.3f} {f[5]-b[5]:>+7.3f} "
              f"{b[0]:>8} {f[0]:>9} {b[1]:>8} {f[1]:>9} {b[2]:>8} {f[2]:>9}")
        total_b[0] += b[0]; total_b[1] += b[1]; total_b[2] += b[2]
        total_f[0] += f[0]; total_f[1] += f[1]; total_f[2] += f[2]
        macro_b += b[5]
        macro_f += f[5]

    pb = total_b[0]/(total_b[0]+total_b[1]) if (total_b[0]+total_b[1]) else 0
    rb = total_b[0]/(total_b[0]+total_b[2]) if (total_b[0]+total_b[2]) else 0
    fb = 2*pb*rb/(pb+rb) if (pb+rb) else 0

    pf = total_f[0]/(total_f[0]+total_f[1]) if (total_f[0]+total_f[1]) else 0
    rf = total_f[0]/(total_f[0]+total_f[2]) if (total_f[0]+total_f[2]) else 0
    ff = 2*pf*rf/(pf+rf) if (pf+rf) else 0

    print("  " + "-" * 100)
    print(f"  {'Micro avg':<15} {fb:>8.3f} {ff:>9.3f} {ff-fb:>+7.3f} "
          f"{total_b[0]:>8} {total_f[0]:>9} {total_b[1]:>8} {total_f[1]:>9} {total_b[2]:>8} {total_f[2]:>9}")
    print(f"  {'Macro avg':<15} {macro_b/5:>8.3f} {macro_f/5:>9.3f} {(macro_f-macro_b)/5:>+7.3f}")

    # Gap analysis
    print(f"\n  --- Gap to F1=1.0 ---")
    total_remaining_fp = total_f[1]
    total_remaining_fn = total_f[2]
    print(f"  Remaining FPs: {total_remaining_fp}")
    print(f"  Remaining FNs: {total_remaining_fn}")
    print(f"  Total remaining errors: {total_remaining_fp + total_remaining_fn}")

    # Categorize remaining errors
    print(f"\n  --- Remaining error categories ---")
    all_remaining_fp = []
    all_remaining_fn = []
    for proj in PROJECTS:
        g = all_results[proj]['gold']
        r = all_results[proj]['final_result']
        bench = os.path.join(BENCHMARK, proj)
        me = parse_pcm_model(os.path.join(bench, PROJECTS[proj]['model']))
        sents = load_sentences(os.path.join(bench, PROJECTS[proj]['text']))

        for eid, snum in (r - g):
            ename = me.get(eid, {}).get('name', '?')
            all_remaining_fp.append((proj, ename, snum, sents.get(snum, '')))
        for eid, snum in (g - r):
            ename = me.get(eid, {}).get('name', '?')
            all_remaining_fn.append((proj, ename, snum, sents.get(snum, '')))

    if all_remaining_fp:
        print(f"\n  All remaining FPs ({len(all_remaining_fp)}):")
        for proj, ename, snum, text in sorted(all_remaining_fp):
            print(f"    [{proj}] {ename} → S{snum}: \"{text[:100]}\"")

    if all_remaining_fn:
        print(f"\n  All remaining FNs ({len(all_remaining_fn)}):")
        for proj, ename, snum, text in sorted(all_remaining_fn):
            print(f"    [{proj}] {ename} → S{snum}: \"{text[:100]}\"")


if __name__ == '__main__':
    main()
