# P19 RANDOM BASELINE FINAL MATHEMATICAL & SEMANTIC VERIFICATION

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: Authoritative Random Baseline Specification, Semantics & Proof  
**Date**: 2026-09-27  
**Verification Status**: VERIFIED  

---

## 1. Verified Summary Metrics

- **protocol**: Balanced Uniform 6-Class Label Permutation Baseline
- **population_and_classes**: Carinthia Defect SEM (4,591 total micrographs across 6 discrete defect classes)
- **randomization_assumption**: Uniform discrete prior over classes; each class is equally likely with probability $p = 1/6$
- **top1_formula**: $\text{Top-1} = 1 / 6$
- **mrr_formula**: $\mathbb{E}[\text{MRR}] = H_6 / 6 = (49 / 20) / 6 = 49 / 120$
- **balanced_random_top1**: $1 / 6 = 0.166666\ldots \approx 0.1667$
- **balanced_random_mrr**: $49 / 120 = 0.408333\ldots \approx 0.4083$
- **notation_status**: VERIFIED

---

## 2. Complete Mathematical Derivations & Notation

### 2.1 Baseline A: Balanced Uniform Six-Class Random Class-Label Baseline
This baseline represents an uninformative classifier operating under a uniform prior across the $C = 6$ discrete defect classes.

1. **Random Top-1 Accuracy**:
   $$\text{Random Top-1} = \frac{1}{6} = 0.166666\ldots \approx 0.1667$$

2. **Sixth Harmonic Number ($H_6$)**:
   $$H_6 = 1 + \frac{1}{2} + \frac{1}{3} + \frac{1}{4} + \frac{1}{5} + \frac{1}{6} = \frac{49}{20} = 2.45$$

3. **Expected Mean Reciprocal Rank ($\mathbb{E}[\text{MRR}]$)**:
   Under a uniformly random ranking/permutation of the 6 classes, the true class rank $r$ is uniformly distributed over $\{1, 2, 3, 4, 5, 6\}$. 
   $$\mathbb{E}[\text{MRR}] = \frac{H_6}{6} = \frac{49 / 20}{6} = \frac{49}{120} = 0.408333\ldots \approx 0.4083$$

   - **Authoritative Text Notation**:
     `H₆ / 6 = (49 / 20) / 6 = 49 / 120 = 0.408333...`

---

### 2.2 Baseline B: Gallery-Weighted Random Image Retrieval Baseline
In contrast to Baseline A, Baseline B models drawing a candidate micrograph uniformly at random from the candidate gallery of $N - 1 = 4,590$ images without class rebalancing.

Due to the extreme physical class distribution skew in the Carinthia corpus:
- Class 1: 55 images ($1.20\%$)
- Class 2: 8 images ($0.17\%$)
- Class 3: 4,008 images ($87.30\%$)
- Class 4: 289 images ($6.29\%$)
- Class 5: 4 images ($0.09\%$)
- Class 6: 227 images ($4.94\%$)

The expected retrieval performance under uniform gallery-image sampling is:
- **Expected Micro-Averaged R@1**:
  $$\mathbb{E}[\text{Micro R@1}_{\text{gallery}}] = \frac{1}{N} \sum_{c=1}^6 \frac{N_c(N_c - 1)}{N - 1} = \frac{16,197,628}{4591 \times 4590} = \mathbf{0.76865} \quad (\approx 76.87\%)$$
  *(Dominated by Class 3's 87.30% frequency; an uncalibrated random image pick hits Class 3 with 87.3% probability for a Class 3 query)*

- **Expected Macro-Averaged R@1**:
  $$\mathbb{E}[\text{Macro R@1}_{\text{gallery}}] = \frac{1}{6} \sum_{c=1}^6 \frac{N_c - 1}{N - 1} = \frac{1}{6} \left(\frac{4585}{4590}\right) = \mathbf{0.16648} \quad (\approx 16.65\%)$$

---

## 3. Explicit Semantic Distinction

| Evaluation Aspect | Baseline A: Balanced Random Class Guessing | Baseline B: Gallery-Weighted Random Retrieval |
|---|---|---|
| **Sampling Entity** | Discrete class label from $\{1, 2, 3, 4, 5, 6\}$ | Image candidate $g$ from gallery of 4,590 images |
| **Class Prior Assumption** | Uniform ($p_c = 1/6$) | Empirical gallery distribution ($\hat{p}_3 = 87.3\%$) |
| **Top-1 / Micro R@1** | $\mathbf{0.1667}$ ($1/6$) | $\mathbf{0.7687}$ ($16,197,628 / 21,072,690$) |
| **Macro R@1** | $\mathbf{0.1667}$ ($1/6$) | $\mathbf{0.1665}$ ($4,585 / 27,540$) |
| **Expected MRR** | $\mathbf{0.4083}$ ($49/120$) | Rank-ordered harmonic sum over gallery |
| **Evaluation Role** | Unbiased multi-class uninformative chance baseline | Empirical demonstration of severe dataset class skew |

---

## 4. Verification Statement

The mathematical derivations, text notations, and semantic distinctions between Baseline A and Baseline B are verified, accurate, and harmonized across all platform reports.
