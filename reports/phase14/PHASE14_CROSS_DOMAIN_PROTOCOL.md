# Phase 14 Cross-Domain Generalization Protocol

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Scope:** Multi-Domain Evaluation Protocol across Scientific Microscopy Regimes

---

## 1. Objective & Hypothesis

The cross-domain generalization protocol evaluates whether self-supervised visual representations (DINOv2 ViT-S/14) and domain-adapted embeddings generalize beyond the single-instrument HCCI metallurgy benchmark to diverse microscopy modalities and application domains without data leakage.

**Central Hypothesis (H2):**  
Self-supervised patch-token representations preserve microstructural clustering across distinct specimen classes (e.g. industrial defects, biological tissues), but exhibit quantifiable performance shifts driven by modality differences (SEM vs TEM) and severe class imbalance.

---

## 2. Participating Domains & Data Governance

1. **Domain A (Ferrous Metallurgy SEM — HCCI):**
   - Modality: Secondary and Backscattered Electron SEM (Zeiss Gemini)
   - Size: 774 valid physical micrographs
   - Role: In-domain baseline and source training split
   - Rights: Restricted to local research (`RIGHTS_UNVERIFIED` on Zenodo)
2. **Domain B (Industrial Semiconductor Defects — Carinthia):**
   - Modality: Industrial SEM
   - Size: 4,591 micrographs across 6 defect classes
   - Role: Target zero-shot transfer and leave-one-out nearest-neighbor evaluation
   - Rights: Restricted to local research (`RIGHTS_UNVERIFIED` on Zenodo)
3. **Domain C (Biological Cellular Structures — Bio-Image TEM):**
   - Modality: Transmission Electron Microscopy (TEM)
   - Size: 1,200 micrographs
   - Role: Cross-modality zero-shot and fine-tuned transfer
   - Rights: Public research access (CC BY 4.0)

---

## 3. Evaluation Tasks & Anti-Leakage Safeguards

- **Task 1: In-Domain vs Cross-Domain Shift Quantification:**
  Compute global centroid cosine similarity and Euclidean distance in normalized embedding space:
  $$\text{Sim}_{\text{domain}}(A, B) = \cos(\bar{z}_A, \bar{z}_B) = \frac{\bar{z}_A \cdot \bar{z}_B}{\|\bar{z}_A\|_2 \|\bar{z}_B\|_2}$$
- **Task 2: Leave-One-Out Nearest-Neighbor Retrieval (Domain B):**
  For each sample $x_i \in \text{Carinthia}$, retrieve top-1 nearest neighbor in $\text{Carinthia} \setminus \{x_i\}$. Measure micro and macro-averaged Recall@1 across all 6 defect classes to eliminate frequency bias from dominant Class 3 (87.3% of corpus).
- **Task 3: Cross-Modality Zero-Shot Evaluation (Domain A $\to$ Domain C):**
  Evaluate retrieval on TEM cellular micrographs using embeddings extracted directly by the SEM-calibrated model.
- **Anti-Leakage Safeguard:** No embeddings from Domain B or Domain C were included in the Phase 4 supervised contrastive training loss. Evaluation is strictly zero-shot.
