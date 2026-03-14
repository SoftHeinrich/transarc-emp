#!/usr/bin/env python3
"""
Build annotated dataset: label every sentence across all 5 projects as
  arch       = architectural responsibility (component role, behavior, interaction)
  pkg_code   = package/code structure description (internal organization, sub-packages)
  impl       = implementation detail (algorithm, data format, technology, API spec)
  meta       = document meta (diagram reference, section header, navigation)
  other      = none of the above (generic, user flow, requirement)

Gold standard cross-reference is included but does NOT drive the label:
a sentence can be gold-traced yet labeled 'impl' or 'meta'.
"""

import csv
import os
import json
import xml.etree.ElementTree as ET

BENCHMARK = "/mnt/hostshare/ardoco-home/ardoco/core/tests-base/src/main/resources/benchmark"
RESULTS = "/mnt/hostshare/ardoco-home/transarc-emp/results"
OUT_DIR = "/mnt/hostshare/ardoco-home/transarc-emp/sentence_classification"

PROJECTS = {
    "mediastore": {
        "text": "text_2016/mediastore.txt",
        "model": "model_2016/pcm/ms.repository",
        "gold": "goldstandards/goldstandard_sad_2016-sam_2016.csv",
    },
    "teastore": {
        "text": "text_2020/teastore.txt",
        "model": "model_2020/pcm/teastore.repository",
        "gold": "goldstandards/goldstandard_sad_2020-sam_2020.csv",
    },
    "teammates": {
        "text": "text_2021/teammates.txt",
        "model": "model_2021/pcm/teammates.repository",
        "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv",
    },
    "jabref": {
        "text": "text_2021/jabref.txt",
        "model": "model_2021/pcm/jabref.repository",
        "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv",
    },
    "bigbluebutton": {
        "text": "text_2021/bigbluebutton.txt",
        "model": "model_2021/pcm/bbb.repository",
        "gold": "goldstandards/goldstandard_sad_2021-sam_2021.csv",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANUAL ANNOTATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Each dict maps sentence_number → label.
# Sentences not listed default to 'other'.
#
# Labels:
#   arch     = describes what a component IS, DOES, or how it INTERACTS
#   pkg_code = describes internal package/file/code organization
#   impl     = implementation detail (algorithm, technology, config, API spec)
#   meta     = document navigation ("diagram below", "the following explains")
#   other    = generic statement, user flow, requirement, not component-specific

ANNOTATIONS = {}

# ── MEDIASTORE (37 sentences) ──────────────────────────────────────────
# Purely architectural descriptions, no package structure discussion.
ANNOTATIONS["mediastore"] = {
    1: "arch",    # Facade component delivers websites, session management
    2: "other",   # Requirement: registration and log-in
    3: "arch",    # Facade delivers registration/login pages
    4: "other",   # User flow: after login, forwarded to file list
    5: "other",   # Generic: "main functionality provided by other components"
    6: "arch",    # Facade: browse, download, upload
    7: "arch",    # MediaManagement component: business logic
    8: "arch",    # MediaManagement coordinates communication
    9: "arch",    # MediaManagement fetches audio files (pronoun: "it")
    10: "other",  # Generic: registration and authentication needed
    11: "arch",   # UserManagement answers registration/authentication requests
    12: "arch",   # UserDBAdapter queries the database
    13: "arch",   # UserManagement hashes passwords
    14: "other",  # Requirement: downloaded files are watermarked
    15: "other",  # Generic: files are first re-encoded
    16: "arch",   # TagWatermarking component watermarks files
    17: "arch",   # MediaManagement forwards files from TagWatermarking
    18: "other",  # Generic: audio file linked to user ID
    19: "arch",   # Packaging component archives files
    20: "arch",   # ReEncoder converts bit rates
    21: "other",  # Generic: can reduce file sizes
    22: "other",  # Generic: persistence tier description
    23: "arch",   # Database component represents actual DB
    24: "arch",   # Database stores user info and meta-data (pronoun: "it")
    25: "arch",   # AudioAccess creates query sent to Database
    26: "arch",   # MediaAccess stores audio at predefined location
    27: "arch",   # MediaAccess encapsulates DB access for meta-data
    28: "arch",   # MediaAccess fetches list of audio files (pronoun: "it")
    29: "arch",   # UserDBAdapter encapsulates DB access for user data
    30: "arch",   # UserDBAdapter creates a query
    31: "arch",   # Database executes the query
    32: "arch",   # Database stores password hashes
    33: "arch",   # DataStorage decoupled from database
    34: "arch",   # MediaAccess fetches meta-data from Database
    35: "arch",   # File retrieved from DataStorage
    36: "arch",   # File stored in DataStorage
    37: "other",  # Generic: download can cause re-encoding
}

# ── TEASTORE (43 sentences) ────────────────────────────────────────────
# Architectural with some implementation details. No package descriptions.
ANNOTATIONS["teastore"] = {
    1: "arch",    # TeaStore consists of 5 services and registry
    2: "arch",    # WebUI retrieves images from Image Provider
    3: "arch",    # Users authenticated by Auth service
    4: "arch",    # Data from PersistenceProvider, recommendations from Recommender
    5: "arch",    # WebUI provides front-end using Servlets/JSP
    6: "arch",    # WebUI logic for cookies (pronoun: "it")
    7: "arch",    # WebUI images from Image Provider
    8: "arch",    # UI provides status page (pronoun: "the UI")
    9: "impl",    # Status view lists instance count and hosts
    10: "arch",   # Image Provider delivers images to WebUI
    11: "arch",   # Image Provider matches product ID/name (pronoun: "it")
    12: "arch",   # Image Provider: not-found image behavior
    13: "impl",   # Scaling logic for wrong-size images
    14: "impl",   # Scaled image stored for later use
    15: "impl",   # Image loading flow
    16: "impl",   # In-memory cache with LFU strategy
    17: "impl",   # Cache lookup before loading from drive
    18: "arch",   # Auth service handles user/session authentication
    19: "impl",   # BCrypt for password hashing
    20: "impl",   # SessionBlob salted/hashed with SHA512
    21: "impl",   # SessionBlob validation flow
    22: "arch",   # Persistence service provides data access
    23: "impl",   # EclipseLink JPA ORM mapper
    24: "arch",   # Persistence CRUD endpoints
    25: "impl",   # Second level entity cache
    26: "arch",   # Persistence acts as caching layer (pronoun: "it")
    27: "arch",   # Recommender generates recommendations
    28: "arch",   # Recommender trained on orders (pronoun: "it")
    29: "impl",   # Recommendation algorithm details
    30: "impl",   # Item rating based on purchases
    31: "impl",   # Fallback algorithm for unknown users
    32: "impl",   # Slope One algorithm
    33: "impl",   # Two versions of algorithm
    34: "impl",   # CPU-intensive vs memory-intensive
    35: "impl",   # Order-based nearest-neighbor
    36: "impl",   # Recommendation time complexity
    37: "arch",   # Registry provides service instance info
    38: "arch",   # Services register at registry on startup
    39: "impl",   # Heartbeat re-registration
    40: "impl",   # 10s timeout for missing heartbeat
    41: "impl",   # Single registry per TeaStore
    42: "other",  # TeaStore is a test application
    43: "impl",   # Single registry enables easy configuration
}

# ── TEAMMATES (198 sentences) ──────────────────────────────────────────
# Large doc with architectural descriptions, package structure, implementation details.
_tm = {}
# Architecture overview (S1-S20)
_tm[1] = "arch"    # Architecture contains components
_tm[2] = "arch"    # TEAMMATES is a Web application on GAE
_tm[3] = "meta"    # "Given above is an overview"
_tm[4] = "arch"    # UI Browser: HTML, CSS, JavaScript, client-side
_tm[5] = "arch"    # UI is single HTML page by Angular
_tm[6] = "impl"    # Initial request over HTTP, AJAX
_tm[7] = "arch"    # UI Server: REST-ful controller entry point
_tm[8] = "arch"    # Logic: main logic in POJOs
_tm[9] = "arch"    # Storage: uses GAE Datastore, NoSQL
_tm[10] = "meta"   # "The following explains the use of Test Driver"
_tm[11] = "other"  # Regression testing usage
_tm[12] = "impl"   # JSON format for test data
_tm[13] = "impl"   # TestNG for Java, Jest for JS
_tm[14] = "impl"   # HttpUnit for simulated web server
_tm[15] = "arch"   # E2E component interacts with browsers
_tm[16] = "arch"   # E2E primary function: tests
_tm[17] = "impl"   # Selenium Java for E2E testing
_tm[18] = "arch"   # Client connects to back end directly
_tm[19] = "arch"   # Client for admin purposes (pronoun: "it")
_tm[20] = "arch"   # Common: utility code, data transfer objects
# Package/code discussion (S21-S28)
_tm[21] = "meta"   # "diagram below shows how code is organized into packages"
_tm[22] = "arch"   # logic, ui.website, ui.controller = MVC pattern
_tm[23] = "pkg_code"  # "ui.website is not a real package"
_tm[24] = "pkg_code"  # "It is a conceptual package representing the front-end"
_tm[25] = "meta"   # "diagram below shows the object structure"
_tm[26] = "pkg_code"  # "ui.website is not a Java package"
_tm[27] = "impl"   # Angular, HTML, SCSS, TypeScript
_tm[28] = "impl"   # Framework builds to HTML, CSS, JavaScript
# UI request flow (S29-S76)
_tm[29] = "arch"   # UI is first stop for 99% of requests
_tm[30] = "meta"   # "Such a request will go through the following steps"
_tm[31] = "impl"   # Request received by GAE server
_tm[32] = "impl"   # Custom filters in web.xml
_tm[33] = "impl"   # Request forwarded to Servlet in web.xml
_tm[34] = "other"  # Two general types of requests
_tm[35] = "other"  # User-invoked vs automated requests
_tm[36] = "other"  # User-invoked requests = from browser
_tm[37] = "meta"   # "Request will be processed as in the image"
_tm[38] = "meta"   # "Initial request processed as follows"
_tm[39] = "impl"   # Request forwarded to WebPageServlet
_tm[40] = "impl"   # WebPageServlet returns index.html
_tm[41] = "impl"   # Browser renders page, AJAX
_tm[42] = "meta"   # "Subsequent AJAX requests processed as follows"
_tm[43] = "impl"   # Request forwarded to WebApiServlet
_tm[44] = "impl"   # WebApiServlet + ActionFactory
_tm[45] = "impl"   # WebApiServlet executes action
_tm[46] = "impl"   # Action checks access rights
_tm[47] = "arch"   # Action interacts with Logic component
_tm[48] = "impl"   # Action packages result into ActionResult
_tm[49] = "impl"   # JsonResult, FileDownloadResult, ImageResult
_tm[50] = "impl"   # WebApiServlet sends result back
_tm[51] = "impl"   # Static asset files served directly
_tm[52] = "impl"   # Web API protected by access control
_tm[53] = "impl"   # Origin check, auth check
_tm[54] = "impl"   # Origin check mitigates CSRF
_tm[55] = "impl"   # Auth check for privileges
_tm[56] = "impl"   # Special keys for bypass
_tm[57] = "impl"   # Keys known only to administrator
_tm[58] = "impl"   # Automated requests from GAE server
_tm[59] = "meta"   # "This type of request processed as follows"
_tm[60] = "impl"   # Source checked for admin privilege
_tm[61] = "impl"   # Non-admin gets 403
_tm[62] = "impl"   # GAE requests have privilege
_tm[63] = "impl"   # Admins can manually invoke
_tm[64] = "impl"   # Useful for testing
_tm[65] = "impl"   # Request forwarded to AutomatedServlet
_tm[66] = "impl"   # AutomatedServlet + ActionFactory
_tm[67] = "impl"   # AutomatedServlet executes action
_tm[68] = "arch"   # AutomatedAction interacts with Logic component
_tm[69] = "impl"   # GAE sends through cron jobs or task queue
_tm[70] = "impl"   # Cron jobs and task queue workers
_tm[71] = "impl"   # Cron jobs scheduling
_tm[72] = "impl"   # Configured in cron.xml
_tm[73] = "impl"   # Task queue workers
_tm[74] = "impl"   # Task queue for long-running tasks
_tm[75] = "impl"   # Configured in queue.xml
_tm[76] = "impl"   # Template Method pattern
# Logic component (S77-S97)
_tm[77] = "arch"   # Logic handles business logic
_tm[78] = "meta"   # "In particular, it is responsible for the following"
_tm[79] = "arch"   # Managing relationships, cascade logic
_tm[80] = "arch"   # Managing transactions, atomicity
_tm[81] = "arch"   # Sanitizing input from UI
_tm[82] = "arch"   # Access control rights mechanism
_tm[83] = "arch"   # Connecting to GAE APIs, task queue, email
_tm[84] = "pkg_code"  # "Package overview contains logic.api, logic.core"
_tm[85] = "pkg_code"  # "logic.api provides the API to be accessed by UI"
_tm[86] = "pkg_code"  # "logic.core contains the core logic"
_tm[87] = "arch"   # Logic API: Logic, GateKeeper, EmailGenerator, EmailSender, TaskQueuer
_tm[88] = "arch"   # Logic is a Facade class connecting to Storage
_tm[89] = "arch"   # GateKeeper checks access rights
_tm[90] = "arch"   # EmailGenerator generates emails
_tm[91] = "arch"   # EmailSender sends email with provider
_tm[92] = "impl"   # Connects to email provider via Service class
_tm[93] = "arch"   # TaskQueuer adds tasks to queue
_tm[94] = "impl"   # Connects to GAE's task queue API
_tm[95] = "meta"   # "To access control the following information..."
_tm[96] = "impl"   # Component provides access control methods but not self-controlled
_tm[97] = "arch"   # UI expected to check access via GateKeeper before Logic
# Logic API details (S98-S117)
_tm[98] = "meta"    # "To API for creating entities the following..."
_tm[99] = "impl"    # Null parameters → assertion failure
_tm[100] = "impl"   # Invalid params → InvalidParametersException
_tm[101] = "arch"   # EntityAlreadyExistsException from Storage level
_tm[102] = "meta"   # "To API for retrieving entities..."
_tm[103] = "impl"   # Null params → assertion failure
_tm[104] = "impl"   # Not found → return null
_tm[105] = "impl"   # Read ops check existence
_tm[106] = "meta"   # "To API for updating entities..."
_tm[107] = "impl"   # UpdateOptions inside Attributes
_tm[108] = "impl"   # UpdateOptions specify identification and update
_tm[109] = "impl"   # Not found → EntityDoesNotExistException
_tm[110] = "impl"   # Invalid → InvalidParametersException
_tm[111] = "meta"   # "To API for deleting entities..."
_tm[112] = "meta"   # "The following explains FailDeleteSilentlyPolicy"
_tm[113] = "impl"   # Delete doesn't throw if not exists
_tm[114] = "impl"   # Not exists = as good as deleted
_tm[115] = "meta"   # "The following explains Cascade policy"
_tm[116] = "impl"   # Cascade delete on parent
_tm[117] = "impl"   # "Refer to API for cascade logic"
# Storage component (S118-S154)
_tm[118] = "arch"   # Storage performs CRUD individually
_tm[119] = "arch"   # Storage: minimal logic beyond CRUD
_tm[120] = "meta"   # "In particular, it is responsible for the following"
_tm[121] = "arch"   # Validating data before create/update
_tm[122] = "arch"   # Hiding complexities of datastore from Logic
_tm[123] = "arch"   # All GQL queries contained in Storage
_tm[124] = "arch"   # Hiding persistable objects
_tm[125] = "pkg_code"  # "Classes in storage.entity package not visible outside"
_tm[126] = "impl"   # Attributes data transfer object returned
_tm[127] = "impl"   # Datatransfer classes in common.datatransfer
_tm[128] = "arch"   # Storage does not do cascade delete/create
_tm[129] = "arch"   # Cascade logic handled by Logic component
_tm[130] = "pkg_code"  # "Package overview contains storage.api, storage.entity, storage.search"
_tm[131] = "pkg_code"  # "storage.api provides the API to be accessed by logic"
_tm[132] = "pkg_code"  # "storage.entity contains persistable entity classes"
_tm[133] = "pkg_code"  # "storage.search contains searching and indexing classes"
_tm[134] = "impl"   # Navigability in reverse direction
_tm[135] = "impl"   # Flexible data schema
_tm[136] = "impl"   # Represented by Db classes
_tm[137] = "arch"   # Db classes bridge to GAE Datastore
_tm[138] = "arch"   # Add/Delete wait until persisted in datastore
_tm[139] = "impl"   # Not enough for eventual consistency
_tm[140] = "impl"   # Expected to avoid test failures
_tm[141] = "arch"   # Eventual consistency in Google's distributed datastore
_tm[142] = "impl"   # Data in inconsistent state briefly
_tm[143] = "impl"   # Example: deleted object may still exist
_tm[144] = "impl"   # Transaction control minimized due to GAE
_tm[145] = "meta"   # "To API for creating..."
_tm[146] = "impl"   # Already exists → exception
_tm[147] = "impl"   # Invalid data → exception
_tm[148] = "meta"   # "To API for retrieving..."
_tm[149] = "impl"   # Not exists → null
_tm[150] = "meta"   # "To API for updating..."
_tm[151] = "impl"   # Not exists → exception
_tm[152] = "impl"   # Invalid → exception
_tm[153] = "meta"   # "To API for deleting..."
_tm[154] = "impl"   # Not exists → silent
# Common component (S155-S167)
_tm[155] = "arch"   # Common contains common utilities
_tm[156] = "pkg_code"  # "Package overview contains common.util, common.exceptions, common.datatransfer"
_tm[157] = "pkg_code"  # "common.util contains utility classes"
_tm[158] = "pkg_code"  # "common.exceptions contains custom exceptions"
_tm[159] = "pkg_code"  # "common.datatransfer contains data transfer objects"
_tm[160] = "pkg_code"  # "common.datatransfer package contains lightweight DTO classes"
_tm[161] = "impl"   # Combined for structured data transfer
_tm[162] = "meta"   # "Given below are three examples"
_tm[163] = "arch"   # Test Driver uses DataBundle to persist
_tm[164] = "other"  # Data structure example: course
_tm[165] = "other"  # Data structure example: feedback session
_tm[166] = "impl"   # Methodless classes = data structures
_tm[167] = "impl"   # Public variables for data
# Test Driver component (S168-S184)
_tm[168] = "arch"   # "This component automates the testing of TEAMMATES"
_tm[169] = "pkg_code"  # "Package overview contains test.driver, test.cases and subpackages"
_tm[170] = "pkg_code"  # "test.driver contains infrastructure and helpers"
_tm[171] = "pkg_code"  # "test.cases contains test cases"
_tm[172] = "pkg_code"  # "Sub-packages contains x.testdriver, x.datatransfer..."
_tm[173] = "pkg_code"  # "x.testdriver contains test cases for test driver"
_tm[174] = "pkg_code"  # "x.datatransfer contains test cases for datatransfer from Common"
_tm[175] = "pkg_code"  # "x.util contains test cases for utility classes from Common"
_tm[176] = "pkg_code"  # "x.logic contains test cases for Logic"
_tm[177] = "pkg_code"  # "x.storage contains test cases for Storage"
_tm[178] = "pkg_code"  # "x.search contains test cases for searching"
_tm[179] = "pkg_code"  # "x.webapi contains system test cases for user-invoked actions"
_tm[180] = "pkg_code"  # "x.automated contains system test cases for automated actions"
_tm[181] = "other"  # Component tests: unit vs integration
_tm[182] = "impl"   # Front-end tested with Jest
_tm[183] = "impl"   # Tests in x.spec.ts files
_tm[184] = "meta"   # "This is how TEAMMATES testing maps to standard types"
# E2E component (S185-S193)
_tm[185] = "arch"   # E2E has no knowledge of internal workings
_tm[186] = "arch"   # E2E primary function: E2E tests and L&P tests
_tm[187] = "pkg_code"  # "Package overview contains e2e.util, e2e.pageobjects..."
_tm[188] = "pkg_code"  # "e2e.util contains helpers for E2E tests"
_tm[189] = "pkg_code"  # "e2e.pageobjects contains page abstractions"
_tm[190] = "pkg_code"  # "e2e.cases contains test cases"
_tm[191] = "pkg_code"  # "x.util contains test cases for test helpers"
_tm[192] = "pkg_code"  # "x.e2e contains system test cases"
_tm[193] = "pkg_code"  # "x.lnp contains L&P tests"
# Client component (S194-S198)
_tm[194] = "arch"   # Client: scripts for admin purposes
_tm[195] = "pkg_code"  # "Package overview contains client.util, client.remoteapi, client.scripts"
_tm[196] = "pkg_code"  # "client.util contains helpers for client scripts"
_tm[197] = "pkg_code"  # "client.remoteapi classes needed to connect to back end"
_tm[198] = "pkg_code"  # "client.scripts scripts for admin purposes"
ANNOTATIONS["teammates"] = _tm

# ── JABREF (13 sentences) ─────────────────────────────────────────────
# Concise architecture description. No package/code structure details.
ANNOTATIONS["jabref"] = {
    1: "arch",    # Structured architecture: model, logic, gui
    2: "arch",    # Utility packages for preferences and cli
    3: "arch",    # Dependencies directed towards center
    4: "impl",    # JUnit tests detect dependency violations
    5: "arch",    # Model: data structures with little logic
    6: "arch",    # Logic: reading/writing/manipulating model
    7: "arch",    # GUI: knows user, preferences, interaction
    8: "arch",    # Packages formed by responsibility (vertical structuring)
    9: "arch",    # Model no deps; logic depends only on model
    10: "arch",   # cli package: command line interface
    11: "arch",   # preferences: user-customizable info
    12: "arch",   # Event bus publishes events from model to other layers
    13: "arch",   # Keep architecture, react to core changes
}

# ── BIGBLUEBUTTON (87 sentences) ──────────────────────────────────────
_bbb = {}
_bbb[1] = "meta"    # "High-level architecture."
_bbb[2] = "meta"    # "diagram provides high-level view"
_bbb[3] = "meta"    # "We'll break down each component"
_bbb[4] = "meta"    # "HTML5 client." (section header)
_bbb[5] = "arch"    # HTML5 client: React.js, WebRTC
_bbb[6] = "arch"    # HTML5 client connects to BBB server
_bbb[7] = "arch"    # Connections handled by nginx
_bbb[8] = "arch"    # HTML5 server sits behind nginx
_bbb[9] = "arch"    # HTML5 server: Meteor.js, MongoDB
_bbb[10] = "arch"   # MongoDB: meeting info, client state
_bbb[11] = "arch"   # Client aware of own meeting state
_bbb[12] = "arch"   # Client subscribes to server collections
_bbb[13] = "arch"   # MongoDB pushes to MiniMongo on client
_bbb[14] = "meta"   # "diagram gives overview of architecture"
_bbb[15] = "meta"   # "Scalability of HTML5 server component."
_bbb[16] = "impl"   # BBB 2.2 single nodejs process
_bbb[17] = "impl"   # Process bottleneck at 100% CPU
_bbb[18] = "impl"   # 16/32 CPU core didn't help scalability
_bbb[19] = "arch"   # BBB 2.3: multiple nodejs processes
_bbb[20] = "arch"   # bbb-html5 uses multiple CPU cores
_bbb[21] = "impl"   # 2 frontend + 2 backend processes, configurable
_bbb[22] = "impl"   # Restart required for config changes
_bbb[23] = "meta"   # "Breakdown of functionality between front-end and back-end"
_bbb[24] = "impl"   # Frontends: ValidateAuthTokenResp
_bbb[25] = "impl"   # Frontends: subscriptions and publishers
_bbb[26] = "impl"   # Frontends: DDP events, method calls to akka-apps
_bbb[27] = "impl"   # Frontends: Streamer redis events
_bbb[28] = "impl"   # Frontends: MeetingStarted/Ended events
_bbb[29] = "impl"   # Backends: non-streamer events
_bbb[30] = "arch"   # bbb-web splits load round-robin with instanceId
_bbb[31] = "impl"   # Backends process redis for matching instanceId
_bbb[32] = "impl"   # ValidateAuthTokenResp also to backends (dev envs)
_bbb[33] = "impl"   # bbb-conf commands
_bbb[34] = "impl"   # Configuration values, helper functions
_bbb[35] = "meta"   # "See Automatically apply configuration changes"
_bbb[36] = "meta"   # "BBB web." (section header)
_bbb[37] = "arch"   # BBB web: Java-based, Scala
_bbb[38] = "arch"   # Implements BBB API, holds meeting state
_bbb[39] = "arch"   # BBB API for third-party integration
_bbb[40] = "other"  # Every access through front-end portal
_bbb[41] = "other"  # Moodle, Wordpress, Canvas integrations
_bbb[42] = "other"  # Greenlight front-end
_bbb[43] = "other"  # LMS usage
_bbb[44] = "other"  # Simple API demos
_bbb[45] = "other"  # All use API under the hood
_bbb[46] = "meta"   # "Redis PubSub." (section header)
_bbb[47] = "arch"   # Redis PubSub: communication channel between apps
_bbb[48] = "meta"   # "Redis DB." (section header)
_bbb[49] = "arch"   # Redis DB: recorded events stored
_bbb[50] = "arch"   # Recording Processor takes events and raw files
_bbb[51] = "meta"   # "Apps akka." (section header)
_bbb[52] = "arch"   # Apps: main app for real-time collaboration
_bbb[53] = "arch"   # Apps provides users, chat, whiteboard, presentations
_bbb[54] = "meta"   # "diagram of different components of Apps Akka"
_bbb[55] = "impl"   # MeetingActor: meeting business logic
_bbb[56] = "impl"   # MeetingActor stores info, processes messages
_bbb[57] = "meta"   # "FSESL akka." (section header)
_bbb[58] = "arch"   # FSESL extracted for FreeSWITCH integration
_bbb[59] = "arch"   # Allows alternative voice conference integrations
_bbb[60] = "arch"   # Communication between apps and FSESL via redis pubsub
_bbb[61] = "meta"   # "FreeSWITCH." (section header)
_bbb[62] = "other"  # "We think FreeSWITCH is an amazing..."
_bbb[63] = "arch"   # FreeSWITCH provides voice conferencing
_bbb[64] = "arch"   # Users join voice conference through headset
_bbb[65] = "arch"   # Chrome/Firefox: WebRTC for higher quality audio
_bbb[66] = "arch"   # FreeSWITCH integrated with VOIP providers
_bbb[67] = "meta"   # "Kurento and WebRTC-SFU." (section header)
_bbb[68] = "arch"   # Kurento: SFU and MCU models
_bbb[69] = "arch"   # KMS: webcams, listen-only audio, screensharing
_bbb[70] = "arch"   # WebRTC-SFU: media controller, negotiations
_bbb[71] = "meta"   # "Joining a voice conference."
_bbb[72] = "arch"   # User joins from HTML5 client or phone
_bbb[73] = "arch"   # Client: Microphone or Listen Only, WebRTC
_bbb[74] = "other"  # "WebRTC provides high-quality audio"
_bbb[75] = "meta"   # "Uploading a presentation."
_bbb[76] = "arch"   # Presentations go through conversion for display in client
_bbb[77] = "impl"   # Office → PDF via LibreOffice
_bbb[78] = "arch"   # PDF → SVG via bbb-web
_bbb[79] = "arch"   # Conversion progress via Redis pubsub to client
_bbb[80] = "meta"   # "Presentation conversion flow."
_bbb[81] = "meta"   # "diagram below describes flow"
_bbb[82] = "impl"   # Configuration for SWF, SVG, PNG conversion
_bbb[83] = "meta"   # "Then below the SVG conversion flow"
_bbb[84] = "impl"   # Conversion fallback
_bbb[85] = "impl"   # Heavy SVG → rasterized image inside SVG
_bbb[86] = "meta"   # "Internal network connections."
_bbb[87] = "meta"   # "diagram shows how components connect via sockets"
ANNOTATIONS["bigbluebutton"] = _bbb


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_pcm_model(repo_path):
    tree = ET.parse(repo_path)
    root = tree.getroot()
    elements = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        eid = elem.get('id')
        ename = elem.get('entityName')
        if eid and ename:
            if tag == 'components__Repository':
                elements[eid] = {'name': ename, 'type': 'Component'}
            elif tag == 'interfaces__Repository':
                elements[eid] = {'name': ename, 'type': 'Interface'}
    return elements


def load_gold(path):
    links = set()
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def load_result(path):
    links = set()
    if not os.path.exists(path):
        return links
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links.add((row['modelElementID'], int(row['sentence'])))
    return links


def build_dataset():
    """Build complete annotated dataset."""
    rows = []

    for project, config in PROJECTS.items():
        bench = os.path.join(BENCHMARK, project)
        model_elements = parse_pcm_model(os.path.join(bench, config['model']))
        gold = load_gold(os.path.join(bench, config['gold']))
        result_path = os.path.join(RESULTS, project, "sad-sam", f"sadSamTlr_{project}.csv")
        result = load_result(result_path)

        # Sentence-level gold/result info
        gold_by_sent = {}
        for eid, snum in gold:
            gold_by_sent.setdefault(snum, []).append(model_elements.get(eid, {}).get('name', eid))
        result_by_sent = {}
        for eid, snum in result:
            result_by_sent.setdefault(snum, []).append(model_elements.get(eid, {}).get('name', eid))

        text_path = os.path.join(bench, config['text'])
        with open(text_path) as f:
            lines = f.readlines()

        annotations = ANNOTATIONS.get(project, {})

        for i, line in enumerate(lines, 1):
            text = line.strip()
            label = annotations.get(i, 'other')
            in_gold = i in gold_by_sent
            in_result = i in result_by_sent
            gold_elements = gold_by_sent.get(i, [])
            result_elements = result_by_sent.get(i, [])

            # Determine SWATTR correctness for this sentence
            if in_result and in_gold:
                swattr_status = 'has_TP'
            elif in_result and not in_gold:
                swattr_status = 'FP_only'
            elif not in_result and in_gold:
                swattr_status = 'FN_only'
            else:
                swattr_status = 'TN'

            rows.append({
                'project': project,
                'sentence_num': i,
                'text': text,
                'label': label,
                'in_gold': in_gold,
                'in_result': in_result,
                'swattr_status': swattr_status,
                'gold_elements': ';'.join(gold_elements),
                'result_elements': ';'.join(result_elements),
            })

    return rows


def write_csv(rows, path):
    """Write annotated dataset to CSV."""
    fields = ['project', 'sentence_num', 'label', 'in_gold', 'in_result',
              'swattr_status', 'gold_elements', 'result_elements', 'text']
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def print_statistics(rows):
    """Print dataset statistics."""
    from collections import Counter

    print("=" * 80)
    print("ANNOTATED DATASET STATISTICS")
    print("=" * 80)

    # Overall
    label_counts = Counter(r['label'] for r in rows)
    total = len(rows)
    print(f"\nTotal sentences: {total}")
    print(f"\nLabel distribution:")
    for label, count in label_counts.most_common():
        print(f"  {label:<12}: {count:>4} ({count/total*100:>5.1f}%)")

    # Per project
    print(f"\nPer-project breakdown:")
    for proj in PROJECTS:
        proj_rows = [r for r in rows if r['project'] == proj]
        proj_labels = Counter(r['label'] for r in proj_rows)
        print(f"\n  {proj} ({len(proj_rows)} sentences):")
        for label in ['arch', 'pkg_code', 'impl', 'meta', 'other']:
            count = proj_labels.get(label, 0)
            print(f"    {label:<12}: {count:>3} ({count/len(proj_rows)*100:>5.1f}%)")

    # Cross-tabulation: label × in_gold
    print(f"\nLabel × Gold Standard:")
    print(f"  {'Label':<12} {'In Gold':>8} {'Not Gold':>9} {'Gold Rate':>10}")
    for label in ['arch', 'pkg_code', 'impl', 'meta', 'other']:
        label_rows = [r for r in rows if r['label'] == label]
        in_gold = sum(1 for r in label_rows if r['in_gold'])
        not_gold = len(label_rows) - in_gold
        rate = in_gold / len(label_rows) * 100 if label_rows else 0
        print(f"  {label:<12} {in_gold:>8} {not_gold:>9} {rate:>9.1f}%")

    # Cross-tabulation: label × swattr_status
    print(f"\nLabel × SWATTR status:")
    print(f"  {'Label':<12} {'has_TP':>8} {'FP_only':>8} {'FN_only':>8} {'TN':>8}")
    for label in ['arch', 'pkg_code', 'impl', 'meta', 'other']:
        label_rows = [r for r in rows if r['label'] == label]
        tp = sum(1 for r in label_rows if r['swattr_status'] == 'has_TP')
        fp = sum(1 for r in label_rows if r['swattr_status'] == 'FP_only')
        fn = sum(1 for r in label_rows if r['swattr_status'] == 'FN_only')
        tn = sum(1 for r in label_rows if r['swattr_status'] == 'TN')
        print(f"  {label:<12} {tp:>8} {fp:>8} {fn:>8} {tn:>8}")

    # The key question: among SWATTR FPs, what are the labels?
    print(f"\nKey insight — SWATTR FP sentences by label:")
    fp_rows = [r for r in rows if r['swattr_status'] == 'FP_only']
    fp_labels = Counter(r['label'] for r in fp_rows)
    print(f"  Total FP sentences: {len(fp_rows)}")
    for label, count in fp_labels.most_common():
        pct = count / len(fp_rows) * 100
        print(f"    {label:<12}: {count:>3} ({pct:>5.1f}%)")

    # Among SWATTR positives, how good would "label != pkg_code" filter be?
    print(f"\nHypothetical filter — remove pkg_code sentences from SWATTR positives:")
    pos_rows = [r for r in rows if r['in_result']]
    pos_tp_before = sum(1 for r in pos_rows if r['in_gold'])
    pos_fp_before = sum(1 for r in pos_rows if not r['in_gold'])
    filtered = [r for r in pos_rows if r['label'] != 'pkg_code']
    pos_tp_after = sum(1 for r in filtered if r['in_gold'])
    pos_fp_after = sum(1 for r in filtered if not r['in_gold'])
    # Note: some sentences have both TP and FP links (different elements)
    # Use link-level not sentence-level for precision
    print(f"  Before: {len(pos_rows)} sentences ({pos_tp_before} have gold, {pos_fp_before} FP-only)")
    print(f"  After:  {len(filtered)} sentences ({pos_tp_after} have gold, {pos_fp_after} FP-only)")
    print(f"  FPs removed: {pos_fp_before - pos_fp_after}")
    print(f"  TPs preserved: {pos_tp_after}/{pos_tp_before}")


def main():
    rows = build_dataset()
    csv_path = os.path.join(OUT_DIR, "annotated_sentences.csv")
    write_csv(rows, csv_path)
    print(f"Wrote {len(rows)} rows to {csv_path}\n")
    print_statistics(rows)

    # Also write JSON for easier downstream use
    json_path = os.path.join(OUT_DIR, "annotated_sentences.json")
    with open(json_path, 'w') as f:
        json.dump(rows, f, indent=2)
    print(f"\nAlso wrote JSON to {json_path}")


if __name__ == '__main__':
    main()
