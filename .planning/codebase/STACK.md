# Technology Stack

**Analysis Date:** 2026-05-29

## Languages

**Primary:**
- Python 3.10+ - All analysis, evaluation, and research scripts

**Secondary:**
- LaTeX - Academic paper writing (`writing/eval.tex`)

## Runtime

**Environment:**
- Python 3 (verified running Python 3.13.12)

**Package Manager:**
- pip (implicit, no lockfile present)
- No requirements.txt or pyproject.toml in repository root
- All imports are from Python standard library

## Frameworks

**Data Processing:**
- csv — CSV file reading/writing for gold standards and results
- json — JSON serialization for classifications and analysis outputs
- pathlib — Cross-platform path handling

**Analysis & Computation:**
- collections (defaultdict, Counter) — Data aggregation and counting
- dataclasses — Data structure definitions for analysis results
- math — Statistical and metric calculations

**Testing & Experimental:**
- subprocess — LLM API calls via CLI (Claude via `claude` command)
- re — Regex pattern matching for response parsing
- xml.etree.ElementTree — PCM repository XML parsing

**Build/Development:**
- No build system detected (pure Python scripts)

## Key Dependencies

**Standard Library Only:**
- csv, json, os, sys, re, pathlib, collections, dataclasses, math, subprocess, time, xml.etree.ElementTree

All external integrations use CLI subprocess calls, not Python packages.

## Configuration

**Environment:**
- No `.env` file required
- Python scripts reference hardcoded paths to benchmark data and results
- Example: `BENCHMARK = Path("/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark")`
- Results directory: `/mnt/hostshare/ardoco-home/transarc-emp/results/`

**Build:**
- No build config files present
- Scripts run directly: `python3 src/lib/transarc_error_analysis.py`

## Platform Requirements

**Development:**
- Python 3.10+ (tested with 3.13.12)
- Unix/Linux environment (uses `/mnt/` paths and shell commands)
- bash or zsh shell (for subprocess calls via Claude CLI)

**Production:**
- ARDoCo framework available at `/mnt/hostshare/ardoco-home/ardoco/` (git subtree)
- Benchmark datasets at `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
- TransArc result CSVs generated in `/mnt/hostshare/ardoco-home/transarc-emp/results/`

## External Tools

**LLM Integration:**
- Claude API accessed via `claude` CLI command (`subprocess.run()`)
- Supports multiple models: `sonnet` (default), others via `--model` flag
- Cache system: responses cached as JSON files in `llm_cache_*` directories

**Java/Maven Integration:**
- ARDoCo framework (located in parallel `/mnt/hostshare/ardoco-home/ardoco/`)
- TransArc executable produces CSV result files consumed by Python scripts

---

*Stack analysis: 2026-05-29*
