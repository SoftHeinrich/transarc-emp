---
phase: 05-consequences-study-converged-metrics
verified: 2026-05-30T00:00:00Z
status: passed
score: 11/11 must-haves verified
overrides_applied: 0
re_verification: # none — initial verification
gaps: []
---

# Phase 5: Consequences Study & Converged Metrics Verification Report

**Phase Goal:** A motivation analysis shows, with numbers, how misleading F1 distorts BOTH SAD-SAM (pure F1) and SAD-CODE (file-level enrollment F1), and proposes a converged metric framework giving the two tasks one coherent evaluation story — written up as a Pillar 2 paper section.
**Verified:** 2026-05-30
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
| -- | ----- | ------ | -------- |
| 1  | `python3 src/bias/consequences_study.py` exits 0 and (re)writes reports/CONSEQUENCES_STUDY.md | ✓ VERIFIED | Ran it: EXIT=0, no stderr; report mtime updated (5398 bytes); deterministic on re-run (md5 unchanged) |
| 2  | Report quantifies SAD-SAM pure-F1 disagreement: link vs sentence/component + MCC/MAP/HUS with per-project deltas (STUDY-01) | ✓ VERIFIED | `## SAD-SAM ... (STUDY-01)` section has a per-project pipe table Link/Sentence/Component/MCC/MAP/HUS + computed Link−Sentence Δ; teammates sentence 0.916 vs link 0.710 (Δ −0.206) flagged in prose |
| 3  | Report consolidates SAD-CODE file-level consequences with validated anchors (JabRef File 0.943 → Decision 0.394; avg File 0.803/Decision 0.596/Component 0.714), no recomputation (STUDY-02) | ✓ VERIFIED | `## SAD-CODE ... (STUDY-02)` table + prose: JabRef rank #1 file / #5 decision flip; avg row 0.803/0.596/0.714 read from CSV; cites EVALUATION_CRITIQUE.md + BENCHMARK_BIAS_STUDY.md; "No metric is recomputed here" |
| 4  | Report proposes converged Decision+Component framework across both tasks (STUDY-03) | ✓ VERIFIED | `## A Converged Decision+Component Framework (STUDY-03)` maps both tasks to decision/component axis; 2-row table SAD-SAM Δ 0.000 / SAD-CODE Δ 0.207; "extends (does not replace)" recommendation |
| 5  | No benchmark-derived word lists in the script (stopwords only; project names opaque) | ✓ VERIFIED | Only imports csv + pathlib; PROJECT_ORDER is opaque ordering data; all "component"/"interface" matches are metric-granularity terms or N/A handling, not benchmark vocab |
| 6  | `python3 src/paper/generate_tables.py` exits 0 and writes consequences.tex + converged_framework.tex | ✓ VERIFIED | Ran it: EXIT=0, prints `TOTAL 12`, both `WROTE writing/tables/...` lines present; deterministic on re-run |
| 7  | Both new tables are booktabs floats with \fone-bearing headers via header_override | ✓ VERIFIED | Both have `\begin{table}`/`\begin{tabular}`/`\toprule`/`\midrule`/`\bottomrule`; headers carry `\fone`; macros `\sadsam`/`\sadcode` emitted verbatim (0 `\textbackslash`); decimals not percentages; em-dash → `--` |
| 8  | eval.tex gains new Ch2 \section with \label + \input{tables/consequences}, after sec:comprehensive-metrics, covering BOTH tasks (STUDY-04) | ✓ VERIFIED | `\section{Misleading \fone Across Both Tasks}` + `\label{sec:eval:misleading-both}` at L405-406 (after sec:comprehensive-metrics intro, before \fone Variants); `\input{tables/consequences}` L424; prose covers both \sadsam and \sadcode |
| 9  | sec:eval:protocol extended with converged Decision+Component recommendation + \input{tables/converged_framework}; existing enumerate preserved | ✓ VERIFIED | `\paragraph{A converged axis for both tasks.}` L1029 after the (unmodified) `\end{enumerate}` L1027; `\input{tables/converged_framework}` L1043 |
| 10 | Every new \Cref/\ref target defined by a \label; single document envelope; existing sections preserved | ✓ VERIFIED | All 28 Cref/ref targets resolve to defined labels; 1 `\begin{document}`/1 `\end{document}` (last non-empty line L1046); sec:comprehensive-metrics, sec:eval:f1, sec:eval:protocol all preserved |
| 11 | Constraints: stdlib-only; no benchmark word lists; no /100 or recompute; citations reference only retained reports | ✓ VERIFIED | consequences_study.py: no `/100`, no `transarc_error_analysis` import, no archive citations; new builders use `_fmt_dec` (not `_fmt_f1`/`/100`); cited reports (EVALUATION_CRITIQUE, BENCHMARK_BIAS_STUDY, NEW_METRICS_REPORT) all exist in reports/, none under archive/ |

**Score:** 11/11 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `src/bias/consequences_study.py` | stdlib analysis script (≥120 lines) | ✓ VERIFIED | 12270 bytes; stdlib only (csv, pathlib); loads both CSVs via load_metrics_csv; 3 section fns + out() accumulator |
| `reports/CONSEQUENCES_STUDY.md` | motivation report (STUDY-01/02/03), contains 0.394 | ✓ VERIFIED | 3 `##` sections; anchors 0.394, 0.943, 0.916, 0.803, 0.596, 0.714, 0.207, 0.710 all present |
| `src/paper/generate_tables.py` | 2 new builders registered (t_consequences) | ✓ VERIFIED | t_consequences (L378) + t_converged_framework (L435) defined and registered in builders list (L603-604); raw_cols added to render_table |
| `writing/tables/consequences.tex` | headline-vs-honest table, contains tabular | ✓ VERIFIED | Valid booktabs, both task blocks, 0.394/0.916/0.943 present |
| `writing/tables/converged_framework.tex` | converged table, contains tabular | ✓ VERIFIED | Valid booktabs, 2 rows, $\Delta$ 0.000/0.207 |
| `writing/eval.tex` | new Ch2 section + extended protocol, contains input{tables/consequences} | ✓ VERIFIED | Both inputs present, section + paragraph inserted, envelope intact |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| consequences_study.py | metrics_sad-sam.csv | csv.DictReader load_metrics_csv('sad-sam') | ✓ WIRED | load_metrics_csv reads both CSVs; report numbers match CSV cells exactly |
| consequences_study.py | metrics_sad-code.csv | csv.DictReader load_metrics_csv('sad-code') | ✓ WIRED | SAD-CODE table values (0.803/0.596/0.714) match CSV Average row |
| consequences_study.py | CONSEQUENCES_STUDY.md | out() single write | ✓ WIRED | File regenerated on run, deterministic |
| generate_tables.py | metrics_sad-{sam,code}.csv | _load_metrics(task) | ✓ WIRED | Both tables single-sourced; values match CSVs |
| eval.tex | tables/consequences.tex | \input{tables/consequences} | ✓ WIRED | L424; preceded by \Cref{tab:consequences} L412; label defined |
| eval.tex | tables/converged_framework.tex | \input{tables/converged_framework} | ✓ WIRED | L1043; preceded by \Cref{tab:converged-framework} L1038; label defined |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| CONSEQUENCES_STUDY.md | per-project rows/avg_row | metrics_sad-sam.csv + metrics_sad-code.csv | Yes — values match CSVs verbatim (only Δ computed) | ✓ FLOWING |
| consequences.tex / converged_framework.tex | _load_metrics rows | same Phase-4 CSVs | Yes — 0.394/0.916/0.803/0.596/0.714/0.207 match CSV cells | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Consequences script runs | `python3 src/bias/consequences_study.py` | EXIT=0, report rewritten, deterministic | ✓ PASS |
| Table generator runs | `python3 src/paper/generate_tables.py` | EXIT=0, TOTAL 12, both .tex written | ✓ PASS |
| No macro mangling | `grep -c textbackslash` on both tables | 0 / 0 | ✓ PASS |
| Cref targets resolve | label/ref cross-check (eval.tex + tables) | 28 refs, 0 unresolved | ✓ PASS |
| Idempotent regeneration | md5 before/after second run | unchanged | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| STUDY-01 | 05-01 | SAD-SAM pure-F1 consequences | ✓ SATISFIED | CONSEQUENCES_STUDY.md SAD-SAM section: link vs sentence/component/MCC/MAP/HUS deltas |
| STUDY-02 | 05-01 | SAD-CODE file-level consequences (consolidated) | ✓ SATISFIED | SAD-CODE section: JabRef 0.943→0.394 flip, avg 0.803/0.596/0.714, no recompute |
| STUDY-03 | 05-01 | Converged metric framework | ✓ SATISFIED | Converged section + tab:converged-framework: decision+component axis, both tasks, Δ 0.207 |
| STUDY-04 | 05-02 | Written into paper, structurally valid, tables regenerate | ✓ SATISFIED | eval.tex new section + extended protocol; 2 tables regenerate; envelope intact; cites only retained material |

No orphaned requirements: REQUIREMENTS.md maps STUDY-01..04 to Phase 5, all claimed by plans 01/02.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | None | — | No TODO/FIXME/placeholder/stub patterns; no empty returns; all outputs wired to live CSV data |

Note: code review (05-REVIEW.md) flagged two Info-level latent-robustness items (IN-01 sort-key None guard, IN-02 redundant em-dash literal). Neither affects current behavior under the committed CSVs; not goal-blocking.

### Human Verification Required

None. The phase produces stdlib scripts and structurally-validated LaTeX (no pdflatex toolchain by design — CONTEXT explicitly defers the PDF build). All checks are programmatic: scripts run to completion, anchors match the source CSVs, tables are valid booktabs, and Cref/label cross-references resolve. The NDG column jitter noted in the brief is a known-deferred item and does not appear in this phase's tables.

### Gaps Summary

No gaps. All 11 must-haves verified by running the scripts and inspecting the actual generated artifacts (not trusting SUMMARY claims). Both scripts exit 0 and regenerate deterministically; the report and both LaTeX tables carry every validated anchor read verbatim from the Phase-4 CSVs (0.394, 0.943, 0.916, 0.803, 0.596, 0.714, 0.207, 0.710); eval.tex integrates a new Ch2 motivation section covering BOTH tasks plus a converged-axis protocol extension with all cross-references resolving and the document envelope and prior sections intact. All locked CONTEXT constraints honored: stdlib-only, no benchmark word lists, no /100 or average recomputation, citations limited to retained reports/scripts (none under archive/).

---

_Verified: 2026-05-30_
_Verifier: Claude (gsd-verifier)_
