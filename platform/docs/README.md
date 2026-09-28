# SciData Platform Documentation

Welcome to the documentation suite for the **SciData Platform**: an AI-powered scientific image data management platform integrating acquisition-robust representation, data integrity assessment, exact vector retrieval, and human-in-the-loop curation.

## Documentation Index
- [Architecture Overview](ARCHITECTURE.md): High-level system topology, module breakdown, and data flow.
- [REST API Reference](API.md): Detailed endpoint contracts, request/response models, and status codes.
- [Scientific Pipeline](SCIENTIFIC_PIPELINE.md): Detailed 14-step idempotent ingestion workflow.
- [Model Registry & Checkpoints](MODELS.md): Specifications for DINOv2 ViT-S/14, Phase 4 linear projection adapter, and FAISS.
- [Cryptographic Provenance](PROVENANCE.md): Cryptographic hashing, SHA-256 verification, and audit logging.
- [Deployment Guide](DEPLOYMENT.md): Docker Compose multi-container setup and local bare-metal execution.
- [Research Reproducibility](REPRODUCIBILITY.md): Protocol for verifying numerical consistency against frozen research benchmarks.
