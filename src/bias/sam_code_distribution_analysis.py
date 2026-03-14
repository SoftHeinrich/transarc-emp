#!/usr/bin/env python3
"""
SAM-CODE Distribution-Level Analysis

Analyzes SAM-CODE link recovery results vs gold standard at the distribution level:
- Per-model-element TP/FP/FN breakdown
- Directory enrollment impact (raw vs enrolled gold sizes)
- Which specific code files are missed (FN) or wrongly included (FP)
- File extension / path pattern distributions
- Standalone vs TransArc-internal SAM-CODE comparison per model element
"""

import sys
from collections import defaultdict
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sam_code_raw,
    load_result_sam_code_standalone,
    load_transarc_intermediate_sam_code,
    load_model_element_names,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/SAM_CODE_DISTRIBUTION.md")


def file_extension(path):
    """Extract file extension from a path."""
    if "/" in path:
        fname = path.rsplit("/", 1)[1]
    else:
        fname = path
    if "." in fname:
        return "." + fname.rsplit(".", 1)[1]
    return "(no ext)"


def path_depth(path):
    """Count directory depth of a path."""
    return path.count("/")


def analyze_project(proj):
    """Full SAM-CODE distribution analysis for one project."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)

    # Gold standard: raw and enrolled
    gs_raw = load_gs_sam_code_raw(proj)
    gs_enrolled = enroll_gold_standard(gs_raw, code_model)

    # Results
    standalone = load_result_sam_code_standalone(proj)
    internal = load_transarc_intermediate_sam_code(proj)

    # --- Per-model-element breakdown ---

    # Collect all model element IDs from gold + results
    all_model_ids = set()
    for m, _ in gs_enrolled:
        all_model_ids.add(m)
    for m, _ in standalone:
        all_model_ids.add(m)
    for m, _ in internal:
        all_model_ids.add(m)

    # Raw gold: count entries per model element and how many are directories
    raw_per_model = defaultdict(lambda: {"total": 0, "dirs": 0, "files": 0})
    for m, c in gs_raw:
        raw_per_model[m]["total"] += 1
        if c.endswith("/"):
            raw_per_model[m]["dirs"] += 1
        else:
            raw_per_model[m]["files"] += 1

    # Enrolled gold per model element
    enrolled_per_model = defaultdict(set)
    for m, c in gs_enrolled:
        enrolled_per_model[m].add(c)

    # Standalone result per model element
    standalone_per_model = defaultdict(set)
    for m, c in standalone:
        standalone_per_model[m].add(c)

    # Internal result per model element
    internal_per_model = defaultdict(set)
    for m, c in internal:
        internal_per_model[m].add(c)

    # Per-model-element metrics
    model_rows = []
    for m in sorted(all_model_ids, key=lambda x: names.get(x, x)):
        gold_set = enrolled_per_model.get(m, set())
        sa_set = standalone_per_model.get(m, set())
        int_set = internal_per_model.get(m, set())

        sa_tp = gold_set & sa_set
        sa_fp = sa_set - gold_set
        sa_fn = gold_set - sa_set

        int_tp = gold_set & int_set
        int_fp = int_set - gold_set
        int_fn = gold_set - int_set

        raw_info = raw_per_model.get(m, {"total": 0, "dirs": 0, "files": 0})

        model_rows.append({
            "id": m,
            "name": names.get(m, m),
            "raw_total": raw_info["total"],
            "raw_dirs": raw_info["dirs"],
            "raw_files": raw_info["files"],
            "enrolled": len(gold_set),
            "enrollment_factor": len(gold_set) / raw_info["total"] if raw_info["total"] > 0 else 0,
            "sa_tp": len(sa_tp), "sa_fp": len(sa_fp), "sa_fn": len(sa_fn),
            "sa_result": len(sa_set),
            "sa_prec": len(sa_tp) / len(sa_set) if sa_set else 0,
            "sa_rec": len(sa_tp) / len(gold_set) if gold_set else 0,
            "int_tp": len(int_tp), "int_fp": len(int_fp), "int_fn": len(int_fn),
            "int_result": len(int_set),
            "int_prec": len(int_tp) / len(int_set) if int_set else 0,
            "int_rec": len(int_tp) / len(gold_set) if gold_set else 0,
            "sa_fp_set": sa_fp,
            "sa_fn_set": sa_fn,
            "int_fp_set": int_fp,
            "int_fn_set": int_fn,
            "gold_set": gold_set,
            # Files only in standalone but not in internal
            "sa_only": sa_set - int_set,
            "int_only": int_set - sa_set,
        })

    # --- File extension distribution of FPs and FNs ---
    sa_tps = gs_enrolled & standalone
    sa_fps = standalone - gs_enrolled
    sa_fns = gs_enrolled - standalone

    fp_ext = defaultdict(int)
    for _, c in sa_fps:
        fp_ext[file_extension(c)] += 1

    fn_ext = defaultdict(int)
    for _, c in sa_fns:
        fn_ext[file_extension(c)] += 1

    tp_ext = defaultdict(int)
    for _, c in sa_tps:
        tp_ext[file_extension(c)] += 1

    gold_ext = defaultdict(int)
    for _, c in gs_enrolled:
        gold_ext[file_extension(c)] += 1

    # --- Code file coverage: which files appear in gold but never recovered ---
    # Group by code file (across all model elements)
    gold_files = defaultdict(set)  # code_path -> set of model elements
    for m, c in gs_enrolled:
        gold_files[c].add(m)

    result_files = defaultdict(set)
    for m, c in standalone:
        result_files[c].add(m)

    never_recovered = set()
    partially_recovered = set()
    fully_recovered = set()
    for c, models in gold_files.items():
        recovered_models = set()
        for m in models:
            if (m, c) in standalone:
                recovered_models.add(m)
        if not recovered_models:
            never_recovered.add(c)
        elif recovered_models == models:
            fully_recovered.add(c)
        else:
            partially_recovered.add(c)

    # Files in result but not in gold at all (spurious files)
    spurious_files = set()
    for m, c in sa_fps:
        if c not in gold_files:
            spurious_files.add(c)

    return {
        "model_rows": model_rows,
        "gs_raw": gs_raw,
        "gs_enrolled": gs_enrolled,
        "standalone": standalone,
        "internal": internal,
        "fp_ext": dict(fp_ext),
        "fn_ext": dict(fn_ext),
        "tp_ext": dict(tp_ext),
        "gold_ext": dict(gold_ext),
        "never_recovered": never_recovered,
        "partially_recovered": partially_recovered,
        "fully_recovered": fully_recovered,
        "spurious_files": spurious_files,
        "sa_fps": sa_fps,
        "sa_fns": sa_fns,
    }


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# SAM-CODE Distribution-Level Analysis")
    out()
    out("Analysis of SAM-CODE link recovery results vs gold standard at the distribution level,")
    out("beyond aggregate precision/recall/F1 metrics.")
    out()

    all_results = {}
    for proj in PROJECTS:
        all_results[proj] = analyze_project(proj)

    # ─── 1. Enrollment Impact ─────────────────────────────────────────────

    out("## 1. Gold Standard Enrollment Impact")
    out()
    out("The SAM-CODE gold standard contains both directory-level and file-level entries.")
    out("Directory entries are expanded (enrolled) to individual files using the `.acm` code model.")
    out()
    out("| Project | Raw Entries | Directories | Files | Enrolled Entries | Expansion Factor |")
    out("|---------|-----------|------------|-------|-----------------|-----------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        raw = len(r["gs_raw"])
        dirs = sum(1 for _, c in r["gs_raw"] if c.endswith("/"))
        files = raw - dirs
        enrolled = len(r["gs_enrolled"])
        factor = enrolled / raw if raw else 0
        out(f"| {proj} | {raw} | {dirs} ({dirs/raw*100:.0f}%) | {files} ({files/raw*100:.0f}%) | {enrolled} | {factor:.1f}x |")

    out()

    # Per-model-element enrollment detail
    out("### Per-Model-Element Enrollment Detail")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        rows = r["model_rows"]
        # Only show if there's interesting enrollment
        has_dirs = any(mr["raw_dirs"] > 0 for mr in rows)
        if not has_dirs:
            continue

        out(f"#### {proj}")
        out()
        out("| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |")
        out("|--------------|-----------|------|-------|---------|--------|")

        for mr in sorted(rows, key=lambda x: x["enrollment_factor"], reverse=True):
            if mr["raw_total"] == 0:
                continue
            out(f"| {mr['name']} | {mr['raw_total']} | {mr['raw_dirs']} | {mr['raw_files']} | {mr['enrolled']} | {mr['enrollment_factor']:.1f}x |")

        out()

    # ─── 2. Per-Model-Element TP/FP/FN ───────────────────────────────────

    out("## 2. Per-Model-Element Standalone SAM-CODE Performance")
    out()
    out("TP/FP/FN breakdown for each architecture element in standalone SAM-CODE recovery.")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        rows = r["model_rows"]

        out(f"### {proj}")
        out()
        out("| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |")
        out("|--------------|------|--------|----|----|-----|-----------|--------|")

        for mr in sorted(rows, key=lambda x: x["enrolled"], reverse=True):
            if mr["enrolled"] == 0 and mr["sa_result"] == 0:
                continue
            out(f"| {mr['name']} | {mr['enrolled']} | {mr['sa_result']} | "
                f"{mr['sa_tp']} | {mr['sa_fp']} | {mr['sa_fn']} | "
                f"{mr['sa_prec']:.3f} | {mr['sa_rec']:.3f} |")

        # Totals
        t_gold = sum(mr["enrolled"] for mr in rows)
        t_result = sum(mr["sa_result"] for mr in rows)
        t_tp = sum(mr["sa_tp"] for mr in rows)
        t_fp = sum(mr["sa_fp"] for mr in rows)
        t_fn = sum(mr["sa_fn"] for mr in rows)
        t_p = t_tp / t_result if t_result else 0
        t_r = t_tp / t_gold if t_gold else 0
        out(f"| **TOTAL** | **{t_gold}** | **{t_result}** | **{t_tp}** | **{t_fp}** | **{t_fn}** | **{t_p:.3f}** | **{t_r:.3f}** |")
        out()

    # ─── 3. Standalone vs Internal SAM-CODE per model element ────────────

    out("## 3. Standalone vs TransArc-Internal SAM-CODE per Model Element")
    out()
    out("TransArc runs SAM-CODE internally on a subset of model elements (only those")
    out("found by SAD-SAM). This comparison shows which model elements lose coverage.")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        rows = r["model_rows"]

        out(f"### {proj}")
        out()
        out("| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |")
        out("|--------------|------|-----------------|--------|---------------|--------|--------------|")

        for mr in sorted(rows, key=lambda x: x["sa_rec"] - x["int_rec"], reverse=True):
            if mr["enrolled"] == 0 and mr["sa_result"] == 0 and mr["int_result"] == 0:
                continue
            loss = mr["sa_rec"] - mr["int_rec"]
            loss_str = f"{loss:+.3f}" if loss != 0 else "0.000"
            out(f"| {mr['name']} | {mr['enrolled']} | "
                f"{mr['sa_tp']}/{mr['sa_fp']} | {mr['sa_rec']:.3f} | "
                f"{mr['int_tp']}/{mr['int_fp']} | {mr['int_rec']:.3f} | {loss_str} |")

        out()

    # ─── 4. FP Analysis: Which wrong files are included? ─────────────────

    out("## 4. False Positive Analysis: Which Wrong Files Are Included?")
    out()
    out("For each project, the specific code files that are incorrectly linked to model elements.")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        sa_fps = r["sa_fps"]
        names = load_model_element_names(proj)

        if not sa_fps:
            out(f"### {proj}: No SAM-CODE FPs")
            out()
            continue

        out(f"### {proj} ({len(sa_fps)} FPs)")
        out()

        # Group FPs by model element
        fps_by_model = defaultdict(list)
        for m, c in sa_fps:
            fps_by_model[m].append(c)

        out("| Model Element | FP Count | Wrong Files |")
        out("|--------------|---------|-------------|")

        for m in sorted(fps_by_model, key=lambda x: len(fps_by_model[x]), reverse=True):
            files = fps_by_model[m]
            # Show first 3 files, truncated
            display = []
            for f in sorted(files)[:5]:
                parts = f.split("/")
                short = "/".join(parts[-2:]) if len(parts) >= 2 else f
                display.append(f"`{short}`")
            extra = f" +{len(files)-5} more" if len(files) > 5 else ""
            out(f"| {names.get(m, m)} | {len(files)} | {', '.join(display)}{extra} |")

        out()

    # ─── 5. FN Analysis: Which files are missed? ─────────────────────────

    out("## 5. False Negative Analysis: Which Gold Files Are Missed?")
    out()
    out("For each project, the specific code files that should be linked but are not recovered.")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        sa_fns = r["sa_fns"]
        names = load_model_element_names(proj)

        if not sa_fns:
            out(f"### {proj}: No SAM-CODE FNs")
            out()
            continue

        out(f"### {proj} ({len(sa_fns)} FNs)")
        out()

        # Group FNs by model element
        fns_by_model = defaultdict(list)
        for m, c in sa_fns:
            fns_by_model[m].append(c)

        out("| Model Element | FN Count | Missed Files |")
        out("|--------------|---------|-------------|")

        for m in sorted(fns_by_model, key=lambda x: len(fns_by_model[x]), reverse=True):
            files = fns_by_model[m]
            display = []
            for f in sorted(files)[:5]:
                parts = f.split("/")
                short = "/".join(parts[-2:]) if len(parts) >= 2 else f
                display.append(f"`{short}`")
            extra = f" +{len(files)-5} more" if len(files) > 5 else ""
            out(f"| {names.get(m, m)} | {len(files)} | {', '.join(display)}{extra} |")

        out()

    # ─── 6. File Extension Distribution ──────────────────────────────────

    out("## 6. File Extension Distribution")
    out()
    out("How do TPs, FPs, and FNs distribute across file types?")
    out()

    for proj in PROJECTS:
        r = all_results[proj]
        tp_ext = r["tp_ext"]
        fp_ext = r["fp_ext"]
        fn_ext = r["fn_ext"]
        gold_ext = r["gold_ext"]

        all_exts = sorted(set(list(tp_ext.keys()) + list(fp_ext.keys()) + list(fn_ext.keys()) + list(gold_ext.keys())))

        if not all_exts:
            continue

        out(f"### {proj}")
        out()
        out("| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |")
        out("|-----------|------|----|----|-----|---------|---------|")

        for ext in sorted(all_exts, key=lambda e: gold_ext.get(e, 0), reverse=True):
            g = gold_ext.get(ext, 0)
            tp = tp_ext.get(ext, 0)
            fp = fp_ext.get(ext, 0)
            fn = fn_ext.get(ext, 0)
            fp_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
            fn_rate = fn / g if g > 0 else 0
            out(f"| {ext} | {g} | {tp} | {fp} | {fn} | {fp_rate:.3f} | {fn_rate:.3f} |")

        out()

    # ─── 7. Code File Coverage ───────────────────────────────────────────

    out("## 7. Code File Recovery Coverage")
    out()
    out("How many unique gold code files are fully recovered, partially recovered, or never recovered?")
    out()
    out("| Project | Gold Files | Fully Recovered | Partially Recovered | Never Recovered | Spurious Files |")
    out("|---------|-----------|----------------|--------------------|-----------------|--------------| ")

    for proj in PROJECTS:
        r = all_results[proj]
        gold_files = set(c for _, c in r["gs_enrolled"])
        out(f"| {proj} | {len(gold_files)} | {len(r['fully_recovered'])} ({len(r['fully_recovered'])/len(gold_files)*100:.0f}%) | "
            f"{len(r['partially_recovered'])} ({len(r['partially_recovered'])/len(gold_files)*100:.0f}%) | "
            f"{len(r['never_recovered'])} ({len(r['never_recovered'])/len(gold_files)*100:.0f}%) | "
            f"{len(r['spurious_files'])} |")

    out()

    # Show never-recovered files for projects with FNs
    for proj in PROJECTS:
        r = all_results[proj]
        if not r["never_recovered"]:
            continue
        out(f"### {proj}: Never-Recovered Files ({len(r['never_recovered'])})")
        out()
        for f in sorted(r["never_recovered"])[:20]:
            parts = f.split("/")
            short = "/".join(parts[-3:]) if len(parts) >= 3 else f
            out(f"- `{short}`")
        if len(r["never_recovered"]) > 20:
            out(f"- ... and {len(r['never_recovered']) - 20} more")
        out()

    # ─── 8. Cross-project summary ────────────────────────────────────────

    out("## 8. Cross-Project Summary")
    out()

    out("### Model Element Error Concentration")
    out()
    out("How concentrated are SAM-CODE errors across model elements?")
    out()
    out("| Project | Model Elements | With FPs | With FNs | Perfect (TP=Gold) | No Links (in result) |")
    out("|---------|---------------|---------|---------|------------------|---------------------|")

    for proj in PROJECTS:
        r = all_results[proj]
        rows = r["model_rows"]
        total_me = len([mr for mr in rows if mr["enrolled"] > 0 or mr["sa_result"] > 0])
        with_fp = len([mr for mr in rows if mr["sa_fp"] > 0])
        with_fn = len([mr for mr in rows if mr["sa_fn"] > 0])
        perfect = len([mr for mr in rows if mr["enrolled"] > 0 and mr["sa_tp"] == mr["enrolled"] and mr["sa_fp"] == 0])
        no_links = len([mr for mr in rows if mr["enrolled"] > 0 and mr["sa_result"] == 0])
        out(f"| {proj} | {total_me} | {with_fp} | {with_fn} | {perfect} | {no_links} |")

    out()

    out("### Enrollment Amplification vs Error Rate")
    out()
    out("Do heavily enrolled model elements (many files from few directory entries) have higher error rates?")
    out()

    out("| Project | Model Element | Raw | Enrolled | Factor | FPs | FNs | Precision | Recall |")
    out("|---------|--------------|-----|---------|--------|-----|-----|-----------|--------|")

    for proj in PROJECTS:
        r = all_results[proj]
        rows = r["model_rows"]
        for mr in sorted(rows, key=lambda x: x["enrollment_factor"], reverse=True):
            if mr["raw_total"] == 0 or mr["enrolled"] == 0:
                continue
            if mr["enrollment_factor"] <= 1.0:
                continue
            out(f"| {proj} | {mr['name']} | {mr['raw_total']} | {mr['enrolled']} | "
                f"{mr['enrollment_factor']:.1f}x | {mr['sa_fp']} | {mr['sa_fn']} | "
                f"{mr['sa_prec']:.3f} | {mr['sa_rec']:.3f} |")

    out()

    # ─── Write report ────────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md))
        f.write("\n")

    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
