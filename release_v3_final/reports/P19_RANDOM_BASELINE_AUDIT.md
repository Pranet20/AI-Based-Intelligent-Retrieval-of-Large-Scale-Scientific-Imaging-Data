# P19 RANDOM BASELINE MATHEMATICAL AUDIT

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: Mathematical Verification & Derivation of Random Baseline (0.1667 / 0.4083)  
**Date**: 2026-09-27  
**Status**: AUDITED_AND_RECONCILED  

---

## 1. Background & Discrepancy Identification

In the Phase 19 model comparison table, the Random Baseline was reported as:
- **Micro R@1**: `0.1667`
- **Macro R@1**: `0.1667`
- **MRR**: `0.4083`

This mathematical audit reconciles these figures against the two possible interpretations:
1. **Discrete Uniform Random Class Guessing** (Balanced Class Assignment)
2. **Uniform Random Gallery Image Retrieval** (Gallery-Proportional Sampling)

---

## 2. Mathematical Derivations

### Protocol A: Discrete Uniform Random Class Guessing (Balanced Prior)
Under a uniform random guess across $C = 6$ equiprobable defect classes:
- **Expected Top-1 Accuracy**:
  $$\mathbb{E}[\text{Top-1}] = \frac{1}{C} = \frac{1}{6} = 0.166667 \approx \mathbf{0.1667}$$
- **Expected Mean Reciprocal Rank (MRR)**:
  Under a random permutation of the 6 classes, the rank $r$ of the true class follows a uniform distribution on $\{1, 2, 3, 4, 5, 6\}$. The expected reciprocal rank is given by the 6th harmonic number $H_6$ divided by 6:
  $$\mathbb{E}[\text{MRR}] = \frac{1}{6} \sum_{r=1}^6 \frac{1}{r} = \frac{1}{6} \left(1 + \frac{1}{2} + \frac{1}{3} + \frac{1}{4} + \frac{1}{5} + \frac{1}{6}\right) = \frac{1}{6} \times \frac{49}{20} = \frac{49}{120} = \mathbf{0.408333}\ldots$$

**Conclusion**: The reported values ($0.1667$ and $0.4083$) are the **exact theoretical values of a balanced 6-class uniform random guessing protocol**.

---

### Protocol B: Gallery-Proportional Random Image Retrieval
If a random image is drawn uniformly from the gallery of $N - 1 = 4,590$ candidate images without class rebalancing:
The Carinthia dataset contains severe class imbalance across its 4,591 images:
- Class 1: 55 images ($1.20\%$)
- Class 2: 8 images ($0.17\%$)
- Class 3: 4,008 images ($87.30\%$)
- Class 4: 289 images ($6.29\%$)
- Class 5: 4 images ($0.09\%$)
- Class 6: 227 images ($4.94\%$)

For a query $q$ belonging to class $c$, the number of valid positives in the gallery is $N_c - 1$. The expected Micro R@1 for a uniform random gallery draw is:
$$\mathbb{E}[\text{Micro R@1}_{\text{gallery}}] = \frac{1}{N} \sum_{c=1}^C \frac{N_c(N_c - 1)}{N - 1}$$
Computing for each class:
- $N_1 = 55$: $55 \times 54 = 2,970$
- $N_2 = 8$: $8 \times 7 = 56$
- $N_3 = 4008$: $4008 \times 4007 = 16,060,056$
- $N_4 = 289$: $289 \times 288 = 83,232$
- $N_5 = 4$: $4 \times 3 = 12$
- $N_6 = 227$: $227 \times 226 = 51,302$
- Sum $= 16,197,628$

$$\mathbb{E}[\text{Micro R@1}_{\text{gallery}}] = \frac{16,197,628}{4591 \times 4590} = \frac{16,197,628}{21,072,690} = \mathbf{0.76865} \quad (\approx 76.87\%)$$

Because Class 3 constitutes $87.3\%$ of the corpus, an uncalibrated random image pick achieves $76.87\%$ top-1 accuracy simply by exploiting majority class frequency.

Conversely, the expected Macro R@1 under unweighted gallery sampling is:
$$\mathbb{E}[\text{Macro R@1}_{\text{gallery}}] = \frac{1}{C} \sum_{c=1}^C \frac{N_c - 1}{N - 1} = \frac{1}{6} \left(\frac{4591 - 6}{4590}\right) = \frac{4585}{27540} = \mathbf{0.16648} \quad (\approx 16.65\%)$$

---

## 3. Authoritative Reconciliation & Table Relabeling

1. **Preserve Historical Values**: The reported $0.1667$ and $0.4083$ are mathematically exact and must be preserved.
2. **Explicit Labeling**: In all reports and matrices, this baseline is formally relabeled as:
   > **"Random Guessing Baseline (Balanced Uniform 6-Class Prior: $1/C = 0.1667$, $H_C/C = 0.4083$)"**
3. **Gallery-Weighted Baseline Noted**: The gallery-weighted random draw baseline ($0.7687$ Micro, $0.1665$ Macro) is documented as an explanatory reference for the effect of severe class imbalance.
