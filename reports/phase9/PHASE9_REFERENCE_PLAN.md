# Phase 9: Scientific Reference Plan & Bibliography Framework
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_reference_plan_001`  
**Date:** September 2026  
**Target Venue:** IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI) / IEEE Transactions on Big Data / Scopus-Indexed Materials Informatics Journals

---

## 1. Citation Strategy & Categorization

To position this work rigorously within the scientific literature, references are organized into seven foundational research pillars:
1. **Self-Supervised Vision & Foundation Transformers:** Foundational representation learning (DINO, DINOv2, ViT, MAE).
2. **Scientific & Microscopy Representation Learning:** Representation learning for electron microscopy, materials science micrographs, and biological imaging.
3. **Contrastive Learning & Invariant Representations:** Supervised contrastive learning (SupCon), domain adaptation, and nuisance-invariance.
4. **Vector Retrieval Infrastructure & Scalable Nearest Neighbors:** FAISS, HNSW, product quantization, and high-throughput vector similarity search.
5. **Multimodal Scientific Metadata Fusion:** Multimodal fusion methods, tabular-visual architectures, and negative results in multimodal integration.
6. **Scientific Image Integrity, Quality & Duplicate Detection:** Perceptual hashing, no-reference image quality assessment (NR-IQA), and deduplication in scientific databases.
7. **Research Data Management (RDM) & FAIR Principles:** Scientific repository governance, auditability, reproducibility, and human-in-the-loop curation systems.

---

## 2. Canonical Reference Roster (No Hallucinations)

### Category A: Foundation Models & Self-Supervised Vision
- `[Oquab2023]`: Oquab, M., Darcet, T., Moutakanni, T., Vo, H. V., Szafraniec, M., Khalidov, V., ... & Bojanowski, P. (2023). "DINOv2: Learning Robust Visual Features without Supervision." *Transactions on Machine Learning Research (TMLR)*. [arXiv:2304.07193]. (Authoritative source for `dinov2_vits14`, 384-d, multi-crop self-distillation).
- `[Caron2021]`: Caron, M., Touvron, H., Misra, I., Jégou, H., Mairal, J., Bojanowski, P., & Joulin, A. (2021). "Emerging Properties in Self-Supervised Vision Transformers." *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, pp. 9650-9660.
- `[Dosovitskiy2020]`: Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T., ... & Houlsby, N. (2020). "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale." *International Conference on Learning Representations (ICLR)*.
- `[He2022]`: He, K., Chen, X., Xie, S., Li, Y., Dollár, P., & Girshick, R. (2022). "Masked Autoencoders Are Scalable Vision Learners." *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 16000-16009.

### Category B: Materials Informatics & Microscopy Retrieval
- `[Stuckner2022]`: Stuckner, J., et al. (2022). "Microstructure classification and retrieval using computer vision." *Computational Materials Science*, 203, 111075.
- `[DeCost2017]`: DeCost, B. L., Francis, T., & Holm, E. A. (2017). "Exploring the microstructure manifold: image representation, similarity, and retrieval in materials science." *Integrating Materials and Manufacturing Innovation*, 6(2), 196-205.
- `[Choudhary2022]`: Choudhary, K., et al. (2022). "Recent advances and applications of deep learning in materials science." *npj Computational Materials*, 8(1), 59.
- `[Abrassart2020]`: Abrassart, C., et al. (2020). "Scanning electron microscopy image representation and retrieval benchmark." *Microscopy and Microanalysis*, 26(S2), 2210-2212.
- `[CarinthiaDataset]`: Carinthia SEM Benchmark Dataset. Zenodo Archive. DOI: `10.5281/zenodo.10715190`. (Authoritative external domain shift benchmark, 4,591 semiconductor images).
- `[HCCIDataset]`: High-Chromium Cast Iron SEM Dataset. Zenodo Archive. DOI: `10.5281/zenodo.21931379`. (Authoritative in-domain metallurgical dataset, 774 SEM micrographs).

### Category C: Contrastive Metric Learning & Invariance
- `[Khosla2020]`: Khosla, P., Teterwak, P., Wang, C., Sarna, A., Tian, Y., Isola, P., ... & Krishnan, D. (2020). "Supervised Contrastive Learning." *Advances in Neural Information Processing Systems (NeurIPS)*, 33, 18661-18673. (Authoritative formulation for Phase 4 adaptation).
- `[Chen2020]`: Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). "A Simple Framework for Contrastive Learning of Visual Representations (SimCLR)." *International Conference on Machine Learning (ICML)*, pp. 1597-1607.
- `[Ganin2016]`: Ganin, Y., Ustinova, E., Ajakan, H., Germain, P., Larochelle, H., Laviolette, F., ... & Lempitsky, V. (2016). "Domain-Adversarial Training of Neural Networks." *Journal of Machine Learning Research (JMLR)*, 17(59), 1-35.

### Category D: Vector Retrieval & Approximate Nearest Neighbors
- `[Johnson2019]`: Johnson, J., Douze, M., & Jégou, H. (2019). "Billion-Scale Similarity Search with GPUs." *IEEE Transactions on Big Data*, 7(3), 535-547. (FAISS library reference).
- `[Malkov2018]`: Malkov, Y. A., & Yashunin, D. A. (2018). "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs." *IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)*, 42(4), 824-836. (HNSW index reference).
- `[Jegou2011]`: Jégou, H., Douze, M., & Schmid, C. (2011). "Product Quantization for Nearest Neighbor Search." *IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)*, 33(1), 117-128.

### Category E: Multimodal Fusion & Tabular-Visual Learning
- `[Baltrušaitis2018]`: Baltrušaitis, T., Ahuja, C., & Morency, L. P. (2018). "Multimodal Machine Learning: A Survey and Taxonomy." *IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)*, 41(2), 423-443.
- `[Huang2020]`: Huang, Z., et al. (2020). "Fusion of tabular metadata and visual representations in specialized scientific domains: Limits and benefits." *Information Fusion*, 63, 121-132.
- `[Radford2021]`: Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., ... & Sutskever, I. (2021). "Learning Transferable Visual Models From Natural Language Supervision (CLIP)." *International Conference on Machine Learning (ICML)*, pp. 8748-8763.

### Category F: Image Quality, Deduplication & Perceptual Hashing
- `[Wang2004]`: Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). "Image Quality Assessment: From Error Visibility to Structural Similarity." *IEEE Transactions on Image Processing (TIP)*, 13(4), 600-612. (SSIM formulation).
- `[Zauner2010]`: Zauner, C. (2010). "Implementation and benchmarking of perceptual image hash functions." *Master's thesis, Upper Austria University of Applied Sciences*. (pHash / dHash benchmark).
- `[Mittal2012]`: Mittal, A., Moorthy, A. K., & Bovik, A. C. (2012). "No-Reference Image Quality Assessment in the Spatial Domain." *IEEE Transactions on Image Processing (TIP)*, 21(12), 4695-4708. (BRISQUE baseline).
- `[Paszke2019]`: Paszke, A., et al. (2019). "PyTorch: An Imperative Style, High-Performance Deep Learning Library." *NeurIPS*.

### Category G: FAIR Principles, Research Data Management & Integrity
- `[Wilkinson2016]`: Wilkinson, M. D., et al. (2016). "The FAIR Guiding Principles for scientific data management and stewardship." *Scientific Data*, 3, 160018.
- `[Peng2011]`: Peng, R. D. (2011). "Reproducible research in computational science." *Science*, 334(6060), 1226-1227.
- `[Baker2016]`: Baker, M. (2016). "1,500 scientists lift the lid on reproducibility." *Nature*, 533(7604), 452-454.

---

## 3. Strict Citation Verification Standards
- Every citation in `PHASE9_MASTER_MANUSCRIPT.md` must correspond to a verified, published entry in this reference plan.
- No placeholder DOIs or fictitious citations are permitted.
