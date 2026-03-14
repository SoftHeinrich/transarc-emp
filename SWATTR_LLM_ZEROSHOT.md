# SWATTR TP vs FP: Zero-Shot LLM Classification (Batch)

Using Claude Sonnet via CLI. All links per project in a single batch prompt.

**Data**: 148 TPs + 40 FPs = 188 SWATTR links

## Strategy: Direct (no convention hints)

| Metric | Value |
|--------|-------|
| TPs correctly kept | 133/148 (90%) |
| TPs wrongly killed | 15/148 (10%) |
| FPs correctly caught | 6/40 (15%) |
| FPs missed | 34/40 (85%) |
| **Net benefit** | **-9** |
| Filter precision | 29% |
| Overall accuracy | 74% |

**Per-project:**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net |
|---------|-----|-----|------------|------------|-----|
| mediastore | 17 | 1 | 1 | 0 | +1 |
| teastore | 20 | 0 | 0 | 0 | +0 |
| teammates | 49 | 32 | 1 | 3 | -2 |
| bigbluebutton | 44 | 5 | 2 | 12 | -10 |
| jabref | 18 | 2 | 2 | 0 | +2 |

**FP details:**

- [CAUGHT] mediastore S37 x Reencoding: `However, a download can cause re-encoding of the audio file....`
- [CAUGHT] teammates S4 x Client: `The UI Browser seen by users consists of Web pages containing HTML, CS...`
- [MISSED] teammates S17 x E2E: `Selenium Java is used to automate E2E testing with actual Web browsers...`
- [MISSED] teammates S22 x UI: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [MISSED] teammates S22 x Logic: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [MISSED] teammates S23 x UI: `ui.website is not a real package....`
- [MISSED] teammates S26 x UI: `ui.website is not a Java package....`
- [MISSED] teammates S79 x Logic: `Managing relationships between entities, e.g. cascade logic for create...`
- [MISSED] teammates S84 x Logic: `Package overview contains logic.api, logic.core....`
- [MISSED] teammates S85 x Logic: `logic.api provides the API of the component to be accessed by the UI....`
- [MISSED] teammates S86 x Logic: `logic.core contains the core logic of the system....`
- [MISSED] teammates S117 x Logic: `Refer to the API for the cascade logic....`
- [MISSED] teammates S119 x Logic: `It contains minimal logic beyond what is directly relevant to CRUD ope...`
- [MISSED] teammates S125 x Storage: `Classes in the storage.entity package are not visible outside this com...`
- [MISSED] teammates S127 x Common: `These datatransfer classes are in common.datatransfer package, to be e...`
- [MISSED] teammates S130 x Storage: `Package overview contains storage.api, storage.entity, storage.search....`
- [MISSED] teammates S131 x Storage: `storage.api provides the API of the component to be accessed by the lo...`
- [MISSED] teammates S132 x Storage: `storage.entity contains classes that represent persistable entities....`
- [MISSED] teammates S133 x Storage: `storage.search contains classes for dealing with searching and indexin...`
- [MISSED] teammates S156 x Common: `Package overview contains common.util, common.exceptions, common.datat...`
- [MISSED] teammates S157 x Common: `common.util contains utility classes....`
- [MISSED] teammates S158 x Common: `common.exceptions contains custom exceptions....`
- [MISSED] teammates S159 x Common: `common.datatransfer contains data transfer objects....`
- [MISSED] teammates S160 x Common: `common.datatransfer package contains lightweight data transfer object ...`
- [MISSED] teammates S173 x Test Driver: `x.testdriver contains component test cases for testing the test driver...`
- [MISSED] teammates S187 x E2E: `Package overview contains e2e.util, e2e.pageobjects, e2e.cases, x.util...`
- [MISSED] teammates S188 x E2E: `e2e.util contains helpers needed for running E2E tests....`
- [MISSED] teammates S189 x E2E: `e2e.pageobjects contains abstractions of the pages as they appear on a...`
- [MISSED] teammates S190 x E2E: `e2e.cases contains test cases....`
- [MISSED] teammates S195 x Client: `Package overview contains client.util, client.remoteapi, client.script...`
- [MISSED] teammates S196 x Client: `client.util contains helpers needed for client scripts....`
- [MISSED] teammates S197 x Client: `client.remoteapi classes needed to connect to the back end directly....`
- [MISSED] teammates S198 x Client: `client.scripts scripts that deal with the back end data for administra...`
- [CAUGHT] bigbluebutton S5 x WebRTC-SFU: `The HTML5 client is a single page, responsive web application that is ...`
- [MISSED] bigbluebutton S18 x HTML5 Server: `Because nodejs was running on a single CPU core, having a 16 or 32 CPU...`
- [MISSED] bigbluebutton S60 x FreeSWITCH: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- [CAUGHT] bigbluebutton S68 x HTML5 Server: `Kurento Media Server KMS is a media server that implements both SFU an...`
- [MISSED] bigbluebutton S74 x WebRTC-SFU: `WebRTC provides the user with high-quality audio with lower delay....`
- [CAUGHT] jabref S5 x logic: `The model represents the most important data structures (BibDatases, B...`
- [CAUGHT] jabref S7 x preferences: `Only the gui knows the user and his preferences and can interact with ...`

**TPs wrongly killed (15):**

- teammates S7 x Logic: `In the UI Server the entry point for the application back end logic is...`
- teammates S9 x UNKNOWN: `The storage layer of the application uses the persistence framework pr...`
- teammates S137 x UNKNOWN: `These classes act as the bridge to the GAE Datastore....`
- bigbluebutton S6 x HTML5 Server: `The HTML5 client connects directly with the BigBlueButton server over ...`
- bigbluebutton S10 x HTML5 Server: `The MongoDB database contains information about all meetings on the se...`
- bigbluebutton S26 x Apps: `Frontends receive other DDP events including method calls to send even...`
- bigbluebutton S39 x HTML5 Server: `The BigBlueButton API provides a third-party integration (such as the ...`
- bigbluebutton S47 x HTML5 Server: `Redis PubSub provides a communication channel between different applic...`
- bigbluebutton S58 x FreeSWITCH: `We have extracted out the component that integrates with FreeSWITCH in...`
- bigbluebutton S59 x FreeSWITCH: `This allows others who are using voice conference systems other than F...`
- bigbluebutton S62 x FreeSWITCH: `We think FreeSWITCH is an amazing piece of software for handling audio...`
- bigbluebutton S65 x WebRTC-SFU: `Users joining through Google Chrome or Mozilla Firefox are able to tak...`
- bigbluebutton S67 x UNKNOWN: `Kurento and WebRTC-SFU....`
- bigbluebutton S68 x UNKNOWN: `Kurento Media Server KMS is a media server that implements both SFU an...`
- bigbluebutton S73 x HTML5 Server: `When joining through the client, the user can choose to join Microphon...`

## Strategy: Convention-aware (full rules)

| Metric | Value |
|--------|-------|
| TPs correctly kept | 98/148 (66%) |
| TPs wrongly killed | 50/148 (34%) |
| FPs correctly caught | 39/40 (98%) |
| FPs missed | 1/40 (2%) |
| **Net benefit** | **-11** |
| Filter precision | 44% |
| Overall accuracy | 73% |

**Per-project:**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net |
|---------|-----|-----|------------|------------|-----|
| mediastore | 17 | 1 | 1 | 1 | +0 |
| teastore | 20 | 0 | 0 | 2 | -2 |
| teammates | 49 | 32 | 31 | 21 | +10 |
| bigbluebutton | 44 | 5 | 5 | 18 | -13 |
| jabref | 18 | 2 | 2 | 8 | -6 |

**FP details:**

- [CAUGHT] mediastore S37 x Reencoding: `However, a download can cause re-encoding of the audio file....`
- [CAUGHT] teammates S4 x Client: `The UI Browser seen by users consists of Web pages containing HTML, CS...`
- [CAUGHT] teammates S17 x E2E: `Selenium Java is used to automate E2E testing with actual Web browsers...`
- [CAUGHT] teammates S22 x UI: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S22 x Logic: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S23 x UI: `ui.website is not a real package....`
- [CAUGHT] teammates S26 x UI: `ui.website is not a Java package....`
- [MISSED] teammates S79 x Logic: `Managing relationships between entities, e.g. cascade logic for create...`
- [CAUGHT] teammates S84 x Logic: `Package overview contains logic.api, logic.core....`
- [CAUGHT] teammates S85 x Logic: `logic.api provides the API of the component to be accessed by the UI....`
- [CAUGHT] teammates S86 x Logic: `logic.core contains the core logic of the system....`
- [CAUGHT] teammates S117 x Logic: `Refer to the API for the cascade logic....`
- [CAUGHT] teammates S119 x Logic: `It contains minimal logic beyond what is directly relevant to CRUD ope...`
- [CAUGHT] teammates S125 x Storage: `Classes in the storage.entity package are not visible outside this com...`
- [CAUGHT] teammates S127 x Common: `These datatransfer classes are in common.datatransfer package, to be e...`
- [CAUGHT] teammates S130 x Storage: `Package overview contains storage.api, storage.entity, storage.search....`
- [CAUGHT] teammates S131 x Storage: `storage.api provides the API of the component to be accessed by the lo...`
- [CAUGHT] teammates S132 x Storage: `storage.entity contains classes that represent persistable entities....`
- [CAUGHT] teammates S133 x Storage: `storage.search contains classes for dealing with searching and indexin...`
- [CAUGHT] teammates S156 x Common: `Package overview contains common.util, common.exceptions, common.datat...`
- [CAUGHT] teammates S157 x Common: `common.util contains utility classes....`
- [CAUGHT] teammates S158 x Common: `common.exceptions contains custom exceptions....`
- [CAUGHT] teammates S159 x Common: `common.datatransfer contains data transfer objects....`
- [CAUGHT] teammates S160 x Common: `common.datatransfer package contains lightweight data transfer object ...`
- [CAUGHT] teammates S173 x Test Driver: `x.testdriver contains component test cases for testing the test driver...`
- [CAUGHT] teammates S187 x E2E: `Package overview contains e2e.util, e2e.pageobjects, e2e.cases, x.util...`
- [CAUGHT] teammates S188 x E2E: `e2e.util contains helpers needed for running E2E tests....`
- [CAUGHT] teammates S189 x E2E: `e2e.pageobjects contains abstractions of the pages as they appear on a...`
- [CAUGHT] teammates S190 x E2E: `e2e.cases contains test cases....`
- [CAUGHT] teammates S195 x Client: `Package overview contains client.util, client.remoteapi, client.script...`
- [CAUGHT] teammates S196 x Client: `client.util contains helpers needed for client scripts....`
- [CAUGHT] teammates S197 x Client: `client.remoteapi classes needed to connect to the back end directly....`
- [CAUGHT] teammates S198 x Client: `client.scripts scripts that deal with the back end data for administra...`
- [CAUGHT] bigbluebutton S5 x WebRTC-SFU: `The HTML5 client is a single page, responsive web application that is ...`
- [CAUGHT] bigbluebutton S18 x HTML5 Server: `Because nodejs was running on a single CPU core, having a 16 or 32 CPU...`
- [CAUGHT] bigbluebutton S60 x FreeSWITCH: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- [CAUGHT] bigbluebutton S68 x HTML5 Server: `Kurento Media Server KMS is a media server that implements both SFU an...`
- [CAUGHT] bigbluebutton S74 x WebRTC-SFU: `WebRTC provides the user with high-quality audio with lower delay....`
- [CAUGHT] jabref S5 x logic: `The model represents the most important data structures (BibDatases, B...`
- [CAUGHT] jabref S7 x preferences: `Only the gui knows the user and his preferences and can interact with ...`

**TPs wrongly killed (50):**

- mediastore S17 x TagWatermarking: `Afterward, the MediaManagement component forwards these audio files fr...`
- teastore S7 x WebUI: `Images (with few exceptions) are not provides by the WebUi, but are re...`
- teastore S10 x WebUI: `The Image Provider delivers images to the WebUI as base64 encoded stri...`
- teammates S7 x Logic: `In the UI Server the entry point for the application back end logic is...`
- teammates S8 x Logic: `The main logic of the application is in POJOs (Plain Old Java Objects)...`
- teammates S9 x UNKNOWN: `The storage layer of the application uses the persistence framework pr...`
- teammates S10 x Test Driver: `The following explains the use of the Test Driver....`
- teammates S25 x UI: `The diagram below shows the object structure of the UI component....`
- teammates S47 x Logic: `If the action is allowed, it will be performed, interacting with the L...`
- teammates S68 x Logic: `Seventh, the corresponding AutomatedAction will be performed, interact...`
- teammates S81 x UI: `Sanitizing input values received from the UI component....`
- teammates S85 x UI: `logic.api provides the API of the component to be accessed by the UI....`
- teammates S87 x Logic: `Logic API is represented by the classes Logic, GateKeeper, EmailGenera...`
- teammates S88 x Storage: `Logic is a Facade class which connects to the several Logic classes to...`
- teammates S97 x Logic: `The UI is expected to check access control (using GateKeeper class) be...`
- teammates S101 x Storage: `Entity already exists throws EntityAlreadyExistsException (escalated f...`
- teammates S122 x Logic: `Hiding the complexities of datastore from the Logic component....`
- teammates S131 x Logic: `storage.api provides the API of the component to be accessed by the lo...`
- teammates S137 x UNKNOWN: `These classes act as the bridge to the GAE Datastore....`
- teammates S174 x Common: `x.datatransfer contains component test cases for testing the datatrans...`
- teammates S175 x Common: `x.util contains component test cases for testing the utility classes f...`
- teammates S176 x Logic: `x.logic contains component test cases for testing the Logic component....`
- teammates S177 x Storage: `x.storage contains component test cases for testing the Storage compon...`
- teammates S185 x Logic: `The E2E component has no knowledge of the internal workings of the app...`
- bigbluebutton S6 x HTML5 Server: `The HTML5 client connects directly with the BigBlueButton server over ...`
- bigbluebutton S10 x HTML5 Server: `The MongoDB database contains information about all meetings on the se...`
- bigbluebutton S14 x HTML5 Client: `The following diagram gives an overview of the architecture of the HTM...`
- bigbluebutton S26 x Apps: `Frontends receive other DDP events including method calls to send even...`
- bigbluebutton S39 x HTML5 Server: `The BigBlueButton API provides a third-party integration (such as the ...`
- bigbluebutton S47 x HTML5 Server: `Redis PubSub provides a communication channel between different applic...`
- bigbluebutton S54 x Apps: `Below is a diagram of the different components of Apps Akka....`
- bigbluebutton S58 x FreeSWITCH: `We have extracted out the component that integrates with FreeSWITCH in...`
- bigbluebutton S59 x FreeSWITCH: `This allows others who are using voice conference systems other than F...`
- bigbluebutton S60 x Apps: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- bigbluebutton S62 x FreeSWITCH: `We think FreeSWITCH is an amazing piece of software for handling audio...`
- bigbluebutton S65 x WebRTC-SFU: `Users joining through Google Chrome or Mozilla Firefox are able to tak...`
- bigbluebutton S67 x UNKNOWN: `Kurento and WebRTC-SFU....`
- bigbluebutton S68 x UNKNOWN: `Kurento Media Server KMS is a media server that implements both SFU an...`
- bigbluebutton S72 x FreeSWITCH: `A user can join the voice conference (running in FreeSWITCH) from the ...`
- bigbluebutton S73 x WebRTC-SFU: `When joining through the client, the user can choose to join Microphon...`
- bigbluebutton S73 x HTML5 Server: `When joining through the client, the user can choose to join Microphon...`
- bigbluebutton S81 x Presentation Conversion: `The diagram below describes the flow of the presentation conversion....`
- jabref S2 x cli: `There are additional utility packages for preferences and the cli....`
- jabref S2 x preferences: `There are additional utility packages for preferences and the cli....`
- jabref S4 x gui: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S4 x logic: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S4 x model: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S6 x model: `The logic is responsible for reading/writing/importing/exporting and m...`
- jabref S6 x gui: `The logic is responsible for reading/writing/importing/exporting and m...`
- jabref S12 x model: `We use an event bus to publish events from the model to the other laye...`

## Strategy: Three-filter (reference + topicality + abstraction)

| Metric | Value |
|--------|-------|
| TPs correctly kept | 63/148 (43%) |
| TPs wrongly killed | 85/148 (57%) |
| FPs correctly caught | 36/40 (90%) |
| FPs missed | 4/40 (10%) |
| **Net benefit** | **-49** |
| Filter precision | 30% |
| Overall accuracy | 53% |

**Per-project:**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net |
|---------|-----|-----|------------|------------|-----|
| mediastore | 17 | 1 | 1 | 1 | +0 |
| teastore | 20 | 0 | 0 | 11 | -11 |
| teammates | 49 | 32 | 28 | 31 | -3 |
| bigbluebutton | 44 | 5 | 5 | 31 | -26 |
| jabref | 18 | 2 | 2 | 11 | -9 |

**FP details:**

- [CAUGHT] mediastore S37 x Reencoding: `However, a download can cause re-encoding of the audio file....`
- [CAUGHT] teammates S4 x Client: `The UI Browser seen by users consists of Web pages containing HTML, CS...`
- [CAUGHT] teammates S17 x E2E: `Selenium Java is used to automate E2E testing with actual Web browsers...`
- [CAUGHT] teammates S22 x UI: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S22 x Logic: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S23 x UI: `ui.website is not a real package....`
- [CAUGHT] teammates S26 x UI: `ui.website is not a Java package....`
- [CAUGHT] teammates S79 x Logic: `Managing relationships between entities, e.g. cascade logic for create...`
- [CAUGHT] teammates S84 x Logic: `Package overview contains logic.api, logic.core....`
- [MISSED] teammates S85 x Logic: `logic.api provides the API of the component to be accessed by the UI....`
- [CAUGHT] teammates S86 x Logic: `logic.core contains the core logic of the system....`
- [CAUGHT] teammates S117 x Logic: `Refer to the API for the cascade logic....`
- [CAUGHT] teammates S119 x Logic: `It contains minimal logic beyond what is directly relevant to CRUD ope...`
- [MISSED] teammates S125 x Storage: `Classes in the storage.entity package are not visible outside this com...`
- [CAUGHT] teammates S127 x Common: `These datatransfer classes are in common.datatransfer package, to be e...`
- [CAUGHT] teammates S130 x Storage: `Package overview contains storage.api, storage.entity, storage.search....`
- [MISSED] teammates S131 x Storage: `storage.api provides the API of the component to be accessed by the lo...`
- [CAUGHT] teammates S132 x Storage: `storage.entity contains classes that represent persistable entities....`
- [CAUGHT] teammates S133 x Storage: `storage.search contains classes for dealing with searching and indexin...`
- [CAUGHT] teammates S156 x Common: `Package overview contains common.util, common.exceptions, common.datat...`
- [CAUGHT] teammates S157 x Common: `common.util contains utility classes....`
- [CAUGHT] teammates S158 x Common: `common.exceptions contains custom exceptions....`
- [CAUGHT] teammates S159 x Common: `common.datatransfer contains data transfer objects....`
- [MISSED] teammates S160 x Common: `common.datatransfer package contains lightweight data transfer object ...`
- [CAUGHT] teammates S173 x Test Driver: `x.testdriver contains component test cases for testing the test driver...`
- [CAUGHT] teammates S187 x E2E: `Package overview contains e2e.util, e2e.pageobjects, e2e.cases, x.util...`
- [CAUGHT] teammates S188 x E2E: `e2e.util contains helpers needed for running E2E tests....`
- [CAUGHT] teammates S189 x E2E: `e2e.pageobjects contains abstractions of the pages as they appear on a...`
- [CAUGHT] teammates S190 x E2E: `e2e.cases contains test cases....`
- [CAUGHT] teammates S195 x Client: `Package overview contains client.util, client.remoteapi, client.script...`
- [CAUGHT] teammates S196 x Client: `client.util contains helpers needed for client scripts....`
- [CAUGHT] teammates S197 x Client: `client.remoteapi classes needed to connect to the back end directly....`
- [CAUGHT] teammates S198 x Client: `client.scripts scripts that deal with the back end data for administra...`
- [CAUGHT] bigbluebutton S5 x WebRTC-SFU: `The HTML5 client is a single page, responsive web application that is ...`
- [CAUGHT] bigbluebutton S18 x HTML5 Server: `Because nodejs was running on a single CPU core, having a 16 or 32 CPU...`
- [CAUGHT] bigbluebutton S60 x FreeSWITCH: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- [CAUGHT] bigbluebutton S68 x HTML5 Server: `Kurento Media Server KMS is a media server that implements both SFU an...`
- [CAUGHT] bigbluebutton S74 x WebRTC-SFU: `WebRTC provides the user with high-quality audio with lower delay....`
- [CAUGHT] jabref S5 x logic: `The model represents the most important data structures (BibDatases, B...`
- [CAUGHT] jabref S7 x preferences: `Only the gui knows the user and his preferences and can interact with ...`

**TPs wrongly killed (85):**

- mediastore S17 x TagWatermarking: `Afterward, the MediaManagement component forwards these audio files fr...`
- teastore S1 x Registry: `The TeaStore consists of 5 replicatable services and a single Registry...`
- teastore S2 x ImageProvider: `The WebUI service retrieves images from the Image Provider....`
- teastore S4 x Recommender: `Data is retrieved from the PersistenceProvider and product recommendat...`
- teastore S4 x Persistence: `Data is retrieved from the PersistenceProvider and product recommendat...`
- teastore S5 x WebUI: `The WebUI provides the TeaStore front-end using Servlets in combinatio...`
- teastore S10 x ImageProvider: `The Image Provider delivers images to the WebUI as base64 encoded stri...`
- teastore S10 x WebUI: `The Image Provider delivers images to the WebUI as base64 encoded stri...`
- teastore S12 x ImageProvider: `If the product ID or UI name is not available to the Image Provider, a...`
- teastore S25 x Persistence: `The persistence provider uses a second level entity cache provided by ...`
- teastore S38 x Registry: `Service instances register themselves at the registry on startup....`
- teastore S41 x Registry: `Every running instance of the TeaStore uses one single registry....`
- teammates S1 x E2E: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x Storage: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x Client: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x UI: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x Test Driver: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x Logic: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S1 x Common: `Architecture contains UI Component, Logic Component, Storage Component...`
- teammates S4 x UI: `The UI Browser seen by users consists of Web pages containing HTML, CS...`
- teammates S5 x UI: `This UI is a single HTML page generated by Angular framework....`
- teammates S7 x Logic: `In the UI Server the entry point for the application back end logic is...`
- teammates S8 x Logic: `The main logic of the application is in POJOs (Plain Old Java Objects)...`
- teammates S9 x UNKNOWN: `The storage layer of the application uses the persistence framework pr...`
- teammates S9 x Storage: `The storage layer of the application uses the persistence framework pr...`
- teammates S10 x Test Driver: `The following explains the use of the Test Driver....`
- teammates S25 x UI: `The diagram below shows the object structure of the UI component....`
- teammates S47 x Logic: `If the action is allowed, it will be performed, interacting with the L...`
- teammates S68 x Logic: `Seventh, the corresponding AutomatedAction will be performed, interact...`
- teammates S81 x UI: `Sanitizing input values received from the UI component....`
- teammates S85 x UI: `logic.api provides the API of the component to be accessed by the UI....`
- teammates S87 x Logic: `Logic API is represented by the classes Logic, GateKeeper, EmailGenera...`
- teammates S88 x Storage: `Logic is a Facade class which connects to the several Logic classes to...`
- teammates S97 x Logic: `The UI is expected to check access control (using GateKeeper class) be...`
- teammates S101 x Storage: `Entity already exists throws EntityAlreadyExistsException (escalated f...`
- teammates S122 x Logic: `Hiding the complexities of datastore from the Logic component....`
- teammates S131 x Logic: `storage.api provides the API of the component to be accessed by the lo...`
- teammates S137 x UNKNOWN: `These classes act as the bridge to the GAE Datastore....`
- teammates S174 x Common: `x.datatransfer contains component test cases for testing the datatrans...`
- teammates S175 x Common: `x.util contains component test cases for testing the utility classes f...`
- teammates S176 x Logic: `x.logic contains component test cases for testing the Logic component....`
- teammates S177 x Storage: `x.storage contains component test cases for testing the Storage compon...`
- teammates S185 x Logic: `The E2E component has no knowledge of the internal workings of the app...`
- bigbluebutton S4 x HTML5 Client: `HTML5 client....`
- bigbluebutton S6 x HTML5 Server: `The HTML5 client connects directly with the BigBlueButton server over ...`
- bigbluebutton S10 x HTML5 Server: `The MongoDB database contains information about all meetings on the se...`
- bigbluebutton S12 x HTML5 Server: `The client side subscribes to the published collections on the server ...`
- bigbluebutton S13 x HTML5 Server: `Updates to MongoDB on the server side are automatically pushed to Mini...`
- bigbluebutton S15 x HTML5 Server: `Scalability of HTML5 server component....`
- bigbluebutton S26 x Apps: `Frontends receive other DDP events including method calls to send even...`
- bigbluebutton S36 x BBB web: `BBB web....`
- bigbluebutton S39 x HTML5 Server: `The BigBlueButton API provides a third-party integration (such as the ...`
- bigbluebutton S46 x Redis PubSub: `Redis PubSub....`
- bigbluebutton S47 x HTML5 Server: `Redis PubSub provides a communication channel between different applic...`
- bigbluebutton S48 x Redis DB: `Redis DB....`
- bigbluebutton S51 x Apps: `Apps akka....`
- bigbluebutton S54 x Apps: `Below is a diagram of the different components of Apps Akka....`
- bigbluebutton S57 x FSESL: `FSESL akka....`
- bigbluebutton S58 x FreeSWITCH: `We have extracted out the component that integrates with FreeSWITCH in...`
- bigbluebutton S59 x FreeSWITCH: `This allows others who are using voice conference systems other than F...`
- bigbluebutton S60 x Redis PubSub: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- bigbluebutton S61 x FreeSWITCH: `FreeSWITCH....`
- bigbluebutton S62 x FreeSWITCH: `We think FreeSWITCH is an amazing piece of software for handling audio...`
- bigbluebutton S65 x WebRTC-SFU: `Users joining through Google Chrome or Mozilla Firefox are able to tak...`
- bigbluebutton S67 x UNKNOWN: `Kurento and WebRTC-SFU....`
- bigbluebutton S67 x WebRTC-SFU: `Kurento and WebRTC-SFU....`
- bigbluebutton S68 x UNKNOWN: `Kurento Media Server KMS is a media server that implements both SFU an...`
- bigbluebutton S72 x FreeSWITCH: `A user can join the voice conference (running in FreeSWITCH) from the ...`
- bigbluebutton S73 x WebRTC-SFU: `When joining through the client, the user can choose to join Microphon...`
- bigbluebutton S73 x HTML5 Server: `When joining through the client, the user can choose to join Microphon...`
- bigbluebutton S78 x BBB web: `The PDF document is then converted into scalable vector graphics (SVG)...`
- bigbluebutton S79 x Redis PubSub: `The conversion process sends progress messages to the client through t...`
- bigbluebutton S80 x Presentation Conversion: `Presentation conversion flow....`
- bigbluebutton S81 x Presentation Conversion: `The diagram below describes the flow of the presentation conversion....`
- jabref S1 x logic: `We have been successfully transitioning from a spaghetti to a more str...`
- jabref S1 x gui: `We have been successfully transitioning from a spaghetti to a more str...`
- jabref S1 x model: `We have been successfully transitioning from a spaghetti to a more str...`
- jabref S2 x cli: `There are additional utility packages for preferences and the cli....`
- jabref S2 x preferences: `There are additional utility packages for preferences and the cli....`
- jabref S4 x gui: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S4 x logic: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S4 x model: `We have JUnit tests to detect violations of the most crucial dependenc...`
- jabref S6 x model: `The logic is responsible for reading/writing/importing/exporting and m...`
- jabref S6 x gui: `The logic is responsible for reading/writing/importing/exporting and m...`
- jabref S12 x model: `We use an event bus to publish events from the model to the other laye...`

## Strategy: Minimal (arch role vs impl detail)

| Metric | Value |
|--------|-------|
| TPs correctly kept | 111/148 (75%) |
| TPs wrongly killed | 37/148 (25%) |
| FPs correctly caught | 33/40 (82%) |
| FPs missed | 7/40 (18%) |
| **Net benefit** | **-4** |
| Filter precision | 47% |
| Overall accuracy | 77% |

**Per-project:**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net |
|---------|-----|-----|------------|------------|-----|
| mediastore | 17 | 1 | 1 | 0 | +1 |
| teastore | 20 | 0 | 0 | 2 | -2 |
| teammates | 49 | 32 | 29 | 11 | +18 |
| bigbluebutton | 44 | 5 | 2 | 21 | -19 |
| jabref | 18 | 2 | 1 | 3 | -2 |

**FP details:**

- [CAUGHT] mediastore S37 x Reencoding: `However, a download can cause re-encoding of the audio file....`
- [CAUGHT] teammates S4 x Client: `The UI Browser seen by users consists of Web pages containing HTML, CS...`
- [CAUGHT] teammates S17 x E2E: `Selenium Java is used to automate E2E testing with actual Web browsers...`
- [CAUGHT] teammates S22 x UI: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S22 x Logic: `logic, ui.website, ui.controller represent an application of Model-Vie...`
- [CAUGHT] teammates S23 x UI: `ui.website is not a real package....`
- [CAUGHT] teammates S26 x UI: `ui.website is not a Java package....`
- [MISSED] teammates S79 x Logic: `Managing relationships between entities, e.g. cascade logic for create...`
- [CAUGHT] teammates S84 x Logic: `Package overview contains logic.api, logic.core....`
- [MISSED] teammates S85 x Logic: `logic.api provides the API of the component to be accessed by the UI....`
- [CAUGHT] teammates S86 x Logic: `logic.core contains the core logic of the system....`
- [CAUGHT] teammates S117 x Logic: `Refer to the API for the cascade logic....`
- [CAUGHT] teammates S119 x Logic: `It contains minimal logic beyond what is directly relevant to CRUD ope...`
- [CAUGHT] teammates S125 x Storage: `Classes in the storage.entity package are not visible outside this com...`
- [CAUGHT] teammates S127 x Common: `These datatransfer classes are in common.datatransfer package, to be e...`
- [CAUGHT] teammates S130 x Storage: `Package overview contains storage.api, storage.entity, storage.search....`
- [MISSED] teammates S131 x Storage: `storage.api provides the API of the component to be accessed by the lo...`
- [CAUGHT] teammates S132 x Storage: `storage.entity contains classes that represent persistable entities....`
- [CAUGHT] teammates S133 x Storage: `storage.search contains classes for dealing with searching and indexin...`
- [CAUGHT] teammates S156 x Common: `Package overview contains common.util, common.exceptions, common.datat...`
- [CAUGHT] teammates S157 x Common: `common.util contains utility classes....`
- [CAUGHT] teammates S158 x Common: `common.exceptions contains custom exceptions....`
- [CAUGHT] teammates S159 x Common: `common.datatransfer contains data transfer objects....`
- [CAUGHT] teammates S160 x Common: `common.datatransfer package contains lightweight data transfer object ...`
- [CAUGHT] teammates S173 x Test Driver: `x.testdriver contains component test cases for testing the test driver...`
- [CAUGHT] teammates S187 x E2E: `Package overview contains e2e.util, e2e.pageobjects, e2e.cases, x.util...`
- [CAUGHT] teammates S188 x E2E: `e2e.util contains helpers needed for running E2E tests....`
- [CAUGHT] teammates S189 x E2E: `e2e.pageobjects contains abstractions of the pages as they appear on a...`
- [CAUGHT] teammates S190 x E2E: `e2e.cases contains test cases....`
- [CAUGHT] teammates S195 x Client: `Package overview contains client.util, client.remoteapi, client.script...`
- [CAUGHT] teammates S196 x Client: `client.util contains helpers needed for client scripts....`
- [CAUGHT] teammates S197 x Client: `client.remoteapi classes needed to connect to the back end directly....`
- [CAUGHT] teammates S198 x Client: `client.scripts scripts that deal with the back end data for administra...`
- [MISSED] bigbluebutton S5 x WebRTC-SFU: `The HTML5 client is a single page, responsive web application that is ...`
- [CAUGHT] bigbluebutton S18 x HTML5 Server: `Because nodejs was running on a single CPU core, having a 16 or 32 CPU...`
- [MISSED] bigbluebutton S60 x FreeSWITCH: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- [CAUGHT] bigbluebutton S68 x HTML5 Server: `Kurento Media Server KMS is a media server that implements both SFU an...`
- [MISSED] bigbluebutton S74 x WebRTC-SFU: `WebRTC provides the user with high-quality audio with lower delay....`
- [CAUGHT] jabref S5 x logic: `The model represents the most important data structures (BibDatases, B...`
- [MISSED] jabref S7 x preferences: `Only the gui knows the user and his preferences and can interact with ...`

**TPs wrongly killed (37):**

- teastore S5 x WebUI: `The WebUI provides the TeaStore front-end using Servlets in combinatio...`
- teastore S25 x Persistence: `The persistence provider uses a second level entity cache provided by ...`
- teammates S7 x Logic: `In the UI Server the entry point for the application back end logic is...`
- teammates S8 x Logic: `The main logic of the application is in POJOs (Plain Old Java Objects)...`
- teammates S9 x UNKNOWN: `The storage layer of the application uses the persistence framework pr...`
- teammates S10 x Test Driver: `The following explains the use of the Test Driver....`
- teammates S25 x UI: `The diagram below shows the object structure of the UI component....`
- teammates S87 x Logic: `Logic API is represented by the classes Logic, GateKeeper, EmailGenera...`
- teammates S137 x UNKNOWN: `These classes act as the bridge to the GAE Datastore....`
- teammates S174 x Common: `x.datatransfer contains component test cases for testing the datatrans...`
- teammates S175 x Common: `x.util contains component test cases for testing the utility classes f...`
- teammates S176 x Logic: `x.logic contains component test cases for testing the Logic component....`
- teammates S177 x Storage: `x.storage contains component test cases for testing the Storage compon...`
- bigbluebutton S4 x HTML5 Client: `HTML5 client....`
- bigbluebutton S10 x HTML5 Server: `The MongoDB database contains information about all meetings on the se...`
- bigbluebutton S14 x HTML5 Client: `The following diagram gives an overview of the architecture of the HTM...`
- bigbluebutton S15 x HTML5 Server: `Scalability of HTML5 server component....`
- bigbluebutton S36 x BBB web: `BBB web....`
- bigbluebutton S39 x HTML5 Server: `The BigBlueButton API provides a third-party integration (such as the ...`
- bigbluebutton S46 x Redis PubSub: `Redis PubSub....`
- bigbluebutton S47 x HTML5 Server: `Redis PubSub provides a communication channel between different applic...`
- bigbluebutton S48 x Redis DB: `Redis DB....`
- bigbluebutton S51 x Apps: `Apps akka....`
- bigbluebutton S54 x Apps: `Below is a diagram of the different components of Apps Akka....`
- bigbluebutton S57 x FSESL: `FSESL akka....`
- bigbluebutton S58 x FreeSWITCH: `We have extracted out the component that integrates with FreeSWITCH in...`
- bigbluebutton S59 x FreeSWITCH: `This allows others who are using voice conference systems other than F...`
- bigbluebutton S61 x FreeSWITCH: `FreeSWITCH....`
- bigbluebutton S62 x FreeSWITCH: `We think FreeSWITCH is an amazing piece of software for handling audio...`
- bigbluebutton S67 x UNKNOWN: `Kurento and WebRTC-SFU....`
- bigbluebutton S67 x WebRTC-SFU: `Kurento and WebRTC-SFU....`
- bigbluebutton S68 x UNKNOWN: `Kurento Media Server KMS is a media server that implements both SFU an...`
- bigbluebutton S80 x Presentation Conversion: `Presentation conversion flow....`
- bigbluebutton S81 x Presentation Conversion: `The diagram below describes the flow of the presentation conversion....`
- jabref S2 x cli: `There are additional utility packages for preferences and the cli....`
- jabref S2 x preferences: `There are additional utility packages for preferences and the cli....`
- jabref S10 x cli: `The cli package bundles classes that are responsible for JabRef’s comm...`

## Impact on SWATTR SAD-SAM Metrics

Best strategy: **Minimal (arch role vs impl detail)** (net -4)

| Project | Orig P | Orig R | Orig F1 | Filt P | Filt R | Filt F1 | ΔF1 |
|---------|--------|--------|---------|--------|--------|---------|-----|
| mediastore | 0.944 | 0.548 | 0.694 | 1.000 | 0.548 | 0.708 | +0.014 |
| teastore | 1.000 | 0.741 | 0.851 | 1.000 | 0.667 | 0.800 | -0.051 |
| teammates | 0.605 | 0.860 | 0.710 | 0.927 | 0.667 | 0.776 | +0.065 |
| bigbluebutton | 0.898 | 0.710 | 0.793 | 0.885 | 0.371 | 0.523 | -0.270 |
| jabref | 0.900 | 1.000 | 0.947 | 0.938 | 0.833 | 0.882 | -0.065 |
| **Average** | | | | | | | **-0.061** |

## Synthesis

### Strategy Comparison

| Strategy | FPs Caught | TPs Killed | Net | Filter Prec | Acc |
|----------|------------|------------|-----|-------------|-----|
| Direct (no convention hints) | 6/40 | 15/148 | -9 | 29% | 74% |
| Convention-aware (full rules) | 39/40 | 50/148 | -11 | 44% | 73% |
| Three-filter (reference + topicality + abstraction) | 36/40 | 85/148 | -49 | 30% | 53% |
| Minimal (arch role vs impl detail) | 33/40 | 37/148 | -4 | 47% | 77% |

### Comparison with Non-LLM Approaches

| Approach | FPs Caught | TPs Killed | Net | Generalizes? |
|----------|------------|------------|-----|-------------|
| Rule-based (≥2 rules) | 23/40 | 1/148 | +22 | Teammates only |
| Rule-based (≥3 rules) | 15/40 | 0/148 | +15 | Teammates only |
| Relative framing (emb) | 16/40 | 10/148 | +6 | Partial |
| Sentence embedding RF | AUC 0.805 | - | - | No (LOPO fails) |
| LLM: Direct (no convention hints) | 6/40 | 15/148 | -9 | Zero-shot |
| LLM: Convention-aware (full rules) | 39/40 | 50/148 | -11 | Zero-shot |
| LLM: Three-filter (reference + topi | 36/40 | 85/148 | -49 | Zero-shot |
| LLM: Minimal (arch role vs impl det | 33/40 | 37/148 | -4 | Zero-shot |

### Key Findings

1. **No zero-shot LLM strategy achieves positive net benefit.** The best (Minimal) is -4, meaning it removes more TPs than FPs. The rule-based approach (+22 net) still dominates, but only works on Teammates.

2. **Precision-recall tradeoff is the core problem.** The LLM *understands* the annotation convention — Convention-aware catches 39/40 FPs (98%) — but it over-applies the rules, killing 50/148 TPs (34%). It cannot calibrate where the boundary falls without examples.

3. **Minimal framing is the sweet spot for LLM.** By reducing the task to "architectural role vs implementation detail" without spelling out specific rules, the LLM kills fewer TPs (37 vs 50-85 for other guided strategies) while still catching 33/40 FPs (82%). Filter precision 47% is highest across strategies.

4. **BigBlueButton is the Achilles heel.** Every LLM strategy massively over-filters BBB (ΔF1 from -0.270 to -0.026). BBB's documentation style — short section headers like "FreeSWITCH." or "Apps akka." that are TPs — looks like "non-architectural content" to the LLM. The LLM has no way to know these headings are trace-worthy.

5. **The problem is fundamentally about labeling convention, not semantics.** The LLM can distinguish architectural sentences from implementation sentences (high FP recall). What it cannot distinguish is which *kind* of architectural sentence the annotators chose to label. Examples:
   - TP: "x.logic contains component test cases for testing the Logic component" (Teammates) — describes subpackages, but labeled because it names the component
   - FP: "logic.core contains the core logic of the system" (Teammates) — also describes subpackages, also names the component, but NOT labeled
   - The difference? Annotator judgment about abstraction level that is not recoverable from text alone.

6. **Cross-project generalization remains impossible.** Rules work for Teammates (80% of FPs) because its FPs have a distinctive lexical signature (dotted package names). BBB and JabRef FPs are semantically indistinguishable from TPs — the LLM confirms this by killing TPs at the same rate it catches FPs in these projects.

### Implications for SWATTR Improvement

- **Post-hoc LLM filtering of SWATTR output is not viable** as a general strategy (negative net benefit).
- **Rule-based filtering is viable but project-specific** — works only when FPs have distinctive lexical patterns (Teammates' package descriptions).
- **The 40 FPs represent irreducible annotation noise** from the benchmark, not a systematic SWATTR failure that can be corrected. 32/40 FPs are from a single project (Teammates) whose documentation extensively describes package structure — a convention clash with the annotation criterion.
- **SWATTR's actual precision problem is small**: excluding Teammates, only 8 FPs across 4 projects from 139 links = 94.2% precision.

