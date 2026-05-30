---
phase: 04-metrics-api
verified: 2026-05-30T00:00:00Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
---

# Phase 4: Metrics API Verification Report

**Phase Goal:** A user can point a stdlib-only API at a TransArc-format results file (sad-sam or sad-code) and get the full metric set out as both CSV and a ready-to-paste LaTeX table.
**Verified:** 2026-05-30
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

The CLI was executed directly (not trusting SUMMARY claims). Both task paths run end-to-end, emit a 7-row wide CSV (header + 5 projects + Average) and a booktabs LaTeX table, and reproduce the already-published reference values exactly (jabref sad-code File 0.943 / Decision 0.394). Reuse-only and stdlib-only constraints hold; the sad-sam path is provably isolated from enrollment helpers.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `--task sad-sam` exits 0, computes metrics for all 5 projects (MTR-01) | ✓ VERIFIED | Ran: exit=0, `projects=5`, CSV has 5 project rows + Average |
| 2 | `--task sad-code` exits 0, applies gold enrollment, all 5 projects (MTR-02) | ✓ VERIFIED | Ran: exit=0, `projects=5`; uses `enroll_with_provenance` + `load_gs_sad_code` path; File/Decision differ per enrollment |
| 3 | Full metric set by reuse only, no benchmark word lists (MTR-03) | ✓ VERIFIED | sad-sam: link/sentence/decision/component + MCC/MAP/HUS numeric, file/weighted/ACF1/NDG = "—"; sad-code: file/decision/component/weighted + MCC/ACF1/NDG/HUS numeric, link/sentence/MAP = "—". 0 local metric-math redefs; only stdlib + 4 local imports |
| 4 | Wide CSV per task, 5 project rows + Average, stdlib csv (MTR-04) | ✓ VERIFIED | Both CSVs have 7 rows, header row[0]="project", last="Average"; `csv.writer` only |
| 5 | Ready-to-paste booktabs LaTeX table per task (MTR-05) | ✓ VERIFIED | Both .tex contain `tabular`, `\toprule/\midrule/\bottomrule`, `\fone` header macros, caption + label |
| 6 | Missing per-project results → stderr WARNING + skip, no crash | ✓ VERIFIED | Renamed jabref sad-code results: `WARNING: no sad-code results for jabref, skipping`, exit=0, projects=4. File restored |
| 7 | sad-code jabref File 0.943 / Decision 0.394 (reuse parity) | ✓ VERIFIED | CSV: jabref file_f1=0.943, decision_f1=0.394 — matches EVALUATION_CRITIQUE.md |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/lib/metrics_api.py` | stdlib CLI, ≥150 lines, argparse | ✓ VERIFIED | 311 lines; argparse with required `--task` choices + validated `--project`; imports all 4 reused modules |
| `reports/metrics_sad-sam.csv` | 5 rows + Average | ✓ VERIFIED | 7 CSV rows, correct schema, byte-identical to committed after regen |
| `reports/metrics_sad-code.csv` | 5 rows + Average | ✓ VERIFIED | 7 CSV rows, correct schema, byte-identical to committed after regen |
| `writing/tables/metrics_sad-sam.tex` | booktabs tabular | ✓ VERIFIED | tabular + booktabs rules + \fone header |
| `writing/tables/metrics_sad-code.tex` | booktabs tabular | ✓ VERIFIED | tabular + booktabs rules + \fone header |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| metrics_api.py | transarc_error_analysis (PROJECTS, calc_metrics, loaders) | `from transarc_error_analysis import` | ✓ WIRED | Imported and used in both compute paths |
| metrics_api.py (sad-code ONLY) | evaluation_critique `_compute_decision/component/weighted_f1` | `from evaluation_critique import` | ✓ WIRED | Used only in `compute_sad_code_row`; provably absent from `compute_sad_sam_row` body |
| metrics_api.py | new_metrics_analysis compute_mcc/map/acf1/ndg/hus | `from new_metrics_analysis import` | ✓ WIRED | All called across both paths |
| metrics_api.py | generate_tables render_table/write_table | `from generate_tables import` | ✓ WIRED | `write_latex` calls both; produces valid .tex |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| metrics_sad-sam.csv | per-project rows | `calc_metrics(load_gs_sad_sam, load_result_sad_sam_standalone)` | Yes — distinct F1 per project (0.694–0.947), matches NEW_METRICS_REPORT.md | ✓ FLOWING |
| metrics_sad-code.csv | per-project rows | provenance enrollment + `_compute_*_f1` over real gold/result sets | Yes — File≠Decision per enrollment inflation; jabref 0.943/0.394 reproduces published values | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| sad-sam full run | `metrics_api.py --task sad-sam` | exit 0, projects=5 | ✓ PASS |
| sad-code full run | `metrics_api.py --task sad-code` | exit 0, projects=5 | ✓ PASS |
| single-project filter | `--task sad-code --project jabref` | exit 0, projects=1 | ✓ PASS |
| invalid project rejected | `--project bogus` | stderr ERROR, exit 2 | ✓ PASS |
| missing results skip | rename jabref sad-code CSV, rerun | WARNING + skip, exit 0, projects=4 | ✓ PASS |
| jabref reuse parity | CSV inspection | File 0.943, Decision 0.394 | ✓ PASS |
| stdlib-only | import scan | no third-party imports | ✓ PASS |
| sad-sam isolation | body scan of compute_sad_sam_row | no `_compute_*`/enroll helpers | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| MTR-01 | 04-01-PLAN | sad-sam run computes all metrics, all projects | ✓ SATISFIED | Truth 1 + sad-sam CSV |
| MTR-02 | 04-01-PLAN | sad-code run with enrollment, all projects | ✓ SATISFIED | Truth 2 + sad-code CSV |
| MTR-03 | 04-01-PLAN | full metric set by reuse, no leakage | ✓ SATISFIED | Truth 3; 0 local metric defs; stdlib-only |
| MTR-04 | 04-01-PLAN | wide CSV, all projects one sheet, stdlib csv | ✓ SATISFIED | Truth 4 |
| MTR-05 | 04-01-PLAN | ready-to-paste booktabs LaTeX | ✓ SATISFIED | Truth 5 |

All 5 PLAN-declared requirement IDs map to Phase 4 in REQUIREMENTS.md traceability table. No orphaned requirements: REQUIREMENTS.md maps exactly MTR-01..05 to Phase 4, all claimed by the plan, all marked `[x]`.

### Anti-Patterns Found

None. The only `jabref` literal in the source is a docstring usage example (`--project jabref`), not a benchmark-derived word list. `PROJECTS` is imported from the loader module, not hardcoded. No TODO/FIXME/placeholder, no empty returns in active paths, no metric math reimplemented (verified 0 local defs of `calc_metrics`/`_compute_*`/`compute_mcc`). Prior code review (04-REVIEW-FIX.md) already removed dead imports including the dangerous non-provenance `enroll_gold_standard` re-export.

### Human Verification Required

None. All behaviors verified programmatically by running the CLI. LaTeX renders structurally correct (booktabs); no pdflatex available locally but that is an accepted deferred item in REQUIREMENTS.md (real PDF build out of scope this milestone).

### Gaps Summary

No gaps. All 7 observable truths verified, all 5 artifacts pass exists/substantive/wired/data-flowing, all 4 key links wired, all 5 requirements satisfied, no blocking anti-patterns. The CONTEXT locked decisions are honored: SAD-SAM uses the no-file link/sentence/component framing (no File column), and the sad-sam path provably never calls `_compute_decision_f1`/`_compute_component_f1`/`_compute_weighted_f1` or any enrollment helper. Reuse parity confirmed against published reference values (jabref 0.943/0.394). The known NDG low-decimal non-determinism did not manifest on these runs (deterministic, byte-identical regeneration) and would not constitute a gap per the verification spec.

---

_Verified: 2026-05-30_
_Verifier: Claude (gsd-verifier)_
