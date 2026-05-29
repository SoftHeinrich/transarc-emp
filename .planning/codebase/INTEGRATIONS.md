# External Integrations

**Analysis Date:** 2026-05-29

## Data Sources & External Systems

**ARDoCo Benchmark Datasets:**
- Location: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
- Contains: 5 projects (mediastore, teastore, teammates, bigbluebutton, jabref)
- Each project has:
  - **Text**: documentation as one sentence per line → `{project}/text_*/[projectname].txt`
  - **Models**: PCM (XML) + Code Model (ACM binary) → `{project}/model_*/`
  - **Gold Standards**: hand-annotated trace links (CSV) → `{project}/goldstandards/`

**ARDoCo Framework (Java/Maven):**
- Location: `/mnt/hostshare/ardoco-home/ardoco/` (git subtree)
- Purpose: Runs TransArc pipeline to generate intermediate and final trace link results
- Output format: CSV files written to `results/{project}/{task}/`
- No direct Python API — consumed as CSV files only

## Data Formats

**Gold Standard CSVs:**
- **SAD-SAM**: `goldstandard_sad_*-sam_*.csv`
  - Columns: `modelElementID`, `sentence` (sentence number)
  - Format: Pairs of architecture model elements and documentation sentences

- **SAM-CODE**: `goldstandard_sam_*-code_*.csv`
  - Columns: `ae_id`, `ae_name`, `ce_id` or `ce_ids`
  - Paths prefixed with `Implementation/` (stripped during processing)
  - Can be directory paths (expanded to files during enrollment)

- **SAD-CODE**: `goldstandard_sad_*-code_*.csv`
  - Columns: mixed (directory or file paths as keys)
  - Paths prefixed with `Implementation/`
  - Directory entries expanded using ACM code model during evaluation

**Code Model (ACM format):**
- Custom archive format parsed by `load_code_model_files()` in `src/lib/transarc_error_analysis.py`
- Maps directory paths to individual files
- Used for enrollment expansion: directory → set of files

**Text Files:**
- One sentence per line, numbered starting from 1
- Read by: `load_text()` in `src/lib/transarc_error_analysis.py`
- Example: `mediastore.txt` has 36 sentences

**Result CSVs (TransArc output):**
- **SAD-SAM**: `results/{project}/sad-sam/sadSamTlr_{project}.csv`
  - Columns: `modelElementID`, `sentence`

- **SAM-CODE**: `results/{project}/sam-code/samCodeTlr_{project}.csv`
  - Columns: `sentenceID`, `codeID`

- **SAD-CODE (final)**: `results/{project}/sad-code/sadCodeTlr_{project}.csv`
  - Columns: `modelElementID`, `codeId` (note: lowercase 'd')

## Analysis & Cache Files

**LLM Classifications (JSON):**
- Single-agent: `llm_classifications/{project}.json`
- Multi-agent: `llm_classifications_multi/{project}_{strategy}.json`
- Improved version: `llm_classifications_improved/{project}_*.json` + meta-analysis
- Format: `{sentence_num: [component_names]}` or aggregated votes

**LLM Cache:**
- Directories: `archive/llm_cache_*` (responses cached as JSON)
- Not committed (listed in `.gitignore`)
- Purpose: Avoid re-querying Claude for identical prompts

**Intermediate Analysis Files:**
- Meta-analysis JSON: `llm_classifications_improved/{project}_meta_analysis.json`
- Discovery outputs: sections, aliases, co-occurrence patterns

## File Storage

**Benchmark Directory Structure:**
```
benchmark/
├── {project}/
│   ├── text_{year}/
│   │   └── {project}.txt
│   ├── model_{year}/
│   │   ├── pcm/
│   │   │   └── *.repository
│   │   └── code/
│   │       └── codeModel.acm
│   └── goldstandards/
│       ├── goldstandard_sad_*-sam_*.csv
│       ├── goldstandard_sam_*-code_*.csv
│       ├── goldstandard_sad_*-code_*.csv
│       └── *_UME.csv (Undocumented Model Elements)
```

**Results Directory Structure:**
```
results/
├── {project}/
│   ├── sad-sam/
│   │   └── sadSamTlr_{project}.csv
│   ├── sam-code/
│   │   └── samCodeTlr_{project}.csv
│   └── sad-code/
│       ├── sadSamTlr_{project}.csv (intermediate)
│       ├── samCodeTlr_{project}.csv (intermediate)
│       └── sadCodeTlr_{project}.csv (final)
```

**Reports Directory:**
```
reports/
├── TRANSARC_EMPIRICAL_STUDY.md
├── BENCHMARK_BIAS_STUDY.md
├── EVALUATION_CRITIQUE.md
├── S12C_VS_TRANSARC.csv
└── *.csv (analysis outputs)
```

## Key Concept: Enrollment

Gold standard entries at directory granularity (e.g., `Implementation/src/main/java/teammates/ui/`) are expanded to individual file entries during evaluation using the ACM code model. This creates significant inflation:

- **MediaStore**: 59 raw → 59 enrolled (1x, no directories)
- **TeaStore**: 707 raw → 707 enrolled (1x)
- **Teammates**: 1,051 raw → 8,097 enrolled (7.7x)
- **BigBlueButton**: 1,529 raw → 1,529 enrolled (1x)
- **JabRef**: 38 raw → 8,268 enrolled (217.6x)

Enrollment expansion is critical for SAD-CODE evaluation because gold standards use directory paths but file-level metrics expect individual files.

## Caching & Reproducibility

**LLM Response Cache:**
- Cached in `archive/llm_cache_swattr/`, `archive/llm_cache_improved/` as JSON
- Prevents re-querying Claude for identical prompts
- Not committed to git (in `.gitignore`)

**Intermediate Results:**
- Transitive link maps stored as JSON or dicts
- Enables "what-if" analysis without re-running Java pipeline

## External Dependencies Summary

- **No external Python packages** — pure standard library
- **Only external system**: ARDoCo Java framework (adjacent directory)
- **Only data source**: Benchmark datasets in adjacent directory
- **Only API integration**: None (historically had Claude CLI, now using standard library only)

---

*Integration audit: 2026-05-29*
