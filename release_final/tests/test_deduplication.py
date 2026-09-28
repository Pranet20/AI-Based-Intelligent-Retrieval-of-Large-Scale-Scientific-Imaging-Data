"""Tests for exact duplicate and near-duplicate detection."""

from pathlib import Path
import shutil
from PIL import Image
import numpy as np
import pytest

from src.deduplication.exact import ExactDuplicateDetector
from src.deduplication.near_duplicate import NearDuplicateDetector


def test_exact_duplicate_detection(synthetic_uint8_png: Path, tmp_test_dir: Path) -> None:
    # Create identical copy
    copy_path = tmp_test_dir / "identical_copy.png"
    shutil.copyfile(synthetic_uint8_png, copy_path)

    # Calculate SHA
    from src.ingestion.reader import compute_sha256
    sha1 = compute_sha256(synthetic_uint8_png)
    sha2 = compute_sha256(copy_path)
    assert sha1 == sha2

    records = [
        {"image_id": "img_1", "sha256": sha1},
        {"image_id": "img_2", "sha256": sha2},
        {"image_id": "img_3", "sha256": "unique_hash_1234567890"},
    ]

    mapping, stats = ExactDuplicateDetector.identify_duplicates(records)

    assert stats.total_files == 3
    assert stats.unique_files == 2
    assert stats.duplicate_files == 2
    assert stats.duplicate_groups_count == 1
    assert mapping["img_1"] == mapping["img_2"]
    assert mapping["img_3"] is None


def test_near_duplicate_detection(tmp_test_dir: Path) -> None:
    # Create base image
    base_path = tmp_test_dir / "near_base.png"
    arr = np.zeros((128, 128), dtype=np.uint8)
    arr[30:90, 30:90] = 200
    Image.fromarray(arr).save(base_path)

    # Create slightly perturbed image (adds 1px noise)
    perturbed_path = tmp_test_dir / "near_perturbed.png"
    arr_p = arr.copy()
    arr_p[30, 30] = 199
    arr_p[31, 31] = 201
    Image.fromarray(arr_p).save(perturbed_path)

    # Create completely different image
    different_path = tmp_test_dir / "different.png"
    arr_diff = np.random.RandomState(99).randint(0, 255, (128, 128), dtype=np.uint8)
    Image.fromarray(arr_diff).save(different_path)

    detector = NearDuplicateDetector(max_hamming_distance=10)

    records = [
        {"image_id": "img_a", "file_path": str(base_path)},
        {"image_id": "img_b", "file_path": str(perturbed_path)},
        {"image_id": "img_c", "file_path": str(different_path)},
    ]

    mapping, groups = detector.cluster_near_duplicates(records)

    assert len(groups) == 1
    assert "img_a" in groups[0].image_ids
    assert "img_b" in groups[0].image_ids
    assert "img_c" not in groups[0].image_ids
    assert mapping["img_a"] == mapping["img_b"]
    assert mapping["img_c"] is None
