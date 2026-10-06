# IEEE Paper Section XII: Limitations
**Target Section**: Section XII. Limitations  

---

## XII. LIMITATIONS

To maintain scientific integrity and provide clear context for future research, this section explicitly outlines the operational and empirical boundaries of the proposed platform.

### A. Absence of Physical Ground-Truth Defect Annotations
The quality-risk assessment subsystem computes image-derived mathematical metrics (Laplacian variance roll-off, estimated SNR, contrast entropy) to identify degraded scans. These scores serve as *algorithmic triage indicators*. The underlying dataset lacks physical ground-truth annotations of instrument hardware faults, electron column misalignments, astigmatism, or mechanical vibrations. Consequently, the platform does not claim physical defect diagnosis, and low quality scores must not be interpreted as definitive physical microscope failures without expert verification.

### B. Domain Generalization Boundaries
While DINOv2 demonstrates strong zero-shot transfer across a range of structural materials (alloys, steels, ceramics), evaluation on out-of-domain biological transmission electron microscopy (Cryo-EM, cellular ultra-thin sections) revealed marked performance degradation ($\text{Recall@1} = 0.6420$). The high contrast and repetitive crystallographic features characteristic of materials science do not directly translate to low-contrast, amorphous biological preparations. Claims of universal cross-domain applicability across all scientific imaging modalities are explicitly disclaimed.

### C. Scalability Boundaries of In-Memory Exact Vector Indexing
The current vector search architecture relies on FAISS CPU `IndexFlatIP`. While exact search is mathematically optimal for departmental laboratory repositories ($N \le 100,000$ micrographs, requiring $< 155\text{ MB}$ RAM and $< 2.5\text{ ms}$ query latency), it scales linearly with collection size:
$$\mathcal{O}(N \cdot d)$$
Deploying the platform at national synchrotron facilities or multi-facility scientific clouds hosting tens of millions of micrographs will require transitioning to approximate distributed vector indexing (e.g., HNSW or inverted product quantization) coupled with distributed infrastructure (e.g., Milvus, Qdrant).

### D. Single-Node Workstation Deployment
The platform is packaged and verified as a single-node multi-container Docker Compose deployment. While sufficient for university research groups and core facilities, the architecture currently lacks distributed cluster orchestration (e.g., Kubernetes Helm charts), distributed task queue workers (e.g., Celery/Redis), and multi-region database replication.

### E. Human Curation Dependency
The platform is intentionally designed around human-in-the-loop triage. Triage scores prioritize micrographs in the curation queue, but final archival decisions (`KEEP`, `MERGE`, `REJECT`) require domain expert confirmation. The system does not support fully autonomous, unsupervised dataset pruning.
