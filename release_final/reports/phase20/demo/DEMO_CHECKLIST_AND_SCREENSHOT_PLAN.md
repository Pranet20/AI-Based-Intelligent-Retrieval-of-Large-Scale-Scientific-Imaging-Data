# Demonstration Checklist & Screenshot Plan

## UI Screenshot Specifications
1. `screenshot_01_ingestion_provenance.png`: Dashboard showing ingested micrographs with SHA-256 digests and metadata tags.
2. `screenshot_02_focus_screening.png`: Quality gating panel displaying Tenengrad energy histogram and flagged blurred images.
3. `screenshot_03_vector_retrieval.png`: Similarity retrieval interface showing query image, top-5 retrieved matches, and 0.12 ms search latency.
4. `screenshot_04_decoupled_filter.png`: Filter panel scoping search by accelerating voltage (20 kV) and detector (BSE).
5. `screenshot_05_curation_workbench.png`: Curator review queue displaying flagged novel specimens with $D_{\text{ref}}$ distance gauge and confirmation buttons.

## Verification Checklist
- Host API active on `http://127.0.0.1:8000`
- Database tables initialized (`provenance_events`, `curation_queue`, `metadata_catalog`)
- HNSW index loaded in memory
