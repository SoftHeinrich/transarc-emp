# CLAUDE.md — TransArc-EMP

Project-local guidance for Claude Code. The workspace-level `../CLAUDE.md` (ARDoCo monorepo) also applies.

## What This Is

Research workspace studying ARDoCo's transitive TLR (TransArc) and its benchmark evaluation. Being refactored down to **two pillars**:

1. **TransArc empirical study** — error analysis, SAD-SAM bottleneck, error amplification/cascade, S12C/S12E-vs-TransArc comparison.
2. **Benchmark bias analysis** — enrollment-inflation critique of file-level P/R/F1, trivial/extreme baselines (evidence), proposed alternative metrics.

Output: aligned LaTeX paper `writing/eval.tex` (Ch1 = TransArc study, Ch2 = Benchmark bias).

## Stack

- Python 3 (stdlib only: csv, json, collections, dataclasses, math, pathlib, re). No requirements.txt — no third-party deps.
- LaTeX (`report` class) for the paper.
- Run a script: `python3 src/<area>/<script>.py`. Outputs land in `reports/`.
- Benchmark data lives outside this repo: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/` (mediastore, teastore, teammates, bigbluebutton, jabref).
- Shared data loaders in `src/lib` (PROJECTS, BENCHMARK, RESULTS, `load_code_model_files`, `enroll_gold_standard`, gold loaders) — imported by both pillars via `sys.path.insert` to `src/lib`.

## Conventions

- **Archival is non-destructive**: out-of-scope work moves to `archive/` via `git mv` — never deleted.
- **No benchmark leakage**: no benchmark-derived word lists in any code (per workspace CLAUDE.md). Stopwords only.
- Reports are generated markdown/CSV in `reports/`; keep them consistent with the script that produces them.

## GSD Workflow

This project uses Get-Shit-Done planning (`.planning/`). Config: YOLO mode, coarse granularity, parallel execution, plan-check + verifier on, research off.

- Roadmap: `.planning/ROADMAP.md` (3 phases: Reorganize → Verify → Paper)
- State: `.planning/STATE.md` · Requirements: `.planning/REQUIREMENTS.md` · Context: `.planning/PROJECT.md`
- Next step: `/gsd-discuss-phase 1` then `/gsd-plan-phase 1`. Use `/gsd-progress` to check status.
- Each phase commits its own artifacts atomically.
