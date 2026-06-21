# Consequences of Misleading \fone Across SAD-SAM and SAD-CODE

> **[SUPERSEDED — v1.2]** The SAD-CODE Component F1 figures in this report (e.g. Average 0.714) use the pre-v1.2 `{b}`-fallback component universe and are **superseded by mapped-only universe (v1.2)**: SAD-CODE component F1 now drops files with no SAM-CODE mapping, moving the swattr/transarc cross-project average from 0.714 to 0.795. The regenerated `writing/tables/consequences.tex` already reflects the new number. See `reports/COMPONENT_UNIVERSE_RECONCILIATION.md` for the measured old→new delta and the full supersession ledger. Original content is retained unchanged below.

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

## A Converged Decision+Component Framework (STUDY-03)

The two tasks distort in different ways — \sadsam through the sentence/quality gap, \sadcode through enrollment inflation — but they share ONE honest axis: **Decision-level + Component-level** \fone. This converged view is layered *atop* the existing corrected metrics; it does not replace them.

Mapping the axis onto each task:

- **\sadsam**: *decision* == the link itself, `(modelElementID, sentence)` (no enrollment inflation); *component* == aggregate by model element.
- **\sadcode**: *decision* == the raw pre-enrollment `(sentence, dir-or-file)` decision; *component* == aggregate by architecture component.

| Task | Headline F1 | Headline metric | Decision F1 | Component F1 | Headline−Decision Δ |
|------|-------------|-----------------|-------------|--------------|---------------------|
| SAD-SAM | 0.799 | link | 0.799 | 0.799 | 0.000 |
| SAD-CODE | 0.803 | file | 0.596 | 0.714 | 0.207 |

For \sadsam the headline link \fone (0.799) already coincides with the decision granularity (Δ = 0.000), so its distortion is the sentence/quality disagreement shown above, *not* enrollment. For \sadcode the file headline (0.803) sits 0.207 above the honest decision \fone (0.596) — the enrollment gap.

Ranking disagreement under \sadcode: of the 5 projects, **3/5** change their relative standing between file \fone and decision \fone — concretely, JabRef ranks #1 by file but #5 by decision.

Under the converged Decision+Component axis, the two tasks tell one coherent story: report Decision and Component \fone alongside any headline number. This converged view *extends* (does not replace) the corrected metrics in `reports/EVALUATION_CRITIQUE.md` and `reports/NEW_METRICS_REPORT.md`.

