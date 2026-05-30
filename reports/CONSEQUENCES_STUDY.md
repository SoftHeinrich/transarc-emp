# Consequences of Misleading \fone Across SAD-SAM and SAD-CODE

*Motivation evidence (Pillar 2): how a single headline \fone distorts BOTH TLR tasks, and the converged Decision+Component axis that tells one coherent story. All numbers read from the Phase-4 metrics CSVs; no metric recomputed.*

## SAD-SAM: What the Single Headline Link \fone Hides (STUDY-01)

The reported \sadsam number is a single link \fone over `(modelElementID, sentence)` pairs. That headline already sits at the honest decision granularity (no enrollment inflation), so its distortion is *not* file-level amplification — it is the gap against the per-sentence retrieval view and the quality-oriented views (MCC/MAP/HUS).

| Project | Link F1 (headline) | Sentence F1 | Component F1 | MCC | MAP | HUS | Link−Sentence Δ |
|---------|--------------------|-------------|--------------|-----|-----|-----|-----------------|
| mediastore | 0.694 | 0.744 | 0.694 | 0.711 | 0.574 | 0.727 | -0.050 |
| teastore | 0.851 | 0.821 | 0.851 | 0.857 | 0.696 | 0.821 | 0.030 |
| teammates | 0.710 | 0.916 | 0.710 | 0.714 | 0.800 | 0.651 | -0.206 |
| bigbluebutton | 0.793 | 0.897 | 0.793 | 0.792 | 0.709 | 0.844 | -0.104 |
| jabref | 0.947 | 1.000 | 0.947 | 0.933 | 0.950 | 0.889 | -0.053 |
| **Average** | 0.799 | 0.875 | 0.799 | 0.801 | 0.746 | 0.786 | -0.076 |

The largest disagreement is **teammates**: sentence \fone 0.916 versus link \fone 0.710 — the headline understates per-sentence retrieval by ~0.206. Across all projects the average sentence \fone (0.875) sits 0.076 above the headline link \fone (0.799).

The quality-oriented views diverge further: MCC (avg 0.801) and HUS (avg 0.786) reward correct rejections and human-usefulness that link \fone ignores, while MAP (avg 0.746) is a ranking view. The single \sadsam headline link \fone hides disagreement with the sentence-, component-, and quality-oriented (MCC/MAP/HUS) perspectives — even before any cascade into \sadcode.

## SAD-CODE: How File-Level Enrollment \fone Misleads (STUDY-02)

The reported \sadcode number is a file-level \fone computed *after* enrollment expands directory-level gold entries into individual files (≈35.5x inflation; see `reports/EVALUATION_CRITIQUE.md` and `reports/BENCHMARK_BIAS_STUDY.md`). The honest comparators are the raw pre-enrollment decision \fone and the architecture-component \fone. The numbers below are read directly from the Phase-4 CSV — this section consolidates prior findings and recomputes nothing.

| Project | File F1 (headline) | Decision F1 | Component F1 | File−Decision Δ |
|---------|--------------------|-------------|--------------|-----------------|
| mediastore | 0.588 | 0.568 | 0.642 | 0.020 |
| teastore | 0.829 | 0.824 | 0.828 | 0.005 |
| teammates | 0.821 | 0.564 | 0.648 | 0.257 |
| bigbluebutton | 0.831 | 0.629 | 0.574 | 0.202 |
| jabref | 0.943 | 0.394 | 0.880 | 0.549 |
| **Average** | 0.803 | 0.596 | 0.714 | 0.207 |

The flagship distortion is **JabRef**: best of all projects on file \fone (0.943) yet worst on decision \fone (0.394) — a complete ranking flip (rank #1 by file, #5 by decision). Cross-project, the headline averages 0.803 (file) while the honest views average only 0.596 (decision) and 0.714 (component) — a file−decision gap of 0.207.

These consolidate the documented enrollment-inflation critique (≈35.5x expansion of raw decisions into files, 96–100% intra-directory block homogeneity, and the pairwise ranking flips) from `reports/EVALUATION_CRITIQUE.md` and `reports/BENCHMARK_BIAS_STUDY.md`. No metric is recomputed here; the anchors are read from `reports/metrics_sad-code.csv`.

