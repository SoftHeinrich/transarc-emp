---
phase: 08-multi-system-comparison-fitness-validation
verified: 2026-06-21T23:05:00Z
status: passed
score: 4/4 success criteria verified (+ all project invariants)
overrides_applied: 1
overrides:
  - must_have: "The scorecard is hardened beyond random/top-3 (≥1 cleverer baseline; legacy systems where data exists)"
    reason: "User-directed, locked deviation (08-CONTEXT D-01/D-02/D-03, verbatim user quotes in <specifics>): NO new synthetic baselines. rq2 Random/Top-3 stays the trivial floor; SC3's 'hardened beyond random/top-3' is satisfied by the REAL multi-system set (3 paper systems: swattr/transarc, s20linker, artemis as the real comparators above the trivial floor). Legacy s11/s13f/s12c explicitly excluded ('just systems in the paper'). The report documents this reinterpretation explicitly (METRIC_FITNESS.md line 3, D-01)."
    accepted_by: "verifier (per 08-CONTEXT D-01..D-03, user-locked)"
    accepted_at: "2026-06-21T23:05:00Z"
---

# Phase 8: Multi-System Comparison & Fitness Validation — Verification Report

**Phase Goal:** A defensible, hardened comparison establishes — with a fitness scorecard — that tail coverage (`min_comp`/`pct_missed`) is the level-stable discriminator and which columns are headline vs diagnostic, across swattr/transarc, s20linker, artemis. (CMP-03, CMP-04)
**Verified:** 2026-06-21T23:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

Verification was goal-backward and adversarial: scripts were re-run in the verifier's own process, CSV cells were read directly, the graceful-skip demo was independently reproduced, and the equivalence/determinism oracle was re-run as a regression gate. SUMMARY claims were treated as unverified until codebase evidence confirmed them.

## Goal Achievement

### Observable Truths (Success Criteria)

| # | Success Criterion | Status | Evidence |
|---|-------------------|--------|----------|
| SC1 | Suite runs over all 3 present systems at both levels into committed `reports/COMPONENT_SUITE_{level}.csv` + hardened `COMPONENT_SUITE.md`; graceful skip for absent external roots; artemis source pinned & deterministic | ✓ VERIFIED | See SC1 below |
| SC2 | `metric_fitness.py` scores each candidate column on 4 axes (separation/validity/stability/degeneracy) at both levels → `METRIC_FITNESS.{md,csv}`; exit 0 + byte-identical 2nd run | ✓ VERIFIED | See SC2 below |
| SC3 | Verdict is DATA-DERIVED from computed axis scores, stated WITH numbers, hardened by 3 real systems vs rq2 trivial floor (no new baselines, D-01); honesty preserved | ✓ VERIFIED (override on the "≥1 cleverer baseline" literal wording — D-01) | See SC3 below |
| SC4 | Artemis long-tail abandonment reproduced + quantified under gold-only tail def; cited AVG numbers MATCH committed `COMPONENT_SUITE_{level}.csv` gold-only columns | ✓ VERIFIED | See SC4 below |

**Score:** 4/4 success criteria verified.

---

### SC1 — CMP-03: 3-system, 2-level comparison (pinned, deterministic, graceful skip)

**PASS.**

- **Artemis source pinned (08-01):** `git ls-files results_artemis_gpt54/` = 25 files tracked; all 5 canonical sad-code link files tracked (`git ls-files 'results_artemis_gpt54/*/sad-code/sadSamTlr_*.csv'` = 5); `git status --short results_artemis_gpt54/` shows nothing untracked. `reports/ARTEMIS_PROVENANCE.md` (68 lines) names `results_artemis_gpt54/` AUTHORITATIVE, `ARTEMIS_DOC_CODE` EXTERNAL/unvendored, `reports_artemis_gpt54_*` + `paper-result/` SECONDARY/SUPERSEDED — and its path claims match `component_suite.py` constants (`ARTEMIS_LOCAL` line 84, `ARTEMIS_DOC_CODE` line 83, `_artemis_model` reads `<proj>/sad-code/sadSamTlr_<proj>.csv` line 145).
- **Determinism (re-run by verifier):** `python3 src/bias/component_suite.py` exit 0, no warnings (all 3 roots present). Run-1 vs Run-2 byte-identical for BOTH levels. `diff` against the committed CSVs is empty; `git diff --stat` on both CSVs is empty — committed numbers reproduce exactly under the pinned source.
- **Coverage:** both CSVs carry 18 data rows (3 systems × 5 projects + 3 AVG); header `project,system,micro,macro,gap,min_comp,pct_missed,gold_gini` unchanged; `grep -c artemis sad-code.csv` = 6 (likewise s20linker, swattr/transarc).
- **Hardened `COMPONENT_SUITE.md`:** cross-level narrative present; `WARNING:` policy (×3) with a guarded-roots table naming `AGENT_LINKER` / `ARTEMIS_DOC_CODE` / `ARTEMIS_LOCAL`; swattr≡transarc one-column note (D-12); `ARTEMIS_PROVENANCE.md` cross-reference; cited swattr/transarc sad-code AVG (0.795/0.813) and artemis sad-model (0.835/0.813, min_comp 0.279, pct_missed 0.083) trace to the CSV cells.
- **Graceful skip independently reproduced:** setting `cs.ARTEMIS_LOCAL = Path('/nonexistent_artemis_root')` and calling `cs.run_level('sad-model',['mediastore'])` emitted the standardized line `WARNING: no sad-model result links for system=artemis project=mediastore (absent or empty external root); skipping`, returned 2 present-system rows (`swattr_transarc`, `s20linker`), skipped artemis, did NOT hard-fail. Committed CSVs + `component_suite.py` unchanged afterward (`git status --short` empty; CSVs still match committed).

### SC2 — CMP-04: fitness scorecard, 4 axes, both levels, deterministic

**PASS.**

- `src/bias/metric_fitness.py` (509 lines) parses; imports are stdlib-only (`csv, random, statistics, sys, collections, pathlib`) + project modules (`component_suite`, `rq2_trivial_baselines`, `transarc_error_analysis`) — no third-party.
- `python3 src/bias/metric_fitness.py` exits 0, writes `reports/METRIC_FITNESS.csv` (10 data rows = 5 columns × 2 levels) + `reports/METRIC_FITNESS.md`. CSV header: `level,column,separation,validity,stability,degeneracy,verdict`.
- **Determinism (re-run by verifier):** Run-1 vs Run-2 byte-identical; matches committed; `git status` clean. **Cross-process:** 3 fresh `PYTHONHASHSEED=random` runs produce one identical md5 (`6434327…`) — the SUMMARY's PYTHONHASHSEED-independence claim is real, achieved by sorting RNG/anchor inputs in `metric_fitness.py` only (rq2 generators reused verbatim; no library edit).
- **Axes are substantive, not stubbed:** `_separation` builds Random + Top-3 from `rq2.baseline_random_same_size` + `baseline_majority_k(k=3)`, collapses via `component_suite._code_inputs(proj)`'s `collapse()`, scores via `component_suite.component_suite()` — the identical path real systems take. `_validity` bounds against `compute_random_f1`/`compute_oracle_f1`. `_stability` = cross-project `pstdev`. `_degeneracy` = cross-system mean spread. All 5 candidate columns (`micro, macro, gap, min_comp, pct_missed`) scored.

### SC3 — Data-derived verdict, hardened by real systems, honesty preserved

**PASS** (with override on the literal "≥1 cleverer baseline" wording — see below).

- **Data-derived, verified by recomputation:** `derive_verdict()` ranks columns headline iff `separation ≥ median AND degeneracy ≥ median` (pooled both levels). Verifier recomputed from the pooled scores in METRIC_FITNESS.md: sep median = 0.4579, deg median = 0.0727 → micro (0.5278/0.0765)✓, macro (0.6200/0.0727)✓, min_comp (0.4579/0.3307)✓ = headline; gap (-0.0621)✗, pct_missed (0.4089<0.4579)✗ = diagnostic. The md verdict ("headline = micro, macro, min_comp; diagnostic = gap, pct_missed") matches the CSV `verdict` column at both levels exactly — NOT a restatement of the milestone's expected answer.
- **Hardened by the 3 real systems vs the rq2 trivial floor:** the separation axis is real-vs-trivial margin using rq2 Random/Top-3 reused as-is. **No new synthetic baseline** exists (`grep "def baseline_"` in metric_fitness.py = none; only a "no new baseline" comment). Legacy s11/s13f/s12c excluded per D-02.
- **Honesty preserved (D-06/D-07):** the script's `micro_macro_close` test evaluates False on the real data (|sep_micro − sep_macro| = 0.092 > 0.05), so it correctly emits the "micro and macro diverge on at least one axis" note rather than overselling. micro ranking headline (contradicting the milestone's expected "micro=diagnostic") is stated honestly. No oversell of macro-as-sole-headline.
- **No new F1 math:** `grep -E 'tp *=|/ *\(tp'` = 0; no local precision/recall/`_f1(` def; the 3 `calc_metrics` mentions are docstring/comments confirming transitive use.
- **Note (SUMMARY-vs-artifact framing):** the 08-03 SUMMARY prose leans on "micro ≈ macro is second-order"; the committed METRIC_FITNESS.md (correctly, per the numbers) says micro/macro DIVERGE on separation (0.092). The artifact is the source of truth and is internally consistent — the SUMMARY's narrative is looser than the committed report but the report itself is honest and data-correct. Carry the artifact's wording (not the SUMMARY's) into Phase 9.

### SC4 — Artemis long-tail abandonment reproduced + quantified

**PASS.**

- METRIC_FITNESS.md states under the gold-only tail definition: sad-code artemis AVG min_comp 0.3455 / pct_missed 0.0533 (min_comp=0 on bigbluebutton, jabref); sad-model AVG min_comp 0.2788 / pct_missed 0.0832 (min_comp=0 on teammates, bigbluebutton, jabref).
- **Cross-checked against the committed CSVs (read directly):** `COMPONENT_SUITE_sad-code.csv` artemis AVG = `0.7995,0.7884,0.0111,0.3455,0.0533` and `COMPONENT_SUITE_sad-model.csv` artemis AVG = `0.8355,0.8132,0.0222,0.2788,0.0832` — the cited min_comp/pct_missed values match exactly, and the per-project min_comp=0 projects match the CSV rows (sad-code bbb/jabref = 0.0000; sad-model teammates/bbb/jabref = 0.0000). Reproduced from the same suite, not re-derived.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `results_artemis_gpt54/` | Canonical ARTEMIS_LOCAL sad-code links, tracked | ✓ VERIFIED | 25 files tracked; 5 sad-code link files; nothing untracked |
| `reports/ARTEMIS_PROVENANCE.md` | Authoritative-source ledger (D-10) | ✓ VERIFIED | 68 lines; paths match component_suite.py constants |
| `reports/COMPONENT_SUITE_sad-code.csv` | 3 systems × 5 proj + AVG, doc-to-code | ✓ VERIFIED | 18 rows; deterministic; clean diff |
| `reports/COMPONENT_SUITE_sad-model.csv` | 3 systems × 5 proj + AVG, doc-to-model | ✓ VERIFIED | 18 rows; deterministic; clean diff |
| `reports/COMPONENT_SUITE.md` | Hardened cross-level narrative + skip-with-notice + D-12 | ✓ VERIFIED | WARNING policy, guarded-roots table, provenance xref, numbers trace to CSV |
| `src/bias/metric_fitness.py` | Standalone 4-axis scorecard + data-derived verdict | ✓ VERIFIED | 509 lines; stdlib-only; real axes; no new F1 math |
| `reports/METRIC_FITNESS.csv` | 10 rows × 4 axis scores + verdict | ✓ VERIFIED | deterministic (incl. cross-process) |
| `reports/METRIC_FITNESS.md` | Per-axis tables + data-derived verdict + SC4 tail | ✓ VERIFIED | verdict matches CSV; SC4 numbers match COMPONENT_SUITE CSVs |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `component_suite._artemis_model` | `results_artemis_gpt54/<proj>/sad-code/sadSamTlr_<proj>.csv` | committed canonical source | ✓ WIRED | line 145; source now tracked |
| `COMPONENT_SUITE.md` | `COMPONENT_SUITE_{level}.csv` | cited numbers trace to CSV cells | ✓ WIRED | swattr/artemis AVG figures match |
| `component_suite._warn_skip` | absent external root | standardized WARNING, present rows still emitted | ✓ WIRED | reproduced by verifier |
| `metric_fitness separation` | rq2 Random/Top-3 floor vs 3 real systems | trivial-vs-real margin, no new baselines | ✓ WIRED | `_floor_suite_rows` reuses rq2 verbatim |
| `metric_fitness validity` | `compute_oracle_f1` / `compute_random_f1` | oracle-band headroom | ✓ WIRED | `_anchors` calls both |
| `metric_fitness verdict + SC4` | gold-only tail (min_comp/pct_missed) | data-derived split + quantified tail | ✓ WIRED | `derive_verdict` + SC4 table |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `COMPONENT_SUITE_{level}.csv` | per-system suite rows | `run_level` → `component_suite()` over committed artemis + external roots | ✓ (re-run deterministic, real per-project values) | ✓ FLOWING |
| `METRIC_FITNESS.csv` | axis scores per column | real `run_level` rows + rq2 floor/anchors via `calc_metrics` | ✓ (varied numeric scores, not constants/empties) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Suite regenerates deterministically | `python3 src/bias/component_suite.py` ×2 | exit 0; byte-identical; clean git diff | ✓ PASS |
| Graceful skip on absent root | `cs.ARTEMIS_LOCAL=/nonexistent; run_level('sad-model',['mediastore'])` | WARNING emitted; 2 present rows; no hard-fail; files unchanged | ✓ PASS |
| Scorecard runs + deterministic | `python3 src/bias/metric_fitness.py` ×2 + 3× PYTHONHASHSEED=random | exit 0; one md5 across all | ✓ PASS |
| Equivalence/determinism oracle (regression) | `python3 src/bias/check_component_suite.py` | exit 0; "PASS: equivalence oracle ... and determinism check ... both hold" | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| Equivalence + determinism oracle | `python3 src/bias/check_component_suite.py` | exit 0; suite-macro == per_component_macro_f1 to 1e-9; CSVs regenerate | PASS |

(No `scripts/*/tests/probe-*.sh` exist in this stdlib-only research repo; `check_component_suite.py` is the project's equivalence/determinism oracle and was run as the probe.)

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CMP-03 | 08-01, 08-02 | Multi-system 2-level comparison; cross-level narrative; swattr≡transarc; graceful skip | ✓ SATISFIED | SC1 |
| CMP-04 | 08-03 | Metric fitness scorecard (4 axes); headline-vs-diagnostic; hardened beyond random/top-3 | ✓ SATISFIED (override on literal "cleverer baseline" — D-01) | SC2, SC3, SC4 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none | — | No TBD/FIXME/XXX or TODO/HACK/PLACEHOLDER in any phase-8 file |

### Project Invariants

| Invariant | Status | Evidence |
|-----------|--------|----------|
| stdlib-only (no third-party imports) | ✓ | metric_fitness.py imports csv/random/statistics/sys/collections/pathlib + project modules |
| No new F1 math (calc_metrics only) | ✓ | no local precision/recall/`_f1(`; `grep -E 'tp *=\|/ *\(tp'` = 0 |
| Non-destructive | ✓ | `paper-result/` + `reports_artemis_gpt54_20260605_030524/` still on disk |
| `component_suite.py` unedited by Phase 8 | ✓ | last commit Phase-7 (e2f93c5); no phase-8 commit touches it; working tree clean |
| `rq2_trivial_baselines.py` unedited by Phase 8 | ✓ | last commit f37ed49; no phase-8 commit touches it; working tree clean |

### Human Verification Required

None. All criteria were verifiable programmatically (scripts re-run, CSV cells read, oracle green). No visual/UX/real-time/external-service dependency.

### Gaps Summary

No blocking gaps. All four success criteria are achieved in the codebase and independently re-verified.

**One documented, user-locked deviation (handled via override, not a gap):** ROADMAP SC3 and REQUIREMENTS CMP-04 literally call for "hardened beyond random/top-3 (≥1 cleverer baseline)". The phase intentionally satisfies this with the REAL multi-system set (3 paper systems above the rq2 trivial floor) instead of a new synthetic baseline, per the user-directed, locked decisions D-01/D-02/D-03 (08-CONTEXT, with verbatim user quotes: *"rq2 is designed for eval baselines ... should be s20union, artemis, transarc"* and *"just systems in the paper"*). The METRIC_FITNESS.md report documents this reinterpretation explicitly. This is recorded as an override above so the literal wording does not register as a FAIL.

**Minor note (non-blocking) for Phase 9:** the 08-03 SUMMARY's narrative ("micro ≈ macro second-order") is looser than the committed METRIC_FITNESS.md, which correctly states micro/macro DIVERGE on separation (0.092). The committed report is the source of truth and is honest/consistent — Phase 9 paper prose should cite the artifact's wording, not the SUMMARY's.

### Follow-ups for Phase 9 (CMP-05 paper integration)

1. **Carry the artifact verdict verbatim:** headline = `micro`, `macro`, `min_comp`; diagnostic = `gap`, `pct_missed`. Do NOT restate the milestone's a-priori "macro-only headline / micro-diagnostic" expectation — the data-derived verdict differs (micro ranks headline; min_comp is the single most discriminating tail column, degeneracy 0.33).
2. **Honesty constraint:** state that the micro-vs-macro contrast carries signal on separation (~0.09) but is not the story; the tail (`min_comp`) is the discriminator. Match every claim to the reconciled numbers (D-07).
3. **Cite only retained artifacts:** `reports/COMPONENT_SUITE.{md,csv}`, `reports/METRIC_FITNESS.{md,csv}`, `reports/ARTEMIS_PROVENANCE.md`. The secondary dirs (`paper-result/`, `reports_artemis_gpt54_*`) are non-authoritative — do not cite.
4. **SWATTR ≡ transarc** remains one column; a distinct external SWATTR doc-to-code result is still an open input (D-12) if ever wanted.

---

_Verified: 2026-06-21T23:05:00Z_
_Verifier: Claude (gsd-verifier)_
