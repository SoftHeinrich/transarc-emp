# Phase 7: Suite & Universe Reconciliation - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden the already-built `src/bias/component_suite.py` into a finalized, tested,
stdlib-only tool whose `micro` and `macro` share one mapped-only component universe,
**and resolve how its numbers relate to the paper's existing headline
`component_f1`** by making the mapped-only definition the single source of truth.
Adds an equivalence oracle + deterministic-regen check. (CMP-01, CMP-02, CMP-06)

**In scope:** finalizing the suite math/columns; rewriting the per-component
definition in `metrics_api` to the mapped-only universe; regenerating all in-repo
artifacts (CSVs + in-repo LaTeX tables) carrying superseded numbers; the
oracle/determinism check script.

**Out of scope (other phases / locked elsewhere):** the hardened fitness scorecard
+ multi-system comparison narrative (Phase 8); writing the suite/finding into
`eval.tex` prose (Phase 9); rewriting the **external** alinker-paper repo prose
(Phase 9 / different repo); a single composite scalar; sam-code; real pdflatex.
</domain>

<decisions>
## Implementation Decisions

### Headline reconciliation — mapped-only universe is the single source of truth (CMP-02)
- **D-01:** Rewrite `metrics_api._compute_component_f1` (in `src/bias/evaluation_critique.py:631`,
  called from `metrics_api.py:395`) to **drop the `{b}` fallback** — files with no
  SAM-CODE mapping are dropped, matching the suite's mapped-only collapse. The
  headline `component_f1` becomes the mapped-only number (~0.795 swattr avg, vs the
  old 0.714). After this, the suite and `metrics_api` agree on `component_f1` by
  construction.
- **D-02:** The change is a **definition change**, not a result-source change. The
  canonical input is the bundled in-repo `results/` directory (what the suite and
  comparison CSVs already read). The older standalone `reports/metrics_sad-code.csv`
  number (0.732) was the *old definition / old run* — it is simply **overwritten**,
  not separately reconciled. One definition + one input = one set of numbers. No
  source-provenance investigation needed.
- **D-03:** **Regenerate all in-repo artifacts** that carry superseded sad-code (and
  sad-model where applicable) numbers: `reports/*.csv` (incl. `metrics_sad-code.csv`,
  the `SADCODE_*` comparison CSVs) **and** the in-repo `writing/tables/*.tex`
  (regenerated via `src/paper/generate_tables.py`). This intentionally pulls some
  table-generation forward from Phase 9; Phase 9 then validates/extends rather than
  first-produces.
- **D-04:** Any committed artifact still carrying old numbers that is **not**
  regenerated here gets an explicit **"superseded by mapped-only universe (v1.2)"**
  banner/note — non-destructive marking, never silent deletion (per CLAUDE.md
  archival rule). The external alinker-paper repo prose is **flagged for Phase 9**,
  not touched in this phase.

### Equivalence oracle + determinism check (CMP-06)
- **D-05:** One **standalone** `src/bias/check_component_suite.py`, modeled on
  `mini-src/check.py`, that does BOTH guarantees. Single `python3 ... ` invocation →
  pass/fail. (Not a `--check` flag on the suite; not two separate scripts.)
- **D-06:** **Equivalence assertion:** `suite-macro == rq2_trivial_baselines.per_component_macro_f1`
  to 1e-9 tolerance, for **every present system** (swattr/transarc always;
  s20linker/artemis when their external roots exist), at **sad-code**, across all 5
  projects. **Skip-with-notice** when a system's data is absent (exactly like
  `mini-src/check.py`). sad-code only — `per_component_macro_f1` is the only
  *independent* macro reference; a sad-model check would reuse the same suite math
  and be circular.
- **D-07:** **Determinism check:** regenerate the suite CSVs to a temp location and
  diff against the committed ones, covering **both levels** and **all present
  systems**. Guarantee is "deterministic given the same inputs present" (see D-09).

### CSV scope & determinism boundary (Phase 7 vs Phase 8)
- **D-08:** Committed Phase-7 CSVs keep **all 3 systems** (as the foundation already
  committed) — do not strip down to core-only.
- **D-09:** The determinism guarantee is **scoped to present-system rows**: the check
  diffs only rows for systems whose roots are present and skips absent ones with a
  notice. swattr/transarc (in-repo, deterministic) always re-checks. Phase 8 then
  *hardens the fitness scorecard / comparison*, not first-produces the run.

### Suite finalization — split universe across columns (CMP-01)
- **D-10:** `micro` and `macro` stay on the **shared gold∪result mapped-only
  universe**. This preserves the core properties: `micro` = link F1 at sad-sam,
  `gap` = aggregation effect alone (CMP-02), and the equivalence oracle passes
  against the (unchanged) `per_component_macro_f1` which also iterates gold∪result.
- **D-11:** `min_comp` and `pct_missed` (the **tail/coverage** metrics) become
  **gold-only** — restricted to components present in gold. Rationale: these measure
  *coverage of real components*; an invented result-only (FP) component scoring 0 is
  not a "missed" component and was polluting the tail signal. This does **not** touch
  the oracle (which only checks `macro`).
- **D-12:** Documentation framing to carry into reports/paper: **headline pair
  (`micro`/`macro`) = shared universe; tail (`min_comp`/`pct_missed`) = gold
  coverage.** Changing the tail to gold-only shifts committed `min_comp`/`pct_missed`
  numbers, so the artemis long-tail-abandonment finding must be **re-confirmed under
  the new definition** during execution (expected to strengthen: `pct_missed` becomes
  "fraction of *real* components abandoned").

### Claude's Discretion
- Remaining purely-mechanical hardening left to the planner/executor: warn-and-skip
  message wording for absent external roots, CSV column ordering/precision (current
  4-dp), `min_comp` tie handling, argparse/CLI polish. Keep stdlib-only and reuse
  `calc_metrics` only (locked, CLAUDE.md + CMP-01).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope (locked requirements & success criteria)
- `.planning/milestones/v1.2-ROADMAP.md` §"Phase 7" — goal + 4 success criteria.
- `.planning/milestones/v1.2-REQUIREMENTS.md` — CMP-01, CMP-02, CMP-06 (and the
  Background/Out-of-Scope framing).

### The tool being hardened + its output docs
- `src/bias/component_suite.py` — the foundation suite. Key sites: `_code_inputs`
  (lines ~208-232, the mapped-only collapse that drops unmapped files);
  `component_suite()` (lines ~165-192, micro/macro/min_comp/pct_missed/gold_gini);
  `SYSTEMS` registry + external-root guards (lines ~72-151).
- `reports/COMPONENT_SUITE.md` — narrative + the universe-reconciliation table;
  §"Caveats / open items" names the metrics_api reconciliation as CMP-02 work.
- `reports/COMPONENT_SUITE_sad-model.csv`, `reports/COMPONENT_SUITE_sad-code.csv` —
  committed outputs the determinism check pins.

### The reconciliation surface (the two legacy per-component-F1 defs)
- `src/bias/evaluation_critique.py:631` — `_compute_component_f1` (MICRO, the `{b}`
  fallback to rewrite). Called from `src/lib/metrics_api.py:395`.
- `src/bias/rq2_trivial_baselines.py:57` — `per_component_macro_f1` (MACRO, the
  equivalence-oracle target; iterates gold∪result, drops unmapped files).
- `src/lib/metrics_api.py` — `compute_sad_code_metrics` (line ~384+, headline row),
  panel constants `PAPER_MAIN_PANEL_SADCODE/SADSAM`.

### Oracle precedent + downstream regeneration
- `mini-src/check.py` + `mini-src/README.md` — the standalone equivalence-check
  style CMP-06 asks for (per-project, both tasks, 1e-9 tol, skip-when-absent).
- `src/paper/generate_tables.py` → `writing/tables/*.tex` — the in-repo table
  generator to re-run after the definition change (D-03).
- Regeneration targets carrying superseded numbers: `reports/metrics_sad-code.csv`,
  `reports/SADCODE_COMPARISON.md` + `reports/SADCODE_S11_S13F_VS_TRANSARC.csv`,
  `reports/lissa_metrics_sad-code.csv`, `writing/tables/metrics_sad-code.tex`.

### Memory (prior findings — verify against code before relying on specific numbers)
- memory `component-suite-finding` — the suite + artemis long-tail finding.
- memory `paper-rq2-primary-panel` — the micro-vs-macro definition trap + which
  artifacts carry the headline `component_f1`.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `transarc_error_analysis.calc_metrics` — the ONLY F1 primitive the suite may call
  (locked). All suite columns are aggregations over per-component `calc_metrics` F1s.
- `component_suite._code_inputs` already implements the mapped-only collapse — its
  rule (drop files with no SAM-CODE component) is the definition to port into
  `metrics_api._compute_component_f1`.
- `mini-src/check.py` — copy its structure for `check_component_suite.py`
  (PANEL/COMPUTE dicts, per-project loop, 1e-9 tol, SKIP/OK/FAIL lines, exit code).
- `src/paper/generate_tables.py` — stdlib table generator; re-run for D-03.

### Established Patterns
- Depth-2 `src/<pillar>/x.py` with `sys.path.insert` to `src/lib` (don't break it).
- Stdlib-only; reports are generated markdown/CSV kept consistent with their script.
- Non-destructive: supersede via banner/note + `git mv`, never delete (CLAUDE.md).
- External result roots are guarded constants (`AGENT_LINKER`, `ARTEMIS_DOC_CODE`,
  `ARTEMIS_LOCAL`); absent → warn + skip. Keep this for present-system determinism.

### Integration Points
- `metrics_api._compute_component_f1` ← change ripples to every caller that reports
  `component_f1` (comparison scripts, table generator). Regenerate, then re-banner
  anything not regenerated.
- The equivalence oracle binds `component_suite.component_suite()` (macro) to
  `rq2_trivial_baselines.per_component_macro_f1` — both must stay on gold∪result for
  sad-code so they remain equal (D-10).
</code_context>

<specifics>
## Specific Ideas

- User directive, verbatim intent: "overwrite anything with our new findings —
  `metrics_api` and all the past doc will be marked as outdated." Interpreted and
  locked as D-01..D-04: mapped-only is canonical; regenerate in-repo; banner-mark
  superseded; defer external-repo prose to Phase 9.
- User reframed the result-source question as "we changed definition of
  per-component" — i.e. treat the 0.732/0.714/0.795 spread as a definition change,
  not source archaeology (D-02).
- User's tail-metric instinct (gold-only) was correct and adopted for
  `min_comp`/`pct_missed` while protecting micro=link-F1 and the oracle for
  `micro`/`macro` (D-10/D-11) — the "split universe" resolution.
</specifics>

<deferred>
## Deferred Ideas

- **Rewrite external alinker-paper repo prose** to the mapped-only headline — Phase 9
  (different repo; Phase 7 only flags it).
- **Hardened fitness scorecard + cleverer baselines + multi-system comparison
  narrative** — Phase 8 (CMP-03, CMP-04).
- **Write suite + tail-coverage finding + universe correction into `eval.tex` Ch2** —
  Phase 9 (CMP-05).
- Pre-existing carry-overs (not this phase): NDG non-determinism in
  `compute_random_f1`; rename `transarc_error_analysis.py` → `data_loaders.py`;
  metrics API → sam-code; `.xlsx` output; real pdflatex.

None of the above arose as scope creep — discussion stayed within Phase 7's
finalize-and-reconcile boundary.
</deferred>

---

*Phase: 7-suite-universe-reconciliation*
*Context gathered: 2026-06-21*
