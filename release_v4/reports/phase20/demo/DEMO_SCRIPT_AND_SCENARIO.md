# PLATFORM DEMONSTRATION SCRIPT & OPERATIONAL SCENARIO

**Scenario**: High-Throughput Ingestion, Automated Defocus Screening, Sub-Millisecond Specimen Retrieval, and Human-in-the-Loop Triage

## Demonstration Steps
1. **Micrograph Ingestion**:
   - Operator submits batch of 10 uncurated SEM micrographs (TIFF format).
   - System computes SHA-256 digests and logs provenance events to SQLite audit database.
   - Batch throughput: verified up to 14.80 img/s.

2. **Integrity Screening Cascade**:
   - System computes Tenengrad focus scores.
   - 2 blurred micrographs (< threshold 42.5) are automatically flagged and routed to Curation Queue.
   - Perceptual hash and cosine matching identify 1 near-duplicate acquisition pair.

3. **Sub-Millisecond Vector Search**:
   - Operator queries repository with an uncharacterized mineral specimen micrograph.
   - Pretrained DINOv2 ViT-S/14 extracts 384-d latent embedding.
   - FAISS HNSW searches 100,000-vector index in 0.317 ms.
   - Top-1 result correctly identifies mineral phase (Sphalerite) with cosine similarity 0.9481.

4. **Decoupled Metadata Scoping**:
   - Operator applies metadata filter: `detector = 'BSE' AND voltage = '20kV'`.
   - Inverted index scopes candidate set without degrading visual feature geometry.

5. **Novelty Flagging & Expert Review**:
   - An external out-of-distribution specimen is submitted.
   - Latent distance $D_{\text{ref}} = 0.5210$ (> in-domain mean 0.2410) triggers novelty flag.
   - Micrograph enters double-blinded curator workbench for expert mineralogist review.

## Verification Checklist
- [x] Ingestion provenance SHA-256 verified
- [x] Tenengrad focus quality gate verified
- [x] FAISS HNSW query latency < 1 ms verified
- [x] Decoupled metadata filtering verified
- [x] Curator triage queue actionability verified
