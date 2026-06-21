#!/usr/bin/env python3
"""
SAD-SAM holistic metric comparison — s_linker19 (paper variant) vs TransArc,
with legacy s_linker11/13f/15 columns kept best-effort for back-compat.

Reuses the canonical architecture-aware metric suite in metrics_api /
new_metrics_analysis (zero metric math reimplemented here):

    link_f1      — exact (modelElementID, sentence) pair match (= decision_f1;
                   SAD-SAM has no enrollment, so file/decision/weighted collapse)
    sentence_f1  — per-sentence: TP iff gold & predicted component sets intersect
    component_f1 — per-component: ids collapsed to component names
    mcc          — Matthews corr. over the full (sentence × component) universe
    map          — mean average precision over confidence-ranked links
    hus          — Harmonic Usefulness Score (coverage × purity)

(file_f1 / weighted_f1 / acf1 / ndg are N/A for SAD-SAM — no files, no enrollment.)

Systems (all produce (modelElementID, sentence) links):
    TransArc     — ARDoCo standalone SAD-SAM (SWATTR), transarc-emp results
    s19_claude   — s_linker19 (Claude) v2.6.3 phase_cache replay  ← PAPER VARIANT
    s19_openai   — s_linker19 (GPT-5.4) v2.6.3 phase_cache replay ← PAPER VARIANT
    s11          — s_linker11 ablation_results (kept for historical context)
    s13f / s15_* — older variants; their result dirs may no longer exist, in which
                   case the columns degrade to NA without failing the run.

Output: reports/SADSAM_S11_S13F_VS_TRANSARC.csv  +  reports/SADSAM_COMPARISON.md
"""

import csv
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import PROJECTS, load_gs_sad_sam, load_result_sad_sam_standalone  # noqa: E402
import metrics_api  # noqa: E402  (need PAPER_MAIN_PANEL_* constants below)
from metrics_api import compute_sad_sam_metrics, NA  # noqa: E402

ABLATION_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/ablation_results")
S15_GPT_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/v2.6.1")
S15_CLAUDE_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/v2.6.1_claude")
S19_CLAUDE_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3/claude")
S19_OPENAI_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3/openai")
REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"
OUTPUT_CSV = REPORTS / "SADSAM_S11_S13F_VS_TRANSARC.csv"
OUTPUT_MD = REPORTS / "SADSAM_COMPARISON.md"

# (key, label, loader_tag)
# loader_tag: None=transarc, "ablation/<name>"=ablation dir,
#             "s15_gpt"/"s15_claude"=v2.6.1 dirs, "s19/{claude|openai}"=v2.6.3.
SYSTEMS = [
    ("transarc", "TransArc", None),
    ("s19_claude", "s_linker19 (Claude)", "s19/claude"),
    ("s19_openai", "s_linker19 (GPT-5.4)", "s19/openai"),
    ("s11", "s_linker11", "ablation/s_linker11"),
    ("s13f", "s_linker13f", "ablation/s_linker13f"),
    ("s15_gpt", "s15_gpt", "s15_gpt/s_linker15"),
    ("s15_claude", "s15_claude", "s15_claude/s_linker15"),
]

# Suite columns meaningful for SAD-SAM (file/decision/weighted/acf1/ndg are
# SAD-CODE-only and N/A at this stage). Ordered to match the paper's RQ2
# layout: main panel first (link F1 is the link-level reference; per-component
# F1 collapses onto link F1 on sad-sam — kept here as a sanity column;
# sentence coverage + noise rate are the developer view). Then appendix
# (per-sentence F1, HUS — both shadowed; ρ ≥ 0.91 with link F1, see
# reports/RQ2_METRIC_REDUNDANCY.md). Then pure diagnostics (MCC, MAP).
METRICS = (
    [metrics_api.PAPER_MAIN_PANEL_SADSAM[0], "component_f1"]
    + metrics_api.PAPER_MAIN_PANEL_SADSAM[1:]
    + metrics_api.PAPER_APPENDIX_SADSAM
    + ["mcc", "map"]
)
METRIC_LABELS = {
    "link_f1": "Link F1",
    "component_f1": "Component F1",
    "sentence_coverage": "Sent. coverage",
    "noise_rate": "Noise rate (↓)",
    "sentence_f1": "Sentence F1",
    "hus": "HUS",
    "mcc": "MCC",
    "map": "MAP",
}


def _load_links_csv(path):
    """Load SAD-SAM links CSV -> set of (component_id, sentence_str)."""
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


def _load_s19_sad_sam(path):
    """Load s_linker19 v2.6.3 SAD-SAM CSV -> set of (modelElementID, sentence_str).

    Schema is ``modelElementID, sentence, source`` — the extra column is ignored
    by csv.DictReader. The ``modelElementID`` here plays the same role as
    ``component_id`` in the older ablation CSVs.
    """
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            ae_id = row["modelElementID"].strip()
            sent = str(row["sentence"]).strip()
            if ae_id and sent:
                links.add((ae_id, sent))
    return links


def system_links(key, loader_tag, project):
    if key == "transarc":
        return load_result_sad_sam_standalone(project)
    if loader_tag.startswith("ablation/"):
        variant = loader_tag[len("ablation/"):]
        return _load_links_csv(ABLATION_DIR / f"{variant}_{project}_links.csv")
    if loader_tag.startswith("s15_gpt/"):
        variant = loader_tag[len("s15_gpt/"):]
        return _load_links_csv(S15_GPT_DIR / f"{variant}_{project}_links.csv")
    if loader_tag.startswith("s15_claude/"):
        variant = loader_tag[len("s15_claude/"):]
        return _load_links_csv(S15_CLAUDE_DIR / f"{variant}_{project}_links.csv")
    if loader_tag.startswith("s19/"):
        backend = loader_tag[len("s19/"):]
        base = {"claude": S19_CLAUDE_DIR, "openai": S19_OPENAI_DIR}[backend]
        return _load_s19_sad_sam(base / project / "sad-sam.csv")
    raise ValueError(f"Unknown loader_tag: {loader_tag}")


def main():
    # data[project][key] = metric row dict
    data = {}
    for proj in PROJECTS:
        data[proj] = {}
        for key, label, loader_tag in SYSTEMS:
            res = system_links(key, loader_tag, proj)
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
            for key, _, loader_tag in SYSTEMS:
                res = system_links(key, loader_tag, proj)
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
    L.append("# SAD-SAM Holistic Comparison — s_linker11 / s_linker13f / s_linker15 / TransArc\n")
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
