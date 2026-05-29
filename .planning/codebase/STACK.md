# Technology Stack

**Analysis Date:** 2026-05-29

## Languages

**Primary:**
- Python 3.13.12 - All analysis, evaluation, and empirical study scripts

**Secondary:**
- LaTeX - Academic paper writing (`writing/eval.tex`)

## Runtime

**Environment:**
- Python 3.13.12

**Package Manager:**
- pip (implicit)
- Lockfile: Not present (no requirements.txt, pyproject.toml, or setup.py)

## Frameworks

**Data Processing:**
- `csv` - CSV file reading/writing for gold standards and results
- `json` - JSON serialization for classifications and intermediate analysis

**Analysis & Computation:**
- `collections` (defaultdict, Counter) - Data aggregation
- `dataclasses` - Data structure definitions for analysis results
- `math` - Statistical and metric calculations
- `pathlib` - Cross-platform path handling
- `re` - Regular expression pattern matching for text analysis

**Utilities:**
- `xml.etree.ElementTree` - PCM model XML parsing (when analyzing models)

## Key Dependencies

**All from Python Standard Library:**
- No external pip packages used
- Entire codebase depends only on built-in Python modules

## Configuration

**Environment:**
- No `.env` file required or present
- All paths hardcoded as absolute paths
- Example: `BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")`
- Results directory: `/mnt/hostshare/ardoco-home/transarc-emp/results/`

**Build:**
- No build configuration files
- Scripts run directly: `python3 src/lib/transarc_error_analysis.py`

## Platform Requirements

**Development:**
- Python 3.13+ (verified with 3.13.12)
- Unix/Linux environment (hardcoded `/mnt/` paths)
- bash or zsh shell

**Production:**
- ARDoCo benchmark datasets available at `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
- TransArc pipeline (Java-based) produces result CSV files in `/mnt/hostshare/ardoco-home/transarc-emp/results/`

---

*Stack analysis: 2026-05-29*
