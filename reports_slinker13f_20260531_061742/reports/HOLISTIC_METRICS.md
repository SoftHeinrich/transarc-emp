# Holistic Evaluation Metrics: Beyond Enrollment-Based P/R/F1

## Problems with Current Evaluation

The current evaluation computes micro-averaged P/R/F1 on enrolled (file-level) gold standards.
This creates systematic distortions:

1. **Enrollment inflation**: A single directory entry `src/main/java/org/jabref/logic/` expands
   to 972 file-level links. Getting one directory right/wrong shifts metrics by 972 units.
2. **Non-uniform weighting**: JabRef/logic (972 files) has 972× the influence of globals (1 file).
   A single error in `logic` matters 972× more than an error in `globals`.
3. **Granularity mismatch**: Annotators wrote directory-level entries, but evaluation is file-level.
   The tool is really doing component→directory mapping, but we measure file-level accuracy.
4. **Cascade blindness**: SAM-CODE P/R/F1 ignores downstream impact. A SAM-CODE FP for a model
   element with 20 SAD-SAM sentences causes 20× more SAD-CODE FPs than one with 1 sentence.

## SAM-CODE Metric Comparison

### M1: Current Micro-Averaged (Enrolled) vs M2: Raw Entry-Level vs M3: Macro-Averaged vs M4: Enrollment-Weighted

| Project | M1 Micro P | M1 R | M1 F1 | M2 Raw P | M2 R | M2 F1 | M3 Macro P | M3 R | M3 F1 | M4 Wt P | M4 R | M4 F1 |
|---------|----------|------|-------|---------|------|-------|-----------|------|-------|--------|------|-------|
| mediastore | 0.983 | 0.983 | 0.983 | 0.982 | 0.982 | 0.982 | 0.982 | 0.987 | 0.982 | 0.982 | 0.982 | 0.982 |
| teastore | 0.976 | 0.976 | 0.976 | 0.971 | 0.892 | 0.930 | 0.842 | 0.816 | 0.825 | 0.892 | 0.892 | 0.892 |
| teammates | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| bigbluebutton | 0.939 | 0.962 | 0.950 | 0.718 | 0.875 | 0.789 | 0.907 | 0.949 | 0.920 | 0.549 | 0.875 | 0.675 |
| jabref | 0.999 | 1.000 | 1.000 | 0.917 | 1.000 | 0.957 | 1.000 | 1.000 | 1.000 | 0.917 | 1.000 | 0.957 |

### Enrollment Inflation: Raw vs Enrolled Gold Size

| Project | Raw Gold Entries | Enrolled Gold Links | Inflation Factor | M1 F1 (Enrolled) | M2 F1 (Raw) | Δ |
|---------|----------------|--------------------|-----------------|-----------------|-----------|----|
| mediastore | 55 | 60 | 1.1x | 0.983 | 0.982 | -0.002 |
| teastore | 37 | 164 | 4.4x | 0.976 | 0.930 | -0.046 |
| teammates | 22 | 1616 | 73.5x | 1.000 | 1.000 | +0.000 |
| bigbluebutton | 64 | 730 | 11.4x | 0.950 | 0.789 | -0.161 |
| jabref | 11 | 1956 | 177.8x | 1.000 | 0.957 | -0.043 |

### M5: Component Coverage Metrics

| Project | Components | Any TP | Perfect | R≥50% | R≥90% | P≥90% | F1≥90% |
|---------|-----------|--------|---------|-------|-------|-------|--------|
| mediastore | 19 | 19/19 (100%) | 17/19 (89%) | 19/19 (100%) | 18/19 (95%) | 18/19 (95%) | 17/19 (89%) |
| teastore | 19 | 16/19 (84%) | 15/19 (79%) | 16/19 (84%) | 15/19 (79%) | 16/19 (84%) | 15/19 (79%) |
| teammates | 14 | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) | 14/14 (100%) |
| bigbluebutton | 22 | 22/22 (100%) | 8/22 (36%) | 22/22 (100%) | 18/22 (82%) | 16/22 (73%) | 14/22 (64%) |
| jabref | 6 | 6/6 (100%) | 5/6 (83%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |

### M6: Cascade-Weighted SAM-CODE Metrics (weighted by downstream sentence count)

Each SAM-CODE link is weighted by the number of SAD-SAM sentences for its model element,
reflecting its actual impact on the TransArc output.

| Project | M1 Micro F1 | M6 Cascade P | M6 R | M6 F1 | Δ F1 |
|---------|-----------|-----------|------|-------|------|
| mediastore | 0.983 | 1.000 | 1.000 | 1.000 | +0.017 |
| teastore | 0.976 | 1.000 | 1.000 | 1.000 | +0.024 |
| teammates | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 |
| bigbluebutton | 0.950 | 0.915 | 0.978 | 0.945 | -0.005 |
| jabref | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 |

## SAD-CODE (TransArc) Metric Comparison

### M1: Current Micro (Enrolled) vs M2: Raw Entry-Level vs M3: Macro (per-sentence) vs M4: Enrollment-Weighted

| Project | M1 Micro P | M1 R | M1 F1 | M2 Raw P | M2 R | M2 F1 | M3 Macro P | M3 R | M3 F1 | M4 Wt P | M4 R | M4 F1 |
|---------|----------|------|-------|---------|------|-------|-----------|------|-------|--------|------|-------|
| mediastore | 0.962 | 0.424 | 0.588 | 0.958 | 0.404 | 0.568 | 0.615 | 0.590 | 0.596 | 0.958 | 0.404 | 0.568 |
| teastore | 1.000 | 0.709 | 0.829 | 1.000 | 0.700 | 0.824 | 0.696 | 0.696 | 0.696 | 1.000 | 0.700 | 0.824 |
| teammates | 0.753 | 0.902 | 0.821 | 0.753 | 0.601 | 0.668 | 0.451 | 0.542 | 0.469 | 0.053 | 0.600 | 0.097 |
| bigbluebutton | 0.820 | 0.842 | 0.831 | 0.520 | 0.795 | 0.629 | 0.660 | 0.714 | 0.673 | 0.265 | 0.789 | 0.397 |
| jabref | 0.893 | 1.000 | 0.943 | 0.826 | 1.000 | 0.905 | 0.918 | 1.000 | 0.933 | 0.037 | 1.000 | 0.071 |

### SAD-CODE Enrollment Inflation

| Project | Raw Gold | Enrolled Gold | Factor | M1 F1 | M2 F1 | Δ |
|---------|---------|-------------|--------|-------|-------|----|
| mediastore | 57 | 59 | 1.0x | 0.588 | 0.568 | -0.020 |
| teastore | 70 | 707 | 10.1x | 0.829 | 0.824 | -0.006 |
| teammates | 228 | 8097 | 35.5x | 0.821 | 0.668 | -0.153 |
| bigbluebutton | 132 | 1529 | 11.6x | 0.831 | 0.629 | -0.202 |
| jabref | 38 | 8268 | 217.6x | 0.943 | 0.905 | -0.039 |

### Per-Sentence Metric Distribution (SAD-CODE)

How do individual sentence-level metrics distribute? Are there sentences with
perfect results and sentences with zero recall?

**mediastore** (26 sentences involved):
- Perfect (TP=Gold, FP=0): 15/25 (60%)
- Recall=100%: 15/25 (60%)
- Recall=0% (all gold links missed): 9/25 (36%)
- Precision=0% (all result links wrong): 1/17 (6%)
- Worst 3 sentences by F1:
  - S24: F1=0.000 (TP=0, FP=0, FN=4, Gold=4) "It stores user information and meta-data of audio files such as the na..."
  - S23: F1=0.000 (TP=0, FP=0, FN=4, Gold=4) "The Database component represents an actual database (e.g., MySQL)...."
  - S33: F1=0.000 (TP=0, FP=0, FN=4, Gold=4) "By contrast, all audio files are stored in a specific location (e.g., ..."

**teastore** (23 sentences involved):
- Perfect (TP=Gold, FP=0): 16/23 (70%)
- Recall=100%: 16/23 (70%)
- Recall=0% (all gold links missed): 7/23 (30%)
- Precision=0% (all result links wrong): 0/16 (0%)
- Worst 3 sentences by F1:
  - S24: F1=0.000 (TP=0, FP=0, FN=30, Gold=30) "It features endpoints for general CRUD-Operations (Create, Read, Updat..."
  - S8: F1=0.000 (TP=0, FP=0, FN=19, Gold=19) "The UI provides a status page at link indicating the current state of ..."
  - S23: F1=0.000 (TP=0, FP=0, FN=30, Gold=30) "It maps the relational entities to the JSON entity objects passed betw..."

**teammates** (101 sentences involved):
- Perfect (TP=Gold, FP=0): 34/92 (37%)
- Recall=100%: 51/92 (55%)
- Recall=0% (all gold links missed): 37/92 (40%)
- Precision=0% (all result links wrong): 10/65 (15%)
- Worst 3 sentences by F1:
  - S107: F1=0.000 (TP=0, FP=0, FN=12, Gold=12) "Update is done using UpdateOptions inside every Attributes...."
  - S168: F1=0.000 (TP=0, FP=0, FN=17, Gold=17) "This component automates the testing of TEAMMATES...."
  - S78: F1=0.000 (TP=0, FP=0, FN=71, Gold=71) "In particular, it is responsible for the following...."

**bigbluebutton** (49 sentences involved):
- Perfect (TP=Gold, FP=0): 7/45 (16%)
- Recall=100%: 30/45 (67%)
- Recall=0% (all gold links missed): 8/45 (18%)
- Precision=0% (all result links wrong): 4/41 (10%)
- Worst 3 sentences by F1:
  - S19: F1=0.000 (TP=0, FP=0, FN=16, Gold=16) "BigBlueButton 2.3 moves away from a single nodejs process for bbb-html..."
  - S53: F1=0.000 (TP=0, FP=0, FN=15, Gold=15) "It provides the list of users, chat, whiteboard, presentations in a me..."
  - S20: F1=0.000 (TP=0, FP=0, FN=16, Gold=16) "This means that bbb-html5 could use multiple CPU cores for processing ..."

**jabref** (10 sentences involved):
- Perfect (TP=Gold, FP=0): 5/10 (50%)
- Recall=100%: 10/10 (100%)
- Recall=0% (all gold links missed): 0/10 (0%)
- Precision=0% (all result links wrong): 0/10 (0%)
- Worst 3 sentences by F1:
  - S5: F1=0.340 (TP=250, FP=972, FN=0, Gold=250) "The model represents the most important data structures (BibDatases, B..."
  - S7: F1=0.987 (TP=707, FP=19, FN=0, Gold=707) "Only the gui knows the user and his preferences and can interact with ..."
  - S1: F1=1.000 (TP=1929, FP=1, FN=0, Gold=1929) "We have been successfully transitioning from a spaghetti to a more str..."

## Summary: What Each Metric Reveals

| Metric | What It Measures | What It Hides | Best For |
|--------|-----------------|--------------|----------|
| **M1**: Micro P/R/F1 (enrolled) | File-level accuracy after enrollment | Large-component bias; one directory dominates | Comparing to prior work (standard metric) |
| **M2**: Raw entry-level P/R/F1 | Accuracy at annotation granularity | File-level errors within correct directories | Understanding annotator-level performance |
| **M3**: Macro-averaged P/R/F1 | Equal weight per model element (SAM-CODE) or per sentence (SAD-CODE) | Overall volume of correct links | Identifying weak spots; fairness across elements |
| **M4**: Enrollment-weighted P/R/F1 | Each raw gold entry counts equally regardless of expansion | Absolute file-level counts | Removing enrollment bias from P/R/F1 |
| **M5**: Component coverage | What fraction of components are well-served | Severity of errors per component | Quick assessment of breadth |
| **M6**: Cascade-weighted P/R/F1 | Downstream TransArc impact per SAM-CODE link | Standalone SAM-CODE quality | Optimizing for end-to-end pipeline performance |

### Key Revelations from Alternative Metrics

**Where metrics diverge most:**

- **teastore SAM-CODE**: M1=0.976, M2=0.930, M3=0.825 (spread=0.151, highest=M1_micro, lowest=M3_macro)
- **bigbluebutton SAM-CODE**: M1=0.950, M2=0.789, M3=0.920 (spread=0.161, highest=M1_micro, lowest=M2_raw)
- **jabref SAM-CODE**: M1=1.000, M2=0.957, M3=1.000 (spread=0.043, highest=M3_macro, lowest=M2_raw)
- **teastore SAD-CODE**: M1=0.829, M2=0.824, M3=0.696 (spread=0.134, highest=M1_micro, lowest=M3_macro)
- **teammates SAD-CODE**: M1=0.821, M2=0.668, M3=0.469 (spread=0.352, highest=M1_micro, lowest=M3_macro)
- **bigbluebutton SAD-CODE**: M1=0.831, M2=0.629, M3=0.673 (spread=0.202, highest=M1_micro, lowest=M2_raw)

### Recommendation

No single metric captures the full picture. We recommend reporting:

1. **M1 (micro enrolled)** for backward compatibility with prior work
2. **M3 (macro per-element/per-sentence)** to reveal performance on under-represented components
3. **M5 (component coverage)** for a quick breadth assessment
4. **M6 (cascade-weighted)** when evaluating SAM-CODE in the TransArc pipeline context

M2 (raw entry-level) and M4 (enrollment-weighted) are recommended when enrollment
inflation is suspected to bias results. For projects with >10x enrollment factor
(TeaStore, Teammates, BigBlueButton, JabRef), these metrics provide a more honest assessment.

