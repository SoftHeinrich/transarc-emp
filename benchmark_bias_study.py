#!/usr/bin/env python3
"""
Benchmark Bias & Long-Tail Distribution Study

Systematic analysis of distributional bias in the ARDoCo benchmark across
SAD-SAM, SAM-CODE, and SAD-CODE tasks. Examines long-tail distributions,
position bias, cross-task correlations, project-level imbalance, and
exploitability via popularity baselines.

Produces BENCHMARK_BIAS_STUDY.md.
"""

import csv
import math
import sys
from collections import Counter
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).parent))
from transarc_error_analysis import (
    BENCHMARK, RESULTS, PROJECTS,
    GS_SAD_SAM, GS_SAM_CODE, GS_SAD_CODE, ACM_FILES, TEXT_FILES,
    normalize_path, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw, load_gs_sad_code_raw,
    load_gs_sad_code_enrolled, load_model_element_names, load_text,
    calc_metrics,
)

# ─── Paths (unique to this script) ───────────────────────────────────────────

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/BENCHMARK_BIAS_STUDY.md")

# TransArc expected thresholds for exploitability comparison
TRANSARC_F1 = {
    "mediastore": 0.588, "teastore": 0.829, "teammates": 0.821,
    "bigbluebutton": 0.831, "jabref": 0.943,
}
LLM_F1 = {
    "mediastore": 0.965, "teastore": 0.845, "teammates": 0.646,
    "bigbluebutton": 0.797, "jabref": 0.916,
}

# ─── Data loading helpers (unique to this script) ────────────────────────────

def load_gs_sam_code_with_names(project):
    """Returns list of (ae_id, ae_name, normalized_ce_path) — NOT enrolled."""
    rows = []
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            ae_id = row["ae_id"]
            ae_name = row["ae_name"]
            ce_path = row.get("ce_ids") or row.get("ce_id")
            rows.append((ae_id, ae_name, normalize_path(ce_path)))
    return rows


def count_sentences(project):
    """Returns total number of sentences in documentation."""
    with open(TEXT_FILES[project]) as f:
        return sum(1 for _ in f)


# ─── Statistical helpers ──────────────────────────────────────────────────────

def gini_coefficient(values):
    """Compute Gini coefficient for a list of non-negative values."""
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    total = sum(sorted_v)
    cumulative = 0
    gini_sum = 0
    for i, v in enumerate(sorted_v):
        cumulative += v
        gini_sum += (2 * (i + 1) - n - 1) * v
    return gini_sum / (n * total) if total > 0 else 0.0


def shannon_entropy(values):
    """Compute Shannon entropy (in bits) from a list of counts."""
    total = sum(values)
    if total == 0:
        return 0.0
    entropy = 0.0
    for v in values:
        if v > 0:
            p = v / total
            entropy -= p * math.log2(p)
    return entropy


def top_k_concentration(values, k=3):
    """Fraction of total contributed by the top-k values."""
    if not values:
        return 0.0
    total = sum(values)
    if total == 0:
        return 0.0
    topk = sorted(values, reverse=True)[:k]
    return sum(topk) / total


def distribution_stats(values):
    """Returns dict with min, max, median, mean, gini, entropy, top3_conc."""
    if not values:
        return {"min": 0, "max": 0, "median": 0, "mean": 0.0,
                "gini": 0.0, "entropy": 0.0, "top3_conc": 0.0}
    sv = sorted(values)
    n = len(sv)
    median = sv[n // 2] if n % 2 == 1 else (sv[n // 2 - 1] + sv[n // 2]) / 2
    return {
        "min": sv[0],
        "max": sv[-1],
        "median": median,
        "mean": sum(sv) / n,
        "gini": gini_coefficient(sv),
        "entropy": shannon_entropy(sv),
        "top3_conc": top_k_concentration(sv, 3),
    }


def ascii_histogram(counter, max_width=40, max_bins=20):
    """Generate ASCII histogram lines from a Counter of fan-out values."""
    if not counter:
        return ["  (no data)"]
    sorted_items = sorted(counter.items())
    # If too many bins, group into ranges
    if len(sorted_items) > max_bins:
        # Logarithmic binning
        all_vals = [k for k, _ in sorted_items]
        min_v, max_v = all_vals[0], all_vals[-1]
        if max_v == min_v:
            bins = [(min_v, max_v)]
        else:
            # Create ~max_bins bins
            step = max(1, (max_v - min_v + 1) // max_bins)
            bins = []
            lo = min_v
            while lo <= max_v:
                hi = min(lo + step - 1, max_v)
                bins.append((lo, hi))
                lo = hi + 1
        binned = Counter()
        for val, cnt in sorted_items:
            for lo, hi in bins:
                if lo <= val <= hi:
                    label = f"{lo}" if lo == hi else f"{lo}-{hi}"
                    binned[label] += cnt
                    break
        sorted_items = [(label, binned[label]) for label in
                        [f"{lo}" if lo == hi else f"{lo}-{hi}" for lo, hi in bins]
                        if label in binned]

    max_count = max(c for _, c in sorted_items) if sorted_items else 1
    label_width = max(len(str(k)) for k, _ in sorted_items)
    lines = []
    for key, count in sorted_items:
        bar_len = int(count / max_count * max_width) if max_count > 0 else 0
        bar = "█" * bar_len
        lines.append(f"  {str(key):>{label_width}} │ {bar} ({count})")
    return lines


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 1 – SAD-SAM Long-Tail Distribution
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_1_sad_sam_distribution():
    """SAD-SAM fan-out analysis for model elements and sentences."""
    results = {}
    for proj in PROJECTS:
        links = load_gs_sad_sam(proj)
        total_sentences = count_sentences(proj)
        names = load_model_element_names(proj)

        # Model element fan-out: how many sentences per model element
        model_fanout = Counter()
        for m, s in links:
            model_fanout[m] += 1

        # Sentence fan-out: how many model elements per sentence
        sent_fanout = Counter()
        for m, s in links:
            sent_fanout[s] += 1

        # All model element IDs from SAM-CODE gold standard (includes those with zero links)
        all_model_ids = set(names.keys())
        # Model elements with zero SAD-SAM links (= Undocumented Model Elements)
        ume = all_model_ids - set(model_fanout.keys())

        # Linked vs unlinked sentences
        linked_sents = set(sent_fanout.keys())
        unlinked_sents = total_sentences - len(linked_sents)

        results[proj] = {
            "model_fanout": model_fanout,
            "sent_fanout": sent_fanout,
            "total_sentences": total_sentences,
            "total_model_elements": len(all_model_ids),
            "ume_count": len(ume),
            "ume_ids": ume,
            "linked_sents": len(linked_sents),
            "unlinked_sents": unlinked_sents,
            "total_links": len(links),
            "names": names,
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 2 – SAD-CODE Long-Tail Distribution (pre/post enrollment)
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_2_sad_code_distribution():
    """SAD-CODE fan-out pre- and post-enrollment."""
    results = {}
    for proj in PROJECTS:
        raw = load_gs_sad_code_raw(proj)
        code_model = load_code_model_files(proj)
        enrolled = load_gs_sad_code_enrolled(proj, code_model)

        # Pre-enrollment
        raw_sent_fanout = Counter()
        raw_code_fanout = Counter()
        for s, c in raw:
            raw_sent_fanout[s] += 1
            raw_code_fanout[c] += 1

        # Post-enrollment
        enr_sent_fanout = Counter()
        enr_code_fanout = Counter()
        for s, c in enrolled:
            enr_sent_fanout[s] += 1
            enr_code_fanout[c] += 1

        # Expansion factor per entity (directory entries only)
        raw_dirs = {(s, c) for s, c in raw if c.endswith("/")}
        expansion = {}
        for s, c in raw_dirs:
            expanded = sum(1 for sc, cc in enrolled if sc == s and cc.startswith(c))
            expansion[(s, c)] = expanded

        results[proj] = {
            "raw_links": len(raw),
            "enrolled_links": len(enrolled),
            "expansion_ratio": len(enrolled) / len(raw) if raw else 0,
            "raw_sent_fanout": raw_sent_fanout,
            "raw_code_fanout": raw_code_fanout,
            "enr_sent_fanout": enr_sent_fanout,
            "enr_code_fanout": enr_code_fanout,
            "expansion_factors": expansion,
            "raw_dir_count": len(raw_dirs),
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 3 – SAM-CODE Long-Tail Distribution
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_3_sam_code_distribution():
    """SAM-CODE fan-out per architectural element and per code file."""
    results = {}
    for proj in PROJECTS:
        raw = load_gs_sam_code_raw(proj)
        code_model = load_code_model_files(proj)
        enrolled = enroll_gold_standard(raw, code_model)
        rows = load_gs_sam_code_with_names(proj)

        # Enrolled fan-out per architectural element
        ae_fanout = Counter()
        ae_names = {}
        for ae_id, ce_path in enrolled:
            ae_fanout[ae_id] += 1

        # Get ae names
        for ae_id, ae_name, _ in rows:
            ae_names[ae_id] = ae_name

        # Fan-out per code file (how many AEs per file)
        code_fanout = Counter()
        for ae_id, ce_path in enrolled:
            code_fanout[ce_path] += 1

        # Component vs Interface split
        comp_fanout = Counter()
        iface_fanout = Counter()
        for ae_id, count in ae_fanout.items():
            name = ae_names.get(ae_id, "")
            if name.startswith("Interface:"):
                iface_fanout[ae_id] = count
            else:
                comp_fanout[ae_id] = count

        results[proj] = {
            "ae_fanout": ae_fanout,
            "ae_names": ae_names,
            "code_fanout": code_fanout,
            "comp_fanout": comp_fanout,
            "iface_fanout": iface_fanout,
            "total_links": len(enrolled),
            "raw_links": len(raw),
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 4 – Sentence Position Bias
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_4_position_bias():
    """Are trace-linked sentences concentrated in certain positions?"""
    results = {}
    for proj in PROJECTS:
        total_sents = count_sentences(proj)
        links = load_gs_sad_sam(proj)

        # Sentence positions with links
        linked_positions = set()
        for m, s in links:
            linked_positions.add(int(s))

        # Quartile analysis
        q_size = total_sents / 4
        quartile_linked = [0, 0, 0, 0]
        quartile_total = [0, 0, 0, 0]

        for pos in range(1, total_sents + 1):
            q = min(int((pos - 1) / q_size), 3)
            quartile_total[q] += 1
            if pos in linked_positions:
                quartile_linked[q] += 1

        quartile_density = []
        for i in range(4):
            density = quartile_linked[i] / quartile_total[i] if quartile_total[i] > 0 else 0
            quartile_density.append(density)

        # Overall density
        overall_density = len(linked_positions) / total_sents if total_sents > 0 else 0

        # Simple chi-squared test (expected = uniform distribution)
        expected_per_q = len(linked_positions) / 4 if linked_positions else 0
        chi_sq = 0.0
        if expected_per_q > 0:
            for i in range(4):
                chi_sq += (quartile_linked[i] - expected_per_q) ** 2 / expected_per_q

        # Also do SAD-CODE position analysis
        sad_code_links = load_gs_sad_code_raw(proj)
        sc_linked_positions = set()
        for s, c in sad_code_links:
            sc_linked_positions.add(int(s))

        sc_quartile_linked = [0, 0, 0, 0]
        for pos in range(1, total_sents + 1):
            q = min(int((pos - 1) / q_size), 3)
            if pos in sc_linked_positions:
                sc_quartile_linked[q] += 1

        sc_quartile_density = []
        for i in range(4):
            density = sc_quartile_linked[i] / quartile_total[i] if quartile_total[i] > 0 else 0
            sc_quartile_density.append(density)

        results[proj] = {
            "total_sents": total_sents,
            "linked_sents_ss": len(linked_positions),
            "linked_sents_sc": len(sc_linked_positions),
            "overall_density_ss": overall_density,
            "quartile_density_ss": quartile_density,
            "quartile_linked_ss": quartile_linked,
            "quartile_total": quartile_total,
            "chi_sq_ss": chi_sq,
            "quartile_density_sc": sc_quartile_density,
            "quartile_linked_sc": sc_quartile_linked,
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 5 – Cross-Task Correlation
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_5_cross_task_correlation():
    """Correlation between SAD-SAM fan-out and SAD-CODE fan-out per sentence."""
    results = {}
    for proj in PROJECTS:
        total_sents = count_sentences(proj)

        # SAD-SAM sentence fan-out
        ss_links = load_gs_sad_sam(proj)
        ss_sent_fanout = Counter()
        for m, s in ss_links:
            ss_sent_fanout[s] += 1

        # SAD-CODE sentence fan-out (enrolled)
        code_model = load_code_model_files(proj)
        sc_enrolled = load_gs_sad_code_enrolled(proj, code_model)
        sc_sent_fanout = Counter()
        for s, c in sc_enrolled:
            sc_sent_fanout[s] += 1

        # Build paired vectors for all sentences
        all_sents = set(str(i) for i in range(1, total_sents + 1))
        ss_vals = []
        sc_vals = []
        for s in sorted(all_sents, key=int):
            ss_vals.append(ss_sent_fanout.get(s, 0))
            sc_vals.append(sc_sent_fanout.get(s, 0))

        # Pearson correlation
        pearson = _pearson(ss_vals, sc_vals)

        # Spearman correlation (rank-based)
        spearman = _spearman(ss_vals, sc_vals)

        results[proj] = {
            "n_sentences": total_sents,
            "pearson": pearson,
            "spearman": spearman,
            "ss_linked": sum(1 for v in ss_vals if v > 0),
            "sc_linked": sum(1 for v in sc_vals if v > 0),
            "both_linked": sum(1 for a, b in zip(ss_vals, sc_vals) if a > 0 and b > 0),
            "neither_linked": sum(1 for a, b in zip(ss_vals, sc_vals) if a == 0 and b == 0),
        }
    return results


def _pearson(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def _spearman(x, y):
    """Compute Spearman rank correlation."""
    def _rank(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed) and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j - 1) / 2 + 1  # 1-based average rank
            for k in range(i, j):
                ranks[indexed[k][0]] = avg_rank
            i = j
        return ranks

    rx = _rank(x)
    ry = _rank(y)
    return _pearson(rx, ry)


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 6 – Project-Level Imbalance
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_6_project_imbalance():
    """Cross-project coefficient of variation for key metrics."""
    data = {}
    for proj in PROJECTS:
        total_sents = count_sentences(proj)
        names = load_model_element_names(proj)
        code_model = load_code_model_files(proj)

        ss_links = load_gs_sad_sam(proj)
        sc_raw = load_gs_sad_code_raw(proj)
        sc_enrolled = load_gs_sad_code_enrolled(proj, code_model)
        sam_raw = load_gs_sam_code_raw(proj)
        sam_enrolled = enroll_gold_standard(sam_raw, code_model)

        # Unique entities
        ss_model_els = set(m for m, s in ss_links)
        ss_sents = set(s for m, s in ss_links)
        sc_sents = set(s for s, c in sc_enrolled)
        sc_files = set(c for s, c in sc_enrolled)
        sam_aes = set(a for a, c in sam_enrolled)
        sam_files = set(c for a, c in sam_enrolled)

        data[proj] = {
            "total_sents": total_sents,
            "total_model_elements": len(names),
            "total_code_files": len(code_model),
            "ss_links": len(ss_links),
            "ss_unique_models": len(ss_model_els),
            "ss_unique_sents": len(ss_sents),
            "ss_links_per_sent": len(ss_links) / total_sents if total_sents else 0,
            "ss_links_per_model": len(ss_links) / len(ss_model_els) if ss_model_els else 0,
            "sc_links_enrolled": len(sc_enrolled),
            "sc_unique_sents": len(sc_sents),
            "sc_unique_files": len(sc_files),
            "sc_links_per_sent": len(sc_enrolled) / total_sents if total_sents else 0,
            "sc_links_per_file": len(sc_enrolled) / len(sc_files) if sc_files else 0,
            "sam_links_enrolled": len(sam_enrolled),
            "sam_unique_aes": len(sam_aes),
            "sam_unique_files": len(sam_files),
            "sam_links_per_ae": len(sam_enrolled) / len(sam_aes) if sam_aes else 0,
            "sam_links_per_file": len(sam_enrolled) / len(sam_files) if sam_files else 0,
        }
    return data


def _coeff_of_variation(values):
    """Coefficient of variation: std/mean."""
    if not values:
        return 0.0
    n = len(values)
    mean = sum(values) / n
    if mean == 0:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / n
    return math.sqrt(var) / mean


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 7 – Exploitability Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_7_exploitability():
    """Top-K popularity baselines to assess distributional bias exploitability."""
    results = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        total_sents = count_sentences(proj)

        # --- SAD-SAM: Link every sentence to top-K model elements ---
        ss_links = load_gs_sad_sam(proj)
        model_fanout = Counter()
        for m, s in ss_links:
            model_fanout[m] += 1

        # All sentences, all model elements
        all_sents = set(str(i) for i in range(1, total_sents + 1))
        all_models = set(model_fanout.keys())

        ss_topk_results = {}
        for k in [1, 3, 5]:
            topk_models = [m for m, _ in model_fanout.most_common(k)]
            baseline_links = set()
            for s in all_sents:
                for m in topk_models:
                    baseline_links.add((m, s))
            p, r, f1, _, _, _ = calc_metrics(ss_links, baseline_links)
            ss_topk_results[k] = (p, r, f1)

        # --- SAD-CODE: Link every sentence to top-K code files ---
        sc_enrolled = load_gs_sad_code_enrolled(proj, code_model)
        code_fanout = Counter()
        for s, c in sc_enrolled:
            code_fanout[c] += 1

        sc_topk_results = {}
        for k in [1, 3, 5, 10]:
            topk_codes = [c for c, _ in code_fanout.most_common(k)]
            baseline_links = set()
            for s in all_sents:
                for c in topk_codes:
                    baseline_links.add((s, c))
            p, r, f1, _, _, _ = calc_metrics(sc_enrolled, baseline_links)
            sc_topk_results[k] = (p, r, f1)

        # --- "Link-all-to-most-popular" single element ---
        most_popular_model = model_fanout.most_common(1)[0] if model_fanout else (None, 0)
        most_popular_code = code_fanout.most_common(1)[0] if code_fanout else (None, 0)

        results[proj] = {
            "ss_topk": ss_topk_results,
            "sc_topk": sc_topk_results,
            "most_popular_model": most_popular_model,
            "most_popular_code": most_popular_code,
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis 8 – Summary Statistics Table
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_8_summary_stats():
    """Per project, per task: Gini, entropy, fan-out stats, top-3 concentration."""
    results = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        names = load_model_element_names(proj)

        # SAD-SAM
        ss_links = load_gs_sad_sam(proj)
        ss_model_fanout = Counter()
        ss_sent_fanout = Counter()
        for m, s in ss_links:
            ss_model_fanout[m] += 1
            ss_sent_fanout[s] += 1

        # SAM-CODE (enrolled)
        sam_enrolled = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
        sam_ae_fanout = Counter()
        sam_code_fanout = Counter()
        for a, c in sam_enrolled:
            sam_ae_fanout[a] += 1
            sam_code_fanout[c] += 1

        # SAD-CODE (enrolled)
        sc_enrolled = load_gs_sad_code_enrolled(proj, code_model)
        sc_sent_fanout = Counter()
        sc_code_fanout = Counter()
        for s, c in sc_enrolled:
            sc_sent_fanout[s] += 1
            sc_code_fanout[c] += 1

        results[proj] = {
            "ss": {
                "total_links": len(ss_links),
                "left_name": "model elements",
                "right_name": "sentences",
                "left_unique": len(ss_model_fanout),
                "right_unique": len(ss_sent_fanout),
                "left_stats": distribution_stats(list(ss_model_fanout.values())),
                "right_stats": distribution_stats(list(ss_sent_fanout.values())),
            },
            "sam": {
                "total_links": len(sam_enrolled),
                "left_name": "arch. elements",
                "right_name": "code files",
                "left_unique": len(sam_ae_fanout),
                "right_unique": len(sam_code_fanout),
                "left_stats": distribution_stats(list(sam_ae_fanout.values())),
                "right_stats": distribution_stats(list(sam_code_fanout.values())),
            },
            "sc": {
                "total_links": len(sc_enrolled),
                "left_name": "sentences",
                "right_name": "code files",
                "left_unique": len(sc_sent_fanout),
                "right_unique": len(sc_code_fanout),
                "left_stats": distribution_stats(list(sc_sent_fanout.values())),
                "right_stats": distribution_stats(list(sc_code_fanout.values())),
            },
        }
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Report generation
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    def md_only(s=""):
        md_lines.append(s)

    out("# Benchmark Bias & Long-Tail Distribution Study")
    out()
    out("A systematic analysis of distributional bias in the ARDoCo benchmark")
    out("across SAD-SAM, SAM-CODE, and SAD-CODE tasks for 5 projects:")
    out("MediaStore, TeaStore, Teammates, BigBlueButton, JabRef.")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 1 – SAD-SAM Long-Tail Distribution
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 1. SAD-SAM Long-Tail Distribution")
    out()

    a1 = analysis_1_sad_sam_distribution()

    out("### 1.1 Model Element Fan-Out (sentences per model element)")
    out()
    out("| Project | Model Elements | With Links | UME (no links) | Total Links | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
    out("|---------|---------------|------------|----------------|-------------|-----|--------|-----|------|------|---------|-------------|")
    for proj in PROJECTS:
        d = a1[proj]
        vals = list(d["model_fanout"].values())
        stats = distribution_stats(vals)
        with_links = len(d["model_fanout"])
        out(f"| {proj} | {d['total_model_elements']} | {with_links} | {d['ume_count']} "
            f"| {d['total_links']} | {stats['min']} | {stats['median']:.0f} | {stats['max']} "
            f"| {stats['mean']:.1f} | {stats['gini']:.3f} | {stats['entropy']:.2f} "
            f"| {stats['top3_conc']:.3f} |")

    out()

    # Histograms
    out("#### Model Element Fan-Out Histograms")
    out()
    for proj in PROJECTS:
        d = a1[proj]
        fanout_dist = Counter()
        for m, cnt in d["model_fanout"].items():
            fanout_dist[cnt] += 1
        out(f"**{proj}** ({len(d['model_fanout'])} elements with links):")
        out("```")
        for line in ascii_histogram(fanout_dist):
            out(line)
        out("```")
        out()

    # UME details
    out("#### Undocumented Model Elements (UMEs)")
    out()
    for proj in PROJECTS:
        d = a1[proj]
        if d["ume_count"] > 0:
            ume_names = [d["names"].get(uid, uid) for uid in d["ume_ids"]]
            out(f"- **{proj}**: {d['ume_count']} UMEs: {', '.join(ume_names)}")
        else:
            out(f"- **{proj}**: No UMEs")
    out()

    out("### 1.2 Sentence Fan-Out (model elements per sentence)")
    out()
    out("| Project | Total Sentences | Linked | Unlinked | % Linked | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
    out("|---------|----------------|--------|----------|----------|-----|--------|-----|------|------|---------|-------------|")
    for proj in PROJECTS:
        d = a1[proj]
        vals = list(d["sent_fanout"].values())
        stats = distribution_stats(vals)
        pct_linked = d["linked_sents"] / d["total_sentences"] * 100 if d["total_sentences"] else 0
        out(f"| {proj} | {d['total_sentences']} | {d['linked_sents']} | {d['unlinked_sents']} "
            f"| {pct_linked:.0f}% | {stats['min']} | {stats['median']:.0f} | {stats['max']} "
            f"| {stats['mean']:.1f} | {stats['gini']:.3f} | {stats['entropy']:.2f} "
            f"| {stats['top3_conc']:.3f} |")
    out()

    # Histograms
    out("#### Sentence Fan-Out Histograms")
    out()
    for proj in PROJECTS:
        d = a1[proj]
        fanout_dist = Counter()
        for s, cnt in d["sent_fanout"].items():
            fanout_dist[cnt] += 1
        out(f"**{proj}** ({d['linked_sents']} linked sentences):")
        out("```")
        for line in ascii_histogram(fanout_dist):
            out(line)
        out("```")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 2 – SAD-CODE Long-Tail Distribution
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 2. SAD-CODE Long-Tail Distribution (Pre- and Post-Enrollment)")
    out()

    a2 = analysis_2_sad_code_distribution()

    out("### 2.1 Enrollment Expansion Overview")
    out()
    out("| Project | Raw Links | Enrolled Links | Expansion Ratio | Directory Entries |")
    out("|---------|-----------|----------------|-----------------|-------------------|")
    for proj in PROJECTS:
        d = a2[proj]
        out(f"| {proj} | {d['raw_links']} | {d['enrolled_links']} | {d['expansion_ratio']:.1f}x | {d['raw_dir_count']} |")
    out()

    out("### 2.2 Per-Sentence Fan-Out (pre vs post enrollment)")
    out()
    out("| Project | Pre: Min | Pre: Med | Pre: Max | Pre: Gini | Post: Min | Post: Med | Post: Max | Post: Gini |")
    out("|---------|----------|----------|----------|-----------|-----------|-----------|-----------|------------|")
    for proj in PROJECTS:
        d = a2[proj]
        pre_stats = distribution_stats(list(d["raw_sent_fanout"].values()))
        post_stats = distribution_stats(list(d["enr_sent_fanout"].values()))
        out(f"| {proj} | {pre_stats['min']} | {pre_stats['median']:.0f} | {pre_stats['max']} | {pre_stats['gini']:.3f} "
            f"| {post_stats['min']} | {post_stats['median']:.0f} | {post_stats['max']} | {post_stats['gini']:.3f} |")
    out()

    out("### 2.3 Per-Code-Entity Fan-Out (post enrollment)")
    out()
    out("| Project | Unique Files | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
    out("|---------|-------------|-----|--------|-----|------|------|---------|-------------|")
    for proj in PROJECTS:
        d = a2[proj]
        vals = list(d["enr_code_fanout"].values())
        stats = distribution_stats(vals)
        out(f"| {proj} | {len(d['enr_code_fanout'])} | {stats['min']} | {stats['median']:.0f} "
            f"| {stats['max']} | {stats['mean']:.1f} | {stats['gini']:.3f} | {stats['entropy']:.2f} "
            f"| {stats['top3_conc']:.3f} |")
    out()

    out("### 2.4 Top Expansion Factors")
    out()
    for proj in PROJECTS:
        d = a2[proj]
        if d["expansion_factors"]:
            sorted_exp = sorted(d["expansion_factors"].items(), key=lambda x: x[1], reverse=True)
            out(f"**{proj}** (top-5 directory expansions):")
            out()
            out("| Sentence | Directory | Expanded Files |")
            out("|----------|-----------|----------------|")
            for (s, c), cnt in sorted_exp[:5]:
                out(f"| {s} | `{c}` | {cnt} |")
            out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 3 – SAM-CODE Long-Tail Distribution
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 3. SAM-CODE Long-Tail Distribution")
    out()

    a3 = analysis_3_sam_code_distribution()

    out("### 3.1 Per Architectural Element (code files per element)")
    out()
    out("| Project | AE Count | Raw Links | Enrolled Links | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
    out("|---------|----------|-----------|----------------|-----|--------|-----|------|------|---------|-------------|")
    for proj in PROJECTS:
        d = a3[proj]
        vals = list(d["ae_fanout"].values())
        stats = distribution_stats(vals)
        out(f"| {proj} | {len(d['ae_fanout'])} | {d['raw_links']} | {d['total_links']} "
            f"| {stats['min']} | {stats['median']:.0f} | {stats['max']} "
            f"| {stats['mean']:.1f} | {stats['gini']:.3f} | {stats['entropy']:.2f} "
            f"| {stats['top3_conc']:.3f} |")
    out()

    # Per-AE detail table
    out("#### Detailed Per-Element Fan-Out")
    out()
    for proj in PROJECTS:
        d = a3[proj]
        sorted_aes = sorted(d["ae_fanout"].items(), key=lambda x: x[1], reverse=True)
        out(f"**{proj}**:")
        out()
        out("| Rank | Element | Type | Files |")
        out("|------|---------|------|-------|")
        for i, (ae_id, count) in enumerate(sorted_aes, 1):
            name = d["ae_names"].get(ae_id, ae_id)
            elem_type = "Interface" if name.startswith("Interface:") else "Component"
            out(f"| {i} | {name} | {elem_type} | {count} |")
        out()

    out("### 3.2 Per Code File (architectural elements per file)")
    out()
    out("| Project | Unique Files | Min | Median | Max | Mean | Gini |")
    out("|---------|-------------|-----|--------|-----|------|------|")
    for proj in PROJECTS:
        d = a3[proj]
        vals = list(d["code_fanout"].values())
        stats = distribution_stats(vals)
        out(f"| {proj} | {len(d['code_fanout'])} | {stats['min']} | {stats['median']:.0f} "
            f"| {stats['max']} | {stats['mean']:.1f} | {stats['gini']:.3f} |")
    out()

    out("### 3.3 Component vs Interface Split")
    out()
    out("| Project | Components | Comp. Files (mean) | Interfaces | Iface. Files (mean) | File Ratio (C/I) |")
    out("|---------|-----------|-------------------|------------|--------------------|--------------------|")
    for proj in PROJECTS:
        d = a3[proj]
        comp_vals = list(d["comp_fanout"].values())
        iface_vals = list(d["iface_fanout"].values())
        comp_mean = sum(comp_vals) / len(comp_vals) if comp_vals else 0
        iface_mean = sum(iface_vals) / len(iface_vals) if iface_vals else 0
        ratio = comp_mean / iface_mean if iface_mean > 0 else float('inf')
        ratio_str = f"{ratio:.1f}" if ratio != float('inf') else "N/A (no interfaces)"
        out(f"| {proj} | {len(d['comp_fanout'])} | {comp_mean:.1f} | {len(d['iface_fanout'])} "
            f"| {iface_mean:.1f} | {ratio_str} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 4 – Sentence Position Bias
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 4. Sentence Position Bias")
    out()
    out("Are trace-linked sentences concentrated in certain positions (beginning/end)?")
    out()

    a4 = analysis_4_position_bias()

    out("### 4.1 SAD-SAM Link Density by Position Quartile")
    out()
    out("| Project | Q1 (start) | Q2 | Q3 | Q4 (end) | Overall | Chi-sq (df=3) |")
    out("|---------|-----------|----|----|----------|---------|---------------|")
    for proj in PROJECTS:
        d = a4[proj]
        qd = d["quartile_density_ss"]
        out(f"| {proj} | {qd[0]:.2f} | {qd[1]:.2f} | {qd[2]:.2f} | {qd[3]:.2f} "
            f"| {d['overall_density_ss']:.2f} | {d['chi_sq_ss']:.2f} |")
    out()
    out("*Chi-squared critical value at alpha=0.05, df=3 is 7.81. Values above this suggest significant position bias.*")
    out()

    out("### 4.2 SAD-CODE Link Density by Position Quartile")
    out()
    out("| Project | Q1 (start) | Q2 | Q3 | Q4 (end) | Linked Sentences |")
    out("|---------|-----------|----|----|----------|-----------------|")
    for proj in PROJECTS:
        d = a4[proj]
        qd = d["quartile_density_sc"]
        out(f"| {proj} | {qd[0]:.2f} | {qd[1]:.2f} | {qd[2]:.2f} | {qd[3]:.2f} "
            f"| {d['linked_sents_sc']}/{d['total_sents']} |")
    out()

    out("### 4.3 Position Bias Visualization")
    out()
    for proj in PROJECTS:
        d = a4[proj]
        qd = d["quartile_density_ss"]
        max_d = max(qd) if max(qd) > 0 else 1
        out(f"**{proj}** (SAD-SAM, Chi-sq={d['chi_sq_ss']:.2f}):")
        out("```")
        labels = ["Q1 (start)", "Q2       ", "Q3       ", "Q4 (end) "]
        for i, (label, density) in enumerate(zip(labels, qd)):
            bar_len = int(density / max_d * 30)
            bar = "█" * bar_len
            linked = d["quartile_linked_ss"][i]
            total = d["quartile_total"][i]
            out(f"  {label} │ {bar} {density:.2f} ({linked}/{total})")
        out("```")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 5 – Cross-Task Correlation
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 5. Cross-Task Correlation (SAD-SAM vs SAD-CODE per Sentence)")
    out()
    out("Do sentences with many SAD-SAM links also have many SAD-CODE links?")
    out()

    a5 = analysis_5_cross_task_correlation()

    out("| Project | Sentences | SAD-SAM Linked | SAD-CODE Linked | Both | Neither | Pearson r | Spearman rho |")
    out("|---------|-----------|---------------|----------------|------|---------|-----------|-------------|")
    for proj in PROJECTS:
        d = a5[proj]
        out(f"| {proj} | {d['n_sentences']} | {d['ss_linked']} | {d['sc_linked']} "
            f"| {d['both_linked']} | {d['neither_linked']} "
            f"| {d['pearson']:.3f} | {d['spearman']:.3f} |")
    out()

    out("**Interpretation**:")
    out()
    out("- Pearson r close to 1.0 means sentences with high SAD-SAM fan-out tend to have high SAD-CODE fan-out.")
    out("- This suggests the transitive assumption (SAD→SAM→CODE) captures real structure.")
    out("- Low correlation would suggest the tasks measure different aspects of the documentation.")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 6 – Project-Level Imbalance
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 6. Project-Level Imbalance")
    out()

    a6 = analysis_6_project_imbalance()

    out("### 6.1 Raw Dimensions")
    out()
    out("| Project | Sentences | Model Elements | Code Files | SAD-SAM Links | SAM-CODE Links | SAD-CODE Links |")
    out("|---------|-----------|---------------|------------|---------------|----------------|----------------|")
    for proj in PROJECTS:
        d = a6[proj]
        out(f"| {proj} | {d['total_sents']} | {d['total_model_elements']} | {d['total_code_files']} "
            f"| {d['ss_links']} | {d['sam_links_enrolled']} | {d['sc_links_enrolled']} |")
    out()

    out("### 6.2 Link Densities")
    out()
    out("| Project | SAD-SAM/sent | SAD-SAM/model | SAD-CODE/sent | SAD-CODE/file | SAM-CODE/AE | SAM-CODE/file |")
    out("|---------|-------------|---------------|---------------|---------------|-------------|---------------|")
    for proj in PROJECTS:
        d = a6[proj]
        out(f"| {proj} | {d['ss_links_per_sent']:.2f} | {d['ss_links_per_model']:.1f} "
            f"| {d['sc_links_per_sent']:.2f} | {d['sc_links_per_file']:.2f} "
            f"| {d['sam_links_per_ae']:.1f} | {d['sam_links_per_file']:.2f} |")
    out()

    # Coefficient of variation
    out("### 6.3 Cross-Project Heterogeneity (Coefficient of Variation)")
    out()
    metrics = [
        ("Total Sentences", [a6[p]["total_sents"] for p in PROJECTS]),
        ("Model Elements", [a6[p]["total_model_elements"] for p in PROJECTS]),
        ("Code Files", [a6[p]["total_code_files"] for p in PROJECTS]),
        ("SAD-SAM Links", [a6[p]["ss_links"] for p in PROJECTS]),
        ("SAM-CODE Links", [a6[p]["sam_links_enrolled"] for p in PROJECTS]),
        ("SAD-CODE Links", [a6[p]["sc_links_enrolled"] for p in PROJECTS]),
        ("SAD-SAM Links/Sent", [a6[p]["ss_links_per_sent"] for p in PROJECTS]),
        ("SAD-CODE Links/Sent", [a6[p]["sc_links_per_sent"] for p in PROJECTS]),
        ("SAM-CODE Links/AE", [a6[p]["sam_links_per_ae"] for p in PROJECTS]),
    ]
    out("| Metric | Min | Max | Mean | CV |")
    out("|--------|-----|-----|------|----|")
    for name, vals in metrics:
        cv = _coeff_of_variation(vals)
        out(f"| {name} | {min(vals):.2f} | {max(vals):.2f} | {sum(vals)/len(vals):.2f} | {cv:.3f} |")
    out()
    out("*CV > 0.5 indicates high cross-project heterogeneity; CV > 1.0 indicates extreme variation.*")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 7 – Exploitability Analysis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 7. Exploitability Analysis (Popularity Baselines)")
    out()
    out("How well does a naive 'link-everything-to-top-K-entities' baseline perform?")
    out("If a simple popularity baseline achieves high F1, the benchmark may be too easy to game.")
    out()

    a7 = analysis_7_exploitability()

    out("### 7.1 SAD-SAM Top-K Baseline")
    out()
    out("Strategy: Link every sentence to the K most popular model elements.")
    out()
    out("| Project | Top-1 P | Top-1 R | Top-1 F1 | Top-3 P | Top-3 R | Top-3 F1 | Top-5 P | Top-5 R | Top-5 F1 |")
    out("|---------|---------|---------|----------|---------|---------|----------|---------|---------|----------|")
    for proj in PROJECTS:
        d = a7[proj]
        t1 = d["ss_topk"][1]
        t3 = d["ss_topk"][3]
        t5 = d["ss_topk"][5]
        out(f"| {proj} | {t1[0]:.3f} | {t1[1]:.3f} | {t1[2]:.3f} "
            f"| {t3[0]:.3f} | {t3[1]:.3f} | {t3[2]:.3f} "
            f"| {t5[0]:.3f} | {t5[1]:.3f} | {t5[2]:.3f} |")
    out()

    out("### 7.2 SAD-CODE Top-K Baseline")
    out()
    out("Strategy: Link every sentence to the K most popular code files.")
    out()
    out("| Project | Top-1 F1 | Top-3 F1 | Top-5 F1 | Top-10 F1 | TransArc F1 | LLM F1 |")
    out("|---------|----------|----------|----------|-----------|-------------|--------|")
    for proj in PROJECTS:
        d = a7[proj]
        t1 = d["sc_topk"][1]
        t3 = d["sc_topk"][3]
        t5 = d["sc_topk"][5]
        t10 = d["sc_topk"][10]
        out(f"| {proj} | {t1[2]:.3f} | {t3[2]:.3f} | {t5[2]:.3f} | {t10[2]:.3f} "
            f"| {TRANSARC_F1[proj]:.3f} | {LLM_F1[proj]:.3f} |")
    out()

    out("### 7.3 Most Popular Entities")
    out()
    out("| Project | Most Popular Model Element | Links | Most Popular Code File | Links |")
    out("|---------|--------------------------|-------|----------------------|-------|")
    for proj in PROJECTS:
        d = a7[proj]
        mm, mc = d["most_popular_model"]
        cm, cc = d["most_popular_code"]
        names = load_model_element_names(proj)
        model_name = names.get(mm, mm) if mm else "N/A"
        code_short = cm.split("/")[-1] if cm and "/" in cm else (cm or "N/A")
        out(f"| {proj} | {model_name} | {mc} | `{code_short}` | {cc} |")
    out()

    out("### 7.4 Exploitability Assessment")
    out()
    out("Does the popularity baseline beat the actual system? If Top-K F1 exceeds TransArc F1, the benchmark")
    out("distribution can be trivially exploited without understanding any semantics.")
    out()
    out("| Project | Top-5 SAD-CODE F1 | TransArc F1 | Exploitable? | Top-10 F1 | Beats TransArc? |")
    out("|---------|------------------|-------------|-------------|-----------|-----------------|")
    for proj in PROJECTS:
        d = a7[proj]
        t5_f1 = d["sc_topk"][5][2]
        t10_f1 = d["sc_topk"][10][2]
        ta_f1 = TRANSARC_F1[proj]
        exploit5 = "YES" if t5_f1 > ta_f1 else "No"
        exploit10 = "YES" if t10_f1 > ta_f1 else "No"
        out(f"| {proj} | {t5_f1:.3f} | {ta_f1:.3f} | {exploit5} | {t10_f1:.3f} | {exploit10} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis 8 – Summary Statistics Table
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 8. Comprehensive Summary Statistics")
    out()

    a8 = analysis_8_summary_stats()

    for task_key, task_label in [("ss", "SAD-SAM"), ("sam", "SAM-CODE"), ("sc", "SAD-CODE")]:
        out(f"### 8.{['ss','sam','sc'].index(task_key)+1} {task_label}")
        out()

        # Left side (model elements / AEs / sentences)
        first = a8[PROJECTS[0]][task_key]
        left_name = first["left_name"].title()
        right_name = first["right_name"].title()

        out(f"#### {left_name} Side")
        out()
        out(f"| Project | Total Links | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
        out(f"|---------|-------------|--------|-----|--------|-----|------|------|---------|-------------|")
        for proj in PROJECTS:
            d = a8[proj][task_key]
            s = d["left_stats"]
            out(f"| {proj} | {d['total_links']} | {d['left_unique']} "
                f"| {s['min']} | {s['median']:.0f} | {s['max']} "
                f"| {s['mean']:.1f} | {s['gini']:.3f} | {s['entropy']:.2f} "
                f"| {s['top3_conc']:.3f} |")
        out()

        out(f"#### {right_name} Side")
        out()
        out(f"| Project | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |")
        out(f"|---------|--------|-----|--------|-----|------|------|---------|-------------|")
        for proj in PROJECTS:
            d = a8[proj][task_key]
            s = d["right_stats"]
            out(f"| {proj} | {d['right_unique']} "
                f"| {s['min']} | {s['median']:.0f} | {s['max']} "
                f"| {s['mean']:.1f} | {s['gini']:.3f} | {s['entropy']:.2f} "
                f"| {s['top3_conc']:.3f} |")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Synthesis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## 9. Synthesis & Key Findings")
    out()

    out("### 9.1 Long-Tail Severity")
    out()
    out("The benchmark exhibits long-tail distributions across all tasks and projects:")
    out()

    # Aggregate Gini stats
    all_gini_ss_model = [a8[p]["ss"]["left_stats"]["gini"] for p in PROJECTS]
    all_gini_ss_sent = [a8[p]["ss"]["right_stats"]["gini"] for p in PROJECTS]
    all_gini_sam_ae = [a8[p]["sam"]["left_stats"]["gini"] for p in PROJECTS]
    all_gini_sam_code = [a8[p]["sam"]["right_stats"]["gini"] for p in PROJECTS]
    all_gini_sc_sent = [a8[p]["sc"]["left_stats"]["gini"] for p in PROJECTS]
    all_gini_sc_code = [a8[p]["sc"]["right_stats"]["gini"] for p in PROJECTS]

    out("| Distribution | Avg Gini | Min Gini | Max Gini | Interpretation |")
    out("|-------------|----------|----------|----------|----------------|")
    for label, ginis in [
        ("SAD-SAM: Model Element fan-out", all_gini_ss_model),
        ("SAD-SAM: Sentence fan-out", all_gini_ss_sent),
        ("SAM-CODE: Arch Element fan-out", all_gini_sam_ae),
        ("SAM-CODE: Code File fan-out", all_gini_sam_code),
        ("SAD-CODE: Sentence fan-out", all_gini_sc_sent),
        ("SAD-CODE: Code File fan-out", all_gini_sc_code),
    ]:
        avg_g = sum(ginis) / len(ginis)
        interpretation = "Highly unequal" if avg_g > 0.4 else ("Moderate" if avg_g > 0.2 else "Relatively uniform")
        out(f"| {label} | {avg_g:.3f} | {min(ginis):.3f} | {max(ginis):.3f} | {interpretation} |")
    out()

    out("### 9.2 Position Bias Summary")
    out()
    sig_count = sum(1 for p in PROJECTS if a4[p]["chi_sq_ss"] > 7.81)
    out(f"- {sig_count}/{len(PROJECTS)} projects show statistically significant position bias (Chi-sq > 7.81, df=3)")
    for proj in PROJECTS:
        d = a4[proj]
        if d["chi_sq_ss"] > 7.81:
            qd = d["quartile_density_ss"]
            peak = ["Q1 (start)", "Q2", "Q3", "Q4 (end)"][qd.index(max(qd))]
            out(f"  - **{proj}**: Chi-sq={d['chi_sq_ss']:.2f}, peak at {peak} ({max(qd):.2f})")
    out()

    out("### 9.3 Cross-Task Coherence")
    out()
    avg_pearson = sum(a5[p]["pearson"] for p in PROJECTS) / len(PROJECTS)
    avg_spearman = sum(a5[p]["spearman"] for p in PROJECTS) / len(PROJECTS)
    out(f"- Average Pearson correlation (SAD-SAM vs SAD-CODE per sentence): **{avg_pearson:.3f}**")
    out(f"- Average Spearman correlation: **{avg_spearman:.3f}**")
    if avg_pearson > 0.5:
        out("- The high correlation confirms that SAD-SAM and SAD-CODE capture the same underlying signal.")
    elif avg_pearson > 0.3:
        out("- Moderate correlation: tasks are related but capture partially different structure.")
    else:
        out("- Low correlation: the tasks measure substantially different aspects of the documentation.")
    out()

    out("### 9.4 Enrollment Amplification")
    out()
    for proj in PROJECTS:
        d = a2[proj]
        if d["expansion_ratio"] > 1.5:
            out(f"- **{proj}**: {d['expansion_ratio']:.1f}x enrollment expansion "
                f"({d['raw_links']}→{d['enrolled_links']} links, {d['raw_dir_count']} directory entries)")
    out()
    max_exp_proj = max(PROJECTS, key=lambda p: a2[p]["expansion_ratio"])
    out(f"Highest expansion: **{max_exp_proj}** at {a2[max_exp_proj]['expansion_ratio']:.1f}x")
    out()

    out("### 9.5 Project-Level Heterogeneity")
    out()
    # Highlight extreme CV metrics
    for name, vals in metrics:
        cv = _coeff_of_variation(vals)
        if cv > 0.5:
            out(f"- **{name}**: CV={cv:.3f} (high heterogeneity)")
    out()

    out("### 9.6 Exploitability Verdict")
    out()
    for proj in PROJECTS:
        d = a7[proj]
        t5_f1 = d["sc_topk"][5][2]
        t10_f1 = d["sc_topk"][10][2]
        ta_f1 = TRANSARC_F1[proj]
        if t10_f1 > ta_f1:
            out(f"- **{proj}**: Top-10 popularity baseline ({t10_f1:.3f}) BEATS TransArc ({ta_f1:.3f}) — **benchmark exploitable**")
        elif t5_f1 > ta_f1 * 0.8:
            out(f"- **{proj}**: Top-5 baseline ({t5_f1:.3f}) achieves {t5_f1/ta_f1*100:.0f}% of TransArc — moderate exploitability")
        else:
            out(f"- **{proj}**: Top-5 baseline ({t5_f1:.3f}) far below TransArc ({ta_f1:.3f}) — low exploitability")
    out()

    out("### 9.7 Implications for Research")
    out()
    out("1. **Evaluation fairness**: The high Gini coefficients mean a system that correctly handles")
    out("   the top-3 most popular entities can achieve disproportionately high scores.")
    out("2. **Enrollment bias**: Directory expansion can inflate link counts by 2-10x,")
    out("   making file-level metrics favor projects with broad directory entries.")
    out("3. **Position bias**: If present, a simple heuristic (link early sentences to everything)")
    out("   could inflate scores without semantic understanding.")
    out("4. **Cross-project comparison**: The high coefficient of variation in link densities")
    out("   means averaging across projects may be misleading — per-project analysis is essential.")
    out("5. **Popularity baselines should be reported**: Any new TLR approach should compare against")
    out("   a Top-K popularity baseline to demonstrate it captures semantics beyond distributional bias.")
    out()

    # ─── Write markdown ───────────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
        f.write("\n")

    print(f"\n\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
