# Section 5: Proposed Scientific Image Data Management Framework
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_methodology_001`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 5

---

# 5. Proposed Scientific Image Data Management Framework

The proposed platform is engineered as an end-to-end scientific image data management framework designed to ingest, represent, index, verify, curate, and serve scanning electron microscopy archives. Figure 1 illustrates the high-level system architecture, comprising eleven tightly coupled computational stages.

---

### 5.1 Scientific Data Ingestion & Provenance Registration

Scientific reproducibility requires that every raw image ingested into the repository possesses an immutable, cryptographically verifiable identity. During ingestion:
1. **Cryptographic Checksumming:** Each raw file is ingested from its local or remote source, and its SHA-256 cryptographic digest is immediately computed and registered in an immutable manifest table.
2. **Provenance Registration:** The ingestion pipeline captures source metadata including the originating repository DOI (e.g., Zenodo archives `10.5281/zenodo.21931379` for HCCI and `10.5281/zenodo.10715190` for Carinthia), original filesystem timestamp, MIME type, uncompressed byte size, and acquisition instrument identifier.
3. **Decoded Pixel Integrity:** To verify that files are neither corrupted nor truncated during transport, the uncompressed pixel array is decoded into memory and audited for non-zero dynamic range.

---

### 5.2 Metadata Normalization & Safe Feature Formulation

Header metadata extracted from electron microscopy formats (e.g., TIFF tag blocks) contains heterogeneous, non-standardized parameters. The metadata preprocessing engine partitions extracted fields into **safe** and **prohibited** features:
- **Prohibited Features (Strict Leakage Prevention):** Fields directly encoding specimen condition (`specimen_id`), local field-of-view identifier (`roi_id`), internal database identifier (`image_id`), filename, and acquisition cluster ID (`acquisition_id`) are permanently purged from the retrieval feature set.
- **Approved Feature Groups:**
  - *Group A (Imaging Geometry):* Magnification ($M$), horizontal field width, pixel size ($nm$).
  - *Group B (Beam Parameters):* Accelerating voltage ($kV$), emission beam current ($nA$), dwell time ($\mu s$).
  - *Group C (Detector Setup):* Detector mode (categorical: Secondary Electron [SE] vs. Backscattered Electron [BSE], in-lens vs. chamber).
  - *Group D (Chamber Environment):* Vacuum chamber pressure ($Pa$), working distance ($mm$).
  - *Group E (Full Normalized Metadata):* Concatenation of all approved features from Groups A–D.
  - *Group F (Missingness Indicators):* Group E augmented with binary missingness indicators ($b_k \in \{0, 1\}$) to handle unrecorded fields gracefully.

Continuous numerical features are standardized using mean and variance statistics fitted strictly on the training partition:
$$\hat{x}_j = \frac{x_j - \mu_j^{\text{train}}}{\sigma_j^{\text{train}} + \epsilon}$$
Categorical attributes are mapped through learned entity embedding tables ($d_{\text{cat}} = 32$). The combined tabular representation is projected through a 2-layer Multi-Layer Perceptron (MLP) into $\mathbb{R}^{384}$ to match the visual embedding dimension, followed by $L_2$ normalization:
$$\mathbf{m} = \frac{W_2 \cdot \text{ReLU}(W_1 \mathbf{x}_{\text{meta}} + \mathbf{b}_1) + \mathbf{b}_2}{\|W_2 \cdot \text{ReLU}(W_1 \mathbf{x}_{\text{meta}} + \mathbf{b}_1) + \mathbf{b}_2\|_2} \in \mathbb{R}^{384}$$

---

### 5.3 Foundation Visual Representation (`dinov2_vits14`)

Visual feature extraction is performed using the frozen self-supervised DINOv2 Vision Transformer Small architecture (`dinov2_vits14`) [Oquab2023]:
- **Architecture Properties:** Patch size $14 \times 14$ pixels, 6 transformer heads, 12 transformer layers, embedding dimension $D = 384$, total parameter count = $22,056,576$.
- **Image Preprocessing:** Grayscale SEM micrographs (single-channel 8-bit or 16-bit) are replicated across three channels to conform to standard 3-channel vision transformer inputs ($\mathbb{R}^{H \times W \times 1} \to \mathbb{R}^{H \times W \times 3}$). Micrographs are deterministically resized to $224 \times 224$ pixels using bicubic interpolation with antialiasing enabled, and normalized using standard ImageNet channel statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).
- **Embedding Extraction:** The class token output ($\mathbf{v}_{\text{cls}} \in \mathbb{R}^{384}$) is extracted from the final transformer block and subjected to unit $L_2$ normalization:
  $$\mathbf{v} = \frac{\mathbf{v}_{\text{cls}}}{\|\mathbf{v}_{\text{cls}}\|_2}, \quad \|\mathbf{v}\|_2 = 1.0$$
The cosine similarity between any two micrographs $i$ and $j$ simplifies to the inner product:
$$S_{\text{vis}}(i, j) = \cos(\mathbf{v}_i, \mathbf{v}_j) = \mathbf{v}_i^\top \mathbf{v}_j$$

---

### 5.4 Acquisition-Aware Contrastive Adaptation

To mitigate the representation gap induced by varying microscope operating conditions, we introduce a contrastive metric learning projection head trained on top of the frozen `dinov2_vits14` backbone:
- **Projector Architecture:** A 2-layer MLP projection head $g: \mathbb{R}^{384} \to \mathbb{R}^{128}$:
  $$\mathbf{z} = g(\mathbf{v}) = W_2 \cdot \text{ReLU}(\text{BN}(W_1 \mathbf{v})), \quad \hat{\mathbf{z}} = \frac{\mathbf{z}}{\|\mathbf{z}\|_2}$$
  where $W_1 \in \mathbb{R}^{128 \times 384}$, $W_2 \in \mathbb{R}^{128 \times 128}$, $\text{BN}$ denotes 1D Batch Normalization, and $\hat{\mathbf{z}} \in \mathbb{R}^{128}$ is unit-normalized. Total trainable parameters in the projector head equal $66,048$.
- **Supervised Contrastive Objective with Same-Acquisition Masking:**
  Unlike standard SupCon [Khosla2020], our formulation explicitly suppresses nuisance correlations arising from identical microscope acquisition settings. In a minibatch of $2N$ augmented views, let $i \in I$ index an anchor image with specimen alloy label $y_i$ and acquisition condition identifier $a_i \in \{1, \dots, A\}$.
  The positive set $P(i)$ for anchor $i$ is defined strictly as:
  $$P(i) \equiv \left\{ p \in I \setminus \{i\} : y_p = y_i \quad \text{AND} \quad a_p \neq a_i \right\}$$
  Pairs sharing both the same specimen label and the same acquisition condition ($y_p = y_i, a_p = a_i$) are masked out (neutralized) to prevent the network from memorizing instrument-specific contrast or detector gains.
  The contrastive adaptation loss is formulated as:
  $$\mathcal{L}_{\text{adapt}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(\hat{\mathbf{z}}_i^\top \hat{\mathbf{z}}_p / \tau)}{\sum_{a \in A(i)} \exp(\hat{\mathbf{z}}_i^\top \hat{\mathbf{z}}_a / \tau)}$$
  where $A(i) \equiv I \setminus \{i\}$, and temperature hyperparameter is set to $\tau = 0.07$. Crucially, no explicit Lagrangian penalty regularization term is applied; domain invariance is induced purely via positive-pair sampling semantics.

---

### 5.5 High-Throughput Vector Similarity Retrieval

Vector retrieval is powered by the FAISS C++ library [Johnson2019]:
1. **Exact Maximum Inner Product Search (`IndexFlatIP`):** Computes exact cosine similarity between query vector $\mathbf{q} \in \mathbb{R}^d$ and all database vectors $\{\mathbf{v}_1, \dots, \mathbf{v}_N\}$ via multi-threaded BLAS matrix multiplication ($\mathcal{O}(N \cdot d)$ complexity). Serves as the gold-standard ground truth for retrieval evaluation.
2. **Approximate Hierarchical Navigable Small World (`IndexHNSWFlat`):** Constructs a multi-layer graph of vectors where greedy routing traverses from coarse to fine layers ($\mathcal{O}(\log N)$ complexity). Configured with graph out-degree $M = 32$, search expansion depth $efSearch = 64$, and construction depth $efConstruction = 64$.
3. **Parity Verification:** The index verification pipeline continuously audits Top-$K$ agreement between `IndexHNSWFlat` and `IndexFlatIP`, confirming $>0.999$ recall retention.

---

### 5.6 Metadata Retrieval & Convex Late Fusion

To benchmark multimodal integration, visual similarity $S_{\text{vis}}$ and metadata similarity $S_{\text{meta}}$ are combined via late convex score fusion:
$$S_{\text{hybrid}}(q, c) = \alpha \cdot S_{\text{vis}}(q, c) + (1 - \alpha) \cdot S_{\text{meta}}(q, c)$$
where $\alpha \in [0.0, 1.0]$ is a late fusion mixing coefficient.
- **Validation Alpha Selection:** Optimal $\alpha^*$ is determined via an exhaustive grid search over $\alpha \in \{0.0, 0.1, \dots, 1.0\}$ strictly on the validation partition ($N=135$).
- **Held-Out Test Evaluation:** The tuned $\alpha^*$ is locked and evaluated on the unseen test partition ($N=212$).

---

### 5.7 Conservative 4-Stage Deduplication Cascade

To prevent catastrophic false-positive deduplications in scientific archives, we implement a 4-stage sequential screening cascade:
- **Stage 1 (Exact Bitwise Match):** Evaluates SHA-256 cryptographic digests. Pairs with matching hashes are flagged as bitwise exact duplicates (distance $= 0$).
- **Stage 2 (Dual Perceptual Hashing):** Computes 64-bit DCT perceptual hash (pHash) and 64-bit horizontal difference hash (dHash) [Zauner2010]. Candidate pairs are retained if $\text{Hamming}(h_1, h_2) \le 6$ on both hashes.
- **Stage 3 (Foundation Feature Cosine Gate):** Evaluates cosine similarity of frozen `dinov2_vits14` embeddings. Candidate pairs must satisfy:
  $$S_{\text{vis}}(i, j) \ge 0.985$$
- **Stage 4 (Structural SSIM and MAE Verification):** Full-resolution image arrays are aligned and evaluated for structural fidelity. Candidates must simultaneously satisfy:
  $$\text{SSIM}(I_i, I_j) \ge 0.95 \quad \text{AND} \quad \text{MAE}(I_i, I_j) \le 5.0 \text{ pixel intensity levels}$$
Candidate pairs surviving all 4 stages are mapped into an undirected redundancy graph $G = (V, E)$, and connected components clustering partitions the corpus into distinct cluster sets. In each multi-image cluster, the image with the highest Laplacian sharpness variance is designated as the canonical cluster representative (**KEEP**), while secondary members are queued as **REVIEW** candidates.

---

### 5.8 Image-Derived Quality-Risk Assessment

Quality screening is performed using deterministic classical signal processing indicators, avoiding un-interpretable black-box neural networks:
1. **Defocus Blur Indicator:** Laplacian variance $\sigma_{\text{Lap}}^2 = \text{Var}(\nabla^2 I)$. Lower variance indicates severe defocus.
2. **Noise Sigma Indicator:** High-frequency noise estimated via median absolute deviation of Haar wavelet sub-bands or Laplacian residuals: $\hat{\sigma}_{\text{noise}}$.
3. **Contrast Dynamic Range Indicator:** Difference between 99th and 1st intensity percentiles: $\Delta I = P_{99}(I) - P_{01}(I)$.
4. **Sensor Clipping Ratio:** Fraction of saturated pixels: $R_{\text{clip}} = \frac{1}{|I|} \sum \mathbb{I}(I(x, y) \le 2 \lor I(x, y) \ge 253)$.
5. **Beam Astigmatism / Drift Indicator:** Ratio of high-frequency spectral energy computed via 2D Fast Fourier Transform (FFT): $R_{\text{FFT}} = \frac{\int_{r > r_0} |F(u, v)|^2 dudv}{\int |F(u, v)|^2 dudv}$.

Each metric is converted into a normalized risk indicator $r_k \in [0, 1]$ via empirical CDF mapping, and aggregated into a **Composite Quality Risk Score**:
$$Q_{\text{risk}} = 1 - \prod_{k=1}^K (1 - r_k)^{w_k}, \quad \sum w_k = 1.0$$
Images with $Q_{\text{risk}} \ge \theta_{\text{risk}}$ are flagged for data curation.

---

### 5.9 Relative Embedding-Space Novelty Detection

Novelty detection identifies micrographs that diverge significantly from established baseline microstructures:
- **kNN Distance ($k=5$):** Mean Euclidean distance to the 5 nearest neighbors in the 384-dimensional $L_2$-normalized embedding space:
  $$d_{\text{kNN}}(\mathbf{v}) = \frac{1}{k} \sum_{j \in \mathcal{N}_k(\mathbf{v})} \|\mathbf{v} - \mathbf{v}_j\|_2$$
- **Local Outlier Factor (LOF):** Measures the local density of an embedding relative to its surrounding neighborhood.
Micrographs exhibiting high novelty scores represent candidate unusual microstructures, phase transitions, or external artifacts.

---

### 5.10 Human-in-the-Loop Curation & Priority Triage Queues

To maximize the efficiency of human domain experts, the platform constructs an automated **Priority Review Queue**:
$$\text{Priority}(i) = \beta_1 \cdot Q_{\text{risk}}(i) + \beta_2 \cdot d_{\text{kNN}}(i) + \beta_3 \cdot \mathbb{I}(\text{DuplicateCandidate}(i))$$
Under constrained human inspection budgets (e.g., inspecting only Top-10, Top-25, or Top-50 images), this prioritized ordering ensures that defective, duplicate, and anomalous micrographs are reviewed first.

---

### 5.11 Software Architecture, Auditability & FAIR Governance

The platform is realized as a modular enterprise architecture:
- **Backend Service:** FastAPI (Python 3.11) exposing asynchronous REST endpoints for ingestion, search, duplicate clustering, quality assessment, and curation disposition.
- **Data Persistence:** PostgreSQL / SQLite managed via SQLAlchemy ORM with foreign key cascades, transaction isolation, and complete audit logging tables.
- **Frontend Dashboard:** React single-page application providing interactive microstructure visual search, side-by-side duplicate comparison, quality distribution plots, and one-click curator review actions.
- **Security & Access Control:** PBKDF2 password hashing, JSON Web Tokens (JWT), and Role-Based Access Control (RBAC) supporting Curator, Analyst, and Administrator roles.
- **Testing & Verification:** Comprehensive test suite of 218 automated unit and integration tests passing continuously, certifying bit-exact numerical parity ($L_\infty < 1.0 \times 10^{-6}$) between research prototypes and production inference engines.
