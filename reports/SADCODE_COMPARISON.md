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

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.588** | **0.917** | **0.907** | **0.912** | — | — | — |
| teastore | **0.829** | **0.999** | **0.978** | **0.948** | — | — | — |
| teammates | **0.821** | **0.860** | **0.802** | **0.785** | — | — | — |
| bigbluebutton | **0.831** | **0.803** | **0.711** | **0.879** | — | — | — |
| jabref | **0.943** | **0.999** | **0.997** | **0.985** | — | — | — |
| **AVG** | **0.803** | **0.916** | **0.879** | **0.902** | — | — | — |

## Component F1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.642** | **0.986** | **0.971** | **0.972** | — | — | — |
| teastore | **0.828** | **0.991** | **0.982** | **0.899** | — | — | — |
| teammates | **0.716** | **0.622** | **0.601** | **0.520** | — | — | — |
| bigbluebutton | **0.832** | **0.914** | **0.833** | **0.949** | — | — | — |
| jabref | **0.957** | **0.977** | **0.930** | **0.978** | — | — | — |
| **AVG** | **0.795** | **0.898** | **0.864** | **0.864** | — | — | — |

## Sent. coverage

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.640** | **1.000** | **0.960** | **1.000** | — | — | — |
| teastore | **0.696** | **1.000** | **0.957** | **1.000** | — | — | — |
| teammates | **0.598** | **0.457** | **0.446** | **0.337** | — | — | — |
| bigbluebutton | **0.822** | **0.889** | **0.800** | **0.978** | — | — | — |
| jabref | **1.000** | **0.900** | **0.900** | **1.000** | — | — | — |
| **AVG** | **0.751** | **0.849** | **0.812** | **0.863** | — | — | — |

## Noise rate (↓)

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.059** | **0.000** | **0.000** | **0.024** | — | — | — |
| teastore | **0.000** | **0.042** | **0.000** | **0.133** | — | — | — |
| teammates | **0.299** | **0.068** | **0.111** | **0.013** | — | — | — |
| bigbluebutton | **0.211** | **0.182** | **0.218** | **0.186** | — | — | — |
| jabref | **0.082** | **0.000** | **0.003** | **0.091** | — | — | — |
| **AVG** | **0.130** | **0.058** | **0.066** | **0.089** | — | — | — |

## HUS

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.762** | **1.000** | **0.980** | **0.980** | — | — | — |
| teastore | **0.821** | **0.979** | **0.978** | **0.894** | — | — | — |
| teammates | **0.591** | **0.608** | **0.588** | **0.500** | — | — | — |
| bigbluebutton | **0.405** | **0.432** | **0.417** | **0.438** | — | — | — |
| jabref | **0.667** | **0.687** | **0.687** | **0.706** | — | — | — |
| **AVG** | **0.649** | **0.741** | **0.730** | **0.703** | — | — | — |

## NDG

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.530** | **0.906** | **0.894** | **0.900** | — | — | — |
| teastore | **0.806** | **0.998** | **0.975** | **0.941** | — | — | — |
| teammates | **0.927** | **0.974** | **0.904** | **0.883** | — | — | — |
| bigbluebutton | **0.850** | **0.820** | **0.720** | **0.903** | — | — | — |
| jabref | **0.915** | **0.999** | **0.996** | **0.977** | — | — | — |
| **AVG** | **0.806** | **0.939** | **0.898** | **0.921** | — | — | — |

## Decision F1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.568** | **0.914** | **0.904** | **0.909** | — | — | — |
| teastore | **0.824** | **0.986** | **0.986** | **0.864** | — | — | — |
| teammates | **0.564** | **0.583** | **0.496** | **0.498** | — | — | — |
| bigbluebutton | **0.629** | **0.640** | **0.593** | **0.647** | — | — | — |
| jabref | **0.394** | **0.923** | **0.897** | **0.608** | — | — | — |
| **AVG** | **0.596** | **0.809** | **0.775** | **0.705** | — | — | — |

## Weighted F1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.568** | **0.914** | **0.904** | **0.909** | — | — | — |
| teastore | **0.824** | **0.986** | **0.986** | **0.864** | — | — | — |
| teammates | **0.562** | **0.581** | **0.493** | **0.500** | — | — | — |
| bigbluebutton | **0.623** | **0.636** | **0.589** | **0.642** | — | — | — |
| jabref | **0.394** | **0.923** | **0.897** | **0.608** | — | — | — |
| **AVG** | **0.594** | **0.808** | **0.774** | **0.705** | — | — | — |

## ACF1

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.739** | **0.948** | **0.953** | **0.955** | — | — | — |
| teastore | **0.851** | **0.982** | **0.981** | **0.915** | — | — | — |
| teammates | **0.624** | **0.630** | **0.597** | **0.537** | — | — | — |
| bigbluebutton | **0.347** | **0.346** | **0.344** | **0.323** | — | — | — |
| jabref | **0.857** | **0.872** | **0.821** | **0.878** | — | — | — |
| **AVG** | **0.684** | **0.756** | **0.739** | **0.722** | — | — | — |

## MCC

| dataset | TransArc | s_linker19 (Claude) | s_linker19 (GPT-5.4) | s_linker11 | s_linker13f | s15_gpt | s15_claude |
|---|---|---|---|---|---|---|---|
| mediastore | **0.630** | **0.918** | **0.908** | **0.909** | — | — | — |
| teastore | **0.813** | **0.998** | **0.973** | **0.936** | — | — | — |
| teammates | **0.801** | **0.852** | **0.784** | **0.786** | — | — | — |
| bigbluebutton | **0.806** | **0.775** | **0.672** | **0.862** | — | — | — |
| jabref | **0.902** | **0.999** | **0.995** | **0.974** | — | — | — |
| **AVG** | **0.790** | **0.908** | **0.866** | **0.893** | — | — | — |
