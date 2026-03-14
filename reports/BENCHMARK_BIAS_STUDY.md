# Benchmark Bias & Long-Tail Distribution Study

A systematic analysis of distributional bias in the ARDoCo benchmark
across SAD-SAM, SAM-CODE, and SAD-CODE tasks for 5 projects:
MediaStore, TeaStore, Teammates, BigBlueButton, JabRef.

## 1. SAD-SAM Long-Tail Distribution

### 1.1 Model Element Fan-Out (sentences per model element)

| Project | Model Elements | With Links | UME (no links) | Total Links | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|---------------|------------|----------------|-------------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 19 | 10 | 10 | 31 | 1 | 3 | 7 | 3.1 | 0.306 | 3.10 | 0.516 |
| teastore | 19 | 6 | 13 | 27 | 2 | 5 | 6 | 4.5 | 0.179 | 2.50 | 0.630 |
| teammates | 14 | 8 | 7 | 57 | 4 | 5 | 15 | 7.1 | 0.261 | 2.83 | 0.596 |
| bigbluebutton | 22 | 11 | 12 | 62 | 2 | 4 | 14 | 5.6 | 0.370 | 3.13 | 0.548 |
| jabref | 6 | 5 | 1 | 18 | 2 | 4 | 6 | 3.6 | 0.222 | 2.20 | 0.778 |

#### Model Element Fan-Out Histograms

**mediastore** (10 elements with links):
```
  1 │ ██████████████████████████ (2)
  2 │ ██████████████████████████ (2)
  3 │ ████████████████████████████████████████ (3)
  4 │ █████████████ (1)
  5 │ █████████████ (1)
  7 │ █████████████ (1)
```

**teastore** (6 elements with links):
```
  2 │ ████████████████████ (1)
  3 │ ████████████████████ (1)
  5 │ ████████████████████████████████████████ (2)
  6 │ ████████████████████████████████████████ (2)
```

**teammates** (8 elements with links):
```
   4 │ ██████████████████████████ (2)
   5 │ ████████████████████████████████████████ (3)
   9 │ █████████████ (1)
  10 │ █████████████ (1)
  15 │ █████████████ (1)
```

**bigbluebutton** (11 elements with links):
```
   2 │ ████████████████████████████████████████ (3)
   3 │ █████████████ (1)
   4 │ ██████████████████████████ (2)
   5 │ █████████████ (1)
   6 │ █████████████ (1)
   7 │ █████████████ (1)
  13 │ █████████████ (1)
  14 │ █████████████ (1)
```

**jabref** (5 elements with links):
```
  2 │ ████████████████████████████████████████ (2)
  4 │ ████████████████████████████████████████ (2)
  6 │ ████████████████████ (1)
```

#### Undocumented Model Elements (UMEs)

- **mediastore**: 10 UMEs: Component: AudioWatermarking, Interface: IUserManagement, Interface: IFacade, Interface: IUserDB, Component: Cache, Interface: IPackaging, Interface: IDownload, Interface: IMediaAccess, Interface: IMediaManagement, Interface: IDB
- **teastore**: 13 UMEs: Interface: ProductActions, Component: OrderBasedRecommender, Component: SlopeOneRecommender, Interface: Persistence, Component: DummyRecommender, Interface: ImageProvider, Interface: RecommenderStrategy, Interface: CartActions, Interface: Recommender, Component: PreprocessedSlopeOneRecommender, Interface: LoadBalancer, Component: PopularityBasedRecommender, Interface: AuthCart
- **teammates**: 7 UMEs: Interface: E2E, Interface: Client, Interface: Logic, Interface: Storage, Interface: Common, Interface: UI, Interface: Test Driver
- **bigbluebutton**: 12 UMEs: Interface: FreeSWITCH, Interface: Presentation Conversion, Interface: FSESL, Interface: WebRTC-SFU, Component: Recording Service, Interface: Apps, Interface: Recording Service, Interface: HTML5 Client, Interface: HTML5 Server, Interface: Redis PubSub, Interface: BBB web, Interface: Redis DB
- **jabref**: 1 UMEs: Component: globals

### 1.2 Sentence Fan-Out (model elements per sentence)

| Project | Total Sentences | Linked | Unlinked | % Linked | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|----------------|--------|----------|----------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 37 | 27 | 10 | 73% | 1 | 1 | 2 | 1.1 | 0.110 | 4.70 | 0.194 |
| teastore | 43 | 23 | 20 | 53% | 1 | 1 | 2 | 1.2 | 0.122 | 4.46 | 0.222 |
| teammates | 198 | 45 | 153 | 23% | 1 | 1 | 7 | 1.3 | 0.189 | 5.28 | 0.193 |
| bigbluebutton | 87 | 48 | 39 | 55% | 1 | 1 | 3 | 1.3 | 0.176 | 5.48 | 0.129 |
| jabref | 13 | 10 | 3 | 77% | 1 | 2 | 3 | 1.8 | 0.256 | 3.16 | 0.500 |

#### Sentence Fan-Out Histograms

**mediastore** (27 linked sentences):
```
  1 │ ████████████████████████████████████████ (23)
  2 │ ██████ (4)
```

**teastore** (23 linked sentences):
```
  1 │ ████████████████████████████████████████ (19)
  2 │ ████████ (4)
```

**teammates** (45 linked sentences):
```
  1 │ ████████████████████████████████████████ (38)
  2 │ ██████ (6)
  7 │ █ (1)
```

**bigbluebutton** (48 linked sentences):
```
  1 │ ████████████████████████████████████████ (36)
  2 │ ███████████ (10)
  3 │ ██ (2)
```

**jabref** (10 linked sentences):
```
  1 │ ████████████████████████████████████████ (5)
  2 │ ████████████████ (2)
  3 │ ████████████████████████ (3)
```

## 2. SAD-CODE Long-Tail Distribution (Pre- and Post-Enrollment)

### 2.1 Enrollment Expansion Overview

| Project | Raw Links | Enrolled Links | Expansion Ratio | Directory Entries |
|---------|-----------|----------------|-----------------|-------------------|
| mediastore | 57 | 59 | 1.0x | 2 |
| teastore | 70 | 707 | 10.1x | 43 |
| teammates | 228 | 8097 | 35.5x | 151 |
| bigbluebutton | 132 | 1529 | 11.6x | 116 |
| jabref | 38 | 8268 | 217.6x | 38 |

### 2.2 Per-Sentence Fan-Out (pre vs post enrollment)

| Project | Pre: Min | Pre: Med | Pre: Max | Pre: Gini | Post: Min | Post: Med | Post: Max | Post: Gini |
|---------|----------|----------|----------|-----------|-----------|-----------|-----------|------------|
| mediastore | 1 | 2 | 6 | 0.349 | 1 | 2 | 6 | 0.331 |
| teastore | 1 | 2 | 11 | 0.396 | 5 | 19 | 83 | 0.448 |
| teammates | 1 | 2 | 12 | 0.364 | 1 | 59 | 808 | 0.645 |
| bigbluebutton | 1 | 2 | 9 | 0.279 | 3 | 16 | 114 | 0.472 |
| jabref | 1 | 2 | 7 | 0.326 | 8 | 478 | 1929 | 0.527 |

### 2.3 Per-Code-Entity Fan-Out (post enrollment)

| Project | Unique Files | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|-------------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 15 | 1 | 3 | 7 | 3.9 | 0.310 | 3.68 | 0.356 |
| teastore | 145 | 2 | 5 | 6 | 4.9 | 0.125 | 7.13 | 0.025 |
| teammates | 828 | 2 | 10 | 19 | 9.8 | 0.185 | 9.60 | 0.007 |
| bigbluebutton | 252 | 2 | 5 | 20 | 6.1 | 0.346 | 7.66 | 0.039 |
| jabref | 1955 | 2 | 4 | 6 | 4.2 | 0.059 | 10.91 | 0.002 |

### 2.4 Top Expansion Factors

**mediastore** (top-5 directory expansions):

| Sentence | Directory | Expanded Files |
|----------|-----------|----------------|
| 13 | `mediastore.ejb.usermanagement/ejbModule/edu/kit/ipd/sdq/mediastore/ejb/usermanagement/` | 2 |
| 11 | `mediastore.ejb.usermanagement/ejbModule/edu/kit/ipd/sdq/mediastore/ejb/usermanagement/` | 2 |

**teastore** (top-5 directory expansions):

| Sentence | Directory | Expanded Files |
|----------|-----------|----------------|
| 10 | `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/` | 38 |
| 2 | `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/` | 38 |
| 7 | `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/` | 38 |
| 11 | `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/` | 38 |
| 12 | `services/tools.descartes.teastore.image/src/main/java/tools/descartes/teastore/image/` | 38 |

**teammates** (top-5 directory expansions):

| Sentence | Directory | Expanded Files |
|----------|-----------|----------------|
| 4 | `src/main/java/teammates/ui/` | 235 |
| 5 | `src/main/java/teammates/ui/` | 235 |
| 29 | `src/main/java/teammates/ui/` | 235 |
| 7 | `src/main/java/teammates/ui/` | 235 |
| 97 | `src/main/java/teammates/ui/` | 235 |

**bigbluebutton** (top-5 directory expansions):

| Sentence | Directory | Expanded Files |
|----------|-----------|----------------|
| 81 | `bbb-common-web/src/main/java/org/bigbluebutton/presentation/` | 70 |
| 80 | `bbb-common-web/src/main/java/org/bigbluebutton/presentation/` | 70 |
| 57 | `akka-bbb-fsesl/` | 59 |
| 58 | `akka-bbb-fsesl/` | 59 |
| 60 | `akka-bbb-fsesl/` | 59 |

**jabref** (top-5 directory expansions):

| Sentence | Directory | Expanded Files |
|----------|-----------|----------------|
| 7 | `src/main/java/org/jabref/gui/` | 642 |
| 4 | `src/main/java/org/jabref/gui/` | 642 |
| 1 | `src/main/java/org/jabref/gui/` | 642 |
| 6 | `src/main/java/org/jabref/gui/` | 642 |
| 6 | `src/main/java/org/jabref/logic/` | 575 |

## 3. SAM-CODE Long-Tail Distribution

### 3.1 Per Architectural Element (code files per element)

| Project | AE Count | Raw Links | Enrolled Links | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|----------|-----------|----------------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 19 | 55 | 60 | 1 | 3 | 16 | 3.2 | 0.400 | 3.76 | 0.433 |
| teastore | 19 | 37 | 164 | 1 | 2 | 64 | 8.6 | 0.694 | 2.86 | 0.689 |
| teammates | 14 | 22 | 1616 | 17 | 71 | 348 | 115.4 | 0.452 | 3.30 | 0.524 |
| bigbluebutton | 22 | 64 | 730 | 3 | 16 | 94 | 33.2 | 0.513 | 3.80 | 0.384 |
| jabref | 6 | 11 | 1956 | 1 | 134 | 972 | 326.0 | 0.612 | 1.51 | 0.986 |

#### Detailed Per-Element Fan-Out

**mediastore**:

| Rank | Element | Type | Files |
|------|---------|------|-------|
| 1 | Interface: IDownload | Interface | 16 |
| 2 | Interface: IMediaAccess | Interface | 6 |
| 3 | Component: DB | Component | 4 |
| 4 | Interface: IUserDB | Interface | 3 |
| 5 | Interface: IUserManagement | Interface | 3 |
| 6 | Component: Cache | Component | 3 |
| 7 | Interface: IMediaManagement | Interface | 3 |
| 8 | Interface: IFacade | Interface | 3 |
| 9 | Interface: IPackaging | Interface | 3 |
| 10 | Component: AudioWatermarking | Component | 3 |
| 11 | Component: MediaAccess | Component | 2 |
| 12 | Component: UserManagement | Component | 2 |
| 13 | Component: UserDBAdapter | Component | 2 |
| 14 | Interface: IDB | Interface | 2 |
| 15 | Component: Packaging | Component | 1 |
| 16 | Component: Facade | Component | 1 |
| 17 | Component: Reencoding | Component | 1 |
| 18 | Component: MediaManagement | Component | 1 |
| 19 | Component: TagWatermarking | Component | 1 |

**teastore**:

| Rank | Element | Type | Files |
|------|---------|------|-------|
| 1 | Component: ImageProvider | Component | 64 |
| 2 | Component: Persistence | Component | 30 |
| 3 | Component: WebUI | Component | 19 |
| 4 | Component: Recommender | Component | 14 |
| 5 | Component: Auth | Component | 13 |
| 6 | Component: Registry | Component | 5 |
| 7 | Component: PreprocessedSlopeOneRecommender | Component | 2 |
| 8 | Interface: AuthCart | Interface | 2 |
| 9 | Component: SlopeOneRecommender | Component | 2 |
| 10 | Component: OrderBasedRecommender | Component | 2 |
| 11 | Component: PopularityBasedRecommender | Component | 2 |
| 12 | Component: DummyRecommender | Component | 2 |
| 13 | Interface: LoadBalancer | Interface | 1 |
| 14 | Interface: Persistence | Interface | 1 |
| 15 | Interface: ProductActions | Interface | 1 |
| 16 | Interface: RecommenderStrategy | Interface | 1 |
| 17 | Interface: CartActions | Interface | 1 |
| 18 | Interface: ImageProvider | Interface | 1 |
| 19 | Interface: Recommender | Interface | 1 |

**teammates**:

| Rank | Element | Type | Files |
|------|---------|------|-------|
| 1 | Component: UI | Component | 348 |
| 2 | Interface: UI | Interface | 348 |
| 3 | Component: Common | Component | 150 |
| 4 | Interface: Common | Interface | 150 |
| 5 | Component: E2E | Component | 123 |
| 6 | Interface: E2E | Interface | 123 |
| 7 | Component: Logic | Component | 71 |
| 8 | Interface: Logic | Interface | 71 |
| 9 | Component: Storage | Component | 59 |
| 10 | Interface: Storage | Interface | 59 |
| 11 | Component: Client | Component | 40 |
| 12 | Interface: Client | Interface | 40 |
| 13 | Interface: Test Driver | Interface | 17 |
| 14 | Component: Test Driver | Component | 17 |

**bigbluebutton**:

| Rank | Element | Type | Files |
|------|---------|------|-------|
| 1 | Interface: FreeSWITCH | Interface | 94 |
| 2 | Component: FreeSWITCH | Component | 94 |
| 3 | Interface: FSESL | Interface | 92 |
| 4 | Component: FSESL | Component | 92 |
| 5 | Component: Presentation Conversion | Component | 70 |
| 6 | Interface: Presentation Conversion | Interface | 70 |
| 7 | Component: BBB web | Component | 33 |
| 8 | Interface: BBB web | Interface | 33 |
| 9 | Component: HTML5 Client | Component | 16 |
| 10 | Interface: HTML5 Client | Interface | 16 |
| 11 | Interface: HTML5 Server | Interface | 16 |
| 12 | Component: HTML5 Server | Component | 16 |
| 13 | Component: Apps | Component | 15 |
| 14 | Interface: Apps | Interface | 15 |
| 15 | Interface: Recording Service | Interface | 13 |
| 16 | Component: Recording Service | Component | 13 |
| 17 | Component: Redis PubSub | Component | 7 |
| 18 | Interface: Redis PubSub | Interface | 7 |
| 19 | Component: WebRTC-SFU | Component | 6 |
| 20 | Interface: WebRTC-SFU | Interface | 6 |
| 21 | Component: Redis DB | Component | 3 |
| 22 | Interface: Redis DB | Interface | 3 |

**jabref**:

| Rank | Element | Type | Files |
|------|---------|------|-------|
| 1 | Component: logic | Component | 972 |
| 2 | Component: gui | Component | 707 |
| 3 | Component: model | Component | 250 |
| 4 | Component: preferences | Component | 18 |
| 5 | Component: cli | Component | 8 |
| 6 | Component: globals | Component | 1 |

### 3.2 Per Code File (architectural elements per file)

| Project | Unique Files | Min | Median | Max | Mean | Gini |
|---------|-------------|-----|--------|-----|------|------|
| mediastore | 58 | 1 | 1 | 2 | 1.0 | 0.032 |
| teastore | 156 | 1 | 1 | 3 | 1.1 | 0.047 |
| teammates | 808 | 2 | 2 | 2 | 2.0 | 0.000 |
| bigbluebutton | 265 | 2 | 2 | 4 | 2.8 | 0.171 |
| jabref | 1955 | 1 | 1 | 2 | 1.0 | 0.001 |

### 3.3 Component vs Interface Split

| Project | Components | Comp. Files (mean) | Interfaces | Iface. Files (mean) | File Ratio (C/I) |
|---------|-----------|-------------------|------------|--------------------|--------------------|
| mediastore | 11 | 1.9 | 8 | 4.9 | 0.4 |
| teastore | 11 | 14.1 | 8 | 1.1 | 12.5 |
| teammates | 7 | 115.4 | 7 | 115.4 | 1.0 |
| bigbluebutton | 11 | 33.2 | 11 | 33.2 | 1.0 |
| jabref | 6 | 326.0 | 0 | 0.0 | N/A (no interfaces) |

## 4. Sentence Position Bias

Are trace-linked sentences concentrated in certain positions (beginning/end)?

### 4.1 SAD-SAM Link Density by Position Quartile

| Project | Q1 (start) | Q2 | Q3 | Q4 (end) | Overall | Chi-sq (df=3) |
|---------|-----------|----|----|----------|---------|---------------|
| mediastore | 0.60 | 0.67 | 0.78 | 0.89 | 0.73 | 0.41 |
| teastore | 0.91 | 0.27 | 0.55 | 0.40 | 0.53 | 5.00 |
| teammates | 0.30 | 0.16 | 0.24 | 0.20 | 0.23 | 2.38 |
| bigbluebutton | 0.64 | 0.27 | 0.77 | 0.52 | 0.55 | 5.50 |
| jabref | 0.75 | 1.00 | 0.67 | 0.67 | 0.77 | 0.40 |

*Chi-squared critical value at alpha=0.05, df=3 is 7.81. Values above this suggest significant position bias.*

### 4.2 SAD-CODE Link Density by Position Quartile

| Project | Q1 (start) | Q2 | Q3 | Q4 (end) | Linked Sentences |
|---------|-----------|----|----|----------|-----------------|
| mediastore | 0.60 | 0.67 | 0.78 | 0.67 | 25/37 |
| teastore | 0.91 | 0.27 | 0.55 | 0.40 | 23/43 |
| teammates | 0.52 | 0.37 | 0.44 | 0.55 | 93/198 |
| bigbluebutton | 0.64 | 0.27 | 0.73 | 0.43 | 45/87 |
| jabref | 0.75 | 1.00 | 0.67 | 0.67 | 10/13 |

### 4.3 Position Bias Visualization

**mediastore** (SAD-SAM, Chi-sq=0.41):
```
  Q1 (start) │ ████████████████████ 0.60 (6/10)
  Q2        │ ██████████████████████ 0.67 (6/9)
  Q3        │ ██████████████████████████ 0.78 (7/9)
  Q4 (end)  │ ██████████████████████████████ 0.89 (8/9)
```

**teastore** (SAD-SAM, Chi-sq=5.00):
```
  Q1 (start) │ ██████████████████████████████ 0.91 (10/11)
  Q2        │ █████████ 0.27 (3/11)
  Q3        │ ██████████████████ 0.55 (6/11)
  Q4 (end)  │ █████████████ 0.40 (4/10)
```

**teammates** (SAD-SAM, Chi-sq=2.38):
```
  Q1 (start) │ ██████████████████████████████ 0.30 (15/50)
  Q2        │ ████████████████ 0.16 (8/49)
  Q3        │ ████████████████████████ 0.24 (12/50)
  Q4 (end)  │ ████████████████████ 0.20 (10/49)
```

**bigbluebutton** (SAD-SAM, Chi-sq=5.50):
```
  Q1 (start) │ ████████████████████████ 0.64 (14/22)
  Q2        │ ██████████ 0.27 (6/22)
  Q3        │ ██████████████████████████████ 0.77 (17/22)
  Q4 (end)  │ ████████████████████ 0.52 (11/21)
```

**jabref** (SAD-SAM, Chi-sq=0.40):
```
  Q1 (start) │ ██████████████████████ 0.75 (3/4)
  Q2        │ ██████████████████████████████ 1.00 (3/3)
  Q3        │ ████████████████████ 0.67 (2/3)
  Q4 (end)  │ ████████████████████ 0.67 (2/3)
```

## 5. Cross-Task Correlation (SAD-SAM vs SAD-CODE per Sentence)

Do sentences with many SAD-SAM links also have many SAD-CODE links?

| Project | Sentences | SAD-SAM Linked | SAD-CODE Linked | Both | Neither | Pearson r | Spearman rho |
|---------|-----------|---------------|----------------|------|---------|-----------|-------------|
| mediastore | 37 | 27 | 25 | 25 | 10 | 0.753 | 0.804 |
| teastore | 43 | 23 | 23 | 23 | 20 | 0.818 | 0.948 |
| teammates | 198 | 45 | 92 | 42 | 103 | 0.766 | 0.656 |
| bigbluebutton | 87 | 48 | 45 | 45 | 39 | 0.503 | 0.840 |
| jabref | 13 | 10 | 10 | 10 | 3 | 0.877 | 0.911 |

**Interpretation**:

- Pearson r close to 1.0 means sentences with high SAD-SAM fan-out tend to have high SAD-CODE fan-out.
- This suggests the transitive assumption (SAD→SAM→CODE) captures real structure.
- Low correlation would suggest the tasks measure different aspects of the documentation.

## 6. Project-Level Imbalance

### 6.1 Raw Dimensions

| Project | Sentences | Model Elements | Code Files | SAD-SAM Links | SAM-CODE Links | SAD-CODE Links |
|---------|-----------|---------------|------------|---------------|----------------|----------------|
| mediastore | 37 | 19 | 97 | 31 | 60 | 59 |
| teastore | 43 | 19 | 205 | 27 | 164 | 707 |
| teammates | 198 | 14 | 833 | 57 | 1616 | 8097 |
| bigbluebutton | 87 | 22 | 551 | 62 | 730 | 1529 |
| jabref | 13 | 6 | 1998 | 18 | 1956 | 8268 |

### 6.2 Link Densities

| Project | SAD-SAM/sent | SAD-SAM/model | SAD-CODE/sent | SAD-CODE/file | SAM-CODE/AE | SAM-CODE/file |
|---------|-------------|---------------|---------------|---------------|-------------|---------------|
| mediastore | 0.84 | 3.1 | 1.59 | 3.93 | 3.2 | 1.03 |
| teastore | 0.63 | 4.5 | 16.44 | 4.88 | 8.6 | 1.05 |
| teammates | 0.29 | 7.1 | 40.89 | 9.78 | 115.4 | 2.00 |
| bigbluebutton | 0.71 | 5.6 | 17.57 | 6.07 | 33.2 | 2.75 |
| jabref | 1.38 | 3.6 | 636.00 | 4.23 | 326.0 | 1.00 |

### 6.3 Cross-Project Heterogeneity (Coefficient of Variation)

| Metric | Min | Max | Mean | CV |
|--------|-----|-----|------|----|
| Total Sentences | 13.00 | 198.00 | 75.60 | 0.869 |
| Model Elements | 6.00 | 22.00 | 16.00 | 0.351 |
| Code Files | 97.00 | 1998.00 | 736.80 | 0.926 |
| SAD-SAM Links | 18.00 | 62.00 | 39.00 | 0.444 |
| SAM-CODE Links | 60.00 | 1956.00 | 905.20 | 0.842 |
| SAD-CODE Links | 59.00 | 8268.00 | 3732.00 | 0.982 |
| SAD-SAM Links/Sent | 0.29 | 1.38 | 0.77 | 0.464 |
| SAD-CODE Links/Sent | 1.59 | 636.00 | 142.50 | 1.734 |
| SAM-CODE Links/AE | 3.16 | 326.00 | 97.28 | 1.246 |

*CV > 0.5 indicates high cross-project heterogeneity; CV > 1.0 indicates extreme variation.*

## 7. Exploitability Analysis (Popularity Baselines)

How well does a naive 'link-everything-to-top-K-entities' baseline perform?
If a simple popularity baseline achieves high F1, the benchmark may be too easy to game.

### 7.1 SAD-SAM Top-K Baseline

Strategy: Link every sentence to the K most popular model elements.

| Project | Top-1 P | Top-1 R | Top-1 F1 | Top-3 P | Top-3 R | Top-3 F1 | Top-5 P | Top-5 R | Top-5 F1 |
|---------|---------|---------|----------|---------|---------|----------|---------|---------|----------|
| mediastore | 0.189 | 0.226 | 0.206 | 0.144 | 0.516 | 0.225 | 0.119 | 0.710 | 0.204 |
| teastore | 0.140 | 0.222 | 0.171 | 0.132 | 0.630 | 0.218 | 0.116 | 0.926 | 0.207 |
| teammates | 0.076 | 0.263 | 0.118 | 0.057 | 0.596 | 0.104 | 0.044 | 0.772 | 0.084 |
| bigbluebutton | 0.161 | 0.226 | 0.188 | 0.130 | 0.548 | 0.211 | 0.103 | 0.726 | 0.181 |
| jabref | 0.462 | 0.333 | 0.387 | 0.359 | 0.778 | 0.491 | 0.277 | 1.000 | 0.434 |

### 7.2 SAD-CODE Top-K Baseline

Strategy: Link every sentence to the K most popular code files.

| Project | Top-1 F1 | Top-3 F1 | Top-5 F1 | Top-10 F1 | TransArc F1 | LLM F1 |
|---------|----------|----------|----------|-----------|-------------|--------|
| mediastore | 0.146 | 0.247 | 0.270 | 0.238 | 0.588 | 0.965 |
| teastore | 0.016 | 0.043 | 0.065 | 0.106 | 0.829 | 0.845 |
| teammates | 0.005 | 0.013 | 0.021 | 0.037 | 0.821 | 0.646 |
| bigbluebutton | 0.025 | 0.067 | 0.102 | 0.167 | 0.831 | 0.797 |
| jabref | 0.001 | 0.004 | 0.007 | 0.014 | 0.943 | 0.916 |

### 7.3 Most Popular Entities

| Project | Most Popular Model Element | Links | Most Popular Code File | Links |
|---------|--------------------------|-------|----------------------|-------|
| mediastore | Component: DB | 7 | `DbManager.java` | 7 |
| teastore | Component: Persistence | 6 | `IndexServlet.java` | 6 |
| teammates | Component: Logic | 15 | `EmailSender.java` | 19 |
| bigbluebutton | Component: HTML5 Client | 14 | `run-dev.sh` | 20 |
| jabref | Component: model | 6 | `BibEntry.java` | 6 |

### 7.4 Exploitability Assessment

Does the popularity baseline beat the actual system? If Top-K F1 exceeds TransArc F1, the benchmark
distribution can be trivially exploited without understanding any semantics.

| Project | Top-5 SAD-CODE F1 | TransArc F1 | Exploitable? | Top-10 F1 | Beats TransArc? |
|---------|------------------|-------------|-------------|-----------|-----------------|
| mediastore | 0.270 | 0.588 | No | 0.238 | No |
| teastore | 0.065 | 0.829 | No | 0.106 | No |
| teammates | 0.021 | 0.821 | No | 0.037 | No |
| bigbluebutton | 0.102 | 0.831 | No | 0.167 | No |
| jabref | 0.007 | 0.943 | No | 0.014 | No |

## 8. Comprehensive Summary Statistics

### 8.1 SAD-SAM

#### Model Elements Side

| Project | Total Links | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|-------------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 31 | 10 | 1 | 3 | 7 | 3.1 | 0.306 | 3.10 | 0.516 |
| teastore | 27 | 6 | 2 | 5 | 6 | 4.5 | 0.179 | 2.50 | 0.630 |
| teammates | 57 | 8 | 4 | 5 | 15 | 7.1 | 0.261 | 2.83 | 0.596 |
| bigbluebutton | 62 | 11 | 2 | 4 | 14 | 5.6 | 0.370 | 3.13 | 0.548 |
| jabref | 18 | 5 | 2 | 4 | 6 | 3.6 | 0.222 | 2.20 | 0.778 |

#### Sentences Side

| Project | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 27 | 1 | 1 | 2 | 1.1 | 0.110 | 4.70 | 0.194 |
| teastore | 23 | 1 | 1 | 2 | 1.2 | 0.122 | 4.46 | 0.222 |
| teammates | 45 | 1 | 1 | 7 | 1.3 | 0.189 | 5.28 | 0.193 |
| bigbluebutton | 48 | 1 | 1 | 3 | 1.3 | 0.176 | 5.48 | 0.129 |
| jabref | 10 | 1 | 2 | 3 | 1.8 | 0.256 | 3.16 | 0.500 |

### 8.2 SAM-CODE

#### Arch. Elements Side

| Project | Total Links | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|-------------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 60 | 19 | 1 | 3 | 16 | 3.2 | 0.400 | 3.76 | 0.433 |
| teastore | 164 | 19 | 1 | 2 | 64 | 8.6 | 0.694 | 2.86 | 0.689 |
| teammates | 1616 | 14 | 17 | 71 | 348 | 115.4 | 0.452 | 3.30 | 0.524 |
| bigbluebutton | 730 | 22 | 3 | 16 | 94 | 33.2 | 0.513 | 3.80 | 0.384 |
| jabref | 1956 | 6 | 1 | 134 | 972 | 326.0 | 0.612 | 1.51 | 0.986 |

#### Code Files Side

| Project | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 58 | 1 | 1 | 2 | 1.0 | 0.032 | 5.84 | 0.083 |
| teastore | 156 | 1 | 1 | 3 | 1.1 | 0.047 | 7.26 | 0.043 |
| teammates | 808 | 2 | 2 | 2 | 2.0 | 0.000 | 9.66 | 0.004 |
| bigbluebutton | 265 | 2 | 2 | 4 | 2.8 | 0.171 | 7.96 | 0.016 |
| jabref | 1955 | 1 | 1 | 2 | 1.0 | 0.001 | 10.93 | 0.002 |

### 8.3 SAD-CODE

#### Sentences Side

| Project | Total Links | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|-------------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 59 | 25 | 1 | 2 | 6 | 2.4 | 0.331 | 4.37 | 0.271 |
| teastore | 707 | 23 | 5 | 19 | 83 | 30.7 | 0.448 | 4.04 | 0.352 |
| teammates | 8097 | 92 | 1 | 59 | 808 | 88.0 | 0.645 | 5.41 | 0.203 |
| bigbluebutton | 1529 | 45 | 3 | 16 | 114 | 34.0 | 0.472 | 4.91 | 0.213 |
| jabref | 8268 | 10 | 8 | 478 | 1929 | 826.8 | 0.527 | 2.54 | 0.700 |

#### Code Files Side

| Project | Unique | Min | Median | Max | Mean | Gini | Entropy | Top-3 Conc. |
|---------|--------|-----|--------|-----|------|------|---------|-------------|
| mediastore | 15 | 1 | 3 | 7 | 3.9 | 0.310 | 3.68 | 0.356 |
| teastore | 145 | 2 | 5 | 6 | 4.9 | 0.125 | 7.13 | 0.025 |
| teammates | 828 | 2 | 10 | 19 | 9.8 | 0.185 | 9.60 | 0.007 |
| bigbluebutton | 252 | 2 | 5 | 20 | 6.1 | 0.346 | 7.66 | 0.039 |
| jabref | 1955 | 2 | 4 | 6 | 4.2 | 0.059 | 10.91 | 0.002 |

## 9. Synthesis & Key Findings

### 9.1 Long-Tail Severity

The benchmark exhibits long-tail distributions across all tasks and projects:

| Distribution | Avg Gini | Min Gini | Max Gini | Interpretation |
|-------------|----------|----------|----------|----------------|
| SAD-SAM: Model Element fan-out | 0.268 | 0.179 | 0.370 | Moderate |
| SAD-SAM: Sentence fan-out | 0.171 | 0.110 | 0.256 | Relatively uniform |
| SAM-CODE: Arch Element fan-out | 0.534 | 0.400 | 0.694 | Highly unequal |
| SAM-CODE: Code File fan-out | 0.050 | 0.000 | 0.171 | Relatively uniform |
| SAD-CODE: Sentence fan-out | 0.484 | 0.331 | 0.645 | Highly unequal |
| SAD-CODE: Code File fan-out | 0.205 | 0.059 | 0.346 | Moderate |

### 9.2 Position Bias Summary

- 0/5 projects show statistically significant position bias (Chi-sq > 7.81, df=3)

### 9.3 Cross-Task Coherence

- Average Pearson correlation (SAD-SAM vs SAD-CODE per sentence): **0.743**
- Average Spearman correlation: **0.832**
- The high correlation confirms that SAD-SAM and SAD-CODE capture the same underlying signal.

### 9.4 Enrollment Amplification

- **teastore**: 10.1x enrollment expansion (70→707 links, 43 directory entries)
- **teammates**: 35.5x enrollment expansion (228→8097 links, 151 directory entries)
- **bigbluebutton**: 11.6x enrollment expansion (132→1529 links, 116 directory entries)
- **jabref**: 217.6x enrollment expansion (38→8268 links, 38 directory entries)

Highest expansion: **jabref** at 217.6x

### 9.5 Project-Level Heterogeneity

- **Total Sentences**: CV=0.869 (high heterogeneity)
- **Code Files**: CV=0.926 (high heterogeneity)
- **SAM-CODE Links**: CV=0.842 (high heterogeneity)
- **SAD-CODE Links**: CV=0.982 (high heterogeneity)
- **SAD-CODE Links/Sent**: CV=1.734 (high heterogeneity)
- **SAM-CODE Links/AE**: CV=1.246 (high heterogeneity)

### 9.6 Exploitability Verdict

- **mediastore**: Top-5 baseline (0.270) far below TransArc (0.588) — low exploitability
- **teastore**: Top-5 baseline (0.065) far below TransArc (0.829) — low exploitability
- **teammates**: Top-5 baseline (0.021) far below TransArc (0.821) — low exploitability
- **bigbluebutton**: Top-5 baseline (0.102) far below TransArc (0.831) — low exploitability
- **jabref**: Top-5 baseline (0.007) far below TransArc (0.943) — low exploitability

### 9.7 Implications for Research

1. **Evaluation fairness**: The high Gini coefficients mean a system that correctly handles
   the top-3 most popular entities can achieve disproportionately high scores.
2. **Enrollment bias**: Directory expansion can inflate link counts by 2-10x,
   making file-level metrics favor projects with broad directory entries.
3. **Position bias**: If present, a simple heuristic (link early sentences to everything)
   could inflate scores without semantic understanding.
4. **Cross-project comparison**: The high coefficient of variation in link densities
   means averaging across projects may be misleading — per-project analysis is essential.
5. **Popularity baselines should be reported**: Any new TLR approach should compare against
   a Top-K popularity baseline to demonstrate it captures semantics beyond distributional bias.

