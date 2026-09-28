### Table 9: Vector Search Query Latency and Scaling (FAISS HNSW, M=16, efSearch=128)

| Index Size (Vectors) | Indexing Time (s) | Memory Footprint (MB) | p50 Latency (ms) | p99 Latency (ms) | Recall@10 vs Flat L2 |
| --- | --- | --- | --- | --- | --- |
| 5,000 | 0.14 s | 9.2 MB | 0.096 ms | 0.142 ms | 100.0% |
| 10,000 | 0.31 s | 18.4 MB | 0.118 ms | 0.185 ms | 100.0% |
| 50,000 | 1.82 s | 91.8 MB | 0.214 ms | 0.328 ms | 100.0% |
| 100,000 | 3.95 s | 183.5 MB | 0.317 ms | 0.482 ms | 100.0% |
