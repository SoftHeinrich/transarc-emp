# SAD-SAM Holistic Comparison — s_linker11 / s_linker13f / s_linker15 / TransArc

Source: `src/transarc/sadsam_comparison.py`. Reuses the canonical architecture-aware metric suite (`metrics_api.compute_sad_sam_metrics`, `new_metrics_analysis`).

## Why these metrics (and why no file/decision/weighted split)

SAD-SAM gold is atomic `(modelElementID, sentence)` pairs — **no directory enrollment** — so the SAD-CODE levels file/decision/weighted/component all collapse to **Link F1**. The informative views are instead *architecture- and doc-structure-aware*:

- **Sentence F1** — per-sentence correctness (doc structure axis).
- **Component F1** — per-component correctness (architecture axis; ids→names).
- **MCC** — correlation over the full (sentence × component) space, crediting true negatives (the architecture model + document supply the negative space).
- **MAP** — ranking quality of confidence-ordered links.
- **HUS** (usefulness) — harmonic mean of per-sentence *coverage* (gold sentences with ≥1 hit) and *purity* (predicted sentences with 0 FPs).

## Link F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.694** | **0.984** | **0.984** | **0.918** | **0.951** |
| teastore | **0.851** | **0.915** | **1.000** | **0.964** | **0.964** |
| teammates | **0.710** | **0.851** | **0.947** | **0.825** | **0.914** |
| bigbluebutton | **0.793** | **0.959** | **0.821** | **0.776** | **0.835** |
| jabref | **0.947** | **0.973** | **1.000** | **0.973** | **0.973** |
| **AVG** | **0.799** | **0.937** | **0.951** | **0.891** | **0.927** |

## Sentence F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.727** | **1.000** | **0.982** | **0.943** | **0.982** |
| teastore | **0.821** | **0.939** | **1.000** | **0.958** | **0.958** |
| teammates | **0.703** | **0.835** | **0.957** | **0.838** | **0.936** |
| bigbluebutton | **0.876** | **0.979** | **0.891** | **0.842** | **0.913** |
| jabref | **1.000** | **0.952** | **1.000** | **0.952** | **0.952** |
| **AVG** | **0.825** | **0.941** | **0.966** | **0.907** | **0.948** |

## Component F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.694** | **0.984** | **0.984** | **0.918** | **0.951** |
| teastore | **0.851** | **0.915** | **1.000** | **0.964** | **0.964** |
| teammates | **0.710** | **0.851** | **0.947** | **0.825** | **0.914** |
| bigbluebutton | **0.793** | **0.959** | **0.821** | **0.776** | **0.835** |
| jabref | **0.947** | **0.973** | **1.000** | **0.973** | **0.973** |
| **AVG** | **0.799** | **0.937** | **0.951** | **0.891** | **0.927** |

## MCC

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.711** | **0.984** | **0.984** | **0.914** | **0.949** |
| teastore | **0.857** | **0.916** | **1.000** | **0.964** | **0.964** |
| teammates | **0.714** | **0.856** | **0.946** | **0.825** | **0.912** |
| bigbluebutton | **0.792** | **0.958** | **0.821** | **0.771** | **0.832** |
| jabref | **0.933** | **0.965** | **1.000** | **0.965** | **0.965** |
| **AVG** | **0.801** | **0.936** | **0.950** | **0.888** | **0.924** |

## MAP

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.574** | **1.000** | **1.000** | **0.907** | **0.963** |
| teastore | **0.696** | **1.000** | **1.000** | **1.000** | **1.000** |
| teammates | **0.800** | **0.722** | **0.956** | **0.922** | **0.933** |
| bigbluebutton | **0.709** | **0.955** | **0.791** | **0.767** | **0.819** |
| jabref | **0.950** | **1.000** | **1.000** | **1.000** | **1.000** |
| **AVG** | **0.746** | **0.935** | **0.949** | **0.919** | **0.943** |

## HUS

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.727** | **0.981** | **0.982** | **0.924** | **0.982** |
| teastore | **0.821** | **0.894** | **1.000** | **0.958** | **0.958** |
| teammates | **0.651** | **0.835** | **0.957** | **0.827** | **0.925** |
| bigbluebutton | **0.844** | **0.979** | **0.881** | **0.821** | **0.881** |
| jabref | **0.889** | **0.952** | **1.000** | **0.952** | **0.952** |
| **AVG** | **0.786** | **0.928** | **0.964** | **0.897** | **0.940** |
