"""Tests for scientific metadata schema and dynamic normalization."""

import json
from src.metadata.normalizer import MetadataNormalizer, parse_float_safe
from src.metadata.schema import NormalizedScientificMetadata, ScientificMetadataContainer


def test_parse_float_safe() -> None:
    assert parse_float_safe(15.0) == 15.0
    assert parse_float_safe("20 kV") == 20.0
    assert parse_float_safe("0.004838") == 0.004838
    assert parse_float_safe("unknown") is None
    assert parse_float_safe(None) is None


def test_normalize_hcci_row() -> None:
    sample_row = {
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
    }

    container = MetadataNormalizer.normalize_hcci_row(sample_row)

    # Verbatim raw data preserved
    assert container.raw_metadata["SEM"] == "Helios G4 PFIB CXe"
    assert container.raw_metadata["Working Distance"] == 0.004838

    # Standardized normalized schema
    norm = container.normalized
    assert norm.microscope == "Helios G4 PFIB CXe"
    assert norm.detector == "ICE"
    assert norm.accelerating_voltage_kv == 15.0
    assert norm.magnification == 2500.0
    assert norm.sample_state == "AsCast"
    # Working distance converted to mm
    assert norm.working_distance_mm == 4.838

    # Serialization test
    d = container.to_json_dict()
    assert "raw_metadata" in d
    assert "normalized" in d
    assert json.dumps(d)


def test_generic_metadata_normalization() -> None:
    container = MetadataNormalizer.normalize_generic(
        raw_dict={"note": "unannotated_test"},
        modality="SEM",
    )
    assert container.normalized.imaging_mode == "SEM"
    assert container.normalized.accelerating_voltage_kv is None
    assert container.raw_metadata["note"] == "unannotated_test"
