"""Tests for Dataset Registry configuration, licensing policies, and variants."""

import json
from pathlib import Path
import sys
import pytest
from src.datasets.registry import DatasetRegistry, DatasetRegistryEntry


def test_registry_loading() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    all_datasets = registry.list_all()
    assert len(all_datasets) == 6, f"Expected 6 datasets, found {len(all_datasets)}"

    expected_ids = {"hcci", "carinthia", "sem_nanoscience", "atomagined", "cigrocksem", "microal"}
    found_ids = {d.dataset_id for d in all_datasets}
    assert expected_ids == found_ids


def test_dataset_roles() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    assert registry.get("hcci").role == "robustness_and_metadata"
    assert registry.get("carinthia").role == "defect_anomaly_evaluation"
    assert registry.get("sem_nanoscience").role == "general_sem_representation"
    assert registry.get("atomagined").role == "retrieval_benchmark"
    assert registry.get("cigrocksem").role == "cross_domain_validation"
    assert registry.get("microal").role == "materials_microscopy_extension"


def test_no_fabricated_licenses() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    # Strictly verified licensing policy:
    # HCCI & Carinthia Zenodo records lack explicit badge -> UNKNOWN_VERIFY_SOURCE_TERMS
    assert registry.get("hcci").license_status == "UNKNOWN_VERIFY_SOURCE_TERMS"
    assert registry.get("carinthia").license_status == "UNKNOWN_VERIFY_SOURCE_TERMS"
    # SEM Nanoscience article explicitly specifies CC BY 4.0
    assert registry.get("sem_nanoscience").license_status == "VERIFIED_OPEN_ACCESS"
    assert registry.get("sem_nanoscience").license == "CC-BY-4.0"
    # atomagined repo is MIT, dataset terms require confirmation
    assert registry.get("atomagined").repository_license == "MIT"
    assert registry.get("atomagined").license_status == "REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION"
    # MicroAl restricted academic subsets
    assert registry.get("microal").license_status == "ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION"


def test_dataset_acquisition_status() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    assert registry.get("hcci").acquisition_status == "FULLY_INGESTED_AVAILABLE_FILES"
    assert registry.get("carinthia").acquisition_status == "FULLY_INGESTED"
    assert registry.get("sem_nanoscience").acquisition_status == "NOT_YET_DOWNLOADED"
    assert registry.get("atomagined").acquisition_status == "NOT_YET_DOWNLOADED"
    assert registry.get("cigrocksem").acquisition_status == "NOT_YET_DOWNLOADED"
    assert registry.get("microal").acquisition_status == "NOT_YET_DOWNLOADED"


def test_hcci_ingestion_status_does_not_imply_777_physical_images() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    entry = registry.get("hcci")
    assert entry.acquisition_status == "FULLY_INGESTED_AVAILABLE_FILES"
    assert "774" in entry.notes
    assert "777" in entry.notes
    assert "omitted" in entry.notes


def test_sem_nanoscience_variants_configuration() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    entry = registry.get("sem_nanoscience")
    assert entry.dataset_family == "SEM_Nanoscience"
    assert entry.variants_available is not None
    assert "Original_SEM_Dataset" in entry.variants_available
    assert "Hierarchical_Dataset" in entry.variants_available
    assert "Majority_Dataset" in entry.variants_available
    assert "100_Percent_Dataset" in entry.variants_available


def test_sem_nanoscience_authoritative_counts_and_correction() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    entry = registry.get("sem_nanoscience")
    assert entry.approximate_image_count == 18577
    assert entry.variants_available["Original_SEM_Dataset"]["image_count"] == 18577
    assert entry.variants_available["Hierarchical_Dataset"]["image_count"] == 1038
    assert entry.variants_available["Majority_Dataset"]["image_count"] == 21272
    assert entry.variants_available["100_Percent_Dataset"]["image_count"] == 21169
    assert "190018" in entry.citation or "190018" in entry.notes


def test_hcci_count_reconciliation() -> None:
    recon_path = Path("reports/dataset_audit/hcci_count_reconciliation.json")
    assert recon_path.is_file(), f"Reconciliation report not found at {recon_path}"

    with open(recon_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["official_image_count"] == 777
    assert data["metadata_record_count"] == 777
    assert data["discovered_image_count"] == 774
    assert data["manifest_image_count"] == 774
    assert data["missing_image_records"] == ["10", "20", "30"]
    assert len(data["explanation"]) > 20


def test_python_runtime_is_311() -> None:
    v = sys.version_info
    assert v.major == 3 and v.minor == 11, f"Expected Python 3.11.x, got {v.major}.{v.minor}.{v.micro}"


def test_missing_dataset_raises() -> None:
    registry = DatasetRegistry("configs/datasets.yaml")
    with pytest.raises(KeyError):
        registry.get("non_existent_dataset")
