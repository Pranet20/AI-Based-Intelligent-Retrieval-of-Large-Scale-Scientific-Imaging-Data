# Dataset Card: Scientific Microscopy Benchmark Suite

## Summary of Datasets
This platform evaluates representation, retrieval, and curation across six scientific microscopy archives:

1. **HCCI (High-Chromium Cast Iron SEM):**
   - **Scale:** 774 valid physical images (305 AsCast, 236 Annealed, 233 Hardened).
   - **Source:** Zenodo DOI `10.5281/zenodo.21931379`.
   - **Rights:** `RIGHTS_UNVERIFIED` (Restricted to academic local research).
   - **Features:** Controlled acquisition variations (5kV–30kV, 250x–10,000x, SE/BSE/InLens detectors).

2. **Carinthia Industrial SEM Defect Dataset:**
   - **Scale:** 4,591 industrial SEM defect micrographs across 6 classes (Class 3 planar substrate: 87.3%).
   - **Source:** Zenodo DOI `10.5281/zenodo.10715190`.
   - **Rights:** `RIGHTS_UNVERIFIED` (Restricted to academic local research).

3. **SEM Images for Nanoscience:**
   - **Scale:** 21,272 SEM micrographs across 10 categories.
   - **Source:** Nature Scientific Data DOI `10.1038/sdata.2018.172`.
   - **Rights:** `CC BY 4.0` (Open Redistribution with Attribution).

4. **Secondary Registered Adapters:** `atomagined` (16,000 synthetic STEM), `cigRockSEM` (1,500 rock SEM), `MicroAl` (800 aluminium micrographs). Rights: `RIGHTS_UNVERIFIED`.

## Anti-Leakage Split Protocol
All benchmark evaluations enforce strict mount-level and specimen-level isolation. No physical specimen mount spans multiple train/test partitions.
