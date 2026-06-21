# Data-Inequality Mini-Study

> **Isolated sub-project.** This `.planning/` directory is self-contained and scoped
> to the `mini-inequality/` study only. It deliberately does NOT share the repo-root
> `.planning/` (which tracks the active **v1.2 Component-Centric Metric Suite**,
> Phases 7-9). Run GSD phase commands against this subdir; never let this milestone
> write to root `.planning/`. Branch: `gsd/mini-data-inequality`.

## What This Is

A self-contained, stdlib-only mini study under `mini-inequality/` that quantifies the
**concentration inequality** of trace links in the ARDoCo benchmark (how a few large
components / files own most of the gold link mass) and uses that empirical evidence to
**verify the paper's distributional-inequality claims** and **motivate the proposed
four-metric evaluation suite**. Audience: the authors of the `alinker-paper`
(architecture-driven trace-link evaluation paper).

## Core Value

The inequality numbers this study produces must be (1) **faithful** — reproducible from
the bundled benchmark with zero cross-module imports, sanity-checked against the
canonical `src/bias/component_suite.py` `gold_gini` and the `eval.tex` tables — and
(2) **claim-grounding** — every distributional-inequality statement the paper makes
(and every `XX` placeholder) is backed by a number this study computed.

## Current Milestone: v0.1 Data-Inequality Mini-Study

**Goal:** Measure trace-link concentration inequality (Gini, Lorenz, top-k share,
enrollment expansion factor) across all 5 projects for both `sad-code` and `sad-sam`;
verify the paper's inequality claims against the computed numbers; fill the paper's
open `XX` placeholders; and empirically demonstrate why file/link micro-F1 needs the
four-metric suite.

**Target features:**
- A self-contained inequality engine (`mini-inequality/inequality.py`) → CSV
- A paper-claim verification report (MATCH / MISMATCH / STALE per claim) + resolved placeholders
- A baseline-exploitation argument (Top-3 / random) motivating the metric suite
- Paper-ready Gini/Lorenz table (+ optional Lorenz-curve data/figure)

## Requirements

### Validated

(None yet — first milestone of this sub-project.)

### Active

<!-- v0.1 — see REQUIREMENTS.md -->

- [ ] **INEQ-01** Per-component gold link-count inequality (Gini + Lorenz points + top-k share + min/median/max), sad-code & sad-sam, 5 projects → CSV
- [ ] **INEQ-02** Per-file (post-enrollment) concentration + per-sentence links/sentence distribution for sad-code
- [ ] **INEQ-03** Per-project enrollment expansion factor (component→file) + aggregate cascade (component FPs → file FPs)
- [ ] **CLAIM-01** Extract paper data-inequality claims (alinker-paper `metric.tex`/`eval.tex`/`intro.tex` + local `eval.tex` Ch1) into a checklist with source locations
- [ ] **CLAIM-02** Verify each claim vs. computed numbers → MATCH / MISMATCH / STALE with the empirical value
- [ ] **CLAIM-03** Resolve the `XX` placeholders in `intro.tex` with computed values
- [ ] **MOTIV-01** Show empirically that file/link micro-F1 is long-tail / large-component dominated (Top-3 + random baselines exploit it) → why the 4-metric suite is needed
- [ ] **OUT-01** Self-contained `mini-inequality/` (README + report MD/CSV), stdlib-only, no cross-module imports, sanity-checked vs. canonical numbers
- [ ] **OUT-02** Paper-ready Gini/Lorenz table (+ optional Lorenz-curve data/figure) the paper can ingest

### Out of Scope

- Touching repo-root `.planning/` or the v1.2 milestone — strict isolation; this study lives only under `mini-inequality/`
- New trace-link *recovery* (this study measures the dataset + scores existing results; it does not produce a linker)
- Re-deriving the full 13-column metric suite — `mini-src/` already does the metric panel; this study is about the *distribution*, not per-system scores
- Third-party deps (pandas/numpy/matplotlib) — stdlib only; figures emitted as pgfplots/TeX or plain data files

## Context

- **Parent workspace**: TransArc-EMP research workspace (two pillars: TransArc empirical study + benchmark bias analysis). The repo-root `.planning/` is mid-milestone (v1.2); this sub-study is isolated to avoid colliding with it.
- **Live paper**: `/mnt/hostshare/ardoco-home/alinker-paper` (`main.tex` + `sections/`). Inequality claims live in `sections/metric.tex` (1.0×→217.6× expansion; long-tail both tasks), `sections/eval.tex` (long tail dominates the average; Top-3/random baselines exploit inequality), `sections/intro.tex` (unfilled `XX` placeholders: % gold-mass concentration on three sentences, trivial-baseline file F1). Local mirror: `writing/eval.tex` Ch1 "Distributional Inequality" (Gini 0.331→0.645; 96.0× / 36→3,457 cascade).
- **Benchmark data**: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/` (5 projects: mediastore, teastore, teammates, bigbluebutton, jabref). Gold standards: `goldstandard_sad_*-sam_*.csv`, `goldstandard_sam_*-code_*.csv`, `goldstandard_sad_*-code_*.csv`; code models `*.acm`.
- **Existing reference code** (read for definitions, do NOT import): `src/bias/component_suite.py` (`_gini`, `gold_gini` = Gini of gold #sentences-per-component), `mini-src/metrics.py` (enrollment, gold loaders, normalize_path — the stdlib pattern to mirror).
- **Key prior findings**: enrollment inflation up to ~217× (JabRef); gold link mass heavily right-skewed; LLM linkers nail popular components and abandon the long tail; file-level micro-F1 summarizes a handful of large components, not the recovery task.

## Constraints

- **Tech stack**: Python 3, stdlib only (`csv`, `json`, `collections`, `math`, `pathlib`, `argparse`). No requirements.txt.
- **Self-contained**: no imports from `src/` or `mini-src/`; definitions copied verbatim and sanity-checked for agreement.
- **Reproducibility**: benchmark/result roots derived from file location, overridable via `$TRANSARC_BENCHMARK` / `$TRANSARC_RESULTS_DIR`.
- **No benchmark leakage**: no benchmark-derived word lists (workspace CLAUDE.md rule). Distributional stats only.
- **Isolation (hard)**: never write to repo-root `.planning/`; commit only `mini-inequality/**` on branch `gsd/mini-data-inequality`.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Isolated branch + nested `mini-inequality/.planning/` | User requirement: must not collide with active v1.2 root `.planning/` | — Pending |
| Stdlib-only, self-contained (mirror `mini-src/`) | Faithful, dependency-free, sanity-checkable reduction | — Pending |
| Measure GOLD distribution as primary; results/baselines secondary | "Data inequality of the dataset" is an intrinsic property of the gold standard | — Pending |
| Verify against the live `alinker-paper`, mirror to local `eval.tex` Ch1 | alinker-paper is the live target (outputs were repointed there); eval.tex Ch1 is the local source of the same claims | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After the milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?

---
*Last updated: 2026-06-21 — v0.1 Data-Inequality Mini-Study defined (isolated sub-project).*
