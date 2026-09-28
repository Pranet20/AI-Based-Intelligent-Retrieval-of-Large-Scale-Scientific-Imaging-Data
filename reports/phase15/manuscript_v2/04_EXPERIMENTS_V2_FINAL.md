# 4. Experimental Setup & Benchmarking Protocols (Final V2 Manuscript Draft)

## 4.1 Benchmark Corpora and Splits

1. **Held-Out Metallurgy Benchmark (HCCI SEM):**
   - **Corpus Size:** 774 physical micrographs captured on a Zeiss GeminiSEM field emission instrument across accelerating voltages from 5 kV to 30 kV and magnifications from $250\times$ to $10{,}000\times$.
   - **Split Protocol:** Stratified split (seed 42) into $N = 212$ query micrographs and $N = 5{,}365$ gallery instances (incorporating background SEM distractor archives to stress retrieval selectivity).
   - **Anti-Leakage Control:** All micrographs from the same specimen mount and metallographic preparation state are strictly confined to either train or test splits.
2. **Industrial Semiconductor Defect Benchmark (Carinthia SEM):**
   - **Corpus Size:** 4,591 industrial SEM micrographs across six defect classes (Class 1 to Class 6).
   - **Evaluation Protocol:** Complete leave-one-out cross-validation across all 4,591 samples, reporting both micro-averaged and macro-averaged Recall@1.
3. **Biological Cross-Modality Benchmark (Bio-Image TEM):**
   - **Corpus Size:** 1,200 transmission electron microscopy cellular micrographs (100 queries, 1,100 gallery).

---

## 4.2 Evaluated Baselines and Experimental Series

- **Visual Baseline Series (RQ1):**
  - Supervised ResNet-50 (ImageNet-1k pretrained, 2048-dim penultimate layer projected to 384-dim).
  - Self-supervised DINOv2 ViT-S/14 baseline (B3, frozen backbone).
  - Supervised contrastive adapted DINOv2 (B4, fine-tuned projection head).
- **Multimodal Series (RQ2):**
  - Metadata-Only linear baseline.
  - Linear late fusion ($\alpha = 0.5$).
  - Non-linear gated MLP fusion.
  - Learned cross-attention fusion.
- **Controlled Perturbation Stress Series:**
  - Evaluated on clean micrographs vs five synthetic variations: JPEG-50 compression, scale-bar overlay, 50% contrast reduction, Gaussian noise ($\sigma = 15$), and severe defocus blur.
- **Human Curation Workflow Series (RQ4):**
  - Condition A: Unprioritized FIFO review over 100 stratified review queue samples.
  - Condition B: AI-prioritized review ordered by Curation Priority Index (CPI).
