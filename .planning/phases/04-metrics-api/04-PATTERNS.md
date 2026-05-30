# Phase 4: Metrics API - Pattern Map

**Mapped:** 2026-05-30
**Files analyzed:** 1 new file (`src/lib/metrics_api.py`)
**Analogs found:** 4 / 4 (all reuse targets exist; zero reimplementation required)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog(s) | Match Quality |
|-------------------|------|-----------|-------------------|---------------|
| `src/lib/metrics_api.py` | utility / CLI script | batch transform (load → compute → emit CSV+LaTeX) | `src/lib/new_metrics_analysis.py` (import + compute loop), `src/bias/evaluation_critique.py` (sad-code granularities), `src/paper/generate_tables.py` (LaTeX emit) | role-match composite |

This is a single new script that composes four existing modules. There is no exact single-file analog; instead the planner must stitch together patterns from three sibling scripts. No `argparse` exists anywhere in `src/` (grep confirmed empty) — the CLI surface (`--task`, `--project`) is genuinely new and is the only thing not copied from an analog. `csv.writer`/`DictWriter` for *output* also does not exist in `src/` (csv is only used for *reading* gold/result files); the wide-CSV writer is also new but trivial stdlib.

---

## Pattern Assignments

### `src/lib/metrics_api.py` (utility / CLI, batch transform)

The file is built from five copied patterns plus two genuinely-new small pieces (argparse CLI, csv output writer).

---

#### Pattern 1 — Module header + import block (COPY from `new_metrics_analysis.py` lines 12-31)

This is the canonical "sibling in `src/lib`" import. Because `metrics_api.py` also lives in `src/lib`, the `sys.path.insert` target is `parent` (NOT `parent.parent / "lib"`):

```python
import csv
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

# Import data loaders from the shared library module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transarc_error_analysis import (
    PROJECTS, BENCHMARK, RESULTS,
    GS_SAD_SAM, GS_SAM_CODE, GS_SAD_CODE, ACM_FILES, TEXT_FILES,
    normalize_path, load_code_model_files, enroll_gold_standard,
    load_gs_sad_sam, load_gs_sad_sam_maps, load_gs_sam_code_raw,
    load_gs_sam_code_maps, load_gs_sad_code_raw, load_gs_sad_code_enrolled,
    load_result_sad_code, load_transarc_intermediate_sad_sam,
    load_transarc_intermediate_sam_code, load_text, load_model_element_names,
    calc_metrics,
)
```

**Importing the sad-code granularity helpers from `src/bias`** is the one cross-package import. `evaluation_critique.py` itself does `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))` (its line 24) to reach `src/lib`; from `src/lib/metrics_api.py` the reverse hop is:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bias"))
from evaluation_critique import (
    _compute_decision_f1, _compute_component_f1, _compute_weighted_f1,
    enroll_with_provenance, load_sad_code_raw_with_provenance,
    load_sam_code_enrolled,
)
```
(CONTEXT "Claude's Discretion" allows refactoring these helpers into `src/lib` only if the import is blocked — it is not blocked, so import-as-is.)

For LaTeX, import from `src/paper`:
```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "paper"))
from generate_tables import render_table, latex_escape, colspec, write_table
```
NOTE: `write_table` in `generate_tables.py` (lines 169-173) hardcodes `OUT = ROOT/"writing"/"tables"` and writes `<name>.tex` there — exactly the CONTEXT-required path `writing/tables/metrics_<task>.tex`. Calling `write_table("metrics_sad-sam", content)` produces `writing/tables/metrics_sad-sam.tex`. Reuse it directly; do not reimplement the file write.

---

#### Pattern 2 — Per-project load + compute loop (COPY shape from `new_metrics_analysis.py` lines 630-662)

The established loop loads everything once per project, then computes. Copy this skeleton, dropping V45:

```python
for proj in PROJECTS:                       # or [args.project] when filtered
    code_model = load_code_model_files(proj)
    gs_sad_sam = load_gs_sad_sam(proj)              # set[(modelElementID, sentence)]
    gs_sad_sam_maps = load_gs_sad_sam_maps(proj)    # (sent->models, model->sents)
    gs_sam_code_map, _ = load_gs_sam_code_maps(proj, code_model)  # model->files
    gs_sad_code = load_gs_sad_code_enrolled(proj, code_model)
    text = load_text(proj)
    model_names = load_model_element_names(proj)
    all_sents = set(text.keys())
    all_comps = set(model_names.keys())
    ...
```

**Result loading + missing-file skip (CONTEXT: "skip + warn, no hard error").** All result loaders already return an empty set when the file is absent — see `load_result_sad_code` lines 223-232 (`if not path.exists(): return links`) and `load_result_sad_sam_standalone` lines 199-208. So the skip pattern is: check the appropriate result path, warn to stderr and `continue` if empty/missing:
```python
res = load_result_sad_sam_standalone(proj)   # sad-sam
# or: res = load_result_sad_code(proj)        # sad-code
if not res:
    print(f"WARNING: no results for {proj}/{task}, skipping", file=sys.stderr)
    continue
```

---

#### Pattern 3 — `calc_metrics` exact-set P/R/F1 + granularity transforms (COPY from `transarc_error_analysis.py` lines 296-309, and `analysis_a` lines 316-342)

`calc_metrics(gold, result) -> (precision, recall, f1, tp, fp, fn)` is exact-set comparison. **Every granularity is built by transforming the link set, then calling `calc_metrics`** (CONTEXT "Established Patterns"). `analysis_a` (lines 320-342) is the reference for how each task's gold/result is prepared:

```python
# SAD-SAM: no enrollment, direct pair compare
p, r, f1, tp, fp, fn = calc_metrics(gs_sad_sam, res)

# SAD-CODE: enrolled gold
gs_enrolled = load_gs_sad_code_enrolled(proj, code_model)
p, r, f1, tp, fp, fn = calc_metrics(gs_enrolled, res)
```

##### >>> CRITICAL TASK ASYMMETRY — granularity wiring <<<

The granularity helpers in `evaluation_critique.py` are **SAD-CODE-ONLY**. They consume enrollment artifacts (`raw_to_enrolled`, `enrolled_to_raw`, `file_to_comps`) that DO NOT EXIST for SAD-SAM. The planner must NOT wire any of these into the sad-sam path.

**SAD-SAM granularities (NO files, NO enrollment) — build inline in `metrics_api.py`:**

| Granularity | How to compute | Source pattern |
|---|---|---|
| **Link/pair-level** (= Decision-level; headline) | `calc_metrics(gs_sad_sam, res)` directly on raw `(modelElementID, sentence)` set | `analysis_a` line 326. Every pair is one human decision → zero inflation, so link == decision. |
| **Sentence-level** | aggregate to `(sentence, ...)`: a sentence is TP if it has any correct component. Build with `compute_hus`-style sentence grouping OR a sentence-set transform then `calc_metrics`. | grouping idiom in `compute_emr` lines 152-157 / `compute_hus` lines 431-436 |
| **Component-level** | the SAD-SAM set is ALREADY keyed by `modelElementID` (the component). Component-level F1 = aggregate the pair set by collapsing sentences, i.e. compare the set of `(modelElementID, sentence)` already — OR map `modelElementID`→component name via `load_model_element_names` and compare component-keyed sets. | `load_model_element_names` lines 604-610; do NOT use `_compute_component_f1` (it needs `file_to_comps`, a sad-code map). |

**SAD-SAM applicable alt metrics:** `compute_mcc(gs_sad_sam, res, all_sents, all_comps)` (lines 90-128) and `compute_map(gs_sad_sam, ranked)` (lines 209-254). TransArc has no per-link confidence → use `transarc_sad_sam_as_ranked` (lines 258-260) to assign uniform 0.5. `compute_acf1`, `compute_ndg`, `compute_hus`-file are SAD-CODE-only (need `gold_sam_code_map`) → render `—` (N/A) in the unified schema.

**SAD-CODE granularities (enrollment) — REUSE evaluation_critique helpers verbatim:**

These require provenance maps built by `enroll_with_provenance` (lines 66-87) and a `file_to_comps` map (built by the caller, lines 712-720). Copy the caller's map-construction exactly:

```python
# Provenance maps (from raw gold, not the plain enroll_gold_standard)
raw_entries = load_sad_code_raw_with_provenance(proj)            # lines 55-63
enrolled, raw_to_enrolled, enrolled_to_raw = enroll_with_provenance(raw_entries, code_model)  # lines 66-87

# file -> {component_name} map  (caller idiom, lines 715-720)
names = load_model_element_names(proj)
sam_enrolled = load_sam_code_enrolled(proj, code_model)          # (ae_id, file_path)
file_to_comps = defaultdict(set)
for ae, fp in sam_enrolled:
    file_to_comps[fp].add(names.get(ae, ae))

res = load_result_sad_code(proj)
file_level   = calc_metrics(enrolled, res)                       # File-level (misleading headline)
decision     = _compute_decision_f1(enrolled, res, raw_to_enrolled)        # lines 600-628 -> dict{p,r,f1,tp,fp,fn}
component    = _compute_component_f1(enrolled, res, file_to_comps)         # lines 631-652 -> dict
weighted     = _compute_weighted_f1(enrolled, res, enrolled_to_raw, raw_to_enrolled)  # lines 655-684 -> dict
```
Caller reference for these exact calls: `part5_alternative_metrics` lines 728-738.

**SAD-CODE alt metrics:** `compute_acf1(gs_sad_code, res, gs_sam_code_map)` (lines 274-326), `compute_ndg` (needs `compute_random_f1` lines 342-383 + `compute_oracle_f1` lines 386-398; call sequence at lines 785-792), `compute_hus(gs_sad_code, res)` (lines 420-475), `compute_mcc` over `all_sents × code_files` universe (caller lines 688-699). MAP at sad-code is optional.

**Convergence axis (feeds Phase 5 STUDY-03):** the two granularities present in BOTH tasks are **Decision** and **Component**. For sad-sam Decision==Link (the raw pair set); for sad-code Decision is `_compute_decision_f1`. Component for sad-sam aggregates by `modelElementID`; for sad-code via `_compute_component_f1`. Keep these two columns populated for both tasks.

---

#### Pattern 4 — Unified column schema with N/A cells

CONTEXT decision: ONE superset of columns across both tasks; inapplicable cells render `"—"`. Suggested ordering (Claude's discretion per CONTEXT, but anchor on this):

```
project, link/pair_F1, sentence_F1, decision_F1, component_F1, file_F1, weighted_F1,
         MCC, MAP, ACF1, NDG, HUS, (+ optional P/R or TP/FP/FN sub-columns)
```
- **sad-sam row:** populate link, sentence, decision(=link), component, MCC, MAP, HUS(sam-level). `file_F1`, `weighted_F1`, `ACF1`, `NDG` → `"—"`.
- **sad-code row:** populate file, decision, component, weighted, MCC, ACF1, NDG, HUS. `link_F1`, `sentence_F1` → `"—"` (or map sentence→link analog if desired; default `"—"`).

Add a trailing **mean/avg row** (CONTEXT "plus a mean/avg row"). Averaging idiom — copy the `sum_.../n` accumulation pattern from `new_metrics_analysis.py` lines 851-860 and the avg-row pattern from `generate_tables.py` lines 374-378:
```python
avg = ["Average"]
for col in numeric_cols:
    vals = [r[col] for r in rows if r[col] != "—"]
    avg.append(sum(vals)/len(vals) if vals else "—")
```

---

#### Pattern 5 — CSV output (NEW; stdlib `csv.writer`, no analog in src/)

No output-CSV writer exists in `src/` (csv module is used only for *reading* via `csv.DictReader`). This is new but trivial. The only existing CSV-*producing* artifact referenced is `reports/S12C_VS_TRANSARC.csv` consumed by `generate_tables.py` `_load_csv` (lines 339-343) using `csv.DictReader` — that confirms reports/ is the CSV home. Write the wide table:
```python
import csv
out_csv = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports") / f"metrics_{task}.csv"
with out_csv.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for row in rows: w.writerow(row)
    w.writerow(avg_row)
```
Use the hardcoded-absolute-path-at-module-top convention (`transarc_error_analysis.py` lines 22-24 define `BENCHMARK`/`RESULTS`; `new_metrics_analysis.py` line 33 defines `OUTPUT_MD = Path(".../reports/...")`). Define `REPORTS = Path(".../reports")` at module top the same way.

---

#### Pattern 6 — LaTeX output (REUSE `generate_tables.py` helpers verbatim, lines 136-173)

`render_table(rows, caption, label, note=None, header_override=None)` (lines 136-166) builds a full booktabs `\begin{table}` float. `colspec` (lines 131-133) left-aligns col 0, right-aligns the rest. `latex_escape` (lines 115-128) protects `&%#_` and existing math. `write_table(name, content)` (lines 169-173) writes to `writing/tables/<name>.tex`. Caller idiom to copy — `t_s12c_four_level` lines 353-397:

```python
header = ["Project", "Link \\fone", "Sentence \\fone", "Decision \\fone", ...]
data   = [[proj, f"{link_f1:.3f}", ...] for proj in PROJECTS] + [avg_row]
write_table(
    f"metrics_{task}",
    render_table([header] + data,
                 caption="Unified metric set for the \\%s task ..." % task,
                 label="tab:metrics-%s" % task,
                 note="Source: \\texttt{reports/metrics\\_%s.csv}." % task,
                 header_override=header),  # header has LaTeX macros -> use override
)
```
Use `header_override` (verbatim emission, line 139) because metric headers contain LaTeX macros like `\fone`; auto-derived headers go through `latex_escape`. Render the N/A cell as `"--"` (matches `_fmt_f1` empty-value convention, line 349).

---

## Shared Patterns

### Hardcoded absolute paths at module top
**Source:** `transarc_error_analysis.py` lines 22-24; `new_metrics_analysis.py` line 33.
**Apply to:** the new file's `REPORTS` output dir (`writing/tables` comes free from `generate_tables.write_table`).
```python
REPORTS = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports")
```

### `sys.path.insert` sibling import
**Source:** `new_metrics_analysis.py` lines 21-22 (to `parent` for `src/lib` siblings); `evaluation_critique.py` line 24 (to `parent.parent/"lib"`).
**Apply to:** all three cross-module imports (lib self, bias, paper) — see Pattern 1.

### `calc_metrics` is the single F1 primitive
**Source:** `transarc_error_analysis.py` lines 296-309.
**Apply to:** every granularity that is not already wrapped by an `evaluation_critique`/`new_metrics` helper. All transforms reduce to "build two link sets, call `calc_metrics`."

### Missing-file tolerance
**Source:** every result loader, e.g. `load_result_sad_code` lines 223-232 returns `set()` if absent.
**Apply to:** the per-project skip-and-warn (CONTEXT: no hard error).

---

## No Analog Found

| Aspect | Reason / Resolution |
|--------|---------------------|
| `argparse` CLI (`--task {sad-sam,sad-code}` required, `--project` optional) | No `argparse` anywhere in `src/` (grep returned nothing). New code; standard stdlib `argparse`. This is the only behavioral surface with no precedent. |
| Output `csv.writer`/`DictWriter` | csv module is used only for *reading* in `src/`; the wide-CSV emitter is new (trivial). The consumed artifact `S12C_VS_TRANSARC.csv` (read by `generate_tables._load_csv` lines 339-343) confirms `reports/` is the destination and `DictReader`-compatible header row is expected downstream. |
| SAD-SAM sentence-level + component-level F1 as standalone functions | No dedicated helper exists; build inline from set-transform + `calc_metrics` using the grouping idiom in `compute_emr`/`compute_hus`. Do NOT borrow `_compute_component_f1` (sad-code/file-based). |

---

## Metadata

**Analog search scope:** `src/lib/`, `src/bias/`, `src/paper/`, `src/transarc/` (full `src/` tree, 14 .py files)
**Files scanned:** 4 read in full/targeted (`transarc_error_analysis.py`, `new_metrics_analysis.py`, `generate_tables.py`, `evaluation_critique.py`); grep across all of `src/` for `argparse`, `csv.writer`, `DictWriter`.
**Pattern extraction date:** 2026-05-30
