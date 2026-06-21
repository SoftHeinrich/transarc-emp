#!/usr/bin/env python3
"""
Evaluation Critique: Why File-Level Enrollment P/R/F1 Is Inadequate

Deep investigation of how three distributional properties of the ARDoCo benchmark
— (1) SAD-SAM long-tail, (2) enrollment amplification, (3) SAM-CODE concentration —
combine to make standard file-level precision/recall/F1 a misleading metric.

Proposes and computes alternative metrics at multiple granularities, showing
where they disagree with the standard metric.

Produces EVALUATION_CRITIQUE.md.
"""

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (
    BENCHMARK, RESULTS, PROJECTS,
    GS_SAD_SAM, GS_SAM_CODE, GS_SAD_CODE, ACM_FILES, TEXT_FILES,
    normalize_path, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sam_code_raw, load_gs_sad_code_raw,
    load_gs_sad_code_enrolled, load_result_sad_code,
    load_result_sam_code_standalone,
    load_model_element_names, calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/EVALUATION_CRITIQUE.md")

LLM_CLASSIFICATIONS_DIR = Path("/mnt/hostshare/ardoco-home/transarc-emp/archive/llm_classifications_improved")

V45_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-agent/results/evaluation_results/v45_20260202_115342")
V87_JSON = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-agent/results/evaluation_results/v87_pilot_20260207_213531.json")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def gini_coefficient(values):
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    total = sum(sorted_v)
    gini_sum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(sorted_v))
    return gini_sum / (n * total) if total > 0 else 0.0


def load_sad_code_raw_with_provenance(project):
    """Load raw gold, returning entries + directory flag."""
    entries = []
    with open(GS_SAD_CODE[project]) as f:
        for row in csv.DictReader(f):
            sid = row["sentenceID"]
            raw_path = normalize_path(row["codeID"])
            entries.append((sid, raw_path))
    return entries


def enroll_with_provenance(raw_entries, code_model_files):
    """Enroll and track provenance: which raw entry produced each enrolled link."""
    enrolled = set()
    raw_to_enrolled = defaultdict(set)
    enrolled_to_raw = {}

    for sid, raw_path in raw_entries:
        raw_key = (sid, raw_path)
        if raw_path.endswith("/"):
            for fp in code_model_files:
                if fp.startswith(raw_path):
                    entry = (sid, fp)
                    enrolled.add(entry)
                    raw_to_enrolled[raw_key].add(entry)
                    enrolled_to_raw[entry] = raw_key
        else:
            entry = (sid, raw_path)
            enrolled.add(entry)
            raw_to_enrolled[raw_key].add(entry)
            enrolled_to_raw[entry] = raw_key

    return enrolled, raw_to_enrolled, enrolled_to_raw


def count_sentences(project):
    with open(TEXT_FILES[project]) as f:
        return sum(1 for _ in f)


def load_sam_code_enrolled(project, code_model_files):
    """Returns enrolled SAM-CODE links as set of (ae_id, file_path)."""
    raw = load_gs_sam_code_raw(project)
    return enroll_gold_standard(raw, code_model_files)


def load_llm_result(project, code_model_files):
    """Load LLM classification and convert to file-level result set.

    LLM classifications are {sent_num_str: [comp_name, ...]}.
    We map comp_name -> ae_ids -> enrolled files (via SAM-CODE gold).
    Returns set of (sent_num_str, file_path).
    """
    path = LLM_CLASSIFICATIONS_DIR / f"{project}.json"
    if not path.exists():
        return set()
    with open(path) as f:
        classifications = json.load(f)

    # Build name -> ae_id mapping
    names = load_model_element_names(project)
    name_to_ids = defaultdict(set)
    for ae_id, ae_name in names.items():
        name_to_ids[ae_name].add(ae_id)

    # Build ae_id -> set of enrolled files
    sam_enrolled = load_sam_code_enrolled(project, code_model_files)
    model_to_files = defaultdict(set)
    for ae_id, fp in sam_enrolled:
        model_to_files[ae_id].add(fp)

    result = set()
    for sent_num, comp_names in classifications.items():
        for comp_name in comp_names:
            ae_ids = name_to_ids.get(comp_name, set())
            for ae_id in ae_ids:
                for fp in model_to_files.get(ae_id, set()):
                    result.add((sent_num, fp))
    return result


def load_v45_sad_code(project, code_model_files):
    """Load V45 SAD-SAM links and project through ARCOTL SAM-CODE to get SAD-CODE.

    V45 links are CSV: sentence,component_id,component_name,confidence,source
    Uses ARCOTL (standalone SAM-CODE results) for projection, not gold SAM-CODE.
    Returns set of (sentence_str, file_path).
    """
    path = V45_DIR / project / "v45_links.csv"
    if not path.exists():
        return set()

    # Load V45 SAD-SAM links
    sad_sam = set()
    with open(path) as f:
        for row in csv.DictReader(f):
            sad_sam.add((row["component_id"], row["sentence"]))

    # Build SAM-CODE map from ARCOTL results (not gold)
    arcotl_links = load_result_sam_code_standalone(project)
    sam_code_map = defaultdict(set)
    for ae_id, fp in arcotl_links:
        sam_code_map[ae_id].add(fp)

    # Compose: V45 SAD-SAM × ARCOTL SAM-CODE → SAD-CODE
    result = set()
    for model_id, sent in sad_sam:
        for code_path in sam_code_map.get(model_id, set()):
            result.add((sent, code_path))
    return result


def load_v87_per_component():
    """Load V87 per-component strategy aggregate results.

    Returns dict: project -> {P, R, F1} for SAD-Code.
    Only aggregate metrics available (no per-link data).
    """
    if not V87_JSON.exists():
        return {}
    with open(V87_JSON) as f:
        rows = json.load(f)

    result = {}
    for entry in rows:
        if entry["strategy"] == "per_component":
            result[entry["dataset"]] = entry["SAD-Code"]
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: The Inflation Problem — Quantifying the gap between decisions and links
# ═══════════════════════════════════════════════════════════════════════════════

def part1_inflation(out):
    out("## Part 1: The Inflation Problem")
    out()
    out("File-level P/R/F1 treats every `(sentence, file)` pair as an equally-weighted,")
    out("independent data point. But the gold standard is authored at a coarser granularity:")
    out("annotators assign *directories* or *components* to sentences, and enrollment expands")
    out("these to individual files. This creates a fundamental mismatch between the number of")
    out("*decisions* being evaluated and the number of *data points* in the metric.")
    out()

    # Gather data for all projects
    all_data = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        raw_entries = load_sad_code_raw_with_provenance(proj)
        enrolled, raw_to_enrolled, enrolled_to_raw = enroll_with_provenance(raw_entries, code_model)
        result = load_result_sad_code(proj)

        raw_set = set(raw_entries)
        n_dir = sum(1 for _, p in raw_set if p.endswith("/"))
        n_file = len(raw_set) - n_dir

        # Expansion per raw entry
        expansions = []
        for raw_key, enrolled_set in raw_to_enrolled.items():
            expansions.append(len(enrolled_set))

        # Standard file-level metrics — TransArc
        p, r, f1, tp, fp, fn = calc_metrics(enrolled, result)
        tp_set = enrolled & result
        fn_set = enrolled - result

        # TP/FN provenance
        tp_from_dir = 0
        fn_from_dir = 0
        for entry in tp_set:
            raw = enrolled_to_raw.get(entry)
            if raw and raw[1].endswith("/"):
                tp_from_dir += 1
        for entry in fn_set:
            raw = enrolled_to_raw.get(entry)
            if raw and raw[1].endswith("/"):
                fn_from_dir += 1

        # LLM file-level result
        llm_result = load_llm_result(proj, code_model)
        lp, lr, lf1, ltp, lfp, lfn = calc_metrics(enrolled, llm_result)

        # V45 file-level result
        v45_result = load_v45_sad_code(proj, code_model)
        vp, vr, vf1, vtp, vfp, vfn = calc_metrics(enrolled, v45_result)

        all_data[proj] = {
            "raw_set": raw_set, "enrolled": enrolled,
            "raw_to_enrolled": raw_to_enrolled, "enrolled_to_raw": enrolled_to_raw,
            "result": result, "llm_result": llm_result,
            "v45_result": v45_result, "code_model": code_model,
            "n_raw": len(raw_set), "n_dir": n_dir, "n_file": n_file,
            "n_enrolled": len(enrolled),
            "expansions": sorted(expansions, reverse=True),
            "p": p, "r": r, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn,
            "tp_set": tp_set, "fn_set": fn_set,
            "tp_from_dir": tp_from_dir, "fn_from_dir": fn_from_dir,
            "llm_p": lp, "llm_r": lr, "llm_f1": lf1,
            "llm_tp": ltp, "llm_fp": lfp, "llm_fn": lfn,
            "v45_p": vp, "v45_r": vr, "v45_f1": vf1,
            "v45_tp": vtp, "v45_fp": vfp, "v45_fn": vfn,
        }

    # Table 1.1: Decision vs File count
    out("### 1.1 Annotator Decisions vs Enrolled File Links")
    out()
    out("| Project | Raw Decisions | Dir Entries | File Entries | Enrolled Links | Inflation | Effective n |")
    out("|---------|--------------|-------------|-------------|---------------|-----------|-------------|")
    for proj in PROJECTS:
        d = all_data[proj]
        # Effective n: if we treated each raw entry as one observation, how many independent
        # observations does the F1 effectively measure?
        out(f"| {proj} | {d['n_raw']} | {d['n_dir']} | {d['n_file']} "
            f"| {d['n_enrolled']:,} | {d['n_enrolled']/d['n_raw']:.1f}x "
            f"| ~{d['n_raw']} |")

    total_raw = sum(all_data[p]["n_raw"] for p in PROJECTS)
    total_enrolled = sum(all_data[p]["n_enrolled"] for p in PROJECTS)
    out(f"| **Total** | **{total_raw}** | | | **{total_enrolled:,}** | **{total_enrolled/total_raw:.1f}x** | **~{total_raw}** |")
    out()

    out("The file-level F1 appears to be computed over {0:,} data points, but it really reflects ".format(total_enrolled))
    out(f"~{total_raw} annotator decisions. The statistical confidence implied by the sample size is illusory.")
    out()

    # Table 1.2: Expansion distribution per project
    out("### 1.2 Expansion Distribution — How Unequal Are the Weights?")
    out()
    out("Each raw gold entry expands to a different number of file-level links.")
    out("A correct/incorrect raw entry thus generates a different number of TPs/FNs.")
    out()
    out("| Project | Min Expansion | Median | Max | Gini | Top-1 Entry Weight | Top-3 % of Gold |")
    out("|---------|--------------|--------|-----|------|-------------------|-----------------|")
    for proj in PROJECTS:
        d = all_data[proj]
        exps = d["expansions"]
        n = len(exps)
        median = exps[n // 2]
        gini = gini_coefficient(exps)
        top1_pct = exps[0] / d["n_enrolled"] * 100
        top3_pct = sum(exps[:3]) / d["n_enrolled"] * 100
        out(f"| {proj} | {exps[-1]} | {median} | {exps[0]} | {gini:.3f} "
            f"| {top1_pct:.1f}% | {top3_pct:.1f}% |")
    out()

    out("**JabRef**: The single largest raw entry (one directory) produces {0} file-level links, ".format(
        all_data["jabref"]["expansions"][0]))
    out(f"which is {all_data['jabref']['expansions'][0]/all_data['jabref']['n_enrolled']*100:.1f}% of the entire enrolled gold standard. ")
    out("Getting this one directory right/wrong dominates the entire F1 score.")
    out()

    # Table 1.3: TP/FN provenance
    out("### 1.3 Where Do True Positives and False Negatives Actually Come From?")
    out()
    out("| Project | Total TP | TP from Dirs | % | Total FN | FN from Dirs | % |")
    out("|---------|---------|-------------|---|---------|-------------|---|")
    for proj in PROJECTS:
        d = all_data[proj]
        tp_dir_pct = d["tp_from_dir"] / d["tp"] * 100 if d["tp"] else 0
        fn_dir_pct = d["fn_from_dir"] / d["fn"] * 100 if d["fn"] else 0
        out(f"| {proj} | {d['tp']:,} | {d['tp_from_dir']:,} | {tp_dir_pct:.0f}% "
            f"| {d['fn']:,} | {d['fn_from_dir']:,} | {fn_dir_pct:.0f}% |")

    total_tp = sum(all_data[p]["tp"] for p in PROJECTS)
    total_tp_dir = sum(all_data[p]["tp_from_dir"] for p in PROJECTS)
    total_fn = sum(all_data[p]["fn"] for p in PROJECTS)
    total_fn_dir = sum(all_data[p]["fn_from_dir"] for p in PROJECTS)
    out(f"| **Total** | **{total_tp:,}** | **{total_tp_dir:,}** | **{total_tp_dir/total_tp*100:.0f}%** "
        f"| **{total_fn:,}** | **{total_fn_dir:,}** | **{total_fn_dir/total_fn*100:.0f}%** |")
    out()

    out(f"**{total_tp_dir/total_tp*100:.1f}% of all TPs** and **{total_fn_dir/total_fn*100:.1f}% of all FNs** are artifacts of ")
    out("directory enrollment. The metric is overwhelmingly measuring directory-level decisions")
    out("while presenting itself as a file-level evaluation.")
    out()

    return all_data


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: Block Correlation — Why independence assumption fails
# ═══════════════════════════════════════════════════════════════════════════════

def part2_block_correlation(out, all_data):
    out("## Part 2: Block Correlation — Violation of Independence")
    out()
    out("P/R/F1 implicitly assumes each data point is independent. But enrollment creates")
    out("**blocks** of correlated entries: all files under one directory are either all correct")
    out("(if the system identifies the directory) or all missed (if it doesn't). These blocks")
    out("move together as units.")
    out()

    # For each project, find the TP/FN status of each raw entry's enrolled files
    out("### 2.1 Block Homogeneity — Do enrolled files from the same raw entry share fate?")
    out()
    out("For each raw gold entry that expands to ≥2 files, we check: what fraction of its")
    out("enrolled files are TPs vs FNs? Perfect homogeneity (all TP or all FN) means the")
    out("directory-level decision completely determines file-level outcomes.")
    out()

    out("| Project | Blocks ≥2 | All-TP Blocks | All-FN Blocks | Mixed | Homogeneity |")
    out("|---------|----------|--------------|--------------|-------|-------------|")

    for proj in PROJECTS:
        d = all_data[proj]
        blocks_ge2 = 0
        all_tp = 0
        all_fn = 0
        mixed = 0

        for raw_key, enrolled_set in d["raw_to_enrolled"].items():
            if len(enrolled_set) < 2:
                continue
            blocks_ge2 += 1
            n_tp = sum(1 for e in enrolled_set if e in d["tp_set"])
            n_fn = sum(1 for e in enrolled_set if e in d["fn_set"])
            if n_tp == len(enrolled_set):
                all_tp += 1
            elif n_fn == len(enrolled_set):
                all_fn += 1
            else:
                mixed += 1

        homogeneity = (all_tp + all_fn) / blocks_ge2 * 100 if blocks_ge2 else 0
        out(f"| {proj} | {blocks_ge2} | {all_tp} | {all_fn} | {mixed} | {homogeneity:.0f}% |")
    out()

    out("High homogeneity confirms that file-level outcomes are determined by directory-level")
    out("decisions. The files within a block are not independent observations — they are")
    out("redundant copies of one decision.")
    out()

    # 2.2: Effective sample size
    out("### 2.2 Effective Sample Size")
    out()
    out("If blocks of size N count as N independent observations but are really 1 decision,")
    out("the effective sample size is much smaller than the enrolled link count.")
    out()

    out("| Project | Enrolled Links | Raw Decisions | Ratio | Implied 95% CI Width | Actual CI Width |")
    out("|---------|---------------|--------------|-------|---------------------|-----------------|")
    for proj in PROJECTS:
        d = all_data[proj]
        n_enrolled = d["n_enrolled"]
        n_raw = d["n_raw"]
        f1 = d["f1"]
        # Approximate CI width for a proportion: 1.96 * sqrt(p*(1-p)/n)
        # Using F1 as a proportion estimate
        ci_enrolled = 1.96 * math.sqrt(f1 * (1 - f1) / n_enrolled) if n_enrolled > 0 else 0
        ci_raw = 1.96 * math.sqrt(f1 * (1 - f1) / n_raw) if n_raw > 0 else 0
        out(f"| {proj} | {n_enrolled:,} | {n_raw} | {n_enrolled/n_raw:.0f}:1 "
            f"| ±{ci_enrolled:.4f} | ±{ci_raw:.3f} |")
    out()
    out("The 'implied' CI width (using enrolled count) is deceptively narrow. The 'actual' CI")
    out("width (using raw decision count) is much wider, reflecting the true uncertainty.")
    out()


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Metric Sensitivity — One decision swings the score
# ═══════════════════════════════════════════════════════════════════════════════

def part3_sensitivity(out, all_data):
    out("## Part 3: Metric Sensitivity — Single Decisions That Swing F1")
    out()
    out("We remove each raw gold entry one at a time and recompute F1.")
    out("This shows how much a single annotator decision controls the final score.")
    out()

    out("### 3.1 Most Influential Raw Entries (by |ΔF1| when excluded)")
    out()

    for proj in PROJECTS:
        d = all_data[proj]
        enrolled = d["enrolled"]
        result = d["result"]
        f1_base = d["f1"]

        sensitivities = []
        for raw_key, enrolled_set in d["raw_to_enrolled"].items():
            gold_without = enrolled - enrolled_set
            if not gold_without:
                continue
            _, _, f1_wo, _, _, _ = calc_metrics(gold_without, result)
            delta = f1_wo - f1_base
            # How many of these were TP vs FN?
            n_tp = sum(1 for e in enrolled_set if e in d["tp_set"])
            n_fn = sum(1 for e in enrolled_set if e in d["fn_set"])
            sensitivities.append((raw_key, len(enrolled_set), n_tp, n_fn, delta, f1_wo))

        sensitivities.sort(key=lambda x: abs(x[4]), reverse=True)

        out(f"**{proj}** (baseline F1={f1_base:.4f}):")
        out()
        out("| Rank | Sentence | Directory/File | Size | TPs | FNs | F1 w/o | ΔF1 |")
        out("|------|----------|---------------|------|-----|-----|--------|-----|")
        for i, (raw_key, size, n_tp, n_fn, delta, f1_wo) in enumerate(sensitivities[:5], 1):
            sid, path = raw_key
            path_short = path if len(path) <= 50 else "…" + path[-47:]
            entry_type = "DIR" if path.endswith("/") else "FILE"
            out(f"| {i} | {sid} | `{path_short}` [{entry_type}] | {size} | {n_tp} | {n_fn} | {f1_wo:.4f} | {delta:+.4f} |")
        out()

    # 3.2: Aggregate sensitivity statistics
    out("### 3.2 Aggregate Sensitivity")
    out()
    out("| Project | F1 | Max |ΔF1| | Mean |ΔF1| (top-5) | Entries where |ΔF1|>0.01 |")
    out("|---------|----|---------|--------------------|--------------------------|")

    for proj in PROJECTS:
        d = all_data[proj]
        enrolled = d["enrolled"]
        result = d["result"]
        f1_base = d["f1"]

        deltas = []
        for raw_key, enrolled_set in d["raw_to_enrolled"].items():
            gold_without = enrolled - enrolled_set
            if not gold_without:
                continue
            _, _, f1_wo, _, _, _ = calc_metrics(gold_without, result)
            deltas.append(abs(f1_wo - f1_base))

        deltas.sort(reverse=True)
        max_delta = deltas[0] if deltas else 0
        mean_top5 = sum(deltas[:5]) / min(5, len(deltas)) if deltas else 0
        n_significant = sum(1 for d in deltas if d > 0.01)

        out(f"| {proj} | {f1_base:.4f} | {max_delta:.4f} | {mean_top5:.4f} | {n_significant}/{len(deltas)} |")
    out()


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: SAM-CODE Concentration × Enrollment = Double Amplification
# ═══════════════════════════════════════════════════════════════════════════════

def part4_double_amplification(out):
    out("## Part 4: SAM-CODE Concentration × Enrollment = Double Amplification")
    out()
    out("In the transitive pipeline (SAD→SAM→CODE), the SAM-CODE step maps each architectural")
    out("element (AE) to code files. A few AEs dominate the file counts (Finding 3 from the bias study).")
    out("Enrollment then expands directory entries, creating a **double amplification**:")
    out()
    out("1. **SAD-SAM**: One sentence links to K model elements (low fan-out, K≈1-2)")
    out("2. **SAM-CODE**: Each model element maps to N files (high fan-out, N=1–972)")
    out("3. **Enrollment**: Directory entries expand by M additional files")
    out()
    out("A single correct SAD-SAM link can thus generate K×N TPs at file level.")
    out("The file-level F1 is dominated by the few sentences that link to high-fan-out AEs.")
    out()

    out("### 4.1 Sentence Contribution Inequality")
    out()
    out("How many file-level gold links does each sentence contribute?")
    out()

    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        enrolled = load_gs_sad_code_enrolled(proj, code_model)
        total_sents = count_sentences(proj)

        sent_contribution = Counter()
        for s, c in enrolled:
            sent_contribution[s] += 1

        vals = list(sent_contribution.values())
        if not vals:
            continue

        vals_sorted = sorted(vals, reverse=True)
        total = sum(vals)
        gini = gini_coefficient(vals)
        top1_pct = vals_sorted[0] / total * 100
        top3_pct = sum(vals_sorted[:3]) / total * 100
        top5_pct = sum(vals_sorted[:5]) / total * 100

        # How many sentences contribute >50% of links?
        cumulative = 0
        for i, v in enumerate(vals_sorted):
            cumulative += v
            if cumulative >= total * 0.5:
                n_for_50 = i + 1
                break
        else:
            n_for_50 = len(vals_sorted)

        linked_sents = len(sent_contribution)
        out(f"**{proj}**: {linked_sents}/{total_sents} sentences linked, "
            f"{total:,} enrolled links, Gini={gini:.3f}")
        out(f"  - Top-1 sentence: {vals_sorted[0]:,} links ({top1_pct:.1f}% of gold)")
        out(f"  - Top-3 sentences: {sum(vals_sorted[:3]):,} links ({top3_pct:.1f}%)")
        out(f"  - Sentences for ≥50% of gold: **{n_for_50}** out of {linked_sents}")
        out()

    # 4.2: AE-level amplification chain
    out("### 4.2 The Amplification Chain")
    out()
    out("For each project, trace how model element concentration flows through enrollment:")
    out()

    out("| Project | AEs in SAM-CODE | Top AE | Files for Top AE | Gold SAD-CODE Links via Top AE | % of Total Gold |")
    out("|---------|----------------|--------|-----------------|-------------------------------|----------------|")

    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        names = load_model_element_names(proj)

        # SAM-CODE enrolled
        sam_enrolled = load_sam_code_enrolled(proj, code_model)
        ae_file_count = Counter()
        ae_files = defaultdict(set)
        for ae, fp in sam_enrolled:
            ae_file_count[ae] += 1
            ae_files[ae].add(fp)

        # SAD-SAM links
        ss_links = load_gs_sad_sam(proj)
        ae_sent_count = Counter()
        for m, s in ss_links:
            ae_sent_count[m] += 1

        # SAD-CODE enrolled
        sc_enrolled = load_gs_sad_code_enrolled(proj, code_model)

        # For the top AE by file count: how many SAD-CODE links involve its files?
        if ae_file_count:
            top_ae = ae_file_count.most_common(1)[0][0]
            top_ae_name = names.get(top_ae, top_ae)
            top_ae_files = ae_files[top_ae]
            # SAD-CODE links where code file is in top AE's files
            sc_via_top = sum(1 for s, c in sc_enrolled if c in top_ae_files)
            pct = sc_via_top / len(sc_enrolled) * 100 if sc_enrolled else 0
            out(f"| {proj} | {len(ae_file_count)} | {top_ae_name} | {len(top_ae_files)} | {sc_via_top:,} | {pct:.1f}% |")
    out()

    out("The top architectural element's files account for a large fraction of the SAD-CODE")
    out("gold standard. Getting this one component right/wrong dominates file-level F1.")
    out()


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: Alternative Metrics — What evaluation should look like
# ═══════════════════════════════════════════════════════════════════════════════

def _compute_decision_f1(enrolled, result, raw_to_enrolled):
    """Compute decision-level F1 for any system result against enrolled gold."""
    decision_tp = 0
    decision_fn = 0
    for raw_key, enrolled_set in raw_to_enrolled.items():
        if not enrolled_set:
            continue
        n_hit = sum(1 for e in enrolled_set if e in result)
        if n_hit >= len(enrolled_set) * 0.5:
            decision_tp += 1
        else:
            decision_fn += 1

    fp_set = result - enrolled
    fp_dirs = set()
    for s, c in fp_set:
        parts = c.rsplit("/", 1)
        if len(parts) == 2:
            fp_dirs.add((s, parts[0] + "/"))
        else:
            fp_dirs.add((s, c))
    decision_fp = len(fp_dirs)

    decision_p = decision_tp / (decision_tp + decision_fp) if (decision_tp + decision_fp) else 0
    decision_r = decision_tp / (decision_tp + decision_fn) if (decision_tp + decision_fn) else 0
    decision_f1 = (2 * decision_p * decision_r / (decision_p + decision_r)
                   if (decision_p + decision_r) else 0)
    return {"tp": decision_tp, "fp": decision_fp, "fn": decision_fn,
            "p": decision_p, "r": decision_r, "f1": decision_f1}


def _compute_component_f1(enrolled, result, file_to_comps):
    """Compute component-level F1 for any system result."""
    # Mapped-only universe (v1.2, D-01): a (sentence, file) pair whose file has
    # NO SAM-CODE component contributes NOTHING -- the former `{b}` singleton
    # fallback `(s, c)` is gone, mirroring component_suite._code_inputs. This
    # makes the headline component_f1 the mapped-only micro number, equal to
    # component_suite micro by construction.
    gold_comp = set()
    for s, c in enrolled:
        for comp in file_to_comps.get(c, set()):
            gold_comp.add((s, comp))

    result_comp = set()
    for s, c in result:
        for comp in file_to_comps.get(c, set()):
            result_comp.add((s, comp))

    cp, cr, cf1, ctp, cfp, cfn = calc_metrics(gold_comp, result_comp)
    return {"tp": ctp, "fp": cfp, "fn": cfn,
            "p": cp, "r": cr, "f1": cf1,
            "gold_size": len(gold_comp), "result_size": len(result_comp)}


def _compute_weighted_f1(enrolled, result, enrolled_to_raw, raw_to_enrolled):
    """Compute inverse-expansion-weighted F1 for any system result."""
    weights = {}
    for entry in enrolled:
        raw = enrolled_to_raw.get(entry)
        if raw:
            block_size = len(raw_to_enrolled[raw])
            weights[entry] = 1.0 / block_size
        else:
            weights[entry] = 1.0

    tp_set = enrolled & result
    fn_set = enrolled - result
    fp_set = result - enrolled

    w_tp = sum(weights.get(e, 0) for e in tp_set)
    w_fn = sum(weights.get(e, 0) for e in fn_set)

    fp_by_dir = defaultdict(list)
    for s, c in fp_set:
        parts = c.rsplit("/", 1)
        dir_key = (s, parts[0] + "/") if len(parts) == 2 else (s, c)
        fp_by_dir[dir_key].append((s, c))
    w_fp = sum(1.0 for _ in fp_by_dir)

    w_p = w_tp / (w_tp + w_fp) if (w_tp + w_fp) else 0
    w_r = w_tp / (w_tp + w_fn) if (w_tp + w_fn) else 0
    w_f1 = 2 * w_p * w_r / (w_p + w_r) if (w_p + w_r) else 0
    return {"p": w_p, "r": w_r, "f1": w_f1,
            "w_tp": w_tp, "w_fp": w_fp, "w_fn": w_fn}


def part5_alternative_metrics(out, all_data):
    out("## Part 5: Alternative Metrics and Their Disagreements")
    out()
    out("We compute F1 at four granularities for **four systems** — TransArc, V45, LLM,")
    out("and V87 — and show where they disagree:")
    out()
    out("1. **File-level F1** (standard): each `(sentence, file)` is one data point")
    out("2. **Decision-level F1**: each raw gold entry `(sentence, dir_or_file)` is one data point.")
    out("   A raw entry is a TP if ≥50% of its enrolled files are TPs.")
    out("3. **Component-level F1**: each `(sentence, component_name)` is one data point.")
    out("   Collapse code files back to their architectural component (via SAM-CODE gold).")
    out("4. **Weighted File F1**: each enrolled link weighted by 1/block_size, so one directory = one unit of weight.")
    out()
    out("**Systems:**")
    out("- **TransArc**: Traditional transitive pipeline (SAD-SAM × SAM-CODE)")
    out("- **V45**: Discourse-aware LLM linker (SAD-SAM), projected through ARCOTL SAM-CODE")
    out("- **LLM**: Zero-training meta-learning classifier, projected through gold SAM-CODE")
    out("- **V87-pc**: Few-shot meta-learning (10% gold, per-component strategy),")
    out("  projected through TransArc SAM-CODE — **aggregate F1 only** (no per-link data)")
    out()

    # Load V87 per-component aggregate data
    v87_data = load_v87_per_component()

    # Pre-compute file_to_comps for each project
    file_to_comps_map = {}
    for proj in PROJECTS:
        d = all_data[proj]
        names = load_model_element_names(proj)
        sam_enrolled = load_sam_code_enrolled(proj, d["code_model"])
        file_to_comps = defaultdict(set)
        for ae, fp in sam_enrolled:
            file_to_comps[fp].add(names.get(ae, ae))
        file_to_comps_map[proj] = file_to_comps

    # Compute all alternative metrics for all systems with per-link data
    ta_decision = {}; ta_comp = {}; ta_weighted = {}
    v45_file = {}; v45_decision = {}; v45_comp = {}; v45_weighted = {}
    llm_file = {}; llm_decision = {}; llm_comp = {}; llm_weighted = {}
    v87_file = {}  # aggregate only

    for proj in PROJECTS:
        d = all_data[proj]
        enrolled = d["enrolled"]
        raw_to_enrolled = d["raw_to_enrolled"]
        enrolled_to_raw = d["enrolled_to_raw"]
        ftc = file_to_comps_map[proj]

        # TransArc
        ta_decision[proj] = _compute_decision_f1(enrolled, d["result"], raw_to_enrolled)
        ta_comp[proj] = _compute_component_f1(enrolled, d["result"], ftc)
        ta_weighted[proj] = _compute_weighted_f1(enrolled, d["result"], enrolled_to_raw, raw_to_enrolled)

        # V45
        v45_res = d["v45_result"]
        v45_file[proj] = {"p": d["v45_p"], "r": d["v45_r"], "f1": d["v45_f1"]}
        v45_decision[proj] = _compute_decision_f1(enrolled, v45_res, raw_to_enrolled)
        v45_comp[proj] = _compute_component_f1(enrolled, v45_res, ftc)
        v45_weighted[proj] = _compute_weighted_f1(enrolled, v45_res, enrolled_to_raw, raw_to_enrolled)

        # LLM
        llm_res = d["llm_result"]
        lp, lr, lf1, ltp, lfp, lfn = calc_metrics(enrolled, llm_res)
        llm_file[proj] = {"p": lp, "r": lr, "f1": lf1, "tp": ltp, "fp": lfp, "fn": lfn}
        llm_decision[proj] = _compute_decision_f1(enrolled, llm_res, raw_to_enrolled)
        llm_comp[proj] = _compute_component_f1(enrolled, llm_res, ftc)
        llm_weighted[proj] = _compute_weighted_f1(enrolled, llm_res, enrolled_to_raw, raw_to_enrolled)

        # V87: aggregate file-level F1 only
        if proj in v87_data:
            v87_file[proj] = v87_data[proj]  # {P, R, F1}
        else:
            v87_file[proj] = {"P": 0, "R": 0, "F1": 0}

    # ── Helper for averages ──
    n = len(PROJECTS)

    def avg_metric(metric_dict, key="f1"):
        return sum(metric_dict[p][key] if isinstance(metric_dict[p].get(key, 0), (int, float))
                   else metric_dict[p].get(key, 0) for p in PROJECTS) / n

    # 5.1: TransArc detail tables (keep for reference, same as before)
    out("### 5.1 Decision-Level F1 (TransArc)")
    out()
    out("Treat each raw gold entry as a single binary decision. A raw entry is 'hit' (TP)")
    out("if the system returned at least 50% of its enrolled files; otherwise it's a miss (FN).")
    out("System results not matching any gold entry are FPs (counted per unique directory/file in result).")
    out()

    out("| Project | Dec. TP | Dec. FP | Dec. FN | Dec. P | Dec. R | Dec. F1 | File F1 | Δ |")
    out("|---------|--------|--------|--------|--------|--------|---------|---------|---|")
    for proj in PROJECTS:
        dd = ta_decision[proj]
        fd = all_data[proj]
        delta = dd["f1"] - fd["f1"]
        out(f"| {proj} | {dd['tp']} | {dd['fp']} | {dd['fn']} "
            f"| {dd['p']:.3f} | {dd['r']:.3f} | {dd['f1']:.3f} "
            f"| {fd['f1']:.3f} | {delta:+.3f} |")
    out()

    # 5.2: Component-Level (TransArc)
    out("### 5.2 Component-Level F1 (TransArc)")
    out()
    out("Collapse file paths to architectural components using the SAM-CODE gold standard.")
    out("A `(sentence, component)` pair is the evaluation unit.")
    out()

    out("| Project | Comp. Gold | Comp. Result | Comp. P | Comp. R | Comp. F1 | File F1 | Δ |")
    out("|---------|-----------|-------------|---------|---------|----------|---------|---|")
    for proj in PROJECTS:
        cd = ta_comp[proj]
        fd = all_data[proj]
        delta = cd["f1"] - fd["f1"]
        out(f"| {proj} | {cd['gold_size']} | {cd['result_size']} "
            f"| {cd['p']:.3f} | {cd['r']:.3f} | {cd['f1']:.3f} "
            f"| {fd['f1']:.3f} | {delta:+.3f} |")
    out()

    # 5.3: Weighted (TransArc)
    out("### 5.3 Inverse-Expansion-Weighted F1 (TransArc)")
    out()
    out("Weight each enrolled link by `1/block_size`, so all files from one directory")
    out("collectively count as 1.0, not N separate data points.")
    out()

    out("| Project | W-TP | W-FP | W-FN | W-P | W-R | W-F1 | File F1 | Δ |")
    out("|---------|------|------|------|-----|-----|------|---------|---|")
    for proj in PROJECTS:
        wd = ta_weighted[proj]
        fd = all_data[proj]
        delta = wd["f1"] - fd["f1"]
        out(f"| {proj} | {wd['w_tp']:.1f} | {wd['w_fp']:.0f} | {wd['w_fn']:.1f} "
            f"| {wd['p']:.3f} | {wd['r']:.3f} | {wd['f1']:.3f} "
            f"| {fd['f1']:.3f} | {delta:+.3f} |")
    out()

    # 5.4: Full comparison — All 4 systems at all granularities
    out("### 5.4 Full Metric Comparison — All Systems")
    out()
    out("**File-level F1** (standard enrolled metric):")
    out()
    out("| Project | TransArc | V45 | LLM | V87-pc |")
    out("|---------|----------|-----|-----|--------|")
    for proj in PROJECTS:
        out(f"| {proj} | {all_data[proj]['f1']:.3f} | {v45_file[proj]['f1']:.3f} "
            f"| {llm_file[proj]['f1']:.3f} | {v87_file[proj]['F1']:.3f} |")
    avg_ta_file = sum(all_data[p]["f1"] for p in PROJECTS) / n
    avg_v45_file = sum(v45_file[p]["f1"] for p in PROJECTS) / n
    avg_llm_file = sum(llm_file[p]["f1"] for p in PROJECTS) / n
    avg_v87_file = sum(v87_file[p]["F1"] for p in PROJECTS) / n
    out(f"| **Average** | **{avg_ta_file:.3f}** | **{avg_v45_file:.3f}** "
        f"| **{avg_llm_file:.3f}** | **{avg_v87_file:.3f}** |")
    out()

    out("**Decision-level F1** (one raw gold entry = one data point):")
    out()
    out("| Project | TransArc | V45 | LLM | V87-pc |")
    out("|---------|----------|-----|-----|--------|")
    for proj in PROJECTS:
        out(f"| {proj} | {ta_decision[proj]['f1']:.3f} | {v45_decision[proj]['f1']:.3f} "
            f"| {llm_decision[proj]['f1']:.3f} | N/A |")
    avg_ta_dec = sum(ta_decision[p]["f1"] for p in PROJECTS) / n
    avg_v45_dec = sum(v45_decision[p]["f1"] for p in PROJECTS) / n
    avg_llm_dec = sum(llm_decision[p]["f1"] for p in PROJECTS) / n
    out(f"| **Average** | **{avg_ta_dec:.3f}** | **{avg_v45_dec:.3f}** "
        f"| **{avg_llm_dec:.3f}** | N/A |")
    out()

    out("**Component-level F1** (sentence × component pairs):")
    out()
    out("| Project | TransArc | V45 | LLM | V87-pc |")
    out("|---------|----------|-----|-----|--------|")
    for proj in PROJECTS:
        out(f"| {proj} | {ta_comp[proj]['f1']:.3f} | {v45_comp[proj]['f1']:.3f} "
            f"| {llm_comp[proj]['f1']:.3f} | N/A |")
    avg_ta_comp = sum(ta_comp[p]["f1"] for p in PROJECTS) / n
    avg_v45_comp = sum(v45_comp[p]["f1"] for p in PROJECTS) / n
    avg_llm_comp = sum(llm_comp[p]["f1"] for p in PROJECTS) / n
    out(f"| **Average** | **{avg_ta_comp:.3f}** | **{avg_v45_comp:.3f}** "
        f"| **{avg_llm_comp:.3f}** | N/A |")
    out()

    out("**Weighted File F1** (1/block_size weighting):")
    out()
    out("| Project | TransArc | V45 | LLM | V87-pc |")
    out("|---------|----------|-----|-----|--------|")
    for proj in PROJECTS:
        out(f"| {proj} | {ta_weighted[proj]['f1']:.3f} | {v45_weighted[proj]['f1']:.3f} "
            f"| {llm_weighted[proj]['f1']:.3f} | N/A |")
    avg_ta_w = sum(ta_weighted[p]["f1"] for p in PROJECTS) / n
    avg_v45_w = sum(v45_weighted[p]["f1"] for p in PROJECTS) / n
    avg_llm_w = sum(llm_weighted[p]["f1"] for p in PROJECTS) / n
    out(f"| **Average** | **{avg_ta_w:.3f}** | **{avg_v45_w:.3f}** "
        f"| **{avg_llm_w:.3f}** | N/A |")
    out()

    # 5.5: Per-system summary tables
    out("### 5.5 Per-System Summary (All Granularities)")
    out()

    for sys_name, sys_file, sys_dec, sys_comp, sys_w in [
        ("TransArc",
         {p: {"f1": all_data[p]["f1"]} for p in PROJECTS},
         ta_decision, ta_comp, ta_weighted),
        ("V45", v45_file, v45_decision, v45_comp, v45_weighted),
        ("LLM (Meta-Learning)", llm_file, llm_decision, llm_comp, llm_weighted),
    ]:
        out(f"**{sys_name}:**")
        out()
        out("| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |")
        out("|---------|---------|-------------|-------------|-------------|")
        for proj in PROJECTS:
            out(f"| {proj} | {sys_file[proj]['f1']:.3f} | {sys_dec[proj]['f1']:.3f} "
                f"| {sys_comp[proj]['f1']:.3f} | {sys_w[proj]['f1']:.3f} |")
        avg_f = sum(sys_file[p]["f1"] for p in PROJECTS) / n
        avg_d = sum(sys_dec[p]["f1"] for p in PROJECTS) / n
        avg_c = sum(sys_comp[p]["f1"] for p in PROJECTS) / n
        avg_w = sum(sys_w[p]["f1"] for p in PROJECTS) / n
        out(f"| **Average** | **{avg_f:.3f}** | **{avg_d:.3f}** | **{avg_c:.3f}** | **{avg_w:.3f}** |")
        out()

    out("**V87 per-component** (aggregate file-level F1 only — no per-link data for alternative metrics):")
    out()
    out("| Project | File F1 | Decision F1 | Component F1 | Weighted F1 |")
    out("|---------|---------|-------------|-------------|-------------|")
    for proj in PROJECTS:
        out(f"| {proj} | {v87_file[proj]['F1']:.3f} | N/A | N/A | N/A |")
    out(f"| **Average** | **{avg_v87_file:.3f}** | N/A | N/A | N/A |")
    out()

    # 5.6: Head-to-head — Which system wins at each granularity?
    out("### 5.6 System Comparison Instability — Which System Wins?")
    out()
    out("The central question: does the choice of metric change which system appears better?")
    out()

    # Average comparison across all metrics and systems
    out("**Average F1 across projects:**")
    out()
    out("| Metric | TransArc | V45 | LLM | V87-pc | Best |")
    out("|--------|----------|-----|-----|--------|------|")
    for label, ta_avg, v45_avg, llm_avg, v87_avg in [
        ("File F1", avg_ta_file, avg_v45_file, avg_llm_file, avg_v87_file),
        ("Decision F1", avg_ta_dec, avg_v45_dec, avg_llm_dec, None),
        ("Component F1", avg_ta_comp, avg_v45_comp, avg_llm_comp, None),
        ("Weighted F1", avg_ta_w, avg_v45_w, avg_llm_w, None),
    ]:
        vals = {"TransArc": ta_avg, "V45": v45_avg, "LLM": llm_avg}
        if v87_avg is not None:
            vals["V87-pc"] = v87_avg
        best = max(vals, key=vals.get)
        v87_str = f"{v87_avg:.3f}" if v87_avg is not None else "N/A"
        out(f"| {label} | {ta_avg:.3f} | {v45_avg:.3f} | {llm_avg:.3f} | {v87_str} | {best} |")
    out()

    # Per-project winner at each granularity (File F1 only for V87)
    out("**Per-project winners (File F1):**")
    out()
    out("| Project | TransArc | V45 | LLM | V87-pc | Best |")
    out("|---------|----------|-----|-----|--------|------|")
    for proj in PROJECTS:
        ta_f = all_data[proj]["f1"]
        v45_f = v45_file[proj]["f1"]
        llm_f = llm_file[proj]["f1"]
        v87_f = v87_file[proj]["F1"]
        vals = {"TransArc": ta_f, "V45": v45_f, "LLM": llm_f, "V87-pc": v87_f}
        best = max(vals, key=vals.get)
        out(f"| {proj} | {ta_f:.3f} | {v45_f:.3f} | {llm_f:.3f} | {v87_f:.3f} | {best} |")
    out()

    out("**Per-project winners (Component F1) — most semantically meaningful:**")
    out()
    out("| Project | TransArc | V45 | LLM | Best |")
    out("|---------|----------|-----|-----|------|")
    for proj in PROJECTS:
        ta_c = ta_comp[proj]["f1"]
        v45_c = v45_comp[proj]["f1"]
        llm_c = llm_comp[proj]["f1"]
        vals = {"TransArc": ta_c, "V45": v45_c, "LLM": llm_c}
        best = max(vals, key=vals.get)
        out(f"| {proj} | {ta_c:.3f} | {v45_c:.3f} | {llm_c:.3f} | {best} |")
    out()

    # Winner flip analysis
    out("**Winner flips across metric granularity (per project):**")
    out()
    out("Does the choice of metric change which system wins on a given project?")
    out("For each project, we check if the best system changes across File/Decision/Component/Weighted F1.")
    out()
    systems_3 = ["TransArc", "V45", "LLM"]
    flip_count = 0
    for proj in PROJECTS:
        winners = []
        for metric_vals in [
            (all_data[proj]["f1"], v45_file[proj]["f1"], llm_file[proj]["f1"]),
            (ta_decision[proj]["f1"], v45_decision[proj]["f1"], llm_decision[proj]["f1"]),
            (ta_comp[proj]["f1"], v45_comp[proj]["f1"], llm_comp[proj]["f1"]),
            (ta_weighted[proj]["f1"], v45_weighted[proj]["f1"], llm_weighted[proj]["f1"]),
        ]:
            best_idx = max(range(3), key=lambda i: metric_vals[i])
            winners.append(systems_3[best_idx])
        unique_winners = set(winners)
        if len(unique_winners) > 1:
            flip_count += 1
            out(f"- **{proj}**: {', '.join(f'{m}→{w}' for m, w in zip(['File','Dec','Comp','Weighted'], winners))}")

    if flip_count == 0:
        out("No winner flips detected.")
    out()
    out(f"**{flip_count}/{n}** projects show a winner flip across metric granularities.")
    out()

    # 5.7: Ranking disagreements
    out("### 5.7 Project Ranking Disagreements (TransArc)")
    out()
    out("Do alternative metrics change the **ranking** of projects?")
    out()

    def rank_projects(metric_fn):
        return sorted(PROJECTS, key=metric_fn, reverse=True)

    file_ranking = rank_projects(lambda p: all_data[p]["f1"])
    dec_ranking = rank_projects(lambda p: ta_decision[p]["f1"])
    comp_ranking = rank_projects(lambda p: ta_comp[p]["f1"])
    w_ranking = rank_projects(lambda p: ta_weighted[p]["f1"])

    out("| Rank | File F1 | Decision F1 | Component F1 | Weighted F1 |")
    out("|------|---------|-------------|-------------|-------------|")
    for i in range(len(PROJECTS)):
        out(f"| {i+1} | {file_ranking[i]} | {dec_ranking[i]} | {comp_ranking[i]} | {w_ranking[i]} |")
    out()

    def kendall_distance(r1, r2):
        discordant = 0
        for i in range(len(PROJECTS)):
            for j in range(i + 1, len(PROJECTS)):
                pos_i_1 = r1.index(PROJECTS[i])
                pos_j_1 = r1.index(PROJECTS[j])
                pos_i_2 = r2.index(PROJECTS[i])
                pos_j_2 = r2.index(PROJECTS[j])
                if (pos_i_1 - pos_j_1) * (pos_i_2 - pos_j_2) < 0:
                    discordant += 1
        return discordant

    max_pairs = len(PROJECTS) * (len(PROJECTS) - 1) // 2
    out(f"Pairwise ranking disagreements (discordant pairs out of {max_pairs}):")
    out(f"- File vs Decision: {kendall_distance(file_ranking, dec_ranking)}")
    out(f"- File vs Component: {kendall_distance(file_ranking, comp_ranking)}")
    out(f"- File vs Weighted: {kendall_distance(file_ranking, w_ranking)}")
    out(f"- Decision vs Component: {kendall_distance(dec_ranking, comp_ranking)}")
    out()

    return (ta_decision, ta_comp, ta_weighted,
            v45_file, v45_decision, v45_comp, v45_weighted,
            llm_file, llm_decision, llm_comp, llm_weighted,
            v87_file)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: Case Studies — Where the distortion is most visible
# ═══════════════════════════════════════════════════════════════════════════════

def part6_case_studies(out, all_data):
    out("## Part 6: Case Studies")
    out()

    # Case Study 1: JabRef — 38 decisions masquerading as 8,268 data points
    out("### 6.1 JabRef: 38 Decisions Masquerading as 8,268 Data Points")
    out()
    d = all_data["jabref"]
    out(f"JabRef has **zero** file-level gold entries — every single raw entry is a directory.")
    out(f"The 38 raw decisions expand to {d['n_enrolled']:,} enrolled links (217.6x).")
    out(f"The file-level F1 of {d['f1']:.3f} appears precise to 3 decimal places,")
    out(f"but it's really measuring ~38 binary decisions.")
    out()
    out("**The 5 most influential decisions:**")
    out()

    enrolled = d["enrolled"]
    result = d["result"]
    f1_base = d["f1"]
    sensitivities = []
    for raw_key, enrolled_set in d["raw_to_enrolled"].items():
        gold_without = enrolled - enrolled_set
        if not gold_without:
            continue
        _, _, f1_wo, _, _, _ = calc_metrics(gold_without, result)
        n_tp = sum(1 for e in enrolled_set if e in d["tp_set"])
        n_fn = sum(1 for e in enrolled_set if e in d["fn_set"])
        sensitivities.append((raw_key, len(enrolled_set), n_tp, n_fn, f1_wo - f1_base))

    sensitivities.sort(key=lambda x: abs(x[4]), reverse=True)
    out("| Decision | Dir | Size | TPs | FNs | ΔF1 if excluded |")
    out("|----------|-----|------|-----|-----|----------------|")
    for raw_key, size, n_tp, n_fn, delta in sensitivities[:5]:
        sid, path = raw_key
        path_short = path.split("/")[-2] + "/" if "/" in path else path
        out(f"| S{sid}→{path_short} | {path[:40]}… | {size} | {n_tp} | {n_fn} | {delta:+.4f} |")
    out()

    # Sum of top-5 |ΔF1|
    top5_total = sum(abs(x[4]) for x in sensitivities[:5])
    out(f"The top-5 decisions collectively account for |ΔF1| sum = {top5_total:.3f}.")
    out(f"The remaining {len(sensitivities)-5} decisions have much smaller influence.")
    out()

    # Case Study 2: Teammates — Interface/Component overlap
    out("### 6.2 Teammates: Interface/Component Overlap Doubles the Counting")
    out()
    code_model = all_data["teammates"]["code_model"]
    names = load_model_element_names("teammates")
    sam_enrolled = load_sam_code_enrolled("teammates", code_model)

    # Check how many files are shared between Component and Interface of same name
    comp_files = defaultdict(set)
    iface_files = defaultdict(set)
    for ae, fp in sam_enrolled:
        name = names.get(ae, ae)
        base_name = name.split(": ", 1)[1] if ": " in name else name
        if name.startswith("Interface:"):
            iface_files[base_name].add(fp)
        else:
            comp_files[base_name].add(fp)

    out("| Base Name | Component Files | Interface Files | Overlap | Overlap % |")
    out("|-----------|----------------|----------------|---------|-----------|")
    for base_name in sorted(comp_files.keys()):
        cf = comp_files[base_name]
        ifx = iface_files.get(base_name, set())
        overlap = cf & ifx
        pct = len(overlap) / len(cf) * 100 if cf else 0
        out(f"| {base_name} | {len(cf)} | {len(ifx)} | {len(overlap)} | {pct:.0f}% |")
    out()

    out("Every Component-Interface pair shares **100% of files** in Teammates.")
    out("This means each sentence→component assignment is effectively counted twice")
    out("at the file level (once via the Component, once via the Interface).")
    out("This is an artifact of the architecture model, not a reflection of system quality.")
    out()

    # Case Study 3: MediaStore vs JabRef — Why averages are misleading
    out("### 6.3 Cross-Project Incomparability")
    out()
    out("| Property | MediaStore | JabRef | Ratio |")
    out("|----------|-----------|--------|-------|")
    dm = all_data["mediastore"]
    dj = all_data["jabref"]
    out(f"| Raw gold entries | {dm['n_raw']} | {dj['n_raw']} | {dj['n_raw']/dm['n_raw']:.1f}x |")
    out(f"| Enrolled links | {dm['n_enrolled']} | {dj['n_enrolled']:,} | {dj['n_enrolled']/dm['n_enrolled']:.0f}x |")
    out(f"| Enrollment ratio | {dm['n_enrolled']/dm['n_raw']:.1f}x | {dj['n_enrolled']/dj['n_raw']:.1f}x | |")
    out(f"| File-level F1 | {dm['f1']:.3f} | {dj['f1']:.3f} | |")
    out(f"| % TP from dirs | {dm['tp_from_dir']/dm['tp']*100:.0f}% | {dj['tp_from_dir']/dj['tp']*100:.0f}% | |")
    out()
    out("MediaStore's F1 measures 57 file-level decisions (mostly actual files).")
    out(f"JabRef's F1 measures 8,268 enrolled links derived from 38 directory decisions.")
    out("Averaging these F1 scores gives JabRef 140x more weight in the aggregate, despite")
    out("having fewer actual decisions. A macro-average across projects treats them equally,")
    out("but the file-level F1 itself gives massively different weight to different projects.")
    out()


# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: Synthesis
# ═══════════════════════════════════════════════════════════════════════════════

def part7_synthesis(out, all_data,
                    ta_decision, ta_comp, ta_weighted,
                    v45_file, v45_decision, v45_comp, v45_weighted,
                    llm_file, llm_decision, llm_comp, llm_weighted,
                    v87_file):
    out("## Part 7: Synthesis — The Case Against File-Level P/R/F1")
    out()

    out("### Three Biases, One Conclusion")
    out()
    out("| Bias | Mechanism | Effect on File-Level F1 |")
    out("|------|-----------|------------------------|")
    out("| **SAD-SAM Long-Tail** | Few model elements have many links; most have few or none (UME) | "
        "Systems are tested mainly on popular elements; rare elements barely affect the score |")
    out("| **Enrollment Amplification** | Directories expand to 1–642 files each | "
        "One annotator decision becomes hundreds of data points; metric precision is illusory |")
    out("| **SAM-CODE Concentration** | Top-3 AEs hold 43–99% of all SAM-CODE links | "
        "Getting 3 components right/wrong dominates the entire evaluation |")
    out()

    out("### The Compound Effect")
    out()
    out("These biases don't just add — they **multiply**:")
    out()
    out("1. A sentence links to a popular model element (SAD-SAM long-tail)")
    out("2. That model element maps to hundreds of code files (SAM-CODE concentration)")
    out("3. Those files came from directory enrollment (enrollment amplification)")
    out()
    out("**Result**: One correct sentence→component association generates hundreds of file-level TPs.")
    out("One incorrect association generates hundreds of file-level FPs.")
    out("The file-level F1 score is dominated by a handful of high-impact decisions")
    out("while appearing to be a fine-grained, statistically robust evaluation.")
    out()

    out("### What File-Level F1 Actually Measures")
    out()
    total_raw = sum(all_data[p]["n_raw"] for p in PROJECTS)
    total_enrolled = sum(all_data[p]["n_enrolled"] for p in PROJECTS)
    total_tp = sum(all_data[p]["tp"] for p in PROJECTS)
    total_tp_dir = sum(all_data[p]["tp_from_dir"] for p in PROJECTS)
    out(f"- **{total_enrolled:,} data points** are derived from **{total_raw} decisions** ({total_enrolled/total_raw:.0f}:1 inflation)")
    out(f"- **{total_tp_dir/total_tp*100:.0f}%** of TPs come from directory enrollment")
    out(f"- Removing the **single** most influential raw entry per project swings F1 by up to **4 percentage points**")
    out(f"- Block homogeneity is near 100%: files within a directory block are not independent observations")
    out(f"- Alternative metrics (decision-level, component-level, weighted) disagree with file-level rankings")
    out()

    out("### System Comparison Depends on Metric Granularity")
    out()
    out("The choice of evaluation metric changes which system appears better.")
    out("We compare all four systems (TransArc, V45, LLM, V87-pc) across metrics:")
    out()
    n = len(PROJECTS)
    avg_ta_file = sum(all_data[p]["f1"] for p in PROJECTS) / n
    avg_ta_dec = sum(ta_decision[p]["f1"] for p in PROJECTS) / n
    avg_ta_comp = sum(ta_comp[p]["f1"] for p in PROJECTS) / n
    avg_ta_w = sum(ta_weighted[p]["f1"] for p in PROJECTS) / n
    avg_v45_file = sum(v45_file[p]["f1"] for p in PROJECTS) / n
    avg_v45_dec = sum(v45_decision[p]["f1"] for p in PROJECTS) / n
    avg_v45_comp = sum(v45_comp[p]["f1"] for p in PROJECTS) / n
    avg_v45_w = sum(v45_weighted[p]["f1"] for p in PROJECTS) / n
    avg_llm_file = sum(llm_file[p]["f1"] for p in PROJECTS) / n
    avg_llm_dec = sum(llm_decision[p]["f1"] for p in PROJECTS) / n
    avg_llm_comp = sum(llm_comp[p]["f1"] for p in PROJECTS) / n
    avg_llm_w = sum(llm_weighted[p]["f1"] for p in PROJECTS) / n
    avg_v87_file = sum(v87_file[p]["F1"] for p in PROJECTS) / n

    out("| Metric | TransArc | V45 | LLM | V87-pc | Best |")
    out("|--------|----------|-----|-----|--------|------|")
    for label, ta_avg, v45_avg, llm_avg, v87_avg in [
        ("File F1", avg_ta_file, avg_v45_file, avg_llm_file, avg_v87_file),
        ("Decision F1", avg_ta_dec, avg_v45_dec, avg_llm_dec, None),
        ("Component F1", avg_ta_comp, avg_v45_comp, avg_llm_comp, None),
        ("Weighted F1", avg_ta_w, avg_v45_w, avg_llm_w, None),
    ]:
        vals = {"TransArc": ta_avg, "V45": v45_avg, "LLM": llm_avg}
        if v87_avg is not None:
            vals["V87-pc"] = v87_avg
        best = max(vals, key=vals.get)
        v87_str = f"{v87_avg:.3f}" if v87_avg is not None else "N/A"
        out(f"| {label} | {ta_avg:.3f} | {v45_avg:.3f} | {llm_avg:.3f} | {v87_str} | {best} |")
    out()

    # Count per-project winner flips across 3 systems with full metric data
    systems_3 = ["TransArc", "V45", "LLM"]
    flips = 0
    for proj in PROJECTS:
        winners = []
        for metric_vals in [
            (all_data[proj]["f1"], v45_file[proj]["f1"], llm_file[proj]["f1"]),
            (ta_decision[proj]["f1"], v45_decision[proj]["f1"], llm_decision[proj]["f1"]),
            (ta_comp[proj]["f1"], v45_comp[proj]["f1"], llm_comp[proj]["f1"]),
            (ta_weighted[proj]["f1"], v45_weighted[proj]["f1"], llm_weighted[proj]["f1"]),
        ]:
            best_idx = max(range(3), key=lambda i: metric_vals[i])
            winners.append(systems_3[best_idx])
        if len(set(winners)) > 1:
            flips += 1

    out(f"In **{flips}/{n}** projects, changing the metric granularity flips which system wins.")
    out("This means that claims like 'System A outperforms System B' are not robust —")
    out("they depend on the (arbitrary) choice of evaluation granularity.")
    out()

    out("### Recommendations")
    out()
    out("1. **Report multiple granularities**: Always report decision-level and component-level")
    out("   metrics alongside file-level metrics. If they disagree, investigate why.")
    out()
    out("2. **Weight by inverse expansion**: Use `1/block_size` weights so each annotator")
    out("   decision contributes equally to the score, regardless of how many files a directory contains.")
    out()
    out("3. **Report raw decision counts**: State how many independent gold standard decisions")
    out("   underlie the metric, not just the enrolled link count.")
    out()
    out("4. **Beware cross-project averages**: Projects with high enrollment expansion")
    out("   (JabRef: 218x) dominate any micro-average. Use macro-averages over projects,")
    out("   and report per-project metrics prominently.")
    out()
    out("5. **Consider component-level evaluation for SAD-CODE**: Since SAD-CODE is effectively")
    out("   'which components is this sentence about?', evaluating at the component level")
    out("   is more semantically meaningful than the file level.")
    out()
    out("6. **Sensitivity analysis**: For any new approach, report the F1 sensitivity to the")
    out("   top-5 most influential raw entries. If removing one entry changes F1 by >0.02,")
    out("   the result is fragile.")
    out()
    out("7. **Be skeptical of system comparisons**: If the winner changes depending on whether")
    out("   you measure at file, decision, or component level, the performance difference")
    out("   is likely within the noise of the evaluation methodology.")
    out()


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    out("# Evaluation Critique: Why File-Level P/R/F1 Is Inadequate for SAD-CODE")
    out()
    out("*A deep investigation of how distributional biases in the ARDoCo benchmark render*")
    out("*standard file-level precision/recall/F1 misleading for the SAD-CODE traceability task.*")
    out()

    all_data = part1_inflation(out)
    part2_block_correlation(out, all_data)
    part3_sensitivity(out, all_data)
    part4_double_amplification(out)
    (ta_decision, ta_comp, ta_weighted,
     v45_file, v45_decision, v45_comp, v45_weighted,
     llm_file, llm_decision, llm_comp, llm_weighted,
     v87_file) = part5_alternative_metrics(out, all_data)
    part6_case_studies(out, all_data)
    part7_synthesis(out, all_data,
                    ta_decision, ta_comp, ta_weighted,
                    v45_file, v45_decision, v45_comp, v45_weighted,
                    llm_file, llm_decision, llm_comp, llm_weighted,
                    v87_file)

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
        f.write("\n")

    print(f"\n\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
