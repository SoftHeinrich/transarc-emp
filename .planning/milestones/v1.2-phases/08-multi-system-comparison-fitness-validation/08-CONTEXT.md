# Phase 8: Multi-System Comparison & Fitness Validation - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn the foundation's 3-system, 2-level component-suite run into a **defensible,
hardened comparison + a metric fitness scorecard** that establishes — with numbers,
not assertion — which suite columns are **headline** vs **diagnostic**, across the
paper's real systems. (CMP-03, CMP-04)

**In scope:**
- Harden/finalize the multi-system, two-level comparison report over the three
  **paper** systems (swattr/transarc, s20linker/s20union, artemis) at sad-model +
  sad-code, with graceful skip for absent external roots (CMP-03).
- A net-new **fitness scorecard** (`src/bias/metric_fitness.py` → `reports/` artifact)
  scoring candidate suite columns on four axes — **separation** (trivial-vs-real),
  **validity** (oracle ceiling), **stability** (cross-project), **degeneracy** —
  reusing the existing trivial baselines as the floor (CMP-04).
- A **data-derived verdict** on headline vs diagnostic columns, stated with the
  supporting numbers.
- Reproduce + quantify the **artemis long-tail-abandonment** finding under the
  Phase-7 gold-only tail definition (SC4).

**Out of scope (other phases / locked elsewhere):**
- Writing the suite/scorecard/finding into `eval.tex` Ch2 prose + final table
  generation — Phase 9 (CMP-05).
- **New synthetic baselines** beyond the existing Random/Top-3 — explicitly rejected
  by the user (see D-01).
- **Legacy linkers s11/s13f/s12c** as scorecard comparators — explicitly excluded
  ("just systems in the paper", D-02).
- A distinct external SWATTR doc-to-code result — deferred; swattr≡transarc stays one
  column (D-12).
- The `metrics_api` headline reconciliation (done in Phase 7); rewriting the external
  alinker-paper repo prose (Phase 9); sam-code; real pdflatex.
</domain>

<decisions>
## Implementation Decisions

### Comparators & baselines — paper systems only, no new naive baselines (CMP-03/CMP-04, SC3)
- **D-01:** **Do NOT invent new synthetic baselines** (no size-proportional, no
  lexical/name-similarity). `src/bias/rq2_trivial_baselines.py` (Random + Top-3) is
  **purpose-built for the alinker-paper eval-section gameability critique** and stays
  in that role. The scorecard **reuses its Random/Top-3 as the trivial floor as-is** —
  it does not expand rq2 with more baselines.
- **D-02:** The scorecard's **"real" comparison set = the three paper systems only**:
  **swattr/transarc, s20linker (a.k.a. s20union — `s_linker20_union_{project}`),
  artemis.** User directive: *"just systems in the paper."* Legacy real linkers
  **s11 / s13f / s12c are excluded** from the scorecard (they live in the
  `sadsam_comparison`/`sadcode_comparison` quick-task, not the suite/paper). SC3's
  "hardened beyond random/top-3" is satisfied by the **real multi-system set**, not by
  cleverer synthetic baselines.
- **D-03:** The **separation** axis is therefore: does each candidate column rank the
  **real systems** clearly above the **trivial floor (Random/Top-3)**, and by what
  margin. A column that fails to separate trivial from real is a degenerate/headline-
  unfit column.

### Fitness scorecard — numeric, standalone script + report (CMP-04)
- **D-04:** New standalone **`src/bias/metric_fitness.py`** (stdlib-only, reuses
  `calc_metrics` / the suite's primitives only) emits a **numeric score per
  (column × axis)** → **`reports/METRIC_FITNESS.md` + a CSV** (e.g.
  `reports/METRIC_FITNESS.csv`), plus a one-line verdict. Mirrors the suite's
  script+CSV+report pattern and the Phase-7 oracle/determinism precedent. (Not a
  qualitative pass/fail table appended to `COMPONENT_SUITE.md`.)
- **D-05:** The four axes are **separation** (trivial-vs-real margin, D-03),
  **validity** (headroom/behaviour under the oracle ceiling — a valid column should
  sit ≤ oracle and move with real quality), **stability** (cross-project variance of
  the column across the 5 projects), **degeneracy** (does the column saturate / go
  insensitive / collapse, e.g. always ≈1 or always ≈0). Candidate columns scored:
  the suite columns (`micro`, `macro`, `gap`, `min_comp`, `pct_missed`; `gold_gini`
  as a descriptor). Exact per-axis numeric formulas + thresholds left to the planner
  (D-13).

### Verdict stance — data-derived, honesty-first (CMP-04, SC3)
- **D-06:** The verdict is **derived from the computed axis scores**, NOT pre-assumed.
  The milestone's expected verdict (headline = macro + tail; diagnostic = micro/gap)
  is the **hypothesis under test**, not a foregone conclusion. The scorecard reports
  **whatever the numbers rank out** — even if that weakens the macro claim, or shows
  micro ≈ macro (aggregation is second-order, per the Phase-7 reconciled finding).
- **D-07:** Honesty constraint (from milestone Notes/Risks): **do not oversell
  micro-vs-macro.** Keep every stated claim matched to the reconciled numbers. If the
  data contradicts the expected verdict, **say so explicitly** in the report.

### Data & system scope — skip-with-notice, both levels, pinned provenance (CMP-03)
- **D-08:** **Absent-root policy = skip-with-notice** (carry Phase 7's pattern): the
  committed scorecard/comparison does **not hard-fail** when an external root is
  missing; it emits the standardized `WARNING:` notice (system/level/project) and
  scores the present systems. Reproducibility is scoped to **present-system rows**
  (mirrors Phase 7 D-09). All three roots are present in this workspace today.
- **D-09:** Run/score at **both levels** — **sad-code AND sad-model** — to preserve
  the cross-level fitness evidence (the suite generalizes across granularities; the
  point is which column carries the signal at each level).
- **D-12:** **swattr ≡ transarc reported as one column.** Do **not** chase a distinct
  external SWATTR doc-to-code result this phase (its path remains an open input,
  deferred). The live contrast stays heuristic-uniform (SWATTR) vs LLM-peaky-but-leaky
  (artemis).
- **D-10:** **Pin `results_artemis_gpt54` (repo-local `ARTEMIS_LOCAL`) as the
  canonical artemis source** for reproducible provenance. The untracked
  `results_artemis_gpt54/`, `reports_artemis_gpt54_*/`, `paper-result/` dirs must be
  resolved (commit the canonical one and/or document which is authoritative) so a
  re-run is deterministic. Doc-code side stays `ARTEMIS_DOC_CODE`
  (`sota/recovered-links/doc-code`).

### Carried forward from Phase 7 (locked — not re-decided here)
- **D-11:** Universe split stays as set in Phase 7: `micro`/`macro`/`gap` on the
  shared `gold ∪ result` mapped-only universe; `min_comp`/`pct_missed` **gold-only**
  (D-10/D-11 of 07-CONTEXT). The scorecard scores these columns **as defined** — it
  does not re-open the universe question. Framing inherited:
  **macro = headline, gap = skew-regime indicator, min/pct_missed = tail coverage,
  micro = anchor/gap term.** The artemis tail finding (SC4) is reproduced under this
  gold-only definition.

### Claude's Discretion
- **D-13:** Exact per-axis numeric rubric (separation margin metric, validity
  headroom computation, stability variance statistic, degeneracy saturation test),
  CSV column order / precision (suite uses 4-dp), verdict wording, and warn-and-skip
  message reuse are left to the planner/executor. Constraints: **stdlib-only**,
  **reuse `calc_metrics` only** (no metric-math reimplementation), reuse the suite's
  loaders + the rq2 Random/Top-3 generators rather than duplicating them.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope (locked requirements & success criteria)
- `.planning/milestones/v1.2-ROADMAP.md` §"Phase 8" — goal + 4 success criteria
  (SC1 comparison artifact + cross-level narrative; SC2 scorecard 4 axes; SC3
  hardened beyond random/top-3 + verdict with numbers; SC4 artemis tail reproduced).
- `.planning/milestones/v1.2-REQUIREMENTS.md` — CMP-03, CMP-04 (+ Background /
  Out-of-Scope framing). Also milestone **Notes/Risks** (honesty risk; external-root
  guard; swattr≡transarc).
- `.planning/phases/07-suite-universe-reconciliation/07-CONTEXT.md` — locked
  universe split (D-10/D-11), oracle target, the framing carried into D-11.

### The tool + outputs Phase 8 builds on
- `src/bias/component_suite.py` — the suite to drive the comparison. Sites:
  `SYSTEMS` registry (lines ~155-159: swattr_transarc / s20linker / artemis);
  external-root guards `AGENT_LINKER` / `ARTEMIS_DOC_CODE` / `ARTEMIS_LOCAL`
  (lines ~81-94); `_s20_model` reads `s_linker20_{p}_links.csv` (line ~136);
  `_artemis_*` loaders (lines ~144-152); suite math (`component_suite()`).
- `reports/COMPONENT_SUITE.md` — current 3-system, 2-level narrative + the
  universe-split + artemis tail finding (§ around lines 105-129) + Caveats/open items
  (lines 131-143). Phase 8 hardens/extends this, the scorecard is a separate artifact.
- `reports/COMPONENT_SUITE_sad-model.csv`, `reports/COMPONENT_SUITE_sad-code.csv` —
  the committed per-system/per-level outputs the scorecard consumes.

### Baselines + oracle reuse (scorecard inputs)
- `src/bias/rq2_trivial_baselines.py` — **trivial floor**: `baseline_random_same_size`
  + `baseline_majority_k(k=3)` (imported from `stupid_baseline_analysis`); also
  `per_component_macro_f1` (the oracle-equivalence target) and the
  `random_f1`/`oracle_f1` NDG anchors (`compute_random_f1`, `compute_oracle_f1`).
  **Reuse as-is — do NOT expand with new naive baselines (D-01).**
- `src/bias/stupid_baseline_analysis.py` — source of the Random / Top-3 generators.
- `src/bias/check_component_suite.py` — Phase-7 equivalence-oracle + determinism check
  (the "validity"/oracle-ceiling precedent + the skip-when-absent pattern to mirror).
- `src/lib/metrics_api.py` — documents the `s_linker20_union_{project}_links.csv`
  pattern (lines 27, 81, 496) = the "s20union" the user named; reconciled mapped-only
  `component_f1` lives here.

### Result roots (external; guarded — skip-with-notice if absent)
- `/mnt/hostshare/ardoco-home/agent-linker/results/ablation_results/` — s20linker
  (`s_linker20_{project}_links.csv`). Present.
- `/mnt/hostshare/ardoco-home/sota/recovered-links/doc-code/` — artemis doc-code
  (`artemis-{project}-gpt-5.4.csv`). Present.
- `results_artemis_gpt54/` (repo-local `ARTEMIS_LOCAL`) — artemis sad-code source;
  **pin as canonical (D-10)**. Currently untracked.

### Memory (prior findings — verify numbers against code before relying on them)
- memory `component-suite-finding` — the suite + artemis long-tail-abandonment story.
- memory `paper-rq2-primary-panel` — which 4 metrics are kept; micro/macro trap.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `component_suite.py` SYSTEMS registry + loaders — already runs all three paper
  systems at both levels; the scorecard reads its per-component F1s (via the same
  `calc_metrics`) rather than recomputing.
- `rq2_trivial_baselines.py` Random/Top-3 generators + `random_f1`/`oracle_f1`
  anchors — the trivial floor and the oracle ceiling for the separation/validity axes,
  reused verbatim.
- `check_component_suite.py` — copy its standalone-script structure (per-project loop,
  skip/ok/fail lines, exit code, skip-when-absent) for `metric_fitness.py`.
- `transarc_error_analysis.calc_metrics` — the ONLY F1 primitive (locked, CLAUDE.md).

### Established Patterns
- Depth-2 `src/<pillar>/x.py` + `sys.path.insert` to `src/lib` (don't break imports).
- Stdlib-only; generated markdown/CSV reports kept consistent with their script.
- External result roots are guarded constants; absent → standardized `WARNING:` skip.
- Non-destructive: supersede via banner/note, never delete (CLAUDE.md).

### Integration Points
- The scorecard binds `component_suite` column outputs (per system/level/project) to
  the rq2 trivial floor + oracle anchors. Keep both on the same gold∪result (headline
  pair) / gold-only (tail pair) universes as Phase 7 fixed, so numbers stay coherent.
- Pinning `ARTEMIS_LOCAL` provenance (D-10) affects determinism: resolve the untracked
  artemis dirs before the determinism/regen claim can hold.
</code_context>

<specifics>
## Specific Ideas

- User reframed SC3's "cleverer baseline", verbatim: *"rq2 is designed for eval
  baselines under alink-paper / eval section, not naive baselines, should be s20union,
  artemis, transarc, etc."* → Interpreted/locked as D-01..D-03: no new synthetic
  baselines; rq2's Random/Top-3 stay the trivial floor; the real comparators are the
  systems.
- User, on which systems: *"just systems in the paper."* → Locked as D-02: scorecard
  real set = swattr/transarc, s20linker/s20union, artemis only; legacy s11/s13f/s12c
  excluded.
- User chose the most rigorous shaping (numeric scorecard, standalone script+report)
  and the honest stance (data-derived verdict) — consistent with the Phase-7
  reconciled finding that micro-vs-macro is second-order.
</specifics>

<deferred>
## Deferred Ideas

- **Distinct external SWATTR doc-to-code result** (its path is an open input) — keep
  swattr≡transarc as one column for now; revisit only if a genuinely distinct SWATTR
  result is wanted (D-12).
- **New synthetic / cleverer baselines** (size-proportional, lexical) — explicitly
  rejected for this phase (D-01); not deferred-for-later so much as out of the study's
  intent (rq2 owns the trivial-baseline role).
- **Legacy linkers s11/s13f/s12c as scorecard comparators** — excluded by "just
  systems in the paper" (D-02). Their comparison still lives in the
  `sadsam_comparison`/`sadcode_comparison` quick-task if ever needed.
- **Paper integration** (suite + scorecard + tail finding + universe correction into
  `eval.tex` Ch2 with generated tables) — Phase 9 (CMP-05).
- Pre-existing carry-overs (not this phase): NDG non-determinism in
  `compute_random_f1`; rename `transarc_error_analysis.py` → `data_loaders.py`;
  metrics API → sam-code; `.xlsx` output; real pdflatex.

Discussion stayed within Phase 8's compare-and-validate boundary — no scope creep.
</deferred>

---

*Phase: 8-multi-system-comparison-fitness-validation*
*Context gathered: 2026-06-21*
