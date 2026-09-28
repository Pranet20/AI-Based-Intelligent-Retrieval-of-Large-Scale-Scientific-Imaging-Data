"""Tests for dataset adapters using synthetic structures."""

from pathlib import Path
from PIL import Image
import pandas as pd
import pytest

from src.datasets.base import BaseDatasetAdapter
from src.datasets.hcci import HCCIDatasetAdapter
from src.datasets.carinthia import CarinthiaDatasetAdapter
from src.datasets.registry import DatasetRegistry
from src.ingestion.manifest import ManifestRecord


def test_hcci_adapter_synthetic(tmp_test_dir: Path) -> None:
    # Build synthetic HCCI structure
    hcci_dir = tmp_test_dir / "hcci_mock"
    img_dir = hcci_dir / "Images"
    img_dir.mkdir(parents=True, exist_ok=True)

    # Save mock image 1.png
    im = Image.new("L", (64, 64), color=120)
    im.save(img_dir / "1.png")

    # Save mock metadata
    meta_df = pd.DataFrame([{
        "File Name": 1,
        "SEM": "Helios G4 PFIB CXe",
        "Detector": "ICE",
        "Voltage": 15,
        "Magnification": 2500,
        "Etching": "Picral 4%",
        "Sample": "HCCI_1",
        "Kind": "AsCast",
        "Pixel Size": 48.3,
        "Beam Current": 0.8,
        "Dwell Time": 10.0,
        "Chamber Pressure": 0.0014,
        "Working Distance": 0.004838,
    }])
    meta_df.to_excel(hcci_dir / "Metadata_All_Samples.xlsx", index=False)

    registry = DatasetRegistry()
    entry = registry.get("hcci")

    adapter = HCCIDatasetAdapter(entry, root_dir=hcci_dir)
    records = adapter.build_manifest_records()

    assert len(records) == 1
    rec = records[0]
    assert rec.dataset_id == "hcci"
    assert rec.image_id == "hcci_1"
    assert rec.specimen_id == "HCCI_1"
    assert rec.label == "AsCast"
    assert "Helios G4 PFIB CXe" in rec.acquisition_id


def test_carinthia_adapter_synthetic(tmp_test_dir: Path) -> None:
    # Build synthetic Carinthia structure
    carinthia_dir = tmp_test_dir / "carinthia_mock"
    img_dir = carinthia_dir / "data" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    im = Image.new("RGB", (64, 64), color=(100, 100, 100))
    im.save(img_dir / "defect_sample.jpg")

    # Write semicolon delimited carinthia.csv
    csv_file = carinthia_dir / "data" / "carinthia.csv"
    csv_file.write_text("image_path;file_name;label\ndata/images/defect_sample.jpg;defect_sample.jpg;3\n")

    registry = DatasetRegistry()
    entry = registry.get("carinthia")

    adapter = CarinthiaDatasetAdapter(entry, root_dir=carinthia_dir)
    records = adapter.build_manifest_records()

    assert len(records) == 1
    rec = records[0]
    assert rec.dataset_id == "carinthia"
    assert rec.label == "defect_class_3"
    assert rec.source_label == "3"
