# SWATTR TP vs FP: Few-Shot LLM Classification with Abstract Examples

Using Claude Sonnet via CLI with abstract reasoning guide (no project-specific examples).

**Data**: 148 TPs + 40 FPs = 188 SWATTR links

## Strategy: Abstract reasoning guide (placeholder examples)

| Metric | Value |
|--------|-------|
| TPs correctly kept | 146/148 (99%) |
| TPs wrongly killed | 2/148 (1%) |
| FPs correctly caught | 38/40 (95%) |
| FPs missed | 2/40 (5%) |
| **Net benefit** | **+36** |
| Filter precision | 95% |
| Overall accuracy | 98% |

**Per-project:**

| Project | TPs | FPs | FPs Caught | TPs Killed | Net |
|---------|-----|-----|------------|------------|-----|
| mediastore | 17 | 1 | 1 | 0 | +1 |
| teastore | 20 | 0 | 0 | 0 | +0 |
| teammates | 49 | 32 | 32 | 0 | +32 |
| bigbluebutton | 44 | 5 | 3 | 2 | +1 |
| jabref | 18 | 2 | 2 | 0 | +2 |

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
- [MISSED] bigbluebutton S18 x HTML5 Server: `Because nodejs was running on a single CPU core, having a 16 or 32 CPU...`
- [MISSED] bigbluebutton S60 x FreeSWITCH: `Communication between apps and FreeSWITCH Event Socket Layer (fsels) u...`
- [CAUGHT] bigbluebutton S68 x HTML5 Server: `Kurento Media Server KMS is a media server that implements both SFU an...`
- [CAUGHT] bigbluebutton S74 x WebRTC-SFU: `WebRTC provides the user with high-quality audio with lower delay....`
- [CAUGHT] jabref S5 x logic: `The model represents the most important data structures (BibDatases, B...`
- [CAUGHT] jabref S7 x preferences: `Only the gui knows the user and his preferences and can interact with ...`

**TPs wrongly killed (2):**

- bigbluebutton S39 x HTML5 Server: `The BigBlueButton API provides a third-party integration (such as the ...`
- bigbluebutton S47 x HTML5 Server: `Redis PubSub provides a communication channel between different applic...`

## Impact on SWATTR SAD-SAM Metrics

| Project | Orig P | Orig R | Orig F1 | Filt P | Filt R | Filt F1 | ΔF1 |
|---------|--------|--------|---------|--------|--------|---------|-----|
| mediastore | 0.944 | 0.548 | 0.694 | 1.000 | 0.548 | 0.708 | +0.014 |
| teastore | 1.000 | 0.741 | 0.851 | 1.000 | 0.741 | 0.851 | +0.000 |
| teammates | 0.605 | 0.860 | 0.710 | 1.000 | 0.860 | 0.925 | +0.214 |
| bigbluebutton | 0.898 | 0.710 | 0.793 | 0.955 | 0.677 | 0.792 | -0.000 |
| jabref | 0.900 | 1.000 | 0.947 | 1.000 | 1.000 | 1.000 | +0.053 |
| **Average** | | | | | | | **+0.056** |

## Comparison with Previous Approaches

| Approach | FPs Caught | TPs Killed | Net | Avg ΔF1 |
|----------|------------|------------|-----|---------|
| Rule-based (≥2 rules) | 23/40 | 1/148 | +22 | +0.026 |
| Zero-shot: Direct | 6/40 | 15/148 | -9 | -0.049 |
| Zero-shot: Convention-aware | 39/40 | 50/148 | -11 | -0.049 |
| Zero-shot: Minimal | 33/40 | 37/148 | -4 | -0.061 |
| **Few-shot: Abstract examples** | **38/40** | **2/148** | **+36** | **+0.056** |

