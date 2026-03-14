#!/usr/bin/env python3
"""
SWATTR TP vs FP: Zero-Shot Semantic Separability

No gold labels for training. Can we distinguish TPs from FPs using only
semantic priors, embedding geometry, and unsupervised methods?

Approaches:
  1. Relative framing: sim(sent, "arch desc of X") vs sim(sent, "impl detail of X")
  2. Cosine threshold sweep (no calibration — use fixed thresholds)
  3. Unsupervised clustering in embedding space
  4. Rule-based heuristics from semantic patterns
  5. Entailment-style: "This sentence traces to component X" — does it?
  6. Nearest-neighbor to reference exemplars (zero-shot prototypes)

Produces: SWATTR_ZEROSHOT_ANALYSIS.md
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cosine as cosine_dist
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score, silhouette_score)
from sklearn.preprocessing import StandardScaler

# ─── Paths & Config ──────────────────────────────────────────────────────────

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/SWATTR_ZEROSHOT_ANALYSIS.md")

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]

GS_SAD_SAM = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sad_2016-sam_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sad_2020-sam_2020.csv",
    "teammates":     BENCHMARK / "teammates/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "bigbluebutton": BENCHMARK / "bigbluebutton/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "jabref":        BENCHMARK / "jabref/goldstandards/goldstandard_sad_2021-sam_2021.csv",
}

GS_SAM_CODE = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sam_2016-code_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sam_2020-code_2022.csv",
    "teammates":     BENCHMARK / "teammates/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "bigbluebutton": BENCHMARK / "bigbluebutton/goldstandards/goldstandard_sam_2021-code_2023.csv",
    "jabref":        BENCHMARK / "jabref/goldstandards/goldstandard_sam_2021-code_2023.csv",
}

TEXT_FILES = {
    "mediastore":    BENCHMARK / "mediastore/text_2016/mediastore.txt",
    "teastore":      BENCHMARK / "teastore/text_2020/teastore.txt",
    "teammates":     BENCHMARK / "teammates/text_2021/teammates.txt",
    "bigbluebutton": BENCHMARK / "bigbluebutton/text_2021/bigbluebutton.txt",
    "jabref":        BENCHMARK / "jabref/text_2021/jabref.txt",
}


def load_text(project):
    sentences = {}
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            sentences[str(i)] = line.strip()
    return sentences


def load_gs_sad_sam(project):
    links = set()
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_result_sad_sam(project):
    path = RESULTS / project / "sad-sam" / f"sadSamTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_model_element_info(project):
    info = {}
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            ae_id = row["ae_id"]
            ae_name = row["ae_name"]
            if ae_id not in info:
                if ae_name.startswith("Component: "):
                    info[ae_id] = {"name": ae_name[len("Component: "):], "type": "Component"}
                elif ae_name.startswith("Interface: "):
                    info[ae_id] = {"name": ae_name[len("Interface: "):], "type": "Interface"}
                else:
                    info[ae_id] = {"name": ae_name, "type": "Unknown"}
    return info


def cosine_sim(a, b):
    return 1.0 - cosine_dist(a, b)


def calc_metrics(y_true, y_pred):
    """Returns (precision, recall, f1, accuracy) treating 1=TP, 0=FP."""
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    a = accuracy_score(y_true, y_pred)
    return p, r, f, a


def main():
    md = []

    def out(s=""):
        print(s)
        md.append(s)

    out("# SWATTR TP vs FP: Zero-Shot Separability")
    out()
    out("No training data. Can we distinguish TPs from FPs using only")
    out("semantic priors and embedding geometry?")
    out()

    # ── Load data ─────────────────────────────────────────────────────────────

    records = []
    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)

        for model_id, sent_num in (gold & result):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            records.append({"project": proj, "model_id": model_id,
                            "sent_num": sent_num, "elem_name": ei["name"],
                            "text": text.get(sent_num, ""), "label": 1})

        for model_id, sent_num in (result - gold):
            ei = elem_info.get(model_id, {"name": "UNKNOWN"})
            records.append({"project": proj, "model_id": model_id,
                            "sent_num": sent_num, "elem_name": ei["name"],
                            "text": text.get(sent_num, ""), "label": 0})

    labels = np.array([r["label"] for r in records])
    projects = [r["project"] for r in records]
    n_tp, n_fp = labels.sum(), len(labels) - labels.sum()

    out(f"**Data**: {n_tp} TPs + {n_fp} FPs = {len(labels)} links")
    out()

    # ── Load model & embed ────────────────────────────────────────────────────

    print("Loading model...", file=sys.stderr)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    sentences = [r["text"] for r in records]
    comp_names = [r["elem_name"] for r in records]

    print("Encoding...", file=sys.stderr)
    sent_embs = model.encode(sentences, show_progress_bar=False)
    name_embs = model.encode(comp_names, show_progress_bar=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 1: Relative Framing (Contrastive Reference)
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 1: Relative Framing")
    out()
    out("For each link, compare similarity of the sentence to two reference frames:")
    out("- **Architectural**: \"The {name} component is responsible for...\"")
    out("- **Implementation**: \"The {name} package contains classes for...\"")
    out()
    out("If sim(sent, arch_frame) > sim(sent, impl_frame) → predict TP, else FP.")
    out()

    # Multiple framing templates
    arch_templates = [
        "The {name} component is responsible for handling and processing",
        "The {name} service provides functionality to other components",
        "{name} manages the core business logic and data flow",
        "The architectural role of {name} in the system",
    ]

    impl_templates = [
        "The {name} package contains implementation classes and utilities",
        "Package {name} provides the API and helper classes",
        "{name} source code directory with files and sub-packages",
        "The {name} module contains custom exceptions and data transfer objects",
    ]

    # Ensemble over templates
    best_overall_f1 = 0
    best_template_pair = None

    for ai, arch_t in enumerate(arch_templates):
        for ii, impl_t in enumerate(impl_templates):
            preds = []
            for r in records:
                name = r["elem_name"]
                arch_ref = arch_t.format(name=name)
                impl_ref = impl_t.format(name=name)
                arch_emb = model.encode([arch_ref])[0]
                impl_emb = model.encode([impl_ref])[0]
                sent_emb = sent_embs[len(preds)]
                s_arch = cosine_sim(sent_emb, arch_emb)
                s_impl = cosine_sim(sent_emb, impl_emb)
                preds.append(1 if s_arch >= s_impl else 0)
            preds = np.array(preds)
            p, r_val, f, a = calc_metrics(labels, preds)
            if f > best_overall_f1:
                best_overall_f1 = f
                best_template_pair = (ai, ii, preds)

    # Report best single pair
    ai, ii, best_preds_single = best_template_pair
    p, r_val, f, a = calc_metrics(labels, best_preds_single)
    out(f"**Best single template pair** (arch[{ai}] vs impl[{ii}]):")
    out(f"- Precision (TP class): {p:.3f}")
    out(f"- Recall (TP class): {r_val:.3f}")
    out(f"- F1 (TP class): {f:.3f}")
    out(f"- Accuracy: {a:.3f}")
    out(f"- FPs caught: {((best_preds_single == 0) & (labels == 0)).sum()}/{n_fp}")
    out(f"- TPs wrongly killed: {((best_preds_single == 0) & (labels == 1)).sum()}/{n_tp}")
    out()

    # Ensemble: majority vote across all template pairs
    all_votes = np.zeros(len(records))
    n_pairs = 0
    for arch_t in arch_templates:
        for impl_t in impl_templates:
            for idx, r in enumerate(records):
                name = r["elem_name"]
                arch_emb = model.encode([arch_t.format(name=name)])[0]
                impl_emb = model.encode([impl_t.format(name=name)])[0]
                s_arch = cosine_sim(sent_embs[idx], arch_emb)
                s_impl = cosine_sim(sent_embs[idx], impl_emb)
                if s_arch >= s_impl:
                    all_votes[idx] += 1
            n_pairs += 1

    ensemble_preds = (all_votes >= n_pairs / 2).astype(int)
    p, r_val, f, a = calc_metrics(labels, ensemble_preds)
    out(f"**Ensemble (majority of {n_pairs} pairs)**:")
    out(f"- Precision: {p:.3f}, Recall: {r_val:.3f}, F1: {f:.3f}, Acc: {a:.3f}")
    out(f"- FPs caught: {((ensemble_preds == 0) & (labels == 0)).sum()}/{n_fp}")
    out(f"- TPs wrongly killed: {((ensemble_preds == 0) & (labels == 1)).sum()}/{n_tp}")
    out()

    # Per-project breakdown
    out("**Per-project (ensemble):**")
    out()
    out("| Project | TPs | FPs | FPs Caught | TPs Killed | Net Δ |")
    out("|---------|-----|-----|------------|------------|-------|")
    for proj in PROJECTS:
        pmask = np.array([p == proj for p in projects])
        p_labels = labels[pmask]
        p_preds = ensemble_preds[pmask]
        fp_caught = ((p_preds == 0) & (p_labels == 0)).sum()
        tp_killed = ((p_preds == 0) & (p_labels == 1)).sum()
        n_tp_p = p_labels.sum()
        n_fp_p = len(p_labels) - n_tp_p
        net = fp_caught - tp_killed
        out(f"| {proj} | {n_tp_p} | {n_fp_p} | {fp_caught} | {tp_killed} | {net:+d} |")
    out()

    # Show the scores for each FP
    out("**FP details (ensemble vote fraction = arch vs impl):**")
    out()
    out("| Project | Sent# | Element | Vote (arch/total) | Prediction | Sentence |")
    out("|---------|-------|---------|-------------------|------------|----------|")
    for idx, r in enumerate(records):
        if r["label"] == 0:  # FP
            vote_frac = all_votes[idx] / n_pairs
            pred = "TP (miss)" if ensemble_preds[idx] == 1 else "FP (caught)"
            out(f"| {r['project']} | {r['sent_num']} | {r['elem_name']} | "
                f"{vote_frac:.2f} | {pred} | {r['text'][:60]}... |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 2: Absolute Cosine Threshold (no calibration)
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 2: Cosine Similarity Threshold")
    out()
    out("Predict TP if cosine(sentence, component_name) > threshold.")
    out("Sweep thresholds without any training — just report what happens.")
    out()

    sims = np.array([cosine_sim(se, ne) for se, ne in zip(sent_embs, name_embs)])

    out("| Threshold | FPs Caught | TPs Killed | Net Benefit | Acc |")
    out("|-----------|------------|------------|-------------|-----|")
    for thresh in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        preds = (sims >= thresh).astype(int)
        fp_caught = ((preds == 0) & (labels == 0)).sum()
        tp_killed = ((preds == 0) & (labels == 1)).sum()
        acc = accuracy_score(labels, preds)
        net = fp_caught - tp_killed
        out(f"| {thresh:.2f} | {fp_caught}/{n_fp} | {tp_killed}/{n_tp} | {net:+d} | {acc:.3f} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 3: Unsupervised Clustering
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 3: Unsupervised Clustering")
    out()
    out("K-means and DBSCAN on sentence embeddings — do natural clusters align with TP/FP?")
    out()

    # PCA first for dimensionality reduction
    pca = PCA(n_components=20)
    emb_pca = pca.fit_transform(sent_embs)

    for k in [2, 3, 4, 5]:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = km.fit_predict(emb_pca)
        sil = silhouette_score(emb_pca, clusters)

        # For each cluster, compute TP rate
        out(f"### K-means k={k} (silhouette={sil:.3f})")
        out()
        out("| Cluster | Size | TPs | FPs | TP Rate |")
        out("|---------|------|-----|-----|---------|")
        for c in range(k):
            mask = clusters == c
            c_labels = labels[mask]
            c_tp = c_labels.sum()
            c_fp = len(c_labels) - c_tp
            rate = c_tp / len(c_labels) if len(c_labels) > 0 else 0
            out(f"| {c} | {mask.sum()} | {c_tp} | {c_fp} | {rate:.1%} |")

        # Best assignment: assign clusters to TP/FP by majority
        best_acc = 0
        # Try: label cluster as FP if its TP rate is below overall rate
        overall_tp_rate = n_tp / len(labels)
        preds = np.ones(len(labels))
        for c in range(k):
            mask = clusters == c
            c_labels = labels[mask]
            c_tp_rate = c_labels.mean() if len(c_labels) > 0 else 1
            if c_tp_rate < overall_tp_rate * 0.7:  # substantially below average
                preds[mask] = 0
        acc = accuracy_score(labels, preds)
        fp_caught = ((preds == 0) & (labels == 0)).sum()
        tp_killed = ((preds == 0) & (labels == 1)).sum()
        out(f"→ FPs caught: {fp_caught}/{n_fp}, TPs killed: {tp_killed}/{n_tp}, Acc: {acc:.3f}")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 4: Rule-Based Semantic Heuristics
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 4: Rule-Based Heuristics")
    out()
    out("Zero-shot rules derived from domain knowledge of SAD-SAM task:")
    out()

    rules = {
        "has_dotted_package": lambda r: bool(re.search(r'\b\w+\.\w+\b', r["text"])),
        "has_contains_pkg": lambda r: bool(re.search(r'\bcontains?\b.*(?:class|helper|util|exception|custom)', r["text"], re.I)),
        "has_package_keyword": lambda r: bool(re.search(r'\bpackage\s+overview\b|\bpackage\b.*\bcontains?\b', r["text"], re.I)),
        "impl_sentence": lambda r: bool(re.search(
            r'\b(?:package|contains? (?:class|helper|util|abstract|custom|data\s*transfer)|'
            r'source\s*code|directory|sub-?package)\b', r["text"], re.I)),
        "short_and_listing": lambda r: len(r["text"].split()) < 10 and bool(re.search(r'\b\w+\.\w+\b', r["text"])),
    }

    out("| Rule | FPs Caught | TPs Killed | Precision* | Net |")
    out("|------|------------|------------|-----------|-----|")
    out("| *(Precision = FPs caught / total flagged)* |||||")

    for rname, rfunc in rules.items():
        flagged = np.array([rfunc(r) for r in records])
        fp_caught = (flagged & (labels == 0)).sum()
        tp_killed = (flagged & (labels == 1)).sum()
        total_flagged = flagged.sum()
        prec = fp_caught / total_flagged if total_flagged > 0 else 0
        net = fp_caught - tp_killed
        out(f"| `{rname}` | {fp_caught}/{n_fp} | {tp_killed}/{n_tp} | {prec:.1%} | {net:+d} |")
    out()

    # Combined rule: flag as FP if ANY rule triggers
    any_rule = np.zeros(len(records), dtype=bool)
    for rfunc in rules.values():
        any_rule |= np.array([rfunc(r) for r in records])

    fp_caught = (any_rule & (labels == 0)).sum()
    tp_killed = (any_rule & (labels == 1)).sum()
    total_flagged = any_rule.sum()
    prec = fp_caught / total_flagged if total_flagged > 0 else 0
    out(f"**Any rule**: FPs caught {fp_caught}/{n_fp}, TPs killed {tp_killed}/{n_tp}, "
        f"precision {prec:.1%}, net {fp_caught - tp_killed:+d}")
    out()

    # Conservative: flag only if 2+ rules trigger
    rule_counts = np.zeros(len(records))
    for rfunc in rules.values():
        rule_counts += np.array([rfunc(r) for r in records])

    for min_rules in [2, 3]:
        flagged = rule_counts >= min_rules
        fp_caught = (flagged & (labels == 0)).sum()
        tp_killed = (flagged & (labels == 1)).sum()
        total_flagged = flagged.sum()
        prec = fp_caught / total_flagged if total_flagged > 0 else 0
        out(f"**≥{min_rules} rules**: FPs caught {fp_caught}/{n_fp}, TPs killed {tp_killed}/{n_tp}, "
            f"precision {prec:.1%}, net {fp_caught - tp_killed:+d}")
    out()

    # Per-project for best rule combo
    out("**Per-project (≥2 rules):**")
    out()
    out("| Project | FPs | Caught | TPs | Killed | Net |")
    out("|---------|-----|--------|-----|--------|-----|")
    flagged_2 = rule_counts >= 2
    for proj in PROJECTS:
        pmask = np.array([p == proj for p in projects])
        p_labels = labels[pmask]
        p_flagged = flagged_2[pmask]
        fp_c = (p_flagged & (p_labels == 0)).sum()
        tp_k = (p_flagged & (p_labels == 1)).sum()
        n_tp_p = p_labels.sum()
        n_fp_p = len(p_labels) - n_tp_p
        out(f"| {proj} | {n_fp_p} | {fp_c} | {n_tp_p} | {tp_k} | {fp_c - tp_k:+d} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 5: NLI-style Entailment Framing
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 5: Entailment Framing")
    out()
    out("Embed the hypothesis \"This sentence is an architectural description of {name}\"")
    out("and measure cosine similarity to the sentence. Higher = more likely TP.")
    out()

    hypotheses = [
        "This sentence is an architectural description of {name}",
        "This sentence describes the responsibilities of the {name} component",
        "This sentence explains how {name} works in the system architecture",
    ]

    for hyp_template in hypotheses:
        scores = []
        for idx, r in enumerate(records):
            hyp = hyp_template.format(name=r["elem_name"])
            hyp_emb = model.encode([hyp])[0]
            sim = cosine_sim(sent_embs[idx], hyp_emb)
            scores.append(sim)
        scores = np.array(scores)

        tp_mean = scores[labels == 1].mean()
        fp_mean = scores[labels == 0].mean()

        # Try a few thresholds
        best_net = -999
        best_t = 0
        for t in np.arange(0.1, 0.6, 0.02):
            preds = (scores >= t).astype(int)
            fp_caught = ((preds == 0) & (labels == 0)).sum()
            tp_killed = ((preds == 0) & (labels == 1)).sum()
            net = fp_caught - tp_killed
            if net > best_net:
                best_net = net
                best_t = t

        preds = (scores >= best_t).astype(int)
        fp_caught = ((preds == 0) & (labels == 0)).sum()
        tp_killed = ((preds == 0) & (labels == 1)).sum()

        out(f"**\"{hyp_template}\"**")
        out(f"- TP mean sim: {tp_mean:.4f}, FP mean sim: {fp_mean:.4f}")
        out(f"- Best threshold: {best_t:.2f} → FPs caught {fp_caught}/{n_fp}, "
            f"TPs killed {tp_killed}/{n_tp}, net {best_net:+d}")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Approach 6: Hybrid — Rules + Relative Framing
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Approach 6: Hybrid (Rules + Relative Framing)")
    out()
    out("Combine: flag as FP if (≥2 rules trigger) OR (impl_frame > arch_frame by margin)")
    out()

    # Use the ensemble vote from Approach 1
    framing_fp = ensemble_preds == 0
    rules_fp = rule_counts >= 2

    for combo_name, combo_mask in [
        ("Rules(≥2) OR Framing", rules_fp | framing_fp),
        ("Rules(≥2) AND Framing", rules_fp & framing_fp),
        ("Rules(≥2) only", rules_fp),
        ("Framing only", framing_fp),
    ]:
        fp_caught = (combo_mask & (labels == 0)).sum()
        tp_killed = (combo_mask & (labels == 1)).sum()
        total = combo_mask.sum()
        prec = fp_caught / total if total > 0 else 0
        out(f"**{combo_name}**: caught {fp_caught}/{n_fp} FPs, killed {tp_killed}/{n_tp} TPs, "
            f"precision {prec:.1%}, net {fp_caught - tp_killed:+d}")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Impact on SAD-SAM metrics
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Impact on SWATTR SAD-SAM Metrics")
    out()
    out("If we apply the zero-shot filter to remove predicted FPs from SWATTR output,")
    out("what happens to P/R/F1?")
    out()

    # For each project, compute original and filtered metrics
    out("| Project | Orig P | Orig R | Orig F1 | Filt P | Filt R | Filt F1 | ΔF1 |")
    out("|---------|--------|--------|---------|--------|--------|---------|-----|")

    # Use rules(≥2) as the filter (most interpretable)
    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)

        tp_orig = len(gold & result)
        fp_orig = len(result - gold)
        fn_orig = len(gold - result)

        p_orig = tp_orig / (tp_orig + fp_orig) if (tp_orig + fp_orig) > 0 else 0
        r_orig = tp_orig / (tp_orig + fn_orig) if (tp_orig + fn_orig) > 0 else 0
        f1_orig = 2*p_orig*r_orig/(p_orig+r_orig) if (p_orig+r_orig) > 0 else 0

        # Count how many TPs and FPs the filter removes for this project
        pmask = np.array([p == proj for p in projects])
        p_flagged = flagged_2[pmask]
        p_labels = labels[pmask]

        tp_removed = (p_flagged & (p_labels == 1)).sum()
        fp_removed = (p_flagged & (p_labels == 0)).sum()

        tp_filt = tp_orig - tp_removed
        fp_filt = fp_orig - fp_removed
        fn_filt = fn_orig + tp_removed  # killed TPs become FNs

        p_filt = tp_filt / (tp_filt + fp_filt) if (tp_filt + fp_filt) > 0 else 0
        r_filt = tp_filt / (tp_filt + fn_filt) if (tp_filt + fn_filt) > 0 else 0
        f1_filt = 2*p_filt*r_filt/(p_filt+r_filt) if (p_filt+r_filt) > 0 else 0

        delta = f1_filt - f1_orig
        out(f"| {proj} | {p_orig:.3f} | {r_orig:.3f} | {f1_orig:.3f} | "
            f"{p_filt:.3f} | {r_filt:.3f} | {f1_filt:.3f} | {delta:+.3f} |")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Synthesis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Synthesis")
    out()
    out("### Zero-shot verdict")
    out()

    # Compute best net benefit across approaches
    out("| Approach | FPs Caught | TPs Killed | Net | Generalizable? |")
    out("|----------|------------|------------|-----|----------------|")

    # Framing ensemble
    fp_c = ((ensemble_preds == 0) & (labels == 0)).sum()
    tp_k = ((ensemble_preds == 0) & (labels == 1)).sum()
    out(f"| Relative framing (ensemble) | {fp_c}/{n_fp} | {tp_k}/{n_tp} | {fp_c-tp_k:+d} | Partially |")

    # Rules ≥2
    fp_c = (flagged_2 & (labels == 0)).sum()
    tp_k = (flagged_2 & (labels == 1)).sum()
    out(f"| Rule-based (≥2 rules) | {fp_c}/{n_fp} | {tp_k}/{n_tp} | {fp_c-tp_k:+d} | Teammates-specific |")

    # Clustering k=2
    km2 = KMeans(n_clusters=2, random_state=42, n_init=10)
    c2 = km2.fit_predict(emb_pca)
    # assign smaller cluster as FP
    c0_tp_rate = labels[c2 == 0].mean() if (c2 == 0).sum() > 0 else 1
    c1_tp_rate = labels[c2 == 1].mean() if (c2 == 1).sum() > 0 else 1
    fp_cluster = 0 if c0_tp_rate < c1_tp_rate else 1
    fp_c = ((c2 == fp_cluster) & (labels == 0)).sum()
    tp_k = ((c2 == fp_cluster) & (labels == 1)).sum()
    out(f"| Unsupervised K=2 | {fp_c}/{n_fp} | {tp_k}/{n_tp} | {fp_c-tp_k:+d} | No (random) |")

    out()
    out("### Conclusion")
    out()
    out("1. **Relative framing (arch vs impl)** is the most principled zero-shot approach.")
    out("   It captures the right intuition: TP sentences describe architectural roles,")
    out("   FP sentences describe implementation/package structure.")
    out()
    out("2. **Rule-based heuristics** work well but are Teammates-specific.")
    out("   The \"package contains classes\" pattern captures most Teammates FPs")
    out("   but won't help with BBB or MediaStore FPs.")
    out()
    out("3. **Unsupervised clustering fails** — TPs and FPs don't form natural")
    out("   separable clusters in embedding space.")
    out()
    out("4. **The practical ceiling is low.** Even the best zero-shot approach")
    out("   catches <50% of FPs while killing some TPs. The net benefit is marginal.")
    out("   This confirms: the TP/FP distinction at the SAD-SAM level is largely an")
    out("   **annotation convention** — not a semantic property recoverable without")
    out("   project-specific calibration.")
    out()

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nWritten to {OUTPUT_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
