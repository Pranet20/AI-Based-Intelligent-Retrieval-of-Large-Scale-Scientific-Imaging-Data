# Canonical Claim-to-Evidence Traceability Map

This map connects every scientific claim (C1–C10) to its corresponding research question, experiment, source code, data artifact, and test assertion.

---

| Claim ID | Formal Scientific Claim | Target RQ | Implementation Module | Source Data / Artifact | Canonical Metric & Proof | Automated Test Assertion |
|:---:|:---|:---:|:---|:---|:---|:---:|
| **C1** | DINOv2 provides a high-performing zero-shot visual foundation baseline for scientific microscopy retrieval. | RQ1 | `src/representation/` | `research/results/freeze1/retrieval_results.json` | Protocol U: Top-5 Acc = 0.9858, MRR = 0.5200 | `tests/test_phase2_retrieval.py` |
| **C2** | Contrastive linear adaptation reduces the observed acquisition-geometry similarity gap by 66.23%. | RQ2 | `src/adaptation/` | `research/results/phase3/acquisition_pairs.csv` | Gap reduced from 0.2016 to 0.0681 ($p = 5.03\times 10^{-36}$, $d_z = 2.19$) | `tests/test_phase3_acquisition_robustness.py` |
| **C3** | Retrieval quality is preserved and improved under unconstrained distractors (Protocol U). | RQ1 | `src/adaptation/` | `research/results/phase3/retrieval_results.csv` | Multi-seed Ensemble Top-5 Acc = 0.9921 (vs 0.9858 baseline) | `tests/test_phase3_faiss.py` |
| **C4** | Visual screening with frozen DINOv2 identifies image quality risks with high precision. | RQ3 | `src/evidence/quality_risk_engine.py` | `research/results/phase4/classification_results.csv` | AUROC = 0.8582, AUPRC = 0.9841, F1 = 0.9632 | `tests/test_phase4_quality_anomaly.py` |
| **C5** | Patch saliency localizes model-derived suspicious regions effectively. | RQ4 | `src/evidence/localization_engine.py` | `research/results/phase4/localization_results.csv` | Macro IoU = 0.4454, Dice = 0.5103 across 10 categories | `tests/test_phase4_evaluation.py` |
| **C6** | High confidence selective prediction requires high abstention rates, necessitating human oversight. | RQ4 | `src/evidence/schemas.py` | `research/results/phase4/calibration_results.csv` | 100% selective accuracy requires 90.27% abstention rate | `tests/test_phase4_quality_anomaly.py` |
| **C7** | Grounded evidence retrieval reliably links queries to comparable same-specimen reference micrographs. | RQ4 | `src/evidence/retrieval_evidence_engine.py` | `research/results/phase6/evidence_results.csv` | 100% valid evidence availability in $N=55$ cohort | `tests/test_phase5_evidence_intelligence.py` |
| **C8** | Dual representations operate effectively as independent architectural components without learned fusion. | RQ2 & RQ3 | `platform/backend/app/api/search.py` | `research/results/phase6/dual_representation_results.csv` | Branch A (screening) & Branch B (retrieval) separation | `platform/tests/test_api.py` |
| **C9** | Multi-image duplicate cascade identifies bitwise and perceptual redundancy with cluster grouping. | RQ5 | `platform/backend/app/services/multi_image.py` | `research/results/phase6/integrated_results.csv` | Stage 1–5 cascade, SSIM $\ge 0.95$ near-duplicate detection | `platform/tests/test_multi_image_workflow.py` |
| **C10** | End-to-end platform executes all 17 lifecycle stages with sub-30 ms interactive latency and audit provenance. | RQ5 | `platform/backend/app/` | `research/results/phase6/latency_results.csv` | Total latency = 23.40 ms (mean), 28.30 ms ($P_{95}$) | `platform/tests/test_canonical_end_to_end.py` |
