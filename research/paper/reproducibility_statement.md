# Reproducibility Statement & Technical Protocol

All experimental results, statistical analyses, and software evaluations reported in the SCI-INTEL manuscript are 100% locally reproducible without proprietary cloud services or external network access.

---

## 1. Computational Environment & Toolchain

- **Operating System:** Microsoft Windows 10/11 / Linux (Ubuntu 22.04 LTS compatible)
- **Python Runtime:** Python 3.11.9
- **Node Runtime:** Node.js v20.18.0 (NPM v10.8.2)
- **Core ML Libraries:** PyTorch 2.x, Torchvision, FAISS (faiss-cpu 1.7.4), Scikit-Learn 1.2+, SciPy 1.10+, NumPy 1.25+
- **Application Framework:** FastAPI 0.110+, Starlette, SQLAlchemy 2.0+, React 18.3.1, TypeScript 4.9+

---

## 2. Cryptographic Checksums & Checkpoint Provenance

| Checkpoint / Artifact | File Location | SHA-256 Checksum |
|:---|:---|:---|
| **Phase 1 Manifest** | `data/manifests/phase1_dataset_manifest.json` | `6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5` |
| **HCCI Split Manifest** | `research/final_manifests/hcci_splits.json` | `bb81b268d241245b8fde478a0c201333cf3e7fed47e3c4d7410f40033b9b7727` |
| **Phase 4 Adapter (Seed 42)** | `checkpoints/phase4/adapter_seed42.pt` | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` |
| **Phase 4 Adapter (Seed 123)** | `checkpoints/phase4/adapter_seed123.pt` | `391fd18c95599a6956018be60b6dc8780be4b8154b899f7807c1c3950a0a931f` |
| **Phase 4 Adapter (Seed 2024)** | `checkpoints/phase4/adapter_seed2024.pt` | `c5ebbc7187dd1e643fb4e59ee77b0ab4b49e8aacd9cb4647733a92258e0d8f7b` |
| **Phase 5 Threshold Container** | `configs/thresholds.json` | `a894676be938dc85b08e2cbf1fba453a25cb73a886a1dfae9e3a09722361665a` |

---

## 3. Reproduction Commands

### 3.1 Environment Setup
```powershell
# Create and activate Python 3.11 virtual environment
python -m venv .venv311
.venv311\Scripts\activate

# Install locked dependencies
pip install -r requirements.txt
```

### 3.2 Automated Test Suite Execution
```powershell
# Full 509 test matrix (424 research + 85 platform integration)
.venv311\Scripts\pytest.exe tests platform/tests -v
```

### 3.3 Publication Figures and Tables Regeneration
```powershell
# Generate all 7 figures in PNG and PDF
python scripts/generate_publication_figures.py

# Generate all 9 tables in Markdown and LaTeX
python scripts/generate_publication_tables.py
```

### 3.4 Live Application Demo Verification
```powershell
# Execute the live 17-stage end-to-end manual demo
python scripts/validation/run_manual_demo_validation.py
```
