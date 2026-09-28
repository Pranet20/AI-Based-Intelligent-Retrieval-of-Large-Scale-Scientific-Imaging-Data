"""Pydantic schemas for raw and normalized scientific metadata."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class NormalizedScientificMetadata(BaseModel):
    """Normalized representation of scientific microscopy metadata.

    Fields are standard across all microscope manufacturers and data repositories.
    Missing fields default to None / null. No fabricated values.
    """

    model_config = ConfigDict(extra="ignore")

    microscope: Optional[str] = Field(default=None, description="Microscope model name/type")
    instrument: Optional[str] = Field(default=None, description="Instrument family or facility ID")
    detector: Optional[str] = Field(default=None, description="Detector type (e.g. SE, BSE, HAADF)")
    accelerating_voltage_kv: Optional[float] = Field(
        default=None, description="Accelerating voltage in kilovolts (kV)"
    )
    magnification: Optional[float] = Field(
        default=None, description="Nominal magnification factor (e.g. 5000.0)"
    )
    pixel_size_nm: Optional[float] = Field(
        default=None, description="Calibrated pixel size in nanometers (nm)"
    )
    beam_current_na: Optional[float] = Field(
        default=None, description="Beam current in nanoamperes (nA)"
    )
    dwell_time_us: Optional[float] = Field(
        default=None, description="Pixel dwell time in microseconds (µs)"
    )
    working_distance_mm: Optional[float] = Field(
        default=None, description="Working distance in millimeters (mm)"
    )
    chamber_pressure_pa: Optional[float] = Field(
        default=None, description="Specimen chamber pressure in Pascals (Pa)"
    )
    sample: Optional[str] = Field(default=None, description="Sample identifier or designation")
    sample_state: Optional[str] = Field(
        default=None, description="Condition or heat treatment state (e.g. AsCast, Q980)"
    )
    etching_agent: Optional[str] = Field(
        default=None, description="Chemical or physical etching agent used"
    )
    imaging_mode: Optional[str] = Field(
        default=None, description="Imaging mode (e.g. Secondary Electron, HAADF-STEM, Backscatter)"
    )
    scale: Optional[str] = Field(
        default=None, description="Scale bar text or calibrated dimension string"
    )
    acquisition_date_if_available: Optional[str] = Field(
        default=None, description="ISO formatted acquisition date if present"
    )


class ScientificMetadataContainer(BaseModel):
    """Container holding both untouched verbatim raw metadata and normalized schema.

    The original raw metadata is never destroyed or modified.
    """

    model_config = ConfigDict(extra="allow")

    raw_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Verbatim, untransformed raw metadata as extracted from source",
    )
    normalized: NormalizedScientificMetadata = Field(
        default_factory=NormalizedScientificMetadata,
        description="Standardized normalized metadata fields",
    )

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert container to serialized dictionary."""
        return {
            "raw_metadata": self.raw_metadata,
            "normalized": self.normalized.model_dump(exclude_none=False),
        }
