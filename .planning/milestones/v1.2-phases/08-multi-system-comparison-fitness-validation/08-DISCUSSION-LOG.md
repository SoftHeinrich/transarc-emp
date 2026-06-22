# Phase 8: Multi-System Comparison & Fitness Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 8-multi-system-comparison-fitness-validation
**Areas discussed:** Cleverer baseline (SC3), Scorecard shape & artifact (CMP-04), Verdict stance (honesty risk), System & data scope

---

## Cleverer baseline / comparators (SC3)

| Option | Description | Selected |
|--------|-------------|----------|
| Size-proportional exploit | New synthetic baseline assigning sentences to largest-enrollment components | |
| Lexical name-similarity | Stopwords-only token-match heuristic baseline | |
| Legacy real systems only | Use existing s11/s13f/s12c linkers as the comparators | |
| (User free-text) | "rq2 is designed for eval baselines under alink-paper / eval section, not naive baselines, should be s20union, artemis, transarc, etc" | ✓ |

**User's choice:** No new synthetic baselines. rq2's Random/Top-3 stay in their
alinker eval-section role as the trivial floor; the scorecard's real comparators are
the **systems** (s20union/s20linker, artemis, swattr/transarc).
**Notes:** Follow-up "just systems in the paper" → exclude legacy s11/s13f/s12c;
real set = the three paper systems only. (Captured as D-01..D-03.)

---

## Scorecard shape & artifact (CMP-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Numeric + new script/report | `src/bias/metric_fitness.py` → numeric score per column×axis → `reports/METRIC_FITNESS.md` + CSV + verdict | ✓ |
| Qualitative, extend COMPONENT_SUITE.md | Pass/fail/partial table appended to existing report, no new script | |
| Numeric scores, extend existing report | Numbers but appended into COMPONENT_SUITE.md | |

**User's choice:** Numeric + new standalone script/report (Recommended).
**Notes:** Mirrors the suite's script+CSV+report pattern and the Phase-7
oracle/determinism precedent. (Captured as D-04, D-05.)

---

## Verdict stance (honesty risk)

| Option | Description | Selected |
|--------|-------------|----------|
| Data-derived verdict | Report whatever the axis scores rank out, even if it weakens the macro claim | ✓ |
| Validate the pre-committed verdict | Treat headline=macro+tail / diagnostic=micro/gap as hypothesis, flag if contradicted | |

**User's choice:** Data-derived verdict (Recommended).
**Notes:** Honors the "don't oversell micro-vs-macro" constraint; verdict is earned,
not assumed. (Captured as D-06, D-07.)

---

## System & data scope

| Option | Description | Selected |
|--------|-------------|----------|
| Skip-w/notice, both levels, swattr≡transarc | Carry Phase-7 absent→warn+skip; score both levels; one swattr column; pin artemis dir | ✓ |
| Require all systems (hard-fail) | Committed scorecard errors if any external root missing | |
| sad-code only | Scope scorecard to sad-code, leave sad-model descriptive | |

**User's choice:** Skip-with-notice, both levels, swattr≡transarc as one column
(Recommended).
**Notes:** Defer chasing a distinct external SWATTR doc-to-code result; pin
`results_artemis_gpt54` as canonical artemis provenance. (Captured as D-08..D-12.)

---

## Claude's Discretion

- Exact per-axis numeric rubric (separation margin, validity headroom, stability
  variance, degeneracy saturation test), CSV column order/precision, verdict wording,
  warn-and-skip message reuse. Constraints: stdlib-only, reuse `calc_metrics` only,
  reuse suite loaders + rq2 generators. (D-13)

## Deferred Ideas

- Distinct external SWATTR doc-to-code result (open input) — keep swattr≡transarc one
  column for now.
- New synthetic/cleverer baselines (size-proportional, lexical) — rejected for this
  phase; rq2 owns the trivial-baseline role.
- Legacy linkers s11/s13f/s12c as comparators — excluded ("just systems in the paper").
- Paper integration (Phase 9, CMP-05).
- Pre-existing carry-overs: NDG non-determinism; loader rename; sam-code; `.xlsx`;
  real pdflatex.
