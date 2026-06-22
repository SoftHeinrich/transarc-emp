# SAD-CODE Holistic Comparison — s_linker11 / s_linker13f / s_linker15 / TransArc

Source: `src/transarc/sadcode_comparison.py`. Reuses the canonical metric suite (`metrics_api.compute_sad_code_metrics`, `evaluation_critique`, `new_metrics_analysis`). s11/s13f/s15 SAD-CODE = SAD-SAM × ARCOTL SAM-CODE (same composition as the s12c comparator); TransArc = full-pipeline output.

## Metric levels

Unlike SAD-SAM, SAD-CODE gold has **directory enrollment** (525 raw → 18,660 files), so the multi-level split is informative — the levels *diverge*:

- **File F1** — enrollment-inflated raw (sentence, file).
- **Decision F1** — de-inflated to human gold entries (≥50% files hit).
- **Component F1** — collapsed to (sentence, component_name).
- **Weighted F1** — file weighted by 1/block_size.
- **ACF1** — amplification-corrected (1/N component weighting).
- **MCC / NDG / HUS** — architecture-aware correlation / discrimination / usefulness.

## File F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.588** | **0.912** | **0.929** | **0.899** | **0.879** |
| teastore | **0.829** | **0.948** | **1.000** | **0.989** | **0.997** |
| teammates | **0.821** | **0.785** | **0.864** | **0.784** | **0.865** |
| bigbluebutton | **0.831** | **0.879** | **0.864** | **0.742** | **0.848** |
| jabref | **0.943** | **0.985** | **1.000** | **0.985** | **0.985** |
| **AVG** | **0.803** | **0.902** | **0.931** | **0.880** | **0.915** |

## Decision F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.568** | **0.909** | **0.926** | **0.895** | **0.874** |
| teastore | **0.824** | **0.864** | **1.000** | **0.952** | **0.972** |
| teammates | **0.564** | **0.498** | **0.582** | **0.502** | **0.579** |
| bigbluebutton | **0.629** | **0.647** | **0.655** | **0.593** | **0.642** |
| jabref | **0.394** | **0.608** | **0.950** | **0.608** | **0.608** |
| **AVG** | **0.596** | **0.705** | **0.822** | **0.710** | **0.735** |

## Component F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.642** | **0.972** | **0.986** | **0.957** | **0.941** |
| teastore | **0.828** | **0.899** | **1.000** | **0.967** | **0.983** |
| teammates | **0.648** | **0.459** | **0.557** | **0.546** | **0.562** |
| bigbluebutton | **0.574** | **0.599** | **0.627** | **0.556** | **0.607** |
| jabref | **0.880** | **0.898** | **0.917** | **0.898** | **0.898** |
| **AVG** | **0.714** | **0.765** | **0.817** | **0.785** | **0.798** |

## Weighted F1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.568** | **0.909** | **0.926** | **0.895** | **0.874** |
| teastore | **0.824** | **0.864** | **1.000** | **0.952** | **0.972** |
| teammates | **0.562** | **0.500** | **0.579** | **0.500** | **0.576** |
| bigbluebutton | **0.623** | **0.642** | **0.650** | **0.589** | **0.638** |
| jabref | **0.394** | **0.608** | **0.950** | **0.608** | **0.608** |
| **AVG** | **0.594** | **0.705** | **0.821** | **0.709** | **0.734** |

## ACF1

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.739** | **0.955** | **0.950** | **0.936** | **0.916** |
| teastore | **0.851** | **0.915** | **1.000** | **0.964** | **0.964** |
| teammates | **0.624** | **0.537** | **0.635** | **0.606** | **0.634** |
| bigbluebutton | **0.347** | **0.323** | **0.397** | **0.327** | **0.369** |
| jabref | **0.857** | **0.878** | **0.900** | **0.878** | **0.878** |
| **AVG** | **0.684** | **0.722** | **0.776** | **0.742** | **0.752** |

## MCC

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.630** | **0.909** | **0.927** | **0.898** | **0.879** |
| teastore | **0.813** | **0.936** | **1.000** | **0.986** | **0.996** |
| teammates | **0.801** | **0.786** | **0.857** | **0.757** | **0.857** |
| bigbluebutton | **0.806** | **0.862** | **0.844** | **0.704** | **0.825** |
| jabref | **0.902** | **0.974** | **1.000** | **0.974** | **0.974** |
| **AVG** | **0.790** | **0.893** | **0.926** | **0.864** | **0.906** |

## NDG

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.516** | **0.897** | **0.916** | **0.881** | **0.857** |
| teastore | **0.806** | **0.941** | **1.000** | **0.987** | **0.997** |
| teammates | **0.927** | **0.883** | **0.979** | **0.882** | **0.980** |
| bigbluebutton | **0.850** | **0.903** | **0.886** | **0.753** | **0.869** |
| jabref | **0.915** | **0.977** | **1.000** | **0.977** | **0.977** |
| **AVG** | **0.803** | **0.920** | **0.956** | **0.896** | **0.936** |

## HUS

| dataset | TransArc | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|
| mediastore | **0.762** | **0.980** | **0.980** | **0.960** | **0.960** |
| teastore | **0.821** | **0.894** | **1.000** | **0.958** | **0.958** |
| teammates | **0.591** | **0.500** | **0.623** | **0.591** | **0.613** |
| bigbluebutton | **0.405** | **0.438** | **0.427** | **0.403** | **0.430** |
| jabref | **0.667** | **0.706** | **0.750** | **0.706** | **0.706** |
| **AVG** | **0.649** | **0.703** | **0.756** | **0.724** | **0.733** |
