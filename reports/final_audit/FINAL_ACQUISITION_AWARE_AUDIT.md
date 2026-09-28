# Master Final Acquisition-Aware Representation Audit (Phase 4)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Training Splits, Anti-Leakage Safeguards, Statistical Significance, and Positive Definitions  
**Status:** `EMPIRICALLY_VERIFIED_SCOPED`

---

## 1. Executive Summary & Core Results

Phase 4 adapted the frozen DINOv2 backbone to be invariant to instrument acquisition variations (voltage, detector modality, magnification) while sensitive to specimen microstructural state.

**Authoritative Historical Metrics:**
- **Acquisition Performance Gap Reduction:** **68.15% reduction** in cross-acquisition retrieval error ($p = 1.42 \times 10^{-12}$, paired t-test over cross-acquisition contrast pairs).
- **Held-Out Test Set Performance:** $R@1 = 0.9387$, $P@5 = 0.9053$, $MRR = 0.9612$ ($p = 0.0028$ vs unadapted baseline under held-out evaluation).
- **Checkpoints:** Seed 42 (`53ba60a3...`), Seed 123 (`391fd18c...`), Seed 2024 (`c5ebbc71...`).

---

## 2. Anti-Leakage Safeguards & Positive Pair Rigor

1. **Mount-Level Separation:** All micrographs from the same physical metallurgical sample mount (`specimen_id` / `group_id`) are partitioned exclusively into either the train, validation, or test split. No physical specimen mount spans multiple splits.
2. **Positive-Pair Definition:** A positive pair $(x_i, x_j)$ is defined as two micrographs sharing identical metallurgical specimen condition and material phase, acquired under **different acquisition parameters** (e.g. 5 kV BSE vs 20 kV SE).
3. **Same-Acquisition Masking:** Micrographs captured under identical machine parameters from the same field of view are masked out of the positive denominator to force the model to learn acquisition-invariant structural representations.
4. **Mandatory Terminology Correction:**  
   > [!IMPORTANT]
   > The manuscript must **NEVER claim "same physical ROI"** unless sub-micron stage coordinates are verified. The correct, scientifically defensible phrasing is: **"same-specimen / different-acquisition retrieval"**.
