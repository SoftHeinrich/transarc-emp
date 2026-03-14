#!/usr/bin/env python3
"""Quick 3-run variance test for rapid iteration."""
import sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from swattr_llm_fewshot import (
    ABSTRACT_EXAMPLES, FEWSHOT_TEMPLATE,
    load_gs_sad_sam, load_result_sad_sam, load_text,
    load_model_element_info, query_claude, parse_batch_response,
    make_items_text, PROJECTS
)

N_RUNS = 3

def run_variance(version_tag):
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

    print(f"\n{'='*60}")
    print(f"VARIANCE TEST: {version_tag} ({N_RUNS} runs)")
    print(f"{'='*60}")

    all_results = []
    for run in range(N_RUNS):
        preds = {}
        for proj in PROJECTS:
            proj_items = per_proj[proj]
            proj_records = [r for _, r in proj_items]
            items_text = make_items_text(proj_records)
            prompt = FEWSHOT_TEMPLATE.format(
                examples=ABSTRACT_EXAMPLES, project=proj, items=items_text
            )
            cache_key = f"qvar_{version_tag}_r{run+1}_{proj}"
            print(f"  R{run+1} {proj}...", end="", file=sys.stderr, flush=True)
            response = query_claude(prompt, cache_key=cache_key)
            if response:
                verdicts = parse_batch_response(response, len(proj_records))
                for j, (gi, _) in enumerate(proj_items):
                    preds[gi] = verdicts[j]
                print(f" {sum(1 for v in verdicts if v==0)}nl", end="", file=sys.stderr)
            else:
                for gi, _ in proj_items:
                    preds[gi] = 1
            time.sleep(0.5)
        print(file=sys.stderr)

        fp_caught = sum(1 for i, r in enumerate(records) if r["label"]==0 and preds.get(i,1)==0)
        tp_killed = sum(1 for i, r in enumerate(records) if r["label"]==1 and preds.get(i,1)==0)
        fp_missed = [f"{r['project']} S{r['sent_num']}×{r['elem_name']}" 
                     for i, r in enumerate(records) if r["label"]==0 and preds.get(i,1)==1]
        tp_killed_items = [f"{r['project']} S{r['sent_num']}×{r['elem_name']}"
                          for i, r in enumerate(records) if r["label"]==1 and preds.get(i,1)==0]
        all_results.append({"fp": fp_caught, "tp_kill": tp_killed, "missed": fp_missed, "killed": tp_killed_items})

    # Summary
    fps = [r["fp"] for r in all_results]
    tps = [r["tp_kill"] for r in all_results]
    
    print(f"\n{'Run':<5} {'FP caught':>10} {'TP killed':>10} {'Net':>5}")
    print("-"*35)
    for i, r in enumerate(all_results):
        print(f" R{i+1:<3} {r['fp']:>6}/40   {r['tp_kill']:>6}/148  +{r['fp']-r['tp_kill']:>3}")
    print("-"*35)
    print(f" Avg  {sum(fps)/len(fps):>6.1f}/40   {sum(tps)/len(tps):>6.1f}/148  +{sum(f-t for f,t in zip(fps,tps))/len(fps):>3.1f}")
    print(f" Min  {min(fps):>6}/40   worst-case net: +{min(f-t for f,t in zip(fps,tps)):>3}")

    # FP miss frequency
    miss_freq = defaultdict(int)
    for r in all_results:
        for item in r["missed"]:
            miss_freq[item] += 1
    print(f"\nFP miss frequency:")
    for item, cnt in sorted(miss_freq.items(), key=lambda x: -x[1]):
        print(f"  {item}: {cnt}/{N_RUNS}")

    kill_freq = defaultdict(int)
    for r in all_results:
        for item in r["killed"]:
            kill_freq[item] += 1
    if kill_freq:
        print(f"\nTP kill frequency:")
        for item, cnt in sorted(kill_freq.items(), key=lambda x: -x[1]):
            print(f"  {item}: {cnt}/{N_RUNS}")

    return {"mean_fp": sum(fps)/len(fps), "mean_tp": sum(tps)/len(tps),
            "min_fp": min(fps), "max_tp": max(tps), "miss_freq": dict(miss_freq)}

if __name__ == "__main__":
    run_variance(sys.argv[1] if len(sys.argv) > 1 else "v21")
