#!/usr/bin/env python3
"""Build the S21 (canonical Full = s_linker21) aalinker dump for RQ1/RQ2.

Self-contained, stdlib only. Reads the S21 gpt-5.4 neutral extracts
(agent-linker/results/v2.6.6_extracts_s21) and writes a NEW `gpt-5.4_s21` config
slot under the sota recovered-links tree:

    <ardoco-home>/sota/recovered-links/model-doc/aalinker/gpt-5.4_s21/<run>/<proj>.csv
    <ardoco-home>/sota/recovered-links/doc-code/aalinker-composed/gpt-5.4_s21/<run>/<proj>.csv

composing model-doc -> code via the prebuilt ArCoTL bridge
(model-code/arcotl/<proj>.csv). The existing `gpt-5.4_full` (s20_union) slot is left
untouched, so rq12.py can score S21 and s20_union side by side.

This is the version-controlled companion to sota/recovered-links/build_unified.py
(that tree is not a git repo). The four helpers below (sha256/write_norm/write_raw/f1)
are copied verbatim from build_unified.py so the dump is byte-identical; gold and bridge
are read from the already-built sota dump rather than rebuilt from raw sources.

    python3 mini-src/build_s21_dump.py
"""
import csv, hashlib, json, os
from pathlib import Path

_HERE = Path(__file__).resolve().parent              # .../transarc-emp/mini-src
_ARDOCO_HOME = _HERE.parents[1]                       # .../ardoco-home
ROOT = os.environ.get("SOTA_LINKS", str(_ARDOCO_HOME / "sota/recovered-links"))
EXTRACTS_S21 = os.environ.get(
    "EXTRACTS_S21", str(_ARDOCO_HOME / "agent-linker/results/v2.6.6_extracts_s21"))

PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]
RUNS = ["run1", "run2", "run3"]
BE_DIR, BE_TAG = "gpt", "gpt-5.4"
CONFIG = "gpt-5.4_s21"


# ---- helpers (verbatim from sota/recovered-links/build_unified.py) ----------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def write_norm(path, rows, header=("sentence_id", "target_id")):
    """Write deduped, sorted normalized links."""
    uniq = sorted(set(rows), key=lambda t: (str(t[0]), str(t[1])))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(uniq)
    return len(uniq)


def write_raw(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def f1(pred, gold):
    pred, gold = set(pred), set(gold)
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    rec = tp / len(gold) if gold else 0.0
    fm = 2 * p * rec / (p + rec) if (p + rec) else 0.0
    return p, rec, fm, tp, len(pred), len(gold)


def write_manifest(path, rows):
    cols = ["task", "system", "config", "backend", "knowledge", "run", "project",
            "n_links", "P", "R", "F1", "src", "sha"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---- inputs read from the already-built sota dump ---------------------------
def load_gold():
    """{project: set((int sentence, component_id))} from model-doc/gold."""
    gold = {}
    for proj in PROJECTS:
        rows = set()
        with open(f"{ROOT}/model-doc/gold/{proj}.csv") as f:
            for r in csv.DictReader(f):
                rows.add((int(r["sentence_id"]), r["target_id"]))
        gold[proj] = rows
    return gold


def load_bridge():
    """{project: {component_id: [code_paths]}} from model-code/arcotl."""
    bridge = {}
    for proj in PROJECTS:
        b = {}
        with open(f"{ROOT}/model-code/arcotl/{proj}.csv") as f:
            for r in csv.DictReader(f):
                b.setdefault(r["source_id"], []).append(r["target_id"])
        bridge[proj] = b
    return bridge


def build_s21(md_gold, arcotl_bridge):
    md_man, dc_man = [], []
    for run in RUNS:
        for proj in PROJECTS:
            jpath = os.path.join(EXTRACTS_S21, BE_DIR, run, f"{proj}.json")
            if not os.path.exists(jpath):
                print(f"  MISSING {run}/{proj}: {jpath}")
                continue
            d = json.load(open(jpath))
            links = d["final"]["links"]

            # --- model-doc (native sentence -> component) ---
            md_pairs = [(int(l["s"]), l["c"]) for l in links]
            base = f"{ROOT}/model-doc/aalinker/{CONFIG}/{run}/{proj}"
            n_md = write_norm(f"{base}.csv", md_pairs)
            write_raw(f"{base}.raw.csv",
                      ["sentence", "component_id", "component_name", "confidence", "source"],
                      [[l["s"], l["c"], l.get("component_name", ""),
                        l.get("confidence", ""), l.get("source", "")] for l in links])
            P, R, F, tp, npred, ngold = f1(md_pairs, md_gold[proj])
            md_man.append(dict(task="model-doc", system="aalinker", config=CONFIG,
                               backend=BE_TAG, knowledge="full", run=run, project=proj,
                               n_links=n_md, P=f"{P:.4f}", R=f"{R:.4f}", F1=f"{F:.4f}",
                               src=os.path.relpath(jpath, _ARDOCO_HOME), sha=sha256(jpath)))

            # --- doc-code (composed: ours model-doc o ArCoTL model-code) ---
            bridge = arcotl_bridge[proj]
            dc_pairs, raw_rows = [], []
            for s, cid in md_pairs:
                for code in bridge.get(cid, []):
                    dc_pairs.append((s, code))
                    raw_rows.append([s, cid, code])
            cbase = f"{ROOT}/doc-code/aalinker-composed/{CONFIG}/{run}/{proj}"
            n_dc = write_norm(f"{cbase}.csv", dc_pairs)
            write_raw(f"{cbase}.raw.csv", ["sentence_id", "via_component", "target_id"], raw_rows)
            dc_man.append(dict(task="doc-code", system="aalinker-composed", config=CONFIG,
                               backend=BE_TAG, knowledge="full", run=run, project=proj,
                               n_links=n_dc, P="", R="", F1="",
                               src=f"model-doc/aalinker/{CONFIG}/{run}/{proj}.csv o model-code/arcotl/{proj}.csv",
                               sha=""))
    return md_man, dc_man


def main():
    md_gold = load_gold()
    arcotl_bridge = load_bridge()
    md_man, dc_man = build_s21(md_gold, arcotl_bridge)

    write_manifest(f"{ROOT}/model-doc/aalinker/_manifest_s21.csv", md_man)
    write_manifest(f"{ROOT}/doc-code/aalinker-composed/_manifest_s21.csv", dc_man)

    fs = [float(r["F1"]) for r in md_man]
    print(f"\n== S21 model-doc F1 vs gold (integrity) ==")
    print(f"  {CONFIG:14s} macro-F1 = {sum(fs)/len(fs):.4f}  ({len(fs)} cells)")
    print(f"wrote {len(md_man)} model-doc + {len(dc_man)} doc-code(composed) S21 entries into {ROOT}.")


if __name__ == "__main__":
    main()
