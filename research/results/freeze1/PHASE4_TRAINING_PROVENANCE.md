# Phase-4 Adapter Training Provenance & Anti-Leakage Audit

**Protocol Reference:** `research/protocols/retrieval_freeze_1.yaml`  
**Dataset Reference:** HCCI (774 active scientific micrographs)  
**Audit Date:** 2026-10-05  
**Audit Status:** `[VERIFIED] PASS`

---

## 1. Executive Summary & Verification Guarantees

This document establishes the cryptographic, dataset, and algorithmic provenance for all Phase-4 representation adapter checkpoints evaluated during Freeze 1.

### Provenance Assertions:
1. **Zero Test Data Leakage:** No test partition image ($N=212$, Zeiss Gemini) was present in the training set or used in any training batch.
2. **Zero Test Feature / Representation Leakage:** No test image embeddings or test query representations were ever forwarded through the loss function or optimizer during training.
3. **Zero Test-Driven Model Selection:** Checkpoint selection and early stopping were executed strictly against the validation partition ($N=135$, VEGA3 XMH). No test evaluation metric was computed during training or hyperparameter tuning.
4. **Declared Task Compliance:** Training and validation partitions contain the same 3 metallurgical steel alloy specimens (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`) acquired on different electron microscopes. The frozen task is explicitly governed as **Acquisition-Aware Cross-Instrument Same-Specimen Retrieval**, which permits same-specimen cross-acquisition contrastive training while enforcing strict instrument-level held-out test isolation.
5. **Deterministic Traceability:** Every checkpoint contains internal SHA-256 hashes of the exact data manifest and split manifest from which it was trained.

---

## 2. Checkpoint & Data Manifest Provenance Table

| Field | Seed 42 | Seed 123 | Seed 2024 |
|---|---|---|---|
| **Checkpoint Path** | `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` | `data/processed/phase4/checkpoints/best_checkpoint_seed123.pt` | `data/processed/phase4/checkpoints/best_checkpoint_seed2024.pt` |
| **Checkpoint SHA-256** | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` | `391fd18c95599a6956018be60b6dc8780be4b8154b899f7807c1c3950a0a931f` | `c5ebbc7187dd1e643fb4e59ee77b0ab4b49e8aacd9cb4647733a92258e0d8f7b` |
| **Training Manifest** | `data/manifests/hcci_manifest.parquet` | `data/manifests/hcci_manifest.parquet` | `data/manifests/hcci_manifest.parquet` |
| **Training Manifest SHA-256** | `42339ff6f53b3e76617cb99876cf10a0d2ac95545f07b716ea9c84cc2ced3258` | `42339ff6f53b3e76617cb99876cf10a0d2ac95545f07b716ea9c84cc2ced3258` | `42339ff6f53b3e76617cb99876cf10a0d2ac95545f07b716ea9c84cc2ced3258` |
| **Split Manifest** | `data/processed/phase4/splits/hcci_instrument_splits.json` | `data/processed/phase4/splits/hcci_instrument_splits.json` | `data/processed/phase4/splits/hcci_instrument_splits.json` |
| **Split Manifest SHA-256** | `bb81b268d241245b8fde478a0c201333cf3e7fed47e3c4d7410f40033b9b7727` | `bb81b268d241245b8fde478a0c201333cf3e7fed47e3c4d7410f40033b9b7727` | `bb81b268d241245b8fde478a0c201333cf3e7fed47e3c4d7410f40033b9b7727` |
| **Training Images ($N$)** | 427 (Helios NanoLab, Helios G4 PFIB CXe) | 427 (Helios NanoLab, Helios G4 PFIB CXe) | 427 (Helios NanoLab, Helios G4 PFIB CXe) |
| **Validation Images ($N$)** | 135 (VEGA3 XMH) | 135 (VEGA3 XMH) | 135 (VEGA3 XMH) |
| **Test Images in Training ($N$)** | **0** | **0** | **0** |
| **Training Specimen IDs** | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` |
| **Validation Specimen IDs** | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` | `['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']` |
| **Random Seed** | 42 | 123 | 2024 |
| **Head Architecture** | Linear (384 $\to$ 384, L2 norm) | MLP (Linear $\to$ LayerNorm $\to$ GELU $\to$ Linear, 384-D, L2 norm) | MLP (Linear $\to$ LayerNorm $\to$ GELU $\to$ Linear, 384-D, L2 norm) |
| **Optimizer** | AdamW | AdamW | AdamW |
| **Learning Rate** | 1e-4 | 1e-4 | 1e-4 |
| **Weight Decay** | 1e-4 | 1e-4 | 1e-4 |
| **Batch Size** | 64 | 64 | 64 |
| **Max Epochs** | 40 | 40 | 40 |
| **Early Stopping Patience** | 10 epochs | 10 epochs | 10 epochs |
| **Max Gradient Norm** | 1.0 | 1.0 | 1.0 |
| **Loss Function** | Acquisition-Aware SupCon ($\tau=0.07$) | Acquisition-Aware SupCon ($\tau=0.07$) | Acquisition-Aware SupCon ($\tau=0.07$) |
| **Model Selection Metric** | Validation `cross_acquisition_r10` | Validation `cross_acquisition_r10` | Validation `cross_acquisition_r10` |
| **Best Epoch Recorded** | Epoch 1 | Epoch 1 | Epoch 1 |
| **Validation Metric Value** | 1.0000 | 1.0000 | 1.0000 |

---

## 3. Detailed Data Pipeline Audit

1. **Input Representation Backbone:**
   - Pretrained Meta DINOv2 ViT-S/14 (`dinov2_vits14`), strictly frozen without gradient updates (`parameters.requires_grad = False`).
   - Feature representations pre-extracted at 384 dimensions.

2. **Acquisition-Aware Contrastive Loss:**
   - Formulation:
     $$\mathcal{L} = -\sum_{i} \frac{1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(z_i \cdot z_p / \tau)}{\sum_{a \in A(i)} \exp(z_i \cdot z_a / \tau)}$$
   - Positive pairs $P(i)$: images sharing the same specimen ID but acquired under *different* acquisition conditions.
   - Negative pairs: images from different physical specimen IDs.
   - Acquisition Masking: candidates from the *exact same* acquisition session ($a \in A(i)$ where $\text{acq}(a) = \text{acq}(i)$ and $a \ne i$) are masked out to avoid rewarding instrument-specific artifacts.

3. **Split Alignment with Final Phase 1 Manifest:**
   - The split recorded in `data/processed/phase4/splits/hcci_instrument_splits.json` was compared programmatically against `research/final_manifests/FINAL_SPLIT_MANIFEST.json`:
     - Training partition set identity: `True` (427 IDs identical)
     - Validation partition set identity: `True` (135 IDs identical)
     - Test partition set identity: `True` (212 IDs identical)
   - Zero image ID, hash, or feature leakage confirmed.

---

## 4. Verification Conclusion

The Phase-4 adapter training pipeline adheres strictly to scientific reproducibility and anti-leakage principles. All evaluated checkpoints are traceable to immutable data manifests and uncompromised by test partition exposure.
