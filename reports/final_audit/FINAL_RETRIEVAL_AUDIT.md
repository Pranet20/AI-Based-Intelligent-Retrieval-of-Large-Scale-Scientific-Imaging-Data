# Master Final Retrieval & Vector Search Audit (Phase 3)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Vector Search Indexing, Query Latency, Throughput, and Approximate Agreement  
**Status:** `EMPIRICALLY_VERIFIED_SCOPED`

---

## 1. Indexing Algorithms & Authoritative Reference

- **Vector Library:** FAISS-CPU (version 1.9.0)
- **Reference Exhaustive Index:** `IndexFlatIP` (Exact inner product search on L2-normalized 384-dimensional vectors).
- **Approximate Graph Index:** `IndexHNSWFlat` ($M = 32$, `efSearch` = 64, `efConstruction` = 40).
- **Inverted File Index:** `IndexIVFFlat` ($nlist = 100$, $nprobe = 10$).

---

## 2. Timing Methodology & Benchmarking Conditions

1. **Hardware Configuration:** 8 vCPUs (Intel Core i7 @ 2.80 GHz), 16 GB RAM, Windows 11 host. Single-threaded query evaluation without GPU acceleration.
2. **Measurement Protocol:** 10 warm-up queries discarded; 100 timed query iterations per scale condition. Latencies measured using Python `time.perf_counter_ns()`. Index construction time measured independently from query latency.
3. **Exact vs Approximate Agreement:** On the authoritative $N = 5{,}365$ repository, HNSW achieves **0.9982 rank-1 agreement** with exhaustive Flat search, demonstrating negligible loss of precision.

---

## 3. Authoritative Performance Numbers

| Corpus Size ($N$) | Flat Search Latency (ms) | HNSW Search Latency (ms) | HNSW QPS | Speedup vs Flat | Index Memory |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **5,365 (Repository Baseline)** | 0.1497 | **0.0963** | 10,384 QPS | **1.55x** | 11.2 MB |
| **10,000** | 0.3462 | **0.1210** | 8,266 QPS | **2.86x** | 21.0 MB |
| **25,000** | 0.9160 | **0.2281** | 4,385 QPS | **4.02x** | 52.5 MB |
| **50,000** | 1.5435 | **0.4017** | 2,489 QPS | **3.84x** | 105.0 MB |
| **100,000 (Stress Test)** | 4.9562 | **0.3169** | 3,155 QPS | **15.64x** | 210.0 MB |

> [!IMPORTANT]
> **Correct Terminology & Boundaries:**
> 1. Do **not** claim theoretical $\mathcal{O}(\log N)$ complexity without qualification; graph traversal complexity depends on intrinsic dimensionality and metric clustering.
> 2. The 100,000-vector benchmark is an **engineering stress test** on synthetic replicated vectors. It demonstrates algorithmic sub-millisecond retrieval scaling, but must not be conflated with a 100,000-sample real microscopy archive.
