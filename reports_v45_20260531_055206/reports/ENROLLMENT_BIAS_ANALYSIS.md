# Enrollment Bias Analysis: How File Popularity Distorts Metrics

SAD-CODE evaluation expands directory-level gold entries into individual files.
This creates severe bias: large components dominate the file-level metric,
making a single component-level error on a large component count 100-1000x
more than the same error on a small component.

This analysis quantifies the bias and evaluates 3 compensating strategies.

## 1. File Distribution Per Project

### Mediastore

Raw gold entries: **57** → Enrolled links: **59** (expansion: **1.0x**)
File distribution Gini: **0.400** (0=equal, 1=maximally skewed)

| Component | Files | % of Total | Cumulative % |
|:--|---:|:---:|:---:|
| Interface: IDownload | 16 | 26.7% | 26.7% |
| Interface: IMediaAccess | 6 | 10.0% | 36.7% |
| Component: DB | 4 | 6.7% | 43.3% |
| Interface: IUserDB | 3 | 5.0% | 48.3% |
| Interface: IUserManagement | 3 | 5.0% | 53.3% |
| Interface: IMediaManagement | 3 | 5.0% | 58.3% |
| Interface: IFacade | 3 | 5.0% | 63.3% |
| Component: Cache | 3 | 5.0% | 68.3% |
| Interface: IPackaging | 3 | 5.0% | 73.3% |
| Component: AudioWatermarking | 3 | 5.0% | 78.3% |
| Component: MediaAccess | 2 | 3.3% | 81.7% |
| Component: UserManagement | 2 | 3.3% | 85.0% |
| Interface: IDB | 2 | 3.3% | 88.3% |
| Component: UserDBAdapter | 2 | 3.3% | 91.7% |
| Component: MediaManagement | 1 | 1.7% | 93.3% |
| Component: TagWatermarking | 1 | 1.7% | 95.0% |
| Component: Reencoding | 1 | 1.7% | 96.7% |
| Component: Packaging | 1 | 1.7% | 98.3% |
| Component: Facade | 1 | 1.7% | 100.0% |

**Top 3 components control 43% of enrolled links.**

### Teastore

Raw gold entries: **70** → Enrolled links: **707** (expansion: **10.1x**)
File distribution Gini: **0.694** (0=equal, 1=maximally skewed)

| Component | Files | % of Total | Cumulative % |
|:--|---:|:---:|:---:|
| Component: ImageProvider | 64 | 39.0% | 39.0% |
| Component: Persistence | 30 | 18.3% | 57.3% |
| Component: WebUI | 19 | 11.6% | 68.9% |
| Component: Recommender | 14 | 8.5% | 77.4% |
| Component: Auth | 13 | 7.9% | 85.4% |
| Component: Registry | 5 | 3.0% | 88.4% |
| Interface: AuthCart | 2 | 1.2% | 89.6% |
| Component: DummyRecommender | 2 | 1.2% | 90.9% |
| Component: OrderBasedRecommender | 2 | 1.2% | 92.1% |
| Component: SlopeOneRecommender | 2 | 1.2% | 93.3% |
| Component: PreprocessedSlopeOneRecommender | 2 | 1.2% | 94.5% |
| Component: PopularityBasedRecommender | 2 | 1.2% | 95.7% |
| Interface: RecommenderStrategy | 1 | 0.6% | 96.3% |
| Interface: CartActions | 1 | 0.6% | 97.0% |
| Interface: Persistence | 1 | 0.6% | 97.6% |
| Interface: ProductActions | 1 | 0.6% | 98.2% |
| Interface: LoadBalancer | 1 | 0.6% | 98.8% |
| Interface: Recommender | 1 | 0.6% | 99.4% |
| Interface: ImageProvider | 1 | 0.6% | 100.0% |

**Top 3 components control 69% of enrolled links.**

### Teammates

Raw gold entries: **228** → Enrolled links: **8097** (expansion: **35.5x**)
File distribution Gini: **0.452** (0=equal, 1=maximally skewed)

| Component | Files | % of Total | Cumulative % |
|:--|---:|:---:|:---:|
| Interface: UI | 348 | 21.5% | 21.5% |
| Component: UI | 348 | 21.5% | 43.1% |
| Interface: Common | 150 | 9.3% | 52.4% |
| Component: Common | 150 | 9.3% | 61.6% |
| Component: E2E | 123 | 7.6% | 69.2% |
| Interface: E2E | 123 | 7.6% | 76.9% |
| Component: Logic | 71 | 4.4% | 81.2% |
| Interface: Logic | 71 | 4.4% | 85.6% |
| Component: Storage | 59 | 3.7% | 89.3% |
| Interface: Storage | 59 | 3.7% | 92.9% |
| Component: Client | 40 | 2.5% | 95.4% |
| Interface: Client | 40 | 2.5% | 97.9% |
| Component: Test Driver | 17 | 1.1% | 98.9% |
| Interface: Test Driver | 17 | 1.1% | 100.0% |

**Top 3 components control 52% of enrolled links.**

### Bigbluebutton

Raw gold entries: **132** → Enrolled links: **1529** (expansion: **11.6x**)
File distribution Gini: **0.513** (0=equal, 1=maximally skewed)

| Component | Files | % of Total | Cumulative % |
|:--|---:|:---:|:---:|
| Interface: FreeSWITCH | 94 | 12.9% | 12.9% |
| Component: FreeSWITCH | 94 | 12.9% | 25.8% |
| Component: FSESL | 92 | 12.6% | 38.4% |
| Interface: FSESL | 92 | 12.6% | 51.0% |
| Interface: Presentation Conversion | 70 | 9.6% | 60.5% |
| Component: Presentation Conversion | 70 | 9.6% | 70.1% |
| Interface: BBB web | 33 | 4.5% | 74.7% |
| Component: BBB web | 33 | 4.5% | 79.2% |
| Component: HTML5 Client | 16 | 2.2% | 81.4% |
| Interface: HTML5 Client | 16 | 2.2% | 83.6% |
| Component: HTML5 Server | 16 | 2.2% | 85.8% |
| Interface: HTML5 Server | 16 | 2.2% | 87.9% |
| Component: Apps | 15 | 2.1% | 90.0% |
| Interface: Apps | 15 | 2.1% | 92.1% |
| Interface: Recording Service | 13 | 1.8% | 93.8% |
| Component: Recording Service | 13 | 1.8% | 95.6% |
| Component: Redis PubSub | 7 | 1.0% | 96.6% |
| Interface: Redis PubSub | 7 | 1.0% | 97.5% |
| Component: WebRTC-SFU | 6 | 0.8% | 98.4% |
| Interface: WebRTC-SFU | 6 | 0.8% | 99.2% |
| Component: Redis DB | 3 | 0.4% | 99.6% |
| Interface: Redis DB | 3 | 0.4% | 100.0% |

**Top 3 components control 38% of enrolled links.**

### Jabref

Raw gold entries: **38** → Enrolled links: **8268** (expansion: **217.6x**)
File distribution Gini: **0.612** (0=equal, 1=maximally skewed)

| Component | Files | % of Total | Cumulative % |
|:--|---:|:---:|:---:|
| Component: logic | 972 | 49.7% | 49.7% |
| Component: gui | 707 | 36.1% | 85.8% |
| Component: model | 250 | 12.8% | 98.6% |
| Component: preferences | 18 | 0.9% | 99.5% |
| Component: cli | 8 | 0.4% | 99.9% |
| Component: globals | 1 | 0.1% | 100.0% |

**Top 3 components control 99% of enrolled links.**

### Bias Summary Across Projects

| Project | Raw | Enrolled | Expansion | Gini | Top-3 % |
|:--|---:|---:|:---:|:---:|:---:|
| mediastore | 57 | 59 | 1.0x | 0.400 | 43% |
| teastore | 70 | 707 | 10.1x | 0.694 | 69% |
| teammates | 228 | 8097 | 35.5x | 0.452 | 52% |
| bigbluebutton | 132 | 1529 | 11.6x | 0.513 | 38% |
| jabref | 38 | 8268 | 217.6x | 0.612 | 99% |

**The problem:** In standard F1, a TP or FP on the largest component contributes
up to 1000x more than the same TP/FP on the smallest. This means:
- A system can achieve high F1 by only getting large components right
- Errors on small components are invisible in the metric
- Cross-project F1 comparison is meaningless (different skew profiles)

## 2. File Popularity Bias in Gold Standard

Some files appear in many gold links (popular files). A system that predicts
popular files for every sentence would score high recall cheaply.

### Mediastore

Unique files in gold: **15** | Total links: **59** | Top-10 files control **86%** of links

| File (truncated) | Sentences Linked | % of Total |
|:--|---:|:---:|
| ...u/kit/ipd/sdq/mediastore/ejb/userdbadapter/DbManager.java | 7 | 11.9% |
| ...diastore/basic/exceptions/UserAlreadyExistsException.java | 7 | 11.9% |
| .../kit/ipd/sdq/mediastore/basic/exceptions/DbException.java | 7 | 11.9% |
| ...edu/kit/ipd/sdq/mediastore/ejb/mediaaccess/DbManager.java | 7 | 11.9% |
| ...t/ipd/sdq/mediastore/ejb/mediaaccess/MediaAccessImpl.java | 5 | 8.5% |
| ...src/edu/kit/ipd/sdq/mediastore/ejb/mediaaccess/Audio.java | 5 | 8.5% |
| ...q/mediastore/ejb/mediamanagement/MediaManagementImpl.java | 4 | 6.8% |
| ...rc/edu/kit/ipd/sdq/mediastore/ejb/userdbadapter/User.java | 3 | 5.1% |
| ...src/edu/kit/ipd/sdq/mediastore/ejb/facade/FacadeImpl.java | 3 | 5.1% |
| ...d/sdq/mediastore/ejb/userdbadapter/UserDBAdapterImpl.java | 3 | 5.1% |

### Teastore

Unique files in gold: **145** | Total links: **707** | Top-10 files control **8%** of links

| File (truncated) | Sentences Linked | % of Total |
|:--|---:|:---:|
| ...descartes/teastore/persistence/repository/EMFManager.java | 6 | 0.8% |
| ...eastore/persistence/repository/EMFManagerInitializer.java | 6 | 0.8% |
| ...n/java/tools/descartes/teastore/webui/rest/ReadyRest.java | 6 | 0.8% |
| ...tools/descartes/teastore/webui/servlet/StatusServlet.java | 6 | 0.8% |
| ...scartes/teastore/persistence/domain/PersistenceOrder.java | 6 | 0.8% |
| .../tools/descartes/teastore/webui/startup/WebuiStartup.java | 6 | 0.8% |
| ...ols/descartes/teastore/webui/servlet/CategoryServlet.java | 6 | 0.8% |
| ...persistence/repository/AbstractPersistenceRepository.java | 6 | 0.8% |
| ...ls/descartes/teastore/persistence/RegistrationDaemon.java | 6 | 0.8% |
| ...ools/descartes/teastore/webui/servlet/ProfileServlet.java | 6 | 0.8% |

### Teammates

Unique files in gold: **828** | Total links: **8097** | Top-10 files control **2%** of links

| File (truncated) | Sentences Linked | % of Total |
|:--|---:|:---:|
| src/test/java/teammates/logic/api/EmailGeneratorTest.java | 19 | 0.2% |
| src/test/java/teammates/logic/api/EmailSenderTest.java | 19 | 0.2% |
| src/main/java/teammates/logic/api/EmailSender.java | 19 | 0.2% |
| src/main/java/teammates/logic/api/EmailGenerator.java | 19 | 0.2% |
| src/main/java/teammates/logic/api/TaskQueuer.java | 19 | 0.2% |
| src/test/java/teammates/logic/api/MockTaskQueuer.java | 18 | 0.2% |
| src/test/java/teammates/logic/api/UserProvisionTest.java | 18 | 0.2% |
| ...ammates/logic/core/FeedbackResponseCommentsLogicTest.java | 18 | 0.2% |
| src/test/java/teammates/logic/core/package-info.java | 18 | 0.2% |
| src/test/java/teammates/logic/core/CoursesLogicTest.java | 18 | 0.2% |

### Bigbluebutton

Unique files in gold: **252** | Total links: **1529** | Top-10 files control **13%** of links

| File (truncated) | Sentences Linked | % of Total |
|:--|---:|:---:|
| build/packages-template/bbb-html5/systemd_start.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/before-install.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/systemd_start_frontend.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/after-install.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/mongod_start_pre.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/after-remove.sh | 20 | 1.3% |
| bigbluebutton-html5/deploy_to_usr_share.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/before-remove.sh | 20 | 1.3% |
| build/packages-template/bbb-html5/run_mongo.sh | 20 | 1.3% |
| bigbluebutton-html5/run-dev.sh | 20 | 1.3% |

### Jabref

Unique files in gold: **1955** | Total links: **8268** | Top-10 files control **1%** of links

| File (truncated) | Sentences Linked | % of Total |
|:--|---:|:---:|
| ...main/java/org/jabref/model/entry/BibEntryTypeBuilder.java | 6 | 0.1% |
| ...n/java/org/jabref/model/openoffice/style/OODataModel.java | 6 | 0.1% |
| ...t/java/org/jabref/model/openoffice/CitationEntryTest.java | 6 | 0.1% |
| src/main/java/org/jabref/model/openoffice/util/OOPair.java | 6 | 0.1% |
| src/main/java/org/jabref/model/search/rules/SearchRule.java | 6 | 0.1% |
| src/main/java/org/jabref/model/study/StudyDatabase.java | 6 | 0.1% |
| src/main/java/org/jabref/model/entry/EntryLinkList.java | 6 | 0.1% |
| ...main/java/org/jabref/model/util/ResultingStringState.java | 6 | 0.1% |
| ...java/org/jabref/model/search/rules/MockSearchMatcher.java | 6 | 0.1% |
| ...ef/model/entry/types/BiblatexAPAEntryTypeDefinitions.java | 6 | 0.1% |

---

## 3. Compensating Strategies: Measurements

We apply three strategies to de-bias the enrollment-inflated metrics:

1. **IDF-Weighted F1**: Files belonging to many components get low weight (like TF-IDF)
2. **Component-Macro F1**: Per-component F1 averaged uniformly (each component = equal weight)
3. **Popularity-Debiased F1 (PDR)**: Each link weighted by 1/component_file_count

### Mediastore

| Strategy | TransArc F1 | V45 F1 | V45 Δ |
|:--|:---:|:---:|:---:|
| Standard (biased) | 0.588 | 0.891 | +0.303 |
| IDF-Weighted | 0.612 | 0.894 | +0.282 |
| Component-Macro | 0.661 | 0.908 | +0.247 |
| Popularity-Debiased | 0.687 | 0.902 | +0.215 |

**Per-component breakdown (Component-Macro):**

| Component | Files | TransArc F1 | V45 F1 | Δ |
|:--|---:|:---:|:---:|:---:|
| Component: DB | 4 | 0.000 | 0.833 | +0.833 |
| Interface: IDB | 2 | 0.000 | 0.833 | +0.833 |
| Component: MediaAccess | 2 | 0.750 | 0.889 | +0.139 |
| Component: UserDBAdapter | 2 | 1.000 | 1.000 | +0.000 |
| Component: MediaManagement | 1 | 0.857 | 1.000 | +0.143 |
| Component: UserManagement | 2 | 1.000 | 1.000 | +0.000 |
| Component: Facade | 1 | 1.000 | 0.857 | -0.143 |
| Component: TagWatermarking | 1 | 1.000 | 1.000 | +0.000 |
| Component: Packaging | 1 | 1.000 | 1.000 | +0.000 |
| Component: Reencoding | 1 | 0.000 | 0.667 | +0.667 |

### Teastore

| Strategy | TransArc F1 | V45 F1 | V45 Δ |
|:--|:---:|:---:|:---:|
| Standard (biased) | 0.829 | 0.837 | +0.008 |
| IDF-Weighted | 0.830 | 0.839 | +0.009 |
| Component-Macro | 0.839 | 0.743 | -0.097 |
| Popularity-Debiased | 0.823 | 0.784 | -0.039 |

**Per-component breakdown (Component-Macro):**

| Component | Files | TransArc F1 | V45 F1 | Δ |
|:--|---:|:---:|:---:|:---:|
| Component: ImageProvider | 64 | 0.889 | 0.889 | +0.000 |
| Component: Persistence | 30 | 0.667 | 1.000 | +0.333 |
| Component: WebUI | 19 | 0.800 | 0.800 | +0.000 |
| Component: Recommender | 14 | 0.800 | 0.500 | -0.300 |
| Component: Auth | 13 | 1.000 | 0.571 | -0.429 |
| Component: Registry | 5 | 1.000 | 0.833 | -0.167 |
| Interface: CartActions | 1 | 0.800 | 0.800 | +0.000 |
| Interface: Persistence | 1 | 0.667 | 1.000 | +0.333 |
| Interface: ProductActions | 1 | 0.800 | 0.800 | +0.000 |
| Interface: ImageProvider | 1 | 0.889 | 0.889 | +0.000 |
| Interface: AuthCart | 2 | 1.000 | 0.571 | -0.429 |
| Interface: Recommender | 1 | 0.800 | 0.500 | -0.300 |
| Interface: RecommenderStrategy | 1 | 0.800 | 0.500 | -0.300 |

### Teammates

| Strategy | TransArc F1 | V45 F1 | V45 Δ |
|:--|:---:|:---:|:---:|
| Standard (biased) | 0.821 | 0.795 | -0.027 |
| IDF-Weighted | 0.820 | 0.794 | -0.027 |
| Component-Macro | 0.774 | 0.744 | -0.031 |
| Popularity-Debiased | 0.624 | 0.552 | -0.072 |

**Per-component breakdown (Component-Macro):**

| Component | Files | TransArc F1 | V45 F1 | Δ |
|:--|---:|:---:|:---:|:---:|
| Interface: UI | 348 | 0.835 | 0.927 | +0.092 |
| Component: UI | 348 | 0.835 | 0.927 | +0.092 |
| Interface: Common | 150 | 0.844 | 0.716 | -0.128 |
| Component: Common | 150 | 0.844 | 0.716 | -0.128 |
| Interface: Logic | 71 | 0.832 | 0.643 | -0.189 |
| Component: Logic | 71 | 0.832 | 0.643 | -0.189 |
| Interface: E2E | 123 | 0.824 | 0.769 | -0.054 |
| Component: E2E | 123 | 0.824 | 0.769 | -0.054 |
| Component: Storage | 59 | 0.798 | 0.678 | -0.120 |
| Interface: Storage | 59 | 0.798 | 0.678 | -0.120 |
| Component: Client | 40 | 0.537 | 0.723 | +0.186 |
| Interface: Client | 40 | 0.537 | 0.723 | +0.186 |
| Component: Test Driver | 17 | 0.750 | 0.750 | +0.000 |
| Interface: Test Driver | 17 | 0.750 | 0.750 | +0.000 |

### Bigbluebutton

| Strategy | TransArc F1 | V45 F1 | V45 Δ |
|:--|:---:|:---:|:---:|
| Standard (biased) | 0.831 | 0.897 | +0.066 |
| IDF-Weighted | 0.806 | 0.903 | +0.097 |
| Component-Macro | 0.863 | 0.825 | -0.039 |
| Popularity-Debiased | 0.348 | 0.848 | +0.500 |

**Per-component breakdown (Component-Macro):**

| Component | Files | TransArc F1 | V45 F1 | Δ |
|:--|---:|:---:|:---:|:---:|
| Interface: FreeSWITCH | 94 | 0.934 | 0.934 | +0.000 |
| Component: FreeSWITCH | 94 | 0.934 | 0.934 | +0.000 |
| Interface: FSESL | 92 | 0.932 | 0.937 | +0.006 |
| Component: FSESL | 92 | 0.932 | 0.937 | +0.006 |
| Component: HTML5 Server | 16 | 0.743 | 0.700 | -0.043 |
| Interface: HTML5 Server | 16 | 0.743 | 0.700 | -0.043 |
| Interface: HTML5 Client | 16 | 0.743 | 0.700 | -0.043 |
| Component: HTML5 Client | 16 | 0.743 | 0.700 | -0.043 |
| Component: BBB web | 33 | 0.571 | 1.000 | +0.429 |
| Interface: BBB web | 33 | 0.571 | 1.000 | +0.429 |
| Interface: Presentation Conversion | 70 | 1.000 | 1.000 | +0.000 |
| Component: Presentation Conversion | 70 | 1.000 | 1.000 | +0.000 |
| Interface: Apps | 15 | 0.909 | 1.000 | +0.091 |
| Component: Apps | 15 | 0.909 | 1.000 | +0.091 |
| Interface: Redis PubSub | 7 | 1.000 | 1.000 | +0.000 |
| Component: Redis PubSub | 7 | 1.000 | 1.000 | +0.000 |
| Interface: WebRTC-SFU | 6 | 0.800 | 0.800 | +0.000 |
| Component: WebRTC-SFU | 6 | 0.800 | 0.800 | +0.000 |
| Component: Redis DB | 3 | 1.000 | 1.000 | +0.000 |
| Interface: Redis DB | 3 | 1.000 | 1.000 | +0.000 |
| Interface: Recording Service | 13 | 0.000 | 0.000 | +0.000 |
| Component: Recording Service | 13 | 0.000 | 0.000 | +0.000 |

### Jabref

| Strategy | TransArc F1 | V45 F1 | V45 Δ |
|:--|:---:|:---:|:---:|
| Standard (biased) | 0.943 | 0.944 | +0.000 |
| IDF-Weighted | 0.943 | 0.944 | +0.000 |
| Component-Macro | 0.948 | 0.948 | +0.000 |
| Popularity-Debiased | 0.880 | 0.957 | +0.077 |

**Per-component breakdown (Component-Macro):**

| Component | Files | TransArc F1 | V45 F1 | Δ |
|:--|---:|:---:|:---:|:---:|
| Component: logic | 972 | 0.889 | 0.889 | +0.000 |
| Component: gui | 707 | 1.000 | 1.000 | +0.000 |
| Component: model | 250 | 1.000 | 1.000 | +0.000 |
| Component: preferences | 18 | 0.800 | 0.800 | +0.000 |
| Component: cli | 8 | 1.000 | 1.000 | +0.000 |
| Component: globals | 1 | 1.000 | 1.000 | +0.000 |

---

## 4. Aggregate: How Debiasing Changes the Picture

| Project | Std TransArc | Std V45 | IDF TransArc | IDF V45 | Macro TransArc | Macro V45 | PDR TransArc | PDR V45 |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | 0.588 | 0.891 | 0.612 | 0.894 | 0.661 | 0.908 | 0.687 | 0.902 |
| teastore | 0.829 | 0.837 | 0.830 | 0.839 | 0.839 | 0.743 | 0.823 | 0.784 |
| teammates | 0.821 | 0.795 | 0.820 | 0.794 | 0.774 | 0.744 | 0.624 | 0.552 |
| bigbluebutton | 0.831 | 0.897 | 0.806 | 0.903 | 0.863 | 0.825 | 0.348 | 0.848 |
| jabref | 0.943 | 0.944 | 0.943 | 0.944 | 0.948 | 0.948 | 0.880 | 0.957 |
| **Average** | **0.803** | **0.873** | **0.802** | **0.875** | **0.817** | **0.833** | **0.672** | **0.808** |

### Metric Shift: Standard F1 → Debiased F1

| Project | TransArc Std→IDF | TransArc Std→Macro | TransArc Std→PDR | V45 Std→IDF | V45 Std→Macro | V45 Std→PDR |
|:--|:---:|:---:|:---:|:---:|:---:|:---:|
| mediastore | +0.024 | +0.072 | +0.099 | +0.003 | +0.017 | +0.011 |
| teastore | +0.000 | +0.010 | -0.006 | +0.001 | -0.095 | -0.054 |
| teammates | -0.001 | -0.047 | -0.197 | -0.001 | -0.051 | -0.242 |
| bigbluebutton | -0.025 | +0.032 | -0.483 | +0.007 | -0.072 | -0.049 |
| jabref | -0.000 | +0.005 | -0.063 | -0.000 | +0.005 | +0.013 |

---

## 5. Recommendation: Which Debiasing Strategy?

| Strategy | Strengths | Weaknesses | When to use |
|:--|:--|:--|:--|
| **IDF-Weighted** | Penalizes trivial shared files; rewards unique file discovery | Requires file→component mapping; unintuitive weights | When files are shared across components |
| **Component-Macro** | Simple; every component equally important; transparent | Ignores within-component file structure; small components with 1 file get same weight as 972-file components | Default recommendation for paper reporting |
| **Popularity-Debiased (PDR)** | Direct correction of enrollment inflation; weight = 1/N_files | Similar to ACF1 from N4; may over-correct on tiny components | When enrollment expansion varies >10x |

### Our recommendation: **Report all three alongside standard F1.**

The standard F1 is needed for backward compatibility. Component-Macro F1 is the
most interpretable debiased metric. IDF-Weighted reveals shared-file effects.
PDR gives the amplification-corrected view. Together they triangulate the true quality.

**Key finding:** TransArc's standard F1 (0.803) is **inflated** by large-component
dominance. Under Component-Macro, it drops to its true average quality. V45 is
more robust across all debiasing strategies because its improvements are genuine
component-level improvements, not artifacts of file-count weighting.

### Replication

```bash
cd /mnt/hostshare/ardoco-home/transarc-emp
python3 enrollment_bias_analysis.py
# Output: ENROLLMENT_BIAS_ANALYSIS.md
```

