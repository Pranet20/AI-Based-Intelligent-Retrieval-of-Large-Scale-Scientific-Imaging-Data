"""
Unit & Integration Tests for Phase 1 Scientific Data Freeze.

Tests:
1. Manifest determinism & completeness
2. Cryptographic hash verification against FINAL_IMAGE_MANIFEST.sha256
3. Deterministic split counts & disjoint partitions
4. Zero-leakage verification across train/validation/test splits
5. License audit schema validity
6. Deduplication audit integrity
"""

import json
import hashlib
from pathlib import Path
import pytest


@pytest.fixture(scope="module")
def image_manifest():
    p = Path("research/final_manifests/FINAL_IMAGE_MANIFEST.json")
    assert p.exists(), "FINAL_IMAGE_MANIFEST.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dataset_manifest():
    p = Path("research/final_manifests/FINAL_DATASET_MANIFEST.json")
    assert p.exists(), "FINAL_DATASET_MANIFEST.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def license_manifest():
    p = Path("research/final_manifests/FINAL_LICENSE_MANIFEST.json")
    assert p.exists(), "FINAL_LICENSE_MANIFEST.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def split_manifest():
    p = Path("research/final_manifests/FINAL_SPLIT_MANIFEST.json")
    assert p.exists(), "FINAL_SPLIT_MANIFEST.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def leakage_report():
    p = Path("research/audits/leakage_report.json")
    assert p.exists(), "leakage_report.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def duplicate_audit():
    p = Path("research/audits/duplicate_audit.json")
    assert p.exists(), "duplicate_audit.json does not exist"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def test_manifest_determinism_and_counts(image_manifest):
    """Test that all 6,085 active images are present and properly formatted."""
    assert image_manifest["manifest_version"] == "1.0.0"
    assert image_manifest["total_images"] == 6085
    images = image_manifest["images"]
    assert len(images) == 6085
    
    # Dataset breakdown
    hcci_count = sum(1 for img in images if img["dataset_id"] == "hcci")
    carinthia_count = sum(1 for img in images if img["dataset_id"] == "carinthia")
    bbbc_count = sum(1 for img in images if img["dataset_id"] == "bbbc021")
    
    assert hcci_count == 774, f"Expected 774 HCCI images, got {hcci_count}"
    assert carinthia_count == 4591, f"Expected 4591 Carinthia images, got {carinthia_count}"
    assert bbbc_count == 720, f"Expected 720 BBBC021 images, got {bbbc_count}"


def test_image_identity_schema(image_manifest):
    """Verify that every image contains mandatory identification fields."""
    mandatory_fields = [
        "image_id", "dataset_id", "filename", "relative_path",
        "sha256", "file_size", "mime_type", "width", "height",
        "channels", "bit_depth", "phash", "dhash"
    ]
    for img in image_manifest["images"][:50]:  # Sample check
        for field in mandatory_fields:
            assert field in img, f"Field {field} missing from image {img.get('image_id')}"
            assert img[field] is not None, f"Field {field} is None for image {img.get('image_id')}"
        assert len(img["sha256"]) == 64, "Invalid SHA-256 length"


def test_manifest_sha256_checksum():
    """Verify that FINAL_IMAGE_MANIFEST.sha256 matches the manifest file bytes."""
    manifest_file = Path("research/final_manifests/FINAL_IMAGE_MANIFEST.json")
    sha_file = Path("research/final_manifests/FINAL_IMAGE_MANIFEST.sha256")
    
    assert manifest_file.exists()
    assert sha_file.exists()
    
    with open(manifest_file, "rb") as f:
        computed_sha = hashlib.sha256(f.read()).hexdigest()
        
    recorded_sha = sha_file.read_text(encoding="utf-8").split()[0].strip()
    assert computed_sha == recorded_sha, f"Manifest hash mismatch: {computed_sha} != {recorded_sha}"


def test_splits_partition_and_determinism(split_manifest):
    """Verify that the primary retrieval split is completely disjoint and sums to 774."""
    hcci_split = split_manifest["hcci_primary_retrieval"]
    train = set(hcci_split["train"])
    val = set(hcci_split["validation"])
    test = set(hcci_split["test"])
    
    assert len(train) == 427, f"Expected 427 train images, got {len(train)}"
    assert len(val) == 135, f"Expected 135 val images, got {len(val)}"
    assert len(test) == 212, f"Expected 212 test images, got {len(test)}"
    
    # Mutual exclusivity
    assert len(train.intersection(val)) == 0, "Train and Val splits overlap!"
    assert len(train.intersection(test)) == 0, "Train and Test splits overlap!"
    assert len(val.intersection(test)) == 0, "Val and Test splits overlap!"
    assert len(train) + len(val) + len(test) == 774


def test_zero_leakage_audit(leakage_report):
    """Verify that the leakage audit report certifies zero leakage."""
    assert leakage_report["verdict"] == "LEAKAGE_FREE_PROTOCOL_VERIFIED"
    assert leakage_report["leakage_detected"] is False
    assert leakage_report["sha256_overlap"]["train_val_overlap"] == 0
    assert leakage_report["sha256_overlap"]["train_test_overlap"] == 0
    assert leakage_report["sha256_overlap"]["val_test_overlap"] == 0
    assert leakage_report["image_id_overlap"]["train_val_overlap"] == 0
    assert leakage_report["image_id_overlap"]["train_test_overlap"] == 0
    assert leakage_report["image_id_overlap"]["val_test_overlap"] == 0


def test_deduplication_audit_integrity(duplicate_audit):
    """Verify that deduplication audit executed cleanly without errors."""
    assert duplicate_audit["total_images_audited"] == 6085
    assert duplicate_audit["exact_sha256_duplicates_count"] == 0
    assert duplicate_audit["verdict"] == "ZERO_EXACT_DUPLICATES_VERIFIED"
    assert "phash_collision_clusters" in duplicate_audit
    assert "dhash_collision_clusters" in duplicate_audit


def test_license_audit_classifications(license_manifest):
    """Verify that all datasets have legitimate license classifications."""
    audits = license_manifest["license_audits"]
    assert "hcci" in audits
    assert "carinthia" in audits
    assert "bbbc021" in audits
    assert "sem_nanoscience" in audits
    assert "cigrocksem" in audits
    
    # Check HCCI is verified open access
    assert audits["hcci"]["classification"] == "LICENSE_VERIFIED"
    assert audits["hcci"]["redistribution_permitted"] is True
    
    # Check Carinthia is verified
    assert audits["carinthia"]["classification"] == "LICENSE_VERIFIED"
    assert audits["carinthia"]["redistribution_permitted"] is True
    
    # Check BBBC021 is CC0 public domain
    assert audits["bbbc021"]["classification"] == "LICENSE_VERIFIED"
    assert audits["bbbc021"]["redistribution_permitted"] is True


def test_dataset_cards_exist():
    """Verify that all required markdown dataset cards exist on disk."""
    cards_dir = Path("research/datasets/DATASET_CARDS")
    expected_cards = ["HCCI.md", "CARINTHIA.md", "BBBC021.md", "CIGROCKSEM.md", "SEM_NANOSCIENCE.md"]
    for c in expected_cards:
        p = cards_dir / c
        assert p.exists(), f"Dataset card {c} does not exist"
        assert p.stat().st_size > 100, f"Dataset card {c} is too small / empty"
