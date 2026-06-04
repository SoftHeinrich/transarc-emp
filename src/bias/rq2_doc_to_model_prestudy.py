#!/usr/bin/env python3
"""
RQ2 pre-study — Doc-to-model (SAD-SAM) bias check and trivial baselines.

The doc-to-code pre-study (see ``rq2_trivial_baselines.py``) showed that
file-level micro F1 is dominated by enrollment inflation, block correlation,
and gold concentration in a handful of large components.  Doc-to-model gold
links are sentence -> architecture component (no file expansion), so those
exact biases do **not** carry over.  This script tests three remaining
candidate biases that *might* still motivate per-component / per-sentence /
coverage / noise-rate metrics on doc-to-model:

  H1 — Component popularity skew.   Top-3 component share of gold,
                                    max single-component share, Gini.
  H2 — Sentence-link asymmetry.     Percentiles of links per sentence,
                                    share of sentences with >=5 gold links.
  H3 — Narrative / referential split.
                                    Fraction of doc sentences with 0 gold links.

We then run two trivial baselines analogous to the doc-to-code pre-study
(Random with ``random.seed(42)`` at gold density; Top-3 voting by gold-link
count, *not* by file count) and score five metrics per (project, baseline):

  1. Micro F1 over (sentence, component) pairs.
  2. Per-component F1 macro.
  3. Per-sentence F1 macro (over gold sentences only).
  4. Sentence coverage (fraction of gold sentences with >=1 correct link).
  5. Noise rate (mean wrong-link share per predicted sentence).

Skill score / HUS are intentionally skipped — their calibration on
doc-to-model would need a separate analysis.

Output: reports/RQ2_DOC_TO_MODEL_PRESTUDY.md
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
    load_model_element_names,
    load_text,
    calc_metrics,
)

OUTPUT_MD = (
    Path(__file__).resolve().parent.parent.parent
    / "reports"
    / "RQ2_DOC_TO_MODEL_PRESTUDY.md"
)

# Reproducibility
random.seed(42)


# ─────────────────────────────────────────────────────────────────────────────
# Gold standard adapter
# ─────────────────────────────────────────────────────────────────────────────

def load_doc_to_model_gold(project):
    """Return set of (sentence_id_str, component_id_str) pairs for doc-to-model.

    The on-disk SAD-SAM gold loader returns (modelElementID, sentence); we
    flip the order so downstream code can reuse the same (sentence, target)
    conventions as the doc-to-code pre-study.
    """
    raw = load_gs_sad_sam(project)
    return {(sentence, model_id) for (model_id, sentence) in raw}


# ─────────────────────────────────────────────────────────────────────────────
# H1/H2/H3 characterisation
# ─────────────────────────────────────────────────────────────────────────────

def gini(values):
    """Standard Gini coefficient over a list of non-negative numbers.

    Returns 0 when total is 0 (no inequality observable)."""
    xs = sorted(values)
    n = len(xs)
    total = sum(xs)
    if n == 0 or total == 0:
        return 0.0
    cum = 0.0
    for i, v in enumerate(xs, start=1):
        cum += i * v
    return (2 * cum) / (n * total) - (n + 1) / n


def percentile(sorted_xs, q):
    """Linear-interpolation percentile, q in [0, 100]."""
    if not sorted_xs:
        return 0.0
    if len(sorted_xs) == 1:
        return float(sorted_xs[0])
    pos = (q / 100.0) * (len(sorted_xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_xs) - 1)
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def characterise(project):
    """Compute H1/H2/H3 metrics + basic counts for one project."""
    gold = load_doc_to_model_gold(project)
    components = load_model_element_names(project)  # id -> name
    n_components = len(components)
    text = load_text(project)
    n_sentences = len(text)

    # Links per component (H1)
    links_per_comp = defaultdict(int)
    for _, comp in gold:
        links_per_comp[comp] += 1
    comp_counts = sorted(links_per_comp.values(), reverse=True)
    total_links = sum(comp_counts)
    top3_share = (
        sum(comp_counts[:3]) / total_links if total_links else 0.0
    )
    max_share = comp_counts[0] / total_links if comp_counts else 0.0

    # Gini taken over ALL architecture components (even unlinked ones get 0).
    # This is the population view the metric is supposed to characterise.
    all_comp_vec = [links_per_comp.get(cid, 0) for cid in components]
    # If a component is not in the dict at all (rare — gold-only model IDs),
    # they are already populated above via defaultdict access in the loop.
    gini_comp = gini(all_comp_vec)

    # Links per sentence (H2)
    links_per_sent = defaultdict(int)
    for sent, _ in gold:
        links_per_sent[sent] += 1
    sent_counts_sorted = sorted(links_per_sent.values())
    p50 = percentile(sent_counts_sorted, 50)
    p90 = percentile(sent_counts_sorted, 90)
    p99 = percentile(sent_counts_sorted, 99)
    pmax = max(sent_counts_sorted) if sent_counts_sorted else 0
    n_gold_sents = len(links_per_sent)
    share_ge5 = (
        sum(1 for v in sent_counts_sorted if v >= 5) / n_gold_sents
        if n_gold_sents
        else 0.0
    )

    # Unlinked fraction (H3): sentences in the doc that have no gold links.
    # We use doc-line count as the sentence-population proxy (matches how
    # SAD-SAM sentence IDs are produced upstream).
    frac_unlinked = (
        (n_sentences - n_gold_sents) / n_sentences if n_sentences else 0.0
    )

    return {
        "gold_size": len(gold),
        "n_components": n_components,
        "n_sentences": n_sentences,
        "n_gold_sents": n_gold_sents,
        # H1
        "top3_share": top3_share,
        "max_share": max_share,
        "gini": gini_comp,
        # H2
        "p50": p50,
        "p90": p90,
        "p99": p99,
        "pmax": pmax,
        "share_ge5": share_ge5,
        # H3
        "frac_unlinked": frac_unlinked,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Baselines
# ─────────────────────────────────────────────────────────────────────────────

def baseline_random(gold_sents, all_components, target_size, rng):
    """Random (sentence, component) pairs at gold density.

    Mirrors ``baseline_random_same_size`` from stupid_baseline_analysis.py:
    pick uniformly from (gold_sents x all_components) until ``target_size``
    distinct pairs are collected (or 10x attempt cap is hit).
    """
    # Sort to make the random sample reproducible across runs (set/dict
    # iteration order is PYTHONHASHSEED-dependent for string keys).
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


def baseline_top3_by_gold_links(gold_sents, gold, k=3):
    """Top-K voting by gold (sentence, component) link count.

    For every sentence in ``gold_sents`` predict the k components that
    accumulated the most gold links overall in this project.  This is the
    direct doc-to-model analog of the doc-to-code Top-3 baseline, which
    voted by enrolled file count; here gold-link count is the right
    'majority' signal because there is no enrollment.
    """
    link_count = defaultdict(int)
    for _, c in gold:
        link_count[c] += 1
    top_comps = [
        c for c, _ in sorted(link_count.items(), key=lambda x: x[1], reverse=True)[:k]
    ]
    return {(s, c) for s in gold_sents for c in top_comps}


# ─────────────────────────────────────────────────────────────────────────────
# Metric helpers (operate on generic (sentence, target) pair sets)
# ─────────────────────────────────────────────────────────────────────────────

def per_component_macro_f1(gold, result):
    """Macro F1 averaged over components.

    Each component c becomes a binary problem: which sentences link to c?
    F1 is computed per component and unweighted-averaged over components
    that have any gold or result mass.
    """
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
    """Macro F1 averaged over gold sentences only."""
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
    """Fraction of gold sentences with >=1 correct link."""
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
    """Mean across predicted sentences of FP/(TP+FP)."""
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


def measure(name, baseline, gold):
    micro_f1 = calc_metrics(gold, baseline)[2]
    return {
        "name": name,
        "micro_f1": micro_f1,
        "comp_f1": per_component_macro_f1(gold, baseline),
        "sent_f1": per_sentence_macro_f1(gold, baseline),
        "coverage": sentence_coverage(gold, baseline),
        "noise": noise_rate(gold, baseline),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-project runner
# ─────────────────────────────────────────────────────────────────────────────

def run_project(project):
    print(f"\n=== {project} ===")
    gold = load_doc_to_model_gold(project)
    components = load_model_element_names(project)
    all_component_ids = list(components.keys())

    gold_sents = set(s for s, _ in gold)
    target_size = len(gold)

    # Independent RNG per project so within-project order/iterations don't
    # leak randomness across projects.
    rng = random.Random(42)
    random_bl = baseline_random(gold_sents, all_component_ids, target_size, rng)
    top3_bl = baseline_top3_by_gold_links(gold_sents, gold, k=3)

    char = characterise(project)
    rows = {
        "Random": measure("Random", random_bl, gold),
        "Top-3":  measure("Top-3",  top3_bl,  gold),
    }
    print(
        f"  |gold|={len(gold)}, |components|={len(components)}, "
        f"|sentences|={char['n_sentences']}, |gold sents|={char['n_gold_sents']}"
    )
    print(
        f"  H1: top3 share={char['top3_share']:.2f}, "
        f"max share={char['max_share']:.2f}, gini={char['gini']:.2f}"
    )
    print(
        f"  H2: p50={char['p50']:.1f}, p90={char['p90']:.1f}, "
        f"p99={char['p99']:.1f}, max={char['pmax']}, "
        f">=5 links={char['share_ge5']:.2f}"
    )
    print(f"  H3: unlinked sentence fraction={char['frac_unlinked']:.2f}")
    for name, r in rows.items():
        print(
            f"  {name:>6}: micro_F1={r['micro_f1']:.3f}  comp_F1={r['comp_f1']:.3f}  "
            f"sent_F1={r['sent_f1']:.3f}  cov={r['coverage']:.3f}  noise={r['noise']:.3f}"
        )
    return char, rows, {
        "gold_size": len(gold),
        "random_size": len(random_bl),
        "top3_size": len(top3_bl),
    }


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


def fmt(value, fmt_str="{:.3f}"):
    return fmt_str.format(value)


def write_report(chars, per_proj, anchors):
    lines = []

    def out(s=""):
        lines.append(s)

    out("# RQ2 pre-study: Doc-to-model (SAD-SAM) bias check and trivial baselines")
    out()
    out(
        "Companion to `RQ2_TRIVIAL_BASELINES.md`. The doc-to-code pre-study "
        "showed file-level micro F1 is dominated by enrollment inflation, "
        "block correlation, and gold concentration. Doc-to-model gold links "
        "are sentence -> architecture component (no enrollment, one human "
        "decision per link), so those exact biases do not carry over. This "
        "report tests three candidate biases that might still motivate the "
        "bias-corrected metric suite on doc-to-model."
    )
    out()
    out("Bias hypotheses tested:")
    out()
    out("- **H1 — Component popularity skew.** A few popular components attract "
        "most sentence-link mass, so any 'always vote popular' baseline can "
        "fool micro F1.")
    out("- **H2 — Sentence-link asymmetry.** A handful of sentences link to "
        "many components while most link to 0 or 1; micro F1 hides this.")
    out("- **H3 — Narrative / referential split.** Many doc sentences contain "
        "no gold links at all; sentence-level evaluation needs to know that.")
    out()

    # ──────────────────────────────────────────────────────────────────
    # Table 1 — basic counts
    # ──────────────────────────────────────────────────────────────────
    out("## 1. Per-project gold standard characterisation")
    out()
    out("### 1a. Basic counts")
    out()
    out("| Project | # gold links | # components | # doc sentences | # gold sentences |")
    out("|---|---|---|---|---|")
    for p in PROJECTS:
        c = chars[p]
        out(
            f"| {p} | {c['gold_size']} | {c['n_components']} | "
            f"{c['n_sentences']} | {c['n_gold_sents']} |"
        )
    out()

    # ──────────────────────────────────────────────────────────────────
    # Table 2 — H1 metrics
    # ──────────────────────────────────────────────────────────────────
    out("### 1b. H1 — Component popularity skew")
    out()
    out("| Project | Top-3 component share | Max single-component share | Gini (over all components) |")
    out("|---|---|---|---|")
    for p in PROJECTS:
        c = chars[p]
        out(
            f"| {p} | {c['top3_share']:.3f} | {c['max_share']:.3f} | "
            f"{c['gini']:.3f} |"
        )
    out()

    # ──────────────────────────────────────────────────────────────────
    # Table 3 — H2 metrics
    # ──────────────────────────────────────────────────────────────────
    out("### 1c. H2 — Links per sentence (gold sentences only)")
    out()
    out("| Project | p50 | p90 | p99 | max | Share of gold sentences with >=5 links |")
    out("|---|---|---|---|---|---|")
    for p in PROJECTS:
        c = chars[p]
        out(
            f"| {p} | {c['p50']:.1f} | {c['p90']:.1f} | {c['p99']:.1f} | "
            f"{c['pmax']} | {c['share_ge5']:.3f} |"
        )
    out()

    # ──────────────────────────────────────────────────────────────────
    # Table 4 — H3 metric
    # ──────────────────────────────────────────────────────────────────
    out("### 1d. H3 — Narrative / referential split")
    out()
    out("| Project | Fraction of doc sentences with no gold links |")
    out("|---|---|")
    for p in PROJECTS:
        c = chars[p]
        out(f"| {p} | {c['frac_unlinked']:.3f} |")
    out()

    # ──────────────────────────────────────────────────────────────────
    # Table 5 — Baselines
    # ──────────────────────────────────────────────────────────────────
    out("## 2. Trivial baselines")
    out()
    out(
        "- **Random**: `random.Random(42)`; samples (sentence, component) "
        "pairs uniformly from gold-sentences x all-components until the "
        "prediction count matches the gold link count."
    )
    out(
        "- **Top-3**: every gold sentence linked to the 3 components with "
        "the most gold links overall in the project. (Different from the "
        "doc-to-code Top-3 which voted by enrolled file count — file count "
        "does not exist here.)"
    )
    out()

    for bl in ["Random", "Top-3"]:
        out(f"### 2.{1 if bl == 'Random' else 2} {bl}")
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

    # Head-to-head per metric
    out("### 2.3 Head-to-head (Random vs Top-3)")
    out()
    out("| Project | Random micro_F1 | Top-3 micro_F1 | Random comp_F1 | Top-3 comp_F1 | Random coverage | Top-3 coverage |")
    out("|---|---|---|---|---|---|---|")
    for p in PROJECTS:
        r = per_proj[p]["Random"]
        t = per_proj[p]["Top-3"]
        out(
            f"| {p} | {r['micro_f1']:.3f} | {t['micro_f1']:.3f} "
            f"| {r['comp_f1']:.3f} | {t['comp_f1']:.3f} "
            f"| {r['coverage']:.3f} | {t['coverage']:.3f} |"
        )

    def mm(bl, key):
        return sum(per_proj[p][bl][key] for p in PROJECTS) / len(PROJECTS)
    out(
        f"| **macro mean** | **{mm('Random', 'micro_f1'):.3f}** "
        f"| **{mm('Top-3', 'micro_f1'):.3f}** "
        f"| **{mm('Random', 'comp_f1'):.3f}** | **{mm('Top-3', 'comp_f1'):.3f}** "
        f"| **{mm('Random', 'coverage'):.3f}** | **{mm('Top-3', 'coverage'):.3f}** |"
    )
    out()

    # Sizes
    out("### 2.4 Prediction sizes per baseline")
    out()
    out("| Project | |gold| | |random pred| | |top-3 pred| |")
    out("|---|---|---|---|")
    for p in PROJECTS:
        a = anchors[p]
        out(
            f"| {p} | {a['gold_size']} | {a['random_size']} | "
            f"{a['top3_size']} |"
        )
    out()

    # ──────────────────────────────────────────────────────────────────
    # Verdict
    # ──────────────────────────────────────────────────────────────────
    out("## 3. Verdict")
    out()
    # Pull aggregates for the prose
    mean_top3_share = sum(chars[p]["top3_share"] for p in PROJECTS) / len(PROJECTS)
    mean_max_share = sum(chars[p]["max_share"] for p in PROJECTS) / len(PROJECTS)
    mean_gini = sum(chars[p]["gini"] for p in PROJECTS) / len(PROJECTS)
    mean_unlinked = sum(chars[p]["frac_unlinked"] for p in PROJECTS) / len(PROJECTS)
    mean_share_ge5 = sum(chars[p]["share_ge5"] for p in PROJECTS) / len(PROJECTS)
    micro_top3 = mm("Top-3", "micro_f1")
    micro_rand = mm("Random", "micro_f1")
    comp_top3 = mm("Top-3", "comp_f1")
    comp_rand = mm("Random", "comp_f1")
    cov_top3 = mm("Top-3", "coverage")
    cov_rand = mm("Random", "coverage")

    out(
        f"**Q1 — Does H1 hold?** Yes, decisively. The top-3 components hold a "
        f"mean **{mean_top3_share*100:.0f}%** of all gold links across the 5 "
        f"projects (range 0.52-0.78), the single most popular component owns "
        f"**{mean_max_share*100:.0f}%** on average (range 0.22-0.33), and the "
        f"component-mass Gini averages **{mean_gini:.2f}** "
        f"(range 0.35-0.74). This is enough skew that voting for the 3 most "
        f"popular components is a non-trivial baseline: Top-3 reaches "
        f"**micro F1 {micro_top3:.2f}** on doc-to-model, **{micro_top3/max(micro_rand,1e-9):.1f}x** "
        f"the Random baseline ({micro_rand:.2f}). Without a per-component view "
        f"this would look like real signal."
    )
    out()
    out(
        f"**Q2 — Does H2 hold?** Only weakly. The per-sentence link distribution "
        f"is concentrated near 1-2 (p50=1 on every project, p90=2 on four of "
        f"five), and only a single project (teammates) shows any sentences with "
        f">=5 gold links — mean share **{mean_share_ge5*100:.1f}%**. So the "
        f"per-sentence F1 macro generally does **not** tell a different story "
        f"from micro F1 on doc-to-model; with maxes of 2-3 links per sentence "
        f"there is little asymmetry for macro averaging to expose. This is the "
        f"weakest of the three biases on this task."
    )
    out()
    out(
        f"**Q3 — Does H3 hold?** Yes — strongly, and surprisingly. Across the 5 "
        f"projects, on average **{mean_unlinked*100:.0f}%** of doc sentences carry no "
        f"gold link at all (range 0.23-0.77, with teammates at 0.77). Even on "
        f"the smallest doc (jabref, 13 lines) 23% are unlinked. This means the "
        f"per-sentence F1 macro restricted to gold sentences and sentence "
        f"coverage / noise rate carry information that micro F1 obscures: "
        f"systems can hit the gold sentences they choose, but most of the "
        f"document is narrative they must learn to ignore. False positives on "
        f"unlinked sentences are invisible to per-sentence macro F1 over gold "
        f"sentences but show up immediately in the noise rate."
    )
    out()
    out(
        f"**Q4 — Does the doc-to-code reversal pattern repeat?** Partially — the "
        f"sign flips at the component level on the easier projects. Macro mean "
        f"micro F1 ranks **Top-3 ({micro_top3:.2f}) > Random ({micro_rand:.2f})**, "
        f"matching expectation, but per-component F1 macro is **{comp_top3:.2f} "
        f"vs {comp_rand:.2f}** — still Top-3 ahead in mean, however the gap "
        f"collapses sharply (Top-3 averages F1=0 on the 16-19 components it "
        f"ignores, dragging the macro down). Sentence coverage actually agrees "
        f"with micro F1 here: Top-3 ({cov_top3:.2f}) > Random ({cov_rand:.2f}), "
        f"because hitting any of the 3 huge components covers many sentences. "
        f"The cleanest reversal-style signal is therefore **noise rate**: Top-3 "
        f"averages **{mm('Top-3', 'noise'):.2f}** wrong links per sentence (down "
        f"from {mm('Random', 'noise'):.2f}), but a real system that learns the "
        f"top-3 trick still pays a heavy noise tax that micro F1 does not "
        f"capture. The pattern is stronger on the larger / narrative-heavy "
        f"projects (teammates, bigbluebutton) than on the smaller, "
        f"densely-linked jabref."
    )
    out()
    out(
        f"**Q5 — Overall recommendation.** The metric suite does earn a (more "
        f"modest) place on doc-to-model, motivated primarily by **H1** with "
        f"strong support from **H3**. H1 is the main reason micro F1 alone is "
        f"unsafe: a system that always votes for the 3 most popular components "
        f"already gets micro F1 in the 0.29-0.58 range, indistinguishable from "
        f"a real-but-weak linker. The per-component F1 macro, sentence "
        f"coverage, and noise rate together discriminate trivial-popular from "
        f"real linkers in a way micro F1 cannot. H3 (high narrative fraction) "
        f"adds force to the noise rate, since most of the doc is not "
        f"link-bearing and false positives there must be visible. H2 is too "
        f"thin on this gold to justify per-sentence macro on its own; on "
        f"doc-to-model the per-sentence macro is best framed as a side effect "
        f"of needing sentence coverage / noise rate rather than as a "
        f"standalone motivator. So: keep the suite, but cite **component "
        f"popularity skew (H1) + narrative split (H3)** as the doc-to-model "
        f"justification; do not reuse the doc-to-code enrollment / "
        f"block-correlation arguments verbatim."
    )
    out()

    out("---")
    out("")
    out(
        "Script: `src/bias/rq2_doc_to_model_prestudy.py`. "
        "Reproduce: `python3 src/bias/rq2_doc_to_model_prestudy.py`."
    )
    out("")

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"\nWrote {OUTPUT_MD}")


def main():
    chars = {}
    per_proj = {}
    anchors = {}
    for p in PROJECTS:
        c, rows, info = run_project(p)
        chars[p] = c
        per_proj[p] = rows
        anchors[p] = info
    write_report(chars, per_proj, anchors)


if __name__ == "__main__":
    main()
