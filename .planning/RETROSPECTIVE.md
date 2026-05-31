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

## Milestone: v1.1 — Metrics Toolkit & Converged-Metric Motivation

**Shipped:** 2026-05-31
**Phases:** 3 | **Plans:** 4

### What Was Built
A stdlib metrics API (`metrics_api.py`) turning TransArc-format results into a full per-task
metric set as CSV + LaTeX; a consequences study (`consequences_study.py` → `CONSEQUENCES_STUDY.md`)
quantifying misleading-F1 harm for both tasks; a converged Decision+Component framework written
into `eval.tex` Ch2 with new generated tables; and a top-level two-pillar `README.md`.

### What Worked
- **User correction caught early in discuss** — the "SAD-SAM has no file level" fix landed during
  grey-area discussion (before any code), so the locked CONTEXT carried the right framing into
  pattern-mapper → planner → executor → verifier. One correction propagated cleanly through the chain.
- **Reuse-only mandate + published-value parity** as the verification anchor — every metric had to
  reproduce an already-published number (JabRef 0.943/0.394), making "correct" objectively checkable.
- **Pattern-mapper before planner** surfaced load-bearing gotchas (CSV is 0–1 decimals with a
  pre-computed Average row; `compute_random_f1` returns a bare float) that would otherwise have been
  runtime crashes — the plan-checker confirmed they were fenced out.
- **Citation-chain wave split** (analysis → paper) kept Phase 5 honest: the paper mirrors numbers the
  script actually emits, verified by the integration checker running the full E2E chain live.

### What Was Inefficient
- **`gsd-sdk` handlers glitchy on this project**: `state.advance-plan` left `--name`/`--phase`
  placeholders in STATE.md (executors patched manually each phase); `milestone.complete` errored
  outright ("version required for phases archive") — milestone archival done by hand.
- **NDG non-determinism** surfaced late (in outputs) rather than predicted from source; cost a couple
  of artifact-refresh commits and a deferred-debt entry.

### Patterns Established
- For metric/analysis phases: anchor acceptance criteria to already-published numbers; treat any
  reused function's return shape as a "read the source first" item in `read_first`.
- Per-task metric schemas with explicit N/A cells beat forcing a shared column that doesn't apply.
- When a CLI SDK handler fails, fall back to manual file ops following the prior milestone's archive pattern.

### Key Lessons
- A single substantive framing correction is far cheaper in discuss than in code — get the
  metric/domain model right before planning.
- "Reuse, don't reimplement" only pays off if verification re-checks the reused numbers against an
  independent source; otherwise silent schema drift hides.

### Cost Observations
- Model mix: Opus orchestrator; sonnet executors/checkers/reviewers/verifiers; opus planners.
- Sequential single-tree execution (one plan/wave) — no worktree parallelism needed at this scale.
- Notable: pattern-mapper + plan-checker caught two would-be runtime crashes pre-execution.

## Cross-Milestone Trends

| Metric | v1.0 | v1.1 |
|--------|------|------|
| Phases | 3 | 3 |
| Plans | 3 | 4 |
| Audit result | PASSED (16/16) | PASSED (11/11) |
| Scope/framing changes | 1 (SC4 reframe) | 1 (SAD-SAM metric framing corrected) |
| Recurring friction | hostshare mount flakiness | `gsd-sdk` state/milestone handler glitches |

- **Persistent theme:** tooling/environment friction (mount in v1.0, SDK handlers in v1.1) repeatedly
  forced manual inline fallbacks. Both milestones still shipped clean audits — the planning structure
  absorbed the friction.
- **Verification discipline held:** both milestones verified against independent ground truth
  (reproducible reports v1.0; published metric values v1.1).
