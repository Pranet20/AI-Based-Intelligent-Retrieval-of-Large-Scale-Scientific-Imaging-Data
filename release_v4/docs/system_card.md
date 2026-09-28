# SYSTEM CARD: AI-POWERED SCIENTIFIC IMAGE DATA MANAGEMENT PLATFORM

## System Overview
The platform is an end-to-end scientific image data management system for high-throughput electron microscopy. It integrates ingestion provenance, reference-free quality screening, self-supervised semantic representation, decoupled metadata scoping, sub-millisecond approximate nearest neighbor search, and human-in-the-loop curation.

## Architectural Components
1. **Ingestion Engine**: Validates image formats (TIFF, PNG, DM3), extracts EXIF/TIFF metadata headers, computes SHA-256 digests, and generates immutable provenance events.
2. **Quality & Integrity Cascade**: Computes Tenengrad gradient energy ($0.8803$ AUROC for defocus detection) and DCT perceptual hashes with latent cosine matching ($0.9810$ F1 for duplicate detection).
3. **Representation & Vector Index**: Extracts 384-dimensional DINOv2 ViT-S/14 embeddings, indexes vectors via FAISS HNSW ($M=16, efSearch=128$), providing $0.096$–$0.317\text{ ms}$ search latencies with $100\%$ Recall@10.
4. **Decoupled Metadata Index**: Operates an independent inverted index to filter search candidates without polluting dense visual vector geometry (resolving the Metadata Paradox).
5. **Curation Workbench**: Surfaces flagged low-quality or novel micrographs ($D_{\text{ref}}$ separation ratio $2.12\text{x}$) to an active review queue, achieving a $91.67\%$ actionability yield ($\kappa = 0.8420$).

## System Status & Limitations
- **Current Operational Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`
- **Substantive Declared Limitations**:
  1. `CLOUD_DEPLOYMENT_NOT_EXECUTED`: Cloud IaC templates (Terraform/K8s) verified statically; no live cloud deployment.
  2. `DOCKER_RUNTIME_NOT_EXECUTED`: Container manifests verified offline; live Docker engine not executed.
  3. `PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`: Synthetic spectral stubs used; no physical spectrometer hardware.
  4. `DATASET_RIGHTS / RAW-DATA REDISTRIBUTION LIMITATIONS`: Restricted raw micrographs excluded; manifests and embeddings provided.
  5. `CLIP/RESNET COMPARATIVE RESULTS ARE DESCRIPTIVE-ONLY`: External literature baselines; local re-execution not verified.
  6. `EXTERNAL GENERALIZATION BOUNDED`: Performance bounded to evaluated SEM benchmarks and protocols.
