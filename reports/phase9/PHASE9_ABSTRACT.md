# Manuscript Abstract & Keywords
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_abstract_001`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Abstract & Keywords

---

## Abstract

Scanning electron microscopy (SEM) generates vast archives of micrographs whose scientific utility is constrained by severe acquisition-induced visual variance, uncalibrated metadata integration, duplicate deposition, and undetected image degradations. Existing computer vision solutions typically address isolated image retrieval or defect classification tasks without providing an integrated, auditable data management platform. In this work, we present an end-to-end scientific image data management framework that combines self-supervised visual foundation representations, acquisition-aware contrastive adaptation, high-throughput vector indexing, conservative deduplication, deterministic quality-risk screening, and auditable human-in-the-loop curation. 

Evaluated on the High-Chromium Cast Iron (HCCI) metallurgical benchmark ($N=774$ physical micrographs across 67 acquisition conditions) and an external semiconductor defect archive (Carinthia SEM, $N=4,591$), frozen DINOv2 ViT-S/14 (`dinov2_vits14`, 384-dimensional, 22.1M parameters) achieves strong zero-shot retrieval accuracy without task-specific fine-tuning (Recall@1 = 0.9819 on HCCI; Micro-Recall@1 = 0.9952 on Carinthia). To overcome instrument-induced visual shifts, we introduce a Supervised Contrastive Learning (SupCon) projection head with same-acquisition masking, which achieves a 68.15% relative reduction in the cross-acquisition similarity gap ($p = 1.42 \times 10^{-12}$), preserves material discriminability at 98.71% linear probe accuracy, and significantly improves deep-ranked precision (Precision@5 = 0.9053 vs. 0.8708, $p = 0.0028$) on an unseen commercial microscope (Zeiss GeminiSEM). Through systematic ablations across six parameter groups, we document an important negative finding: under saturated visual representations, late score-level metadata fusion yields zero additive retrieval improvement ($\Delta \text{Recall@1} = 0.0000, \alpha^* = 1.0$), establishing that scalar metadata parameters do not enhance saturated visual ranking but remain essential for relational pre-filtering and provenance. 

For repository integrity, a 4-stage screening cascade achieves 100% precision and a 0.0% false-positive rate on controlled duplicate benchmarks, partitioning the natural HCCI archive into 769 clusters (764 singletons, 5 pairs) to categorize 769 canonical representatives and 5 review candidates. Deterministic classical signal metrics aggregated into a composite quality-risk indicator achieve AUROC = 0.8803 and AUPRC = 0.9618 in detecting corrupted micrographs, enabling priority triage queues that capture 100% of anomalies within top-25 inspection budgets. The complete framework is realized as an enterprise FastAPI, React, PostgreSQL, and FAISS platform passing 218 automated tests with bit-exact research-to-platform tensor parity ($L_\infty < 1.0 \times 10^{-6}$). While bounded by modest in-domain sample sizes and synthetic quality ground truth, the platform reproduces deterministically from 110 cryptographically frozen files, establishing a rigorous, FAIR-compliant foundation for scientific image repository governance.

---

## Keywords

Scientific Image Data Management, Scanning Electron Microscopy, Self-Supervised Vision Transformers, DINOv2, Contrastive Metric Learning, Acquisition Invariance, Vector Similarity Search, FAISS, Multimodal Metadata Ablation, Negative Result, Perceptual Hashing, Data Integrity, Image Quality Risk Assessment, FAIR Data Principles, Reproducibility.
