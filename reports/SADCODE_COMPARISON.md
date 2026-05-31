# SAD-CODE Holistic Comparison — s_linker11 / s_linker13f / TransArc

Source: `src/transarc/sadcode_comparison.py`. Reuses the canonical metric suite (`metrics_api.compute_sad_code_metrics`, `evaluation_critique`, `new_metrics_analysis`). s11/s13f SAD-CODE = their SAD-SAM × ARCOTL SAM-CODE (same composition as the s12c comparator); TransArc = full-pipeline output.

## Metric levels

Unlike SAD-SAM, SAD-CODE gold has **directory enrollment** (525 raw → 18,660 files), so the multi-level split is informative — the levels *diverge*:

- **File F1** — enrollment-inflated raw (sentence, file).
- **Decision F1** — de-inflated to human gold entries (≥50% files hit).
- **Component F1** — collapsed to (sentence, component_name).
- **Weighted F1** — file weighted by 1/block_size.
- **ACF1** — amplification-corrected (1/N component weighting).
- **MCC / NDG / HUS** — architecture-aware correlation / discrimination / usefulness.

## File F1

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.588** | **0.912** | **0.929** |
| teastore | **0.829** | **0.948** | **1.000** |
| teammates | **0.821** | **0.785** | **0.864** |
| bigbluebutton | **0.831** | **0.879** | **0.864** |
| jabref | **0.943** | **0.985** | **1.000** |
| **AVG** | **0.803** | **0.902** | **0.931** |

## Decision F1

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.568** | **0.909** | **0.926** |
| teastore | **0.824** | **0.864** | **1.000** |
| teammates | **0.564** | **0.498** | **0.582** |
| bigbluebutton | **0.629** | **0.647** | **0.655** |
| jabref | **0.394** | **0.608** | **0.950** |
| **AVG** | **0.596** | **0.705** | **0.822** |

## Component F1

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.642** | **0.972** | **0.986** |
| teastore | **0.828** | **0.899** | **1.000** |
| teammates | **0.648** | **0.459** | **0.557** |
| bigbluebutton | **0.574** | **0.599** | **0.627** |
| jabref | **0.880** | **0.898** | **0.917** |
| **AVG** | **0.714** | **0.765** | **0.817** |

## Weighted F1

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.568** | **0.909** | **0.926** |
| teastore | **0.824** | **0.864** | **1.000** |
| teammates | **0.562** | **0.500** | **0.579** |
| bigbluebutton | **0.623** | **0.642** | **0.650** |
| jabref | **0.394** | **0.608** | **0.950** |
| **AVG** | **0.594** | **0.705** | **0.821** |

## ACF1

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.739** | **0.955** | **0.950** |
| teastore | **0.851** | **0.915** | **1.000** |
| teammates | **0.624** | **0.537** | **0.635** |
| bigbluebutton | **0.347** | **0.323** | **0.397** |
| jabref | **0.857** | **0.878** | **0.900** |
| **AVG** | **0.684** | **0.722** | **0.776** |

## MCC

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.630** | **0.909** | **0.927** |
| teastore | **0.813** | **0.936** | **1.000** |
| teammates | **0.801** | **0.786** | **0.857** |
| bigbluebutton | **0.806** | **0.862** | **0.844** |
| jabref | **0.902** | **0.974** | **1.000** |
| **AVG** | **0.790** | **0.893** | **0.926** |

## NDG

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.472** | **0.888** | **0.908** |
| teastore | **0.780** | **0.933** | **1.000** |
| teammates | **0.921** | **0.874** | **0.977** |
| bigbluebutton | **0.840** | **0.896** | **0.879** |
| jabref | **0.900** | **0.973** | **1.000** |
| **AVG** | **0.783** | **0.913** | **0.953** |

## HUS

| dataset | TransArc | s_linker11 | s_linker13f |
|---|---|---|---|
| mediastore | **0.762** | **0.980** | **0.980** |
| teastore | **0.821** | **0.894** | **1.000** |
| teammates | **0.591** | **0.500** | **0.623** |
| bigbluebutton | **0.405** | **0.438** | **0.427** |
| jabref | **0.667** | **0.706** | **0.750** |
| **AVG** | **0.649** | **0.703** | **0.756** |
