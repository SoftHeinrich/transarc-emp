#!/usr/bin/env python3
"""
RQ2 — Trivial baselines under file-level F1 vs bias-corrected metrics.

Demonstrates that two trivial systems (Random, Top-3) may look misleadingly
strong under standard file-level micro-F1 yet weak under bias-corrected
metrics (per-component F1 macro, per-sentence F1 macro, sentence coverage,
noise rate, HUS, NDG).

For each project x baseline, computes 7 metrics:
  1. File-level (micro) F1
  2. Per-component F1 (macro over components)
  3. Per-sentence F1 (macro over gold sentences)
  4. Sentence coverage (fraction of gold sentences with >=1 correct link)
  5. Noise rate (mean fraction of wrong links per result sentence)
  6. HUS (harmonic of sentence coverage and sentence purity)
  7. NDG (system_f1 normalized between random_f1 and oracle_f1)

Output: reports/RQ2_TRIVIAL_BASELINES.md
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

# Shared loaders
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS,
    load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam_maps, load_gs_sam_code_raw, load_gs_sam_code_maps,
    load_gs_sad_code_enrolled,
    load_model_element_names,
    calc_metrics,
)
from new_metrics_analysis import (  # noqa: E402
    compute_hus, compute_ndg, compute_random_f1, compute_oracle_f1,
)

# Reuse the Random and Top-3 (Majority-K) generators from stupid_baseline_analysis
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stupid_baseline_analysis import (  # noqa: E402
    baseline_random_same_size, baseline_majority_k,
)

OUTPUT_MD = Path(__file__).resolve().parent.parent.parent / "reports" / "RQ2_TRIVIAL_BASELINES.md"

# Reproducibility
random.seed(42)


# ─────────────────────────────────────────────────────────────────────────────
# Bias-corrected metric helpers
# ─────────────────────────────────────────────────────────────────────────────

def per_component_macro_f1(gold_sad_code, result_sad_code, file_to_comps):
    """Macro F1 averaged over components.

    For each component c, treat the set of (sentence, c) pairs as the binary
    classification problem (a file in c maps to its component c). Compute F1
    per component, then unweighted mean over components that have any gold or
    any result.
    """
    # Project file-level links to (sentence, component) level
    gold_by_comp = defaultdict(set)
    for s, f in gold_sad_code:
        for comp in file_to_comps.get(f, ()):
            gold_by_comp[comp].add(s)
    result_by_comp = defaultdict(set)
    for s, f in result_sad_code:
        for comp in file_to_comps.get(f, ()):
            result_by_comp[comp].add(s)

    comps = set(gold_by_comp) | set(result_by_comp)
    if not comps:
        return 0.0
    f1s = []
    for c in comps:
        g = gold_by_comp.get(c, set())
        r = result_by_comp.get(c, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        if tp + fp + fn == 0:
            continue
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def per_sentence_macro_f1(gold_sad_code, result_sad_code):
    """Macro F1 averaged over gold sentences (file sets)."""
    gold_by_sent = defaultdict(set)
    result_by_sent = defaultdict(set)
    for s, f in gold_sad_code:
        gold_by_sent[s].add(f)
    for s, f in result_sad_code:
        result_by_sent[s].add(f)

    gold_sents = set(gold_by_sent)
    if not gold_sents:
        return 0.0
    f1s = []
    for s in gold_sents:
        g = gold_by_sent[s]
        r = result_by_sent.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def sentence_coverage(gold_sad_code, result_sad_code):
    """Fraction of gold sentences with >=1 correct link."""
    gold_by_sent = defaultdict(set)
    result_by_sent = defaultdict(set)
    for s, f in gold_sad_code:
        gold_by_sent[s].add(f)
    for s, f in result_sad_code:
        result_by_sent[s].add(f)
    gold_sents = list(gold_by_sent.keys())
    if not gold_sents:
        return 0.0
    covered = sum(1 for s in gold_sents if gold_by_sent[s] & result_by_sent.get(s, set()))
    return covered / len(gold_sents)


def noise_rate(gold_sad_code, result_sad_code):
    """Mean across result-sentences of FP/(TP+FP). Sentences with no
    predictions are excluded from the mean."""
    gold_by_sent = defaultdict(set)
    result_by_sent = defaultdict(set)
    for s, f in gold_sad_code:
        gold_by_sent[s].add(f)
    for s, f in result_sad_code:
        result_by_sent[s].add(f)
    vals = []
    for s, r in result_by_sent.items():
        g = gold_by_sent.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        if tp + fp > 0:
            vals.append(fp / (tp + fp))
    return sum(vals) / len(vals) if vals else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Per-project measurement
# ─────────────────────────────────────────────────────────────────────────────

def measure(name, baseline, gold_sad_code, file_to_comps, random_f1, oracle_f1):
    file_f1 = calc_metrics(gold_sad_code, baseline)[2]
    comp_f1 = per_component_macro_f1(gold_sad_code, baseline, file_to_comps)
    sent_f1 = per_sentence_macro_f1(gold_sad_code, baseline)
    cov = sentence_coverage(gold_sad_code, baseline)
    noise = noise_rate(gold_sad_code, baseline)
    hus = compute_hus(gold_sad_code, baseline)["hus"]
    ndg = compute_ndg(file_f1, random_f1, oracle_f1)
    return {
        "name": name,
        "file_f1": file_f1,
        "comp_f1": comp_f1,
        "sent_f1": sent_f1,
        "coverage": cov,
        "noise": noise,
        "hus": hus,
        "ndg": ndg,
    }


def run_project(proj):
    print(f"\n=== {proj} ===")
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)

    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
    gs_sam_code_raw = load_gs_sam_code_raw(proj)
    gs_sam_code_enrolled = enroll_gold_standard(gs_sam_code_raw, code_model)
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
    gs_sad_sam_maps = load_gs_sad_sam_maps(proj)

    # file -> {component name} (collapsing synonymous IDs by component name)
    file_to_comps = defaultdict(set)
    for ae, fp in gs_sam_code_enrolled:
        file_to_comps[fp].add(names.get(ae, ae))

    gold_sents = set(s for s, _ in gs_sad_code)

    # Baselines
    random.seed(42)  # reset for each project so order independence is preserved
    target_size = len(gs_sad_code)  # "gold link density" -> total predictions ~= |gold|
    random_bl = baseline_random_same_size(gold_sents, code_model, target_size)
    top3_bl = baseline_majority_k(gold_sents, gs_sam_code_enrolled, code_model, k=3)

    # NDG anchors: random_f1 (analytical) and oracle_f1 (perfect transitive)
    # Use a representative sentence count = number of distinct gold sentences
    # (matches new_metrics_analysis.py's compute_random_f1 usage which passes len(text))
    n_sents = len(gold_sents)
    random_f1 = compute_random_f1(gs_sad_code, n_sents, len(names), gs_sam_code_map)
    oracle_f1, _ = compute_oracle_f1(gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)

    print(f"  |gold|={len(gs_sad_code)}, |random|={len(random_bl)}, |top3|={len(top3_bl)}")
    print(f"  random_f1 (anchor)={random_f1:.4f}, oracle_f1 (anchor)={oracle_f1:.4f}")

    rows = {
        "Random": measure("Random", random_bl, gs_sad_code, file_to_comps, random_f1, oracle_f1),
        "Top-3":  measure("Top-3",  top3_bl,  gs_sad_code, file_to_comps, random_f1, oracle_f1),
    }
    for name, r in rows.items():
        print(f"  {name:>7}: file_F1={r['file_f1']:.3f}  comp_F1={r['comp_f1']:.3f}  "
              f"sent_F1={r['sent_f1']:.3f}  cov={r['coverage']:.3f}  noise={r['noise']:.3f}  "
              f"hus={r['hus']:.3f}  ndg={r['ndg']:.3f}")
    return rows, {"random_f1": random_f1, "oracle_f1": oracle_f1,
                  "gold_size": len(gs_sad_code),
                  "random_size": len(random_bl),
                  "top3_size": len(top3_bl)}


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

METRIC_ORDER = [
    ("file_f1",  "File-level F1 (micro)"),
    ("comp_f1",  "Per-component F1 (macro)"),
    ("sent_f1",  "Per-sentence F1 (macro)"),
    ("coverage", "Sentence coverage"),
    ("noise",    "Noise rate"),
    ("hus",      "HUS"),
    ("ndg",      "NDG (skill score)"),
]


def write_report(per_proj, anchors):
    lines = []

    def out(s=""):
        lines.append(s)

    out("# RQ2: Trivial Baselines Under File-Level F1 vs Bias-Corrected Metrics")
    out()
    out("Two trivial baselines computed on SAM-CODE-enrolled SAD-CODE gold for")
    out("the 5 ARDoCo benchmark projects:")
    out()
    out("- **Random**: `random.seed(42)`, samples `(sentence, file)` pairs at gold link density")
    out("  (total predictions ~= |gold|), reusing `baseline_random_same_size` from")
    out("  `src/bias/stupid_baseline_analysis.py`.")
    out("- **Top-3**: every sentence linked to the files of the 3 components with the most")
    out("  enrolled gold files in the project, reusing `baseline_majority_k(..., k=3)` from")
    out("  the same module.")
    out()
    out("Each baseline is scored on 7 metrics per project: file-level micro F1,")
    out("per-component F1 (macro), per-sentence F1 (macro), sentence coverage,")
    out("noise rate, HUS (`src/lib/new_metrics_analysis.py`), and NDG skill score")
    out("`(system_F1 - random_F1) / (oracle_F1 - random_F1)`.")
    out()

    # Per-baseline table: rows = metric, cols = projects + macro mean
    for bl in ["Random", "Top-3"]:
        out(f"## {bl}")
        out()
        header = "| Metric | " + " | ".join(p for p in PROJECTS) + " | **macro mean** |"
        sep    = "|" + "---|" * (len(PROJECTS) + 2)
        out(header)
        out(sep)
        for key, label in METRIC_ORDER:
            vals = [per_proj[p][bl][key] for p in PROJECTS]
            mean = sum(vals) / len(vals)
            row = f"| {label} | " + " | ".join(f"{v:.3f}" for v in vals) + f" | **{mean:.3f}** |"
            out(row)
        out()

    # Combined head-to-head table (per project, both baselines per row, per metric)
    out("## Head-to-head per metric (Random vs Top-3 vs SOTA reference)")
    out()
    out("SOTA reference = TransArc / s11 / s13f file-level F1 from")
    out("`reports/SADCODE_S11_S13F_VS_TRANSARC.csv` (the best of TransArc, S11, S13F per project).")
    out()
    # Hard-coded SOTA file-level F1 from SADCODE_S11_S13F_VS_TRANSARC.csv
    SOTA_FILE_F1 = {
        "mediastore":    {"transarc": 0.5882, "s11": 0.9123, "s13f": 0.9286},
        "teastore":      {"transarc": 0.8295, "s11": 0.9477, "s13f": 1.0000},
        "teammates":     {"transarc": 0.8211, "s11": 0.7850, "s13f": 0.8636},
        "bigbluebutton": {"transarc": 0.8309, "s11": 0.8789, "s13f": 0.8639},
        "jabref":        {"transarc": 0.9433, "s11": 0.9849, "s13f": 0.9998},
    }
    out("| Project | Random file_F1 | Top-3 file_F1 | TransArc file_F1 | S11 file_F1 | S13F file_F1 |")
    out("|---|---|---|---|---|---|")
    for p in PROJECTS:
        s = SOTA_FILE_F1[p]
        out(f"| {p} | {per_proj[p]['Random']['file_f1']:.3f} "
            f"| {per_proj[p]['Top-3']['file_f1']:.3f} "
            f"| {s['transarc']:.3f} | {s['s11']:.3f} | {s['s13f']:.3f} |")
    avg_r  = sum(per_proj[p]['Random']['file_f1'] for p in PROJECTS) / len(PROJECTS)
    avg_t3 = sum(per_proj[p]['Top-3']['file_f1']  for p in PROJECTS) / len(PROJECTS)
    avg_ta = sum(SOTA_FILE_F1[p]['transarc'] for p in PROJECTS) / len(PROJECTS)
    avg_s11 = sum(SOTA_FILE_F1[p]['s11']     for p in PROJECTS) / len(PROJECTS)
    avg_s13f = sum(SOTA_FILE_F1[p]['s13f']    for p in PROJECTS) / len(PROJECTS)
    out(f"| **macro mean** | **{avg_r:.3f}** | **{avg_t3:.3f}** "
        f"| **{avg_ta:.3f}** | **{avg_s11:.3f}** | **{avg_s13f:.3f}** |")
    out()

    # NDG anchors per project (for reference)
    out("## NDG anchors per project")
    out()
    out("| Project | random_f1 (analytic prior) | oracle_f1 (perfect transitive) "
        "| |gold| | |random pred| | |top-3 pred| |")
    out("|---|---|---|---|---|---|")
    for p in PROJECTS:
        a = anchors[p]
        out(f"| {p} | {a['random_f1']:.4f} | {a['oracle_f1']:.4f} "
            f"| {a['gold_size']:,} | {a['random_size']:,} | {a['top3_size']:,} |")
    out()

    out("---")
    out("")
    out("Script: `src/bias/rq2_trivial_baselines.py`. Reproduce: `python3 src/bias/rq2_trivial_baselines.py`.")
    out("")

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"\nWrote {OUTPUT_MD}")


def main():
    per_proj = {}
    anchors = {}
    for p in PROJECTS:
        rows, info = run_project(p)
        per_proj[p] = rows
        anchors[p] = info
    write_report(per_proj, anchors)


if __name__ == "__main__":
    main()
