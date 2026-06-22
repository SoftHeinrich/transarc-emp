#!/usr/bin/env python3
"""Per-component development activity (commit-touch share) vs link-pair weight.

A third annotation-free importance signal for the Ch2 benchmark-bias argument:
how much of a project's *development history* touches each gold component's
files. A component that owns a tiny share of enrolled link pairs can still be
edited in a large share of commits -- i.e. it is actively maintained, not a stub.

Method
------
Component -> path-prefix map comes from the SAM-CODE gold (ae_id -> ce_path; a
directory prefix or a single file), the same mapping the F1 suite enrolls. We
walk the repo's default-branch history (``git log --name-only``), and for each
commit mark every component whose prefix matches at least one changed file. We
then report, per component, the count and % of commits that touched it.

History is bounded with ``--until=<snapshot-year>-12-31`` so the window
approximates the code state the benchmark `.acm` was extracted from (model_YYYY).
A commit may touch several components, so the percentages do not sum to 100.

MediaStore is excluded: its benchmark repo is a single-commit academic snapshot
(no development history to mine).

Run
---
    python3 src/bias/component_commits.py            # all repos found under /tmp
    python3 src/bias/component_commits.py --project jabref --repo /tmp/cm_jabref
"""
import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB))
from transarc_error_analysis import (  # noqa: E402
    load_gs_sam_code_raw, load_model_element_names,
)

REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"

# project -> (default clone dir, snapshot-year cutoff matching the benchmark .acm)
DEFAULTS = {
    "jabref":        ("/tmp/cm_jabref",    "2023-12-31"),
    "teastore":      ("/tmp/cm_teastore",  "2022-12-31"),
    "teammates":     ("/tmp/cm_teammates", "2023-12-31"),
    "bigbluebutton": ("/tmp/cm_bbb",       "2023-12-31"),
}


def _short(c):
    return c.replace("Component: ", "").replace("Interface: ", "")


def component_prefixes(proj):
    """component short-name -> list of (prefix, is_dir) from SAM-CODE gold."""
    names = load_model_element_names(proj)
    pref = defaultdict(set)
    for ae, ce in load_gs_sam_code_raw(proj):
        pref[_short(names.get(ae, ae))].add(ce)
    # collapse Interface/Component that share an identical prefix set
    return {c: sorted(ps) for c, ps in pref.items()}


def _match(path, prefixes):
    for p in prefixes:
        if p.endswith("/"):
            if path.startswith(p):
                return True
        elif path == p or path.endswith("/" + p) or path.startswith(p):
            return True
    return False


def walk(repo, until):
    """Yield sets of changed file paths per commit on the default branch."""
    cmd = ["git", "-C", repo, "log", f"--until={until}",
           "--name-only", "--pretty=tformat:__COMMIT__"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    files = None
    for line in out.splitlines():
        if line == "__COMMIT__":
            if files is not None:
                yield files
            files = set()
        elif line.strip() and files is not None:
            files.add(line.strip())
    if files is not None:
        yield files


def analyze(proj, repo, until):
    prefixes = component_prefixes(proj)
    touched = defaultdict(int)
    total = 0
    for changed in walk(repo, until):
        total += 1
        for comp, ps in prefixes.items():
            if any(_match(f, ps) for f in changed):
                touched[comp] += 1
    rows = []
    for comp in sorted(prefixes, key=lambda c: -touched[c]):
        rows.append((comp, touched[comp], 100 * touched[comp] / total if total else 0.0))
    return total, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    ap.add_argument("--repo", default=None)
    args = ap.parse_args()

    if args.project:
        repo = args.repo or DEFAULTS[args.project][0]
        targets = {args.project: (repo, DEFAULTS[args.project][1])}
    else:
        targets = {p: v for p, v in DEFAULTS.items() if Path(v[0], ".git").exists()}

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "COMPONENT_COMMITS.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["project", "component", "commits_touching", "commit_pct", "total_commits"])
        for proj, (repo, until) in targets.items():
            total, rows = analyze(proj, repo, until)
            print(f"\n=== {proj} (history until {until}, {total} commits) ===")
            print(f"{'component':28}{'commits':>9}{'commit%':>9}")
            for comp, n, pct in rows:
                print(f"{comp:28}{n:>9}{pct:>9.1f}")
                w.writerow([proj, comp, n, f"{pct:.2f}", total])
    print(f"\n[commits] csv={out}")


if __name__ == "__main__":
    main()
