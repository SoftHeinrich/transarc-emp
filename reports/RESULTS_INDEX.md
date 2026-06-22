# Results Index — where to find every system's numbers (RQ1 / RQ2)

One place that says, per system and per task, **where the raw recovered links live**,
**where the scored panel lives**, and **how to regenerate it**. All systems are scored by
one tool — `transarc-emp/mini-src/metrics.py` — against the ArDoCo benchmark gold
(`ardoco/core/tests-base/src/main/resources/benchmark`), so every cell shares one metric
definition and one gold loader.

Repo roots (siblings under `ardoco-home/`): `transarc-emp/` (paper + eval infra),
`sota/recovered-links/` (normalized baseline links), `agent-linker/` (our approach, ALinker).

Tasks: **model-doc = SAD-SAM** (sentence→arch-model element), **doc-code = SAD-Code**
(sentence→code file). Dataset = 5 projects: bigbluebutton, jabref, mediastore, teammates, teastore.

---

## RQ1 — primary effectiveness panel (fill from here)

**Macro averages (n=5 unless noted). Headline F1 + the two kept secondary metrics.**

### model-doc (SAD-SAM) — link F1
| System | link F1 | sent_cov | noise |
|--------|:------:|:--------:|:-----:|
| **ALinker (claude)** | **.939** | .955 | .052 |
| **ALinker (gpt-5.4)** | **.922** | .937 | .050 |
| Artemis (gpt-5.4) | .835 | .788 | .072 |
| SWATTR | .799 | .789 | .137 |
| LiSSA (gpt-5-mini) | .425 | .839 | .603 |
| LiSSA (gpt-4o-mini) | .280 | .893 | .733 |

### doc-code (SAD-Code) — file F1 (also per-component F1)
| System | file F1 | comp F1 | sent_cov | noise |
|--------|:------:|:------:|:--------:|:-----:|
| **ALinker (claude)** | **.939** | .885 | .869 | .050 |
| **ALinker (gpt-5.4)** | **.919** | .867 | .841 | .045 |
| Artemis (gpt-5.4) | .849 | .732 | .709 | .060 |
| TransArC | .803 | .714 | .751 | .130 |
| LiSSA (gpt-5-mini) | .198 † | .210 | .839 | .810 |
| LiSSA (gpt-4o-mini) | .196 † | .194 | .874 | .818 |

† LiSSA doc-code is **3/5 projects** (mediastore, teastore, bigbluebutton; no teammates/jabref).
All other cells are 5/5.

**Scored panels (per-project CSVs):** `transarc-emp/reports/rq1/<system>_<task>.csv`
- schema sad-sam: `project,link_p,link_r,link_f1,sentence_coverage,noise_rate`
- schema sad-code: `project,file_p,file_r,file_f1,component_f1,sentence_coverage,noise_rate`

| System | reports/rq1 panel (sad-sam / sad-code) |
|--------|----------------------------------------|
| ALinker (claude) | `aalinker-claude_sad-sam.csv` / `aalinker-claude_sad-code.csv` |
| ALinker (gpt-5.4) | `aalinker-openai_sad-sam.csv` / `aalinker-openai_sad-code.csv` |
| Artemis | `artemis_sad-sam.csv` / `artemis_sad-code.csv` |
| SWATTR | `swattr_sad-sam.csv` / — |
| TransArC | — / `transarc_sad-code.csv` |
| LiSSA (gpt-5-mini) | `lissa_sad-sam.csv` / `lissa_sad-code.csv` |
| LiSSA (gpt-4o-mini) | `lissa-gpt4omini_sad-sam.csv` / `lissa-gpt4omini_sad-code.csv` |

**Regenerate all RQ1 panels:** `python3 transarc-emp/src/paper/rq1_panels.py` (reads the
raw links below, writes `reports/rq1/`).

---

## Raw recovered links (inputs to RQ1)

| System | model-doc (SAD-SAM) | doc-code (SAD-Code) |
|--------|---------------------|---------------------|
| **ALinker** | `agent-linker/results/v2.6.3/{claude,openai}/<proj>/sad-sam.csv` | `…/<proj>/sad-code.csv` |
| Artemis | `sota/recovered-links/model-doc/artemis-<proj>-gpt-5.4.csv` | `sota/recovered-links/doc-code/artemis-<proj>-gpt-5.4.csv` |
| SWATTR | `sota/recovered-links/model-doc/swattr-<proj>.csv` | — |
| TransArC | — | `sota/recovered-links/doc-code/transarc-<proj>.csv` |
| LiSSA | `sota/recovered-links/model-doc/lissa-<proj>-{gpt-5-mini,gpt-4o-mini}.csv` | `sota/recovered-links/doc-code/lissa-<proj>-{gpt-5-mini,gpt-4o-mini}.csv` |

All `sota/recovered-links/*` files are normalized (`sentence_id,target_id`, 1-based,
deduped) — see `sota/recovered-links/README.md` for provenance, normalization, and the
saved mini-src panels in `sota/recovered-links/eval/`. The `agent-linker` files are the
approach's native output (also accepted by mini-src).

---

## RQ2 — metric redundancy (fill from here)

- **Narrative + matrix:** `transarc-emp/reports/RQ2_METRIC_REDUNDANCY.md`
- **Companion analyses:** `RQ2_TRIVIAL_BASELINES.md`, `RQ2_DOC_TO_MODEL_PRESTUDY.md`,
  `RQ2_DOC_TO_MODEL_RANKING_COMPARE.md` (all in `transarc-emp/reports/`)
- **Per-cell CSVs:** `transarc-emp/reports/SADSAM_S11_S13F_VS_TRANSARC.csv`,
  `SADCODE_S11_S13F_VS_TRANSARC.csv`
- **Generator:** `transarc-emp/src/bias/rq2_metric_redundancy.py`
- Systems in the RQ2 matrix: TransArC, S11 (`s_linker11`), Random (seed 42), Top-3.
  Conclusion that motivated the kept-metric set: most of the 13-metric suite is shadowed
  (Spearman ρ ≥ 0.85, ~0 rank reversals) → mini-src keeps only the non-redundant panel.

---

## Validation (numbers confirmed correct)

- **SWATTR / TransArC**: mini-src reproduces the paper headline (~.80) and the ArDoCo
  built-in eval `TraceLinkEvaluationIT#evaluateSadSamTlrIT`/`#evaluateSadSamCodeTlrIT`
  passes **10/10** vs the packages' published `ExpectedResults`.
- **LiSSA**: mini-src reproduces `lissa-replication/results/COMPARISON.md` per-project F1
  exactly (sad-sam avg .280, gpt-4o-mini).

## Caveats (pick before finalizing the paper tables)
1. **Model pairing.** ALinker has claude + gpt-5.4 backends; Artemis is gpt-5.4; LiSSA has
   gpt-5-mini + gpt-4o-mini; SWATTR/TransArC are deterministic. Pair comparably.
2. **LiSSA doc-code = 3/5 projects** (no teammates/jabref — needs an OpenAI key to extend).
3. **SWATTR/TransArC bigbluebutton provenance = canonical** `transarc-emp/results` run
   (bbb .79/.83). A from-Central-reproducible ICSE24 run scores bbb lower (.29/.35); 4/5
   projects identical. Details in `sota/recovered-links/README.md` caveat 4.
