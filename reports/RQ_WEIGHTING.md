# Importance-Weighted F1: Combating the Enrollment Bias

**Pillar 2 (benchmark bias).** The enrollment bias is fundamentally a *weighting*
problem: file-level SAD-CODE F1 weights each gold component by how many files sit
under its enrolled directories — i.e. by **package fatness**, an implementation
accident, not architectural importance. This note recomputes a macro F1 over the
*same* per-component F1s under four aggregation weights and asks two questions:

1. Does the weight choice change **which system wins**?
2. Which annotation-free importance signals are **necessary** as weights?

## Method

Per-component F1 comes from `component_suite._code_inputs` (set-overlap F1 on the
mapped-only sad-code universe). Four weights, each Laplace-smoothed (`w+1` so a
zero-weight component is down-weighted, never deleted — every gold component is
real and must still count):

| weight | `w` per component | character |
|--------|-------------------|-----------|
| `file` | # files mapped to component | the biased status-quo weight |
| `flat` | 1 | unweighted macro; size-blind |
| `fanin` | cross-component dependency edges *into* it | structural centrality |
| `commit`| commits touching its files | dev activity (4 real-history repos) |

Weights from `component_centrality.py` (fan-in, files, from the `.acm`) and
`component_commits.py` (commit-touch, from blobless full-history clones bounded
to the benchmark snapshot year). Systems: `swattr/transarc`, `s20linker` (v45 LLM
pipeline), `artemis`. Scripts: `src/bias/weighted_f1.py` → `reports/WEIGHTED_F1.csv`.

## Full per-project results

| project | system | file | flat | fanin | commit |
|---------|--------|-----:|-----:|------:|-------:|
| mediastore | swattr/transarc | 0.591 | 0.661 | 0.363 | — |
| mediastore | s20linker | 0.903 | 0.908 | 0.875 | — |
| mediastore | artemis | 0.909 | 0.931 | 0.840 | — |
| teastore | swattr/transarc | 0.837 | 0.839 | 0.826 | 0.815 |
| teastore | s20linker | 0.819 | 0.743 | 0.658 | 0.805 |
| teastore | artemis | 0.834 | 0.832 | 0.821 | 0.811 |
| teammates | swattr/transarc | 0.647 | 0.736 | 0.623 | 0.680 |
| teammates | s20linker | 0.536 | 0.586 | 0.352 | 0.577 |
| teammates | artemis | 0.532 | 0.602 | 0.353 | 0.604 |
| bigbluebutton | swattr/transarc | 0.939 | 0.883 | 0.864 | 0.757 |
| bigbluebutton | s20linker | 0.961 | 0.908 | 0.943 | 0.741 |
| bigbluebutton | artemis | 0.704 | 0.743 | 0.718 | 0.730 |
| jabref | swattr/transarc | 0.943 | 0.948 | 0.958 | 0.951 |
| jabref | s20linker | 0.943 | 0.948 | 0.958 | 0.951 |
| jabref | artemis | 0.990 | 0.833 | 0.888 | 0.932 |

(JabRef `s20linker` == `swattr/transarc`: the v45 jabref links carry
`source=transarc`, so the composed sad-code set is identical — not a bug.)

### Average over all 5 projects (commit = its 4 repos)

| system | file | flat | fanin | commit |
|--------|-----:|-----:|------:|-------:|
| swattr/transarc | 0.792 | 0.813 | 0.727 | 0.801 |
| s20linker | 0.832 | 0.819 | 0.757 | 0.768 |
| artemis | 0.794 | 0.788 | 0.724 | 0.769 |

```
file   : s20linker(0.832) > artemis(0.794) > swattr/transarc(0.792)
flat   : s20linker(0.819) > swattr/transarc(0.813) > artemis(0.788)
fanin  : s20linker(0.757) > swattr/transarc(0.727) > artemis(0.724)
commit : swattr/transarc(0.801) > artemis(0.769) > s20linker(0.768)
```

### Average over the 4 commit-repos ONLY (fair fanin-vs-commit)

| system | file | flat | fanin | commit |
|--------|-----:|-----:|------:|-------:|
| swattr/transarc | 0.842 | 0.852 | 0.818 | 0.801 |
| s20linker | 0.815 | 0.796 | 0.728 | 0.768 |
| artemis | 0.765 | 0.753 | 0.695 | 0.769 |

```
file   : swattr/transarc(0.842) > s20linker(0.815) > artemis(0.765)
flat   : swattr/transarc(0.852) > s20linker(0.796) > artemis(0.753)
fanin  : swattr/transarc(0.818) > s20linker(0.728) > artemis(0.695)
commit : swattr/transarc(0.801) > artemis(0.769) > s20linker(0.768)
```

## Findings

**1. The weight is outcome-determining (the bias is not cosmetic).**
The `swattr/transarc`-vs-`artemis` pair flips on weight choice: under `file`,
artemis (0.794) edges swattr (0.792); under every debiased weight (`flat`,
`fanin`, `commit`) swattr beats artemis. The enrollment weight is the *only* ruler
that ranks artemis above swattr. Engine = JabRef: artemis's file-F1 **0.990 (best
of all)** collapses to 0.833 (`flat`) / 0.888 (`fanin`) because it drops the
high-fan-in `preferences` component — the bias manufactures the win.

**2. `fanin` is justified but does not change the verdict vs `flat`.**
`fanin` and `flat` produce the *same ranking* in both averaging regimes. Fan-in's
value is **legitimacy, not a different answer**: it defends `flat` against the
"size-blind, over-weights trivial components" objection by showing a principled
centrality weight reaches the same conclusion. (See `RQ_*` dep-centrality note:
small-but-central components — JabRef `preferences` fan-in/file 20.0 — are real.)

**3. `commit` weighting is NOT necessary.**
On a like-for-like project set (the 4 real-history repos), `commit` and `fanin`
**agree on the winner** (swattr/transarc) and differ only on a ~1pp `s20linker`
-vs-`artemis` near-tie for 2nd (0.768 vs 0.769) — within noise. The apparent
"commit flips the winner" in the all-5 table is an artifact of MediaStore (strong
s20linker, present in the fanin-5 average but absent from the commit-4 average),
not a real disagreement. Commit weighting is also the noisier, less reproducible
signal (external repos, default-branch only, test-churn confound — teammates
`Test Driver` is 0.4% of link-pairs but 23.5% of commits). **Keep commit activity
as descriptive prose corroboration; do not use it as a metric weight.**

## Recommendation (anti-bias stack)

1. **Combat the bias** — drop file-weighting. `flat` (unweighted macro), plus
   decision-level F1 and the tail metrics (`min_comp`, `pct_missed`) from
   `component_suite`, change the score so small components count.
2. **Legitimize** — **fan-in-weighted macro F1** as the principled capstone:
   shows the flip survives a centrality-weighted ruler, rebutting "macro just
   rewards junk components."
3. **Corroborate** — one prose sentence on commit activity as an independent,
   weakly-correlated (ρ≈0.18) second witness. **Not a weight.**

## Caveats

- `s20linker` = the **v45** LLM pipeline links (`evaluation_results/v45_*_links.csv`).
  The adaptive-agent variant (`agent_*`) is selectable via `S20_LINKS_PREFIX=agent`.
- MediaStore has no commit analysis (1-commit academic snapshot repo).
- BBB `HTML5 Client`/`Server` share one path prefix → identical commit counts.
- Smoothing (`w+1`) keeps zero-fan-in / zero-commit components in the average.
