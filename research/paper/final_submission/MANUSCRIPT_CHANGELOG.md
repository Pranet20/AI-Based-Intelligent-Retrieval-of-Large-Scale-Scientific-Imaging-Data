# Manuscript Changelog & Engineering Decisions

1. **Title Selection:**
   - Evaluated candidate titles: Selected *SCI-INTEL: Acquisition-Aware Retrieval and Quality-Risk Curation of Scientific Microscopy Images*.
   - Rationale: Most concise and accurate representation of the paper's core dual contribution (acquisition robustness + quality-risk curation).

2. **Author-Neutral Byline:**
   - In accordance with the prompt's explicit mandate, all student names (Pranet Pallati, Charan Deep, Pooja Vunnam), roll numbers, guide names (Ms. C. Bhavana), and institutional emails were omitted from manuscript text, document properties, and image metadata.
   - Inserted a standard double-blind / author-neutral placeholder: `[Author names, academic affiliations, and email addresses omitted for initial peer review / to be populated prior to publication]`.

3. **Architecture Diagram Redesign:**
   - Produced `figures/architecture_final.png`, `architecture_final.pdf`, and `architecture_final.svg`.
   - Distinctly rendered the 5 operational layers: (1) Ingestion & Integrity, (2) Dual Representations (Branch A: Frozen DINOv2 vs Branch B: Phase-4 Adapter), (3) Deterministic Orchestration, (4) Explanation & Uncertainty Abstention, and (5) Human-Governed Curation & Audit.
   - Explicitly clarified that Branch A and Branch B are separate 384-d representations with NO learned fusion.

4. **Strict 4+1 Page Budget Calibration:**
   - Calibrated paragraph leads and table paddings so all technical narrative, equations, Table I, and Fig. 1 fit within Pages 1–4.
   - Placed PageBreak right after Conclusion to ensure References and Ethical Standards sit cleanly on Page 5, preventing disqualifying technical spillover.

5. **Reference Reconciliation:**
   - Preserved all 29 authentic literature citations covering microscopy CBIR, Vision Transformers, DINOv2, contrastive metric learning, vector indexing (FAISS/HNSW), BRISQUE, SSIM, MVTec, calibration, and FAIR data principles.
