---
quick_id: 20260625-rq12-bigtable-csv
status: complete
---

# Summary: RQ1/RQ2 cross-system big-table CSV generator

## Delivered
- `mini-src/rq12.py` (stdlib, imports `metrics.py`) — sweeps the 4-system roster,
  macro-averages over the 5 projects, averages the approach over its 3 runs, and
  writes one wide CSV: `reports/RQ12_BIGTABLE.csv`. `--lissa` / `$SOTA_LINKS` knobs.
- `reports/RQ12_BIGTABLE.csv` — the big table (rows = systems + a Δ row;
  columns = both tasks' panels, a superset of every RQ1/RQ2 cell).

## How the big table maps to the paper tables
- RQ1 doc-to-model (`tab:rq1-sadsam`) = `ss_P, ss_R, ss_linkF1`.
- RQ1 doc-to-code (`tab:rq1-sadcode`) = `sc_P, sc_R, sc_fileF1`.
- RQ2 panel (`tab:rq2-summary`) = GPT-5.4 rows' `sc_fileF1, sc_sentCov, sc_worstC, sc_harmC` + Δ row.

## Verification
- `mini-src/check.py` → PASS (metrics impl unchanged).
- RQ1 reproduces the paper exactly (3 dp), all 4 systems × both tasks:
  approach Claude .949/.915/.928 (ss) · .957/.866/.906 (sc);
  approach GPT-5.4 .940/.858/.894 · .913/.842/.875;
  Artemis .930/.763/.835 · .941/.778/.849; TransArC .869/.772/.799 · .886/.775/.803.
- RQ2 SOTA tail reproduces (TransArc worst .54 / harm .67 / cov .75;
  Artemis .35 / .47 / .71).

## Known gap (carried, not fixed here)
RQ2 approach **tail** does not reconcile with the paper (.62/.71): the source
run set (`v2.6.5_s20union_gpt_re_medium`) and script (`/tmp/v265.py`) are deleted.
From surviving data the generator emits the reproducible worst .59 / harmonic .78
(file-F1 still matches .875). Resolving this means either re-deriving from
`v2.6.5_s20union/gpt` or correcting `working/table/rq2-summary.tex` to .59/.78 —
left for a follow-up since the user scoped this task to the CSV.
