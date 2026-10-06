# Phase 6 Localization Provenance Audit

**Audit Date:** 2026-10-06  
**Audit Scope:** Spatial Localization Benchmark Categories ($N = 500$ Test Micrographs)  
**Verification Standard:** IEEE Scientific Integrity & Provenance Standards  
**Status:** LOCALIZATION PROVENANCE VERIFIED  

---

## Executive Summary

Every spatial artifact localization category evaluated in Phase 6 traces directly to the frozen Phase 4 synthetic artifact manifest (`synthetic_manifest.csv`) created and sealed prior to Phase 6. Zero localization categories, labels, or masks were created or altered during Phase 6. All labels represent controlled synthetic perturbations with deterministic ground-truth spatial masks rather than confirmed physical defects.

---

## Category-Wise Provenance Records

### 1. CHARGING_LIKE_SYNTHETIC_ARTIFACT
- **Category:** CHARGING_LIKE_SYNTHETIC_ARTIFACT
- **Source:** HCCI SEM dataset (high-chromium cast iron)
- **Image population:** $N = 100$ localized test micrographs (plus 100 train, 50 val)
- **Label source:** Phase 4 deterministic directional high-contrast streak generator with ground-truth binary mask
- **Synthetic/Natural:** Controlled synthetic artifact
- **Manifest:** `research/results/phase4/synthetic_manifest.csv`
- **Manifest SHA:** `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947`
- **Created before Phase 6?:** YES (Created in Phase 4)
- **Frozen before Phase 6?:** YES (Sealed in Phase 4 evidence freeze)
- **Status:** LOCALIZATION PROVENANCE VERIFIED

---

### 2. OVEREXPOSURE
- **Category:** OVEREXPOSURE
- **Source:** HCCI SEM dataset (high-chromium cast iron)
- **Image population:** $N = 100$ localized test micrographs (plus 100 train, 50 val)
- **Label source:** Phase 4 deterministic saturation clipping generator with ground-truth binary mask
- **Synthetic/Natural:** Controlled synthetic artifact
- **Manifest:** `research/results/phase4/synthetic_manifest.csv`
- **Manifest SHA:** `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947`
- **Created before Phase 6?:** YES (Created in Phase 4)
- **Frozen before Phase 6?:** YES (Sealed in Phase 4 evidence freeze)
- **Status:** LOCALIZATION PROVENANCE VERIFIED

---

### 3. UNDEREXPOSURE
- **Category:** UNDEREXPOSURE
- **Source:** HCCI SEM dataset (high-chromium cast iron)
- **Image population:** $N = 100$ localized test micrographs (plus 100 train, 50 val)
- **Label source:** Phase 4 deterministic low-intensity attenuation generator with ground-truth binary mask
- **Synthetic/Natural:** Controlled synthetic artifact
- **Manifest:** `research/results/phase4/synthetic_manifest.csv`
- **Manifest SHA:** `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947`
- **Created before Phase 6?:** YES (Created in Phase 4)
- **Frozen before Phase 6?:** YES (Sealed in Phase 4 evidence freeze)
- **Status:** LOCALIZATION PROVENANCE VERIFIED

---

### 4. LOCAL_ILLUMINATION_ABNORMALITY
- **Category:** LOCAL_ILLUMINATION_ABNORMALITY
- **Source:** HCCI SEM dataset (high-chromium cast iron)
- **Image population:** $N = 100$ localized test micrographs (plus 100 train, 50 val)
- **Label source:** Phase 4 deterministic spatial Gaussian gradient generator with ground-truth binary mask
- **Synthetic/Natural:** Controlled synthetic artifact
- **Manifest:** `research/results/phase4/synthetic_manifest.csv`
- **Manifest SHA:** `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947`
- **Created before Phase 6?:** YES (Created in Phase 4)
- **Frozen before Phase 6?:** YES (Sealed in Phase 4 evidence freeze)
- **Status:** LOCALIZATION PROVENANCE VERIFIED

---

### 5. CLIPPING
- **Category:** CLIPPING
- **Source:** HCCI SEM dataset (high-chromium cast iron)
- **Image population:** $N = 100$ localized test micrographs (plus 100 train, 50 val)
- **Label source:** Phase 4 deterministic dynamic range truncation generator with ground-truth binary mask
- **Synthetic/Natural:** Controlled synthetic artifact
- **Manifest:** `research/results/phase4/synthetic_manifest.csv`
- **Manifest SHA:** `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947`
- **Created before Phase 6?:** YES (Created in Phase 4)
- **Frozen before Phase 6?:** YES (Sealed in Phase 4 evidence freeze)
- **Status:** LOCALIZATION PROVENANCE VERIFIED

---

## Final Provenance Determination

All 5 localization categories and their associated ground-truth spatial masks originate from the frozen Phase 4 synthetic benchmark. Zero labels or images were generated during Phase 6.

**Final Determination:** **LOCALIZATION PROVENANCE VERIFIED**
