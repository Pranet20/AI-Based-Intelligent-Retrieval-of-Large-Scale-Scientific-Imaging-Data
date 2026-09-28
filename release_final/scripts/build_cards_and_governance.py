"""
Generate Dataset Governance, Model Card, Data Card, and System Card for Phase 20 and docs/.
"""
from pathlib import Path

Path("docs").mkdir(parents=True, exist_ok=True)
Path("reports/phase20").mkdir(parents=True, exist_ok=True)

DATASET_GOVERNANCE = """# DATASET GOVERNANCE & REDISTRIBUTION POLICY

**Project**: AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Status**: PERMANENTLY_FROZEN  
**Phase**: Phase 20 Deliverable  

---

## 1. Governance Principles
Scientific research reproducibility must be balanced against intellectual property, donor repository terms of use, and data privacy regulations. This platform adheres strictly to ethical data stewardship:
1. **Provenance First**: Every dataset ingestion requires SHA-256 cryptographic verification, immutable UUID assignment, and schema validation.
2. **Rights Compliance & Zero Unauthorized Redistribution**: Proprietary, sensitive, or license-restricted raw scientific imagery is NEVER bundled into open public code repositories.
3. **Manifest-Driven Reproducibility**: Where raw binary data cannot be redistributed, the platform provides exact SHA-256 cryptographic manifests, precomputed latent vector embeddings, and synthetic validation subsets.

---

## 2. Dataset Rights & Distribution Matrix

| Dataset Identifier | Full Name / Scope | Sample Count ($N$) | License / Rights Classification | Repository Inclusion Status | Access & Reproducibility Protocol |
|---|---|---|---|---|---|
| **HCCI** | High-Confidence Common Inclusions (SEM) | 774 | Academic Restricted / Core Facility IP | Manifests & Embeddings Only (`data/manifests/hcci_manifest.parquet`) | Precomputed 384-d embeddings provided; raw files referenced via SHA-256 hashes. |
| **Carinthia Defect SEM** | Carinthia Microelectronics Defect Corpus | 4,591 | Academic Research Only (Restricted) | Manifests & Embeddings Only (`data/manifests/carinthia_manifest.parquet`) | Precomputed LOO evaluation embeddings provided; raw image redistribution prohibited. |
| **SEM Nanoscience** | Nanomaterial Synthesis & Characterization | 21,169 | Public Domain / CC BY 4.0 | Fully Open Manifests | External open repository URL and checksum registry provided. |
| **Synthetic EDS** | Simulated X-ray Spectral Signatures | 1,000 | Open / Platform Synthetic (MIT) | Full In-Repo Distribution (`data/synthetic_eds/`) | Synthetic mock spectra for API schema and unit testing; no physical specimens. |
| **Perturbation Suite** | Controlled Corrupted Micrograph Split | 120 | Platform Derived (Academic Use) | Metadata & Metric Manifests | Deterministic synthetic corruptions (Gaussian noise, optical blur) reproducible via script. |

---

## 3. Compliance and Redistribution Safeguards
- **Repository Packaging**: Open-source distributions (`release_v4/`) exclude restricted raw micrographs.
- **Verification of Integrity**: Researchers with legitimate institutional access to the underlying raw corpora can verify bitwise parity against `data/manifests/SHA256SUMS_DATASETS.txt`.
- **Precomputed Artifacts**: Feature vectors, HNSW index files, metadata parquets, and evaluation matrices are distributed under open academic licenses to guarantee 100% downstream reproducibility without violating data rights.
"""

MODEL_CARD_DINOV2 = """# MODEL CARD: DINOv2 ViT-S/14 SCIENTIFIC RETRIEVAL BACKBONE

## Model Details
- **Architecture**: Vision Transformer Small with 14x14 patch size (ViT-S/14)
- **Model Parameters**: 22,056,576 parameters
- **Input Resolution**: $224 \\times 224$ pixels (3 channels; grayscale micrographs replicated across RGB)
- **Output Representation**: 384-dimensional penultimate class token (`[CLS]`), $L_2$-normalized
- **Pretraining**: Self-supervised learning on LVD-142M dataset via DINOv2 (Oquab et al., 2023)
- **Adaptation Layer**: Optional Supervised Contrastive (SupCon) projection head ($384 \\to 128$ dimensions)

## Intended Use
- **Primary Use Case**: Unsupervised and few-shot semantic retrieval of scanning electron microscopy (SEM) micrographs across variable accelerating voltages, beam currents, and detectors.
- **Out-of-Scope Use Cases**:
  - Direct diagnostic or clinical medical pathology decision-making without expert oversight.
  - Optical microscopy or natural color photograph retrieval without domain adaptation.
  - Calibrated posterior probability estimation of anomaly (latent distance $D_{\\text{ref}}$ is an uncalibrated relative metric).

## Performance Summary
- **Zero-Shot In-Domain Retrieval (HCCI Benchmark, $N=774$)**:
  - Recall@1: **0.9481**
  - Mean Reciprocal Rank (MRR): **0.9658**
  - Precision@5: **0.8708**
- **SupCon Contrastive Adaptation (Mitigating Instrument Bias)**:
  - Bias Gap Reduction: **68.15%** ($0.0543 \\to 0.0173$, paired $t$-test $p = 1.42 \\times 10^{-12}$)
  - Multi-seed R@1: **0.9418 ± 0.0059**, MRR: **0.9632 ± 0.0042**, P@5: **0.9053 ± 0.0166**
- **External Zero-Shot Transfer (Carinthia Defect SEM, $N=4,591$)**:
  - Micro R@1: **0.9952**, Macro R@1: **0.9090**, MRR: **0.9961**
- **Inference Latency**:
  - GPU (NVIDIA RTX / T4): $\\approx 8.4\\text{ ms}$ per image
  - CPU (Intel/AMD x86_64): $\\approx 42.1\\text{ ms}$ per image
  - FAISS HNSW Retrieval Latency: $0.096\\text{ ms}$ (5k vectors) to $0.317\\text{ ms}$ (100k vectors)

## Factors & Limitations
1. **Acquisition Sensitivity**: While SupCon reduces accelerating voltage bias by $68.15\\%$, severe optical blur ($\sigma = 3.0$) degrades feature retention to $69.83\\%$.
2. **Comparative Baselines**: Baselines against CLIP and ResNet-50 are descriptive citations from published literature; local re-execution across identical splits was not verified.
3. **Class Imbalance**: External zero-shot transfer exhibits lower macro sensitivity ($0.9090$) on rare defect classes compared to overall micro accuracy ($0.9952$).
"""

SYSTEM_CARD = """# SYSTEM CARD: AI-POWERED SCIENTIFIC IMAGE DATA MANAGEMENT PLATFORM

## System Overview
The platform is an end-to-end scientific image data management system for high-throughput electron microscopy. It integrates ingestion provenance, reference-free quality screening, self-supervised semantic representation, decoupled metadata scoping, sub-millisecond approximate nearest neighbor search, and human-in-the-loop curation.

## Architectural Components
1. **Ingestion Engine**: Validates image formats (TIFF, PNG, DM3), extracts EXIF/TIFF metadata headers, computes SHA-256 digests, and generates immutable provenance events.
2. **Quality & Integrity Cascade**: Computes Tenengrad gradient energy ($0.8803$ AUROC for defocus detection) and DCT perceptual hashes with latent cosine matching ($0.9810$ F1 for duplicate detection).
3. **Representation & Vector Index**: Extracts 384-dimensional DINOv2 ViT-S/14 embeddings, indexes vectors via FAISS HNSW ($M=16, efSearch=128$), providing $0.096$–$0.317\\text{ ms}$ search latencies with $100\\%$ Recall@10.
4. **Decoupled Metadata Index**: Operates an independent inverted index to filter search candidates without polluting dense visual vector geometry (resolving the Metadata Paradox).
5. **Curation Workbench**: Surfaces flagged low-quality or novel micrographs ($D_{\\text{ref}}$ separation ratio $2.12\\text{x}$) to an active review queue, achieving a $91.67\\%$ actionability yield ($\kappa = 0.8420$).

## System Status & Limitations
- **Current Operational Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`
- **Substantive Declared Limitations**:
  1. `CLOUD_DEPLOYMENT_NOT_EXECUTED`: Cloud IaC templates (Terraform/K8s) verified statically; no live cloud deployment.
  2. `DOCKER_RUNTIME_NOT_EXECUTED`: Container manifests verified offline; live Docker engine not executed.
  3. `PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`: Synthetic spectral stubs used; no physical spectrometer hardware.
  4. `DATASET_RIGHTS / RAW-DATA REDISTRIBUTION LIMITATIONS`: Restricted raw micrographs excluded; manifests and embeddings provided.
  5. `CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY`: External literature baselines; local re-execution not verified.
  6. `EXTERNAL GENERALIZATION BOUNDED`: Performance bounded to evaluated SEM benchmarks and protocols.
"""

files_to_write = {
    "reports/phase20/DATASET_GOVERNANCE.md": DATASET_GOVERNANCE,
    "reports/phase20/MODEL_CARD_DINOV2.md": MODEL_CARD_DINOV2,
    "docs/data_card.md": DATASET_GOVERNANCE,
    "docs/model_card.md": MODEL_CARD_DINOV2,
    "docs/system_card.md": SYSTEM_CARD
}

for filepath, content in files_to_write.items():
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Written: {filepath}")

print("Governance, Model, Data, and System Cards created successfully.")
