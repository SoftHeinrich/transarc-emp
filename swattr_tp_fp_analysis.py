#!/usr/bin/env python3
"""
SWATTR (SAD-SAM) TP vs FP Feature Analysis

Extracts features for each SWATTR trace link and analyzes whether
true positives (TPs) and false positives (FPs) are separable in
a feature space. Uses logistic regression, random forest, and
statistical tests.

Produces: SWATTR_TP_FP_ANALYSIS.md
"""

import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

# ─── Paths ────────────────────────────────────────────────────────────────────

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/SWATTR_TP_FP_ANALYSIS.md")

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

PCM_FILES = {
    "mediastore":    BENCHMARK / "mediastore/model_2016/pcm/ms.repository",
    "teastore":      BENCHMARK / "teastore/model_2020/pcm/teastore.repository",
    "teammates":     BENCHMARK / "teammates/model_2021/pcm/teammates.repository",
    "bigbluebutton": BENCHMARK / "bigbluebutton/model_2021/pcm/bbb.repository",
    "jabref":        BENCHMARK / "jabref/model_2021/pcm/jabref.repository",
}


# ─── Data loaders ─────────────────────────────────────────────────────────────

def load_text(project):
    """Returns dict: sentence_number_str -> sentence_text."""
    sentences = {}
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            sentences[str(i)] = line.strip()
    return sentences


def load_gs_sad_sam(project):
    """Returns set of (modelElementID, sentence_str)."""
    links = set()
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_result_sad_sam(project):
    """SWATTR standalone SAD-SAM result: set of (modelElementID, sentence_str)."""
    path = RESULTS / project / "sad-sam" / f"sadSamTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_model_element_info(project):
    """Returns dict: model_element_id -> {name, type} from SAM-CODE gold + PCM XML."""
    info = {}
    # From SAM-CODE gold standard (has ae_name with "Component: X" / "Interface: X")
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
    # Also try PCM XML for any elements not in SAM-CODE gold
    try:
        tree = ET.parse(PCM_FILES[project])
        root = tree.getroot()
        ns = {"repository": "http://palladiosimulator.org/PalladioComponentModel/Repository/5.2"}
        for comp in root.findall(".//repository:BasicComponent", ns) + root.findall(".//{http://palladiosimulator.org/PalladioComponentModel/Repository/5.2}BasicComponent"):
            eid = comp.get("id")
            ename = comp.get("entityName")
            if eid and ename and eid not in info:
                info[eid] = {"name": ename, "type": "Component"}
        # Also check for components in non-namespaced format
        for comp in root.iter():
            if "BasicComponent" in comp.tag:
                eid = comp.get("id")
                ename = comp.get("entityName")
                if eid and ename and eid not in info:
                    info[eid] = {"name": ename, "type": "Component"}
            elif "OperationInterface" in comp.tag:
                eid = comp.get("id")
                ename = comp.get("entityName")
                if eid and ename and eid not in info:
                    info[eid] = {"name": ename, "type": "Interface"}
    except Exception:
        pass
    return info


# ─── Feature extraction ──────────────────────────────────────────────────────

def tokenize(text):
    """Simple word tokenization."""
    return re.findall(r'[a-zA-Z]+', text.lower())


def split_camel_case(name):
    """Split camelCase/PascalCase into words."""
    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    words = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', words)
    return words.lower().split()


def extract_features(project, model_id, sent_num, sent_text, elem_info,
                     gold_links, result_links, total_sentences):
    """Extract feature dict for a single (model_id, sent_num) link."""
    sent_words = tokenize(sent_text)
    sent_num_int = int(sent_num)

    # Element info
    ei = elem_info.get(model_id, {"name": "UNKNOWN", "type": "Unknown"})
    elem_name = ei["name"]
    elem_type = ei["type"]
    elem_name_words = split_camel_case(elem_name)
    elem_name_tokens = tokenize(elem_name)

    # Gold/result fan-out counts
    gold_sent_fanout = sum(1 for (m, s) in gold_links if s == sent_num)
    gold_elem_fanout = sum(1 for (m, s) in gold_links if m == model_id)
    result_sent_fanout = sum(1 for (m, s) in result_links if s == sent_num)
    result_elem_fanout = sum(1 for (m, s) in result_links if m == model_id)

    # Name matching features
    sent_lower = sent_text.lower()
    name_lower = elem_name.lower()

    # Exact name match in sentence
    exact_match = 1 if name_lower in sent_lower else 0

    # Fraction of element name words found in sentence
    name_words_found = sum(1 for w in elem_name_tokens if w in sent_lower) if elem_name_tokens else 0
    name_word_fraction = name_words_found / len(elem_name_tokens) if elem_name_tokens else 0

    # Also check camelCase-split words
    camel_words_found = sum(1 for w in elem_name_words if w in sent_lower) if elem_name_words else 0
    camel_word_fraction = camel_words_found / len(elem_name_words) if elem_name_words else 0

    # Jaccard similarity between sentence words and element name words
    sent_word_set = set(sent_words)
    elem_word_set = set(elem_name_tokens) | set(elem_name_words)
    if sent_word_set or elem_word_set:
        jaccard = len(sent_word_set & elem_word_set) / len(sent_word_set | elem_word_set)
    else:
        jaccard = 0

    # Best substring match ratio (SequenceMatcher)
    best_ratio = 0
    for word in sent_words:
        ratio = SequenceMatcher(None, name_lower, word).ratio()
        if ratio > best_ratio:
            best_ratio = ratio

    # Best match for camelCase parts
    best_camel_ratio = 0
    for cw in elem_name_words:
        for sw in sent_words:
            ratio = SequenceMatcher(None, cw, sw).ratio()
            if ratio > best_camel_ratio:
                best_camel_ratio = ratio

    # Sentence position features
    norm_position = sent_num_int / total_sentences if total_sentences > 0 else 0

    features = {
        # Sentence features
        "sent_length": len(sent_text),
        "sent_word_count": len(sent_words),
        "sent_position_norm": norm_position,
        "sent_is_first_quarter": 1 if norm_position <= 0.25 else 0,
        "sent_is_last_quarter": 1 if norm_position > 0.75 else 0,

        # Element features
        "elem_is_interface": 1 if elem_type == "Interface" else 0,
        "elem_name_length": len(elem_name),
        "elem_name_word_count": len(elem_name_tokens),

        # Fan-out (structural)
        "gold_sent_fanout": gold_sent_fanout,
        "gold_elem_fanout": gold_elem_fanout,
        "result_sent_fanout": result_sent_fanout,
        "result_elem_fanout": result_elem_fanout,

        # Name matching
        "exact_name_match": exact_match,
        "name_word_fraction": name_word_fraction,
        "camel_word_fraction": camel_word_fraction,
        "jaccard_similarity": jaccard,
        "best_word_ratio": best_ratio,
        "best_camel_ratio": best_camel_ratio,
    }
    return features


# ─── Analysis ─────────────────────────────────────────────────────────────────

def collect_all_data():
    """Collect features for all TPs and FPs across all projects."""
    all_features = []
    all_labels = []     # 1 = TP, 0 = FP
    all_projects = []
    all_details = []    # (project, model_id, sent_num, elem_name, sent_text_snippet)

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)
        total_sentences = len(text)

        tp_set = gold & result
        fp_set = result - gold

        for model_id, sent_num in tp_set:
            sent_text = text.get(sent_num, "")
            feats = extract_features(proj, model_id, sent_num, sent_text, elem_info,
                                     gold, result, total_sentences)
            all_features.append(feats)
            all_labels.append(1)
            all_projects.append(proj)
            ei = elem_info.get(model_id, {"name": "?"})
            all_details.append((proj, model_id, sent_num, ei["name"], sent_text[:80]))

        for model_id, sent_num in fp_set:
            sent_text = text.get(sent_num, "")
            feats = extract_features(proj, model_id, sent_num, sent_text, elem_info,
                                     gold, result, total_sentences)
            all_features.append(feats)
            all_labels.append(0)
            all_projects.append(proj)
            ei = elem_info.get(model_id, {"name": "?"})
            all_details.append((proj, model_id, sent_num, ei["name"], sent_text[:80]))

    return all_features, all_labels, all_projects, all_details


def features_to_matrix(all_features):
    """Convert list of feature dicts to numpy matrix + feature names."""
    if not all_features:
        return np.array([]), []
    names = sorted(all_features[0].keys())
    X = np.array([[f[n] for n in names] for f in all_features])
    return X, names


def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    out("# SWATTR (SAD-SAM) TP vs FP Feature Analysis")
    out()
    out("Can we distinguish SWATTR true positives from false positives using")
    out("externally observable features? This analysis extracts a feature vector")
    out("for each SWATTR link and tests separability.")
    out()

    # ─── 1. Data collection ───────────────────────────────────────────────────

    out("## 1. Data Overview")
    out()

    all_features, all_labels, all_projects, all_details = collect_all_data()
    labels = np.array(all_labels)
    X, feature_names = features_to_matrix(all_features)

    n_tp = sum(labels)
    n_fp = len(labels) - n_tp

    out(f"Total links analyzed: **{len(labels)}** ({n_tp} TPs, {n_fp} FPs)")
    out()

    out("| Project | TPs | FPs | Total | FP Rate |")
    out("|---------|-----|-----|-------|---------|")
    for proj in PROJECTS:
        mask = [p == proj for p in all_projects]
        tp_proj = sum(1 for m, l in zip(mask, labels) if m and l == 1)
        fp_proj = sum(1 for m, l in zip(mask, labels) if m and l == 0)
        total = tp_proj + fp_proj
        rate = fp_proj / total if total > 0 else 0
        out(f"| {proj} | {tp_proj} | {fp_proj} | {total} | {rate:.1%} |")
    out()

    # ─── 2. Feature distributions ────────────────────────────────────────────

    out("## 2. Feature Distributions: TP vs FP")
    out()
    out("Mean values and Cohen's d effect size for each feature.")
    out("Cohen's d: |d|<0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, >0.8 large.")
    out()

    tp_mask = labels == 1
    fp_mask = labels == 0

    out("| Feature | TP Mean | FP Mean | Cohen's d | Direction |")
    out("|---------|---------|---------|-----------|-----------|")

    effect_sizes = []
    for i, name in enumerate(feature_names):
        tp_vals = X[tp_mask, i]
        fp_vals = X[fp_mask, i]
        d = cohens_d(tp_vals, fp_vals)
        effect_sizes.append((name, d))
        direction = "TP > FP" if d > 0 else "FP > TP" if d < 0 else "="
        out(f"| {name} | {np.mean(tp_vals):.3f} | {np.mean(fp_vals):.3f} | {d:+.3f} | {direction} |")
    out()

    # Sort by absolute effect size
    effect_sizes.sort(key=lambda x: abs(x[1]), reverse=True)
    out("**Top features by |Cohen's d|:**")
    out()
    for name, d in effect_sizes[:5]:
        size = "large" if abs(d) > 0.8 else "medium" if abs(d) > 0.5 else "small" if abs(d) > 0.2 else "negligible"
        out(f"- `{name}`: d={d:+.3f} ({size})")
    out()

    # ─── 3. Per-project feature analysis ──────────────────────────────────────

    out("## 3. Per-Project Feature Separability")
    out()
    out("Cohen's d for top features per project:")
    out()

    top_features = [name for name, _ in effect_sizes[:6]]
    header = "| Project | " + " | ".join(f"`{f}`" for f in top_features) + " |"
    sep = "|---------|" + "|".join("---------" for _ in top_features) + "|"
    out(header)
    out(sep)
    for proj in PROJECTS:
        proj_mask = np.array([p == proj for p in all_projects])
        proj_tp = proj_mask & tp_mask
        proj_fp = proj_mask & fp_mask
        vals = []
        for fname in top_features:
            fi = feature_names.index(fname)
            if proj_tp.sum() > 1 and proj_fp.sum() > 1:
                d = cohens_d(X[proj_tp, fi], X[proj_fp, fi])
                vals.append(f"{d:+.2f}")
            else:
                vals.append("N/A")
        out(f"| {proj} | " + " | ".join(vals) + " |")
    out()

    # ─── 4. Classification experiments ────────────────────────────────────────

    out("## 4. Classification Experiments")
    out()
    out("Can a classifier distinguish TPs from FPs? Using stratified 5-fold CV.")
    out()

    # Remove gold-based features for the "fair" classifier
    # gold_sent_fanout and gold_elem_fanout are oracle features
    fair_features = [i for i, n in enumerate(feature_names)
                     if not n.startswith("gold_")]
    oracle_features = [i for i, n in enumerate(feature_names)]

    # Also build a "no result fanout" version (truly external features only)
    external_features = [i for i, n in enumerate(feature_names)
                         if not n.startswith("gold_") and not n.startswith("result_")]

    scaler = StandardScaler()

    for feat_set_name, feat_indices in [
        ("All features (incl. oracle gold fanout)", oracle_features),
        ("Fair features (no gold, has result fanout)", fair_features),
        ("External-only (no gold, no result fanout)", external_features),
    ]:
        out(f"### {feat_set_name}")
        out()
        X_sub = X[:, feat_indices]
        feat_sub_names = [feature_names[i] for i in feat_indices]

        if len(X_sub) < 10:
            out("Too few samples for classification.")
            out()
            continue

        X_scaled = scaler.fit_transform(X_sub)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Logistic Regression
        lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
        lr_preds = cross_val_predict(lr, X_scaled, labels, cv=cv)
        lr_proba = cross_val_predict(lr, X_scaled, labels, cv=cv, method="predict_proba")[:, 1]
        lr_acc = accuracy_score(labels, lr_preds)
        lr_auc = roc_auc_score(labels, lr_proba)

        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_preds = cross_val_predict(rf, X_scaled, labels, cv=cv)
        rf_proba = cross_val_predict(rf, X_scaled, labels, cv=cv, method="predict_proba")[:, 1]
        rf_acc = accuracy_score(labels, rf_preds)
        rf_auc = roc_auc_score(labels, rf_proba)

        # Majority baseline
        majority_acc = n_tp / len(labels) if n_tp > n_fp else n_fp / len(labels)

        out(f"| Classifier | Accuracy | AUC-ROC |")
        out(f"|------------|----------|---------|")
        out(f"| Majority baseline | {majority_acc:.3f} | 0.500 |")
        out(f"| Logistic Regression | {lr_acc:.3f} | {lr_auc:.3f} |")
        out(f"| Random Forest | {rf_acc:.3f} | {rf_auc:.3f} |")
        out()

        # Feature importances from full-data RF
        rf_full = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_full.fit(X_scaled, labels)
        importances = sorted(zip(feat_sub_names, rf_full.feature_importances_),
                             key=lambda x: x[1], reverse=True)

        out("**RF Feature Importances (top 8):**")
        out()
        for fname, imp in importances[:8]:
            bar = "#" * int(imp * 100)
            out(f"- `{fname}`: {imp:.3f} {bar}")
        out()

        # LR coefficients
        lr_full = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
        lr_full.fit(X_scaled, labels)
        coefs = sorted(zip(feat_sub_names, lr_full.coef_[0]),
                       key=lambda x: abs(x[1]), reverse=True)

        out("**LR Coefficients (top 8, positive = predicts TP):**")
        out()
        for fname, coef in coefs[:8]:
            out(f"- `{fname}`: {coef:+.3f}")
        out()

    # ─── 5. Leave-one-project-out ─────────────────────────────────────────────

    out("## 5. Leave-One-Project-Out Cross-Validation")
    out()
    out("Tests generalization: train on 4 projects, predict on held-out project.")
    out("Using external-only features (no oracle info).")
    out()

    X_ext = X[:, external_features]
    X_ext_scaled = scaler.fit_transform(X_ext)

    out("| Held-out Project | n_TP | n_FP | LR Acc | LR AUC | RF Acc | RF AUC |")
    out("|------------------|------|------|--------|--------|--------|--------|")

    for proj in PROJECTS:
        proj_mask = np.array([p == proj for p in all_projects])
        train_mask = ~proj_mask
        test_mask = proj_mask

        if test_mask.sum() < 3 or train_mask.sum() < 5:
            out(f"| {proj} | - | - | N/A | N/A | N/A | N/A |")
            continue

        X_train, y_train = X_ext_scaled[train_mask], labels[train_mask]
        X_test, y_test = X_ext_scaled[test_mask], labels[test_mask]

        n_tp_test = y_test.sum()
        n_fp_test = len(y_test) - n_tp_test

        if n_tp_test == 0 or n_fp_test == 0:
            out(f"| {proj} | {n_tp_test} | {n_fp_test} | N/A (single class) | N/A | N/A | N/A |")
            continue

        lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
        lr.fit(X_train, y_train)
        lr_acc = accuracy_score(y_test, lr.predict(X_test))
        lr_auc = roc_auc_score(y_test, lr.predict_proba(X_test)[:, 1])

        rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf.fit(X_train, y_train)
        rf_acc = accuracy_score(y_test, rf.predict(X_test))
        rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])

        out(f"| {proj} | {n_tp_test} | {n_fp_test} | {lr_acc:.3f} | {lr_auc:.3f} | {rf_acc:.3f} | {rf_auc:.3f} |")
    out()

    # ─── 6. Error inspection ──────────────────────────────────────────────────

    out("## 6. FP Inspection: What Do False Positives Look Like?")
    out()
    out("All FP links with key features:")
    out()

    for proj in PROJECTS:
        proj_fps = [(d, f) for d, f, p, l in zip(all_details, all_features, all_projects, labels)
                    if p == proj and l == 0]
        if not proj_fps:
            continue
        out(f"### {proj} ({len(proj_fps)} FPs)")
        out()
        out("| Sent# | Element | Exact Match | Name Frac | Best Ratio | Sentence (truncated) |")
        out("|-------|---------|-------------|-----------|------------|---------------------|")
        for detail, feats in proj_fps:
            _, _, sent_num, elem_name, snippet = detail
            out(f"| {sent_num} | {elem_name} | {feats['exact_name_match']} | "
                f"{feats['name_word_fraction']:.2f} | {feats['best_word_ratio']:.2f} | "
                f"{snippet[:60]}... |")
        out()

    # ─── 7. FN analysis ──────────────────────────────────────────────────────

    out("## 7. False Negative Analysis")
    out()
    out("What gold links did SWATTR miss? Features of FNs vs TPs.")
    out()

    fn_features = []
    fn_labels = []  # all 0
    fn_details = []

    for proj in PROJECTS:
        gold = load_gs_sad_sam(proj)
        result = load_result_sad_sam(proj)
        text = load_text(proj)
        elem_info = load_model_element_info(proj)
        total_sentences = len(text)

        fn_set = gold - result
        for model_id, sent_num in fn_set:
            sent_text = text.get(sent_num, "")
            feats = extract_features(proj, model_id, sent_num, sent_text, elem_info,
                                     gold, result, total_sentences)
            fn_features.append(feats)
            fn_labels.append(0)
            ei = elem_info.get(model_id, {"name": "?"})
            fn_details.append((proj, model_id, sent_num, ei["name"], sent_text[:80]))

    tp_features_only = [f for f, l in zip(all_features, all_labels) if l == 1]
    X_fn, _ = features_to_matrix(fn_features)
    X_tp, _ = features_to_matrix(tp_features_only)

    if len(X_fn) > 0 and len(X_tp) > 0:
        out("| Feature | TP Mean | FN Mean | Cohen's d | Interpretation |")
        out("|---------|---------|---------|-----------|----------------|")
        for i, name in enumerate(feature_names):
            tp_vals = X_tp[:, i]
            fn_vals = X_fn[:, i]
            d = cohens_d(tp_vals, fn_vals)
            interp = ""
            if abs(d) > 0.5:
                if d > 0:
                    interp = "TPs higher"
                else:
                    interp = "FNs higher"
            out(f"| {name} | {np.mean(tp_vals):.3f} | {np.mean(fn_vals):.3f} | {d:+.3f} | {interp} |")
        out()

        out(f"Total FNs: **{len(fn_features)}** across all projects")
        out()

        out("**FN breakdown by project:**")
        out()
        for proj in PROJECTS:
            proj_fns = [(d, f) for d, f, l in zip(fn_details, fn_features, fn_labels)
                        if d[0] == proj]
            if not proj_fns:
                continue
            out(f"- **{proj}**: {len(proj_fns)} FNs")
            for detail, feats in proj_fns[:5]:
                _, _, sent_num, elem_name, snippet = detail
                out(f"  - S{sent_num} x {elem_name}: exact={feats['exact_name_match']}, "
                    f"name_frac={feats['name_word_fraction']:.2f}, "
                    f"best_ratio={feats['best_word_ratio']:.2f}")
            if len(proj_fns) > 5:
                out(f"  - ... and {len(proj_fns) - 5} more")
        out()

    # ─── 8. Synthesis ─────────────────────────────────────────────────────────

    out("## 8. Synthesis")
    out()

    # Determine overall separability
    # Re-run external-only classification for summary
    X_ext = X[:, external_features]
    X_ext_scaled = scaler.fit_transform(X_ext)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf_proba = cross_val_predict(rf, X_ext_scaled, labels, cv=cv, method="predict_proba")[:, 1]
    ext_auc = roc_auc_score(labels, rf_proba)

    X_all_scaled = scaler.fit_transform(X)
    rf_all = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf_all_proba = cross_val_predict(rf_all, X_all_scaled, labels, cv=cv, method="predict_proba")[:, 1]
    all_auc = roc_auc_score(labels, rf_all_proba)

    if ext_auc < 0.6:
        verdict = "NOT SEPARABLE"
        explanation = ("External features achieve near-random AUC (<0.6). "
                       "TPs and FPs are essentially indistinguishable from "
                       "observable text/structural features alone.")
    elif ext_auc < 0.7:
        verdict = "WEAKLY SEPARABLE"
        explanation = ("Some signal exists (AUC 0.6-0.7) but insufficient for "
                       "reliable TP/FP discrimination. A classifier would make "
                       "too many errors to be useful as a filter.")
    elif ext_auc < 0.8:
        verdict = "MODERATELY SEPARABLE"
        explanation = ("Meaningful signal exists (AUC 0.7-0.8). A classifier could "
                       "identify some FPs but at the cost of also removing TPs.")
    else:
        verdict = "SEPARABLE"
        explanation = ("Strong signal (AUC >0.8). A classifier could reliably "
                       "distinguish TPs from FPs.")

    out(f"### Verdict: **{verdict}**")
    out()
    out(f"- External-only RF AUC: **{ext_auc:.3f}**")
    out(f"- All-features RF AUC: **{all_auc:.3f}**")
    out()
    out(explanation)
    out()

    out("### Key Findings")
    out()
    out("1. **Most discriminative features** (by effect size):")
    for name, d in effect_sizes[:3]:
        out(f"   - `{name}` (d={d:+.3f})")
    out()

    # Check if name matching is the key
    name_features = [n for n in feature_names if "name" in n or "match" in n or "ratio" in n or "jaccard" in n]
    name_indices = [feature_names.index(n) for n in name_features]
    if name_indices:
        X_name = X[:, name_indices]
        X_name_scaled = scaler.fit_transform(X_name)
        rf_name = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_name_proba = cross_val_predict(rf_name, X_name_scaled, labels, cv=cv, method="predict_proba")[:, 1]
        name_auc = roc_auc_score(labels, rf_name_proba)
        out(f"2. **Name-matching features alone**: AUC = {name_auc:.3f}")
        out()

    out("3. **Implications for SWATTR improvement**:")
    out()
    if ext_auc < 0.65:
        out("   SWATTR FPs are not systematically different from TPs in observable features.")
        out("   This means:")
        out("   - Post-hoc filtering based on text features cannot reliably remove FPs")
        out("   - FPs are 'hard' — they look like genuine trace links from text alone")
        out("   - Improvement requires richer signals (code structure, runtime, cross-references)")
    else:
        out("   Some FPs are systematically distinguishable from TPs.")
        out("   The most useful features for a post-hoc filter would be:")
        for name, d in effect_sizes[:3]:
            out(f"   - `{name}`")
    out()

    # ─── Write output ─────────────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"\nWritten to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
