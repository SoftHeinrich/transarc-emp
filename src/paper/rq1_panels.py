#!/usr/bin/env python3
"""Regenerate the RQ1 primary-panel CSVs through the mini-src eval infra.

One consistent scorer (``mini-src/metrics.py``) over every RQ1 system, so the
whole panel shares one metric definition and one gold-standard loader. Every
baseline is read from the normalized recovered links under
``sota/recovered-links/``:

  * SWATTR  (sad-sam)       : 5/5 — deterministic
  * TransArc (sad-code)     : 5/5 — deterministic
  * Artemis (gpt-5.4)       : 5/5 on both tasks
  * LiSSA   (gpt-5-mini)    : 5/5 sad-sam, 3/5 sad-code (no teammates/jabref);
                              gpt-4o-mini variant emitted alongside for record
  * \\approach{} (aalinker)  -> llm-sad-sam-v45/results/v2.6.3/<backend>/<proj>/
                              Claude and GPT (OpenAI) backends.

\\approach{} aalinker is the **s_linker19 (v2.6.3)** baseline used here as a
*placeholder* for the canonical s_linker20_union (s20U) RQ1 numbers, whose raw
per-run link CSVs are not present on this mount (the ``agent-linker`` results
tree is absent; only logs + rendered tables survive). When s20U links return,
only the ``aalinker-*`` roots below need repointing — the scoring path is
already the canonical one:

  * sad-sam : the v2.6.3 SAD-SAM link CSV scored directly.
  * sad-code: each SAD-SAM link composed with ArCoTL's **recovered** SAM->code
    links (``transarc-emp/results/<proj>/sam-code/samCodeTlr_<proj>.csv``), the
    same footing as the TransArC / Artemis baselines (recovered SAD-SAM o
    recovered ArCoTL SAM->code) — NOT the bundled direct ``sad-code.csv`` and
    NOT gold SAM->code. This mirrors ``gen_s20u_rq1_tables.py`` exactly.

SWATTR/TransArc are deterministic, dumped from the self-contained ICSE24 package
(``sota/baseline-repos/transarc-icse24``, via ``RawLinkDumpIT`` — builds from
Maven Central, unlike the TAAS25 tooling which needs an unpublished NER snapshot)
and normalized into ``sota-recovered-links/``. Scoring them here reproduces the
legacy ``reports/{swattr_rq1_d2m,transarc_rq1_d2c}.csv`` exactly across all five
projects (macro SWATTR link F1 .799, TransArc file F1 .803).

Output: one panel CSV per (system, task) under reports/rq1/, schema = the
mini-src primary panel (sad-sam: link P/R/F1, sent_cov, noise; sad-code: file
P/R/F1, comp F1, sent_cov, noise), with a trailing Average row.

Stdlib only; imports mini-src/metrics.py by path (no other src/ modules).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent                  # transarc-emp/src/paper
_REPO = _HERE.parents[1]                                  # transarc-emp
_ARDOCO_HOME = _REPO.parent                               # ardoco-home
OUT_DIR = _REPO / "reports" / "rq1"

# ── Import mini-src/metrics.py as a module ────────────────────────────────────
_MINI = _REPO / "mini-src" / "metrics.py"
_spec = importlib.util.spec_from_file_location("mini_metrics", _MINI)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

RECOVERED = _ARDOCO_HOME / "sota-recovered-links"
V263 = _ARDOCO_HOME / "llm-sad-sam-v45" / "results" / "v2.6.3"
SAMCODE = _REPO / "results"          # recovered ArCoTL SAM->code maps live here

# System -> {task -> (root, "{project}" filename pattern)}.  A project whose file
# is absent is skipped with a WARNING (mini-src.load_result returns empty set).
SYSTEMS = {
    # Deterministic ICSE24 baselines (SWATTR = SAD-SAM only, TransArc = SAD-Code only).
    "swattr": {
        "sad-sam":  (RECOVERED, "model-doc/swattr-{project}.csv"),
    },
    "transarc": {
        "sad-code": (RECOVERED, "doc-code/transarc-{project}.csv"),
    },
    "artemis": {
        "sad-sam":  (RECOVERED, "model-doc/artemis-{project}-gpt-5.4.csv"),
        "sad-code": (RECOVERED, "doc-code/artemis-{project}-gpt-5.4.csv"),
    },
    # Canonical LiSSA = gpt-5-mini (paired with Artemis gpt-5.4 per
    # recovered-links/README.md). gpt-4o-mini emitted below for the record.
    "lissa": {
        "sad-sam":  (RECOVERED, "model-doc/lissa-{project}-gpt-5-mini.csv"),
        "sad-code": (RECOVERED, "doc-code/lissa-{project}-gpt-5-mini.csv"),
    },
    "lissa-gpt4omini": {
        "sad-sam":  (RECOVERED, "model-doc/lissa-{project}-gpt-4o-mini.csv"),
        "sad-code": (RECOVERED, "doc-code/lissa-{project}-gpt-4o-mini.csv"),
    },
    # aalinker sad-code is transitive: SAD-SAM links (read from the same
    # sad-sam.csv) composed with recovered ArCoTL SAM->code (mode="transitive").
    "aalinker-claude": {
        "sad-sam":  (V263 / "claude", "{project}/sad-sam.csv"),
        "sad-code": (V263 / "claude", "{project}/sad-sam.csv", "transitive"),
    },
    "aalinker-openai": {
        "sad-sam":  (V263 / "openai", "{project}/sad-sam.csv"),
        "sad-code": (V263 / "openai", "{project}/sad-sam.csv", "transitive"),
    },
}


def arcotl_map(project):
    """ae_id -> {normalized code path} from recovered ArCoTL SAM->code."""
    path = SAMCODE / project / "sam-code" / f"samCodeTlr_{project}.csv"
    m = {}
    if path.exists():
        import csv
        with open(path) as f:
            for r in csv.DictReader(f):
                m.setdefault(r["sentenceID"], set()).add(M.normalize_path(r["codeID"]))
    return m


def score(system: str, task: str, root: Path, pattern: str, mode: str = "direct"):
    compute = M.compute_sad_code if task == "sad-code" else M.compute_sad_sam
    rows = []
    for project in M.PROJECTS:
        path = root / pattern.format(project=project)
        if mode == "transitive":
            # sad-code = recovered SAD-SAM o recovered ArCoTL SAM->code.
            # `path` holds the SAD-SAM links (component_id, sentence).
            sadsam = M.load_result(path, "sad-sam")
            amap = arcotl_map(project)
            res = {(s, code) for (c, s) in sadsam for code in amap.get(c, ())}
        else:
            res = M.load_result(path, task)
        if not res:
            print(f"  WARNING: no {task} links for {system}/{project} "
                  f"({path}); skipping", file=sys.stderr)
            continue
        rows.append(compute(project, res))
    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []
    for system, tasks in SYSTEMS.items():
        for task, spec in tasks.items():
            root, pattern = spec[0], spec[1]
            mode = spec[2] if len(spec) > 2 else "direct"
            rows = score(system, task, root, pattern, mode)
            out = OUT_DIR / f"{system}_{task}.csv"
            M.write_csv(task, rows, out)
            f1key = "file_f1" if task == "sad-code" else "link_f1"
            avg = (sum(r[f1key] for r in rows) / len(rows)) if rows else 0.0
            summary.append((system, task, len(rows), avg, out))
            print(f"[rq1-panels] {system:18s} {task:9s} "
                  f"projects={len(rows)}/5  macro_{f1key}={avg:.4f}  -> {out}")
    print("\nwrote", len(summary), "panel CSVs to", OUT_DIR)


if __name__ == "__main__":
    main()
