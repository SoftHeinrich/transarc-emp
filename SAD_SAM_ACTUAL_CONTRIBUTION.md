# SAD-SAM Actual Contribution to SAD-CODE Output

Every TransArc output link (S, C) was produced by composing an intermediate
SAD-SAM link (M, S) with an intermediate SAM-CODE link (M, C). This study
traces each **actual** SAD-CODE output link back to its SAD-SAM source and
counts the real TPs and FPs each SAD-SAM link produced.

A single SAD-CODE link may be attributed to multiple SAD-SAM links if
multiple bridging model elements exist. Counts reflect actual attribution.

## Overview

| Project | SAD-SAM TPs | SAD-SAM FPs | SAD-CODE TPs | SAD-CODE FPs | SAD-CODE Total |
|---------|------------|------------|-------------|-------------|---------------|
| mediastore | 17 | 1 | 25 | 1 | 26 |
| teastore | 20 | 0 | 501 | 0 | 501 |
| teammates | 49 | 32 | 7307 | 2395 | 9702 |
| bigbluebutton | 44 | 5 | 1287 | 282 | 1569 |
| jabref | 18 | 2 | 8268 | 994 | 9262 |

## MEDIASTORE

TransArc output: 25 TPs + 1 FPs = 26 total | Gold: 59

### SAD-SAM TPs → Actual SAD-CODE Links Produced (17 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: MediaAccess | 27 | The MediaAccess component encapsulates database access for meta-d... | **2** | 0 | 2 |
| 2 | Component: UserManagement | 13 | When a user logs into the system, Media Store does not store the ... | **2** | 0 | 2 |
| 3 | Component: UserDBAdapter | 12 | The UserDBAdapter component queries the database. | **2** | 0 | 2 |
| 4 | Component: MediaAccess | 26 | When a user uploads an audio file, the MediaAccess component stor... | **2** | 0 | 2 |
| 5 | Component: UserDBAdapter | 29 | By contrast, the UserDBAdapter component provides all functions r... | **2** | 0 | 2 |
| 6 | Component: UserManagement | 11 | The UserManagement component answers the requests for registratio... | **2** | 0 | 2 |
| 7 | Component: MediaAccess | 34 | When a user requests files to download, the MediaAccess component... | **2** | 0 | 2 |
| 8 | Component: UserDBAdapter | 30 | The UserDBAdapter component creates a query based on the user's r... | **2** | 0 | 2 |
| 9 | Component: TagWatermarking | 16 | The re-encoded files are then digitally and individually watermar... | **1** | 0 | 1 |
| 10 | Component: Facade | 1 | One of the main components of Media Store is a server-side web fr... | **1** | 0 | 1 |
| 11 | Component: TagWatermarking | 17 | Afterward, the MediaManagement component forwards these audio fil... | **1** | 0 | 1 |
| 12 | Component: MediaManagement | 7 | Application business logic is provided by a central business logi... | **1** | 0 | 1 |
| 13 | Component: Facade | 3 | To this end, the Facade component delivers the corresponding regi... | **1** | 0 | 1 |
| 14 | Component: MediaManagement | 8 | The MediaManagement component coordinates the communication of ot... | **1** | 0 | 1 |
| 15 | Component: Packaging | 19 | To allow users to download several files at a time, we provide th... | **1** | 0 | 1 |
| 16 | Component: Facade | 6 | In addition, users can browse, download, and upload audio files u... | **1** | 0 | 1 |
| 17 | Component: MediaManagement | 17 | Afterward, the MediaManagement component forwards these audio fil... | **1** | 0 | 1 |
| | **TOTAL** | | | **25** | **0** | **25** |

### SAD-SAM FPs → Actual SAD-CODE Links Produced (1 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: Reencoding | 37 | However, a download can cause re-encoding of the audio file. | 0 | **1** | 1 |
| | **TOTAL** | | | **0** | **1** | **1** |

### Per-Model-Element Summary

| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |
|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|
| Component: MediaAccess | 3 | 6 | 0 | 0 | 0 | 0 | +6 |
| Component: UserDBAdapter | 3 | 6 | 0 | 0 | 0 | 0 | +6 |
| Component: UserManagement | 2 | 4 | 0 | 0 | 0 | 0 | +4 |
| Component: Facade | 3 | 3 | 0 | 0 | 0 | 0 | +3 |
| Component: MediaManagement | 3 | 3 | 0 | 0 | 0 | 0 | +3 |
| Component: TagWatermarking | 2 | 2 | 0 | 0 | 0 | 0 | +2 |
| Component: Packaging | 1 | 1 | 0 | 0 | 0 | 0 | +1 |
| Component: Reencoding | 0 | 0 | 0 | 1 | 0 | 1 | -1 |

## TEASTORE

TransArc output: 501 TPs + 0 FPs = 501 total | Gold: 707

### SAD-SAM TPs → Actual SAD-CODE Links Produced (20 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: ImageProvider | 10 | The Image Provider delivers images to the WebUI as base64 encoded... | **64** | 0 | 64 |
| 2 | Component: ImageProvider | 12 | If the product ID or UI name is not available to the Image Provid... | **64** | 0 | 64 |
| 3 | Component: ImageProvider | 7 | Images (with few exceptions) are not provides by the WebUi, but a... | **64** | 0 | 64 |
| 4 | Component: ImageProvider | 2 | The WebUI service retrieves images from the Image Provider. | **64** | 0 | 64 |
| 5 | Component: Persistence | 22 | The Persistence service provides access to the data persisted in ... | **30** | 0 | 30 |
| 6 | Component: Persistence | 25 | The persistence provider uses a second level entity cache provide... | **30** | 0 | 30 |
| 7 | Component: Persistence | 4 | Data is retrieved from the PersistenceProvider and product recomm... | **30** | 0 | 30 |
| 8 | Component: WebUI | 5 | The WebUI provides the TeaStore front-end using Servlets in combi... | **19** | 0 | 19 |
| 9 | Component: WebUI | 2 | The WebUI service retrieves images from the Image Provider. | **19** | 0 | 19 |
| 10 | Component: WebUI | 10 | The Image Provider delivers images to the WebUI as base64 encoded... | **19** | 0 | 19 |
| 11 | Component: WebUI | 7 | Images (with few exceptions) are not provides by the WebUi, but a... | **19** | 0 | 19 |
| 12 | Component: Recommender | 27 | The Recommender is used to generate individual product recommenda... | **14** | 0 | 14 |
| 13 | Component: Recommender | 4 | Data is retrieved from the PersistenceProvider and product recomm... | **14** | 0 | 14 |
| 14 | Component: Auth | 3 | Users are authenticated by the Auth service. | **13** | 0 | 13 |
| 15 | Component: Auth | 18 | The Auth service handles user and session authentication. | **13** | 0 | 13 |
| 16 | Component: Registry | 41 | Every running instance of the TeaStore uses one single registry. | **5** | 0 | 5 |
| 17 | Component: Registry | 43 | By limiting it to a single registry instance, it enables easy con... | **5** | 0 | 5 |
| 18 | Component: Registry | 38 | Service instances register themselves at the registry on startup. | **5** | 0 | 5 |
| 19 | Component: Registry | 37 | The Registry provides information about how many service instance... | **5** | 0 | 5 |
| 20 | Component: Registry | 1 | The TeaStore consists of 5 replicatable services and a single Reg... | **5** | 0 | 5 |
| | **TOTAL** | | | **501** | **0** | **501** |

### SAD-SAM FPs → No SAD-SAM FPs in this project

### Per-Model-Element Summary

| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |
|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|
| Component: ImageProvider | 4 | 256 | 0 | 0 | 0 | 0 | +256 |
| Component: Persistence | 3 | 90 | 0 | 0 | 0 | 0 | +90 |
| Component: WebUI | 4 | 76 | 0 | 0 | 0 | 0 | +76 |
| Component: Recommender | 2 | 28 | 0 | 0 | 0 | 0 | +28 |
| Component: Auth | 2 | 26 | 0 | 0 | 0 | 0 | +26 |
| Component: Registry | 5 | 25 | 0 | 0 | 0 | 0 | +25 |

## TEAMMATES

TransArc output: 7307 TPs + 2395 FPs = 9702 total | Gold: 8097

### SAD-SAM TPs → Actual SAD-CODE Links Produced (49 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: UI | 4 | The UI Browser seen by users consists of Web pages containing HTM... | **348** | 0 | 348 |
| 2 | Component: UI | 85 | logic.api provides the API of the component to be accessed by the... | **348** | 0 | 348 |
| 3 | Component: UI | 5 | This UI is a single HTML page generated by Angular framework. | **348** | 0 | 348 |
| 4 | Component: UI | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **348** | 0 | 348 |
| 5 | Component: UI | 25 | The diagram below shows the object structure of the UI component. | **348** | 0 | 348 |
| 6 | Component: UI | 7 | In the UI Server the entry point for the application back end log... | **348** | 0 | 348 |
| 7 | Component: UI | 97 | The UI is expected to check access control (using GateKeeper clas... | **348** | 0 | 348 |
| 8 | Component: UI | 81 | Sanitizing input values received from the UI component. | **348** | 0 | 348 |
| 9 | Component: UI | 29 | The UI component is the first stop for 99% of all requests that a... | **348** | 0 | 348 |
| 10 | Component: Common | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **150** | 0 | 150 |
| 11 | Component: Common | 175 | x.util contains component test cases for testing the utility clas... | **150** | 0 | 150 |
| 12 | Component: Common | 174 | x.datatransfer contains component test cases for testing the data... | **150** | 0 | 150 |
| 13 | Component: Common | 20 | The Common component contains utility code (data transfer objects... | **150** | 0 | 150 |
| 14 | Component: Common | 155 | The Common component contains common utilities used across TEAMMA... | **150** | 0 | 150 |
| 15 | Component: E2E | 15 | The E2E end-to-end component is used to interact with the applica... | **123** | 0 | 123 |
| 16 | Component: E2E | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **123** | 0 | 123 |
| 17 | Component: E2E | 185 | The E2E component has no knowledge of the internal workings of th... | **123** | 0 | 123 |
| 18 | Component: E2E | 186 | Its primary function is for E2E tests and L&P (Load & Performance... | **123** | 0 | 123 |
| 19 | Component: E2E | 16 | Its primary function is for E2E tests. | **123** | 0 | 123 |
| 20 | Component: Logic | 8 | The main logic of the application is in POJOs (Plain Old Java Obj... | **71** | 0 | 71 |
| 21 | Component: Logic | 68 | Seventh, the corresponding AutomatedAction will be performed, int... | **71** | 0 | 71 |
| 22 | Component: Logic | 7 | In the UI Server the entry point for the application back end log... | **71** | 0 | 71 |
| 23 | Component: Logic | 47 | If the action is allowed, it will be performed, interacting with ... | **71** | 0 | 71 |
| 24 | Component: Logic | 88 | Logic is a Facade class which connects to the several Logic class... | **71** | 0 | 71 |
| 25 | Component: Logic | 129 | Cascade logic is handled by the Logic component. | **71** | 0 | 71 |
| 26 | Component: Logic | 87 | Logic API is represented by the classes Logic, GateKeeper, EmailG... | **71** | 0 | 71 |
| 27 | Component: Logic | 97 | The UI is expected to check access control (using GateKeeper clas... | **71** | 0 | 71 |
| 28 | Component: Logic | 176 | x.logic contains component test cases for testing the Logic compo... | **71** | 0 | 71 |
| 29 | Component: Logic | 122 | Hiding the complexities of datastore from the Logic component. | **71** | 0 | 71 |
| 30 | Component: Logic | 131 | storage.api provides the API of the component to be accessed by t... | **71** | 0 | 71 |
| 31 | Component: Logic | 77 | The Logic component handles the business logic of TEAMMATES. | **71** | 0 | 71 |
| 32 | Component: Logic | 185 | The E2E component has no knowledge of the internal workings of th... | **71** | 0 | 71 |
| 33 | Component: Logic | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **71** | 0 | 71 |
| 34 | Component: Storage | 128 | The Storage component does not perform any cascade delete/create ... | **59** | 0 | 59 |
| 35 | Component: Storage | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **59** | 0 | 59 |
| 36 | Component: Storage | 88 | Logic is a Facade class which connects to the several Logic class... | **59** | 0 | 59 |
| 37 | Component: Storage | 177 | x.storage contains component test cases for testing the Storage c... | **59** | 0 | 59 |
| 38 | Component: Storage | 101 | Entity already exists throws EntityAlreadyExistsException (escala... | **59** | 0 | 59 |
| 39 | Component: Storage | 9 | The storage layer of the application uses the persistence framewo... | **59** | 0 | 59 |
| 40 | Component: Storage | 123 | All GQL queries are to be contained inside the Storage component. | **59** | 0 | 59 |
| 41 | Component: Storage | 118 | The Storage component performs CRUD (Create, Read, Update, Delete... | **59** | 0 | 59 |
| 42 | Component: Client | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **40** | 0 | 40 |
| 43 | Component: Client | 18 | The Client component can connect to the back end directly without... | **40** | 0 | 40 |
| 44 | Component: Client | 194 | The Client component contains scripts that can connect directly t... | **40** | 0 | 40 |
| 45 | Component: Test Driver | 163 | Test Driver can use the DataBundle in this manner to send an arbi... | **17** | 0 | 17 |
| 46 | Component: Test Driver | 10 | The following explains the use of the Test Driver. | **17** | 0 | 17 |
| 47 | Component: Test Driver | 1 | Architecture contains UI Component, Logic Component, Storage Comp... | **17** | 0 | 17 |
| 48 | _KGVMcKETEeu-mYqkDskRow | 9 | The storage layer of the application uses the persistence framewo... | **0** | 0 | 0 |
| 49 | _KGVMcKETEeu-mYqkDskRow | 137 | These classes act as the bridge to the GAE Datastore. | **0** | 0 | 0 |
| | **TOTAL** | | | **6134** | **0** | **6134** |

### SAD-SAM FPs → Actual SAD-CODE Links Produced (32 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: UI | 23 | ui.website is not a real package. | 0 | **348** | 348 |
| 2 | Component: UI | 26 | ui.website is not a Java package. | 0 | **348** | 348 |
| 3 | Component: UI | 22 | logic, ui.website, ui.controller represent an application of Mode... | 125 | **223** | 348 |
| 4 | Component: Common | 158 | common.exceptions contains custom exceptions. | 11 | **139** | 150 |
| 5 | Component: E2E | 17 | Selenium Java is used to automate E2E testing with actual Web bro... | 0 | **123** | 123 |
| 6 | Component: E2E | 189 | e2e.pageobjects contains abstractions of the pages as they appear... | 0 | **123** | 123 |
| 7 | Component: E2E | 190 | e2e.cases contains test cases. | 0 | **123** | 123 |
| 8 | Component: Common | 157 | common.util contains utility classes. | 32 | **118** | 150 |
| 9 | Component: Logic | 119 | It contains minimal logic beyond what is directly relevant to CRU... | 0 | **71** | 71 |
| 10 | Component: Logic | 117 | Refer to the API for the cascade logic. | 0 | **71** | 71 |
| 11 | Component: Logic | 79 | Managing relationships between entities, e.g. cascade logic for c... | 0 | **71** | 71 |
| 12 | Component: Logic | 85 | logic.api provides the API of the component to be accessed by the... | 21 | **50** | 71 |
| 13 | Component: Storage | 132 | storage.entity contains classes that represent persistable entiti... | 14 | **45** | 59 |
| 14 | Component: Storage | 125 | Classes in the storage.entity package are not visible outside thi... | 14 | **45** | 59 |
| 15 | Component: Common | 159 | common.datatransfer contains data transfer objects. | 107 | **43** | 150 |
| 16 | Component: Common | 160 | common.datatransfer package contains lightweight data transfer ob... | 107 | **43** | 150 |
| 17 | Component: Common | 127 | These datatransfer classes are in common.datatransfer package, to... | 107 | **43** | 150 |
| 18 | Component: Storage | 133 | storage.search contains classes for dealing with searching and in... | 16 | **43** | 59 |
| 19 | Component: Logic | 86 | logic.core contains the core logic of the system. | 30 | **41** | 71 |
| 20 | Component: Client | 198 | client.scripts scripts that deal with the back end data for admin... | 0 | **40** | 40 |
| 21 | Component: Client | 4 | The UI Browser seen by users consists of Web pages containing HTM... | 0 | **40** | 40 |
| 22 | Component: Client | 197 | client.remoteapi classes needed to connect to the back end direct... | 2 | **38** | 40 |
| 23 | Component: Client | 196 | client.util contains helpers needed for client scripts. | 4 | **36** | 40 |
| 24 | Component: Client | 195 | Package overview contains client.util, client.remoteapi, client.s... | 6 | **34** | 40 |
| 25 | Component: Storage | 131 | storage.api provides the API of the component to be accessed by t... | 29 | **30** | 59 |
| 26 | Component: Logic | 22 | logic, ui.website, ui.controller represent an application of Mode... | 42 | **29** | 71 |
| 27 | Component: Logic | 84 | Package overview contains logic.api, logic.core. | 51 | **20** | 71 |
| 28 | Component: Test Driver | 173 | x.testdriver contains component test cases for testing the test d... | 0 | **17** | 17 |
| 29 | Component: Storage | 130 | Package overview contains storage.api, storage.entity, storage.se... | 59 | **0** | 59 |
| 30 | Component: E2E | 187 | Package overview contains e2e.util, e2e.pageobjects, e2e.cases, x... | 123 | **0** | 123 |
| 31 | Component: E2E | 188 | e2e.util contains helpers needed for running E2E tests. | 123 | **0** | 123 |
| 32 | Component: Common | 156 | Package overview contains common.util, common.exceptions, common.... | 150 | **0** | 150 |
| | **TOTAL** | | | **1173** | **2395** | **3568** |

### Per-Model-Element Summary

| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |
|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|
| Component: UI | 9 | 3132 | 0 | 3 | 125 | 919 | +2338 |
| Component: Logic | 14 | 994 | 0 | 7 | 144 | 353 | +785 |
| Component: Common | 5 | 750 | 0 | 6 | 514 | 386 | +878 |
| Component: Storage | 8 | 472 | 0 | 5 | 132 | 163 | +441 |
| Component: E2E | 5 | 615 | 0 | 5 | 246 | 369 | +492 |
| Component: Test Driver | 3 | 51 | 0 | 1 | 0 | 17 | +34 |
| _KGVMcKETEeu-mYqkDskRow | 2 | 0 | 0 | 0 | 0 | 0 | +0 |
| Component: Client | 3 | 120 | 0 | 5 | 12 | 188 | -56 |

## BIGBLUEBUTTON

TransArc output: 1287 TPs + 282 FPs = 1569 total | Gold: 1529

### SAD-SAM TPs → Actual SAD-CODE Links Produced (44 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: FreeSWITCH | 72 | A user can join the voice conference (running in FreeSWITCH) from... | **94** | 1 | 95 |
| 2 | Component: FreeSWITCH | 58 | We have extracted out the component that integrates with FreeSWIT... | **94** | 1 | 95 |
| 3 | Component: FreeSWITCH | 61 | FreeSWITCH. | **94** | 1 | 95 |
| 4 | Component: FreeSWITCH | 62 | We think FreeSWITCH is an amazing piece of software for handling ... | **94** | 1 | 95 |
| 5 | Component: FreeSWITCH | 66 | FreeSWITCH can also be integrated with VOIP providers so that use... | **94** | 1 | 95 |
| 6 | Component: FreeSWITCH | 63 | FreeSWITCH provides the voice conferencing capability in BigBlueB... | **94** | 1 | 95 |
| 7 | Component: FSESL | 57 | FSESL akka. | **92** | 0 | 92 |
| 8 | Component: Presentation Conversion | 81 | The diagram below describes the flow of the presentation conversi... | **70** | 3 | 73 |
| 9 | Component: Presentation Conversion | 80 | Presentation conversion flow. | **70** | 3 | 73 |
| 10 | Component: BBB web | 36 | BBB web. | **22** | 0 | 22 |
| 11 | Component: BBB web | 30 | If more than one backend is running, bbb-web splits the load in r... | **22** | 0 | 22 |
| 12 | Component: BBB web | 78 | The PDF document is then converted into scalable vector graphics ... | **22** | 0 | 22 |
| 13 | Component: HTML5 Server | 13 | Updates to MongoDB on the server side are automatically pushed to... | **16** | 8 | 24 |
| 14 | Component: HTML5 Server | 10 | The MongoDB database contains information about all meetings on t... | **16** | 8 | 24 |
| 15 | Component: HTML5 Server | 12 | The client side subscribes to the published collections on the se... | **16** | 8 | 24 |
| 16 | Component: HTML5 Server | 15 | Scalability of HTML5 server component. | **16** | 8 | 24 |
| 17 | Component: HTML5 Client | 14 | The following diagram gives an overview of the architecture of th... | **16** | 5 | 21 |
| 18 | Component: HTML5 Server | 8 | The HTML5 server sits behind nginx. | **16** | 8 | 24 |
| 19 | Component: HTML5 Server | 47 | Redis PubSub provides a communication channel between different a... | **16** | 8 | 24 |
| 20 | Component: HTML5 Server | 6 | The HTML5 client connects directly with the BigBlueButton server ... | **16** | 8 | 24 |
| 21 | Component: HTML5 Server | 39 | The BigBlueButton API provides a third-party integration (such as... | **16** | 8 | 24 |
| 22 | Component: HTML5 Client | 6 | The HTML5 client connects directly with the BigBlueButton server ... | **16** | 5 | 21 |
| 23 | Component: HTML5 Server | 9 | The HTML5 server is built upon Meteor.js in ECMA2015 for communic... | **16** | 8 | 24 |
| 24 | Component: HTML5 Client | 4 | HTML5 client. | **16** | 5 | 21 |
| 25 | Component: HTML5 Client | 5 | The HTML5 client is a single page, responsive web application tha... | **16** | 5 | 21 |
| 26 | Component: HTML5 Server | 73 | When joining through the client, the user can choose to join Micr... | **16** | 8 | 24 |
| 27 | Component: Apps | 54 | Below is a diagram of the different components of Apps Akka. | **15** | 1 | 16 |
| 28 | Component: Apps | 51 | Apps akka. | **15** | 1 | 16 |
| 29 | Component: Apps | 60 | Communication between apps and FreeSWITCH Event Socket Layer (fse... | **15** | 1 | 16 |
| 30 | Component: Apps | 52 | BigBlueButton Apps is the main application that pulls together th... | **15** | 1 | 16 |
| 31 | Component: Apps | 26 | Frontends receive other DDP events including method calls to send... | **15** | 1 | 16 |
| 32 | Component: Redis PubSub | 79 | The conversion process sends progress messages to the client thro... | **7** | 0 | 7 |
| 33 | Component: Redis PubSub | 46 | Redis PubSub. | **7** | 0 | 7 |
| 34 | Component: Redis PubSub | 60 | Communication between apps and FreeSWITCH Event Socket Layer (fse... | **7** | 0 | 7 |
| 35 | Component: Redis PubSub | 47 | Redis PubSub provides a communication channel between different a... | **7** | 0 | 7 |
| 36 | Component: WebRTC-SFU | 73 | When joining through the client, the user can choose to join Micr... | **6** | 0 | 6 |
| 37 | Component: WebRTC-SFU | 67 | Kurento and WebRTC-SFU. | **6** | 0 | 6 |
| 38 | Component: WebRTC-SFU | 65 | Users joining through Google Chrome or Mozilla Firefox are able t... | **6** | 0 | 6 |
| 39 | Component: WebRTC-SFU | 70 | The WebRTC-SFU acts as the media controller handling negotiations... | **6** | 0 | 6 |
| 40 | Component: Redis DB | 49 | When a meeting is recorded, all events are stored in Redis DB. | **3** | 0 | 3 |
| 41 | Component: Redis DB | 48 | Redis DB. | **3** | 0 | 3 |
| 42 | _oN4CMFkHEeyewPSmlgszyA | 68 | Kurento Media Server KMS is a media server that implements both S... | **0** | 0 | 0 |
| 43 | Component: FreeSWITCH | 59 | This allows others who are using voice conference systems other t... | **0** | 95 | 95 |
| 44 | _oN4CMFkHEeyewPSmlgszyA | 67 | Kurento and WebRTC-SFU. | **0** | 0 | 0 |
| | **TOTAL** | | | **1219** | **212** | **1431** |

### SAD-SAM FPs → Actual SAD-CODE Links Produced (5 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: HTML5 Server | 18 | Because nodejs was running on a single CPU core, having a 16 or 3... | 0 | **24** | 24 |
| 2 | Component: HTML5 Server | 68 | Kurento Media Server KMS is a media server that implements both S... | 0 | **24** | 24 |
| 3 | Component: FreeSWITCH | 60 | Communication between apps and FreeSWITCH Event Socket Layer (fse... | 84 | **11** | 95 |
| 4 | Component: WebRTC-SFU | 5 | The HTML5 client is a single page, responsive web application tha... | 0 | **6** | 6 |
| 5 | Component: WebRTC-SFU | 74 | WebRTC provides the user with high-quality audio with lower delay... | 0 | **6** | 6 |
| | **TOTAL** | | | **84** | **71** | **155** |

### Per-Model-Element Summary

| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |
|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|
| Component: FreeSWITCH | 7 | 564 | 101 | 1 | 84 | 11 | +536 |
| Component: Presentation Conversion | 2 | 140 | 6 | 0 | 0 | 0 | +134 |
| Component: HTML5 Server | 10 | 160 | 80 | 2 | 0 | 48 | +32 |
| Component: FSESL | 1 | 92 | 0 | 0 | 0 | 0 | +92 |
| Component: Apps | 5 | 75 | 5 | 0 | 0 | 0 | +70 |
| Component: BBB web | 3 | 66 | 0 | 0 | 0 | 0 | +66 |
| Component: HTML5 Client | 4 | 64 | 20 | 0 | 0 | 0 | +44 |
| Component: Redis PubSub | 4 | 28 | 0 | 0 | 0 | 0 | +28 |
| Component: WebRTC-SFU | 4 | 24 | 0 | 2 | 0 | 12 | +12 |
| Component: Redis DB | 2 | 6 | 0 | 0 | 0 | 0 | +6 |
| _oN4CMFkHEeyewPSmlgszyA | 2 | 0 | 0 | 0 | 0 | 0 | +0 |

## JABREF

TransArc output: 8268 TPs + 994 FPs = 9262 total | Gold: 8268

### SAD-SAM TPs → Actual SAD-CODE Links Produced (18 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: logic | 6 | The logic is responsible for reading/writing/importing/exporting ... | **972** | 0 | 972 |
| 2 | Component: logic | 1 | We have been successfully transitioning from a spaghetti to a mor... | **972** | 0 | 972 |
| 3 | Component: logic | 4 | We have JUnit tests to detect violations of the most crucial depe... | **972** | 0 | 972 |
| 4 | Component: logic | 9 | The model should have no dependencies to other classes of JabRef ... | **972** | 0 | 972 |
| 5 | Component: gui | 1 | We have been successfully transitioning from a spaghetti to a mor... | **707** | 1 | 708 |
| 6 | Component: gui | 4 | We have JUnit tests to detect violations of the most crucial depe... | **707** | 1 | 708 |
| 7 | Component: gui | 7 | Only the gui knows the user and his preferences and can interact ... | **707** | 1 | 708 |
| 8 | Component: gui | 6 | The logic is responsible for reading/writing/importing/exporting ... | **707** | 1 | 708 |
| 9 | Component: model | 6 | The logic is responsible for reading/writing/importing/exporting ... | **250** | 0 | 250 |
| 10 | Component: model | 5 | The model represents the most important data structures (BibDatas... | **250** | 0 | 250 |
| 11 | Component: model | 1 | We have been successfully transitioning from a spaghetti to a mor... | **250** | 0 | 250 |
| 12 | Component: model | 4 | We have JUnit tests to detect violations of the most crucial depe... | **250** | 0 | 250 |
| 13 | Component: model | 9 | The model should have no dependencies to other classes of JabRef ... | **250** | 0 | 250 |
| 14 | Component: model | 12 | We use an event bus to publish events from the model to the other... | **250** | 0 | 250 |
| 15 | Component: preferences | 11 | The preferences represents all information customizable by a user... | **18** | 0 | 18 |
| 16 | Component: preferences | 2 | There are additional utility packages for preferences and the cli... | **18** | 0 | 18 |
| 17 | Component: cli | 10 | The cli package bundles classes that are responsible for JabRef’s... | **8** | 0 | 8 |
| 18 | Component: cli | 2 | There are additional utility packages for preferences and the cli... | **8** | 0 | 8 |
| | **TOTAL** | | | **8268** | **4** | **8272** |

### SAD-SAM FPs → Actual SAD-CODE Links Produced (2 links)

| Rank | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs | Total |
|------|--------------|------|---------------|-------------|-------------|-------|
| 1 | Component: logic | 5 | The model represents the most important data structures (BibDatas... | 0 | **972** | 972 |
| 2 | Component: preferences | 7 | Only the gui knows the user and his preferences and can interact ... | 0 | **18** | 18 |
| | **TOTAL** | | | **0** | **990** | **990** |

### Per-Model-Element Summary

| Model Element | SAD-SAM TPs | →SAD-CODE TPs | →SAD-CODE FPs | SAD-SAM FPs | →SAD-CODE TPs | →SAD-CODE FPs | Net Value |
|--------------|-------------|--------------|--------------|------------|--------------|--------------|-----------|
| Component: logic | 4 | 3888 | 0 | 1 | 0 | 972 | +2916 |
| Component: gui | 4 | 2828 | 4 | 0 | 0 | 0 | +2824 |
| Component: model | 6 | 1500 | 0 | 0 | 0 | 0 | +1500 |
| Component: preferences | 2 | 36 | 0 | 1 | 0 | 18 | +18 |
| Component: cli | 2 | 16 | 0 | 0 | 0 | 0 | +16 |

## Cross-Project Ranking: SAD-SAM TPs by Actual SAD-CODE TPs Produced

| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |
|------|---------|--------------|------|---------------|-------------|-------------|
| 1 | jabref | Component: logic | 6 | The logic is responsible for reading/writing/importing/... | **972** | 0 |
| 2 | jabref | Component: logic | 1 | We have been successfully transitioning from a spaghett... | **972** | 0 |
| 3 | jabref | Component: logic | 4 | We have JUnit tests to detect violations of the most cr... | **972** | 0 |
| 4 | jabref | Component: logic | 9 | The model should have no dependencies to other classes ... | **972** | 0 |
| 5 | jabref | Component: gui | 1 | We have been successfully transitioning from a spaghett... | **707** | 1 |
| 6 | jabref | Component: gui | 4 | We have JUnit tests to detect violations of the most cr... | **707** | 1 |
| 7 | jabref | Component: gui | 7 | Only the gui knows the user and his preferences and can... | **707** | 1 |
| 8 | jabref | Component: gui | 6 | The logic is responsible for reading/writing/importing/... | **707** | 1 |
| 9 | teammates | Component: UI | 4 | The UI Browser seen by users consists of Web pages cont... | **348** | 0 |
| 10 | teammates | Component: UI | 85 | logic.api provides the API of the component to be acces... | **348** | 0 |
| 11 | teammates | Component: UI | 5 | This UI is a single HTML page generated by Angular fram... | **348** | 0 |
| 12 | teammates | Component: UI | 1 | Architecture contains UI Component, Logic Component, St... | **348** | 0 |
| 13 | teammates | Component: UI | 25 | The diagram below shows the object structure of the UI ... | **348** | 0 |
| 14 | teammates | Component: UI | 7 | In the UI Server the entry point for the application ba... | **348** | 0 |
| 15 | teammates | Component: UI | 97 | The UI is expected to check access control (using GateK... | **348** | 0 |
| 16 | teammates | Component: UI | 81 | Sanitizing input values received from the UI component. | **348** | 0 |
| 17 | teammates | Component: UI | 29 | The UI component is the first stop for 99% of all reque... | **348** | 0 |
| 18 | jabref | Component: model | 6 | The logic is responsible for reading/writing/importing/... | **250** | 0 |
| 19 | jabref | Component: model | 5 | The model represents the most important data structures... | **250** | 0 |
| 20 | jabref | Component: model | 1 | We have been successfully transitioning from a spaghett... | **250** | 0 |
| 21 | jabref | Component: model | 4 | We have JUnit tests to detect violations of the most cr... | **250** | 0 |
| 22 | jabref | Component: model | 9 | The model should have no dependencies to other classes ... | **250** | 0 |
| 23 | jabref | Component: model | 12 | We use an event bus to publish events from the model to... | **250** | 0 |
| 24 | teammates | Component: Common | 1 | Architecture contains UI Component, Logic Component, St... | **150** | 0 |
| 25 | teammates | Component: Common | 175 | x.util contains component test cases for testing the ut... | **150** | 0 |
| 26 | teammates | Component: Common | 174 | x.datatransfer contains component test cases for testin... | **150** | 0 |
| 27 | teammates | Component: Common | 20 | The Common component contains utility code (data transf... | **150** | 0 |
| 28 | teammates | Component: Common | 155 | The Common component contains common utilities used acr... | **150** | 0 |
| 29 | teammates | Component: E2E | 15 | The E2E end-to-end component is used to interact with t... | **123** | 0 |
| 30 | teammates | Component: E2E | 1 | Architecture contains UI Component, Logic Component, St... | **123** | 0 |
| 31 | teammates | Component: E2E | 185 | The E2E component has no knowledge of the internal work... | **123** | 0 |
| 32 | teammates | Component: E2E | 186 | Its primary function is for E2E tests and L&P (Load & P... | **123** | 0 |
| 33 | teammates | Component: E2E | 16 | Its primary function is for E2E tests. | **123** | 0 |
| 34 | bigbluebutton | Component: FreeSWITCH | 72 | A user can join the voice conference (running in FreeSW... | **94** | 1 |
| 35 | bigbluebutton | Component: FreeSWITCH | 58 | We have extracted out the component that integrates wit... | **94** | 1 |
| 36 | bigbluebutton | Component: FreeSWITCH | 61 | FreeSWITCH. | **94** | 1 |
| 37 | bigbluebutton | Component: FreeSWITCH | 62 | We think FreeSWITCH is an amazing piece of software for... | **94** | 1 |
| 38 | bigbluebutton | Component: FreeSWITCH | 66 | FreeSWITCH can also be integrated with VOIP providers s... | **94** | 1 |
| 39 | bigbluebutton | Component: FreeSWITCH | 63 | FreeSWITCH provides the voice conferencing capability i... | **94** | 1 |
| 40 | bigbluebutton | Component: FSESL | 57 | FSESL akka. | **92** | 0 |

## Cross-Project Ranking: SAD-SAM FPs by Actual SAD-CODE FPs Produced

| Rank | Project | Model Element | Sent | Sentence Text | SAD-CODE TPs | SAD-CODE FPs |
|------|---------|--------------|------|---------------|-------------|-------------|
| 1 | jabref | Component: logic | 5 | The model represents the most important data structures... | 0 | **972** |
| 2 | teammates | Component: UI | 23 | ui.website is not a real package. | 0 | **348** |
| 3 | teammates | Component: UI | 26 | ui.website is not a Java package. | 0 | **348** |
| 4 | teammates | Component: UI | 22 | logic, ui.website, ui.controller represent an applicati... | 125 | **223** |
| 5 | teammates | Component: Common | 158 | common.exceptions contains custom exceptions. | 11 | **139** |
| 6 | teammates | Component: E2E | 17 | Selenium Java is used to automate E2E testing with actu... | 0 | **123** |
| 7 | teammates | Component: E2E | 189 | e2e.pageobjects contains abstractions of the pages as t... | 0 | **123** |
| 8 | teammates | Component: E2E | 190 | e2e.cases contains test cases. | 0 | **123** |
| 9 | teammates | Component: Common | 157 | common.util contains utility classes. | 32 | **118** |
| 10 | teammates | Component: Logic | 119 | It contains minimal logic beyond what is directly relev... | 0 | **71** |
| 11 | teammates | Component: Logic | 117 | Refer to the API for the cascade logic. | 0 | **71** |
| 12 | teammates | Component: Logic | 79 | Managing relationships between entities, e.g. cascade l... | 0 | **71** |
| 13 | teammates | Component: Logic | 85 | logic.api provides the API of the component to be acces... | 21 | **50** |
| 14 | teammates | Component: Storage | 132 | storage.entity contains classes that represent persista... | 14 | **45** |
| 15 | teammates | Component: Storage | 125 | Classes in the storage.entity package are not visible o... | 14 | **45** |
| 16 | teammates | Component: Common | 159 | common.datatransfer contains data transfer objects. | 107 | **43** |
| 17 | teammates | Component: Common | 160 | common.datatransfer package contains lightweight data t... | 107 | **43** |
| 18 | teammates | Component: Common | 127 | These datatransfer classes are in common.datatransfer p... | 107 | **43** |
| 19 | teammates | Component: Storage | 133 | storage.search contains classes for dealing with search... | 16 | **43** |
| 20 | teammates | Component: Logic | 86 | logic.core contains the core logic of the system. | 30 | **41** |
| 21 | teammates | Component: Client | 198 | client.scripts scripts that deal with the back end data... | 0 | **40** |
| 22 | teammates | Component: Client | 4 | The UI Browser seen by users consists of Web pages cont... | 0 | **40** |
| 23 | teammates | Component: Client | 197 | client.remoteapi classes needed to connect to the back ... | 2 | **38** |
| 24 | teammates | Component: Client | 196 | client.util contains helpers needed for client scripts. | 4 | **36** |
| 25 | teammates | Component: Client | 195 | Package overview contains client.util, client.remoteapi... | 6 | **34** |
| 26 | teammates | Component: Storage | 131 | storage.api provides the API of the component to be acc... | 29 | **30** |
| 27 | teammates | Component: Logic | 22 | logic, ui.website, ui.controller represent an applicati... | 42 | **29** |
| 28 | bigbluebutton | Component: HTML5 Server | 18 | Because nodejs was running on a single CPU core, having... | 0 | **24** |
| 29 | bigbluebutton | Component: HTML5 Server | 68 | Kurento Media Server KMS is a media server that impleme... | 0 | **24** |
| 30 | teammates | Component: Logic | 84 | Package overview contains logic.api, logic.core. | 51 | **20** |
| 31 | jabref | Component: preferences | 7 | Only the gui knows the user and his preferences and can... | 0 | **18** |
| 32 | teammates | Component: Test Driver | 173 | x.testdriver contains component test cases for testing ... | 0 | **17** |
| 33 | bigbluebutton | Component: FreeSWITCH | 60 | Communication between apps and FreeSWITCH Event Socket ... | 84 | **11** |
| 34 | bigbluebutton | Component: WebRTC-SFU | 5 | The HTML5 client is a single page, responsive web appli... | 0 | **6** |
| 35 | bigbluebutton | Component: WebRTC-SFU | 74 | WebRTC provides the user with high-quality audio with l... | 0 | **6** |
| 36 | mediastore | Component: Reencoding | 37 | However, a download can cause re-encoding of the audio ... | 0 | **1** |
| 37 | teammates | Component: Storage | 130 | Package overview contains storage.api, storage.entity, ... | 59 | **0** |
| 38 | teammates | Component: E2E | 187 | Package overview contains e2e.util, e2e.pageobjects, e2... | 123 | **0** |
| 39 | teammates | Component: E2E | 188 | e2e.util contains helpers needed for running E2E tests. | 123 | **0** |
| 40 | teammates | Component: Common | 156 | Package overview contains common.util, common.exception... | 150 | **0** |

## SAD-SAM Link Efficiency

What fraction of SAD-CODE output from each SAD-SAM link is correct?

### SAD-SAM TPs: Precision of SAD-CODE Output

| Project | SAD-SAM TP | Model Element | Sent | Total Produced | TPs | FPs | Precision |
|---------|-----------|--------------|------|---------------|-----|-----|-----------|
| bigbluebutton | (Component: FreeSWITCH, S59) | Component: FreeSWITCH | 59 | 95 | 0 | 95 | 0.000 |
| bigbluebutton | (Component: HTML5 Server, S13) | Component: HTML5 Server | 13 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S10) | Component: HTML5 Server | 10 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S12) | Component: HTML5 Server | 12 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S15) | Component: HTML5 Server | 15 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S8) | Component: HTML5 Server | 8 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S47) | Component: HTML5 Server | 47 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S6) | Component: HTML5 Server | 6 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S39) | Component: HTML5 Server | 39 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S9) | Component: HTML5 Server | 9 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Server, S73) | Component: HTML5 Server | 73 | 24 | 16 | 8 | 0.667 |
| bigbluebutton | (Component: HTML5 Client, S14) | Component: HTML5 Client | 14 | 21 | 16 | 5 | 0.762 |
| bigbluebutton | (Component: HTML5 Client, S6) | Component: HTML5 Client | 6 | 21 | 16 | 5 | 0.762 |
| bigbluebutton | (Component: HTML5 Client, S4) | Component: HTML5 Client | 4 | 21 | 16 | 5 | 0.762 |
| bigbluebutton | (Component: HTML5 Client, S5) | Component: HTML5 Client | 5 | 21 | 16 | 5 | 0.762 |
| bigbluebutton | (Component: Apps, S54) | Component: Apps | 54 | 16 | 15 | 1 | 0.938 |
| bigbluebutton | (Component: Apps, S51) | Component: Apps | 51 | 16 | 15 | 1 | 0.938 |
| bigbluebutton | (Component: Apps, S60) | Component: Apps | 60 | 16 | 15 | 1 | 0.938 |
| bigbluebutton | (Component: Apps, S52) | Component: Apps | 52 | 16 | 15 | 1 | 0.938 |
| bigbluebutton | (Component: Apps, S26) | Component: Apps | 26 | 16 | 15 | 1 | 0.938 |

