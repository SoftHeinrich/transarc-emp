# External Integrations

**Analysis Date:** 2026-05-29

## APIs & External Services

**Claude LLM (via CLI):**
- Service: Anthropic Claude API
- Usage: Few-shot/zero-shot classification of SAD-SAM and SAD-CODE trace links
- Integration: `subprocess.run(['claude', ...])` with prompt text
- Models: `sonnet` (Sonnet 3.5), configurable via `--model` flag
- Cache: Responses cached in `llm_cache_swattr/`, `llm_cache_improved/` directories as JSON
- Scripts using: `archive/swattr_llm_fewshot.py`, `archive/llm_improved_classifier.py`, `archive/llm_agentic_eval.py`
- Auth: Environment-based (`.env` not committed)
- Response format: JSON output captured from stdout and cached

**JavaSubprocess Integration:**
- Tool: ARDoCo framework (Java, Maven-based)
- Location: `/mnt/hostshare/ardoco-home/ardoco/` (git subtree)
- Usage: Runs TransArc pipeline to generate SAD-CODE trace link results
- Output: CSV files at `results/{project}/{task}/`
- No direct Python API — results consumed via CSV files only

## Data Storage

**Databases:**
- None — all data is file-based

**File Storage:**
- Local filesystem only
- Benchmark datasets: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/{project}/`
- Results: `/mnt/hostshare/ardoco-home/transarc-emp/results/{project}/{task}/`
- Reports: `/mnt/hostshare/ardoco-home/transarc-emp/reports/`

**Caching:**
- LLM response cache: `llm_cache_swattr/`, `llm_cache_improved/`, `llm_classifications/`, `llm_classifications_multi/`, `llm_classifications_improved/` (JSON files)
- No database cache

## Data Formats

**Input Gold Standards (CSV):**
- SAD-SAM: `{project}/goldstandards/goldstandard_sad_*-sam_*.csv` with columns: `modelElementID`, `sentence`
- SAM-CODE: `{project}/goldstandards/goldstandard_sam_*-code_*.csv` with columns: `ae_id`, `ae_name`, `ce_id/ce_ids`
- SAD-CODE: `{project}/goldstandards/goldstandard_sad_*-code_*.csv` with columns: directory/file paths, `Implementation/` prefix

**Input Models & Text:**
- PCM Model: `{project}/model_*/pcm/*.repository` (XML format)
- Code Model: `{project}/model_*/code/codeModel.acm` (custom archive format)
- Text: `{project}/text_*/[projectname].txt` (one sentence per line, numbered 1+)

**Output Results (CSV):**
- SAD-SAM results: `results/{project}/sad-sam/sadSamTlr_{project}.csv` → columns: `modelElementID`, `sentence`
- SAM-CODE results: `results/{project}/sam-code/samCodeTlr_{project}.csv` → columns: `sentenceID`, `codeID`
- SAD-CODE results: `results/{project}/sad-code/sadCodeTlr_{project}.csv` → columns: `modelElementID`, `codeId`

**LLM Classifications (JSON):**
- Single-agent: `llm_classifications/{project}.json` → dict of `{sentence_num: [component_names]}`
- Multi-agent: `llm_classifications_multi/{project}_{strategy}.json` → aggregated votes
- Improved classifier: `llm_classifications_improved/{project}_*.json` → meta-analysis + multi-phase outputs
- Cache: `llm_cache_*/batch_*.json` → raw API responses

**Analysis Reports (Markdown):**
- Error decomposition: `reports/TRANSARC_EMPIRICAL_STUDY.md`
- Bias analysis: `reports/BENCHMARK_BIAS_STUDY.md`, `reports/EVALUATION_CRITIQUE.md`
- Metric analysis: `reports/NEW_METRICS_REPORT.md`, `reports/CREATIVE_METRICS.md`
- LLM baselines: `archive/LLM_BASELINE.md`, `archive/LLM_IMPROVED_CLASSIFIER.md`

## Authentication & Identity

**Auth Provider:**
- None required for local execution
- LLM access: Uses system credentials from `claude` CLI (environment variable or `.env` not committed)
- All benchmark data is public/read-only

## Monitoring & Observability

**Error Tracking:**
- None — stderr output from subprocess calls printed to console
- Example: `print(f"  ERROR: {e}", file=sys.stderr)`

**Logs:**
- Console output (stdout/stderr)
- Cached LLM responses (JSON files for reproducibility)
- No structured logging framework

## CI/CD & Deployment

**Hosting:**
- None — local research evaluation scripts
- Run manually: `python3 src/lib/transarc_error_analysis.py` → stdout + `reports/TRANSARC_EMPIRICAL_STUDY.md`

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars (for LLM integration):**
- No Python environment variables required within scripts
- Claude CLI authentication handled externally (system `claude` command)

**Secrets location:**
- No secrets stored in repository
- LLM credentials (if any) managed by `claude` CLI, not by these scripts

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Benchmark Datasets (5 Projects)

**Each project contains:**
- **Artifacts:**
  - Text: documentation sentences (1 per line)
  - PCM Model: architectural components/interfaces (XML)
  - Code Model: source code structure (ACM archive)
  - Gold Standards: hand-annotated trace links (3 types: SAD-SAM, SAM-CODE, SAD-CODE)

- **Projects:**
  1. MediaStore (2016) — 19 components+interfaces, 59 enrolled SAD-CODE links
  2. TeaStore (2020/2022) — 19 components+interfaces, 707 enrolled SAD-CODE links
  3. Teammates (2021/2023) — 14 components+interfaces, 8,097 enrolled SAD-CODE links
  4. BigBlueButton (2021/2023) — 22 components+interfaces, 1,529 enrolled SAD-CODE links
  5. JabRef (2021/2023) — 6 components, 8,268 enrolled SAD-CODE links

- **Location:** `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/{project}/`

- **Key Concept — Enrollment:**
  - Gold standard SAD-CODE/SAM-CODE entries at directory granularity (e.g., `src/main/java/teammates/ui/`) are expanded to individual files during evaluation
  - Expansion uses `.acm` code model to determine which files exist in each directory
  - Creates up to 217.6x inflation (JabRef: 38 raw annotations → 8,268 enrolled links)

---

*Integration audit: 2026-05-29*
