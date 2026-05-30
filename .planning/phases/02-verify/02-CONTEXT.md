# Phase 2: Verify - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning
**Mode:** Infrastructure/verification phase — minimal discuss (technical success criteria only)

<domain>
## Phase Boundary

Confirm both pillars run reproducibly after the Phase 1 moves: every retained pillar
script executes end-to-end without import/path errors and (re)writes its report. The
shared `src/lib/` loader layer must be importable from both `src/transarc/` and `src/bias/`.

Out of scope: changing analysis logic, the paper (Phase 3), fixing any pre-existing
numerical issues unrelated to the move (only move-induced breakage is in scope).
</domain>

<decisions>
## Implementation Decisions

### Definition of "runs reproducibly"
- A script passes if `python3 src/<pillar>/<script>.py` exits 0 AND its report artifact
  in `reports/` exists with a refreshed mtime (or is unchanged-but-present for scripts
  that print to stdout only).
- Run from the repo root (`cd transarc-emp`), Python 3 (3.13 per existing pycache).

### Scope of scripts to verify (13 total)
- Pillar 1 (`src/transarc/`): sad_sam_actual_contribution, sad_sam_tp_gain_analysis,
  sam_code_cascade_analysis, s12c_sadcode_comparison.
- Pillar 2 (`src/bias/`): benchmark_bias_study, enrollment_bias_analysis,
  enrollment_distortion_analysis, sam_code_distribution_analysis, evaluation_critique,
  creative_metrics_analysis, holistic_metrics_analysis, extreme_baseline_analysis,
  stupid_baseline_analysis.

### Failure handling
- If a script fails ONLY due to the Phase 1 move (broken import/path), fix the path
  (in scope). If it fails for a pre-existing reason (missing input data, prior bug),
  record it as a known issue — do NOT alter analysis logic to force a pass.

### Claude's Discretion
- Execution order, per-script timeout, how outputs are captured/logged.
</decisions>

<code_context>
## Existing Code Insights

### Inputs each script reads
- Shared loader `src/lib/transarc_error_analysis.py` (PROJECTS, loaders, calc_metrics).
- Benchmark data: `/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark/`
  (5 projects: bigbluebutton, jabref, mediastore, teammates, teastore) — confirmed present.
- `results/<project>/<task>/` run outputs in-repo — confirmed present (mount stat is flaky;
  real python reads succeed).

### Smoke test (pre-plan)
- `src/transarc/sad_sam_actual_contribution.py` → exit 0.
- `src/bias/benchmark_bias_study.py` → exit 0.
  Both confirm the `parent.parent/lib` import resolves from the new pillar dirs.

### Environment caveat
- Hostshare mount: shell `ls`/`test -d` and command output are unreliable (doubling,
  truncation, transient ENOENT, cwd resets). Real python script I/O works. Prefer running
  scripts with output redirected to a log file and checking exit codes; avoid trusting a
  single porcelain `git status` — refresh first.
</code_context>

<specifics>
## Specific Ideas

- Capture each run's exit code + tail of stdout/stderr into a per-script log; summarize
  pass/fail in the SUMMARY. Verify `reports/` artifacts present after the batch.
</specifics>

<deferred>
## Deferred Ideas

- Per-pillar reproduce scripts / Makefile (DOC-02, v2).
- Pinning Python/deps (stdlib-only today, low risk).
</deferred>
