# COMPREHENSIVE PLATFORM REPRODUCTION GUIDE

**Project**: AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Document**: Phase 20 Authoritative Reproduction Guide  
**Status**: PERMANENTLY_FROZEN  

---

## 1. System Requirements & Environment Setup
- **Operating System**: Windows 11 Enterprise (64-bit) / Ubuntu 22.04 LTS
- **Python Runtime**: Python 3.11.x (tested on 3.11.9 in virtual environment `.venv311`)
- **Key Dependencies**:
  - `torch>=2.2.0`, `torchvision>=0.17.0`
  - `faiss-cpu>=1.8.0`
  - `fastapi>=0.110.0`, `uvicorn>=0.28.0`
  - `numpy>=1.26.0`, `scipy>=1.12.0`, `scikit-learn>=1.4.0`
  - `pytest>=8.0.0`

### Quickstart Setup Commands
```bash
# Clone repository
git clone <repository_url>
cd "Mini Project"

# Activate environment
.venv311\Scripts\activate  # On Windows
# source .venv/bin/activate # On Linux

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Regression Testing & Verification (190/190 Tests)
Execute the complete test suite to verify system integrity:
```bash
pytest tests/ -q
```
Expected output:
```text
.................................................................................... [ 44%]
.................................................................................... [ 88%]
......................                                                               [100%]
190 passed in ~28s
```

---

## 3. Dataset Verification & Checksum Manifests
Verify historical artifact and dataset manifests:
```bash
python -c "
import hashlib
from pathlib import Path

manifest_path = Path('data/manifests/hcci_manifest.parquet')
if manifest_path.exists():
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    print(f'HCCI Manifest SHA-256: {digest}')
"
```

---

## 4. End-to-End Pipeline Reproduction

### Step 1: Feature Extraction & Embedding Generation
```bash
python scripts/extract_embeddings.py --dataset hcci --model dinov2_vits14
```
Extracts 384-dimensional $L_2$-normalized class tokens (`[CLS]`) into `data/processed/embeddings/`.

### Step 2: Vector Index Construction (FAISS HNSW)
```bash
python scripts/build_hnsw_index.py --dim 384 --M 16 --efSearch 128
```
Constructs the sub-millisecond HNSW graph index.

### Step 3: Zero-Shot Retrieval Benchmark
```bash
python scripts/evaluate_retrieval.py --benchmark hcci
```
Verifies frozen metrics: $\text{R@1} = 0.9481$, $\text{MRR} = 0.9658$, $\text{P@5} = 0.8708$.

### Step 4: Quality & Integrity Screening
```bash
python scripts/evaluate_integrity.py
```
Evaluates Tenengrad focus screening (AUROC $0.8803$) and duplicate cascade (0 exact duplicates, 5 near-duplicate pairs).

### Step 5: Start Host Serving Tier & Curation API
```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Access interactive documentation at `http://127.0.0.1:8000/docs`.

---

## 5. Explicit Limitations & Boundaries
When reproducing this platform, note the following verified boundaries:
1. `CLOUD_DEPLOYMENT_NOT_EXECUTED`: Live cloud infrastructure is not executed; IaC is offline.
2. `DOCKER_RUNTIME_NOT_EXECUTED`: Docker containers are validated offline without active engine daemon.
3. `PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`: Spectral EDS pipelines utilize synthetic mock stubs.
4. `DATASET_RIGHTS`: Restricted raw micrograph files are replaced with cryptographic manifests and precomputed embeddings.
5. `CLIP/RESNET`: Comparative baselines are descriptive citations from published literature.
6. `GENERALIZATION`: Performance is bounded to the evaluated microscopy benchmarks and regimes.
