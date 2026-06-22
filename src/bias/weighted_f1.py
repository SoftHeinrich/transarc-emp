#!/usr/bin/env python3
"""Importance-weighted macro F1: does the aggregation weight change who wins?

The enrollment bias is a WEIGHT problem: file-level F1 weights each gold
component by package fatness (#enrolled files). This script recomputes a macro
F1 over the SAME per-component F1s under four weights and compares system
rankings:

  file      w = #files mapped to component          (the biased, status-quo weight)
  flat      w = 1                                    (unweighted macro; size-blind)
  fanin     w = cross-component dependency edges in  (structural centrality)
  commit    w = commits touching component's files   (dev activity; 4 repos only)

Weights are Laplace-smoothed (w+1) so a zero-weight component is down-weighted,
not deleted (every gold component is real and must still count).

Two questions:
  1. Does fanin-weighting reorder systems vs file/flat? (is it a distinct ruler?)
  2. Is commit-weighting NECESSARY -- does it ever change the ranking that
     fanin-weighting already produces, or is it redundant with fanin?

Per-component F1 comes from component_suite (calc_metrics on the mapped-only
sad-code universe). Weights come from component_centrality / component_commits.

Run:  python3 src/bias/weighted_f1.py
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from component_suite import _code_inputs, SYSTEMS  # noqa: E402
from component_centrality import analyze as centrality_analyze  # noqa: E402

sys.path.insert(0, str(HERE.parent / "lib"))
from transarc_error_analysis import PROJECTS, calc_metrics  # noqa: E402

REPORTS = HERE.parent.parent / "reports"
WEIGHTS = ["file", "flat", "fanin", "commit"]


def _short(c):
    return c.replace("Component: ", "").replace("Interface: ", "")


def commit_weights():
    """short component name -> commits_touching, per project (4 repos)."""
    out = defaultdict(dict)
    p = REPORTS / "COMPONENT_COMMITS.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            out[r["project"]][r["component"]] = int(r["commits_touching"])
    return out


def per_component_f1(proj):
    """system key -> {component (full name) -> F1} on sad-code."""
    gold, collapse = _code_inputs(proj)
    loaders = {k: cl for k, _, _, cl in SYSTEMS}
    gold_by_c = defaultdict(set)
    for s, c in gold:
        gold_by_c[c].add(s)
    res = {}
    for k in loaders:
        links = loaders[k](proj)
        if not links:
            continue
        rc = defaultdict(set)
        for s, c in collapse(links):
            rc[c].add(s)
        res[k] = {c: calc_metrics({(s, c) for s in gold_by_c[c]},
                                  {(s, c) for s in rc.get(c, set())})[2]
                  for c in gold_by_c}
    return gold_by_c, res


def project_weights(proj, gold_components, cwts):
    """component (full name) -> {weight scheme -> smoothed weight}."""
    # fan-in + file counts from centrality (analyze() returns FULL component names;
    # the centrality CSV/display shorts them, but analyze() does not).
    cen = {c: m for c, m in centrality_analyze(proj)}  # full name -> metrics
    w = {}
    for c in gold_components:
        files = cen.get(c, {}).get("files", 0)
        fanin = cen.get(c, {}).get("fan_in", 0)
        commit = cwts.get(proj, {}).get(_short(c))  # commit CSV is short-keyed
        w[c] = {
            "file": files + 1,
            "flat": 1,
            "fanin": fanin + 1,
            "commit": (commit + 1) if commit is not None else None,
        }
    return w


def weighted(f1_by_c, w_by_c, scheme):
    num = den = 0.0
    for c, f1 in f1_by_c.items():
        wt = w_by_c[c][scheme]
        if wt is None:
            return None
        num += wt * f1
        den += wt
    return num / den if den else 0.0


def _avg(xs):
    return sum(xs) / len(xs) if xs else None


def main():
    cwts = commit_weights()
    commit_projects = set(cwts)  # repos with real commit history (no mediastore)
    # cell[system][scheme][project] = weighted F1
    cell = defaultdict(lambda: defaultdict(dict))
    print(f"{'project':14}{'system':18}" + "".join(f"{s:>9}" for s in WEIGHTS))
    for proj in PROJECTS:
        gold_by_c, res = per_component_f1(proj)
        w_by_c = project_weights(proj, gold_by_c.keys(), cwts)
        for k in res:
            label = dict((kk, lab) for kk, lab, _, _ in SYSTEMS)[k]
            vals = {}
            for sc in WEIGHTS:
                v = weighted(res[k], w_by_c, sc)
                vals[sc] = v
                if v is not None:
                    cell[label][sc][proj] = v
            cells = "".join(f"{(f'{vals[sc]:.3f}' if vals[sc] is not None else '--'):>9}"
                            for sc in WEIGHTS)
            print(f"{proj:14}{label:18}{cells}")

    labels = sorted(cell)

    REPORTS.mkdir(parents=True, exist_ok=True)
    with (REPORTS / "WEIGHTED_F1.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["project", "system"] + WEIGHTS)
        for proj in PROJECTS:
            for lab in labels:
                if any(proj in cell[lab][sc] for sc in WEIGHTS):
                    w.writerow([proj, lab] + [
                        (f"{cell[lab][sc][proj]:.4f}" if proj in cell[lab][sc] else "")
                        for sc in WEIGHTS])

    def block(title, projset):
        print(f"\n=== {title} ===")
        print(f"{'system':18}" + "".join(f"{s:>9}" for s in WEIGHTS))
        avgs = {}
        for lab in labels:
            avgs[lab] = {sc: _avg([v for p, v in cell[lab][sc].items() if p in projset])
                         for sc in WEIGHTS}
            cells = "".join(f"{(f'{avgs[lab][sc]:.3f}' if avgs[lab][sc] is not None else '--'):>9}"
                            for sc in WEIGHTS)
            print(f"{lab:18}{cells}")
        print("-- ranking (best first) --")
        for sc in WEIGHTS:
            rank = sorted([l for l in labels if avgs[l][sc] is not None],
                          key=lambda l: -avgs[l][sc])
            if rank:
                print(f"  {sc:8}: " + " > ".join(f"{l}({avgs[l][sc]:.3f})" for l in rank))
        return avgs

    block("average over ALL 5 projects (commit = its 4 repos)", set(PROJECTS))
    block("average over the 4 commit-repos ONLY (fair fanin-vs-commit)", commit_projects)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
