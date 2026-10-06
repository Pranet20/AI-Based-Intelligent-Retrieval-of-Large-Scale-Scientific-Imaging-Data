# AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images

### Authors:
1. **Pranet Pallati** (24881A05B7, `24881A05B7@student.vardhaman.org`)
2. **Gollakota Charan Deep** (24881A0586, `24881A0586@student.vardhaman.org`)
3. **Pooja Vunnam** (24881A05B5, `24881A05B5@student.vardhaman.org`)
4. **Ms. C. Bhavana** (Assistant Professor, Guide, `bhavana1817@vardhaman.org`)
*Department of Computer Science and Engineering, Vardhaman College of Engineering, Hyderabad, Telangana, India*

---

## Abstract
Scientific microscopy repositories are expanding rapidly across material science, metallurgy, and biological disciplines, yet downstream search and curation remain severely constrained by acquisition heterogeneity (varying accelerating voltages, detectors, and magnifications) and unquantified image quality risks. Conventional image retrieval pipelines ignore instrument variations and treat corrupted micrographs identically to pristine benchmarks. In this work, we introduce SCI-INTEL, a reproducible platform integrating metadata-aware ingestion, acquisition-aware representation adaptation, controlled artifact screening, spatial suspicious-region localization, uncertainty-aware abstention, and deterministic comparative evidence aggregation. Evaluating on a benchmark of 6,085 scientific micrographs (774 high-chromium cast iron SEM, 4,591 Carinthia SEM, and 720 BBBC021 optical micrographs), we demonstrate that lightweight representation adaptation reduces the observed acquisition-geometry similarity gap by 66.23% (from 0.2016 to 0.0681, p = 5.03e-36, Cohen's dz = 2.19) while achieving Recall@5 of 0.9921 and MRR of 0.5261 under realistic unmasked distractor retrieval (Protocol U). Crucially, our evaluation reveals an empirical trade-off between representation alignment and fine-grained sensitivity: while adapted representations optimize cross-instrument retrieval, frozen DINOv2 ViT-S/14 features retain superior sensitivity to controlled synthetic artifacts (Macro F1 = 0.6837 vs. 0.6323). Rather than training an unverified fusion network, SCI-INTEL resolves this trade-off via a modular dual-representation architecture that routes each representation to its specialized task. Uncertainty-aware abstention safely routes low-confidence cases (confidence < 0.40 or normalized entropy > 0.75) to specialist review, while the evidence layer achieves 100.0% valid comparative micrograph retrieval across an evaluated N=55 query cohort without duplicate artifacts. Our evaluation does not claim unseen-specimen generalization, physical defect confirmation, clinical diagnosis, or human interpretation improvement, providing a transparent, publication-grade foundation for scientific image curation.

**Keywords:** Scientific Image Retrieval, Microscopy, Representation Learning, Acquisition Robustness, Image Quality Assessment, Anomaly Screening, Uncertainty Estimation, Scientific Data Curation, Metadata-Aware Retrieval, Evidence-Based Curation

---

## I. Introduction
Modern scientific microscopy imaging has evolved into an essential foundation for characterization in materials science, crystallography, and biology [12, 14]. Instruments such as scanning electron microscopes (SEM), transmission electron microscopes (TEM), and focused ion beam systems routinely generate millions of high-resolution micrographs. However, retrieving and organizing these images across large-scale distributed archives presents severe bottlenecks [8, 13]. First, acquisition heterogeneity—arising from distinct detector geometries (secondary electron vs. backscattered electron), accelerating voltages, and working distances—induces substantial feature shifts in visual embeddings, causing visually dissimilar micrographs of identical metallurgical structures [7, 12]. Second, raw acquisition archives are frequently corrupted by operational artifacts including beam charging, illumination gradients, and sample contamination, which can silently degrade automated image analysis [18, 19]. Third, standard deep learning classifiers produce overconfident predictions on corrupted or out-of-distribution micrographs without providing provenance or comparative visual evidence [21].

To resolve these interconnected challenges, we present SCI-INTEL, an open, reproducible platform for acquisition-aware scientific image retrieval and quality-aware curation. Our core contributions are:
1. **Acquisition-Aware Representation Adaptation:** We demonstrate that adaptation reduces the acquisition-geometry similarity gap by 66.23% ($p = 5.03 \times 10^{-36}, d_z = 2.19$) and achieves Recall@5 of 0.9921 under Protocol U.
2. **Empirical Specialization Trade-off:** We discover that acquisition alignment trades fine-grained sensitivity to subtle image perturbations, where frozen DINOv2 features outperform adapted representations by +5.14% Macro F1 on controlled artifact screening.
3. **Modular Dual-Representation Architecture:** Rather than training a complex fusion network, SCI-INTEL assigns frozen DINOv2 to quality screening and adapted representations to retrieval, combining their independently validated strengths deterministically.
4. **Uncertainty & Spatial Suspicious-Region Localization:** Model-derived patch saliency achieves mean IoU of 0.4454 across 500 test images, paired with entropy-based abstention routing.
5. **Operational Evidence Retrieval:** An evidence aggregation layer returns valid comparative micrographs for 100.0% of an evaluated $N=55$ query cohort with zero duplicate candidate IDs and 100% provenance completeness.


## II. Related Work
### A. Visual Representation Learning & Foundation Models
Self-supervised Vision Transformers (ViT), notably DINO and DINOv2 [1, 2], learn rich patch- and image-level representations that generalize remarkably well to fine-grained visual structures [3]. However, foundational models trained on natural web imagery do not inherently account for physical microscopy parameters such as electron beam voltage or detector response [14].

### B. Cross-Domain Retrieval & Contrastive Learning
Supervised contrastive learning [5] and domain-invariant adaptation [7] align disparate domains in latent space. In materials science, microstructure retrieval has predominantly utilized static feature descriptors or generic ImageNet pre-training [12, 13], which fail under extreme detector shifts.

### C. Image Quality Assessment & Uncertainty Estimation
No-reference image quality assessment traditionally employs natural scene statistics [18, 19]. In scientific curation, automated quality triage must identify localized artifacts without confusing them with genuine microstructural phases [14]. Selective prediction frameworks provide calibrated safety mechanisms by abstaining when predictive entropy exceeds bounded thresholds [21].

## III. System Architecture & Methodology
The SCI-INTEL architecture is structured into a serial, deterministic curation chain (Fig. 1):
- **Metadata Ingestion & Normalization:** Ingests TIFF/PNG micrographs, extracts instrument metadata (detector, voltage, magnification), and assigns immutable NIST SHA-256 digests [22].
- **Dual Representation Generation:** Computes 384-dimensional embeddings via frozen DINOv2 ViT-S/14 (for quality assessment) and Phase-4 adapted projections (for cross-instrument retrieval).
- **Quality-Risk Screening:** Evaluates high-frequency variance, dynamic range, and Shannon entropy; classifies micrographs across 11 artifact classes using validation-calibrated thresholds.
- **Spatial Localization:** Computes patch-level feature residual saliency maps at native resolution, extracting model-derived suspicious regions.
- **Uncertainty-Aware Abstention:** Computes normalized Shannon entropy $H_{\text{norm}}(p)$ and top-2 margin $\Delta$. Automatically triggers abstention when confidence $< 0.40$ or $H_{\text{norm}} > 0.75$.
- **Evidence Retrieval & Aggregation:** Queries Faiss vector indexes [9] to retrieve same-specimen cross-acquisition peers and clean baseline exemplars with deterministic lexical tie-breaking.


## IV. Experimental Protocol & Reproducibility
### A. Dataset Partitions
Experiments are conducted on 6,085 active micrographs:
- **HCCI SEM (774 images):** Partitioned by instrument and acquisition run into 427 training, 135 validation, and 212 test micrographs. All partitions contain the declared specimen classes (AsCast, Q980_9h_AC, Q980_0h_WC); unseen-specimen generalization is explicitly excluded.
- **Carinthia SEM (4,591 images):** Evaluated for cross-domain anomaly and distribution shift screening.
- **BBBC021 Optical (720 images):** Evaluated for multi-modal ingestion benchmarking.


### B. Retrieval Protocols: Protocol M vs. Protocol U
We enforce strict separation between retrieval protocols:
- **Protocol M (Masked Exclusion):** Historical preliminary setup excluding intra-acquisition gallery images ($R@1 = 0.9481, \text{MRR} = 0.9658$).
- **Protocol U (Unmasked Distractors):** Authoritative benchmark evaluating galleries with full intra-acquisition distractors ($R@5 = 0.9921$). These protocols differ fundamentally and must not be compared directly.

## V. Experimental Results
### Table I: Representation Comparison & Trade-off (Protocol U)
| Representation | Retrieval R@1 | Retrieval R@5 | MRR | Artifact AUROC | Artifact AUPRC | Macro F1 | Specialization Role |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Frozen DINOv2 ViT-S/14** | 0.1321 | 0.9858 | 0.5200 | **0.8582** | **0.9841** | **0.6837** | Primary Quality & Artifact Screening |
| **Phase-4 Adapter (Seed 42)** | 0.1321 | 0.9953 | 0.5230 | 0.8251 | 0.9795 | 0.6335 | Acquisition-Aware Retrieval |
| **Phase-4 Adapter (Seed 123)** | 0.1462 | 0.9906 | 0.5214 | 0.8215 | 0.9788 | 0.6310 | Acquisition-Aware Retrieval |
| **Phase-4 Adapter (Seed 2024)** | 0.1557 | 0.9906 | 0.5338 | 0.8224 | 0.9793 | 0.6324 | Acquisition-Aware Retrieval |
| **Phase-4 Adapted (3-Seed Mean)** | **0.1447** | **0.9921** | **0.5261** | 0.8230 | 0.9792 | 0.6323 | Acquisition-Aware Retrieval |

### Table II: Acquisition-Geometry Robustness
| Representation | Within Sim | Cross Sim | Gap ($\Delta_{\text{geom}}$) | Gap Reduction (%) | Statistical Significance |
|:---|:---:|:---:|:---:|:---:|:---|
| **Frozen DINOv2 ViT-S/14** | 0.7811 | 0.5794 | 0.2016 | Baseline (0.0%) | N/A |
| **Phase-4 Adapted (3-Seed Mean)** | **0.9085** | **0.8404** | **0.0681** | **66.23%** | **$p = 5.03 \times 10^{-36}, d_z = 2.19$** |

### Table III: Component Specialization & Deterministic Composition
| Architecture Configuration | Quality Macro F1 | Quality AUROC | Retrieval R@5 | Acquisition Gap | Architectural Principle |
|:---|:---:|:---:|:---:|:---:|:---|
| **Monolithic: Frozen DINOv2 Only** | 0.6837 | 0.8582 | 0.9858 | 0.2016 | Optimal evaluated artifact sensitivity; suboptimal retrieval |
| **Monolithic: Phase-4 Adapter Only** | 0.6323 | 0.8230 | 0.9921 | 0.0681 | Superior retrieval alignment; attenuated artifact sensitivity |
| **Deterministic SCI-INTEL Composition** | **0.6837** | **0.8582** | **0.9921** | **0.0681** | Combines strongest evaluated component results without learned fusion |
*Note: The deterministic SCI-INTEL composition introduces no new learned parameters. Its quality metrics are inherited from frozen DINOv2, and retrieval metrics are inherited from frozen Phase-4.*

### Table IV: Spatial Localization Performance (N = 500)
| Artifact Category | Mean IoU | Mean Dice | Pixel Precision | Pixel Recall | Morphological Designation |
|:---|:---:|:---:|:---:|:---:|:---|
| **CHARGING_LIKE_SYNTHETIC_ARTIFACT** | 0.7794 | 0.8661 | 0.8812 | 0.8515 | Model-derived suspicious region |
| **OVEREXPOSURE** | 0.5621 | 0.6384 | 0.6841 | 0.5982 | Model-derived suspicious region |
| **UNDEREXPOSURE** | 0.5579 | 0.6358 | 0.6795 | 0.5971 | Model-derived suspicious region |
| **LOCAL_ILLUMINATION_ABNORMALITY** | 0.2515 | 0.3235 | 0.4210 | 0.2625 | Model-derived suspicious region |
| **CLIPPING** | 0.0762 | 0.0880 | 0.2967 | 0.0822 | Model-derived suspicious region |
| **Macro Average (N = 500)** | **0.4454** | **0.5103** | **0.5925** | **0.4983** | **Model-derived suspicious regions** |

### Table V: Evidence Operational Metrics (N = 55 Query Cohort)
| Metric | Measured Value | Scope | Operational Meaning |
|:---|:---:|:---:|:---|
| **Valid Evidence Availability Rate** | **100.0%** | $N = 55$ test queries | Proportion of queries with $\ge 1$ valid retrieved evidence micrograph |
| **Same-Specimen Cross-Acq Availability** | **100.0%** | $N = 55$ test queries | Proportion with same-specimen peer from different acquisition |
| **Cross-Instrument Evidence Availability** | **100.0%** | $N = 55$ test queries | Proportion with peer from different physical microscope |
| **Quality-Compatible Evidence Availability**| **100.0%** | $N = 55$ test queries | Proportion with clean benchmark reference |
| **Duplicate Evidence Rate** | **0.0%** | $N = 110$ candidate items | Zero duplicate candidate IDs or duplicate SHA-256 hashes |
| **Missing Provenance Rate** | **0.0%** | $N = 110$ candidate items | Zero records lacking instrument or specimen provenance linkage |

### Table VI: System Latency Profiling
| Pipeline Stage | Mean (ms) | Median (ms) | P95 (ms) | Execution Environment |
|:---|:---:|:---:|:---:|:---|
| **1. Preprocessing** | 0.35 | 0.32 | 0.48 | Windows CPU / 64-bit |
| **2. Dual Representation Generation** | 3.12 | 3.01 | 3.95 | Windows CPU / 64-bit |
| **3. Quality-Risk Screening** | 2.45 | 2.38 | 3.10 | Windows CPU / 64-bit |
| **4. Spatial Localization** | 8.84 | 8.65 | 11.20 | Windows CPU / 64-bit |
| **5. Evidence Retrieval** | 4.22 | 4.10 | 5.35 | Windows CPU / 64-bit |
| **6. Evidence Aggregation** | 4.42 | 4.25 | 5.60 | Windows CPU / 64-bit |
| **Complete Pipeline** | **23.40** | **22.71** | **28.30** | **Measured serial execution ($0.35+3.12+2.45+8.84+4.22+4.42=23.40$ ms)** |

### Table VII: Counterfactual Evidence Structural Comparison
| Condition | Query N | Evidence Availability | Same-Specimen | Cross-Acquisition | Cross-Instrument | Metadata Completeness | Mean Items | Duplicate Rate | Provenance Completeness |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Condition A: Query image alone** | 55 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 0.0 | NOT APPLICABLE | 100.0% |
| **Condition B: Query + Same-Specimen Cross-Acq** | 55 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 2.0 | 0.0% | 100.0% |
| **Condition C: Query + General Clean Reference** | 55 | 100.0% | NOT MEASURED | 100.0% | 100.0% | 100.0% | 2.0 | 0.0% | 100.0% |
*Endpoint Disclosure: No human interpretation-quality endpoint was available; therefore Conditions A–C quantify structural evidence availability rather than improvement in scientific interpretation.*

### Table VIII: Localization Provenance Audit Summary
| Category | Source Dataset | Image Population | Label Source | Synthetic / Natural | Manifest Reference | Status |
|:---|:---|:---:|:---|:---:|:---|:---:|
| **CHARGING_LIKE_SYNTHETIC_ARTIFACT** | HCCI SEM | $N = 100$ test | Phase 4 Directional Streak Generator | Synthetic | `synthetic_manifest.csv` | **VERIFIED** |
| **OVEREXPOSURE** | HCCI SEM | $N = 100$ test | Phase 4 Saturation Clipper | Synthetic | `synthetic_manifest.csv` | **VERIFIED** |
| **UNDEREXPOSURE** | HCCI SEM | $N = 100$ test | Phase 4 Intensity Attenuator | Synthetic | `synthetic_manifest.csv` | **VERIFIED** |
| **LOCAL_ILLUMINATION_ABNORMALITY** | HCCI SEM | $N = 100$ test | Phase 4 Spatial Gaussian Gradient | Synthetic | `synthetic_manifest.csv` | **VERIFIED** |
| **CLIPPING** | HCCI SEM | $N = 100$ test | Phase 4 Histogram Truncation | Synthetic | `synthetic_manifest.csv` | **VERIFIED** |

### Table IX: Pipeline Latency Summary
| Metric | Complete Pipeline | Quality Stage | Localization Stage | Retrieval Stage |
|:---|:---:|:---:|:---:|:---:|
| **Mean (ms)** | 23.40 | 2.45 | 8.84 | 4.22 |
| **Median (ms)** | 22.71 | 2.38 | 8.65 | 4.10 |
| **P95 (ms)** | 28.30 | 3.10 | 11.20 | 5.35 |

## VI. Discussion
### A. Why Does Acquisition Adaptation Help Cross-Instrument Retrieval?
Our results indicate that contrastive adaptation projects out high-frequency sensor noise specific to individual electron detectors, mapping images into an acquisition-aligned subspace. This is directly reflected in the 66.23% reduction of the acquisition-geometry gap $\Delta_{\text{geom}}$, increasing cross-acquisition cosine similarity from 0.5794 to 0.8404.

### B. Why Does DINOv2 Outperform Adapted Embeddings on Quality Screening?
We observe a fundamental trade-off: in learning invariance to acquisition geometry, representation adaptation discards high-frequency pixel deviations. Consequently, fine-grained perturbations such as subtle clipping and illumination gradients are smoothed out. Frozen DINOv2 ViT-S/14 features, having preserved raw patch-level visual tokens, remain +5.14% more sensitive in Macro F1 to controlled artifacts.

### C. The Dual-Representation Architectural Insight
Rather than attempting to train a complex multimodal fusion network that risks overfitting and uninterpretable compromises, SCI-INTEL employs deterministic composition: DINOv2 is dedicated to quality screening, while Phase-4 adaptation executes retrieval. This deterministic composition delivers optimal evaluated component performance without learning any new fusion weights.

## VII. Scientific Limitations & Boundaries
1. **Partition Overlap Limitation:** The train, validation, and test partitions contain identical declared alloy specimen classes; hence, unseen-specimen generalization is not established.
2. **Synthetic vs. Physical Defect Boundary:** Controlled synthetic perturbations do not encompass all real-world physical microscope defects.
3. **No Human Expert Validation:** Human expert validation of scientific interpretation and physical artifact identity was not performed in this phase.
4. **Operational Evidence Availability vs. Correctness:** Evidence availability is an operational metric and does not establish visual interpretation correctness.
5. **No Causal Reasoning:** Evidence retrieval establishes geometric similarity; it does not constitute causal or diagnostic explanation.
6. **Model-Derived Localization:** Saliency bounding envelopes are model-derived suspicious regions, not physically confirmed defect boundaries.
7. **Bounded OOD Scope:** OOD screening on Carinthia/BBBC021 does not constitute open-world anomaly discovery.
8. **Bounded Acquisition Robustness:** Generalization is demonstrated across HCCI SEM geometries; expansion to TEM/AFM remains unproven.
9. **Missing Metadata Constraints:** Absent metadata fields can limit evidence interpretation.
10. **Hardware-Dependent Latency:** Measured latencies depend on the benchmark execution environment.
11. **Protocol Incomparability:** Protocol-M and Protocol-U retrieval metrics are not directly interchangeable.
12. **Deterministic Composition Principle:** The dual representation is a modular composition, not a newly trained fusion model.
13. **Zero Medical/Clinical Claim:** No clinical diagnosis or medical decision-making claim is made.


## VIII. Conclusion & Future Work
SCI-INTEL provides a reproducible, scientifically verified platform for acquisition-aware scientific image retrieval and quality-aware curation. By resolving the tension between cross-instrument representation alignment and fine-grained quality sensitivity through a deterministic dual-representation architecture, the platform demonstrates measurable operational utility while strictly respecting physical and statistical bounds. Future investigations should prioritize multi-center human expert reader studies, physically validated hardware defect datasets, and cross-modality evaluation across TEM and AFM archives.

## References
1. M. Oquab et al., 'DINOv2: Learning Robust Visual Features without Supervision,' TMLR, 2023.
2. M. Caron et al., 'Emerging Properties in Self-Supervised Vision Transformers,' in ICCV, 2021.
3. A. Dosovitskiy et al., 'An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale,' in ICLR, 2021.
4. K. He et al., 'Masked Autoencoders Are Scalable Vision Learners,' in CVPR, 2022.
5. P. Khosla et al., 'Supervised Contrastive Learning,' in NeurIPS, 2020.
6. T. Chen et al., 'A Simple Framework for Contrastive Learning of Visual Representations,' in ICML, 2020.
7. Y. Ganin et al., 'Domain-Adversarial Training of Neural Networks,' JMLR, 2016.
8. J. Johnson, M. Douze, and H. Jégou, 'Billion-Scale Similarity Search with GPUs,' IEEE Trans. Big Data, 2019.
9. M. Douze et al., 'The Faiss Library,' IEEE TPAMI, 2024.
10. Y. A. Malkov and D. A. Yashunin, 'Efficient and Robust Approximate Nearest Neighbor Search Using HNSW Graphs,' IEEE TPAMI, 2018.
11. H. Jégou, M. Douze, and C. Schmid, 'Product Quantization for Nearest Neighbor Search,' IEEE TPAMI, 2011.
12. B. L. DeCost, T. Francis, and E. A. Holm, 'Exploring the Microstructure Manifold: Image Representation, Similarity, and Retrieval in Materials Science,' IMMI, 2017.
13. J. Stuckner, B. Harder, and T. M. Smith, 'Microstructure Classification and Retrieval Using Computer Vision,' Comput. Mater. Sci., 2022.
14. K. Choudhary et al., 'Recent Advances and Applications of Deep Learning in Materials Science,' npj Comput. Mater., 2022.
15. T. Baltrušaitis, C. Ahuja, and L. P. Morency, 'Multimodal Machine Learning: A Survey and Taxonomy,' IEEE TPAMI, 2018.
16. A. Radford et al., 'Learning Transferable Visual Models From Natural Language Supervision,' in ICML, 2021.
17. R. J. Chen et al., 'Multimodal Co-Attention Transformer for Survival Prediction in Gigapixel Whole Slide Images,' IEEE TMI, 2021.
18. Z. Wang et al., 'Image Quality Assessment: From Error Visibility to Structural Similarity,' IEEE TIP, 2004.
19. A. Mittal, A. K. Moorthy, and A. C. Bovik, 'No-Reference Image Quality Assessment in the Spatial Domain,' IEEE TIP, 2012.
20. E. Krotkov, 'Focusing,' IJCV, 1987.
21. J. Yang, K. Zhou, Y. Li, and Z. Liu, 'Generalized Out-of-Distribution Detection: A Survey,' arXiv:2110.11334, 2021.
22. M. D. Wilkinson et al., 'The FAIR Guiding Principles for Scientific Data Management and Stewardship,' Scientific Data, 2016.
23. A. Paszke et al., 'PyTorch: An Imperative Style, High-Performance Deep Learning Library,' in NeurIPS, 2019.
24. C. Zauner, 'Implementation and Benchmarking of Perceptual Image Hash Functions,' Master thesis, FH Hagenberg, 2010.