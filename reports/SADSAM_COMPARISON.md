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

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.694** | **0.931** | **0.951** | **0.984** | — | — | — |
| teastore | **0.851** | **0.982** | **0.981** | **0.915** | — | — | — |
| teammates | **0.710** | **0.912** | **0.862** | **0.851** | — | — | — |
| bigbluebutton | **0.793** | **0.897** | **0.815** | **0.959** | — | — | — |
| jabref | **0.947** | **0.973** | **1.000** | **0.973** | — | — | — |
| **AVG** | **0.799** | **0.939** | **0.922** | **0.937** | — | — | — |

## Component F1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.694** | **0.931** | **0.951** | **0.984** | — | — | — |
| teastore | **0.851** | **0.982** | **0.981** | **0.915** | — | — | — |
| teammates | **0.710** | **0.912** | **0.862** | **0.851** | — | — | — |
| bigbluebutton | **0.793** | **0.897** | **0.815** | **0.959** | — | — | — |
| jabref | **0.947** | **0.973** | **1.000** | **0.973** | — | — | — |
| **AVG** | **0.799** | **0.939** | **0.922** | **0.937** | — | — | — |

## Sent. coverage

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.593** | **0.926** | **0.963** | **1.000** | — | — | — |
| teastore | **0.696** | **1.000** | **0.957** | **1.000** | — | — | — |
| teammates | **0.844** | **0.956** | **0.933** | **0.733** | — | — | — |
| bigbluebutton | **0.812** | **0.896** | **0.833** | **0.979** | — | — | — |
| jabref | **1.000** | **1.000** | **1.000** | **1.000** | — | — | — |
| **AVG** | **0.789** | **0.955** | **0.937** | **0.943** | — | — | — |

## Noise rate (↓)

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.059** | **0.000** | **0.037** | **0.019** | — | — | — |
| teastore | **0.000** | **0.042** | **0.000** | **0.154** | — | — | — |
| teammates | **0.447** | **0.096** | **0.163** | **0.029** | — | — | — |
| bigbluebutton | **0.081** | **0.034** | **0.048** | **0.021** | — | — | — |
| jabref | **0.100** | **0.091** | **0.000** | **0.091** | — | — | — |
| **AVG** | **0.137** | **0.052** | **0.050** | **0.063** | — | — | — |

## Sentence F1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.727** | **0.962** | **0.963** | **1.000** | — | — | — |
| teastore | **0.821** | **0.979** | **0.978** | **0.939** | — | — | — |
| teammates | **0.703** | **0.935** | **0.894** | **0.835** | — | — | — |
| bigbluebutton | **0.876** | **0.935** | **0.889** | **0.979** | — | — | — |
| jabref | **1.000** | **0.952** | **1.000** | **0.952** | — | — | — |
| **AVG** | **0.825** | **0.952** | **0.945** | **0.941** | — | — | — |

## HUS

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.727** | **0.962** | **0.963** | **0.981** | — | — | — |
| teastore | **0.821** | **0.979** | **0.978** | **0.894** | — | — | — |
| teammates | **0.651** | **0.924** | **0.871** | **0.835** | — | — | — |
| bigbluebutton | **0.844** | **0.924** | **0.889** | **0.979** | — | — | — |
| jabref | **0.889** | **0.952** | **1.000** | **0.952** | — | — | — |
| **AVG** | **0.786** | **0.948** | **0.940** | **0.928** | — | — | — |

## MCC

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.711** | **0.930** | **0.949** | **0.984** | — | — | — |
| teastore | **0.857** | **0.981** | **0.981** | **0.916** | — | — | — |
| teammates | **0.714** | **0.910** | **0.859** | **0.856** | — | — | — |
| bigbluebutton | **0.792** | **0.896** | **0.819** | **0.958** | — | — | — |
| jabref | **0.933** | **0.965** | **1.000** | **0.965** | — | — | — |
| **AVG** | **0.801** | **0.937** | **0.922** | **0.936** | — | — | — |

## MAP

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.574** | **0.889** | **0.963** | **1.000** | — | — | — |
| teastore | **0.696** | **1.000** | **0.957** | **1.000** | — | — | — |
| teammates | **0.800** | **0.911** | **0.867** | **0.722** | — | — | — |
| bigbluebutton | **0.709** | **0.851** | **0.767** | **0.955** | — | — | — |
| jabref | **0.950** | **1.000** | **1.000** | **1.000** | — | — | — |
| **AVG** | **0.746** | **0.930** | **0.911** | **0.935** | — | — | — |
