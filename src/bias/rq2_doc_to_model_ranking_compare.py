#!/usr/bin/env python3
"""
RQ2 doc-to-model (SAD-SAM) — non-leaky Top-3 ranking comparison.

The existing doc-to-model pre-study (`rq2_doc_to_model_prestudy.py`) used a
Top-3 baseline that ranks architecture components by *gold-link count*. That
leaks the answer: the very signal a real system tries to predict is being
used to pick the trivial baseline. This runner re-runs the Top-3 idea with
two non-leaky candidate rankings:

  R1 — File count.
      Top-3 = the three components with the most enrolled files in the
      architecture model (i.e., from the SAM-CODE gold standard, treating
      it as a public component-structure inventory). Uses no SAD-SAM gold.
      This is the same model-structure signal the doc-to-code Top-3
      baseline uses.

  R2 — Name frequency in the doc.
      Count case-insensitive *substring* occurrences of each component's
      display name in the document text (one count per sentence in which
      the name appears at least once). Top-3 = the three components whose
      names appear in the most distinct sentences. Uses doc text but no
      gold links. This is a "naive grep" ranking.

      Matching rule (documented for reproducibility):
        - Component name is taken as the SAM-CODE `ae_name`. If the name
          contains `": "`, only the suffix after it is used (the on-disk
          format is `<TypeTag>: <DisplayName>`).
        - The name is lowercased and stripped. Sentences are lowercased.
        - For each (component, sentence) we check
          `display_name in sentence_text` (case-insensitive substring).
          Components whose normalized display name is shorter than 3
          characters are ignored to suppress noise.

For both R1 and R2 the prediction rule is the same as before: for every
GOLD sentence (sentences with >= 1 gold link), predict the chosen 3
components. Sentences with no gold links are not predicted on, matching the
existing pre-study so the numbers are directly comparable.

Per (ranking x project) we report:
  1. Micro F1 over (sentence, component) pairs.
  2. Per-component F1 (macro).
  3. Per-sentence F1 (macro, over gold sentences).
  4. Sentence coverage.
  5. Noise rate.

For reference we also re-run:
  - R0 = Top-3 by gold-link count (the existing leaky baseline).
  - Random = uniform (gold-sent x all-components) at gold density,
             seeded with `random.Random(42)`.

A diagnostic table lists the 3 selected components per (project, ranking),
and the overlap |R1 ∩ R0| / |R2 ∩ R0| per project.

Output: reports/RQ2_DOC_TO_MODEL_RANKING_COMPARE.md
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

# Shared loaders
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (  # noqa: E402
    PROJECTS,
    load_gs_sad_sam,
    load_gs_sam_code_raw,
    load_code_model_files,
    enroll_gold_standard,
    load_model_element_names,
    load_text,
    calc_metrics,
)

OUTPUT_MD = (
    Path(__file__).resolve().parent.parent.parent
    / "reports"
    / "RQ2_DOC_TO_MODEL_RANKING_COMPARE.md"
)

# Reproducibility
random.seed(42)
K = 3
MIN_NAME_LEN = 3  # ignore very short component display names for R2


# ─────────────────────────────────────────────────────────────────────────────
# Adapters and helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_doc_to_model_gold(project):
    """(sentence_str, component_id_str) pairs."""
    raw = load_gs_sad_sam(project)
    return {(sentence, model_id) for (model_id, sentence) in raw}


def display_name(raw_name):
    """Extract the human-readable display name from an `ae_name`.

    On-disk names are formatted as ``"<TypeTag>: <DisplayName>"`` or just
    ``"<DisplayName>"``. Returns the lowercase, whitespace-stripped
    display name.
    """
    name = raw_name
    if ": " in name:
        name = name.split(": ", 1)[1]
    return name.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# Rankings
# ─────────────────────────────────────────────────────────────────────────────

def rank_by_gold_link_count(gold):
    """R0 — Top-K by gold-link count (LEAKY; reference only)."""
    link_count = defaultdict(int)
    for _, c in gold:
        link_count[c] += 1
    ranked = sorted(link_count.items(), key=lambda x: (-x[1], x[0]))
    return [c for c, _ in ranked[:K]], dict(link_count)


def rank_by_file_count(component_ids, model_to_files):
    """R1 — Top-K by enrolled file count per component."""
    sizes = {c: len(model_to_files.get(c, set())) for c in component_ids}
    ranked = sorted(sizes.items(), key=lambda x: (-x[1], x[0]))
    return [c for c, _ in ranked[:K]], sizes


def rank_by_name_frequency(component_ids, names, text):
    """R2 — Top-K by case-insensitive substring count of display name in doc.

    Score = number of sentences in which the component's display name
    occurs as a case-insensitive substring (each sentence contributes at
    most 1 to the score, regardless of how many times the name occurs in
    that sentence). Components whose normalized display name is shorter
    than ``MIN_NAME_LEN`` are scored 0 (filtered).
    """
    # Pre-normalize sentences once.
    sent_texts = [t.lower() for t in text.values()]
    scores = {}
    for c in component_ids:
        raw = names.get(c, "")
        disp = display_name(raw)
        if len(disp) < MIN_NAME_LEN:
            scores[c] = 0
            continue
        scores[c] = sum(1 for s in sent_texts if disp in s)
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [c for c, _ in ranked[:K]], scores


# ─────────────────────────────────────────────────────────────────────────────
# Baselines
# ─────────────────────────────────────────────────────────────────────────────

def baseline_from_top(gold_sents, top_components):
    """Predict each top-K component for every gold sentence."""
    return {(s, c) for s in gold_sents for c in top_components}


def baseline_random(gold_sents, all_components, target_size, rng):
    sent_list = sorted(gold_sents)
    comp_list = sorted(all_components)
    if not sent_list or not comp_list:
        return set()
    result = set()
    attempts = 0
    cap = max(target_size * 10, 10)
    while len(result) < target_size and attempts < cap:
        s = rng.choice(sent_list)
        c = rng.choice(comp_list)
        result.add((s, c))
        attempts += 1
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Metric helpers
# ─────────────────────────────────────────────────────────────────────────────

def per_component_macro_f1(gold, result):
    gold_by_c = defaultdict(set)
    result_by_c = defaultdict(set)
    for s, c in gold:
        gold_by_c[c].add(s)
    for s, c in result:
        result_by_c[c].add(s)
    comps = set(gold_by_c) | set(result_by_c)
    if not comps:
        return 0.0
    f1s = []
    for c in comps:
        g = gold_by_c.get(c, set())
        r = result_by_c.get(c, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        if tp + fp + fn == 0:
            continue
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def per_sentence_macro_f1(gold, result):
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, c in gold:
        gold_by_s[s].add(c)
    for s, c in result:
        result_by_s[s].add(c)
    gold_sents = set(gold_by_s)
    if not gold_sents:
        return 0.0
    f1s = []
    for s in gold_sents:
        g = gold_by_s[s]
        r = result_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        fn = len(g - r)
        p = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * rc / (p + rc) if (p + rc) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def sentence_coverage(gold, result):
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, c in gold:
        gold_by_s[s].add(c)
    for s, c in result:
        result_by_s[s].add(c)
    sents = list(gold_by_s.keys())
    if not sents:
        return 0.0
    covered = sum(
        1 for s in sents if gold_by_s[s] & result_by_s.get(s, set())
    )
    return covered / len(sents)


def noise_rate(gold, result):
    gold_by_s = defaultdict(set)
    result_by_s = defaultdict(set)
    for s, c in gold:
        gold_by_s[s].add(c)
    for s, c in result:
        result_by_s[s].add(c)
    vals = []
    for s, r in result_by_s.items():
        g = gold_by_s.get(s, set())
        tp = len(g & r)
        fp = len(r - g)
        if tp + fp > 0:
            vals.append(fp / (tp + fp))
    return sum(vals) / len(vals) if vals else 0.0


def measure(name, prediction, gold):
    micro_f1 = calc_metrics(gold, prediction)[2]
    return {
        "name": name,
        "micro_f1": micro_f1,
        "comp_f1": per_component_macro_f1(gold, prediction),
        "sent_f1": per_sentence_macro_f1(gold, prediction),
        "coverage": sentence_coverage(gold, prediction),
        "noise": noise_rate(gold, prediction),
        "pred_size": len(prediction),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-project runner
# ─────────────────────────────────────────────────────────────────────────────

def run_project(project):
    print(f"\n=== {project} ===")
    gold = load_doc_to_model_gold(project)
    gold_sents = set(s for s, _ in gold)
    target_size = len(gold)

    names = load_model_element_names(project)            # ae_id -> ae_name
    component_ids = list(names.keys())
    text = load_text(project)                            # sent_id -> sentence

    # Build model->files via SAM-CODE enrollment (same as extreme_baseline).
    code_model = load_code_model_files(project)
    sam_code_enrolled = enroll_gold_standard(load_gs_sam_code_raw(project), code_model)
    model_to_files = defaultdict(set)
    for m, c in sam_code_enrolled:
        model_to_files[m].add(c)
    model_to_files = dict(model_to_files)

    # Rankings.
    r0_top, gold_count_map = rank_by_gold_link_count(gold)
    r1_top, file_size_map = rank_by_file_count(component_ids, model_to_files)
    r2_top, name_freq_map = rank_by_name_frequency(component_ids, names, text)

    # Predictions.
    rng = random.Random(42)
    random_pred = baseline_random(gold_sents, component_ids, target_size, rng)
    r0_pred = baseline_from_top(gold_sents, r0_top)
    r1_pred = baseline_from_top(gold_sents, r1_top)
    r2_pred = baseline_from_top(gold_sents, r2_top)

    rows = {
        "Random": measure("Random", random_pred, gold),
        "R0 (gold-link count, leaky)": measure("R0", r0_pred, gold),
        "R1 (file count)":             measure("R1", r1_pred, gold),
        "R2 (name freq in doc)":       measure("R2", r2_pred, gold),
    }

    print(f"  |gold|={len(gold)}, |components|={len(component_ids)}, "
          f"|gold sents|={len(gold_sents)}, |sentences|={len(text)}")
    print(f"  R0 picks: {[(c, names.get(c, c), gold_count_map.get(c, 0)) for c in r0_top]}")
    print(f"  R1 picks: {[(c, names.get(c, c), file_size_map.get(c, 0)) for c in r1_top]}")
    print(f"  R2 picks: {[(c, names.get(c, c), name_freq_map.get(c, 0)) for c in r2_top]}")
    for name, r in rows.items():
        print(f"  {name:>32}: micro_F1={r['micro_f1']:.3f} "
              f"comp_F1={r['comp_f1']:.3f} sent_F1={r['sent_f1']:.3f} "
              f"cov={r['coverage']:.3f} noise={r['noise']:.3f}")

    diag = {
        "r0_top": r0_top,
        "r1_top": r1_top,
        "r2_top": r2_top,
        "names": names,
        "gold_count_map": gold_count_map,
        "file_size_map": file_size_map,
        "name_freq_map": name_freq_map,
        "n_gold": len(gold),
        "n_components": len(component_ids),
        "n_gold_sents": len(gold_sents),
        "n_sentences": len(text),
    }
    return rows, diag


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

METRIC_ORDER = [
    ("micro_f1", "Micro F1 (sentence, component)"),
    ("comp_f1",  "Per-component F1 (macro)"),
    ("sent_f1",  "Per-sentence F1 (macro)"),
    ("coverage", "Sentence coverage"),
    ("noise",    "Noise rate"),
]

BASELINE_ORDER = [
    "Random",
    "R0 (gold-link count, leaky)",
    "R1 (file count)",
    "R2 (name freq in doc)",
]


def write_report(per_proj, diag):
    lines = []

    def out(s=""):
        lines.append(s)

    out("# RQ2 doc-to-model — non-leaky Top-3 ranking comparison (R1 vs R2)")
    out()
    out(
        "Companion to `RQ2_DOC_TO_MODEL_PRESTUDY.md`. The original "
        "doc-to-model Top-3 baseline ranks components by **gold-link "
        "count**, which leaks the answer. This report re-runs Top-3 with "
        "two non-leaky rankings and compares them to the leaky R0 "
        "(reference) and Random."
    )
    out()
    out("**Rankings.**")
    out()
    out(
        "- **R0 — Gold-link count (LEAKY, reference only).** Top-3 = the 3 "
        "components with the most gold (sentence, component) links."
    )
    out(
        "- **R1 — File count.** Top-3 = the 3 components with the most "
        "enrolled files in the architecture model (built from the "
        "SAM-CODE gold standard, used as a public component-structure "
        "inventory — no SAD-SAM gold used)."
    )
    out(
        "- **R2 — Name frequency in the doc.** Top-3 = the 3 components "
        "whose display names appear in the most distinct doc sentences. "
        "Matching rule: case-insensitive substring match of the lowercased "
        "display name (after the `\"<TypeTag>: \"` prefix is stripped, if "
        "present); each sentence contributes at most 1 to a component's "
        "score; components whose normalized display name is shorter than "
        f"{MIN_NAME_LEN} characters are filtered out."
    )
    out(
        "- **Random.** `random.Random(42)`; samples (sentence, component) "
        "pairs uniformly from `gold_sents x all_components` until the "
        "prediction count matches the gold link count."
    )
    out()
    out(
        "For all 3 ranking-based predictions (R0, R1, R2), the prediction "
        "rule is identical: for every **gold sentence** (sentence with "
        ">= 1 gold link) predict the chosen 3 components. Sentences with "
        "no gold links are not predicted on (matches the existing "
        "pre-study so numbers are directly comparable)."
    )
    out()

    # ──────────────────────────────────────────────────────────────────
    # 1. Per-baseline metric tables
    # ──────────────────────────────────────────────────────────────────
    out("## 1. Per-baseline metrics")
    out()
    for bl in BASELINE_ORDER:
        out(f"### 1.{BASELINE_ORDER.index(bl)+1} {bl}")
        out()
        header = "| Metric | " + " | ".join(PROJECTS) + " | **macro mean** |"
        sep = "|" + "---|" * (len(PROJECTS) + 2)
        out(header)
        out(sep)
        for key, label in METRIC_ORDER:
            vals = [per_proj[p][bl][key] for p in PROJECTS]
            mean = sum(vals) / len(vals)
            row = (
                f"| {label} | "
                + " | ".join(f"{v:.3f}" for v in vals)
                + f" | **{mean:.3f}** |"
            )
            out(row)
        out()

    # ──────────────────────────────────────────────────────────────────
    # 2. Head-to-head — micro F1 across all 4 baselines
    # ──────────────────────────────────────────────────────────────────
    out("## 2. Head-to-head: micro F1 (all baselines)")
    out()
    out(
        "| Project | Random | R0 (leaky) | R1 (file count) | "
        "R2 (name freq) |"
    )
    out("|---|---|---|---|---|")
    for p in PROJECTS:
        out(
            f"| {p} | {per_proj[p]['Random']['micro_f1']:.3f} | "
            f"{per_proj[p]['R0 (gold-link count, leaky)']['micro_f1']:.3f} | "
            f"{per_proj[p]['R1 (file count)']['micro_f1']:.3f} | "
            f"{per_proj[p]['R2 (name freq in doc)']['micro_f1']:.3f} |"
        )

    def mm(bl, key):
        return sum(per_proj[p][bl][key] for p in PROJECTS) / len(PROJECTS)

    out(
        f"| **macro mean** | **{mm('Random', 'micro_f1'):.3f}** | "
        f"**{mm('R0 (gold-link count, leaky)', 'micro_f1'):.3f}** | "
        f"**{mm('R1 (file count)', 'micro_f1'):.3f}** | "
        f"**{mm('R2 (name freq in doc)', 'micro_f1'):.3f}** |"
    )
    out()

    out("### 2b. Same head-to-head — per-component macro F1")
    out()
    out("| Project | Random | R0 (leaky) | R1 (file count) | R2 (name freq) |")
    out("|---|---|---|---|---|")
    for p in PROJECTS:
        out(
            f"| {p} | {per_proj[p]['Random']['comp_f1']:.3f} | "
            f"{per_proj[p]['R0 (gold-link count, leaky)']['comp_f1']:.3f} | "
            f"{per_proj[p]['R1 (file count)']['comp_f1']:.3f} | "
            f"{per_proj[p]['R2 (name freq in doc)']['comp_f1']:.3f} |"
        )
    out(
        f"| **macro mean** | **{mm('Random', 'comp_f1'):.3f}** | "
        f"**{mm('R0 (gold-link count, leaky)', 'comp_f1'):.3f}** | "
        f"**{mm('R1 (file count)', 'comp_f1'):.3f}** | "
        f"**{mm('R2 (name freq in doc)', 'comp_f1'):.3f}** |"
    )
    out()

    out("### 2c. Same head-to-head — sentence coverage")
    out()
    out("| Project | Random | R0 (leaky) | R1 (file count) | R2 (name freq) |")
    out("|---|---|---|---|---|")
    for p in PROJECTS:
        out(
            f"| {p} | {per_proj[p]['Random']['coverage']:.3f} | "
            f"{per_proj[p]['R0 (gold-link count, leaky)']['coverage']:.3f} | "
            f"{per_proj[p]['R1 (file count)']['coverage']:.3f} | "
            f"{per_proj[p]['R2 (name freq in doc)']['coverage']:.3f} |"
        )
    out(
        f"| **macro mean** | **{mm('Random', 'coverage'):.3f}** | "
        f"**{mm('R0 (gold-link count, leaky)', 'coverage'):.3f}** | "
        f"**{mm('R1 (file count)', 'coverage'):.3f}** | "
        f"**{mm('R2 (name freq in doc)', 'coverage'):.3f}** |"
    )
    out()

    # ──────────────────────────────────────────────────────────────────
    # 3. Diagnostic — which 3 components does each rule pick?
    # ──────────────────────────────────────────────────────────────────
    out("## 3. Diagnostic — selected Top-3 components per ranking")
    out()
    out(
        "Each cell lists the 3 selected components for the given "
        "(project, ranking). Format: ``display_name (rank_score)``. "
        "Score = gold-link count for R0, enrolled file count for R1, "
        "in-doc name-frequency (sentences-with-substring) for R2."
    )
    out()
    for p in PROJECTS:
        d = diag[p]
        out(f"### 3.{PROJECTS.index(p)+1} {p}")
        out()
        out("| Ranking | Pick #1 | Pick #2 | Pick #3 |")
        out("|---|---|---|---|")
        for label, top, score_map in [
            ("R0 (gold-link count)", d["r0_top"], d["gold_count_map"]),
            ("R1 (file count)",      d["r1_top"], d["file_size_map"]),
            ("R2 (name freq in doc)", d["r2_top"], d["name_freq_map"]),
        ]:
            cells = []
            for cid in top:
                disp = display_name(d["names"].get(cid, cid))
                score = score_map.get(cid, 0)
                cells.append(f"{disp} ({score})")
            while len(cells) < 3:
                cells.append("—")
            out(f"| {label} | {cells[0]} | {cells[1]} | {cells[2]} |")
        out()

    # ──────────────────────────────────────────────────────────────────
    # 4. Set overlap with R0
    # ──────────────────────────────────────────────────────────────────
    out("## 4. Set overlap with R0 (leaky reference)")
    out()
    out(
        "How many of R1's / R2's Top-3 picks are also in R0's Top-3? "
        "If |R1 ∩ R0| is consistently 3/3, file count is essentially "
        "equivalent to gold-link count as a ranking signal and R1 is the "
        "simpler swap. If the overlap is low, R1 picks may differ enough "
        "that the inflation pattern shifts."
    )
    out()
    out("| Project | |R1 ∩ R0| / 3 | |R2 ∩ R0| / 3 | |R1 ∩ R2| / 3 |")
    out("|---|---|---|---|")
    overlap_r1 = []
    overlap_r2 = []
    overlap_r1r2 = []
    for p in PROJECTS:
        d = diag[p]
        s0 = set(d["r0_top"])
        s1 = set(d["r1_top"])
        s2 = set(d["r2_top"])
        a = len(s1 & s0)
        b = len(s2 & s0)
        c = len(s1 & s2)
        overlap_r1.append(a)
        overlap_r2.append(b)
        overlap_r1r2.append(c)
        out(f"| {p} | {a}/3 | {b}/3 | {c}/3 |")
    out(
        f"| **mean** | **{sum(overlap_r1)/len(overlap_r1):.2f}/3** | "
        f"**{sum(overlap_r2)/len(overlap_r2):.2f}/3** | "
        f"**{sum(overlap_r1r2)/len(overlap_r1r2):.2f}/3** |"
    )
    out()

    # ──────────────────────────────────────────────────────────────────
    # 5. Verdict
    # ──────────────────────────────────────────────────────────────────
    out("## 5. Verdict")
    out()

    micro_rand = mm("Random", "micro_f1")
    micro_r0   = mm("R0 (gold-link count, leaky)", "micro_f1")
    micro_r1   = mm("R1 (file count)", "micro_f1")
    micro_r2   = mm("R2 (name freq in doc)", "micro_f1")
    mean_ovl_r1 = sum(overlap_r1) / len(overlap_r1)
    mean_ovl_r2 = sum(overlap_r2) / len(overlap_r2)

    def ratio(a, b):
        return a / b if b > 1e-9 else float("inf")

    out(
        f"**Q1 — Does R1 (file count) still expose the popularity-skew bias?** "
        f"R1 mean micro F1 = **{micro_r1:.3f}** vs Random "
        f"**{micro_rand:.3f}** ({ratio(micro_r1, micro_rand):.1f}x). "
        f"{'Yes — it inflates Top-3 well above Random.' if micro_r1 > 2 * micro_rand else 'Only weakly — gap is too narrow to expose the bias.'}"
    )
    out()
    out(
        f"**Q2 — Does R2 (name frequency) still expose it?** "
        f"R2 mean micro F1 = **{micro_r2:.3f}** vs Random "
        f"**{micro_rand:.3f}** ({ratio(micro_r2, micro_rand):.1f}x). "
        f"{'Yes — R2 also inflates Top-3 above Random.' if micro_r2 > 2 * micro_rand else 'Only weakly — gap is too narrow to expose the bias.'}"
    )
    out()

    diff_r1 = abs(micro_r1 - micro_r0)
    diff_r2 = abs(micro_r2 - micro_r0)
    closer = "R1" if diff_r1 < diff_r2 else "R2"
    out(
        f"**Q3 — Which is closer to R0 (leaky reference, {micro_r0:.3f})?** "
        f"R1 sits at **{micro_r1:.3f}** (|R1-R0| = {diff_r1:.3f}); "
        f"R2 sits at **{micro_r2:.3f}** (|R2-R0| = {diff_r2:.3f}). "
        f"**{closer}** is closer to R0 in macro mean micro F1."
    )
    out()
    out(
        f"**Q4 — Overlap with R0's picks.** Mean |R1 ∩ R0| = "
        f"**{mean_ovl_r1:.2f}/3**, mean |R2 ∩ R0| = **{mean_ovl_r2:.2f}/3**. "
        f"{'R1 nearly matches R0 — file count is essentially equivalent to gold-link count as a ranking signal, so R1 is fine as a drop-in non-leaky swap and we do not need R2.' if mean_ovl_r1 >= 2.0 else 'R1 differs noticeably from R0 — R2 may be a better proxy for the leaky baseline.'}"
    )
    out()

    # Recommendation
    r1_inflates = micro_r1 > 2 * micro_rand
    r2_inflates = micro_r2 > 2 * micro_rand
    if r1_inflates and mean_ovl_r1 >= 2.0:
        rec = (
            "**Use R1 (file count).** It exposes the popularity-skew bias "
            "cleanly, lands close to R0 in macro mean micro F1, and its "
            "Top-3 picks overlap heavily with R0 — i.e., file count is a "
            "good non-leaky proxy for gold-link count as a ranking signal. "
            "Simpler than R2 (no text matching needed) and matches the "
            "doc-to-code Top-3 baseline's signal source, which keeps the "
            "two pre-studies methodologically aligned."
        )
    elif r1_inflates and not r2_inflates:
        rec = "**Use R1 (file count).** R2 does not inflate Top-3 above Random."
    elif not r1_inflates and r2_inflates:
        rec = "**Use R2 (name frequency).** R1 fails to inflate Top-3 above Random."
    elif r1_inflates and r2_inflates:
        rec = (
            "**Use R1 (file count).** Both R1 and R2 expose the bias; "
            "R1 is the simpler, leak-free choice and aligns with the "
            "doc-to-code pre-study's signal source. R2 can be cited in a "
            "footnote as a secondary check."
        )
    else:
        rec = (
            "**Neither R1 nor R2 cleanly exposes the bias.** Consider "
            "alternative non-leaky rankings (e.g., name length, "
            "alphabetical, dependency count)."
        )
    out(f"**Q5 — Final recommendation.** {rec}")
    out()

    out("---")
    out("")
    out(
        "Script: `src/bias/rq2_doc_to_model_ranking_compare.py`. "
        "Reproduce: `python3 src/bias/rq2_doc_to_model_ranking_compare.py`."
    )
    out("")

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"\nWrote {OUTPUT_MD}")


def main():
    per_proj = {}
    diag = {}
    for p in PROJECTS:
        rows, d = run_project(p)
        per_proj[p] = rows
        diag[p] = d
    write_report(per_proj, diag)


if __name__ == "__main__":
    main()
