# TransArc Empirical Error Study

An empirical decomposition of TransArc's false positives and false negatives
back to their component causes in SAD-SAM and SAM-CODE.

## Analysis A – Baseline Metrics

### SAD-SAM (Swattr)

| Project | Gold | Result | TP | FP | FN | Precision | Recall | F1 | Exp P | Exp R | Exp F1 |
|---------|------|--------|----|----|-----|-----------|--------|-----|-------|-------|--------|
| mediastore | 31 | 18 | 17 | 1 | 14 | 0.944 | 0.548 | 0.694 | 0.940 | 0.548 | 0.690 |
| teastore | 27 | 20 | 20 | 0 | 7 | 1.000 | 0.741 | 0.851 | 0.999 | 0.740 | 0.850 |
| teammates | 57 | 81 | 49 | 32 | 8 | 0.605 | 0.860 | 0.710 | 0.600 | 0.859 | 0.709 |
| bigbluebutton | 62 | 49 | 44 | 5 | 18 | 0.898 | 0.710 | 0.793 | 0.897 | 0.709 | 0.790 |
| jabref | 18 | 20 | 18 | 2 | 0 | 0.900 | 1.000 | 0.947 | 0.899 | 0.999 | 0.946 |

### SAM-CODE (Arcotl)

| Project | Gold | Result | TP | FP | FN | Precision | Recall | F1 | Exp P | Exp R | Exp F1 |
|---------|------|--------|----|----|-----|-----------|--------|-----|-------|-------|--------|
| mediastore | 60 | 60 | 59 | 1 | 1 | 0.983 | 0.983 | 0.983 | 0.975 | 0.995 | 0.985 |
| teastore | 164 | 164 | 160 | 4 | 4 | 0.976 | 0.976 | 0.976 | 0.975 | 0.975 | 0.975 |
| teammates | 1616 | 1616 | 1616 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.999 | 0.999 | 0.999 |
| bigbluebutton | 730 | 748 | 702 | 46 | 28 | 0.939 | 0.962 | 0.950 | 0.874 | 0.953 | 0.912 |
| jabref | 1956 | 1957 | 1956 | 1 | 0 | 0.999 | 1.000 | 1.000 | 0.999 | 0.999 | 0.999 |

### SAD-CODE (TransArc)

| Project | Gold | Result | TP | FP | FN | Precision | Recall | F1 | Exp P | Exp R | Exp F1 |
|---------|------|--------|----|----|-----|-----------|--------|-----|-------|-------|--------|
| mediastore | 59 | 26 | 25 | 1 | 34 | 0.962 | 0.424 | 0.588 | 0.960 | 0.420 | 0.588 |
| teastore | 707 | 501 | 501 | 0 | 206 | 1.000 | 0.709 | 0.829 | 0.999 | 0.708 | 0.829 |
| teammates | 8097 | 9702 | 7307 | 2395 | 790 | 0.753 | 0.902 | 0.821 | 0.750 | 0.900 | 0.820 |
| bigbluebutton | 1529 | 1569 | 1287 | 282 | 242 | 0.820 | 0.842 | 0.831 | 0.820 | 0.840 | 0.830 |
| jabref | 8268 | 9262 | 8268 | 994 | 0 | 0.893 | 1.000 | 0.943 | 0.885 | 0.999 | 0.935 |

### Baseline Verification

- WARNING: sam-code/mediastore: P=0.983 (exp>=0.975), R=0.983 (exp>=0.995), F1=0.983 (exp>=0.985)

## Analysis B – False Positive Decomposition

For each TransArc FP (S, C), we trace back to the bridging model element(s) M
and check whether the SAD-SAM link (M, S) and/or SAM-CODE link (M, C) are correct.

| Category | Description |
|----------|-------------|
| SAD_SAM_CAUSED | SAD-SAM link (M,S) is wrong; SAM-CODE link (M,C) is correct |
| SAM_CODE_CAUSED | SAD-SAM link (M,S) is correct; SAM-CODE link (M,C) is wrong |
| BOTH_CAUSED | Both component links are wrong |
| COMBINATION_ERROR | Both component links are individually correct, but (S,C) is not in gold |

### FP Distribution by Project

| Project | Total FP | SAD_SAM | SAM_CODE | BOTH | COMBINATION |
|---------|----------|---------|----------|------|-------------|
| mediastore | 1 | 1 (100%) | 0 (0%) | 0 (0%) | 0 (0%) |
| teastore | 0 | 0 | 0 | 0 | 0 |
| teammates | 2395 | 2395 (100%) | 0 (0%) | 0 (0%) | 0 (0%) |
| bigbluebutton | 282 | 54 (19%) | 117 (41%) | 17 (6%) | 94 (33%) |
| jabref | 994 | 990 (100%) | 4 (0%) | 0 (0%) | 0 (0%) |

### Annotated FP Examples

#### mediastore

**SAD_SAM_CAUSED** (1 FPs):

- Sentence 37: "However, a download can cause re-encoding of the audio file."
  - Code: `mediastore.ejb.reencoder/src/edu/kit/ipd/sdq/mediastore/ejb/reencoder/ReEncoderImpl.java`
  - Via model element(s): Component: Reencoding

#### teastore

#### teammates

**SAD_SAM_CAUSED** (2395 FPs):

- Sentence 158: "common.exceptions contains custom exceptions."
  - Code: `src/test/java/teammates/common/datatransfer/package-info.java`
  - Via model element(s): Component: Common

- Sentence 158: "common.exceptions contains custom exceptions."
  - Code: `src/main/java/teammates/common/datatransfer/questions/FeedbackRankRecipientsResponseDetails.java`
  - Via model element(s): Component: Common

#### bigbluebutton

**SAD_SAM_CAUSED** (54 FPs):

- Sentence 68: "Kurento Media Server KMS is a media server that implements both SFU and MCU models."
  - Code: `build/packages-template/bbb-html5/build.sh`
  - Via model element(s): Component: HTML5 Server

- Sentence 60: "Communication between apps and FreeSWITCH Event Socket Layer (fsels) uses messages through redis pub..."
  - Code: `build/packages-template/bbb-freeswitch-core/build.sh`
  - Via model element(s): Component: FreeSWITCH

**SAM_CODE_CAUSED** (117 FPs):

- Sentence 47: "Redis PubSub provides a communication channel between different applications running on the BigBlueB..."
  - Code: `build/packages-template/bbb-graphql-server/after-install.sh`
  - Via model element(s): Component: HTML5 Server

- Sentence 5: "The HTML5 client is a single page, responsive web application that is built upon the following compo..."
  - Code: `bbb-graphql-middleware/demo/client/run.sh`
  - Via model element(s): Component: HTML5 Client

**BOTH_CAUSED** (17 FPs):

- Sentence 18: "Because nodejs was running on a single CPU core, having a 16 or 32 CPU core server for BigBlueButton..."
  - Code: `build/packages-template/bbb-graphql-server/opts-jammy.sh`
  - Via model element(s): Component: HTML5 Server

- Sentence 18: "Because nodejs was running on a single CPU core, having a 16 or 32 CPU core server for BigBlueButton..."
  - Code: `build/packages-template/bbb-html5-nodejs/build.sh`
  - Via model element(s): Component: HTML5 Server

**COMBINATION_ERROR** (94 FPs):

- Sentence 59: "This allows others who are using voice conference systems other than FreeSWITCH to easily create the..."
  - Code: `akka-bbb-fsesl/src/main/java/org/bigbluebutton/freeswitch/voice/events/FreeswitchHeartbeatEvent.java`
  - Via model element(s): Component: FreeSWITCH

- Sentence 59: "This allows others who are using voice conference systems other than FreeSWITCH to easily create the..."
  - Code: `akka-bbb-fsesl/src/main/java/org/bigbluebutton/freeswitch/voice/events/FreeswitchStatusReplyEvent.java`
  - Via model element(s): Component: FreeSWITCH

#### jabref

**SAD_SAM_CAUSED** (990 FPs):

- Sentence 5: "The model represents the most important data structures (BibDatases, BibEntries, Events, and related..."
  - Code: `src/test/java/org/jabref/logic/net/ProxyTest.java`
  - Via model element(s): Component: logic

- Sentence 5: "The model represents the most important data structures (BibDatases, BibEntries, Events, and related..."
  - Code: `src/test/java/org/jabref/logic/layout/format/RemoveBracketsAddCommaTest.java`
  - Via model element(s): Component: logic

**SAM_CODE_CAUSED** (4 FPs):

- Sentence 6: "The logic is responsible for reading/writing/importing/exporting and manipulating the model, and it ..."
  - Code: `src/test/java/org/jabref/testutils/category/GUITest.java`
  - Via model element(s): Component: gui

- Sentence 4: "We have JUnit tests to detect violations of the most crucial dependencies (between logic, model, and..."
  - Code: `src/test/java/org/jabref/testutils/category/GUITest.java`
  - Via model element(s): Component: gui

## Analysis C – False Negative Decomposition

For each missed gold link (S, C), we classify the root cause:

| Category | Description |
|----------|-------------|
| THEORETICAL_LIMIT | No transitive path exists even in gold standards |
| SAD_SAM_MISS | TransArc found no/wrong SAD-SAM link for sentence S |
| SAM_CODE_MISS | Correct model element found via SAD-SAM, but SAM-CODE missed code C |
| BOTH_MISS | Both components contributed to the miss |

### FN Distribution by Project

| Project | Total FN | THEORETICAL | SAD_SAM_MISS | SAM_CODE_MISS | BOTH_MISS |
|---------|----------|-------------|--------------|---------------|-----------|
| mediastore | 34 | 0 (0%) | 34 (100%) | 0 (0%) | 0 (0%) |
| teastore | 206 | 0 (0%) | 206 (100%) | 0 (0%) | 0 (0%) |
| teammates | 790 | 544 (69%) | 246 (31%) | 0 (0%) | 0 (0%) |
| bigbluebutton | 242 | 8 (3%) | 201 (83%) | 33 (14%) | 0 (0%) |
| jabref | 0 | 0 | 0 | 0 | 0 |

### Annotated FN Examples

#### mediastore

**SAD_SAM_MISS** (34 FNs):

- Sentence 34: "When a user requests files to download, the MediaAccess component fetches the associated meta-data f..."
  - Expected code: `mediastore.basic/src/edu/kit/ipd/sdq/mediastore/basic/exceptions/UserAlreadyExistsException.java`
  - Required bridging model(s): ['Component: DB']
  - Miss type: wrong_model

- Sentence 25: "After the user calls the page to list all available audio files, AudioAccess creates a query that is..."
  - Expected code: `mediastore.basic/src/edu/kit/ipd/sdq/mediastore/basic/exceptions/UserAlreadyExistsException.java`
  - Required bridging model(s): ['Component: DB']
  - Miss type: no_link

#### teastore

**SAD_SAM_MISS** (206 FNs):

- Sentence 11: "It matches the provided product ID or UI name (the filename for images not representing a product an..."
  - Expected code: `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/storage/DriveStorage.java`
  - Required bridging model(s): ['Component: ImageProvider']
  - Miss type: no_link

- Sentence 8: "The UI provides a status page at link indicating the current state of the TeaStore."
  - Expected code: `services/tools.descartes.teastore.webui/src/main/java/tools/descartes/teastore/webui/servlet/DataBaseServlet.java`
  - Required bridging model(s): ['Component: WebUI']
  - Miss type: no_link

#### teammates

**THEORETICAL_LIMIT** (544 FNs):

- Sentence 172: "Sub-packages contains x.testdriver, x.datatransfer, x.util, x.logic, x.storage, x.search, x.webapi, ..."
  - Expected code: `src/test/java/teammates/logic/core/BaseLogicTest.java`
  - Gold SAD-SAM models for sentence: NONE
  - Gold SAM-CODE models for code: ['Interface: Logic', 'Component: Logic']

- Sentence 172: "Sub-packages contains x.testdriver, x.datatransfer, x.util, x.logic, x.storage, x.search, x.webapi, ..."
  - Expected code: `src/test/java/teammates/logic/api/EmailSenderTest.java`
  - Gold SAD-SAM models for sentence: NONE
  - Gold SAM-CODE models for code: ['Interface: Logic', 'Component: Logic']

**SAD_SAM_MISS** (246 FNs):

- Sentence 119: "It contains minimal logic beyond what is directly relevant to CRUD operations."
  - Expected code: `src/main/java/teammates/storage/api/AccountsDb.java`
  - Required bridging model(s): ['Component: Storage']
  - Miss type: wrong_model

- Sentence 19: "It is used for administrative purposes, e.g. migrating data to a new schema."
  - Expected code: `src/client/java/teammates/client/scripts/GenerateUsageStatisticsObjects.java`
  - Required bridging model(s): ['Component: Client']
  - Miss type: no_link

#### bigbluebutton

**THEORETICAL_LIMIT** (8 FNs):

- Sentence 58: "We have extracted out the component that integrates with FreeSWITCH into it’s own application."
  - Expected code: `akka-bbb-fsesl/src/debian/DEBIAN/preinst`
  - Gold SAD-SAM models for sentence: ['Component: FreeSWITCH']
  - Gold SAM-CODE models for code: ['Component: FSESL', 'Interface: FSESL']

- Sentence 58: "We have extracted out the component that integrates with FreeSWITCH into it’s own application."
  - Expected code: `akka-bbb-fsesl/src/debian/DEBIAN/postinst`
  - Gold SAD-SAM models for sentence: ['Component: FreeSWITCH']
  - Gold SAM-CODE models for code: ['Component: FSESL', 'Interface: FSESL']

**SAD_SAM_MISS** (201 FNs):

- Sentence 11: "Each user's client is only aware of the their meeting's state, such the user's public and private ch..."
  - Expected code: `build/packages-template/bbb-html5/before-remove.sh`
  - Required bridging model(s): ['Component: HTML5 Client']
  - Miss type: no_link

- Sentence 38: "It implements the BigBlueButton API and holds a copy of the meeting state."
  - Expected code: `bbb-common-web/src/main/java/org/bigbluebutton/web/services/KeepAlivePong.java`
  - Required bridging model(s): ['Component: BBB web']
  - Miss type: no_link

**SAM_CODE_MISS** (33 FNs):

- Sentence 30: "If more than one backend is running, bbb-web splits the load in round-robin fashion by assigning an ..."
  - Expected code: `bigbluebutton-web/grailsw`
  - TransArc found model(s): ['Component: BBB web']

- Sentence 78: "The PDF document is then converted into scalable vector graphics (SVG) via bbb-web."
  - Expected code: `bigbluebutton-web/pres-checker/run.sh`
  - TransArc found model(s): ['Component: BBB web']

#### jabref

## Analysis D – Error Propagation / Amplification

One component error can induce multiple TransArc errors. This analysis quantifies the cascade.

### SAD-SAM FP Amplification (Top offenders)

| Project | SAD-SAM FP (M, S) | Model Element | Induced TransArc FPs |
|---------|-------------------|---------------|---------------------|
| mediastore | (_o10-YHDrEeSqnN80MQ2..., S37) | Component: Reencoding | 1 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S23) | Component: UI | 348 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S26) | Component: UI | 348 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S22) | Component: UI | 223 |
| bigbluebutton | (_yGgUMFkHEeyewPSmlgs..., S18) | Component: HTML5 Server | 24 |
| bigbluebutton | (_yGgUMFkHEeyewPSmlgs..., S68) | Component: HTML5 Server | 24 |
| bigbluebutton | (_nwrCMFwPEeyiuNx_RO7..., S60) | Component: FreeSWITCH | 11 |
| jabref | (_He3LoEl4Ee243f2e4VW..., S5) | Component: logic | 972 |
| jabref | (_NUdtEEl4Ee243f2e4VW..., S7) | Component: preferences | 18 |

### SAM-CODE FP Amplification (Top offenders)

| Project | SAM-CODE FP (M, C) | Model Element | Induced TransArc FPs |
|---------|--------------------|--------------|-----------------------|
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/build.sh) | Component: HTML5 Server | 12 |
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/before-remove.sh) | Component: HTML5 Server | 12 |
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/install-hasura.sh) | Component: HTML5 Server | 12 |
| jabref | (Component: gui, category/GUITest.java) | Component: gui | 4 |

### Amplification Summary

| Project | SAD-SAM FPs | Total Induced TransArc FPs | Avg Amplification | SAM-CODE FPs | Total Induced | Avg Amplification |
|---------|-------------|---------------------------|-------------------|--------------|---------------|-------------------|
| mediastore | 1 | 1 | 1.0 | 0 | 0 | 0.0 |
| teastore | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| teammates | 28 | 2395 | 85.5 | 0 | 0 | 0.0 |
| bigbluebutton | 5 | 71 | 14.2 | 18 | 135 | 7.5 |
| jabref | 2 | 990 | 495.0 | 1 | 4 | 4.0 |

## Analysis E – Per-Project Deep Dives

### MEDIASTORE

**TransArc Performance**: P=0.962, R=0.424, F1=0.588 (TP=25, FP=1, FN=34)

**FP Breakdown**: SAD_SAM=1, SAM_CODE=0, BOTH=0, COMBINATION=0

**FN Breakdown**: THEORETICAL=0, SAD_SAM_MISS=34, SAM_CODE_MISS=0, BOTH_MISS=0

**Top-5 Most Impactful Component Errors:**

| Rank | Type | Model Element | Link Target | Induced TransArc FPs |
|------|------|---------------|-------------|---------------------|
| 1 | SAD-SAM FP | Component: Reencoding | Sentence 37: "However, a download can cause re-encoding of the a..." | 1 |

**Dominant FP cause**: SAD_SAM_CAUSED (1/1 = 100%)
**Dominant FN cause**: SAD_SAM_MISS (34/34 = 100%)

### TEASTORE

**TransArc Performance**: P=1.000, R=0.709, F1=0.829 (TP=501, FP=0, FN=206)

**FP Breakdown**: SAD_SAM=0, SAM_CODE=0, BOTH=0, COMBINATION=0

**FN Breakdown**: THEORETICAL=0, SAD_SAM_MISS=206, SAM_CODE_MISS=0, BOTH_MISS=0

**Top-5 Most Impactful Component Errors:**

| Rank | Type | Model Element | Link Target | Induced TransArc FPs |
|------|------|---------------|-------------|---------------------|

**Dominant FN cause**: SAD_SAM_MISS (206/206 = 100%)

### TEAMMATES

**TransArc Performance**: P=0.753, R=0.902, F1=0.821 (TP=7307, FP=2395, FN=790)

**FP Breakdown**: SAD_SAM=2395, SAM_CODE=0, BOTH=0, COMBINATION=0

**FN Breakdown**: THEORETICAL=544, SAD_SAM_MISS=246, SAM_CODE_MISS=0, BOTH_MISS=0

**Top-5 Most Impactful Component Errors:**

| Rank | Type | Model Element | Link Target | Induced TransArc FPs |
|------|------|---------------|-------------|---------------------|
| 1 | SAD-SAM FP | Component: UI | Sentence 23: "ui.website is not a real package...." | 348 |
| 2 | SAD-SAM FP | Component: UI | Sentence 26: "ui.website is not a Java package...." | 348 |
| 3 | SAD-SAM FP | Component: UI | Sentence 22: "logic, ui.website, ui.controller represent an appl..." | 223 |
| 4 | SAD-SAM FP | Component: Common | Sentence 158: "common.exceptions contains custom exceptions...." | 139 |
| 5 | SAD-SAM FP | Component: E2E | Sentence 17: "Selenium Java is used to automate E2E testing with..." | 123 |

**Dominant FP cause**: SAD_SAM_CAUSED (2395/2395 = 100%)
**Dominant FN cause**: THEORETICAL_LIMIT (544/790 = 69%)

### BIGBLUEBUTTON

**TransArc Performance**: P=0.820, R=0.842, F1=0.831 (TP=1287, FP=282, FN=242)

**FP Breakdown**: SAD_SAM=54, SAM_CODE=117, BOTH=17, COMBINATION=94

**FN Breakdown**: THEORETICAL=8, SAD_SAM_MISS=201, SAM_CODE_MISS=33, BOTH_MISS=0

**Top-5 Most Impactful Component Errors:**

| Rank | Type | Model Element | Link Target | Induced TransArc FPs |
|------|------|---------------|-------------|---------------------|
| 1 | SAD-SAM FP | Component: HTML5 Server | Sentence 18: "Because nodejs was running on a single CPU core, h..." | 24 |
| 2 | SAD-SAM FP | Component: HTML5 Server | Sentence 68: "Kurento Media Server KMS is a media server that im..." | 24 |
| 3 | SAM-CODE FP | Component: HTML5 Server | `build.sh` | 12 |
| 4 | SAM-CODE FP | Component: HTML5 Server | `before-remove.sh` | 12 |
| 5 | SAM-CODE FP | Component: HTML5 Server | `install-hasura.sh` | 12 |

**Dominant FP cause**: SAM_CODE_CAUSED (117/282 = 41%)
**Dominant FN cause**: SAD_SAM_MISS (201/242 = 83%)

### JABREF

**TransArc Performance**: P=0.893, R=1.000, F1=0.943 (TP=8268, FP=994, FN=0)

**FP Breakdown**: SAD_SAM=990, SAM_CODE=4, BOTH=0, COMBINATION=0

**FN Breakdown**: THEORETICAL=0, SAD_SAM_MISS=0, SAM_CODE_MISS=0, BOTH_MISS=0

**Top-5 Most Impactful Component Errors:**

| Rank | Type | Model Element | Link Target | Induced TransArc FPs |
|------|------|---------------|-------------|---------------------|
| 1 | SAD-SAM FP | Component: logic | Sentence 5: "The model represents the most important data struc..." | 972 |
| 2 | SAD-SAM FP | Component: preferences | Sentence 7: "Only the gui knows the user and his preferences an..." | 18 |
| 3 | SAM-CODE FP | Component: gui | `GUITest.java` | 4 |

**Dominant FP cause**: SAD_SAM_CAUSED (990/994 = 100%)

## Analysis F – What-If Component Comparison

### Scenario 1: Perfect SAD-SAM + Actual SAM-CODE

| Project | P | R | F1 | TP | FP | FN | Result Size | vs Actual F1 |
|---------|---|---|----|----|----|----|------------|--------------|
| mediastore | 1.000 | 0.881 | 0.937 | 52 | 0 | 7 | 52 | +0.349 |
| teastore | 1.000 | 1.000 | 1.000 | 707 | 0 | 0 | 707 | +0.171 |
| teammates | 1.000 | 0.788 | 0.881 | 6380 | 0 | 1717 | 6380 | +0.060 |
| bigbluebutton | 0.840 | 0.959 | 0.895 | 1466 | 280 | 63 | 1746 | +0.064 |
| jabref | 1.000 | 1.000 | 1.000 | 8268 | 4 | 0 | 8272 | +0.056 |

### Scenario 2: Actual SAD-SAM + Perfect SAM-CODE

| Project | P | R | F1 | TP | FP | FN | Result Size | vs Actual F1 |
|---------|---|---|----|----|----|----|------------|--------------|
| mediastore | 0.962 | 0.424 | 0.588 | 25 | 1 | 34 | 26 | +0.000 |
| teastore | 1.000 | 0.709 | 0.829 | 501 | 0 | 206 | 501 | +0.000 |
| teammates | 0.753 | 0.902 | 0.821 | 7307 | 2395 | 790 | 9702 | +0.000 |
| bigbluebutton | 0.899 | 0.863 | 0.881 | 1320 | 148 | 209 | 1468 | +0.050 |
| jabref | 0.893 | 1.000 | 0.944 | 8268 | 990 | 0 | 9258 | +0.000 |

### Scenario 3: TransArc-Internal SAM-CODE vs Standalone SAM-CODE

| Project | Internal P | Internal R | Internal F1 | Standalone P | Standalone R | Standalone F1 | Internal Size | Standalone Size |
|---------|-----------|-----------|-------------|-------------|-------------|--------------|---------------|----------------|
| mediastore | 1.000 | 0.333 | 0.500 | 0.983 | 0.983 | 0.983 | 20 | 60 |
| teastore | 1.000 | 0.945 | 0.972 | 0.976 | 0.976 | 0.976 | 155 | 164 |
| teammates | 1.000 | 0.500 | 0.667 | 1.000 | 1.000 | 1.000 | 808 | 1616 |
| bigbluebutton | 0.939 | 0.481 | 0.636 | 0.939 | 0.962 | 0.950 | 374 | 748 |
| jabref | 0.999 | 1.000 | 1.000 | 0.999 | 1.000 | 1.000 | 1957 | 1957 |

## Analysis G – SAD-SAM Actual Contribution to SAD-CODE Output

Every TransArc output link (S, C) was produced by composing an intermediate
SAD-SAM link (M, S) with an intermediate SAM-CODE link (M, C). This analysis
traces each **actual** SAD-CODE output link back to its SAD-SAM source and
counts the real TPs and FPs each SAD-SAM link produced.

### Cross-Project Ranking: SAD-SAM TPs by Actual SAD-CODE TPs Produced (Top 20)

| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |
|------|---------|--------------|------|---------------|-------------|-------------|
| 1 | jabref | Component: logic | 6 | The logic is responsible for reading/writing/importing/exporting... | **972** | 0 |
| 2 | jabref | Component: logic | 1 | We have been successfully transitioning from a spaghetti to a mor... | **972** | 0 |
| 3 | jabref | Component: logic | 4 | We have JUnit tests to detect violations of the most crucial depe... | **972** | 0 |
| 4 | jabref | Component: logic | 9 | The model should have no dependencies to other classes of JabRef... | **972** | 0 |
| 5 | jabref | Component: gui | 1 | We have been successfully transitioning from a spaghetti to a mor... | **707** | 1 |
| 6 | jabref | Component: gui | 7 | Only the gui knows the user and his preferences and can interact... | **707** | 1 |
| 7 | teammates | Component: UI | 4 | The UI Browser seen by users consists of Web pages containing HTM... | **348** | 0 |
| 8 | teammates | Component: UI | 5 | This UI is a single HTML page generated by Angular framework. | **348** | 0 |
| 9 | teammates | Component: UI | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **348** | 0 |
| 10 | jabref | Component: model | 5 | The model represents the most important data structures (BibDatas... | **250** | 0 |
| 11 | jabref | Component: model | 12 | We use an event bus to publish events from the model to the other... | **250** | 0 |
| 12 | teammates | Component: Common | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **150** | 0 |
| 13 | teammates | Component: Common | 20 | The Common component contains utility code (data transfer objects... | **150** | 0 |
| 14 | teammates | Component: E2E | 15 | The E2E end-to-end component is used to interact with the applica... | **123** | 0 |
| 15 | bigbluebutton | Component: FreeSWITCH | 58 | We have extracted out the component that integrates with FreeSWIT... | **94** | 1 |
| 16 | bigbluebutton | Component: FSESL | 57 | FSESL akka. | **92** | 0 |
| 17 | teammates | Component: Logic | 77 | The Logic component handles the business logic of TEAMMATES. | **71** | 0 |
| 18 | bigbluebutton | Component: Presentation Conversion | 80 | Presentation conversion flow. | **70** | 3 |
| 19 | teastore | Component: ImageProvider | 10 | The Image Provider delivers images to the WebUI as base64 encoded... | **64** | 0 |
| 20 | teammates | Component: Storage | 118 | The Storage component performs CRUD (Create, Read, Update, Delete... | **59** | 0 |

The amplification factor depends on the model element's SAM-CODE footprint: JabRef's `logic` component maps to 972 code files, so *every* SAD-SAM link to `logic` produces 972 SAD-CODE links. By contrast, MediaStore's components map to 1-3 code files each.

### Cross-Project Ranking: SAD-SAM FPs by Actual SAD-CODE FPs Produced (Top 15)

| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |
|------|---------|--------------|------|---------------|-------------|-------------|
| 1 | jabref | Component: logic | 5 | The model represents the most important data structures... | 0 | **972** |
| 2 | teammates | Component: UI | 23 | ui.website is not a real package. | 0 | **348** |
| 3 | teammates | Component: UI | 26 | ui.website is not a Java package. | 0 | **348** |
| 4 | teammates | Component: UI | 22 | logic, ui.website, ui.controller represent an application of Mode... | 125 | **223** |
| 5 | teammates | Component: Common | 158 | common.exceptions contains custom exceptions. | 11 | **139** |
| 6 | teammates | Component: E2E | 17 | Selenium Java is used to automate E2E testing with actual Web bro... | 0 | **123** |
| 7 | teammates | Component: E2E | 190 | e2e.cases contains test cases. | 0 | **123** |
| 8 | teammates | Component: Common | 157 | common.util contains utility classes. | 32 | **118** |
| 9 | teammates | Component: Logic | 119 | It contains minimal logic beyond what is directly relevant to CRU... | 0 | **71** |
| 10 | teammates | Component: Logic | 117 | Refer to the API for the cascade logic. | 0 | **71** |
| 11 | teammates | Component: Logic | 85 | logic.api provides the API of the component to be accessed by the... | 21 | **50** |
| 12 | teammates | Component: Storage | 132 | storage.entity contains classes that represent persistable entiti... | 14 | **45** |
| 13 | teammates | Component: Storage | 125 | Classes in the storage.entity package are not visible outside thi... | 14 | **45** |
| 14 | teammates | Component: Common | 159 | common.datatransfer contains data transfer objects. | 107 | **43** |
| 15 | bigbluebutton | Component: HTML5 Server | 18 | Because nodejs was running on a single CPU core, having a 16 or 3... | 0 | **24** |

Note: some SAD-SAM FPs produce *both* TPs and FPs (e.g., Teammates S22 linked to UI produces 125 TPs + 223 FPs). This happens when the sentence does relate to some of the model element's code, but not all.

### Per-Model-Element Net Value

Net value = (SAD-CODE TPs from TPs + SAD-CODE TPs from FPs) - (SAD-CODE FPs from TPs + SAD-CODE FPs from FPs).

| Project | Model Element | SAD-SAM TPs | Produced TPs | Produced FPs | SAD-SAM FPs | Produced TPs | Produced FPs | Net |
|---------|--------------|-------------|-------------|-------------|------------|-------------|-------------|-----|
| jabref | Component: logic | 4 | 3888 | 0 | 1 | 0 | 972 | +2916 |
| jabref | Component: gui | 4 | 2828 | 4 | 0 | 0 | 0 | +2824 |
| teammates | Component: UI | 9 | 3132 | 0 | 3 | 125 | 919 | +2338 |
| jabref | Component: model | 6 | 1500 | 0 | 0 | 0 | 0 | +1500 |
| teammates | Component: Common | 5 | 750 | 0 | 6 | 514 | 386 | +878 |
| teammates | Component: Logic | 14 | 994 | 0 | 7 | 144 | 353 | +785 |
| bigbluebutton | Component: FreeSWITCH | 7 | 564 | 101 | 1 | 84 | 11 | +536 |
| teammates | Component: E2E | 5 | 615 | 0 | 5 | 246 | 369 | +492 |
| teammates | Component: Storage | 8 | 472 | 0 | 5 | 132 | 163 | +441 |
| bigbluebutton | Component: Presentation Conversion | 2 | 140 | 6 | 0 | 0 | 0 | +134 |
| bigbluebutton | Component: FSESL | 1 | 92 | 0 | 0 | 0 | 0 | +92 |
| bigbluebutton | Component: Apps | 5 | 75 | 5 | 0 | 0 | 0 | +70 |
| bigbluebutton | Component: BBB web | 3 | 66 | 0 | 0 | 0 | 0 | +66 |
| bigbluebutton | Component: HTML5 Client | 4 | 64 | 20 | 0 | 0 | 0 | +44 |
| teammates | Component: Test Driver | 3 | 51 | 0 | 1 | 0 | 17 | +34 |
| bigbluebutton | Component: HTML5 Server | 10 | 160 | 80 | 2 | 0 | 48 | +32 |
| teammates | Component: Client | 3 | 120 | 0 | 5 | 12 | 188 | **-56** |

Teammates/Client is the only model element with negative net value: its 5 SAD-SAM FPs produce more damage (188 FPs) than its 3 TPs contribute (120 TPs).

## Analysis H – Deep Dive: Three Failure Patterns in Error Amplification

The transitive composition SAD-SAM + SAM-CODE = SAD-CODE creates three distinct failure patterns where small component errors produce disproportionate SAD-CODE errors. All three are visible in BigBlueButton.

### Pattern 1: Contextual Mention Without Code Traceability

**Case**: (Component: FreeSWITCH, Sentence 59)

Sentence 59: *"This allows others who are using voice conference systems other than FreeSWITCH to easily create their own integration."*

This is a correct SAD-SAM link — the sentence does mention FreeSWITCH. FreeSWITCH maps to 95 code files via SAM-CODE (94 correct + 1 FP). But the gold SAD-CODE standard assigns **zero** code files to sentence 59, because the sentence discusses *other* systems, not FreeSWITCH's implementation.

Result: 0 TPs, **95 FPs** — every single transitive link is wrong.

Compare with the immediately preceding sentence 58: *"We have extracted out the component that integrates with FreeSWITCH into it's own application."* — same model element, same 95 SAM-CODE links, but produces **94 TPs** and 1 FP because it actually describes the component's architecture.

| Sentence | Text | SAD-SAM | SAD-CODE Gold | Via FreeSWITCH TPs | FPs |
|----------|------|---------|-------------|-------------------|-----|
| S58 | "We have extracted out the component that integrates with FreeSWITCH..." | TP | 102 links | 94 | 1 |
| S59 | "This allows others who are using voice conference systems other than FreeSWITCH..." | TP | 0 links | 0 | 95 |
| S61 | "FreeSWITCH." | TP | 94 links | 94 | 1 |
| S62 | "We think FreeSWITCH is an amazing piece of software for handling audio." | TP | 94 links | 94 | 1 |

This is the only case of this pattern across all 5 benchmark projects. It reveals a granularity mismatch between the gold standards: SAD-SAM captures "mentions" while SAD-CODE captures "is implementationally related to". The transitive approach cannot distinguish these two types of mentions.

### Pattern 2: SAM-CODE Maps Wrong Files to Correct Model Element

**Case**: Component: HTML5 Server in BigBlueButton

The gold standard maps HTML5 Server to files under `bigbluebutton-html5/` and `build/packages-template/bbb-html5/`. The SAM-CODE tool correctly finds these 16 files but also incorrectly includes 8 additional files from related but distinct components:

| Wrong File | Actual Component |
|-----------|-----------------|
| `bbb-graphql-server/build_hasura.sh` | GraphQL Server |
| `bbb-graphql-server/install-hasura.sh` | GraphQL Server |
| `build/packages-template/bbb-graphql-server/after-install.sh` | GraphQL Server |
| `build/packages-template/bbb-graphql-server/after-remove.sh` | GraphQL Server |
| `build/packages-template/bbb-graphql-server/before-remove.sh` | GraphQL Server |
| `build/packages-template/bbb-graphql-server/build.sh` | GraphQL Server |
| `build/packages-template/bbb-graphql-server/opts-jammy.sh` | GraphQL Server |
| `build/packages-template/bbb-html5-nodejs/build.sh` | Node.js Runtime |

These 8 wrong files are multiplied by the 10 correct SAD-SAM sentences for HTML5 Server, producing **80 SAD-CODE FPs** — pure SAM-CODE error amplified by the number of sentences.

### Pattern 3: SAD-SAM Links Wrong Sentences to Correct Model Element

**Case**: Component: HTML5 Server, Sentences 18 and 68

| Sentence | Text | Why it's wrong |
|----------|------|---------------|
| S18 | "Because nodejs was running on a single CPU core, having a 16 or 32 CPU core server for BigBlueButton 2.2 failed to yield much additional scalability." | About general scalability, mentions nodejs but not HTML5 Server |
| S68 | "Kurento Media Server KMS is a media server that implements both SFU and MCU models." | About Kurento/KMS, a different component entirely |

Each wrong sentence is composed with all 24 intermediate SAM-CODE files for HTML5 Server (16 correct + 8 from Pattern 2), producing **24 FPs per wrong sentence** = 48 SAD-CODE FPs total.

### The Compound Effect

These three patterns combine within a single model element:

| Pattern | Root Error | Amplification | SAD-CODE FPs |
|---------|-----------|---------------|-------------|
| 1. Contextual mention | 1 sentence with 0 gold SAD-CODE links | ×95 SAM-CODE links | 95 |
| 2. Wrong SAM-CODE files | 8 wrong code files | ×10 correct sentences | 80 |
| 3. Wrong SAD-SAM sentences | 2 wrong sentences | ×24 SAM-CODE links | 48 |
| **Combined** | **11 root errors** | **average 20× each** | **223** |

The amplification factor is proportional to the model element's "footprint":
- **SAD-SAM FP amplification** = number of SAM-CODE files for the model element
- **SAM-CODE FP amplification** = number of SAD-SAM sentences for the model element

This explains why coarse-grained architectures (JabRef: 5 components, Teammates: 7 components) produce dramatically higher amplification than fine-grained ones (MediaStore: 10+ components). JabRef's `logic` component maps to 972 code files, so a single SAD-SAM FP linking sentence 5 to `logic` produces 972 SAD-CODE FPs.

## Synthesis

### Aggregate FP Causes

| Category | Count | Percentage |
|----------|-------|------------|
| SAD_SAM_CAUSED | 3440 | 93.7% |
| SAM_CODE_CAUSED | 121 | 3.3% |
| BOTH_CAUSED | 17 | 0.5% |
| COMBINATION_ERROR | 94 | 2.6% |
| **Total** | **3672** | **100%** |

### Aggregate FN Causes

| Category | Count | Percentage |
|----------|-------|------------|
| THEORETICAL_LIMIT | 552 | 43.4% |
| SAD_SAM_MISS | 687 | 54.0% |
| SAM_CODE_MISS | 33 | 2.6% |
| BOTH_MISS | 0 | 0.0% |
| **Total** | **1272** | **100%** |

### Hypothesis Testing

**H1: SAD-SAM is the primary bottleneck for TransArc recall**

- Among recoverable FNs: SAD_SAM_MISS = 687/720 (95.4%), SAM_CODE_MISS = 33/720 (4.6%)
- Theoretical limit accounts for 552/1272 (43.4%) of all FNs
- **Verdict**: SUPPORTED — SAD-SAM miss rate = 95.4% of recoverable FNs

**H2: Error amplification is multiplicative and project-dependent**

- mediastore: SAD-SAM FP amplification range [1, 1], mean=1.0
- teastore: No SAD-SAM FP amplification (no SAD-SAM FPs in intermediates that induced TransArc FPs)
- teammates: SAD-SAM FP amplification range [17, 348], mean=85.5
- bigbluebutton: SAD-SAM FP amplification range [6, 24], mean=14.2
- jabref: SAD-SAM FP amplification range [18, 972], mean=495.0

**H3: MediaStore has lowest recall purely due to SAD-SAM recall limitations**

- MediaStore FN breakdown: THEORETICAL=0, SAD_SAM_MISS=34, SAM_CODE_MISS=0
- Theoretical recoverability: 100.0% of FNs are recoverable
- **Verdict**: SUPPORTED

**H4: For high-SAD-SAM-precision projects, FPs are primarily SAM_CODE_CAUSED**

- teastore: SAD-SAM P=1.000, No TransArc FPs
- jabref: SAD-SAM P=0.900, TransArc FPs: SAM_CODE_CAUSED=4/994 (0%)

### Recommendations

**Which component to improve first?**

| Project | Actual F1 | Perfect SAD-SAM F1 | Delta | Perfect SAM-CODE F1 | Delta | Priority |
|---------|-----------|-------------------|-------|--------------------|---------|----|
| mediastore | 0.588 | 0.937 | +0.349 | 0.588 | +0.000 | SAD-SAM |
| teastore | 0.829 | 1.000 | +0.171 | 0.829 | +0.000 | SAD-SAM |
| teammates | 0.821 | 0.881 | +0.060 | 0.821 | +0.000 | SAD-SAM |
| bigbluebutton | 0.831 | 0.895 | +0.064 | 0.881 | +0.050 | SAD-SAM |
| jabref | 0.943 | 1.000 | +0.056 | 0.944 | +0.000 | SAD-SAM |

### Where the Transitive Approach Breaks Down

The transitive approach fundamentally cannot recover links where no bridging
model element exists in the gold standards. This is the 'theoretical limit'.

| Project | Gold SAD-CODE | Theoretical Limit FNs | Unrecoverable % |
|---------|-------------|----------------------|-----------------|
| mediastore | 59 | 0 | 0.0% |
| teastore | 707 | 0 | 0.0% |
| teammates | 8097 | 544 | 6.7% |
| bigbluebutton | 1529 | 8 | 0.5% |
| jabref | 8268 | 0 | 0.0% |

## Analysis I – SAM-CODE Error Cascade & Holistic Pipeline Analysis

SAM-CODE achieves near-perfect aggregate metrics (P/R/F1 > 0.95 on most projects), but these metrics hide how SAM-CODE errors cascade through the transitive pipeline. This analysis traces every SAM-CODE link forward through TransArc to measure its actual impact on SAD-CODE output, then combines with SAD-SAM error contributions for a holistic per-model-element view.

### SAM-CODE FP Cascade: Wrong File × Sentences

Every SAM-CODE FP (M, C_wrong) is composed with all intermediate SAD-SAM sentences for M, producing |sentences(M)| SAD-CODE links — most of which are FPs. The amplification factor equals the number of SAD-SAM sentences for that model element.

**Top SAM-CODE FPs by induced SAD-CODE FPs:**

| Rank | Project | Model Element | Wrong Code File | ×Sents | →SAD-CODE FPs |
|------|---------|--------------|----------------|--------|-------------|
| 1-8 | bigbluebutton | HTML5 Server | 8 `bbb-graphql-server/*` files | ×12 | **12 each** (96 total) |
| 9 | bigbluebutton | FreeSWITCH | `bbb-resync-freeswitch` | ×8 | **8** |
| 10 | bigbluebutton | Apps | `BbbAppsIsAliveMessage.java` | ×5 | **5** |
| 11-15 | bigbluebutton | HTML5 Client | 5 client/test shell scripts | ×4 | **4 each** (20 total) |
| 16 | jabref | gui | `GUITest.java` | ×4 | **4** |
| 17-19 | bigbluebutton | Pres. Conversion | 3 `bbb-playback-presentation/*` | ×2 | **2 each** (6 total) |

SAM-CODE FPs are exclusively a BigBlueButton problem (23 FPs → 135 SAD-CODE FPs = 47.9% of BBB's TransArc FPs) plus 1 JabRef FP (→ 4 SAD-CODE FPs = 0.4% of JabRef's). No other project has SAM-CODE FPs in the internal pipeline.

### SAM-CODE FN Cascade: Missed File × Sentences

Every SAM-CODE FN (M, C_missed) blocks all correctly-linked sentences from reaching that code file. The cascade: each missed file causes FNs for every sentence that should trace to it.

All 11 SAM-CODE FNs with SAD-CODE impact are BBB web files, each causing **3 SAD-CODE FNs** (3 sentences correctly linked to BBB web via SAD-SAM). Total: 33 SAD-CODE FNs = 13.6% of BigBlueButton's TransArc FNs.

| Project | SAM-CODE FNs | With SAD-CODE Impact | Caused SAD-CODE FNs | % of TransArc FNs |
|---------|-------------|---------------------|--------------------|--------------------|
| mediastore | 40 | 0 | 0 | 0.0% |
| teastore | 9 | 0 | 0 | 0.0% |
| teammates | 808 | 0 | 0 | 0.0% |
| bigbluebutton | 379 | 11 | 33 | 13.6% |
| jabref | 0 | 0 | 0 | 0.0% |

Note: MediaStore has 40 SAM-CODE FNs and Teammates has 808, but they cause **zero** SAD-CODE FNs because SAD-SAM didn't find the relevant sentences — the SAM-CODE FNs are "dormant" errors masked by prior SAD-SAM failures.

### SAM-CODE TPs with Low Cascade Precision

Even correct SAM-CODE links (TPs) can produce mostly FPs through the cascade when the model element has many SAD-SAM FPs. The SAD-SAM FPs inject wrong sentences, which get composed with the correct file:

| Project | Model Element | Correct File Example | →TPs | →FPs | Cascade Precision | Root Cause |
|---------|--------------|---------------------|------|------|-------------------|-----------|
| mediastore | Reencoding | `ReEncoderImpl.java` | 0 | 1 | 0.000 | 1 SAD-SAM FP |
| teammates | Client | 40 files × same pattern | 3 | 5 | 0.375 | 5 SAD-SAM FPs |
| teammates | Logic | 71 files × same pattern | 17 | 4 | 0.810 | 7 SAD-SAM FPs |

Teammates/Client: every correct SAM-CODE file produces only 3 TPs but 5 FPs because 5 wrong sentences were linked to the Client component by SAD-SAM. The SAD-SAM FPs outnumber the TPs, degrading every file's cascade precision.

### Holistic Per-Model-Element Pipeline View

For each model element, the combined effect of both error sources on the final SAD-CODE output. FP categories: SS = SAD-SAM caused, SC = SAM-CODE caused, Both = both wrong, Combo = both individually correct but combination not in gold.

**Teammates** (all FPs are SAD-SAM caused — SAM-CODE is perfect):

| Model Element | Int Sents | Int Files | →TPs | →FPs (SS) | →FPs (SC) |
|--------------|----------|----------|------|----------|----------|
| UI | 12 | 348 | 3257 | 919 | 0 |
| Common | 11 | 150 | 1264 | 386 | 0 |
| Logic | 21 | 71 | 1138 | 353 | 0 |
| E2E | 10 | 123 | 861 | 369 | 0 |
| Storage | 13 | 59 | 604 | 163 | 0 |
| Client | 8 | 40 | 132 | 188 | 0 |
| Test Driver | 4 | 17 | 51 | 17 | 0 |
| **TOTAL** | | | **7307** | **2395** | **0** |

**BigBlueButton** (the only project where both error sources contribute):

| Model Element | Int Sents | Int Files | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|----------|----------|------|----------|----------|-----------|------------|---------|
| FreeSWITCH | 8 | 95 | 648 | 10 | 7 | 1 | 94 | 0 |
| HTML5 Server | 12 | 24 | 160 | 32 | 80 | 16 | 0 | 0 |
| Pres. Conversion | 2 | 73 | 140 | 0 | 6 | 0 | 0 | 0 |
| FSESL | 1 | 92 | 92 | 0 | 0 | 0 | 0 | 0 |
| Apps | 5 | 16 | 75 | 0 | 5 | 0 | 0 | 0 |
| BBB web | 3 | 22 | 66 | 0 | 0 | 0 | 0 | 33 |
| HTML5 Client | 4 | 21 | 64 | 0 | 20 | 0 | 0 | 0 |
| **TOTAL** | | | **1303** | **54** | **118** | **17** | **94** | **33** |

HTML5 Server is the compound error hotspot: 32 FPs from SAD-SAM + 80 FPs from SAM-CODE + 16 from both = 128 FPs from 12 sentences × 24 files. Its 8 wrong GraphQL files (SAM-CODE FPs) × 12 sentences = 96 FPs; its 2 wrong sentences (SAD-SAM FPs) × 24 files = 48 FPs.

**JabRef** (almost entirely SAD-SAM caused):

| Model Element | Int Sents | Int Files | →TPs | →FPs (SS) | →FPs (SC) |
|--------------|----------|----------|------|----------|----------|
| logic | 5 | 972 | 3888 | 972 | 0 |
| gui | 4 | 708 | 2828 | 0 | 4 |
| model | 6 | 250 | 1500 | 0 | 0 |
| preferences | 3 | 18 | 36 | 18 | 0 |
| **TOTAL** | | | **8268** | **990** | **4** |

### The Fundamental Asymmetry: Why SAD-SAM Dominates

The transitive product creates an asymmetry in error amplification:

- **SAD-SAM FP** for model M → amplified by |SAM-CODE files for M| (typically large)
- **SAM-CODE FP** for model M → amplified by |SAD-SAM sentences for M| (typically small)

| Project | Avg Files/Model | Avg Sents/Model | Ratio (Files÷Sents) |
|---------|----------------|----------------|---------------------|
| mediastore | 1.4 | 2.2 | 0.6x |
| teastore | 24.2 | 3.3 | 7.2x |
| teammates | 115.4 | 11.3 | **10.2x** |
| bigbluebutton | 35.9 | 4.7 | 7.6x |
| jabref | 391.2 | 4.0 | **97.8x** |

JabRef's ratio of 97.8x explains why a single SAD-SAM FP (sentence 5 → logic) produces 972 FPs, while the single SAM-CODE FP (gui → GUITest.java) produces only 4. For Teammates (10.2x), each SAD-SAM FP is amplified ~10x more than each SAM-CODE FP.

This asymmetry is structural: architectures have few documentation sentences but many code files per component. The transitive approach inherently amplifies documentation-level errors more than code-level errors.

### Cross-Project Error Source Cascade Summary

| Project | SAD-CODE TPs | FPs (SAD-SAM) | FPs (SAM-CODE) | FPs (Both) | FPs (Combo) | FNs from SC | Total FNs |
|---------|------------|-------------|--------------|-----------|-----------|-----------|----------|
| mediastore | 25 | 1 | 0 | 0 | 0 | 0 | 34 |
| teastore | 501 | 0 | 0 | 0 | 0 | 0 | 206 |
| teammates | 7307 | 2395 | 0 | 0 | 0 | 0 | 790 |
| bigbluebutton | 1303 | 54 | 118 | 17 | 94 | 33 | 242 |
| jabref | 8268 | 990 | 4 | 0 | 0 | 0 | 0 |
| **TOTAL** | **17404** | **3440** | **122** | **17** | **94** | **33** | **1272** |

**FP attribution**: SAD-SAM caused 3440/3673 (93.7%), SAM-CODE caused 122/3673 (3.3%), Both 17/3673 (0.5%), Combination 94/3673 (2.6%).

**FN attribution**: SAM-CODE FNs caused 33/1272 (2.6%) of TransArc FNs. The remaining 1239 (97.4%) are from SAD-SAM misses or theoretical limits.

### Key Findings

1. **SAM-CODE errors cascade only in BigBlueButton.** SAM-CODE FPs produce 135 SAD-CODE FPs (47.9% of BBB's FPs), and SAM-CODE FNs cause 33 SAD-CODE FNs (13.6% of BBB's FNs). All other projects: zero SAD-CODE impact from SAM-CODE errors.

2. **Dormant SAM-CODE errors are widespread.** MediaStore has 40 and Teammates 808 SAM-CODE FNs that cause zero SAD-CODE FNs because SAD-SAM already failed to find the relevant sentences. These errors are masked by the prior SAD-SAM bottleneck but would surface if SAD-SAM improves.

3. **The file/sentence asymmetry is structural.** Components map to 7-98x more files than sentences. This inherent imbalance means SAD-SAM FPs will always amplify more than SAM-CODE FPs in the transitive product, making SAD-SAM the priority regardless of project.

4. **Compound errors are rare but devastating.** Only BigBlueButton's HTML5 Server shows compound errors where both SAD-SAM and SAM-CODE errors interact (16 "both-caused" FPs). In all other cases, errors come from a single source.

5. **Correct SAM-CODE links can still produce mostly FPs** when SAD-SAM FPs outnumber TPs for a model element (Teammates/Client: cascade precision 0.375 on correct files due to 5 SAD-SAM FPs vs 3 TPs).

## Analysis J – Holistic Evaluation Metrics: Beyond Enrollment-Based P/R/F1

The current evaluation computes micro-averaged P/R/F1 on enrolled (file-level) gold standards. This creates systematic distortions:

1. **Enrollment inflation**: A single directory entry `src/main/java/org/jabref/logic/` expands to 972 file-level links. Getting one directory right/wrong shifts metrics by 972 units.
2. **Non-uniform weighting**: JabRef/logic (972 files) has 972x the influence of globals (1 file).
3. **Granularity mismatch**: Annotators wrote directory-level entries, but evaluation is file-level. The tool is really doing component→directory mapping, but we measure file-level accuracy.
4. **Cascade blindness**: SAM-CODE P/R/F1 ignores downstream impact on SAD-CODE.

### Proposed Alternative Metrics

| Metric | Definition | Rationale |
|--------|-----------|-----------|
| **M1**: Micro P/R/F1 (enrolled) | Current standard: P/R/F1 on enrolled file-level links | Backward compatibility |
| **M2**: Raw entry-level P/R/F1 | Evaluate at annotation granularity (pre-enrollment) | Matches annotator intent |
| **M3**: Macro-averaged P/R/F1 | Average per-element (SAM-CODE) or per-sentence (SAD-CODE) P/R/F1 | Equal weight per unit |
| **M4**: Enrollment-weighted P/R/F1 | Each enrolled link weighted by 1/(enrollment factor of its raw entry) | Removes enrollment bias |
| **M5**: Component coverage | Fraction of model elements with R≥90%, P≥90%, F1≥90% | Breadth assessment |
| **M6**: Cascade-weighted P/R/F1 | SAM-CODE links weighted by sentence count for downstream impact | Pipeline-aware |

### SAM-CODE: Current vs Alternative Metrics

| Project | M1 F1 | M2 F1 (raw) | M3 F1 (macro) | Enrollment Factor |
|---------|-------|------------|-------------|------------------|
| mediastore | 0.983 | 0.982 | 0.982 | 1.1x |
| teastore | 0.976 | 0.930 | **0.825** | 4.4x |
| teammates | 1.000 | 1.000 | 1.000 | 73.5x |
| bigbluebutton | 0.950 | **0.789** | 0.920 | 11.4x |
| jabref | 1.000 | 0.957 | 1.000 | 177.8x |

**BigBlueButton** drops from F1=0.950 (M1) to F1=0.789 (M2) because the enrolled metric inflates the contribution of large, correctly-mapped directories while the raw metric gives equal weight to each gold standard entry — exposing that 8/64 raw entries are wrong.

**TeaStore** drops from F1=0.976 (M1) to F1=0.825 (M3 macro) because 3 of 19 model elements have zero recall (Interface: ProductActions, Interface: RecommenderStrategy, Interface: Persistence). Micro-averaging hides these complete failures behind the 15 perfect components.

### SAD-CODE: Current vs Alternative Metrics

| Project | M1 F1 | M2 F1 (raw) | M3 F1 (macro/sent) | Enrollment Factor |
|---------|-------|------------|-------------------|------------------|
| mediastore | 0.588 | 0.568 | 0.596 | 1.0x |
| teastore | 0.829 | 0.824 | **0.696** | 10.1x |
| teammates | 0.821 | 0.668 | **0.469** | 35.5x |
| bigbluebutton | 0.831 | **0.629** | 0.673 | 11.6x |
| jabref | 0.943 | 0.905 | 0.933 | 217.6x |

**Teammates** shows the most dramatic divergence: M1=0.821 (looks good) but M3=0.469 (macro per-sentence). This means TransArc performs well on sentences that map to many files (inflating micro-average) but completely fails on 40% of sentences (37/92 sentences have zero recall). The micro-average is dominated by a few high-file-count sentences.

**BigBlueButton** drops from M1=0.831 to M2=0.629 — the raw-entry view reveals that many directory-level gold entries are not covered, masked by the large number of correctly enrolled files from other directories.

### Per-Sentence Distribution (SAD-CODE)

The macro-averaged metric reveals a bimodal distribution — sentences are either perfectly recovered or completely missed:

| Project | Sentences | Perfect (TP=Gold,FP=0) | Recall=100% | Recall=0% | Precision=0% |
|---------|----------|----------------------|------------|-----------|-------------|
| mediastore | 25 | 15 (60%) | 15 (60%) | **9 (36%)** | 1 (6%) |
| teastore | 23 | 16 (70%) | 16 (70%) | **7 (30%)** | 0 (0%) |
| teammates | 92 | 34 (37%) | 51 (55%) | **37 (40%)** | 10 (15%) |
| bigbluebutton | 45 | 7 (16%) | 30 (67%) | **8 (18%)** | 4 (10%) |
| jabref | 10 | 5 (50%) | 10 (100%) | 0 (0%) | 0 (0%) |

For Teammates, 37 out of 92 sentences (40%) have **zero** recall — every gold link missed. These are sentences that SAD-SAM failed to link to any model element. The micro-average F1=0.821 completely hides this: TransArc essentially doesn't work for 40% of the documentation.

JabRef's worst sentence is S5 ("The model represents the most important data structures...") with F1=0.340: 250 TPs but 972 FPs because it's incorrectly linked to `logic` via SAD-SAM.

### Component Coverage (SAM-CODE)

| Project | Components | F1≥90% | R≥90% | P≥90% | Perfect |
|---------|-----------|--------|-------|-------|---------|
| mediastore | 19 | 17 (89%) | 18 (95%) | 18 (95%) | 17 (89%) |
| teastore | 19 | 15 (79%) | 15 (79%) | 16 (84%) | 15 (79%) |
| teammates | 14 | **14 (100%)** | **14 (100%)** | **14 (100%)** | **14 (100%)** |
| bigbluebutton | 22 | 14 (64%) | 18 (82%) | 16 (73%) | **8 (36%)** |
| jabref | 6 | 6 (100%) | 6 (100%) | 6 (100%) | 5 (83%) |

BigBlueButton's M1 F1=0.950 looks excellent, but only 8/22 (36%) of its model elements achieve perfect recovery. The aggregate metric is propped up by a few large, correctly-mapped components.

### Cascade-Weighted SAM-CODE (M6)

Weighting each SAM-CODE link by downstream sentence count (= TransArc impact):

| Project | M1 F1 | M6 F1 (cascade) | Δ | Interpretation |
|---------|-------|----------------|---|----------------|
| mediastore | 0.983 | 1.000 | +0.017 | FP/FN are in components with 0 sentences — no cascade impact |
| teastore | 0.976 | 1.000 | +0.024 | Same: errors in components not reached by SAD-SAM |
| teammates | 1.000 | 1.000 | +0.000 | Already perfect |
| bigbluebutton | 0.950 | 0.945 | -0.005 | Errors slightly concentrated in high-sentence components |
| jabref | 1.000 | 1.000 | +0.000 | Already perfect |

Cascade-weighted metrics are similar to or better than micro metrics, confirming that SAM-CODE errors tend to occur in components with few SAD-SAM sentences (low downstream impact). This reinforces that SAD-SAM, not SAM-CODE, is the pipeline bottleneck.

### Recommendation

No single metric captures the full picture. For comprehensive evaluation:

1. **M1 (micro enrolled)** — for backward compatibility with prior work
2. **M3 (macro per-element/per-sentence)** — reveals performance on under-represented elements; exposes the bimodal "all or nothing" pattern
3. **M5 (component coverage)** — quick breadth assessment; catches cases where M1 is inflated by a few large components
4. **M6 (cascade-weighted)** — when evaluating SAM-CODE in the TransArc pipeline context

The key insight: **current micro-averaged enrollment-based F1 systematically overestimates performance** by letting large components dominate and hiding complete failures on small components and minority sentences. Teammates M1=0.821 vs M3=0.469 is the starkest example.

## Analysis K – Stupid Baselines: Why Micro-Averaged F1 Is Insufficient

To demonstrate concretely that micro-averaged enrollment-based F1 is an inadequate sole evaluation metric, we implement several trivially simple baselines that require no NLP, no architecture model understanding, and no machine learning. We evaluate them with both standard F1 and holistic metrics.

### Baseline Definitions

| ID | Name | Description | Oracle? |
|----|------|-------------|---------|
| B0 | **TransArc** | Actual system (reference) | No |
| B1 | **Link-All** | Every gold sentence x every code file (trivial R=100%) | No* |
| B2 | **Majority-1** | Every sentence x files of the single largest component | No |
| B4 | **Random** | Random links, same count as TransArc output | No |
| B5 | **Oracle-Top3** | Predict only for 3 sentences with most gold links, link to all files | Yes |
| B6 | **Keyword-Grep** | If sentence contains component name substring, link to its files | No |

\* B1 uses the set of gold sentences (which sentences have trace links). B5 uses oracle knowledge. B6 uses only component names (public info) and simple string matching.

### Per-Project Micro F1

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref |
|----------|-----------|---------|----------|-------------|--------|
| B0: TransArc | 0.588 | 0.829 | 0.821 | 0.831 | 0.943 |
| B1: Link-All | 0.048 | 0.261 | 0.191 | 0.115 | 0.585 |
| B2: Majority-1 | 0.000 | 0.294 | 0.181 | 0.254 | 0.432 |
| B4: Random | 0.024 | 0.126 | 0.120 | 0.063 | 0.440 |
| B5: Oracle-Top3 | 0.091 | 0.377 | 0.311 | 0.204 | **0.812** |
| **B6: Keyword-Grep** | **0.595** | 0.515 | 0.565 | 0.699 | **0.944** |

### Key Finding 1: Keyword-Grep Matches TransArc (Zero NLP)

The most damning result is **Keyword-Grep** (B6) — a baseline that simply checks whether a sentence contains a component name as a substring (e.g., "database" or "logic"), and if so, links it to all files of that component. It uses zero NLP, zero model comprehension, zero machine learning:

- **MediaStore**: Keyword-Grep F1=**0.595** vs TransArc F1=0.588 — **exceeds TransArc** (+0.007)
- **JabRef**: Keyword-Grep F1=**0.944** vs TransArc F1=0.943 — **virtually identical** (+0.001)
- **BigBlueButton**: Keyword-Grep F1=0.699 — 84% of TransArc's F1

For MediaStore, Keyword-Grep achieves P=1.000 (every link correct) vs TransArc P=0.962, with identical recall (0.424). For JabRef, both produce ~9,260 links with nearly identical TP/FP distributions. This demonstrates that for these projects, the apparent quality measured by F1 is largely attributable to trivial component-name pattern matching, not sophisticated NLP.

### Key Finding 2: Oracle-Top3 Exploits Gold Concentration

The Oracle-Top3 baseline predicts links only for the 3 sentences with the most gold links, revealing extreme gold standard concentration:

| Project | 3 Sentences Capture | Total Gold | Fraction | Oracle-Top3 F1 |
|---------|-------------------|-----------|----------|---------------|
| jabref | 5,787 | 8,268 | **70.0%** | **0.812** |
| teastore | 249 | 707 | 35.2% | 0.377 |
| mediastore | 16 | 59 | 27.1% | 0.091 |
| bigbluebutton | 324 | 1,529 | 21.2% | 0.204 |
| teammates | 1,646 | 8,097 | 20.3% | 0.311 |

For JabRef, just 3 out of 10 sentences contain 70% of all enrolled gold links. A system that works perfectly for only 3 sentences achieves F1=0.812 — nearly TransArc quality — while being useless for 7/10 sentences.

### Key Finding 3: Random Baseline on JabRef is Non-Trivial

On JabRef, even a **random** baseline (same output size as TransArc, random sentence-file pairs) achieves F1=0.440. This is because the gold standard contains 8,268 links out of 10 × 1,998 = 19,980 possible links (41.4% density). A random guess at the right output size hits 41.7% of the gold by chance. This density is entirely an artifact of enrollment inflation (11 raw gold entries → 8,268 enrolled links, 217.6x factor).

### Key Finding 4: Holistic Metrics Expose All Stupid Baselines

While Keyword-Grep achieves competitive F1, holistic metrics differentiate it from TransArc on projects where it underperforms:

| Metric | TransArc (avg) | Keyword-Grep (avg) | Link-All (avg) | Majority-1 (avg) |
|--------|-------------|-------------------|-------------|-----------------|
| Micro F1 | 0.803 | **0.664** | 0.240 | 0.232 |
| Macro F1 | 0.810 | **0.772** | 0.240 | 0.164 |
| Sentence Coverage | 0.751 | 0.763 | 1.000 | 0.218 |
| Usefulness | **0.887** | 0.780 | 0.087 | 0.179 |
| Noise | **0.130** | 0.208 | 0.849 | 0.819 |
| Wasted Effort | **0.14** | 0.30 | 14.19 | 4.74 |

For Link-All and Majority-1, the holistic collapse is immediate: noise >0.8 (80%+ of results are wrong), usefulness <0.2 (sentences get more wrong links than right ones), wasted effort 5-40x (developer sees 5-40 wrong files per correct one). These baselines are obviously useless.

For Keyword-Grep, the picture is subtler: it achieves good usefulness (0.780) and moderate noise (0.208), but coverage and macro F1 reveal its limitations on projects with non-obvious component names (e.g., Teammates components like "Client", "UI", "Storage" are too generic for reliable grep matching).

### Implication

**Micro-averaged F1 alone cannot distinguish TransArc from a 3-line grep script** on 2 out of 5 projects. This is not because TransArc is bad — it is because the metric:

1. **Inflates** the contribution of large correctly-mapped components
2. **Hides** complete failures on minority sentences (40% have zero recall)
3. **Rewards** any system that correctly identifies the few dominant components
4. **Ignores** developer experience (noise, wasted effort, information overload)

Comprehensive evaluation using sentence coverage, noise, usefulness, wasted effort, macro F1, and other holistic metrics is essential to distinguish meaningful trace link recovery from trivial pattern matching.

### Extreme Baselines: The Task Reduces to Component Classification

To push distributional exploitation to its limit, we introduce oracle baselines that operate at **component granularity only** — they select which components a sentence should link to, then output ALL enrolled files of those components with zero file-level precision.

| Baseline | Avg Micro F1 | Description |
|----------|------------|-------------|
| **Oracle-Subset** | **0.987** | Per-sentence: oracle-select best component SUBSET (2^K search) |
| **Oracle-Component** | **0.906** | Per-sentence: oracle-select best SINGLE component |
| TransArc | 0.803 | Full NLP pipeline |
| Keyword-Grep | 0.698 | Simple substring match |
| Round-Robin | 0.136 | Cycle sentences through components by size (zero content) |

**Oracle-Subset achieves F1=0.987 averaged across all projects** — near-perfect — using only component-level assignments. Per project:

| Project | Oracle-Subset F1 | TransArc F1 | Δ |
|---------|-----------------|-------------|---|
| mediastore | **1.000** | 0.588 | +0.412 |
| teastore | **1.000** | 0.829 | +0.171 |
| teammates | **0.934** | 0.821 | +0.113 |
| bigbluebutton | **1.000** | 0.831 | +0.169 |
| jabref | **1.000** | 0.943 | +0.057 |

Even Oracle-Single-Component (one component per sentence) achieves F1=0.906 — exceeding TransArc's 0.803 average. This means: **if you simply classify each sentence into the correct component and link to all that component's enrolled files, you outperform TransArc on micro F1 without any file-level precision.**

This proves that under enrollment-based evaluation, the SAD-CODE task effectively **reduces to component-level sentence classification**. Enrollment inflation does the rest. The full hierarchy of intelligence required:

| Rank | Baseline | Avg F1 | Intelligence Required |
|------|----------|--------|---------------------|
| 1 | Oracle-Subset | 0.987 | Component knowledge per sentence |
| 2 | Perfect-Transitive | 0.970 | Gold SAD-SAM × gold SAM-CODE |
| 3 | Oracle-Component | 0.906 | Single component per sentence |
| 4 | TransArc | 0.803 | Full NLP pipeline |
| 5 | Keyword-Grep | 0.698 | Substring match |
| 6 | Round-Robin | 0.136 | None (positional) |

The fundamental insight: **file-level precision is free under enrollment** — what matters is sentence-level coverage and component assignment accuracy, which are exactly what holistic metrics capture and micro F1 misses.

## Analysis L – Agentic LLM Baseline for SAD-CODE

Analysis K established that SAD-CODE reduces to component-level sentence classification under enrollment-based evaluation (Oracle-Subset F1=0.987). This analysis tests whether a zero-training LLM can perform that classification, replacing the entire TransArc pipeline with Claude agents.

### Approach

Multiple agentic strategies, all using Claude models with zero training:

| Strategy | Description | Agents |
|----------|------------|--------|
| Single-Agent | One Claude Sonnet agent classifies all sentences | 1 |
| Multi-Agent Majority | 3 agents (2x Sonnet + 1x Haiku), keep if >=2/3 agree | 3 |
| Multi-Agent Intersection | 3 agents, keep only if ALL agree | 3 |
| Per-Component | Specialized binary classifier per component (teammates only) | 4 |
| Self-Critique | Classifier + reviewer agent filters over-assignments | 2 |
| Adaptive Best | Best strategy selected per project (by document size heuristic) | varies |

Each agent receives: (1) the full documentation text with sentence numbers, (2) the list of component/interface names from SAM-CODE gold, (3) instructions to classify each sentence into 0+ components. The output is mapped to enrolled files via SAM-CODE gold for evaluation.

### Results: Cross-Project Micro F1

| Baseline | mediastore | teastore | teammates | bigbluebutton | jabref | **Avg** |
|----------|-----------|---------|----------|-------------|--------|---------|
| **Adaptive Best** | **0.965** | 0.764 | 0.707 | 0.710 | **0.999** | **0.829** |
| Multi-Agent Majority | **0.965** | 0.764 | 0.371 | 0.710 | 0.848 | 0.732 |
| Single-Agent | 0.361 | 0.745 | 0.377 | 0.622 | **0.999** | 0.621 |
| TransArc | 0.588 | **0.829** | **0.821** | **0.831** | 0.943 | 0.803 |
| Keyword-Grep | 0.595 | 0.515 | 0.608 | 0.827 | 0.944 | 0.698 |
| Oracle-Subset | 0.987 | 0.993 | 0.981 | 0.993 | 0.980 | 0.987 |

The adaptive LLM baseline achieves **0.829 average micro F1**, beating TransArc (0.803) by +0.026. The strategy selection follows a simple document-size heuristic (intersection for large docs, majority for medium, single for tiny).

### Per-Project Analysis

- **MediaStore** (LLM 0.965 vs TransArc 0.588, +0.377): Multi-agent majority achieves P=1.000, R=0.932. The LLM correctly identifies all components for this small, well-structured document. TransArc's low recall is due to SAD-SAM missing 13/25 gold sentences.

- **JabRef** (LLM 0.999 vs TransArc 0.943, +0.056): Single-agent achieves near-perfect classification. JabRef's 13-sentence document with clear component names is trivial for the LLM.

- **TeaStore** (LLM 0.764 vs TransArc 0.829, -0.065): LLM over-classifies behavioral sentences (ImageProvider caching, Auth hashing) that aren't in gold. TransArc's perfect precision (P=1.000) gives it the edge.

- **BigBlueButton** (LLM 0.710 vs TransArc 0.831, -0.121): HTML5 Client/Server always co-occur in gold but LLM assigns only one. Presentation Conversion wrongly assigned to 5 sentences.

- **Teammates** (LLM 0.707 vs TransArc 0.821, -0.114): Intersection vote too strict (58/92 gold sentences classified). UI's 6 FP sentences cause 2,088 file-level FPs.

### Error Analysis: Three Systematic Patterns

**1. Interface Blind Spot**: The LLM assigns `Component: X` but never `Interface: X`. For Teammates and BBB, this has zero file-level impact (Interfaces share 100% of files with Components). For TeaStore, Interfaces map to different files (26 file-level FNs).

**2. Component Co-occurrence Blindness**: BBB's HTML5 Client and HTML5 Server always co-occur in gold (shared code files) but the LLM assigns only one. This single failure pattern accounts for 320 file-level FNs.

**3. Over-classification of Behavioral Sentences**: The LLM classifies sentences describing component behavior (caching, hashing) even when those sentences have no SAD-CODE gold links. A single wrong UI assignment in Teammates causes 348 file-level FPs.

### Holistic Comparison

| Baseline | Avg Micro F1 | Avg Macro F1 | Avg Noise | Avg Coverage | Avg Usefulness |
|----------|------------|------------|-----------|------------|--------------|
| Adaptive LLM | 0.829 | **0.790** | 0.208 | **0.810** | 0.791 |
| TransArc | 0.803 | 0.699 | **0.130** | 0.751 | **0.887** |
| Keyword-Grep | 0.698 | 0.668 | 0.127 | 0.763 | 0.858 |

The LLM baseline has higher macro F1 (0.790 vs 0.699) and coverage (0.810 vs 0.751), meaning it classifies more sentences and provides more uniform per-sentence quality. TransArc has lower noise (0.130 vs 0.208) and higher usefulness (0.887 vs 0.791), meaning its outputs are more precise when it does produce links.

### Implications

1. **Zero-training LLM agents beat TransArc on average micro F1** (0.829 vs 0.803) using only component names and document text — no NLP pipeline, no training data, no code analysis.

2. **The task is solvable by reading comprehension**: The LLM demonstrates that component-level sentence classification — the core task under enrollment — is fundamentally a reading comprehension problem, not a software engineering problem.

3. **LLM and TransArc have complementary strengths**: TransArc has high precision (low noise), LLM has high coverage and macro F1. A hybrid combining TransArc's precision with LLM coverage could exceed both.

4. **Remaining LLM errors are addressable**: File-overlap co-assignment (BBB), interface-aware prompting (TeaStore), and two-phase classification (filtering behavioral sentences) could close the gap on the 3 projects where TransArc leads.

