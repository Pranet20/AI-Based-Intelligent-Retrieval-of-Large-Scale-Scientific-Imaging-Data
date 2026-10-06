# Dataset Card: Broad Bioimage Benchmark Collection 021 (BBBC021)

## Summary
* **Dataset Identifier**: `bbbc021`
* **Role**: `INGESTION_BENCHMARK` & `QUALITY_BENCHMARK`
* **Status**: `ACCEPTED_VERIFIED`
* **Total Authentic Micrographs**: 720
* **Image Format**: 16-bit uncompressed TIFF (uint16, [0, 65535])
* **Native Dimensions**: 1280 × 1024 pixels
* **Authoritative Source**: Broad Institute Imaging Platform (https://bbbc.broadinstitute.org/BBBC021)
* **Citation**: Ljosa et al., Nature Methods 2012
* **License**: CC0 1.0 Universal (Public Domain Dedication)
* **Redistribution**: Unrestricted public domain

## Multi-Channel Fluorescence Channels
* **w1 (240 images)**: DAPI (Nuclear counterstain, ~460 nm emission)
* **w2 (240 images)**: Tubulin (Cytoskeleton microtubules, ~520 nm emission)
* **w4 (240 images)**: F-Actin (Phalloidin microfilaments, ~590 nm emission)
* **Instrument**: Molecular Devices ImageXpress Micro (sCMOS / CCD)
* **Overall Metadata Completeness**: 87.5%

## Evaluation Protocol
* **Primary Role**: Evaluation of 16-bit high-dynamic-range scientific image ingestion, optical focus variance, and multi-channel cellular quality screening.
