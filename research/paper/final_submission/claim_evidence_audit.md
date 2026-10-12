# Manuscript Claim-to-Evidence Traceability Audit
**Document:** `SCI_INTEL_ISBI2027_Manuscript.docx` and `SCI_INTEL_ISBI2027_Manuscript.pdf`  
**Grounding Source:** `research/results/phase6/` and `docs/CANONICAL_RESEARCH_EVIDENCE_MANIFEST.md`  
**Status:** 100% NUMERICAL TRACEABILITY VERIFIED  

| Claim ID | Manuscript Statement | Grounding Artifact | Code / Test Source | Protocol | Grounded Value | Verification Status |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **CLM-001** | Acquisition-geometry gap reduced by 66.23% (0.2016 to 0.0681, p=5.03e-36, dz=2.19) | `research/results/phase6/representation_tradeoff.csv` | `tests/test_phase3_acquisition_robustness.py` | Protocol U, N=210 paired | 66.23% (p=5.03e-36) | **PASS** |
| **CLM-002** | Adapter achieves Recall@5 of 0.9921 and MRR of 0.5261 under Protocol U | `research/results/freeze1/retrieval_results.csv` | `tests/test_phase2_retrieval_freeze.py` | Protocol U (212 queries, 211 distractors) | R@5 = 0.9921, MRR = 0.5261 | **PASS** |
| **CLM-003** | Frozen DINOv2 has superior artifact sensitivity (Macro F1=0.6837, AUROC=0.8582 vs 0.6323, 0.8230) | `research/results/phase6/quality_comparison.csv` | `tests/test_phase4_quality_anomaly.py` | 11-class synthetic benchmark (N=1,100) | DINOv2 F1=0.6837 vs Adapter 0.6323 | **PASS** |
| **CLM-004** | Dual representations composed deterministically without learned fusion | `research/results/phase6/dual_representation_results.csv` | `tests/test_phase6_validation_suite.py` | Architectural composition | Macro F1=0.6837 & R@5=0.9921 | **PASS** |
| **CLM-005** | Model-derived suspicious-region localization attains Mean IoU 0.4454 and Dice 0.5103 | `research/results/phase6/localization_results.csv` | `tests/test_phase4_quality_anomaly.py` | N=500 synthetic spatial masks | IoU = 0.4454, Dice = 0.5103 | **PASS** |
| **CLM-006** | Uncertainty abstention gates cases with conf < 0.40 or entropy > 0.75 | `research/results/phase6/uncertainty_results.csv` | `tests/test_phase4_quality_anomaly.py` | Selective prediction | Selective Acc = 99.08% at tau=0.4 | **PASS** |
| **CLM-007** | Comparative evidence available for 100.0% of evaluated N=55 query cohort | `research/results/phase6/counterfactual_evidence_results.csv` | `tests/test_phase5_evidence_intelligence.py` | N=55 query cohort | 100.0% availability, 0% duplicates | **PASS** |
| **CLM-008** | Serial pipeline latency averaged 23.40 ms (P95 28.30 ms) on benchmark testbed | `research/results/phase6/latency_results.csv` | `tests/test_phase6_validation_suite.py` | 55 serial queries on CPU | Mean 23.40 ms, P95 28.30 ms | **PASS** |
| **CLM-009** | Saturated visual representations render late score-level metadata fusion redundant | `research/results/phase5/metadata_fusion_results.csv` | `tests/test_phase5_fusion.py` | Validation grid search | Delta R@1 = 0.0000 (alpha* = 1.0) | **PASS** |
| **CLM-010** | Active repository micrographs total 6,085 (HCCI: 774, Carinthia: 4,591, BBBC021: 720) | `research/final_manifests/FINAL_IMAGE_MANIFEST.json` | `tests/test_phase1_data_freeze.py` | Repository manifest | 6,085 active micrographs | **PASS** |

**Determination:** 10 / 10 Canonical Claims Validated. 0 Stale or Hallucinated Values.
