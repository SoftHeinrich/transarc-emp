# TransArc-EMP — Retrospective

## Milestone: v1.0 — Two-Pillar Refactor

**Shipped:** 2026-05-30
**Phases:** 3 | **Plans:** 3 | **Tasks:** 8

### What Was Built

- **Phase 1 (Reorganize)**: `src/` collapsed into two pillars — `src/transarc/` (3 propagation scripts + s12c) and `src/bias/` (4 original + 5 evaluation scripts) — shared `src/lib/` untouched; annotation work archived. All via `git mv`, zero code edits (depth-2 import invariant held).
- **Phase 2 (Verify)**: all 13 pillar scripts run clean (exit 0); reports regenerate byte-identically — reproducibility confirmed.
- **Phase 3 (Paper)**: `writing/eval.tex` restructured to Ch1=TransArc study (`\input{ch1_transarc}`) + Ch2=merged Benchmark Bias; new stdlib `src/paper/generate_tables.py` emits 10 booktabs tables from retained data.

### What Worked

- **Ground-truth-first planning**: the planner verified actual filenames/tracking state via `git ls-files` before writing the plan, catching that s12c was untracked (needs `mv`+`add`, not `git mv`) and that `new_metrics_analysis.py` is a library (stays in lib).
- **Depth-preserving moves**: keeping `src/<pillar>/x.py` depth meant `sys.path.insert(parent.parent/"lib")` resolved everywhere with no `.py` edits — a pure-move phase stayed pure.
- **Reframing SC4 with the user** instead of forcing a pdflatex install — matched the real need (tables from data for an external paper).

### What Was Inefficient

- **Hostshare mount fought every step**: flaky git stat-cache (false "deleted"/"stub" alarms), corrupted Read-tool output, aliased phantom files during archival, dropped/delayed shell output. Cost many re-reads and a false "files are stubs" investigation.
- **Subagent git ops were unsafe** on the mount (index races) — forced all git work inline in the main context, serializing what could have parallelized.

### Patterns Established

- On this mount: `git update-index -q --refresh` before any status read; prefer `git ls-files`/`git hash-object`/`find` over porcelain + shell `ls`; `sed -n` with sandbox off for clean file reads; subagents write files only, orchestrator commits.
- Reorg phases: verify tracked-vs-untracked per file before choosing `git mv` vs `mv`+`add`.

### Key Lessons

- Distrust a single shell/`ls`/Read result on a network mount — confirm via an independent path (git object layer, `find`, re-run) before acting destructively.
- "Move-only" phases benefit enormously from a static depth/import invariant stated up front; it turns verification into grep checks.

### Cost Observations

- Model mix: Opus (orchestrator + planning/paper subagents). Subagents: gsd-planner (Phase 1), claude (Phase 3 authoring).
- Notable: inline serial execution due to mount constraints raised orchestrator token use but avoided index corruption.

## Cross-Milestone Trends

(first milestone — trends begin next cycle)
