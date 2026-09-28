"""High-resolution latency, throughput, and memory benchmarking for FAISS indexing."""

from __future__ import annotations

import gc
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.retrieval.faiss_index import FAISSVectorIndex, IndexType
from src.utils.logging import get_logger

logger = get_logger("retrieval.benchmark")


class FAISSLatencyBenchmark:
    """Rigorous, high-resolution latency and memory benchmark suite."""

    def __init__(
        self,
        storage_dir: str | Path = "data/processed/indexes",
        reports_dir: str | Path = "reports/phase3",
        warmup_queries: int = 20,
        repetitions: int = 3,
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.warmup_queries = warmup_queries
        self.repetitions = repetitions

    def benchmark_index_lifecycle(
        self,
        name: str,
        index_type: IndexType,
        embeddings: np.ndarray,
        ids: List[str],
        query_vectors: np.ndarray,
        k: int = 10,
        nlist: int = 32,
        nprobe: int = 4,
        hnsw_m: int = 16,
        ef_search: int = 32,
    ) -> Dict[str, Any]:
        """Measure index build time, serialization size/time, load time, and query latency."""
        logger.info("Benchmarking %s (type=%s, N=%d, K=%d)...", name, index_type.value, len(embeddings), k)

        # 1. Build Index Time
        gc.collect()
        t0 = time.perf_counter()
        index = FAISSVectorIndex(
            dimension=embeddings.shape[1],
            index_type=index_type,
            nlist=nlist,
            nprobe=nprobe,
            hnsw_m=hnsw_m,
            ef_search=ef_search,
        )
        index.build(embeddings, ids=ids)
        build_time_sec = time.perf_counter() - t0

        # 2. Serialize / Save Time and Disk Size
        save_path = self.storage_dir / f"{name}.faiss"
        t0 = time.perf_counter()
        idx_file, meta_file = index.save(save_path)
        save_time_sec = time.perf_counter() - t0
        index_file_bytes = idx_file.stat().st_size if idx_file.is_file() else 0
        meta_file_bytes = meta_file.stat().st_size if meta_file.is_file() else 0
        total_disk_mb = (index_file_bytes + meta_file_bytes) / (1024 * 1024)

        # 3. Load Time
        t0 = time.perf_counter()
        loaded_index = FAISSVectorIndex.load(save_path)
        load_time_sec = time.perf_counter() - t0

        # 4. Query Latency & QPS
        # Warmup phase (excluded from timed results)
        n_queries = len(query_vectors)
        warmup_n = min(self.warmup_queries, n_queries)
        if warmup_n > 0:
            warmup_q = query_vectors[:warmup_n]
            _ = loaded_index.search(warmup_q, k=k, nprobe=nprobe, ef_search=ef_search)

        # Timed individual queries over repetitions
        query_latencies_ms: List[float] = []
        for rep in range(self.repetitions):
            for i in range(n_queries):
                q = query_vectors[i : i + 1]
                t_q0 = time.perf_counter()
                _ = loaded_index.search(q, k=k, nprobe=nprobe, ef_search=ef_search)
                lat_ms = (time.perf_counter() - t_q0) * 1000.0
                query_latencies_ms.append(lat_ms)

        mean_lat_ms = float(np.mean(query_latencies_ms))
        median_lat_ms = float(np.median(query_latencies_ms))
        p95_lat_ms = float(np.percentile(query_latencies_ms, 95))
        p99_lat_ms = float(np.percentile(query_latencies_ms, 99))
        qps = 1000.0 / mean_lat_ms if mean_lat_ms > 0 else 0.0

        stats = {
            "index_name": name,
            "index_type": index_type.value,
            "sample_count": len(embeddings),
            "dimension": embeddings.shape[1],
            "nlist": nlist if index_type == IndexType.IVF_FLAT else None,
            "nprobe": nprobe if index_type == IndexType.IVF_FLAT else None,
            "hnsw_m": hnsw_m if index_type == IndexType.HNSW_FLAT else None,
            "ef_search": ef_search if index_type == IndexType.HNSW_FLAT else None,
            "k": k,
            "build_time_sec": round(build_time_sec, 4),
            "save_time_sec": round(save_time_sec, 4),
            "load_time_sec": round(load_time_sec, 4),
            "index_size_mb": round(total_disk_mb, 4),
            "mean_latency_ms": round(mean_lat_ms, 4),
            "median_latency_ms": round(median_lat_ms, 4),
            "p95_latency_ms": round(p95_lat_ms, 4),
            "p99_latency_ms": round(p99_lat_ms, 4),
            "qps": round(qps, 2),
            "warmup_queries": warmup_n,
            "repetitions": self.repetitions,
            "total_timed_queries": len(query_latencies_ms),
        }
        return stats

    def benchmark_brute_force_latency(
        self,
        embeddings: np.ndarray,
        query_vectors: np.ndarray,
        k: int = 10,
    ) -> Dict[str, Any]:
        """Benchmark reference exact brute-force cosine search under identical conditions."""
        n_queries = len(query_vectors)
        warmup_n = min(self.warmup_queries, n_queries)
        if warmup_n > 0:
            for i in range(warmup_n):
                q = query_vectors[i : i + 1]
                scores = np.dot(q, embeddings.T)[0]
                _ = np.argsort(-scores)[:k]

        latencies_ms: List[float] = []
        for rep in range(self.repetitions):
            for i in range(n_queries):
                q = query_vectors[i : i + 1]
                t0 = time.perf_counter()
                scores = np.dot(q, embeddings.T)[0]
                _ = np.argsort(-scores)[:k]
                lat_ms = (time.perf_counter() - t0) * 1000.0
                latencies_ms.append(lat_ms)

        mean_lat = float(np.mean(latencies_ms))
        median_lat = float(np.median(latencies_ms))
        p95_lat = float(np.percentile(latencies_ms, 95))
        p99_lat = float(np.percentile(latencies_ms, 99))
        qps = 1000.0 / mean_lat if mean_lat > 0 else 0.0

        return {
            "index_name": "BruteForce_Reference",
            "index_type": "Exact_NumPy_Cosine",
            "sample_count": len(embeddings),
            "dimension": embeddings.shape[1],
            "nlist": None,
            "nprobe": None,
            "hnsw_m": None,
            "ef_search": None,
            "k": k,
            "build_time_sec": 0.0,
            "save_time_sec": 0.0,
            "load_time_sec": 0.0,
            "index_size_mb": round((embeddings.nbytes) / (1024 * 1024), 4),
            "mean_latency_ms": round(mean_lat, 4),
            "median_latency_ms": round(median_lat, 4),
            "p95_latency_ms": round(p95_lat, 4),
            "p99_latency_ms": round(p99_lat, 4),
            "qps": round(qps, 2),
            "warmup_queries": warmup_n,
            "repetitions": self.repetitions,
            "total_timed_queries": len(latencies_ms),
        }

    def run_synthetic_scaling_stress_test(
        self,
        base_embeddings: np.ndarray,
        target_sizes: List[int] = [5365, 10730, 21460, 42920, 85840],
        test_queries_count: int = 50,
    ) -> List[Dict[str, Any]]:
        """Run controlled engineering scalability stress test by vector duplication.

        CRITICAL SCIENTIFIC INTEGRITY REQUIREMENT:
        This is an ENGINEERING SCALABILITY STRESS TEST only.
        It must NEVER be presented as scientific retrieval data.
        """
        logger.info("Executing engineering scalability stress test across sizes %s...", target_sizes)
        results = []
        base_n = len(base_embeddings)
        query_sample = base_embeddings[:test_queries_count]

        for target_n in target_sizes:
            # Replicate vectors to reach target size
            repeats = int(np.ceil(target_n / base_n))
            scaled_matrix = np.tile(base_embeddings, (repeats, 1))[:target_n]
            scaled_ids = [f"synth_{i}" for i in range(target_n)]

            logger.info("Testing scaled corpus N=%d vectors...", target_n)

            # Test FlatIP
            t0 = time.perf_counter()
            flat_idx = FAISSVectorIndex(dimension=384, index_type=IndexType.FLAT_IP)
            flat_idx.build(scaled_matrix, ids=scaled_ids)
            flat_build_s = time.perf_counter() - t0

            # Measure Flat query latency
            flat_lats = []
            for i in range(len(query_sample)):
                t_q = time.perf_counter()
                _ = flat_idx.search(query_sample[i : i + 1], k=10)
                flat_lats.append((time.perf_counter() - t_q) * 1000.0)

            results.append({
                "benchmark_type": "engineering_scalability_stress_test",
                "index_type": "IndexFlatIP",
                "corpus_size": target_n,
                "dimension": 384,
                "build_time_sec": round(flat_build_s, 4),
                "mean_latency_ms": round(float(np.mean(flat_lats)), 4),
                "median_latency_ms": round(float(np.median(flat_lats)), 4),
                "qps": round(1000.0 / float(np.mean(flat_lats)), 2),
            })

            # Test HNSW (M=16, efSearch=32)
            t0 = time.perf_counter()
            hnsw_idx = FAISSVectorIndex(dimension=384, index_type=IndexType.HNSW_FLAT, hnsw_m=16, ef_search=32)
            hnsw_idx.build(scaled_matrix, ids=scaled_ids)
            hnsw_build_s = time.perf_counter() - t0

            hnsw_lats = []
            for i in range(len(query_sample)):
                t_q = time.perf_counter()
                _ = hnsw_idx.search(query_sample[i : i + 1], k=10, ef_search=32)
                hnsw_lats.append((time.perf_counter() - t_q) * 1000.0)

            results.append({
                "benchmark_type": "engineering_scalability_stress_test",
                "index_type": "IndexHNSWFlat(M=16,efSearch=32)",
                "corpus_size": target_n,
                "dimension": 384,
                "build_time_sec": round(hnsw_build_s, 4),
                "mean_latency_ms": round(float(np.mean(hnsw_lats)), 4),
                "median_latency_ms": round(float(np.median(hnsw_lats)), 4),
                "qps": round(1000.0 / float(np.mean(hnsw_lats)), 2),
            })

        return results
