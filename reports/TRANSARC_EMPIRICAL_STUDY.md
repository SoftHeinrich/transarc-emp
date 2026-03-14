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
  - Code: `src/test/java/teammates/common/datatransfer/questions/FeedbackTextResponseDetailsTest.java`
  - Via model element(s): Component: Common

- Sentence 17: "Selenium Java is used to automate E2E testing with actual Web browsers."
  - Code: `src/e2e/java/teammates/e2e/cases/axe/AdminSessionsPageAxeTest.java`
  - Via model element(s): Component: E2E

#### bigbluebutton

**SAD_SAM_CAUSED** (54 FPs):

- Sentence 74: "WebRTC provides the user with high-quality audio with lower delay."
  - Code: `build/packages-template/bbb-webrtc-sfu/build.sh`
  - Via model element(s): Component: WebRTC-SFU

- Sentence 60: "Communication between apps and FreeSWITCH Event Socket Layer (fsels) uses messages through redis pub..."
  - Code: `build/packages-template/bbb-freeswitch-core/build.sh`
  - Via model element(s): Component: FreeSWITCH

**SAM_CODE_CAUSED** (117 FPs):

- Sentence 72: "A user can join the voice conference (running in FreeSWITCH) from the BigBlueButton HTML5 client or ..."
  - Code: `bigbluebutton-config/cron.hourly/bbb-resync-freeswitch`
  - Via model element(s): Component: FreeSWITCH

- Sentence 6: "The HTML5 client connects directly with the BigBlueButton server over port 443 (SSL), from loading t..."
  - Code: `bbb-graphql-client-test/deploy.sh`
  - Via model element(s): Component: HTML5 Client

**BOTH_CAUSED** (17 FPs):

- Sentence 68: "Kurento Media Server KMS is a media server that implements both SFU and MCU models."
  - Code: `build/packages-template/bbb-graphql-server/build.sh`
  - Via model element(s): Component: HTML5 Server

- Sentence 68: "Kurento Media Server KMS is a media server that implements both SFU and MCU models."
  - Code: `build/packages-template/bbb-graphql-server/after-install.sh`
  - Via model element(s): Component: HTML5 Server

**COMBINATION_ERROR** (94 FPs):

- Sentence 59: "This allows others who are using voice conference systems other than FreeSWITCH to easily create the..."
  - Code: `bbb-fsesl-client/src/main/java/org/freeswitch/esl/client/manager/DefaultManagerConnection.java`
  - Via model element(s): Component: FreeSWITCH

- Sentence 59: "This allows others who are using voice conference systems other than FreeSWITCH to easily create the..."
  - Code: `akka-bbb-fsesl/src/main/java/org/bigbluebutton/freeswitch/voice/freeswitch/actions/DelayedCommand.java`
  - Via model element(s): Component: FreeSWITCH

#### jabref

**SAD_SAM_CAUSED** (990 FPs):

- Sentence 5: "The model represents the most important data structures (BibDatases, BibEntries, Events, and related..."
  - Code: `src/main/java/org/jabref/logic/citationstyle/CSLAdapter.java`
  - Via model element(s): Component: logic

- Sentence 5: "The model represents the most important data structures (BibDatases, BibEntries, Events, and related..."
  - Code: `src/main/java/org/jabref/logic/importer/ParserResult.java`
  - Via model element(s): Component: logic

**SAM_CODE_CAUSED** (4 FPs):

- Sentence 7: "Only the gui knows the user and his preferences and can interact with him to help him solve tasks."
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

- Sentence 32: "All salted hashes of passwords are also stored in the Database component."
  - Expected code: `mediastore.ejb.userdbadapter/src/edu/kit/ipd/sdq/mediastore/ejb/userdbadapter/DbManager.java`
  - Required bridging model(s): ['Component: DB']
  - Miss type: no_link

- Sentence 31: "The Database component then executes the actual query for files."
  - Expected code: `mediastore.basic/src/edu/kit/ipd/sdq/mediastore/basic/exceptions/UserAlreadyExistsException.java`
  - Required bridging model(s): ['Component: DB']
  - Miss type: no_link

#### teastore

**SAD_SAM_MISS** (206 FNs):

- Sentence 23: "It maps the relational entities to the JSON entity objects passed between services using the Eclipse..."
  - Expected code: `services/tools.descartes.teastore.persistence/src/main/java/tools/descartes/teastore/persistence/repository/CacheManager.java`
  - Required bridging model(s): ['Component: Persistence']
  - Miss type: no_link

- Sentence 11: "It matches the provided product ID or UI name (the filename for images not representing a product an..."
  - Expected code: `services/tools.descartes.teastore.image/src/test/java/tools/descartes/teastore/image/storage/rules/TestStoreAll.java`
  - Required bridging model(s): ['Component: ImageProvider']
  - Miss type: no_link

#### teammates

**THEORETICAL_LIMIT** (544 FNs):

- Sentence 179: "x.webapi contains system test cases for testing the user-invoked actions."
  - Expected code: `src/test/java/teammates/ui/webapi/FeedbackSessionClosedRemindersActionTest.java`
  - Gold SAD-SAM models for sentence: NONE
  - Gold SAM-CODE models for code: ['Interface: UI', 'Component: UI']

- Sentence 126: "Instead, a corresponding non-persistent data transfer object named Attributes (e.g., CourseAttribute..."
  - Expected code: `src/main/java/teammates/common/datatransfer/attributes/CourseAttributes.java`
  - Gold SAD-SAM models for sentence: NONE
  - Gold SAM-CODE models for code: ['Interface: Common', 'Component: Common']

**SAD_SAM_MISS** (246 FNs):

- Sentence 168: "This component automates the testing of TEAMMATES."
  - Expected code: `src/test/java/teammates/test/TestPropertiesTest.java`
  - Required bridging model(s): ['Component: Test Driver']
  - Miss type: no_link

- Sentence 120: "In particular, it is reponsible for the following."
  - Expected code: `src/main/java/teammates/storage/entity/Instructor.java`
  - Required bridging model(s): ['Component: Storage']
  - Miss type: no_link

#### bigbluebutton

**THEORETICAL_LIMIT** (8 FNs):

- Sentence 58: "We have extracted out the component that integrates with FreeSWITCH into it’s own application."
  - Expected code: `akka-bbb-fsesl/src/debian/DEBIAN/postrm`
  - Gold SAD-SAM models for sentence: ['Component: FreeSWITCH']
  - Gold SAM-CODE models for code: ['Interface: FSESL', 'Component: FSESL']

- Sentence 58: "We have extracted out the component that integrates with FreeSWITCH into it’s own application."
  - Expected code: `akka-bbb-fsesl/src/debian/DEBIAN/postinst`
  - Gold SAD-SAM models for sentence: ['Component: FreeSWITCH']
  - Gold SAM-CODE models for code: ['Interface: FSESL', 'Component: FSESL']

**SAD_SAM_MISS** (201 FNs):

- Sentence 37: "BigBlueButton web application is a Java-based application written in Scala."
  - Expected code: `build/packages-template/bbb-web/setenv.sh`
  - Required bridging model(s): ['Component: BBB web']
  - Miss type: no_link

- Sentence 37: "BigBlueButton web application is a Java-based application written in Scala."
  - Expected code: `bbb-common-web/src/main/java/org/bigbluebutton/web/services/UserCleanupTimerTask.java`
  - Required bridging model(s): ['Component: BBB web']
  - Miss type: no_link

**SAM_CODE_MISS** (33 FNs):

- Sentence 36: "BBB web."
  - Expected code: `bigbluebutton-web/test/groovy/org/bigbluebutton/api/ParamsProcessorUtilTest.java`
  - TransArc found model(s): ['Component: BBB web']

- Sentence 30: "If more than one backend is running, bbb-web splits the load in round-robin fashion by assigning an ..."
  - Expected code: `bigbluebutton-web/build.sh`
  - TransArc found model(s): ['Component: BBB web']

#### jabref

## Analysis D – Error Propagation / Amplification

One component error can induce multiple TransArc errors. This analysis quantifies the cascade.

### SAD-SAM FP Amplification (Top offenders)

| Project | SAD-SAM FP (M, S) | Model Element | Induced TransArc FPs |
|---------|-------------------|---------------|---------------------|
| mediastore | (_o10-YHDrEeSqnN80MQ2..., S37) | Component: Reencoding | 1 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S26) | Component: UI | 348 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S23) | Component: UI | 348 |
| teammates | (_1lMqsKESEeu-mYqkDsk..., S22) | Component: UI | 223 |
| bigbluebutton | (_yGgUMFkHEeyewPSmlgs..., S18) | Component: HTML5 Server | 24 |
| bigbluebutton | (_yGgUMFkHEeyewPSmlgs..., S68) | Component: HTML5 Server | 24 |
| bigbluebutton | (_nwrCMFwPEeyiuNx_RO7..., S60) | Component: FreeSWITCH | 11 |
| jabref | (_He3LoEl4Ee243f2e4VW..., S5) | Component: logic | 972 |
| jabref | (_NUdtEEl4Ee243f2e4VW..., S7) | Component: preferences | 18 |

### SAM-CODE FP Amplification (Top offenders)

| Project | SAM-CODE FP (M, C) | Model Element | Induced TransArc FPs |
|---------|--------------------|--------------|-----------------------|
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/install-hasura.sh) | Component: HTML5 Server | 12 |
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/after-remove.sh) | Component: HTML5 Server | 12 |
| bigbluebutton | (Component: HTML5 Server, bbb-graphql-server/build_hasura.sh) | Component: HTML5 Server | 12 |
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
| 1 | SAD-SAM FP | Component: UI | Sentence 26: "ui.website is not a Java package...." | 348 |
| 2 | SAD-SAM FP | Component: UI | Sentence 23: "ui.website is not a real package...." | 348 |
| 3 | SAD-SAM FP | Component: UI | Sentence 22: "logic, ui.website, ui.controller represent an appl..." | 223 |
| 4 | SAD-SAM FP | Component: Common | Sentence 158: "common.exceptions contains custom exceptions...." | 139 |
| 5 | SAD-SAM FP | Component: E2E | Sentence 190: "e2e.cases contains test cases...." | 123 |

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
| 3 | SAM-CODE FP | Component: HTML5 Server | `install-hasura.sh` | 12 |
| 4 | SAM-CODE FP | Component: HTML5 Server | `after-remove.sh` | 12 |
| 5 | SAM-CODE FP | Component: HTML5 Server | `build_hasura.sh` | 12 |

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

