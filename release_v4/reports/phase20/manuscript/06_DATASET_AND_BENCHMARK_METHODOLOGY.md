# 4. DATASET & BENCHMARK METHODOLOGY

Rigorous evaluation of scientific image data systems requires ecologically valid microscopy benchmarks that reflect realistic instrument variations, mineralogical complexities, and acquisition artifacts.

### 4.1 Benchmark Datasets
1. **HCCI Mineralogy Benchmark**: The primary in-domain benchmark comprises $N=774$ high-resolution SEM micrographs collected across six distinct mineralogical categories: Sphalerite, Chalcopyrite, Galena, Pyrite, Arsenopyrite, and Pyrrhotite. Micrographs were acquired using both secondary electron (SE) and backscattered electron (BSE) detectors across multiple accelerating voltages ($5\text{ kV}$ to $20\text{ kV}$). Specimen-level clustering identified 769 distinct perceptual clusters and exactly 0 identical duplicate pairs, establishing a rigorous basis for retrieval evaluation.
2. **Carinthia Defect SEM Benchmark**: Used for external zero-shot transfer and out-of-distribution evaluation. Consists of $N=4,591$ SEM micrographs depicting semiconductor and materials defect classes across six categories.
3. **SEM Nanoscience Benchmark**: An external corpus of $N=21,169$ SEM micrographs representing broad nanoscale synthesis and characterization, utilized for distribution shift analysis ($	ext{MMD}^2$).

### 4.2 Evaluation Metrics
- **Recall at Rank $k$ (R@$k$)**: Proportion of queries for which at least one relevant specimen-level micrograph appears in the top $k$ retrieved results.
- **Mean Reciprocal Rank (MRR)**: Average reciprocal rank of the first relevant retrieved result:
  $$	ext{MRR} = rac{1}{|Q|} \sum_{i=1}^{|Q|} rac{1}{	ext{rank}_i}$$
- **Precision at Rank 5 (P@5)**: Proportion of relevant results among the top 5 retrieved items.
- **Tenengrad Focus AUROC & AUPRC**: Area under the ROC and Precision-Recall curves evaluating defocus screening against reference focus sweeps.
- **Maximum Mean Discrepancy ($	ext{MMD}^2$)**: Unbiased kernel two-sample test measuring distribution shift between domain representations:
  $$	ext{MMD}^2(P, Q) = \mathbb{E}[k(x,x')] - 2\mathbb{E}[k(x,y)] + \mathbb{E}[k(y,y')]$$

### 4.3 Reference Random Baselines
To guard against metric inflation in retrieval evaluations, we establish two exact mathematical random baselines:
- **Balanced Uniform Random Baseline (6 Classes)**:
  $$	ext{Top-1 Accuracy} = rac{1}{6} pprox 0.1667$$
  $$	ext{MRR} = rac{1}{6} \sum_{k=1}^6 rac{1}{k} = rac{49}{120} pprox 0.4083$$
- **Gallery-Weighted Random Baseline (Empirical Carinthia Class Distribution)**:
  $$	ext{Micro R@1} = 0.7687, \quad 	ext{Macro R@1} = 0.1665$$
All experimental evaluations are strictly benchmarked against these theoretical baselines.
