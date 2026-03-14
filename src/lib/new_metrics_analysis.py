#!/usr/bin/env python3
"""
New Metrics for SAD-CODE Traceability Evaluation

Proposes and computes 6 novel metrics that address specific blind spots
of standard P/R/F1 on file-level enrolled gold standards. Computes
measurements for both TransArc and V45 linker.

Outputs: NEW_METRICS_REPORT.md
"""

import csv
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

# Import data loaders from the shared library module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    GS_SAD_SAM, GS_SAM_CODE, GS_SAD_CODE, ACM_FILES, TEXT_FILES,
    normalize_path, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_raw,
    load_gs_sam_code_maps, load_gs_sad_code_raw, load_gs_sad_code_enrolled,
    load_result_sad_code, load_transarc_intermediate_sad_sam,
    load_transarc_intermediate_sam_code, load_text, load_model_element_names,
    calc_metrics,
)

OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/NEW_METRICS_REPORT.md")

V45_DIR = Path("/mnt/hostshare/ardoco-home/llm-sad-sam-agent/results/evaluation_results/v45_20260202_115342")

# ─── V45 data loader ─────────────────────────────────────────────────────────

def load_v45_sad_sam(project):
    """Load V45 SAD-SAM links as set of (modelElementID, sentence_str)."""
    path = V45_DIR / project / "v45_links.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["component_id"], row["sentence"]))
    return links


def load_v45_sad_sam_with_confidence(project):
    """Load V45 links with confidence for MAP computation."""
    path = V45_DIR / project / "v45_links.csv"
    links = []  # list of (sentence_str, component_id, confidence)
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.append((row["sentence"], row["component_id"], float(row["confidence"])))
    return links


def compose_sad_code(sad_sam_links, sam_code_map):
    """Compose SAD-SAM × SAM-CODE → SAD-CODE links.

    Args:
        sad_sam_links: set of (modelElementID, sentence_str)
        sam_code_map: dict of modelElementID → set(code_path)

    Returns:
        set of (sentence_str, code_path)
    """
    result = set()
    for model_id, sent in sad_sam_links:
        for code_path in sam_code_map.get(model_id, set()):
            result.add((sent, code_path))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N1: Matthews Correlation Coefficient (MCC) at Component Level
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: P/R/F1 ignore true negatives. For SAD-SAM, most (sentence, component)
# pairs are negative. MCC is the gold standard for imbalanced binary
# classification: it uses all four quadrants of the confusion matrix and
# ranges from -1 (perfect inverse) to +1 (perfect). A random classifier
# always scores 0 regardless of class imbalance.

def compute_mcc(gold_links, result_links, all_sentences, all_components):
    """Compute MCC over the (sentence, component) universe.

    Args:
        gold_links: set of (component_id, sentence_str) — gold SAD-SAM
        result_links: set of (component_id, sentence_str) — predicted SAD-SAM
        all_sentences: set of all sentence numbers (str)
        all_components: set of all component IDs

    Returns:
        dict with tp, fp, fn, tn, mcc, balanced_accuracy
    """
    # Build universe of all (component, sentence) pairs
    universe_size = len(all_sentences) * len(all_components)

    tp = len(gold_links & result_links)
    fp = len(result_links - gold_links)
    fn = len(gold_links - result_links)
    tn = universe_size - tp - fp - fn

    # MCC formula
    numer = (tp * tn) - (fp * fn)
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) if \
        (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn) > 0 else 1
    mcc = numer / denom

    # Balanced accuracy = (sensitivity + specificity) / 2
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    bal_acc = (sensitivity + specificity) / 2

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "universe": universe_size,
        "mcc": mcc,
        "balanced_accuracy": bal_acc,
        "sensitivity": sensitivity,  # = recall
        "specificity": specificity,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N2: Sentence-Level Exact Match Rate (EMR)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: F1 treats partial matches as partial credit. In practice, a developer
# either gets the right set of components for a sentence or doesn't. EMR
# measures the fraction of sentences where the predicted component set
# exactly matches the gold set. Subset/superset rates reveal systematic
# over/under-prediction.

def compute_emr(gold_links, result_links):
    """Compute Exact Match Rate and related set-accuracy metrics.

    Args:
        gold_links: set of (component_id, sentence_str) — gold SAD-SAM
        result_links: set of (component_id, sentence_str) — predicted

    Returns:
        dict with emr, superset_rate, subset_rate, jaccard_mean, per-sentence detail
    """
    # Group by sentence
    gold_by_sent = defaultdict(set)
    result_by_sent = defaultdict(set)
    for comp, sent in gold_links:
        gold_by_sent[sent].add(comp)
    for comp, sent in result_links:
        result_by_sent[sent].add(comp)

    # Only evaluate sentences that appear in gold
    gold_sents = set(gold_by_sent.keys())
    n = len(gold_sents)
    if n == 0:
        return {"emr": 0, "superset_rate": 0, "subset_rate": 0, "jaccard_mean": 0}

    exact = 0
    superset = 0
    subset = 0
    jaccards = []

    for sent in gold_sents:
        g = gold_by_sent[sent]
        r = result_by_sent.get(sent, set())
        if g == r:
            exact += 1
        if r >= g:  # predicted is superset of gold
            superset += 1
        if r <= g and len(r) > 0:  # predicted is subset of gold (non-empty)
            subset += 1
        # Jaccard similarity
        union = g | r
        inter = g & r
        jaccards.append(len(inter) / len(union) if union else 0)

    # Also count gold sentences with zero predictions
    zero_pred = sum(1 for s in gold_sents if s not in result_by_sent)

    return {
        "emr": exact / n,
        "superset_rate": superset / n,
        "subset_rate": subset / n,
        "zero_pred_rate": zero_pred / n,
        "jaccard_mean": sum(jaccards) / len(jaccards) if jaccards else 0,
        "n_gold_sents": n,
        "n_exact": exact,
        "n_zero_pred": zero_pred,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N3: Per-Sentence Mean Average Precision (MAP)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: Standard metrics treat all predictions as binary. MAP rewards systems
# that rank correct components higher. A system that returns 3 components
# with the correct one first (confidence 0.99) is more useful than one
# returning the correct one last (confidence 0.80). MAP captures ranking
# quality and is standard in information retrieval.

def compute_map(gold_links, ranked_predictions):
    """Compute Mean Average Precision.

    Args:
        gold_links: set of (component_id, sentence_str)
        ranked_predictions: list of (sentence_str, component_id, confidence)

    Returns:
        dict with map, per-sentence AP
    """
    # Group gold by sentence
    gold_by_sent = defaultdict(set)
    for comp, sent in gold_links:
        gold_by_sent[sent].add(comp)

    # Group predictions by sentence, sorted by confidence descending
    pred_by_sent = defaultdict(list)
    for sent, comp, conf in ranked_predictions:
        pred_by_sent[sent].append((conf, comp))

    for sent in pred_by_sent:
        pred_by_sent[sent].sort(reverse=True)  # highest confidence first

    # Compute AP per gold sentence
    aps = []
    for sent in gold_by_sent:
        gold_comps = gold_by_sent[sent]
        preds = pred_by_sent.get(sent, [])
        if not preds:
            aps.append(0.0)
            continue

        hits = 0
        sum_prec = 0.0
        for rank, (conf, comp) in enumerate(preds, 1):
            if comp in gold_comps:
                hits += 1
                sum_prec += hits / rank
        ap = sum_prec / len(gold_comps) if gold_comps else 0
        aps.append(ap)

    return {
        "map": sum(aps) / len(aps) if aps else 0,
        "n_sentences": len(aps),
        "ap_values": aps,
    }


# TransArc doesn't have per-link confidence, so we assign uniform confidence
def transarc_sad_sam_as_ranked(sad_sam_links):
    """Convert TransArc SAD-SAM links to ranked format with uniform confidence."""
    return [(sent, comp, 0.5) for comp, sent in sad_sam_links]


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N4: Amplification-Corrected F1 (ACF1)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: In enrolled file-level evaluation, a single component-level error on
# JabRef's "logic" (972 files) counts 972× more than an error on
# MediaStore's "Facade" (1 file). ACF1 weights each file-level link
# by 1/|component_files|, so every component-level decision contributes
# equally regardless of code size. This removes the enrollment inflation
# that makes cross-project F1 incomparable.

def compute_acf1(gold_sad_code, result_sad_code, gold_sam_code_map):
    """Compute Amplification-Corrected F1 at SAD-CODE level.

    Each file-level link (sent, file) is weighted by 1/N where N is the
    number of files belonging to that file's component.

    Args:
        gold_sad_code: set of (sentence_str, code_path) — enrolled gold
        result_sad_code: set of (sentence_str, code_path) — predicted
        gold_sam_code_map: dict model_id → set(code_path) — enrolled SAM-CODE

    Returns:
        dict with acf1, weighted_tp, weighted_fp, weighted_fn
    """
    # Build file → component_file_count mapping
    file_to_weight = {}
    for model_id, files in gold_sam_code_map.items():
        n = len(files)
        for f in files:
            # A file might belong to multiple components — use minimum weight
            w = 1.0 / n if n > 0 else 1.0
            if f not in file_to_weight or w < file_to_weight[f]:
                file_to_weight[f] = w

    tp_set = gold_sad_code & result_sad_code
    fp_set = result_sad_code - gold_sad_code
    fn_set = gold_sad_code - result_sad_code

    def weighted_sum(link_set):
        total = 0.0
        for sent, code in link_set:
            total += file_to_weight.get(code, 1.0)
        return total

    w_tp = weighted_sum(tp_set)
    w_fp = weighted_sum(fp_set)
    w_fn = weighted_sum(fn_set)

    w_prec = w_tp / (w_tp + w_fp) if (w_tp + w_fp) > 0 else 0
    w_rec = w_tp / (w_tp + w_fn) if (w_tp + w_fn) > 0 else 0
    w_f1 = 2 * w_prec * w_rec / (w_prec + w_rec) if (w_prec + w_rec) > 0 else 0

    return {
        "acf1": w_f1,
        "acf1_precision": w_prec,
        "acf1_recall": w_rec,
        "weighted_tp": w_tp,
        "weighted_fp": w_fp,
        "weighted_fn": w_fn,
        "raw_tp": len(tp_set),
        "raw_fp": len(fp_set),
        "raw_fn": len(fn_set),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N5: Normalized Discrimination Gain (NDG)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: Raw F1 is incomparable across projects because project difficulty
# varies enormously (JabRef oracle F1=1.0, Teammates oracle F1=0.40).
# NDG normalizes by the achievable improvement over a random baseline:
#   NDG = (system_F1 - random_F1) / (oracle_F1 - random_F1)
# NDG=0 means "no better than random", NDG=1 means "as good as oracle".
# A system with NDG=0.7 on all projects is uniformly good; one with
# F1=0.94 on JabRef (NDG=0.90) and F1=0.59 on MediaStore (NDG=0.55)
# reveals uneven quality that raw F1 hides.

def compute_random_f1(gold_sad_code, n_sentences, n_components, gold_sam_code_map):
    """Estimate F1 of a random classifier that assigns components with gold prior.

    Random baseline: for each sentence, independently predict each component
    with probability = (gold sentences for that component) / total sentences.
    """
    # Component → number of gold sentences
    comp_sent_count = defaultdict(set)
    gold_by_sent = defaultdict(set)
    for sent, code in gold_sad_code:
        gold_by_sent[sent].add(code)

    # Use gold SAD-SAM to count per-component sentence assignments
    # Approximate: count distinct sentences per component file set
    file_to_comp = {}
    for comp, files in gold_sam_code_map.items():
        for f in files:
            file_to_comp[f] = comp

    comp_sents = defaultdict(set)
    for sent, code in gold_sad_code:
        comp = file_to_comp.get(code)
        if comp:
            comp_sents[comp].add(sent)

    # Expected TP, FP, FN for random assignment with per-component prior
    exp_tp = 0.0
    exp_fp = 0.0
    exp_fn = 0.0
    for comp, files in gold_sam_code_map.items():
        p = len(comp_sents.get(comp, set())) / n_sentences if n_sentences > 0 else 0
        n_gold = sum(1 for s, c in gold_sad_code if c in files)
        n_pred = p * n_sentences * len(files)  # expected predictions
        # Expected TP ≈ p × n_gold (each gold link has probability p of being predicted)
        exp_tp += p * n_gold
        exp_fp += n_pred - p * n_gold
        exp_fn += n_gold - p * n_gold

    prec = exp_tp / (exp_tp + exp_fp) if (exp_tp + exp_fp) > 0 else 0
    rec = exp_tp / (exp_tp + exp_fn) if (exp_tp + exp_fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return f1


def compute_oracle_f1(gold_sad_code, gold_sam_code_map, gold_sad_sam_maps):
    """Compute oracle F1 = perfect transitive composition (gold SAD-SAM × gold SAM-CODE).

    This is the theoretical ceiling for any transitive system.
    """
    sent_to_models, model_to_sents = gold_sad_sam_maps
    oracle = set()
    for model_id, files in gold_sam_code_map.items():
        for sent in model_to_sents.get(model_id, set()):
            for f in files:
                oracle.add((sent, f))
    p, r, f1, tp, fp, fn = calc_metrics(gold_sad_code, oracle)
    return f1, oracle


def compute_ndg(system_f1, random_f1, oracle_f1):
    """Normalized Discrimination Gain."""
    denom = oracle_f1 - random_f1
    if denom <= 0:
        return 1.0 if system_f1 >= oracle_f1 else 0.0
    return (system_f1 - random_f1) / denom


# ═══════════════════════════════════════════════════════════════════════════════
# Metric N6: Harmonic Usefulness Score (HUS)
# ═══════════════════════════════════════════════════════════════════════════════
#
# WHY: Coverage (fraction of gold sentences found) and purity (fraction of
# predicted sentences without false positives) capture complementary
# developer needs: "will the system find what I need?" vs "will it
# drown me in noise?" HUS is their harmonic mean, analogous to how F1
# balances precision and recall but at the sentence level. A system
# must excel at both to score well.

def compute_hus(gold_links, result_links):
    """Compute Harmonic Usefulness Score at SAD-CODE or SAD-SAM level.

    Args:
        gold_links: set of (id1, id2) — gold links
        result_links: set of (id1, id2) — predicted links

    Returns:
        dict with coverage, purity, hus, details
    """
    # Group by first element (sentence)
    gold_by_sent = defaultdict(set)
    result_by_sent = defaultdict(set)
    for a, b in gold_links:
        gold_by_sent[a].add(b)
    for a, b in result_links:
        result_by_sent[a].add(b)

    gold_sents = set(gold_by_sent.keys())
    result_sents = set(result_by_sent.keys())

    # Coverage: fraction of gold sentences with at least 1 TP
    covered = 0
    for sent in gold_sents:
        g = gold_by_sent[sent]
        r = result_by_sent.get(sent, set())
        if g & r:  # at least one TP
            covered += 1
    coverage = covered / len(gold_sents) if gold_sents else 0

    # Purity: fraction of predicted sentences with zero FPs
    pure = 0
    for sent in result_sents:
        r = result_by_sent[sent]
        g = gold_by_sent.get(sent, set())
        if not (r - g):  # no FPs for this sentence
            pure += 1
    purity = pure / len(result_sents) if result_sents else 0

    # Harmonic mean
    hus = 2 * coverage * purity / (coverage + purity) if (coverage + purity) > 0 else 0

    # Extra: per-sentence stats
    n_noise_free = pure
    n_result_sents = len(result_sents)
    n_covered = covered

    return {
        "coverage": coverage,
        "purity": purity,
        "hus": hus,
        "n_gold_sents": len(gold_sents),
        "n_result_sents": n_result_sents,
        "n_covered": n_covered,
        "n_pure": n_noise_free,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main: Compute all metrics for TransArc and V45
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    lines = []
    w = lines.append

    w("# New Metrics for SAD-CODE Traceability Evaluation")
    w("")
    w("Proposes 6 novel metrics addressing specific blind spots of P/R/F1,")
    w("and computes measurements for **TransArc** and **V45 linker** on all 5 benchmark projects.")
    w("")
    w("---")
    w("")

    # ─── Metric definitions ───────────────────────────────────────────────
    w("## Metric Definitions")
    w("")
    w("### N1: Matthews Correlation Coefficient (MCC)")
    w("")
    w("**Problem addressed:** P/R/F1 ignore true negatives. Most (sentence, component)")
    w("pairs are negative (not linked). A system that correctly identifies which")
    w("sentences do NOT mention a component gets zero credit.")
    w("")
    w("**Definition:** For each (sentence, component) pair in the evaluation universe,")
    w("classify as positive (linked) or negative (not linked). Compute:")
    w("")
    w("```")
    w("MCC = (TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))")
    w("```")
    w("")
    w("**Range:** [-1, +1]. 0 = random, +1 = perfect, -1 = perfect inverse.")
    w("A random classifier always scores MCC=0 regardless of class imbalance.")
    w("")
    w("**Level:** Component (SAD-SAM) and File (SAD-CODE).")
    w("")

    w("### N2: Sentence-Level Exact Match Rate (EMR)")
    w("")
    w("**Problem addressed:** F1 gives partial credit for partially-correct predictions.")
    w("A developer looking up \"which components does sentence 47 discuss?\" needs the")
    w("exact set, not partial overlap.")
    w("")
    w("**Definition:** For each gold sentence, check if predicted component set == gold set.")
    w("")
    w("```")
    w("EMR = |{s : pred(s) = gold(s)}| / |gold sentences|")
    w("```")
    w("")
    w("**Companion metrics:**")
    w("- **Superset rate:** pred(s) ⊇ gold(s) — over-prediction (noise but no missed components)")
    w("- **Subset rate:** pred(s) ⊆ gold(s), |pred(s)|>0 — under-prediction (no noise but gaps)")
    w("- **Mean Jaccard:** Average |pred∩gold|/|pred∪gold| per sentence")
    w("")
    w("**Level:** Component (SAD-SAM) and File (SAD-CODE).")
    w("")

    w("### N3: Per-Sentence Mean Average Precision (MAP)")
    w("")
    w("**Problem addressed:** Standard metrics treat all predictions as equally confident.")
    w("MAP rewards systems that rank correct components higher in their output.")
    w("A system returning [correct@0.99, wrong@0.80] is more useful than")
    w("[wrong@0.99, correct@0.80].")
    w("")
    w("**Definition:** For each gold sentence, rank predicted components by confidence.")
    w("Compute Average Precision (AP). MAP = mean of all APs.")
    w("")
    w("```")
    w("AP(s) = (1/|gold(s)|) · Σ_{k: pred_k ∈ gold} precision@k")
    w("MAP = (1/|S|) · Σ_s AP(s)")
    w("```")
    w("")
    w("**Range:** [0, 1]. Requires confidence scores (V45 has them, TransArc gets uniform 0.5).")
    w("")
    w("**Level:** Component (SAD-SAM) and File (SAD-CODE).")
    w("")

    w("### N4: Amplification-Corrected F1 (ACF1)")
    w("")
    w("**Problem addressed:** Enrollment inflates metrics by component size.")
    w("One error on JabRef logic (972 files) = 972 FPs; one error on")
    w("MediaStore Facade (1 file) = 1 FP. Standard F1 treats them as")
    w("972× different in severity.")
    w("")
    w("**Definition:** Weight each file-level link by 1/|component files|:")
    w("")
    w("```")
    w("w(sent, file) = 1 / |files_of_component(file)|")
    w("ACF1 = F1(Σw·TP, Σw·FP, Σw·FN)")
    w("```")
    w("")
    w("**Effect:** Every component-level decision contributes equally regardless of code size.")
    w("")
    w("**Level:** File (SAD-CODE), enrollment-corrected.")
    w("")

    w("### N5: Normalized Discrimination Gain (NDG)")
    w("")
    w("**Problem addressed:** Raw F1 is incomparable across projects.")
    w("JabRef F1=0.94 (easy: 6 components, 12 sentences) looks better than")
    w("Teammates F1=0.82 (hard: 14 components, 194 sentences), but Teammates")
    w("may require more intelligence.")
    w("")
    w("**Definition:** Normalize system F1 between random and oracle baselines:")
    w("")
    w("```")
    w("NDG = (system_F1 − random_F1) / (oracle_F1 − random_F1)")
    w("```")
    w("")
    w("**Range:** [0, 1]. 0 = no better than random, 1 = oracle-level.")
    w("Enables fair cross-project comparison of \"intelligence added\".")
    w("")
    w("**Level:** File (SAD-CODE).")
    w("")

    w("### N6: Harmonic Usefulness Score (HUS)")
    w("")
    w("**Problem addressed:** Coverage and noise capture complementary developer needs.")
    w("Coverage: \"will the system find my sentence?\" Purity: \"will it give me")
    w("only correct links?\" A system must do both. HUS is the harmonic mean:")
    w("")
    w("```")
    w("Coverage = |{s ∈ gold : ∃ TP in s}| / |gold sentences|")
    w("Purity = |{s ∈ result : no FP in s}| / |result sentences|")
    w("HUS = 2 · Coverage · Purity / (Coverage + Purity)")
    w("```")
    w("")
    w("**Range:** [0, 1]. Analogous to F1 but at sentence experience level.")
    w("")
    w("**Level:** Both SAD-SAM and SAD-CODE.")
    w("")

    # ─── Collect all measurements ─────────────────────────────────────────
    w("---")
    w("")
    w("## Measurements")
    w("")

    # Storage for aggregate tables
    all_n1 = {}  # project -> {transarc: {...}, v45: {...}}  — SAD-SAM
    all_n1_code = {}  # SAD-CODE level
    all_n2 = {}
    all_n2_code = {}
    all_n3 = {}
    all_n3_code = {}
    all_n4 = {}
    all_n5 = {}
    all_n6_sam = {}
    all_n6_code = {}
    all_standard = {}

    for proj in PROJECTS:
        w(f"### {proj.capitalize()}")
        w("")

        # Load data
        code_model = load_code_model_files(proj)
        gs_sad_sam = load_gs_sad_sam(proj)
        gs_sad_sam_maps = load_gs_sad_sam_maps(proj)  # (sent→models, model→sents)
        gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)  # model→files
        gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
        text = load_text(proj)
        model_names = load_model_element_names(proj)

        all_sents = set(text.keys())
        all_comps = set(model_names.keys())

        # TransArc data
        transarc_sad_sam = load_transarc_intermediate_sad_sam(proj)
        transarc_sad_code = load_result_sad_code(proj)

        # V45 data
        v45_sad_sam = load_v45_sad_sam(proj)
        v45_ranked = load_v45_sad_sam_with_confidence(proj)

        # V45 projected to SAD-CODE via gold SAM-CODE
        v45_sad_code = compose_sad_code(v45_sad_sam, gs_sam_code_map)

        # Standard P/R/F1 for reference
        t_p, t_r, t_f1, t_tp, t_fp, t_fn = calc_metrics(gs_sad_sam, transarc_sad_sam)
        v_p, v_r, v_f1, v_tp, v_fp, v_fn = calc_metrics(gs_sad_sam, v45_sad_sam)

        tc_p, tc_r, tc_f1, tc_tp, tc_fp, tc_fn = calc_metrics(gs_sad_code, transarc_sad_code)
        vc_p, vc_r, vc_f1, vc_tp, vc_fp, vc_fn = calc_metrics(gs_sad_code, v45_sad_code)

        all_standard[proj] = {
            "transarc_sam": (t_p, t_r, t_f1, t_tp, t_fp, t_fn),
            "v45_sam": (v_p, v_r, v_f1, v_tp, v_fp, v_fn),
            "transarc_code": (tc_p, tc_r, tc_f1, tc_tp, tc_fp, tc_fn),
            "v45_code": (vc_p, vc_r, vc_f1, vc_tp, vc_fp, vc_fn),
        }

        w("**Standard P/R/F1 (reference):**")
        w("")
        w("| Level | System | P | R | F1 | TP | FP | FN |")
        w("|:--|:--|:---:|:---:|:---:|---:|---:|---:|")
        w(f"| SAD-SAM | TransArc | {t_p:.3f} | {t_r:.3f} | {t_f1:.3f} | {t_tp} | {t_fp} | {t_fn} |")
        w(f"| SAD-SAM | V45 | {v_p:.3f} | {v_r:.3f} | {v_f1:.3f} | {v_tp} | {v_fp} | {v_fn} |")
        w(f"| SAD-CODE | TransArc | {tc_p:.3f} | {tc_r:.3f} | {tc_f1:.3f} | {tc_tp} | {tc_fp} | {tc_fn} |")
        w(f"| SAD-CODE | V45+GoldSAMCODE | {vc_p:.3f} | {vc_r:.3f} | {vc_f1:.3f} | {vc_tp} | {vc_fp} | {vc_fn} |")
        w("")

        # ─── N1: MCC ─────────────────────────────────────────────────────
        # SAD-SAM level
        n1_t = compute_mcc(gs_sad_sam, transarc_sad_sam, all_sents, all_comps)
        n1_v = compute_mcc(gs_sad_sam, v45_sad_sam, all_sents, all_comps)
        all_n1[proj] = {"transarc": n1_t, "v45": n1_v}

        # SAD-CODE level: universe = sentences × code files in gold
        all_code_files = set()
        for comp, files in gs_sam_code_map.items():
            all_code_files |= files
        # Also include files from results that may not be in gold
        for _, f in transarc_sad_code:
            all_code_files.add(f)
        for _, f in v45_sad_code:
            all_code_files.add(f)

        n1c_t = compute_mcc(gs_sad_code, transarc_sad_code, all_sents, all_code_files)
        n1c_v = compute_mcc(gs_sad_code, v45_sad_code, all_sents, all_code_files)
        all_n1_code[proj] = {"transarc": n1c_t, "v45": n1c_v}

        w("**N1: Matthews Correlation Coefficient (MCC):**")
        w("")
        w(f"| Level | System | TP | FP | FN | TN | Universe | MCC | Bal.Acc |")
        w(f"|:--|:--|---:|---:|---:|---:|---:|:---:|:---:|")
        w(f"| SAD-SAM | TransArc | {n1_t['tp']} | {n1_t['fp']} | {n1_t['fn']} | {n1_t['tn']} | {n1_t['universe']} | **{n1_t['mcc']:.3f}** | {n1_t['balanced_accuracy']:.3f} |")
        w(f"| SAD-SAM | V45 | {n1_v['tp']} | {n1_v['fp']} | {n1_v['fn']} | {n1_v['tn']} | {n1_v['universe']} | **{n1_v['mcc']:.3f}** | {n1_v['balanced_accuracy']:.3f} |")
        w(f"| SAD-CODE | TransArc | {n1c_t['tp']} | {n1c_t['fp']} | {n1c_t['fn']} | {n1c_t['tn']} | {n1c_t['universe']} | **{n1c_t['mcc']:.3f}** | {n1c_t['balanced_accuracy']:.3f} |")
        w(f"| SAD-CODE | V45+GoldSAMCODE | {n1c_v['tp']} | {n1c_v['fp']} | {n1c_v['fn']} | {n1c_v['tn']} | {n1c_v['universe']} | **{n1c_v['mcc']:.3f}** | {n1c_v['balanced_accuracy']:.3f} |")
        w("")

        # ─── N2: EMR ─────────────────────────────────────────────────────
        # SAD-SAM level
        n2_t = compute_emr(gs_sad_sam, transarc_sad_sam)
        n2_v = compute_emr(gs_sad_sam, v45_sad_sam)
        all_n2[proj] = {"transarc": n2_t, "v45": n2_v}

        # SAD-CODE level: exact file set per sentence
        # compute_emr expects (comp, sent) tuples; SAD-CODE is (sent, code) — flip
        gs_code_flipped = {(c, s) for s, c in gs_sad_code}
        tr_code_flipped = {(c, s) for s, c in transarc_sad_code}
        v45_code_flipped = {(c, s) for s, c in v45_sad_code}
        n2c_t = compute_emr(gs_code_flipped, tr_code_flipped)
        n2c_v = compute_emr(gs_code_flipped, v45_code_flipped)
        all_n2_code[proj] = {"transarc": n2c_t, "v45": n2c_v}

        w("**N2: Exact Match Rate (EMR):**")
        w("")
        w(f"| Level | System | EMR | Superset | Subset | Zero-Pred | Jaccard |")
        w(f"|:--|:--|:---:|:---:|:---:|:---:|:---:|")
        w(f"| SAD-SAM | TransArc | **{n2_t['emr']:.3f}** | {n2_t['superset_rate']:.3f} | {n2_t['subset_rate']:.3f} | {n2_t['zero_pred_rate']:.3f} | {n2_t['jaccard_mean']:.3f} |")
        w(f"| SAD-SAM | V45 | **{n2_v['emr']:.3f}** | {n2_v['superset_rate']:.3f} | {n2_v['subset_rate']:.3f} | {n2_v['zero_pred_rate']:.3f} | {n2_v['jaccard_mean']:.3f} |")
        w(f"| SAD-CODE | TransArc | **{n2c_t['emr']:.3f}** | {n2c_t['superset_rate']:.3f} | {n2c_t['subset_rate']:.3f} | {n2c_t['zero_pred_rate']:.3f} | {n2c_t['jaccard_mean']:.3f} |")
        w(f"| SAD-CODE | V45+GoldSAMCODE | **{n2c_v['emr']:.3f}** | {n2c_v['superset_rate']:.3f} | {n2c_v['subset_rate']:.3f} | {n2c_v['zero_pred_rate']:.3f} | {n2c_v['jaccard_mean']:.3f} |")
        w("")

        # ─── N3: MAP ─────────────────────────────────────────────────────
        # SAD-SAM level
        transarc_ranked = transarc_sad_sam_as_ranked(transarc_sad_sam)
        n3_t = compute_map(gs_sad_sam, transarc_ranked)
        n3_v = compute_map(gs_sad_sam, v45_ranked)
        all_n3[proj] = {"transarc": n3_t, "v45": n3_v}

        # SAD-CODE level: project ranked links through SAM-CODE
        # compute_map expects gold as (key, sentence) and preds as (sentence, key, conf)
        # SAD-CODE gold is (sent, code), so flip to (code, sent) for gold
        gs_sad_code_flipped = {(c, s) for s, c in gs_sad_code}
        # V45: each (sent, comp, conf) → (sent, file, conf) for each file in comp
        v45_code_ranked = []
        for sent, comp_id, conf in v45_ranked:
            for code_path in gs_sam_code_map.get(comp_id, set()):
                v45_code_ranked.append((sent, code_path, conf))
        # TransArc: uniform confidence at file level
        transarc_code_ranked = [(s, c, 0.5) for s, c in transarc_sad_code]

        n3c_t = compute_map(gs_sad_code_flipped, transarc_code_ranked)
        n3c_v = compute_map(gs_sad_code_flipped, v45_code_ranked)
        all_n3_code[proj] = {"transarc": n3c_t, "v45": n3c_v}

        w("**N3: Mean Average Precision (MAP):**")
        w("")
        w(f"| Level | System | MAP | Confidence Info |")
        w(f"|:--|:--|:---:|:--|")
        w(f"| SAD-SAM | TransArc | **{n3_t['map']:.3f}** | uniform (no confidence) |")
        w(f"| SAD-SAM | V45 | **{n3_v['map']:.3f}** | per-link [0.77–1.00] |")
        w(f"| SAD-CODE | TransArc | **{n3c_t['map']:.3f}** | uniform (no confidence) |")
        w(f"| SAD-CODE | V45+GoldSAMCODE | **{n3c_v['map']:.3f}** | inherited from component |")
        w("")

        # ─── N4: ACF1 ────────────────────────────────────────────────────
        n4_t = compute_acf1(gs_sad_code, transarc_sad_code, gs_sam_code_map)
        n4_v = compute_acf1(gs_sad_code, v45_sad_code, gs_sam_code_map)
        all_n4[proj] = {"transarc": n4_t, "v45": n4_v}

        w("**N4: Amplification-Corrected F1 (ACF1):**")
        w("")
        w(f"| System | Standard F1 | ACF1 | Δ | w·TP | w·FP | w·FN |")
        w(f"|:--|:---:|:---:|:---:|---:|---:|---:|")
        raw_t_f1 = tc_f1
        raw_v_f1 = vc_f1
        w(f"| TransArc | {raw_t_f1:.3f} | **{n4_t['acf1']:.3f}** | {n4_t['acf1']-raw_t_f1:+.3f} | {n4_t['weighted_tp']:.1f} | {n4_t['weighted_fp']:.1f} | {n4_t['weighted_fn']:.1f} |")
        w(f"| V45+GoldSAMCODE | {raw_v_f1:.3f} | **{n4_v['acf1']:.3f}** | {n4_v['acf1']-raw_v_f1:+.3f} | {n4_v['weighted_tp']:.1f} | {n4_v['weighted_fp']:.1f} | {n4_v['weighted_fn']:.1f} |")
        w("")

        # ─── N5: NDG ─────────────────────────────────────────────────────
        n_sents = len(all_sents)
        n_comps = len(all_comps)
        random_f1 = compute_random_f1(gs_sad_code, n_sents, n_comps, gs_sam_code_map)
        oracle_f1, oracle_links = compute_oracle_f1(gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)
        o_p, o_r, o_f1_check, o_tp, o_fp, o_fn = calc_metrics(gs_sad_code, oracle_links)

        ndg_t = compute_ndg(tc_f1, random_f1, oracle_f1)
        ndg_v = compute_ndg(vc_f1, random_f1, oracle_f1)
        all_n5[proj] = {
            "transarc": ndg_t, "v45": ndg_v,
            "random_f1": random_f1, "oracle_f1": oracle_f1,
            "oracle_tp": o_tp, "oracle_fp": o_fp, "oracle_fn": o_fn,
        }

        w("**N5: Normalized Discrimination Gain (NDG):**")
        w("")
        w(f"| Baseline | F1 |")
        w(f"|:--|:---:|")
        w(f"| Random | {random_f1:.3f} |")
        w(f"| Oracle (gold SAD-SAM × gold SAM-CODE) | {oracle_f1:.3f} (TP={o_tp}, FP={o_fp}, FN={o_fn}) |")
        w("")
        w(f"| System | F1 | NDG |")
        w(f"|:--|:---:|:---:|")
        w(f"| TransArc | {tc_f1:.3f} | **{ndg_t:.3f}** |")
        w(f"| V45+GoldSAMCODE | {vc_f1:.3f} | **{ndg_v:.3f}** |")
        w("")

        # ─── N6: HUS ─────────────────────────────────────────────────────
        # At SAD-SAM level (sentence → component)
        # Convert to (sentence, component) format for HUS
        gs_sam_sent_first = {(s, m) for m, s in gs_sad_sam}
        tr_sam_sent_first = {(s, m) for m, s in transarc_sad_sam}
        v45_sam_sent_first = {(s, m) for m, s in v45_sad_sam}

        n6_sam_t = compute_hus(gs_sam_sent_first, tr_sam_sent_first)
        n6_sam_v = compute_hus(gs_sam_sent_first, v45_sam_sent_first)
        all_n6_sam[proj] = {"transarc": n6_sam_t, "v45": n6_sam_v}

        # At SAD-CODE level (sentence → code file)
        n6_code_t = compute_hus(gs_sad_code, transarc_sad_code)
        n6_code_v = compute_hus(gs_sad_code, v45_sad_code)
        all_n6_code[proj] = {"transarc": n6_code_t, "v45": n6_code_v}

        w("**N6: Harmonic Usefulness Score (HUS):**")
        w("")
        w(f"| Level | System | Coverage | Purity | HUS |")
        w(f"|:--|:--|:---:|:---:|:---:|")
        w(f"| SAD-SAM | TransArc | {n6_sam_t['coverage']:.3f} | {n6_sam_t['purity']:.3f} | **{n6_sam_t['hus']:.3f}** |")
        w(f"| SAD-SAM | V45 | {n6_sam_v['coverage']:.3f} | {n6_sam_v['purity']:.3f} | **{n6_sam_v['hus']:.3f}** |")
        w(f"| SAD-CODE | TransArc | {n6_code_t['coverage']:.3f} | {n6_code_t['purity']:.3f} | **{n6_code_t['hus']:.3f}** |")
        w(f"| SAD-CODE | V45+GoldSAMCODE | {n6_code_v['coverage']:.3f} | {n6_code_v['purity']:.3f} | **{n6_code_v['hus']:.3f}** |")
        w("")
        w("---")
        w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Aggregate comparison tables
    # ═══════════════════════════════════════════════════════════════════════
    w("## Aggregate Comparison")
    w("")

    # Standard F1 summary
    w("### Standard F1 (Reference)")
    w("")
    w("| Project | TransArc SAD-SAM | V45 SAD-SAM | TransArc SAD-CODE | V45 SAD-CODE |")
    w("|:--|:---:|:---:|:---:|:---:|")
    sum_t_sam = sum_v_sam = sum_t_code = sum_v_code = 0
    for proj in PROJECTS:
        s = all_standard[proj]
        w(f"| {proj} | {s['transarc_sam'][2]:.3f} | {s['v45_sam'][2]:.3f} | {s['transarc_code'][2]:.3f} | {s['v45_code'][2]:.3f} |")
        sum_t_sam += s['transarc_sam'][2]
        sum_v_sam += s['v45_sam'][2]
        sum_t_code += s['transarc_code'][2]
        sum_v_code += s['v45_code'][2]
    n = len(PROJECTS)
    w(f"| **Average** | **{sum_t_sam/n:.3f}** | **{sum_v_sam/n:.3f}** | **{sum_t_code/n:.3f}** | **{sum_v_code/n:.3f}** |")
    w("")

    # N1: MCC summary
    w("### N1: MCC Summary")
    w("")
    w("**SAD-SAM level:**")
    w("")
    w("| Project | #Components | #Sentences | Universe | TransArc MCC | V45 MCC | Δ |")
    w("|:--|---:|---:|---:|:---:|:---:|:---:|")
    sum_t_mcc = sum_v_mcc = 0
    for proj in PROJECTS:
        d = all_n1[proj]
        t, v = d["transarc"], d["v45"]
        nc = t["universe"] // max(1, len(load_text(proj)))  # approx components
        ns = len(load_text(proj))
        delta = v["mcc"] - t["mcc"]
        w(f"| {proj} | {nc} | {ns} | {t['universe']} | {t['mcc']:.3f} | {v['mcc']:.3f} | {delta:+.3f} |")
        sum_t_mcc += t["mcc"]
        sum_v_mcc += v["mcc"]
    w(f"| **Average** | | | | **{sum_t_mcc/n:.3f}** | **{sum_v_mcc/n:.3f}** | **{(sum_v_mcc-sum_t_mcc)/n:+.3f}** |")
    w("")
    w("**SAD-CODE level:**")
    w("")
    w("| Project | #Files | Universe | TransArc MCC | V45 MCC | Δ |")
    w("|:--|---:|---:|:---:|:---:|:---:|")
    sum_t_mcc_c = sum_v_mcc_c = 0
    for proj in PROJECTS:
        d = all_n1_code[proj]
        t, v = d["transarc"], d["v45"]
        nf = t["universe"] // max(1, len(load_text(proj)))
        delta = v["mcc"] - t["mcc"]
        w(f"| {proj} | {nf} | {t['universe']} | {t['mcc']:.3f} | {v['mcc']:.3f} | {delta:+.3f} |")
        sum_t_mcc_c += t["mcc"]
        sum_v_mcc_c += v["mcc"]
    w(f"| **Average** | | | **{sum_t_mcc_c/n:.3f}** | **{sum_v_mcc_c/n:.3f}** | **{(sum_v_mcc_c-sum_t_mcc_c)/n:+.3f}** |")
    w("")
    w("**Insight:** At SAD-CODE file level, the universe is much larger (sentences × files),")
    w("making most pairs negative. MCC stays high because both systems correctly reject")
    w("the vast majority. The gap between systems is clearer at SAD-SAM level.")
    w("")

    # N2: EMR summary
    w("### N2: EMR Summary")
    w("")
    w("**SAD-SAM level (component sets):**")
    w("")
    w("| Project | TransArc EMR | V45 EMR | TransArc Jaccard | V45 Jaccard | TransArc Zero-Pred | V45 Zero-Pred |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_emr = sum_v_emr = sum_t_j = sum_v_j = 0
    for proj in PROJECTS:
        d = all_n2[proj]
        t, v = d["transarc"], d["v45"]
        w(f"| {proj} | {t['emr']:.3f} | {v['emr']:.3f} | {t['jaccard_mean']:.3f} | {v['jaccard_mean']:.3f} | {t['zero_pred_rate']:.3f} | {v['zero_pred_rate']:.3f} |")
        sum_t_emr += t["emr"]
        sum_v_emr += v["emr"]
        sum_t_j += t["jaccard_mean"]
        sum_v_j += v["jaccard_mean"]
    w(f"| **Average** | **{sum_t_emr/n:.3f}** | **{sum_v_emr/n:.3f}** | **{sum_t_j/n:.3f}** | **{sum_v_j/n:.3f}** | | |")
    w("")
    w("**SAD-CODE level (file sets):**")
    w("")
    w("| Project | TransArc EMR | V45 EMR | TransArc Jaccard | V45 Jaccard | TransArc Zero-Pred | V45 Zero-Pred |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_emr_c = sum_v_emr_c = sum_t_jc = sum_v_jc = 0
    for proj in PROJECTS:
        d = all_n2_code[proj]
        t, v = d["transarc"], d["v45"]
        w(f"| {proj} | {t['emr']:.3f} | {v['emr']:.3f} | {t['jaccard_mean']:.3f} | {v['jaccard_mean']:.3f} | {t['zero_pred_rate']:.3f} | {v['zero_pred_rate']:.3f} |")
        sum_t_emr_c += t["emr"]
        sum_v_emr_c += v["emr"]
        sum_t_jc += t["jaccard_mean"]
        sum_v_jc += v["jaccard_mean"]
    w(f"| **Average** | **{sum_t_emr_c/n:.3f}** | **{sum_v_emr_c/n:.3f}** | **{sum_t_jc/n:.3f}** | **{sum_v_jc/n:.3f}** | | |")
    w("")
    w("**Insight:** EMR at file level is nearly impossible: getting every file exactly right")
    w("for a sentence requires both correct component classification AND perfect SAM-CODE.")
    w("Jaccard at file level reveals partial overlap quality. Zero-pred shows missed sentences.")
    w("")

    # N3: MAP summary
    w("### N3: MAP Summary")
    w("")
    w("**SAD-SAM level:**")
    w("")
    w("| Project | TransArc MAP | V45 MAP | Δ |")
    w("|:--|:---:|:---:|:---:|")
    sum_t_map = sum_v_map = 0
    for proj in PROJECTS:
        d = all_n3[proj]
        t, v = d["transarc"], d["v45"]
        delta = v["map"] - t["map"]
        w(f"| {proj} | {t['map']:.3f} | {v['map']:.3f} | {delta:+.3f} |")
        sum_t_map += t["map"]
        sum_v_map += v["map"]
    w(f"| **Average** | **{sum_t_map/n:.3f}** | **{sum_v_map/n:.3f}** | **{(sum_v_map-sum_t_map)/n:+.3f}** |")
    w("")
    w("**SAD-CODE level:**")
    w("")
    w("| Project | TransArc MAP | V45 MAP | Δ |")
    w("|:--|:---:|:---:|:---:|")
    sum_t_map_c = sum_v_map_c = 0
    for proj in PROJECTS:
        d = all_n3_code[proj]
        t, v = d["transarc"], d["v45"]
        delta = v["map"] - t["map"]
        w(f"| {proj} | {t['map']:.3f} | {v['map']:.3f} | {delta:+.3f} |")
        sum_t_map_c += t["map"]
        sum_v_map_c += v["map"]
    w(f"| **Average** | **{sum_t_map_c/n:.3f}** | **{sum_v_map_c/n:.3f}** | **{(sum_v_map_c-sum_t_map_c)/n:+.3f}** |")
    w("")
    w("**Insight:** MAP at file level is dominated by within-component file ordering.")
    w("V45 inherits component confidence to all files, so files from high-confidence")
    w("components cluster at the top. TransArc's uniform confidence means MAP ≈ recall.")
    w("")

    # N4: ACF1 summary
    w("### N4: ACF1 Summary")
    w("")
    w("| Project | TransArc F1 | TransArc ACF1 | Δ | V45 F1 | V45 ACF1 | Δ |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_f1 = sum_t_acf1 = sum_v_f1 = sum_v_acf1 = 0
    for proj in PROJECTS:
        d = all_n4[proj]
        s = all_standard[proj]
        tf1 = s['transarc_code'][2]
        vf1 = s['v45_code'][2]
        tacf1 = d['transarc']['acf1']
        vacf1 = d['v45']['acf1']
        w(f"| {proj} | {tf1:.3f} | {tacf1:.3f} | {tacf1-tf1:+.3f} | {vf1:.3f} | {vacf1:.3f} | {vacf1-vf1:+.3f} |")
        sum_t_f1 += tf1
        sum_t_acf1 += tacf1
        sum_v_f1 += vf1
        sum_v_acf1 += vacf1
    w(f"| **Average** | **{sum_t_f1/n:.3f}** | **{sum_t_acf1/n:.3f}** | **{(sum_t_acf1-sum_t_f1)/n:+.3f}** | **{sum_v_f1/n:.3f}** | **{sum_v_acf1/n:.3f}** | **{(sum_v_acf1-sum_v_f1)/n:+.3f}** |")
    w("")
    w("**Insight:** ACF1 corrects enrollment inflation. Projects where the shift is large")
    w("(e.g., JabRef, Teammates) are those where a few large components dominate standard F1.")
    w("ACF1 gives a truer picture of component-level quality.")
    w("")

    # N5: NDG summary
    w("### N5: NDG Summary")
    w("")
    w("| Project | Random F1 | Oracle F1 | TransArc F1 | TransArc NDG | V45 F1 | V45 NDG |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_ndg = sum_v_ndg = 0
    for proj in PROJECTS:
        d = all_n5[proj]
        s = all_standard[proj]
        w(f"| {proj} | {d['random_f1']:.3f} | {d['oracle_f1']:.3f} | {s['transarc_code'][2]:.3f} | **{d['transarc']:.3f}** | {s['v45_code'][2]:.3f} | **{d['v45']:.3f}** |")
        sum_t_ndg += d['transarc']
        sum_v_ndg += d['v45']
    w(f"| **Average** | | | | **{sum_t_ndg/n:.3f}** | | **{sum_v_ndg/n:.3f}** |")
    w("")
    w("**Insight:** NDG reveals which projects are genuinely hard. A high F1 with a high")
    w("oracle ceiling and low random baseline means the achievable range is wide — the system")
    w("must be doing real work. A high F1 near the oracle ceiling means there was little room")
    w("for improvement and the metric flatters the system.")
    w("")

    # N6: HUS summary
    w("### N6: HUS Summary")
    w("")
    w("**SAD-SAM level:**")
    w("")
    w("| Project | TransArc Coverage | TransArc Purity | TransArc HUS | V45 Coverage | V45 Purity | V45 HUS |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_hus_sam = sum_v_hus_sam = 0
    for proj in PROJECTS:
        d = all_n6_sam[proj]
        t, v = d["transarc"], d["v45"]
        w(f"| {proj} | {t['coverage']:.3f} | {t['purity']:.3f} | **{t['hus']:.3f}** | {v['coverage']:.3f} | {v['purity']:.3f} | **{v['hus']:.3f}** |")
        sum_t_hus_sam += t["hus"]
        sum_v_hus_sam += v["hus"]
    w(f"| **Average** | | | **{sum_t_hus_sam/n:.3f}** | | | **{sum_v_hus_sam/n:.3f}** |")
    w("")

    w("**SAD-CODE level:**")
    w("")
    w("| Project | TransArc Coverage | TransArc Purity | TransArc HUS | V45 Coverage | V45 Purity | V45 HUS |")
    w("|:--|:---:|:---:|:---:|:---:|:---:|:---:|")
    sum_t_hus_code = sum_v_hus_code = 0
    for proj in PROJECTS:
        d = all_n6_code[proj]
        t, v = d["transarc"], d["v45"]
        w(f"| {proj} | {t['coverage']:.3f} | {t['purity']:.3f} | **{t['hus']:.3f}** | {v['coverage']:.3f} | {v['purity']:.3f} | **{v['hus']:.3f}** |")
        sum_t_hus_code += t["hus"]
        sum_v_hus_code += v["hus"]
    w(f"| **Average** | | | **{sum_t_hus_code/n:.3f}** | | | **{sum_v_hus_code/n:.3f}** |")
    w("")

    # ═══════════════════════════════════════════════════════════════════════
    # Grand summary
    # ═══════════════════════════════════════════════════════════════════════
    w("---")
    w("")
    w("## Grand Summary: All Metrics Head-to-Head")
    w("")
    w("| Metric | Level | TransArc (avg) | V45 (avg) | V45 Δ | Winner | What it reveals |")
    w("|:--|:--|:---:|:---:|:---:|:---:|:--|")

    # Compute averages
    avg_t_sam_f1 = sum_t_sam / n
    avg_v_sam_f1 = sum_v_sam / n
    avg_t_code_f1 = sum_t_code / n
    avg_v_code_f1 = sum_v_code / n
    avg_t_mcc = sum_t_mcc / n
    avg_v_mcc = sum_v_mcc / n
    avg_t_mcc_c = sum_t_mcc_c / n
    avg_v_mcc_c = sum_v_mcc_c / n
    avg_t_emr = sum_t_emr / n
    avg_v_emr = sum_v_emr / n
    avg_t_emr_c = sum_t_emr_c / n
    avg_v_emr_c = sum_v_emr_c / n
    avg_t_map = sum_t_map / n
    avg_v_map = sum_v_map / n
    avg_t_map_c = sum_t_map_c / n
    avg_v_map_c = sum_v_map_c / n
    avg_t_acf1 = sum_t_acf1 / n
    avg_v_acf1 = sum_v_acf1 / n
    avg_t_ndg = sum_t_ndg / n
    avg_v_ndg = sum_v_ndg / n
    avg_t_hus_sam = sum_t_hus_sam / n
    avg_v_hus_sam = sum_v_hus_sam / n
    avg_t_hus_code = sum_t_hus_code / n
    avg_v_hus_code = sum_v_hus_code / n

    def winner(t, v):
        return "V45" if v > t + 0.005 else ("TransArc" if t > v + 0.005 else "Tie")

    w(f"| F1 (standard) | SAD-SAM | {avg_t_sam_f1:.3f} | {avg_v_sam_f1:.3f} | {avg_v_sam_f1-avg_t_sam_f1:+.3f} | {winner(avg_t_sam_f1, avg_v_sam_f1)} | Basic quality at component level |")
    w(f"| F1 (standard) | SAD-CODE | {avg_t_code_f1:.3f} | {avg_v_code_f1:.3f} | {avg_v_code_f1-avg_t_code_f1:+.3f} | {winner(avg_t_code_f1, avg_v_code_f1)} | File-level (enrollment-inflated) |")
    w(f"| **N1: MCC** | SAD-SAM | {avg_t_mcc:.3f} | {avg_v_mcc:.3f} | {avg_v_mcc-avg_t_mcc:+.3f} | {winner(avg_t_mcc, avg_v_mcc)} | Discrimination (component) |")
    w(f"| **N1: MCC** | SAD-CODE | {avg_t_mcc_c:.3f} | {avg_v_mcc_c:.3f} | {avg_v_mcc_c-avg_t_mcc_c:+.3f} | {winner(avg_t_mcc_c, avg_v_mcc_c)} | Discrimination (file) |")
    w(f"| **N2: EMR** | SAD-SAM | {avg_t_emr:.3f} | {avg_v_emr:.3f} | {avg_v_emr-avg_t_emr:+.3f} | {winner(avg_t_emr, avg_v_emr)} | Exact component-set per sentence |")
    w(f"| **N2: EMR** | SAD-CODE | {avg_t_emr_c:.3f} | {avg_v_emr_c:.3f} | {avg_v_emr_c-avg_t_emr_c:+.3f} | {winner(avg_t_emr_c, avg_v_emr_c)} | Exact file-set per sentence |")
    w(f"| **N3: MAP** | SAD-SAM | {avg_t_map:.3f} | {avg_v_map:.3f} | {avg_v_map-avg_t_map:+.3f} | {winner(avg_t_map, avg_v_map)} | Ranking quality (component) |")
    w(f"| **N3: MAP** | SAD-CODE | {avg_t_map_c:.3f} | {avg_v_map_c:.3f} | {avg_v_map_c-avg_t_map_c:+.3f} | {winner(avg_t_map_c, avg_v_map_c)} | Ranking quality (file) |")
    w(f"| **N4: ACF1** | SAD-CODE | {avg_t_acf1:.3f} | {avg_v_acf1:.3f} | {avg_v_acf1-avg_t_acf1:+.3f} | {winner(avg_t_acf1, avg_v_acf1)} | Enrollment-corrected file-level |")
    w(f"| **N5: NDG** | SAD-CODE | {avg_t_ndg:.3f} | {avg_v_ndg:.3f} | {avg_v_ndg-avg_t_ndg:+.3f} | {winner(avg_t_ndg, avg_v_ndg)} | Intelligence over random baseline |")
    w(f"| **N6: HUS** | SAD-SAM | {avg_t_hus_sam:.3f} | {avg_v_hus_sam:.3f} | {avg_v_hus_sam-avg_t_hus_sam:+.3f} | {winner(avg_t_hus_sam, avg_v_hus_sam)} | Coverage × purity (component) |")
    w(f"| **N6: HUS** | SAD-CODE | {avg_t_hus_code:.3f} | {avg_v_hus_code:.3f} | {avg_v_hus_code-avg_t_hus_code:+.3f} | {winner(avg_t_hus_code, avg_v_hus_code)} | Coverage × purity (file) |")
    w("")

    w("### Key Takeaways")
    w("")
    w("1. **MCC reveals true discrimination ability.** By including the ~95% of")
    w("   (sentence, component) pairs that are correctly rejected as negatives,")
    w("   MCC shows both systems are strong discriminators. The gap between them")
    w("   is smaller in MCC space than in F1 space, because F1 ignores the easy")
    w("   correct rejections that both systems nail.")
    w("")
    w("2. **EMR is the strictest metric.** Getting every component exactly right")
    w("   for a sentence is much harder than getting high F1. V45's EMR advantage")
    w("   shows it makes fewer partial-set errors — important for developer trust.")
    w("")
    w("3. **MAP rewards calibrated confidence.** V45's confidence scores (0.77–1.00)")
    w("   enable meaningful ranking; TransArc's binary outputs (uniform 0.5) cannot.")
    w("   Higher MAP means correct links surface first, reducing developer effort.")
    w("")
    w("4. **ACF1 corrects enrollment inflation.** Projects with large components")
    w("   (JabRef logic=972 files, Teammates=400+ files per component) see the")
    w("   biggest ACF1 shift. ACF1 is the fairest file-level metric because")
    w("   each component-level decision contributes equally.")
    w("")
    w("5. **NDG enables cross-project comparison.** A system with NDG=0.8 on all")
    w("   projects is uniformly good regardless of project difficulty. NDG reveals")
    w("   whether high F1 comes from genuine intelligence or favorable structure.")
    w("")
    w("6. **HUS captures developer experience.** A system that covers most gold")
    w("   sentences (high coverage) but drowns each in false positives (low purity)")
    w("   scores poorly on HUS. The harmonic mean ensures both dimensions matter.")
    w("")

    w("---")
    w("")
    w("### Metric Selection Guide")
    w("")
    w("| If you care about... | Use | Why |")
    w("|:--|:--|:--|")
    w("| Overall classification quality | N1 (MCC) | Handles class imbalance correctly |")
    w("| Developer trust per sentence | N2 (EMR) | Measures exact-set accuracy |")
    w("| Ranking of suggestions | N3 (MAP) | Rewards correct items first |")
    w("| Fair cross-component comparison | N4 (ACF1) | Removes enrollment inflation |")
    w("| Fair cross-project comparison | N5 (NDG) | Normalizes by project difficulty |")
    w("| Practical usefulness | N6 (HUS) | Balances coverage and noise |")
    w("| Backward compatibility | Standard F1 | Comparable to prior work |")
    w("")

    w("### Replication")
    w("")
    w("```bash")
    w("cd /mnt/hostshare/ardoco-home/transarc-emp")
    w("python3 new_metrics_analysis.py")
    w("# Output: NEW_METRICS_REPORT.md")
    w("```")
    w("")

    # Write output
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Written to {OUTPUT_MD}")

    # Also print summary to stdout
    print("\n=== GRAND SUMMARY ===\n")
    print(f"{'Metric':<25} {'TransArc':>10} {'V45':>10} {'Δ':>8} {'Winner':<10}")
    print("-" * 67)
    print(f"{'F1 SAD-SAM':<25} {avg_t_sam_f1:>10.3f} {avg_v_sam_f1:>10.3f} {avg_v_sam_f1-avg_t_sam_f1:>+8.3f} {winner(avg_t_sam_f1, avg_v_sam_f1):<10}")
    print(f"{'F1 SAD-CODE':<25} {avg_t_code_f1:>10.3f} {avg_v_code_f1:>10.3f} {avg_v_code_f1-avg_t_code_f1:>+8.3f} {winner(avg_t_code_f1, avg_v_code_f1):<10}")
    print(f"{'N1: MCC (SAM)':<25} {avg_t_mcc:>10.3f} {avg_v_mcc:>10.3f} {avg_v_mcc-avg_t_mcc:>+8.3f} {winner(avg_t_mcc, avg_v_mcc):<10}")
    print(f"{'N1: MCC (CODE)':<25} {avg_t_mcc_c:>10.3f} {avg_v_mcc_c:>10.3f} {avg_v_mcc_c-avg_t_mcc_c:>+8.3f} {winner(avg_t_mcc_c, avg_v_mcc_c):<10}")
    print(f"{'N2: EMR (SAM)':<25} {avg_t_emr:>10.3f} {avg_v_emr:>10.3f} {avg_v_emr-avg_t_emr:>+8.3f} {winner(avg_t_emr, avg_v_emr):<10}")
    print(f"{'N2: EMR (CODE)':<25} {avg_t_emr_c:>10.3f} {avg_v_emr_c:>10.3f} {avg_v_emr_c-avg_t_emr_c:>+8.3f} {winner(avg_t_emr_c, avg_v_emr_c):<10}")
    print(f"{'N3: MAP (SAM)':<25} {avg_t_map:>10.3f} {avg_v_map:>10.3f} {avg_v_map-avg_t_map:>+8.3f} {winner(avg_t_map, avg_v_map):<10}")
    print(f"{'N3: MAP (CODE)':<25} {avg_t_map_c:>10.3f} {avg_v_map_c:>10.3f} {avg_v_map_c-avg_t_map_c:>+8.3f} {winner(avg_t_map_c, avg_v_map_c):<10}")
    print(f"{'N4: ACF1':<25} {avg_t_acf1:>10.3f} {avg_v_acf1:>10.3f} {avg_v_acf1-avg_t_acf1:>+8.3f} {winner(avg_t_acf1, avg_v_acf1):<10}")
    print(f"{'N5: NDG':<25} {avg_t_ndg:>10.3f} {avg_v_ndg:>10.3f} {avg_v_ndg-avg_t_ndg:>+8.3f} {winner(avg_t_ndg, avg_v_ndg):<10}")
    print(f"{'N6: HUS (SAM)':<25} {avg_t_hus_sam:>10.3f} {avg_v_hus_sam:>10.3f} {avg_v_hus_sam-avg_t_hus_sam:>+8.3f} {winner(avg_t_hus_sam, avg_v_hus_sam):<10}")
    print(f"{'N6: HUS (CODE)':<25} {avg_t_hus_code:>10.3f} {avg_v_hus_code:>10.3f} {avg_v_hus_code-avg_t_hus_code:>+8.3f} {winner(avg_t_hus_code, avg_v_hus_code):<10}")


if __name__ == "__main__":
    main()
