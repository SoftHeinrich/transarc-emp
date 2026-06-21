# Artemis Provenance Ledger

*Generated doc (Phase 8, plan 08-01). Discharges 08-CONTEXT decision **D-10**.*

Three artemis-related directories coexist in this workspace. Only **one** is read by
the component suite. This ledger states which is **authoritative**, which input stays
**external (unvendored)**, and which are **secondary / superseded** — so that the
Phase-8 comparison (08-02) and scorecard (08-03) can assert deterministic regeneration.

Source of truth for what is read: `src/bias/component_suite.py`
(`ARTEMIS_LOCAL`, `ARTEMIS_DOC_CODE`, `_artemis_model`, `_artemis_code`).

## (a) AUTHORITATIVE — `results_artemis_gpt54/` (committed)

- **Path:** `results_artemis_gpt54/` — the repo-local `ARTEMIS_LOCAL` constant
  (`Path(__file__).resolve().parent.parent.parent / "results_artemis_gpt54"`).
- **Read by:** `component_suite._artemis_model(p)`, which loads
  `results_artemis_gpt54/<proj>/sad-code/sadSamTlr_<proj>.csv`
  (keys `a=(modelElementID, component_id)`, `b=(sentence)`) for all 5 projects:
  **mediastore, teastore, teammates, bigbluebutton, jabref**.
- **Status:** This is the **canonical artemis sad-code links source** for the suite and
  the Phase-8 scorecard. As of plan 08-01 it is **committed under version control**
  (25 files; was previously untracked). A fresh clone now reproduces the artemis
  sad-code rows bit-for-bit — the only artemis links input is pinned. See plan 08-01
  Task 1.

## (b) EXTERNAL — `ARTEMIS_DOC_CODE` (not vendored)

- **Path:** `ARTEMIS_DOC_CODE = /mnt/hostshare/ardoco-home/sota/recovered-links/doc-code`,
  files `artemis-<proj>-gpt-5.4.csv`.
- **Read by:** `component_suite._artemis_code(p)` (the doc-to-code side; keys
  `a=(sentence_id, sentence)`, `b=(target_id, codeId, codeID)`).
- **Status:** This is a **guarded external root** and stays **unvendored** per D-10.
  It is **not** committed to this repo. If absent, the suite degrades gracefully via the
  standardized `WARNING:` **skip-with-notice** (naming system/level/project) rather than
  hard-failing (D-08) — reproducibility is scoped to present-system rows. Present in this
  workspace today.

## (c) SECONDARY / SUPERSEDED — never read by the suite

These directories are **NOT** links sources and the suite **never reads** them. They are
retained for history but are **not authoritative**. Per the non-destructive convention
(CLAUDE.md) they are **documented-as-secondary, not deleted** — both still exist on disk.

- **`reports_artemis_gpt54_20260605_030524/`** — a derived `reports/` + `tables/` snapshot
  (~576K). A secondary/superseded reports artifact, not a links source. The suite does not
  read it.
- **`paper-result/artemis-gpt5.csv`** and **`paper-result/s20U.csv`** — a pre-computed
  `link_p` / `link_r` / `link_f1` summary. A superseded **summary**, not a links source;
  the suite recomputes from the canonical source above (via `calc_metrics`) and never reads
  these. Retained for history.

## Note on swattr ≡ transarc (D-12)

The suite reports **swattr ≡ transarc as one column** (SWATTR ⋈ ArCoTL at doc-to-code); a
distinct external SWATTR doc-to-code result is deferred this phase. This clarifies that
**artemis is the LLM contrast** (peaky-but-leaky) against the heuristic-uniform SWATTR —
which is why the artemis source pinned here matters for the comparison.

## Reproduce

```
python3 src/bias/component_suite.py
```

reads the canonical `results_artemis_gpt54/` source (committed) and the external
`ARTEMIS_DOC_CODE` root (skip-with-notice if absent) → regenerates
`reports/COMPONENT_SUITE_sad-model.csv` + `reports/COMPONENT_SUITE_sad-code.csv`.
