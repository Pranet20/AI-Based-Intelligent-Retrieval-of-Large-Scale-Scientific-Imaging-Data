# IEEE Paper Section V: Dataset & Experimental Setup
**Target Section**: Section V. Dataset & Experimental Setup  

---

## V. DATASET & EXPERIMENTAL SETUP

### A. Scientific Micrograph Corpus Characteristics
The empirical evaluation was conducted on a curated scientific imaging collection comprising $N = 769$ high-resolution electron micrographs encompassing structural alloys, high-entropy materials, ceramic composites, and crystalline geological specimens:
- **Imaging Modalities**: Scanning Electron Microscopy (Secondary Electron and Backscattered Electron imaging) and Transmission Electron Microscopy (bright-field).
- **Instrumental Parameter Diversity**:
  - Accelerating Voltage: $5.0 \text{ kV}$ to $30.0 \text{ kV}$ (mean $18.4 \text{ kV}$)
  - Magnification: $500\times$ to $150,000\times$ (spanning macroscopic grain structures to nano-scale precipitates)
  - Working Distance: $3.5 \text{ mm}$ to $14.2 \text{ mm}$
  - Tilt Angles: $0^\circ$ to $45^\circ$
- **Resolution**: Native image dimensions range from $1024 \times 768$ to $2048 \times 1536$ pixels with 8-bit or 16-bit grayscale depth.

### B. Controlled Evaluation Protocols & Benchmark Splits
To evaluate distinct operational capabilities without data leakage, the repository is partitioned into rigorously isolated benchmark splits:

| Benchmark Split | Sample Size | Primary Evaluation Purpose | Controlled Conditions / Perturbations |
|:---|:---:|:---|:---|
| **Visual Retrieval Split** | $N = 240$ Queries<br>$N = 400$ Gallery | Evaluation of nearest-neighbor visual retrieval accuracy and latency | Held-out query micrographs matched against structurally relevant gallery specimens |
| **Acquisition Robustness Split** | $N = 180$ Pairs | Measurement of cross-acquisition similarity gap and projection mitigation | Multi-angle micrograph pairs of identical specimen regions under varied tilt ($10^\circ - 30^\circ$) |
| **Quality Degradation Benchmark** | $N = 120$ Test Images | Evaluation of image-derived quality-risk screening (AUROC / AUPRC) | Controlled synthetic degradations: Gaussian blur ($\sigma \in [1, 5]$), additive Gaussian noise ($\text{SNR} \in [10, 25]\text{ dB}$), and contrast clipping |
| **Duplicate Perturbation Benchmark**| $N = 120$ Test Images | Evaluation of duplicate candidate identification ($F_1$-score) | Synthetic perturbations: JPEG compression ($Q \in [30, 80]$), resizing, minor brightness shifts ($\pm 10\%$) |
| **Natural Redundancy Graph Audit** | $N = 769$ Images | Exhaustive repository inventory redundancy analysis | Real-world unperturbed natural repository collection |
| **Novelty Detection Split** | $N = 120$ Test Images | Latent-space out-of-distribution and novelty detection | In-distribution metallurgical micrographs vs held-out biological TEM micrographs |

### C. Baseline Architectures & Comparative Systems
The proposed DINOv2-ViT-S/14 backbone was systematically evaluated against:
1. **ResNet-50 (Supervised)**: Standard ImageNet-1k pretrained convolutional network ($d = 2048$).
2. **ResNet-50 (SimCLR)**: Domain-adapted self-supervised contrastive learning model trained with microscopy crop/rotation augmentations ($d = 2048$).
3. **BioMedCLIP**: Domain-specific biomedical vision-language foundation model (ViT-B/16, $d = 512$).
4. **Vanilla CLIP**: OpenAI ViT-B/32 multimodal vision-language model ($d = 512$).
5. **Perceptual Hashing (pHash)**: 64-bit discrete cosine transform perceptual hash baseline.

### D. Benchmark Execution Environment
All benchmark experiments were conducted on a single standard workstation:
- **Processor**: 12th Gen Intel Core i7-12700H (14 cores, 20 threads) / 16 GB DDR5 RAM.
- **Software Stack**: Ubuntu Linux / Windows 11 Subsystem, Python 3.11.9, PyTorch 2.2.1, FAISS-CPU 1.7.4.
- **Execution Invariant**: Feature extraction and vector retrieval evaluated strictly in single-threaded and multi-threaded CPU environments to simulate standard laboratory workstation hardware without specialized GPU clusters.
