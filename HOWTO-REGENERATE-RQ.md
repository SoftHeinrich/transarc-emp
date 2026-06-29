# Regenerating the RQ1–RQ4 results by hand

This is the manual, step-by-step recipe for rebuilding every number behind the
paper's research questions, from the raw agent-linker run outputs to the scored
CSVs the paper floats read. Everything here is **stdlib-only Python 3** — no
`pip install`, no `requirements.txt`.

Run all commands from the evaluation repo root (`transarc-emp/`, i.e.
`mono/evaluation/`). Paths assume the standard sibling layout under
`/mnt/hostshare/ardoco-home/` (`agent-linker/`, `transarc-emp/`, `sota/`).

---

## 0. What lives where (the two data forms)

The RQs are computed by **two** scoring engines that read **two different
forms** of the same agent-linker runs:

| RQs | Engine | Reads | Why |
|-----|--------|-------|-----|
| RQ1, RQ2 | `mini-src/` | the normalized **`sota/recovered-links/` dump** (built from the run *extracts*) | needs only the final link sets, scored against gold |
| RQ3, RQ4 | `mini-rq34/` | the run **`phase_cache/*.pkl` pickles** directly | needs per-validator and per-linker decisions that the final link set throws away |

So the pipeline is:

```
agent-linker runs ──► extracts ──► sota/recovered-links dump ──► mini-src ──► RQ1, RQ2
       └────────────► phase_cache pickles ─────────────────────► mini-rq34 ─► RQ3, RQ4
```

### Run inputs (agent-linker repo)

The canonical N=3 `s_linker21` (v2.6.6) sweep, four variants:

| Backend | Knowledge | Run dir (pickles → RQ3/RQ4) | Extracts dir (→ sota dump → RQ1/RQ2) |
|---------|-----------|------------------------------|---------------------------------------|
| GPT-5.4 | full   | `agent-linker/results/v2.6.6_s21_gpt`           | `agent-linker/results/v2.6.6_extracts_s21`            |
| Claude  | full   | `agent-linker/results/v2.6.6_s21_sonnet`        | `agent-linker/results/v2.6.6_extracts_s21_sonnet`     |
| GPT-5.4 | noknow | `agent-linker/results/v2.6.6_s21_noknow_gpt`    | `agent-linker/results/v2.6.6_extracts_s21_noknow`     |
| Claude  | noknow | `agent-linker/results/v2.6.6_s21_noknow_sonnet` | `agent-linker/results/v2.6.6_extracts_s21_noknow_sonnet` |

GPT-5.4 = paper body, Claude = appendix mirror (decision D-04 revised).
Gold standard is read from `$TRANSARC_BENCHMARK` (the ARDoCo benchmark tree); if
unset, each script falls back to its built-in default path.

### sota config slots (the "named correctly" dump)

`sota/recovered-links/` stores each run as a normalized link dump in a config
slot named **`<backend>_<knowledge-tag>`**:

| Config slot | Backend | Knowledge | Built by |
|-------------|---------|-----------|----------|
| `gpt-5.4_s21`, `sonnet_s21`       | gpt-5.4 / claude | full (s_linker21)| `build_s21_dump.py` |
| `gpt-5.4_s21_noknow`, `sonnet_s21_noknow` | gpt-5.4 / claude | noknow (s_linker21) | `build_s21_dump.py` (with `S21_KNOW=noknow`) |

**s21 is the only shipped approach config.** `build_unified.py` also emits legacy
`gpt-5.4_full` / `sonnet_full` slots from the old `s_linker20_union` run — these
are **deprecated**; s21 supersedes them, so ignore those slots everywhere.

Each slot holds `model-doc/aalinker/<slot>/run{1,2,3}/<project>.csv` (doc→model)
and `doc-code/aalinker-composed/<slot>/run{1,2,3}/<project>.csv` (doc→code,
composed through the ArCoTL model→code bridge). `sota/` is a plain data tree, not
a git repo — these dumps are regenerable artifacts, not version-controlled.

---

## 1. Build the normalized sota dump (needed for RQ1 / RQ2)

Skip this if `sota/recovered-links/` is already populated. The build is
**additive and idempotent** — it never touches existing slots.

```bash
HOME_ABS=/mnt/hostshare/ardoco-home

# (a) gold standards + ArCoTL model→code bridge + SOTA baselines (TransArC, Artemis).
#     The s21 build below depends on the gold + bridge this produces, so run it first.
#     (It also emits the deprecated s20_union approach slots; s21 supersedes them — ignore.)
python3 ../sota/recovered-links/build_unified.py

# (b) s_linker21 FULL slots (gpt-5.4_s21 / sonnet_s21)
python3 mini-src/build_s21_dump.py                                   # gpt-5.4_s21 (defaults)
EXTRACTS_S21=$HOME_ABS/agent-linker/results/v2.6.6_extracts_s21_sonnet \
  S21_BE_DIR=sonnet S21_BE_TAG=claude \
  S21_CONFIG=sonnet_s21 S21_MANIFEST_TAG=s21_sonnet \
  python3 mini-src/build_s21_dump.py                                 # sonnet_s21

# (c) s_linker21 NO-KNOWLEDGE slots (gpt-5.4_s21_noknow / sonnet_s21_noknow)
EXTRACTS_S21=$HOME_ABS/agent-linker/results/v2.6.6_extracts_s21_noknow \
  S21_BE_DIR=gpt S21_BE_TAG=gpt-5.4 \
  S21_CONFIG=gpt-5.4_s21_noknow S21_MANIFEST_TAG=s21_noknow S21_KNOW=noknow \
  python3 mini-src/build_s21_dump.py                                 # gpt-5.4_s21_noknow
EXTRACTS_S21=$HOME_ABS/agent-linker/results/v2.6.6_extracts_s21_noknow_sonnet \
  S21_BE_DIR=sonnet S21_BE_TAG=claude \
  S21_CONFIG=sonnet_s21_noknow S21_MANIFEST_TAG=s21_noknow_sonnet S21_KNOW=noknow \
  python3 mini-src/build_s21_dump.py                                 # sonnet_s21_noknow
```

Each `build_s21_dump.py` run prints a `model-doc F1 vs gold` integrity figure and
rewrites `sota/recovered-links/UNIFIED_MANIFEST.csv`. Sanity check at time of
writing: full s21 ≈ 0.95 macro-F1, no-knowledge ≈ 0.88 (knowledge removal costs
~7 points, as expected).

---

## 2. RQ1 (link / file P/R/F1) and RQ2 (size-aware panel)

Both come out of `mini-src/`, which scores the sota dump against gold. No new
metric code — `metrics.py` is the sole implementation, pinned by `check.py`.

```bash
# RQ1 + RQ2 wide table (one row per system, approach averaged over 3 runs)
python3 mini-src/rq12.py
#   → reports/RQ12_BIGTABLE.csv   (superset of every RQ1/RQ2 cell)
#   → reports/RQ2_PANEL.csv       (focused RQ2 size-aware panel, both backends)
#   → reports/RQ12_PERPROJECT.csv (per system×backend×project, whole suite — feeds the per-project big table)

# RQ2 cell-grain panel + rank-correlation of size-aware metrics vs file F1
python3 mini-src/rq2_corr.py
#   → reports/RQ2_CELLS.csv, reports/RQ2_CORR.csv
```

> `mini-src/noenroll.py` (the no-enrollment benchmark-bias side analysis) is
> **deprecated** — it scores the old `s_linker20_union` run and is not part of the
> s21 RQ1–RQ4 pipeline. Skip it.

### Which CSV column feeds which paper table

| Paper table | CSV | Columns |
|-------------|-----|---------|
| RQ1 doc-to-model (`tab:rq1-sadsam`) | `RQ12_BIGTABLE.csv` | `doc_to_model_link_{precision,recall,f1}` |
| RQ1 doc-to-code (`tab:rq1-sadcode`) | `RQ12_BIGTABLE.csv` | `doc_to_code_file_{precision,recall,f1}` |
| RQ2 size-aware (`tab:rq2-summary`)  | `RQ2_PANEL.csv` | `doc_to_code_file_f1`, `..._sentence_coverage`, `..._worst_component_f1`, `..._harmonic_component_f1` |

### Paper snapshot (what the floats actually read)

The paper floats read a **curated copy** under `reports/s21/`, not the live
`reports/` output. After regenerating, refresh the snapshot:

```bash
cp reports/RQ12_BIGTABLE.csv reports/s21/RQ12_BIGTABLE_s21.csv
cp reports/RQ2_PANEL.csv     reports/s21/RQ2_PANEL.csv
```

⚠️ **Gotcha:** rq12's default table still carries deprecated `s20_union` approach
rows (`approach (GPT-5.4)` / `approach (Claude)`) alongside the current
`approach S21 (...)` rows. **Read only the `S21` rows.** To drop the legacy rows
entirely, remove the `gpt-5.4_full` / `sonnet_full` entries from `ROSTER` in
`mini-src/rq12.py`.

---

## 3. RQ3 (validator contribution) and RQ4 (per-module ablation)

Both come out of `mini-rq34/`, which reads the run `phase_cache` pickles directly
(it needs the candidate-vs-validated split and per-linker provenance that the
final link set discards). Defaults to the **full** s21 slots.

```bash
# RQ3 + RQ4 aggregates (both backends, all 3 runs + average), per-project drill-downs
python3 mini-rq34/rq34.py
#   → reports/rq3_validators.csv, reports/rq3_variants.csv
#   → reports/rq4_linkers.csv,    reports/rq4_variants.csv
#   → reports/<backend>/<project>/{rq3,rq3_audit,rq4,rq4_upset}.csv
#   → reports/<backend>/runs_summary.csv

# RQ3/RQ4 link sets composed to doc-to-code and re-scored with the RQ2 metric panel
python3 mini-rq34/rq34_rq2.py
#   → reports/rq34_rq2_variants.csv, reports/rq34_rq2_linkers.csv
#   → reports/rq34_rq2_variants_perproject.csv, reports/rq34_rq2_linkers_perproject.csv
#                                                (per-project size-aware — feeds the RQ4 per-project big table)
#   → reports/RQ34_RQ2_INVESTIGATION.md
```

`rq34.py` cross-checks every Full-variant `tp/fp/fn` against the run's
`ablation_*.json` and prints `validate=OK` per backend. Canonical (median-macro)
runs: `claude` run1 ≈ 0.9318, `openai` run3 ≈ 0.9338.

Useful flags / env knobs:

```bash
python3 mini-rq34/rq34.py --backends openai          # one backend only
python3 mini-rq34/rq34.py --run run1                 # force a drill-down run
python3 mini-rq34/rq34.py --no-validate              # skip the ablation-JSON cross-check
# Point at a different run slot via env (RQ34_VARIANT / RQ34_OPENAI_SLOT /
# RQ34_CLAUDE_SLOT) — see §4b for the no-knowledge invocation.
```

---

## 4. No-knowledge ablation

The no-knowledge variant answers "how much does the injected knowledge buy us?"
Its slots/runs are listed in §0.

### 4a. RQ1 / RQ2 (size-aware) for no-knowledge

The no-knowledge doc→model and doc→code link sets live in the
`gpt-5.4_s21_noknow` / `sonnet_s21_noknow` sota slots (built in §1c). The
canonical way to get the **size-aware tail** (file F1 / coverage / worst-component
/ harmonic-component) is `rq34_rq2.py`, which composes the no-knowledge link sets
and scores them with the RQ2 panel:

```bash
RQ34_VARIANT=s_linker21 \
  RQ34_OPENAI_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_gpt \
  python3 mini-rq34/rq34_rq2.py --backends openai \
    --csv-root mini-rq34/reports_s21_noknow
# read the openai,average,Full row → doc-to-code: file .851, cov .767, worst .533, harmonic .661

RQ34_VARIANT=s_linker21 \
  RQ34_CLAUDE_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_sonnet \
  python3 mini-rq34/rq34_rq2.py --backends claude \
    --csv-root mini-rq34/reports_s21_noknow_sonnet
```

For a quick per-run file-level check straight off the sota slot:

```bash
python3 mini-src/metrics.py --task sad-code \
  --results-dir $HOME_ABS/sota/recovered-links/doc-code/aalinker-composed/gpt-5.4_s21_noknow/run1 \
  --result-pattern '{project}.csv'
```

The per-run doc→model P/R/F1 for no-knowledge is also recorded directly in the
slot manifests:
`sota/recovered-links/model-doc/aalinker/_manifest_s21_noknow.csv` (gpt) and
`_manifest_s21_noknow_sonnet.csv` (claude).

### 4b. RQ3 / RQ4 for no-knowledge

Same `rq34.py`, pointed at the no-knowledge run slots:

```bash
RQ34_VARIANT=s_linker21 \
  RQ34_OPENAI_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_gpt \
  RQ34_CLAUDE_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_sonnet \
  python3 mini-rq34/rq34.py --csv-root mini-rq34/reports_s21_noknow
```

---

## 5. Paper tables: per-RQ CSVs → TeX (the CSV→TeX pipeline)

The paper's RQ floats are **generated**, not hand-typed. Two stdlib scripts sit on
top of the CSVs above:

```bash
# (a) reshape the wide CSVs into one small "this is the table" CSV per float
python3 mini-src/rq_tables.py
#   → reports/tex_src/rq1.csv  rq2.csv  rq3.csv  rq3_claude.csv  rq3_perproject.csv  rq4.csv   (body + RQ3 appendix)
#   → reports/tex_src/bigtable_rq12_avg.csv  bigtable_rq12_perproject.csv               (RQ1+RQ2 big tables)
#   → reports/tex_src/bigtable_rq4_avg.csv   bigtable_rq4_perproject.csv                (RQ4 big tables)

# (b) render each tex_src CSV into a booktabs .tex via the SPECS registry
python3 mini-src/csv_to_tex.py
#   → reports/tex/*.tex   (rq{1,2,3,4}-results / rq3-confusion / big-table* / rq4-bigtable*)
```

`rq_tables.py` does NO metric math — it only selects rows/columns from the CSVs in
§2–§4 (it reads the no-knowledge `rq34_rq2_*` for the RQ4 "No knowledge" row, so run
§4 first). `csv_to_tex.py` is a declarative renderer: edit the `SPECS` list to change
columns, headers, precision, bolding, or captions. Re-running is byte-identical.

**Copy into the paper** (the manual snapshot step — the generated `.tex` lives here,
the paper just consumes copies):

```bash
cp reports/tex/rq1-results.tex reports/tex/rq2-results.tex \
   reports/tex/rq3-confusion.tex reports/tex/rq4-results.tex   ../alinker-paper/table/
cp reports/tex/big-table.tex reports/tex/big-table-perproject.tex \
   reports/tex/rq4-bigtable.tex reports/tex/rq4-bigtable-perproject.tex \
   reports/tex/rq3-confusion-claude.tex reports/tex/rq3-perproject.tex   ../alinker-paper/appendix/
```

The copied files carry a `% GENERATED ... do not edit by hand` header; edit the CSV
specs and re-render instead. Which float each CSV feeds:

| Paper float (label) | tex_src CSV | Backend / grain |
|---------------------|-------------|-----------------|
| body RQ1 `tab:rq1` | `rq1.csv` | GPT-5.4, macro |
| body RQ2 `tab:rq2` | `rq2.csv` | GPT-5.4, macro size-aware |
| body RQ3 `tab:rq3-confusion` | `rq3.csv` | GPT-5.4, canonical run |
| body RQ4 `tab:rq4` | `rq4.csv` | GPT-5.4, macro |
| appendix `tab:detailed-macro` | `bigtable_rq12_avg.csv` | both backends, whole suite |
| appendix `tab:detailed-perproject` | `bigtable_rq12_perproject.csv` | both backends, per project |
| appendix `tab:rq4-detailed` | `bigtable_rq4_avg.csv` | both backends, whole suite |
| appendix `tab:rq4-perproject` | `bigtable_rq4_perproject.csv` | both backends, per project |
| appendix `tab:rq3-confusion-claude` | `rq3_claude.csv` | Claude, canonical run |
| appendix `tab:rq3-perproject` | `rq3_perproject.csv` | GPT-5.4, per project |

---

## 6. Verification

```bash
python3 mini-src/check.py     # frozen-golden regression on metrics.py → PASS
```

`check.py` asserts `metrics.py` reproduces a frozen golden table to 1e-4, so any
arithmetic drift in the RQ1/RQ2 numbers is caught. RQ3/RQ4 carry their own
`validate=OK` cross-check inside `rq34.py` (§3).

Bundled-TransArc headline (a quick smoke reference): sad-code file F1 .80 /
worst-comp .54 / harmonic .67 / cov .75; sad-sam link F1 .80 / cov .79.

---

## Quick reference — one block, full rebuild

```bash
cd mono/evaluation
HOME_ABS=/mnt/hostshare/ardoco-home

# 1. sota dump (full + noknow, both backends) — see §1 for the 5 build commands
# 2. RQ1 + RQ2
python3 mini-src/rq12.py && python3 mini-src/rq2_corr.py
cp reports/RQ12_BIGTABLE.csv reports/s21/RQ12_BIGTABLE_s21.csv
cp reports/RQ2_PANEL.csv     reports/s21/RQ2_PANEL.csv
# 3. RQ3 + RQ4
python3 mini-rq34/rq34.py && python3 mini-rq34/rq34_rq2.py
# 4. no-knowledge ablation — see §4 (needed for the RQ4 "No knowledge" big-table row)
RQ34_VARIANT=s_linker21 RQ34_OPENAI_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_gpt \
  python3 mini-rq34/rq34_rq2.py --backends openai --csv-root mini-rq34/reports_s21_noknow
RQ34_VARIANT=s_linker21 RQ34_CLAUDE_SLOT=$HOME_ABS/agent-linker/results/v2.6.6_s21_noknow_sonnet \
  python3 mini-rq34/rq34_rq2.py --backends claude --csv-root mini-rq34/reports_s21_noknow_sonnet
# 5. paper tables: reshape -> render -> copy into ../alinker-paper (see §5)
python3 mini-src/rq_tables.py && python3 mini-src/csv_to_tex.py
cp reports/tex/{rq1-results,rq2-results,rq3-confusion,rq4-results}.tex ../alinker-paper/table/
cp reports/tex/{big-table,big-table-perproject,rq4-bigtable,rq4-bigtable-perproject,rq3-confusion-claude,rq3-perproject}.tex ../alinker-paper/appendix/
# 6. verify
python3 mini-src/check.py
```
