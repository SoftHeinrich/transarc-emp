---
phase: 05-consequences-study-converged-metrics
reviewed: 2026-05-30T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - src/bias/consequences_study.py
  - src/paper/generate_tables.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-05-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed the new `src/bias/consequences_study.py` and the delta in
`src/paper/generate_tables.py` (new `_load_metrics`/`_fmt_dec` helpers, the
`t_consequences`/`t_converged_framework` builders, and the `raw_cols=` parameter
on `render_table`). Both scripts run cleanly and produce output that exactly
matches the source CSVs.

All project-rule checks pass:

- **Stdlib only** — `consequences_study.py` imports only `csv` and `pathlib`;
  the new code in `generate_tables.py` adds no imports. No third-party deps.
- **No benchmark leakage** — `PROJECT_ORDER` is opaque CSV ordering data
  (acceptable per the brief); no derived word lists.
- **No /100 division** — verified `consequences_study.py` contains no `/100`;
  the new builders use `_fmt_dec` (raw `float(v)`), never `_fmt_f1`. `_fmt_f1`
  remains correctly scoped to the percentage-based `S12C_VS_TRANSARC.csv`
  builders only.
- **`raw_cols` default preserves prior behavior** — `raw_cols=None` resolves to
  an empty `set`, so every cell is escaped via `latex_escape` exactly as before
  the change. All eight pre-existing `render_table` callers omit `raw_cols`,
  confirmed unaffected.
- **Em-dash / CSV handling correct** — the CSV uses U+2014 (`e2 80 94`);
  `num()` and `_fmt_dec` both match U+2014 and map it (plus blank/None) to N/A.
  In the generated `consequences.tex`, all SAD-CODE `sentence_f1` cells (em-dash
  in the CSV) render as `--`. Confirmed against generated output.
- **No average recomputation** — `consequences_study.py` reads the CSV
  `Average` row verbatim; `t_converged_framework` reads the `Average` rows
  directly. (The pre-existing `t_s12c_four_level`/`t_dashboard` recompute
  averages, but those are untouched and out of delta scope.)

Verified numeric claims against the CSVs: largest SAD-SAM link−sentence gap is
teammates (−0.206, matches the "understates per-sentence retrieval" prose);
JabRef ranks #1 by file F1 and #5 by decision F1 (matches the "best yet worst"
ranking-flip narrative); SAD-CODE ranking flips = 3; converged deltas
0.000 (SAM) and 0.207 (CODE) match the rendered table.

Only two minor Info items, both latent robustness notes — no behavioral bug
under the current CSVs.

## Info

### IN-01: Sort keys assume `file_f1`/`decision_f1` are never N/A (latent fragility)

**File:** `src/bias/consequences_study.py:161-162`, `225-226`
**Issue:** The ranking sorts use `key=lambda p: num(rows[p]["file_f1"])` and
`...["decision_f1"]`. `num()` returns `None` for an em-dash/blank cell, and
Python 3 raises `TypeError` when `sorted` compares `None` against a `float`. The
current `metrics_sad-code.csv` always populates these two columns, so this never
triggers today — but unlike `part_sad_sam`'s `worst = max(...)` (line 107),
which guards `None` with a `-1` sentinel, these `sorted` calls have no guard. A
future CSV with an N/A in either column would crash these SAD-CODE sections.
**Fix:** Mirror the sentinel guard already used at line 107, e.g.
`key=lambda p: (num(rows[p]["file_f1"]) or -1.0)`, for the four `sorted` calls.

### IN-02: Redundant duplicate em-dash literal in `num()`

**File:** `src/bias/consequences_study.py:54`
**Issue:** The membership tuple is `("—", "—", "", None)` — both string
literals are the identical character U+2014 (verified by codepoint), so the
second entry is dead/redundant. Harmless, but it reads as if it were guarding
two distinct dash characters (e.g. en-dash vs em-dash) when it is not.
**Fix:** Drop the duplicate: `return None if v in ("—", "", None) else float(v)`.
If the intent was to also tolerate an en-dash (U+2013), replace the duplicate
with `"–"` instead.

---

_Reviewed: 2026-05-30T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
