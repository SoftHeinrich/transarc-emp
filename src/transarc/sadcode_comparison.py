#!/usr/bin/env python3
"""
SAD-CODE holistic metric comparison — s_linker19 (paper variant) vs TransArc,
with legacy s_linker11/13f/15 columns kept best-effort for back-compat.

Counterpart to sadsam_comparison.py, at the transitive SAD-CODE level. Reuses
the canonical metric suite (`metrics_api.compute_sad_code_metrics`,
`evaluation_critique`, `new_metrics_analysis`) — zero metric math reimplemented.

Systems (all produce (sentence, code_path) links):
    TransArc     — full ARDoCo pipeline SAD-CODE, transarc-emp results
    s19_claude   — s_linker19 (Claude) v2.6.3 direct SAD-CODE  ← PAPER VARIANT
    s19_openai   — s_linker19 (GPT-5.4) v2.6.3 direct SAD-CODE ← PAPER VARIANT
    s11          — s_linker11 SAD-SAM × ARCOTL SAM-CODE (composed)
    s13f / s15_* — older variants, composed; result dirs may no longer exist.

Note: s11/s13f/s15 are composed from SAD-SAM × ARCOTL SAM-CODE (legacy pipeline).
The s19 variants ship direct SAD-CODE predictions, so we load them as-is — no
external composition. This matches the paper variant's intended evaluation path.

Metrics (SAD-CODE has directory enrollment, so the multi-level split IS
informative here — contrast with SAD-SAM where it collapses):
    file_f1      — raw enrolled (sentence, file) match  [enrollment-inflated]
    decision_f1  — raw gold entry TP if >=50% enrolled files hit  [de-inflated]
    component_f1 — (sentence, component_name) collapse  [architecture axis]
    weighted_f1  — file weighted 1/block_size  [de-inflated]
    acf1         — amplification-corrected F1 (1/N component weighting)
    mcc          — Matthews corr. over (sentence × code-file) universe
    ndg          — normalized discrimination gain vs random/oracle baselines
    hus          — Harmonic Usefulness Score (per-sentence coverage × purity)

(link_f1 / sentence_f1 / map are SAD-SAM-only and reported NA here.)

Output: reports/SADCODE_S11_S13F_VS_TRANSARC.csv  +  reports/SADCODE_COMPARISON.md
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS, load_result_sad_code, load_result_sam_code_standalone,
)
import metrics_api  # noqa: E402  (need PAPER_MAIN_PANEL_* constants below)
from metrics_api import compute_sad_code_metrics, NA  # noqa: E402

ABLATION_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/ablation_results")
S15_GPT_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/v2.6.1")
S15_CLAUDE_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-v45/results/v2.6.1_claude")
S19_CLAUDE_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3/claude")
S19_OPENAI_DIR = Path("/mnt/hostshare/ardoco-home/agent-linker/results/v2.6.3/openai")
REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"
OUTPUT_CSV = REPORTS / "SADCODE_S11_S13F_VS_TRANSARC.csv"
OUTPUT_MD = REPORTS / "SADCODE_COMPARISON.md"

# (key, label, loader_tag). s19 uses direct SAD-CODE predictions; others compose.
SYSTEMS = [
    ("transarc", "TransArc", None),
    ("s19_claude", "s_linker19 (Claude)", "s19/claude"),
    ("s19_openai", "s_linker19 (GPT-5.4)", "s19/openai"),
    ("s11", "s_linker11", "ablation/s_linker11"),
    ("s13f", "s_linker13f", "ablation/s_linker13f"),
    ("s15_gpt", "s15_gpt", "s15_gpt/s_linker15"),
    ("s15_claude", "s15_claude", "s15_claude/s_linker15"),
]

# Suite columns meaningful for SAD-CODE (link/sentence/map are SAD-SAM-only).
# Ordered to match the paper's RQ2 layout: main panel first (file F1 ->
# per-component F1 -> decision F1; then sentence coverage + noise rate); then
# the appendix-only block (HUS, NDG — both shadowed on this benchmark, see
# reports/RQ2_METRIC_REDUNDANCY.md and project-paper-metric-choices); then
# pure diagnostics (Weighted F1, ACF1, MCC) that the paper does not report.
METRICS = (
    metrics_api.PAPER_MAIN_PANEL_SADCODE          # 4 metrics
    + metrics_api.PAPER_APPENDIX_SADCODE          # hus, ndg
    + ["decision_f1", "weighted_f1", "acf1", "mcc"]  # diagnostic-only
)
METRIC_LABELS = {
    "file_f1": "File F1",
    "component_f1": "Component F1",
    "sentence_coverage": "Sent. coverage",
    "noise_rate": "Noise rate (↓)",
    "hus": "HUS",
    "ndg": "NDG",
    "decision_f1": "Decision F1",
    "weighted_f1": "Weighted F1",
    "acf1": "ACF1",
    "mcc": "MCC",
}


def _load_sad_sam_csv(path):
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


def _load_sad_sam_for_tag(loader_tag, project):
    if loader_tag.startswith("ablation/"):
        variant = loader_tag[len("ablation/"):]
        return _load_sad_sam_csv(ABLATION_DIR / f"{variant}_{project}_links.csv")
    if loader_tag.startswith("s15_gpt/"):
        variant = loader_tag[len("s15_gpt/"):]
        return _load_sad_sam_csv(S15_GPT_DIR / f"{variant}_{project}_links.csv")
    if loader_tag.startswith("s15_claude/"):
        variant = loader_tag[len("s15_claude/"):]
        return _load_sad_sam_csv(S15_CLAUDE_DIR / f"{variant}_{project}_links.csv")
    raise ValueError(f"Unknown loader_tag: {loader_tag}")


def _load_s19_sad_code(path):
    """Load s_linker19 v2.6.3 SAD-CODE CSV -> set of (sentence_str, code_path).

    Schema is ``sentence, codeID`` — s19 ships direct SAD-CODE predictions, so
    no SAD-SAM × SAM-CODE composition is needed.
    """
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            sent = str(row["sentence"]).strip()
            code = row["codeID"].strip()
            if sent and code:
                links.add((sent, code))
    return links


def compose_sad_code(sad_sam_links, sam_code_standalone):
    """Compose SAD-SAM × ARCOTL SAM-CODE → SAD-CODE (sentence, code)."""
    model_to_codes = defaultdict(set)
    for ae_id, code_path in sam_code_standalone:
        model_to_codes[ae_id].add(code_path)
    result = set()
    for ae_id, sentence in sad_sam_links:
        for code in model_to_codes.get(ae_id, ()):
            result.add((sentence, code))
    return result


def system_links(key, loader_tag, project):
    if key == "transarc":
        return load_result_sad_code(project)
    if loader_tag.startswith("s19/"):
        backend = loader_tag[len("s19/"):]
        base = {"claude": S19_CLAUDE_DIR, "openai": S19_OPENAI_DIR}[backend]
        return _load_s19_sad_code(base / project / "sad-code.csv")
    sad_sam = _load_sad_sam_for_tag(loader_tag, project)
    sam_code = load_result_sam_code_standalone(project)
    return compose_sad_code(sad_sam, sam_code)


def main():
    data = {}
    for proj in PROJECTS:
        data[proj] = {}
        for key, label, loader_tag in SYSTEMS:
            res = system_links(key, loader_tag, proj)
            if not res:
                print(f"WARNING: no SAD-CODE links for {label}/{proj}", file=sys.stderr)
                data[proj][key] = None
                continue
            data[proj][key] = compute_sad_code_metrics(proj, res)

    def avg(key, metric):
        vals = [data[p][key][metric] for p in PROJECTS
                if data[p][key] and isinstance(data[p][key].get(metric), (int, float))]
        return sum(vals) / len(vals) if vals else None

    # ── CSV ──
    REPORTS.mkdir(parents=True, exist_ok=True)
    header = ["dataset"]
    for key, _, _ in SYSTEMS:
        header.append(f"{key}_links")
        header += [f"{key}_{m}" for m in METRICS]
    with open(OUTPUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for proj in PROJECTS:
            row = [proj]
            for key, _, loader_tag in SYSTEMS:
                res = system_links(key, loader_tag, proj)
                row.append(len(res))
                r = data[proj][key]
                for m in METRICS:
                    v = r.get(m) if r else None
                    row.append(round(v, 4) if isinstance(v, (int, float)) else NA)
            w.writerow(row)
        avg_row = ["Average"]
        for key, _, _ in SYSTEMS:
            avg_row.append("")
            for m in METRICS:
                a = avg(key, m)
                avg_row.append(round(a, 4) if a is not None else NA)
        w.writerow(avg_row)

    # ── Markdown ──
    L = []
    L.append("# SAD-CODE Holistic Comparison — s_linker11 / s_linker13f / s_linker15 / TransArc\n")
    L.append("Source: `src/transarc/sadcode_comparison.py`. Reuses the canonical metric "
             "suite (`metrics_api.compute_sad_code_metrics`, `evaluation_critique`, "
             "`new_metrics_analysis`). s11/s13f/s15 SAD-CODE = SAD-SAM × ARCOTL SAM-CODE "
             "(same composition as the s12c comparator); TransArc = full-pipeline output.\n")
    L.append("## Metric levels\n")
    L.append("Unlike SAD-SAM, SAD-CODE gold has **directory enrollment** (525 raw → 18,660 "
             "files), so the multi-level split is informative — the levels *diverge*:\n")
    L.append("- **File F1** — enrollment-inflated raw (sentence, file).")
    L.append("- **Decision F1** — de-inflated to human gold entries (≥50% files hit).")
    L.append("- **Component F1** — collapsed to (sentence, component_name).")
    L.append("- **Weighted F1** — file weighted by 1/block_size.")
    L.append("- **ACF1** — amplification-corrected (1/N component weighting).")
    L.append("- **MCC / NDG / HUS** — architecture-aware correlation / discrimination / usefulness.\n")

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
    print("SAD-CODE holistic comparison written:")
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
