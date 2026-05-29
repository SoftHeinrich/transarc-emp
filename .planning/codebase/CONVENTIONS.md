# Coding Conventions

**Analysis Date:** 2026-05-29

## Naming Patterns

**Files:**
- Snake case with descriptive function/topic names: `transarc_error_analysis.py`, `benchmark_bias_study.py`, `evaluation_critique.py`, `swattr_fn_leakage_test.py`
- Scripts organized by analysis type: `src/lib/`, `src/bias/`, `src/evaluation/`, `src/annotation/`, `src/propagation/`
- Version/iteration numbering when multiple approaches exist: `doc_structure_analysis_v2.py`, `llm_improved_classifier.py`

**Functions:**
- Snake case consistently used throughout
- Loader functions prefixed with `load_`: `load_gs_sad_sam()`, `load_code_model_files()`, `load_result_sad_code()`
- Analysis/computation functions named descriptively: `analysis_a()`, `analysis_b()`, `calc_metrics()`, `distribution_stats()`
- Helper functions remain lowercase: `normalize_path()`, `enroll_gold_standard()`, `gini_coefficient()`, `ascii_histogram()`

**Variables:**
- Snake case for all variables: `code_model_files`, `sent_to_models`, `model_to_codes`, `bridging_models`
- Abbreviations used consistently: `gs_` (gold standard), `int_` (intermediate), `proj` (project), `ae_id`, `fp`, `tp`, `fn`
- Collections use plural form: `gs_sad_sam_maps`, `model_to_codes`, `code_model_files`
- Result/output variables explicitly named: `transarc_result`, `perfect_sad_sam_result`, `enrolled_set`

**Types/Constants:**
- All-caps for constants: `BENCHMARK`, `RESULTS`, `PROJECTS`, `EXPECTED`, `OUTPUT_MD`, `GS_SAD_SAM`, `GS_SAM_CODE`
- Dataclass names in PascalCase: `FPClassification`, `FNClassification`, `ErrorPropagation`
- Dict keys use descriptive strings: `"perfect_sad_sam"`, `"sad_sam_caused"`, `"theoretical_limit"`

## Code Style

**Formatting:**
- No automated formatter detected (no `.pylintrc`, `pyproject.toml`, `.flake8`, etc.)
- Manual PEP 8 adherence observed throughout
- Line length appears reasonable (80-120 char range typical)
- 4-space indentation used consistently

**Imports Organization:**
- Standard library imports first: `csv`, `json`, `sys`, `os`, `re`, `subprocess`, `time`, `math`
- Third-party imports next: `xml.etree.ElementTree`, `statistics`
- Collection imports grouped: `from collections import Counter, defaultdict, namedtuple`
- Dataclass decorator used: `from dataclasses import dataclass, field`
- Relative imports with sys.path manipulation for shared libraries:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from transarc_error_analysis import (
    BENCHMARK, PROJECTS, normalize_path, load_gs_sad_sam, calc_metrics
)
```

**Module docstrings:**
- Every script starts with triple-quoted docstring (80-200 chars)
- Describes purpose, inputs, and output artifacts:

```python
"""
TransArc Empirical Error Analysis

Decomposes TransArc (SAD-CODE) false positives and false negatives back to their
component causes in SAD-SAM and SAM-CODE, quantifies error propagation / amplification,
and performs "what-if" component comparison analysis.

Produces structured stdout output and writes TRANSARC_EMPIRICAL_STUDY.md.
"""
```

## Error Handling

**Approach:**
- Minimal explicit error handling in primary analysis scripts
- Graceful degradation with sensible defaults where needed
- Try-except blocks used selectively for external dependencies and subprocess calls

**Patterns:**

- **File existence checks:** Use `.exists()` before reading, return empty collections on missing files:
```python
def load_result_sad_code(project):
    path = RESULTS / project / "sad-code" / f"sadCodeTlr_{project}.csv"
    links = set()
    if not path.exists():
        return links  # Silent return of empty set
    with open(path) as f:
        for row in csv.DictReader(f):
            links.add((row["modelElementID"], normalize_path(row["codeId"])))
    return links
```

- **JSON parsing:** Try-except with fallback to next parsing strategy:
```python
try:
    data = json.loads(result.stdout.strip())
    # ... extract from data ...
except json.JSONDecodeError:
    # Try line-by-line JSON event parsing
    for line in result.stdout.strip().split('\n'):
        try:
            event = json.loads(line)
            # ... extract from event ...
        except json.JSONDecodeError:
            continue
```

- **Subprocess timeouts:** Catch `subprocess.TimeoutExpired` and `Exception` with stderr logging:
```python
except subprocess.TimeoutExpired:
    print(f"  TIMEOUT", file=sys.stderr)
    return None
except Exception as e:
    print(f"  ERROR: {e}", file=sys.stderr)
    return None
```

- **XML parsing:** Broad exception catch for robustness with third-party libraries:
```python
try:
    tree = ET.parse(pcm_path)
    root = tree.getroot()
    # ... extract elements ...
except Exception:
    pass  # Silent failure; use fallback data
```

## Data Validation & Assertions

**Runtime Assertions:**
- Consistency checks between component counts and totals
- Verify TP+FP equals result size, TP+FN equals gold standard size:

```python
assert tp + fp == rs, f"{task}/{proj}: TP+FP={tp+fp} != result={rs}"
assert tp + fn == gs, f"{task}/{proj}: TP+FN={tp+fn} != gold={gs}"
assert total == total_fp, f"{proj}: FP categories sum={total} != total_fp={total_fp}"
```

**CSV Handling:**
- Always use `csv.DictReader` for structured parsing with field name safety
- Normalize paths immediately on read: `normalize_path(row["codeID"])`
- Handle column name variations: `row.get("ce_ids") or row.get("ce_id")` (Teammates uses singular)

## Output/Report Generation

**Pattern:** All analysis scripts follow report generation convention with dual output:

1. **Stdout:** Human-readable formatted output during execution
2. **Markdown file:** Comprehensive structured report written to `reports/` directory

**Implementation:**
```python
md_lines = []

def out(s=""):
    print(s)
    md_lines.append(s)

def md_only(s=""):
    md_lines.append(s)

# ... analysis code calls out() and md_only() ...

with open(OUTPUT_MD, "w") as f:
    f.write("\n".join(md_lines))
    f.write("\n")

print(f"\n\nReport written to {OUTPUT_MD}")
```

**Markdown formatting:**
- Headings with `# Level 1`, `## Level 2`, `### Level 3` (no level 0)
- Tables use pipe syntax with alignment markers: `| Col1 | Col2 |`
- Code blocks use triple backticks with language: `` ```python ``
- Emphasis: `**bold**` for headers, `*italic*` for emphasis, backticks for inline code
- Lists use `- ` or numbered `1. `

## Project-Specific Abbreviations

**Consistent abbreviations across all scripts:**
- `gs`: Gold standard (truth data from ARDoCo benchmark)
- `int_`: Intermediate results (TransArc stage outputs)
- `proj`: Project name (one of: mediastore, teastore, teammates, bigbluebutton, jabref)
- `ae_id`: Architecture Element ID (UUID from PCM model)
- `ce_id`: Code Element ID (file path)
- `sent`: Sentence (from documentation text)
- `code`: Code file path
- `tp`/`fp`/`fn`: True Positive / False Positive / False Negative
- `p`/`r`/`f1`: Precision / Recall / F1-score (metrics)

**Task abbreviations:**
- `sad-sam`: Sentence-to-Architectural-Description mapping (documentation → architecture model)
- `sam-code`: Architectural-Model-to-Code mapping (architecture model → code)
- `sad-code`: Sentence-to-Code mapping (documentation → code, transitive)

## Reproducibility Conventions

**Path handling:**
- All paths use `Path` objects from `pathlib`
- Absolute paths used throughout (mounted at `/mnt/hostshare/ardoco-home/`)
- Central constants define all benchmark/result locations at module top:

```python
BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")
RESULTS   = Path("/mnt/hostshare/ardoco-home/transarc-emp/results")
OUTPUT_MD = Path("/mnt/hostshare/ardoco-home/transarc-emp/reports/FILENAME.md")
```

**Data structure initialization:**
- Path dictionaries mapped by project for all datasets:

```python
GS_SAD_SAM = {
    "mediastore":    BENCHMARK / "mediastore/goldstandards/goldstandard_sad_2016-sam_2016.csv",
    "teastore":      BENCHMARK / "teastore/goldstandards/goldstandard_sad_2020-sam_2020.csv",
    # ... per-project entries ...
}
```

**Script execution:**
- Entry point: `if __name__ == "__main__": main()`
- Always runs analysis from within `main()` function to ensure isolation
- No command-line arguments used (parameters hardcoded as constants)

---

*Convention analysis: 2026-05-29*
