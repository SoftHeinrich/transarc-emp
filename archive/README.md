# Archive — TransArc Empirical Study

This directory contains scripts, reports, and data from the TransArc empirical study
that are **not** about benchmark properties. They are preserved for reference but are
no longer part of the active analysis.

All files were previously in the repository root. Git history is preserved.

---

## Categories

### E. Proposed LLM Linkers (10 scripts, 7 reports)

LLM-based SAD-CODE traceability approaches and their error analysis.

- `llm_baseline_eval.py` — Single-agent LLM baseline (superseded by agentic)
- `llm_agentic_eval.py` — Multi-agent LLM evaluation library
- `llm_multi_agent_eval.py` — Multi-agent runner (superseded)
- `llm_improved_classifier.py` — Meta-learning improved classifier
- `llm_improved_baseline.py` — Improved baseline runner
- `llm_precision_classifier.py` — Precision filtering (failed experiment, all strategies ΔF1=-0.080)
- `llm_error_analysis.py` — LLM error analysis
- `llm_deep_error_analysis.py` — Deep error analysis
- `llm_fix_simulation.py` — Fix impact simulation
- `llm_failure_mode_analysis.py` — Failure mode analysis
- Reports: `LLM_BASELINE.md`, `LLM_BETTER_SOLUTIONS.md`, `LLM_DEEP_ERROR_ANALYSIS.md`, `LLM_FIX_SIMULATION.md`, `LLM_IMPROVED_BASELINE.md`, `LLM_IMPROVED_CLASSIFIER.md`, `LLM_PRECISION_CLASSIFIER.md`

### F. SWATTR LLM Filters (6 scripts, 2 reports)

LLM-based post-filters for SWATTR SAD-SAM results.

- `swattr_llm_fewshot.py` — Few-shot LLM filter library
- `swattr_llm_zeroshot.py` — Zero-shot LLM filter (failed experiment)
- `swattr_fn_leakage_test.py` — FN leakage testing
- `swattr_variance_test.py` — Variance testing (5-run)
- `swattr_quick_variance.py` — Quick variance check
- `swattr_extended_variance.py` — Extended variance analysis
- Reports: `SWATTR_LLM_FEWSHOT.md`, `SWATTR_LLM_ZEROSHOT.md` (outdated)

### G. SWATTR Empirical Analysis (6 scripts, 4 reports, 1 data file)

Empirical analysis of SWATTR SAD-SAM behavior.

- `swattr_ablation_study.py` — Ablation study
- `swattr_sad_sam_error_analysis.py` — SAD-SAM error analysis
- `swattr_signal_analysis.py` — Signal analysis
- `swattr_tp_fp_analysis.py` — TP/FP pattern analysis
- `swattr_semantic_analysis.py` — Semantic analysis
- `swattr_zeroshot_analysis.py` — Zero-shot analysis
- Reports: `SWATTR_ABLATION_STUDY.md`, `SWATTR_TP_FP_ANALYSIS.md`, `SWATTR_SEMANTIC_ANALYSIS.md`, `SWATTR_ZEROSHOT_ANALYSIS.md`
- Data: `swattr_ablation_results.json`

### H. System Comparisons (4 scripts, 5 reports)

Cross-system performance comparisons.

- `three_system_comparison.py` — 3-system comparison (superseded by four)
- `four_system_comparison.py` — 4-system comparison
- `transarc_vs_v23e_comparison.py` — TransArc vs v23e (superseded by v24)
- `transarc_vs_v24_comparison.py` — TransArc vs v24
- Reports: `THREE_SYSTEM_COMPARISON.md`, `FOUR_SYSTEM_COMPARISON.md`, `TRANSARC_VS_V22_COMPARISON.md`, `TRANSARC_VS_V23E_COMPARISON.md`, `TRANSARC_VS_V24_COMPARISON.md`

### I. Sentence Classification (11 scripts, 1 report, 2 data files)

Sentence-level classification experiments.

- `sentence_classification/` — Entire directory

### J. Superseded Scripts

- `doc_structure_analysis.py` — Superseded by `doc_structure_analysis_v2.py` (kept in root)

### K. LLM Data Directories

Cached LLM classification outputs and API response caches.

- `llm_classifications/` — Single-agent classifications
- `llm_classifications_multi/` — Multi-agent classifications
- `llm_classifications_improved/` — Improved classifier outputs
- `llm_classifications_precision/` — Precision classifier outputs
- `llm_cache_swattr/` — SWATTR LLM API cache (gitignored)
