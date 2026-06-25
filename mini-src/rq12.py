#!/usr/bin/env python3
"""RQ1/RQ2 cross-system "big table" generator (CSV).

``metrics.py`` is a per-*system* calculator whose output axis is *projects*: it
scores one result set at a time and prints a per-project panel + macro average.
The paper's RQ1/RQ2 tables have *systems* on the row axis, the approach averaged
over three runs, and a per-task layout. This driver closes that gap: it sweeps
the system roster, scores each through ``metrics.py`` (the sole metric impl),
macro-averages over the five projects, averages the approach over its three
runs, and emits ONE wide CSV whose columns are the union of both tasks.

That single big table is a superset of every RQ1/RQ2 cell:
  * RQ1 doc-to-model (tab:rq1-sadsam) = columns ``ss_P, ss_R, ss_linkF1``.
  * RQ1 doc-to-code  (tab:rq1-sadcode) = columns ``sc_P, sc_R, sc_fileF1``.
  * RQ2 size-aware panel (tab:rq2-summary) = the GPT-5.4 rows' columns
    ``sc_fileF1, sc_sentCov, sc_worstC, sc_harmC`` (+ the appended Delta row).

It generates only the numbers (a CSV); it does not write .tex. No new metric
code lives here — every cell comes from ``metrics.compute_sad_{code,sam}``, so
``check.py``'s frozen goldens still pin the arithmetic.

Inputs (the normalized SOTA dump; ``sentence_id,target_id`` dialect, which
``metrics.load_result`` auto-detects):
    <ardoco-home>/sota/recovered-links/
      model-doc/   doc-to-model links  (SWATTR/Artemis/LiSSA + aalinker/<be>/run*)
      doc-code/    doc-to-code  links  (TransArc/Artemis/LiSSA + aalinker-composed/<be>/run*)
Override the root via ``$SOTA_LINKS``.

Usage
-----
    python3 mini-src/rq12.py                      # -> reports/RQ12_BIGTABLE.csv (+ stdout)
    python3 mini-src/rq12.py --csv /tmp/big.csv
    python3 mini-src/rq12.py --lissa              # also include the LiSSA row(s)

Provenance note (worst/harmonic, the approach rows): these are recomputed here
from the bundled three-run ``aalinker-composed`` dump (mean of the three runs).
The paper's RQ2 worst/harmonic for the approach (.62/.71) were produced by a
now-deleted script over a now-deleted run set (``v2.6.5_s20union_gpt_re_medium``);
the file-F1 still matches (~.874), but the run-sensitive tail does not. The
values emitted here are the reproducible ones from surviving data.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as m   # noqa: E402  (mini-src/metrics.py — sole metric impl + loaders)

SOTA_LINKS = Path(os.environ.get("SOTA_LINKS", m._ARDOCO_HOME / "sota/recovered-links"))

# ── System roster (matches tables/cross_system.tex) ───────────────────────────
# Each entry resolves a per-(run,)project file path for both tasks. `runs=None`
# means single-shot (deterministic / SOTA); a run list means mean-of-runs.
# `aalinker`/`aalinker-composed` are the recovered doc-to-model / composed
# doc-to-code dumps of s_linker20_union. SWATTR is TransArC's deterministic
# doc-to-model stage (TransArC has no standalone doc-to-model system).
ROSTER = [
    {"label": "approach (Claude)",  "backend": "claude",  "runs": ["run1", "run2", "run3"],
     "sad-sam":  "model-doc/aalinker/sonnet_full/{run}/{project}.csv",
     "sad-code": "doc-code/aalinker-composed/sonnet_full/{run}/{project}.csv"},
    {"label": "approach (GPT-5.4)", "backend": "gpt-5.4", "runs": ["run1", "run2", "run3"],
     "sad-sam":  "model-doc/aalinker/gpt-5.4_full/{run}/{project}.csv",
     "sad-code": "doc-code/aalinker-composed/gpt-5.4_full/{run}/{project}.csv"},
    {"label": "Artemis (GPT-5.4)",  "backend": "gpt-5.4", "runs": None,
     "sad-sam":  "model-doc/artemis-{project}-gpt-5.4.csv",
     "sad-code": "doc-code/artemis-{project}-gpt-5.4.csv"},
    {"label": "TransArC",           "backend": "deterministic", "runs": None,
     "sad-sam":  "model-doc/swattr-{project}.csv",        # SWATTR = TransArC doc-model
     "sad-code": "doc-code/transarc-{project}.csv"},
]
LISSA = {"label": "LiSSA (gpt-5-mini)", "backend": "gpt-5-mini", "runs": None,
         "sad-sam":  "model-doc/lissa-{project}-gpt-5-mini.csv",
         "sad-code": "doc-code/lissa-{project}-gpt-5-mini.csv"}

# Combined big-table column layout: friendly name -> (task, metric key in PANELS).
SS = "sad-sam"
SC = "sad-code"
COLUMNS = [
    ("ss_P",       SS, "link_p"),       ("ss_R",       SS, "link_r"),
    ("ss_linkF1",  SS, "link_f1"),      ("ss_sentCov", SS, "sentence_coverage"),
    ("ss_noise",   SS, "noise_rate"),
    ("sc_P",       SC, "file_p"),       ("sc_R",       SC, "file_r"),
    ("sc_fileF1",  SC, "file_f1"),      ("sc_compF1",  SC, "component_f1"),
    ("sc_worstC",  SC, "worst_component_f1"),
    ("sc_harmC",   SC, "harmonic_component_f1"),
    ("sc_sentCov", SC, "sentence_coverage"),
    ("sc_noise",   SC, "noise_rate"),
]


def macro_panel(system, task):
    """Macro-averaged metric vector for one system on one task.

    Scores every project through ``metrics.compute_*`` (skipping projects whose
    result file is absent), macro-averages, and — for multi-run systems —
    averages those macro vectors over the runs (the paper's "mean of three
    runs"). Returns (vector_dict | None, n_projects_covered).
    """
    cols = m.PANELS[task]
    compute = m.compute_sad_code if task == SC else m.compute_sad_sam
    pattern = system[task]
    runs = system["runs"] or [None]

    run_vectors, n_covered = [], 0
    for run in runs:
        rows = []
        for proj in m.PROJECTS:
            rel = pattern.format(run=run, project=proj) if run else pattern.format(project=proj)
            path = SOTA_LINKS / rel
            if not path.exists():
                continue
            res = m.load_result(path, task)
            if not res:
                continue
            rows.append(compute(proj, res))
        if not rows:
            continue
        run_vectors.append({c: sum(r[c] for r in rows) / len(rows) for c in cols})
        n_covered = max(n_covered, len(rows))
    if not run_vectors:
        return None, 0
    vec = {c: sum(v[c] for v in run_vectors) / len(run_vectors) for c in cols}
    return vec, n_covered


def build_row(system):
    """One big-table row: {label, backend, n_ss, n_sc, <COLUMNS...>}."""
    ss_vec, n_ss = macro_panel(system, SS)
    sc_vec, n_sc = macro_panel(system, SC)
    row = {"system": system["label"], "backend": system["backend"],
           "n_ss": n_ss, "n_sc": n_sc}
    for name, task, key in COLUMNS:
        vec = ss_vec if task == SS else sc_vec
        row[name] = vec[key] if vec is not None else None
    return row


def delta_row(rows, a_label, b_label):
    """Δ row (a − b), per the RQ2 panel's Δ = approach − Artemis column."""
    a = next((r for r in rows if r["system"] == a_label), None)
    b = next((r for r in rows if r["system"] == b_label), None)
    if not a or not b:
        return None
    out = {"system": f"Delta ({a_label} - {b_label})", "backend": "", "n_ss": "", "n_sc": ""}
    for name, _, _ in COLUMNS:
        out[name] = (a[name] - b[name]) if (a[name] is not None and b[name] is not None) else None
    return out


def fmt(v):
    return "" if v is None or v == "" else (f"{v:.4f}" if isinstance(v, float) else str(v))


def print_table(rows):
    names = [c[0] for c in COLUMNS]
    w = max(len(r["system"]) for r in rows) + 1
    head = "system".ljust(w) + "".join(n.rjust(11) for n in names)
    print(head)
    print("-" * len(head))
    for r in rows:
        print(r["system"].ljust(w) + "".join(fmt(r[n]).rjust(11) for n in names))


def write_csv(rows, path):
    fields = ["system", "backend", "n_ss", "n_sc"] + [c[0] for c in COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            w.writerow([fmt(r[k]) for k in fields])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=None,
                    help="output CSV path (default: <evaluation>/reports/RQ12_BIGTABLE.csv)")
    ap.add_argument("--lissa", action="store_true",
                    help="also include the LiSSA row (covers 3/5 projects for doc-to-code)")
    args = ap.parse_args()

    roster = ROSTER + ([LISSA] if args.lissa else [])
    rows = [build_row(s) for s in roster]
    d = delta_row(rows, "approach (GPT-5.4)", "Artemis (GPT-5.4)")
    if d:
        rows.append(d)

    print_table(rows)
    print(f"\nProvenance: {SOTA_LINKS}  (approach = mean of run1/run2/run3)")
    print("RQ1 sad-sam = ss_P/ss_R/ss_linkF1 ; RQ1 sad-code = sc_P/sc_R/sc_fileF1 ;")
    print("RQ2 panel  = GPT-5.4 rows' sc_fileF1/sc_sentCov/sc_worstC/sc_harmC (+ Delta row).")

    out = Path(args.csv) if args.csv else (m._ARDOCO_HOME / "transarc-emp/reports/RQ12_BIGTABLE.csv")
    write_csv(rows, out)
    print(f"\n[rq12] wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
