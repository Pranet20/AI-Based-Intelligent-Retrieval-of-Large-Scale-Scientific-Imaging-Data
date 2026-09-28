# PHYSICAL EDS HARDWARE MANUAL VALIDATION PROTOCOL

**Project**: AI-Powered Scientific Image Data Management Platform  
**Status**: `REQUIRES_PHYSICAL_DATA_OR_HARDWARE` / `PHYSICAL_EDS_VALIDATION_NOT_EXECUTED`  
**Prerequisites**: Physical Scanning Electron Microscope (SEM) column coupled to a physical Silicon Drift Detector (SDD) Energy Dispersive X-ray Spectrometer.  

---

## 1. Operational Declaration
Software pipelines cannot replace physical hardware coupling. The platform includes synthetic spectral stubs for API schema validation (`is_synthetic = true`). Real physical EDS validation requires interfacing with physical spectrometer instrumentation.

## 2. Physical Acquisition & Ingestion Protocol
1. **Physical Sample Preparation**: Mount a certified multi-phase metallurgical specimen (e.g., chalcopyrite-galena polished mount) in the SEM chamber.
2. **Microscope Alignment**: Establish beam parameters: accelerating voltage $20.0\text{ kV}$, beam current $1.5\text{ nA}$, working distance $8.5\text{ mm}$.
3. **Spectral Acquisition**: Acquire live X-ray count spectra using Oxford Aztec / EDAX detector software across 0–20 keV range.
4. **Data Export**: Export raw spectral data in standard EMSA/MSA or calibrated CSV format.
5. **Platform Ingestion**: Submit micrograph and spectral pair via `/api/v1/eds/ingest`.
6. **Expert Adjudication**: Have a certified materials scientist verify peak deconvolution ($K_\alpha, K_\beta, L_\alpha$ lines).
7. **Prohibition**: Never fabricate spectra or report synthetic test results as physical experimental evidence.
