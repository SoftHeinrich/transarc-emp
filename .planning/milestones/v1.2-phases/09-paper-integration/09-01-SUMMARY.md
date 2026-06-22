---
phase: 09-paper-integration
plan: 01
type: execute
status: complete
requirements: [CMP-05]
commit: feat(09) integrate component suite into eval.tex Ch2
---

# 09-01 Summary — CMP-05 Paper Integration

## What was built

1. **Two generated tables** (`src/paper/generate_tables.py`, two new `t_*` builders
   registered in `main()` under the Ch2 group):
   - `tab:component-suite` (`writing/tables/component_suite.tex`) — the level-agnostic
     suite over the three systems at both granularities (AVG rows: micro / macro / gap /
     min comp. / pct. missed), read from `reports/COMPONENT_SUITE_{sad-model,sad-code}.csv`.
   - `tab:metric-fitness` (`writing/tables/metric_fitness.tex`) — the fitness scorecard,
     pooled over both levels (separation / validity / stability / degeneracy + the
     headline/diagnostic role), read from `reports/METRIC_FITNESS.csv` (per-column mean of
     the two per-level rows; verdict asserted identical across levels).
   Both reuse `render_table`/`write_table`; no hardcoded metric values; stdlib-only.

2. **New Ch2 section** (`writing/eval.tex` §`sec:eval:component-suite`, appended after the
   converged-framework table): "A Level-Agnostic Component Suite and the Long-Tail
   Discriminator." Three claims, each traced to a retained artifact:
   - the suite is one object (5 columns) at both granularities (cite `component_suite.py`,
     `reports/COMPONENT_SUITE.md`);
   - the universe-reconciliation correction — apparent enrollment gap −0.099→−0.019 (avg)
     and −0.31→−0.05 (bbb), headline component F1 0.714→0.795; aggregation is second-order
     (cite `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`);
   - tail coverage is the level-stable discriminator: artemis competitive on micro (2nd,
     0.836/0.799) but last on worst real-component coverage (min_comp 0.279/0.345) and
     scores 0 on real gold components (bbb+jabref both levels, teammates doc-to-model);
     fitness verdict headline = micro/macro/min_comp, diagnostic = gap/pct_missed
     (cite `reports/METRIC_FITNESS.md`). `\input` + `\Cref` both new tables.

3. **Stale-prose fix** (`writing/eval.tex` L417): the buggy Sentence-F1 example (Teammates
   0.916, "0.206 gap") re-anchored to BigBlueButton (sentence 0.876 vs link 0.793, +0.083),
   matching `writing/tables/metrics_sad-sam.tex`. Resolves the paper consequence of
   STATE open-item #1 (the `sentence_f1` bug was already fixed in `b9a18f4`; 0.703/0.825
   confirmed correct — see 09-CONTEXT pre-phase resolution).

4. **Structural validator** (`src/paper/check_eval_structure.py`, stdlib): follows the
   `\input` graph from `eval.tex`, checks every `\ref`/`\Cref`/`\cref`/… resolves to a
   `\label` and every `\input{tables/X}` exists. SC3 gate in place of pdflatex.

## Success criteria

- **SC1** (new Ch2 section, suite + two-level finding, retained citations only): ✅
- **SC2** (tables via `generate_tables.py` into `writing/tables/`): ✅ — generator emits
  both new tables; 2nd run byte-identical (deterministic); no churn in the other 12 tables.
- **SC3** (eval.tex validates structurally; tables regenerate): ✅ —
  `check_eval_structure.py` exits 0 (69 labels / 47 refs / 15 inputs, all resolve).

## Invariants held
- Stdlib-only (csv/re/pathlib/sys); no third-party deps.
- No benchmark-derived word lists — project/system/column names read as opaque CSV data.
- Every emitted table traces to a retained `reports/` artifact.
- No metric math reimplemented; upstream scripts (`component_suite.py`,
  `metric_fitness.py`, `metrics_api.py`) untouched.

## Deviations / notes
- alinker-paper mirror deferred (D-17) — CMP-05 is local `writing/eval.tex` only.
- No `pdflatex` PDF build (deferred since v1.1); SC3 met via the structural validator.
- Initial draft `\Cref`'d the two tables without `\input`; the validator caught the two
  dangling refs and they were added (validator did its job).
