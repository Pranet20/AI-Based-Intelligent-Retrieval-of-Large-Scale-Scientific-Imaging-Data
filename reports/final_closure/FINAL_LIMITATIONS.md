# FINAL AUTHORITATIVE SYSTEM LIMITATIONS & BOUNDARY REGISTER

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: Authoritative Master Limitations (Post Phase 18–19 Audit)  
**Date**: 2026-09-27  
**Declared Limitation Count**: 6  
**Status**: OFFICIALLY_RATIFIED  

---

## 1. Limitation 1: Remote Cloud Deployment Execution (`CLOUD_DEPLOYMENT_NOT_EXECUTED`)
- **Factual Status**: **NOT_EXECUTED**.
- **Context & Boundary**: The evaluation host lacks remote cloud service provider API keys and IAM credentials (AWS, GCP, Azure). 
- **Declared Scope**: Platform container blueprints, Terraform infrastructure configurations, Kubernetes manifests, and environment profiles are verified syntactically. Operators must provision live cloud accounts prior to remote production provisioning.

---

## 2. Limitation 2: Container Runtime Daemon Execution (`DOCKER_RUNTIME_NOT_EXECUTED`)
- **Factual Status**: **NOT_EXECUTED**.
- **Context & Boundary**: The local Docker Desktop Linux Engine background daemon on Windows was inactive during audit execution.
- **Declared Scope**: Static buildfile compliance, multi-stage image pinning (`v2.0.0`), unprivileged user definitions (`scidata`, UID 1000), and docker-compose healthchecks are verified. Live container execution requires launching the Docker daemon.

---

## 3. Limitation 3: Physical EDS Microanalysis Validation (`PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`)
- **Factual Status**: **NOT_EXECUTED**.
- **Context & Boundary**: The platform has not been attached to physical electron microscope spectrometers. 
- **Declared Scope**: All EDS routines, Gaussian spectrum generators, and peak deconvolution modules are synthetic engineering stubs for data schema verification. Physical microanalysis claims are strictly disclaimed.

---

## 4. Limitation 4: Dataset Rights & Raw-Data Redistribution Limitations
- **Factual Status**: **RESTRICTED_GOVERNANCE_ENFORCED**.
- **Context & Boundary**: Several upstream research corpora (in-domain HCCI, Carinthia Defect SEM, Bio-Image TEM, MicroAl) carry academic and non-redistribution licenses.
- **Declared Scope**: The distribution package distributes manifests, embeddings, and code only (`MANIFEST_ONLY_DUE_TO_RIGHTS`). Only SEM Images for Nanoscience (Nature Scientific Data, CC BY 4.0) is permitted for open redistribution.

---

## 5. Limitation 5: Baseline Reproducibility Status (`CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY AND THEIR LOCAL REPRODUCTION IS NOT VERIFIED`)
- **Factual Status**: **RECORDED_NOT_REPRODUCED**.
- **Context & Boundary**: Cached per-image 512-d CLIP ViT-B/32 and 2048-d ResNet-50 embeddings were not persisted in the frozen local repository artifacts.
- **Declared Scope**: Comparative metrics (DINOv2 0.9952 vs CLIP 0.7840 and ResNet-50 0.6420) are preserved strictly as descriptive empirical point estimates. Inferential claims ($p < 10^{-15}$) have been demoted from all formal claims.

---

## 6. Limitation 6: External Generalization Remains Bounded to Evaluated Domains & Protocols
- **Factual Status**: **EMPIRICALLY_BOUNDED**.
- **Context & Specific Boundaries**:
  1. **Previously Evaluated Corpus**: Carinthia Defect SEM was previously evaluated in Phase 2 and Phase 14; it is classified as a previously evaluated cross-domain corpus rather than a newly discovered independent benchmark.
  2. **Class Imbalance Sensitivity**: In nearest-neighbor class retrieval, minority defect classes ($N < 10$) exhibit lower recall (Class 5 at 0.7500; macro R@1 is 0.9090 vs micro 0.9952).
  3. **Optical Defocus Blur Breakdown**: Retrieval accuracy drops sharply to 69.83% under heavy defocus blur ($\sigma = 3.0$), identifying the boundary where microscopic textures are lost.
  4. **Cross-Modality Invariance Gap**: Zero-shot transfer from SEM to TEM exhibits high distributional shift ($\text{MMD}^2 = 0.5410$); supervised adapter tuning is mandatory when crossing microscopy modalities.
  5. **Metadata-Only Inadequacy**: Metadata-only retrieval achieves an MRR of only 0.3443 on noisy logs; complex end-to-end multimodal fusion architectures degraded performance ($p < 0.001$).
  6. **Anomaly False Alarm Rate**: Embedding-space novelty screening exhibits a 24.50% false positive rate at 95% true positive sensitivity, requiring human curation triage for borderline flags.
