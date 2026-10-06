# Reproducibility Protocol & Cryptographic Provenance
**Platform**: AI-Powered Scientific Image Data Management Platform  
**Target Manuscript**: Section: Reproducibility & Open Science  

---

## 1. Reproducibility Principles
To adhere to the highest standards of scientific reproducibility, every component of the platform—from pre-trained model weights and benchmark datasets to container builds and evaluation scripts—is deterministically frozen and cryptographically verifiable.

---

## 2. Checksum Verification Manifests

### 2.1 Pretrained Foundation Model Weights
- **Model Architecture**: DINOv2-ViT-S/14 (`dinov2_vits14`)
- **PyTorch Hub Release Checkpoint**:
  - File: `dinov2_vits14_pretrain.pth`
  - Canonical SHA-256 Digest:
    ```
    96924d552309f4eb3fa7e1efda352ba85fa71c66f4cb76ec38290f6e57ab723b
    ```

### 2.2 Historical Research Artifacts (Phases 1–20)
- **Manifest Location**: `reports/final_closure/pre_phase18_frozen_checksums.json`
- **Total Verified Files**: **128**
- **Verification Command**:
  ```bash
  python scripts/reproduce/final_validate_project.py --verify-only
  ```
- **Observed Result**: 128 / 128 files MATCH (0 mismatches, 0 missing).

### 2.3 Release Distribution Package
- **Manifest Location**: `release_final/checksums/SHA256SUMS.txt`
- **Total Verified Files**: **437**
- **Verification Command**:
  ```bash
  python scripts/reproduce/verify_final_release.py
  ```
- **Observed Result**: 437 / 437 files MATCH (0 mismatches, 0 missing).

---

## 3. End-to-End Reproduction Workflow

To reproduce all platform evaluations from a clean workstation:

```bash
# 1. Clone repository
git clone https://github.com/Pranet20/AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data.git
cd AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data

# 2. Verify frozen scientific research checksums
python scripts/reproduce/final_validate_project.py --verify-only

# 3. Run complete automated regression test suite (224 tests)
pytest tests/ platform/tests/ -q

# 4. Perform security & credentials scan
python scripts/reproduce/run_secret_scan.py

# 5. Build and launch containerized platform
docker compose build --no-cache
docker compose up -d

# 6. Execute live end-to-end integration and workflow test
python scripts/reproduce/test_live_docker_workflow.py

# 7. Verify distribution release integrity
python scripts/reproduce/verify_final_release.py
```

---

## 4. Software Environment Specification
- **Python**: 3.11.9
- **PyTorch**: 2.2.1+cpu
- **FAISS**: 1.7.4 (faiss-cpu)
- **FastAPI**: 0.110.0
- **PostgreSQL**: 15.6 Alpine
- **Node.js**: 18.19.0 / React 18.2.0
- **Docker Compose**: v2.24+
