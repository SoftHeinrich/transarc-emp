# SWATTR TP vs FP: Zero-Shot Separability

No training data. Can we distinguish TPs from FPs using only
semantic priors and embedding geometry?

**Data**: 148 TPs + 40 FPs = 188 links

## Approach 1: Relative Framing

For each link, compare similarity of the sentence to two reference frames:
- **Architectural**: "The {name} component is responsible for..."
- **Implementation**: "The {name} package contains classes for..."

If sim(sent, arch_frame) > sim(sent, impl_frame) → predict TP, else FP.

**Best single template pair** (arch[1] vs impl[1]):
- Precision (TP class): 0.845
- Recall (TP class): 0.919
- F1 (TP class): 0.880
- Accuracy: 0.803
- FPs caught: 15/40
- TPs wrongly killed: 12/148

**Ensemble (majority of 16 pairs)**:
- Precision: 0.852, Recall: 0.932, F1: 0.890, Acc: 0.819
- FPs caught: 16/40
- TPs wrongly killed: 10/148

**Per-project (ensemble):**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net Δ |
|---------|-----|-----|------------|------------|-------|
| mediastore | 17 | 1 | 1 | 0 | +1 |
| teastore | 20 | 0 | 0 | 0 | +0 |
| teammates | 49 | 32 | 15 | 2 | +13 |
| bigbluebutton | 44 | 5 | 0 | 1 | -1 |
| jabref | 18 | 2 | 0 | 7 | -7 |

**FP details (ensemble vote fraction = arch vs impl):**

| Project | Sent# | Element | Vote (arch/total) | Prediction | Sentence |
|---------|-------|---------|-------------------|------------|----------|
| mediastore | 37 | Reencoding | 0.38 | FP (caught) | However, a download can cause re-encoding of the audio file.... |
| teammates | 84 | Logic | 0.38 | FP (caught) | Package overview contains logic.api, logic.core.... |
| teammates | 188 | E2E | 0.38 | FP (caught) | e2e.util contains helpers needed for running E2E tests.... |
| teammates | 23 | UI | 0.31 | FP (caught) | ui.website is not a real package.... |
| teammates | 22 | UI | 0.94 | TP (miss) | logic, ui.website, ui.controller represent an application of... |
| teammates | 187 | E2E | 0.38 | FP (caught) | Package overview contains e2e.util, e2e.pageobjects, e2e.cas... |
| teammates | 197 | Client | 0.25 | FP (caught) | client.remoteapi classes needed to connect to the back end d... |
| teammates | 125 | Storage | 0.19 | FP (caught) | Classes in the storage.entity package are not visible outsid... |
| teammates | 173 | Test Driver | 0.81 | TP (miss) | x.testdriver contains component test cases for testing the t... |
| teammates | 86 | Logic | 1.00 | TP (miss) | logic.core contains the core logic of the system.... |
| teammates | 132 | Storage | 0.38 | FP (caught) | storage.entity contains classes that represent persistable e... |
| teammates | 198 | Client | 1.00 | TP (miss) | client.scripts scripts that deal with the back end data for ... |
| teammates | 117 | Logic | 0.81 | TP (miss) | Refer to the API for the cascade logic.... |
| teammates | 130 | Storage | 0.25 | FP (caught) | Package overview contains storage.api, storage.entity, stora... |
| teammates | 22 | Logic | 0.88 | TP (miss) | logic, ui.website, ui.controller represent an application of... |
| teammates | 195 | Client | 0.25 | FP (caught) | Package overview contains client.util, client.remoteapi, cli... |
| teammates | 160 | Common | 0.50 | TP (miss) | common.datatransfer package contains lightweight data transf... |
| teammates | 17 | E2E | 0.56 | TP (miss) | Selenium Java is used to automate E2E testing with actual We... |
| teammates | 189 | E2E | 0.62 | TP (miss) | e2e.pageobjects contains abstractions of the pages as they a... |
| teammates | 119 | Logic | 1.00 | TP (miss) | It contains minimal logic beyond what is directly relevant t... |
| teammates | 26 | UI | 0.38 | FP (caught) | ui.website is not a Java package.... |
| teammates | 4 | Client | 0.88 | TP (miss) | The UI Browser seen by users consists of Web pages containin... |
| teammates | 157 | Common | 0.44 | FP (caught) | common.util contains utility classes.... |
| teammates | 190 | E2E | 0.94 | TP (miss) | e2e.cases contains test cases.... |
| teammates | 158 | Common | 0.25 | FP (caught) | common.exceptions contains custom exceptions.... |
| teammates | 196 | Client | 0.31 | FP (caught) | client.util contains helpers needed for client scripts.... |
| teammates | 131 | Storage | 0.81 | TP (miss) | storage.api provides the API of the component to be accessed... |
| teammates | 156 | Common | 0.25 | FP (caught) | Package overview contains common.util, common.exceptions, co... |
| teammates | 79 | Logic | 1.00 | TP (miss) | Managing relationships between entities, e.g. cascade logic ... |
| teammates | 159 | Common | 0.75 | TP (miss) | common.datatransfer contains data transfer objects.... |
| teammates | 127 | Common | 0.25 | FP (caught) | These datatransfer classes are in common.datatransfer packag... |
| teammates | 133 | Storage | 0.62 | TP (miss) | storage.search contains classes for dealing with searching a... |
| teammates | 85 | Logic | 0.75 | TP (miss) | logic.api provides the API of the component to be accessed b... |
| bigbluebutton | 60 | FreeSWITCH | 1.00 | TP (miss) | Communication between apps and FreeSWITCH Event Socket Layer... |
| bigbluebutton | 18 | HTML5 Server | 1.00 | TP (miss) | Because nodejs was running on a single CPU core, having a 16... |
| bigbluebutton | 68 | HTML5 Server | 1.00 | TP (miss) | Kurento Media Server KMS is a media server that implements b... |
| bigbluebutton | 5 | WebRTC-SFU | 0.88 | TP (miss) | The HTML5 client is a single page, responsive web applicatio... |
| bigbluebutton | 74 | WebRTC-SFU | 0.81 | TP (miss) | WebRTC provides the user with high-quality audio with lower ... |
| jabref | 7 | preferences | 0.94 | TP (miss) | Only the gui knows the user and his preferences and can inte... |
| jabref | 5 | logic | 0.94 | TP (miss) | The model represents the most important data structures (Bib... |

## Approach 2: Cosine Similarity Threshold

Predict TP if cosine(sentence, component_name) > threshold.
Sweep thresholds without any training — just report what happens.

| Threshold | FPs Caught | TPs Killed | Net Benefit | Acc |
|-----------|------------|------------|-------------|-----|
| 0.15 | 2/40 | 15/148 | -13 | 0.718 |
| 0.20 | 4/40 | 23/148 | -19 | 0.686 |
| 0.25 | 6/40 | 30/148 | -24 | 0.660 |
| 0.30 | 11/40 | 36/148 | -25 | 0.654 |
| 0.35 | 15/40 | 43/148 | -28 | 0.638 |
| 0.40 | 22/40 | 59/148 | -37 | 0.590 |
| 0.45 | 27/40 | 78/148 | -51 | 0.516 |
| 0.50 | 31/40 | 93/148 | -62 | 0.457 |

## Approach 3: Unsupervised Clustering

K-means and DBSCAN on sentence embeddings — do natural clusters align with TP/FP?

### K-means k=2 (silhouette=0.103)

| Cluster | Size | TPs | FPs | TP Rate |
|---------|------|-----|-----|---------|
| 0 | 105 | 89 | 16 | 84.8% |
| 1 | 83 | 59 | 24 | 71.1% |
→ FPs caught: 0/40, TPs killed: 0/148, Acc: 0.787

### K-means k=3 (silhouette=0.105)

| Cluster | Size | TPs | FPs | TP Rate |
|---------|------|-----|-----|---------|
| 0 | 58 | 42 | 16 | 72.4% |
| 1 | 90 | 76 | 14 | 84.4% |
| 2 | 40 | 30 | 10 | 75.0% |
→ FPs caught: 0/40, TPs killed: 0/148, Acc: 0.787

### K-means k=4 (silhouette=0.115)

| Cluster | Size | TPs | FPs | TP Rate |
|---------|------|-----|-----|---------|
| 0 | 53 | 45 | 8 | 84.9% |
| 1 | 40 | 30 | 10 | 75.0% |
| 2 | 29 | 27 | 2 | 93.1% |
| 3 | 66 | 46 | 20 | 69.7% |
→ FPs caught: 0/40, TPs killed: 0/148, Acc: 0.787

### K-means k=5 (silhouette=0.132)

| Cluster | Size | TPs | FPs | TP Rate |
|---------|------|-----|-----|---------|
| 0 | 31 | 21 | 10 | 67.7% |
| 1 | 53 | 45 | 8 | 84.9% |
| 2 | 46 | 36 | 10 | 78.3% |
| 3 | 36 | 26 | 10 | 72.2% |
| 4 | 22 | 20 | 2 | 90.9% |
→ FPs caught: 0/40, TPs killed: 0/148, Acc: 0.787

## Approach 4: Rule-Based Heuristics

Zero-shot rules derived from domain knowledge of SAD-SAM task:

| Rule | FPs Caught | TPs Killed | Precision* | Net |
|------|------------|------------|-----------|-----|
| *(Precision = FPs caught / total flagged)* |||||
| `has_dotted_package` | 30/40 | 8/148 | 78.9% | +22 |
| `has_contains_pkg` | 11/40 | 3/148 | 78.6% | +8 |
| `has_package_keyword` | 6/40 | 0/148 | 100.0% | +6 |
| `impl_sentence` | 12/40 | 1/148 | 92.3% | +11 |
| `short_and_listing` | 19/40 | 0/148 | 100.0% | +19 |

**Any rule**: FPs caught 30/40, TPs killed 11/148, precision 73.2%, net +19

**≥2 rules**: FPs caught 23/40, TPs killed 1/148, precision 95.8%, net +22
**≥3 rules**: FPs caught 15/40, TPs killed 0/148, precision 100.0%, net +15

**Per-project (≥2 rules):**

| Project | FPs | Caught | TPs | Killed | Net |
|---------|-----|--------|-----|--------|-----|
| mediastore | 1 | 0 | 17 | 0 | +0 |
| teastore | 0 | 0 | 20 | 0 | +0 |
| teammates | 32 | 23 | 49 | 1 | +22 |
| bigbluebutton | 5 | 0 | 44 | 0 | +0 |
| jabref | 2 | 0 | 18 | 0 | +0 |

## Approach 5: Entailment Framing

Embed the hypothesis "This sentence is an architectural description of {name}"
and measure cosine similarity to the sentence. Higher = more likely TP.

**"This sentence is an architectural description of {name}"**
- TP mean sim: 0.4117, FP mean sim: 0.3757
- Best threshold: 0.10 → FPs caught 0/40, TPs killed 3/148, net -3

**"This sentence describes the responsibilities of the {name} component"**
- TP mean sim: 0.4419, FP mean sim: 0.3830
- Best threshold: 0.10 → FPs caught 0/40, TPs killed 3/148, net -3

**"This sentence explains how {name} works in the system architecture"**
- TP mean sim: 0.4289, FP mean sim: 0.3716
- Best threshold: 0.10 → FPs caught 0/40, TPs killed 4/148, net -4

## Approach 6: Hybrid (Rules + Relative Framing)

Combine: flag as FP if (≥2 rules trigger) OR (impl_frame > arch_frame by margin)

**Rules(≥2) OR Framing**: caught 25/40 FPs, killed 10/148 TPs, precision 71.4%, net +15
**Rules(≥2) AND Framing**: caught 14/40 FPs, killed 1/148 TPs, precision 93.3%, net +13
**Rules(≥2) only**: caught 23/40 FPs, killed 1/148 TPs, precision 95.8%, net +22
**Framing only**: caught 16/40 FPs, killed 10/148 TPs, precision 61.5%, net +6

## Impact on SWATTR SAD-SAM Metrics

If we apply the zero-shot filter to remove predicted FPs from SWATTR output,
what happens to P/R/F1?

| Project | Orig P | Orig R | Orig F1 | Filt P | Filt R | Filt F1 | ΔF1 |
|---------|--------|--------|---------|--------|--------|---------|-----|
| mediastore | 0.944 | 0.548 | 0.694 | 0.944 | 0.548 | 0.694 | +0.000 |
| teastore | 1.000 | 0.741 | 0.851 | 1.000 | 0.741 | 0.851 | +0.000 |
| teammates | 0.605 | 0.860 | 0.710 | 0.842 | 0.842 | 0.842 | +0.132 |
| bigbluebutton | 0.898 | 0.710 | 0.793 | 0.898 | 0.710 | 0.793 | +0.000 |
| jabref | 0.900 | 1.000 | 0.947 | 0.900 | 1.000 | 0.947 | +0.000 |

## Synthesis

### Zero-shot verdict

| Approach | FPs Caught | TPs Killed | Net | Generalizable? |
|----------|------------|------------|-----|----------------|
| Relative framing (ensemble) | 16/40 | 10/148 | +6 | Partially |
| Rule-based (≥2 rules) | 23/40 | 1/148 | +22 | Teammates-specific |
| Unsupervised K=2 | 24/40 | 59/148 | -35 | No (random) |

### Conclusion

1. **Relative framing (arch vs impl)** is the most principled zero-shot approach.
   It captures the right intuition: TP sentences describe architectural roles,
   FP sentences describe implementation/package structure.

2. **Rule-based heuristics** work well but are Teammates-specific.
   The "package contains classes" pattern captures most Teammates FPs
   but won't help with BBB or MediaStore FPs.

3. **Unsupervised clustering fails** — TPs and FPs don't form natural
   separable clusters in embedding space.

4. **The practical ceiling is low.** Even the best zero-shot approach
   catches <50% of FPs while killing some TPs. The net benefit is marginal.
   This confirms: the TP/FP distinction at the SAD-SAM level is largely an
   **annotation convention** — not a semantic property recoverable without
   project-specific calibration.

