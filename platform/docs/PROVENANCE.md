# Cryptographic Provenance and Audit Specification

## 1. Principles of Scientific Provenance
To meet research data integrity standards, the SciData Platform records an immutable cryptographic event log for every state mutation:
1. **Source Immutability**: Uploaded image bytes are hashed via SHA-256 upon ingestion and saved to an immutable storage location. The file on disk is never altered.
2. **Audit Logging**: Every action (upload, feature extraction, duplicate detection, review queue triage, human review decision) is recorded with timestamp, actor ID, and cryptographic hashes in the `audit_logs` table.
3. **Traceability**: An image's full lifecycle can be reconstructed using `/api/v1/provenance/image/{id}`.

## 2. Audit Event Types
- `IMAGE_INGESTED`: Initial upload, file validation, and SHA-256 calculation.
- `QUALITY_EVALUATED`: Computation of the 6 physical quality risk indicators.
- `DUPLICATE_CASCADE_EVALUATED`: Exact and near-duplicate matching results.
- `EMBEDDING_EXTRACTED`: DINOv2 384-D representation and Phase 4 adapter projection.
- `FAISS_INDEXED`: Vector registered in exact `IndexFlatIP`.
- `NOVELTY_EVALUATED`: Relative embedding-space novelty score computed.
- `HUMAN_REVIEW_SUBMITTED`: Curator action committed (KEEP, DUPLICATE, LOW_QUALITY, etc.).
