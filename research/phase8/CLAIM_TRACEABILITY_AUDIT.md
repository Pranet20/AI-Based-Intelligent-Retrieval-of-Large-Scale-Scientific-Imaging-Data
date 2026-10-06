# Claim & Numerical Traceability Audit

**Document:** `SCI_INTEL_IEEE_FINAL_MANUSCRIPT.docx` and `.pdf`  
**Grounding Source:** `research/phase7/CLAIM_TO_EVIDENCE_MATRIX.csv`  
**Status:** 100% NUMERICAL TRACEABILITY VERIFIED  

---

| Numerical Value in Manuscript | Context in Manuscript | Mapped Claim ID | Grounding Artifact | Exact Match? |
|:---:|:---|:---:|:---|:---:|
| **66.23%** | Mean acquisition gap reduction | `CLM-001` | `representation_tradeoff.csv` | **YES** |
| **0.2016** | Frozen DINOv2 acquisition gap | `CLM-001` | `representation_tradeoff.csv` | **YES** |
| **0.0681** | Phase-4 adapted acquisition gap | `CLM-001` | `representation_tradeoff.csv` | **YES** |
| **p = 5.03e-36** | Wilcoxon signed-rank test p-value | `CLM-001` | `geometry_results.csv` | **YES** |
| **dz = 2.19** | Cohen's dz paired effect size | `CLM-001` | `geometry_results.csv` | **YES** |
| **0.9921** | Phase-4 ensemble Recall@5 under Protocol U | `CLM-002` | `retrieval_results.csv` | **YES** |
| **0.9858** | Frozen DINOv2 Recall@5 under Protocol U | `CLM-002` | `retrieval_results.csv` | **YES** |
| **0.5261** | Phase-4 ensemble MRR under Protocol U | `CLM-002` | `retrieval_results.csv` | **YES** |
| **0.5200** | Frozen DINOv2 MRR under Protocol U | `CLM-002` | `retrieval_results.csv` | **YES** |
| **0.6837** | Frozen DINOv2 artifact Macro F1 | `CLM-003` | `quality_comparison.csv` | **YES** |
| **0.6323** | Phase-4 adapted artifact Macro F1 | `CLM-003` | `quality_comparison.csv` | **YES** |
| **0.8582** | Frozen DINOv2 artifact AUROC | `CLM-003` | `quality_comparison.csv` | **YES** |
| **0.8230** | Phase-4 adapted artifact AUROC | `CLM-003` | `quality_comparison.csv` | **YES** |
| **0.4454** | Spatial localization mean IoU | `CLM-005` | `localization_results.csv` | **YES** |
| **0.5103** | Spatial localization mean Dice | `CLM-005` | `localization_results.csv` | **YES** |
| **100.0%** | Valid comparative evidence availability | `CLM-007` | `counterfactual_evidence_results.csv` | **YES** |
| **23.40 ms** | Complete pipeline serial mean latency | `CLM-008` | `latency_results.csv` | **YES** |
| **28.30 ms** | Complete pipeline serial P95 latency | `CLM-008` | `latency_results.csv` | **YES** |
| **6,085** | Active dataset micrographs | Phase 1 Manifest | `FINAL_IMAGE_MANIFEST.json` | **YES** |
| **427 / 135 / 212** | HCCI train / val / test split counts | Phase 1 Split | `hcci_instrument_splits.json` | **YES** |

**Audit Determination:** **20 / 20 PASS (100% Traceability)**
