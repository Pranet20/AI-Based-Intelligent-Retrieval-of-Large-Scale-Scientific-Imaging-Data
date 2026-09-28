# PHASE 18–19 COMPREHENSIVE LIMITATIONS REGISTER

**Project**: AI-Powered Scientific Image Data Management Platform  
**Scope**: Complete Platform, Real-World Deployment, and External Scientific Validation  
**Date**: 2026-09-27  
**Status**: OFFICIALLY_REGISTERED  

---

## 1. Infrastructure & Real-World Cloud Deployment Limitations

### 1.1 Remote Cloud Deployment Status (`CLOUD_DEPLOYMENT_NOT_EXECUTED`)
- **Limitation**: The local workstation environment lacks remote cloud provider credentials (AWS IAM role, GCP service account key, Azure service principal). 
- **Impact**: While Terraform configurations, Kubernetes deployment descriptors, and Docker Compose configurations are complete and validated syntactically, live provisioning against remote cloud infrastructure was not executed.
- **Remediation**: Operators must configure standard cloud environment variables (`AWS_ACCESS_KEY_ID`, `GOOGLE_APPLICATION_CREDENTIALS`) and execute standard Terraform/K8s automation.

### 1.2 Docker Container Runtime Status (`DOCKER_RUNTIME_NOT_EXECUTED`)
- **Limitation**: The Docker Desktop Linux Engine daemon named pipe on Windows was inactive during audit execution.
- **Impact**: Container runtime isolation was verified via static buildfile inspection and non-containerized local backend regression tests rather than live Docker daemon containers.
- **Remediation**: Run `net start docker` or launch Docker Desktop before invoking `docker compose up --build`.

### 1.3 Database Concurrency in Local Testing
- **Limitation**: The local benchmarking environment uses SQLite with file locking.
- **Impact**: Concurrency is limited by write locks; stress load testing was evaluated on read-only endpoints (`/api/v1/health`, `/api/v1/version`).
- **Remediation**: Production deployments must configure PostgreSQL 15+ with pgBouncer connection pooling.

---

## 2. Scientific Generalization & Representation Limitations

### 2.1 Extreme Class Imbalance & Representation Sparsity
- **Limitation**: In real-world defect SEM archives (e.g. Carinthia), extreme class distribution skew exists (Class 3 represents 87.3% of the dataset; Class 5 contains only 4 images).
- **Impact**: While micro-averaged zero-shot R@1 reaches 0.9952, macro-averaged R@1 is 0.9090, and Class 5 recall drops to 0.7500.
- **Boundary**: Unadapted foundation models cannot overcome extreme representation sparsity without targeted few-shot or active-learning curation.

### 2.2 Severe Optical Defocus Blur Degradation Threshold
- **Limitation**: Optical defocus blur destroys high-frequency edge gradients and microstructural grain boundaries.
- **Impact**: Accuracy retention remains high (>96%) under Gaussian noise ($\sigma=0.05$) and contrast changes ($\pm 30\%$), but drops sharply to 69.83% under heavy blur ($\sigma=3.0$).
- **Boundary**: Micrographs with Laplacian variance below calibrated focus thresholds cannot support reliable morphological retrieval and must be queued for re-acquisition.

### 2.3 Cross-Modality Domain Shift (SEM to TEM)
- **Limitation**: Differing instrument physics (scanning electron scattering vs transmitted electron diffraction) create a large distributional gap ($\text{MMD}^2 = 0.5410$).
- **Impact**: Zero-shot unadapted retrieval drops from 0.9481 to 0.7642 across modalities.
- **Boundary**: Supervised adapter fine-tuning or domain adaptation is strictly required when crossing microscopy modalities.

### 2.4 Metadata-Only Inadequacy
- **Limitation**: Scientific instrument metadata logs are noisy, inconsistent, and often omit critical specimen phase identities.
- **Impact**: Authoritative metadata-only retrieval achieves an MRR of only 0.3443, and naive end-to-end multimodal fusion architectures degrade performance ($p < 0.001$).
- **Boundary**: Metadata should be utilized exclusively for post-filtering and query constraint scoping, not as an end-to-end replacement for visual feature embeddings.

---

## 3. Physical Acquisition & Hardware Integration Limitations

### 3.1 Energy-Dispersive X-Ray Spectroscopy (EDS) Microanalysis
- **Limitation**: The platform has not been interfaced with physical EDAX / Oxford Instruments spectrometers.
- **Status**: **NOT_EXECUTED**.
- **Boundary**: All spectral processing modules and Gaussian peak generators are synthetic engineering stubs designed for data pipeline testing. Physical microanalysis claims are strictly disclaimed.

---

## 4. Human-in-the-Loop Operational Guidelines

- **Borderline Anomaly False Alarms**: Out-of-distribution detection exhibits a 24.50% false positive rate at 95% true positive sensitivity. Human expert triage is required for borderline flags.
- **Continuous Auditing**: New instrument acquisitions should undergo automated quality screening and periodic drift auditing prior to being incorporated into production vector indexes.
