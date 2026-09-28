"""Script to run end-to-end ingestion, quality audit, deduplication, and report generation."""

from __future__ import annotations

import json
from pathlib import Path

from src.datasets import ADAPTER_MAPPING, DatasetRegistry
from src.deduplication.exact import ExactDuplicateDetector
from src.deduplication.near_duplicate import NearDuplicateDetector
from src.ingestion.manifest import ManifestManager
from src.ingestion.reader import ScientificImageReader
from src.quality.evaluator import QualityEvaluator
from src.quality.metrics import calculate_quality_metrics
from src.utils.contact_sheet import generate_contact_sheet
from src.utils.logging import AuditErrorCollector, get_logger
from src.utils.report_generator import DatasetReportGenerator
from src.utils.versioning import DatasetVersionManager

logger = get_logger("scripts.run_full_audit")


def audit_single_dataset(dataset_id: str, limit: int | None = None) -> None:
    registry = DatasetRegistry()
    entry = registry.get(dataset_id)

    raw_path = Path(entry.local_path)
    if not raw_path.exists() or not any(raw_path.iterdir()):
        logger.warning(
            "Dataset '%s' local directory %s is empty or missing. Skipping full run.",
            dataset_id,
            raw_path,
        )
        return

    adapter_cls = ADAPTER_MAPPING.get(dataset_id)
    if not adapter_cls:
        logger.error("No adapter registered for %s", dataset_id)
        return

    error_collector = AuditErrorCollector()
    adapter = adapter_cls(entry, error_collector=error_collector)

    logger.info("Ingesting %s (%s)...", entry.name, dataset_id)
    records = adapter.build_manifest_records()
    if limit and limit > 0:
        records = records[:limit]

    logger.info("Discovered and processed %d records for %s", len(records), dataset_id)
    dict_records = [r.to_dict() for r in records]

    # Deduplication
    exact_map, exact_stats = ExactDuplicateDetector.identify_duplicates(dict_records)
    logger.info(
        "Exact duplicates: %d files in %d groups",
        exact_stats.duplicate_files,
        exact_stats.duplicate_groups_count,
    )

    near_detector = NearDuplicateDetector(config_path="configs/deduplication.yaml")
    near_map, near_groups = near_detector.cluster_near_duplicates(
        dict_records, id_key="image_id", path_key="absolute_path_if_local_only"
    )
    logger.info("Near-duplicate clusters: %d clusters", len(near_groups))

    # Quality indicators
    evaluator = QualityEvaluator(config_path="configs/quality.yaml")
    for r in dict_records:
        r["duplicate_group_id"] = exact_map.get(r["image_id"])
        r["near_duplicate_group_id"] = near_map.get(r["image_id"])

        fpath = r.get("absolute_path_if_local_only")
        if fpath and Path(fpath).is_file():
            try:
                arr, _ = ScientificImageReader.load_array(fpath)
                q_metrics = calculate_quality_metrics(arr, bit_depth=r.get("bit_depth", 8))
                status, score, flags = evaluator.evaluate(q_metrics, bit_depth=r.get("bit_depth", 8))
                r["quality_status"] = status
                r["quality_score"] = score
            except Exception as e:
                error_collector.record_error(dataset_id, fpath, "quality_metrics", str(e))
                r["quality_status"] = "ERROR"
                r["quality_score"] = 0.0

    # Save manifest
    manifest_prefix = Path("data/manifests") / f"{dataset_id}_manifest"
    save_res = ManifestManager.save_manifest(dict_records, manifest_prefix)
    logger.info("Manifest saved: %s (Parquet) and %s (CSV)", save_res["parquet"], save_res["csv"])

    # Version tracking
    v_mgr = DatasetVersionManager()
    total_bytes = sum(r["file_size_bytes"] for r in dict_records)
    v_mgr.record_version(entry, save_res["parquet"], len(dict_records), total_bytes)

    # Reports and contact sheet
    df = ManifestManager.load_manifest(save_res["parquet"])
    rep_gen = DatasetReportGenerator()
    rep_files = rep_gen.generate_full_report(entry, df, error_collector.to_dict())
    logger.info("Audit reports generated: HTML=%s, JSON=%s", rep_files["html"], rep_files["json"])

    cs_path = Path("reports/dataset_audit/contact_sheets") / f"{dataset_id}_contact_sheet.jpg"
    try:
        generate_contact_sheet(dict_records, cs_path, dataset_id=dataset_id)
        logger.info("Contact sheet saved: %s", cs_path)
    except Exception as e:
        logger.warning("Contact sheet skipped: %s", e)


def main() -> None:
    logger.info("Starting Full Dataset Audit Pipeline across all available datasets...")
    registry = DatasetRegistry()
    for entry in registry.list_all():
        audit_single_dataset(entry.dataset_id)
    logger.info("Audit pipeline finished.")


if __name__ == "__main__":
    main()
