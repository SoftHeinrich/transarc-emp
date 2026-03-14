# SWATTR TP vs FP: Semantic Separability Analysis

Can sentence embeddings distinguish SWATTR true positives from false positives?

## 1. Data: 148 TPs, 40 FPs across 5 projects

## 2. Semantic Sentence Type Analysis

Regex-based sentence type classification — do FPs cluster in certain types?

| Sentence Type | TP count (rate) | FP count (rate) | FP/TP Ratio |
|--------------|-----------------|-----------------|-------------|
| api_description | 2 (1.4%) | 2 (5.0%) | 3.70 ** |
| behavioral | 7 (4.7%) | 1 (2.5%) | 0.53 |
| class_enumeration | 0 (0.0%) | 6 (15.0%) | inf ** |
| communication | 16 (10.8%) | 3 (7.5%) | 0.69 |
| data_flow | 11 (7.4%) | 0 (0.0%) | 0.00 |
| definition | 10 (6.8%) | 1 (2.5%) | 0.37 |
| none | 99 (66.9%) | 7 (17.5%) | 0.26 |
| package_description | 0 (0.0%) | 6 (15.0%) | inf ** |
| structural_overview | 2 (1.4%) | 6 (15.0%) | 11.10 ** |
| sub_package | 8 (5.4%) | 30 (75.0%) | 13.88 ** |

## 3. Sentence Embedding Analysis

### Strategy A: Sentence-only embedding

### Strategy B: Sentence ↔ Component Name cosine similarity

- TP mean cosine sim: **0.4478** (std 0.2153)
- FP mean cosine sim: **0.3901** (std 0.1344)
- Cohen's d: **+0.286**

Per-project cosine similarity:

| Project | TP mean sim | FP mean sim | Cohen's d |
|---------|-------------|-------------|-----------|
| mediastore | 0.5498 | 0.1320 | +0.000 |
| teastore | 0.5108 | N/A (0 FPs) | N/A |
| teammates | 0.3378 | 0.4136 | -0.486 |
| bigbluebutton | 0.5337 | 0.3324 | +0.787 |
| jabref | 0.3713 | 0.2867 | +0.481 |

### Strategy C: Contextualized pair embedding

Embed: "This sentence describes the architectural component {name}: {text}"

## 4. Embedding-Based Classification (5-fold CV)

| Feature Set | LR Acc | LR AUC | RF Acc | RF AUC | Majority |
|-------------|--------|--------|--------|--------|----------|
| Sentence embedding (384d) | 0.809 | 0.805 | 0.787 | 0.768 | 0.787 |
| Cosine sim only (1d) | 0.564 | 0.577 | 0.681 | 0.536 | 0.787 |
| Contextualized pair (384d) | 0.809 | 0.795 | 0.803 | 0.778 | 0.787 |
| Sentence emb + cosine (385d) | 0.793 | 0.803 | 0.777 | 0.760 | 0.787 |

Best: **Sentence embedding (384d)** (AUC=0.805)

## 5. Combined: Embedding + Surface Features

Add surface features from previous analysis to the best embedding.

| Feature Set | LR Acc | LR AUC | RF Acc | RF AUC |
|-------------|--------|--------|--------|--------|
| Surface features only (4d) | 0.899 | 0.819 | 0.862 | 0.808 |
| Best embedding + surface | 0.830 | 0.813 | 0.787 | 0.798 |
| Best embedding + surface + cosine | 0.803 | 0.817 | 0.793 | 0.799 |
| Cosine + surface (5d) | 0.899 | 0.876 | 0.878 | 0.831 |

## 6. Leave-One-Project-Out (Embedding)

Train on 4 projects, test on held-out. Using sentence embedding + cosine sim.

| Held-out | n_TP | n_FP | LR Acc | LR AUC | RF Acc | RF AUC |
|----------|------|------|--------|--------|--------|--------|
| mediastore | 17 | 1 | 1.000 | 1.000 | 0.944 | 0.471 |
| teastore | 20 | 0 | N/A | N/A | N/A | N/A |
| teammates | 49 | 32 | 0.580 | 0.399 | 0.605 | 0.431 |
| bigbluebutton | 44 | 5 | 0.755 | 0.573 | 0.898 | 0.411 |
| jabref | 18 | 2 | 0.850 | 0.194 | 0.900 | 0.333 |

## 7. TF-IDF Discriminative Words

Words most associated with TP vs FP sentences (by LR coefficient on TF-IDF).

**Top 15 TP-associated words/bigrams** (positive LR coefficient):

- `component`: +1.664
- `service`: +0.669
- `freeswitch`: +0.524
- `bigbluebutton`: +0.522
- `using`: +0.519
- `database`: +0.485
- `storage component`: +0.477
- `akka`: +0.447
- `files`: +0.443
- `server`: +0.442
- `common component`: +0.427
- `application`: +0.426
- `provider`: +0.417
- `registry`: +0.395
- `image`: +0.395

**Top 15 FP-associated words/bigrams** (negative LR coefficient):

- `contains`: -1.702
- `package`: -1.320
- `core`: -1.041
- `ui website`: -0.788
- `website`: -0.788
- `e2e`: -0.786
- `api`: -0.756
- `util`: -0.750
- `scripts`: -0.726
- `storage entity`: -0.701
- `helpers`: -0.674
- `needed`: -0.667
- `common datatransfer`: -0.661
- `datatransfer`: -0.658
- `cascade logic`: -0.654

TF-IDF LR classification: Acc=0.819, AUC=0.830

## 8. PCA Projection (2D)

Sentence embeddings projected to 2D via PCA. ASCII scatter plot.

Explained variance: PC1=8.7%, PC2=5.7%

```
  + = TP    o = FP    * = overlap
                                                              
                                                              
                                                 +            
                                                              
       +    + +                               +               
       +          +        *                 +                
                +        *+   *                 +  *  +       
       +         +++ o        +                      *        
              +  +      +  +o+   ++    ++    o  *    *        
               *      +  ++ oo o       ++ ++        +   +     
      +      +         +   ++ + +          o+++ o             
          o           + o+ + +    +   +      o   *            
                  + +  +      o+++o  oo  o+*+                 
                  +  +  ++   + +  +                           
                         * +   o     *        +               
               +o   +     +      ++     o       *             
                        ++      ++  o+ o   + +                
                    +  ++        +     +                      
                        + +         + +                       
                           +         ++                       
                                  +   + o *                   
                                                              
                                                              
                                           o                  
                                                              
```

**TP/FP centroids per project in PCA space:**

| Project | TP centroid (PC1,PC2) | FP centroid (PC1,PC2) | Distance |
|---------|----------------------|----------------------|----------|
| mediastore | (-0.13, -0.17) | (-0.37, -0.21) | 0.238 |
| teastore | (-0.10, -0.25) | N/A (0 FPs) | N/A |
| teammates | (0.20, 0.02) | (0.13, -0.05) | 0.097 |
| bigbluebutton | (-0.28, 0.12) | (-0.29, 0.10) | 0.025 |
| jabref | (0.24, 0.14) | (0.13, 0.14) | 0.108 |

## 9. Architectural vs Implementation Framing

Cosine similarity of each sentence to reference phrases:

| Reference Phrase | TP Mean Sim | FP Mean Sim | Cohen's d |
|-----------------|-------------|-------------|-----------|
| "This component is responsible for handling" | 0.2230 | 0.2087 | +0.132 |
| "The architectural component provides services" | 0.2538 | 0.2432 | +0.084 |
| "This package contains implementation classes" | 0.1276 | 0.2127 | -0.750 |
| "The source code directory structure" | 0.1049 | 0.1620 | -0.619 |
| "Package overview of the system structure" | 0.1813 | 0.2372 | -0.443 |

Reference-phrase similarity features: AUC = **0.688**

## 10. Synthesis

### Summary of all approaches:

| Approach | AUC | Verdict |
|----------|-----|---------|
| Surface features (prev analysis) | 0.713 | Moderate |
| Sentence embedding (384d) | 0.805 | Good |
| Cosine sim (sent↔name) | 0.577 | Not separable |
| TF-IDF (500 features) | 0.830 | Good |
| Reference phrase sims (5d) | 0.688 | Weak |
| Everything combined | 0.818 | Good |

### Key Findings

1. **Semantic embeddings do NOT solve the TP/FP problem.**
   The 384-dimensional sentence embedding (capturing deep semantics)
   performs comparably to simple surface features (position, length).

2. **Sentence ↔ Component cosine similarity** is the single best
   semantic signal, but its effect size is limited. FP sentences
   are semantically similar to their component — because they ARE about
   the component, just at a different granularity than the gold standard expects.

3. **TF-IDF discriminative words** reveal the FP pattern:
   FPs are associated with package-level descriptions ('contains',
   'package', sub-package dotted names). TPs are associated with
   architectural-role language. But this pattern is project-specific
   (dominated by Teammates' package descriptions).

4. **The fundamental problem remains:** SWATTR FPs describe the *right*
   component at the *wrong* abstraction level. From a semantic perspective,
   'storage.api provides the API of the component' IS about Storage — it's
   a true statement, just not one the gold standard considers a trace link.
   This is an **annotation boundary** issue, not a semantic one.

5. **Cross-project generalization** (LOPO) remains poor for embeddings,
   confirming that the FP pattern is project-specific.

