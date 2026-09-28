# AUTHORITATIVE FINAL SYSTEM LIMITATIONS

**Project**: AI-Powered Scientific Image Data Management Platform  
**Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`  
**Status**: PERMANENTLY_FROZEN  

---

In adherence to absolute scientific integrity and transparency, the platform explicitly declares the following substantive operational and scientific limitations:

1. **`CLOUD_DEPLOYMENT_NOT_EXECUTED`**: Cloud-native Infrastructure-as-Code (Terraform templates, Kubernetes manifests, Helm charts) has been authored and verified offline. No live public cloud infrastructure (AWS/GCP/Azure) was provisioned, and no live cloud deployment was executed.
2. **`DOCKER_RUNTIME_NOT_EXECUTED`**: Production Dockerfiles and container configurations were validated statically on the host environment; live container runtime execution was not performed due to Docker Desktop daemon unavailability on the host.
3. **`PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`**: Energy Dispersive X-ray Spectroscopy (EDS) data pipelines were engineered using synthetic, simulated spectral signatures (`is_synthetic = true`). No physical EDS spectrometer hardware was interfaced.
4. **`DATASET_RIGHTS / RAW-DATA REDISTRIBUTION LIMITATIONS`**: Due to third-party proprietary rights and licensing restrictions, raw micrograph files for certain datasets (HCCI, Carinthia) cannot be redistributed in open repositories. The release package provides complete SHA-256 cryptographic manifests, precomputed embeddings, and synthetic validation subsets.
5. **`CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY AND LOCAL REPRODUCTION IS NOT VERIFIED`**: Comparative retrieval numbers for CLIP and ResNet-50 are cited as descriptive baselines from external published literature; identical local re-evaluation across our exact cross-domain splits was not conducted.
6. **`EXTERNAL GENERALIZATION REMAINS BOUNDED TO THE DATASETS, DOMAINS AND PROTOCOLS ACTUALLY EVALUATED`**: While the platform demonstrates high zero-shot nearest-neighbor consistency on Carinthia defect SEM (Micro R@1 $0.9952$), macro-average sensitivity drops ($0.9090$) on rare classes, and domain shift is pronounced on biological TEM ($	ext{MMD}^2 = 0.5410$). Generalization is strictly bounded to the evaluated material and imaging regimes.
