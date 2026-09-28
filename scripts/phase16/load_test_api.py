"""Synthetic Engineering Load Testing Suite for SciData Platform API.

Evaluates API performance under concurrent workloads (10, 25, 50, 100 concurrent workers).
Measures latency (mean, p50, p95, p99), throughput (req/s), and error rates.

NOTE: This is SYNTHETIC ENGINEERING LOAD TESTING, NOT SCIENTIFIC VALIDATION.
"""

import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from fastapi.testclient import TestClient
from app.main import app


def run_concurrency_tier(client: TestClient, concurrency: int, total_requests: int) -> Dict[str, Any]:
    latencies: List[float] = []
    errors: int = 0
    endpoints = ["/api/v1/health", "/api/v1/version", "/"]

    def make_request(idx: int):
        nonlocal errors
        ep = endpoints[idx % len(endpoints)]
        t0 = time.perf_counter()
        try:
            resp = client.get(ep)
            t1 = time.perf_counter()
            if resp.status_code not in (200, 429):
                errors += 1
            return (t1 - t0) * 1000.0  # ms
        except Exception:
            errors += 1
            return None

    start_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request, i) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            lat = f.result()
            if lat is not None:
                latencies.append(lat)

    elapsed_wall = time.perf_counter() - start_wall
    throughput = len(latencies) / elapsed_wall if elapsed_wall > 0 else 0.0

    lat_arr = np.array(latencies) if latencies else np.array([0.0])
    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successful_requests": len(latencies),
        "failed_requests": errors,
        "error_rate_pct": float((errors / total_requests) * 100.0) if total_requests > 0 else 0.0,
        "elapsed_seconds": round(elapsed_wall, 3),
        "throughput_req_per_sec": round(throughput, 1),
        "mean_latency_ms": round(float(np.mean(lat_arr)), 2),
        "p50_latency_ms": round(float(np.percentile(lat_arr, 50)), 2),
        "p95_latency_ms": round(float(np.percentile(lat_arr, 95)), 2),
        "p99_latency_ms": round(float(np.percentile(lat_arr, 99)), 2),
    }


def main():
    print("=" * 65)
    print("SCIDATA PLATFORM — SYNTHETIC LOAD TESTING SUITE")
    print("Evaluation: 10, 25, 50, 100 Concurrent Synthetic Workloads")
    print("=" * 65)

    out_dir = PROJECT_ROOT / "reports" / "phase16"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    tiers = [
        (10, 50),
        (25, 100),
        (50, 150),
        (100, 200),
    ]

    with TestClient(app) as client:
        # Warmup
        _ = client.get("/api/v1/health")

        for concurrency, req_count in tiers:
            print(f"\n[Testing Tier] Concurrency: {concurrency} workers | Total Requests: {req_count}...")
            tier_res = run_concurrency_tier(client, concurrency, req_count)
            results[f"concurrency_{concurrency}"] = tier_res
            print(f"  Throughput: {tier_res['throughput_req_per_sec']} req/s | Mean Latency: {tier_res['mean_latency_ms']} ms | P95: {tier_res['p95_latency_ms']} ms | Errors: {tier_res['failed_requests']}")

    out_json = out_dir / "load_test_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Synthetic load test results written to: {out_json}")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
