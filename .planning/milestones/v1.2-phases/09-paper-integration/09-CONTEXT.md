# Phase 9: Paper Integration (CMP-05) - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning
**Mode:** Smart-discuss (autonomous) — grey areas proposed below, all determined by the
CMP-05 success criteria + locked v1.2 decisions (D-01…D-12). One pre-phase blocker
(STATE open-item #1, SAD-SAM Sentence F1) was investigated and resolved before discuss.

<domain>
## Phase Boundary

Write the **level-agnostic component suite**, the **tail-coverage discriminator**
(artemis abandons the long tail), and the **universe-reconciliation correction** into
`writing/eval.tex` Chapter 2, with generated tables and a structural validation. This
is the publication step that closes milestone v1.2. (CMP-05)

**In scope:**
- A new/extended Ch2 section presenting (a) the suite as one object over
  `(sentence, component)` pairs at *both* granularities, (b) the universe-reconciliation
  correction, (c) the cross-system comparison + the artemis long-tail finding, (d) which
  columns are headline vs diagnostic per the fitness scorecard.
- Tables generated via `src/paper/generate_tables.py` into `writing/tables/` (the only
  sanctioned table path), reading **only** retained `reports/` artifacts.
- Structural validation: tables regenerate deterministically and every `\label`/`\ref`/
  `\Cref` and `\input` resolves.
- Fix the one stale-prose consequence of the resolved Sentence-F1 bug (eval.tex L416–418).

**Out of scope (locked elsewhere / other work):**
- The external `alinker-paper` repo prose (mirror) — deferred (D-17); CMP-05 = local
  `writing/eval.tex` only.
- A real `pdflatex` PDF build — deferred since v1.1 (no local LaTeX toolchain).
- New baselines / new systems / sam-code / re-deriving any metric (all upstream-locked).
- Re-opening micro-vs-macro as the headline story — the reconciled finding is that
  aggregation is **second-order**; tail coverage is the story (honesty risk, roadmap Notes).
</domain>

<pre_phase_resolution>
## Pre-Phase Blocker — STATE open-item #1 (RESOLVED before discuss)

The user directed (autonomous upfront decision) to **investigate the `sentence_f1` bug
before paper integration**. Findings:

- The `sentence_f1` gold-negative-FP bug was **real but already fixed** on 2026-06-03
  (commit `b9a18f4`), *before* Phase 7. Current `metrics_api.py:311–313` is the fixed
  (standard-IR) version: `res_S = {(s,"*") for s in res_by_s}` (all predicted sentences).
- **Empirically reproduced:** teammates corrected Sentence F1 = **0.703** (buggy = 0.916);
  27/66 = **40.9 %** of teammates result sentences are pure-FP (no gold entry). AVG = 0.825
  (buggy 0.875). The canonical `compute_sad_sam_metrics` API returns the fixed values
  exactly; committed `reports/metrics_sad-sam.csv` and `writing/tables/metrics_sad-sam.tex`
  are mutually consistent at 0.703 / 0.825. **→ 0.703 / 0.825 is trustworthy & paper-ready.**
- **One stale consequence:** `writing/eval.tex:416–418` still narrates the *buggy* 0.916
  with a now-false "0.206 gap" using Teammates. With corrected data Teammates is ~parity
  (0.703 vs link 0.710). The "link F1 understates per-sentence retrieval" point survives in
  aggregate (AVG sentence 0.825 > link 0.799) and most strongly at **BigBlueButton**
  (sentence 0.876 vs link 0.793, +0.083). → re-anchor in this phase (D-16).
</pre_phase_resolution>

<decisions>
## Implementation Decisions (grey areas — proposed & accepted in autonomous mode)

### D-13 [Placement] New Ch2 section as the cross-system culmination
Append a new section to Ch2 **after** "Recommended Evaluation Protocol" + the
`tab:converged-framework` table (current end of chapter, before `\end{document}`).
The converged-axis paragraph already introduces decision/component F1 for both tasks;
the suite extends it to **cross-system + tail coverage**. Do not duplicate the v1.1
single-system component material (Component Coverage §, Component-Level F1 §).
Working title: *"A Level-Agnostic Component Suite and the Long-Tail Discriminator."*

### D-14 [Message] Three claims, matched to the reconciled numbers
1. One suite, five columns (`micro`, `macro`, `gap`, `min_comp`, `pct_missed`; `gold_gini`
   a descriptor), same object at sad-model and sad-code.
2. **Universe-reconciliation correction:** a large part of the apparent
   enrollment-inflation *component* gap was a universe-mismatch artifact
   (swattr/transarc avg micro/macro gap −0.099 → −0.019); once reconciled, micro/macro
   aggregation is **second-order** (gap sign still fingerprints the skew regime, magnitude
   small). Cite `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`.
3. **Tail coverage (gold-only) is the level-stable, first-order discriminator** and it
   indicts the LLM SOTA: artemis is competitive on `micro`/link F1 (2nd) but **last** on
   worst real-component coverage (`min_comp` 0.345 sad-code / 0.279 sad-model) and abandons
   real gold components (`min_comp = 0` on bbb + jabref both levels; +teammates sad-model).
   SWATTR is more uniform despite a lower headline. Cite `reports/COMPONENT_SUITE.md`.
**Honesty guard:** do NOT oversell micro-vs-macro; keep every claim matched to the CSVs.

### D-15 [Tables] Two new generated tables, same generator idiom
- `tab:component-suite` — 3 systems × 2 levels (AVG rows): micro / macro / gap / min_comp /
  pct_missed, from `reports/COMPONENT_SUITE_{sad-code,sad-model}.csv`.
- `tab:metric-fitness` — fitness scorecard verdict (column × separation / validity /
  stability / degeneracy / verdict), from `reports/METRIC_FITNESS.csv`.
Both via new `t_*` functions in `src/paper/generate_tables.py`, registered in `main()`
under the Ch2 group, reusing `render_table`/`write_table`. Stdlib-only, data read from
`reports/` (no hardcoded numbers).

### D-16 [Stale-prose fix] Re-anchor the Sentence-F1 example to corrected data
Rewrite `eval.tex:416–418`: replace the buggy Teammates 0.916 / "0.206 gap" with the
corrected BigBlueButton example (sentence 0.876 vs link 0.793, +0.083), or the aggregate
(AVG sentence 0.825 > link 0.799). Keeps the rhetorical point true to
`writing/tables/metrics_sad-sam.tex` (= `reports/metrics_sad-sam.csv`).

### D-17 [alinker-paper] Local-only
CMP-05 writes `writing/eval.tex`. The external `alinker-paper` mirror is deferred.

### D-18 [Validation] Table-regen + structural checker (no pdflatex)
SC3 satisfied by: (a) `python3 src/paper/generate_tables.py` runs clean and the two new
tables are byte-identical on a 2nd run; (b) a new stdlib `src/paper/check_eval_structure.py`
asserts every `\label` is referenced-resolvable (no dangling `\ref`/`\Cref`/`\cref`) and
every `\input{tables/X}` file exists. No `pdflatex` (deferred since v1.1).
</decisions>

<code_context>
## Existing Code Insights

- `writing/eval.tex` (1046 lines): Ch1 via `\input{ch1_transarc}`; Ch2 =
  "Benchmark Bias and Evaluation Metrics" (L32→end). Chapter currently ends at
  "Recommended Evaluation Protocol" + `\input{tables/converged_framework}` (L1009–1043).
- `src/paper/generate_tables.py`: `render_table(rows, caption, label, note, header_override,
  raw_cols)` + `write_table(name, content)` → `writing/tables/<name>.tex`. CSV readers use
  `csv.DictReader`. `main()` lists builders in two groups (Ch1, Ch2). Pattern to copy:
  `t_consequences` / `t_converged_framework` (read `reports/*.csv`, emit booktabs + source note).
- Suite CSVs: `reports/COMPONENT_SUITE_{sad-code,sad-model}.csv` (cols:
  project,system,micro,macro,gap,min_comp,pct_missed,gold_gini; AVG rows present, 4-dp).
- Scorecard CSV: `reports/METRIC_FITNESS.csv` (level,column,separation,validity,stability,
  degeneracy,verdict).
- Narrative sources (cite, don't re-derive): `reports/COMPONENT_SUITE.md`,
  `reports/METRIC_FITNESS.md`, `reports/COMPONENT_UNIVERSE_RECONCILIATION.md`,
  `reports/ARTEMIS_PROVENANCE.md`.
- No leakage / stdlib-only invariants carry over; tables must trace to retained `reports/`.
</code_context>

<specifics>
## Specific Ideas
- Tie the new section back to the converged-axis paragraph so the chapter reads as one arc:
  v1.1 converged decision/component axis → v1.2 cross-system suite + tail discriminator.
- Use AVG rows in the headline tables; point to the CSVs for per-project 4-dp.
- State the artemis verdict crisply: "competitive by link F1, last by worst real-component
  coverage — the LLM nails popular components and abandons the long tail."
</specifics>

<deferred>
## Deferred Ideas
- alinker-paper mirror of the suite section (D-17).
- pdflatex PDF build (since v1.1).
- A distinct external SWATTR doc-to-code column (D-12; swattr ≡ transarc stays one column).
</deferred>
