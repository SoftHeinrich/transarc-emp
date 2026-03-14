# SAM-CODE Distribution-Level Analysis

Analysis of SAM-CODE link recovery results vs gold standard at the distribution level,
beyond aggregate precision/recall/F1 metrics.

## 1. Gold Standard Enrollment Impact

The SAM-CODE gold standard contains both directory-level and file-level entries.
Directory entries are expanded (enrolled) to individual files using the `.acm` code model.

| Project | Raw Entries | Directories | Files | Enrolled Entries | Expansion Factor |
|---------|-----------|------------|-------|-----------------|-----------------|
| mediastore | 55 | 3 (5%) | 52 (95%) | 60 | 1.1x |
| teastore | 37 | 10 (27%) | 27 (73%) | 164 | 4.4x |
| teammates | 22 | 22 (100%) | 0 (0%) | 1616 | 73.5x |
| bigbluebutton | 64 | 42 (66%) | 22 (34%) | 730 | 11.4x |
| jabref | 11 | 10 (91%) | 1 (9%) | 1956 | 177.8x |

### Per-Model-Element Enrollment Detail

#### mediastore

| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |
|--------------|-----------|------|-------|---------|--------|
| Component: AudioWatermarking | 1 | 1 | 0 | 3 | 3.0x |
| Component: Cache | 1 | 1 | 0 | 3 | 3.0x |
| Component: UserManagement | 1 | 1 | 0 | 2 | 2.0x |
| Component: DB | 4 | 0 | 4 | 4 | 1.0x |
| Component: Facade | 1 | 0 | 1 | 1 | 1.0x |
| Component: MediaAccess | 2 | 0 | 2 | 2 | 1.0x |
| Component: MediaManagement | 1 | 0 | 1 | 1 | 1.0x |
| Component: Packaging | 1 | 0 | 1 | 1 | 1.0x |
| Component: Reencoding | 1 | 0 | 1 | 1 | 1.0x |
| Component: TagWatermarking | 1 | 0 | 1 | 1 | 1.0x |
| Component: UserDBAdapter | 2 | 0 | 2 | 2 | 1.0x |
| Interface: IDB | 2 | 0 | 2 | 2 | 1.0x |
| Interface: IDownload | 16 | 0 | 16 | 16 | 1.0x |
| Interface: IFacade | 3 | 0 | 3 | 3 | 1.0x |
| Interface: IMediaAccess | 6 | 0 | 6 | 6 | 1.0x |
| Interface: IMediaManagement | 3 | 0 | 3 | 3 | 1.0x |
| Interface: IPackaging | 3 | 0 | 3 | 3 | 1.0x |
| Interface: IUserDB | 3 | 0 | 3 | 3 | 1.0x |
| Interface: IUserManagement | 3 | 0 | 3 | 3 | 1.0x |

#### teastore

| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |
|--------------|-----------|------|-------|---------|--------|
| Component: ImageProvider | 2 | 2 | 0 | 64 | 32.0x |
| Component: Persistence | 2 | 2 | 0 | 30 | 15.0x |
| Component: WebUI | 2 | 1 | 1 | 19 | 9.5x |
| Component: Auth | 2 | 2 | 0 | 13 | 6.5x |
| Component: Registry | 1 | 1 | 0 | 5 | 5.0x |
| Component: Recommender | 9 | 2 | 7 | 14 | 1.6x |
| Component: DummyRecommender | 2 | 0 | 2 | 2 | 1.0x |
| Component: OrderBasedRecommender | 2 | 0 | 2 | 2 | 1.0x |
| Component: PopularityBasedRecommender | 2 | 0 | 2 | 2 | 1.0x |
| Component: PreprocessedSlopeOneRecommender | 2 | 0 | 2 | 2 | 1.0x |
| Component: SlopeOneRecommender | 2 | 0 | 2 | 2 | 1.0x |
| Interface: AuthCart | 2 | 0 | 2 | 2 | 1.0x |
| Interface: CartActions | 1 | 0 | 1 | 1 | 1.0x |
| Interface: ImageProvider | 1 | 0 | 1 | 1 | 1.0x |
| Interface: LoadBalancer | 1 | 0 | 1 | 1 | 1.0x |
| Interface: Persistence | 1 | 0 | 1 | 1 | 1.0x |
| Interface: ProductActions | 1 | 0 | 1 | 1 | 1.0x |
| Interface: Recommender | 1 | 0 | 1 | 1 | 1.0x |
| Interface: RecommenderStrategy | 1 | 0 | 1 | 1 | 1.0x |

#### teammates

| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |
|--------------|-----------|------|-------|---------|--------|
| Component: UI | 2 | 2 | 0 | 348 | 174.0x |
| Interface: UI | 2 | 2 | 0 | 348 | 174.0x |
| Component: E2E | 1 | 1 | 0 | 123 | 123.0x |
| Interface: E2E | 1 | 1 | 0 | 123 | 123.0x |
| Component: Common | 2 | 2 | 0 | 150 | 75.0x |
| Interface: Common | 2 | 2 | 0 | 150 | 75.0x |
| Component: Client | 1 | 1 | 0 | 40 | 40.0x |
| Interface: Client | 1 | 1 | 0 | 40 | 40.0x |
| Component: Logic | 2 | 2 | 0 | 71 | 35.5x |
| Interface: Logic | 2 | 2 | 0 | 71 | 35.5x |
| Component: Storage | 2 | 2 | 0 | 59 | 29.5x |
| Interface: Storage | 2 | 2 | 0 | 59 | 29.5x |
| Component: Test Driver | 1 | 1 | 0 | 17 | 17.0x |
| Interface: Test Driver | 1 | 1 | 0 | 17 | 17.0x |

#### bigbluebutton

| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |
|--------------|-----------|------|-------|---------|--------|
| Component: Presentation Conversion | 1 | 1 | 0 | 70 | 70.0x |
| Interface: Presentation Conversion | 1 | 1 | 0 | 70 | 70.0x |
| Component: FSESL | 3 | 3 | 0 | 92 | 30.7x |
| Interface: FSESL | 3 | 3 | 0 | 92 | 30.7x |
| Component: FreeSWITCH | 6 | 5 | 1 | 94 | 15.7x |
| Interface: FreeSWITCH | 6 | 5 | 1 | 94 | 15.7x |
| Component: BBB web | 3 | 3 | 0 | 33 | 11.0x |
| Interface: BBB web | 3 | 3 | 0 | 33 | 11.0x |
| Component: HTML5 Client | 2 | 2 | 0 | 16 | 8.0x |
| Component: HTML5 Server | 2 | 2 | 0 | 16 | 8.0x |
| Interface: HTML5 Client | 2 | 2 | 0 | 16 | 8.0x |
| Interface: HTML5 Server | 2 | 2 | 0 | 16 | 8.0x |
| Component: Apps | 2 | 2 | 0 | 15 | 7.5x |
| Interface: Apps | 2 | 2 | 0 | 15 | 7.5x |
| Component: Redis PubSub | 1 | 1 | 0 | 7 | 7.0x |
| Interface: Redis PubSub | 1 | 1 | 0 | 7 | 7.0x |
| Component: WebRTC-SFU | 2 | 1 | 1 | 6 | 3.0x |
| Interface: WebRTC-SFU | 2 | 1 | 1 | 6 | 3.0x |
| Component: Recording Service | 7 | 1 | 6 | 13 | 1.9x |
| Interface: Recording Service | 7 | 1 | 6 | 13 | 1.9x |
| Component: Redis DB | 3 | 0 | 3 | 3 | 1.0x |
| Interface: Redis DB | 3 | 0 | 3 | 3 | 1.0x |

#### jabref

| Model Element | Raw Entries | Dirs | Files | Enrolled | Factor |
|--------------|-----------|------|-------|---------|--------|
| Component: gui | 2 | 2 | 0 | 707 | 353.5x |
| Component: logic | 3 | 3 | 0 | 972 | 324.0x |
| Component: model | 2 | 2 | 0 | 250 | 125.0x |
| Component: preferences | 1 | 1 | 0 | 18 | 18.0x |
| Component: cli | 2 | 2 | 0 | 8 | 4.0x |
| Component: globals | 1 | 0 | 1 | 1 | 1.0x |

## 2. Per-Model-Element Standalone SAM-CODE Performance

TP/FP/FN breakdown for each architecture element in standalone SAM-CODE recovery.

### mediastore

| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |
|--------------|------|--------|----|----|-----|-----------|--------|
| Interface: IDownload | 16 | 16 | 16 | 0 | 0 | 1.000 | 1.000 |
| Interface: IMediaAccess | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 |
| Component: DB | 4 | 3 | 3 | 0 | 1 | 1.000 | 0.750 |
| Component: AudioWatermarking | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Component: Cache | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: IFacade | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: IMediaManagement | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: IPackaging | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: IUserDB | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: IUserManagement | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Component: MediaAccess | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: UserDBAdapter | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: UserManagement | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Interface: IDB | 2 | 3 | 2 | 1 | 0 | 0.667 | 1.000 |
| Component: Facade | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Component: MediaManagement | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Component: Packaging | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Component: Reencoding | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Component: TagWatermarking | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| **TOTAL** | **60** | **60** | **59** | **1** | **1** | **0.983** | **0.983** |

### teastore

| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |
|--------------|------|--------|----|----|-----|-----------|--------|
| Component: ImageProvider | 64 | 64 | 64 | 0 | 0 | 1.000 | 1.000 |
| Component: Persistence | 30 | 30 | 30 | 0 | 0 | 1.000 | 1.000 |
| Component: WebUI | 19 | 19 | 19 | 0 | 0 | 1.000 | 1.000 |
| Component: Recommender | 14 | 14 | 14 | 0 | 0 | 1.000 | 1.000 |
| Component: Auth | 13 | 13 | 13 | 0 | 0 | 1.000 | 1.000 |
| Component: Registry | 5 | 5 | 5 | 0 | 0 | 1.000 | 1.000 |
| Component: DummyRecommender | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: OrderBasedRecommender | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: PopularityBasedRecommender | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: PreprocessedSlopeOneRecommender | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Component: SlopeOneRecommender | 2 | 2 | 2 | 0 | 0 | 1.000 | 1.000 |
| Interface: AuthCart | 2 | 1 | 1 | 0 | 1 | 1.000 | 0.500 |
| Interface: CartActions | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Interface: ImageProvider | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Interface: LoadBalancer | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Interface: Persistence | 1 | 4 | 0 | 4 | 1 | 0.000 | 0.000 |
| Interface: ProductActions | 1 | 0 | 0 | 0 | 1 | 0.000 | 0.000 |
| Interface: Recommender | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| Interface: RecommenderStrategy | 1 | 0 | 0 | 0 | 1 | 0.000 | 0.000 |
| **TOTAL** | **164** | **164** | **160** | **4** | **4** | **0.976** | **0.976** |

### teammates

| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |
|--------------|------|--------|----|----|-----|-----------|--------|
| Component: UI | 348 | 348 | 348 | 0 | 0 | 1.000 | 1.000 |
| Interface: UI | 348 | 348 | 348 | 0 | 0 | 1.000 | 1.000 |
| Component: Common | 150 | 150 | 150 | 0 | 0 | 1.000 | 1.000 |
| Interface: Common | 150 | 150 | 150 | 0 | 0 | 1.000 | 1.000 |
| Component: E2E | 123 | 123 | 123 | 0 | 0 | 1.000 | 1.000 |
| Interface: E2E | 123 | 123 | 123 | 0 | 0 | 1.000 | 1.000 |
| Component: Logic | 71 | 71 | 71 | 0 | 0 | 1.000 | 1.000 |
| Interface: Logic | 71 | 71 | 71 | 0 | 0 | 1.000 | 1.000 |
| Component: Storage | 59 | 59 | 59 | 0 | 0 | 1.000 | 1.000 |
| Interface: Storage | 59 | 59 | 59 | 0 | 0 | 1.000 | 1.000 |
| Component: Client | 40 | 40 | 40 | 0 | 0 | 1.000 | 1.000 |
| Interface: Client | 40 | 40 | 40 | 0 | 0 | 1.000 | 1.000 |
| Component: Test Driver | 17 | 17 | 17 | 0 | 0 | 1.000 | 1.000 |
| Interface: Test Driver | 17 | 17 | 17 | 0 | 0 | 1.000 | 1.000 |
| **TOTAL** | **1616** | **1616** | **1616** | **0** | **0** | **1.000** | **1.000** |

### bigbluebutton

| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |
|--------------|------|--------|----|----|-----|-----------|--------|
| Component: FreeSWITCH | 94 | 95 | 94 | 1 | 0 | 0.989 | 1.000 |
| Interface: FreeSWITCH | 94 | 95 | 94 | 1 | 0 | 0.989 | 1.000 |
| Component: FSESL | 92 | 92 | 92 | 0 | 0 | 1.000 | 1.000 |
| Interface: FSESL | 92 | 92 | 92 | 0 | 0 | 1.000 | 1.000 |
| Component: Presentation Conversion | 70 | 73 | 70 | 3 | 0 | 0.959 | 1.000 |
| Interface: Presentation Conversion | 70 | 73 | 70 | 3 | 0 | 0.959 | 1.000 |
| Component: BBB web | 33 | 22 | 22 | 0 | 11 | 1.000 | 0.667 |
| Interface: BBB web | 33 | 22 | 22 | 0 | 11 | 1.000 | 0.667 |
| Component: HTML5 Client | 16 | 21 | 16 | 5 | 0 | 0.762 | 1.000 |
| Component: HTML5 Server | 16 | 24 | 16 | 8 | 0 | 0.667 | 1.000 |
| Interface: HTML5 Client | 16 | 21 | 16 | 5 | 0 | 0.762 | 1.000 |
| Interface: HTML5 Server | 16 | 24 | 16 | 8 | 0 | 0.667 | 1.000 |
| Component: Apps | 15 | 16 | 15 | 1 | 0 | 0.938 | 1.000 |
| Interface: Apps | 15 | 16 | 15 | 1 | 0 | 0.938 | 1.000 |
| Component: Recording Service | 13 | 15 | 10 | 5 | 3 | 0.667 | 0.769 |
| Interface: Recording Service | 13 | 15 | 10 | 5 | 3 | 0.667 | 0.769 |
| Component: Redis PubSub | 7 | 7 | 7 | 0 | 0 | 1.000 | 1.000 |
| Interface: Redis PubSub | 7 | 7 | 7 | 0 | 0 | 1.000 | 1.000 |
| Component: WebRTC-SFU | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 |
| Interface: WebRTC-SFU | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 |
| Component: Redis DB | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| Interface: Redis DB | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 |
| **TOTAL** | **730** | **748** | **702** | **46** | **28** | **0.939** | **0.962** |

### jabref

| Model Element | Gold | Result | TP | FP | FN | Precision | Recall |
|--------------|------|--------|----|----|-----|-----------|--------|
| Component: logic | 972 | 972 | 972 | 0 | 0 | 1.000 | 1.000 |
| Component: gui | 707 | 708 | 707 | 1 | 0 | 0.999 | 1.000 |
| Component: model | 250 | 250 | 250 | 0 | 0 | 1.000 | 1.000 |
| Component: preferences | 18 | 18 | 18 | 0 | 0 | 1.000 | 1.000 |
| Component: cli | 8 | 8 | 8 | 0 | 0 | 1.000 | 1.000 |
| Component: globals | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| **TOTAL** | **1956** | **1957** | **1956** | **1** | **0** | **0.999** | **1.000** |

## 3. Standalone vs TransArc-Internal SAM-CODE per Model Element

TransArc runs SAM-CODE internally on a subset of model elements (only those
found by SAD-SAM). This comparison shows which model elements lose coverage.

### mediastore

| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |
|--------------|------|-----------------|--------|---------------|--------|--------------|
| Interface: IDB | 2 | 2/1 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IDownload | 16 | 16/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IFacade | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IMediaAccess | 6 | 6/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IMediaManagement | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IPackaging | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IUserDB | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: IUserManagement | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Component: AudioWatermarking | 3 | 3/0 | 1.000 | 3/0 | 1.000 | 0.000 |
| Component: Cache | 3 | 3/0 | 1.000 | 3/0 | 1.000 | 0.000 |
| Component: DB | 4 | 3/0 | 0.750 | 3/0 | 0.750 | 0.000 |
| Component: Facade | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: MediaAccess | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: MediaManagement | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: Packaging | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: Reencoding | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: TagWatermarking | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: UserDBAdapter | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: UserManagement | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |

### teastore

| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |
|--------------|------|-----------------|--------|---------------|--------|--------------|
| Interface: CartActions | 1 | 1/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: ImageProvider | 1 | 1/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: LoadBalancer | 1 | 1/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Recommender | 1 | 1/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: AuthCart | 2 | 1/0 | 0.500 | 0/0 | 0.000 | +0.500 |
| Component: Auth | 13 | 13/0 | 1.000 | 13/0 | 1.000 | 0.000 |
| Component: DummyRecommender | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: ImageProvider | 64 | 64/0 | 1.000 | 64/0 | 1.000 | 0.000 |
| Component: OrderBasedRecommender | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: Persistence | 30 | 30/0 | 1.000 | 30/0 | 1.000 | 0.000 |
| Component: PopularityBasedRecommender | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: PreprocessedSlopeOneRecommender | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: Recommender | 14 | 14/0 | 1.000 | 14/0 | 1.000 | 0.000 |
| Component: Registry | 5 | 5/0 | 1.000 | 5/0 | 1.000 | 0.000 |
| Component: SlopeOneRecommender | 2 | 2/0 | 1.000 | 2/0 | 1.000 | 0.000 |
| Component: WebUI | 19 | 19/0 | 1.000 | 19/0 | 1.000 | 0.000 |
| Interface: Persistence | 1 | 0/4 | 0.000 | 0/0 | 0.000 | 0.000 |
| Interface: ProductActions | 1 | 0/0 | 0.000 | 0/0 | 0.000 | 0.000 |
| Interface: RecommenderStrategy | 1 | 0/0 | 0.000 | 0/0 | 0.000 | 0.000 |

### teammates

| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |
|--------------|------|-----------------|--------|---------------|--------|--------------|
| Interface: Client | 40 | 40/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Common | 150 | 150/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: E2E | 123 | 123/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Logic | 71 | 71/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Storage | 59 | 59/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Test Driver | 17 | 17/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: UI | 348 | 348/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Component: Client | 40 | 40/0 | 1.000 | 40/0 | 1.000 | 0.000 |
| Component: Common | 150 | 150/0 | 1.000 | 150/0 | 1.000 | 0.000 |
| Component: E2E | 123 | 123/0 | 1.000 | 123/0 | 1.000 | 0.000 |
| Component: Logic | 71 | 71/0 | 1.000 | 71/0 | 1.000 | 0.000 |
| Component: Storage | 59 | 59/0 | 1.000 | 59/0 | 1.000 | 0.000 |
| Component: Test Driver | 17 | 17/0 | 1.000 | 17/0 | 1.000 | 0.000 |
| Component: UI | 348 | 348/0 | 1.000 | 348/0 | 1.000 | 0.000 |

### bigbluebutton

| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |
|--------------|------|-----------------|--------|---------------|--------|--------------|
| Interface: Apps | 15 | 15/1 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: FSESL | 92 | 92/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: FreeSWITCH | 94 | 94/1 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: HTML5 Client | 16 | 16/5 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: HTML5 Server | 16 | 16/8 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Presentation Conversion | 70 | 70/3 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Redis DB | 3 | 3/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Redis PubSub | 7 | 7/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: WebRTC-SFU | 6 | 6/0 | 1.000 | 0/0 | 0.000 | +1.000 |
| Interface: Recording Service | 13 | 10/5 | 0.769 | 0/0 | 0.000 | +0.769 |
| Interface: BBB web | 33 | 22/0 | 0.667 | 0/0 | 0.000 | +0.667 |
| Component: Apps | 15 | 15/1 | 1.000 | 15/1 | 1.000 | 0.000 |
| Component: BBB web | 33 | 22/0 | 0.667 | 22/0 | 0.667 | 0.000 |
| Component: FSESL | 92 | 92/0 | 1.000 | 92/0 | 1.000 | 0.000 |
| Component: FreeSWITCH | 94 | 94/1 | 1.000 | 94/1 | 1.000 | 0.000 |
| Component: HTML5 Client | 16 | 16/5 | 1.000 | 16/5 | 1.000 | 0.000 |
| Component: HTML5 Server | 16 | 16/8 | 1.000 | 16/8 | 1.000 | 0.000 |
| Component: Presentation Conversion | 70 | 70/3 | 1.000 | 70/3 | 1.000 | 0.000 |
| Component: Recording Service | 13 | 10/5 | 0.769 | 10/5 | 0.769 | 0.000 |
| Component: Redis DB | 3 | 3/0 | 1.000 | 3/0 | 1.000 | 0.000 |
| Component: Redis PubSub | 7 | 7/0 | 1.000 | 7/0 | 1.000 | 0.000 |
| Component: WebRTC-SFU | 6 | 6/0 | 1.000 | 6/0 | 1.000 | 0.000 |

### jabref

| Model Element | Gold | Standalone TP/FP | Recall | Internal TP/FP | Recall | Coverage Loss |
|--------------|------|-----------------|--------|---------------|--------|--------------|
| Component: cli | 8 | 8/0 | 1.000 | 8/0 | 1.000 | 0.000 |
| Component: globals | 1 | 1/0 | 1.000 | 1/0 | 1.000 | 0.000 |
| Component: gui | 707 | 707/1 | 1.000 | 707/1 | 1.000 | 0.000 |
| Component: logic | 972 | 972/0 | 1.000 | 972/0 | 1.000 | 0.000 |
| Component: model | 250 | 250/0 | 1.000 | 250/0 | 1.000 | 0.000 |
| Component: preferences | 18 | 18/0 | 1.000 | 18/0 | 1.000 | 0.000 |

## 4. False Positive Analysis: Which Wrong Files Are Included?

For each project, the specific code files that are incorrectly linked to model elements.

### mediastore (1 FPs)

| Model Element | FP Count | Wrong Files |
|--------------|---------|-------------|
| Interface: IDB | 1 | `exceptions/DbException.java` |

### teastore (4 FPs)

| Model Element | FP Count | Wrong Files |
|--------------|---------|-------------|
| Interface: Persistence | 4 | `domain/PersistenceCategory.java`, `domain/PersistenceOrder.java`, `domain/PersistenceProduct.java`, `domain/PersistenceUser.java` |

### teammates: No SAM-CODE FPs

### bigbluebutton (46 FPs)

| Model Element | FP Count | Wrong Files |
|--------------|---------|-------------|
| Component: HTML5 Server | 8 | `bbb-graphql-server/build_hasura.sh`, `bbb-graphql-server/install-hasura.sh`, `bbb-graphql-server/after-install.sh`, `bbb-graphql-server/after-remove.sh`, `bbb-graphql-server/before-remove.sh` +3 more |
| Interface: HTML5 Server | 8 | `bbb-graphql-server/build_hasura.sh`, `bbb-graphql-server/install-hasura.sh`, `bbb-graphql-server/after-install.sh`, `bbb-graphql-server/after-remove.sh`, `bbb-graphql-server/before-remove.sh` +3 more |
| Component: HTML5 Client | 5 | `bbb-graphql-client-test/deploy.sh`, `client/run-watch.sh`, `client/run.sh`, `client/stress-test.sh`, `bbb-html5-nodejs/build.sh` |
| Interface: Recording Service | 5 | `service/ServiceUtils.java`, `service/SessionService.java`, `service/ValidationService.java`, `service/XmlService.java`, `impl/XmlServiceImpl.java` |
| Component: Recording Service | 5 | `service/ServiceUtils.java`, `service/SessionService.java`, `service/ValidationService.java`, `service/XmlService.java`, `impl/XmlServiceImpl.java` |
| Interface: HTML5 Client | 5 | `bbb-graphql-client-test/deploy.sh`, `client/run-watch.sh`, `client/run.sh`, `client/stress-test.sh`, `bbb-html5-nodejs/build.sh` |
| Interface: Presentation Conversion | 3 | `bbb-playback-presentation/after-install.sh`, `bbb-playback-presentation/build.sh`, `bbb-playback-presentation/opts-jammy.sh` |
| Component: Presentation Conversion | 3 | `bbb-playback-presentation/after-install.sh`, `bbb-playback-presentation/build.sh`, `bbb-playback-presentation/opts-jammy.sh` |
| Interface: Apps | 1 | `messages/BbbAppsIsAliveMessage.java` |
| Component: Apps | 1 | `messages/BbbAppsIsAliveMessage.java` |
| Interface: FreeSWITCH | 1 | `cron.hourly/bbb-resync-freeswitch` |
| Component: FreeSWITCH | 1 | `cron.hourly/bbb-resync-freeswitch` |

### jabref (1 FPs)

| Model Element | FP Count | Wrong Files |
|--------------|---------|-------------|
| Component: gui | 1 | `category/GUITest.java` |

## 5. False Negative Analysis: Which Gold Files Are Missed?

For each project, the specific code files that should be linked but are not recovered.

### mediastore (1 FNs)

| Model Element | FN Count | Missed Files |
|--------------|---------|-------------|
| Component: DB | 1 | `exceptions/UserAlreadyExistsException.java` |

### teastore (4 FNs)

| Model Element | FN Count | Missed Files |
|--------------|---------|-------------|
| Interface: RecommenderStrategy | 1 | `algorithm/IRecommender.java` |
| Interface: AuthCart | 1 | `rest/AuthUserActionsRest.java` |
| Interface: ProductActions | 1 | `servlet/ProductServlet.java` |
| Interface: Persistence | 1 | `repository/AbstractPersistenceRepository.java` |

### teammates: No SAM-CODE FNs

### bigbluebutton (28 FNs)

| Model Element | FN Count | Missed Files |
|--------------|---------|-------------|
| Interface: BBB web | 11 | `bigbluebutton-web/build.sh`, `bigbluebutton-web/deploy_to_usr_share.sh`, `bigbluebutton-web/gradlew`, `bigbluebutton-web/grailsw`, `pres-checker/build.sh` +6 more |
| Component: BBB web | 11 | `bigbluebutton-web/build.sh`, `bigbluebutton-web/deploy_to_usr_share.sh`, `bigbluebutton-web/gradlew`, `bigbluebutton-web/grailsw`, `pres-checker/build.sh` +6 more |
| Interface: Recording Service | 3 | `api/RecordingServiceHelper.java`, `api2/IRecordingService.java`, `api2/RecordingServiceGW.java` |
| Component: Recording Service | 3 | `api/RecordingServiceHelper.java`, `api2/IRecordingService.java`, `api2/RecordingServiceGW.java` |

### jabref: No SAM-CODE FNs

## 6. File Extension Distribution

How do TPs, FPs, and FNs distribute across file types?

### mediastore

| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |
|-----------|------|----|----|-----|---------|---------|
| .java | 60 | 59 | 1 | 1 | 0.017 | 0.017 |

### teastore

| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |
|-----------|------|----|----|-----|---------|---------|
| .java | 163 | 159 | 4 | 4 | 0.025 | 0.025 |
| .sh | 1 | 1 | 0 | 0 | 0.000 | 0.000 |

### teammates

| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |
|-----------|------|----|----|-----|---------|---------|
| .java | 1616 | 1616 | 0 | 0 | 0.000 | 0.000 |

### bigbluebutton

| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |
|-----------|------|----|----|-----|---------|---------|
| .java | 576 | 564 | 12 | 12 | 0.021 | 0.021 |
| .sh | 138 | 126 | 32 | 12 | 0.203 | 0.087 |
| (no ext) | 16 | 12 | 2 | 4 | 0.143 | 0.250 |

### jabref

| Extension | Gold | TP | FP | FN | FP Rate | FN Rate |
|-----------|------|----|----|-----|---------|---------|
| .java | 1956 | 1956 | 1 | 0 | 0.001 | 0.000 |

## 7. Code File Recovery Coverage

How many unique gold code files are fully recovered, partially recovered, or never recovered?

| Project | Gold Files | Fully Recovered | Partially Recovered | Never Recovered | Spurious Files |
|---------|-----------|----------------|--------------------|-----------------|--------------| 
| mediastore | 58 | 57 (98%) | 0 (0%) | 1 (2%) | 0 |
| teastore | 156 | 152 (97%) | 4 (3%) | 0 (0%) | 0 |
| teammates | 808 | 808 (100%) | 0 (0%) | 0 (0%) | 0 |
| bigbluebutton | 265 | 251 (95%) | 0 (0%) | 14 (5%) | 22 |
| jabref | 1955 | 1955 (100%) | 0 (0%) | 0 (0%) | 1 |

### mediastore: Never-Recovered Files (1)

- `basic/exceptions/UserAlreadyExistsException.java`

### bigbluebutton: Never-Recovered Files (14)

- `bigbluebutton/api/RecordingServiceHelper.java`
- `bigbluebutton/api2/IRecordingService.java`
- `bigbluebutton/api2/RecordingServiceGW.java`
- `bigbluebutton-web/build.sh`
- `bigbluebutton-web/deploy_to_usr_share.sh`
- `bigbluebutton-web/gradlew`
- `bigbluebutton-web/grailsw`
- `bigbluebutton-web/pres-checker/build.sh`
- `bigbluebutton-web/pres-checker/run.sh`
- `bigbluebutton/prescheck/Main.java`
- `bigbluebutton-web/run-dev.sh`
- `bigbluebutton-web/run.sh`
- `bigbluebutton/api/ParamsProcessorUtilTest.java`
- `api/messaging/NullMessagingService.java`

## 8. Cross-Project Summary

### Model Element Error Concentration

How concentrated are SAM-CODE errors across model elements?

| Project | Model Elements | With FPs | With FNs | Perfect (TP=Gold) | No Links (in result) |
|---------|---------------|---------|---------|------------------|---------------------|
| mediastore | 19 | 1 | 1 | 17 | 0 |
| teastore | 19 | 1 | 4 | 15 | 2 |
| teammates | 14 | 0 | 0 | 14 | 0 |
| bigbluebutton | 22 | 12 | 4 | 8 | 0 |
| jabref | 6 | 1 | 0 | 5 | 0 |

### Enrollment Amplification vs Error Rate

Do heavily enrolled model elements (many files from few directory entries) have higher error rates?

| Project | Model Element | Raw | Enrolled | Factor | FPs | FNs | Precision | Recall |
|---------|--------------|-----|---------|--------|-----|-----|-----------|--------|
| mediastore | Component: AudioWatermarking | 1 | 3 | 3.0x | 0 | 0 | 1.000 | 1.000 |
| mediastore | Component: Cache | 1 | 3 | 3.0x | 0 | 0 | 1.000 | 1.000 |
| mediastore | Component: UserManagement | 1 | 2 | 2.0x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: ImageProvider | 2 | 64 | 32.0x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: Persistence | 2 | 30 | 15.0x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: WebUI | 2 | 19 | 9.5x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: Auth | 2 | 13 | 6.5x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: Registry | 1 | 5 | 5.0x | 0 | 0 | 1.000 | 1.000 |
| teastore | Component: Recommender | 9 | 14 | 1.6x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: UI | 2 | 348 | 174.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: UI | 2 | 348 | 174.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: E2E | 1 | 123 | 123.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: E2E | 1 | 123 | 123.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: Common | 2 | 150 | 75.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: Common | 2 | 150 | 75.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: Client | 1 | 40 | 40.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: Client | 1 | 40 | 40.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: Logic | 2 | 71 | 35.5x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: Logic | 2 | 71 | 35.5x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: Storage | 2 | 59 | 29.5x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: Storage | 2 | 59 | 29.5x | 0 | 0 | 1.000 | 1.000 |
| teammates | Component: Test Driver | 1 | 17 | 17.0x | 0 | 0 | 1.000 | 1.000 |
| teammates | Interface: Test Driver | 1 | 17 | 17.0x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Component: Presentation Conversion | 1 | 70 | 70.0x | 3 | 0 | 0.959 | 1.000 |
| bigbluebutton | Interface: Presentation Conversion | 1 | 70 | 70.0x | 3 | 0 | 0.959 | 1.000 |
| bigbluebutton | Component: FSESL | 3 | 92 | 30.7x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Interface: FSESL | 3 | 92 | 30.7x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Component: FreeSWITCH | 6 | 94 | 15.7x | 1 | 0 | 0.989 | 1.000 |
| bigbluebutton | Interface: FreeSWITCH | 6 | 94 | 15.7x | 1 | 0 | 0.989 | 1.000 |
| bigbluebutton | Component: BBB web | 3 | 33 | 11.0x | 0 | 11 | 1.000 | 0.667 |
| bigbluebutton | Interface: BBB web | 3 | 33 | 11.0x | 0 | 11 | 1.000 | 0.667 |
| bigbluebutton | Component: HTML5 Client | 2 | 16 | 8.0x | 5 | 0 | 0.762 | 1.000 |
| bigbluebutton | Component: HTML5 Server | 2 | 16 | 8.0x | 8 | 0 | 0.667 | 1.000 |
| bigbluebutton | Interface: HTML5 Client | 2 | 16 | 8.0x | 5 | 0 | 0.762 | 1.000 |
| bigbluebutton | Interface: HTML5 Server | 2 | 16 | 8.0x | 8 | 0 | 0.667 | 1.000 |
| bigbluebutton | Component: Apps | 2 | 15 | 7.5x | 1 | 0 | 0.938 | 1.000 |
| bigbluebutton | Interface: Apps | 2 | 15 | 7.5x | 1 | 0 | 0.938 | 1.000 |
| bigbluebutton | Component: Redis PubSub | 1 | 7 | 7.0x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Interface: Redis PubSub | 1 | 7 | 7.0x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Component: WebRTC-SFU | 2 | 6 | 3.0x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Interface: WebRTC-SFU | 2 | 6 | 3.0x | 0 | 0 | 1.000 | 1.000 |
| bigbluebutton | Component: Recording Service | 7 | 13 | 1.9x | 5 | 3 | 0.667 | 0.769 |
| bigbluebutton | Interface: Recording Service | 7 | 13 | 1.9x | 5 | 3 | 0.667 | 0.769 |
| jabref | Component: gui | 2 | 707 | 353.5x | 1 | 0 | 0.999 | 1.000 |
| jabref | Component: logic | 3 | 972 | 324.0x | 0 | 0 | 1.000 | 1.000 |
| jabref | Component: model | 2 | 250 | 125.0x | 0 | 0 | 1.000 | 1.000 |
| jabref | Component: preferences | 1 | 18 | 18.0x | 0 | 0 | 1.000 | 1.000 |
| jabref | Component: cli | 2 | 8 | 4.0x | 0 | 0 | 1.000 | 1.000 |

