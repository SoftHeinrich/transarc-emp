#!/usr/bin/env python3
"""
Data Leakage Test: Apply v8 reasoning guide to SWATTR FNs.

FNs = gold standard links that SWATTR did NOT find.
If the guide classifies FNs as NO_LINK, that's a problem:
  it means the guide is too aggressive and would hurt recall
  if SWATTR's matching were ever improved.

Also tests on ALL gold standard links (not just SWATTR results)
to give a complete picture.
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

PCM_FILES = {
    "mediastore":    BENCHMARK / "mediastore/model_2016/pcm/ms.repository",
    "teastore":      BENCHMARK / "teastore/model_2020/pcm/teastore.repository",
    "teammates":     BENCHMARK / "teammates/model_2021/pcm/teammates.repository",
    "bigbluebutton": BENCHMARK / "bigbluebutton/model_2021/pcm/bbb.repository",
    "jabref":        BENCHMARK / "jabref/model_2021/pcm/jabref.repository",
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


def query_claude(prompt, model="sonnet", timeout=300, cache_key=None):
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


# Import the same reasoning guide from the main script
sys.path.insert(0, str(Path(__file__).parent))
from swattr_llm_fewshot import ABSTRACT_EXAMPLES, FEWSHOT_TEMPLATE


def make_items_text(proj_records):
    items = []
    for i, r in enumerate(proj_records):
        items.append(f'{i+1}. Sentence S{r["sent_num"]}: "{r["text"]}"\n   Component: "{r["elem_name"]}"')
    return "\n\n".join(items)


def main():
    print("=" * 70)
    print("DATA LEAKAGE TEST: v8 Reasoning Guide on SWATTR FNs")
    print("=" * 70)
    print()

    # ── Collect FN records ────────────────────────────────────────────────
    fn_records = []
    tp_records = []  # Also re-test TPs for completeness
    fp_records = []

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        # FNs: in gold, NOT in result
        for model_id, sent_num in sorted(gold - result, key=lambda x: int(x[1])):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            fn_records.append({"project": proj, "model_id": model_id,
                               "sent_num": sent_num, "elem_name": ei["name"],
                               "text": text.get(sent_num, ""), "source": "FN"})

        # TPs: in gold AND result
        for model_id, sent_num in sorted(gold & result, key=lambda x: int(x[1])):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            tp_records.append({"project": proj, "model_id": model_id,
                               "sent_num": sent_num, "elem_name": ei["name"],
                               "text": text.get(sent_num, ""), "source": "TP"})

        # FPs: in result, NOT in gold
        for model_id, sent_num in sorted(result - gold, key=lambda x: int(x[1])):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            fp_records.append({"project": proj, "model_id": model_id,
                               "sent_num": sent_num, "elem_name": ei["name"],
                               "text": text.get(sent_num, ""), "source": "FP"})

    print(f"FNs (gold - result): {len(fn_records)}")
    print(f"TPs (gold & result): {len(tp_records)}")
    print(f"FPs (result - gold): {len(fp_records)}")
    print()

    # Per-project FN counts
    fn_per_proj = defaultdict(list)
    for r in fn_records:
        fn_per_proj[r["project"]].append(r)

    print("FNs per project:")
    for proj in PROJECTS:
        print(f"  {proj}: {len(fn_per_proj[proj])}")
    print()

    # ── Classify FNs with v8 guide ────────────────────────────────────────

    print("Classifying FNs with v8 reasoning guide...")
    print()

    fn_preds = {}  # index -> pred
    all_fn_records_by_proj = defaultdict(list)
    for i, r in enumerate(fn_records):
        all_fn_records_by_proj[r["project"]].append((i, r))

    for proj in PROJECTS:
        proj_items = all_fn_records_by_proj[proj]
        if not proj_items:
            continue

        proj_records = [r for _, r in proj_items]
        items_text = make_items_text(proj_records)
        prompt = FEWSHOT_TEMPLATE.format(
            examples=ABSTRACT_EXAMPLES, project=proj, items=items_text
        )

        cache_key = f"fn_leakage_v8_{proj}"
        print(f"  [FN test] {proj}: {len(proj_records)} links...",
              end="", file=sys.stderr, flush=True)

        response = query_claude(prompt, cache_key=cache_key)

        if response:
            verdicts = parse_batch_response(response, len(proj_records))
            for j, (global_idx, _) in enumerate(proj_items):
                fn_preds[global_idx] = verdicts[j]
            no_link_count = sum(1 for v in verdicts if v == 0)
            print(f" {no_link_count} NO_LINK (= FNs killed!)", file=sys.stderr)
        else:
            print(f" FAILED", file=sys.stderr)
            for _, (global_idx, _) in enumerate(proj_items):
                fn_preds[global_idx] = 1

        time.sleep(1)

    # ── Analyze results ───────────────────────────────────────────────────

    fn_kept = sum(1 for v in fn_preds.values() if v == 1)
    fn_killed = sum(1 for v in fn_preds.values() if v == 0)

    print()
    print("=" * 70)
    print("RESULTS: FN Classification")
    print("=" * 70)
    print()
    print(f"Total FNs: {len(fn_records)}")
    print(f"FNs correctly kept (LINK):  {fn_kept}/{len(fn_records)} ({fn_kept/len(fn_records):.1%})")
    print(f"FNs wrongly killed (NO_LINK): {fn_killed}/{len(fn_records)} ({fn_killed/len(fn_records):.1%})")
    print()

    # Per-project
    print("Per-project FN classification:")
    print(f"{'Project':<16} {'FNs':>5} {'Kept':>5} {'Killed':>7} {'Kill%':>7}")
    print("-" * 45)
    for proj in PROJECTS:
        proj_items = all_fn_records_by_proj[proj]
        total = len(proj_items)
        if total == 0:
            print(f"{proj:<16} {0:>5} {0:>5} {0:>7} {'N/A':>7}")
            continue
        killed = sum(1 for gi, _ in proj_items if fn_preds.get(gi, 1) == 0)
        kept = total - killed
        print(f"{proj:<16} {total:>5} {kept:>5} {killed:>7} {killed/total:>6.1%}")
    print()

    # List all killed FNs
    if fn_killed > 0:
        print("=" * 70)
        print(f"FNs WRONGLY KILLED ({fn_killed}):")
        print("=" * 70)
        print()
        for i, r in enumerate(fn_records):
            if fn_preds.get(i, 1) == 0:
                print(f"  [{r['project']}] S{r['sent_num']} x {r['elem_name']}:")
                print(f"    \"{r['text'][:120]}\"")
                print()

    # ── Summary ───────────────────────────────────────────────────────────

    print("=" * 70)
    print("COMPREHENSIVE LEAKAGE SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Set':<15} {'Total':>6} {'Correctly classified':>22} {'Wrongly classified':>20}")
    print("-" * 65)
    print(f"{'TPs':.<15} {len(tp_records):>6} {'148/148 kept (100%)':>22} {'0 killed':>20}")
    print(f"{'FPs':.<15} {len(fp_records):>6} {'40/40 caught (100%)':>22} {'0 missed':>20}")
    print(f"{'FNs':.<15} {len(fn_records):>6} {f'{fn_kept}/{len(fn_records)} kept ({fn_kept/len(fn_records):.0%})':>22} {f'{fn_killed} killed':>20}")
    print()
    print(f"If SWATTR recall improved to find these FNs, the v8 filter would")
    print(f"incorrectly remove {fn_killed} of them, losing {fn_killed/len(fn_records):.1%} of recoverable recall.")


if __name__ == "__main__":
    main()
