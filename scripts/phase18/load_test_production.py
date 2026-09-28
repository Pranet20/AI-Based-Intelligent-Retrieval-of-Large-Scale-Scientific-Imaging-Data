"""Phase 18 Production Load Testing Suite.

Executes synthetic engineering workloads up to 250 requests across multiple concurrency tiers:
- Concurrency 1 (Baseline Sequential)
- Concurrency 10 (Moderate Load)
- Concurrency 25 (High Concurrent Workload)
- Concurrency 50 (Stress Burst Workload)

IMPORTANT NOTE:
This is SYNTHETIC ENGINEERING BENCHMARKING to evaluate server responsiveness,
thread pool behavior, and latency under load.
It is NOT scientific validation of machine learning retrieval models.

Saves benchmark results to:
reports/phase18/PHASE18_DEPLOYMENT_EVIDENCE/load_test_metrics.json
"""

import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from fastapi.testclient import TestClient
from app.main import app


def run_workload_tier(client: TestClient, concurrency: int, total_requests: int) -> Dict[str, Any]:
    latencies: List[float] = []
    status_codes: Dict[int, int] = {}
    errors: int = 0
    endpoints = ["/api/v1/health", "/api/v1/version", "/"]

    def worker_request(req_idx: int):
        nonlocal errors
        ep = endpoints[req_idx % len(endpoints)]
        t0 = time.perf_counter()
        try:
            resp = client.get(ep)
            t1 = time.perf_counter()
            code = resp.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
            if code not in (200, 429):
                errors += 1
            return (t1 - t0) * 1000.0  # milliseconds
        except Exception:
            errors += 1
            return None

    t_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker_request, i) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res is not None:
                latencies.append(res)

    t_elapsed = time.perf_counter() - t_start
    throughput = len(latencies) / t_elapsed if t_elapsed > 0 else 0.0
    lat_arr = np.array(latencies) if latencies else np.array([0.0])

    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "completed_requests": len(latencies),
        "failed_requests": errors,
        "error_rate_pct": float(round((errors / total_requests) * 100.0, 2)) if total_requests > 0 else 0.0,
        "elapsed_seconds": round(t_elapsed, 4),
        "throughput_req_per_sec": round(throughput, 2),
        "latency_ms": {
            "mean": round(float(np.mean(lat_arr)), 2),
            "p50": round(float(np.percentile(lat_arr, 50)), 2),
            "p90": round(float(np.percentile(lat_arr, 90)), 2),
            "p95": round(float(np.percentile(lat_arr, 95)), 2),
            "p99": round(float(np.percentile(lat_arr, 99)), 2),
            "min": round(float(np.min(lat_arr)), 2),
            "max": round(float(np.max(lat_arr)), 2)
        },
        "status_code_distribution": status_codes
    }


def main():
    print("====================================================================")
    print("PHASE 18 — PRODUCTION LOAD TESTING (UP TO 250 REQUESTS)")
    print("====================================================================")
    print("NOTE: SYNTHETIC WORKLOAD FOR SYSTEM RESPONSIVENESS (NOT SCIENTIFIC VALIDATION)")

    evidence_dir = PROJECT_ROOT / "reports" / "phase18" / "PHASE18_DEPLOYMENT_EVIDENCE"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    client = TestClient(app)

    # Warm-up request
    _ = client.get("/api/v1/health")

    tiers = [
        {"concurrency": 1, "requests": 50, "label": "Baseline Sequential"},
        {"concurrency": 10, "requests": 100, "label": "Moderate Concurrency"},
        {"concurrency": 25, "requests": 200, "label": "High Concurrency"},
        {"concurrency": 50, "requests": 250, "label": "Peak Stress Load (250 reqs)"}
    ]

    tier_results = []
    for tier in tiers:
        print(f"Running {tier['label']} ({tier['concurrency']} workers, {tier['requests']} requests)...")
        res = run_workload_tier(client, tier["concurrency"], tier["requests"])
        res["label"] = tier["label"]
        tier_results.append(res)
        print(f"  Throughput: {res['throughput_req_per_sec']} req/s | Mean Latency: {res['latency_ms']['mean']} ms | p95: {res['latency_ms']['p95']} ms | Errors: {res['failed_requests']}")

    summary = {
        "experiment_id": "P18-LOAD-01",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "workload_type": "Synthetic Engineering API Load Test",
        "scientific_validation": False,
        "max_requests_tested": 250,
        "target_endpoints": ["/api/v1/health", "/api/v1/version", "/"],
        "tiers": tier_results,
        "pass_criteria": {
            "p95_latency_under_50ms": all(t["latency_ms"]["p95"] < 50.0 for t in tier_results),
            "zero_unhandled_errors": sum(t["failed_requests"] for t in tier_results) == 0,
            "sustainable_concurrency_50": tier_results[-1]["completed_requests"] == 250
        }
    }

    out_file = evidence_dir / "load_test_metrics.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[SUCCESS] Production load test completed. Metrics recorded to: {out_file}")


if __name__ == "__main__":
    main()
