#!/usr/bin/env python3
"""Reproducibility gate for the component suite (CMP-06).

ONE standalone command runs BOTH guarantees and returns a pass/fail exit code,
modeled on ``mini-src/check.py`` (per-(system/project) loop, ``TOL = 1e-9``,
``SKIP``/``OK``/``FAIL`` lines, a ``failures`` counter, ``sys.exit(1)`` on any
mismatch):

PART 1 — EQUIVALENCE ORACLE (D-06, sad-code only).
    For every PRESENT system in ``component_suite.SYSTEMS`` and every project,
    assert ``component_suite.component_suite(gold_sc, result_sc)['macro']``
    equals the INDEPENDENT macro reference
    ``rq2_trivial_baselines.per_component_macro_f1(<file gold>, <file result>,
    file_to_comps)`` to within ``TOL``. sad-code only: ``per_component_macro_f1``
    is the sole independent macro reference (a sad-model check would reuse the
    suite math and be circular). swattr/transarc is in-repo and ALWAYS asserted;
    absent external systems skip-with-notice.

    Note: ``component_suite._code_inputs(proj)`` returns ONLY ``(gold_sc, collapse)``
    — it does NOT hand back the file-level ``enrolled`` gold or ``file_to_comps``
    that the oracle's ``per_component_macro_f1`` needs. So this check REBUILDS
    those itself, replicating ``_code_inputs``' internals EXACTLY (same loaders,
    same mapped-only construction). The 1e-9 assertion catches any drift between
    the two reconstructions.

PART 2 — DETERMINISM CHECK (D-07/D-09, both levels, present systems).
    Regenerate the suite into a TEMP directory (``tempfile.mkdtemp``) by
    temporarily pointing ``component_suite.REPORTS`` at the temp dir, then diff
    the regenerated CSV against the committed ``reports/COMPONENT_SUITE_{level}.csv``
    for BOTH levels — comparing ONLY rows whose system is present now (absent
    systems skip-with-notice, D-09). ``component_suite.REPORTS`` is restored and
    NOTHING is written into the real ``reports/`` directory.

No new F1 math is added: every score flows through the imported suite/oracle
functions (which in turn call the single ``calc_metrics`` primitive).

    python3 src/bias/check_component_suite.py
"""

import csv
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent              # src/bias
sys.path.insert(0, str(HERE.parent / "lib"))        # src/lib (shared loaders)
sys.path.insert(0, str(HERE))                        # src/bias (suite + oracle)

import component_suite                                # noqa: E402
import rq2_trivial_baselines                          # noqa: E402
from transarc_error_analysis import (                 # noqa: E402
    PROJECTS,
    load_code_model_files, load_model_element_names,
    enroll_gold_standard, load_gs_sam_code_raw, load_gs_sad_code_enrolled,
)

TOL = 1e-9
ALWAYS_PRESENT = "swattr_transarc"   # in-repo system; never legitimately absent
LEVELS = ("sad-model", "sad-code")


# ── File-level oracle inputs (re-derived; _code_inputs does NOT expose these) ──

def _oracle_file_inputs(proj):
    """Rebuild (enrolled file-level gold, file_to_comps) EXACTLY like
    ``component_suite._code_inputs``' internals, so the suite-macro side and the
    ``per_component_macro_f1`` side share one mapped-only component universe.
    """
    code_model = load_code_model_files(proj)
    names = load_model_element_names(proj)
    sam_enrolled = enroll_gold_standard(load_gs_sam_code_raw(proj), code_model)
    file_to_comps = defaultdict(set)
    for ae, fp in sam_enrolled:
        name = names.get(ae, ae)
        if name.startswith("Interface:"):   # D-12: mirror _code_inputs' interface drop
            continue
        file_to_comps[fp].add(name)
    enrolled = load_gs_sad_code_enrolled(proj, code_model)   # set[(sentence, file)]
    return enrolled, file_to_comps


# ── Committed-vs-regen CSV row reader ─────────────────────────────────────────

def _read_rows(path):
    """Return {(project, system_label): full_row_list} keyed for present-scope diff."""
    rows = {}
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)                  # header
        for row in reader:
            if not row:
                continue
            rows[(row[0], row[1])] = row     # (project, system) -> row
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1 — EQUIVALENCE ORACLE (sad-code only)
# ═══════════════════════════════════════════════════════════════════════════════

def run_oracle():
    failures = 0
    print("== PART 1: equivalence oracle (suite-macro == per_component_macro_f1, "
          "sad-code, TOL=1e-9) ==")
    for proj in PROJECTS:
        # _code_inputs gives the collapsed gold + the collapse(); the oracle's
        # file-level inputs are rebuilt separately (see module docstring).
        gold_sc, collapse = component_suite._code_inputs(proj)
        enrolled, file_to_comps = _oracle_file_inputs(proj)

        for key, label, _mloader, cloader in component_suite.SYSTEMS:
            links = cloader(proj)            # file-level result: set[(sentence, file)]
            if not links:
                if key == ALWAYS_PRESENT:
                    failures += 1
                    print(f"FAIL  oracle  {label:16} {proj:14} "
                          f"(always-present system returned no sad-code links)")
                else:
                    print(f"SKIP  oracle  {label:16} {proj:14} "
                          f"(absent/empty external root)")
                continue

            result_sc = collapse(links)
            suite_macro = component_suite.component_suite(gold_sc, result_sc)["macro"]
            oracle_macro = rq2_trivial_baselines.per_component_macro_f1(
                enrolled, links, file_to_comps)

            if abs(suite_macro - oracle_macro) <= TOL:
                print(f"OK    oracle  {label:16} {proj:14} "
                      f"macro={suite_macro:.6f}  |delta|={abs(suite_macro - oracle_macro):.2e}")
            else:
                failures += 1
                print(f"FAIL  oracle  {label:16} {proj:14} "
                      f"suite={suite_macro!r} oracle={oracle_macro!r} "
                      f"|delta|={abs(suite_macro - oracle_macro):.3e}")
    return failures


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2 — DETERMINISM CHECK (both levels, present-system scope)
# ═══════════════════════════════════════════════════════════════════════════════

def run_determinism():
    failures = 0
    print("\n== PART 2: determinism check (regenerate to temp; diff committed CSVs, "
          "present-system rows) ==")
    committed_reports = component_suite.REPORTS          # the real reports/ dir
    tmpdir = Path(tempfile.mkdtemp(prefix="component_suite_det_"))
    saved_reports = component_suite.REPORTS
    try:
        # Regenerate into the temp dir ONLY (never the committed reports/).
        component_suite.REPORTS = tmpdir
        for level in LEVELS:
            rows = component_suite.run_level(level, list(component_suite.PROJECTS))
            avg = component_suite.averages(rows)
            component_suite.write_csv(level, rows, avg)

            committed = _read_rows(committed_reports / f"COMPONENT_SUITE_{level}.csv")
            regen = _read_rows(tmpdir / f"COMPONENT_SUITE_{level}.csv")
            present_labels = {label for (_p, label) in regen}

            for (proj, label) in sorted(committed):
                if label not in present_labels:
                    print(f"SKIP  det     {level:9} {label:16} {proj:14} "
                          f"(absent system; not regenerated)")
                    continue
                key = (proj, label)
                if key not in regen:
                    failures += 1
                    print(f"FAIL  det     {level:9} {label:16} {proj:14} "
                          f"(present system but row missing in regen)")
                elif committed[key] == regen[key]:
                    print(f"OK    det     {level:9} {label:16} {proj:14}")
                else:
                    failures += 1
                    print(f"FAIL  det     {level:9} {label:16} {proj:14} "
                          f"committed={committed[key]} regen={regen[key]}")
    finally:
        component_suite.REPORTS = saved_reports          # restore (never leave temp)
        shutil.rmtree(tmpdir, ignore_errors=True)
    return failures


def main():
    failures = run_oracle()
    failures += run_determinism()

    print()
    if failures:
        print(f"FAILED: {failures} mismatch(es)")
        sys.exit(1)
    print("PASS: equivalence oracle (suite-macro == per_component_macro_f1 to 1e-9) "
          "and determinism check (committed CSVs regenerate for present systems) "
          "both hold.")


if __name__ == "__main__":
    main()
