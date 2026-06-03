"""
Long-tail distribution analysis for SAM-CODE trace links.
Views: component-centric (#files per architecture element, after enrollment)
       file-centric (#components per code file)
"""

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")

PROJECTS = {
    "mediastore":    "sam_2016-code_2016",
    "teastore":      "sam_2020-code_2022",
    "teammates":     "sam_2021-code_2023",
    "bigbluebutton": "sam_2021-code_2023",
    "jabref":        "sam_2021-code_2023",
}


def load_code_model(project: str) -> dict[str, list[str]]:
    acm_glob = list((BENCHMARK / project).rglob("codeModel.acm"))
    if not acm_glob:
        return {}
    with open(acm_glob[0]) as f:
        data = json.load(f)
    files: list[str] = []
    repo = data.get("codeItemRepository", {}).get("repository", {})
    if not repo:
        def walk(node):
            if isinstance(node, dict):
                p = node.get("path", "")
                if p.endswith((".java", ".py", ".cpp", ".h", ".c", ".cs")):
                    files.append(p.lstrip("/"))
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        walk(data)
    else:
        for item in repo.values():
            if item.get("type") == "CodeCompilationUnit":
                parts = item.get("pathElements", [])
                name = item.get("name", "")
                ext = item.get("extension", "")
                if parts and name:
                    fname = f"{name}.{ext}" if ext else name
                    files.append("/".join(parts) + "/" + fname)
    dir_index: dict[str, list[str]] = defaultdict(list)
    for fp in files:
        parts = fp.split("/")
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i]) + "/"
            dir_index[prefix].append(fp)
    return dict(dir_index)


def load_sam_code_enrolled(project: str, suffix: str) -> list[tuple[str, str, str]]:
    """Returns list of (ae_id, ae_name, file_path) after directory enrollment."""
    path = BENCHMARK / project / "goldstandards" / f"goldstandard_{suffix}.csv"
    dir_index = load_code_model(project)
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        ce_col = "ce_id" if "ce_id" in reader.fieldnames and "ce_ids" not in reader.fieldnames else "ce_ids"
        for row in reader:
            ae_id = row["ae_id"].strip()
            ae_name = row.get("ae_name", "").strip()
            cid = row[ce_col].strip()
            cid_stripped = cid.removeprefix("Implementation/")
            if cid_stripped.endswith("/"):
                expanded = dir_index.get(cid_stripped, [])
                for fp in expanded:
                    rows.append((ae_id, ae_name, fp))
            else:
                rows.append((ae_id, ae_name, cid_stripped))
    return rows


# ── statistics (same as longtail_analysis.py) ────────────────────────────────

def gini(counts):
    if not counts or sum(counts) == 0: return 0.0
    n = len(counts); s = sorted(counts); cumsum = 0
    for i, v in enumerate(s):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * sum(counts))

def top_k_share(counts, k=0.2):
    if not counts: return 0.0
    s = sorted(counts, reverse=True); cutoff = max(1, int(len(s) * k))
    return sum(s[:cutoff]) / sum(s)

def cv(counts):
    if not counts: return 0.0
    n = len(counts); mean = sum(counts) / n
    if mean == 0: return 0.0
    return math.sqrt(sum((x - mean) ** 2 for x in counts) / n) / mean

def skewness(counts):
    if len(counts) < 3: return 0.0
    n = len(counts); mean = sum(counts) / n
    variance = sum((x - mean) ** 2 for x in counts) / n
    if variance == 0: return 0.0
    std = math.sqrt(variance)
    return (sum((x - mean) ** 3 for x in counts) / n) / (std ** 3)

def percentiles(counts, pcts=(50, 75, 90, 95, 99)):
    if not counts: return {p: 0.0 for p in pcts}
    s = sorted(counts); n = len(s); result = {}
    for p in pcts:
        idx = (p / 100) * (n - 1); lo, hi = int(idx), min(int(idx) + 1, n - 1)
        result[p] = s[lo] * (1 - (idx - lo)) + s[hi] * (idx - lo)
    return result

def zipf_r2(counts):
    s = sorted([c for c in counts if c > 0], reverse=True)
    if len(s) < 3: return 0.0
    lr = [math.log(i + 1) for i in range(len(s))]; lf = [math.log(c) for c in s]
    n = len(lr); mr = sum(lr)/n; mf = sum(lf)/n
    cov = sum((r-mr)*(f-mf) for r,f in zip(lr,lf))
    vr = sum((r-mr)**2 for r in lr); vf = sum((f-mf)**2 for f in lf)
    return (cov**2)/(vr*vf) if vr and vf else 0.0

def summarize(counts):
    if not counts: return {}
    pcts = percentiles(counts)
    return {
        "n": len(counts), "total": sum(counts),
        "mean": sum(counts)/len(counts), "median": pcts[50],
        "p75": pcts[75], "p90": pcts[90], "p95": pcts[95], "p99": pcts[99],
        "max": max(counts), "min": min(counts),
        "cv": cv(counts), "skew": skewness(counts), "gini": gini(counts),
        "top20": top_k_share(counts, 0.2), "top10": top_k_share(counts, 0.1),
        "max_share": max(counts)/sum(counts),
        "zipf_r2": zipf_r2(counts),
        "singletons": sum(1 for c in counts if c == 1),
        "singleton_frac": sum(1 for c in counts if c == 1)/len(counts),
    }

def verdict(s):
    if not s: return "N/A"
    score = 0; reasons = []
    if s["gini"] > 0.5: score+=1; reasons.append(f"Gini={s['gini']:.2f}")
    if s["cv"] > 1.0:   score+=1; reasons.append(f"CoV={s['cv']:.2f}")
    if s["skew"] > 2.0: score+=1; reasons.append(f"skew={s['skew']:.2f}")
    if s["top20"] > 0.6:score+=1; reasons.append(f"top20={s['top20']:.2f}")
    if s["zipf_r2"] > 0.8: score+=1; reasons.append(f"ZipfR²={s['zipf_r2']:.2f}")
    labels = {0:"NOT long-tail",1:"weak",2:"moderate",3:"strong",4:"very strong",5:"HEAVY-TAIL"}
    return f"{labels.get(score,'strong')}  [{'; '.join(reasons) or 'none'}]"

def histogram(counts, bins=None):
    pass

def print_stats(s, indent="  "):
    if not s: print(f"{indent}(empty)"); return
    print(f"{indent}n={s['n']}  total={s['total']}  mean={s['mean']:.1f}  median={s['median']:.0f}")
    print(f"{indent}p75={s['p75']:.0f}  p90={s['p90']:.0f}  p95={s['p95']:.0f}  p99={s['p99']:.0f}  max={s['max']}")
    print(f"{indent}Gini={s['gini']:.3f}  CoV={s['cv']:.3f}  skew={s['skew']:.3f}")
    print(f"{indent}top20%={s['top20']:.3f}  top10%={s['top10']:.3f}  max_share={s['max_share']:.3f}")
    print(f"{indent}Zipf R²={s['zipf_r2']:.3f}  singletons={s['singletons']} ({100*s['singleton_frac']:.0f}%)")


def main():
    summary_rows = []

    for project, suffix in PROJECTS.items():
        print(f"\n{'='*70}")
        print(f"PROJECT: {project.upper()}")
        print('='*70)

        links = load_sam_code_enrolled(project, suffix)
        raw_path = BENCHMARK / project / "goldstandards" / f"goldstandard_{suffix}.csv"
        raw_count = sum(1 for _ in open(raw_path)) - 1

        print(f"  Raw gold entries: {raw_count}  →  enrolled pairs: {len(links)}")

        # Build distributions
        comp_to_files: dict[str, set] = defaultdict(set)
        file_to_comps: dict[str, set] = defaultdict(set)
        comp_names: dict[str, str] = {}

        for ae_id, ae_name, fp in links:
            comp_to_files[ae_id].add(fp)
            file_to_comps[fp].add(ae_id)
            comp_names[ae_id] = ae_name

        comp_counts = [len(v) for v in comp_to_files.values()]
        file_counts = [len(v) for v in file_to_comps.values()]

        # Component detail
        print(f"\n  [Component view: #files per architecture element (after enrollment)]")
        s_comp = summarize(comp_counts)
        print_stats(s_comp)
        print(f"  >>> {verdict(s_comp)}")

        if comp_counts:
            print(f"\n  Top components by file count:")
            top = sorted(comp_to_files.items(), key=lambda x: -len(x[1]))[:8]
            for ae_id, files in top:
                name = comp_names.get(ae_id, ae_id[:16])
                print(f"    {name:45s}: {len(files):5d} files")

            print(f"\n  Histogram (components by #files):")
            bins = [1,2,3,5,10,20,50,100,500,999999]
            prev = 0
            for b in bins:
                n = sum(1 for c in comp_counts if prev < c <= b)
                label = f">{prev}" if b>=999999 else (f"={b}" if prev+1==b else f"{prev+1}-{b}")
                bar = "█" * int(30 * n / len(comp_counts))
                print(f"    {label:>8}: {n:3d} ({100*n/len(comp_counts):5.1f}%) {bar}")
                prev = b

        # File detail
        print(f"\n  [File view: #components per code file]")
        s_file = summarize(file_counts)
        print_stats(s_file)
        print(f"  >>> {verdict(s_file)}")

        if file_counts:
            print(f"\n  Histogram (files by #components):")
            bins = [1,2,3,4,5,10,999999]
            prev = 0
            for b in bins:
                n = sum(1 for c in file_counts if prev < c <= b)
                label = f">{prev}" if b>=999999 else (f"={b}" if prev+1==b else f"{prev+1}-{b}")
                bar = "█" * int(30 * n / max(1, len(file_counts)))
                print(f"    {label:>8}: {n:4d} ({100*n/len(file_counts):5.1f}%) {bar}")
                prev = b

        summary_rows.append((project, "comp→files", s_comp))
        summary_rows.append((project, "file→comps", s_file))

    # Summary table
    print(f"\n\n{'='*70}")
    print("CROSS-PROJECT SUMMARY — SAM-CODE")
    print('='*70)
    hdr = f"{'Project':14} {'View':12} {'n':>5} {'total':>7} {'mean':>7} {'Gini':>6} {'CoV':>6} {'skew':>6} {'top20%':>7} {'ZipfR2':>7}  Verdict"
    print(hdr); print("-"*len(hdr))
    for proj, view, s in summary_rows:
        if not s: continue
        v = verdict(s).split("[")[0].strip()
        print(f"{proj:14} {view:12} {s['n']:5d} {s['total']:7d} {s['mean']:7.1f} "
              f"{s['gini']:6.3f} {s['cv']:6.3f} {s['skew']:6.2f} "
              f"{s['top20']:7.3f} {s['zipf_r2']:7.3f}  {v}")
    print()


if __name__ == "__main__":
    main()
