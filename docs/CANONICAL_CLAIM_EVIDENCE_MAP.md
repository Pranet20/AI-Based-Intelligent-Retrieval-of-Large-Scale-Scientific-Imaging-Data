# SCI-INTEL Canonical Scientific Claim-to-Evidence Traceability Map

**Platform:** SCI-INTEL — Scientific Imaging Intelligence Platform  
**Repository:** `Pranet20/AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data`  
**Classification:** CURRENT SCIENTIFIC TRACEABILITY MATRIX  

---

## 1. Traceability Methodology

Every empirical claim made in the manuscript, platform documentation, and IEEE submission package is mapped directly to:
1. Target Research Phase
2. Specific Frozen Metric Value
3. Mathematical Definition & Protocol
4. Source Code Implementation File
5. Frozen Result / Evidence Artifact
6. Cryptographic Hash or Checksum

---

## 2. Claim-to-Evidence Matrix

| Claim ID | Paper / Platform Claim Statement | Research Phase | Authoritative Metric | Source Implementation File | Authoritative Result Artifact | Verification Hash / Seal |
| :---: | :--- | :---: | :--- | :--- | :--- | :--- |
| **C1** | Self-supervised DINOv2 ViT-S/14 serves as an effective foundation visual encoder for scientific micrographs without instrument pretraining. | Phase 2 | Protocol U Top-5 Accuracy = **`0.9858`** (Baseline Top-1: 0.1321, Top-10: 1.0000). | `src/retrieval/embedder.py`, `app/ml/dinov2_engine.py` | `research/results/freeze1/retrieval_results.json` | `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361` |
| **C2** | Supervised contrastive adaptation reduces the observed cross-instrument acquisition similarity gap by 66.23% under the evaluated protocol. | Phase 3 / 4 | Baseline Gap = `0.2016`, Adapted Gap = **`0.0681`**; Relative Reduction = **`66.23%`** ($p = 5.03 \times 10^{-36}$, $d_z = 2.19$). | `src/adaptation/projection_head.py`, `app/ml/phase4_engine.py` | `research/results/phase3/acquisition_robustness_results.json` | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` (Checkpoint) |
| **C3** | Adaptation preserves fine-grained intra-instrument specimen discriminability under matched acquisition conditions (Protocol M). | Phase 2 | Protocol M Recall@1 = **`0.9481`**, MRR = **`0.9658`**. | `src/retrieval/metrics.py` | `research/results/freeze1/retrieval_results.csv` | `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361` |
| **C4** | Computational image-derived quality indicators reliably identify corrupted micrographs without proprietary hardware telemetry. | Phase 4 | Binary Risk AUROC = **`0.8582`**, AUPRC = **`0.9841`**, F1 = **`0.9632`** on synthetic benchmark ($N=1,100$). | `src/integrity/quality_indicators.py`, `src/evidence/quality_risk_engine.py` | `data/processed/phase4/metrics/phase4_evaluation_results.json` | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` (Phase 6 Seal) |
| **C5** | Spatial saliency maps isolate corrupted patches as model-derived suspicious regions without asserting physical defect ground truth. | Phase 4 / 5 | Macro IoU = **`0.4454`**, Dice = **`0.5103`**, Pixel Precision = `0.5259`, Recall = `0.4957` ($N=500$). | `src/evidence/localization_engine.py`, `app/services/ingestion.py` | `research/results/phase4/localization_results.csv` | `a894676be938dc85b08e2cbf1fba453a25cb73a886a1dfae9e3a09722361665a` |
| **C6** | Principled uncertainty evaluation and confidence thresholding enable reliable automated abstention for ambiguous captures. | Phase 4 | At confidence threshold $\tau \ge 0.60$, selective accuracy reaches **`100.0%`** with `90.27%` abstention rate routed to curation queue. | `src/evidence/explanation_generator.py` | `research/results/phase4/calibration_results.csv` | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` |
| **C7** | Grounded reference cohort retrieval ($N=55$) enables deterministic mapping to operational microscope adjustment targets. | Phase 5 / 6 | **100.0%** valid peer retrieval; 10 deterministic operational categories (`beam_current`, `dwell_time`, `gain`, `stigmation`). | `src/evidence/retrieval_evidence_engine.py`, `src/evidence/explanation_generator.py` | `research/results/phase6/evidence_results.csv` | `93e5520120356ec584771eda2a94b9889af9f932de1556674b8c7c4df2141996` |
| **C8** | Dual-representation pipeline provides low-latency inference suitable for interactive scientific micrograph curation. | Phase 6 | End-to-end REST latency = **`23.40 ms`** (mean), **`28.30 ms`** (P95) across full 6-stage evidence pipeline. | `app/api/search.py`, `src/evidence/evidence_aggregator.py` | `research/results/phase6/latency_results.csv` | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` |
| **C9** | Multi-image comparative workflow executes complete pairwise redundancy cascade and collaborative review without autonomous deletion. | Phase 10 | $N(N-1)/2$ pairwise matrix, multi-stage duplicate cascade, graph election, human review logging (`ReviewItem`). | `app/api/multi_image.py`, `app/services/multi_image.py` | `platform/tests/test_multi_image_workflow.py` | Test suite verified (28/28 passed) |
| **C10** | Complete platform lifecycle provides immutable cryptographic provenance and audit logging across all operational events. | Platform | 17-stage canonical workflow preserves SHA-256 hashes, timestamps, user IDs, and provenance parentage trees. | `app/services/provenance.py`, `app/services/audit.py` | `platform/tests/test_canonical_scientific_flow.py` | `test_canonical_scientific_flow_complete` passed |

---

## 3. Boundary & Terminology Enforcement

To maintain rigorous scientific accuracy, the following boundary definitions are programmatically and editorially enforced across the repository:
1. **No "Acquisition Invariance":** The contrastive adapter compresses the observed cross-instrument similarity gap under the tested acquisition regimes; it does not achieve complete or universal invariance.
2. **No "Physical Defect Confirmation":** Saliency overlays identify *model-derived suspicious regions* based on statistical pixel anomalies; physical confirmation requires independent laboratory characterization.
3. **No "Autonomous Curation Decisions":** Automated triage generates *suggested corrective actions* and sorts priority review queues; final curation determinations are made exclusively by domain scientists.
4. **Protocol M and U Separation:** Protocol M (Masked Distractors) and Protocol U (Unmasked Distractors) evaluate distinct operational regimes and are never aggregated or compared without explicit protocol labels.
