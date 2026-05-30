---
phase: 04-metrics-api
reviewed: 2026-05-30T16:53:05Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - src/lib/metrics_api.py
findings:
  critical: 0
  warning: 1
  info: 5
  total: 6
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-05-30T16:53:05Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Reviewed `src/lib/metrics_api.py`, a stdlib-only Python 3 CLI that reports a unified
metric set for `sad-sam` and `sad-code` TransArc runs by reusing existing primitives.
Verification was cross-checked against the actual signatures and return shapes of every
reused helper in `transarc_error_analysis.py`, `new_metrics_analysis.py`,
`evaluation_critique.py`, and `generate_tables.py`.

**Project-rule compliance (all PASS):**
- **stdlib-only**: confirmed. Only `csv`, `json`, `math`, `os`, `sys`, `argparse`,
  `collections.defaultdict`, `pathlib.Path` are imported. No third-party deps.
- **No benchmark-derived word lists**: confirmed. No hardcoded component names, aliases,
  or synonym tables anywhere. Component naming is resolved at runtime via
  `load_model_element_names`.
- **sad-sam path does NOT call SAD-CODE-only enrollment helpers**: confirmed.
  `compute_sad_sam_row` (lines 98-168) never calls `_compute_decision_f1`,
  `_compute_component_f1`, or `_compute_weighted_f1`; those are confined to
  `compute_sad_code_row` (lines 203-206). The dispatch in `main` (line 291) routes each
  task to its own function.
- **Graceful missing-results handling**: confirmed at three levels — per-project skip+warn
  on empty `res` (lines 109-112, 181-183), `load_result_*` returns `set()` when the file is
  absent, and `main` emits a "no results found" warning while still writing a header +
  empty Average row (lines 299-305).
- **argparse correctness**: confirmed. `--task` is `required=True` with
  `choices=["sad-sam","sad-code"]`; `--project` defaults to `None` and is validated in
  `select_projects` with `sys.exit(2)` on an unknown value.
- **Call-convention correctness** (high-risk area) verified against source:
  - `compute_random_f1` returns a bare float and is used as such (line 217) — matches the
    inline comment and the definition at `new_metrics_analysis.py:383`.
  - `compute_oracle_f1` returns `(f1, oracle)`; correctly unpacked as `oracle_f1, _`
    (line 219).
  - `compute_hus` groups by element `[0]`; the sad-sam path correctly flips pairs to group
    by sentence (lines 159-161), the sad-code path correctly passes `enrolled` unflipped
    (line 223, already `(sentence, file)`).
  - `transarc_sad_sam_as_ranked` consumes `(comp, sent)` and yields `(sent, comp, 0.5)`;
    `compute_map` expects exactly that ranked shape (line 154-155).
  - `render_table` emits `header_override` verbatim, so the `\fone` macros in
    `LATEX_HEADER` survive un-escaped (correct), while data cells are escaped.

No correctness or security defects were found. The one Warning and the Info items below
are maintainability / robustness improvements.

## Warnings

### WR-01: Unused imports (`json`, `os`) and unused re-exported symbols

**File:** `src/lib/metrics_api.py:23-25, 36, 38, 55`
**Issue:** Seven imported names are never referenced in the module body (each appears
exactly once — on its import line). Confirmed by usage scan:
- `import json` (line 23) — unused
- `import os` (line 25) — unused
- `enroll_gold_standard` (line 36) — unused (the code uses `enroll_with_provenance` and
  `load_sam_code_enrolled` instead)
- `load_gs_sad_code_enrolled` (line 38) — unused (the code uses
  `load_sad_code_raw_with_provenance` + `enroll_with_provenance`)
- `latex_escape` (line 55) — unused (escaping happens inside `render_table`)
- `colspec` (line 55) — unused (`render_table` derives the colspec internally)
- `BENCHMARK` (line 35) — unused

This is grouped as a single Warning rather than Info because the dead `enrollment` /
`escape` imports invite a future maintainer to call the wrong helper — e.g. reaching for
`enroll_gold_standard` (no provenance) in the sad-code path, which would silently break the
decision/weighted F1 math that depends on the provenance maps. Removing them removes that
trap.
**Fix:**
```python
import csv
import math
import sys
import argparse
from collections import defaultdict
from pathlib import Path

from transarc_error_analysis import (
    PROJECTS, RESULTS, calc_metrics,
    load_code_model_files,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_maps,
    load_result_sad_sam_standalone,
    load_result_sad_code, load_text, load_model_element_names,
)
...
from generate_tables import render_table, write_table
```
(Drop `json`, `os`, `BENCHMARK`, `enroll_gold_standard`, `load_gs_sad_code_enrolled`,
`latex_escape`, `colspec`. Verify `RESULTS` is still wanted — it is unused too, but is the
sibling of the hardcoded `REPORTS` path and arguably documents intent; keep or drop per
preference.)

## Info

### IN-01: `RESULTS` import is also unused

**File:** `src/lib/metrics_api.py:35`
**Issue:** `RESULTS` is imported but never referenced (the result paths are resolved inside
the `load_result_*` helpers). Listed separately from WR-01 because it is harmless
documentation rather than a misuse trap.
**Fix:** Remove from the import list, or leave a comment if intentionally kept for symmetry
with the hardcoded `REPORTS` path.

### IN-02: MCC universe for sad-code mixes two enrollment sources

**File:** `src/lib/metrics_api.py:226-228`
**Issue:** `all_files` is built from `gs_sam_code_map.values()` (SAM-CODE enrollment) while
`enrolled` / `res` use SAD-CODE enrollment. If the two file universes diverge, the `tn`
term in `compute_mcc` (and thus MCC) is computed against a slightly inconsistent universe.
This cannot crash and is a defensible modeling choice, but it is worth a one-line comment so
a future reader does not mistake it for a bug.
**Fix:** Add a comment documenting that the MCC universe is the SAM-CODE file set by design,
or union it with the SAD-CODE file set: `all_files = set().union(*gs_sam_code_map.values()) | {c for (_s, c) in enrolled}`.

### IN-03: `_fmt` em-dash equality check is value-based, not sentinel-based

**File:** `src/lib/metrics_api.py:267`
**Issue:** `write_latex` decides LaTeX N/A cells with `row[c] != NA` (string comparison
against the em dash). This works today because all metric values are floats or the exact
`NA` constant, but a future metric that legitimately returns the string `"—"` would be
silently rendered as `--`. Low risk.
**Fix:** Prefer a type check that mirrors `_fmt` / `build_avg_row`:
`cells.append(_fmt(row[c]) if isinstance(row[c], (int, float)) else NA_TEX)`.

### IN-04: Three `sys.path.insert(0, ...)` calls mutate global import state

**File:** `src/lib/metrics_api.py:33, 47, 54`
**Issue:** The module inserts three sibling directories onto `sys.path` at import time. This
is the established pattern for this codebase (per CLAUDE.md, shared loaders are imported via
`sys.path.insert`), so it is not a defect — flagged only for awareness that importing this
module as a library (rather than running it as a script) has the side effect of permanently
altering `sys.path` and could shadow same-named modules elsewhere.
**Fix:** None required given project conventions. If stricter isolation is ever wanted,
guard the inserts behind `if __name__ == "__main__":` or de-dupe with
`if p not in sys.path:`.

### IN-05: Inline transform comment references "CONTEXT" not present in the file

**File:** `src/lib/metrics_api.py:130, 231`
**Issue:** Comments cite a `CONTEXT` document ("sanctioned by CONTEXT ...", "CONTEXT: MAP at
sad-code is optional") that is not linked or reproduced in-repo. Harmless, but the reference
will rot once the planning artifact is archived.
**Fix:** Replace `CONTEXT` with a concrete pointer (e.g. the phase plan path) or inline the
one-sentence rationale so the justification survives independently.

---

_Reviewed: 2026-05-30T16:53:05Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
