---
quick_id: 20260625-rq12-bigtable-csv
status: complete
---

# Quick Task: RQ1/RQ2 cross-system big-table CSV generator

## Goal
`mini-src/metrics.py` is a per-*system* calculator (output axis = projects); the
paper's RQ1/RQ2 tables are per-*system* (rows = systems), with the approach
averaged over three runs. Add a driver that sweeps the system roster, averages
runs, and emits ONE wide "big table" CSV covering every RQ1 and RQ2 cell.
CSV output is the deliverable — no `.tex` generation.

## Approach
- New `mini-src/rq12.py`, stdlib-only, imports `metrics.py` (sole metric impl;
  no new metric math — `check.py` goldens still pin the arithmetic).
- Roster matches `working/tables/cross_system.tex`: approach (Claude / GPT-5.4,
  each mean of run1/2/3), Artemis (GPT-5.4), TransArC (SWATTR for doc-to-model).
- Inputs = normalized SOTA dump `sota/recovered-links/{model-doc,doc-code}/`
  (`sentence_id,target_id` dialect, auto-detected by `metrics.load_result`);
  approach links from `aalinker/<be>/run*` and `aalinker-composed/<be>/run*`.
- Big-table columns = union of both task panels: doc-to-model `ss_*` and
  doc-to-code `sc_*` (incl. the RQ2 tail `sc_worstC`, `sc_harmC`, `sc_sentCov`).
  Appended `Delta` row = approach(GPT-5.4) − Artemis for the RQ2 Δ column.
- `--lissa` adds the LiSSA row; `$SOTA_LINKS` overrides the input root.

## Verification
- RQ1 must reproduce the paper to 3 dp for all 4 systems × both tasks.
- RQ2 SOTA tail (TransArc, Artemis) must reproduce; the approach tail is the
  reproducible value from surviving data (see Deviation).

## Deviation / known gap
The paper's RQ2 worst/harmonic for the approach (.62/.71) came from a
now-deleted run set (`v2.6.5_s20union_gpt_re_medium`) + a deleted script
(`/tmp/v265.py`). From the surviving `aalinker-composed` dump the file-F1 still
matches (~.875) but the run-sensitive tail gives worst .59 / harmonic .78. The
generator emits these reproducible values and documents the provenance in its
module docstring and stdout footer.

## Output
`reports/RQ12_BIGTABLE.csv` (+ stdout table).
