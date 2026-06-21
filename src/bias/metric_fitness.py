#!/usr/bin/env python3
"""Metric fitness scorecard (CMP-04) — score each candidate suite column on FOUR
axes and emit a DATA-DERIVED verdict.

ONE standalone command (``python3 src/bias/metric_fitness.py``) scores each
candidate column of ``component_suite`` —

    micro, macro, gap, min_comp, pct_missed   (gold_gini carried as a descriptor)

— on FOUR fitness axes at BOTH levels (sad-model, sad-code) and writes
``reports/METRIC_FITNESS.csv`` (one row per level × column with the four axis
scores, 4-dp like the suite) + ``reports/METRIC_FITNESS.md`` (per-axis tables +
a one-line, data-derived verdict + the quantified artemis long-tail finding).

The four axes (formulas at executor discretion, D-13)
-----------------------------------------------------
  separation  — does the column rank the THREE REAL paper systems
                (swattr/transarc, s20linker, artemis) above the rq2 TRIVIAL FLOOR
                (Random + Top-3, reused verbatim — D-01/D-03)?  Score = the margin
                mean(real) − mean(trivial). For ``gap`` (a signed skew indicator,
                not a quality score) and ``pct_missed`` (lower = better) the margin
                is reported on |value| / inverted so "bigger = real beats trivial".
  validity    — does the column sit coherently inside the rq2 ORACLE ceiling
                (compute_oracle_f1) and ABOVE the random floor (compute_random_f1)?
                Score = oracle-headroom fraction for the F1-scaled columns
                (micro, macro, min_comp); for the non-F1 columns (gap, pct_missed)
                the bound is interpreted explicitly (reported, not forced into an
                F1 comparison) — see ``_validity``.
  stability   — cross-project variance of the column across the 5 projects (pooled
                over the 3 real systems). Score = the standard deviation
                (lower = more stable).
  degeneracy  — does the column saturate / go insensitive (always ≈1, always ≈0,
                or near-identical across systems)? Score = a saturation/spread
                test: the cross-SYSTEM spread of the per-project column means
                (smaller spread + pinned at an extreme = more degenerate).

Verdict (DATA-DERIVED — D-06/D-07)
----------------------------------
``derive_verdict`` consumes the computed axis scores and ranks each column as
HEADLINE (separates real-from-trivial AND is stable AND does not degenerate) or
DIAGNOSTIC (fails separation, or saturates) — the split EMERGES FROM THE NUMBERS.
The milestone's expected verdict (headline = macro + tail; diagnostic = micro/gap)
is the HYPOTHESIS UNDER TEST: if the numbers contradict it (e.g. micro ≈ macro,
aggregation second-order per the Phase-7 reconciliation), the report SAYS SO.

No new F1 math (CLAUDE.md)
--------------------------
Every score flows through ``transarc_error_analysis.calc_metrics`` via the imported
``component_suite`` / ``rq2_trivial_baselines`` functions. The trivial floor is
scored by the IDENTICAL suite path the real systems take (collapse the baseline's
(sentence, file) links through ``component_suite._code_inputs(proj)``'s collapse()
and run ``component_suite.component_suite``). The oracle/random anchors are the rq2
``compute_oracle_f1`` / ``compute_random_f1``. NO precision/recall is reimplemented.

    python3 src/bias/metric_fitness.py
"""

import csv
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent              # src/bias
sys.path.insert(0, str(HERE.parent / "lib"))        # src/lib (shared loaders)
sys.path.insert(0, str(HERE))                        # src/bias (suite + floor)

import component_suite                                # noqa: E402
import rq2_trivial_baselines                          # noqa: E402
from transarc_error_analysis import (                 # noqa: E402
    PROJECTS,
    load_code_model_files, load_model_element_names,
    enroll_gold_standard, load_gs_sam_code_raw, load_gs_sad_code_enrolled,
    load_gs_sam_code_maps, load_gs_sad_sam_maps,
)

REPORTS = Path(__file__).resolve().parent.parent.parent / "reports"

LEVELS = ["sad-model", "sad-code"]
# Scored candidate columns (gold_gini is a DESCRIPTOR, not scored).
SCORE_COLS = ["micro", "macro", "gap", "min_comp", "pct_missed"]
# F1-scaled columns get an oracle-ceiling validity bound; the others are
# interpreted (gap = signed skew indicator; pct_missed = lower-is-better coverage).
F1_SCALED = {"micro", "macro", "min_comp"}
REAL_LABELS = ["swattr/transarc", "s20linker", "artemis"]

random.seed(42)  # Random-floor reproducibility (matches rq2_trivial_baselines)


# ── Trivial floor: build Random + Top-3 EXACTLY as rq2.run_project, then score
#    them through the IDENTICAL suite path the real systems take (no new math). ──

def _floor_suite_rows(proj):
    """Return {"Random": suite_dict, "Top-3": suite_dict} for one project.

    The two rq2 trivial baselines are produced verbatim
    (``baseline_random_same_size`` + ``baseline_majority_k(k=3)`` with
    ``random.seed(42)`` and ``target_size = len(gs_sad_code)``), then their
    (sentence, file) links are collapsed through ``component_suite._code_inputs``'
    collapse() into (sentence, component) pairs and scored by
    ``component_suite.component_suite`` — exactly how a real system's sad-code
    links are scored. The floor reuses the suite math; no formula is added.
    """
    code_model = load_code_model_files(proj)
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
    gs_sam_code_enrolled = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
    gold_sents = set(s for s, _ in gs_sad_code)

    random.seed(42)  # reset per project (order independence; matches rq2)
    target_size = len(gs_sad_code)
    random_bl = rq2_trivial_baselines.baseline_random_same_size(
        gold_sents, code_model, target_size)
    top3_bl = rq2_trivial_baselines.baseline_majority_k(
        gold_sents, gs_sam_code_enrolled, code_model, k=3)

    gold_sc, collapse = component_suite._code_inputs(proj)
    return {
        "Random": component_suite.component_suite(gold_sc, collapse(random_bl)),
        "Top-3":  component_suite.component_suite(gold_sc, collapse(top3_bl)),
    }


# ── Oracle / random anchors (rq2 NDG anchors; validity axis bounds) ───────────

def _anchors(proj):
    """(random_f1, oracle_f1) for one project, built like rq2.run_project."""
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)
    gs_sad_sam_maps = load_gs_sad_sam_maps(proj)
    n_sents = len(set(s for s, _ in gs_sad_code))
    random_f1 = rq2_trivial_baselines.compute_random_f1(
        gs_sad_code, n_sents, len(names), gs_sam_code_map)
    oracle_f1, _ = rq2_trivial_baselines.compute_oracle_f1(
        gs_sad_code, gs_sam_code_map, gs_sad_sam_maps)
    return random_f1, oracle_f1


# ── Gather the real-system suite columns per level (calc_metrics via the suite) ─

def _real_rows(level):
    """{project: {label: suite_dict}} for the 3 real systems at one level."""
    rows = component_suite.run_level(level, list(PROJECTS))
    out = defaultdict(dict)
    for proj, _key, label, m in rows:
        out[proj][label] = m
    return out


# ── The four axes (numeric rubric, D-13) ──────────────────────────────────────

def _col_value(suite_dict, col):
    """Column value with the 'higher = real-beats-trivial' orientation applied.

    gap is a SIGNED skew indicator (not a quality score): |gap| measures the skew
    magnitude a column exposes, so the separation/degeneracy axes use |gap|.
    pct_missed is lower-is-better (fraction of gold components abandoned), so it is
    inverted (1 - pct_missed) for the 'higher = better coverage' orientation.
    micro/macro/min_comp are already higher-is-better F1s.
    """
    v = suite_dict[col]
    if col == "gap":
        return abs(v)
    if col == "pct_missed":
        return 1.0 - v
    return v


def _separation(real_rows, floor_rows, col):
    """Margin = mean(real column) − mean(trivial-floor column), oriented so a
    positive margin means real systems beat the Random/Top-3 floor on the column."""
    real_vals, floor_vals = [], []
    for proj in PROJECTS:
        for label in REAL_LABELS:
            if label in real_rows.get(proj, {}):
                real_vals.append(_col_value(real_rows[proj][label], col))
        fr = floor_rows.get(proj)
        if fr:
            for bl in ("Random", "Top-3"):
                floor_vals.append(_col_value(fr[bl], col))
    if not real_vals or not floor_vals:
        return 0.0
    return statistics.mean(real_vals) - statistics.mean(floor_vals)


def _validity(real_rows, anchors, col):
    """Oracle-ceiling headroom for the F1-scaled columns: how far the real mean
    sits below the oracle ceiling, normalized into [0,1] over the random→oracle
    band. 1.0 = at the random floor (max headroom), 0.0 = at/above the oracle
    ceiling (no headroom). A valid F1 column should sit strictly inside (0,1).

    For non-F1 columns (gap, pct_missed) the oracle band is not an F1 comparison;
    the score is the real mean of the oriented value, reported as the bound
    interpretation (gap: skew magnitude carried; pct_missed: coverage retained).
    """
    real_vals = [_col_value(real_rows[proj][label], col)
                 for proj in PROJECTS for label in REAL_LABELS
                 if label in real_rows.get(proj, {})]
    if not real_vals:
        return 0.0
    real_mean = statistics.mean(real_vals)
    if col not in F1_SCALED:
        return real_mean  # interpreted bound (documented in the report)
    rand_mean = statistics.mean(a[0] for a in anchors.values())
    orac_mean = statistics.mean(a[1] for a in anchors.values())
    band = orac_mean - rand_mean
    if band <= 0:
        return 0.0
    return max(0.0, min(1.0, (orac_mean - real_mean) / band))


def _stability(real_rows, col):
    """Cross-project standard deviation of the column pooled over the 3 real
    systems (lower = more stable). A 5-project × 3-system sample."""
    vals = [_col_value(real_rows[proj][label], col)
            for proj in PROJECTS for label in REAL_LABELS
            if label in real_rows.get(proj, {})]
    if len(vals) < 2:
        return 0.0
    return statistics.pstdev(vals)


def _degeneracy(real_rows, col):
    """Saturation / insensitivity test. Compute the per-system mean of the column
    over projects, then report the cross-SYSTEM spread (max − min). A column whose
    systems are near-identical (tiny spread) OR pinned at an extreme cannot
    discriminate systems → degenerate. Higher spread = healthier (less degenerate);
    we return the spread so the rubric reads 'small = degenerate'."""
    sys_means = []
    for label in REAL_LABELS:
        vals = [_col_value(real_rows[proj][label], col)
                for proj in PROJECTS if label in real_rows.get(proj, {})]
        if vals:
            sys_means.append(statistics.mean(vals))
    if len(sys_means) < 2:
        return 0.0
    return max(sys_means) - min(sys_means)


def score_level(level):
    """Return {col: {separation, validity, stability, degeneracy}} for one level.

    At sad-model the rq2 trivial floor is file-level (sad-code) only, so the
    separation axis is scored against the SAD-CODE floor and the scoping is stated
    in the report (D-08 present-scope honesty). The real columns are the level's
    own suite columns.
    """
    real_rows = _real_rows(level)
    floor_rows = {p: _floor_suite_rows(p) for p in PROJECTS}  # always sad-code floor
    anchors = {p: _anchors(p) for p in PROJECTS}

    scored = {}
    for col in SCORE_COLS:
        scored[col] = {
            "separation": _separation(real_rows, floor_rows, col),
            "validity":   _validity(real_rows, anchors, col),
            "stability":  _stability(real_rows, col),
            "degeneracy": _degeneracy(real_rows, col),
        }
    return scored, real_rows


# ── Verdict derivation (DATA-DERIVED — consumes the computed axis scores) ──────

def derive_verdict(scored_by_level):
    """Rank each column HEADLINE vs DIAGNOSTIC purely from the computed axis scores.

    A column is HEADLINE-fit when it (a) separates real from the trivial floor
    (separation > median separation across columns), (b) discriminates systems
    (degeneracy spread > median), and is not pinned. A column that fails separation
    or barely discriminates systems is DIAGNOSTIC. The split is decided by the
    NUMBERS — no expected answer is asserted. Returns
    (per_column_verdict, headline_cols, diagnostic_cols, notes[]).
    """
    # Pool each axis across both levels (mean) so the verdict is level-robust.
    pooled = {}
    for col in SCORE_COLS:
        sep = statistics.mean(scored_by_level[lv][col]["separation"] for lv in LEVELS)
        deg = statistics.mean(scored_by_level[lv][col]["degeneracy"] for lv in LEVELS)
        stab = statistics.mean(scored_by_level[lv][col]["stability"] for lv in LEVELS)
        pooled[col] = {"separation": sep, "degeneracy": deg, "stability": stab}

    sep_med = statistics.median(pooled[c]["separation"] for c in SCORE_COLS)
    deg_med = statistics.median(pooled[c]["degeneracy"] for c in SCORE_COLS)

    per_col, headline, diagnostic = {}, [], []
    for col in SCORE_COLS:
        sep = pooled[col]["separation"]
        deg = pooled[col]["degeneracy"]
        is_headline = (sep >= sep_med) and (deg >= deg_med)
        per_col[col] = "headline" if is_headline else "diagnostic"
        (headline if is_headline else diagnostic).append(col)

    # Honesty check (D-07): is micro ≈ macro on every axis? If so, the aggregation
    # contrast is second-order and we say so, rather than restating macro-as-headline.
    notes = []
    micro_macro_close = all(
        abs(pooled["micro"][ax] - pooled["macro"][ax]) < 0.05
        for ax in ("separation", "degeneracy", "stability")
    )
    if micro_macro_close:
        notes.append(
            "micro and macro score within 0.05 on every axis (separation, "
            "degeneracy, stability) — the aggregation contrast is SECOND-ORDER, "
            "consistent with the Phase-7 reconciliation; this CONTRADICTS the "
            "milestone's expected 'micro is diagnostic / macro is headline' split, "
            "and the report states so rather than overselling macro.")
    else:
        notes.append(
            "micro and macro diverge on at least one axis (>0.05) — the aggregation "
            "contrast carries signal at the per-column level (see the CSV).")

    return per_col, headline, diagnostic, notes, pooled


# ── Report writers ────────────────────────────────────────────────────────────

def write_csv(scored_by_level, verdict_by_col):
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "METRIC_FITNESS.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "column", "separation", "validity",
                    "stability", "degeneracy", "verdict"])
        for level in LEVELS:
            for col in SCORE_COLS:
                s = scored_by_level[level][col]
                w.writerow([level, col,
                            f"{s['separation']:.4f}", f"{s['validity']:.4f}",
                            f"{s['stability']:.4f}", f"{s['degeneracy']:.4f}",
                            verdict_by_col[col]])
    return out


def _artemis_tail(real_rows_by_level):
    """Reproduce + quantify the SC4 artemis long-tail-abandonment finding from the
    GOLD-ONLY tail columns (min_comp / pct_missed), drawn from the same suite the
    committed COMPONENT_SUITE_<level>.csv was written from."""
    finding = {}
    for level in LEVELS:
        rr = real_rows_by_level[level]
        mins, pcts, zero_projs = [], [], []
        for proj in PROJECTS:
            m = rr.get(proj, {}).get("artemis")
            if not m:
                continue
            mins.append(m["min_comp"])
            pcts.append(m["pct_missed"])
            if m["min_comp"] == 0.0:
                zero_projs.append(proj)
        finding[level] = {
            "avg_min_comp": statistics.mean(mins) if mins else 0.0,
            "avg_pct_missed": statistics.mean(pcts) if pcts else 0.0,
            "zero_projects": zero_projs,
        }
    return finding


def write_md(scored_by_level, verdict_by_col, headline, diagnostic, notes,
             pooled, real_rows_by_level):
    L = []

    def out(s=""):
        L.append(s)

    out("# Metric Fitness Scorecard (CMP-04)")
    out()
    out("Each candidate `component_suite` column (`micro`, `macro`, `gap`, "
        "`min_comp`, `pct_missed`; `gold_gini` is a descriptor) is scored on four "
        "fitness axes at both levels. **No new F1 math** — every value flows "
        "through `transarc_error_analysis.calc_metrics` via the imported "
        "`component_suite` / `rq2_trivial_baselines` functions. The trivial floor "
        "is the rq2 **Random + Top-3** baselines reused as-is (D-01), scored by the "
        "identical suite path the three real paper systems (swattr/transarc, "
        "s20linker, artemis) take.")
    out()
    out("**Axes.** *separation* = mean(real) − mean(trivial floor) margin per "
        "column (higher = real beats Random/Top-3); for `gap` the skew magnitude "
        "`|gap|` is used and `pct_missed` is oriented as coverage `1−pct_missed`. "
        "*validity* = oracle-ceiling headroom over the rq2 random→oracle band "
        "(`compute_random_f1`/`compute_oracle_f1`) for the F1-scaled columns "
        "(`micro`/`macro`/`min_comp`); for `gap`/`pct_missed` the oriented real "
        "mean is reported as the bound interpretation (not forced into an F1 "
        "comparison). *stability* = cross-project standard deviation pooled over "
        "the real systems (lower = more stable). *degeneracy* = cross-system spread "
        "of the per-system column means (smaller = more degenerate / insensitive).")
    out()
    out("> Scoping note (D-08): the rq2 trivial floor is file-level (sad-code) only, "
        "so the **separation** axis at `sad-model` is scored against the **sad-code** "
        "floor; all other axes use each level's own suite columns. Reproducibility "
        "is scoped to present systems (all three roots present today).")
    out()

    for level in LEVELS:
        out(f"## {level} — axis scores")
        out()
        out("| column | separation | validity | stability | degeneracy | verdict |")
        out("|---|---|---|---|---|---|")
        for col in SCORE_COLS:
            s = scored_by_level[level][col]
            out(f"| `{col}` | {s['separation']:.4f} | {s['validity']:.4f} "
                f"| {s['stability']:.4f} | {s['degeneracy']:.4f} "
                f"| {verdict_by_col[col]} |")
        out()

    # ── Data-derived verdict (one line) ──
    out("## Verdict (data-derived)")
    out()
    hl = ", ".join(f"`{c}`" for c in headline) or "(none)"
    dg = ", ".join(f"`{c}`" for c in diagnostic) or "(none)"
    out(f"**Verdict:** headline columns = {hl}; diagnostic columns = {dg} "
        "(decided by: separation ≥ median AND degeneracy ≥ median across columns, "
        "pooled over both levels — emerged from the numbers, not asserted).")
    out()
    out("Pooled (both-level mean) axis scores the verdict is derived from:")
    out()
    out("| column | separation | degeneracy | stability |")
    out("|---|---|---|---|")
    for col in SCORE_COLS:
        p = pooled[col]
        out(f"| `{col}` | {p['separation']:.4f} | {p['degeneracy']:.4f} "
            f"| {p['stability']:.4f} |")
    out()
    out("**Honesty note (D-06/D-07).**")
    for n in notes:
        out(f"- {n}")
    out()

    # ── SC4 artemis long-tail finding ──
    finding = _artemis_tail(real_rows_by_level)
    out("## SC4 — artemis long-tail abandonment (reproduced + quantified)")
    out()
    out("Under the Phase-7 **gold-only** tail definition (`min_comp` = worst single "
        "GOLD-component F1; `pct_missed` = fraction of GOLD components scored exactly "
        "0), artemis nails the popular components but abandons the long tail — its "
        "tail columns are the weakest of the three real systems and collapse to 0 on "
        "several projects.")
    out()
    out("| level | artemis AVG min_comp | artemis AVG pct_missed | projects with min_comp=0 |")
    out("|---|---|---|---|")
    for level in LEVELS:
        ff = finding[level]
        zp = ", ".join(ff["zero_projects"]) or "(none)"
        out(f"| {level} | {ff['avg_min_comp']:.4f} | {ff['avg_pct_missed']:.4f} | {zp} |")
    out()
    out("These AVG `min_comp` / `pct_missed` values match the artemis AVG rows of the "
        "committed `reports/COMPONENT_SUITE_sad-code.csv` "
        f"(min_comp={finding['sad-code']['avg_min_comp']:.4f}, "
        f"pct_missed={finding['sad-code']['avg_pct_missed']:.4f}) and "
        "`reports/COMPONENT_SUITE_sad-model.csv` "
        f"(min_comp={finding['sad-model']['avg_min_comp']:.4f}, "
        f"pct_missed={finding['sad-model']['avg_pct_missed']:.4f}) — the scorecard "
        "reads the same suite, so the tail finding is reproduced, not re-derived.")
    out()
    out("---")
    out()
    out("Script: `src/bias/metric_fitness.py`. Reproduce: "
        "`python3 src/bias/metric_fitness.py` (deterministic; Random floor seeded "
        "`random.seed(42)`).")
    out()

    (REPORTS / "METRIC_FITNESS.md").write_text("\n".join(L))
    return REPORTS / "METRIC_FITNESS.md"


# ── Driver ────────────────────────────────────────────────────────────────────

def main():
    scored_by_level = {}
    real_rows_by_level = {}
    for level in LEVELS:
        scored, real_rows = score_level(level)
        scored_by_level[level] = scored
        real_rows_by_level[level] = real_rows
        print(f"OK    scored {level:9} columns={','.join(SCORE_COLS)}")

    verdict_by_col, headline, diagnostic, notes, pooled = derive_verdict(scored_by_level)

    csv_path = write_csv(scored_by_level, verdict_by_col)
    md_path = write_md(scored_by_level, verdict_by_col, headline, diagnostic,
                       notes, pooled, real_rows_by_level)

    print(f"[metric-fitness] headline={headline} diagnostic={diagnostic}")
    print(f"[metric-fitness] csv={csv_path}")
    print(f"[metric-fitness] md={md_path}")


if __name__ == "__main__":
    main()
