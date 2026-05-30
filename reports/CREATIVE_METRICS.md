# Creative Holistic Metrics for Trace Link Recovery

## 1. Sentence-Centric Metrics

These answer: **how well does the documentation connect to code?**

| Metric | Definition |
|--------|-----------|
| **Coverage** | Fraction of gold sentences with ≥1 correct link (TP) |
| **Completeness** | Among covered sentences, average recall (what fraction of gold links found?) |
| **Usefulness** | Fraction of result sentences where TP > FP (more helpful than harmful) |
| **Noise** | Average FP/(TP+FP) per result sentence (developer frustration proxy) |
| **All-or-Nothing** | Fraction of gold sentences with recall = 0% or 100% (bimodality) |

| Project | P/R/F1 (M1) | Sent Coverage | Completeness | Usefulness | Noise | All-or-Nothing |
|---------|-----------|-------------|-------------|-----------|-------|---------------|
| mediastore | 0.962/0.424/0.588 | 0.640 (16/25) | 0.958 | 0.941 (16/17) | 0.059 | 0.960 |
| teastore | 1.000/0.709/0.829 | 0.696 (16/23) | 1.000 | 1.000 (16/16) | 0.000 | 1.000 |
| teammates | 0.753/0.902/0.821 | 0.598 (55/92) | 0.996 | 0.692 (45/65) | 0.299 | 0.957 |
| bigbluebutton | 0.820/0.842/0.831 | 0.822 (37/45) | 0.946 | 0.902 (37/41) | 0.211 | 0.844 |
| jabref | 0.893/1.000/0.943 | 1.000 (10/10) | 1.000 | 0.900 (9/10) | 0.082 | 1.000 |

### Sentence Recall Distribution

| Project | Gold Sents | R=0% | 0<R<50% | 50%≤R<100% | R=100% | Median R | Gini | Worst-Q25 F1 |
|---------|----------|------|---------|-----------|--------|---------|------|-------------|
| mediastore | 25 | 9 (36%) | 1 (4%) | 0 (0%) | 15 (60%) | 1.000 | 0.386 | 0.000 |
| teastore | 23 | 7 (30%) | 0 (0%) | 0 (0%) | 16 (70%) | 1.000 | 0.304 | 0.000 |
| teammates | 92 | 37 (40%) | 0 (0%) | 4 (4%) | 51 (55%) | 1.000 | 0.405 | 0.000 |
| bigbluebutton | 45 | 8 (18%) | 1 (2%) | 6 (13%) | 30 (67%) | 1.000 | 0.219 | 0.176 |
| jabref | 10 | 0 (0%) | 0 (0%) | 0 (0%) | 10 (100%) | 1.000 | 0.000 | 0.663 |

## 2. Code-Centric Metrics

These answer: **how well is the codebase reachable from documentation?**

| Metric | Definition |
|--------|-----------|
| **Reachability** | Fraction of gold code files correctly linked to ≥1 sentence |
| **Pollution** | Fraction of result code files not in any gold link (spurious) |
| **Orphan Rate** | Fraction of gold code files with zero result links (completely invisible) |

| Project | Gold Files | Result Files | Reachability | Pollution | Orphan Rate |
|---------|----------|-------------|-------------|----------|------------|
| mediastore | 15 | 11 | 0.667 | 0.000 | 0.267 (4/15) |
| teastore | 145 | 145 | 1.000 | 0.000 | 0.000 (0/145) |
| teammates | 828 | 808 | 0.976 | 0.000 | 0.024 (20/828) |
| bigbluebutton | 252 | 258 | 0.956 | 0.066 | 0.044 (11/252) |
| jabref | 1955 | 1956 | 1.000 | 0.001 | 0.000 (0/1955) |

## 3. Bridge & Component Metrics

These answer: **does the transitive bridge work?**

| Metric | Definition |
|--------|-----------|
| **Bridge Utilization** | Fraction of gold model elements that appear in the intermediate |
| **Bridge Accuracy** | Precision of intermediate SAD-SAM links (correct bridges) |
| **Bridge Recall** | Fraction of gold SAD-SAM links found in intermediate |

| Project | Gold Models | Int Models | Utilization | Bridge Accuracy | Bridge Recall |
|---------|-----------|-----------|------------|----------------|--------------|
| mediastore | 10 | 8 | 0.800 | 0.944 | 0.548 |
| teastore | 6 | 6 | 1.000 | 1.000 | 0.741 |
| teammates | 8 | 8 | 1.000 | 0.605 | 0.860 |
| bigbluebutton | 11 | 11 | 1.000 | 0.898 | 0.710 |
| jabref | 5 | 5 | 1.000 | 0.900 | 1.000 |

### Component Confusion (SAD-SAM FPs: wrong model element assigned)

When SAD-SAM assigns a sentence to the wrong model element, which confusions occur?

**teammates:**

| Assigned (Wrong) | Should Be (Correct) | Count |
|-----------------|--------------------|----- |
| Component: Logic | Component: Storage | 1 |
| Component: Storage | Component: Logic | 1 |
| Component: Logic | Component: UI | 1 |
| Component: Client | Component: UI | 1 |

**bigbluebutton:**

| Assigned (Wrong) | Should Be (Correct) | Count |
|-----------------|--------------------|----- |
| Component: HTML5 Server | _oN4CMFkHEeyewPSmlgszyA | 1 |
| Component: WebRTC-SFU | Component: HTML5 Client | 1 |
| Component: FreeSWITCH | Component: FSESL | 1 |
| Component: FreeSWITCH | Component: Redis PubSub | 1 |
| Component: FreeSWITCH | Component: Apps | 1 |

**jabref:**

| Assigned (Wrong) | Should Be (Correct) | Count |
|-----------------|--------------------|----- |
| Component: preferences | Component: gui | 1 |
| Component: logic | Component: model | 1 |

## 4. Practical Utility Metrics

These answer: **how useful is the tool for a developer?**

| Metric | Definition |
|--------|-----------|
| **Query Success** | P(≥1 correct file \| developer queries a sentence) |
| **Median Precision** | Median per-sentence precision (typical developer experience) |
| **Completeness Gap** | Among covered sentences, avg fraction of gold files still missing |
| **Overwhelm Ratio** | Median (result files / gold files) per sentence (information overload) |
| **Wasted Effort** | Total FP / Total TP (wrong links per correct one) |

| Project | Query Success | Median Prec | Completeness Gap | Overwhelm Ratio | Wasted Effort |
|---------|-------------|-----------|-----------------|----------------|-------------- |
| mediastore | 0.941 | 1.000 | 0.042 | 1.0x | 0.04 |
| teastore | 1.000 | 1.000 | 0.000 | 1.0x | 0.00 |
| teammates | 0.846 | 1.000 | 0.004 | 1.0x | 0.33 |
| bigbluebutton | 0.902 | 0.938 | 0.054 | 1.0x | 0.22 |
| jabref | 1.000 | 1.000 | 0.000 | 1.0x | 0.12 |

## 5. Comprehensive Dashboard: All Metrics Side by Side

| Metric | mediastore | teastore | teammates | bigbluebutton | jabref |
|--------|-----------|---------|----------|-------------|--------|
| **Standard P/R/F1** | 0.588 | 0.829 | 0.821 | 0.831 | 0.943 |
| | | | | | |
| *Sentence-Centric* |  |  |  |  |  |
| Sentence Coverage | 0.640 | 0.696 | 0.598 | 0.822 | 1.000 |
| Sentence Completeness | 0.958 | 1.000 | 0.996 | 0.946 | 1.000 |
| Sentence Usefulness | 0.941 | 1.000 | 0.692 | 0.902 | 0.900 |
| Sentence Noise | 0.059 | 0.000 | 0.299 | 0.211 | 0.082 |
| All-or-Nothing Rate | 0.960 | 1.000 | 0.957 | 0.844 | 1.000 |
| Recall Gini | 0.386 | 0.304 | 0.405 | 0.219 | 0.000 |
| Worst-Q25 F1 | 0.000 | 0.000 | 0.000 | 0.176 | 0.663 |
| Recall Median | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| | | | | | |
| *Code-Centric* |  |  |  |  |  |
| Code Reachability | 0.667 | 1.000 | 0.976 | 0.956 | 1.000 |
| Code Pollution | 0.000 | 0.000 | 0.000 | 0.066 | 0.001 |
| Code Orphan Rate | 0.267 | 0.000 | 0.024 | 0.044 | 0.000 |
| | | | | | |
| *Bridge* |  |  |  |  |  |
| Bridge Utilization | 0.800 | 1.000 | 1.000 | 1.000 | 1.000 |
| Bridge Accuracy | 0.944 | 1.000 | 0.605 | 0.898 | 0.900 |
| Bridge Recall | 0.548 | 0.741 | 0.860 | 0.710 | 1.000 |
| | | | | | |
| *Practical Utility* |  |  |  |  |  |
| Query Success | 0.941 | 1.000 | 0.846 | 0.902 | 1.000 |
| Median Sent Precision | 1.000 | 1.000 | 1.000 | 0.938 | 1.000 |
| Completeness Gap | 0.042 | 0.000 | 0.004 | 0.054 | 0.000 |
| Overwhelm Ratio | 1.0x | 1.0x | 1.0x | 1.0x | 1.0x |
| Wasted Effort | 0.04 | 0.00 | 0.33 | 0.22 | 0.12 |

## 6. What These Metrics Reveal That P/R/F1 Cannot

### Insight 1: F1 Hides Bimodal Sentence Coverage

Standard F1 averages over all links uniformly. But sentences are either fully
recovered or completely missed. The All-or-Nothing rate reveals this:

- **mediastore**: F1=0.588, but 96% of sentences are all-or-nothing (R=0: 9, R=100%: 15)
- **teastore**: F1=0.829, but 100% of sentences are all-or-nothing (R=0: 7, R=100%: 16)
- **teammates**: F1=0.821, but 96% of sentences are all-or-nothing (R=0: 37, R=100%: 51)
- **bigbluebutton**: F1=0.831, but 84% of sentences are all-or-nothing (R=0: 8, R=100%: 30)
- **jabref**: F1=0.943, but 100% of sentences are all-or-nothing (R=0: 0, R=100%: 10)

### Insight 2: Completeness Gap Shows Partial Recovery Is Rare

- **mediastore**: Completeness gap = 0.042 (only 1/25 sentences have partial recall)
- **teastore**: Completeness gap = 0.000 (only 0/23 sentences have partial recall)
- **teammates**: Completeness gap = 0.004 (only 4/92 sentences have partial recall)
- **bigbluebutton**: Completeness gap = 0.054 (only 7/45 sentences have partial recall)
- **jabref**: Completeness gap = 0.000 (only 0/10 sentences have partial recall)

### Insight 3: Overwhelm Ratio Shows Information Overload

The developer sees N result files per sentence. How does N compare to the actual gold count?

- **mediastore**: Median overwhelm = 1.0x (result files are 1.0× the gold count)
- **teastore**: Median overwhelm = 1.0x (result files are 1.0× the gold count)
- **teammates**: Median overwhelm = 1.0x (result files are 1.0× the gold count)
- **bigbluebutton**: Median overwhelm = 1.0x (result files are 1.0× the gold count)
- **jabref**: Median overwhelm = 1.0x (result files are 1.0× the gold count)

### Insight 4: Gini Coefficient Reveals Inequality

A Gini of 0 means all sentences are equally well-served; 1 means all recall is
concentrated in one sentence. High Gini = unfair distribution of quality.

- **mediastore**: Gini = 0.386
- **teastore**: Gini = 0.304
- **teammates**: Gini = 0.405
- **bigbluebutton**: Gini = 0.219
- **jabref**: Gini = 0.000

### Insight 5: Component Confusion Reveals Systematic Errors

- **teammates**: Top confusion: Component: Logic → Component: Storage (1× — sentences about Component: Storage are assigned to Component: Logic)
- **bigbluebutton**: Top confusion: Component: HTML5 Server → _oN4CMFkHEeyewPSmlgszyA (1× — sentences about _oN4CMFkHEeyewPSmlgszyA are assigned to Component: HTML5 Server)
- **jabref**: Top confusion: Component: preferences → Component: gui (1× — sentences about Component: gui are assigned to Component: preferences)

### Insight 6: Query Success vs F1

F1 counts individual links. Query success counts whether a developer
gets *any* useful result per query. These can diverge significantly:

- **mediastore**: F1=0.588, Query Success=0.941
- **teastore**: F1=0.829, Query Success=1.000
- **teammates**: F1=0.821, Query Success=0.846
- **bigbluebutton**: F1=0.831, Query Success=0.902
- **jabref**: F1=0.943, Query Success=1.000

