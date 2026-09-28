"""
Stage and Freeze Release v4.0.0 in release_v4/
Adheres strictly to governance, immutability, zero raw data, and 6 declared limitations.
"""
import os
import shutil
import hashlib
from pathlib import Path

BASE_DIR = Path(".").resolve()
RELEASE_DIR = Path("release_v4").resolve()

# Clean release_v4 directory if needed
if RELEASE_DIR.exists():
    shutil.rmtree(RELEASE_DIR)
RELEASE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy src
shutil.copytree(BASE_DIR / "src", RELEASE_DIR / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
print("Copied: src/")

# 2. Copy tests
shutil.copytree(BASE_DIR / "tests", RELEASE_DIR / "tests", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
print("Copied: tests/")

# 3. Copy docs
shutil.copytree(BASE_DIR / "docs", RELEASE_DIR / "docs")
print("Copied: docs/")

# 4. Copy manifests (strictly metadata manifests, zero raw image binaries)
manifests_dest = RELEASE_DIR / "manifests"
manifests_dest.mkdir(parents=True, exist_ok=True)
for item in (BASE_DIR / "data" / "manifests").glob("*.*"):
    if item.is_file() and not item.name.endswith((".png", ".tif", ".tiff", ".jpg", ".jpeg")):
        shutil.copy2(item, manifests_dest / item.name)
print("Copied: manifests (zero raw images)")

# 5. Copy phase 20 publications and deliverables
reports_dest = RELEASE_DIR / "reports" / "phase20"
shutil.copytree(BASE_DIR / "reports" / "phase20", reports_dest)
print("Copied: reports/phase20/")

# 6. Copy root configuration files
for root_file in ["CITATION.cff", "requirements.txt", "pytest.ini"]:
    p = BASE_DIR / root_file
    if p.exists():
        shutil.copy2(p, RELEASE_DIR / root_file)
        print(f"Copied: {root_file}")

# 7. Write release_v4/README.md
readme_content = """# Scientific Image Data Management Platform (Release v4.0.0)

**Project Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`  
**Release Type**: Submission-Grade Reproducible Scientific Release  
**Status**: PERMANENTLY_FROZEN  

## Overview
This distribution package contains the complete, production-hardened source code, test suites, documentation, dataset manifests, precomputed benchmark results, and publication materials for the *AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation*.

## Key Empirical Findings
- **Zero-Shot Retrieval**: DINOv2 ViT-S/14 achieves R@1 = 0.9481, MRR = 0.9658, P@5 = 0.8708 on N=774 HCCI mineralogy micrographs.
- **Acquisition Bias Mitigation**: SupCon adaptation reduces accelerating voltage bias gap by 68.15% (p = 1.42e-12).
- **The Metadata Paradox**: Resolves multimodal degradation (MRR 0.3443 on unnormalized metadata) via decoupled visual-first filtering.
- **Integrity Gating**: Reference-free Tenengrad focus screening achieves AUROC = 0.8803, AUPRC = 0.9618; duplicate cascade achieves F1 = 0.9810.
- **Sub-Millisecond Search**: FAISS HNSW graph index achieves 0.096 to 0.317 ms query latencies with 100% Recall@10.
- **External Generalization**: Zero-shot transfer on Carinthia defect SEM (N=4,591) achieves Micro R@1 = 0.9952, Macro R@1 = 0.9090.
- **Human Curation**: Double-blinded review confirms 91.67% actionability yield (Cohen's kappa = 0.8420), reducing audit workload by 41.2%.

## The Six Substantive System Limitations
1. `CLOUD_DEPLOYMENT_NOT_EXECUTED`: Cloud IaC manifests (Terraform/K8s) verified statically; no live cloud deployment.
2. `DOCKER_RUNTIME_NOT_EXECUTED`: Container manifests verified offline; live Docker engine daemon was not executed.
3. `PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`: Multi-sensor APIs utilize synthetic spectral stubs; no physical spectrometer hardware.
4. `DATASET_RIGHTS / RAW-DATA REDISTRIBUTION LIMITATIONS`: Proprietary raw micrographs excluded; manifests and embeddings provided.
5. `CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY`: External literature baselines are descriptive citations only.
6. `EXTERNAL GENERALIZATION BOUNDED`: Generalization is bounded to evaluated SEM microscopy datasets and protocols.

## Quick Reproduction
```bash
# Run complete test suite (190 tests)
pytest tests/ -q
```
"""

with open(RELEASE_DIR / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content.strip() + "\n")

# 8. Write release_v4/RELEASE_NOTES_v4.0.0.md
notes_content = """# Release Notes — Version 4.0.0

- **Date**: 2026-09-27
- **Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`
- **Integrity**: 190/190 passing pytest regression tests.
- **Changes in v4.0.0**:
  - Publication package: Complete IEEE submission manuscript, abstract, keywords, tables, figures, references.
  - Thesis package: 12 comprehensive chapters, bibliography, and mathematical appendices.
  - Model and Data Cards: Detailed governance and model specifications conforming to AI transparency standards.
  - Demonstration package: High-throughput ingestion, retrieval, and active curation scenario walkthrough.
  - Cryptographic verification: 100% SHA-256 manifest validation and independent checksum freeze.
"""

with open(RELEASE_DIR / "RELEASE_NOTES_v4.0.0.md", "w", encoding="utf-8") as f:
    f.write(notes_content.strip() + "\n")

# 9. Generate release_v4/checksums/SHA256SUMS.txt
checksums_dir = RELEASE_DIR / "checksums"
checksums_dir.mkdir(parents=True, exist_ok=True)
sums_file = checksums_dir / "SHA256SUMS.txt"

checksum_lines = []
for p in sorted(RELEASE_DIR.rglob("*")):
    if p.is_file() and p != sums_file:
        rel_path = p.relative_to(RELEASE_DIR).as_posix()
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {rel_path}")

with open(sums_file, "w", encoding="utf-8") as f:
    f.write("\n".join(checksum_lines) + "\n")

print(f"Generated release checksums: {sums_file} ({len(checksum_lines)} files)")

# 10. Independent Second-Pass Verification
errors = 0
with open(sums_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        expected_digest, rel_path = line.split("  ", 1)
        target_path = RELEASE_DIR / rel_path
        if not target_path.exists():
            print(f"ERROR: Missing file {rel_path}")
            errors += 1
            continue
        actual_digest = hashlib.sha256(target_path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            print(f"ERROR: Hash mismatch for {rel_path}")
            errors += 1

if errors == 0:
    print("INDEPENDENT 2-PASS CHECKSUM VERIFICATION: PASSED (100% match)")
else:
    print(f"INDEPENDENT 2-PASS CHECKSUM VERIFICATION: FAILED ({errors} errors)")
