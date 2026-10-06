# Dataset Card: High-Chromium Cast Iron (HCCI) SEM Dataset

## Summary
* **Dataset Identifier**: `hcci`
* **Role**: `PRIMARY_RETRIEVAL`
* **Status**: `ACCEPTED_VERIFIED`
* **Total Authentic Micrographs**: 774
* **Image Format**: 8-bit PNG, single-channel / RGB-encoded grayscale
* **Native Dimensions**: 2860 × 1922 pixels
* **Authoritative Source**: Zenodo (DOI: 10.5281/zenodo.21931379)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Redistribution**: Permitted with attribution

## Acquisition & Instrument Metadata
* **Instruments Represented**: FEI Helios G4 PFIB CXe, Zeiss Sigma 300, Tescan MIRA3
* **Detectors**: Secondary Electron (SE), Backscattered Electron (BSE)
* **Accelerating Voltages**: 5.0 kV, 10.0 kV, 15.0 kV, 20.0 kV
* **Magnifications**: 500×, 1000×, 2000×, 5000×
* **Specimens**: AsCast, HeatTreated, CryoTreated alloy specimens
* **Overall Metadata Completeness**: 100.0%

## Evaluation Splits
* **Train Split**: 427 images
* **Validation Split**: 135 images
* **Held-out Test Split**: 212 images (Zeiss Sigma 300 cross-instrument isolation)
* **Leakage Status**: VERIFIED ZERO LEAKAGE (SHA overlap: 0, ID overlap: 0)
