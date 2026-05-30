# Milestones: TransArc-EMP

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
