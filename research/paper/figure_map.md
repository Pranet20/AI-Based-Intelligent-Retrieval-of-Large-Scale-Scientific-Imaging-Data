# Manuscript Figure Specifications & Captions

All figures are compiled in vector PDF and 300 DPI PNG under `research/figures/`.

---

### Figure 1: SCI-INTEL System Architecture
- **File:** `research/figures/fig1_system_architecture.png` (PDF: `fig1_system_architecture.pdf`)
- **Caption:** *Fig. 1. End-to-end SCI-INTEL platform architecture illustrating the 17-stage scientific research lifecycle connecting raw micrograph ingestion, TIFF metadata extraction, strict dual representation generation, quality-risk screening, acquisition-aware vector retrieval, grounded evidence retrieval, and human curatorial review with tamper-evident audit logging.*
- **Placement:** Top of Page 2 (Width: Double Column / 2-column span).

### Figure 2: Dual Representation Separation Framework
- **File:** `research/figures/fig2_dual_representation_framework.png` (PDF: `fig2_dual_representation_framework.pdf`)
- **Caption:** *Fig. 2. Strict dual representation workflow. Input micrographs are processed by a frozen DINOv2 ViT-S/14 visual backbone (384 dimensions). Branch A utilizes the frozen baseline embeddings for quality-risk and artifact screening. Branch B projects representations through a linear adaptation head ($384 \to 384$) optimized for acquisition-geometry invariance and multi-instrument vector search.*
- **Placement:** Column 1, Page 3.

### Figure 3: Acquisition-Geometry Similarity Gap Reduction
- **File:** `research/figures/fig3_acquisition_robustness.png` (PDF: `fig3_acquisition_robustness.pdf`)
- **Caption:** *Fig. 3. Comparison of cosine similarity distributions and similarity gap ($\Delta$) between within-acquisition and cross-acquisition pairs on the evaluated $N=55$ matched query cohort. The contrastive linear adapter compresses the observed similarity gap from $0.2016$ to $0.0681$, achieving a $66.23\%$ gap reduction (Wilcoxon $W=21743$, $p=5.03\times 10^{-36}$, $d_z=2.19$).*
- **Placement:** Column 2, Page 3.

### Figure 4: Protocol U Retrieval Performance & Protocol Separation
- **File:** `research/figures/fig4_retrieval_performance.png` (PDF: `fig4_retrieval_performance.pdf`)
- **Caption:** *Fig. 4. Retrieval evaluation across protocols: (a) Protocol U Top-5 retrieval accuracy across perceptual hashing, deep ResNet-50 baselines, frozen DINOv2, and multi-seed Phase 4 ensemble ($99.21\%$). (b) Protocol M (masked distractors; intra-acquisition discriminability) vs. Protocol U (unmasked distractors; cross-acquisition robustness) metric separation.*
- **Placement:** Column 1, Page 4.

### Figure 5: Quality-Risk Classification & Selective Abstention
- **File:** `research/figures/fig5_quality_risk_curves.png` (PDF: `fig5_quality_risk_curves.pdf`)
- **Caption:** *Fig. 5. Quality assessment performance: (a) Receiver Operating Characteristic (AUROC = 0.8582) and Precision-Recall (AUPRC = 0.9841) metric comparison across feature spaces. (b) Coverage versus selective accuracy trade-off under uncertainty thresholding ($\tau$). Achieving 100% selective precision requires a 90.27% abstention rate, necessitating human-in-the-loop curation.*
- **Placement:** Column 2, Page 4.

### Figure 6: Model-Derived Suspicious Region Localization
- **File:** `research/figures/fig6_localization_performance.png` (PDF: `fig6_localization_performance.pdf`)
- **Caption:** *Fig. 6. Spatial localization performance across 10 controlled artifact categories evaluated on $N=500$ synthetic test masks. The patch-level saliency engine achieves a Macro Mean Intersection-over-Union (IoU) of $0.4454$ and a Dice coefficient of $0.5103$.*
- **Placement:** Optional Extended Appendix / Supplementary.

### Figure 7: Integrated Curation & Human Governance Workflow
- **File:** `research/figures/fig7_curation_workflow.png` (PDF: `fig7_curation_workflow.pdf`)
- **Caption:** *Fig. 7. Grounded evidence intelligence and curation workflow. Degraded query micrographs are linked with same-specimen, cross-instrument reference exemplars from the $N=55$ cohort, generating actionable corrective guidelines before curatorial decision logging.*
- **Placement:** Optional Extended Appendix / Supplementary.
