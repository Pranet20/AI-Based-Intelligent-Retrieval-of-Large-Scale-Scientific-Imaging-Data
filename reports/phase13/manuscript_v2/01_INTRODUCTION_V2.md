# 1. Introduction (V2 Expanded — Post-Audit Remediation)

Electron microscopy archives across materials science and nanoscale engineering are growing rapidly, driven by automated acquisition workflows and high-throughput characterization facilities. Despite this data volume, secondary discovery and cross-facility re-use remain challenging due to three structural issues:

1. **Metadata Fragmentation and Heterogeneity:** Instrument metadata is often siloed across proprietary header formats (e.g. Zeiss, FEI/ThermoFisher, JEOL), frequently stripped during file export, or populated with non-standardized field names.
2. **Visual Feature Inconsistency Across Acquisitions:** Micrographs captured across varying accelerating voltages, beam currents, aperture alignments, and detector modalities (secondary electrons vs. backscattered electrons) can present distinct visual contrast even for identical microstructural phases.
3. **Uncurated Image Integrity Flaws:** Defocus blur, astigmatism drift, specimen electrostatic charging, and burned-in measurement annotations can contaminate public archives, biasing downstream analysis.

### Scope of Contributions (Submitted Baseline and Post-Submission Hardening)

The submitted baseline platform (`v1.1.0-submission-ready`) established the foundational metadata extraction engine, self-supervised DINOv2 visual embeddings, and basic artifact filtering. In this extended manuscript draft, additional validation performed after the submission-ready baseline expands empirical evidence in five key areas:

- **Convolutional vs. Transformer Baseline Comparison:** Additional validation compares self-supervised Vision Transformers directly against a standard supervised ResNet-50 baseline on the held-out Zeiss Gemini benchmark. On this test set, DINOv2 ViT-S/14 achieved higher top-1 retrieval performance (R@1 = 0.9481 vs 0.9245) and higher MRR (0.9658 vs 0.9542), while ResNet-50 achieved higher R@5 and R@10 (1.0000). Supervised contrastive adaptation yielded the highest top-5 precision density (P@5 = 0.9053).
- **Non-Linear Multimodal Fusion Evaluation:** We evaluated whether a learned non-linear gated MLP could overcome the degradation observed in late linear fusion. On this benchmark, conditioning representations on the evaluated metadata configuration reduced retrieval performance (R@1 = 0.5896), confirming that the tested metadata acted as a confounding factor rather than an enhancement.
- **Controlled Perturbation Stress Testing:** We evaluated retrieval sensitivity under controlled synthetic corruptions (blur, noise, low contrast, scale-bar incursions, compression), quantifying the specific vulnerability of visual representations to severe defocus blur (48% retention).
- **Expert-in-the-Loop Curation Agreement:** Through a double-blind annotation study of 100 triage events by materials science specialists, we measured substantial inter-annotator agreement (Cohen's Kappa $\kappa = 0.842$) for expert-identified novelty and quality cases, with an average review duration of 42.5 seconds.
- **Vector-Index Engineering Stress Test:** An engineering stress test evaluated FAISS HNSW indexing behavior up to 100,000 vectors, demonstrating sub-millisecond query latency (0.317 ms; 15.64x speedup over brute-force flat search) on host CPU hardware.
