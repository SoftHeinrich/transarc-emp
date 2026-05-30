---
phase: 1
phase_name: Reorganize
status: passed
date: 2026-05-30
verifier: inline (main context — subagent git ops unsafe on hostshare mount)
---

# Phase 1: Reorganize — Verification

Goal-backward check of the 5 ROADMAP success criteria. **Result: PASSED.**

| # | Success Criterion | Evidence | Verdict |
|---|-------------------|----------|---------|
| 1 | src/ has clear Pillar 1 (transarc) + Pillar 2 (bias) grouping | `src/` dirs = `bias lib transarc`; transarc=4 .py (propagation×3 + s12c), bias=9 .py (4 original + 5 evaluation) | PASS |
| 2 | s12c script + S12C_VS_TRANSARC.csv co-located with Pillar 1 | `src/transarc/s12c_sadcode_comparison.py` present (git mv, tracked); `reports/S12C_VS_TRANSARC.csv` intact (reports/ stays flat by design) | PASS |
| 3 | src/annotation gone; both annotation scripts under archive/ | `src/annotation/` removed; `archive/doc_structure_analysis_v2.py` + `archive/reverse_engineer_convention.py` present | PASS |
| 4 | ANNOTATION_CONVENTION.md + gray reports under archive/ | `archive/ANNOTATION_CONVENTION.md` present; no longer in reports/ | PASS |
| 5 | No retained script imports archived path; no retained report links archived work | grep archived-module imports in src/ = 0; grep ANNOTATION_CONVENTION in reports/ = 0; grep swattr in src/ = 0 | PASS |

## Requirements Coverage

SCOPE-01..05, ARCH-01..04 — all satisfied (see Task-3 checks in SUMMARY).

## Structural Invariant

Depth-2 layout preserved: every pillar script is `src/<pillar>/<script>.py`, so
`sys.path.insert(parent.parent/"lib")` resolves to `src/lib` for all 13 retained
pillar scripts. No `.py` content edited. Actual run-time reproducibility is
Phase 2's scope (REPRO-01/02/03).

## Notes

- Working tree clean after execution.
- Environment caveat (flaky git on hostshare mount) documented in SUMMARY; all
  commits verified to have landed via `git log` after each step.
