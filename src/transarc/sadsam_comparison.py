#!/usr/bin/env python3
"""
SAD-SAM holistic metric comparison — s_linker11 / s_linker13f / TransArc.

Counterpart to src/transarc/s12c_sadcode_comparison.py, for the SAD-SAM stage.
Reuses the canonical architecture-aware metric suite in metrics_api /
new_metrics_analysis (zero metric math reimplemented here):

    link_f1      — exact (modelElementID, sentence) pair match (= decision_f1;
                   SAD-SAM has no enrollment, so file/decision/weighted collapse)
    sentence_f1  — per-sentence: TP iff gold & predicted component sets intersect
    component_f1 — per-component: ids collapsed to component names
    mcc          — Matthews corr. over the full (sentence × component) universe
    map          — mean average precision over confidence-ranked links
    hus          — Harmonic Usefulness Score (coverage × purity), the "usefulness"
                   metric: per-sentence coverage and FP-purity

(file_f1 / weighted_f1 / acf1 / ndg are N/A for SAD-SAM — no files, no enrollment.)

Systems (all produce (modelElementID, sentence) links):
    TransArc — ARDoCo standalone SAD-SAM (SWATTR), transarc-emp results
    s11      — s_linker11 SAD-SAM, llm-sad-sam-v45 ablation results
    s13f     — s_linker13f SAD-SAM (latest), ablation results

Output: reports/SADSAM_S11_S13F_VS_TRANSARC.csv  +  reports/SADSAM_COMPARISON.md
"""

import csv
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import PROJECTS, load_gs_sad_sam, load_result_sad_sam_standalone  # noqa: E402
from metrics_api import compute_sad_sam_metrics, NA  # noqa: E402

ABLATION_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/ablation_results")
REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"
OUTPUT_CSV = REPORTS / "SADSAM_S11_S13F_VS_TRANSARC.csv"
OUTPUT_MD = REPORTS / "SADSAM_COMPARISON.md"

# (key, label, ablation_variant_or_None)
SYSTEMS = [
    ("transarc", "TransArc", None),
    ("s11", "s_linker11", "s_linker11"),
    ("s13f", "s_linker13f", "s_linker13f"),
]

# Suite columns meaningful for SAD-SAM (others are NA at this stage).
METRICS = ["link_f1", "sentence_f1", "component_f1", "mcc", "map", "hus"]
METRIC_LABELS = {
    "link_f1": "Link F1",
    "sentence_f1": "Sentence F1",
    "component_f1": "Component F1",
    "mcc": "MCC",
    "map": "MAP",
    "hus": "HUS",
}


def load_ablation_sad_sam(variant, project):
    """Load ablation SAD-SAM links -> set of (component_id, sentence_str)."""
    path = ABLATION_DIR / f"{variant}_{project}_links.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            comp_id = row["component_id"].strip()
            sent = str(row["sentence"].strip())
            if comp_id and sent:
                links.add((comp_id, sent))
    return links


def system_links(key, variant, project):
    if key == "transarc":
        return load_result_sad_sam_standalone(project)
    return load_ablation_sad_sam(variant, project)


def main():
    # data[project][key] = metric row dict
    data = {}
    for proj in PROJECTS:
        data[proj] = {}
        for key, label, variant in SYSTEMS:
            res = system_links(key, variant, proj)
            if not res:
                print(f"WARNING: no SAD-SAM links for {label}/{proj}", file=sys.stderr)
                data[proj][key] = None
                continue
            data[proj][key] = compute_sad_sam_metrics(proj, res)

    # ── averages (over projects where the system produced a row) ──
    def avg(key, metric):
        vals = [data[p][key][metric] for p in PROJECTS
                if data[p][key] and isinstance(data[p][key].get(metric), (int, float))]
        return sum(vals) / len(vals) if vals else None

    # ── CSV (wide: one row per project, all metrics × all systems) ──
    REPORTS.mkdir(parents=True, exist_ok=True)
    header = ["dataset", "gold_links"]
    for key, _, _ in SYSTEMS:
        header.append(f"{key}_links")
        header += [f"{key}_{m}" for m in METRICS]
    with open(OUTPUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for proj in PROJECTS:
            gold = load_gs_sad_sam(proj)
            row = [proj, len(gold)]
            for key, _, variant in SYSTEMS:
                res = system_links(key, variant, proj)
                row.append(len(res))
                r = data[proj][key]
                for m in METRICS:
                    v = r.get(m) if r else None
                    row.append(round(v, 4) if isinstance(v, (int, float)) else NA)
            w.writerow(row)
        # average row
        avg_row = ["Average", ""]
        for key, _, _ in SYSTEMS:
            avg_row.append("")
            for m in METRICS:
                a = avg(key, m)
                avg_row.append(round(a, 4) if a is not None else NA)
        w.writerow(avg_row)

    # ── Markdown ──
    L = []
    L.append("# SAD-SAM Holistic Comparison — s_linker11 / s_linker13f / TransArc\n")
    L.append("Source: `src/transarc/sadsam_comparison.py`. Reuses the canonical "
             "architecture-aware metric suite (`metrics_api.compute_sad_sam_metrics`, "
             "`new_metrics_analysis`).\n")
    L.append("## Why these metrics (and why no file/decision/weighted split)\n")
    L.append(
        "SAD-SAM gold is atomic `(modelElementID, sentence)` pairs — **no directory "
        "enrollment** — so the SAD-CODE levels file/decision/weighted/component all "
        "collapse to **Link F1**. The informative views are instead *architecture- and "
        "doc-structure-aware*:\n")
    L.append("- **Sentence F1** — per-sentence correctness (doc structure axis).")
    L.append("- **Component F1** — per-component correctness (architecture axis; ids→names).")
    L.append("- **MCC** — correlation over the full (sentence × component) space, crediting "
             "true negatives (the architecture model + document supply the negative space).")
    L.append("- **MAP** — ranking quality of confidence-ordered links.")
    L.append("- **HUS** (usefulness) — harmonic mean of per-sentence *coverage* (gold "
             "sentences with ≥1 hit) and *purity* (predicted sentences with 0 FPs).\n")

    for m in METRICS:
        L.append(f"## {METRIC_LABELS[m]}\n")
        L.append("| dataset | " + " | ".join(label for _, label, _ in SYSTEMS) + " |")
        L.append("|" + "---|" * (len(SYSTEMS) + 1))
        for proj in PROJECTS:
            cells = []
            for key, _, _ in SYSTEMS:
                r = data[proj][key]
                v = r.get(m) if r else None
                cells.append(f"**{v:.3f}**" if isinstance(v, (int, float)) else NA)
            L.append(f"| {proj} | " + " | ".join(cells) + " |")
        avg_cells = []
        for key, _, _ in SYSTEMS:
            a = avg(key, m)
            avg_cells.append(f"**{a:.3f}**" if a is not None else NA)
        L.append(f"| **AVG** | " + " | ".join(avg_cells) + " |")
        L.append("")

    OUTPUT_MD.write_text("\n".join(L))

    # ── console summary ──
    print("SAD-SAM holistic comparison written:")
    print(f"  {OUTPUT_CSV}")
    print(f"  {OUTPUT_MD}\n")
    colw = 12
    print(f"{'metric':14} | " + " | ".join(f"{lbl:>{colw}}" for _, lbl, _ in SYSTEMS))
    print("-" * (16 + (colw + 3) * len(SYSTEMS)))
    for m in METRICS:
        cells = " | ".join(
            f"{(avg(k, m) if avg(k, m) is not None else float('nan')):>{colw}.3f}"
            for k, _, _ in SYSTEMS
        )
        print(f"{METRIC_LABELS[m]:14} | {cells}")


if __name__ == "__main__":
    main()
