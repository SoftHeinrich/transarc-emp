# mini-src — minimal trace-link metrics

A single self-contained, stdlib-only script that computes **only the paper's
non-redundant primary metric panel** for doc-to-code (`sad-code`) and
doc-to-model (`sad-sam`) trace-link recovery.

The canonical implementation (`src/lib/metrics_api.py`) computes **13** metric
columns by importing across four modules (`transarc_error_analysis`,
`evaluation_critique`, `new_metrics_analysis`, `generate_tables`). The RQ2
redundancy analysis (`reports/RQ2_METRIC_REDUNDANCY.md`,
`src/bias/rq2_metric_redundancy.py`) showed most of those carry no independent
ranking signal — Spearman ρ ≥ 0.85 with a kept metric and ~0 system-pair
reversals. `mini-src` keeps just the metrics that earn their place and drops the
rest, in ~250 lines with zero cross-module imports.

## What it computes

| Task       | Metrics kept                                                     |
|------------|------------------------------------------------------------------|
| `sad-code` | file P/R/F1, per-component F1, sentence coverage, noise rate      |
| `sad-sam`  | link P/R/F1, sentence coverage, noise rate                       |

Dropped as redundant (appendix-only in the paper): sentence F1, decision F1,
weighted F1, MCC, MAP, ACF1, NDG, HUS. For `sad-sam`, per-component F1 is also
dropped because, without enrolment, it collapses onto link F1 (ρ = +1.00).

Definitions match `metrics_api` exactly:

- **per-component F1** is the **micro** form (one P/R/F1 over all
  (sentence, component) pairs) — the form the paper headline
  (`reports/SADCODE_S11_S13F_VS_TRANSARC.csv`, `table/rq2-summary.tex`) reports.
  Note a *macro* variant also exists in the codebase
  (`rq2_trivial_baselines.per_component_macro_f1`); it gives slightly different
  numbers and is **not** what the headline uses.
- **sentence coverage** = fraction of gold sentences with ≥1 *correct* hit.
- **noise rate** = mean over *predicted* sentences of FP/(TP+FP); lower is better.

## Usage

```bash
# All five projects, bundled TransArc results:
python3 mini-src/metrics.py --task sad-code
python3 mini-src/metrics.py --task sad-sam

# One project, also dump a CSV:
python3 mini-src/metrics.py --task sad-code --project jabref --csv /tmp/panel.csv

# Score arbitrarily-named result CSVs (column dialect auto-detected):
python3 mini-src/metrics.py --task sad-sam \
    --results-dir /path/to/run \
    --result-pattern 's_linker20_union_{project}_links.csv'
```

Benchmark and result roots default to the bundled tree and can be overridden via
`$TRANSARC_BENCHMARK` / `$TRANSARC_RESULTS_DIR` or the `--results-dir` flag.

## Verification

`check.py` proves the reduction is faithful — it scores the same inputs with
both `mini-src/metrics.py` and `src/lib/metrics_api.py` and asserts every panel
cell agrees to 1e-9:

```bash
python3 mini-src/check.py     # → PASS
```

The bundled TransArc results reproduce the paper headline averages exactly:
sad-code file F1 .80 / comp F1 .71 / cov .75 / noise .13; sad-sam link F1 .80 /
cov .79 / noise .14.
