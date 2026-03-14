# SAM-CODE Error Cascade & Holistic Pipeline Analysis

## 1. SAM-CODE FP Cascade: Each Wrong File × Number of Sentences

Every SAM-CODE FP (M, C_wrong) is composed with all intermediate SAD-SAM
sentences for M, producing |sentences(M)| SAD-CODE links — most of which are FPs.

### SAM-CODE FPs Ranked by Induced SAD-CODE FPs

| Rank | Project | Model Element | Wrong Code File | SAD-SAM Sents | →SAD-CODE TPs | →SAD-CODE FPs | Total |
|------|---------|--------------|----------------|---------------|-------------|-------------|-------|
| 1 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/after-install.sh` | 12 | 0 | **12** | 12 |
| 2 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/install-hasura.sh` | 12 | 0 | **12** | 12 |
| 3 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/after-remove.sh` | 12 | 0 | **12** | 12 |
| 4 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/build_hasura.sh` | 12 | 0 | **12** | 12 |
| 5 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/build.sh` | 12 | 0 | **12** | 12 |
| 6 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/before-remove.sh` | 12 | 0 | **12** | 12 |
| 7 | bigbluebutton | Component: HTML5 Server | `bbb-html5-nodejs/build.sh` | 12 | 0 | **12** | 12 |
| 8 | bigbluebutton | Component: HTML5 Server | `bbb-graphql-server/opts-jammy.sh` | 12 | 0 | **12** | 12 |
| 9 | bigbluebutton | Component: FreeSWITCH | `cron.hourly/bbb-resync-freeswitch` | 8 | 0 | **8** | 8 |
| 10 | bigbluebutton | Component: Apps | `messages/BbbAppsIsAliveMessage.java` | 5 | 0 | **5** | 5 |
| 11 | bigbluebutton | Component: HTML5 Client | `bbb-graphql-client-test/deploy.sh` | 4 | 0 | **4** | 4 |
| 12 | bigbluebutton | Component: HTML5 Client | `bbb-html5-nodejs/build.sh` | 4 | 0 | **4** | 4 |
| 13 | bigbluebutton | Component: HTML5 Client | `client/run-watch.sh` | 4 | 0 | **4** | 4 |
| 14 | bigbluebutton | Component: HTML5 Client | `client/run.sh` | 4 | 0 | **4** | 4 |
| 15 | bigbluebutton | Component: HTML5 Client | `client/stress-test.sh` | 4 | 0 | **4** | 4 |
| 16 | jabref | Component: gui | `category/GUITest.java` | 4 | 0 | **4** | 4 |
| 17 | bigbluebutton | Component: Presentation Conversion | `bbb-playback-presentation/build.sh` | 2 | 0 | **2** | 2 |
| 18 | bigbluebutton | Component: Presentation Conversion | `bbb-playback-presentation/opts-jammy.sh` | 2 | 0 | **2** | 2 |
| 19 | bigbluebutton | Component: Presentation Conversion | `bbb-playback-presentation/after-install.sh` | 2 | 0 | **2** | 2 |
| 20 | bigbluebutton | Component: Recording Service | `service/ServiceUtils.java` | 0 | 0 | **0** | 0 |
| 21 | bigbluebutton | Component: Recording Service | `service/XmlService.java` | 0 | 0 | **0** | 0 |
| 22 | bigbluebutton | Component: Recording Service | `service/ValidationService.java` | 0 | 0 | **0** | 0 |
| 23 | bigbluebutton | Component: Recording Service | `service/SessionService.java` | 0 | 0 | **0** | 0 |
| 24 | bigbluebutton | Component: Recording Service | `impl/XmlServiceImpl.java` | 0 | 0 | **0** | 0 |

### SAM-CODE FP Cascade Summary

| Project | SAM-CODE FPs | Total Induced SAD-CODE FPs | Avg Amplification (sents/FP) | SAD-CODE FPs from SAM-CODE | % of All TransArc FPs |
|---------|-------------|---------------------------|------------------------------|--------------------------|---------------------|
| mediastore | 0 | 0 | 0.0 | 0 | 0.0% |
| teastore | 0 | 0 | 0.0 | 0 | 0.0% |
| teammates | 0 | 0 | 0.0 | 0 | 0.0% |
| bigbluebutton | 23 | 135 | 5.9 | 135 | 47.9% |
| jabref | 1 | 4 | 4.0 | 4 | 0.4% |

## 2. SAM-CODE FN Cascade: Each Missed File × Number of Sentences

Every SAM-CODE FN (M, C_missed) means sentences correctly linked to M via
SAD-SAM cannot reach C_missed. The missed code file causes SAD-CODE FNs
for all sentences that should link to it.

### SAM-CODE FNs Ranked by Caused SAD-CODE FNs

| Rank | Project | Model Element | Missed Code File | Caused SAD-CODE FNs |
|------|---------|--------------|-----------------|-------------------|
| 1 | bigbluebutton | Component: BBB web | `api/ParamsProcessorUtilTest.java` | **3** |
| 2 | bigbluebutton | Component: BBB web | `bigbluebutton-web/build.sh` | **3** |
| 3 | bigbluebutton | Component: BBB web | `prescheck/Main.java` | **3** |
| 4 | bigbluebutton | Component: BBB web | `messaging/NullMessagingService.java` | **3** |
| 5 | bigbluebutton | Component: BBB web | `bigbluebutton-web/run.sh` | **3** |
| 6 | bigbluebutton | Component: BBB web | `bigbluebutton-web/run-dev.sh` | **3** |
| 7 | bigbluebutton | Component: BBB web | `pres-checker/build.sh` | **3** |
| 8 | bigbluebutton | Component: BBB web | `bigbluebutton-web/deploy_to_usr_share.sh` | **3** |
| 9 | bigbluebutton | Component: BBB web | `bigbluebutton-web/gradlew` | **3** |
| 10 | bigbluebutton | Component: BBB web | `bigbluebutton-web/grailsw` | **3** |
| 11 | bigbluebutton | Component: BBB web | `pres-checker/run.sh` | **3** |

### SAM-CODE FN Cascade Summary

| Project | SAM-CODE FNs | With SAD-CODE Impact | Total Caused SAD-CODE FNs | % of All TransArc FNs |
|---------|-------------|---------------------|--------------------------|--------------------|
| mediastore | 40 | 0 | 0 | 0.0% |
| teastore | 9 | 0 | 0 | 0.0% |
| teammates | 808 | 0 | 0 | 0.0% |
| bigbluebutton | 379 | 11 | 33 | 13.6% |
| jabref | 0 | 0 | 0 | 0.0% |

## 3. SAM-CODE TP Value: Each Correct File × Number of Sentences

Each SAM-CODE TP (M, C_correct) is composed with all SAD-SAM sentences for M.
With correct SAD-SAM links this produces TPs; with wrong SAD-SAM links, FPs.

### SAM-CODE TPs Ranked by SAD-CODE TPs Produced (Top 20)

| Rank | Project | Model Element | Correct Code File | →SAD-CODE TPs | →SAD-CODE FPs | Precision |
|------|---------|--------------|------------------|-------------|-------------|-----------|
| 1 | teammates | Component: Logic | `core/UsageStatisticsLogic.java` | **17** | 4 | 0.810 |
| 2 | teammates | Component: Logic | `api/package-info.java` | **17** | 4 | 0.810 |
| 3 | teammates | Component: Logic | `core/FeedbackResponsesLogic.java` | **17** | 4 | 0.810 |
| 4 | teammates | Component: Logic | `core/package-info.java` | **17** | 4 | 0.810 |
| 5 | teammates | Component: Logic | `api/AuthProxy.java` | **17** | 4 | 0.810 |
| 6 | teammates | Component: Logic | `api/EmailGenerator.java` | **17** | 4 | 0.810 |
| 7 | teammates | Component: Logic | `api/RecaptchaVerifier.java` | **17** | 4 | 0.810 |
| 8 | teammates | Component: Logic | `core/LogicStarter.java` | **17** | 4 | 0.810 |
| 9 | teammates | Component: Logic | `core/AccountsLogic.java` | **17** | 4 | 0.810 |
| 10 | teammates | Component: Logic | `api/LogsProcessor.java` | **17** | 4 | 0.810 |
| 11 | teammates | Component: Logic | `core/DataBundleLogic.java` | **17** | 4 | 0.810 |
| 12 | teammates | Component: Logic | `core/FeedbackSessionsLogic.java` | **17** | 4 | 0.810 |
| 13 | teammates | Component: Logic | `core/FeedbackResponseCommentsLogic.java` | **17** | 4 | 0.810 |
| 14 | teammates | Component: Logic | `api/UserProvision.java` | **17** | 4 | 0.810 |
| 15 | teammates | Component: Logic | `core/StudentsLogic.java` | **17** | 4 | 0.810 |
| 16 | teammates | Component: Logic | `api/Logic.java` | **17** | 4 | 0.810 |
| 17 | teammates | Component: Logic | `api/EmailSender.java` | **17** | 4 | 0.810 |
| 18 | teammates | Component: Logic | `core/FeedbackQuestionsLogic.java` | **17** | 4 | 0.810 |
| 19 | teammates | Component: Logic | `core/DeadlineExtensionsLogic.java` | **17** | 4 | 0.810 |
| 20 | teammates | Component: Logic | `core/InstructorsLogic.java` | **17** | 4 | 0.810 |

### SAM-CODE TPs with Lowest Cascade Precision (correct file, but most SAD-CODE output is wrong)

| Project | Model Element | Correct Code File | →SAD-CODE TPs | →SAD-CODE FPs | Precision | Root Cause |
|---------|--------------|------------------|-------------|-------------|-----------|-----------|
| mediastore | Component: Reencoding | `reencoder/ReEncoderImpl.java` | 0 | 1 | 0.000 | 1 SAD-SAM FPs for Component: Reencoding |
| teammates | Component: Client | `statistics/StatisticsPerInstitute.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/package-info.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `statistics/package-info.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForFeedbackSessionMismatchedTimezone.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/MockCourseWithLargeResponseScript.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/ListActiveInstructors.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `statistics/StatisticsBundle.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForInstructorNullIsArchivedField.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForTextQuestionDetailsFormat.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForSampleGoogleIdInStudentAttributes.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForStudentsAndTeamsRecipientType.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataBundleRegenerator.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForSanitizedDataInInstructorAttributes.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |
| teammates | Component: Client | `scripts/DataMigrationForUnencryptedKeyForStudents.java` | 3 | 5 | 0.375 | 5 SAD-SAM FPs for Component: Client |

## 4. Holistic Per-Model-Element Pipeline View

For each model element M, the combined effect of SAD-SAM and SAM-CODE
errors on the final SAD-CODE output. Shows how errors from both components
compound through the transitive composition.

### MEDIASTORE

TransArc output: 25 TPs + 1 FPs = 26 | FNs: 34

| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|
| Component: UserDBAdapter | 6 | 3 | 2 | **6** | 0 | 0 | 0 | 0 | 0 |
| Component: MediaAccess | 10 | 3 | 2 | **6** | 0 | 0 | 0 | 0 | 0 |
| Component: UserManagement | 4 | 2 | 2 | **4** | 0 | 0 | 0 | 0 | 0 |
| Component: Facade | 3 | 3 | 1 | **3** | 0 | 0 | 0 | 0 | 0 |
| Component: MediaManagement | 4 | 3 | 1 | **3** | 0 | 0 | 0 | 0 | 0 |
| Component: TagWatermarking | 2 | 2 | 1 | **2** | 0 | 0 | 0 | 0 | 0 |
| Component: Packaging | 1 | 1 | 1 | **1** | 0 | 0 | 0 | 0 | 0 |
| Component: Reencoding | 1 | 1 | 1 | **0** | 1 | 0 | 0 | 0 | 0 |
| Component: Cache | 0 | 0 | 3 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: AudioWatermarking | 0 | 0 | 3 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: DB | 28 | 0 | 3 | **0** | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | | | | **25** | **1** | **0** | **0** | **0** | **0** |

### TEASTORE

TransArc output: 501 TPs + 0 FPs = 501 | FNs: 206

| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|
| Component: ImageProvider | 320 | 4 | 64 | **256** | 0 | 0 | 0 | 0 | 0 |
| Component: Persistence | 180 | 3 | 30 | **90** | 0 | 0 | 0 | 0 | 0 |
| Component: WebUI | 114 | 4 | 19 | **76** | 0 | 0 | 0 | 0 | 0 |
| Component: Recommender | 42 | 2 | 14 | **28** | 0 | 0 | 0 | 0 | 0 |
| Component: Auth | 26 | 2 | 13 | **26** | 0 | 0 | 0 | 0 | 0 |
| Component: Registry | 25 | 5 | 5 | **25** | 0 | 0 | 0 | 0 | 0 |
| Component: DummyRecommender | 0 | 0 | 2 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: PreprocessedSlopeOneRecommender | 0 | 0 | 2 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: PopularityBasedRecommender | 0 | 0 | 2 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: OrderBasedRecommender | 0 | 0 | 2 | **0** | 0 | 0 | 0 | 0 | 0 |
| Component: SlopeOneRecommender | 0 | 0 | 2 | **0** | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | | | | **501** | **0** | **0** | **0** | **0** | **0** |

### TEAMMATES

TransArc output: 7307 TPs + 2395 FPs = 9702 | FNs: 790

| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|
| Component: UI | 3132 | 12 | 348 | **3257** | 919 | 0 | 0 | 0 | 0 |
| Component: Common | 750 | 11 | 150 | **1264** | 386 | 0 | 0 | 0 | 0 |
| Component: Logic | 1065 | 21 | 71 | **1138** | 353 | 0 | 0 | 0 | 0 |
| Component: E2E | 615 | 10 | 123 | **861** | 369 | 0 | 0 | 0 | 0 |
| Component: Storage | 590 | 13 | 59 | **604** | 163 | 0 | 0 | 0 | 0 |
| Component: Client | 160 | 8 | 40 | **132** | 188 | 0 | 0 | 0 | 0 |
| Component: Test Driver | 68 | 4 | 17 | **51** | 17 | 0 | 0 | 0 | 0 |
| _KGVMcKETEeu-mYqkDskRow | 0 | 2 | 0 | **0** | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | | | | **7307** | **2395** | **0** | **0** | **0** | **0** |

### BIGBLUEBUTTON

TransArc output: 1287 TPs + 282 FPs = 1569 | FNs: 242

| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|
| Component: FreeSWITCH | 658 | 8 | 95 | **648** | 10 | 7 | 1 | 94 | 0 |
| Component: HTML5 Server | 208 | 12 | 24 | **160** | 32 | 80 | 16 | 0 | 0 |
| Component: Presentation Conversion | 140 | 2 | 73 | **140** | 0 | 6 | 0 | 0 | 0 |
| Component: FSESL | 184 | 1 | 92 | **92** | 0 | 0 | 0 | 0 | 0 |
| Component: HTML5 Client | 224 | 4 | 21 | **64** | 0 | 20 | 0 | 0 | 0 |
| Component: Apps | 90 | 5 | 16 | **75** | 0 | 5 | 0 | 0 | 0 |
| Component: BBB web | 165 | 3 | 22 | **66** | 0 | 0 | 0 | 0 | 33 |
| Component: WebRTC-SFU | 24 | 6 | 6 | **24** | 12 | 0 | 0 | 0 | 0 |
| Component: Redis PubSub | 28 | 4 | 7 | **28** | 0 | 0 | 0 | 0 | 0 |
| Component: Redis DB | 6 | 2 | 3 | **6** | 0 | 0 | 0 | 0 | 0 |
| Component: Recording Service | 0 | 0 | 15 | **0** | 0 | 0 | 0 | 0 | 0 |
| _oN4CMFkHEeyewPSmlgszyA | 0 | 2 | 0 | **0** | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | | | | **1303** | **54** | **118** | **17** | **94** | **33** |

### JABREF

TransArc output: 8268 TPs + 994 FPs = 9262 | FNs: 0

| Model Element | Gold S×C | Int S | Int C | →TPs | →FPs (SS) | →FPs (SC) | →FPs (Both) | →FPs (Combo) | FNs(SC) |
|--------------|---------|-------|-------|------|----------|----------|------------|-------------|---------|
| Component: logic | 3888 | 5 | 972 | **3888** | 972 | 0 | 0 | 0 | 0 |
| Component: gui | 2828 | 4 | 708 | **2828** | 0 | 4 | 0 | 0 | 0 |
| Component: model | 1500 | 6 | 250 | **1500** | 0 | 0 | 0 | 0 | 0 |
| Component: preferences | 36 | 3 | 18 | **36** | 18 | 0 | 0 | 0 | 0 |
| Component: cli | 16 | 2 | 8 | **16** | 0 | 0 | 0 | 0 | 0 |
| Component: globals | 0 | 0 | 1 | **0** | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | | | | **8268** | **990** | **4** | **0** | **0** | **0** |

## 5. Error Interaction: How SAD-SAM and SAM-CODE Errors Compound

The transitive product means errors multiply: |FPs| = |SAD-SAM FP sents| × |SAM-CODE files| + |SAD-SAM sents| × |SAM-CODE FP files|.
This section quantifies how the two error sources interact per model element.

### Per-Model Error Budget

For each model element with errors, decompose the total SAD-CODE output:

| Project | Model Element | SS TPs × SC TPs → | SS TPs × SC FPs → | SS FPs × SC TPs → | SS FPs × SC FPs → | Total Output |
|---------|--------------|-------------------|-------------------|-------------------|-------------------|-------------|
| mediastore | Component: Reencoding | 0 (0%) | 0 (0%) | 1 (100%) | 0 (0%) | 1 |
| teammates | Component: UI | 3257 (78%) | 0 (0%) | 919 (22%) | 0 (0%) | 4176 |
| teammates | Component: Common | 1264 (77%) | 0 (0%) | 386 (23%) | 0 (0%) | 1650 |
| teammates | Component: E2E | 861 (70%) | 0 (0%) | 369 (30%) | 0 (0%) | 1230 |
| teammates | Component: Logic | 1138 (76%) | 0 (0%) | 353 (24%) | 0 (0%) | 1491 |
| teammates | Component: Client | 132 (41%) | 0 (0%) | 188 (59%) | 0 (0%) | 320 |
| teammates | Component: Storage | 604 (79%) | 0 (0%) | 163 (21%) | 0 (0%) | 767 |
| teammates | Component: Test Driver | 51 (75%) | 0 (0%) | 17 (25%) | 0 (0%) | 68 |
| bigbluebutton | Component: HTML5 Server | 160 (56%) | 80 (28%) | 32 (11%) | 16 (6%) | 288 |
| bigbluebutton | Component: FreeSWITCH | 742 (98%) | 7 (1%) | 10 (1%) | 1 (0%) | 760 |
| bigbluebutton | Component: HTML5 Client | 64 (76%) | 20 (24%) | 0 (0%) | 0 (0%) | 84 |
| bigbluebutton | Component: WebRTC-SFU | 24 (67%) | 0 (0%) | 12 (33%) | 0 (0%) | 36 |
| bigbluebutton | Component: Presentation Conversion | 140 (96%) | 6 (4%) | 0 (0%) | 0 (0%) | 146 |
| bigbluebutton | Component: Apps | 75 (94%) | 5 (6%) | 0 (0%) | 0 (0%) | 80 |
| bigbluebutton | Component: BBB web | 66 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 66 |
| jabref | Component: logic | 3888 (80%) | 0 (0%) | 972 (20%) | 0 (0%) | 4860 |
| jabref | Component: preferences | 36 (67%) | 0 (0%) | 18 (33%) | 0 (0%) | 54 |
| jabref | Component: gui | 2828 (100%) | 4 (0%) | 0 (0%) | 0 (0%) | 2832 |

## 6. Amplification Comparison: SAD-SAM vs SAM-CODE

How does the amplification factor compare between the two error sources?
- SAD-SAM FP amplification = number of SAM-CODE files for that model element
- SAM-CODE FP amplification = number of SAD-SAM sentences for that model element

| Project | Component | SAD-SAM FPs | ×Files | =SAD-CODE FPs | SAM-CODE FPs | ×Sents | =SAD-CODE FPs |
|---------|----------|------------|--------|-------------|-------------|--------|-------------|
| mediastore | Component: Reencoding | 1 | ×1 | 1 | 0 | ×1 | 0 |
| teammates | Component: UI | 3 | ×348 | 919 | 0 | ×12 | 0 |
| teammates | Component: Common | 6 | ×150 | 386 | 0 | ×11 | 0 |
| teammates | Component: E2E | 5 | ×123 | 369 | 0 | ×10 | 0 |
| teammates | Component: Logic | 7 | ×71 | 353 | 0 | ×21 | 0 |
| teammates | Component: Client | 5 | ×40 | 188 | 0 | ×8 | 0 |
| teammates | Component: Storage | 5 | ×59 | 163 | 0 | ×13 | 0 |
| teammates | Component: Test Driver | 1 | ×17 | 17 | 0 | ×4 | 0 |
| bigbluebutton | Component: HTML5 Server | 2 | ×24 | 48 | 8 | ×12 | 96 |
| bigbluebutton | Component: FreeSWITCH | 1 | ×95 | 11 | 1 | ×8 | 8 |
| bigbluebutton | Component: HTML5 Client | 0 | ×21 | 0 | 5 | ×4 | 20 |
| bigbluebutton | Component: WebRTC-SFU | 2 | ×6 | 12 | 0 | ×6 | 0 |
| bigbluebutton | Component: Presentation Conversion | 0 | ×73 | 0 | 3 | ×2 | 6 |
| bigbluebutton | Component: Apps | 0 | ×16 | 0 | 1 | ×5 | 5 |
| jabref | Component: logic | 1 | ×972 | 972 | 0 | ×5 | 0 |
| jabref | Component: preferences | 1 | ×18 | 18 | 0 | ×3 | 0 |
| jabref | Component: gui | 0 | ×708 | 0 | 1 | ×4 | 4 |

## 7. Cross-Project Error Source Summary

| Project | SAD-CODE TPs | FPs (SAD-SAM) | FPs (SAM-CODE) | FPs (Both) | FPs (Combo) | FNs from SC | Total FNs |
|---------|------------|-------------|-------------|-----------|-----------|-----------|----------|
| mediastore | 25 | 1 | 0 | 0 | 0 | 0 | 34 |
| teastore | 501 | 0 | 0 | 0 | 0 | 0 | 206 |
| teammates | 7307 | 2395 | 0 | 0 | 0 | 0 | 790 |
| bigbluebutton | 1303 | 54 | 118 | 17 | 94 | 33 | 242 |
| jabref | 8268 | 990 | 4 | 0 | 0 | 0 | 0 |
| **TOTAL** | **17404** | **3440** | **122** | **17** | **94** | **33** | **1272** |

**FP attribution**: SAD-SAM caused 3440/3673 (93.7%), SAM-CODE caused 122/3673 (3.3%), Both 17/3673 (0.5%), Combination 94/3673 (2.6%)

**FN attribution**: SAM-CODE FNs caused 33/1272 (2.6%) of TransArc FNs. The remaining 1239 (97.4%) are from SAD-SAM misses or theoretical limits.

### Key Insight: The Asymmetry of Error Sources

SAD-SAM errors dominate because of a fundamental asymmetry in the transitive product:

- A SAD-SAM FP for model M gets multiplied by ALL SAM-CODE files for M
- A SAM-CODE FP for model M gets multiplied by ALL SAD-SAM sentences for M

Since SAM-CODE footprints (files per model element) are typically much larger
than SAD-SAM footprints (sentences per model element), SAD-SAM FPs amplify more.

| Project | Avg Files/Model | Avg Sents/Model | Ratio (Files/Sents) |
|---------|----------------|----------------|-------------------|
| mediastore | 1.4 | 2.2 | 0.6x |
| teastore | 24.2 | 3.3 | 7.2x |
| teammates | 115.4 | 11.3 | 10.2x |
| bigbluebutton | 35.9 | 4.7 | 7.6x |
| jabref | 391.2 | 4.0 | 97.8x |

This ratio explains why SAD-SAM errors cause ~94% of TransArc FPs:
each SAD-SAM FP is amplified by the (larger) file count, while each
SAM-CODE FP is amplified by the (smaller) sentence count.

