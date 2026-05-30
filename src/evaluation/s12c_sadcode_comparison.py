#!/usr/bin/env python3
"""
S12C / S12E SAD-CODE vs TransArc SAD-CODE — Comprehensive Metrics Comparison

Ablation SAD-SAM pipeline:
    S-Linker1X SAD-SAM links  (from ../llm-sad-sam-v45 ablation results)
    × ARDoCo standalone SAM-CODE links  (ARCOTL, from transarc-emp results)
    → transitive SAD-CODE result

Systems compared:
    TransArc  — traditional pipeline
    S12C      — s_linker12c SAD-SAM + ARCOTL SAM-CODE
    S12E      — s_linker12e SAD-SAM + ARCOTL SAM-CODE

Metrics computed at four levels (per evaluation_critique.py):
    1. File-level    : each (sentence, file) is one data point
    2. Decision-level: each raw gold entry (sentence, dir_or_file) is one data point
                       TP if ≥50% of its enrolled files are hit
    3. Component-level: (sentence, component_name) collapsed via SAM-CODE gold
    4. Weighted-file : each enrolled link weighted by 1/block_size

Output: reports/S12C_VS_TRANSARC.csv
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (
    PROJECTS,
    load_code_model_files,
    enroll_gold_standard,
    load_gs_sad_code_raw,
    load_gs_sam_code_raw,
    load_result_sad_code,
    load_result_sam_code_standalone,
    load_model_element_names,
    calc_metrics,
)

ABLATION_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/ablation_results")
OUTPUT_CSV   = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/S12C_VS_TRANSARC.csv")

# Ablation variants to include alongside TransArc
ABLATION_SYSTEMS = ["s_linker12c", "s_linker12e"]


# ─── Loaders ──────────────────────────────────────────────────────────────────

def load_ablation_sad_sam(variant, project):
    """Load ablation SAD-SAM links → set of (component_id, sentence_str)."""
    path = ABLATION_DIR / f"{variant}_{project}_links.csv"
    links = set()
    with open(path) as f:
        for row in csv.DictReader(f):
            comp_id = row["component_id"].strip()
            sent = str(row["sentence"].strip())
            if comp_id and sent:
                links.add((comp_id, sent))
    return links


def compose_sad_code(ablation_sad_sam, sam_code_standalone):
    """Transitively compose ablation SAD-SAM × ARDoCo SAM-CODE → SAD-CODE result.

    ablation_sad_sam   : set of (ae_id, sentence_str)
    sam_code_standalone: set of (ae_id, code_path)  [already normalized]

    Returns set of (sentence_str, code_path).
    """
    model_to_codes = defaultdict(set)
    for ae_id, code_path in sam_code_standalone:
        model_to_codes[ae_id].add(code_path)

    result = set()
    for ae_id, sentence in ablation_sad_sam:
        for code in model_to_codes.get(ae_id, ()):
            result.add((sentence, code))
    return result


# ─── Gold standard helpers ────────────────────────────────────────────────────

def build_raw_to_enrolled(raw_entries, code_model_files):
    """Return (enrolled set, raw_to_enrolled dict, enrolled_to_raw dict)."""
    enrolled = set()
    raw_to_enrolled = defaultdict(set)
    enrolled_to_raw = {}
    for sid, raw_path in raw_entries:
        raw_key = (sid, raw_path)
        if raw_path.endswith("/"):
            for fp in code_model_files:
                if fp.startswith(raw_path):
                    entry = (sid, fp)
                    enrolled.add(entry)
                    raw_to_enrolled[raw_key].add(entry)
                    enrolled_to_raw[entry] = raw_key
        else:
            entry = (sid, raw_path)
            enrolled.add(entry)
            raw_to_enrolled[raw_key].add(entry)
            enrolled_to_raw[entry] = raw_key
    return enrolled, dict(raw_to_enrolled), enrolled_to_raw


# ─── Metric helpers ───────────────────────────────────────────────────────────

def compute_decision(enrolled, result, raw_to_enrolled):
    """Decision-level: raw entry is TP if ≥50% enrolled files hit."""
    decision_tp = decision_fn = 0
    for raw_key, enrolled_set in raw_to_enrolled.items():
        if not enrolled_set:
            continue
        n_hit = sum(1 for e in enrolled_set if e in result)
        if n_hit >= len(enrolled_set) * 0.5:
            decision_tp += 1
        else:
            decision_fn += 1

    fp_dirs = set()
    for s, c in (result - enrolled):
        parts = c.rsplit("/", 1)
        fp_dirs.add((s, parts[0] + "/") if len(parts) == 2 else (s, c))
    decision_fp = len(fp_dirs)

    p = decision_tp / (decision_tp + decision_fp) if (decision_tp + decision_fp) else 0
    r = decision_tp / (decision_tp + decision_fn) if (decision_tp + decision_fn) else 0
    f1 = 2 * p * r / (p + r) if (p + r) else 0
    return {"tp": decision_tp, "fp": decision_fp, "fn": decision_fn, "p": p, "r": r, "f1": f1}


def compute_component(enrolled, result, file_to_comps):
    """Component-level: collapse (sentence, file) → (sentence, component_name)."""
    def to_comp_set(link_set):
        out = set()
        for s, c in link_set:
            comps = file_to_comps.get(c, set())
            for comp in comps:
                out.add((s, comp))
            if not comps:
                out.add((s, c))
        return out

    gold_comp   = to_comp_set(enrolled)
    result_comp = to_comp_set(result)
    p, r, f1, tp, fp, fn = calc_metrics(gold_comp, result_comp)
    return {"tp": tp, "fp": fp, "fn": fn, "p": p, "r": r, "f1": f1}


def compute_weighted(enrolled, result, enrolled_to_raw, raw_to_enrolled):
    """Weighted-file: each enrolled link weighted by 1/block_size."""
    weights = {
        entry: 1.0 / len(raw_to_enrolled[enrolled_to_raw[entry]])
        if entry in enrolled_to_raw else 1.0
        for entry in enrolled
    }

    w_tp = sum(weights.get(e, 0) for e in (enrolled & result))
    w_fn = sum(weights.get(e, 0) for e in (enrolled - result))

    fp_by_dir = defaultdict(list)
    for s, c in (result - enrolled):
        parts = c.rsplit("/", 1)
        fp_by_dir[(s, parts[0] + "/") if len(parts) == 2 else (s, c)].append((s, c))
    w_fp = float(len(fp_by_dir))

    p  = w_tp / (w_tp + w_fp) if (w_tp + w_fp) else 0
    r  = w_tp / (w_tp + w_fn) if (w_tp + w_fn) else 0
    f1 = 2 * p * r / (p + r)  if (p + r)       else 0
    return {"p": p, "r": r, "f1": f1}


def all_metrics(result, enrolled, raw_to_enrolled, enrolled_to_raw, file_to_comps):
    """Return all four metric levels for one system result."""
    fp, fr, ff1, ftp, ffp, ffn = calc_metrics(enrolled, result)
    dec  = compute_decision(enrolled, result, raw_to_enrolled)
    comp = compute_component(enrolled, result, file_to_comps)
    wt   = compute_weighted(enrolled, result, enrolled_to_raw, raw_to_enrolled)

    def pct(v): return round(v * 100, 1)

    return {
        "n_links": len(result),
        "file_TP": ftp,        "file_FP": ffp,        "file_FN": ffn,
        "file_P":  pct(fp),    "file_R":  pct(fr),    "file_F1": pct(ff1),
        "dec_TP":  dec["tp"],  "dec_FP":  dec["fp"],  "dec_FN":  dec["fn"],
        "dec_P":   pct(dec["p"]),  "dec_R":  pct(dec["r"]),  "dec_F1": pct(dec["f1"]),
        "comp_TP": comp["tp"], "comp_FP": comp["fp"], "comp_FN": comp["fn"],
        "comp_P":  pct(comp["p"]), "comp_R": pct(comp["r"]), "comp_F1": pct(comp["f1"]),
        "wt_P":    pct(wt["p"]),   "wt_R":   pct(wt["r"]),   "wt_F1":  pct(wt["f1"]),
    }


def sys_cols(prefix, m, include_counts=True):
    """Flatten one system's all_metrics dict into CSV columns."""
    cols = {f"{prefix}_links": m["n_links"]}
    for level, has_counts in [("file", True), ("dec", True), ("comp", True), ("wt", False)]:
        if has_counts and include_counts:
            cols[f"{prefix}_{level}_TP"] = m[f"{level}_TP"]
            cols[f"{prefix}_{level}_FP"] = m[f"{level}_FP"]
            cols[f"{prefix}_{level}_FN"] = m[f"{level}_FN"]
        cols[f"{prefix}_{level}_P"]  = m[f"{level}_P"]
        cols[f"{prefix}_{level}_R"]  = m[f"{level}_R"]
        cols[f"{prefix}_{level}_F1"] = m[f"{level}_F1"]
    return cols


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    rows = []
    LEVELS = ("file", "dec", "comp", "wt")

    # Accumulate per-level F1 for macro average
    # Keys: "ta", "s_linker12c", "s_linker12e"
    all_systems = ["ta"] + ABLATION_SYSTEMS
    accum = {sys: {lvl: [] for lvl in LEVELS} for sys in all_systems}

    for proj in PROJECTS:
        code_model   = load_code_model_files(proj)
        raw_entries  = list(load_gs_sad_code_raw(proj))
        enrolled, raw_to_enrolled, enrolled_to_raw = build_raw_to_enrolled(raw_entries, code_model)

        # file → component name map via SAM-CODE gold
        sam_raw      = load_gs_sam_code_raw(proj)
        sam_enrolled = enroll_gold_standard(sam_raw, code_model)
        names        = load_model_element_names(proj)
        file_to_comps = defaultdict(set)
        for ae, fp in sam_enrolled:
            file_to_comps[fp].add(names.get(ae, ae))

        ctx = (enrolled, raw_to_enrolled, enrolled_to_raw, file_to_comps)

        # TransArc
        ta_m = all_metrics(load_result_sad_code(proj), *ctx)

        # Ablation systems (shared SAM-CODE standalone)
        sam_code_sa = load_result_sam_code_standalone(proj)
        abl_m = {}
        for variant in ABLATION_SYSTEMS:
            sad_sam = load_ablation_sad_sam(variant, proj)
            abl_m[variant] = all_metrics(compose_sad_code(sad_sam, sam_code_sa), *ctx)

        # Accumulate for macro
        for lvl in LEVELS:
            key = "wt_F1" if lvl == "wt" else f"{lvl}_F1"
            accum["ta"][lvl].append(ta_m[key])
            for variant in ABLATION_SYSTEMS:
                accum[variant][lvl].append(abl_m[variant][key])

        # Build row
        row = {
            "dataset":      proj,
            "gold_enrolled": len(enrolled),
            "gold_raw":      len(raw_entries),
            **sys_cols("ta",    ta_m),
            **sys_cols("s12c",  abl_m["s_linker12c"]),
            **sys_cols("s12e",  abl_m["s_linker12e"]),
        }
        # Deltas vs TransArc
        for variant, prefix in zip(ABLATION_SYSTEMS, ["s12c", "s12e"]):
            for lvl in LEVELS:
                key = "wt_F1" if lvl == "wt" else f"{lvl}_F1"
                row[f"delta_{prefix}_{lvl}_F1"] = round(abl_m[variant][key] - ta_m[key], 1)

        rows.append(row)

        print(f"{proj:15s}  "
              f"file: TA={ta_m['file_F1']:5.1f} "
              f"S12C={abl_m['s_linker12c']['file_F1']:5.1f} "
              f"S12E={abl_m['s_linker12e']['file_F1']:5.1f}  |  "
              f"dec: TA={ta_m['dec_F1']:5.1f} "
              f"S12C={abl_m['s_linker12c']['dec_F1']:5.1f} "
              f"S12E={abl_m['s_linker12e']['dec_F1']:5.1f}  |  "
              f"comp: TA={ta_m['comp_F1']:5.1f} "
              f"S12C={abl_m['s_linker12c']['comp_F1']:5.1f} "
              f"S12E={abl_m['s_linker12e']['comp_F1']:5.1f}")

    # ── Macro averages row ────────────────────────────────────────────────────
    def _avg(lst): return round(sum(lst) / len(lst), 1) if lst else 0.0

    macro = {"dataset": "MACRO_AVG", "gold_enrolled": "", "gold_raw": ""}
    for sys_key, prefix in [("ta", "ta"), ("s_linker12c", "s12c"), ("s_linker12e", "s12e")]:
        macro[f"{prefix}_links"] = ""
        for level in ("file", "dec", "comp"):
            for col in ("TP", "FP", "FN"):
                macro[f"{prefix}_{level}_{col}"] = ""
            macro[f"{prefix}_{level}_P"]  = ""
            macro[f"{prefix}_{level}_R"]  = ""
            macro[f"{prefix}_{level}_F1"] = _avg(accum[sys_key][level])
        macro[f"{prefix}_wt_P"]  = ""
        macro[f"{prefix}_wt_R"]  = ""
        macro[f"{prefix}_wt_F1"] = _avg(accum[sys_key]["wt"])

    for prefix, sys_key in [("s12c", "s_linker12c"), ("s12e", "s_linker12e")]:
        for lvl in LEVELS:
            macro[f"delta_{prefix}_{lvl}_F1"] = round(
                _avg(accum[sys_key][lvl]) - _avg(accum["ta"][lvl]), 1
            )

    rows.append(macro)

    # ── Write CSV ─────────────────────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWritten: {OUTPUT_CSV}")
    print(f"\n{'':15s}  {'file F1':>30}   {'dec F1':>30}   {'comp F1':>30}")
    print(f"{'':15s}  {'TA':>8} {'S12C':>8} {'S12E':>8}   {'TA':>8} {'S12C':>8} {'S12E':>8}   {'TA':>8} {'S12C':>8} {'S12E':>8}")
    print("-" * 100)
    for row in rows[:-1]:
        print(f"{row['dataset']:15s}  "
              f"{row['ta_file_F1']:8} {row['s12c_file_F1']:8} {row['s12e_file_F1']:8}   "
              f"{row['ta_dec_F1']:8} {row['s12c_dec_F1']:8} {row['s12e_dec_F1']:8}   "
              f"{row['ta_comp_F1']:8} {row['s12c_comp_F1']:8} {row['s12e_comp_F1']:8}")
    print("-" * 100)
    m = rows[-1]
    print(f"{'MACRO':15s}  "
          f"{m['ta_file_F1']:8} {m['s12c_file_F1']:8} {m['s12e_file_F1']:8}   "
          f"{m['ta_dec_F1']:8} {m['s12c_dec_F1']:8} {m['s12e_dec_F1']:8}   "
          f"{m['ta_comp_F1']:8} {m['s12c_comp_F1']:8} {m['s12e_comp_F1']:8}")


if __name__ == "__main__":
    main()
