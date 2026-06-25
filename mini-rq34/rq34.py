#!/usr/bin/env python3
"""mini-rq34 — paper RQ3 (validator contribution) + RQ4 (per-module ablation)
metrics, computed from the agent-linker running results.

Self-contained, stdlib-only. Reads the canonical N=3 ``s_linker20_union`` sweep
(``v2.6.5_s20union_sonnet`` -> Claude / paper main body; ``v2.6.5_s20union/gpt``
-> GPT-5.4 / appendix), reconstructs each validator's per-link decisions and
each linker's provenance from the ``phase_cache`` pickles (``layer3``,
``layer4``, ``final``), scores every link against the SAD-SAM gold standard, and
writes:

    reports/<backend>/<project>/rq3.csv         (4 variant rows)
    reports/<backend>/<project>/rq3_audit.csv   (2 validator rows)
    reports/<backend>/<project>/rq4.csv         (2 linker rows)
    reports/<backend>/<project>/rq4_upset.csv   (3 overlap-cell rows)
    reports/<backend>/runs_summary.csv          (all 3 runs, canonical marked)
    reports/rq3_validators.csv  reports/rq3_variants.csv   (aggregated, both backends)
    reports/rq4_linkers.csv     reports/rq4_variants.csv   (aggregated, both backends)

CSV only — no TeX, no markdown. Top-level aggregates sum counts (and average
ΔF1) over the 5 projects of the single canonical (median-macro-F1) run.

Method (faithful to alinker-paper working/sections/results.tex):
  * RQ3 measures validator contribution from the full pipeline's *logged
    decisions*, not by re-running with a validator removed. The "validator
    removed" link set is the final set with that validator's rejected links
    added back; the macro-F1 drop is the contribution.
  * RQ4 decomposes each linker by *set overlap* (only_E / both / only_C). The
    leave-one-out delta-F1 is also emitted but is the contaminated comparison
    (the surviving linker recovers some removed hits), so overlap is headline.

Conventions (inherited from the mini-* studies):
  * stdlib only; no cross-module imports — the gold loader is inlined and the
    agent-linker dataclasses are *vendored* (see ``_alinker_types.py``), not
    imported from the approach package.
  * Roots derive from this file's location; override via ``$TRANSARC_BENCHMARK``,
    ``$RQ34_CLAUDE_SLOT``, ``$RQ34_OPENAI_SLOT``.
"""

from __future__ import annotations

import argparse
import csv
import importlib.abc
import importlib.machinery
import json
import os
import statistics
import sys
import types
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# --------------------------------------------------------------------------- #
# Roots (derived from file location; env-overridable).
# --------------------------------------------------------------------------- #
_HERE = Path(__file__).resolve().parent           # .../transarc-emp/mini-rq34
_ARDOCO_HOME = _HERE.parents[1]                    # .../ardoco-home

BENCHMARK = Path(os.environ.get(
    "TRANSARC_BENCHMARK",
    _ARDOCO_HOME / "ardoco/core/tests-base/src/main/resources/benchmark",
))

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]
RUNS = ["run1", "run2", "run3"]
VARIANT = "s_linker20_union"

# backend -> (results slot, phase_cache backend subdir, paper role)
SLOTS: Dict[str, Path] = {
    "claude": Path(os.environ.get(
        "RQ34_CLAUDE_SLOT", _ARDOCO_HOME / "agent-linker/results/v2.6.5_s20union_sonnet")),
    "openai": Path(os.environ.get(
        "RQ34_OPENAI_SLOT", _ARDOCO_HOME / "agent-linker/results/v2.6.5_s20union/gpt")),
}
PCACHE_BACKEND = {"claude": "claude", "openai": "openai"}

GS_SAD_SAM = {
    "mediastore":    "mediastore/goldstandards/goldstandard_sad_2016-sam_2016.csv",
    "teastore":      "teastore/goldstandards/goldstandard_sad_2020-sam_2020.csv",
    "teammates":     "teammates/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "bigbluebutton": "bigbluebutton/goldstandards/goldstandard_sad_2021-sam_2021.csv",
    "jabref":        "jabref/goldstandards/goldstandard_sad_2021-sam_2021.csv",
}

LinkKey = Tuple[int, str]  # (sentence_number, component_id)


# --------------------------------------------------------------------------- #
# Unpickling support: register the vendored agent-linker dataclasses under their
# original module path so pickle finds them, with a permissive fallback for any
# other llm_sad_sam.* symbol (only the knowledge layer, which RQ3/RQ4 skip).
# --------------------------------------------------------------------------- #
import _alinker_types  # noqa: E402  (vendored copy; see module docstring)


class _Stub:
    def __setstate__(self, state):
        if isinstance(state, dict):
            self.__dict__.update(state)


class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        cls = type(name, (_Stub,), {"__module__": self.__name__})
        setattr(self, name, cls)
        return cls


class _StubLoader(importlib.abc.Loader):
    def create_module(self, spec):
        mod = _StubModule(spec.name)
        mod.__path__ = []
        return mod

    def exec_module(self, module):
        pass


class _StubFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "llm_sad_sam" or fullname.startswith("llm_sad_sam."):
            return importlib.machinery.ModuleSpec(fullname, _StubLoader(), is_package=True)
        return None


def install_unpickler() -> None:
    # Real, vendored core types take precedence (this is what layer3/4/final use).
    sys.modules.setdefault("llm_sad_sam.core.data_types_v2", _alinker_types)
    if not any(isinstance(f, _StubFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _StubFinder())


# --------------------------------------------------------------------------- #
# Gold standard (inlined; SAD-SAM grain).
# --------------------------------------------------------------------------- #
def load_gold(project: str) -> Set[LinkKey]:
    """SAD-SAM gold as {(sentence_number:int, component_id:str)}."""
    gold: Set[LinkKey] = set()
    with (BENCHMARK / GS_SAD_SAM[project]).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gold.add((int(row["sentence"]), row["modelElementID"]))
    return gold


# --------------------------------------------------------------------------- #
# Metric primitives.
# --------------------------------------------------------------------------- #
import pickle  # noqa: E402  (after the unpickler classes are defined)


def prf(pred: Set[LinkKey], gold: Set[LinkKey]) -> Tuple[int, int, int, float]:
    tp = len(pred & gold)
    fp = len(pred - gold)
    fn = len(gold - pred)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return tp, fp, fn, f1


def _key(obj) -> LinkKey:
    return (int(obj.sentence_number), str(obj.component_id))


def _validated_sets(candidates: List, validated: List) -> Tuple[Set[LinkKey], Set[LinkKey]]:
    """(kept, killed) for one linker. ``kept`` = the validator-approved output
    actually emitted (authoritative ``validated`` list); ``killed`` = proposed
    candidates the validator rejected."""
    kept = {_key(x) for x in validated}
    killed = {_key(x) for x in candidates} - kept
    return kept, killed


# --------------------------------------------------------------------------- #
# Per-(backend, run, project) cell.
# --------------------------------------------------------------------------- #
class Cell:
    def __init__(self, project: str):
        self.project = project
        self.gold: Set[LinkKey] = set()
        self.final: Set[LinkKey] = set()
        self.ent_kept: Set[LinkKey] = set()
        self.ent_killed: Set[LinkKey] = set()
        self.cor_kept: Set[LinkKey] = set()
        self.cor_killed: Set[LinkKey] = set()
        self.warnings: List[str] = []


def _phase_dir(slot: Path, run: str, backend: str, project: str) -> Path:
    return slot / run / "phase_cache" / VARIANT / PCACHE_BACKEND[backend] / project


def compute_cell(slot: Path, run: str, backend: str, project: str) -> Cell:
    pdir = _phase_dir(slot, run, backend, project)
    with (pdir / "layer3.pkl").open("rb") as f:
        l3 = pickle.load(f)
    with (pdir / "layer4.pkl").open("rb") as f:
        l4 = pickle.load(f)
    with (pdir / "final.pkl").open("rb") as f:
        fin = pickle.load(f)

    cell = Cell(project)
    cell.gold = load_gold(project)
    cell.final = {_key(x) for x in fin["final"]}
    cell.ent_kept, cell.ent_killed = _validated_sets(l3["candidates"], l3["validated"])
    cell.cor_kept, cell.cor_killed = _validated_sets(l4["coref_raw"], l4["coref_validated"])

    union = cell.ent_kept | cell.cor_kept
    if union != cell.final:
        cell.warnings.append(
            f"final({len(cell.final)}) != entity_kept|coref_kept({len(union)}); "
            f"final-only={len(cell.final - union)} union-only={len(union - cell.final)}"
        )
    return cell


# --------------------------------------------------------------------------- #
# Derived rows.
# --------------------------------------------------------------------------- #
def rq3_variant_sets(cell: Cell) -> Dict[str, Set[LinkKey]]:
    return {
        "Full": cell.final,
        "NoEntityValid": cell.final | cell.ent_killed,
        "NoCitation": cell.final | cell.cor_killed,
        "NoValidator": cell.final | cell.ent_killed | cell.cor_killed,
    }


def rq3_audit(cell: Cell) -> Dict[str, Dict[str, int]]:
    def a(killed, kept):
        return {
            "killed_gold": len(killed & cell.gold),
            "killed_spurious": len(killed - cell.gold),
            "kept_gold": len(kept & cell.gold),
            "kept_spurious": len(kept - cell.gold),
        }
    return {"entity": a(cell.ent_killed, cell.ent_kept),
            "coref": a(cell.cor_killed, cell.cor_kept)}


def rq4_linkers(cell: Cell) -> Dict[str, Dict[str, float]]:
    E, C, G = cell.ent_kept, cell.cor_kept, cell.gold
    _, _, _, f1_full = prf(E | C, G)
    _, _, _, f1_c_only = prf(C, G)  # entity removed
    _, _, _, f1_e_only = prf(E, G)  # coref removed
    return {
        "Entity": {"tps_caught": len(E & G), "unique_tps": len((E & G) - C),
                   "fps": len(E - G), "delta_f1_if_removed": f1_full - f1_c_only},
        "Coref": {"tps_caught": len(C & G), "unique_tps": len((C & G) - E),
                  "fps": len(C - G), "delta_f1_if_removed": f1_full - f1_e_only},
    }


def rq4_upset(cell: Cell) -> Dict[str, int]:
    E, C, G = cell.ent_kept, cell.cor_kept, cell.gold
    return {"only_E": len((E & G) - C), "both": len(E & C & G), "only_C": len((C & G) - E)}


# --------------------------------------------------------------------------- #
# Run selection + I/O.
# --------------------------------------------------------------------------- #
def macro_f1(cells: Dict[str, Cell]) -> float:
    f1s = [prf(cells[p].final, cells[p].gold)[3] for p in PROJECTS if p in cells]
    return statistics.fmean(f1s) if f1s else 0.0


def pick_canonical(per_run: Dict[str, Dict[str, Cell]]) -> str:
    scored = sorted((macro_f1(cells), run) for run, cells in per_run.items())
    return scored[len(scored) // 2][1]


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def read_ablation_full(slot: Path, run: str, project: str) -> Optional[Dict]:
    files = sorted((slot / run / project).glob("ablation_*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8")).get(project, {}).get(VARIANT)


# --------------------------------------------------------------------------- #
# Backend aggregate (over the canonical run's 5 projects).
# --------------------------------------------------------------------------- #
class BackendAgg:
    def __init__(self, backend: str, canonical: str):
        self.backend = backend
        self.canonical = canonical
        self.macro_full = 0.0
        self.macro_no_entity = 0.0
        self.macro_no_coref = 0.0
        self.macro_no_all = 0.0
        self.macro_entity_only = 0.0
        self.macro_coref_only = 0.0
        self.audit = {v: {"killed_gold": 0, "killed_spurious": 0, "kept_gold": 0, "kept_spurious": 0}
                      for v in ("entity", "coref")}
        self.linkers = {l: {"tps_caught": 0, "unique_tps": 0, "fps": 0, "delta_f1_sum": 0.0, "n": 0}
                        for l in ("Entity", "Coref")}
        self.upset = {"only_E": 0, "both": 0, "only_C": 0}

    @property
    def dF1_no_entity(self):  # contribution of the entity validator
        return self.macro_full - self.macro_no_entity

    @property
    def dF1_no_coref(self):
        return self.macro_full - self.macro_no_coref

    @property
    def dF1_no_all(self):
        return self.macro_full - self.macro_no_all


def process_backend(backend: str, csv_root: Path, run_override: Optional[str],
                    validate: bool) -> Tuple[BackendAgg, List[str], int, int, int]:
    slot = SLOTS[backend]
    per_run: Dict[str, Dict[str, Cell]] = {}
    for run in RUNS:
        cells = {}
        for project in PROJECTS:
            if (_phase_dir(slot, run, backend, project) / "final.pkl").exists():
                cells[project] = compute_cell(slot, run, backend, project)
        if cells:
            per_run[run] = cells
    if not per_run:
        raise SystemExit(f"[{backend}] no runs found under {slot}")

    if run_override is not None and run_override not in per_run:
        raise SystemExit(f"[{backend}] --run {run_override} has no loadable cells under {slot}")
    canonical = run_override or pick_canonical(per_run)

    # runs_summary.csv
    summary = []
    for run in RUNS:
        if run not in per_run:
            continue
        for project in PROJECTS:
            if project not in per_run[run]:
                continue
            tp, fp, fn, f1 = prf(per_run[run][project].final, per_run[run][project].gold)
            summary.append({"run": run, "project": project, "tp": tp, "fp": fp, "fn": fn,
                            "f1": f"{f1:.6f}", "canonical": "yes" if run == canonical else ""})
        summary.append({"run": run, "project": "MACRO", "tp": "", "fp": "", "fn": "",
                        "f1": f"{macro_f1(per_run[run]):.6f}",
                        "canonical": "yes" if run == canonical else ""})
    _write_csv(csv_root / backend / "runs_summary.csv",
               ["run", "project", "tp", "fp", "fn", "f1", "canonical"], summary)

    agg = BackendAgg(backend, canonical)
    f1_full_list, f1_ne_list, f1_nc_list, f1_na_list = [], [], [], []
    f1_e_only_list, f1_c_only_list = [], []
    warns: List[str] = []
    mismatch = 0
    checked = 0
    skipped = 0

    for project in PROJECTS:
        if project not in per_run[canonical]:
            continue
        cell = per_run[canonical][project]
        warns += [f"  [{backend}/{canonical}/{project}] {w}" for w in cell.warnings]

        # ---- per-project drill-down CSVs ----
        base = csv_root / backend / project
        variants = rq3_variant_sets(cell)
        v_f1 = {}
        rq3_rows = []
        for vname in ("Full", "NoEntityValid", "NoCitation", "NoValidator"):
            tp, fp, fn, f1 = prf(variants[vname], cell.gold)
            v_f1[vname] = f1
            rq3_rows.append({"variant": vname, "project": project, "tp": tp, "fp": fp,
                             "fn": fn, "f1": f"{f1:.6f}"})
        _write_csv(base / "rq3.csv", ["variant", "project", "tp", "fp", "fn", "f1"], rq3_rows)

        audit = rq3_audit(cell)
        _write_csv(base / "rq3_audit.csv",
                   ["validator", "killed_gold", "killed_spurious", "kept_gold", "kept_spurious"],
                   [{"validator": v, **audit[v]} for v in ("entity", "coref")])

        linkers = rq4_linkers(cell)
        _write_csv(base / "rq4.csv",
                   ["linker", "tps_caught", "unique_tps", "fps", "delta_f1_if_removed"],
                   [{"linker": l, "tps_caught": linkers[l]["tps_caught"],
                     "unique_tps": linkers[l]["unique_tps"], "fps": linkers[l]["fps"],
                     "delta_f1_if_removed": f"{linkers[l]['delta_f1_if_removed']:.6f}"}
                    for l in ("Entity", "Coref")])

        upset = rq4_upset(cell)
        _write_csv(base / "rq4_upset.csv", ["cell", "count"],
                   [{"cell": c, "count": upset[c]} for c in ("only_E", "both", "only_C")])

        # ---- accumulate aggregate ----
        f1_full_list.append(v_f1["Full"])
        f1_ne_list.append(v_f1["NoEntityValid"])
        f1_nc_list.append(v_f1["NoCitation"])
        f1_na_list.append(v_f1["NoValidator"])
        _, _, _, f1e = prf(cell.ent_kept, cell.gold)
        _, _, _, f1c = prf(cell.cor_kept, cell.gold)
        f1_e_only_list.append(f1e)
        f1_c_only_list.append(f1c)
        for v in ("entity", "coref"):
            for k in agg.audit[v]:
                agg.audit[v][k] += audit[v][k]
        for l in ("Entity", "Coref"):
            agg.linkers[l]["tps_caught"] += linkers[l]["tps_caught"]
            agg.linkers[l]["unique_tps"] += linkers[l]["unique_tps"]
            agg.linkers[l]["fps"] += linkers[l]["fps"]
            agg.linkers[l]["delta_f1_sum"] += linkers[l]["delta_f1_if_removed"]
            agg.linkers[l]["n"] += 1
        for c in agg.upset:
            agg.upset[c] += upset[c]

        if validate:
            ref = read_ablation_full(slot, canonical, project)
            if ref:
                checked += 1
                tp, fp, fn, _ = prf(cell.final, cell.gold)
                if (tp, fp, fn) != (int(ref["tp"]), int(ref["fp"]), int(ref["fn"])):
                    mismatch += 1
                    warns.append(f"  [{backend}/{canonical}/{project}] FULL MISMATCH vs "
                                 f"ablation.json: {tp}/{fp}/{fn} != "
                                 f"{ref['tp']}/{ref['fp']}/{ref['fn']}")
            else:
                skipped += 1
                warns.append(f"  [{backend}/{canonical}/{project}] no ablation_*.json reference "
                             f"-- Full variant NOT cross-checked")

    agg.macro_full = statistics.fmean(f1_full_list)
    agg.macro_no_entity = statistics.fmean(f1_ne_list)
    agg.macro_no_coref = statistics.fmean(f1_nc_list)
    agg.macro_no_all = statistics.fmean(f1_na_list)
    agg.macro_entity_only = statistics.fmean(f1_e_only_list)
    agg.macro_coref_only = statistics.fmean(f1_c_only_list)
    return agg, warns, mismatch, checked, skipped


# --------------------------------------------------------------------------- #
# Aggregated report writers.
# --------------------------------------------------------------------------- #
def write_aggregates(csv_root: Path, aggs: Dict[str, BackendAgg]) -> None:
    # rq3_validators.csv
    rows = []
    for backend, agg in aggs.items():
        for v, dF1 in (("entity", agg.dF1_no_entity), ("coref", agg.dF1_no_coref)):
            a = agg.audit[v]
            rows.append({"backend": backend, "validator": v, "canonical_run": agg.canonical,
                         **a, "delta_f1_if_removed": f"{dF1:+.6f}"})
        comb = {k: agg.audit["entity"][k] + agg.audit["coref"][k] for k in agg.audit["entity"]}
        rows.append({"backend": backend, "validator": "all_combined", "canonical_run": agg.canonical,
                     **comb, "delta_f1_if_removed": f"{agg.dF1_no_all:+.6f}"})
    _write_csv(csv_root / "rq3_validators.csv",
               ["backend", "validator", "canonical_run", "killed_gold", "killed_spurious",
                "kept_gold", "kept_spurious", "delta_f1_if_removed"], rows)

    # rq4_linkers.csv
    rows = []
    for backend, agg in aggs.items():
        for l in ("Entity", "Coref"):
            e = agg.linkers[l]
            rows.append({"backend": backend, "linker": l, "canonical_run": agg.canonical,
                         "tps_caught": e["tps_caught"], "unique_tps": e["unique_tps"],
                         "fps": e["fps"],
                         "delta_f1_if_removed": f"{e['delta_f1_sum'] / max(e['n'], 1):+.6f}"})
        rows.append({"backend": backend, "linker": "overlap(only_E/both/only_C)",
                     "canonical_run": agg.canonical,
                     "tps_caught": agg.upset["only_E"], "unique_tps": agg.upset["both"],
                     "fps": agg.upset["only_C"], "delta_f1_if_removed": ""})
    _write_csv(csv_root / "rq4_linkers.csv",
               ["backend", "linker", "canonical_run", "tps_caught", "unique_tps", "fps",
                "delta_f1_if_removed"], rows)

    # rq3_variants.csv -- macro-F1 per RQ3 variant (the "validator removed" sets).
    rows = []
    for backend, agg in aggs.items():
        for variant, macro in (("Full", agg.macro_full),
                               ("NoEntityValid", agg.macro_no_entity),
                               ("NoCitation", agg.macro_no_coref),
                               ("NoValidator", agg.macro_no_all)):
            rows.append({"backend": backend, "variant": variant, "canonical_run": agg.canonical,
                         "macro_f1": f"{macro:.6f}",
                         "delta_f1_vs_full": f"{agg.macro_full - macro:+.6f}"})
    _write_csv(csv_root / "rq3_variants.csv",
               ["backend", "variant", "canonical_run", "macro_f1", "delta_f1_vs_full"], rows)

    # rq4_variants.csv -- single-linker macro-F1 (entity-only / coref-only / full).
    rows = []
    for backend, agg in aggs.items():
        for label, macro in (("entity_only", agg.macro_entity_only),
                             ("coref_only", agg.macro_coref_only),
                             ("full", agg.macro_full)):
            rows.append({"backend": backend, "linker_set": label, "canonical_run": agg.canonical,
                         "macro_f1": f"{macro:.6f}"})
    _write_csv(csv_root / "rq4_variants.csv",
               ["backend", "linker_set", "canonical_run", "macro_f1"], rows)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Compute RQ3/RQ4 paper metrics from running results.")
    ap.add_argument("--csv-root", type=Path, default=_HERE / "reports",
                    help="output root (default: mini-rq34/reports)")
    ap.add_argument("--backends", nargs="+", default=["claude", "openai"],
                    choices=["claude", "openai"])
    ap.add_argument("--run", default=None, choices=RUNS,
                    help="force a run instead of the median-macro run")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip cross-check of Full vs ablation_*.json")
    args = ap.parse_args()

    install_unpickler()
    print(f"[mini-rq34] benchmark = {BENCHMARK}")
    print(f"[mini-rq34] csv-root  = {args.csv_root}")

    aggs: Dict[str, BackendAgg] = {}
    for backend in args.backends:
        agg, warns, mismatch, checked, skipped = process_backend(
            backend, args.csv_root, args.run, validate=not args.no_validate)
        aggs[backend] = agg
        if args.no_validate:
            flag = "skipped (--no-validate)"
        elif mismatch:
            flag = f"{mismatch} MISMATCH ({checked} checked, {skipped} no-ref)"
        else:
            flag = f"OK ({checked} checked, {skipped} no-ref)"
        print(f"[mini-rq34] {backend}: canonical={agg.canonical} macro-F1={agg.macro_full:.4f} "
              f"validate={flag}")
        for w in warns:
            print(w)

    write_aggregates(args.csv_root, aggs)
    print(f"[mini-rq34] wrote per-project CSVs + rq3_validators.csv + rq3_variants.csv + "
          f"rq4_linkers.csv + rq4_variants.csv under {args.csv_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
