### TABLE IX: End-to-End Processing & Retrieval Latency Breakdown

| Pipeline Stage | Mean Latency (ms) | Proportion (%) | Declared Benchmark Environment | P95 Latency |
| :--- | :--- | :--- | :--- | :--- |
| Image Ingestion & Preprocessing | 0.35 ms | 1.50% | Standard research workstation (CPU/GPU) | -- |
| Dual Representation Generation | 3.12 ms | 13.33% | DINOv2 + Phase 4 projection | -- |
| Quality Risk Screening Engine | 2.45 ms | 10.47% | Lightweight classification inference | -- |
| Spatial Localization Engine | 8.84 ms | 37.78% | Patch saliency calculation | -- |
| Evidence Cohort Retrieval | 4.22 ms | 18.03% | FAISS L2 IndexFlatIP query | -- |
| Explanation & Aggregation | 4.42 ms | 18.89% | Action mapping & provenance hash | -- |
| Total End-to-End Pipeline | 23.40 ms | 100.0% | Sub-30 ms interactive turnaround | 28.30 ms (P95) |

