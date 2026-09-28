"""Step 0: Generate PHASE20_SOURCE_INVENTORY.csv.

Catalogs all authoritative frozen artifacts across Phases 1-19, calculates SHA-256 hashes,
and documents their scientific and publication roles.
"""

import csv
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

# Key artifacts to include in source inventory
inventory_items = [
    # Data & Manifests
    {
        "artifact_id": "P20-INV-001",
        "path": "data/manifests/hcci_manifest.parquet",
        "artifact_type": "DATASET_MANIFEST",
        "phase": "Phase 1",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative in-domain HCCI metallurgy dataset manifest (774 images)",
        "publication_role": "Table 1 (Dataset Inventory), Table 2 (Splits)"
    },
    {
        "artifact_id": "P20-INV-002",
        "path": "data/manifests/carinthia_manifest.parquet",
        "artifact_type": "DATASET_MANIFEST",
        "phase": "Phase 2",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative cross-domain Carinthia defect SEM manifest (4591 images)",
        "publication_role": "Table 1, Table 8 (Cross-Domain Evaluation)"
    },
    {
        "artifact_id": "P20-INV-003",
        "path": "data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet",
        "artifact_type": "EMBEDDING_STORE",
        "phase": "Phase 2",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Frozen 384-d DINOv2 embeddings for HCCI dataset",
        "publication_role": "Representation benchmarking & vector search"
    },
    {
        "artifact_id": "P20-INV-004",
        "path": "data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet",
        "artifact_type": "EMBEDDING_STORE",
        "phase": "Phase 2",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Frozen 384-d DINOv2 embeddings for Carinthia dataset",
        "publication_role": "Leave-one-out nearest-neighbor class retrieval"
    },
    # Phase 3 Indexing
    {
        "artifact_id": "P20-INV-005",
        "path": "data/processed/indexes/combined_HNSW_M16_ef128.faiss",
        "artifact_type": "FAISS_INDEX",
        "phase": "Phase 3",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "HNSW index (M=16, efSearch=128) sub-millisecond retrieval",
        "publication_role": "Table 3 (FAISS Latency & Recall Scaling)"
    },
    {
        "artifact_id": "P20-INV-006",
        "path": "reports/phase3/latency_benchmark.csv",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 3",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Latency scaling benchmark (0.096 ms to 0.317 ms)",
        "publication_role": "Figure 5 (Query Latency vs Index Size)"
    },
    # Phase 4 Contrastive Adaptation
    {
        "artifact_id": "P20-INV-007",
        "path": "data/processed/phase4/checkpoints/best_checkpoint_seed42.pt",
        "artifact_type": "MODEL_CHECKPOINT",
        "phase": "Phase 4",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Trained SupCon projection head checkpoint (seed 42)",
        "publication_role": "Table 4 (Acquisition-Aware Adaptation)"
    },
    {
        "artifact_id": "P20-INV-008",
        "path": "data/processed/phase4/training_summary.json",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 4",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Phase 4 multi-seed metrics (R@1=0.9418, P@5=0.9053, gap reduction 68.15%)",
        "publication_role": "Table 4, Section 8 (Acquisition Adaptation)"
    },
    # Phase 5 Metadata Fusion
    {
        "artifact_id": "P20-INV-009",
        "path": "reports/phase9/PHASE9_FINAL_MRR_VERIFICATION_REPORT.md",
        "artifact_type": "AUDIT_REPORT",
        "phase": "Phase 9",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative metadata-only MRR (0.3443396) verification",
        "publication_role": "Table 5 (Metadata Retrieval & Fusion Results)"
    },
    # Phase 6 Data Integrity & Curation
    {
        "artifact_id": "P20-INV-010",
        "path": "artifacts/phase6/curation_summary.json",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 6",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Integrity & focus metrics (Focus AUROC=0.8803, 0 exact duplicates)",
        "publication_role": "Table 7 (Integrity Assessment & Redundancy)"
    },
    # Phase 8 Checksums
    {
        "artifact_id": "P20-INV-011",
        "path": "artifacts/phase8/final_frozen_checksums.json",
        "artifact_type": "CHECKSUM_MANIFEST",
        "phase": "Phase 8",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Cryptographic baseline for Phases 1-7",
        "publication_role": "Reproducibility validation"
    },
    # Phase 13 V2 Hardening
    {
        "artifact_id": "P20-INV-012",
        "path": "experiments/phase13/p13_exp01_multimodal_fusion/p13_exp01_metrics.json",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 13",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Multimodal fusion degradation results (Gated MLP 0.5896, Cross-Attn 0.6132)",
        "publication_role": "Table 9 (Multimodal Architectural Ablations)"
    },
    {
        "artifact_id": "P20-INV-013",
        "path": "experiments/phase13/p13_exp07_human_in_the_loop/p13_exp07_metrics.json",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 13",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Active queue human review workload reduction (41.2%, kappa=0.856)",
        "publication_role": "Table 10 (Curator Review Workflow)"
    },
    # Phase 14 Cross-Domain Results
    {
        "artifact_id": "P20-INV-014",
        "path": "reports/phase14/PHASE14_CROSS_DOMAIN_RESULTS.csv",
        "artifact_type": "METRIC_REPORT",
        "phase": "Phase 14",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Carinthia LOO Micro R@1=0.9952, Macro R@1=0.9090, TEM MMD^2=0.5410",
        "publication_role": "Table 8 (Cross-Domain & Cross-Modality Shift)"
    },
    # Phase 18 Production Deployment
    {
        "artifact_id": "P20-INV-015",
        "path": "reports/phase18/PHASE18_SECURITY_AUDIT.md",
        "artifact_type": "AUDIT_REPORT",
        "phase": "Phase 18",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "RBAC verification (5/5 passed), credential hygiene (0 secrets)",
        "publication_role": "Section 9 (Production Engineering & Security)"
    },
    {
        "artifact_id": "P20-INV-016",
        "path": "reports/final_closure/PHASE18_LOAD_TEST_REPORT.md",
        "artifact_type": "BENCHMARK_REPORT",
        "phase": "Phase 18",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Controlled host-side synthetic load test (600 reqs, 67.61 req/s peak)",
        "publication_role": "Table 11 (Platform Throughput & Resilience)"
    },
    # Phase 19 External Validation
    {
        "artifact_id": "P20-INV-017",
        "path": "reports/phase19/PHASE19_EXPERIMENT_REGISTRY.json",
        "artifact_type": "REGISTRY_JSON",
        "phase": "Phase 19",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Complete registry for experiments P19-EXP-01 through P19-EXP-10",
        "publication_role": "Table 12 (Comprehensive Experiment Registry)"
    },
    {
        "artifact_id": "P20-INV-018",
        "path": "reports/phase19/FINAL_CLAIM_EVIDENCE_GRAPH_V3.json",
        "artifact_type": "CLAIM_GRAPH",
        "phase": "Phase 19",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative 22-claim evidence graph (0 unsupported claims)",
        "publication_role": "Table 12 (Claim-Evidence Traceability)"
    },
    # Final Closure Deliverables
    {
        "artifact_id": "P20-INV-019",
        "path": "reports/final_closure/FINAL_CLOSURE_BASELINE_MANIFEST.csv",
        "artifact_type": "CHECKSUM_MANIFEST",
        "phase": "Final Closure",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "145/145 complete historical artifact inventory verification",
        "publication_role": "Section 12 (Artifact Traceability & Immutability)"
    },
    {
        "artifact_id": "P20-INV-020",
        "path": "reports/final_closure/FINAL_LIMITATIONS.md",
        "artifact_type": "LIMITATIONS_REGISTER",
        "phase": "Final Closure",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative register of the 6 substantive system limitations",
        "publication_role": "Section 11 (Declared System Limitations)"
    },
    {
        "artifact_id": "P20-INV-021",
        "path": "reports/final_closure/P19_RANDOM_BASELINE_FINAL_VERIFICATION.md",
        "artifact_type": "MATHEMATICAL_AUDIT",
        "phase": "Final Closure",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Mathematical proof for 1/6=0.1667 and H6/6=49/120=0.4083",
        "publication_role": "Section 8, Table 8 (Mathematical Baseline)"
    },
    {
        "artifact_id": "P20-INV-022",
        "path": "reports/final_closure/FINAL_DATASET_RIGHTS_MATRIX.csv",
        "artifact_type": "GOVERNANCE_MATRIX",
        "phase": "Final Closure",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Rights governance across all 8 datasets (manifest-first compliance)",
        "publication_role": "Table 1 (Governance & Redistribution Compliance)"
    },
    {
        "artifact_id": "P20-INV-023",
        "path": "reports/final_closure/PERMANENT_RELEASE_FREEZE.md",
        "artifact_type": "FREEZE_CERTIFICATE",
        "phase": "Final Closure",
        "authoritative": True,
        "frozen": True,
        "scientific_role": "Authoritative freeze certification for Release V3 Final",
        "publication_role": "Section 12 (Release Certification)"
    }
]

rows = []
for item in inventory_items:
    file_path = root / item["path"]
    if file_path.exists():
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        chk = hasher.hexdigest()
    else:
        chk = "FILE_NOT_FOUND"

    rows.append({
        "artifact_id": item["artifact_id"],
        "path": item["path"],
        "artifact_type": item["artifact_type"],
        "phase": item["phase"],
        "authoritative": "YES" if item["authoritative"] else "NO",
        "frozen": "YES" if item["frozen"] else "NO",
        "checksum": chk,
        "scientific_role": item["scientific_role"],
        "publication_role": item["publication_role"]
    })

out_csv = root / "reports" / "phase20" / "PHASE20_SOURCE_INVENTORY.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "artifact_id", "path", "artifact_type", "phase",
        "authoritative", "frozen", "checksum", "scientific_role", "publication_role"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated source inventory with {len(rows)} authoritative artifacts at {out_csv}")
