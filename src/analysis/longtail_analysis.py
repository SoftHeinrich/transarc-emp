"""
Long-tail distribution analysis for SAD-SAM and SAD-CODE trace links.
Two views: sentence-centric (how many targets per sentence) and
component-centric (how many sentences per component/model-element).
"""

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")

PROJECTS = {
    "mediastore":    ("sad_2016-sam_2016",  "sad_2016-code_2016"),
    "teastore":      ("sad_2020-sam_2020",  "sad_2020-code_2022"),
    "teammates":     ("sad_2021-sam_2021",  "sad_2021-code_2023"),
    "bigbluebutton": ("sad_2021-sam_2021",  "sad_2021-code_2023"),
    "jabref":        ("sad_2021-sam_2021",  "sad_2021-code_2023"),
}


# ── data loaders ────────────────────────────────────────────────────────────

def load_sad_sam(project: str, suffix: str) -> list[tuple[str, str]]:
    path = BENCHMARK / project / "goldstandards" / f"goldstandard_{suffix}.csv"
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((row["modelElementID"].strip(), row["sentence"].strip()))
    return rows


def load_code_model(project: str) -> dict[str, list[str]]:
    """Return {directory_prefix: [file_paths]} from .acm JSON."""
    acm_glob = list((BENCHMARK / project).rglob("codeModel.acm"))
    if not acm_glob:
        return {}
    with open(acm_glob[0]) as f:
        data = json.load(f)

    # ACM format: flat repository dict with CodeCompilationUnit entries
    # each has pathElements: list[str] + name + extension
    files: list[str] = []
    repo = data.get("codeItemRepository", {}).get("repository", {})
    if not repo:
        # older format: nested tree with "path" string fields
        def walk(node):
            if isinstance(node, dict):
                path = node.get("path", "")
                if path.endswith((".java", ".py", ".cpp", ".h", ".c", ".cs")):
                    files.append(path.lstrip("/"))
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
                    fp = "/".join(parts) + "/" + fname
                    files.append(fp)

    # Build dir → files index
    dir_index: dict[str, list[str]] = defaultdict(list)
    for fp in files:
        parts = fp.split("/")
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i]) + "/"
            dir_index[prefix].append(fp)
    return dict(dir_index)


def load_sad_code_enrolled(project: str, suffix: str) -> list[tuple[str, str]]:
    """Load SAD-CODE gold, enrolling directory entries to file entries."""
    path = BENCHMARK / project / "goldstandards" / f"goldstandard_{suffix}.csv"
    dir_index = load_code_model(project)

    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["sentenceID"].strip()
            cid = row["codeID"].strip()
            # strip Implementation/ prefix
            cid_stripped = cid.removeprefix("Implementation/")
            if cid_stripped.endswith("/"):
                # directory entry → expand
                expanded = dir_index.get(cid_stripped, [])
                if not expanded:
                    # fallback: try without trailing slash
                    expanded = dir_index.get(cid_stripped.rstrip("/") + "/", [])
                for fp in expanded:
                    rows.append((sid, fp))
            else:
                rows.append((sid, cid_stripped))
    return rows


# ── statistics ──────────────────────────────────────────────────────────────

def gini(counts: list[int]) -> float:
    if not counts or sum(counts) == 0:
        return 0.0
    n = len(counts)
    s = sorted(counts)
    cumsum = 0
    for i, v in enumerate(s):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * sum(counts))


def top_k_share(counts: list[int], k: float = 0.2) -> float:
    """Fraction of total links held by top k fraction of nodes."""
    if not counts:
        return 0.0
    s = sorted(counts, reverse=True)
    cutoff = max(1, int(len(s) * k))
    return sum(s[:cutoff]) / sum(s)


def cv(counts: list[int]) -> float:
    if not counts:
        return 0.0
    n = len(counts)
    mean = sum(counts) / n
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in counts) / n
    return math.sqrt(variance) / mean


def skewness(counts: list[int]) -> float:
    if len(counts) < 3:
        return 0.0
    n = len(counts)
    mean = sum(counts) / n
    variance = sum((x - mean) ** 2 for x in counts) / n
    if variance == 0:
        return 0.0
    std = math.sqrt(variance)
    return (sum((x - mean) ** 3 for x in counts) / n) / (std ** 3)


def percentiles(counts: list[int], pcts=(50, 75, 90, 95, 99)) -> dict[int, float]:
    if not counts:
        return {p: 0.0 for p in pcts}
    s = sorted(counts)
    n = len(s)
    result = {}
    for p in pcts:
        idx = (p / 100) * (n - 1)
        lo, hi = int(idx), min(int(idx) + 1, n - 1)
        frac = idx - lo
        result[p] = s[lo] * (1 - frac) + s[hi] * frac
    return result


def max_entry_share(counts: list[int]) -> float:
    """Max single node's share of total links."""
    if not counts or sum(counts) == 0:
        return 0.0
    return max(counts) / sum(counts)


def zipf_r2(counts: list[int]) -> float:
    """Fit rank-frequency to log-log; return R² as Zipf-fit quality."""
    s = sorted(counts, reverse=True)
    s = [c for c in s if c > 0]
    if len(s) < 3:
        return 0.0
    log_ranks = [math.log(i + 1) for i in range(len(s))]
    log_freqs = [math.log(c) for c in s]
    n = len(log_ranks)
    mean_r = sum(log_ranks) / n
    mean_f = sum(log_freqs) / n
    cov = sum((r - mean_r) * (f - mean_f) for r, f in zip(log_ranks, log_freqs))
    var_r = sum((r - mean_r) ** 2 for r in log_ranks)
    var_f = sum((f - mean_f) ** 2 for f in log_freqs)
    if var_r == 0 or var_f == 0:
        return 0.0
    return (cov ** 2) / (var_r * var_f)


def summarize(label: str, counts: list[int]) -> dict:
    if not counts:
        return {}
    pcts = percentiles(counts)
    return {
        "label": label,
        "n_nodes": len(counts),
        "total_links": sum(counts),
        "mean": sum(counts) / len(counts),
        "median": pcts[50],
        "p75": pcts[75],
        "p90": pcts[90],
        "p95": pcts[95],
        "p99": pcts[99],
        "max": max(counts),
        "min": min(counts),
        "cv": cv(counts),
        "skewness": skewness(counts),
        "gini": gini(counts),
        "top20_share": top_k_share(counts, 0.2),
        "top10_share": top_k_share(counts, 0.1),
        "max_share": max_entry_share(counts),
        "zipf_r2": zipf_r2(counts),
        "n_singletons": sum(1 for c in counts if c == 1),
        "singleton_frac": sum(1 for c in counts if c == 1) / len(counts),
    }


# ── per-project analysis ─────────────────────────────────────────────────────

def analyze_project(project: str, sam_suffix: str, code_suffix: str) -> dict:
    result = {"project": project}

    # ── SAD-SAM ──
    sam_links = load_sad_sam(project, sam_suffix)
    # sentence view: how many model elements per sentence
    sent_to_comps = defaultdict(set)
    comp_to_sents = defaultdict(set)
    for comp, sent in sam_links:
        sent_to_comps[sent].add(comp)
        comp_to_sents[comp].add(sent)

    sam_sent_counts = [len(v) for v in sent_to_comps.values()]
    sam_comp_counts = [len(v) for v in comp_to_sents.values()]
    result["sad_sam_total_links"] = len(sam_links)
    result["sad_sam_sentence_view"] = summarize("SAD-SAM sent→comp", sam_sent_counts)
    result["sad_sam_component_view"] = summarize("SAD-SAM comp→sent", sam_comp_counts)

    # ── SAD-CODE (enrolled) ──
    try:
        code_links = load_sad_code_enrolled(project, code_suffix)
    except Exception as e:
        result["sad_code_error"] = str(e)
        return result

    sent_to_files = defaultdict(set)
    file_to_sents = defaultdict(set)
    for sent, fp in code_links:
        sent_to_files[sent].add(fp)
        file_to_sents[fp].add(sent)

    code_sent_counts = [len(v) for v in sent_to_files.values()]
    code_file_counts = [len(v) for v in file_to_sents.values()]
    result["sad_code_total_links"] = len(code_links)
    result["sad_code_raw_entries"] = len(set((s, c) for s, c in code_links))
    result["sad_code_sentence_view"] = summarize("SAD-CODE sent→files", code_sent_counts)
    result["sad_code_file_view"] = summarize("SAD-CODE file→sents", code_file_counts)

    return result


# ── report ───────────────────────────────────────────────────────────────────

def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def print_view(stats: dict, indent: str = "  ") -> None:
    fields = [
        ("n_nodes",        "nodes"),
        ("total_links",    "total links"),
        ("mean",           "mean links/node"),
        ("median",         "median"),
        ("p75",            "p75"),
        ("p90",            "p90"),
        ("p95",            "p95"),
        ("p99",            "p99"),
        ("max",            "max"),
        ("cv",             "CoV (std/mean)"),
        ("skewness",       "skewness"),
        ("gini",           "Gini coeff"),
        ("top20_share",    "top-20% share"),
        ("top10_share",    "top-10% share"),
        ("max_share",      "max-node share"),
        ("zipf_r2",        "Zipf log-log R²"),
        ("n_singletons",   "singletons (=1)"),
        ("singleton_frac", "singleton frac"),
    ]
    for key, label in fields:
        val = stats.get(key, "—")
        print(f"{indent}{label:22s}: {fmt(val)}")


def long_tail_verdict(stats: dict) -> str:
    gini_v = stats.get("gini", 0)
    cv_v = stats.get("cv", 0)
    skew_v = stats.get("skewness", 0)
    t20 = stats.get("top20_share", 0)
    z_r2 = stats.get("zipf_r2", 0)
    score = 0
    reasons = []
    if gini_v > 0.5:
        score += 1; reasons.append(f"Gini={gini_v:.2f}>0.5")
    if cv_v > 1.0:
        score += 1; reasons.append(f"CoV={cv_v:.2f}>1")
    if skew_v > 2.0:
        score += 1; reasons.append(f"skew={skew_v:.2f}>2")
    if t20 > 0.6:
        score += 1; reasons.append(f"top20%={t20:.2f}>0.6")
    if z_r2 > 0.8:
        score += 1; reasons.append(f"Zipf R²={z_r2:.2f}>0.8")
    verdict = {0: "NOT long-tail", 1: "weak long-tail",
               2: "moderate long-tail", 3: "strong long-tail",
               4: "very strong long-tail", 5: "HEAVY-TAIL / power-law"}
    return f"{verdict.get(score,'strong')}  [{'; '.join(reasons) or 'none triggered'}]"


def print_histogram(counts: list[int], bins: list[int] = [1,2,3,5,10,20,50,100,999999]) -> None:
    if not counts:
        return
    bucket_labels = []
    bucket_counts_hist = []
    prev = 0
    for b in bins:
        n = sum(1 for c in counts if prev < c <= b)
        if b >= 999999:
            label = f">{prev}"
        elif prev + 1 == b:
            label = f"={b}"
        else:
            label = f"{prev+1}-{b}"
        bucket_labels.append(label)
        bucket_counts_hist.append(n)
        prev = b
    total = len(counts)
    for label, cnt in zip(bucket_labels, bucket_counts_hist):
        bar = "█" * int(cnt / max(bucket_counts_hist) * 30) if bucket_counts_hist else ""
        print(f"    {label:>8}: {cnt:4d} ({100*cnt/total:5.1f}%) {bar}")


def main():
    all_results = []
    for project, (sam_suffix, code_suffix) in PROJECTS.items():
        print(f"\n{'='*70}")
        print(f"PROJECT: {project.upper()}")
        print('='*70)
        r = analyze_project(project, sam_suffix, code_suffix)
        all_results.append(r)

        # SAD-SAM
        print(f"\n  SAD-SAM  ({r['sad_sam_total_links']} links)")
        print(f"\n  [Sentence view: links-per-sentence = #components this sentence mentions]")
        sv = r["sad_sam_sentence_view"]
        print_view(sv)
        print(f"  >>> VERDICT: {long_tail_verdict(sv)}")
        sv_counts = []
        sam_links = load_sad_sam(project, PROJECTS[project][0])
        from collections import defaultdict as dd
        stc = dd(set)
        for comp, sent in sam_links:
            stc[sent].add(comp)
        sv_counts = [len(v) for v in stc.values()]
        print(f"\n  Histogram (sentences by #components linked):")
        print_histogram(sv_counts, [1,2,3,4,5,6,7,8,9,10,20,999999])

        print(f"\n  [Component view: links-per-component = #sentences mentioning this component]")
        cv_stats = r["sad_sam_component_view"]
        print_view(cv_stats)
        print(f"  >>> VERDICT: {long_tail_verdict(cv_stats)}")
        cts = dd(set)
        for comp, sent in sam_links:
            cts[comp].add(sent)
        cv_counts = [len(v) for v in cts.values()]
        print(f"\n  Histogram (components by #sentences mentioning them):")
        print_histogram(cv_counts, [1,2,3,4,5,6,7,8,9,10,20,50,100,999999])

        # SAD-CODE
        if "sad_code_error" in r:
            print(f"\n  SAD-CODE error: {r['sad_code_error']}")
            continue
        print(f"\n  SAD-CODE enrolled ({r['sad_code_total_links']} enrolled link pairs)")

        print(f"\n  [Sentence view: #files this sentence links to (after enrollment)]")
        sc_sent = r["sad_code_sentence_view"]
        print_view(sc_sent)
        print(f"  >>> VERDICT: {long_tail_verdict(sc_sent)}")

        code_links = load_sad_code_enrolled(project, PROJECTS[project][1])
        stf = dd(set)
        fts = dd(set)
        for sent, fp in code_links:
            stf[sent].add(fp)
            fts[fp].add(sent)
        sc_sent_counts = [len(v) for v in stf.values()]
        print(f"\n  Histogram (sentences by #files linked):")
        print_histogram(sc_sent_counts, [1,2,5,10,20,50,100,200,500,999999])

        print(f"\n  [File view: #sentences linking to this file]")
        sc_file = r["sad_code_file_view"]
        print_view(sc_file)
        print(f"  >>> VERDICT: {long_tail_verdict(sc_file)}")
        sc_file_counts = [len(v) for v in fts.values()]
        print(f"\n  Histogram (files by #sentences linking to them):")
        print_histogram(sc_file_counts, [1,2,3,4,5,6,7,8,9,10,20,999999])

    # ── Cross-project summary table ──────────────────────────────────────────
    print(f"\n\n{'='*70}")
    print("CROSS-PROJECT SUMMARY")
    print('='*70)

    header = f"{'Project':14} {'Task':10} {'View':10} {'Gini':6} {'CoV':6} {'Skew':6} {'Top20%':7} {'ZipfR2':7} {'Verdict'}"
    print(header)
    print("-" * len(header))

    for r in all_results:
        proj = r["project"]
        for task_key, view_key, task_label, view_label in [
            ("sad_sam_sentence_view",   None, "SAD-SAM", "sent"),
            ("sad_sam_component_view",  None, "SAD-SAM", "comp"),
            ("sad_code_sentence_view",  None, "SAD-CODE","sent"),
            ("sad_code_file_view",      None, "SAD-CODE","file"),
        ]:
            if task_key not in r:
                continue
            s = r[task_key]
            if not s:
                continue
            v = long_tail_verdict(s).split("[")[0].strip()
            print(f"{proj:14} {task_label:10} {view_label:10} "
                  f"{s['gini']:6.3f} {s['cv']:6.2f} {s['skewness']:6.2f} "
                  f"{s['top20_share']:7.3f} {s['zipf_r2']:7.3f}  {v}")

    print()


if __name__ == "__main__":
    main()
