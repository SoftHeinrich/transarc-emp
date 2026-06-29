#!/usr/bin/env python3
"""Guard: the paper's table/gold_concentration.{tex,csv} must equal the freshly
regenerated OUT-02 artifacts (reports/out02_concentration.{tex,csv}), byte for byte.

Both are paper-ready and copied verbatim into the paper: the .tex (project aliases +
thousands separators) and the machine-readable .csv companion (full project names).
This regenerates from the engine and fails loudly if either committed file has
drifted -- catching a rerun-without-recopy or a hand-edit.

    python3 check_paper_table.py                      # auto-locate the table dir
    PAPER_TABLE_DIR=/path/to/alinker-paper/table python3 check_paper_table.py
    python3 check_paper_table.py /path/to/alinker-paper/table

Exit 0 = in sync; exit 1 = drift (prints a unified diff); exit 2 = table dir not found.
"""
import difflib
import os
import sys
from pathlib import Path

import motivation as mot

HERE = Path(__file__).resolve().parent
# (regenerated artifact, paper filename)
PAIRS = [
    (mot.REPORTS / "out02_concentration.tex", "gold_concentration.tex"),
    (mot.REPORTS / "out02_concentration.csv", "gold_concentration.csv"),
]


def _locate_paper_table_dir():
    candidates = [
        sys.argv[1] if len(sys.argv) > 1 else None,
        os.environ.get("PAPER_TABLE_DIR"),
        # sibling repo layout: .../transarc-emp/mini-inequality -> .../alinker-paper
        HERE.parent.parent / "alinker-paper" / "table",
        # mono symlink lens, if present
        HERE.parent.parent / "mono" / "working" / "table",
    ]
    for c in candidates:
        if c and Path(c).is_dir():
            return Path(c)
    return None


def main():
    table_dir = _locate_paper_table_dir()
    if table_dir is None:
        print("ERROR: could not locate the paper table dir (.../alinker-paper/table).")
        print("Pass it as an argument or set PAPER_TABLE_DIR=...")
        return 2

    mot.write_out02_concentration()  # regenerate the canonical artifacts

    drift = False
    for generated, paper_name in PAIRS:
        paper = table_dir / paper_name
        if not paper.is_file():
            print(f"DRIFT: missing {paper}")
            drift = True
            continue
        g, c = generated.read_text(), paper.read_text()
        if g == c:
            print(f"IN SYNC: {paper.name} == {generated.name} (byte-identical).")
            continue
        drift = True
        print(f"\nDRIFT: {paper} differs from regenerated {generated}.")
        print(f"  cp {generated} {paper}")
        print("--- unified diff (paper <- generated) ---")
        sys.stdout.writelines(difflib.unified_diff(
            c.splitlines(keepends=True), g.splitlines(keepends=True),
            fromfile=str(paper), tofile=str(generated)))
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
