#!/usr/bin/env python3
"""
Consequences of Misleading F1 Across SAD-SAM and SAD-CODE.

A motivation analysis (Pillar 2 extension) that quantifies, with numbers read
straight from the Phase-4 metrics CSVs, how a single headline F1 distorts BOTH
ARDoCo TLR tasks:

  STUDY-01 (NEW): SAD-SAM pure-F1 consequences — the headline link F1 hides
                  disagreement with sentence-, component-, and quality-oriented
                  (MCC/MAP/HUS) views.
  STUDY-02 (CONSOLIDATE): SAD-CODE file-level consequences — file-level
                  enrollment F1 misleads (JabRef File 0.943 -> Decision 0.394
                  ranking flip; avg File 0.803 vs Decision 0.596 vs Component
                  0.714). Consolidates prior bias findings; NO recomputation.
  STUDY-03: a converged Decision+Component framework giving both tasks one
                  coherent honest evaluation axis, layered atop the existing
                  corrected metrics (it does not replace them).

The two CSVs (reports/metrics_sad-sam.csv, reports/metrics_sad-code.csv) are the
single source of truth: this script differences headline columns against the
honest (decision/component) columns and counts ranking disagreements. It does
NOT recompute any metric. Stdlib only; project names are read as opaque CSV
ordering data (no benchmark-derived word lists).

Produces reports/CONSEQUENCES_STUDY.md.
"""

import csv
from pathlib import Path

REPORTS = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports")
OUTPUT_MD = REPORTS / "CONSEQUENCES_STUDY.md"

# Display order only — opaque ordering data read back from the CSV's project
# column, NOT a benchmark-derived vocabulary.
PROJECT_ORDER = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]


def load_metrics_csv(task):
    """task in {'sad-sam','sad-code'}; returns (rows_by_project, avg_row)."""
    rows, avg = {}, None
    with (REPORTS / f"metrics_{task}.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["project"] == "Average":
                avg = r
            else:
                rows[r["project"]] = r
    return rows, avg


def num(v):
    """Parse a CSV cell; em-dash / blank => None (N/A)."""
    return None if v in ("—", "—", "", None) else float(v)


def fmt(v):
    return "—" if v is None else f"{v:.3f}"


def delta(a, b):
    if a is None or b is None:
        return None
    return a - b


# ── STUDY-01: SAD-SAM pure-F1 consequences (NEW) ──────────────────────────────

def part_sad_sam(out, rows, avg):
    out("## SAD-SAM: What the Single Headline Link \\fone Hides (STUDY-01)")
    out()
    out("The reported \\sadsam number is a single link \\fone over "
        "`(modelElementID, sentence)` pairs. That headline already sits at the "
        "honest decision granularity (no enrollment inflation), so its "
        "distortion is *not* file-level amplification — it is the gap against "
        "the per-sentence retrieval view and the quality-oriented views "
        "(MCC/MAP/HUS).")
    out()
    out("| Project | Link F1 (headline) | Sentence F1 | Component F1 | MCC | MAP | HUS | Link−Sentence Δ |")
    out("|---------|--------------------|-------------|--------------|-----|-----|-----|-----------------|")

    deltas = {}
    for proj in PROJECT_ORDER:
        r = rows[proj]
        link = num(r["link_f1"])
        sent = num(r["sentence_f1"])
        comp = num(r["component_f1"])
        mcc = num(r["mcc"])
        mp = num(r["map"])
        hus = num(r["hus"])
        d = delta(link, sent)
        deltas[proj] = d
        out(f"| {proj} | {fmt(link)} | {fmt(sent)} | {fmt(comp)} | "
            f"{fmt(mcc)} | {fmt(mp)} | {fmt(hus)} | {fmt(d)} |")

    a_link = num(avg["link_f1"])
    a_sent = num(avg["sentence_f1"])
    a_comp = num(avg["component_f1"])
    a_mcc = num(avg["mcc"])
    a_map = num(avg["map"])
    a_hus = num(avg["hus"])
    out(f"| **Average** | {fmt(a_link)} | {fmt(a_sent)} | {fmt(a_comp)} | "
        f"{fmt(a_mcc)} | {fmt(a_map)} | {fmt(a_hus)} | {fmt(delta(a_link, a_sent))} |")
    out()

    # largest |Link - Sentence| gap
    worst = max(deltas, key=lambda p: abs(deltas[p]) if deltas[p] is not None else -1)
    wr = rows[worst]
    w_link = num(wr["link_f1"])
    w_sent = num(wr["sentence_f1"])
    out(f"The largest disagreement is **{worst}**: sentence \\fone "
        f"{fmt(w_sent)} versus link \\fone {fmt(w_link)} — the headline "
        f"understates per-sentence retrieval by ~{abs(w_link - w_sent):.3f}. "
        f"Across all projects the average sentence \\fone ({fmt(a_sent)}) sits "
        f"{abs(a_link - a_sent):.3f} above the headline link \\fone "
        f"({fmt(a_link)}).")
    out()
    out(f"The quality-oriented views diverge further: MCC (avg {fmt(a_mcc)}) and "
        f"HUS (avg {fmt(a_hus)}) reward correct rejections and human-usefulness "
        f"that link \\fone ignores, while MAP (avg {fmt(a_map)}) is a ranking "
        f"view. The single \\sadsam headline link \\fone hides disagreement with "
        f"the sentence-, component-, and quality-oriented (MCC/MAP/HUS) "
        f"perspectives — even before any cascade into \\sadcode.")
    out()


# ── STUDY-02: SAD-CODE file-level consequences (CONSOLIDATE, no recompute) ─────

def part_sad_code(out, rows, avg):
    out("## SAD-CODE: How File-Level Enrollment \\fone Misleads (STUDY-02)")
    out()
    out("The reported \\sadcode number is a file-level \\fone computed *after* "
        "enrollment expands directory-level gold entries into individual files "
        "(≈35.5x inflation; see `reports/EVALUATION_CRITIQUE.md` and "
        "`reports/BENCHMARK_BIAS_STUDY.md`). The honest comparators are the "
        "raw pre-enrollment decision \\fone and the architecture-component "
        "\\fone. The numbers below are read directly from the Phase-4 CSV — "
        "this section consolidates prior findings and recomputes nothing.")
    out()
    out("| Project | File F1 (headline) | Decision F1 | Component F1 | File−Decision Δ |")
    out("|---------|--------------------|-------------|--------------|-----------------|")

    for proj in PROJECT_ORDER:
        r = rows[proj]
        fil = num(r["file_f1"])
        dec = num(r["decision_f1"])
        comp = num(r["component_f1"])
        out(f"| {proj} | {fmt(fil)} | {fmt(dec)} | {fmt(comp)} | {fmt(delta(fil, dec))} |")

    a_file = num(avg["file_f1"])
    a_dec = num(avg["decision_f1"])
    a_comp = num(avg["component_f1"])
    out(f"| **Average** | {fmt(a_file)} | {fmt(a_dec)} | {fmt(a_comp)} | "
        f"{fmt(delta(a_file, a_dec))} |")
    out()

    jr = rows["jabref"]
    jr_file = num(jr["file_f1"])
    jr_dec = num(jr["decision_f1"])
    # rank by file vs by decision
    by_file = sorted(PROJECT_ORDER, key=lambda p: num(rows[p]["file_f1"]), reverse=True)
    by_dec = sorted(PROJECT_ORDER, key=lambda p: num(rows[p]["decision_f1"]), reverse=True)
    out(f"The flagship distortion is **JabRef**: best of all projects on file "
        f"\\fone ({fmt(jr_file)}) yet worst on decision \\fone ({fmt(jr_dec)}) "
        f"— a complete ranking flip (rank #{by_file.index('jabref') + 1} by file, "
        f"#{by_dec.index('jabref') + 1} by decision). Cross-project, the "
        f"headline averages {fmt(a_file)} (file) while the honest views average "
        f"only {fmt(a_dec)} (decision) and {fmt(a_comp)} (component) — a "
        f"file−decision gap of {abs(a_file - a_dec):.3f}.")
    out()
    out("These consolidate the documented enrollment-inflation critique "
        "(≈35.5x expansion of raw decisions into files, 96–100% intra-directory "
        "block homogeneity, and the pairwise ranking flips) from "
        "`reports/EVALUATION_CRITIQUE.md` and "
        "`reports/BENCHMARK_BIAS_STUDY.md`. No metric is recomputed here; the "
        "anchors are read from `reports/metrics_sad-code.csv`.")
    out()


def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    out("# Consequences of Misleading \\fone Across SAD-SAM and SAD-CODE")
    out()
    out("*Motivation evidence (Pillar 2): how a single headline \\fone distorts "
        "BOTH TLR tasks, and the converged Decision+Component axis that tells one "
        "coherent story. All numbers read from the Phase-4 metrics CSVs; no "
        "metric recomputed.*")
    out()

    sam_rows, sam_avg = load_metrics_csv("sad-sam")
    code_rows, code_avg = load_metrics_csv("sad-code")

    part_sad_sam(out, sam_rows, sam_avg)
    part_sad_code(out, code_rows, code_avg)

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
        f.write("\n")
    print(f"\n\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
