# Phase 7: Suite & Universe Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 7-suite-universe-reconciliation
**Areas discussed:** Headline reconcile vs document, Oracle + determinism check, Committed-CSV / determinism scope, Suite finalization details

---

## Headline reconcile vs document

| Option | Description | Selected |
|--------|-------------|----------|
| Document the delta | Keep `{b}`-fallback headline; record both defs + delta in a report | |
| Reconcile in metrics_api | Change to mapped-only universe; headline becomes ~0.795 | |
| Document + expose both | Document + add a secondary mapped-only column/flag | |
| **Other (free-text)** | "overwrite anything with our new findings, metrics_api and all the past doc will be marked as outdated" | ✓ |

**User's choice:** Free-text — go beyond "reconcile": the mapped-only universe becomes the **single source of truth**; rewrite `metrics_api`; mark all past docs carrying old numbers as outdated/superseded.
**Notes:** Two boundary clarifications captured in plain text:
- **(a) → "regen":** Regenerate the in-repo `writing/tables/*.tex` now; defer only the external alinker-paper repo prose to Phase 9.
- **(b) → "all":** Treat all past sad-code AND sad-model artifacts (incl. the older standalone `metrics_sad-code.csv`) as in scope for overwrite/superseding, not just the sad-code `component_f1` artifacts.

---

## Committed-CSV / determinism scope (incl. canonical result source)

| Option | Description | Selected |
|--------|-------------|----------|
| All present, determinism = present-rows | Keep all 3 systems; determinism scoped to present-system rows | ✓ |
| Core-only in Phase 7 | Commit only swattr/transarc; full 3-system run → Phase 8 | |

**Canonical result source follow-up:**

| Option | Description | Selected |
|--------|-------------|----------|
| Bundled `results/` | Pin in-repo `results/`; regenerate `metrics_sad-code.csv` from it | |
| Keep both, label sources | Annotate each artifact with its result source | |
| Investigate first | Diff the two result sources before picking | |
| **Other (free-text)** | "we changed definition of per-component" | ✓ |

**User's choice:** All-present CSVs with present-row determinism. On the result source: reframed as a **definition change** (mapped-only per-component), not source archaeology — old standalone numbers simply overwritten; canonical input = bundled `results/`.
**Notes:** User asked me to verify against the suite docs how the new component suite defines per-component; confirmed from `component_suite.py:208-232` (mapped-only collapse, drops unmapped files) and `reports/COMPONENT_SUITE.md` before locking.

---

## Oracle + determinism check

| Option | Description | Selected |
|--------|-------------|----------|
| One standalone check script | Single `check_component_suite.py` (mini-src/check.py style); macro-equivalence + determinism diff | ✓ |
| --check flag on the suite | Bake both checks into `component_suite.py --check` | |
| Two separate scripts | Split equivalence-oracle and determinism-regen | |

**Oracle coverage follow-up:**

| Option | Description | Selected |
|--------|-------------|----------|
| All present systems, sad-code, all projects | Assert per present system, skip-with-notice; determinism diff both levels | ✓ |
| swattr/transarc only, sad-code | Just the in-repo deterministic system | |
| Add a sad-model macro cross-check | Also assert at sad-model (circular reference caveat) | |

**User's choice:** One standalone script doing both; macro-equivalence for all present systems at sad-code across 5 projects (skip-with-notice); determinism diff over both levels + all present systems.
**Notes:** sad-code only for the equivalence assertion because `per_component_macro_f1` is the only independent macro reference; sad-model would be circular.

---

## Suite finalization details

| Option | Description | Selected |
|--------|-------------|----------|
| Include FP components everywhere | Current behavior; oracle passes as-is | |
| Gold-only universe | Restrict macro/pct_missed to gold components | (initial pick) |

**Tension surfaced (thinking-partner):** Gold-only on `micro`/`macro` would break micro=link F1, the CMP-02 shared-universe property, and the equivalence oracle — but is the *more correct* choice for the tail metrics. Re-asked with consistent resolutions:

| Option | Description | Selected |
|--------|-------------|----------|
| Split: micro/macro shared, tail gold-only | micro/macro on gold∪result (preserves properties + oracle); min_comp/pct_missed gold-only | ✓ |
| Gold-only everywhere | One gold universe but micro≠link F1; rewrite per_component_macro_f1 | |
| Include everywhere (gold∪result) | Revert to current; tail signal stays muddied | |

**User's choice:** Split universe — `micro`/`macro` shared (gold∪result), `min_comp`/`pct_missed` gold-only.
**Notes:** Changes committed tail numbers → artemis long-tail finding to be re-confirmed under the new definition during execution (expected to strengthen).

---

## Claude's Discretion

- Mechanical hardening left to planner/executor: warn-and-skip wording for absent external roots, CSV column ordering/precision, `min_comp` tie handling, argparse/CLI polish. Stdlib-only + reuse `calc_metrics` only stays locked.

## Deferred Ideas

- External alinker-paper repo prose rewrite → Phase 9 (different repo).
- Hardened fitness scorecard + cleverer baselines + comparison narrative → Phase 8.
- Suite/finding/universe-correction prose in `eval.tex` Ch2 → Phase 9.
- Pre-existing carry-overs (not this phase): NDG non-determinism; `transarc_error_analysis.py` → `data_loaders.py` rename; metrics API → sam-code; `.xlsx` output; real pdflatex.
