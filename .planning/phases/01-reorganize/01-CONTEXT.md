# Phase 1: Reorganize - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Restructure `src/` and `reports/` into two explicit pillars and move out-of-scope
work into `archive/` — non-destructively (`git mv`). This phase is **moves only**:
no behavioral code changes, no renames of shared modules, no edits to analysis logic.

- **Pillar 1 — TransArc empirical study**: error/cascade/contribution analysis + s12c comparison.
- **Pillar 2 — Benchmark bias analysis**: enrollment-inflation critique, File/Decision/Component
  metrics, trivial/extreme baselines, proposed alternative metrics.

Out of this phase: verifying scripts still run (Phase 2), paper restructure (Phase 3).
</domain>

<decisions>
## Implementation Decisions

### Pillar Layout (depth-2 preserved → zero import edits)
- Target tree:
  ```
  src/
    transarc/   <- propagation/*.py (3) + evaluation/s12c_sadcode_comparison.py
    bias/       <- existing bias/*.py (4) + evaluation/{evaluation_critique,
                   creative_metrics_analysis, holistic_metrics_analysis,
                   extreme_baseline_analysis, stupid_baseline_analysis}.py (5)
    lib/        <- transarc_error_analysis.py, new_metrics_analysis.py (UNCHANGED)
  archive/      <- src/annotation/* + reports/ANNOTATION_CONVENTION.md
  ```
- Scripts stay at depth `src/<pillar>/script.py` so every
  `sys.path.insert(0, parent.parent / "lib")` still resolves — **no code edits**.
- Remove the now-empty `src/evaluation/` and `src/propagation/` directories after moves.
- All moves use `git mv` (non-destructive archival convention).

### Shared Library Handling
- Keep `src/lib/transarc_error_analysis.py` name as-is even though it serves both
  pillars (9 importers via `from transarc_error_analysis import ...`). Renaming would
  force a sed across 9 files + re-verification — out of scope for a move-only milestone.
- `src/lib/new_metrics_analysis.py` **stays in `src/lib/`**: it is imported as a library
  by other scripts (not a standalone Pillar-2 script), so it is shared infrastructure.
  This resolves the STATE.md open question on SCOPE-05 — it is NOT moved into the bias pillar.

### Reports Grouping
- `reports/` stays flat (no per-pillar subdirs) — scripts write outputs to `reports/`
  via fixed relative paths; subdividing would break output paths. Pillar association is
  documented, not enforced by directory.
- `reports/ANNOTATION_CONVENTION.md` → `archive/` (supports archived annotation work).
- Other reports stay; each maps to a retained script (Pillar 1 or 2).

### Archive Targets
- `src/annotation/doc_structure_analysis_v2.py` and `src/annotation/reverse_engineer_convention.py`
  → `archive/` (self-contained pair; reverse_engineer imports doc_structure_analysis_v2, both move).
- SWATTR FP-filter work already in `archive/` — leave untouched, confirm nothing retained imports it.

### Claude's Discretion
- Exact `git mv` ordering and whether to `git rm` the stale `__pycache__` dirs during moves.
- Final cleanup of empty directories.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/lib/transarc_error_analysis.py` (1186 ln) — shared data loaders: PROJECTS,
  load_code_model_files, enroll_gold_standard, gold loaders, calc_metrics. 9 importers.
- `src/lib/new_metrics_analysis.py` (1183 ln) — proposed-metrics library, imported by other scripts.

### Established Patterns
- Every analysis script: `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))`
  then `from transarc_error_analysis import (...)`. Fixed depth-2 assumption.
- Scripts read benchmark data from `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/.../benchmark/`
  and write reports to `reports/`.

### Integration Points
- Import edges to preserve: bias/*, evaluation/*, propagation/*, s12c → `lib/transarc_error_analysis`.
- `evaluation/extreme_baseline_analysis` (and others) → `lib/new_metrics_analysis`.
- `annotation/reverse_engineer_convention` → `annotation/doc_structure_analysis_v2` (both archived together).

### Environment Caveat
- Repo lives on a hostshare mount with a flaky git stat-cache: `git status` can transiently
  report tracked files as "deleted". Run `git update-index -q --refresh` before trusting status.
</code_context>

<specifics>
## Specific Ideas

- s12c script + `reports/S12C_VS_TRANSARC.csv` already committed (b1407e1) in their pre-move
  location (`src/evaluation/`, `reports/`); Phase 1 moves the script into `src/transarc/`.
</specifics>

<deferred>
## Deferred Ideas

- Rename `transarc_error_analysis.py` → `data_loaders.py` for clarity (v2; needs 9-file sed).
- Top-level README mapping the two-pillar structure (DOC-01, v2).
- Per-pillar reproduce instructions (DOC-02, v2).
</deferred>
