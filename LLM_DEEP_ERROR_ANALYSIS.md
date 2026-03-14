# Deep Error Analysis: LLM Adaptive Component Classification

---

## Mediastore

### 1. Strategy Comparison

| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |
|:--|---:|---:|---:|---:|:---:|
| single | 36 | 34 | 45 | 1 | 0.361 |
| majority ** | 24 | 27 | 0 | 8 | 0.965 |
| intersection | 24 | 26 | 0 | 9 | 0.946 |

### 2. Per-Agent Disagreement

- All 3 agree: 26 (96.3%)
- 2/3 agree: 1 (3.7%)
- Only 1: 0 (0.0%)

**Intersection vs Majority:** Intersection drops 1 pairs (1 TPs lost, 0 FPs removed)
FP/TP removal ratio: 0.00 (>1 means intersection helps)

**Gold links predicted by ≤1 agent:** 8/35 (22.9%) — irretrievable by voting

| Sent | Component | Agents | Sentence Text |
|---:|:--|:--|:--|
| 23 | Interface: IDB | none | The Database component represents an actual database (e.g., MySQL). |
| 24 | Interface: IDB | none | It stores user information and meta-data of audio files such as the name and the... |
| 25 | Interface: IDB | none | After the user calls the page to list all available audio files, AudioAccess cre... |
| 31 | Interface: IDB | none | The Database component then executes the actual query for files. |
| 32 | Interface: IDB | none | All salted hashes of passwords are also stored in the Database component. |
| 33 | Interface: IDB | none | By contrast, all audio files are stored in a specific location (e.g., a dedicate... |
| 33 | Component: DB | none | By contrast, all audio files are stored in a specific location (e.g., a dedicate... |
| 34 | Interface: IDB | none | When a user requests files to download, the MediaAccess component fetches the as... |

### 3. Error Taxonomy

| Error Type | Count | Description |
|:--|---:|:--|
| interface_missed_entirely | 7 | Interface FN and no matching Component either |
| sentence_not_classified | 1 | Gold sentence not classified at all by LLM |

### 4. Component Confusion Matrix

### 5. TransArc vs LLM: Error Overlap

| Category | Count | % |
|:--|---:|:---:|
| Both exactly correct | 15 | 60.0% |
| LLM correct, TransArc wrong | 3 | 12.0% |
| TransArc correct, LLM wrong | 0 | 0.0% |
| Both wrong | 7 | 28.0% |

**Complementarity:** If we took the better answer per sentence, 18/25 (72.0%) would be exact-match correct (vs LLM=18, TransArc=15)

### 6. Hardest Sentences

Top 10 hardest sentences (most errors across LLM + TransArc):

| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |
|---:|---:|---:|---:|---:|---:|:--|
| 25 | 3 | 0 | 1 | 0 | 3 | After the user calls the page to list all available audio fi... |
| 33 | 2 | 0 | 2 | 0 | 2 | By contrast, all audio files are stored in a specific locati... |
| 31 | 2 | 0 | 1 | 0 | 2 | The Database component then executes the actual query for fi... |
| 24 | 2 | 0 | 1 | 0 | 2 | It stores user information and meta-data of audio files such... |
| 23 | 2 | 0 | 1 | 0 | 2 | The Database component represents an actual database (e.g., ... |
| 34 | 3 | 0 | 1 | 0 | 2 | When a user requests files to download, the MediaAccess comp... |
| 32 | 2 | 0 | 1 | 0 | 2 | All salted hashes of passwords are also stored in the Databa... |
| 20 | 1 | 0 | 0 | 0 | 1 | The ReEncoder component converts the bit rates of audio file... |
| 28 | 1 | 0 | 0 | 0 | 1 | Furthermore, it fetches a list of all available audio files.... |
| 9 | 1 | 0 | 0 | 0 | 1 | Furthermore, it fetches audio files from a specific location... |

### 7. Error Amplification

| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |
|:--|---:|---:|---:|---:|---:|---:|---:|
| Component: DB | 4 | 0 | 0 | —x | 1 | 4 | 4.0x |
| Interface: IDB | 2 | 0 | 0 | —x | 7 | 14 | 2.0x |

### 8. Gold Standard Quality Check

FP sentences where the LLM's assignment seems reasonable:

No debatable FPs found.

---

## Teastore

### 1. Strategy Comparison

| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |
|:--|---:|---:|---:|---:|:---:|
| single | 42 | 40 | 40 | 18 | 0.745 |
| majority | 40 | 27 | 20 | 31 | 0.764 |
| intersection ** | 33 | 25 | 12 | 33 | 0.764 |

### 2. Per-Agent Disagreement

- All 3 agree: 37 (48.1%)
- 2/3 agree: 10 (13.0%)
- Only 1: 30 (39.0%)

**Intersection vs Majority:** Intersection drops 10 pairs (2 TPs lost, 8 FPs removed)
FP/TP removal ratio: 4.00 (>1 means intersection helps)

**Gold links predicted by ≤1 agent:** 31/58 (53.4%) — irretrievable by voting

| Sent | Component | Agents | Sentence Text |
|---:|:--|:--|:--|
| 2 | Interface: ProductActions | none | The WebUI service retrieves images from the Image Provider. |
| 2 | Interface: CartActions | none | The WebUI service retrieves images from the Image Provider. |
| 2 | Interface: ImageProvider | v3 | The WebUI service retrieves images from the Image Provider. |
| 3 | Interface: AuthCart | none | Users are authenticated by the Auth service. |
| 4 | Interface: RecommenderStrategy | none | Data is retrieved from the PersistenceProvider and product recommendations from ... |
| 4 | Interface: Persistence | v3 | Data is retrieved from the PersistenceProvider and product recommendations from ... |
| 4 | Interface: Recommender | v3 | Data is retrieved from the PersistenceProvider and product recommendations from ... |
| 5 | Interface: ProductActions | none | The WebUI provides the TeaStore front-end using Servlets in combination with JSP... |
| 5 | Interface: CartActions | none | The WebUI provides the TeaStore front-end using Servlets in combination with JSP... |
| 6 | Interface: ProductActions | none | It contains logic to save and retireve values from cookies. |

### 3. Error Taxonomy

| Error Type | Count | Description |
|:--|---:|:--|
| interface_missed_entirely | 17 | Interface FN and no matching Component either |
| interface_covered_by_component | 14 | Interface FN but matching Component was assigned (no file impact) |
| behavioral_overclassification | 12 | Sentence has no gold links but LLM assigns a component |
| sentence_not_classified | 2 | Gold sentence not classified at all by LLM |

**behavioral_overclassification examples:**

- Sent 13: assigned `Component: ImageProvider`, gold=[], file impact=64
  > If the product ID or UI name is found but not in the requested size, the largest image will be loade...
- Sent 14: assigned `Component: ImageProvider`, gold=[], file impact=64
  > The scaled image is stored for later use....
- Sent 15: assigned `Component: ImageProvider`, gold=[], file impact=64
  > If the product ID or UI name and size is found, the image will be loaded and delivered....

### 4. Component Confusion Matrix

**Sentence has no gold, LLM assigns:**

| Wrongly Assigned | Count |
|:--|---:|
| Component: ImageProvider | 5 |
| Component: Auth | 3 |
| Component: Recommender | 2 |
| Component: Registry | 2 |

### 5. TransArc vs LLM: Error Overlap

| Category | Count | % |
|:--|---:|:---:|
| Both exactly correct | 4 | 17.4% |
| LLM correct, TransArc wrong | 0 | 0.0% |
| TransArc correct, LLM wrong | 1 | 4.3% |
| Both wrong | 18 | 78.3% |

**Complementarity:** If we took the better answer per sentence, 5/23 (21.7%) would be exact-match correct (vs LLM=4, TransArc=5)

### 6. Hardest Sentences

Top 10 hardest sentences (most errors across LLM + TransArc):

| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |
|---:|---:|---:|---:|---:|---:|:--|
| 7 | 5 | 0 | 3 | 0 | 3 | Images (with few exceptions) are not provides by the WebUi, ... |
| 10 | 5 | 0 | 3 | 0 | 3 | The Image Provider delivers images to the WebUI as base64 en... |
| 8 | 3 | 0 | 3 | 0 | 3 | The UI provides a status page at link indicating the current... |
| 4 | 5 | 0 | 3 | 0 | 3 | Data is retrieved from the PersistenceProvider and product r... |
| 2 | 5 | 0 | 3 | 0 | 3 | The WebUI service retrieves images from the Image Provider.... |
| 28 | 3 | 0 | 2 | 0 | 3 | It is trained using all existing orders.... |
| 6 | 3 | 0 | 2 | 0 | 3 | It contains logic to save and retireve values from cookies.... |
| 5 | 3 | 0 | 2 | 0 | 2 | The WebUI provides the TeaStore front-end using Servlets in ... |
| 27 | 3 | 0 | 2 | 0 | 2 | The Recommender is used to generate individual product recom... |
| 24 | 2 | 0 | 1 | 0 | 2 | It features endpoints for general CRUD-Operations (Create, R... |

### 7. Error Amplification

| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |
|:--|---:|---:|---:|---:|---:|---:|---:|
| Component: Auth | 13 | 3 | 39 | 13.0x | 0 | 0 | —x |
| Component: ImageProvider | 64 | 5 | 320 | 64.0x | 0 | 0 | —x |
| Component: Recommender | 14 | 2 | 28 | 14.0x | 0 | 0 | —x |
| Component: Registry | 5 | 2 | 10 | 5.0x | 1 | 5 | 5.0x |
| Component: WebUI | 19 | 0 | 0 | —x | 1 | 19 | 19.0x |
| Interface: AuthCart | 2 | 0 | 0 | —x | 2 | 4 | 2.0x |
| Interface: CartActions | 1 | 0 | 0 | —x | 6 | 6 | 1.0x |
| Interface: ImageProvider | 1 | 0 | 0 | —x | 5 | 5 | 1.0x |
| Interface: Persistence | 1 | 0 | 0 | —x | 6 | 6 | 1.0x |
| Interface: ProductActions | 1 | 0 | 0 | —x | 6 | 6 | 1.0x |
| Interface: Recommender | 1 | 0 | 0 | —x | 3 | 3 | 1.0x |
| Interface: RecommenderStrategy | 1 | 0 | 0 | —x | 3 | 3 | 1.0x |

### 8. Gold Standard Quality Check

FP sentences where the LLM's assignment seems reasonable:

No debatable FPs found.

---

## Teammates

### 1. Strategy Comparison

| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |
|:--|---:|---:|---:|---:|:---:|
| single | 177 | 98 | 139 | 124 | 0.377 |
| majority | 194 | 92 | 125 | 130 | 0.371 |
| intersection ** | 58 | 51 | 21 | 171 | 0.707 |

### 2. Per-Agent Disagreement

- All 3 agree: 72 (30.8%)
- 2/3 agree: 145 (62.0%)
- Only 1: 17 (7.3%)

**Intersection vs Majority:** Intersection drops 145 pairs (41 TPs lost, 104 FPs removed)
FP/TP removal ratio: 2.54 (>1 means intersection helps)

**Gold links predicted by ≤1 agent:** 130/222 (58.6%) — irretrievable by voting

| Sent | Component | Agents | Sentence Text |
|---:|:--|:--|:--|
| 1 | Interface: Logic | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: UI | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: Client | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: Common | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: Test Driver | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: Storage | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 1 | Interface: E2E | none | Architecture contains UI Component, Logic Component, Storage Component, Common C... |
| 4 | Interface: UI | none | The UI Browser seen by users consists of Web pages containing HTML, CSS for styl... |
| 5 | Interface: UI | none | This UI is a single HTML page generated by Angular framework. |
| 7 | Interface: Logic | none | In the UI Server the entry point for the application back end logic is designed ... |

### 3. Error Taxonomy

| Error Type | Count | Description |
|:--|---:|:--|
| interface_missed_entirely | 60 | Interface FN and no matching Component either |
| interface_covered_by_component | 51 | Interface FN but matching Component was assigned (no file impact) |
| sentence_not_classified | 51 | Gold sentence not classified at all by LLM |
| behavioral_overclassification | 13 | Sentence has no gold links but LLM assigns a component |
| component_missed | 9 | Component FN (sentence classified but this component missed) |
| keyword_triggered | 6 | Component name keyword appears in text, triggers wrong assignment |
| semantic_confusion | 2 | LLM infers wrong component from context (no keyword match) |

**behavioral_overclassification examples:**

- Sent 6: assigned `Component: UI`, gold=[], file impact=348
  > The initial page request is sent to the server over HTTP, and requests for data are sent asynchronou...
- Sent 23: assigned `Component: UI`, gold=[], file impact=348
  > ui.website is not a real package....
- Sent 24: assigned `Component: UI`, gold=[], file impact=348
  > It is a conceptual package representing the front-end of the application....

**keyword_triggered examples:**

- Sent 174: assigned `Component: Test Driver`, gold=['Component: Common', 'Interface: Common'], file impact=17
  > x.datatransfer contains component test cases for testing the datatransfer objects from the Common co...
- Sent 175: assigned `Component: Test Driver`, gold=['Component: Common', 'Interface: Common'], file impact=17
  > x.util contains component test cases for testing the utility classes from the Common component....
- Sent 176: assigned `Component: Test Driver`, gold=['Component: Logic', 'Interface: Logic'], file impact=17
  > x.logic contains component test cases for testing the Logic component....

**semantic_confusion examples:**

- Sent 81: assigned `Component: Logic`, gold=['Component: UI', 'Interface: UI'], file impact=71
  > Sanitizing input values received from the UI component....
- Sent 122: assigned `Component: Storage`, gold=['Component: Logic', 'Interface: Logic'], file impact=59
  > Hiding the complexities of datastore from the Logic component....

### 4. Component Confusion Matrix

**When gold has components, LLM wrongly adds:**

| Gold Component | Wrongly Assigned | Count |
|:--|:--|---:|
| Interface: Common | Component: Test Driver | 2 |
| Component: Common | Component: Test Driver | 2 |
| Component: Storage | Component: Test Driver | 2 |
| Interface: Storage | Component: Test Driver | 2 |
| Component: UI | Component: Logic | 1 |
| Interface: UI | Component: Logic | 1 |
| Interface: Logic | Component: Storage | 1 |
| Component: Logic | Component: Storage | 1 |
| Interface: Logic | Component: Test Driver | 1 |
| Component: Logic | Component: Test Driver | 1 |
| Component: UI | Component: Test Driver | 1 |
| Interface: UI | Component: Test Driver | 1 |

**Sentence has no gold, LLM assigns:**

| Wrongly Assigned | Count |
|:--|---:|
| Component: UI | 6 |
| Component: E2E | 4 |
| Component: Test Driver | 2 |
| Component: Client | 1 |

### 5. TransArc vs LLM: Error Overlap

| Category | Count | % |
|:--|---:|:---:|
| Both exactly correct | 0 | 0.0% |
| LLM correct, TransArc wrong | 0 | 0.0% |
| TransArc correct, LLM wrong | 1 | 1.1% |
| Both wrong | 91 | 98.9% |

**Complementarity:** If we took the better answer per sentence, 1/92 (1.1%) would be exact-match correct (vs LLM=0, TransArc=1)

**Shared FP components (both systems assign wrong):**

- `Component: UI`: 2 sentences
- `Component: Test Driver`: 1 sentences
- `Component: E2E`: 1 sentences
- `Component: Client`: 1 sentences

### 6. Hardest Sentences

Top 10 hardest sentences (most errors across LLM + TransArc):

| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |
|---:|---:|---:|---:|---:|---:|:--|
| 172 | 8 | 0 | 8 | 0 | 8 | Sub-packages contains x.testdriver, x.datatransfer, x.util, ... |
| 1 | 14 | 0 | 7 | 0 | 7 | Architecture contains UI Component, Logic Component, Storage... |
| 126 | 4 | 0 | 4 | 0 | 4 | Instead, a corresponding non-persistent data transfer object... |
| 101 | 4 | 0 | 3 | 0 | 3 | Entity already exists throws EntityAlreadyExistsException (e... |
| 47 | 4 | 0 | 3 | 0 | 3 | If the action is allowed, it will be performed, interacting ... |
| 131 | 4 | 0 | 4 | 0 | 2 | storage.api provides the API of the component to be accessed... |
| 163 | 4 | 0 | 3 | 0 | 3 | Test Driver can use the DataBundle in this manner to send an... |
| 185 | 4 | 0 | 3 | 0 | 2 | The E2E component has no knowledge of the internal workings ... |
| 179 | 2 | 1 | 2 | 0 | 2 | x.webapi contains system test cases for testing the user-inv... |
| 178 | 2 | 1 | 2 | 0 | 2 | x.search contains component test cases for testing the searc... |

### 7. Error Amplification

| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |
|:--|---:|---:|---:|---:|---:|---:|---:|
| Component: Client | 40 | 1 | 40 | 40.0x | 1 | 6 | 6.0x |
| Component: Common | 150 | 0 | 0 | —x | 20 | 595 | 29.8x |
| Component: E2E | 123 | 4 | 492 | 123.0x | 1 | 123 | 123.0x |
| Component: Logic | 71 | 1 | 71 | 71.0x | 13 | 562 | 43.2x |
| Component: Storage | 59 | 1 | 59 | 59.0x | 8 | 201 | 25.1x |
| Component: Test Driver | 17 | 8 | 136 | 17.0x | 0 | 0 | —x |
| Component: UI | 348 | 6 | 2088 | 348.0x | 17 | 365 | 21.5x |
| Interface: Client | 40 | 0 | 0 | —x | 7 | 172 | 24.6x |
| Interface: Common | 150 | 0 | 0 | —x | 25 | 1345 | 53.8x |
| Interface: E2E | 123 | 0 | 0 | —x | 7 | 861 | 123.0x |
| Interface: Logic | 71 | 0 | 0 | —x | 23 | 1243 | 54.0x |
| Interface: Storage | 59 | 0 | 0 | —x | 18 | 746 | 41.4x |
| Interface: Test Driver | 17 | 0 | 0 | —x | 4 | 68 | 17.0x |
| Interface: UI | 348 | 0 | 0 | —x | 27 | 3622 | 134.1x |

### 8. Gold Standard Quality Check

FP sentences where the LLM's assignment seems reasonable:

| Sent | LLM Assigned (FP) | Gold Components | Sentence Text |
|---:|:--|:--|:--|
| 173 | Component: Test Driver | [] | x.testdriver contains component test cases for testing the test driver infrastru... |
| 174 | Component: Test Driver | ['Component: Common', 'Interface: Common'] | x.datatransfer contains component test cases for testing the datatransfer object... |
| 175 | Component: Test Driver | ['Component: Common', 'Interface: Common'] | x.util contains component test cases for testing the utility classes from the Co... |
| 176 | Component: Test Driver | ['Component: Logic', 'Interface: Logic'] | x.logic contains component test cases for testing the Logic component. |
| 177 | Component: Test Driver | ['Component: Storage', 'Interface: Storage'] | x.storage contains component test cases for testing the Storage component. |
| 178 | Component: Test Driver | ['Component: Storage', 'Interface: Storage'] | x.search contains component test cases for testing the search functions. |
| 179 | Component: Test Driver | ['Component: UI', 'Interface: UI'] | x.webapi contains system test cases for testing the user-invoked actions. |
| 180 | Component: Test Driver | [] | x.automated contains system test cases for testing the system-automated actions ... |
| 189 | Component: E2E | [] | e2e.pageobjects contains abstractions of the pages as they appear on a Browser (... |
| 192 | Component: E2E | [] | x.e2e contains system test cases for testing the application as a whole. |
| 198 | Component: Client | [] | client.scripts scripts that deal with the back end data for administrative purpo... |

---

## Bigbluebutton

### 1. Strategy Comparison

| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |
|:--|---:|---:|---:|---:|:---:|
| single | 77 | 57 | 57 | 101 | 0.622 |
| majority ** | 45 | 36 | 17 | 122 | 0.710 |
| intersection | 23 | 22 | 4 | 136 | 0.593 |

### 2. Per-Agent Disagreement

- All 3 agree: 26 (31.7%)
- 2/3 agree: 27 (32.9%)
- Only 1: 29 (35.4%)

**Intersection vs Majority:** Intersection drops 27 pairs (14 TPs lost, 13 FPs removed)
FP/TP removal ratio: 0.93 (>1 means intersection helps)

**Gold links predicted by ≤1 agent:** 122/158 (77.2%) — irretrievable by voting

| Sent | Component | Agents | Sentence Text |
|---:|:--|:--|:--|
| 4 | Interface: HTML5 Client | none | HTML5 client. |
| 4 | Interface: HTML5 Server | none | HTML5 client. |
| 4 | Component: HTML5 Server | none | HTML5 client. |
| 5 | Interface: HTML5 Client | none | The HTML5 client is a single page, responsive web application that is built upon... |
| 5 | Interface: HTML5 Server | none | The HTML5 client is a single page, responsive web application that is built upon... |
| 5 | Component: HTML5 Server | none | The HTML5 client is a single page, responsive web application that is built upon... |
| 6 | Interface: HTML5 Client | none | The HTML5 client connects directly with the BigBlueButton server over port 443 (... |
| 6 | Interface: HTML5 Server | none | The HTML5 client connects directly with the BigBlueButton server over port 443 (... |
| 6 | Component: HTML5 Server | none | The HTML5 client connects directly with the BigBlueButton server over port 443 (... |
| 8 | Component: HTML5 Client | none | The HTML5 server sits behind nginx. |

### 3. Error Taxonomy

| Error Type | Count | Description |
|:--|---:|:--|
| interface_missed_entirely | 43 | Interface FN and no matching Component either |
| interface_covered_by_component | 36 | Interface FN but matching Component was assigned (no file impact) |
| component_missed | 26 | Component FN (sentence classified but this component missed) |
| sentence_not_classified | 17 | Gold sentence not classified at all by LLM |
| behavioral_overclassification | 10 | Sentence has no gold links but LLM assigns a component |
| semantic_confusion | 4 | LLM infers wrong component from context (no keyword match) |
| keyword_triggered | 2 | Component name keyword appears in text, triggers wrong assignment |
| interface_fn | 1 | interface_fn |

**behavioral_overclassification examples:**

- Sent 24: assigned `Component: HTML5 Server`, gold=[], file impact=16
  > Frontends receive the ValidateAuthTokenResp event to complete authentication....
- Sent 25: assigned `Component: HTML5 Server`, gold=[], file impact=16
  > Frontends collect subscriptions and publishers....
- Sent 27: assigned `Component: HTML5 Server`, gold=[], file impact=16
  > Frontends handle completely the Streamer redis events, i.e., Cursor, Annotations, External video sha...

**keyword_triggered examples:**

- Sent 76: assigned `Component: Presentation Conversion`, gold=['Component: HTML5 Client', 'Component: HTML5 Server', 'Interface: HTML5 Client', 'Interface: HTML5 Server'], file impact=70
  > Uploaded presentations go through a conversion process in order to be displayed inside the client....
- Sent 79: assigned `Component: Presentation Conversion`, gold=['Component: HTML5 Client', 'Component: HTML5 Server', 'Component: Redis PubSub', 'Interface: HTML5 Client', 'Interface: HTML5 Server', 'Interface: Redis PubSub'], file impact=70
  > The conversion process sends progress messages to the client through the Redis pubsub....

**semantic_confusion examples:**

- Sent 26: assigned `Component: HTML5 Server`, gold=['Component: Apps', 'Interface: Apps'], file impact=16
  > Frontends receive other DDP events including method calls to send events to akka-apps....
- Sent 39: assigned `Component: BBB web`, gold=['Component: HTML5 Client', 'Component: HTML5 Server', 'Interface: HTML5 Client', 'Interface: HTML5 Server'], file impact=33
  > The BigBlueButton API provides a third-party integration (such as the BigBlueButtonBN plugin for Moo...
- Sent 65: assigned `Component: FreeSWITCH`, gold=['Component: WebRTC-SFU', 'Interface: WebRTC-SFU'], file impact=94
  > Users joining through Google Chrome or Mozilla Firefox are able to take advantage of higher quality ...

### 4. Component Confusion Matrix

**When gold has components, LLM wrongly adds:**

| Gold Component | Wrongly Assigned | Count |
|:--|:--|---:|
| Interface: HTML5 Client | Component: Presentation Conversion | 2 |
| Component: HTML5 Server | Component: Presentation Conversion | 2 |
| Interface: HTML5 Server | Component: Presentation Conversion | 2 |
| Component: HTML5 Client | Component: Presentation Conversion | 2 |
| Interface: Apps | Component: HTML5 Server | 1 |
| Component: Apps | Component: HTML5 Server | 1 |
| Interface: HTML5 Client | Component: BBB web | 1 |
| Component: HTML5 Server | Component: BBB web | 1 |
| Interface: HTML5 Server | Component: BBB web | 1 |
| Component: HTML5 Client | Component: BBB web | 1 |
| Interface: HTML5 Client | Interface: BBB web | 1 |
| Component: HTML5 Server | Interface: BBB web | 1 |
| Interface: HTML5 Server | Interface: BBB web | 1 |
| Component: HTML5 Client | Interface: BBB web | 1 |
| Component: WebRTC-SFU | Component: FreeSWITCH | 1 |

**Sentence has no gold, LLM assigns:**

| Wrongly Assigned | Count |
|:--|---:|
| Component: HTML5 Server | 6 |
| Component: Presentation Conversion | 2 |
| Component: Recording Service | 1 |
| Component: WebRTC-SFU | 1 |

### 5. TransArc vs LLM: Error Overlap

| Category | Count | % |
|:--|---:|:---:|
| Both exactly correct | 0 | 0.0% |
| LLM correct, TransArc wrong | 0 | 0.0% |
| TransArc correct, LLM wrong | 0 | 0.0% |
| Both wrong | 45 | 100.0% |

**Complementarity:** If we took the better answer per sentence, 0/45 (0.0%) would be exact-match correct (vs LLM=0, TransArc=0)

### 6. Hardest Sentences

Top 10 hardest sentences (most errors across LLM + TransArc):

| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |
|---:|---:|---:|---:|---:|---:|:--|
| 72 | 8 | 0 | 6 | 0 | 7 | A user can join the voice conference (running in FreeSWITCH)... |
| 79 | 6 | 1 | 5 | 0 | 5 | The conversion process sends progress messages to the client... |
| 60 | 8 | 0 | 5 | 0 | 5 | Communication between apps and FreeSWITCH Event Socket Layer... |
| 73 | 6 | 0 | 6 | 0 | 4 | When joining through the client, the user can choose to join... |
| 76 | 4 | 1 | 4 | 0 | 4 | Uploaded presentations go through a conversion process in or... |
| 47 | 6 | 0 | 5 | 0 | 4 | Redis PubSub provides a communication channel between differ... |
| 39 | 4 | 2 | 4 | 0 | 3 | The BigBlueButton API provides a third-party integration (su... |
| 21 | 4 | 0 | 4 | 0 | 4 | As of 2.3-alpha-7, bbb-html5 uses 2 "frontend" and two "back... |
| 11 | 4 | 0 | 4 | 0 | 4 | Each user's client is only aware of the their meeting's stat... |
| 20 | 4 | 0 | 3 | 0 | 4 | This means that bbb-html5 could use multiple CPU cores for p... |

### 7. Error Amplification

| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |
|:--|---:|---:|---:|---:|---:|---:|---:|
| Component: Apps | 15 | 0 | 0 | —x | 2 | 30 | 15.0x |
| Component: BBB web | 33 | 1 | 33 | 33.0x | 0 | 0 | —x |
| Component: FSESL | 92 | 0 | 0 | —x | 5 | 420 | 84.0x |
| Component: FreeSWITCH | 94 | 1 | 94 | 94.0x | 1 | 84 | 84.0x |
| Component: HTML5 Client | 16 | 0 | 0 | —x | 15 | 240 | 16.0x |
| Component: HTML5 Server | 16 | 7 | 112 | 16.0x | 15 | 240 | 16.0x |
| Component: Presentation Conversion | 70 | 5 | 350 | 70.0x | 2 | 140 | 70.0x |
| Component: Recording Service | 13 | 1 | 13 | 13.0x | 0 | 0 | —x |
| Component: WebRTC-SFU | 6 | 1 | 6 | 6.0x | 3 | 18 | 6.0x |
| Interface: Apps | 15 | 0 | 0 | —x | 6 | 90 | 15.0x |
| Interface: BBB web | 33 | 1 | 33 | 33.0x | 5 | 165 | 33.0x |
| Interface: FSESL | 92 | 0 | 0 | —x | 8 | 696 | 87.0x |
| Interface: FreeSWITCH | 94 | 0 | 0 | —x | 8 | 732 | 91.5x |
| Interface: HTML5 Client | 16 | 0 | 0 | —x | 20 | 320 | 16.0x |
| Interface: HTML5 Server | 16 | 0 | 0 | —x | 20 | 320 | 16.0x |
| Interface: Presentation Conversion | 70 | 0 | 0 | —x | 2 | 140 | 70.0x |
| Interface: Redis DB | 3 | 0 | 0 | —x | 2 | 6 | 3.0x |
| Interface: Redis PubSub | 7 | 0 | 0 | —x | 4 | 28 | 7.0x |
| Interface: WebRTC-SFU | 6 | 0 | 0 | —x | 4 | 24 | 6.0x |

### 8. Gold Standard Quality Check

FP sentences where the LLM's assignment seems reasonable:

| Sent | LLM Assigned (FP) | Gold Components | Sentence Text |
|---:|:--|:--|:--|
| 50 | Component: Recording Service | [] | When the meeting ends, the Recording Processor will take all the recorded events... |
| 76 | Component: Presentation Conversion | ['Component: HTML5 Client', 'Component: HTML5 Server', 'Interface: HTML5 Client', 'Interface: HTML5 Server'] | Uploaded presentations go through a conversion process in order to be displayed ... |
| 77 | Component: Presentation Conversion | [] | When the uploaded presentation is an Office document, it needs to be converted i... |
| 79 | Component: Presentation Conversion | ['Component: HTML5 Client', 'Component: HTML5 Server', 'Component: Redis PubSub', 'Interface: HTML5 Client', 'Interface: HTML5 Server', 'Interface: Redis PubSub'] | The conversion process sends progress messages to the client through the Redis p... |
| 82 | Component: Presentation Conversion | [] | We take in consideration the configuration for enabling and disabling SWF, SVG a... |

---

## Jabref

### 1. Strategy Comparison

| Strategy | Sentences | Comp-TPs | Comp-FPs | Comp-FNs | File-F1 |
|:--|---:|---:|---:|---:|:---:|
| single ** | 10 | 18 | 1 | 4 | 0.999 |
| majority | 9 | 14 | 0 | 8 | 0.848 |
| intersection | 7 | 9 | 0 | 13 | 0.558 |

### 2. Per-Agent Disagreement

- All 3 agree: 9 (47.4%)
- 2/3 agree: 5 (26.3%)
- Only 1: 5 (26.3%)

**Intersection vs Majority:** Intersection drops 5 pairs (5 TPs lost, 0 FPs removed)
FP/TP removal ratio: 0.00 (>1 means intersection helps)

**Gold links predicted by ≤1 agent:** 8/22 (36.4%) — irretrievable by voting

| Sent | Component | Agents | Sentence Text |
|---:|:--|:--|:--|
| 1 | Component: globals | none | We have been successfully transitioning from a spaghetti to a more structured ar... |
| 4 | Component: model | v2 | We have JUnit tests to detect violations of the most crucial dependencies (betwe... |
| 4 | Component: logic | v2 | We have JUnit tests to detect violations of the most crucial dependencies (betwe... |
| 4 | Component: gui | v2 | We have JUnit tests to detect violations of the most crucial dependencies (betwe... |
| 4 | Component: globals | none | We have JUnit tests to detect violations of the most crucial dependencies (betwe... |
| 6 | Component: globals | none | The logic is responsible for reading/writing/importing/exporting and manipulatin... |
| 6 | Component: model | v2 | The logic is responsible for reading/writing/importing/exporting and manipulatin... |
| 7 | Component: globals | none | Only the gui knows the user and his preferences and can interact with him to hel... |

### 3. Error Taxonomy

| Error Type | Count | Description |
|:--|---:|:--|
| component_missed | 4 | Component FN (sentence classified but this component missed) |
| keyword_triggered | 1 | Component name keyword appears in text, triggers wrong assignment |

**keyword_triggered examples:**

- Sent 7: assigned `Component: preferences`, gold=['Component: globals', 'Component: gui'], file impact=18
  > Only the gui knows the user and his preferences and can interact with him to help him solve tasks....

### 4. Component Confusion Matrix

**When gold has components, LLM wrongly adds:**

| Gold Component | Wrongly Assigned | Count |
|:--|:--|---:|
| Component: globals | Component: preferences | 1 |
| Component: gui | Component: preferences | 1 |

### 5. TransArc vs LLM: Error Overlap

| Category | Count | % |
|:--|---:|:---:|
| Both exactly correct | 5 | 50.0% |
| LLM correct, TransArc wrong | 1 | 10.0% |
| TransArc correct, LLM wrong | 0 | 0.0% |
| Both wrong | 4 | 40.0% |

**Complementarity:** If we took the better answer per sentence, 6/10 (60.0%) would be exact-match correct (vs LLM=6, TransArc=5)

**Shared FP components (both systems assign wrong):**

- `Component: preferences`: 1 sentences

### 6. Hardest Sentences

Top 10 hardest sentences (most errors across LLM + TransArc):

| Sent | Gold Components | LLM FP | LLM FN | TA FP | TA FN | Text |
|---:|---:|---:|---:|---:|---:|:--|
| 7 | 2 | 1 | 1 | 1 | 1 | Only the gui knows the user and his preferences and can inte... |
| 1 | 4 | 0 | 1 | 0 | 1 | We have been successfully transitioning from a spaghetti to ... |
| 4 | 4 | 0 | 1 | 0 | 1 | We have JUnit tests to detect violations of the most crucial... |
| 6 | 4 | 0 | 1 | 0 | 1 | The logic is responsible for reading/writing/importing/expor... |
| 5 | 1 | 0 | 0 | 1 | 0 | The model represents the most important data structures (Bib... |

### 7. Error Amplification

| Component | Files | Comp FPs | File FPs | Amp Factor | Comp FNs | File FNs | Amp Factor |
|:--|---:|---:|---:|---:|---:|---:|---:|
| Component: globals | 1 | 0 | 0 | —x | 4 | 4 | 1.0x |
| Component: preferences | 18 | 1 | 18 | 18.0x | 0 | 0 | —x |

### 8. Gold Standard Quality Check

FP sentences where the LLM's assignment seems reasonable:

| Sent | LLM Assigned (FP) | Gold Components | Sentence Text |
|---:|:--|:--|:--|
| 7 | Component: preferences | ['Component: globals', 'Component: gui'] | Only the gui knows the user and his preferences and can interact with him to hel... |

---

## Cross-Project Summary

### Error Type Distribution (all projects)

| Error Type | Total | % of All Errors |
|:--|---:|:---:|
| interface_missed_entirely | 127 | 32.6% |
| interface_covered_by_component | 101 | 26.0% |
| sentence_not_classified | 71 | 18.3% |
| component_missed | 39 | 10.0% |
| behavioral_overclassification | 35 | 9.0% |
| keyword_triggered | 9 | 2.3% |
| semantic_confusion | 6 | 1.5% |
| interface_fn | 1 | 0.3% |
| **Total** | **389** | |

### TransArc vs LLM Complementarity

| Project | Both OK | LLM Only | TransArc Only | Both Wrong | Combo Ceiling |
|:--|---:|---:|---:|---:|:---:|
| mediastore | 15 | 3 | 0 | 7 | 72.0% |
| teastore | 4 | 0 | 1 | 18 | 21.7% |
| teammates | 0 | 0 | 1 | 91 | 1.1% |
| bigbluebutton | 0 | 0 | 0 | 45 | 0.0% |
| jabref | 5 | 1 | 0 | 4 | 60.0% |
| **Total** | 24 | 4 | 2 | 165 | 15.4% |

**Insight:** The two systems are partially complementary. An oracle combiner that picks the better system per sentence would achieve 15.4% exact-match accuracy (vs LLM alone: 14.4%, TransArc alone: 13.3%).

### Top Error Sources by File Impact

**Largest FP sources (file-level):**

| Project:Component | File FPs | Comp FPs |
|:--|---:|---:|
| teammates:Component: UI | 2088 | 6 |
| teammates:Component: E2E | 492 | 4 |
| bigbluebutton:Component: Presentation Conversion | 350 | 5 |
| teastore:Component: ImageProvider | 320 | 5 |
| teammates:Component: Test Driver | 136 | 8 |
| bigbluebutton:Component: HTML5 Server | 112 | 7 |
| bigbluebutton:Component: FreeSWITCH | 94 | 1 |
| teammates:Component: Logic | 71 | 1 |
| teammates:Component: Storage | 59 | 1 |
| teammates:Component: Client | 40 | 1 |

**Largest FN sources (file-level):**

| Project:Component | File FNs | Comp FNs |
|:--|---:|---:|
| teammates:Interface: UI | 3622 | 27 |
| teammates:Interface: Common | 1345 | 25 |
| teammates:Interface: Logic | 1243 | 23 |
| teammates:Interface: E2E | 861 | 7 |
| teammates:Interface: Storage | 746 | 18 |
| bigbluebutton:Interface: FreeSWITCH | 732 | 8 |
| bigbluebutton:Interface: FSESL | 696 | 8 |
| teammates:Component: Common | 595 | 20 |
| teammates:Component: Logic | 562 | 13 |
| bigbluebutton:Component: FSESL | 420 | 5 |

### Actionable Recommendations

Based on error frequency analysis:

1. **interface_missed_entirely** (127, 33%): Interface-aware prompting — include Interface names in all agent prompts, not just Component names.
2. **interface_covered_by_component** (101, 26%): No action needed — Interface FNs where Component was correctly assigned have zero file impact (files fully overlap). This is a gold standard artifact, not a real error.
3. **sentence_not_classified** (71, 18%): Coverage gap — gold sentences that no agent classifies. These may be implicit references that require coreference resolution or context window expansion.

---

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 llm_deep_error_analysis.py
# Output: LLM_DEEP_ERROR_ANALYSIS.md
```
