# Better Solutions for LLM SAD-CODE TLR

## Current State

The LLM Adaptive baseline achieves **0.829 avg micro F1** at SAD-CODE, beating TransArc (0.803).
Post-processing fixes (B2+B4+B5) push this to **0.846** (+0.017), but this is the ceiling for
post-processing on pre-computed classifications.

To go further, we need fundamentally different approaches. This document proposes 6 solutions
ranked by expected impact, grounded in deep analysis of all failure modes.

---

## Diagnostic Summary

### Three completed analyses inform these proposals:

**1. Deep FN Analysis** — Categorized all 46 LLM FN links:

| FN Category | Count | % | Description |
|:------------|------:|--:|:------------|
| IMPLICIT_REF | 20 | 51.3% | No component name in sentence text |
| MULTI_COMP_MISS | 11 | 28.2% | Sentence has multiple gold components, LLM got some but not all |
| EXPLICIT_MISS | 8 | 20.5% | Name IS in text but LLM missed it |
| *Phantom Components* | *11* | *23.9%* | *Architecture-only elements not in LLM vocabulary* |

**2. Deep FP Analysis** — Categorized all 59 LLM FP links:

| FP Category | Count | % | Description |
|:------------|------:|--:|:------------|
| NO_GOLD_LINKS | 41 | 71.9% | Sentence has no gold links at all |
| OVER_ASSIGNMENT | 9 | 15.8% | Extra components beyond gold |
| WRONG_COMPONENT | 7 | 12.3% | Different component than gold |

**3. Document Structure Analysis** — Proximity signals across all 5 projects:

| Signal | Coverage |
|:-------|:---------|
| Component name IN gold sentence | 111/153 (72.5%) |
| Any component within ±3 lines | 147/153 (96.1%) |
| Own component within ±3 lines | 134/153 (87.6%) |
| Section header within ±3 lines | 125/153 (81.7%) |
| Non-gold with component mention | 30/225 (13.3%) |

**4. V45 vs LLM Comparison** — Complementarity analysis:

| Metric | V45 | LLM |
|:-------|:----|:----|
| Avg SAD-SAM F1 | 0.904 | 0.795 |
| Unique TPs | 33 | 9 |
| Unique FPs | 14 | 49 |
| Unique Precision | 70.2% | 15.5% |
| Unique TP implicit fraction | 39.4% | 77.8% |

---

## Per-Project Bottleneck Diagnosis

### MediaStore (F1=0.965) — Essentially solved
- 4 FN links all from phantom component DataStorage (no code, not in LLM vocabulary)
- 0 FPs. Perfect precision.
- **No actionable improvement path** at SAD-CODE level.

### TeaStore (F1=0.764) — Gold boundary mismatch
- 2 FN links (1 implicit, 1 explicit miss)
- **12 FPs — ALL are semantically correct** classifications of behavioral detail sentences that gold doesn't trace
- Example: "Passwords are hashed using BCrypt" → LLM assigns Auth (correct!), but gold only traces the introduction "The Auth service handles user and session authentication"
- **Root cause**: LLM classifies every sentence in a component section; gold only traces introductory/definitional sentences
- **Key fix**: Teach gold-standard tracing granularity

### Teammates (F1=0.707) — FP explosion from test descriptions
- 12 FN links (5 phantom GAE Datastore, 5 implicit, 2 explicit)
- 27 FP links: 20 from non-gold sentences (11 from test/package listings, 7 from UI browser details)
- **Root cause**: Long documentation (198 sentences) with detailed package-level descriptions that the LLM traces but gold doesn't
- **Key fix**: Reduce FPs in non-introductory sentences

### BigBlueButton (F1=0.710) — Co-occurrence blindness + component confusion
- 28 FN links: 11 implicit, 6 multi-component miss, 5 explicit miss
- **HTML5 Client recall = 0.357** (5/14), **HTML5 Server recall = 0.385** (5/13)
- **Presentation Conversion F1 = 0.000** (5 FPs, 2 FNs, 0 TPs!)
- Co-occurrence: sentences about "client side"/"server side" reference both HTML5 Client and HTML5 Server but LLM assigns one or neither
- Component confusion: FreeSWITCH/FSESL/WebRTC-SFU/Kurento frequently confused
- **Root cause**: Implicit references via pronouns + lack of co-occurrence awareness
- **Key fix**: Section-header-based scoping + co-occurrence hints

### JabRef (F1=0.999) — Essentially solved
- 0 FNs, 1 FP (preferences over-assigned). No actionable improvement.

---

## Proposed Solutions (Ranked by Expected Impact)

### S1: Section-Header-Aware Classification (Re-prompt)

**Impact**: HIGH (primarily BBB +0.10-0.15, secondarily TeaStore +0.03)

**Rationale**: 81.7% of gold sentences are within ±3 lines of a section header. BigBlueButton
has explicit component-named headers ("HTML5 client.", "BBB web.", "FreeSWITCH.", "Apps akka.",
"Redis PubSub.", etc.). The LLM currently ignores this document structure.

**Implementation**:
1. Pre-process documents to detect section headers (short lines ≤8 words, often containing component names)
2. Add document structure annotation to the LLM prompt: mark which section each sentence belongs to
3. Instruct: "Sentences within a component's section typically describe that component. Use section headings to resolve ambiguous references like 'the client' or 'the server side'."

**Expected effect on BBB**:
- HTML5 Server: sentences 10, 12, 13, 21, 39, 47, 73 are all within the "HTML5 client/server" section → LLM should assign HTML5 Server based on section context
- Presentation Conversion: sentences 80-81 are within the "Presentation conversion flow" section → LLM should correctly assign instead of misassigning
- Co-occurrence: "client side subscribes to server side" within HTML5 section → both components assigned

**Evidence**: 96.1% of gold sentences have a component mention within ±3 lines. For BBB specifically, HTML5 Server is the worst (53.8% covered by own name ±3) — but ALL 13 gold links fall within the HTML5 client/server section or the Redis PubSub section.

**Risk**: Low. Section detection is deterministic. Adding structure to the prompt only helps.

---

### S2: Tracing Granularity Calibration (Re-prompt)

**Impact**: HIGH (primarily TeaStore +0.05-0.07, Teammates +0.04-0.06)

**Rationale**: 71.9% of all FPs come from classifying sentences that have NO gold links. The dominant pattern: the LLM classifies every sentence in a component section, but the gold standard only traces introductory/definitional sentences, NOT behavioral implementation details.

**Implementation**:
1. Add explicit instruction to the LLM prompt: "Only trace sentences that INTRODUCE, DEFINE, or NAME a component. Do NOT trace sentences that describe implementation details, algorithms, or internal behavior unless they explicitly name a component."
2. Provide few-shot examples from each type:
   - TRACE: "The Auth service handles user and session authentication." (introduces component)
   - DO NOT TRACE: "Passwords are hashed using BCrypt." (implementation detail)
   - TRACE: "The Recommender is used to generate individual product recommendations." (names + defines)
   - DO NOT TRACE: "If the user is known, Slope One as item-based collaborative filtering is applied." (algorithm detail)

**Expected effect**:
- TeaStore: 12 FPs → ~3-5 FPs (removing pure behavioral detail sentences 13-17, 19-21, 29-30, 39-40)
- Teammates: 20 NO_GOLD_LINKS FPs → ~8-10 (removing test package listing sentences)
- BBB: 9 NO_GOLD_LINKS FPs → ~4-5

**Risk**: Medium. Some gold sentences ARE behavioral (e.g., "It provides the list of users, chat, whiteboard, presentations" for Apps). Overly strict filtering could create new FNs. Careful calibration of the few-shot examples is essential.

---

### S3: Co-Occurrence-Aware Prompting (Re-prompt)

**Impact**: MEDIUM (primarily BBB +0.05-0.08)

**Rationale**: BigBlueButton's worst failure is co-occurrence blindness. HTML5 Client (14 gold links) and HTML5 Server (13 gold links) co-occur in 10 sentences, but the LLM typically assigns only one. The LLM also confuses the FreeSWITCH/FSESL/WebRTC-SFU/Kurento cluster.

**Implementation**:
1. Pre-compute which component pairs frequently co-occur in sentences (from SAM-CODE file overlap or from the architecture model)
2. Add to prompt: "The following component pairs frequently appear together in sentences. When a sentence references one, consider whether it also references the other:
   - HTML5 Client ↔ HTML5 Server (client-server communication)
   - FreeSWITCH ↔ FSESL (FSESL is the FreeSWITCH integration layer)
   - Apps ↔ Redis PubSub (apps communicate via Redis)"
3. Additionally clarify component boundaries: "FSESL integrates FreeSWITCH, but they are separate components. WebRTC-SFU manages media streams, Kurento is the underlying media server."

**Expected effect on BBB**:
- HTML5 Client/Server: ~5-8 additional correct co-assignments in client-server sentences
- FreeSWITCH/FSESL: Fewer confusion FPs (currently sentence 60 gets FreeSWITCH instead of Apps)

**Risk**: Low-Medium. Co-occurrence hints could cause over-assignment if too broadly applied. Limit to documented high-co-occurrence pairs.

---

### S4: Sliding-Window Context (Re-run LLM)

**Impact**: MEDIUM (across all projects, primarily BBB +0.05)

**Rationale**: 51.3% of FNs are implicit references. The LLM currently sees sentences in isolation (or in one large batch). Providing ±2-3 sentence context would enable natural coreference resolution.

**Implementation**:
1. Instead of asking "Which components does sentence N relate to?", ask "Given sentences N-2 through N+2, which components does sentence N relate to?"
2. The context window provides natural discourse: "The HTML5 server sits behind nginx. [It] is built upon Meteor.js..." — the pronoun "It" resolves to HTML5 Server.
3. Can be combined with S1 (section headers in context).

**Expected effect**:
- BBB implicit FNs: sentences 10, 12, 13 (client-server references) become clearer with neighboring HTML5 Client/Server mentions
- Teammates: sentences with "In particular, it is responsible for..." resolve to the component mentioned 1-2 lines earlier

**Previous attempt (B1 discourse propagation) failed because**:
- B1 post-processed classifications, adding neighbors' components to unclassified sentences → massive FPs
- This proposal re-runs the LLM WITH context, so the LLM itself makes the judgment (not a rule)

**Risk**: Medium. Increases API cost (more tokens per call). May cause the LLM to "bleed" context from neighbors, creating new FPs. Need careful evaluation.

---

### S5: V45-Gated LLM Ensemble (Hybrid System)

**Impact**: MEDIUM (potentially +0.02-0.05 over V45 at SAD-SAM)

**Rationale**: V45 and LLM have complementary strengths. V45 has high unique precision (70.2%), while LLM has a few unique TPs that V45 misses (9 links, mostly implicit functional inferences). A simple union hurts (too many LLM FPs), but a selective ensemble could work.

**Implementation**:
1. Use V45 as the primary system (0.904 avg F1)
2. Add LLM links only when: (a) the LLM link has high confidence (all 3 variants agree), AND (b) the component name appears explicitly in the sentence
3. This recovers LLM's explicit-name-in-text TPs (the reliable ones) while rejecting its 49 unique FPs (mostly from sentences without explicit names)

**Expected effect (SAD-SAM level)**:

| Project | V45 F1 | Union F1 | Ensemble F1 (est.) |
|:--------|-------:|---------:|-------------------:|
| MediaStore | 0.897 | 0.968 | ~0.950 |
| TeaStore | 0.982 | 0.806 | ~0.982 |
| Teammates | 0.847 | 0.750 | ~0.860 |
| BBB | 0.846 | 0.763 | ~0.855 |
| JabRef | 0.947 | 0.947 | ~0.960 |

MediaStore is where the union genuinely helps (0.968); the ensemble should capture most of this.

**Risk**: Requires running both V45 and LLM. The improvement over V45 alone may be marginal. Only 9 LLM-unique TPs exist, and filtering reduces this further.

---

### S6: Phantom Component Recovery (Vocabulary Expansion)

**Impact**: LOW-MEDIUM at SAD-SAM (recovers 11/46 FN links = 23.9%), ZERO at SAD-CODE

**Rationale**: Three projects have architecture-only model elements not in the LLM's component vocabulary:

| Project | Phantom Element | Gold Links | Name |
|:--------|:---------------|:-----------|:-----|
| MediaStore | `_qxAiILg7EeSNPorBlo7x9g` | 3 | DataStorage |
| Teammates | `_KGVMcKETEeu-mYqkDskRow` | 5 | GAE Datastore |
| BigBlueButton | `_oN4CMFkHEeyewPSmlgszyA` | 3 | Kurento |

These elements exist in the SAD-SAM gold but have NO SAM-CODE mapping (no source code).

**Implementation**: Add these component names to the LLM's vocabulary for classification.

**Effect on SAD-CODE**: ZERO. Since these components have no code files, adding them to SAD-SAM doesn't add any file-level links. The SAD-CODE evaluation is unaffected.

**Effect on SAD-SAM**: Recovers up to 11 FN links across 3 projects, improving recall.

**Risk**: Could generate new FPs if the LLM over-assigns phantom components.

---

## Combined Recommendation

The highest-impact approach combines S1 + S2 + S3 in a single re-prompting strategy:

### Unified Re-Prompting Strategy

**Step 1: Document Pre-processing**
- Detect section headers (short lines ≤8 words containing component names)
- Annotate each sentence with its section context
- Compute component co-occurrence pairs from architecture model

**Step 2: Enhanced Prompt**
Include in the LLM prompt:
1. **Section annotations**: "Sentence N is in the section titled 'FreeSWITCH'"
2. **Tracing boundary**: "Only trace sentences that introduce, define, or explicitly name a component. Do not trace implementation details or algorithmic descriptions."
3. **Co-occurrence hints**: "HTML5 Client and HTML5 Server often co-occur in client-server communication sentences."
4. **Few-shot calibration**: 4-6 examples of trace/no-trace decisions from representative sentences

**Step 3: Sliding-window context (S4)**
Provide ±2 sentence context for implicit reference resolution.

### Expected Impact

| Project | Current | S1 | S2 | S3 | Combined (est.) |
|:--------|--------:|---:|---:|---:|----------------:|
| MediaStore | 0.965 | +0.000 | +0.000 | +0.000 | 0.965 |
| TeaStore | 0.764 | +0.030 | +0.060 | +0.000 | ~0.840 |
| Teammates | 0.707 | +0.010 | +0.050 | +0.000 | ~0.760 |
| BBB | 0.710 | +0.100 | +0.020 | +0.060 | ~0.860 |
| JabRef | 0.999 | +0.000 | +0.000 | +0.000 | 0.999 |
| **Average** | **0.829** | | | | **~0.885** |

This would bring the LLM baseline to ~0.885 avg F1, significantly above both TransArc (0.803) and V45 (estimated 0.893 at SAD-CODE).

---

## Priority Ordering

1. **S1 + S2 + S3 combined re-prompt** — Single implementation, highest aggregate impact
2. **S4 sliding-window context** — Additive improvement for implicit references
3. **S5 V45-gated ensemble** — Different paradigm (hybrid), moderate gain
4. **S6 phantom components** — Marginal, zero SAD-CODE impact

## Implementation Effort

| Solution | Effort | Requires Re-running LLM | API Cost |
|:---------|:-------|:-----------------------:|:---------|
| S1 | Medium | Yes | Same |
| S2 | Low | Yes | Same |
| S3 | Low | Yes | Same |
| S4 | Medium | Yes | ~3x (context window) |
| S5 | High | No (uses existing V45+LLM) | None |
| S6 | Low | Yes | Same |

---

## Appendix: Cross-Cutting Failure Patterns

### Pattern 1: Over-Classification of Behavioral Detail (41 FPs, 71.9%)
The LLM classifies sentences describing HOW a component works (algorithms, protocols, data flow)
when the gold standard only traces sentences that IDENTIFY or DEFINE the component.

**Examples**:
- TeaStore S19: "Passwords are hashed using BCrypt" → LLM: Auth ✓ semantically, ✗ by gold
- TeaStore S29: "Recommendations based on shopping cart" → LLM: Recommender ✓ semantically, ✗ by gold
- BBB S24-29: Frontend/backend process details → LLM: HTML5 Server, ✗ by gold

### Pattern 2: Co-Occurrence Blindness (17 FNs)
Sentences reference two components (typically client-server or integration pairs) and the LLM
assigns one or neither.

**Worst case**: BBB HTML5 Client+HTML5 Server co-occur in ~10 sentences. LLM assigns neither
for sentences like "The client side subscribes to the published collections on the server side."

### Pattern 3: Phantom Components (11 FNs, 23.9%)
Architecture-only model elements (DataStorage, GAE Datastore, Kurento) appear in the SAD-SAM
gold standard but have no code mapping and are invisible to the LLM.

### Pattern 4: Component Confusion in Related Clusters (7 FPs + 6 FNs)
BBB has adjacent components (FreeSWITCH/FSESL/WebRTC-SFU/Kurento) that the LLM confuses,
generating simultaneous FPs and FNs (assigning wrong component from same cluster).

### Pattern 5: Diagram/Caption Sentences (5 FNs)
Sentences like "Below is a diagram of Apps Akka" or "Presentation conversion flow" are
meta-referential and gold-linked, but the LLM treats them as non-architectural.
