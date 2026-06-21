# Motivation — Trivial Baselines Exploit the Inequality

> Gold-only. A content-blind Top-3 (most-gold-linked) baseline scores a high file-/link-level micro-F1 *because* a few large components own most of the gold mass; the four-metric suite exposes it. No system results are used; randomness is seeded (0).

## sad-code — Top-3 micro-F1 0.353 vs random 0.149 (2.4× random)

| Baseline | micro-F1 | per-comp macro F1 | coverage | noise | file F1 |
|----------|----------|-------------------|----------|-------|---------|
| top3 | 0.353 | 0.186 | 0.486 | 0.762 | 0.353 |
| random | 0.149 | 0.243 | 0.659 | 0.852 | 0.149 |
| gold | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## sad-sam — Top-3 micro-F1 0.381 vs random 0.206 (1.9× random)

| Baseline | micro-F1 | per-comp macro F1 | coverage | noise |
|----------|----------|-------------------|----------|-------|
| top3 | 0.381 | 0.185 | 0.629 | 0.720 |
| random | 0.206 | 0.200 | 0.274 | 0.803 |
| gold | 1.000 | 1.000 | 1.000 | 0.000 |

**Reading:** Top-3 posts a respectable micro-F1 (≈2× random) but a far lower **per-component macro F1** (~0.19 vs a micro of ~0.35-0.38) — it nails the few popular components and scores ~0 on the long tail of small ones. The large micro−macro gap, not micro-F1 itself, is the tell: micro-F1 alone cannot separate this content-blind baseline from a real-but-weak linker; per-component F1 (plus coverage and noise rate) can.

## Why each suite metric is needed (driver → metric)

| Inequality driver | Metric it motivates | What it catches |
|-------------------|---------------------|-----------------|
| Enrollment inflation (1.0×→217.6×) | **file-level F1** | a few directory decisions dominate the score — report it but caveat it |
| Component concentration (files-per-component Gini 0.400→0.694) | **per-component macro F1** | size-blind: small components count as much as the giants |
| Long-tail per-sentence distribution (Gini 0.331→0.645) | **sentence coverage** | exposes whether the tail of sentences is covered at all |
| Narrative / non-link sentences | **noise rate** | penalises false positives on the large non-link-bearing part of the doc |

## Resolved placeholder (intro.tex:64)

- **Trivial-baseline file-level F1** = **0.353** (gold-only Top-3 popularity baseline, sad-code, avg over 5 projects). This is the trivial baseline that the standard \fone lets look competitive.

- *Deferred → Phase 3+ (need published system scores):* strongest-published-pipeline file F1; \approach file F1 + improvement pp.

