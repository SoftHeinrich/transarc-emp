# Hardcoded Rules Analysis: "Fully Automatic" pkg_code Pipeline

## Verdict

The pipeline claims "ZERO hardcoded patterns" but contains **34 hardcoded decisions** across 4 categories. The 6 "candidate patterns" in Phase 2 are essentially the same rules as the manually-crafted Rule V2 — the pipeline doesn't discover them, it pre-defines them and checks which ones match seeds.

---

## Inventory of Hardcoded Elements

### Category A: Domain-Specific Patterns (6 items) — THE MAIN CHEAT

These are the 6 candidate regex patterns in Phase 2 `extract_patterns()`:

| # | Pattern name | Regex | Origin |
|---|-------------|-------|--------|
| 1 | `starts_dotted` | `^[a-z][a-z0-9]*\.[a-z]` | Java package naming |
| 2 | `starts_x_dot` | `^x\.[a-z]` | Teammates doc convention |
| 3 | `sub_packages` | `^sub-?packages?\s+contains` | Teammates doc |
| 4 | `overview_contains` | `overview\s+contains` | Teammates doc |
| 5 | `not_a_X_package` | `is not a \w+ package` | Teammates doc |
| 6 | `classes_in_package` | `classes in the \S+\.\S+ package` | Teammates doc |

**What the code does**: tests these 6 pre-written regexes against seeds, keeps the "seed-exclusive" ones.
**What it claims**: "auto-discovers structural patterns."
**Reality**: The regexes ARE the domain knowledge. The "auto" part is just a filter (keep if seed-exclusive). If you remove these 6 lines, the pipeline collapses.

**Comparison with Rule V2**: 5/8 Rule V2 patterns have direct equivalents in these 6 candidates. The pipeline is Rule V2 dressed up as auto-discovery.

### Category B: Domain Keywords & Features (8 items)

| # | Element | Location | Why it's hardcoded |
|---|---------|----------|--------------------|
| 7 | `'contains' in text` | Feature `has_contains` | Verb specific to package listings |
| 8 | `'package' in text` | Feature `has_package` | Directly targets the concept |
| 9 | dot-id regex `\b[a-z][a-z0-9]*\.[a-z][a-z0-9]*\b` | Feature `has_dot_id` | Java package name pattern |
| 10 | `^x\.` | Feature `starts_x_dot` | Teammates sub-package convention |
| 11 | `n_words <= 12` | Feature `is_short` | Tuned on this data |
| 12 | `for keyword in ['package']` | Modifier discovery | Only checks "package" |
| 13 | Pronoun list `('it ', 'its ', ...)` | Propagation | English-specific |
| 14 | `dot_token_ratio` feature | Anomaly score | Derived from #9 |

### Category C: Tuned Weights & Thresholds (14 items)

| # | Element | Value | Where |
|---|---------|-------|-------|
| 15 | starts_lower weight | +2 | anomaly_score |
| 16 | has_dot_id weight | +2 | anomaly_score |
| 17 | n_dot_ids >= 2 weight | +2 | anomaly_score |
| 18 | n_dot_ids >= 4 weight | +2 | anomaly_score |
| 19 | starts_dot_id weight | +2 | anomaly_score |
| 20 | has_contains weight | +1 | anomaly_score |
| 21 | has_contains+is_short weight | +1 | anomaly_score |
| 22 | dot_ratio >= 0.15 weight | +2 | anomaly_score |
| 23 | dot_ratio >= 0.30 weight | +1 | anomaly_score |
| 24 | starts_x_dot weight | +2 | anomaly_score |
| 25 | has_package+has_dot_id weight | +2 | anomaly_score |
| 26 | gap threshold ≤ 20% | 0.20 | discover_seeds |
| 27 | disc feature threshold > 0.3, < 0.1 | | extract_patterns |
| 28 | disc word threshold > 0.3, < 0.05 | | extract_patterns |

### Category D: Algorithm Design Choices (6 items)

| # | Element | Why it matters |
|---|---------|---------------|
| 29 | Feature profile: ≥ 3 disc features to match | Could be 2 or 4 |
| 30 | Propagation: only check snum+1 | Could be +2 or window |
| 31 | Propagation: require pronoun + disc word | Could be just disc word |
| 32 | Propagation disc word threshold > 0.20, < 0.05 | Tuned |
| 33 | Disc word min length > 3 | Filters short words |
| 34 | 3-phase pipeline structure | Design choice |

---

## What is genuinely automatic?

Only these mechanisms require no human knowledge about pkg_code:

1. **Gap-finding** in score distribution — generic algorithm
2. **Seed-exclusive filtering** — "if regex matches only seeds, keep it" — generic
3. **Word frequency comparison** — seed vs non-seed rates — generic
4. **Pronoun detection** — generic English (though the pronoun list is hardcoded)
5. **The pipeline structure** — anomaly → refine → propagate

But these generic mechanisms only FILTER and SELECT from human-provided candidates. They cannot GENERATE the candidates.

---

## The key question: What breaks without each hardcoded element?

### If we remove Category A (the 6 candidate patterns):
Phase 2 has no patterns to test → falls back to feature profile only → misses 9 sentences → F1=0.870.

### If we remove Category B (keywords "contains", "package", dot-id regex):
Phase 1 anomaly scoring loses its strongest signals → can't distinguish pkg_code from normal prose → threshold becomes meaningless.

### If we remove Category C (tuned weights):
Equal weights make all features equivalent → no natural score gap → threshold selection fails.

### If we remove Category D (propagation design):
S24 is not recovered → F1=0.987 instead of 1.000.

---

## Comparison: what's the actual "auto" contribution?

| Component | Auto contribution | Human contribution |
|-----------|------------------|--------------------|
| Phase 1 seeds | Gap-finding threshold | Features, weights, keywords |
| Phase 2 patterns | Seed-exclusive filter | All 6 candidate regexes |
| Phase 2 features | Rate comparison | Feature selection, thresholds |
| Phase 3 propagation | Disc word discovery | Pronoun list, search range |

The auto-discovery contributes **~20%** of the pipeline's discriminative power. The remaining **~80%** comes from hardcoded features, patterns, and weights that encode human knowledge of what pkg_code looks like.

---

## What would truly automatic look like?

A genuinely zero-knowledge system would need to:

1. **Discover features from raw text** — e.g., character n-gram analysis finds dot-patterns are unusual without a pre-defined regex
2. **Learn keywords automatically** — e.g., find words with high variance across sentence clusters
3. **Generate regexes from examples** — e.g., from seed sentences, extract common character-level patterns
4. **Learn weights from data** — e.g., logistic regression on auto-discovered features
5. **Handle threshold selection robustly** — e.g., Otsu's method or cross-validation

Such a system would be equivalent to a text anomaly detector trained on normal English prose, flagging sentences that deviate from expected syntax. This is fundamentally what an LLM does when prompted "does this sentence describe package structure?"

---

## Honest summary

The pipeline is best described as: **semi-automatic application of manually-designed rules**. The human designed 6 regex patterns and 8 features that capture pkg_code. The "auto" part checks which patterns match seeds and filters false positives. This is useful engineering but not meta-learning.

The gap between this and true meta-learning:
- Rule V2 (fully hardcoded): F1=1.000
- "Auto" pipeline (hardcoded patterns + auto filter): F1=1.000
- Anomaly detection only (no candidate patterns): F1=0.894
- True zero-knowledge: unknown, would require fundamentally different approach
