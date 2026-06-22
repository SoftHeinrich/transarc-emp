#!/usr/bin/env python3
"""Per-component structural importance vs enrollment-inflated link-pair weight.

Thesis (Ch2 benchmark-bias pillar)
----------------------------------
File-level SAD-CODE F1 weights each gold component by how many *files* live under
its enrolled directories -- an implementation accident (package fatness), not an
architectural importance signal. A small package can be a central dependency hub.

This module measures, per gold component, signals that are INDEPENDENT of the
link annotation and of file count:

  files        # code files mapped to the component (the F1 weight proxy)
  file_pct     files as % of all mapped files
  linkpair_pct % of enrolled (sentence,file) gold pairs (the F1 ruler) [ref]
  classes      # ClassUnit + InterfaceUnit
  methods      # ControlElement members (sum over classes)
  fan_in       # cross-component datatype references pointing INTO the component
  fanin_pct    fan_in as % of all cross-component edges
  fanin_file   fan_in / files  -- depended-upon-ness per file (centrality density)

fan_in is mined straight from `datatypeReferencesIds` in the `.acm` code model:
an edge A->B where comp(A) != comp(B) is one cross-component dependency into B.
A small component with high fanin_file is small-but-central (e.g. a config hub);
a small component with low fanin_file is genuinely peripheral. Link-pair % cannot
tell the two apart -- this suite can.

Component universe = the SAM-CODE gold mapping (same file->component map the F1
suite uses), so a file maps to >=1 gold component and the rows align with
component_suite.py. Files with no SAM-CODE mapping are dropped (not gold
components). A file shared by N components contributes to each.

Run
---
    python3 src/bias/component_centrality.py                 # all projects -> CSV
    python3 src/bias/component_centrality.py --project jabref
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS, ACM_FILES, normalize_path,
    load_code_model_files, load_model_element_names,
    load_gs_sam_code_raw, load_gs_sad_code_enrolled, enroll_gold_standard,
)

REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"
COLS = ["files", "file_pct", "linkpair_pct", "classes", "methods",
        "fan_in", "fanin_pct", "fanin_file"]


def _short(c):
    return c.replace("Component: ", "").replace("Interface: ", "")


def _file_to_comps(proj, code_model):
    """Map each enrolled code file -> set(component names) via SAM-CODE gold."""
    names = load_model_element_names(proj)
    f2c = defaultdict(set)
    for ae, fp in enroll_gold_standard(load_gs_sam_code_raw(proj), code_model):
        f2c[fp].add(names.get(ae, ae))
    return f2c


def _cu_path(item):
    """Reconstruct a CodeCompilationUnit's normalized path (matches the loader)."""
    pe = item.get("pathElements", [])
    name = item.get("name", "")
    if not (pe and name):
        return None
    p = "/".join(pe) + "/" + name
    ext = item.get("extension", "")
    if ext:
        p += "." + ext
    return normalize_path(p)


def analyze(proj):
    code_model = load_code_model_files(proj)
    f2c = _file_to_comps(proj, code_model)

    repo = json.load(open(ACM_FILES[proj]))["codeItemRepository"]["repository"]

    # CU id -> normalized path -> components
    cu_comps = {}
    for v in repo.values():
        if v.get("type") == "CodeCompilationUnit":
            p = _cu_path(v)
            cu_comps[v["id"]] = f2c.get(p, set()) if p else set()

    # datatype (ClassUnit/InterfaceUnit) id -> components; class/method tallies
    dt_comps = {}
    classes = defaultdict(int)
    methods = defaultdict(int)
    files = defaultdict(set)
    for v in repo.values():
        if v.get("type") in ("ClassUnit", "InterfaceUnit"):
            comps = cu_comps.get(v.get("compilationUnitId"), set())
            dt_comps[v["id"]] = comps
            for c in comps:
                classes[c] += 1
                files[c].add(v.get("compilationUnitId"))
                methods[c] += len(v.get("content", []))

    # cross-component fan-in over datatype reference edges
    fan_in = defaultdict(int)
    for v in repo.values():
        if v.get("type") in ("ClassUnit", "InterfaceUnit"):
            src = dt_comps.get(v["id"], set())
            for ref in v.get("datatypeReferencesIds", []):
                dst = dt_comps.get(ref, set())
                for dc in dst:
                    if dc not in src:  # edge crosses into component dc
                        fan_in[dc] += 1

    # link-pair weight (the F1 ruler) per component
    linkpairs = defaultdict(int)
    for s, f in load_gs_sad_code_enrolled(proj, code_model):
        for c in f2c.get(f, ()):
            linkpairs[c] += 1

    # Teammates/BBB define an Interface:X and Component:X over IDENTICAL file sets
    # (100% file overlap). They produce byte-identical metric rows -- collapse to
    # one so the table is not doubled. Distinct components that merely share a
    # short name but differ in files (e.g. TeaStore Recommender 14-file vs 1-file)
    # are kept separate because their file signature differs.
    seen = {}
    for c in list(files):
        sig = (_short(c), frozenset(files[c]))
        if sig in seen:
            del files[c]
        else:
            seen[sig] = c

    comps = sorted(files, key=lambda c: -len(files[c]))
    totf = sum(len(files[c]) for c in comps) or 1
    totlp = sum(linkpairs.values()) or 1
    totfi = sum(fan_in[c] for c in comps) or 1

    rows = []
    for c in comps:
        nf = len(files[c])
        rows.append((c, {
            "files": nf,
            "file_pct": 100 * nf / totf,
            "linkpair_pct": 100 * linkpairs[c] / totlp,
            "classes": classes[c],
            "methods": methods[c],
            "fan_in": fan_in[c],
            "fanin_pct": 100 * fan_in[c] / totfi,
            "fanin_file": fan_in[c] / max(nf, 1),
        }))
    return rows


def _fmt(c, v):
    if c in ("file_pct", "linkpair_pct", "fanin_pct"):
        return f"{v:.1f}"
    if c == "fanin_file":
        return f"{v:.1f}"
    return f"{v:d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    args = ap.parse_args()
    projects = [args.project] if args.project else list(PROJECTS)

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "COMPONENT_CENTRALITY.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["project", "component"] + COLS)
        for proj in projects:
            rows = analyze(proj)
            print(f"\n=== {proj} ===")
            print(f"{'component':22}" + "".join(f"{c:>13}" for c in COLS))
            for c, m in rows:
                print(f"{_short(c):22}" + "".join(f"{_fmt(k, m[k]):>13}" for k in COLS))
                w.writerow([proj, _short(c)] + [f"{m[k]:.4f}" if isinstance(m[k], float)
                                                else m[k] for k in COLS])
    print(f"\n[centrality] csv={out}")


if __name__ == "__main__":
    main()
