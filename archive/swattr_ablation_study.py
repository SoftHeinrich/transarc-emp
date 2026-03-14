#!/usr/bin/env python3
"""
SWATTR Leave-One-Out Ablation Study

Sweeps key SWATTR parameters across all 5 benchmark projects and performs
leave-one-out cross-validation to test whether default thresholds generalize.

Tier 1 parameters (CommonTextToolsConfig.properties - static final, need file modification):
  - jaroWinkler_SimilarityThreshold (default: 0.90)
  - getMostRecommendedIByRef_MinProportion (default: 0.50)

Tier 2 parameters (@Configurable - passed via additionalConfigs):
  - MappingCombinerInformant::minCosineSimilarity (default: 0.40)

Usage: python3 swattr_ablation_study.py [--skip-runs] [--tier1-only] [--tier2-only]
"""

import subprocess
import re
import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime

ARDOCO_DIR = Path("/mnt/hostshare/ardoco-home/ardoco")
PROPS_SRC = ARDOCO_DIR / "core/framework/common/src/main/resources/configs/CommonTextToolsConfig.properties"
PROPS_TARGET = ARDOCO_DIR / "core/framework/common/target/classes/configs/CommonTextToolsConfig.properties"
RESULTS_FILE = Path(__file__).parent / "swattr_ablation_results.json"
REPORT_FILE = Path(__file__).parent / "SWATTR_ABLATION_STUDY.md"

PROJECTS = ["MEDIASTORE", "TEASTORE", "TEAMMATES", "BIGBLUEBUTTON", "JABREF"]

# Parameter sweep definitions
PARAMETERS = {
    "jaroWinkler_SimilarityThreshold": {
        "tier": 1,
        "default": 0.90,
        "values": [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00],
        "props_key": "jaroWinkler_SimilarityThreshold",
    },
    "getMostRecommendedIByRef_MinProportion": {
        "tier": 1,
        "default": 0.50,
        "values": [0.30, 0.40, 0.50, 0.60, 0.70, 0.80],
        "props_key": "getMostRecommendedIByRef_MinProportion",
    },
    "MappingCombinerInformant::minCosineSimilarity": {
        "tier": 2,
        "default": 0.40,
        "values": [0.20, 0.30, 0.40, 0.50, 0.60, 0.70],
        "config_key": "MappingCombinerInformant::minCosineSimilarity",
    },
}


def read_properties(path):
    """Read properties file into a dict, preserving comments."""
    lines = path.read_text().splitlines()
    props = {}
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            if "=" in stripped:
                key, val = stripped.split("=", 1)
                props[key.strip()] = val.strip()
    return props


def write_property(props_path, key, value):
    """Modify a single property value in a properties file."""
    lines = props_path.read_text().splitlines()
    new_lines = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _ = stripped.split("=", 1)
            if k.strip() == key:
                new_lines.append(f"{key}={value}")
                found = True
                continue
        new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    props_path.write_text("\n".join(new_lines) + "\n")


def backup_properties():
    """Backup both copies of the properties file."""
    backups = {}
    for p in [PROPS_SRC, PROPS_TARGET]:
        if p.exists():
            backups[p] = p.read_text()
    return backups


def restore_properties(backups):
    """Restore properties files from backup."""
    for p, content in backups.items():
        p.write_text(content)


def reinstall_common_module():
    """Reinstall the common module so the modified properties file is picked up by the jar."""
    cmd = [
        "mvn", "install",
        "-pl", "core/framework/common",
        "-DskipTests", "-q",
    ]
    print("    Reinstalling common module...")
    result = subprocess.run(
        cmd, cwd=str(ARDOCO_DIR), capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"    WARNING: reinstall failed: {result.stderr[-200:]}")


def run_tier1_sweep(param_name, value):
    """Run all projects with a Tier 1 parameter modified in the properties file."""
    param_def = PARAMETERS[param_name]
    props_key = param_def["props_key"]

    # Modify both src and target copies
    for p in [PROPS_SRC, PROPS_TARGET]:
        if p.exists():
            write_property(p, props_key, str(value))

    # Reinstall common module so jar picks up the change
    reinstall_common_module()

    # Run SwattrAblationTest (no additional system props needed for Tier 1)
    return run_maven_test([])


def run_tier2_sweep(param_name, value):
    """Run all projects with a Tier 2 @Configurable parameter override."""
    param_def = PARAMETERS[param_name]
    config_key = param_def["config_key"]
    sys_prop = f"-Dablation.{config_key}={value}"
    return run_maven_test([sys_prop])


def run_maven_test(extra_args):
    """Run SwattrAblationTest and parse results."""
    cmd = [
        "mvn", "test",
        "-pl", "tlr/tests-tlr",
        "-Dtest=SwattrAblationTest",
        "-Dmaven.test.failure.ignore=true",
        "-Dsurefire.useFile=false",
    ] + extra_args

    print(f"  Running: {' '.join(cmd)}")
    start = time.time()

    result = subprocess.run(
        cmd,
        cwd=str(ARDOCO_DIR),
        capture_output=True,
        text=True,
        timeout=900,  # 15 min max
    )
    elapsed = time.time() - start
    print(f"  Completed in {elapsed:.0f}s")

    output = result.stdout + "\n" + result.stderr
    return parse_ablation_output(output)


def parse_ablation_output(output):
    """Parse ABLATION_RESULT lines from Maven output."""
    results = {}
    for line in output.splitlines():
        if "ABLATION_RESULT|" in line:
            # Extract the ABLATION_RESULT portion
            idx = line.index("ABLATION_RESULT|")
            payload = line[idx:]
            parts = payload.split("|")
            if len(parts) >= 7:
                project = parts[1]
                metrics = {}
                for part in parts[2:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        try:
                            metrics[k] = float(v)
                        except ValueError:
                            metrics[k] = v
                if "ERROR" not in metrics:
                    results[project] = {
                        "precision": metrics.get("P", 0),
                        "recall": metrics.get("R", 0),
                        "f1": metrics.get("F1", 0),
                        "tp": int(metrics.get("TP", 0)),
                        "fp": int(metrics.get("FP", 0)),
                        "fn": int(metrics.get("FN", 0)),
                    }
                else:
                    print(f"    ERROR for {project}: {metrics['ERROR']}")
    return results


def run_all_sweeps(skip_tiers=None):
    """Run all parameter sweeps, collecting results."""
    all_results = {}
    skip_tiers = skip_tiers or set()

    for param_name, param_def in PARAMETERS.items():
        tier = param_def["tier"]
        if tier in skip_tiers:
            print(f"\nSkipping {param_name} (tier {tier})")
            continue

        print(f"\n{'='*60}")
        print(f"Parameter: {param_name} (Tier {tier}, default={param_def['default']})")
        print(f"Values to sweep: {param_def['values']}")
        print(f"{'='*60}")

        param_results = {}
        backups = backup_properties()

        try:
            for value in param_def["values"]:
                print(f"\n  --- {param_name} = {value} ---")
                if tier == 1:
                    results = run_tier1_sweep(param_name, value)
                else:
                    results = run_tier2_sweep(param_name, value)

                param_results[str(value)] = results

                # Print summary
                if results:
                    f1s = [r["f1"] for r in results.values()]
                    avg_f1 = sum(f1s) / len(f1s) if f1s else 0
                    print(f"  Avg F1: {avg_f1:.4f} | Per-project: ", end="")
                    for proj in PROJECTS:
                        if proj in results:
                            print(f"{proj[:3]}={results[proj]['f1']:.3f} ", end="")
                    print()
                else:
                    print("  No results parsed!")
        finally:
            restore_properties(backups)
            if tier == 1:
                reinstall_common_module()
            print(f"  Properties restored to defaults.")

        all_results[param_name] = param_results

    return all_results


def leave_one_out_analysis(all_results):
    """Perform leave-one-out cross-validation analysis."""
    analysis = {}

    for param_name, param_results in all_results.items():
        param_def = PARAMETERS[param_name]
        param_analysis = {
            "default_value": param_def["default"],
            "projects": {},
            "default_performance": {},
        }

        # Get default performance
        default_key = str(param_def["default"])
        if default_key in param_results:
            param_analysis["default_performance"] = param_results[default_key]

        # For each project as test set
        for test_project in PROJECTS:
            train_projects = [p for p in PROJECTS if p != test_project]

            # Find best threshold on training set (avg F1 across 4 train projects)
            best_train_value = None
            best_train_f1 = -1

            for value_str, results in param_results.items():
                train_f1s = [results[p]["f1"] for p in train_projects if p in results]
                if train_f1s:
                    avg_train_f1 = sum(train_f1s) / len(train_f1s)
                    if avg_train_f1 > best_train_f1:
                        best_train_f1 = avg_train_f1
                        best_train_value = value_str

            # Get test performance with train-optimal threshold
            test_f1_loo = None
            if best_train_value and best_train_value in param_results:
                if test_project in param_results[best_train_value]:
                    test_f1_loo = param_results[best_train_value][test_project]["f1"]

            # Get test performance with default threshold
            test_f1_default = None
            if default_key in param_results and test_project in param_results[default_key]:
                test_f1_default = param_results[default_key][test_project]["f1"]

            # Get test performance with best-on-all-5 threshold
            best_all_value = None
            best_all_f1 = -1
            for value_str, results in param_results.items():
                all_f1s = [results[p]["f1"] for p in PROJECTS if p in results]
                if all_f1s:
                    avg_all_f1 = sum(all_f1s) / len(all_f1s)
                    if avg_all_f1 > best_all_f1:
                        best_all_f1 = avg_all_f1
                        best_all_value = value_str

            test_f1_best_all = None
            if best_all_value and best_all_value in param_results:
                if test_project in param_results[best_all_value]:
                    test_f1_best_all = param_results[best_all_value][test_project]["f1"]

            param_analysis["projects"][test_project] = {
                "train_optimal_value": best_train_value,
                "train_optimal_avg_f1": best_train_f1,
                "test_f1_with_loo_optimal": test_f1_loo,
                "test_f1_with_default": test_f1_default,
                "test_f1_with_best_all": test_f1_best_all,
                "best_all_value": best_all_value,
            }

        analysis[param_name] = param_analysis

    return analysis


def generate_report(all_results, analysis):
    """Generate the markdown report."""
    lines = []
    lines.append("# SWATTR Leave-One-Out Ablation Study")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("This study tests whether SWATTR's default threshold values generalize across")
    lines.append("benchmark projects by using leave-one-out cross-validation: for each held-out")
    lines.append("test project, we find the optimal threshold on the remaining 4 training projects")
    lines.append("and evaluate on the test project.")
    lines.append("")

    # Parameters studied
    lines.append("## Parameters Studied")
    lines.append("")
    lines.append("| Parameter | Tier | Default | Sweep Values |")
    lines.append("|-----------|------|---------|-------------|")
    for pname, pdef in PARAMETERS.items():
        vals = ", ".join(f"{v}" for v in pdef["values"])
        lines.append(f"| `{pname}` | {pdef['tier']} | {pdef['default']} | {vals} |")
    lines.append("")

    # Per-parameter sections
    for param_name, param_results in all_results.items():
        param_def = PARAMETERS[param_name]
        param_anal = analysis.get(param_name, {})

        lines.append(f"## {param_name}")
        lines.append("")
        lines.append(f"**Tier {param_def['tier']}** | Default: {param_def['default']}")
        lines.append("")

        # Sensitivity table: F1 vs threshold per project
        lines.append("### Parameter Sensitivity (F1 vs Threshold)")
        lines.append("")
        header = "| Value |"
        sep = "|-------|"
        SHORT_NAMES = {"MEDIASTORE": "Med", "TEASTORE": "Tea", "TEAMMATES": "Tmm", "BIGBLUEBUTTON": "BBB", "JABREF": "Jab"}
        for proj in PROJECTS:
            short = SHORT_NAMES.get(proj, proj[:3])
            header += f" {short} |"
            sep += "------|"
        header += " **Avg** |"
        sep += "--------|"
        lines.append(header)
        lines.append(sep)

        for value in param_def["values"]:
            value_str = str(value)
            results = param_results.get(value_str, {})
            row = f"| {value} |"
            f1s = []
            for proj in PROJECTS:
                if proj in results:
                    f1 = results[proj]["f1"]
                    f1s.append(f1)
                    # Bold the default value row
                    marker = ""
                    if value == param_def["default"]:
                        marker = "**"
                    row += f" {marker}{f1:.3f}{marker} |"
                else:
                    row += " - |"
            avg = sum(f1s) / len(f1s) if f1s else 0
            marker = "**" if value == param_def["default"] else ""
            row += f" {marker}{avg:.3f}{marker} |"
            lines.append(row)
        lines.append("")

        # Full metrics table (P/R/F1)
        lines.append("### Detailed Metrics (P / R / F1)")
        lines.append("")
        for value in param_def["values"]:
            value_str = str(value)
            results = param_results.get(value_str, {})
            if not results:
                continue
            lines.append(f"**{param_name} = {value}**")
            lines.append("")
            lines.append("| Project | P | R | F1 | TP | FP | FN |")
            lines.append("|---------|---|---|----|----|----|----|")
            for proj in PROJECTS:
                if proj in results:
                    r = results[proj]
                    lines.append(f"| {proj} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['tp']} | {r['fp']} | {r['fn']} |")
            lines.append("")

        # Leave-one-out table
        lines.append("### Leave-One-Out Cross-Validation")
        lines.append("")
        lines.append("| Test Project | LOO-Optimal Value | LOO Train F1 | LOO Test F1 | Default Test F1 | Best-All Value | Best-All Test F1 | Gap (LOO - Default) |")
        lines.append("|-------------|-------------------|-------------|-------------|-----------------|----------------|------------------|---------------------|")

        loo_test_f1s = []
        default_test_f1s = []
        for proj in PROJECTS:
            proj_anal = param_anal.get("projects", {}).get(proj, {})
            loo_val = proj_anal.get("train_optimal_value", "-")
            loo_train = proj_anal.get("train_optimal_avg_f1")
            loo_test = proj_anal.get("test_f1_with_loo_optimal")
            def_test = proj_anal.get("test_f1_with_default")
            ba_val = proj_anal.get("best_all_value", "-")
            ba_test = proj_anal.get("test_f1_with_best_all")

            gap = (loo_test - def_test) if (loo_test is not None and def_test is not None) else None

            loo_train_s = f"{loo_train:.3f}" if loo_train is not None else "-"
            loo_test_s = f"{loo_test:.3f}" if loo_test is not None else "-"
            def_test_s = f"{def_test:.3f}" if def_test is not None else "-"
            ba_test_s = f"{ba_test:.3f}" if ba_test is not None else "-"
            gap_s = f"{gap:+.3f}" if gap is not None else "-"

            if loo_test is not None:
                loo_test_f1s.append(loo_test)
            if def_test is not None:
                default_test_f1s.append(def_test)

            lines.append(f"| {proj} | {loo_val} | {loo_train_s} | {loo_test_s} | {def_test_s} | {ba_val} | {ba_test_s} | {gap_s} |")

        # Summary row
        avg_loo = sum(loo_test_f1s) / len(loo_test_f1s) if loo_test_f1s else 0
        avg_def = sum(default_test_f1s) / len(default_test_f1s) if default_test_f1s else 0
        avg_gap = avg_loo - avg_def
        lines.append(f"| **Average** | - | - | **{avg_loo:.3f}** | **{avg_def:.3f}** | - | - | **{avg_gap:+.3f}** |")
        lines.append("")

        # Interpretation
        lines.append("### Interpretation")
        lines.append("")
        if abs(avg_gap) < 0.005:
            lines.append(f"The default value ({param_def['default']}) generalizes well — the LOO gap is negligible ({avg_gap:+.3f}).")
        elif avg_gap > 0:
            lines.append(f"LOO-optimal thresholds improve over default by {avg_gap:+.3f} on average, suggesting the default ({param_def['default']}) is suboptimal.")
        else:
            lines.append(f"LOO-optimal thresholds perform worse than default by {avg_gap:+.3f} on average, suggesting cross-validation would hurt performance.")
        lines.append("")

    # Overall summary
    lines.append("## Overall Summary")
    lines.append("")
    lines.append("| Parameter | Default | Avg F1 (Default) | Avg F1 (LOO) | Generalization Gap |")
    lines.append("|-----------|---------|------------------|-------------|-------------------|")
    for param_name in all_results:
        param_def = PARAMETERS[param_name]
        param_anal = analysis.get(param_name, {})
        loo_f1s = []
        def_f1s = []
        for proj in PROJECTS:
            proj_anal = param_anal.get("projects", {}).get(proj, {})
            loo_f1 = proj_anal.get("test_f1_with_loo_optimal")
            def_f1 = proj_anal.get("test_f1_with_default")
            if loo_f1 is not None:
                loo_f1s.append(loo_f1)
            if def_f1 is not None:
                def_f1s.append(def_f1)
        avg_loo = sum(loo_f1s) / len(loo_f1s) if loo_f1s else 0
        avg_def = sum(def_f1s) / len(def_f1s) if def_f1s else 0
        gap = avg_loo - avg_def
        lines.append(f"| `{param_name}` | {param_def['default']} | {avg_def:.3f} | {avg_loo:.3f} | {gap:+.3f} |")
    lines.append("")

    # Best configuration
    lines.append("## Best Per-Project Configuration")
    lines.append("")
    lines.append("For each project, the parameter value that maximizes F1:")
    lines.append("")
    for param_name, param_results in all_results.items():
        lines.append(f"### {param_name}")
        lines.append("")
        lines.append("| Project | Best Value | F1 | Default F1 | Delta |")
        lines.append("|---------|-----------|-----|-----------|-------|")
        default_key = str(PARAMETERS[param_name]["default"])
        for proj in PROJECTS:
            best_val = None
            best_f1 = -1
            for value_str, results in param_results.items():
                if proj in results and results[proj]["f1"] > best_f1:
                    best_f1 = results[proj]["f1"]
                    best_val = value_str
            def_f1 = param_results.get(default_key, {}).get(proj, {}).get("f1", 0)
            delta = best_f1 - def_f1 if best_f1 >= 0 and def_f1 > 0 else 0
            lines.append(f"| {proj} | {best_val} | {best_f1:.3f} | {def_f1:.3f} | {delta:+.3f} |")
        lines.append("")

    return "\n".join(lines)


def main():
    skip_runs = "--skip-runs" in sys.argv
    tier1_only = "--tier1-only" in sys.argv
    tier2_only = "--tier2-only" in sys.argv

    skip_tiers = set()
    if tier1_only:
        skip_tiers.add(2)
    if tier2_only:
        skip_tiers.add(1)

    if skip_runs:
        print("Loading cached results...")
        if not RESULTS_FILE.exists():
            print(f"ERROR: No cached results at {RESULTS_FILE}")
            sys.exit(1)
        all_results = json.loads(RESULTS_FILE.read_text())
    else:
        print("Starting SWATTR Ablation Study")
        print(f"Ardoco dir: {ARDOCO_DIR}")
        print(f"Properties: {PROPS_SRC}")
        print()

        # Verify properties file exists
        if not PROPS_SRC.exists():
            print(f"ERROR: Properties file not found: {PROPS_SRC}")
            sys.exit(1)

        # Read current defaults
        current_props = read_properties(PROPS_SRC)
        print("Current properties:")
        for k, v in current_props.items():
            print(f"  {k} = {v}")
        print()

        all_results = run_all_sweeps(skip_tiers)

        # Save results
        RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
        print(f"\nResults saved to {RESULTS_FILE}")

    # Analysis
    print("\nPerforming leave-one-out analysis...")
    analysis = leave_one_out_analysis(all_results)

    # Generate report
    report = generate_report(all_results, analysis)
    REPORT_FILE.write_text(report)
    print(f"Report saved to {REPORT_FILE}")

    # Verify properties restored
    if not skip_runs:
        current = read_properties(PROPS_SRC)
        expected_jw = "0.90"
        # Properties might be stored as 0.9 or 0.90
        actual_jw = current.get("jaroWinkler_SimilarityThreshold", "")
        if float(actual_jw) != 0.9:
            print(f"WARNING: Properties NOT properly restored! JW threshold = {actual_jw}")
        else:
            print("Properties verified: restored to defaults.")


if __name__ == "__main__":
    main()
