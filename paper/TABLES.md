# IEEE Manuscript Tables
**Target Manuscript**: Complete Table Evidence Suite (Tables I – VIII)  

---

### TABLE I
**Scientific Imaging Corpus Characteristics**

| Dataset Partition / Characteristic | Primary Modality | Specimen Classes | Sample Count ($N$) | Parameter Ranges (Voltage / Mag) |
|:---|:---|:---|:---:|:---|
| In-Domain Materials Benchmark | SEM (SE / BSE) | High-entropy alloys, dual-phase steels, ceramics | 769 | $5.0 - 30.0\text{ kV}$ / $500\times - 150,000\times$ |
| Visual Retrieval Evaluation Split | SEM (SE / BSE) | Structural crystalline materials | 240 queries / 400 gallery | $10.0 - 25.0\text{ kV}$ / $2,000\times - 50,000\times$ |
| Acquisition Robustness Benchmark | SEM (Multi-tilt) | Multi-angle metallurgical samples | 180 pairs | $15.0 - 20.0\text{ kV}$ / Tilt: $0^\circ - 45^\circ$ |
| Quality Degradation Benchmark | SEM / TEM | Synthetic blur, noise, contrast perturbations | 120 | $15.0\text{ kV}$ / $10,000\times$ |
| Synthetic Duplicate Benchmark | SEM | Compression, scaling, brightness shifts | 120 | $15.0\text{ kV}$ / $10,000\times$ |
| Out-of-Domain Novelty Benchmark | Biological TEM | Cellular ultrastructure, soft-matter thin films | 120 | $80.0 - 120.0\text{ kV}$ / $5,000\times - 40,000\times$ |

---

### TABLE II
**DINOv2 Visual Retrieval Performance vs Baselines**

| Representation Model | Backbone Architecture | Embedding Dimension | $\text{Recall@1}$ | $\text{Recall@5}$ | $\text{Recall@10}$ | $\text{MRR}$ | Single-Query Latency |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Random Baseline | — | — | 0.0042 | 0.0208 | 0.0417 | 0.0134 | — |
| Perceptual Hash (pHash) | DCT 64-bit | 64 | 0.4120 | 0.5840 | 0.6710 | 0.4930 | **1.2 ms** |
| ResNet-50 (Supervised) | ResNet-50 | 2048 | 0.8125 | 0.8950 | 0.9310 | 0.8492 | 14.2 ms |
| SimCLR (Contrastive) | ResNet-50 | 2048 | 0.7815 | 0.8710 | 0.9125 | 0.8320 | 14.1 ms |
| BioMedCLIP | ViT-B/16 | 512 | 0.8620 | 0.9240 | 0.9510 | 0.8875 | 32.6 ms |
| Vanilla CLIP | ViT-B/32 | 512 | 0.7240 | 0.8315 | 0.8840 | 0.7680 | 22.1 ms |
| **DINOv2 (Proposed)** | **ViT-S/14** | **384** | **0.9481** | **0.9852** | **0.9917** | **0.9658** | **18.4 ms** |

---

### TABLE III
**Vector Search Indexing Benchmarks (CPU Execution)**

| Index Algorithm | Index Implementation | Exact Recall@10 | Latency ($N=1,000$) | Latency ($N=10,000$) | RAM Usage ($N=10,000$) | Build Time ($N=10,000$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| Exact Inner Product | FAISS `IndexFlatIP` | **1.0000** | **0.12 ms** | **0.24 ms** | **15.4 MB** | **< 10 ms** |
| Exact Euclidean | FAISS `IndexFlatL2` | **1.0000** | 0.14 ms | 0.28 ms | 15.4 MB | < 10 ms |
| Inverted File ($nlist=64$) | FAISS `IndexIVFFlat` | 0.9912 | 0.08 ms | 0.11 ms | 16.2 MB | 420 ms |
| Hierarchical NSW | FAISS `IndexHNSWFlat` | 0.9985 | 0.06 ms | 0.09 ms | 28.6 MB | 1,840 ms |

---

### TABLE IV
**Acquisition-Geometry Robustness & Alignment Evaluation**

| Adaptation Configuration | Evaluation Split | Cross-Angle Cosine Similarity | Similarity Gap ($\Delta_{\text{geom}}$) | Cross-Angle $\text{Recall@1}$ | Zero-Tilt $\text{Recall@1}$ |
|:---|:---|:---:|:---:|:---:|:---:|
| Unadapted Baseline | Multi-Angle ($N=180$) | 0.765 | 0.235 | 0.7140 | 0.9481 |
| Linear Projection Layer | Multi-Angle ($N=180$) | 0.822 | 0.178 | 0.7890 | 0.9481 |
| **Affine Alignment Layer** | **Multi-Angle ($N=180$)** | **0.864** | **0.136 (-42.3%)** | **0.8415** | **0.9481** |

---

### TABLE V
**Metadata & Multimodal Retrieval Comparison**

| Modality / Architecture | Visual Input | Metadata Features | Optimal Alpha ($\alpha^*$) | $\text{Recall@1}$ | $\text{MRR}$ | Outcome vs Visual Baseline |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| Metadata-Only Retrieval | None | Instrument, kV, Mag, WD | 0.0 | 0.1820 | 0.3443 | -64.4% MRR drop |
| Late Fusion (Grid Search) | DINOv2 (384-d) | Tabular Embedding (64-d) | **1.0** | **0.9481** | **0.9658** | No improvement over visual |
| Gated MLP Fusion | DINOv2 (384-d) | Tabular Embedding (64-d) | Learned | 0.9412 | 0.9610 | No improvement over visual |
| Cross-Attention Network | DINOv2 (384-d) | Tabular Embedding (64-d) | Learned | 0.9380 | 0.9585 | No improvement over visual |

---

### TABLE VI
**Quality Triage, Duplicate Screening & Novelty Benchmarks**

| Task Subsystem | Benchmark Dataset Split | Evaluation Metric | Baseline Metric | Platform Performance |
|:---|:---|:---|:---|:---:|
| **Quality-Risk Screening** | Controlled Degradation ($N=120$) | $\text{AUROC}$ / $\text{AUPRC}$ | Random: 0.5000 / 0.5000 | **0.8803 / 0.9618** |
| **Duplicate Screening** | Synthetic Perturbations ($N=120$) | $\text{AUROC}$ / $F_1$-score | Pixel MSE: $F_1 = 0.7240$ | **0.9998 / 0.9810** |
| **Redundancy Graph Audit** | Natural Repository ($N=769$) | Connected Components | N/A | **764 singletons / 5 pairs** |
| **Relative Novelty Detection** | Out-of-Distribution ($N=120$) | $\text{AUROC}$ | Isolation Forest: 0.9140 | **0.9825** |

---

### TABLE VII
**Architecture & Backbone Resource Profiling**

| Model Backbone | Parameters (M) | Embedding Dim | FLOPs (G) | Peak RAM (MB) | CPU Throughput (img/sec) |
|:---|:---:|:---:|:---:|:---:|:---:|
| ResNet-50 | 25.6 | 2048 | 4.1 | 185 | 68.4 |
| BioMedCLIP (ViT-B/16) | 86.2 | 512 | 17.6 | 420 | 28.5 |
| **DINOv2-ViT-S/14** | **22.1** | **384** | **4.6** | **210** | **54.3** |
| DINOv2-ViT-B/14 | 86.6 | 768 | 18.0 | 440 | 26.2 |

---

### TABLE VIII
**Cross-Domain Generalization Evaluation**

| Target Evaluation Domain | Specimen Modality | Contrast Regime | In-Domain Silhouette | Cross-Domain $\text{Recall@1}$ | Evaluation Status |
|:---|:---|:---|:---:|:---:|:---|
| Ultra-High Carbon Steel | SEM | High-contrast crystalline | 0.612 | 0.9310 | Validated Transfer |
| Ceramic Matrix Composites | SEM | Dual-phase boundary | 0.584 | 0.9140 | Validated Transfer |
| Geological Mineral Thin-Sections| Optical / SEM | Variable birefringence | 0.510 | 0.8420 | Moderate Degradation |
| Biological Ultra-Thin Sections | Cryo-TEM | Low-contrast amorphous | 0.320 | 0.6420 | Marked Degradation |
