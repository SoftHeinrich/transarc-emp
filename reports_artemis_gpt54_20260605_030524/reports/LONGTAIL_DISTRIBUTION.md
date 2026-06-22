# Link Distribution Analysis: Long-tail in SAD-SAM, SAM-CODE, SAD-CODE

Empirical analysis of whether trace-link distributions are long-tail (skewed, concentrated)
across three axes: task, node type, and direction.

Scripts: `src/analysis/longtail_analysis.py` (SAD-SAM, SAD-CODE),
         `src/analysis/longtail_samcode.py` (SAM-CODE).
Enrollment uses `.acm` code models to expand directory gold entries to file entries.

---

## Summary verdict

| Task     | View             | Long-tail? | Key stats (avg across projects) |
|----------|------------------|------------|----------------------------------|
| SAD-SAM  | sentence→component | **No**   | 80% singletons, max 2–7 comp/sent |
| SAD-SAM  | component→sentence | Borderline | Zipf R²≈0.87 but n=5–11 |
| SAM-CODE | component→files  | **Yes (strong/heavy, 4/5)** | Gini 0.44–0.69, top-20% holds 50–69% |
| SAM-CODE | file→component   | **No**    | 96–100% singletons |
| SAD-CODE | sentence→files   | **Yes (enrollment-driven)** | Gini 0.34–0.65, Teammates very strong |
| SAD-CODE | file→sentence    | **No**    | Gini ≤0.35, flat |

---

## SAD-SAM

### Sentence view (how many components does each sentence mention?)

Not long-tail. Near-degenerate distribution: most sentences link to exactly one component.

| Project      | n sent | Singletons | Max | Gini | CoV  | Skew  | Top-20% |
|--------------|--------|-----------|-----|------|------|-------|---------|
| mediastore   | 27     | 85%       | 2   | 0.11 | 0.31 | 1.98  | 0.29    |
| teastore     | 23     | 83%       | 2   | 0.12 | 0.32 | 1.72  | 0.30    |
| teammates    | 45     | 84%       | 7   | 0.19 | 0.73 | 5.28  | 0.37    |
| bigbluebutton| 48     | 75%       | 3   | 0.18 | 0.42 | 1.69  | 0.32    |
| jabref       | 10     | 50%       | 3   | 0.26 | 0.48 | 0.40  | 0.33    |

75–85% of sentences link to exactly one component across all projects. Even the Teammates
outlier (one sentence → 7 components) does not change the overall picture: the distribution
is right-skewed but not heavy-tailed. This is a structural property of technical
documentation: sentences tend to be about one thing.

### Component view (how many sentences mention each component?)

Weak signal, small n prevents strong claims.

| Project      | n comp | Mean | Max | Gini | Zipf R² |
|--------------|--------|------|-----|------|---------|
| mediastore   | 10     | 3.1  | 7   | 0.31 | 0.85    |
| teastore     | 6      | 4.5  | 6   | 0.18 | 0.64    |
| teammates    | 8      | 7.1  | 15  | 0.26 | 0.95    |
| bigbluebutton| 11     | 5.6  | 14  | 0.37 | 0.93    |
| jabref       | 5      | 3.6  | 6   | 0.22 | 0.86    |

Zipf R² ≥ 0.85 in 4/5 cases, suggesting rank-frequency follows a log-linear pattern.
However, with n = 5–11 nodes, any two-parameter line will fit well. The range of mention
counts is narrow (1–15). Conclusion: some components are mentioned more often than others,
but this is not a meaningful long-tail — it is just "the document covers some components
more than others."

---

## SAM-CODE

### Component view (how many files per architecture element, after enrollment?)

**Strong to heavy-tail in 4/5 projects.** A few large-directory components dominate
the enrolled file count.

| Project      | n comp | Enrolled | Mean  | Max   | Gini | CoV  | Top-20% | Verdict        |
|--------------|--------|----------|-------|-------|------|------|---------|----------------|
| mediastore   | 16     | 52       | 3.2   | 16    | 0.44 | 1.09 | 0.50    | strong         |
| teastore     | 19     | 164      | 8.6   | 64    | 0.69 | 1.76 | 0.69    | **HEAVY-TAIL** |
| teammates    | 14     | 1616     | 115   | 348   | 0.45 | 0.90 | 0.43    | weak           |
| bigbluebutton| 22     | 730      | 33    | 94    | 0.51 | 1.00 | 0.51    | strong         |
| jabref       | 6      | 1956     | 326   | 972   | 0.61 | 1.17 | 0.50    | strong         |

Dominant components per project:
- **JabRef**: `logic` → 972 files = 49.7% of all enrolled pairs; `gui` → 707 files
- **TeaStore**: `ImageProvider` → 64 files = 39% of enrolled pairs
- **BBB**: `FreeSWITCH` → 94 files, `FSESL` → 92 files
- **Teammates**: UI/Common/E2E each 123–348 files (compressed range → only "weak")

The long-tail here reflects a real property of software architecture: some components
own large package trees, others are narrow. But enrollment amplifies the gap by 5–354×
(raw 1–3 directory entries → 5–972 enrolled files). A single correct directory-level
assignment becomes the dominant contributor to aggregate F1.

**Consequence for evaluation**: Getting JabRef's `logic` component right yields 972 TPs
out of 1956 total (50%). A system that links every sentence to `logic` obtains half
of JabRef's TPs for free, independent of any traceability reasoning.

Teammates registers only "weak" because all 14 components (7 Interface + 7 Component)
map to the same directory sets — Interface/Component pairs share 100% of their files.
The between-component variance is compressed by this structural symmetry.

### File view (how many components does each file belong to?)

**Not long-tail. Near-uniform.**

| Project      | n files | Mean | Max | Gini | Singletons |
|--------------|---------|------|-----|------|-----------|
| mediastore   | 50      | 1.0  | 2   | 0.04 | 96%       |
| teastore     | 156     | 1.1  | 3   | 0.05 | 96%       |
| teammates    | 808     | 2.0  | 2   | 0.00 | 0%        |
| bigbluebutton| 265     | 2.8  | 4   | 0.17 | 0%        |
| jabref       | 1955    | 1.0  | 2   | 0.00 | 100%      |

Files belong to exactly 1 component in MediaStore, TeaStore, JabRef.
Teammates: every file belongs to exactly 2 components (one Component + one Interface,
always the same pair). BBB: 62% belong to 2, 38% to 4 — same Interface/Component
duplication pattern. No file accumulates many components. The distribution is structurally
determined by the gold standard annotation convention, not by any long-tail phenomenon.

---

## SAD-CODE

SAD-CODE gold contains both directory and file entries. Enrollment expands directory
entries to individual files. The enrolled counts dwarf the raw link counts.

| Project      | Raw  | Enrolled | Expansion |
|--------------|------|----------|-----------|
| mediastore   | 31   | 55       | 1.8×      |
| teastore     | 27   | 707      | 26×       |
| teammates    | 57   | 8154     | 143×      |
| bigbluebutton| 62   | 1613     | 26×       |
| jabref       | 18   | 8268     | 459×      |

### Sentence view (how many files does each sentence link to, post-enrollment?)

**Project-dependent: Teammates very strong; others weak. Driven by enrollment.**

| Project      | n sent | Enrolled | Gini | CoV  | Skew | Top-20% | Zipf R² | Verdict       |
|--------------|--------|----------|------|------|------|---------|---------|---------------|
| mediastore   | 23     | 55       | 0.34 | 0.66 | 0.99 | 0.36    | 0.86    | weak          |
| teastore     | 9      | 707      | 0.45 | 0.84 | 0.98 | 0.44    | 0.80    | weak          |
| teammates    | 31     | 8154     | 0.65 | 1.45 | 2.78 | 0.64    | 0.70    | **very strong**|
| bigbluebutton| 12     | 1613     | 0.47 | 0.98 | 1.30 | 0.57    | 0.80    | weak          |
| jabref       | 18     | 8268     | 0.53 | 0.97 | 0.41 | 0.47    | 0.69    | weak          |

Mechanism: a sentence that references a large directory (e.g., `src/main/java/org/jabref/`)
after enrollment links to hundreds of files. A handful of "umbrella sentences" account
for the majority of enrolled pairs. In Teammates, the top 20% of sentences (6 sentences)
hold 64% of enrolled links.

This is **not a property of the documentation** — it is an artifact of the enrollment
procedure converting directory-level human annotations into file-level counts.

### File view (how many sentences link to each file, post-enrollment?)

**Not long-tail.** Files within a directory block inherit the same sentence set, so the
distribution compresses.

| Project      | n files | Gini | CoV  | Verdict     |
|--------------|---------|------|------|-------------|
| mediastore   | 13      | 0.29 | 0.52 | NOT         |
| teastore     | 56      | 0.13 | 0.25 | NOT         |
| teammates    | 808     | 0.19 | 0.35 | NOT         |
| bigbluebutton| 265     | 0.35 | 0.72 | NOT         |
| jabref       | 1955    | 0.06 | 0.17 | NOT         |

---

## Interpretation for the benchmark bias argument

The long-tail in SAM-CODE (comp→files) is the most consequential finding.

1. **Evaluation weight is non-uniform.** Because components differ by up to 972× in
   their enrolled file counts, aggregate F1 is dominated by a handful of large components.
   Correct classification of JabRef `logic` is worth 50% of JabRef's total F1 contribution.
   Small components (e.g., `globals` with 1 file) are negligible.

2. **Trivial strategies exploit the distribution.** A system that always links every
   sentence to the largest component by directory size would harvest a large fraction of TPs
   with no reasoning. This is not a corner case: the top-1 component accounts for 25–50%
   of enrolled pairs in 4/5 projects.

3. **SAD-CODE sentence-level concentration is pure enrollment artifact.** The raw link
   count (18–62 across all projects) treats each sentence-component assignment as one
   decision. After enrollment, a single directory-level decision expands to 100s of
   file-level pseudo-observations — but the system only made one decision. F1 measured
   at the file level credits this single decision 100–970× more than a file-specific link.

4. **SAD-SAM is the uniform baseline.** The only task where distribution is consistently
   flat (sentences) or only mildly skewed (components). Evaluation here is closest to
   uniform weighting across decisions.
