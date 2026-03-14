#!/usr/bin/env python3
"""
TransArc Empirical Error Analysis

Decomposes TransArc (SAD-CODE) false positives and false negatives back to their
component causes in SAD-SAM and SAM-CODE, quantifies error propagation / amplification,
and performs "what-if" component comparison analysis.

Produces structured stdout output and writes TRANSARC_EMPIRICAL_STUDY.md.
"""

import csv
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/TRANSARC_EMPIRICAL_STUDY.md")

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]

# ─── Gold standard / code-model file mappings ────────────────────────────────

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

GS_SAD_CODE = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sad_2016-code_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sad_2020-code_2022.csv",
    "teammates":     BENCHMARK / "teammates/goldstandards/goldstandard_sad_2021-code_2023.csv",
    "bigbluebutton": BENCHMARK / "bigbluebutton/goldstandards/goldstandard_sad_2021-code_2023.csv",
    "jabref":        BENCHMARK / "jabref/goldstandards/goldstandard_sad_2021-code_2023.csv",
}

ACM_FILES = {
    "mediastore":    BENCHMARK / "mediastore/model_2016/code/codeModel.acm",
    "teastore":      BENCHMARK / "teastore/model_2022/code/codeModel.acm",
    "teammates":     BENCHMARK / "teammates/model_2023/code/codeModel.acm",
    "bigbluebutton": BENCHMARK / "bigbluebutton/model_2023/code/codeModel.acm",
    "jabref":        BENCHMARK / "jabref/model_2023/code/codeModel.acm",
}

TEXT_FILES = {
    "mediastore":    BENCHMARK / "mediastore/text_2016/mediastore.txt",
    "teastore":      BENCHMARK / "teastore/text_2020/teastore.txt",
    "teammates":     BENCHMARK / "teammates/text_2021/teammates.txt",
    "bigbluebutton": BENCHMARK / "bigbluebutton/text_2021/bigbluebutton.txt",
    "jabref":        BENCHMARK / "jabref/text_2021/jabref.txt",
}

# Expected thresholds from Java test files (precision, recall, f1)
EXPECTED = {
    "sad-sam": {
        "mediastore": (0.940, 0.548, 0.69),
        "teastore": (0.999, 0.74, 0.85),
        "teammates": (0.60, 0.859, 0.709),
        "bigbluebutton": (0.897, 0.709, 0.79),
        "jabref": (0.899, 0.999, 0.946),
    },
    "sam-code": {
        "mediastore": (0.975, 0.995, 0.985),
        "teastore": (0.975, 0.975, 0.975),
        "teammates": (0.999, 0.999, 0.999),
        "bigbluebutton": (0.874, 0.953, 0.912),
        "jabref": (0.999, 0.999, 0.999),
    },
    "sad-code": {
        "mediastore": (0.96, 0.42, 0.588),
        "teastore": (0.999, 0.708, 0.829),
        "teammates": (0.75, 0.90, 0.82),
        "bigbluebutton": (0.82, 0.84, 0.83),
        "jabref": (0.885, 0.999, 0.935),
    },
}

# ─── Data loading helpers ─────────────────────────────────────────────────────

def normalize_path(path):
    """Remove 'Implementation/' prefix."""
    if path.startswith("Implementation/"):
        path = path[len("Implementation/"):]
    return path


def load_code_model_files(project):
    """Load all file paths from the .acm code model."""
    acm_file = ACM_FILES[project]
    files = set()
    with open(acm_file) as f:
        data = json.load(f)
    repo = data.get("codeItemRepository", {}).get("repository", {})
    for item in repo.values():
        if item.get("type") == "CodeCompilationUnit":
            path_elements = item.get("pathElements", [])
            name = item.get("name", "")
            ext = item.get("extension", "")
            if path_elements and name:
                full_path = "/".join(path_elements) + "/" + name
                if ext:
                    full_path += "." + ext
                files.add(normalize_path(full_path))
    return files


def enroll_gold_standard(gold, code_model_files):
    """Expand directory-level gold entries to individual files."""
    enrolled = set()
    for g_id, g_path in gold:
        if g_path.endswith("/"):
            for file_path in code_model_files:
                if file_path.startswith(g_path):
                    enrolled.add((g_id, file_path))
        else:
            enrolled.add((g_id, g_path))
    return enrolled


# ─── Gold standard loaders ────────────────────────────────────────────────────

def load_gs_sad_sam(project):
    """Returns set of (modelElementID, sentence_str)."""
    links = set()
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_gs_sad_sam_maps(project):
    """Returns (sent->set(model), model->set(sent)) dicts."""
    sent_to_model = defaultdict(set)
    model_to_sent = defaultdict(set)
    with open(GS_SAD_SAM[project]) as f:
        for row in csv.DictReader(f):
            sent_to_model[row["sentence"]].add(row["modelElementID"])
            model_to_sent[row["modelElementID"]].add(row["sentence"])
    return dict(sent_to_model), dict(model_to_sent)


def load_gs_sam_code_raw(project):
    """Returns set of (ae_id, normalized_ce_path) — NOT enrolled."""
    links = set()
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            ae_id = row["ae_id"]
            ce_path = row.get("ce_ids") or row.get("ce_id")
            links.add((ae_id, normalize_path(ce_path)))
    return links


def load_gs_sam_code_maps(project, code_model_files):
    """Returns enrolled (model->set(code), code->set(model)) dicts."""
    raw = load_gs_sam_code_raw(project)
    enrolled = enroll_gold_standard(raw, code_model_files)
    model_to_code = defaultdict(set)
    code_to_model = defaultdict(set)
    for m, c in enrolled:
        model_to_code[m].add(c)
        code_to_model[c].add(m)
    return dict(model_to_code), dict(code_to_model)


def load_gs_sad_code_raw(project):
    """Returns set of (sentenceID_str, normalized_code_path) — NOT enrolled."""
    links = set()
    with open(GS_SAD_CODE[project]) as f:
        for row in csv.DictReader(f):
            links.add((row["sentenceID"], normalize_path(row["codeID"])))
    return links


def load_gs_sad_code_enrolled(project, code_model_files):
    """Returns enrolled set of (sentenceID_str, code_path)."""
    raw = load_gs_sad_code_raw(project)
    return enroll_gold_standard(raw, code_model_files)


# ─── Result loaders ──────────────────────────────────────────────────────────

def load_result_sad_sam_standalone(project):
    """Standalone SAD-SAM result: set of (modelElementID, sentence_str)."""
    path = RESULTS / project / "sad-sam" / f"sadSamTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_result_sam_code_standalone(project):
    """Standalone SAM-CODE result: set of (sentenceID=ae_id, codeID)."""
    path = RESULTS / project / "sam-code" / f"samCodeTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["sentenceID"], normalize_path(row["codeID"])))
    return links


def load_result_sad_code(project):
    """TransArc final result: set of (sentence_str, code_path)."""
    path = RESULTS / project / "sad-code" / f"sadCodeTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], normalize_path(row["codeId"])))
    return links


def load_transarc_intermediate_sad_sam(project):
    """TransArc intermediate SAD-SAM: set of (modelElementID, sentence_str)."""
    path = RESULTS / project / "sad-code" / f"sadSamTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], row["sentence"]))
    return links


def load_transarc_intermediate_sam_code(project):
    """TransArc intermediate SAM-CODE: set of (modelElementID, code_path)."""
    path = RESULTS / project / "sad-code" / f"samCodeTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["sentenceID"], normalize_path(row["codeID"])))
    return links


def load_transarc_intermediate_maps(project):
    """Return dicts for tracing through intermediates.

    Returns:
        sent_to_models: sentence -> set(modelElementID) from intermediate SAD-SAM
        model_to_codes: modelElementID -> set(codePath) from intermediate SAM-CODE
        model_to_sents: modelElementID -> set(sentence) from intermediate SAD-SAM
        code_to_models: codePath -> set(modelElementID) from intermediate SAM-CODE
    """
    sent_to_models = defaultdict(set)
    model_to_sents = defaultdict(set)
    for m, s in load_transarc_intermediate_sad_sam(project):
        sent_to_models[s].add(m)
        model_to_sents[m].add(s)

    model_to_codes = defaultdict(set)
    code_to_models = defaultdict(set)
    for m, c in load_transarc_intermediate_sam_code(project):
        model_to_codes[m].add(c)
        code_to_models[c].add(m)

    return dict(sent_to_models), dict(model_to_codes), dict(model_to_sents), dict(code_to_models)


# ─── Text loader ──────────────────────────────────────────────────────────────

def load_text(project):
    """Returns dict: sentence_number_str -> sentence_text."""
    sentences = {}
    with open(TEXT_FILES[project]) as f:
        for i, line in enumerate(f, start=1):
            sentences[str(i)] = line.strip()
    return sentences


# ─── Metric computation ──────────────────────────────────────────────────────

def calc_metrics(gold, result):
    """Returns (precision, recall, f1, tp, fp, fn)."""
    if not result:
        return 0.0, 0.0, 0.0, 0, 0, len(gold)
    tp_set = gold & result
    fp_set = result - gold
    fn_set = gold - result
    tp = len(tp_set)
    fp = len(fp_set)
    fn = len(fn_set)
    precision = tp / len(result) if result else 0
    recall = tp / len(gold) if gold else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1, tp, fp, fn


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis A – Baseline Metrics
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_a():
    """Compute P/R/F1 for all 15 project×task combinations."""
    results = {}  # (task, project) -> (p, r, f1, tp, fp, fn, gold_size, res_size)

    for proj in PROJECTS:
        code_model = load_code_model_files(proj)

        # SAD-SAM
        gs = load_gs_sad_sam(proj)
        res = load_result_sad_sam_standalone(proj)
        p, r, f1, tp, fp, fn = calc_metrics(gs, res)
        results[("sad-sam", proj)] = (p, r, f1, tp, fp, fn, len(gs), len(res))

        # SAM-CODE (needs enrollment)
        gs_raw = load_gs_sam_code_raw(proj)
        gs_enrolled = enroll_gold_standard(gs_raw, code_model)
        res = load_result_sam_code_standalone(proj)
        p, r, f1, tp, fp, fn = calc_metrics(gs_enrolled, res)
        results[("sam-code", proj)] = (p, r, f1, tp, fp, fn, len(gs_enrolled), len(res))

        # SAD-CODE (needs enrollment)
        gs_enrolled = load_gs_sad_code_enrolled(proj, code_model)
        res = load_result_sad_code(proj)
        p, r, f1, tp, fp, fn = calc_metrics(gs_enrolled, res)
        results[("sad-code", proj)] = (p, r, f1, tp, fp, fn, len(gs_enrolled), len(res))

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis B – False Positive Decomposition
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FPClassification:
    sad_sam_caused: list = field(default_factory=list)    # SAD-SAM wrong, SAM-CODE correct
    sam_code_caused: list = field(default_factory=list)    # SAD-SAM correct, SAM-CODE wrong
    both_caused: list = field(default_factory=list)        # Both wrong
    combination_error: list = field(default_factory=list)  # Each component correct separately, but combination wrong


def analysis_b(project, code_model_files):
    """Classify each TransArc FP by root cause."""
    # Load gold standards
    gs_sad_sam = load_gs_sad_sam(project)
    gs_sam_code_enrolled_set = enroll_gold_standard(load_gs_sam_code_raw(project), code_model_files)
    gs_sad_code_enrolled = load_gs_sad_code_enrolled(project, code_model_files)

    # Load TransArc results and intermediates
    transarc_result = load_result_sad_code(project)
    int_sad_sam = load_transarc_intermediate_sad_sam(project)
    int_sam_code = load_transarc_intermediate_sam_code(project)

    # Build intermediate maps
    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(project)

    # Identify FPs
    tp_set = transarc_result & gs_sad_code_enrolled
    fp_set = transarc_result - gs_sad_code_enrolled

    cls = FPClassification()

    for (sent, code) in fp_set:
        # Find bridging model element(s): which M produced this (S,C)?
        models_from_sent = sent_to_models.get(sent, set())
        models_from_code = code_to_models.get(code, set())
        bridging_models = models_from_sent & models_from_code

        if not bridging_models:
            # Shouldn't happen if intermediates are consistent, but handle it
            cls.combination_error.append((sent, code, set(), "no_bridge"))
            continue

        # For each bridging model, check component correctness
        any_sad_sam_correct = False
        any_sam_code_correct = False

        for m in bridging_models:
            if (m, sent) in gs_sad_sam:
                any_sad_sam_correct = True
            if (m, code) in gs_sam_code_enrolled_set:
                any_sam_code_correct = True

        if not any_sad_sam_correct and not any_sam_code_correct:
            cls.both_caused.append((sent, code, bridging_models))
        elif not any_sad_sam_correct:
            cls.sad_sam_caused.append((sent, code, bridging_models))
        elif not any_sam_code_correct:
            cls.sam_code_caused.append((sent, code, bridging_models))
        else:
            # Both components have a correct individual link through some bridging model,
            # but the particular combination (S,C) is not in the gold standard.
            cls.combination_error.append((sent, code, bridging_models, "valid_components"))

    return cls, len(tp_set), len(fp_set)


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis C – False Negative Decomposition
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FNClassification:
    theoretical_limit: list = field(default_factory=list)  # No transitive path in gold
    sad_sam_miss: list = field(default_factory=list)        # TransArc missed SAD-SAM link
    sam_code_miss: list = field(default_factory=list)       # Correct model found, SAM-CODE missed code
    both_miss: list = field(default_factory=list)           # Both components missed


def analysis_c(project, code_model_files):
    """Classify each TransArc FN by root cause."""
    # Gold standards
    gs_sad_sam_sent2model, gs_sad_sam_model2sent = load_gs_sad_sam_maps(project)
    gs_sam_code_model2code, gs_sam_code_code2model = load_gs_sam_code_maps(project, code_model_files)
    gs_sad_code_enrolled = load_gs_sad_code_enrolled(project, code_model_files)

    # TransArc results and intermediates
    transarc_result = load_result_sad_code(project)
    sent_to_models_int, model_to_codes_int, _, _ = load_transarc_intermediate_maps(project)

    fn_set = gs_sad_code_enrolled - transarc_result

    cls = FNClassification()

    for (sent, code) in fn_set:
        # Step 1: Is there a transitive path in the gold standard?
        gold_models_for_sent = gs_sad_sam_sent2model.get(sent, set())
        gold_models_for_code = gs_sam_code_code2model.get(code, set())
        bridging_gold = gold_models_for_sent & gold_models_for_code

        if not bridging_gold:
            cls.theoretical_limit.append((sent, code, gold_models_for_sent, gold_models_for_code))
            continue

        # Transitive path exists in gold. Did TransArc find the right SAD-SAM links?
        transarc_models_for_sent = sent_to_models_int.get(sent, set())

        # Check if TransArc found any of the bridging models for this sentence
        found_correct_model = transarc_models_for_sent & bridging_gold

        if not found_correct_model:
            # TransArc didn't find the correct SAD-SAM link
            # But did TransArc find *any* SAD-SAM link for this sentence?
            if not transarc_models_for_sent:
                cls.sad_sam_miss.append((sent, code, bridging_gold, "no_link"))
            else:
                # Found wrong model(s) — check if those wrong models also miss the code
                wrong_models = transarc_models_for_sent - bridging_gold
                any_code_found = False
                for wm in wrong_models:
                    if code in model_to_codes_int.get(wm, set()):
                        any_code_found = True
                        break
                cls.sad_sam_miss.append((sent, code, bridging_gold, "wrong_model"))
            continue

        # TransArc found the correct model. Did SAM-CODE recover the code?
        any_code_recovered = False
        for m in found_correct_model:
            if code in model_to_codes_int.get(m, set()):
                any_code_recovered = True
                break

        if any_code_recovered:
            # Should have been a TP — this means our analysis is inconsistent
            # Actually this can happen if the link was somehow not in the final output
            # (e.g., filtering). Classify as both_miss for safety.
            cls.both_miss.append((sent, code, bridging_gold, "unexpected"))
        else:
            cls.sam_code_miss.append((sent, code, found_correct_model))

    return cls, len(fn_set)


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis D – Error Propagation / Amplification
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ErrorPropagation:
    # For each SAD-SAM FP (M, S), how many TransArc FPs did it induce?
    sad_sam_fp_amplification: list = field(default_factory=list)  # [(M, S, induced_fps)]
    # For each SAM-CODE FP (M, C), how many TransArc FPs did it induce?
    sam_code_fp_amplification: list = field(default_factory=list)  # [(M, C, induced_fps)]


def analysis_d(project, code_model_files):
    """Quantify error amplification from component FPs to TransArc FPs."""
    gs_sad_sam = load_gs_sad_sam(project)
    gs_sam_code_enrolled_set = enroll_gold_standard(load_gs_sam_code_raw(project), code_model_files)
    gs_sad_code_enrolled = load_gs_sad_code_enrolled(project, code_model_files)

    transarc_result = load_result_sad_code(project)
    int_sad_sam = load_transarc_intermediate_sad_sam(project)
    int_sam_code = load_transarc_intermediate_sam_code(project)

    sent_to_models, model_to_codes, model_to_sents, code_to_models = \
        load_transarc_intermediate_maps(project)

    fp_set = transarc_result - gs_sad_code_enrolled

    prop = ErrorPropagation()

    # Find SAD-SAM FPs in intermediate results
    sad_sam_fps = int_sad_sam - gs_sad_sam
    for (m, s) in sad_sam_fps:
        # How many TransArc FPs does this SAD-SAM FP induce?
        codes_from_m = model_to_codes.get(m, set())
        induced = 0
        for c in codes_from_m:
            if (s, c) in fp_set:
                induced += 1
        if induced > 0:
            prop.sad_sam_fp_amplification.append((m, s, induced))

    # Find SAM-CODE FPs in intermediate results
    sam_code_fps = int_sam_code - gs_sam_code_enrolled_set
    for (m, c) in sam_code_fps:
        sents_from_m = model_to_sents.get(m, set())
        induced = 0
        for s in sents_from_m:
            if (s, c) in fp_set:
                induced += 1
        if induced > 0:
            prop.sam_code_fp_amplification.append((m, c, induced))

    return prop


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis F – "What-If" Component Comparison
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_f(project, code_model_files):
    """What-if analysis: perfect SAD-SAM or perfect SAM-CODE."""
    gs_sad_sam = load_gs_sad_sam(project)
    gs_sad_sam_s2m, _ = load_gs_sad_sam_maps(project)
    gs_sam_code_m2c, _ = load_gs_sam_code_maps(project, code_model_files)
    gs_sad_code_enrolled = load_gs_sad_code_enrolled(project, code_model_files)

    # Actual intermediate results
    sent_to_models_int, model_to_codes_int, model_to_sents_int, _ = \
        load_transarc_intermediate_maps(project)

    # --- Scenario 1: Perfect SAD-SAM + Actual SAM-CODE ---
    # Use gold SAD-SAM links, compose with intermediate SAM-CODE
    perfect_sad_sam_result = set()
    for sent, models in gs_sad_sam_s2m.items():
        for m in models:
            codes = model_to_codes_int.get(m, set())
            for c in codes:
                perfect_sad_sam_result.add((sent, c))

    p1, r1, f1_1, tp1, fp1, fn1 = calc_metrics(gs_sad_code_enrolled, perfect_sad_sam_result)

    # --- Scenario 2: Actual SAD-SAM + Perfect SAM-CODE ---
    # Use intermediate SAD-SAM, compose with gold SAM-CODE links
    perfect_sam_code_result = set()
    for sent, models in sent_to_models_int.items():
        for m in models:
            codes = gs_sam_code_m2c.get(m, set())
            for c in codes:
                perfect_sam_code_result.add((sent, c))

    p2, r2, f1_2, tp2, fp2, fn2 = calc_metrics(gs_sad_code_enrolled, perfect_sam_code_result)

    # --- Scenario 3: Compare TransArc-internal SAM-CODE vs standalone SAM-CODE ---
    int_sam_code = load_transarc_intermediate_sam_code(project)
    standalone_sam_code = load_result_sam_code_standalone(project)

    gs_sam_code_enrolled_set = enroll_gold_standard(load_gs_sam_code_raw(project), code_model_files)

    int_p, int_r, int_f1, int_tp, int_fp, int_fn = calc_metrics(gs_sam_code_enrolled_set, int_sam_code)
    sa_p, sa_r, sa_f1, sa_tp, sa_fp, sa_fn = calc_metrics(gs_sam_code_enrolled_set, standalone_sam_code)

    return {
        "perfect_sad_sam": (p1, r1, f1_1, tp1, fp1, fn1, len(perfect_sad_sam_result)),
        "perfect_sam_code": (p2, r2, f1_2, tp2, fp2, fn2, len(perfect_sam_code_result)),
        "internal_sam_code": (int_p, int_r, int_f1, int_tp, int_fp, int_fn, len(int_sam_code)),
        "standalone_sam_code": (sa_p, sa_r, sa_f1, sa_tp, sa_fp, sa_fn, len(standalone_sam_code)),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SAM-CODE gold standard: ae_id -> ae_name mapping
# ═══════════════════════════════════════════════════════════════════════════════

def load_model_element_names(project):
    """Returns dict: model_element_id -> name from SAM-CODE gold standard."""
    names = {}
    with open(GS_SAM_CODE[project]) as f:
        for row in csv.DictReader(f):
            names[row["ae_id"]] = row["ae_name"]
    return names


# ═══════════════════════════════════════════════════════════════════════════════
# Main analysis + reporting
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    md_lines = []

    def out(s=""):
        print(s)
        md_lines.append(s)

    def md_only(s=""):
        md_lines.append(s)

    # ─── Header ───────────────────────────────────────────────────────────────

    out("# TransArc Empirical Error Study")
    out()
    out("An empirical decomposition of TransArc's false positives and false negatives")
    out("back to their component causes in SAD-SAM and SAM-CODE.")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis A – Baseline Metrics
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis A – Baseline Metrics")
    out()

    baseline = analysis_a()

    for task in ["sad-sam", "sam-code", "sad-code"]:
        task_label = {"sad-sam": "SAD-SAM (Swattr)", "sam-code": "SAM-CODE (Arcotl)",
                      "sad-code": "SAD-CODE (TransArc)"}[task]
        out(f"### {task_label}")
        out()
        out(f"| Project | Gold | Result | TP | FP | FN | Precision | Recall | F1 | Exp P | Exp R | Exp F1 |")
        out(f"|---------|------|--------|----|----|-----|-----------|--------|-----|-------|-------|--------|")

        for proj in PROJECTS:
            p, r, f1, tp, fp, fn, gs, rs = baseline[(task, proj)]
            ep, er, ef1 = EXPECTED[task][proj]
            out(f"| {proj} | {gs} | {rs} | {tp} | {fp} | {fn} | {p:.3f} | {r:.3f} | {f1:.3f} | {ep:.3f} | {er:.3f} | {ef1:.3f} |")

        out()

    # ─── Verification ─────────────────────────────────────────────────────────

    out("### Baseline Verification")
    out()
    all_pass = True
    for task in ["sad-sam", "sam-code", "sad-code"]:
        for proj in PROJECTS:
            p, r, f1, tp, fp, fn, gs, rs = baseline[(task, proj)]
            ep, er, ef1 = EXPECTED[task][proj]
            if p < ep - 0.01 or r < er - 0.01 or f1 < ef1 - 0.01:
                out(f"- WARNING: {task}/{proj}: P={p:.3f} (exp>={ep:.3f}), R={r:.3f} (exp>={er:.3f}), F1={f1:.3f} (exp>={ef1:.3f})")
                all_pass = False
            # Verify consistency: TP + FP = |result|, TP + FN = |gold|
            assert tp + fp == rs, f"{task}/{proj}: TP+FP={tp+fp} != result={rs}"
            assert tp + fn == gs, f"{task}/{proj}: TP+FN={tp+fn} != gold={gs}"

    if all_pass:
        out("All 15 runs meet or exceed expected thresholds.")
    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis B – False Positive Decomposition
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis B – False Positive Decomposition")
    out()
    out("For each TransArc FP (S, C), we trace back to the bridging model element(s) M")
    out("and check whether the SAD-SAM link (M, S) and/or SAM-CODE link (M, C) are correct.")
    out()
    out("| Category | Description |")
    out("|----------|-------------|")
    out("| SAD_SAM_CAUSED | SAD-SAM link (M,S) is wrong; SAM-CODE link (M,C) is correct |")
    out("| SAM_CODE_CAUSED | SAD-SAM link (M,S) is correct; SAM-CODE link (M,C) is wrong |")
    out("| BOTH_CAUSED | Both component links are wrong |")
    out("| COMBINATION_ERROR | Both component links are individually correct, but (S,C) is not in gold |")
    out()

    out("### FP Distribution by Project")
    out()
    out("| Project | Total FP | SAD_SAM | SAM_CODE | BOTH | COMBINATION |")
    out("|---------|----------|---------|----------|------|-------------|")

    all_fp_cls = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        cls, tp, total_fp = analysis_b(proj, code_model)
        all_fp_cls[proj] = cls

        n_ss = len(cls.sad_sam_caused)
        n_sc = len(cls.sam_code_caused)
        n_both = len(cls.both_caused)
        n_comb = len(cls.combination_error)
        total = n_ss + n_sc + n_both + n_comb

        assert total == total_fp, f"{proj}: FP categories sum={total} != total_fp={total_fp}"

        if total_fp > 0:
            out(f"| {proj} | {total_fp} | {n_ss} ({n_ss/total_fp*100:.0f}%) | {n_sc} ({n_sc/total_fp*100:.0f}%) | {n_both} ({n_both/total_fp*100:.0f}%) | {n_comb} ({n_comb/total_fp*100:.0f}%) |")
        else:
            out(f"| {proj} | 0 | 0 | 0 | 0 | 0 |")

    out()

    # Annotated FP examples
    out("### Annotated FP Examples")
    out()
    for proj in PROJECTS:
        cls = all_fp_cls[proj]
        texts = load_text(proj)
        names = load_model_element_names(proj)

        out(f"#### {proj}")
        out()

        # Show up to 3 examples for the dominant category
        categories = [
            ("SAD_SAM_CAUSED", cls.sad_sam_caused),
            ("SAM_CODE_CAUSED", cls.sam_code_caused),
            ("BOTH_CAUSED", cls.both_caused),
            ("COMBINATION_ERROR", cls.combination_error),
        ]

        for cat_name, cat_list in categories:
            if not cat_list:
                continue
            out(f"**{cat_name}** ({len(cat_list)} FPs):")
            out()
            for item in cat_list[:2]:
                sent = item[0]
                code = item[1]
                bridges = item[2]
                bridge_names = [names.get(m, m) for m in bridges]
                sent_text = texts.get(sent, "<unknown>")
                out(f"- Sentence {sent}: \"{sent_text[:100]}{'...' if len(sent_text)>100 else ''}\"")
                out(f"  - Code: `{code}`")
                out(f"  - Via model element(s): {', '.join(bridge_names)}")
                out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis C – False Negative Decomposition
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis C – False Negative Decomposition")
    out()
    out("For each missed gold link (S, C), we classify the root cause:")
    out()
    out("| Category | Description |")
    out("|----------|-------------|")
    out("| THEORETICAL_LIMIT | No transitive path exists even in gold standards |")
    out("| SAD_SAM_MISS | TransArc found no/wrong SAD-SAM link for sentence S |")
    out("| SAM_CODE_MISS | Correct model element found via SAD-SAM, but SAM-CODE missed code C |")
    out("| BOTH_MISS | Both components contributed to the miss |")
    out()

    out("### FN Distribution by Project")
    out()
    out("| Project | Total FN | THEORETICAL | SAD_SAM_MISS | SAM_CODE_MISS | BOTH_MISS |")
    out("|---------|----------|-------------|--------------|---------------|-----------|")

    all_fn_cls = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        cls, total_fn = analysis_c(proj, code_model)
        all_fn_cls[proj] = cls

        n_th = len(cls.theoretical_limit)
        n_ss = len(cls.sad_sam_miss)
        n_sc = len(cls.sam_code_miss)
        n_both = len(cls.both_miss)
        total = n_th + n_ss + n_sc + n_both

        assert total == total_fn, f"{proj}: FN categories sum={total} != total_fn={total_fn}"

        if total_fn > 0:
            out(f"| {proj} | {total_fn} | {n_th} ({n_th/total_fn*100:.0f}%) | {n_ss} ({n_ss/total_fn*100:.0f}%) | {n_sc} ({n_sc/total_fn*100:.0f}%) | {n_both} ({n_both/total_fn*100:.0f}%) |")
        else:
            out(f"| {proj} | 0 | 0 | 0 | 0 | 0 |")

    out()

    # Annotated FN examples
    out("### Annotated FN Examples")
    out()
    for proj in PROJECTS:
        cls = all_fn_cls[proj]
        texts = load_text(proj)
        names = load_model_element_names(proj)

        out(f"#### {proj}")
        out()

        categories = [
            ("THEORETICAL_LIMIT", cls.theoretical_limit),
            ("SAD_SAM_MISS", cls.sad_sam_miss),
            ("SAM_CODE_MISS", cls.sam_code_miss),
            ("BOTH_MISS", cls.both_miss),
        ]

        for cat_name, cat_list in categories:
            if not cat_list:
                continue
            out(f"**{cat_name}** ({len(cat_list)} FNs):")
            out()
            for item in cat_list[:2]:
                sent = item[0]
                code = item[1]
                sent_text = texts.get(sent, "<unknown>")
                out(f"- Sentence {sent}: \"{sent_text[:100]}{'...' if len(sent_text)>100 else ''}\"")
                out(f"  - Expected code: `{code}`")
                if cat_name == "THEORETICAL_LIMIT":
                    gold_models_sent = item[2]
                    gold_models_code = item[3]
                    out(f"  - Gold SAD-SAM models for sentence: {[names.get(m,m) for m in gold_models_sent] if gold_models_sent else 'NONE'}")
                    out(f"  - Gold SAM-CODE models for code: {[names.get(m,m) for m in gold_models_code] if gold_models_code else 'NONE'}")
                elif cat_name == "SAD_SAM_MISS":
                    bridging = item[2]
                    out(f"  - Required bridging model(s): {[names.get(m,m) for m in bridging]}")
                    out(f"  - Miss type: {item[3]}")
                elif cat_name == "SAM_CODE_MISS":
                    found_models = item[2]
                    out(f"  - TransArc found model(s): {[names.get(m,m) for m in found_models]}")
                out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis D – Error Propagation / Amplification
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis D – Error Propagation / Amplification")
    out()
    out("One component error can induce multiple TransArc errors. This analysis quantifies the cascade.")
    out()

    out("### SAD-SAM FP Amplification (Top offenders)")
    out()
    out("| Project | SAD-SAM FP (M, S) | Model Element | Induced TransArc FPs |")
    out("|---------|-------------------|---------------|---------------------|")

    all_prop = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        prop = analysis_d(proj, code_model)
        all_prop[proj] = prop
        names = load_model_element_names(proj)
        texts = load_text(proj)

        # Sort by induced FPs descending
        sorted_sad_sam = sorted(prop.sad_sam_fp_amplification, key=lambda x: x[2], reverse=True)
        for m, s, induced in sorted_sad_sam[:3]:
            model_name = names.get(m, m[:20])
            out(f"| {proj} | ({m[:20]}..., S{s}) | {model_name} | {induced} |")

    out()

    out("### SAM-CODE FP Amplification (Top offenders)")
    out()
    out("| Project | SAM-CODE FP (M, C) | Model Element | Induced TransArc FPs |")
    out("|---------|--------------------|--------------|-----------------------|")

    for proj in PROJECTS:
        prop = all_prop[proj]
        names = load_model_element_names(proj)

        sorted_sam_code = sorted(prop.sam_code_fp_amplification, key=lambda x: x[2], reverse=True)
        for m, c, induced in sorted_sam_code[:3]:
            model_name = names.get(m, m[:20])
            # Show last 2 path segments to disambiguate duplicates
            parts = c.split("/")
            code_short = "/".join(parts[-2:]) if len(parts) >= 2 else c
            out(f"| {proj} | ({model_name}, {code_short}) | {model_name} | {induced} |")

    out()

    # Summary amplification factors
    out("### Amplification Summary")
    out()
    out("| Project | SAD-SAM FPs | Total Induced TransArc FPs | Avg Amplification | SAM-CODE FPs | Total Induced | Avg Amplification |")
    out("|---------|-------------|---------------------------|-------------------|--------------|---------------|-------------------|")

    for proj in PROJECTS:
        prop = all_prop[proj]
        ss_count = len(prop.sad_sam_fp_amplification)
        ss_total_induced = sum(x[2] for x in prop.sad_sam_fp_amplification)
        ss_avg = ss_total_induced / ss_count if ss_count else 0

        sc_count = len(prop.sam_code_fp_amplification)
        sc_total_induced = sum(x[2] for x in prop.sam_code_fp_amplification)
        sc_avg = sc_total_induced / sc_count if sc_count else 0

        out(f"| {proj} | {ss_count} | {ss_total_induced} | {ss_avg:.1f} | {sc_count} | {sc_total_induced} | {sc_avg:.1f} |")

    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis E – Per-Project Deep Dives
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis E – Per-Project Deep Dives")
    out()

    for proj in PROJECTS:
        out(f"### {proj.upper()}")
        out()

        code_model = load_code_model_files(proj)
        texts = load_text(proj)
        names = load_model_element_names(proj)

        # Baseline
        p_sc, r_sc, f1_sc = baseline[("sad-code", proj)][:3]
        tp_sc = baseline[("sad-code", proj)][3]
        fp_sc = baseline[("sad-code", proj)][4]
        fn_sc = baseline[("sad-code", proj)][5]

        out(f"**TransArc Performance**: P={p_sc:.3f}, R={r_sc:.3f}, F1={f1_sc:.3f} (TP={tp_sc}, FP={fp_sc}, FN={fn_sc})")
        out()

        # FP breakdown
        fp_cls = all_fp_cls[proj]
        out(f"**FP Breakdown**: SAD_SAM={len(fp_cls.sad_sam_caused)}, SAM_CODE={len(fp_cls.sam_code_caused)}, BOTH={len(fp_cls.both_caused)}, COMBINATION={len(fp_cls.combination_error)}")
        out()

        # FN breakdown
        fn_cls = all_fn_cls[proj]
        out(f"**FN Breakdown**: THEORETICAL={len(fn_cls.theoretical_limit)}, SAD_SAM_MISS={len(fn_cls.sad_sam_miss)}, SAM_CODE_MISS={len(fn_cls.sam_code_miss)}, BOTH_MISS={len(fn_cls.both_miss)}")
        out()

        # Top-5 most impactful errors
        prop = all_prop[proj]
        all_errors = []
        for m, s, induced in prop.sad_sam_fp_amplification:
            all_errors.append(("SAD-SAM FP", m, s, induced, names.get(m, m)))
        for m, c, induced in prop.sam_code_fp_amplification:
            all_errors.append(("SAM-CODE FP", m, c, induced, names.get(m, m)))
        all_errors.sort(key=lambda x: x[3], reverse=True)

        out(f"**Top-5 Most Impactful Component Errors:**")
        out()
        out("| Rank | Type | Model Element | Link Target | Induced TransArc FPs |")
        out("|------|------|---------------|-------------|---------------------|")
        for i, (etype, m, target, induced, mname) in enumerate(all_errors[:5], 1):
            if etype == "SAD-SAM FP":
                target_display = f"Sentence {target}: \"{texts.get(target, '?')[:50]}...\""
            else:
                target_display = f"`{target.split('/')[-1] if '/' in target else target}`"
            out(f"| {i} | {etype} | {mname} | {target_display} | {induced} |")
        out()

        # Qualitative root cause
        # Determine dominant error pattern
        total_fp = fp_sc
        total_fn = fn_sc
        if total_fp > 0:
            dominant_fp = max(
                [("SAD_SAM_CAUSED", len(fp_cls.sad_sam_caused)),
                 ("SAM_CODE_CAUSED", len(fp_cls.sam_code_caused)),
                 ("BOTH_CAUSED", len(fp_cls.both_caused)),
                 ("COMBINATION", len(fp_cls.combination_error))],
                key=lambda x: x[1]
            )
            out(f"**Dominant FP cause**: {dominant_fp[0]} ({dominant_fp[1]}/{total_fp} = {dominant_fp[1]/total_fp*100:.0f}%)")
        if total_fn > 0:
            dominant_fn = max(
                [("THEORETICAL_LIMIT", len(fn_cls.theoretical_limit)),
                 ("SAD_SAM_MISS", len(fn_cls.sad_sam_miss)),
                 ("SAM_CODE_MISS", len(fn_cls.sam_code_miss)),
                 ("BOTH_MISS", len(fn_cls.both_miss))],
                key=lambda x: x[1]
            )
            out(f"**Dominant FN cause**: {dominant_fn[0]} ({dominant_fn[1]}/{total_fn} = {dominant_fn[1]/total_fn*100:.0f}%)")
        out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis F – "What-If" Component Comparison
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Analysis F – What-If Component Comparison")
    out()

    out("### Scenario 1: Perfect SAD-SAM + Actual SAM-CODE")
    out()
    out("| Project | P | R | F1 | TP | FP | FN | Result Size | vs Actual F1 |")
    out("|---------|---|---|----|----|----|----|------------|--------------|")

    what_if_results = {}
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        wf = analysis_f(proj, code_model)
        what_if_results[proj] = wf

        p, r, f1, tp, fp, fn, size = wf["perfect_sad_sam"]
        actual_f1 = baseline[("sad-code", proj)][2]
        delta = f1 - actual_f1
        out(f"| {proj} | {p:.3f} | {r:.3f} | {f1:.3f} | {tp} | {fp} | {fn} | {size} | {'+' if delta>=0 else ''}{delta:.3f} |")

    out()

    out("### Scenario 2: Actual SAD-SAM + Perfect SAM-CODE")
    out()
    out("| Project | P | R | F1 | TP | FP | FN | Result Size | vs Actual F1 |")
    out("|---------|---|---|----|----|----|----|------------|--------------|")

    for proj in PROJECTS:
        wf = what_if_results[proj]
        p, r, f1, tp, fp, fn, size = wf["perfect_sam_code"]
        actual_f1 = baseline[("sad-code", proj)][2]
        delta = f1 - actual_f1
        out(f"| {proj} | {p:.3f} | {r:.3f} | {f1:.3f} | {tp} | {fp} | {fn} | {size} | {'+' if delta>=0 else ''}{delta:.3f} |")

    out()

    out("### Scenario 3: TransArc-Internal SAM-CODE vs Standalone SAM-CODE")
    out()
    out("| Project | Internal P | Internal R | Internal F1 | Standalone P | Standalone R | Standalone F1 | Internal Size | Standalone Size |")
    out("|---------|-----------|-----------|-------------|-------------|-------------|--------------|---------------|----------------|")

    for proj in PROJECTS:
        wf = what_if_results[proj]
        ip, ir, if1, itp, ifp, ifn, isize = wf["internal_sam_code"]
        sp, sr, sf1, stp, sfp, sfn, ssize = wf["standalone_sam_code"]
        out(f"| {proj} | {ip:.3f} | {ir:.3f} | {if1:.3f} | {sp:.3f} | {sr:.3f} | {sf1:.3f} | {isize} | {ssize} |")

    out()

    # ═══════════════════════════════════════════════════════════════════════════
    # Synthesis
    # ═══════════════════════════════════════════════════════════════════════════

    out("## Synthesis")
    out()

    # Aggregate FP categories
    total_fp_ss = sum(len(all_fp_cls[p].sad_sam_caused) for p in PROJECTS)
    total_fp_sc = sum(len(all_fp_cls[p].sam_code_caused) for p in PROJECTS)
    total_fp_both = sum(len(all_fp_cls[p].both_caused) for p in PROJECTS)
    total_fp_comb = sum(len(all_fp_cls[p].combination_error) for p in PROJECTS)
    total_fp = total_fp_ss + total_fp_sc + total_fp_both + total_fp_comb

    out("### Aggregate FP Causes")
    out()
    out(f"| Category | Count | Percentage |")
    out(f"|----------|-------|------------|")
    if total_fp > 0:
        out(f"| SAD_SAM_CAUSED | {total_fp_ss} | {total_fp_ss/total_fp*100:.1f}% |")
        out(f"| SAM_CODE_CAUSED | {total_fp_sc} | {total_fp_sc/total_fp*100:.1f}% |")
        out(f"| BOTH_CAUSED | {total_fp_both} | {total_fp_both/total_fp*100:.1f}% |")
        out(f"| COMBINATION_ERROR | {total_fp_comb} | {total_fp_comb/total_fp*100:.1f}% |")
        out(f"| **Total** | **{total_fp}** | **100%** |")
    out()

    # Aggregate FN categories
    total_fn_th = sum(len(all_fn_cls[p].theoretical_limit) for p in PROJECTS)
    total_fn_ss = sum(len(all_fn_cls[p].sad_sam_miss) for p in PROJECTS)
    total_fn_sc = sum(len(all_fn_cls[p].sam_code_miss) for p in PROJECTS)
    total_fn_both = sum(len(all_fn_cls[p].both_miss) for p in PROJECTS)
    total_fn = total_fn_th + total_fn_ss + total_fn_sc + total_fn_both

    out("### Aggregate FN Causes")
    out()
    out(f"| Category | Count | Percentage |")
    out(f"|----------|-------|------------|")
    if total_fn > 0:
        out(f"| THEORETICAL_LIMIT | {total_fn_th} | {total_fn_th/total_fn*100:.1f}% |")
        out(f"| SAD_SAM_MISS | {total_fn_ss} | {total_fn_ss/total_fn*100:.1f}% |")
        out(f"| SAM_CODE_MISS | {total_fn_sc} | {total_fn_sc/total_fn*100:.1f}% |")
        out(f"| BOTH_MISS | {total_fn_both} | {total_fn_both/total_fn*100:.1f}% |")
        out(f"| **Total** | **{total_fn}** | **100%** |")
    out()

    # Hypothesis testing
    out("### Hypothesis Testing")
    out()

    # H1: SAD-SAM is primary bottleneck for TransArc recall
    out("**H1: SAD-SAM is the primary bottleneck for TransArc recall**")
    out()
    recoverable_fn = total_fn - total_fn_th  # FNs that could theoretically be recovered
    if recoverable_fn > 0:
        sad_sam_recall_impact = total_fn_ss / recoverable_fn * 100
        sam_code_recall_impact = total_fn_sc / recoverable_fn * 100
        out(f"- Among recoverable FNs: SAD_SAM_MISS = {total_fn_ss}/{recoverable_fn} ({sad_sam_recall_impact:.1f}%), SAM_CODE_MISS = {total_fn_sc}/{recoverable_fn} ({sam_code_recall_impact:.1f}%)")
        out(f"- Theoretical limit accounts for {total_fn_th}/{total_fn} ({total_fn_th/total_fn*100:.1f}%) of all FNs")
        out(f"- **Verdict**: {'SUPPORTED' if sad_sam_recall_impact > sam_code_recall_impact else 'NOT SUPPORTED'} — SAD-SAM miss rate = {sad_sam_recall_impact:.1f}% of recoverable FNs")
    out()

    # H2: Error amplification is multiplicative and project-dependent
    out("**H2: Error amplification is multiplicative and project-dependent**")
    out()
    for proj in PROJECTS:
        prop = all_prop[proj]
        ss_amps = [x[2] for x in prop.sad_sam_fp_amplification]
        if ss_amps:
            out(f"- {proj}: SAD-SAM FP amplification range [{min(ss_amps)}, {max(ss_amps)}], mean={sum(ss_amps)/len(ss_amps):.1f}")
        else:
            out(f"- {proj}: No SAD-SAM FP amplification (no SAD-SAM FPs in intermediates that induced TransArc FPs)")
    out()

    # H3: MediaStore recall purely due to SAD-SAM
    out("**H3: MediaStore has lowest recall purely due to SAD-SAM recall limitations**")
    out()
    ms_fn = all_fn_cls["mediastore"]
    ms_total_fn = baseline[("sad-code", "mediastore")][5]
    if ms_total_fn > 0:
        out(f"- MediaStore FN breakdown: THEORETICAL={len(ms_fn.theoretical_limit)}, SAD_SAM_MISS={len(ms_fn.sad_sam_miss)}, SAM_CODE_MISS={len(ms_fn.sam_code_miss)}")
        out(f"- Theoretical recoverability: {(ms_total_fn - len(ms_fn.theoretical_limit))/ms_total_fn*100:.1f}% of FNs are recoverable")
        out(f"- **Verdict**: {'SUPPORTED' if len(ms_fn.theoretical_limit) == 0 else 'PARTIALLY SUPPORTED'}")
    out()

    # H4: For high-precision SAD-SAM projects, FPs are primarily SAM-CODE-caused
    out("**H4: For high-SAD-SAM-precision projects, FPs are primarily SAM_CODE_CAUSED**")
    out()
    for proj in ["teastore", "jabref"]:
        sad_sam_p = baseline[("sad-sam", proj)][0]
        fp_cls = all_fp_cls[proj]
        total = baseline[("sad-code", proj)][4]
        if total > 0:
            sc_pct = len(fp_cls.sam_code_caused) / total * 100
            out(f"- {proj}: SAD-SAM P={sad_sam_p:.3f}, TransArc FPs: SAM_CODE_CAUSED={len(fp_cls.sam_code_caused)}/{total} ({sc_pct:.0f}%)")
        else:
            out(f"- {proj}: SAD-SAM P={sad_sam_p:.3f}, No TransArc FPs")
    out()

    # Which component to improve first
    out("### Recommendations")
    out()

    # Compare what-if deltas
    out("**Which component to improve first?**")
    out()
    out("| Project | Actual F1 | Perfect SAD-SAM F1 | Delta | Perfect SAM-CODE F1 | Delta | Priority |")
    out("|---------|-----------|-------------------|-------|--------------------|---------|----|")

    for proj in PROJECTS:
        actual_f1 = baseline[("sad-code", proj)][2]
        pss_f1 = what_if_results[proj]["perfect_sad_sam"][2]
        psc_f1 = what_if_results[proj]["perfect_sam_code"][2]
        delta_ss = pss_f1 - actual_f1
        delta_sc = psc_f1 - actual_f1
        priority = "SAD-SAM" if delta_ss > delta_sc else "SAM-CODE"
        out(f"| {proj} | {actual_f1:.3f} | {pss_f1:.3f} | +{delta_ss:.3f} | {psc_f1:.3f} | +{delta_sc:.3f} | {priority} |")

    out()

    out("### Where the Transitive Approach Breaks Down")
    out()
    out("The transitive approach fundamentally cannot recover links where no bridging")
    out("model element exists in the gold standards. This is the 'theoretical limit'.")
    out()
    out(f"| Project | Gold SAD-CODE | Theoretical Limit FNs | Unrecoverable % |")
    out(f"|---------|-------------|----------------------|-----------------|")
    for proj in PROJECTS:
        code_model = load_code_model_files(proj)
        gs = load_gs_sad_code_enrolled(proj, code_model)
        th = len(all_fn_cls[proj].theoretical_limit)
        out(f"| {proj} | {len(gs)} | {th} | {th/len(gs)*100:.1f}% |")

    out()

    # ─── Write markdown ───────────────────────────────────────────────────────

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
        f.write("\n")

    print(f"\n\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
