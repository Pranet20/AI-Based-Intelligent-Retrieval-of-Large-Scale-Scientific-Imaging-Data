"""Dynamic scientific metadata normalizer for microscopy datasets."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from src.metadata.schema import NormalizedScientificMetadata, ScientificMetadataContainer


def parse_float_safe(value: Any) -> Optional[float]:
    """Safely parse float from various formats (numbers, strings with units)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        import math

        return None if math.isnan(value) else float(value)
    if isinstance(value, str):
        v = value.strip()
        if not v or v.lower() in ("nan", "none", "null", "n/a", "unknown"):
            return None
        # Extract leading numeric component
        match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", v)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
    return None


class MetadataNormalizer:
    """Normalizes raw acquisition metadata into standardized schema while preserving verbatim raw data."""

    @staticmethod
    def normalize_hcci_row(row_dict: Dict[str, Any]) -> ScientificMetadataContainer:
        """Dynamically normalize a metadata row from the HCCI dataset (Metadata_All_Samples.xlsx)."""
        # Store exact raw dict
        raw_metadata = {k: v for k, v in row_dict.items() if v is not None}

        # Dynamic mapping
        sem_val = str(row_dict.get("SEM", "")).strip() or None
        detector_val = str(row_dict.get("Detector", "")).strip() or None
        sample_val = str(row_dict.get("Sample", "")).strip() or None
        kind_val = str(row_dict.get("Kind", "")).strip() or None
        etching_val = str(row_dict.get("Etching", "")).strip() or None

        voltage = parse_float_safe(row_dict.get("Voltage"))
        mag = parse_float_safe(row_dict.get("Magnification"))
        pixel_size = parse_float_safe(row_dict.get("Pixel Size"))
        beam_curr = parse_float_safe(row_dict.get("Beam Current"))
        dwell_time = parse_float_safe(row_dict.get("Dwell Time"))
        chamber_press = parse_float_safe(row_dict.get("Chamber Pressure"))

        # Working distance in HCCI: e.g. 0.004838 meters -> 4.838 mm
        wd_raw = parse_float_safe(row_dict.get("Working Distance"))
        wd_mm: Optional[float] = None
        if wd_raw is not None:
            if wd_raw < 0.1:  # likely in meters
                wd_mm = round(wd_raw * 1000.0, 4)
            else:
                wd_mm = round(wd_raw, 4)

        normalized = NormalizedScientificMetadata(
            microscope=sem_val,
            instrument=sem_val,
            detector=detector_val,
            accelerating_voltage_kv=voltage,
            magnification=mag,
            pixel_size_nm=pixel_size,
            beam_current_na=beam_curr,
            dwell_time_us=dwell_time,
            working_distance_mm=wd_mm,
            chamber_pressure_pa=chamber_press,
            sample=sample_val,
            sample_state=kind_val,
            etching_agent=etching_val,
            imaging_mode="SEM",
            scale=f"{pixel_size} nm/pixel" if pixel_size else None,
            acquisition_date_if_available=None,
        )

        return ScientificMetadataContainer(raw_metadata=raw_metadata, normalized=normalized)

    @staticmethod
    def normalize_generic(
        raw_dict: Optional[Dict[str, Any]] = None,
        modality: Optional[str] = None,
    ) -> ScientificMetadataContainer:
        """Create container for datasets without rich instrument metadata."""
        raw = raw_dict or {}
        normalized = NormalizedScientificMetadata(
            imaging_mode=modality,
        )
        return ScientificMetadataContainer(raw_metadata=raw, normalized=normalized)
