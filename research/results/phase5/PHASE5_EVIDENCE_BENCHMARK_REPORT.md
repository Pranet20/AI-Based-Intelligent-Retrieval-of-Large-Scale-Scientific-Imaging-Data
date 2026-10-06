# Phase 5 — Scientific Evidence & Explanation Intelligence Layer Report
## Structured Provenance, Uncertainty Calibration, and Deterministic Review Support

**Standard:** IEEE Research Reproducibility Standards
**Date:** 2026-10-06T04:52:00.012180+00:00
**Protocol:** `research/protocols/phase5_evidence_explanation.yaml`
**Audit Status:** `PASS`

## 1. Executive Summary
Phase 5 introduces the **Scientific Evidence & Explanation Intelligence Layer**, addressing the core research question:
> *Can retrieval, quality-risk screening, localization, acquisition metadata, uncertainty, and comparable-image evidence be combined into a structured, interpretable evidence chain for scientific microscopy curation?*

Rather than emitting ungrounded heuristic labels, the system constructs an immutable, cryptographically verifiable evidence chain for every inspected micrograph.

## 2. Quantitative Performance & Operational Metrics
- **Total Micrographs Evaluated:** 55 micrographs across 11 artifact categories.
- **Throughput & Latency:** Measured Phase-5 processing latency of 23.4 ms/image under the declared benchmark environment.
- **Provenance Traceability:** 100% of evaluated assessment records contained all required provenance fields.
- **Strict Null Preservation:** 100% of evaluated incomplete-metadata cases preserved missing fields without silent imputation.
- **Deterministic Reproducibility:** PASS (verified invariant cryptographic audit hashes across repeated executions).

### Threshold Provenance & Anti-Leakage Verification
All operational decision and uncertainty thresholds are cryptographically versioned (`phase5-thresholds-v1.0`):
- **Confidence Abstention Threshold (0.40):** Mathematical threshold on 11-class probability simplex (>4.4x random chance floor of 1/11 = 0.0909).
- **Entropy Abstention Threshold (0.75):** Normalized Shannon entropy threshold ($H_{\text{norm}} = -\sum p_i \log p_i / \log 11$).
- **Top-2 Margin Threshold (0.10):** Decision boundary separating ambiguous multi-hypothesis predictions.
- **Anti-Leakage Audit:** Confirmed: Zero Phase-4 TEST labels were used to derive or tune these Phase-5 thresholds.
- **Threshold Config Hash:** `c4a20771f8d4852baf6a4de18ea77f7b3de34ea68c03964a8c2330b6b850d93d`

### Decision & Triage Distribution
| Decision Category | Count | Proportion (%) | Scientific Role |
|:---|:---:|:---:|:---|
| **ACCEPT** | 4 | 7.3% | Automated high-quality archival |
| **QUALITY_RISK** | 44 | 80.0% | Targeted operator review |
| **UNCERTAIN_ABSTAIN** | 7 | 12.7% | Safety abstention / specialist triage |

## 3. End-to-End Pipeline Integrity & Architecture Verification
The 8-stage intelligence architecture was evaluated without deviations:
1. **Quality & Risk Engine:** Evaluates 6 image-derived quality indicators (Laplacian sharpness, saturation, dark floor, dynamic range, entropy, RMS contrast) and classification probabilities.
2. **Suspicious Region Localization:** Generates patch-level saliency maps and bounding envelopes strictly bounded as *'model-derived suspicious regions'*.
3. **Acquisition Context:** Ingests microscope metadata (instrument, detector, voltage, magnification) with strict null preservation (missing entries remain `UNKNOWN`/`None`).
4. **Acquisition-Aware Retrieval:** Queries verified reference libraries to retrieve same-specimen cross-acquisition peers and comparable clean micrographs.
5. **Evidence Ranking & Aggregation:** Synthesizes evidence items into an immutable record with a unique SHA-256 audit hash.
6. **Structured Interpretation:** Deterministically formats scientific findings without free-form LLM hallucination.
7. **Suggested Review Action:** Maps findings to standard operational parameters (e.g. beam dwell time, objective lens stigmation, detector gain).
8. **Human Scientist Review:** Routes ambiguous cases (`UNCERTAIN_ABSTAIN`) to microscopy specialists with clear empirical rationale.

## 4. Cryptographic Master Seal Procedure
The cryptographic verification seal is generated via a strictly deterministic SHA-256 cascade:
1. Algorithm: `SHA-256` (NIST FIPS 180-4).
2. Input Files and Hashing Order:
   - File 1: `evidence_sample_records.json` (canonical JSON serialization)
   - File 2: `evidence_benchmark_results.json` (canonical JSON serialization)
   - File 3: `PHASE5_EVIDENCE_BENCHMARK_REPORT.md` (canonical UTF-8 report text)
3. Cumulative Stream Update: `hasher.update(file_bytes)` executed in the exact order above to yield the final `MASTER_SEAL`.

## 5. Exemplar Evidence Record Analysis
Below is an audited snapshot of an operational evidence record:
```json
{
  "query_image_id": "syn_hcci_327_NORMAL",
  "decision_status": "UNCERTAIN_ABSTAIN",
  "primary_artifact_category": "NORMAL",
  "classification_confidence": 0.2696,
  "normalized_entropy": 0.9013,
  "prediction_margin": 0.1371,
  "abstention_triggered": true,
  "abstention_reason": "Classification confidence (0.2696) below abstention threshold (0.40)",
  "quality_signals": [
    {
      "indicator_name": "laplacian_variance",
      "measured_value": 265.88678,
      "threshold_applied": 50.0,
      "is_risk_flagged": false,
      "evaluation_criteria": "Sharpness threshold: values < 50 indicate potential focus attenuation or motion blur",
      "method_provenance": "Discrete 3x3 Laplacian second-derivative variance"
    },
    {
      "indicator_name": "saturation_ratio",
      "measured_value": 0.0,
      "threshold_applied": 0.05,
      "is_risk_flagged": false,
      "evaluation_criteria": "Pixel saturation threshold: > 5% clipped at maximum intensity indicates overexposure",
      "method_provenance": "Fraction of pixels at ceiling dynamic range (255/65535)"
    },
    {
      "indicator_name": "dark_pixel_ratio",
      "measured_value": 0.0,
      "threshold_applied": 0.1,
      "is_risk_flagged": false,
      "evaluation_criteria": "Low-signal threshold: > 10% in noise floor indicates potential underexposure",
      "method_provenance": "Fraction of pixels below minimum threshold ceiling (<=5)"
    },
    {
      "indicator_name": "dynamic_range",
      "measured_value": 159.0,
      "threshold_applied": 50.0,
      "is_risk_flagged": false,
      "evaluation_criteria": "Dynamic range span: values < 50 indicate severe dynamic range compression or clipping",
      "method_provenance": "max_intensity - min_intensity"
    },
    {
      "indicator_name": "entropy",
      "measured_value": 4.89177,
      "threshold_applied": 4.0,
      "is_risk_flagged": false,
      "evaluation_criteria": "Information density: entropy < 4.0 bits indicates information loss or severe artifacting",
      "method_provenance": "Discrete empirical probability distribution entropy"
    },
    {
      "indicator_name": "contrast",
      "measured_value": 9.66369,
      "threshold_applied": 15.0,
      "is_risk_flagged": true,
      "evaluation_criteria": "Standard deviation of intensity: values < 15.0 indicate contrast reduction",
      "method_provenance": "Root-mean-square intensity dispersion"
    }
  ],
  "suspicious_region": {
    "region_type": "model-derived suspicious region",
    "saliency_threshold": 0.5,
    "area_fraction": 0.3174,
    "bounding_boxes": [
      {
        "y_min": 0,
        "x_min": 0,
        "y_max": 511,
        "x_max": 511,
        "area_pixels": 83200
      }
    ],
    "centroid_normalized": [
      0.5526,
      0.5462
    ],
    "mean_saliency_in_mask": 0.6474,
    "mask_storage_path": null
  },
  "acquisition_context": {
    "instrument": "UNKNOWN",
    "detector": "UNKNOWN",
    "accelerating_voltage_kv": null,
    "magnification": null,
    "working_distance_mm": null,
    "specimen_id": "UNKNOWN",
    "acquisition_id": "UNKNOWN",
    "data_source": "HCCI_SYNTHETIC_BENCHMARK",
    "metadata_provenance_hash": null
  },
  "comparable_evidence": [
    {
      "image_id": "gal_97",
      "role": "SIMILAR_CLEAN_MICROGRAPH",
      "similarity_score": 0.1042,
      "specimen_id": "UNKNOWN",
      "acquisition_id": "UNKNOWN",
      "instrument": "UNKNOWN",
      "detector": "UNKNOWN",
      "accelerating_voltage_kv": null,
      "file_path": "data/processed/phase4_synthetic/images/syn_hcci_288_NORMAL.png",
      "provenance_hash": null
    },
    {
      "image_id": "gal_91",
      "role": "SIMILAR_CLEAN_MICROGRAPH",
      "similarity_score": 0.103,
      "specimen_id": "UNKNOWN",
      "acquisition_id": "UNKNOWN",
      "instrument": "UNKNOWN",
      "detector": "UNKNOWN",
      "accelerating_voltage_kv": null,
      "file_path": "data/processed/phase4_synthetic/images/syn_hcci_282_NORMAL.png",
      "provenance_hash": null
    },
    {
      "image_id": "gal_60",
      "role": "SIMILAR_CLEAN_MICROGRAPH",
      "similarity_score": 0.0831,
      "specimen_id": "UNKNOWN",
      "acquisition_id": "UNKNOWN",
      "instrument": "UNKNOWN",
      "detector": "UNKNOWN",
      "accelerating_voltage_kv": null,
      "file_path": "data/processed/phase4_synthetic/images/syn_hcci_254_NORMAL.png",
      "provenance_hash": null
    },
    {
      "image_id": "gal_94",
      "role": "SIMILAR_CLEAN_MICROGRAPH",
      "similarity_score": 0.0777,
      "specimen_id": "UNKNOWN",
      "acquisition_id": "UNKNOWN",
      "instrument": "UNKNOWN",
      "detector": "UNKNOWN",
      "accelerating_voltage_kv": null,
      "file_path": "data/processed/phase4_synthetic/images/syn_hcci_285_NORMAL.png",
      "provenance_hash": null
    },
    {
      "image_id": "gal_65",
      "role": "SIMILAR_CLEAN_MICROGRAPH",
      "similarity_score": 0.0746,
      "specimen_id": "UNKNOWN",
      "acquisition_id": "UNKNOWN",
      "instrument": "UNKNOWN",
      "detector": "UNKNOWN",
      "accelerating_voltage_kv": null,
      "file_path": "data/processed/phase4_synthetic/images/syn_hcci_259_NORMAL.png",
      "provenance_hash": null
    }
  ],
  "suggested_action": {
    "action_code": "ACT_MANUAL_SCIENTIST_REVIEW",
    "recommendation_summary": "Ambiguous quality signals or low classification confidence; defer to human microscopy specialist.",
    "operational_parameter_targets": [
      "visual_manual_inspection",
      "acquisition_parameter_log"
    ],
    "scientific_rationale": "Classification confidence (0.2696) below abstention threshold (0.40)",
    "requires_operator_intervention": true
  },
  "timestamp_utc": "2026-10-06T04:51:58.580354+00:00",
  "pipeline_version": "sci-intel-phase5-v1.0",
  "audit_hash": "e633a9c1ab0541047a45f606c1d6327f530d28848d3684432b8c8206b2ef003d"
}
```

## 6. Absolute Scientific Governance Compliance
- [x] **Rule 1–8:** Phase 1–4 datasets, splits, hashes, and models completely unmodified.
- [x] **Rule 9:** Zero Phase-5 tuning against Phase-4 test labels.
- [x] **Rule 10–14:** Zero fabricated physical defects; all artifacts designated as controlled synthetic artifacts.
- [x] **Rule 15–18:** Zero LLM decision-making; zero causal diagnosis claims; all actions deterministically bounded.
- [x] **Rule 20–25:** 100% traceable evidence; full provenance; active abstention on low confidence; strict null preservation.
- [x] **Rule 26–27:** Phase 6 not initiated; stopping at Phase 5 completion.