---
quick_id: 20260625-rq12-bigtable-csv
status: complete
---

# Summary: RQ1/RQ2 cross-system big-table CSV generator

## Delivered
- `mini-src/rq12.py` (stdlib, imports `metrics.py`) — sweeps the 4-system roster,
  macro-averages over the 5 projects, averages the approach over its 3 runs, and
  writes two CSVs. `--lissa` / `$SOTA_LINKS` knobs.
- `reports/RQ12_BIGTABLE.csv` — the big table (rows = systems + a Δ row;
  columns = both tasks' panels, a superset of every RQ1/RQ2 cell).
- `reports/RQ2_PANEL.csv` — focused RQ2 size-aware panel
  (`sc_fileF1/sc_sentCov/sc_worstC/sc_harmC`) for **both** approach backends —
  GPT-5.4 **and Claude/sonnet** (the latter is not in the current paper table) —
  the deltas vs Artemis, and a row flagged **OUTDATED** carrying the paper's
  archived approach numbers (.62/.71) so the stale values are visibly marked.

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

## Input provenance verified (GPT = newest, no-reasoning)
Confirmed the GPT input is the correct run, not the paper's reasoning run:
- `aalinker[-composed]/gpt-5.4_full` is extracted from
  `agent-linker/results/v2.6.6_extracts/gpt` (per the dump's `_manifest` `src`).
- `v2.6.6_extracts` = newest extracts; the plain `gpt` N=3 runner is **no
  reasoning** (`OPENAI_REASONING_EFFORT` unset → temperature kept; `llm_client.py`),
  i.e. NOT `run_s20union_gpt_re_medium_n3.sh` (reasoning=medium). Model gpt-5.4
  (→ gpt-5.4-2026-03-05; `llm_logs` dominant snapshot).
- The paper's RQ2 used the deleted `v2.6.5_s20union_gpt_re_medium` (reasoning=medium).
- Re-running after the provenance fixes left every number unchanged — the input
  was already correct; only docs/labels changed.

## RQ2 paper numbers marked OUTDATED (resolution)
The paper's RQ2 approach tail (.62/.71) was produced from the now-deleted run set
`v2.6.5_s20union_gpt_re_medium` via the deleted `/tmp/v265.py`; it no longer
reproduces. Per user decision we do **not** chase it: the live panel emits the
reproducible values from surviving data (GPT-5.4 worst .59 / harmonic .78;
Claude/sonnet worst .69 / harmonic .82) and carries the paper's stale numbers as
an explicit `OUTDATED` row (`PAPER_RQ2_OUTDATED` in `rq12.py`). Follow-up if
desired: update `working/table/rq2-summary.tex` to the live numbers (and consider
adding the Claude/sonnet column).
