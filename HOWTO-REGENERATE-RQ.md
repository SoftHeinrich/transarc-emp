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
| `gpt-5.4_full`, `sonnet_full`     | gpt-5.4 / claude | full (s20_union) | `build_unified.py` |
| `gpt-5.4_s21`, `sonnet_s21`       | gpt-5.4 / claude | full (s_linker21)| `build_s21_dump.py` |
| `gpt-5.4_s21_noknow`, `sonnet_s21_noknow` | gpt-5.4 / claude | noknow (s_linker21) | `build_s21_dump.py` (with `S21_KNOW=noknow`) |

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

# (a) baselines + full s20_union slots (gpt-5.4_full / sonnet_full) + arcotl bridge + gold
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

# RQ2 cell-grain panel + rank-correlation of size-aware metrics vs file F1
python3 mini-src/rq2_corr.py
#   → reports/RQ2_CELLS.csv, reports/RQ2_CORR.csv

# No-enrollment doc-to-code comparison (RQ2 motivation / benchmark-bias pillar)
python3 mini-src/noenroll.py --csv reports/NOENROLL_DOC_CODE.csv
#   prints the macro panel to stdout; --csv writes the CSV (omit it for stdout only).
#   reports/NOENROLL_DOC_CODE.md is hand-written commentary — NOT generated.
```

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

⚠️ **Gotcha:** these tables carry TWO approach rows. `approach (GPT-5.4)` is the
OLD s20union baseline; `approach S21 (GPT-5.4)` is the latest. **Always read the
`S21` rows** for the current paper numbers.

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
# Point at different run slots / variant (e.g. score the old s20_union):
RQ34_VARIANT=s_linker20_union \
  RQ34_OPENAI_SLOT=$HOME_ABS/agent-linker/results/v2.6.5_s20union_gpt \
  python3 mini-rq34/rq34.py --backends openai
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

## 5. Verification

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
python3 mini-src/noenroll.py --csv reports/NOENROLL_DOC_CODE.csv
cp reports/RQ12_BIGTABLE.csv reports/s21/RQ12_BIGTABLE_s21.csv
cp reports/RQ2_PANEL.csv     reports/s21/RQ2_PANEL.csv
# 3. RQ3 + RQ4
python3 mini-rq34/rq34.py && python3 mini-rq34/rq34_rq2.py
# 4. no-knowledge ablation — see §4
# 5. verify
python3 mini-src/check.py
```
