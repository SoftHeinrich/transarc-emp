#!/usr/bin/env python3
"""
SWATTR TP vs FP: Zero-Shot LLM Classification (Batch Mode)

Uses Claude Sonnet via CLI to classify SWATTR links as TP or FP.
All links per project sent in a single batch prompt.

Four prompt strategies:
  1. Direct: "Is this an architectural trace link?"
  2. Convention-aware: Feed the reverse-engineered rules
  3. Three-filter: Check reference, topicality, abstraction
  4. Minimal: Just ask "architectural role or implementation detail?"

Produces: SWATTR_LLM_ZEROSHOT.md
"""

import csv
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/SWATTR_LLM_ZEROSHOT.md")
CACHE_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/llm_cache_swattr")
CACHE_DIR.mkdir(exist_ok=True)

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


def query_claude(prompt, model="sonnet", timeout=300, cache_key=None):
    """Query Claude via CLI. Returns response text or None."""
    if cache_key:
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                cached = json.load(f)
            return cached.get("response")

    cmd = ["claude", "-p", "--output-format", "json", "--dangerously-skip-permissions",
           "--model", model, prompt]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                cwd=str(CACHE_DIR), env=env)
        response_text = ""
        try:
            data = json.loads(result.stdout.strip())
            if data.get('type') == 'result':
                response_text = data.get('result', '')
        except json.JSONDecodeError:
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if event.get('type') == 'result':
                        response_text = event.get('result', '')
                        break
                except json.JSONDecodeError:
                    continue
        if not response_text and result.stdout.strip():
            response_text = result.stdout.strip()

        if cache_key and response_text:
            with open(CACHE_DIR / f"{cache_key}.json", 'w') as f:
                json.dump({"response": response_text}, f)

        return response_text if response_text else None

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None


def parse_batch_response(response_text, n_expected):
    """Parse batch response to extract verdicts. Returns list of 0/1."""
    if not response_text:
        return [1] * n_expected  # default: keep all

    verdicts = [None] * n_expected

    # Try to find JSON array
    try:
        m = re.search(r'\[[\s\S]*\]', response_text)
        if m:
            arr = json.loads(m.group())
            for item in arr:
                idx = item.get("id", 0) - 1
                if 0 <= idx < n_expected:
                    v = str(item.get("verdict", item.get("classification", ""))).upper()
                    if "NO" in v:
                        verdicts[idx] = 0
                    else:
                        verdicts[idx] = 1
    except json.JSONDecodeError:
        pass

    # If JSON parsing failed, try line-by-line
    if all(v is None for v in verdicts):
        lines = response_text.strip().split('\n')
        idx = 0
        for line in lines:
            line_upper = line.upper()
            if re.search(r'\b(NO_LINK|NO LINK|NOT.LINK)\b', line_upper):
                if idx < n_expected:
                    verdicts[idx] = 0
                    idx += 1
            elif re.search(r'\bLINK\b', line_upper) and "NO" not in line_upper.split("LINK")[0][-5:]:
                if idx < n_expected:
                    verdicts[idx] = 1
                    idx += 1

    # Fill remaining with default (keep = 1)
    return [v if v is not None else 1 for v in verdicts]


def make_items_text(proj_records):
    """Format records as numbered list for batch prompt."""
    items = []
    for i, r in enumerate(proj_records):
        items.append(f'{i+1}. Sentence S{r["sent_num"]}: "{r["text"]}"\n   Component: "{r["elem_name"]}"')
    return "\n\n".join(items)


# ─── Prompt strategies (batch versions) ───────────────────────────────────────

STRATEGIES = {}

STRATEGIES["direct"] = {
    "name": "Direct (no convention hints)",
    "template": """You are evaluating traceability links between software architecture documentation and architecture model elements.

A trace link connects a documentation sentence to an architectural component when the sentence describes that component's architectural role, behavior, or interactions in the system.

For the project "{project}", classify each sentence-component pair as LINK (valid trace link) or NO_LINK (not a valid trace link).

{items}

Reply with ONLY a JSON array, one object per item:
[{{"id": 1, "verdict": "LINK" or "NO_LINK", "reason": "brief"}}, ...]"""
}

STRATEGIES["convention"] = {
    "name": "Convention-aware (full rules)",
    "template": """You are evaluating traceability links between software architecture documentation (SAD) and software architecture model (SAM) elements.

ANNOTATION CONVENTION:
A sentence S is linked to component C if and only if:
1. S refers to C as an architectural component (not just a generic word match — e.g. "logic" the word vs "Logic" the component)
2. S is primarily ABOUT C (not mentioning it incidentally while describing another component)
3. S describes C at the ARCHITECTURAL level — its role, behavior, services, interactions with other components

A sentence is NOT linked even if it mentions C when:
- S describes C's internal package structure (e.g. "storage.api provides the API", "common.util contains utility classes")
- S lists implementation classes/helpers/utilities within C
- S is a package overview header ("Package overview contains X.a, X.b, X.c")
- S is a meta-comment about C's naming or implementation details
- S mentions C only incidentally while primarily describing another component
- The component name appears as a generic English word, not as the component reference
- S describes a technology (e.g. "WebRTC") rather than the component (e.g. "WebRTC-SFU")

For the project "{project}", classify each sentence-component pair:

{items}

Reply with ONLY a JSON array, one object per item:
[{{"id": 1, "verdict": "LINK" or "NO_LINK", "reason": "which rule"}}]"""
}

STRATEGIES["three_filter"] = {
    "name": "Three-filter (reference + topicality + abstraction)",
    "template": """You are evaluating traceability links. Apply THREE sequential filters to each pair:

FILTER 1 — REFERENCE: Does the sentence refer to the component as an architectural entity?
(Not a generic word like "logic"/"server", not a technology name mismatch like "WebRTC" vs "WebRTC-SFU")

FILTER 2 — TOPICALITY: Is the sentence primarily ABOUT this component?
(Not mentioning it incidentally while describing another component)

FILTER 3 — ABSTRACTION: Does the sentence describe the component at the ARCHITECTURAL level?
(Role, behavior, interactions — NOT package structure, class listings, directory layout, implementation details)

A link is valid only if ALL THREE filters pass.

For the project "{project}", classify each:

{items}

Reply with ONLY a JSON array:
[{{"id": 1, "f1": "PASS/FAIL", "f2": "PASS/FAIL", "f3": "PASS/FAIL", "verdict": "LINK" or "NO_LINK"}}]"""
}

STRATEGIES["minimal"] = {
    "name": "Minimal (arch role vs impl detail)",
    "template": """Classify each sentence-component pair. Does the sentence describe the component's ARCHITECTURAL ROLE in the system, or is it about IMPLEMENTATION DETAILS (packages, classes, directory structure)?

Only "architectural role" counts as a valid trace link.

Project: "{project}"

{items}

Reply with ONLY a JSON array:
[{{"id": 1, "verdict": "LINK" or "NO_LINK"}}]"""
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    md = []
    def out(s=""):
        print(s)
        md.append(s)

    out("# SWATTR TP vs FP: Zero-Shot LLM Classification (Batch)")
    out()
    out("Using Claude Sonnet via CLI. All links per project in a single batch prompt.")
    out()

    # ── Collect records ───────────────────────────────────────────────────────

    records = []
    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        for model_id, sent_num in sorted(gold & result, key=lambda x: int(x[1])):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            records.append({"project": proj, "model_id": model_id,
                            "sent_num": sent_num, "elem_name": ei["name"],
                            "text": text.get(sent_num, ""), "label": 1})

        for model_id, sent_num in sorted(result - gold, key=lambda x: int(x[1])):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            records.append({"project": proj, "model_id": model_id,
                            "sent_num": sent_num, "elem_name": ei["name"],
                            "text": text.get(sent_num, ""), "label": 0})

    n_tp = sum(r["label"] for r in records)
    n_fp = len(records) - n_tp
    out(f"**Data**: {n_tp} TPs + {n_fp} FPs = {len(records)} SWATTR links")
    out()

    per_proj = defaultdict(list)
    for i, r in enumerate(records):
        per_proj[r["project"]].append((i, r))

    # ── Run each strategy ─────────────────────────────────────────────────────

    all_strategy_results = {}

    for strat_key, strat_info in STRATEGIES.items():
        strat_name = strat_info["name"]
        template = strat_info["template"]

        out(f"## Strategy: {strat_name}")
        out()

        all_preds = [1] * len(records)  # default: keep
        raw_responses = {}

        for proj in PROJECTS:
            proj_items = per_proj[proj]
            if not proj_items:
                continue

            proj_records = [r for _, r in proj_items]
            items_text = make_items_text(proj_records)
            prompt = template.format(project=proj, items=items_text)

            cache_key = f"batch_{strat_key}_{proj}"
            print(f"  [{strat_key}] {proj}: {len(proj_records)} links...",
                  end="", file=sys.stderr, flush=True)

            response = query_claude(prompt, cache_key=cache_key)
            raw_responses[proj] = response

            if response:
                verdicts = parse_batch_response(response, len(proj_records))
                for j, (global_idx, _) in enumerate(proj_items):
                    all_preds[global_idx] = verdicts[j]
                parsed_count = sum(1 for v in verdicts if v == 0)
                print(f" {parsed_count} NO_LINK", file=sys.stderr)
            else:
                print(f" FAILED", file=sys.stderr)

            time.sleep(1)

        # Compute metrics
        labels = [r["label"] for r in records]
        tp_correct = sum(1 for p, l in zip(all_preds, labels) if p == 1 and l == 1)
        tp_killed = sum(1 for p, l in zip(all_preds, labels) if p == 0 and l == 1)
        fp_caught = sum(1 for p, l in zip(all_preds, labels) if p == 0 and l == 0)
        fp_missed = sum(1 for p, l in zip(all_preds, labels) if p == 1 and l == 0)
        accuracy = (tp_correct + fp_caught) / len(records)
        filt_prec = fp_caught / (fp_caught + tp_killed) if (fp_caught + tp_killed) > 0 else 0
        net = fp_caught - tp_killed

        out(f"| Metric | Value |")
        out(f"|--------|-------|")
        out(f"| TPs correctly kept | {tp_correct}/{n_tp} ({tp_correct/n_tp:.0%}) |")
        out(f"| TPs wrongly killed | {tp_killed}/{n_tp} ({tp_killed/n_tp:.0%}) |")
        out(f"| FPs correctly caught | {fp_caught}/{n_fp} ({fp_caught/n_fp:.0%}) |")
        out(f"| FPs missed | {fp_missed}/{n_fp} ({fp_missed/n_fp:.0%}) |")
        out(f"| **Net benefit** | **{net:+d}** |")
        out(f"| Filter precision | {filt_prec:.0%} |")
        out(f"| Overall accuracy | {accuracy:.0%} |")
        out()

        # Per-project
        out("**Per-project:**")
        out()
        out("| Project | TPs | FPs | FPs Caught | TPs Killed | Net |")
        out("|---------|-----|-----|------------|------------|-----|")
        for proj in PROJECTS:
            proj_items = per_proj[proj]
            p_tp = sum(1 for _, r in proj_items if r["label"] == 1)
            p_fp = sum(1 for _, r in proj_items if r["label"] == 0)
            p_fp_caught = sum(1 for gi, r in proj_items if r["label"] == 0 and all_preds[gi] == 0)
            p_tp_killed = sum(1 for gi, r in proj_items if r["label"] == 1 and all_preds[gi] == 0)
            out(f"| {proj} | {p_tp} | {p_fp} | {p_fp_caught} | {p_tp_killed} | {p_fp_caught - p_tp_killed:+d} |")
        out()

        # FP details
        out("**FP details:**")
        out()
        for gi, r in enumerate(records):
            if r["label"] == 0:
                tag = "CAUGHT" if all_preds[gi] == 0 else "MISSED"
                out(f"- [{tag}] {r['project']} S{r['sent_num']} x {r['elem_name']}: `{r['text'][:70]}...`")
        out()

        # TP errors
        killed_list = [(gi, r) for gi, r in enumerate(records)
                       if r["label"] == 1 and all_preds[gi] == 0]
        if killed_list:
            out(f"**TPs wrongly killed ({len(killed_list)}):**")
            out()
            for gi, r in killed_list:
                out(f"- {r['project']} S{r['sent_num']} x {r['elem_name']}: `{r['text'][:70]}...`")
            out()

        all_strategy_results[strat_key] = {
            "preds": all_preds, "fp_caught": fp_caught, "tp_killed": tp_killed,
            "accuracy": accuracy, "filt_prec": filt_prec, "net": net,
        }

    # ── Impact on SAD-SAM metrics ─────────────────────────────────────────────

    out("## Impact on SWATTR SAD-SAM Metrics")
    out()

    best_strat = max(all_strategy_results, key=lambda k: all_strategy_results[k]["net"])
    best = all_strategy_results[best_strat]
    best_preds = best["preds"]

    out(f"Best strategy: **{STRATEGIES[best_strat]['name']}** (net {best['net']:+d})")
    out()
    out("| Project | Orig P | Orig R | Orig F1 | Filt P | Filt R | Filt F1 | ΔF1 |")
    out("|---------|--------|--------|---------|--------|--------|---------|-----|")

    avg_delta = 0
    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)

        tp_orig = len(gold & result)
        fp_orig = len(result - gold)
        fn_orig = len(gold - result)

        p_o = tp_orig / (tp_orig + fp_orig) if (tp_orig + fp_orig) > 0 else 0
        r_o = tp_orig / (tp_orig + fn_orig) if (tp_orig + fn_orig) > 0 else 0
        f1_o = 2*p_o*r_o/(p_o+r_o) if (p_o+r_o) > 0 else 0

        proj_items = per_proj[proj]
        tp_removed = sum(1 for gi, r in proj_items if r["label"] == 1 and best_preds[gi] == 0)
        fp_removed = sum(1 for gi, r in proj_items if r["label"] == 0 and best_preds[gi] == 0)

        tp_f = tp_orig - tp_removed
        fp_f = fp_orig - fp_removed
        fn_f = fn_orig + tp_removed

        p_f = tp_f / (tp_f + fp_f) if (tp_f + fp_f) > 0 else 0
        r_f = tp_f / (tp_f + fn_f) if (tp_f + fn_f) > 0 else 0
        f1_f = 2*p_f*r_f/(p_f+r_f) if (p_f+r_f) > 0 else 0
        delta = f1_f - f1_o
        avg_delta += delta

        out(f"| {proj} | {p_o:.3f} | {r_o:.3f} | {f1_o:.3f} | "
            f"{p_f:.3f} | {r_f:.3f} | {f1_f:.3f} | {delta:+.3f} |")

    out(f"| **Average** | | | | | | | **{avg_delta/5:+.3f}** |")
    out()

    # ── Synthesis ─────────────────────────────────────────────────────────────

    out("## Synthesis")
    out()
    out("### Strategy Comparison")
    out()
    out("| Strategy | FPs Caught | TPs Killed | Net | Filter Prec | Acc |")
    out("|----------|------------|------------|-----|-------------|-----|")
    for sk, si in STRATEGIES.items():
        r = all_strategy_results[sk]
        out(f"| {si['name']} | {r['fp_caught']}/{n_fp} | {r['tp_killed']}/{n_tp} | "
            f"{r['net']:+d} | {r['filt_prec']:.0%} | {r['accuracy']:.0%} |")
    out()

    out("### Comparison with Non-LLM Approaches")
    out()
    out("| Approach | FPs Caught | TPs Killed | Net | Generalizes? |")
    out("|----------|------------|------------|-----|-------------|")
    out(f"| Rule-based (≥2 rules) | 23/40 | 1/148 | +22 | Teammates only |")
    out(f"| Rule-based (≥3 rules) | 15/40 | 0/148 | +15 | Teammates only |")
    out(f"| Relative framing (emb) | 16/40 | 10/148 | +6 | Partial |")
    out(f"| Sentence embedding RF | AUC 0.805 | - | - | No (LOPO fails) |")
    for sk, si in STRATEGIES.items():
        r = all_strategy_results[sk]
        out(f"| LLM: {si['name'][:30]} | {r['fp_caught']}/{n_fp} | {r['tp_killed']}/{n_tp} | "
            f"{r['net']:+d} | Zero-shot |")
    out()

    out("### Key Findings")
    out()
    out("(Filled after results)")
    out()

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nWritten to {OUTPUT_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
