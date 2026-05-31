# Milestones: TransArc-EMP

## v1.1 — Metrics Toolkit & Converged-Metric Motivation

**Shipped:** 2026-05-31
**Phases:** 3 | **Plans:** 4 | **Tasks:** 6
**Tag:** `v1.1`

**Delivered:** A reproducible stdlib metrics API + a motivation study quantifying how a
misleading headline F1 distorts BOTH evaluation tasks, a converged metric framework
unifying them, and a handoff-ready two-pillar repo.

**Key accomplishments:**
1. `src/lib/metrics_api.py` — stdlib CLI computing the full per-task metric set for sad-sam + sad-code, emitting CSV + paste-ready LaTeX, reusing existing primitives with zero metric-math reimplementation.
2. Corrected the SAD-SAM metric framing: no file/enrollment granularity (link/sentence/component only); the SAD-CODE enrollment helpers are fenced out of the sad-sam path.
3. `src/bias/consequences_study.py` → `reports/CONSEQUENCES_STUDY.md` quantifying SAD-SAM pure-F1 and SAD-CODE file-level consequences (JabRef File 0.943 → Decision 0.394 flip).
4. Converged metric framework — Decision + Component as the common honest axis across both tasks — written into `eval.tex` Ch2 (`sec:eval:misleading-both` + protocol extension) with new generated tables.
5. Top-level `README.md`: two-pillar map + per-pillar reproduce instructions, commands spot-run live.

**Known deferred:** NDG/weighted column low-decimal non-determinism (`compute_random_f1` set-iteration order) — source-level fix deferred. CLI `milestone.complete` handler errored; archival done manually.

**Archives:** `milestones/v1.1-ROADMAP.md`, `milestones/v1.1-REQUIREMENTS.md`,
`milestones/v1.1-MILESTONE-AUDIT.md`.

**Audit:** PASSED (11/11 requirements, integration clean, E2E reproduce verified).

---

## v1.0 — Two-Pillar Refactor

**Shipped:** 2026-05-30
**Phases:** 3 | **Plans:** 3 | **Tasks:** 8
**Tag:** `v1.0`

**Delivered:** Narrowed the TransArc-EMP workspace to two reproducible pillars
(TransArc empirical study + benchmark bias analysis) and aligned the paper.

**Key accomplishments:**
1. Reorganized `src/` into Pillar 1 (`src/transarc/`) + Pillar 2 (`src/bias/`) + shared `src/lib/`; out-of-scope work archived non-destructively.
2. Co-located the S12C/S12E-vs-TransArc comparison with Pillar 1.
3. Verified both pillars: 13/13 scripts run clean, reports regenerate deterministically.
4. Restructured `writing/eval.tex`: Ch1 = TransArc study, Ch2 = Benchmark bias (two prior chapters merged).
5. Added a stdlib data-driven LaTeX table generator (`src/paper/generate_tables.py` → 10 tables).

**Scope change:** Phase 3 SC4 reframed from "pdflatex compiles" to "tables generated
via script + structural validation" (no local LaTeX toolchain; chapters feed a larger
external paper).

**Archives:** `milestones/v1.0-ROADMAP.md`, `milestones/v1.0-REQUIREMENTS.md`,
`milestones/v1.0-MILESTONE-AUDIT.md`.

**Audit:** PASSED (16/16 requirements). No known gaps.
