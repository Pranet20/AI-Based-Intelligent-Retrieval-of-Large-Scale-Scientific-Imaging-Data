"""
Unit tests for Phase 6 Track D: Provenance and Physical Linkage Audit.
"""

import json
import pandas as pd
import pytest

from src.integrity.provenance_audit import audit_hcci_metadata, audit_carinthia_metadata


def test_provenance_audit_hcci_flags_no_stage_coords():
    """Verify audit accurately flags missing stage coordinates and 1-to-1 ROI mapping."""
    fake_df = pd.DataFrame({
        "image_id": ["img1", "img2", "img3"],
        "roi_id": ["roi1", "roi2", "roi3"],
        "metadata_json": [
            json.dumps({"normalized": {"magnification": 1000.0, "accelerating_voltage_kv": 10000.0}}),
            json.dumps({"normalized": {"magnification": 2000.0, "accelerating_voltage_kv": 15000.0}}),
            json.dumps({"normalized": {"magnification": 5000.0, "accelerating_voltage_kv": 20000.0}}),
        ],
    })

    audit = audit_hcci_metadata(fake_df)
    assert audit["has_stage_coordinates"] is False
    assert audit["is_roi_one_to_one"] is True
    assert audit["physical_linkage_status"] == "NOT AVAILABLE / UNVERIFIED"
    assert audit["range_audit"]["magnification"]["in_expected_range"] is True


def test_provenance_audit_carinthia_missing_acquisition():
    """Verify Carinthia audit confirms missing acquisition metadata."""
    fake_carinthia = pd.DataFrame({
        "image_id": ["c1", "c2"],
        "width": [512, 512],
    })
    audit = audit_carinthia_metadata(fake_carinthia)
    assert audit["has_acquisition_metadata"] is False
