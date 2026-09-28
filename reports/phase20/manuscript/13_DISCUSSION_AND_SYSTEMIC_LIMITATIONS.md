# 11. DISCUSSION & SYSTEMIC LIMITATIONS

### 11.1 Architectural Lessons & Scientific Insights
1. **Self-Supervised Vision Transformers for Microscopy**: Pretrained DINOv2 ViT-S/14 serves as an exceptional zero-shot backbone for electron microscopy ($0.9481$ R@1), demonstrating that self-supervised patch distillation captures microstructural morphology far more effectively than supervised ImageNet features.
2. **Mitigating Instrument Bias via Contrastive Learning**: Instrument acquisition parameters induce measurable feature bias. Supervised contrastive adaptation on same-specimen pairs eliminates $68.15\%$ of this bias gap without catastrophic forgetting.
3. **The Metadata Paradox**: Direct multimodal neural fusion with noisy instrument logs degrades retrieval precision ($0.9658 \to 0.6132$ MRR). Decoupling visual indexing from inverted metadata filtering resolves this paradox.

### 11.2 The Six Substantive System Limitations
In adherence to scientific transparency, we declare six substantive limitations:

1. **`CLOUD_DEPLOYMENT_NOT_EXECUTED`**: All cloud IaC (Terraform, Kubernetes, Docker Compose) was authored, linted, and verified statically. No live public cloud clusters (AWS, GCP, Azure) were provisioned or tested under external network traffic.
2. **`DOCKER_RUNTIME_NOT_EXECUTED`**: Docker container runtime execution was not performed due to daemon unavailability in the test environment; container configurations are validated via offline static analysis.
3. **`PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`**: Energy Dispersive X-ray Spectroscopy (EDS) data pipelines were engineered using synthetic, simulated spectral signatures. No physical EDS spectrometer hardware was coupled to the platform.
4. **`DATASET_RIGHTS / RAW-DATA REDISTRIBUTION LIMITATIONS`**: Due to third-party proprietary rights and licensing restrictions, raw micrograph files for certain datasets cannot be redistributed in open repositories. The release package provides complete SHA-256 cryptographic manifests, precomputed embeddings, and synthetic validation subsets.
5. **`CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY AND THEIR LOCAL REPRODUCTION IS NOT VERIFIED`**: Comparative retrieval numbers for CLIP and ResNet-50 are cited as descriptive baselines from external published literature; identical local re-evaluation across our exact cross-domain splits was not conducted.
6. **`EXTERNAL GENERALIZATION REMAINS BOUNDED TO THE DATASETS, DOMAINS, AND PROTOCOLS ACTUALLY EVALUATED`**: While the platform demonstrates high previously evaluated cross-domain generalization on Carinthia defect SEM (Micro R@1 $0.9952$), macro-average sensitivity drops ($0.9090$) on rare classes, and domain shift is pronounced on biological TEM ($	ext{MMD}^2 = 0.5410$). Generalization is strictly bounded to the evaluated material and imaging regimes.
