# 7. Limitations & Boundary Conditions (Final V2 Manuscript Draft)

## 7.1 Data Independence & Metallurgical Mount Grouping

In all evaluated benchmarks, multiple fields of view originate from common metallurgical mounts and specimen states. While our experimental splits enforce strict mount-level isolation (no specimen overlaps between train and test partitions), our retrieval metrics evaluate micrograph-level representation matching. They must not be interpreted as generalizations over broad metallurgical alloy populations or destructive mechanical properties.

---

## 7.2 Instrument Modality Scope & Spectral Data Availability

1. **Microscopy Modality Boundaries:** Primary empirical validations focus on scanning electron microscopy (SEM) platforms (Zeiss GeminiSEM and industrial defect instruments). Transfer evaluation to transmission electron microscopy (TEM) demonstrated lower zero-shot accuracy (R@1 = 0.7642), confirming that specialized fine-tuning is necessary for diffraction contrast and high-resolution cryo-TEM regimes.
2. **EDS Spectral Integration Status:** In strict accordance with data honesty, Energy Dispersive X-Ray Spectroscopy (EDS) integration is marked **`EDS_INTEGRATION_NOT_EXECUTED`**. None of the studied public repositories contained paired raw multi-channel EDS spectral traces (`.spc` / `.msa` files); no synthetic spectral data was manufactured.

---

## 7.3 Ground-Truth Definition in Expert Curation

The labels established in the human curation study represent **post-hoc expert consensus classifications** rather than external physical ground truth (such as destructive focused-ion-beam cross-sectioning or elemental chemical assay). The 68% triage yield reflects expert-identified novelty and quality cases, not certified physical defects.

---

## 7.4 Vector Scalability & Container Deployment Status

1. **Engineering Stress Test vs Corpus Scale:** The 100,000-vector scalability benchmark evaluated FAISS HNSW search latency under synthetic replicated embeddings on CPU hardware. While it proves sub-millisecond algorithmic scaling (0.317 ms), it does not represent validation on a 100,000-sample real microscopy archive.
2. **Container Deployment Environment:** Platform unit and integration tests passed completely natively on Python 3.11.9 (218/218 tests). However, live Docker container runtime execution is formally designated **`DOCKER_VALIDATION_NOT_EXECUTED`** due to the absence of an active Docker engine daemon on the Windows test environment.
