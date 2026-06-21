# Metric Fitness Scorecard (CMP-04)

Each candidate `component_suite` column (`micro`, `macro`, `gap`, `min_comp`, `pct_missed`; `gold_gini` is a descriptor) is scored on four fitness axes at both levels. **No new F1 math** — every value flows through `transarc_error_analysis.calc_metrics` via the imported `component_suite` / `rq2_trivial_baselines` functions. The trivial floor is the rq2 **Random + Top-3** baselines reused as-is (D-01), scored by the identical suite path the three real paper systems (swattr/transarc, s20linker, artemis) take.

**Axes.** *separation* = mean(real) − mean(trivial floor) margin per column (higher = real beats Random/Top-3); for `gap` the skew magnitude `|gap|` is used and `pct_missed` is oriented as coverage `1−pct_missed`. *validity* = oracle-ceiling headroom over the rq2 random→oracle band (`compute_random_f1`/`compute_oracle_f1`) for the F1-scaled columns (`micro`/`macro`/`min_comp`); for `gap`/`pct_missed` the oriented real mean is reported as the bound interpretation (not forced into an F1 comparison). *stability* = cross-project standard deviation pooled over the real systems (lower = more stable). *degeneracy* = cross-system spread of the per-system column means (smaller = more degenerate / insensitive).

> Scoping note (D-08): the rq2 trivial floor is file-level (sad-code) only, so the **separation** axis at `sad-model` is scored against the **sad-code** floor; all other axes use each level's own suite columns. Reproducibility is scoped to present systems (all three roots present today).

## sad-model — axis scores

| column | separation | validity | stability | degeneracy | verdict |
|---|---|---|---|---|---|
| `micro` | 0.5398 | 0.1716 | 0.0973 | 0.0900 | headline |
| `macro` | 0.6245 | 0.1904 | 0.1040 | 0.0817 | headline |
| `gap` | -0.0661 | 0.0328 | 0.0342 | 0.0194 | diagnostic |
| `min_comp` | 0.4420 | 0.6621 | 0.3192 | 0.3808 | headline |
| `pct_missed` | 0.4040 | 0.9523 | 0.0893 | 0.0832 | diagnostic |

## sad-code — axis scores

| column | separation | validity | stability | degeneracy | verdict |
|---|---|---|---|---|---|
| `micro` | 0.5159 | 0.2033 | 0.1307 | 0.0630 | headline |
| `macro` | 0.6155 | 0.2025 | 0.1134 | 0.0638 | headline |
| `gap` | -0.0582 | 0.0407 | 0.0307 | 0.0349 | diagnostic |
| `min_comp` | 0.4738 | 0.6197 | 0.3019 | 0.2806 | headline |
| `pct_missed` | 0.4139 | 0.9622 | 0.0842 | 0.0600 | diagnostic |

## Verdict (data-derived)

**Verdict:** headline columns = `micro`, `macro`, `min_comp`; diagnostic columns = `gap`, `pct_missed` (decided by: separation ≥ median AND degeneracy ≥ median across columns, pooled over both levels — emerged from the numbers, not asserted).

Pooled (both-level mean) axis scores the verdict is derived from:

| column | separation | degeneracy | stability |
|---|---|---|---|
| `micro` | 0.5278 | 0.0765 | 0.1140 |
| `macro` | 0.6200 | 0.0727 | 0.1087 |
| `gap` | -0.0621 | 0.0272 | 0.0324 |
| `min_comp` | 0.4579 | 0.3307 | 0.3105 |
| `pct_missed` | 0.4089 | 0.0716 | 0.0868 |

**Honesty note (D-06/D-07).**
- micro and macro diverge on at least one axis (>0.05) — the aggregation contrast carries signal at the per-column level (see the CSV).

## SC4 — artemis long-tail abandonment (reproduced + quantified)

Under the Phase-7 **gold-only** tail definition (`min_comp` = worst single GOLD-component F1; `pct_missed` = fraction of GOLD components scored exactly 0), artemis nails the popular components but abandons the long tail — its tail columns are the weakest of the three real systems and collapse to 0 on several projects.

| level | artemis AVG min_comp | artemis AVG pct_missed | projects with min_comp=0 |
|---|---|---|---|
| sad-model | 0.2788 | 0.0832 | teammates, bigbluebutton, jabref |
| sad-code | 0.3455 | 0.0533 | bigbluebutton, jabref |

These AVG `min_comp` / `pct_missed` values match the artemis AVG rows of the committed `reports/COMPONENT_SUITE_sad-code.csv` (min_comp=0.3455, pct_missed=0.0533) and `reports/COMPONENT_SUITE_sad-model.csv` (min_comp=0.2788, pct_missed=0.0832) — the scorecard reads the same suite, so the tail finding is reproduced, not re-derived.

---

Script: `src/bias/metric_fitness.py`. Reproduce: `python3 src/bias/metric_fitness.py` (deterministic; Random floor seeded `random.seed(42)`).
