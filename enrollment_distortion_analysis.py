#!/usr/bin/env python3
"""
Enrollment Distortion Analysis

Quantifies how file-level enrollment of directory gold standard entries
distorts SAD-CODE evaluation metrics.

For each project, computes:
A) File-level TP/FP/FN with provenance tracing to raw gold entries
B) Metric sensitivity: how much one raw gold entry swings F1

Uses data loading infrastructure from transarc_error_analysis.py.
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

# ── Import shared infrastructure ──────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).parent))
from transarc_error_analysis import (
    BENCHMARK, RESULTS, PROJECTS,
    GS_SAD_CODE, ACM_FILES,
    normalize_path, load_code_model_files,
    load_result_sad_code, calc_metrics,
)


# ── Raw gold standard loader with provenance ─────────────────────────────────

def load_gs_sad_code_raw_with_provenance(project):
    """Load raw SAD-CODE gold standard, returning:
       - raw_entries: set of (sentenceID, raw_path) -- as written in CSV
       - is_directory: dict mapping (sentenceID, raw_path) -> bool
    """
    raw_entries = set()
    is_directory = {}
    with open(GS_SAD_CODE[project]) as f:
        for row in csv.DictReader(f):
            sid = row["sentenceID"]
            raw_path = normalize_path(row["codeID"])
            entry = (sid, raw_path)
            raw_entries.add(entry)
            is_directory[entry] = raw_path.endswith("/")
    return raw_entries, is_directory


def enroll_with_provenance(raw_entries, is_directory, code_model_files):
    """Enroll directory entries, tracking which raw entry each enrolled file came from.

    Returns:
        enrolled: set of (sentenceID, file_path) -- the full enrolled gold standard
        file_to_raw: dict mapping (sentenceID, file_path) -> (sentenceID, raw_path)
        raw_to_files: dict mapping (sentenceID, raw_path) -> set of (sentenceID, file_path)
    """
    enrolled = set()
    file_to_raw = {}  # enrolled entry -> raw entry it came from
    raw_to_files = defaultdict(set)  # raw entry -> set of enrolled entries

    for (sid, raw_path) in raw_entries:
        if raw_path.endswith("/"):
            # Directory entry: expand to all matching files
            matched = set()
            for file_path in code_model_files:
                if file_path.startswith(raw_path):
                    enrolled_entry = (sid, file_path)
                    enrolled.add(enrolled_entry)
                    file_to_raw[enrolled_entry] = (sid, raw_path)
                    matched.add(enrolled_entry)
            raw_to_files[(sid, raw_path)] = matched
        else:
            # File entry: keep as-is
            enrolled_entry = (sid, raw_path)
            enrolled.add(enrolled_entry)
            file_to_raw[enrolled_entry] = (sid, raw_path)
            raw_to_files[(sid, raw_path)] = {enrolled_entry}

    return enrolled, file_to_raw, raw_to_files


# ── Main analysis ─────────────────────────────────────────────────────────────

def main():
    print("=" * 90)
    print("ENROLLMENT DISTORTION ANALYSIS")
    print("How file-level enrollment of directory gold entries distorts SAD-CODE evaluation")
    print("=" * 90)
    print()

    # Collect summary data for final table
    summary = {}

    for proj in PROJECTS:
        print(f"\n{'#' * 90}")
        print(f"# {proj.upper()}")
        print(f"{'#' * 90}")

        code_model = load_code_model_files(proj)
        raw_entries, is_directory = load_gs_sad_code_raw_with_provenance(proj)
        enrolled, file_to_raw, raw_to_files = enroll_with_provenance(
            raw_entries, is_directory, code_model
        )
        result = load_result_sad_code(proj)

        # ── A) Basic file-level metrics ──────────────────────────────────────

        p, r, f1, tp_count, fp_count, fn_count = calc_metrics(enrolled, result)
        tp_set = enrolled & result
        fp_set = result - enrolled
        fn_set = enrolled - result

        n_raw = len(raw_entries)
        n_raw_dir = sum(1 for v in is_directory.values() if v)
        n_raw_file = n_raw - n_raw_dir
        n_enrolled = len(enrolled)
        expansion_ratio = n_enrolled / n_raw if n_raw > 0 else 0

        print(f"\n  A) File-level Metrics")
        print(f"  ─────────────────────")
        print(f"  Raw gold entries:      {n_raw}  ({n_raw_dir} directories, {n_raw_file} files)")
        print(f"  Enrolled gold entries:  {n_enrolled}  (expansion ratio: {expansion_ratio:.1f}x)")
        print(f"  Result entries:         {len(result)}")
        print(f"  TP={tp_count}  FP={fp_count}  FN={fn_count}")
        print(f"  P={p:.4f}  R={r:.4f}  F1={f1:.4f}")

        # ── A.3) TPs grouped by raw gold entry ──────────────────────────────

        # For each TP, find which raw entry it came from
        tp_from_dir = 0
        tp_from_file = 0
        tp_by_raw = defaultdict(int)  # raw entry -> count of TPs from it

        for entry in tp_set:
            raw = file_to_raw.get(entry)
            if raw is None:
                continue
            tp_by_raw[raw] += 1
            if is_directory.get(raw, False):
                tp_from_dir += 1
            else:
                tp_from_file += 1

        print(f"\n  A.3) TP Provenance")
        print(f"  ──────────────────")
        print(f"  TPs from directory expansions: {tp_from_dir} / {tp_count}  ({tp_from_dir/tp_count*100:.1f}%)" if tp_count > 0 else "  No TPs")
        print(f"  TPs from file entries:         {tp_from_file} / {tp_count}  ({tp_from_file/tp_count*100:.1f}%)" if tp_count > 0 else "")

        # Top 10 raw entries by TP count (block size)
        sorted_tp_raw = sorted(tp_by_raw.items(), key=lambda x: x[1], reverse=True)
        print(f"\n  Top raw entries by TP count (largest 'blocks'):")
        for i, ((sid, raw_path), count) in enumerate(sorted_tp_raw[:10], 1):
            entry_type = "DIR " if raw_path.endswith("/") else "FILE"
            total_enrolled = len(raw_to_files.get((sid, raw_path), set()))
            print(f"    {i:2d}. [{entry_type}] sent={sid:>3s}, path={raw_path:<60s} -> {count:>4d} TPs / {total_enrolled:>4d} enrolled")

        # ── A.4) FNs grouped by raw gold entry ──────────────────────────────

        fn_from_dir = 0
        fn_from_file = 0
        fn_by_raw = defaultdict(int)  # raw entry -> count of FNs from it

        for entry in fn_set:
            raw = file_to_raw.get(entry)
            if raw is None:
                continue
            fn_by_raw[raw] += 1
            if is_directory.get(raw, False):
                fn_from_dir += 1
            else:
                fn_from_file += 1

        print(f"\n  A.4) FN Provenance")
        print(f"  ──────────────────")
        print(f"  FNs from directory expansions: {fn_from_dir} / {fn_count}  ({fn_from_dir/fn_count*100:.1f}%)" if fn_count > 0 else "  No FNs")
        print(f"  FNs from file entries:         {fn_from_file} / {fn_count}  ({fn_from_file/fn_count*100:.1f}%)" if fn_count > 0 else "")

        # Top 10 raw entries by FN count (biggest missed blocks)
        sorted_fn_raw = sorted(fn_by_raw.items(), key=lambda x: x[1], reverse=True)
        print(f"\n  Top raw entries by FN count (biggest missed blocks):")
        for i, ((sid, raw_path), count) in enumerate(sorted_fn_raw[:10], 1):
            entry_type = "DIR " if raw_path.endswith("/") else "FILE"
            total_enrolled = len(raw_to_files.get((sid, raw_path), set()))
            print(f"    {i:2d}. [{entry_type}] sent={sid:>3s}, path={raw_path:<60s} -> {count:>4d} FNs / {total_enrolled:>4d} enrolled")

        # ── A.5) Largest single block of TPs ─────────────────────────────────

        if sorted_tp_raw:
            biggest_tp_raw, biggest_tp_count = sorted_tp_raw[0]
            biggest_tp_total = len(raw_to_files.get(biggest_tp_raw, set()))
            print(f"\n  A.5) Largest single TP block")
            print(f"  ────────────────────────────")
            print(f"  Raw entry: sent={biggest_tp_raw[0]}, path={biggest_tp_raw[1]}")
            print(f"  Type: {'DIRECTORY' if biggest_tp_raw[1].endswith('/') else 'FILE'}")
            print(f"  TPs from this one entry: {biggest_tp_count}")
            print(f"  Total enrolled from this entry: {biggest_tp_total}")
            print(f"  This single entry accounts for {biggest_tp_count/tp_count*100:.1f}% of all TPs" if tp_count > 0 else "")

        # ── B) Metric Sensitivity ────────────────────────────────────────────

        print(f"\n  B) Metric Sensitivity")
        print(f"  ─────────────────────")

        # Find the raw entry that expands to the most enrolled entries
        raw_by_expansion = sorted(
            [(raw_entry, enrolled_set) for raw_entry, enrolled_set in raw_to_files.items()],
            key=lambda x: len(x[1]),
            reverse=True
        )

        if raw_by_expansion:
            biggest_raw, biggest_enrolled_set = raw_by_expansion[0]
            biggest_expansion_count = len(biggest_enrolled_set)

            print(f"\n  Largest expansion: sent={biggest_raw[0]}, path={biggest_raw[1]}")
            print(f"  Type: {'DIRECTORY' if biggest_raw[1].endswith('/') else 'FILE'}")
            print(f"  Expands to: {biggest_expansion_count} file-level entries")

            # F1 with this entry INCLUDED (= baseline, full gold standard)
            f1_with = f1
            p_with = p
            r_with = r

            # F1 with this entry EXCLUDED from gold standard
            gold_without = enrolled - biggest_enrolled_set
            # Also need to adjust result: TP/FP change
            # A result entry that was TP against gold becomes: still in result, but if
            # it was only a TP because of the excluded gold entries, it's now an FP.
            # However, the result set doesn't change -- only the gold changes.
            p_wo, r_wo, f1_wo, tp_wo, fp_wo, fn_wo = calc_metrics(gold_without, result)

            # How many of the excluded entries were TPs vs FNs?
            excluded_tps = biggest_enrolled_set & tp_set
            excluded_fns = biggest_enrolled_set & fn_set

            print(f"\n  Impact of excluding this one entry:")
            print(f"  ────────────────────────────────────")
            print(f"  Excluded entries:  {biggest_expansion_count}  ({len(excluded_tps)} were TPs, {len(excluded_fns)} were FNs)")
            print(f"  {'':30s} {'WITH entry':>14s} {'WITHOUT entry':>14s} {'Delta':>10s}")
            print(f"  {'Gold size':30s} {len(enrolled):>14d} {len(gold_without):>14d} {len(gold_without)-len(enrolled):>+10d}")
            print(f"  {'TP':30s} {tp_count:>14d} {tp_wo:>14d} {tp_wo-tp_count:>+10d}")
            print(f"  {'FP':30s} {fp_count:>14d} {fp_wo:>14d} {fp_wo-fp_count:>+10d}")
            print(f"  {'FN':30s} {fn_count:>14d} {fn_wo:>14d} {fn_wo-fn_count:>+10d}")
            print(f"  {'Precision':30s} {p_with:>14.4f} {p_wo:>14.4f} {p_wo-p_with:>+10.4f}")
            print(f"  {'Recall':30s} {r_with:>14.4f} {r_wo:>14.4f} {r_wo-r_with:>+10.4f}")
            print(f"  {'F1':30s} {f1_with:>14.4f} {f1_wo:>14.4f} {f1_wo-f1_with:>+10.4f}")

            # Also show: what if we add this entry to a system that currently misses it entirely?
            # i.e., what does recovering this one directory "decision" buy you?

            # For additional context: show the 2nd and 3rd largest as well
            print(f"\n  Top-5 raw entries by enrollment expansion:")
            for i, (raw_entry, enrolled_set) in enumerate(raw_by_expansion[:5], 1):
                entry_type = "DIR " if raw_entry[1].endswith("/") else "FILE"
                n_enrolled_from = len(enrolled_set)
                n_tp = len(enrolled_set & tp_set)
                n_fn = len(enrolled_set & fn_set)
                pct_of_gold = n_enrolled_from / len(enrolled) * 100 if enrolled else 0
                print(f"    {i}. [{entry_type}] sent={raw_entry[0]:>3s}, path={raw_entry[1]:<55s}")
                print(f"       expands to {n_enrolled_from:>4d} entries ({pct_of_gold:.1f}% of enrolled gold)  |  {n_tp} TPs, {n_fn} FNs")

        # ── B bonus) Full "per-raw-entry" metric sensitivity ─────────────────

        # For each raw entry, compute the F1 if that entry alone were excluded
        print(f"\n  B.bonus) Per-raw-entry F1 sensitivity (top-10 by |delta F1|):")
        print(f"  ────────────────────────────────────────────────────────────")

        entry_sensitivity = []
        for raw_entry, enrolled_set in raw_to_files.items():
            if len(enrolled_set) == 0:
                continue
            gold_without = enrolled - enrolled_set
            if len(gold_without) == 0:
                continue
            _, _, f1_wo_entry, _, _, _ = calc_metrics(gold_without, result)
            delta = f1_wo_entry - f1
            entry_sensitivity.append((raw_entry, len(enrolled_set), delta, f1_wo_entry))

        entry_sensitivity.sort(key=lambda x: abs(x[2]), reverse=True)
        print(f"  {'Raw entry':<70s} {'Size':>5s} {'F1_base':>8s} {'F1_excl':>8s} {'Delta':>8s}")
        for (raw_entry, size, delta, f1_wo_entry) in entry_sensitivity[:10]:
            path_display = f"s={raw_entry[0]},p={raw_entry[1]}"
            if len(path_display) > 68:
                path_display = path_display[:65] + "..."
            print(f"  {path_display:<70s} {size:>5d} {f1:>8.4f} {f1_wo_entry:>8.4f} {delta:>+8.4f}")

        # ── Collect summary ──────────────────────────────────────────────────

        summary[proj] = {
            "n_raw": n_raw,
            "n_raw_dir": n_raw_dir,
            "n_raw_file": n_raw_file,
            "n_enrolled": n_enrolled,
            "expansion_ratio": expansion_ratio,
            "tp": tp_count, "fp": fp_count, "fn": fn_count,
            "p": p, "r": r, "f1": f1,
            "tp_from_dir": tp_from_dir,
            "tp_from_file": tp_from_file,
            "fn_from_dir": fn_from_dir,
            "fn_from_file": fn_from_file,
            "largest_tp_block": sorted_tp_raw[0][1] if sorted_tp_raw else 0,
            "largest_tp_block_entry": sorted_tp_raw[0][0] if sorted_tp_raw else None,
            "largest_expansion": raw_by_expansion[0][1] if raw_by_expansion else set(),
            "largest_expansion_entry": raw_by_expansion[0][0] if raw_by_expansion else None,
            "largest_expansion_count": len(raw_by_expansion[0][1]) if raw_by_expansion else 0,
            "f1_without_largest": f1_wo if raw_by_expansion else f1,
            "f1_delta_largest": (f1_wo - f1) if raw_by_expansion else 0.0,
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-project Summary Tables
    # ═══════════════════════════════════════════════════════════════════════════

    print(f"\n\n{'=' * 90}")
    print(f"CROSS-PROJECT SUMMARY")
    print(f"{'=' * 90}")

    # Table 1: Enrollment expansion
    print(f"\n  Table 1: Enrollment Expansion")
    print(f"  {'Project':<16s} {'Raw':>5s} {'Dirs':>5s} {'Files':>5s} {'Enrolled':>9s} {'Ratio':>7s}")
    print(f"  {'─'*16} {'─'*5} {'─'*5} {'─'*5} {'─'*9} {'─'*7}")
    for proj in PROJECTS:
        s = summary[proj]
        print(f"  {proj:<16s} {s['n_raw']:>5d} {s['n_raw_dir']:>5d} {s['n_raw_file']:>5d} {s['n_enrolled']:>9d} {s['expansion_ratio']:>6.1f}x")

    # Table 2: TP/FN provenance
    print(f"\n  Table 2: TP/FN Provenance (directory vs file entries)")
    print(f"  {'Project':<16s} {'TP':>5s} {'TP_dir':>7s} {'TP_dir%':>8s} {'FN':>5s} {'FN_dir':>7s} {'FN_dir%':>8s}")
    print(f"  {'─'*16} {'─'*5} {'─'*7} {'─'*8} {'─'*5} {'─'*7} {'─'*8}")
    for proj in PROJECTS:
        s = summary[proj]
        tp_dir_pct = s['tp_from_dir']/s['tp']*100 if s['tp'] > 0 else 0
        fn_dir_pct = s['fn_from_dir']/s['fn']*100 if s['fn'] > 0 else 0
        print(f"  {proj:<16s} {s['tp']:>5d} {s['tp_from_dir']:>7d} {tp_dir_pct:>7.1f}% {s['fn']:>5d} {s['fn_from_dir']:>7d} {fn_dir_pct:>7.1f}%")

    # Table 3: Largest TP block
    print(f"\n  Table 3: Largest Single TP Block")
    print(f"  {'Project':<16s} {'Block TPs':>10s} {'Total TPs':>10s} {'% of TPs':>9s} {'Entry type':>11s}")
    print(f"  {'─'*16} {'─'*10} {'─'*10} {'─'*9} {'─'*11}")
    for proj in PROJECTS:
        s = summary[proj]
        block = s['largest_tp_block']
        total = s['tp']
        pct = block/total*100 if total > 0 else 0
        entry = s['largest_tp_block_entry']
        etype = "DIRECTORY" if entry and entry[1].endswith("/") else "FILE"
        print(f"  {proj:<16s} {block:>10d} {total:>10d} {pct:>8.1f}% {etype:>11s}")

    # Table 4: Metric sensitivity
    print(f"\n  Table 4: F1 Sensitivity to Largest Single Raw Entry")
    print(f"  {'Project':<16s} {'Expansion':>10s} {'F1_full':>8s} {'F1_excl':>8s} {'Delta':>8s} {'Entry type':>11s}")
    print(f"  {'─'*16} {'─'*10} {'─'*8} {'─'*8} {'─'*8} {'─'*11}")
    for proj in PROJECTS:
        s = summary[proj]
        entry = s['largest_expansion_entry']
        etype = "DIRECTORY" if entry and entry[1].endswith("/") else "FILE"
        print(f"  {proj:<16s} {s['largest_expansion_count']:>10d} {s['f1']:>8.4f} {s['f1_without_largest']:>8.4f} {s['f1_delta_largest']:>+8.4f} {etype:>11s}")

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Findings
    # ═══════════════════════════════════════════════════════════════════════════

    print(f"\n\n{'=' * 90}")
    print(f"KEY FINDINGS")
    print(f"{'=' * 90}")

    # 1. Enrollment amplification
    total_raw = sum(s['n_raw'] for s in summary.values())
    total_enrolled = sum(s['n_enrolled'] for s in summary.values())
    total_dir_raw = sum(s['n_raw_dir'] for s in summary.values())
    print(f"\n  1) ENROLLMENT AMPLIFICATION")
    print(f"     Total raw entries across 5 projects:     {total_raw}")
    print(f"     Total enrolled entries:                   {total_enrolled}")
    print(f"     Overall expansion ratio:                  {total_enrolled/total_raw:.1f}x")
    print(f"     Raw entries that are directories:         {total_dir_raw}/{total_raw} ({total_dir_raw/total_raw*100:.1f}%)")

    # 2. TP inflation
    total_tp = sum(s['tp'] for s in summary.values())
    total_tp_dir = sum(s['tp_from_dir'] for s in summary.values())
    print(f"\n  2) TP INFLATION FROM DIRECTORIES")
    print(f"     Total TPs across 5 projects:             {total_tp}")
    print(f"     TPs from directory expansions:            {total_tp_dir} ({total_tp_dir/total_tp*100:.1f}%)")
    print(f"     A single directory hit can generate hundreds of 'correct' file matches.")

    # 3. FN inflation
    total_fn = sum(s['fn'] for s in summary.values())
    total_fn_dir = sum(s['fn_from_dir'] for s in summary.values())
    print(f"\n  3) FN INFLATION FROM DIRECTORIES")
    print(f"     Total FNs across 5 projects:             {total_fn}")
    print(f"     FNs from directory expansions:            {total_fn_dir} ({total_fn_dir/total_fn*100:.1f}%)")
    print(f"     A single missed directory creates a 'block' of FNs.")

    # 4. Metric instability
    max_delta_proj = max(PROJECTS, key=lambda p: abs(summary[p]['f1_delta_largest']))
    max_delta = summary[max_delta_proj]['f1_delta_largest']
    max_exp = summary[max_delta_proj]['largest_expansion_count']
    print(f"\n  4) METRIC INSTABILITY")
    print(f"     Most sensitive project: {max_delta_proj}")
    print(f"     Removing its largest entry ({max_exp} files) changes F1 by {max_delta:+.4f}")
    print(f"     One annotator 'decision' (assign directory X to sentence Y) can swing F1 substantially.")

    # 5. Effective decisions
    print(f"\n  5) EFFECTIVE DECISION COUNT")
    print(f"     The enrolled gold standard has {total_enrolled} entries, but these come from only")
    print(f"     {total_raw} raw decisions. The true 'degrees of freedom' in the gold standard")
    print(f"     are {total_raw}, not {total_enrolled}.")
    for proj in PROJECTS:
        s = summary[proj]
        print(f"     {proj:<16s}: {s['n_enrolled']:>5d} enrolled entries from {s['n_raw']:>3d} raw decisions")

    print()


if __name__ == "__main__":
    main()
