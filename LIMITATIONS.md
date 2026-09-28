# Explicit Project Limitations & Boundary Conditions

**Document Version:** 1.0.0-final  
**Date:** 2026-09-27  
**Status:** AUTHORITATIVE COMPLIANCE DISCLOSURE

---

1. **Docker Container Runtime Status:**
   Native platform unit and integration tests passed completely on Python 3.11.9 (218/218 tests). However, live Docker container runtime execution is formally designated **`DOCKER_RUNTIME_REMAINING_LIMITATION`** due to the absence of an active Docker engine daemon on the Windows host environment.

2. **Dataset Rights & Third-Party Redistribution:**
   While SEM Nanoscience is verified CC BY 4.0, HCCI and Carinthia Zenodo records lack visible explicit license badges and are classified as **`RIGHTS_UNVERIFIED`**. Consequently, raw image files are excluded from public redistribution and restricted to academic local research.

3. **EDS / Spectral Data Non-Execution:**
   None of the studied public archives contain paired multi-channel EDS spectral traces (`.spc` / `.msa` files). In compliance with anti-fabrication standards, EDS integration is recorded as **`EDS_INTEGRATION_NOT_EXECUTED`**.

4. **Human Curation Ground-Truth Scope:**
   The labels established in the expert curation studies represent **post-hoc expert consensus classifications**, not certified destructive physical ground truth. The 68% triage yield reflects expert-identified novelty and quality cases.

5. **100K Vector Scaling Scope:**
   The 100,000-vector scalability benchmark evaluated FAISS HNSW search latency under synthetic replicated embeddings on CPU hardware. It demonstrates algorithmic sub-millisecond retrieval scaling (0.317 ms), not scientific validation on a 100,000-sample real microscopy archive.

6. **Microscopy Modality Scope:**
   Primary validations focus on scanning electron microscopy (SEM). Transmission electron microscopy (TEM) and high-resolution cryo-TEM regimes require domain-specific fine-tuning.
