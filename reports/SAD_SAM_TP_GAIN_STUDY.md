# SAD-SAM TP Gain → SAD-CODE Impact Study

For each missed SAD-SAM gold link (a SAD-SAM FN), we ask: if TransArc had found
this link, how many **new SAD-CODE true positives** would it unlock?

The mechanism: a recovered SAD-SAM link (M, S) composes with the actual
intermediate SAM-CODE links for M to produce transitive links (S, C).
We check each (S, C) against the enrolled SAD-CODE gold standard.

## Overview

| Project | SAD-SAM FNs | Total Potential New SAD-CODE TPs | Max Single-Link Gain | Avg Gain/FN |
|---------|-------------|--------------------------------|---------------------|-------------|
| mediastore | 14 | 27 | 3 | 1.9 |
| teastore | 7 | 206 | 64 | 29.4 |
| teammates | 8 | 246 | 71 | 30.8 |
| bigbluebutton | 18 | 195 | 22 | 10.8 |
| jabref | 0 | 0 | 0 | 0.0 |

### Gain vs Current SAD-CODE FNs

| Project | SAD-CODE FNs | Recoverable via SAD-SAM FN Recovery | Coverage |
|---------|-------------|-------------------------------------|----------|
| mediastore | 34 | 27 | 79.4% |
| teastore | 206 | 206 | 100.0% |
| teammates | 790 | 246 | 31.1% |
| bigbluebutton | 242 | 179 | 74.0% |
| jabref | 0 | 0 | 0.0% |

## Per-Project Ranking: SAD-SAM FNs by Potential SAD-CODE TP Gain

### MEDIASTORE

SAD-SAM: 17 TP, 14 FN, 1 FP | SAD-CODE: 25 TP, 34 FN

| Rank | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | Already Found | SAM-CODE Links |
|------|--------------|----------|----------------------|---------|---------|---------------|----------------|
| 1 | Component: DB | 23 | The Database component represents an actual database (e.g., ... | **3** | 0 | 0 | 3 |
| 2 | Component: DB | 33 | By contrast, all audio files are stored in a specific locati... | **3** | 0 | 0 | 3 |
| 3 | Component: DB | 34 | When a user requests files to download, the MediaAccess comp... | **3** | 0 | 0 | 3 |
| 4 | Component: DB | 32 | All salted hashes of passwords are also stored in the Databa... | **3** | 0 | 0 | 3 |
| 5 | Component: DB | 25 | After the user calls the page to list all available audio fi... | **3** | 0 | 0 | 3 |
| 6 | Component: DB | 24 | It stores user information and meta-data of audio files such... | **3** | 0 | 0 | 3 |
| 7 | Component: DB | 31 | The Database component then executes the actual query for fi... | **3** | 0 | 0 | 3 |
| 8 | Component: MediaAccess | 28 | Furthermore, it fetches a list of all available audio files. | **2** | 0 | 0 | 2 |
| 9 | Component: MediaAccess | 25 | After the user calls the page to list all available audio fi... | **2** | 0 | 0 | 2 |
| 10 | Component: MediaManagement | 9 | Furthermore, it fetches audio files from a specific location... | **1** | 0 | 0 | 1 |
| 11 | Component: Reencoding | 20 | The ReEncoder component converts the bit rates of audio file... | **1** | 0 | 0 | 1 |
| 12 | _qxAiILg7EeSNPorBlo7x9g | 33 | By contrast, all audio files are stored in a specific locati... | **0** | 0 | 0 | 0 |
| 13 | _qxAiILg7EeSNPorBlo7x9g | 36 | When a user uploads a file, it will be stored in the DataSto... | **0** | 0 | 0 | 0 |
| 14 | _qxAiILg7EeSNPorBlo7x9g | 35 | Afterwards, based on the user request and the corresponding ... | **0** | 0 | 0 | 0 |

**Summary**: 14 SAD-SAM FNs → 27 potential new SAD-CODE TPs, 0 new FPs | 3 FNs with zero TP gain

### TEASTORE

SAD-SAM: 20 TP, 7 FN, 0 FP | SAD-CODE: 501 TP, 206 FN

| Rank | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | Already Found | SAM-CODE Links |
|------|--------------|----------|----------------------|---------|---------|---------------|----------------|
| 1 | Component: ImageProvider | 11 | It matches the provided product ID or UI name (the filename ... | **64** | 0 | 0 | 64 |
| 2 | Component: Persistence | 23 | It maps the relational entities to the JSON entity objects p... | **30** | 0 | 0 | 30 |
| 3 | Component: Persistence | 26 | As such, it also acts as a caching layer. | **30** | 0 | 0 | 30 |
| 4 | Component: Persistence | 24 | It features endpoints for general CRUD-Operations (Create, R... | **30** | 0 | 0 | 30 |
| 5 | Component: WebUI | 8 | The UI provides a status page at link indicating the current... | **19** | 0 | 0 | 19 |
| 6 | Component: WebUI | 6 | It contains logic to save and retireve values from cookies. | **19** | 0 | 0 | 19 |
| 7 | Component: Recommender | 28 | It is trained using all existing orders. | **14** | 0 | 0 | 14 |

**Summary**: 7 SAD-SAM FNs → 206 potential new SAD-CODE TPs, 0 new FPs | 0 FNs with zero TP gain

### TEAMMATES

SAD-SAM: 49 TP, 8 FN, 32 FP | SAD-CODE: 7307 TP, 790 FN

| Rank | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | Already Found | SAM-CODE Links |
|------|--------------|----------|----------------------|---------|---------|---------------|----------------|
| 1 | Component: Logic | 78 | In particular, it is responsible for the following. | **71** | 0 | 0 | 71 |
| 2 | Component: Storage | 119 | It contains minimal logic beyond what is directly relevant t... | **59** | 0 | 0 | 59 |
| 3 | Component: Storage | 120 | In particular, it is reponsible for the following. | **59** | 0 | 0 | 59 |
| 4 | Component: Client | 19 | It is used for administrative purposes, e.g. migrating data ... | **40** | 0 | 0 | 40 |
| 5 | Component: Test Driver | 168 | This component automates the testing of TEAMMATES. | **17** | 0 | 0 | 17 |
| 6 | _KGVMcKETEeu-mYqkDskRow | 122 | Hiding the complexities of datastore from the Logic componen... | **0** | 0 | 0 | 0 |
| 7 | _KGVMcKETEeu-mYqkDskRow | 141 | Eventual consistency here means it takes some time for a dat... | **0** | 0 | 0 | 0 |
| 8 | _KGVMcKETEeu-mYqkDskRow | 138 | Add and Delete operations try to wait until data is persiste... | **0** | 0 | 0 | 0 |

**Summary**: 8 SAD-SAM FNs → 246 potential new SAD-CODE TPs, 0 new FPs | 3 FNs with zero TP gain

### BIGBLUEBUTTON

SAD-SAM: 44 TP, 18 FN, 5 FP | SAD-CODE: 1287 TP, 242 FN

| Rank | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | Already Found | SAM-CODE Links |
|------|--------------|----------|----------------------|---------|---------|---------------|----------------|
| 1 | Component: BBB web | 38 | It implements the BigBlueButton API and holds a copy of the ... | **22** | 0 | 0 | 22 |
| 2 | Component: BBB web | 37 | BigBlueButton web application is a Java-based application wr... | **22** | 0 | 0 | 22 |
| 3 | Component: HTML5 Server | 21 | As of 2.3-alpha-7, bbb-html5 uses 2 "frontend" and two "back... | **16** | 8 | 0 | 24 |
| 4 | Component: HTML5 Server | 20 | This means that bbb-html5 could use multiple CPU cores for p... | **16** | 8 | 0 | 24 |
| 5 | Component: HTML5 Client | 72 | A user can join the voice conference (running in FreeSWITCH)... | **16** | 5 | 0 | 21 |
| 6 | Component: HTML5 Client | 79 | The conversion process sends progress messages to the client... | **16** | 5 | 0 | 21 |
| 7 | Component: HTML5 Server | 19 | BigBlueButton 2.3 moves away from a single nodejs process fo... | **16** | 8 | 0 | 24 |
| 8 | Component: HTML5 Client | 11 | Each user's client is only aware of the their meeting's stat... | **16** | 5 | 0 | 21 |
| 9 | Component: HTML5 Client | 19 | BigBlueButton 2.3 moves away from a single nodejs process fo... | **16** | 5 | 0 | 21 |
| 10 | Component: HTML5 Client | 76 | Uploaded presentations go through a conversion process in or... | **16** | 5 | 0 | 21 |
| 11 | Component: Apps | 53 | It provides the list of users, chat, whiteboard, presentatio... | **15** | 1 | 0 | 16 |
| 12 | Component: FSESL | 60 | Communication between apps and FreeSWITCH Event Socket Layer... | **8** | 0 | 84 | 92 |
| 13 | _oN4CMFkHEeyewPSmlgszyA | 69 | KMS is responsible for streaming of webcams, listen-only aud... | **0** | 0 | 0 | 0 |
| 14 | Component: HTML5 Client | 73 | When joining through the client, the user can choose to join... | **0** | 5 | 16 | 21 |
| 15 | Component: HTML5 Client | 10 | The MongoDB database contains information about all meetings... | **0** | 5 | 16 | 21 |
| 16 | Component: HTML5 Client | 9 | The HTML5 server is built upon Meteor.js in ECMA2015 for com... | **0** | 5 | 16 | 21 |
| 17 | Component: HTML5 Client | 13 | Updates to MongoDB on the server side are automatically push... | **0** | 5 | 16 | 21 |
| 18 | Component: HTML5 Client | 12 | The client side subscribes to the published collections on t... | **0** | 5 | 16 | 21 |

**Summary**: 18 SAD-SAM FNs → 195 potential new SAD-CODE TPs, 75 new FPs | 6 FNs with zero TP gain

### JABREF

SAD-SAM: 18 TP, 0 FN, 2 FP | SAD-CODE: 8268 TP, 0 FN

No SAD-SAM FNs — all gold links are already recovered.

## Cross-Project Aggregate Ranking (Top 30)

All SAD-SAM FNs across all projects, ranked by potential SAD-CODE TP gain.

| Rank | Project | Model Element | Sentence | Sent Text (truncated) | New TPs | New FPs | TP/FP Ratio |
|------|---------|--------------|----------|----------------------|---------|---------|-------------|
| 1 | teammates | Component: Logic | 78 | In particular, it is responsible for the following. | **71** | 0 | inf |
| 2 | teastore | Component: ImageProvider | 11 | It matches the provided product ID or UI name (the file... | **64** | 0 | inf |
| 3 | teammates | Component: Storage | 119 | It contains minimal logic beyond what is directly relev... | **59** | 0 | inf |
| 4 | teammates | Component: Storage | 120 | In particular, it is reponsible for the following. | **59** | 0 | inf |
| 5 | teammates | Component: Client | 19 | It is used for administrative purposes, e.g. migrating ... | **40** | 0 | inf |
| 6 | teastore | Component: Persistence | 23 | It maps the relational entities to the JSON entity obje... | **30** | 0 | inf |
| 7 | teastore | Component: Persistence | 26 | As such, it also acts as a caching layer. | **30** | 0 | inf |
| 8 | teastore | Component: Persistence | 24 | It features endpoints for general CRUD-Operations (Crea... | **30** | 0 | inf |
| 9 | bigbluebutton | Component: BBB web | 38 | It implements the BigBlueButton API and holds a copy of... | **22** | 0 | inf |
| 10 | bigbluebutton | Component: BBB web | 37 | BigBlueButton web application is a Java-based applicati... | **22** | 0 | inf |
| 11 | teastore | Component: WebUI | 8 | The UI provides a status page at link indicating the cu... | **19** | 0 | inf |
| 12 | teastore | Component: WebUI | 6 | It contains logic to save and retireve values from cook... | **19** | 0 | inf |
| 13 | teammates | Component: Test Driver | 168 | This component automates the testing of TEAMMATES. | **17** | 0 | inf |
| 14 | bigbluebutton | Component: HTML5 Server | 21 | As of 2.3-alpha-7, bbb-html5 uses 2 "frontend" and two ... | **16** | 8 | 2.0 |
| 15 | bigbluebutton | Component: HTML5 Server | 20 | This means that bbb-html5 could use multiple CPU cores ... | **16** | 8 | 2.0 |
| 16 | bigbluebutton | Component: HTML5 Client | 72 | A user can join the voice conference (running in FreeSW... | **16** | 5 | 3.2 |
| 17 | bigbluebutton | Component: HTML5 Client | 79 | The conversion process sends progress messages to the c... | **16** | 5 | 3.2 |
| 18 | bigbluebutton | Component: HTML5 Server | 19 | BigBlueButton 2.3 moves away from a single nodejs proce... | **16** | 8 | 2.0 |
| 19 | bigbluebutton | Component: HTML5 Client | 11 | Each user's client is only aware of the their meeting's... | **16** | 5 | 3.2 |
| 20 | bigbluebutton | Component: HTML5 Client | 19 | BigBlueButton 2.3 moves away from a single nodejs proce... | **16** | 5 | 3.2 |
| 21 | bigbluebutton | Component: HTML5 Client | 76 | Uploaded presentations go through a conversion process ... | **16** | 5 | 3.2 |
| 22 | bigbluebutton | Component: Apps | 53 | It provides the list of users, chat, whiteboard, presen... | **15** | 1 | 15.0 |
| 23 | teastore | Component: Recommender | 28 | It is trained using all existing orders. | **14** | 0 | inf |
| 24 | bigbluebutton | Component: FSESL | 60 | Communication between apps and FreeSWITCH Event Socket ... | **8** | 0 | inf |
| 25 | mediastore | Component: DB | 23 | The Database component represents an actual database (e... | **3** | 0 | inf |
| 26 | mediastore | Component: DB | 33 | By contrast, all audio files are stored in a specific l... | **3** | 0 | inf |
| 27 | mediastore | Component: DB | 34 | When a user requests files to download, the MediaAccess... | **3** | 0 | inf |
| 28 | mediastore | Component: DB | 32 | All salted hashes of passwords are also stored in the D... | **3** | 0 | inf |
| 29 | mediastore | Component: DB | 25 | After the user calls the page to list all available aud... | **3** | 0 | inf |
| 30 | mediastore | Component: DB | 24 | It stores user information and meta-data of audio files... | **3** | 0 | inf |

## Existing SAD-SAM TPs: Current SAD-CODE Contribution

How many SAD-CODE TPs does each existing SAD-SAM TP currently produce?
(If this SAD-SAM TP were lost, these SAD-CODE TPs would become FNs.)

### MEDIASTORE

| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |
|------|--------------|----------|----------------------|-------------|-------------|----------------|
| 1 | Component: UserDBAdapter | 12 | The UserDBAdapter component queries the database. | **2** | 0 | 2 |
| 2 | Component: MediaAccess | 26 | When a user uploads an audio file, the MediaAccess component... | **2** | 0 | 2 |
| 3 | Component: UserManagement | 11 | The UserManagement component answers the requests for regist... | **2** | 0 | 2 |
| 4 | Component: MediaAccess | 27 | The MediaAccess component encapsulates database access for m... | **2** | 0 | 2 |
| 5 | Component: UserDBAdapter | 30 | The UserDBAdapter component creates a query based on the use... | **2** | 0 | 2 |
| 6 | Component: UserDBAdapter | 29 | By contrast, the UserDBAdapter component provides all functi... | **2** | 0 | 2 |
| 7 | Component: UserManagement | 13 | When a user logs into the system, Media Store does not store... | **2** | 0 | 2 |
| 8 | Component: MediaAccess | 34 | When a user requests files to download, the MediaAccess comp... | **2** | 0 | 2 |
| 9 | Component: MediaManagement | 7 | Application business logic is provided by a central business... | **1** | 0 | 1 |
| 10 | Component: Facade | 6 | In addition, users can browse, download, and upload audio fi... | **1** | 0 | 1 |
| 11 | Component: MediaManagement | 8 | The MediaManagement component coordinates the communication ... | **1** | 0 | 1 |
| 12 | Component: MediaManagement | 17 | Afterward, the MediaManagement component forwards these audi... | **1** | 0 | 1 |
| 13 | Component: Facade | 1 | One of the main components of Media Store is a server-side w... | **1** | 0 | 1 |
| 14 | Component: TagWatermarking | 16 | The re-encoded files are then digitally and individually wat... | **1** | 0 | 1 |
| 15 | Component: Facade | 3 | To this end, the Facade component delivers the corresponding... | **1** | 0 | 1 |
| 16 | Component: TagWatermarking | 17 | Afterward, the MediaManagement component forwards these audi... | **1** | 0 | 1 |
| 17 | Component: Packaging | 19 | To allow users to download several files at a time, we provi... | **1** | 0 | 1 |

**Summary**: 17 SAD-SAM TPs produce 25 SAD-CODE TPs and 0 SAD-CODE FPs

### TEASTORE

| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |
|------|--------------|----------|----------------------|-------------|-------------|----------------|
| 1 | Component: ImageProvider | 12 | If the product ID or UI name is not available to the Image P... | **64** | 0 | 64 |
| 2 | Component: ImageProvider | 7 | Images (with few exceptions) are not provides by the WebUi, ... | **64** | 0 | 64 |
| 3 | Component: ImageProvider | 10 | The Image Provider delivers images to the WebUI as base64 en... | **64** | 0 | 64 |
| 4 | Component: ImageProvider | 2 | The WebUI service retrieves images from the Image Provider. | **64** | 0 | 64 |
| 5 | Component: Persistence | 25 | The persistence provider uses a second level entity cache pr... | **30** | 0 | 30 |
| 6 | Component: Persistence | 4 | Data is retrieved from the PersistenceProvider and product r... | **30** | 0 | 30 |
| 7 | Component: Persistence | 22 | The Persistence service provides access to the data persiste... | **30** | 0 | 30 |
| 8 | Component: WebUI | 10 | The Image Provider delivers images to the WebUI as base64 en... | **19** | 0 | 19 |
| 9 | Component: WebUI | 2 | The WebUI service retrieves images from the Image Provider. | **19** | 0 | 19 |
| 10 | Component: WebUI | 5 | The WebUI provides the TeaStore front-end using Servlets in ... | **19** | 0 | 19 |
| 11 | Component: WebUI | 7 | Images (with few exceptions) are not provides by the WebUi, ... | **19** | 0 | 19 |
| 12 | Component: Recommender | 27 | The Recommender is used to generate individual product recom... | **14** | 0 | 14 |
| 13 | Component: Recommender | 4 | Data is retrieved from the PersistenceProvider and product r... | **14** | 0 | 14 |
| 14 | Component: Auth | 18 | The Auth service handles user and session authentication. | **13** | 0 | 13 |
| 15 | Component: Auth | 3 | Users are authenticated by the Auth service. | **13** | 0 | 13 |
| 16 | Component: Registry | 43 | By limiting it to a single registry instance, it enables eas... | **5** | 0 | 5 |
| 17 | Component: Registry | 1 | The TeaStore consists of 5 replicatable services and a singl... | **5** | 0 | 5 |
| 18 | Component: Registry | 37 | The Registry provides information about how many service ins... | **5** | 0 | 5 |
| 19 | Component: Registry | 41 | Every running instance of the TeaStore uses one single regis... | **5** | 0 | 5 |
| 20 | Component: Registry | 38 | Service instances register themselves at the registry on sta... | **5** | 0 | 5 |

**Summary**: 20 SAD-SAM TPs produce 501 SAD-CODE TPs and 0 SAD-CODE FPs

### TEAMMATES

| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |
|------|--------------|----------|----------------------|-------------|-------------|----------------|
| 1 | Component: UI | 7 | In the UI Server the entry point for the application back en... | **348** | 0 | 348 |
| 2 | Component: UI | 4 | The UI Browser seen by users consists of Web pages containin... | **348** | 0 | 348 |
| 3 | Component: UI | 85 | logic.api provides the API of the component to be accessed b... | **348** | 0 | 348 |
| 4 | Component: UI | 29 | The UI component is the first stop for 99% of all requests t... | **348** | 0 | 348 |
| 5 | Component: UI | 81 | Sanitizing input values received from the UI component. | **348** | 0 | 348 |
| 6 | Component: UI | 5 | This UI is a single HTML page generated by Angular framework... | **348** | 0 | 348 |
| 7 | Component: UI | 1 | Architecture contains UI Component, Logic Component, Storage... | **348** | 0 | 348 |
| 8 | Component: UI | 25 | The diagram below shows the object structure of the UI compo... | **348** | 0 | 348 |
| 9 | Component: UI | 97 | The UI is expected to check access control (using GateKeeper... | **348** | 0 | 348 |
| 10 | Component: Common | 174 | x.datatransfer contains component test cases for testing the... | **150** | 0 | 150 |
| 11 | Component: Common | 175 | x.util contains component test cases for testing the utility... | **150** | 0 | 150 |
| 12 | Component: Common | 1 | Architecture contains UI Component, Logic Component, Storage... | **150** | 0 | 150 |
| 13 | Component: Common | 20 | The Common component contains utility code (data transfer ob... | **150** | 0 | 150 |
| 14 | Component: Common | 155 | The Common component contains common utilities used across T... | **150** | 0 | 150 |
| 15 | Component: E2E | 15 | The E2E end-to-end component is used to interact with the ap... | **123** | 0 | 123 |
| 16 | Component: E2E | 16 | Its primary function is for E2E tests. | **123** | 0 | 123 |
| 17 | Component: E2E | 1 | Architecture contains UI Component, Logic Component, Storage... | **123** | 0 | 123 |
| 18 | Component: E2E | 185 | The E2E component has no knowledge of the internal workings ... | **123** | 0 | 123 |
| 19 | Component: E2E | 186 | Its primary function is for E2E tests and L&P (Load & Perfor... | **123** | 0 | 123 |
| 20 | Component: Logic | 87 | Logic API is represented by the classes Logic, GateKeeper, E... | **71** | 0 | 71 |
| 21 | Component: Logic | 88 | Logic is a Facade class which connects to the several Logic ... | **71** | 0 | 71 |
| 22 | Component: Logic | 129 | Cascade logic is handled by the Logic component. | **71** | 0 | 71 |
| 23 | Component: Logic | 1 | Architecture contains UI Component, Logic Component, Storage... | **71** | 0 | 71 |
| 24 | Component: Logic | 185 | The E2E component has no knowledge of the internal workings ... | **71** | 0 | 71 |
| 25 | Component: Logic | 47 | If the action is allowed, it will be performed, interacting ... | **71** | 0 | 71 |
| 26 | Component: Logic | 8 | The main logic of the application is in POJOs (Plain Old Jav... | **71** | 0 | 71 |
| 27 | Component: Logic | 97 | The UI is expected to check access control (using GateKeeper... | **71** | 0 | 71 |
| 28 | Component: Logic | 131 | storage.api provides the API of the component to be accessed... | **71** | 0 | 71 |
| 29 | Component: Logic | 7 | In the UI Server the entry point for the application back en... | **71** | 0 | 71 |
| 30 | Component: Logic | 68 | Seventh, the corresponding AutomatedAction will be performed... | **71** | 0 | 71 |
| 31 | Component: Logic | 77 | The Logic component handles the business logic of TEAMMATES. | **71** | 0 | 71 |
| 32 | Component: Logic | 122 | Hiding the complexities of datastore from the Logic componen... | **71** | 0 | 71 |
| 33 | Component: Logic | 176 | x.logic contains component test cases for testing the Logic ... | **71** | 0 | 71 |
| 34 | Component: Storage | 128 | The Storage component does not perform any cascade delete/cr... | **59** | 0 | 59 |
| 35 | Component: Storage | 177 | x.storage contains component test cases for testing the Stor... | **59** | 0 | 59 |
| 36 | Component: Storage | 123 | All GQL queries are to be contained inside the Storage compo... | **59** | 0 | 59 |
| 37 | Component: Storage | 88 | Logic is a Facade class which connects to the several Logic ... | **59** | 0 | 59 |
| 38 | Component: Storage | 9 | The storage layer of the application uses the persistence fr... | **59** | 0 | 59 |
| 39 | Component: Storage | 1 | Architecture contains UI Component, Logic Component, Storage... | **59** | 0 | 59 |
| 40 | Component: Storage | 101 | Entity already exists throws EntityAlreadyExistsException (e... | **59** | 0 | 59 |
| 41 | Component: Storage | 118 | The Storage component performs CRUD (Create, Read, Update, D... | **59** | 0 | 59 |
| 42 | Component: Client | 18 | The Client component can connect to the back end directly wi... | **40** | 0 | 40 |
| 43 | Component: Client | 1 | Architecture contains UI Component, Logic Component, Storage... | **40** | 0 | 40 |
| 44 | Component: Client | 194 | The Client component contains scripts that can connect direc... | **40** | 0 | 40 |
| 45 | Component: Test Driver | 10 | The following explains the use of the Test Driver. | **17** | 0 | 17 |
| 46 | Component: Test Driver | 1 | Architecture contains UI Component, Logic Component, Storage... | **17** | 0 | 17 |
| 47 | Component: Test Driver | 163 | Test Driver can use the DataBundle in this manner to send an... | **17** | 0 | 17 |
| 48 | _KGVMcKETEeu-mYqkDskRow | 9 | The storage layer of the application uses the persistence fr... | **0** | 0 | 0 |
| 49 | _KGVMcKETEeu-mYqkDskRow | 137 | These classes act as the bridge to the GAE Datastore. | **0** | 0 | 0 |

**Summary**: 49 SAD-SAM TPs produce 6134 SAD-CODE TPs and 0 SAD-CODE FPs

### BIGBLUEBUTTON

| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |
|------|--------------|----------|----------------------|-------------|-------------|----------------|
| 1 | Component: FreeSWITCH | 61 | FreeSWITCH. | **94** | 1 | 95 |
| 2 | Component: FreeSWITCH | 58 | We have extracted out the component that integrates with Fre... | **94** | 1 | 95 |
| 3 | Component: FreeSWITCH | 63 | FreeSWITCH provides the voice conferencing capability in Big... | **94** | 1 | 95 |
| 4 | Component: FreeSWITCH | 72 | A user can join the voice conference (running in FreeSWITCH)... | **94** | 1 | 95 |
| 5 | Component: FreeSWITCH | 66 | FreeSWITCH can also be integrated with VOIP providers so tha... | **94** | 1 | 95 |
| 6 | Component: FreeSWITCH | 62 | We think FreeSWITCH is an amazing piece of software for hand... | **94** | 1 | 95 |
| 7 | Component: FSESL | 57 | FSESL akka. | **92** | 0 | 92 |
| 8 | Component: Presentation Conversion | 81 | The diagram below describes the flow of the presentation con... | **70** | 3 | 73 |
| 9 | Component: Presentation Conversion | 80 | Presentation conversion flow. | **70** | 3 | 73 |
| 10 | Component: BBB web | 30 | If more than one backend is running, bbb-web splits the load... | **22** | 0 | 22 |
| 11 | Component: BBB web | 78 | The PDF document is then converted into scalable vector grap... | **22** | 0 | 22 |
| 12 | Component: BBB web | 36 | BBB web. | **22** | 0 | 22 |
| 13 | Component: HTML5 Server | 47 | Redis PubSub provides a communication channel between differ... | **16** | 8 | 24 |
| 14 | Component: HTML5 Client | 14 | The following diagram gives an overview of the architecture ... | **16** | 5 | 21 |
| 15 | Component: HTML5 Server | 8 | The HTML5 server sits behind nginx. | **16** | 8 | 24 |
| 16 | Component: HTML5 Server | 15 | Scalability of HTML5 server component. | **16** | 8 | 24 |
| 17 | Component: HTML5 Client | 5 | The HTML5 client is a single page, responsive web applicatio... | **16** | 5 | 21 |
| 18 | Component: HTML5 Client | 4 | HTML5 client. | **16** | 5 | 21 |
| 19 | Component: HTML5 Client | 6 | The HTML5 client connects directly with the BigBlueButton se... | **16** | 5 | 21 |
| 20 | Component: HTML5 Server | 6 | The HTML5 client connects directly with the BigBlueButton se... | **16** | 8 | 24 |
| 21 | Component: HTML5 Server | 13 | Updates to MongoDB on the server side are automatically push... | **16** | 8 | 24 |
| 22 | Component: HTML5 Server | 73 | When joining through the client, the user can choose to join... | **16** | 8 | 24 |
| 23 | Component: HTML5 Server | 10 | The MongoDB database contains information about all meetings... | **16** | 8 | 24 |
| 24 | Component: HTML5 Server | 39 | The BigBlueButton API provides a third-party integration (su... | **16** | 8 | 24 |
| 25 | Component: HTML5 Server | 9 | The HTML5 server is built upon Meteor.js in ECMA2015 for com... | **16** | 8 | 24 |
| 26 | Component: HTML5 Server | 12 | The client side subscribes to the published collections on t... | **16** | 8 | 24 |
| 27 | Component: Apps | 51 | Apps akka. | **15** | 1 | 16 |
| 28 | Component: Apps | 54 | Below is a diagram of the different components of Apps Akka. | **15** | 1 | 16 |
| 29 | Component: Apps | 52 | BigBlueButton Apps is the main application that pulls togeth... | **15** | 1 | 16 |
| 30 | Component: Apps | 60 | Communication between apps and FreeSWITCH Event Socket Layer... | **15** | 1 | 16 |
| 31 | Component: Apps | 26 | Frontends receive other DDP events including method calls to... | **15** | 1 | 16 |
| 32 | Component: Redis PubSub | 60 | Communication between apps and FreeSWITCH Event Socket Layer... | **7** | 0 | 7 |
| 33 | Component: Redis PubSub | 47 | Redis PubSub provides a communication channel between differ... | **7** | 0 | 7 |
| 34 | Component: Redis PubSub | 46 | Redis PubSub. | **7** | 0 | 7 |
| 35 | Component: Redis PubSub | 79 | The conversion process sends progress messages to the client... | **7** | 0 | 7 |
| 36 | Component: WebRTC-SFU | 67 | Kurento and WebRTC-SFU. | **6** | 0 | 6 |
| 37 | Component: WebRTC-SFU | 65 | Users joining through Google Chrome or Mozilla Firefox are a... | **6** | 0 | 6 |
| 38 | Component: WebRTC-SFU | 73 | When joining through the client, the user can choose to join... | **6** | 0 | 6 |
| 39 | Component: WebRTC-SFU | 70 | The WebRTC-SFU acts as the media controller handling negotia... | **6** | 0 | 6 |
| 40 | Component: Redis DB | 48 | Redis DB. | **3** | 0 | 3 |
| 41 | Component: Redis DB | 49 | When a meeting is recorded, all events are stored in Redis D... | **3** | 0 | 3 |
| 42 | _oN4CMFkHEeyewPSmlgszyA | 67 | Kurento and WebRTC-SFU. | **0** | 0 | 0 |
| 43 | Component: FreeSWITCH | 59 | This allows others who are using voice conference systems ot... | **0** | 95 | 95 |
| 44 | _oN4CMFkHEeyewPSmlgszyA | 68 | Kurento Media Server KMS is a media server that implements b... | **0** | 0 | 0 |

**Summary**: 44 SAD-SAM TPs produce 1219 SAD-CODE TPs and 212 SAD-CODE FPs

### JABREF

| Rank | Model Element | Sentence | Sent Text (truncated) | SAD-CODE TPs | SAD-CODE FPs | SAM-CODE Links |
|------|--------------|----------|----------------------|-------------|-------------|----------------|
| 1 | Component: logic | 6 | The logic is responsible for reading/writing/importing/expor... | **972** | 0 | 972 |
| 2 | Component: logic | 1 | We have been successfully transitioning from a spaghetti to ... | **972** | 0 | 972 |
| 3 | Component: logic | 4 | We have JUnit tests to detect violations of the most crucial... | **972** | 0 | 972 |
| 4 | Component: logic | 9 | The model should have no dependencies to other classes of Ja... | **972** | 0 | 972 |
| 5 | Component: gui | 7 | Only the gui knows the user and his preferences and can inte... | **707** | 1 | 708 |
| 6 | Component: gui | 4 | We have JUnit tests to detect violations of the most crucial... | **707** | 1 | 708 |
| 7 | Component: gui | 1 | We have been successfully transitioning from a spaghetti to ... | **707** | 1 | 708 |
| 8 | Component: gui | 6 | The logic is responsible for reading/writing/importing/expor... | **707** | 1 | 708 |
| 9 | Component: model | 5 | The model represents the most important data structures (Bib... | **250** | 0 | 250 |
| 10 | Component: model | 12 | We use an event bus to publish events from the model to the ... | **250** | 0 | 250 |
| 11 | Component: model | 4 | We have JUnit tests to detect violations of the most crucial... | **250** | 0 | 250 |
| 12 | Component: model | 6 | The logic is responsible for reading/writing/importing/expor... | **250** | 0 | 250 |
| 13 | Component: model | 9 | The model should have no dependencies to other classes of Ja... | **250** | 0 | 250 |
| 14 | Component: model | 1 | We have been successfully transitioning from a spaghetti to ... | **250** | 0 | 250 |
| 15 | Component: preferences | 2 | There are additional utility packages for preferences and th... | **18** | 0 | 18 |
| 16 | Component: preferences | 11 | The preferences represents all information customizable by a... | **18** | 0 | 18 |
| 17 | Component: cli | 2 | There are additional utility packages for preferences and th... | **8** | 0 | 8 |
| 18 | Component: cli | 10 | The cli package bundles classes that are responsible for Jab... | **8** | 0 | 8 |

**Summary**: 18 SAD-SAM TPs produce 8268 SAD-CODE TPs and 4 SAD-CODE FPs

## Model Element Impact Analysis

Which model elements have the highest total SAD-CODE impact (TPs gained + TPs lost)?

### MEDIASTORE

| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |
|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|
| Component: DB | 0 | 0 | 7 | 21 | 0 | 21 |
| Component: MediaAccess | 3 | 6 | 2 | 4 | 0 | 10 |
| Component: UserDBAdapter | 3 | 6 | 0 | 0 | 0 | 6 |
| Component: MediaManagement | 3 | 3 | 1 | 1 | 0 | 4 |
| Component: UserManagement | 2 | 4 | 0 | 0 | 0 | 4 |
| Component: Facade | 3 | 3 | 0 | 0 | 0 | 3 |
| Component: TagWatermarking | 2 | 2 | 0 | 0 | 0 | 2 |
| Component: Reencoding | 0 | 0 | 1 | 1 | 0 | 1 |
| Component: Packaging | 1 | 1 | 0 | 0 | 0 | 1 |
| _qxAiILg7EeSNPorBlo7x9g | 0 | 0 | 3 | 0 | 0 | 0 |

### TEASTORE

| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |
|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|
| Component: ImageProvider | 4 | 256 | 1 | 64 | 0 | 320 |
| Component: Persistence | 3 | 90 | 3 | 90 | 0 | 180 |
| Component: WebUI | 4 | 76 | 2 | 38 | 0 | 114 |
| Component: Recommender | 2 | 28 | 1 | 14 | 0 | 42 |
| Component: Auth | 2 | 26 | 0 | 0 | 0 | 26 |
| Component: Registry | 5 | 25 | 0 | 0 | 0 | 25 |

### TEAMMATES

| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |
|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|
| Component: UI | 9 | 3132 | 0 | 0 | 0 | 3132 |
| Component: Logic | 14 | 994 | 1 | 71 | 0 | 1065 |
| Component: Common | 5 | 750 | 0 | 0 | 0 | 750 |
| Component: E2E | 5 | 615 | 0 | 0 | 0 | 615 |
| Component: Storage | 8 | 472 | 2 | 118 | 0 | 590 |
| Component: Client | 3 | 120 | 1 | 40 | 0 | 160 |
| Component: Test Driver | 3 | 51 | 1 | 17 | 0 | 68 |
| _KGVMcKETEeu-mYqkDskRow | 2 | 0 | 3 | 0 | 0 | 0 |

### BIGBLUEBUTTON

| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |
|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|
| Component: FreeSWITCH | 7 | 564 | 0 | 0 | 0 | 564 |
| Component: HTML5 Server | 10 | 160 | 3 | 48 | 24 | 208 |
| Component: HTML5 Client | 4 | 64 | 10 | 80 | 50 | 144 |
| Component: Presentation Conversion | 2 | 140 | 0 | 0 | 0 | 140 |
| Component: BBB web | 3 | 66 | 2 | 44 | 0 | 110 |
| Component: FSESL | 1 | 92 | 1 | 8 | 0 | 100 |
| Component: Apps | 5 | 75 | 1 | 15 | 1 | 90 |
| Component: Redis PubSub | 4 | 28 | 0 | 0 | 0 | 28 |
| Component: WebRTC-SFU | 4 | 24 | 0 | 0 | 0 | 24 |
| Component: Redis DB | 2 | 6 | 0 | 0 | 0 | 6 |
| _oN4CMFkHEeyewPSmlgszyA | 2 | 0 | 1 | 0 | 0 | 0 |

### JABREF

| Model Element | SAD-SAM TPs | TP→SAD-CODE TPs | SAD-SAM FNs | FN→Potential TPs | FN→New FPs | Total Impact |
|--------------|-------------|-----------------|-------------|-----------------|------------|-------------|
| Component: logic | 4 | 3888 | 0 | 0 | 0 | 3888 |
| Component: gui | 4 | 2828 | 0 | 0 | 0 | 2828 |
| Component: model | 6 | 1500 | 0 | 0 | 0 | 1500 |
| Component: preferences | 2 | 36 | 0 | 0 | 0 | 36 |
| Component: cli | 2 | 16 | 0 | 0 | 0 | 16 |

## Cumulative Recovery Curve

If we recover SAD-SAM FNs in order of highest TP gain, how does SAD-CODE recall improve?

### MEDIASTORE

Current SAD-CODE: TP=25, FN=34, Gold=59

| SAD-SAM FNs Recovered | Cumul. New TPs | New Recall | Recall Delta |
|----------------------|----------------|-----------|--------------|
| 1/14 | 3 | 0.475 | +0.051 |
| 2/14 | 6 | 0.525 | +0.102 |
| 3/14 | 9 | 0.576 | +0.153 |
| 4/14 | 12 | 0.627 | +0.203 |
| 5/14 | 15 | 0.678 | +0.254 |
| 7/14 | 21 | 0.780 | +0.356 |
| 10/14 | 26 | 0.864 | +0.441 |
| 14/14 | 27 | 0.881 | +0.458 |

### TEASTORE

Current SAD-CODE: TP=501, FN=206, Gold=707

| SAD-SAM FNs Recovered | Cumul. New TPs | New Recall | Recall Delta |
|----------------------|----------------|-----------|--------------|
| 1/7 | 64 | 0.799 | +0.091 |
| 2/7 | 94 | 0.842 | +0.133 |
| 3/7 | 124 | 0.884 | +0.175 |
| 4/7 | 154 | 0.926 | +0.218 |
| 5/7 | 173 | 0.953 | +0.245 |
| 7/7 | 206 | 1.000 | +0.291 |

### TEAMMATES

Current SAD-CODE: TP=7307, FN=790, Gold=8097

| SAD-SAM FNs Recovered | Cumul. New TPs | New Recall | Recall Delta |
|----------------------|----------------|-----------|--------------|
| 1/8 | 71 | 0.911 | +0.009 |
| 2/8 | 130 | 0.918 | +0.016 |
| 3/8 | 189 | 0.926 | +0.023 |
| 4/8 | 229 | 0.931 | +0.028 |
| 5/8 | 246 | 0.933 | +0.030 |
| 6/8 | 246 | 0.933 | +0.030 |
| 8/8 | 246 | 0.933 | +0.030 |

### BIGBLUEBUTTON

Current SAD-CODE: TP=1287, FN=242, Gold=1529

| SAD-SAM FNs Recovered | Cumul. New TPs | New Recall | Recall Delta |
|----------------------|----------------|-----------|--------------|
| 1/18 | 22 | 0.856 | +0.014 |
| 2/18 | 44 | 0.871 | +0.029 |
| 3/18 | 60 | 0.881 | +0.039 |
| 4/18 | 76 | 0.891 | +0.050 |
| 5/18 | 92 | 0.902 | +0.060 |
| 9/18 | 140 | 0.933 | +0.092 |
| 10/18 | 156 | 0.944 | +0.102 |
| 13/18 | 179 | 0.959 | +0.117 |
| 18/18 | 179 | 0.959 | +0.117 |

