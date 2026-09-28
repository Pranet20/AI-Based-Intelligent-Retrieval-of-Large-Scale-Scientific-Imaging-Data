"""CLI subcommands for dataset management, auditing, and manifest generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import pandas as pd

from src.datasets import ADAPTER_MAPPING, DatasetRegistry
from src.datasets.downloader import DatasetDownloader
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

logger = get_logger("cli.dataset")


@click.group(name="dataset", help="Manage scientific microscopy datasets, manifests, and audits.")
def dataset_group() -> None:
    pass


@dataset_group.command(name="list", help="List all registered scientific datasets and their roles.")
@click.option("--enabled-only", is_flag=True, help="Display only enabled datasets.")
@click.option("--config", default="configs/datasets.yaml", help="Path to datasets.yaml configuration.")
def list_datasets(enabled_only: bool, config: str) -> None:
    try:
        registry = DatasetRegistry(config)
        entries = registry.list_all(enabled_only=enabled_only)
        click.echo("=" * 90)
        click.echo(f"{'ID':<18} | {'ROLE':<28} | {'MODALITY':<12} | {'IMAGES (approx)':<15} | {'DOI'}")
        click.echo("-" * 90)
        for e in entries:
            click.echo(f"{e.dataset_id:<18} | {e.role:<28} | {e.modality:<12} | {e.approximate_image_count:<15} | {e.doi}")
        click.echo("=" * 90)
        click.echo(f"Total registered datasets: {len(entries)}")
    except Exception as e:
        click.echo(f"Error loading dataset registry: {e}", err=True)


@dataset_group.command(name="register", help="Validate registered datasets configuration.")
@click.option("--config", default="configs/datasets.yaml", help="Path to datasets.yaml configuration.")
def register_datasets(config: str) -> None:
    try:
        registry = DatasetRegistry(config)
        issues = registry.validate_all()
        click.echo(f"Validated {len(registry.list_all())} dataset configurations.")
        if issues:
            click.echo("Validation notices / issues detected:")
            for issue in issues:
                click.echo(f"  * {issue}")
        else:
            click.echo("All dataset registry configurations are strictly valid.")
    except Exception as e:
        click.echo(f"Error during registration validation: {e}", err=True)


@dataset_group.command(name="download", help="Acquire or extract dataset archives.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier (e.g. hcci, carinthia).")
@click.option("--yes", is_flag=True, help="Confirm download/extraction without interactive prompt.")
def download_dataset(dataset_id: str, yes: bool) -> None:
    downloader = DatasetDownloader()
    info = downloader.get_acquisition_info(dataset_id)

    click.echo("=" * 80)
    click.echo(f"DATASET ACQUISITION: {info['name']} ({dataset_id})")
    click.echo(f"Source URL:    {info['source_url']}")
    click.echo(f"DOI:           {info['doi']}")
    click.echo(f"Expected Size: {info['expected_size']}")
    click.echo(f"Target Path:   {info['destination']}")
    click.echo(f"License:       {info['license']}")
    click.echo(f"Access Notes:  {info['access_notes']}")
    click.echo("=" * 80)

    # First check if local archive exists and unpack
    unpacked = downloader.unpack_local_archive_if_available(dataset_id)
    if unpacked:
        click.echo(f"Successfully extracted dataset from local archive into: {info['destination']}")
        return

    # If already extracted
    if info["is_extracted"]:
        click.echo(f"Dataset files are already present in {info['destination']}.")
        return

    # Otherwise display manual acquisition guide
    click.echo(downloader.get_manual_instructions(dataset_id))


@dataset_group.command(name="manifest", help="Generate normalized Parquet and CSV manifest for a dataset.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
@click.option("--output-dir", default="data/manifests", help="Output directory for manifests.")
@click.option("--limit", default=None, type=int, help="Optional limit on images to process for quick testing.")
def generate_manifest(dataset_id: str, output_dir: str, limit: Optional[int]) -> None:
    registry = DatasetRegistry()
    entry = registry.get(dataset_id)

    adapter_cls = ADAPTER_MAPPING.get(dataset_id)
    if not adapter_cls:
        click.echo(f"No adapter implemented for dataset: {dataset_id}", err=True)
        return

    error_collector = AuditErrorCollector()
    adapter = adapter_cls(entry, error_collector=error_collector)

    click.echo(f"Building manifest records for {entry.name}...")
    records = adapter.build_manifest_records(limit=limit)

    if not records:
        click.echo(f"No records generated for {dataset_id}. Check if dataset files exist in {entry.local_path}.", err=True)
        return

    output_prefix = Path(output_dir) / f"{dataset_id}_manifest"
    result = ManifestManager.save_manifest(records, output_prefix)

    # Update dataset versions
    version_mgr = DatasetVersionManager()
    total_bytes = sum(r.file_size_bytes for r in records)
    version_mgr.record_version(entry, result["parquet"], len(records), total_bytes)

    click.echo(f"Successfully generated manifest for {dataset_id}:")
    click.echo(f"  Parquet: {result['parquet']}")
    click.echo(f"  CSV:     {result['csv']}")
    click.echo(f"  Count:   {result['count']} images")


@dataset_group.command(name="audit", help="Audit dataset images, compute quality indicators and exact/near duplicates.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
@click.option("--limit", default=None, type=int, help="Optional limit for rapid testing.")
def audit_dataset(dataset_id: str, limit: Optional[int]) -> None:
    registry = DatasetRegistry()
    entry = registry.get(dataset_id)

    adapter_cls = ADAPTER_MAPPING.get(dataset_id)
    if not adapter_cls:
        click.echo(f"No adapter found for {dataset_id}", err=True)
        return

    error_collector = AuditErrorCollector()
    adapter = adapter_cls(entry, error_collector=error_collector)

    click.echo(f"Discovering and ingesting {dataset_id}...")
    records = adapter.build_manifest_records(limit=limit)

    if not records:
        click.echo(f"No images discovered in {entry.local_path}", err=True)
        return

    click.echo(f"Auditing {len(records)} images...")
    dict_records = [r.to_dict() for r in records]

    # 1. Exact Duplicate Detection
    exact_map, exact_stats = ExactDuplicateDetector.identify_duplicates(dict_records)
    click.echo(f"Exact duplicates found: {exact_stats.duplicate_files} files in {exact_stats.duplicate_groups_count} groups.")

    # 2. Near Duplicate Detection
    near_detector = NearDuplicateDetector(config_path="configs/deduplication.yaml")
    near_map, near_groups = near_detector.cluster_near_duplicates(
        dict_records, id_key="image_id", path_key="absolute_path_if_local_only"
    )
    click.echo(f"Near-duplicate clusters found: {len(near_groups)} clusters.")

    # 3. Quality Indicators Computation
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

    # Save audited manifest
    output_prefix = Path("data/manifests") / f"{dataset_id}_manifest"
    ManifestManager.save_manifest(dict_records, output_prefix)

    # Save Audit Error Report if any
    if error_collector.has_errors():
        err_path = Path("reports/dataset_audit") / f"{dataset_id}_errors.json"
        error_collector.save_report(err_path)
        click.echo(f"Recorded {error_collector.error_count()} errors in {err_path}")

    click.echo(f"Completed audit for {dataset_id}. Manifest updated.")


@dataset_group.command(name="stats", help="Show summary statistics for an ingested dataset.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
def show_stats(dataset_id: str) -> None:
    manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.parquet"
    if not manifest_path.is_file():
        # Try CSV
        manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.csv"
        if not manifest_path.is_file():
            click.echo(f"No manifest found for {dataset_id}. Run 'research dataset manifest --id {dataset_id}' first.", err=True)
            return

    df = ManifestManager.load_manifest(manifest_path)
    click.echo("=" * 60)
    click.echo(f"DATASET STATISTICS: {dataset_id}")
    click.echo("=" * 60)
    click.echo(f"Total Images:     {len(df)}")
    if "file_size_bytes" in df.columns:
        click.echo(f"Total Storage:    {df['file_size_bytes'].sum() / (1024*1024):.2f} MB")
    if "format" in df.columns:
        click.echo(f"Formats:          {df['format'].value_counts().to_dict()}")
    if "bit_depth" in df.columns:
        click.echo(f"Bit Depths:       {df['bit_depth'].value_counts().to_dict()}")
    if "quality_status" in df.columns:
        click.echo(f"Quality Status:   {df['quality_status'].value_counts().to_dict()}")
    if "duplicate_group_id" in df.columns:
        dups = df["duplicate_group_id"].notna().sum()
        click.echo(f"Exact Duplicates: {dups}")
    if "near_duplicate_group_id" in df.columns:
        ndups = df["near_duplicate_group_id"].notna().sum()
        click.echo(f"Near Duplicates:  {ndups}")
    click.echo("=" * 60)


@dataset_group.command(name="duplicates", help="Inspect exact and near duplicate clusters.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
def show_duplicates(dataset_id: str) -> None:
    manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.parquet"
    if not manifest_path.is_file():
        manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.csv"
    if not manifest_path.is_file():
        click.echo(f"No manifest found for {dataset_id}.", err=True)
        return

    df = ManifestManager.load_manifest(manifest_path)
    exact_df = df[df["duplicate_group_id"].notna()]
    near_df = df[df["near_duplicate_group_id"].notna()]

    click.echo(f"Exact Duplicate Groups in {dataset_id}:")
    if not exact_df.empty:
        for grp, grp_df in exact_df.groupby("duplicate_group_id"):
            click.echo(f"  Group {grp}: {len(grp_df)} images ({', '.join(grp_df['filename'].tolist()[:5])}...)")
    else:
        click.echo("  No exact duplicates detected.")

    click.echo(f"\nNear-Duplicate Groups in {dataset_id}:")
    if not near_df.empty:
        for grp, grp_df in near_df.groupby("near_duplicate_group_id"):
            click.echo(f"  Group {grp}: {len(grp_df)} images ({', '.join(grp_df['filename'].tolist()[:5])}...)")
    else:
        click.echo("  No near-duplicates detected.")


@dataset_group.command(name="quality", help="Inspect computational image quality breakdown.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
def show_quality(dataset_id: str) -> None:
    manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.parquet"
    if not manifest_path.is_file():
        manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.csv"
    if not manifest_path.is_file():
        click.echo(f"No manifest found for {dataset_id}.", err=True)
        return

    df = ManifestManager.load_manifest(manifest_path)
    if "quality_status" not in df.columns or df["quality_status"].dropna().empty:
        click.echo(f"Quality evaluation not yet run on {dataset_id}. Run 'research dataset audit --id {dataset_id}' first.")
        return

    click.echo(f"Quality Status Breakdown for {dataset_id}:")
    counts = df["quality_status"].value_counts()
    for status, count in counts.items():
        pct = (count / len(df)) * 100
        click.echo(f"  {status:<10}: {count} ({pct:.1f}%)")


@dataset_group.command(name="report", help="Generate HTML and JSON audit reports and contact sheet.")
@click.option("--id", "dataset_id", required=True, help="Dataset identifier.")
def generate_report(dataset_id: str) -> None:
    registry = DatasetRegistry()
    entry = registry.get(dataset_id)

    manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.parquet"
    if not manifest_path.is_file():
        manifest_path = Path("data/manifests") / f"{dataset_id}_manifest.csv"
    if not manifest_path.is_file():
        click.echo(f"No manifest found for {dataset_id}. Run audit first.", err=True)
        return

    df = ManifestManager.load_manifest(manifest_path)
    report_gen = DatasetReportGenerator()
    results = report_gen.generate_full_report(entry, df)

    # Contact sheet
    cs_path = Path("reports/dataset_audit/contact_sheets") / f"{dataset_id}_contact_sheet.jpg"
    try:
        generate_contact_sheet(df.to_dict(orient="records"), cs_path, dataset_id=dataset_id)
        click.echo(f"  Contact Sheet: {cs_path}")
    except Exception as e:
        click.echo(f"  Note: Contact sheet generation skipped: {e}")

    click.echo(f"Audit report generated for {dataset_id}:")
    click.echo(f"  HTML: {results['html']}")
    click.echo(f"  JSON: {results['json']}")
