# Phase 1: Inequality Engine — INEQ-01, INEQ-02, INEQ-03, OUT-01 - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — grey-area tables accepted/overridden by user

<domain>
## Phase Boundary

Deliver a self-contained, stdlib-only inequality engine at the study root —
`inequality.py` (i.e. `mini-inequality/inequality.py` from the repo root) — that
measures the **gold** trace-link concentration inequality of the ARDoCo benchmark
and reproduces the paper's distributional-inequality numbers:

- **INEQ-01** — per-component gold link-count inequality (Gini, Lorenz points,
  top-k share, min/median/max) for `sad-code` (component level) and `sad-sam`,
  across all 5 projects → CSV.
- **INEQ-02** — per-file (post-enrollment) concentration + per-sentence gold
  links-per-sentence distribution for `sad-code`.
- **INEQ-03** — per-project enrollment expansion factor (component decision →
  file-level pairs) and the aggregate component-FP → file-FP cascade.
- **OUT-01** — self-contained artifacts (engine + `reports/` MD/CSV), stdlib only,
  no cross-module imports, sanity-checked against canonical numbers.

IN scope: measuring the dataset distribution + reproducing the paper's Ch1
inequality tables. OUT of scope (later phases): paper-claim MATCH/MISMATCH audit
& `XX` placeholder resolution (Phase 2); Top-3/random baseline exploitation,
paper-ready Gini/Lorenz **table/figure** for ingestion, Lorenz **TeX figure**
(Phase 3 / OUT-02). New trace-link recovery is never in scope.

**Isolation (HARD):** this study lives only under `mini-inequality/`. All GSD
commands and the engine run with project root = `mini-inequality/`. Never write
to repo-root `.planning/` (active **v1.2** milestone). Commit only
`mini-inequality/**` on branch `gsd/mini-data-inequality`.
</domain>

<decisions>
## Implementation Decisions

### Area 1 — Output & report shape
- **Per-task CSVs**: `reports/inequality_sad_code.csv` and
  `reports/inequality_sad_sam.csv` (column sets differ by task), plus a combined
  long-format `reports/inequality.csv` is acceptable if cheap. Mirror the
  `COMPONENT_SUITE_{level}.csv` / `metrics.py` panel style.
- **Per-project rows + an `AVG`/`Total` row** (matches `metrics.py average_row`
  and the eval.tex tables which report per-project then aggregate).
- **Markdown report = tables-first, each section prefixed by a one-line headline**
  stating the claim (e.g. "Gini ranges 0.331→0.645"), mirroring eval.tex Ch1 prose
  so numbers are paste-ready. Report file: `reports/INEQUALITY.md`.
- **Outputs land in `mini-inequality/reports/`** (i.e. `reports/` relative to the
  study root). Engine at the study root (`inequality.py`).

### Area 2 — Distribution, Lorenz & top-k  (user: "use the most inequality-ed ones")
- **Canonical inequality unit = # distinct sentences per component** for sad-code
  (component level) and sad-sam — this is the sanity-anchored unit that matches
  `component_suite.gold_gini` and eval.tex `tab:sent_gini` (0.331→0.645).
- **ALSO report the more-skewed supplementary units** that reveal stronger
  inequality: **# links (pairs) per component** and **# files per component**
  (post-enrollment fan-out). These are supplementary views, NOT the sanity target.
- **Lorenz: emit the FULL cumulative curve** (per-component points: cumulative
  population %, cumulative mass %) to CSV, **plus an 11-point decile summary** in
  the markdown.
- **Emit the raw Lorenz CSV now** (`reports/lorenz_*.csv`, pgfplots-friendly:
  `cum_pop_pct,cum_mass_pct`). The formatted TeX figure is deferred to Phase 3.
- **Concentration set = top-1, top-3, top-10% shares + the Palma ratio**
  (top-10% mass ÷ bottom-40% mass). top-1/top-3 are required by INEQ-01; top-10%
  and Palma are the "most inequality-ed" extras.

### Area 3 — Sanity-check gate
- **Source of truth = frozen eval.tex literals**, embedded as cited expected
  constants (Gini 0.331…0.645 from `tab:sent_gini`; enrolled total 18,660 and
  per-project factors from `tab:enrollment`; cascade 36→3,457 / 96.0× from
  `tab:amplification`). The engine recomputes each value with its OWN copied
  `_gini`/enrollment and asserts agreement — imports from `src/`/`mini-src/` are
  forbidden, so component_suite is NOT called live; agreement of the copied
  definitions with the published numbers IS the faithfulness proof.
- **Tolerance: |Δ| ≤ 0.005 on Gini** (eval.tex reports 3 decimals); **exact match
  on integer counts** (18,660; 36; 3,457; per-project enrolled counts).
- **Fail loud on mismatch — non-zero exit + a diff table** (project, metric,
  expected, computed, Δ). Matches the workspace "fail loud" convention (WR-03).
- **The sanity check runs by default at the end of every run** (prints a `CHECK`
  section); a `--check-only` flag runs just the gate.

### Area 4 — Expansion & cascade framing
- **Enrollment expansion = pure-gold structural**: reproduce eval.tex
  `tab:enrollment` columns (Raw, Dir. Entries, Enrolled, Factor) per project;
  totals 525 raw → 18,660 enrolled (35.5× avg), per-project range 1.0×
  (MediaStore) → 217.6× (JabRef). Computed from raw sad-code gold + `.acm` code
  model via the copied `enroll`/`normalize_path`.
- **Cascade = reproduce eval.tex `tab:amplification`** (sad-sam FPs → induced
  file-level sad-code FPs): per project = TransArc sad-sam FPs and Σ|files(m)|
  over FP elements; aggregate 36 → 3,457 (96.0× mean amplification). Uses the
  **bundled TransArc sad-sam results** (`results/<project>/sad-sam/sadSamTlr_<project>.csv`)
  — the same source eval.tex used. This is the ONE place INEQ-03 reads a system
  result (permitted: the study "measures the dataset + scores existing results").
- **Feature all three headline numbers** in the report (enrollment 1.0×→217.6× &
  35.5× avg; cascade 36→3,457 = 96.0×; Gini 0.331→0.645) so Phase 2's claim-check
  has them ready.
- **Q4 OVERRIDE — the enrollment-expansion table is sad-code-only**: omit the
  sad-sam `1.0×` row from the expansion table. (sad-sam is still fully measured
  for the inequality distribution in Area 1/2; "omit" applies ONLY to the
  enrollment-expansion table. The cascade still consumes sad-sam FPs.)

### Claude's Discretion
- Exact CSV column names/order, markdown layout details, argparse flag names
  (beyond `--check-only`), and internal function decomposition — mirror
  `mini-src/metrics.py` style.
- Whether to also emit the combined long-format `inequality.csv` (nice-to-have).
- Choice of Palma denominator edge-case handling (empty bottom-40%).
</decisions>

<code_context>
## Existing Code Insights

### Reusable definitions (COPY verbatim, do NOT import — isolation rule)
- `src/bias/component_suite.py`:
  - `_gini(values)` — the Gini formula to copy (sorted, cumulative form).
  - `gold_gini` = `_gini([len(sentences) for each component])` — the canonical
    "#sentences-per-component" inequality the sanity check must reproduce.
  - `_code_inputs` — the reconciled sad-code universe: collapse (sentence, file)
    → (sentence, component) via the enrolled SAM-CODE map, **dropping files with
    no SAM-CODE component** (apply the same drop rule consistently).
- `mini-src/metrics.py` (the stdlib pattern to mirror):
  - `enroll(gold, code_files)` — expand directory-trailing-`/` gold entries to
    individual files.
  - `normalize_path(path)` — strip leading `Implementation/`.
  - `load_code_model_files` (parse `.acm` JSON), `load_gs_sad_sam`,
    `load_gs_sad_code_raw`, `load_file_to_comps` (file→{component} via SAM-CODE).
  - Benchmark/result roots derived from file location (`_ARDOCO_HOME = parents[2]`)
    with `$TRANSARC_BENCHMARK` / `$TRANSARC_RESULTS_DIR` overrides — replicate so
    `inequality.py` at the study root resolves the same `ardoco-home` root.
  - CLI/table/CSV pattern (`argparse`, `print_table`, `write_csv`, `average_row`).

### Data inputs
- Benchmark gold: `goldstandard_sad_*-sam_*.csv`, `goldstandard_sam_*-code_*.csv`,
  `goldstandard_sad_*-code_*.csv`; code models `*.acm` — 5 projects.
- TransArc sad-sam results (for the cascade only):
  `results/<project>/sad-sam/sadSamTlr_<project>.csv` (all 5 present, verified).

### Path-relativity note (PREVENTS the double-nesting trap)
The engine and all GSD commands run with **project root = `mini-inequality/`**.
- Engine path = `inequality.py` (study root) = `mini-inequality/inequality.py`
  from repo root — do NOT create `mini-inequality/mini-inequality/…`.
- Outputs = `reports/…` (study root) = `mini-inequality/reports/…` from repo root.
- Reference modules/docs are one level up: `../src/bias/component_suite.py`,
  `../mini-src/metrics.py`, `../writing/eval.tex`.
</code_context>

<canonical_refs>
## Canonical References (downstream agents MUST read these)

Paths are repo-root-relative (repo root = `/mnt/hostshare/ardoco-home/transarc-emp`).
From the study root (`mini-inequality/`), prefix with `../`. The `alinker-paper`
refs live one level above the repo root (`/mnt/hostshare/ardoco-home/alinker-paper`).

- `writing/eval.tex` — **local Ch1 source of the sanity targets**. Key tables:
  `tab:enrollment` (lines ~57-74: 525→18,660, 35.5×, 1.0×→217.6×),
  `tab:amplification` (lines ~156-173: 36→3,457, 96.0×; per-project sad-sam FPs &
  induced file FPs), `tab:sent_gini` (Gini 0.331→0.645, Top-3 %). MUST read before
  implementing the sanity gate and the expansion/cascade tables.
- `src/bias/component_suite.py` — `_gini`, `gold_gini`, `_code_inputs` (copy the
  definitions; sanity-check agreement). READ, do not import.
- `mini-src/metrics.py` — `enroll`, `normalize_path`, `.acm`/gold loaders, CLI
  pattern (mirror). READ, do not import.
- `mini-src/check.py` — example of the sanity-check pattern in this workspace.
- `/mnt/hostshare/ardoco-home/alinker-paper/sections/metric.tex` — expansion
  1.0×→217.6×, long-tail-both-tasks (claim source for Phase 2; context here).
- `/mnt/hostshare/ardoco-home/alinker-paper/sections/eval.tex` — long tail
  dominates the average; Top-3/random exploit inequality (Phase 3 context).
- `/mnt/hostshare/ardoco-home/alinker-paper/sections/intro.tex` — `XX`
  placeholders (Phase 2/3 targets; not resolved in Phase 1).
- Benchmark root: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
  (5 projects; gold standards + `.acm`). Overridable via `$TRANSARC_BENCHMARK`.
- Results root: `results/` (repo) — `$TRANSARC_RESULTS_DIR` override; holds the
  TransArc sad-sam CSVs used by the cascade.
</canonical_refs>

<specifics>
## Specific Ideas

- The engine must reproduce these EXACT published numbers (faithfulness gate):
  Gini 0.331 (MediaStore) → 0.645 (Teammates); enrolled total 18,660 (35.5× avg),
  JabRef 217.6×; cascade total 36 sad-sam FPs → 3,457 file FPs (96.0×), with
  per-project amplification (Teammates 85.5×, JabRef 495.0×, BBB 14.2×,
  MediaStore 1.0×, TeaStore —).
- "Most inequality-ed" (user, Area 2): prefer the richest concentration
  characterization — supplementary #links/#files-per-component units, full Lorenz
  curve, top-10% + Palma — alongside the sanity-anchored #sentences unit.
- sad-sam is omitted from the **enrollment-expansion table only** (Area 4 Q4),
  not from the inequality distribution.
</specifics>

<deferred>
## Deferred Ideas

- Paper-ready Gini/Lorenz **table/figure** for ingestion + Lorenz **TeX figure**
  → Phase 3 (OUT-02).
- Top-3 / random **baseline exploitation** argument → Phase 3 (MOTIV-01).
- Paper-claim **MATCH/MISMATCH/STALE audit** + `XX` placeholder resolution
  → Phase 2 (CLAIM-01/02/03).
</deferred>
