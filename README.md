# TransArc-EMP

A stdlib-only Python analysis workspace plus a LaTeX paper studying ARDoCo's
transitive Traceability Link Recovery (**TransArc**) and how its benchmark is
evaluated. The codebase is organized into **two pillars** — a *TransArc
empirical study* and a *benchmark bias analysis* — and the paper
(`writing/eval.tex`) is aligned to match them.

**Audience:** a new researcher/reviewer who needs to understand the two-pillar
structure and regenerate either pillar's reports from scratch without
reverse-engineering the scripts.

## Prerequisites

- **Python 3, stdlib only** — no `pip install`, no `requirements.txt`. Every
  script runs with a bare Python 3 interpreter.
- **External benchmark data** lives outside this repo at:
  `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
  (5 projects: `mediastore`, `teastore`, `teammates`, `bigbluebutton`, `jabref`).
- **TransArc run outputs** are already present under `results/`.
- **How to run any script:** from the repo root run `python3 src/<area>/<script>.py`.
  Markdown/CSV reports land in `reports/`; LaTeX tables land in `writing/tables/`.
- **Known limitation:** `pdflatex` is **not** available locally. The paper is
  validated via `python3 src/paper/generate_tables.py` plus structural checks —
  there is no PDF build step.
- For deeper dev/build/leakage rules see the linked rule files (do **not**
  duplicate their content here): [CLAUDE.md](CLAUDE.md) (project) and
  [../CLAUDE.md](../CLAUDE.md) (ARDoCo workspace).

## Two Pillars

| Pillar | Code dirs | Key scripts | Output reports | Paper chapter |
|--------|-----------|-------------|----------------|---------------|
| **Pillar 1 — TransArc empirical study** | `src/transarc/`, `src/lib/` | `transarc_error_analysis.py`, `sad_sam_actual_contribution.py`, `s12c_sadcode_comparison.py` (+ `sad_sam_tp_gain_analysis.py`, `sam_code_cascade_analysis.py`) | `reports/TRANSARC_EMPIRICAL_STUDY.md` (+ contribution / tp-gain / cascade / S12C reports) | `writing/ch1_transarc.tex` (`eval.tex` Ch1) |
| **Pillar 2 — Benchmark bias & metrics** | `src/bias/`, `src/lib/` (incl. `src/lib/metrics_api.py`), `src/bias/consequences_study.py`, `src/paper/generate_tables.py` | `benchmark_bias_study.py`, `evaluation_critique.py`, `metrics_api.py`, `consequences_study.py`, `generate_tables.py` (+ baselines, holistic/creative metrics) | `reports/BENCHMARK_BIAS_STUDY.md`, `EVALUATION_CRITIQUE.md`, `metrics_*.csv`, `CONSEQUENCES_STUDY.md` | `writing/eval.tex` Ch2 |

## Pillar 1 — Reproduce

The TransArc empirical study. These commands are runnable top-to-bottom from the
repo root; each regenerates its named report deterministically. (Note:
`transarc_error_analysis.py` lives in `src/lib/` — it is the Pillar 1 study
entrypoint plus shared loaders — but is run directly.)

| Command | Output |
|---------|--------|
| `python3 src/lib/transarc_error_analysis.py` | `reports/TRANSARC_EMPIRICAL_STUDY.md` |
| `python3 src/transarc/sad_sam_actual_contribution.py` | `reports/SAD_SAM_ACTUAL_CONTRIBUTION.md` |
| `python3 src/transarc/sad_sam_tp_gain_analysis.py` | `reports/SAD_SAM_TP_GAIN_STUDY.md` |
| `python3 src/transarc/sam_code_cascade_analysis.py` | `reports/SAM_CODE_CASCADE.md` |
| `python3 src/transarc/s12c_sadcode_comparison.py` | `reports/S12C_VS_TRANSARC.csv` |

## Pillar 2 — Reproduce

The benchmark bias & metrics analysis. Run the standalone bias/baseline/metric
scripts first, then the Phase-4 metrics API, then the Phase-5 consequences study
(which **reads the two `metrics_*.csv` files**, so the API must run first).

**1. Standalone bias / baseline / proposed-metric scripts** (any order):

| Command | Output |
|---------|--------|
| `python3 src/bias/benchmark_bias_study.py` | `reports/BENCHMARK_BIAS_STUDY.md` |
| `python3 src/bias/evaluation_critique.py` | `reports/EVALUATION_CRITIQUE.md` |
| `python3 src/bias/enrollment_bias_analysis.py` | `reports/ENROLLMENT_BIAS_ANALYSIS.md` |
| `python3 src/bias/extreme_baseline_analysis.py` | `reports/EXTREME_BASELINES.md` |
| `python3 src/bias/stupid_baseline_analysis.py` | `reports/STUPID_BASELINES.md` |
| `python3 src/bias/holistic_metrics_analysis.py` | `reports/HOLISTIC_METRICS.md` |
| `python3 src/bias/creative_metrics_analysis.py` | `reports/CREATIVE_METRICS.md` |
| `python3 src/bias/sam_code_distribution_analysis.py` | `reports/SAM_CODE_DISTRIBUTION.md` |
| `python3 src/lib/new_metrics_analysis.py` | `reports/NEW_METRICS_REPORT.md` |

**2. Phase-4 metrics API** (run before the consequences study):

| Command | Output |
|---------|--------|
| `python3 src/lib/metrics_api.py --task sad-sam` | `reports/metrics_sad-sam.csv` + `writing/tables/metrics_sad-sam.tex` |
| `python3 src/lib/metrics_api.py --task sad-code` | `reports/metrics_sad-code.csv` + `writing/tables/metrics_sad-code.tex` |

**3. Phase-5 consequences study** (reads the two `metrics_*.csv` above):

| Command | Output |
|---------|--------|
| `python3 src/bias/consequences_study.py` | `reports/CONSEQUENCES_STUDY.md` |

**Supporting/intermediate:** `python3 src/bias/enrollment_distortion_analysis.py`
prints to stdout and produces no single report file.

## Paper

`python3 src/paper/generate_tables.py` regenerates `writing/tables/*.tex`, which
are `\input` by `writing/eval.tex` (Ch1 = TransArc empirical study via
`\input{ch1_transarc}`, Ch2 = Benchmark bias). As noted in the prerequisites,
`pdflatex` is not available locally — the paper is validated via
`generate_tables.py` plus structural checks, not a PDF build.
