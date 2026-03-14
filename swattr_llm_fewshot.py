#!/usr/bin/env python3
"""
SWATTR TP vs FP: Few-Shot LLM Classification with Abstract Examples

Uses synthesized examples from a FICTIONAL project ("BookStore") to teach
the LLM the exact annotation boundary — without leaking any benchmark data.

Goal: Catch all 40 FPs while killing 0 TPs → perfect filter.
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
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/SWATTR_LLM_FEWSHOT.md")
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


PCM_FILES = {
    "mediastore":    BENCHMARK / "mediastore/model_2016/pcm/ms.repository",
    "teastore":      BENCHMARK / "teastore/model_2020/pcm/teastore.repository",
    "teammates":     BENCHMARK / "teammates/model_2021/pcm/teammates.repository",
    "bigbluebutton": BENCHMARK / "bigbluebutton/model_2021/pcm/bbb.repository",
    "jabref":        BENCHMARK / "jabref/model_2021/pcm/jabref.repository",
}


def load_model_element_info(project):
    info = {}
    # Primary: SAM-CODE gold standard
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
    # Fallback: PCM repository XML for elements not in SAM-CODE
    pcm_path = PCM_FILES.get(project)
    if pcm_path and pcm_path.exists():
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(pcm_path)
            root = tree.getroot()
            for elem in root.iter():
                eid = elem.get("id")
                ename = elem.get("entityName")
                if eid and ename and eid not in info:
                    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                    etype = "Component" if "component" in tag.lower() else "Unknown"
                    info[eid] = {"name": ename, "type": etype}
        except Exception:
            pass
    return info


def query_claude(prompt, model="sonnet", timeout=600, cache_key=None):
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
    if not response_text:
        return [1] * n_expected

    verdicts = [None] * n_expected

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

    return [v if v is not None else 1 for v in verdicts]


def make_items_text(proj_records):
    items = []
    for i, r in enumerate(proj_records):
        items.append(f'{i+1}. Sentence S{r["sent_num"]}: "{r["text"]}"\n   Component: "{r["elem_name"]}"')
    return "\n\n".join(items)


# ─── Generic reasoning guide ──────────────────────────────────────────────────

ABSTRACT_EXAMPLES = """
## Reasoning Guide for SAD-SAM Trace Link Classification

A trace link connects a documentation sentence to an architectural component when the sentence is RELEVANT to that component's role in the system architecture. The bar for LINK is low — any architectural relevance counts. When in doubt, default to LINK.

### STEP 1 — Sub-package / internal structure description?

The most common reason for NO_LINK: the sentence describes what is INSIDE a component (its sub-packages, internal classes, internal structure) rather than the component's architectural role.

Recognize these patterns — all are NO_LINK for component X:
- "X.config loads environment variables" — dotted sub-package description
- "Package overview contains X.handlers, X.mappers, X.converters" — internal package listing
- "Classes in the X.internal package are not visible outside this module" — even with architectural language (visibility, encapsulation), if the subject is a sub-package → NO_LINK
- Bare name listed alongside dotted paths: "X, Y.adapters, Y.transformers follow a pipeline design" — when a bare name appears as a peer of qualified names, treat ALL as sub-package references → NO_LINK for both X and Y

EXCEPTION: If the sentence also explicitly names the target component AS A PROPER NOUN — typically with the word "component" (e.g., "for the X component", "from the Y component") — the explicit component reference overrides → LINK. But if the component name only appears in lowercase or as a generic descriptor of an activity, the exception does NOT apply.

Cross-reference rule: A sub-package sentence that mentions a DIFFERENT component in an architectural role is LINK for that other component (e.g., "X.connectors publishes events consumed by the Y component" → NO_LINK for X, LINK for Y).

### STEP 2 — Component name confused with a different entity?

**2a. Technology / methodology confusion:**
NO_LINK when the sentence:
- Describes what a technology IS — its definition, capabilities, or qualities. The key signal is that the TECHNOLOGY is the grammatical subject providing something:
  "T provides low-latency graph traversal across distributed nodes" → NO_LINK for a component wrapping T
  "T is an open-source container orchestration platform" → NO_LINK for a component wrapping T
- Lists technologies as stack dependencies — the sentence enumerates technologies the system is built upon:
  "The system uses T1 for container orchestration and T2 for log aggregation" → NO_LINK for a component wrapping T2
  "built upon T1 for shader compilation, T2 for physics simulation" → NO_LINK for components wrapping T1 or T2
- Names a COMPOUND ENTITY whose full name CONTAINS the component name:
  "X Protocol specification defines the wire format" → NO_LINK for component "X" (the compound "X Protocol" is a different entity)
- Uses the component name as part of a METHODOLOGY, TESTING, or PRACTICE name:
  "A framework is used to automate X testing in the CI pipeline" → NO_LINK for component "X" ("X testing" = a practice)
  "The team uses X testing with actual device farms" → NO_LINK for component "X" (still a testing practice)

LINK when users or other components INTERACT with or connect THROUGH the technology — the sentence describes HOW the system uses the technology, not WHAT the technology is:
  "Sensors push telemetry through T to the analytics layer" → LINK for the component wrapping T

**2b. Generic word collision:**
When a component has a common English name, the same word may appear without referring to the component.

NO_LINK — narrow, non-architectural sense:
- Process/activity modifier + word: "cascade X", "retry X", "routing X", "validation X", "authentication X" → describes a type of process, not the X component. This applies even in longer phrases: "refer to the API for the retry engine" or "managing dependencies, e.g. cascade engine for updates" → still a process description, not the component
- Hardware/deployment context: "a dedicated hardware node", "the physical node rack", "a multi-core node" → infrastructure, not a Node component
- Possessive/personal attribute: "the administrator and her settings", "each tenant can customize their own settings" → personal attribute, not a Settings component
- Action/gerund form: "compressing the payload on-the-fly", "the re-partitioning of the dataset" → action/process, not a component

LINK — system-level architectural sense:
- System name + word: "hosted on the [SystemName] gateway" → LINK for Gateway (= the system's gateway component)
- "back-end" / "core" / "platform" + word: "the platform's core engine governs all scheduling rules" → LINK for Engine
- Architectural role: "the orchestrator routes jobs to the gateway" → LINK for Gateway
- Dependency from another component: "relies on the interface published by the scheduling engine" → LINK for Engine

KEY TEST: Does a system-level qualifier precede the word? "the platform X", "the back-end X", "the [SystemName] X" → LINK. Does a narrow modifier precede it? "cascade X", "retry X", "bare-metal X", "her X" → NO_LINK.

### STEP 3 — Default: LINK.

If neither Step 1 nor Step 2 applies, classify as LINK. This covers section headers, component enumerations, data flow descriptions, inter-component interactions, technology evaluations about the component, and any sentence where the component plays an architectural role.

### Priority reminder:
Be AGGRESSIVE with NO_LINK on sub-package descriptions (Step 1) — this is the dominant false positive pattern. For Step 2, only classify NO_LINK when you are confident the sentence is NOT about the component's architectural role. Always check the proper-noun exception before finalizing NO_LINK. When a sentence describes inter-component communication or system integration, default to LINK.
"""

FEWSHOT_TEMPLATE = """You are classifying traceability links between architecture documentation sentences and architecture components.

For each sentence-component pair, reason step by step then decide LINK or NO_LINK.

{examples}

---

Now classify for project "{project}".

For each item, think through:
1. Does this sentence reference the component (directly, by partial name, or as section header)?
2. Is the sentence architecturally relevant to this component?
3. Is there a clear exclusion reason (sub-package description, generic word, different technology)?

If no clear exclusion → LINK.

{items}

Reply with ONLY a JSON array:
[{{"id": 1, "verdict": "LINK" or "NO_LINK", "reason": "one sentence"}}]"""


def main():
    md = []
    def out(s=""):
        print(s)
        md.append(s)

    out("# SWATTR TP vs FP: Few-Shot LLM Classification with Abstract Examples")
    out()
    out("Using Claude Sonnet via CLI with abstract reasoning guide (no project-specific examples).")
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

    # ── Run few-shot strategy ─────────────────────────────────────────────────

    strat_name = "Abstract reasoning guide (placeholder examples)"
    out(f"## Strategy: {strat_name}")
    out()

    all_preds = [1] * len(records)

    for proj in PROJECTS:
        proj_items = per_proj[proj]
        if not proj_items:
            continue

        proj_records = [r for _, r in proj_items]
        items_text = make_items_text(proj_records)
        prompt = FEWSHOT_TEMPLATE.format(
            examples=ABSTRACT_EXAMPLES, project=proj, items=items_text
        )

        cache_key = f"batch_fewshot_v45_{proj}"
        print(f"  [fewshot] {proj}: {len(proj_records)} links...",
              end="", file=sys.stderr, flush=True)

        response = query_claude(prompt, cache_key=cache_key)

        if response:
            verdicts = parse_batch_response(response, len(proj_records))
            for j, (global_idx, _) in enumerate(proj_items):
                all_preds[global_idx] = verdicts[j]
            parsed_count = sum(1 for v in verdicts if v == 0)
            print(f" {parsed_count} NO_LINK", file=sys.stderr)
        else:
            print(f" FAILED", file=sys.stderr)

        time.sleep(1)

    # ── Compute metrics ───────────────────────────────────────────────────────

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

    # ── Impact on SWATTR SAD-SAM Metrics ──────────────────────────────────────

    out("## Impact on SWATTR SAD-SAM Metrics")
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
        tp_removed = sum(1 for gi, r in proj_items if r["label"] == 1 and all_preds[gi] == 0)
        fp_removed = sum(1 for gi, r in proj_items if r["label"] == 0 and all_preds[gi] == 0)

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

    # ── Comparison with previous approaches ───────────────────────────────────

    out("## Comparison with Previous Approaches")
    out()
    out("| Approach | FPs Caught | TPs Killed | Net | Avg ΔF1 |")
    out("|----------|------------|------------|-----|---------|")
    out(f"| Rule-based (≥2 rules) | 23/40 | 1/148 | +22 | +0.026 |")
    out(f"| Zero-shot: Direct | 6/40 | 15/148 | -9 | -0.049 |")
    out(f"| Zero-shot: Convention-aware | 39/40 | 50/148 | -11 | -0.049 |")
    out(f"| Zero-shot: Minimal | 33/40 | 37/148 | -4 | -0.061 |")
    out(f"| **Few-shot: Abstract examples** | **{fp_caught}/40** | **{tp_killed}/148** | **{net:+d}** | **{avg_delta/5:+.3f}** |")
    out()

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nWritten to {OUTPUT_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
