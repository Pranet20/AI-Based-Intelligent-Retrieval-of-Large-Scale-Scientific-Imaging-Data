"""Tests for dataset manifest generation, validation, and Parquet/CSV round-trip."""

from pathlib import Path
import pytest

from src.ingestion.manifest import ManifestManager, ManifestRecord, MANIFEST_COLUMNS


def test_manifest_record_and_save(tmp_test_dir: Path) -> None:
    rec1 = ManifestRecord(
        dataset_id="test_ds",
        sample_id="sample_01",
        image_id="test_01",
        relative_path="sample_01.png",
        absolute_path_if_local_only=str(tmp_test_dir / "sample_01.png"),
        filename="sample_01.png",
        extension=".png",
        file_size_bytes=1024,
        sha256="abc1234567890",
        width=128,
        height=128,
        channels=1,
        bit_depth=8,
        dtype="uint8",
        format="png",
        color_mode="L",
        modality="SEM",
        split="train",
        label="defect_a",
        source_label="1",
        group_id="group_1",
        specimen_id="spec_1",
        roi_id="roi_1",
        acquisition_id="acq_1",
        metadata_json="{}",
        quality_status="PASS",
        quality_score=0.92,
        duplicate_group_id=None,
        near_duplicate_group_id=None,
    )

    prefix = tmp_test_dir / "test_manifest"
    res = ManifestManager.save_manifest([rec1], prefix)

    assert Path(res["parquet"]).is_file()
    assert Path(res["csv"]).is_file()
    assert res["count"] == "1"

    # Test load Parquet
    df_p = ManifestManager.load_manifest(res["parquet"])
    assert len(df_p) == 1
    assert list(df_p.columns) == MANIFEST_COLUMNS
    assert df_p.iloc[0]["dataset_id"] == "test_ds"
    assert df_p.iloc[0]["quality_score"] == pytest.approx(0.92, 0.01)

    # Test load CSV
    df_c = ManifestManager.load_manifest(res["csv"])
    assert len(df_c) == 1
    assert df_c.iloc[0]["image_id"] == "test_01"
