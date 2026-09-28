# P19 STATISTICAL TEST AUDIT & INFERENTIAL BOUNDARY

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: Statistical Audit of P19 Inferential Tests ($p < 10^{-15}$)  
**Date**: 2026-09-27  
**Status**: AUDITED_AND_RESTRICTED  

---

## 1. Audit Scope & Claimed Values

In Phase 19 reporting, the comparative evaluation between DINOv2 ViT-S/14, CLIP ViT-B/32, and ResNet-50 included:
- DINOv2 vs CLIP: $\Delta = +21.12\%$ Micro R@1, claimed *"Wilcoxon signed-rank test $p < 10^{-15}$"*
- DINOv2 vs ResNet-50: $\Delta = +35.32\%$ Micro R@1, claimed *"Wilcoxon signed-rank test $p < 10^{-15}$"*

---

## 2. Forensic Audit Findings

| Audit Parameter | Declared Protocol | Empirical Status in Repository |
|---|---|---|
| **Statistical Test** | Paired Wilcoxon signed-rank test / McNemar's test | Declared in text |
| **Unit of Analysis** | Binary indicator $\mathbb{I}[\text{top-1 correct}]$ per query ($N=4,591$) | Queried leave-one-out |
| **Null Hypothesis ($H_0$)** | The median paired difference in top-1 retrieval indicator is zero | Standard paired formulation |
| **Paired Query Arrays** | Per-query 0/1 vectors for CLIP and ResNet-50 | **NOT PERSISTED IN LOCAL REPO** |
| **Test Statistic Value ($W$ or $Z$)** | Unreported raw test statistic | Absent from raw output |
| **P-Value Derivation** | Asymptotic normal approximation for large $N$ | Calculated in transient memory |

### Key Finding:
While the aggregate point estimates (DINOv2: 0.9952 vs CLIP: 0.7840 and ResNet-50: 0.6420) represent enormous effect sizes on $N = 4,591$ samples where an asymptotic paired test mathematically yields $Z > 15$ ($p < 10^{-15}$), the **underlying per-query paired binary vector files are not committed to the repository artifacts**. 

Therefore, retaining an exact inferential claim of $p < 10^{-15}$ violates strict artifact-traceability standards.

---

## 3. Remediation & Claim Demotion

In strict compliance with audit instructions:
1. **Remove Inferential $p$-value from Formal Claims**:
   - The inferential claim *"statistically significant superiority with $p < 10^{-15}$"* is demoted to a **purely descriptive empirical comparison**.
2. **Authoritative Claim Language**:
   > **"Under the evaluated nearest-neighbor class retrieval protocol on the Carinthia defect corpus, DINOv2 achieved substantially higher Micro R@1 (0.9952) than zero-shot CLIP ViT-B/32 (0.7840) and supervised ResNet-50 (0.6420)."**
3. **Traceability Status**: Marked as `DESCRIPTIVE_ONLY_TRACEABLE` in the Claim-Evidence Graph. No replacement $p$-value is manufactured.
