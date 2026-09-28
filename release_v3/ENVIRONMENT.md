# Execution Environment Specification

### Pinned Hardware & Software Configuration

| Component | Tested Host Specification | Minimum Requirement |
|---|---|---|
| **OS** | Windows 11 Enterprise (Build 26200.5050) | Windows 10/11 x64 or Linux (Ubuntu 20.04+) |
| **CPU Architecture** | AMD64 (x86_64 Family 25 Model 104 Stepping 1) | 4-Core x86_64 CPU |
| **System Memory** | 16 GB DDR4 RAM | 8 GB RAM |
| **Disk Space** | NVMe SSD (~15 GB free space for datasets/caches) | 10 GB free space |
| **Python Runtime** | Python 3.11.9 (CPython 64-bit) | Python 3.11.x strictly |

---

### Core Pinned Python Dependencies

| Package | Pinned Version | Purpose |
|---|---|---|
| `torch` | `2.2.0+cpu` | Neural network forward pass, contrastive loss, embeddings |
| `torchvision` | `0.17.0+cpu` | Image transformation, normalization pipelines |
| `faiss-cpu` | `1.8.0` | Dense vector indexing, exact FlatIP, and approximate HNSW search |
| `scikit-learn` | `1.4.1.post1` | Linear probes, logistic regression, clustering, ROC/PR curves |
| `fastapi` | `0.110.0` | REST API framework for platform backend |
| `sqlalchemy` | `2.0.28` | Database ORM and relational modeling |
| `pydantic` | `2.6.4` | Data validation and schema enforcement |
| `pillow` | `10.2.0` | Micrograph ingestion and verification |
| `tifffile` | `2024.2.12` | High-bit-depth scientific TIFF format parsing |
| `pandas` | `2.2.1` | Tabular data manipulation and parquet storage |
| `numpy` | `1.26.4` | Numerical array operations and metric computation |

---

### Docker Execution Environment

- **Base Image**: `python:3.11-slim-bookworm`
- **Compose Service**: Backend API + SQLite/PostgreSQL storage + volume mounts for FAISS indices.
- **Limitation**: When host Docker engine daemon is unavailable (`DOCKER_RUNTIME_REMAINING_LIMITATION`), all workloads execute natively within `.venv311`.
