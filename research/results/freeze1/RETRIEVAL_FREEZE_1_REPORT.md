# SCI-INTEL: Retrieval Freeze 1 Benchmark Report
## Controlled Acquisition-Aware Same-Specimen Retrieval on Frozen Phase 1 Data

**Protocol:** `research/protocols/retrieval_freeze_1.yaml`  
**Dataset Reference:** HCCI (774 active scientific micrographs)  
**Evaluation Partition:** Held-Out Zeiss Gemini Test Split (212 micrographs)  
**Gallery Size:** 211 candidates per query (self excluded)  
**Deterministic Reproducibility:** PASS (Verified exact match)  
**Audit Date:** 2026-10-05  

---

## 1. Scientific Verification & Partition Integrity

| Check | Expected | Observed | Status |
|---|---|---|---|
| HCCI Total Images | 774 | 774 | PASS |
| Train Partition (Helios) | 427 | 427 | PASS |
| Val Partition (VEGA3) | 135 | 135 | PASS |
| Test Partition (Zeiss Gemini) | 212 | 212 | PASS |
| Train-Test Image ID Overlap | 0 | 0 | PASS |
| Train-Test SHA-256 Collision | 0 | 0 | PASS |
| Train-Test Near-Duplicate Overlap | 0 | 0 | PASS |
| Specimen Overlap ($|S_{\text{train}} \cap S_{\text{test}}|$) | 3 physical alloys | 3 physical alloys (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`) | VERIFIED |

> **Scientific Governance Statement:** In full adherence to transparent reporting, all 3 metallurgical steel alloys (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`) exist across training (Helios instruments), validation (VEGA3 instrument), and held-out testing (Zeiss Gemini instrument). The task is rigorously defined as **Acquisition-Aware Cross-Instrument Same-Specimen Retrieval**, evaluating representation invariance across electron optics, acceleration voltages, and detectors. It is NOT unseen-specimen generalization or novel alloy discovery.

---

## 2. Benchmark Results Table

| Model Architecture | Feature Dim | Recall@1 [95% CI] | Recall@5 | Recall@10 | MRR [95% CI] | Precision@5 [95% CI] | Latency (Mean / p95 ms) | Index (KB) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Perceptual Hash (pHash)** | 64 | 0.0991 [0.0613, 0.1368] | 0.9717 | 1.0000 | 0.4894 [0.4627, 0.5168] | 0.6736 [0.6462, 0.7028] | 2.92 / 4.11 | 1.66 |
| **Difference Hash (dHash)** | 64 | 0.1085 [0.0660, 0.1509] | 0.9481 | 0.9717 | 0.4995 [0.4722, 0.5253] | 0.6236 [0.5915, 0.6538] | 2.78 / 3.19 | 1.66 |
| **ResNet-50 (ImageNet-1K)** | 2048 | 0.0802 [0.0425, 0.1179] | 0.9811 | 1.0000 | 0.4836 [0.4588, 0.5090] | 0.5726 [0.5434, 0.6028] | 2.00 / 2.78 | 1696.00 |
| **DINOv2 ViT-S/14 (Frozen)** | 384 | 0.1321 [0.0896, 0.1792] | 0.9858 | 1.0000 | 0.5200 [0.4943, 0.5478] | 0.6160 [0.5887, 0.6453] | 0.52 / 0.69 | 318.00 |
| **Phase-4 Adapter (Seed 42)** | 384 | 0.1321 [0.0896, 0.1792] | 0.9953 | 1.0000 | 0.5230 [0.4974, 0.5502] | 0.6321 [0.6047, 0.6594] | 0.50 / 0.62 | 318.00 |
| **Phase-4 Adapter (Seed 123)** | 384 | 0.1462 [0.1038, 0.1934] | 0.9906 | 1.0000 | 0.5214 [0.4935, 0.5501] | 0.6217 [0.5943, 0.6491] | 0.52 / 0.62 | 318.00 |
| **Phase-4 Adapter (Seed 2024)** | 384 | 0.1557 [0.1085, 0.2028] | 0.9906 | 1.0000 | 0.5338 [0.5076, 0.5625] | 0.6443 [0.6160, 0.6717] | 0.61 / 0.83 | 318.00 |
| **Phase-4 Adapter (3-Seed Mean)** | 384 | **0.1447 ± 0.0097** | **0.9921 ± 0.0022** | **1.0000 ± 0.0000** | **0.5261 ± 0.0055** | **0.6327 ± 0.0093** | **0.54** | **318.00** |

---

## 3. Detailed Error and Failure Mode Analysis

### A. Individual Model Top-5 Success and Failure Breakdown
In strict concordance with individual model evaluations over all 212 test queries:
- **Perceptual Hash (pHash):** 206 / 212 successful (6 failed queries, exact Recall@5 = 0.971698)
- **Difference Hash (dHash):** 201 / 212 successful (11 failed queries, exact Recall@5 = 0.948113)
- **ResNet-50 (ImageNet-1K):** 208 / 212 successful (4 failed queries, exact Recall@5 = 0.981132)
- **DINOv2 ViT-S/14 (Frozen):** 209 / 212 successful (3 failed queries, exact Recall@5 = 0.985849)
- **Phase-4 Adapter (Seed 42):** 211 / 212 successful (1 failed query, exact Recall@5 = 0.995283)
- **Phase-4 Adapter (Seed 123):** 210 / 212 successful (2 failed queries, exact Recall@5 = 0.990566)
- **Phase-4 Adapter (Seed 2024):** 210 / 212 successful (2 failed queries, exact Recall@5 = 0.990566)
- **Simultaneous Failure Across All Models:** 0 / 212 queries (0.0%) failed simultaneously across all models at top-5. Every query was successfully retrieved in top-5 by at least one model family.

### B. Cross-Model Win/Loss Comparison
- **Queries failing across ALL evaluated models at R@1 (R@1=0):** 155 / 212 (73.1%)
- **Queries failing across ALL evaluated models at R@5 (R@5=0):** 0 / 212 (0.0%)
- **DINOv2 ViT-S/14 wins over ResNet-50 (DINOv2 R@1=1, ResNet R@1=0):** 21 queries
- **ResNet-50 wins over DINOv2 (ResNet R@1=1, DINOv2 R@1=0):** 10 queries
- **Phase-4 Adapter (Seed 42) wins over Frozen DINOv2 (Adapter R@1=1, DINOv2 R@1=0):** 1 query
- **Frozen DINOv2 wins over Phase-4 Adapter (Seed 42) (DINOv2 R@1=1, Adapter R@1=0):** 1 query

### C. Performance by Detector Type (SE vs. BSE vs. InLens)
| Detector | Count | ResNet-50 R@1 | DINOv2 R@1 | Phase-4 Adapter R@1 |
|---|:---:|:---:|:---:|:---:|
| **Secondary Electron (SE)** | 71 | 0.0986 | 0.2254 | 0.2113 |
| **Backscattered Electron (BSE)** | 71 | 0.0845 | 0.1549 | 0.1690 |
| **InLens Detector** | 70 | 0.0571 | 0.0143 | 0.0143 |

### D. Performance by Accelerating Voltage (kV)
| Voltage | Count | ResNet-50 R@1 | DINOv2 R@1 | Phase-4 Adapter R@1 |
|---|:---:|:---:|:---:|:---:|
| **5.0 kV** | 71 | 0.0423 | 0.1549 | 0.1549 |
| **10.0 kV** | 71 | 0.1127 | 0.1408 | 0.1408 |
| **20.0 kV** | 70 | 0.0857 | 0.1000 | 0.1000 |

### E. Scientifically Conservative Interpretation of Retrieval Variations
The following failure patterns represent observational correlations and empirical hypotheses:
1. **Observed InLens-Associated Retrieval Degradation:** Micrographs captured using the InLens detector exhibit significantly reduced rank-1 retrieval rates across all representation models (0.0143 for DINOv2 and Adapter vs. 0.2254 for SE). InLens detectors predominantly collect low-energy secondary electrons along the electron beam axis, resulting in distinct edge contrast and surface potential characteristics that differ from standard chamber detectors.
2. **Possible Detector-Dependent Contrast/Morphology Shift:** Secondary Electron (SE) micrographs prioritize topographical relief, while Backscattered Electron (BSE) micrographs capture atomic number density variations. Discrepancies between SE and BSE representations suggest that cross-detector alignment remains an ongoing challenge for generic vision models.
3. **Potential Acquisition Artifacts:** Sub-micron localized scanning at higher beam currents may introduce carbon deposition contamination or slight astigmatic blur, presenting visual perturbations that degrade cosine similarity. These physical mechanisms are posited as potential causes rather than conclusively proven within this single benchmark.

---

## 4. Reproducibility Evidence Hash

```ini
RERUN_EQUALITY_VERIFIED=True
BENCHMARK_STATUS=VERIFIED
```
