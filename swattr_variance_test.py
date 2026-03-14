#!/usr/bin/env python3
"""
Variance test: Run the v21 SWATTR reasoning guide multiple times
with different cache keys to measure stochastic LLM variance.
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

# Import from main script
sys.path.insert(0, str(Path(__file__).parent))
from swattr_llm_fewshot import (
    ABSTRACT_EXAMPLES, FEWSHOT_TEMPLATE,
    load_gs_sad_sam, load_result_sad_sam, load_text,
    load_model_element_info, query_claude, parse_batch_response,
    make_items_text
)

N_RUNS = 5


def main():
    # Collect records
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

    per_proj = defaultdict(list)
    for i, r in enumerate(records):
        per_proj[r["project"]].append((i, r))

    print(f"Data: {n_tp} TPs + {n_fp} FPs = {len(records)} links")
    print(f"Running {N_RUNS} independent trials...\n")

    all_run_results = []

    for run in range(N_RUNS):
        print(f"=== Run {run+1}/{N_RUNS} ===")
        preds = {}

        for proj in PROJECTS:
            proj_items = per_proj[proj]
            proj_records = [r for _, r in proj_items]
            items_text = make_items_text(proj_records)
            prompt = FEWSHOT_TEMPLATE.format(
                examples=ABSTRACT_EXAMPLES, project=proj, items=items_text
            )

            cache_key = f"variance_run{run+1}_{proj}"
            print(f"  {proj}: {len(proj_records)} links...", end="", flush=True)

            response = query_claude(prompt, cache_key=cache_key)

            if response:
                verdicts = parse_batch_response(response, len(proj_records))
                for j, (global_idx, _) in enumerate(proj_items):
                    preds[global_idx] = verdicts[j]
                no_link = sum(1 for v in verdicts if v == 0)
                print(f" {no_link} NO_LINK")
            else:
                print(f" FAILED")
                for global_idx, _ in proj_items:
                    preds[global_idx] = 1

            time.sleep(1)

        # Compute metrics
        tp_kept = sum(1 for i, r in enumerate(records) if r["label"] == 1 and preds.get(i, 1) == 1)
        tp_killed = n_tp - tp_kept
        fp_caught = sum(1 for i, r in enumerate(records) if r["label"] == 0 and preds.get(i, 1) == 0)
        fp_missed = n_fp - fp_caught

        # Per-project
        proj_stats = {}
        for proj in PROJECTS:
            proj_items = per_proj[proj]
            p_tp = sum(1 for gi, r in proj_items if r["label"] == 1)
            p_fp = sum(1 for gi, r in proj_items if r["label"] == 0)
            p_tp_killed = sum(1 for gi, r in proj_items if r["label"] == 1 and preds.get(gi, 1) == 0)
            p_fp_caught = sum(1 for gi, r in proj_items if r["label"] == 0 and preds.get(gi, 1) == 0)
            proj_stats[proj] = {"tp": p_tp, "fp": p_fp, "tp_killed": p_tp_killed, "fp_caught": p_fp_caught}

        # Identify which specific items were misclassified
        tp_killed_items = []
        fp_missed_items = []
        for i, r in enumerate(records):
            if r["label"] == 1 and preds.get(i, 1) == 0:
                tp_killed_items.append(f"{r['project']} S{r['sent_num']}×{r['elem_name']}")
            if r["label"] == 0 and preds.get(i, 1) == 1:
                fp_missed_items.append(f"{r['project']} S{r['sent_num']}×{r['elem_name']}")

        run_result = {
            "fp_caught": fp_caught, "fp_missed": fp_missed,
            "tp_killed": tp_killed, "tp_kept": tp_kept,
            "net": fp_caught - tp_killed,
            "proj_stats": proj_stats,
            "tp_killed_items": tp_killed_items,
            "fp_missed_items": fp_missed_items,
        }
        all_run_results.append(run_result)

        print(f"  → FPs caught: {fp_caught}/{n_fp}, TPs killed: {tp_killed}/{n_tp}, Net: +{fp_caught - tp_killed}")
        if tp_killed_items:
            print(f"    TPs killed: {', '.join(tp_killed_items)}")
        if fp_missed_items:
            print(f"    FPs missed: {', '.join(fp_missed_items)}")
        print()

    # Summary
    print("=" * 70)
    print("VARIANCE SUMMARY")
    print("=" * 70)
    print()

    fps = [r["fp_caught"] for r in all_run_results]
    tps = [r["tp_killed"] for r in all_run_results]
    nets = [r["net"] for r in all_run_results]

    print(f"{'Run':<6} {'FPs caught':>12} {'TPs killed':>12} {'Net':>6}")
    print("-" * 40)
    for i, r in enumerate(all_run_results):
        print(f"  {i+1:<4} {r['fp_caught']:>8}/{n_fp}   {r['tp_killed']:>8}/{n_tp}   +{r['net']:>3}")
    print("-" * 40)
    print(f"  Mean {sum(fps)/len(fps):>8.1f}/{n_fp}   {sum(tps)/len(tps):>8.1f}/{n_tp}   +{sum(nets)/len(nets):>3.1f}")
    print(f"  Min  {min(fps):>8}/{n_fp}   {min(tps):>8}/{n_tp}   +{min(nets):>3}")
    print(f"  Max  {max(fps):>8}/{n_fp}   {max(tps):>8}/{n_tp}   +{max(nets):>3}")

    import statistics
    if len(fps) > 1:
        print(f"  Std  {statistics.stdev(fps):>8.2f}        {statistics.stdev(tps):>8.2f}        {statistics.stdev(nets):>5.2f}")
    print()

    # Item-level stability
    all_tp_killed = defaultdict(int)
    all_fp_missed = defaultdict(int)
    for r in all_run_results:
        for item in r["tp_killed_items"]:
            all_tp_killed[item] += 1
        for item in r["fp_missed_items"]:
            all_fp_missed[item] += 1

    if all_fp_missed:
        print("FP miss frequency (how often each FP was missed across runs):")
        for item, count in sorted(all_fp_missed.items(), key=lambda x: -x[1]):
            print(f"  {item}: {count}/{N_RUNS} runs ({count/N_RUNS:.0%})")
        print()

    if all_tp_killed:
        print("TP kill frequency (how often each TP was wrongly killed):")
        for item, count in sorted(all_tp_killed.items(), key=lambda x: -x[1]):
            print(f"  {item}: {count}/{N_RUNS} runs ({count/N_RUNS:.0%})")
        print()

    # Per-project variance
    print("Per-project FP catch rate across runs:")
    print(f"{'Project':<16} " + " ".join(f"{'R'+str(i+1):>4}" for i in range(N_RUNS)) + "  Mean")
    print("-" * (16 + 5*N_RUNS + 6))
    for proj in PROJECTS:
        catches = [r["proj_stats"][proj]["fp_caught"] for r in all_run_results]
        totals = all_run_results[0]["proj_stats"][proj]["fp"]
        if totals > 0:
            vals = " ".join(f"{c:>3}/{totals}" for c in catches)
            print(f"{proj:<16} {vals}  {sum(catches)/len(catches):.1f}/{totals}")
    print()


if __name__ == "__main__":
    main()
