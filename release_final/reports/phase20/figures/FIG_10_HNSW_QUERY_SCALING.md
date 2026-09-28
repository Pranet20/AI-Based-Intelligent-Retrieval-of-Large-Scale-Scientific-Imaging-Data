# Figure 10: FAISS HNSW Query Latency Scaling Under Vector Expansion

**Caption**: Sub-millisecond query latency progression (0.096 ms to 0.317 ms) across 5,000 to 100,000 indexed feature vectors.

**Figure Type**: Latency Curve

```mermaid
xychart-beta
    title "FAISS HNSW p50 Query Latency (ms)"
    x-axis ["5k Vectors", "10k Vectors", "50k Vectors", "100k Vectors"]
    y-axis "Latency (ms)" 0.0 --> 0.4
    line [0.096, 0.118, 0.214, 0.317]
```
