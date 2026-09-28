# Figure 11: System Throughput and Latency Under Concurrency Stress

**Caption**: Throughput (peak 67.61 req/s) and p95 latency under concurrency scaling from 10 to 250 simulated client threads.

**Figure Type**: Throughput Scaling

```mermaid
xychart-beta
    title "Serving Throughput (req/s) vs Client Concurrency"
    x-axis ["10 Clients", "50 Clients", "100 Clients", "250 Clients"]
    y-axis "Requests per Second" 0.0 --> 80.0
    bar [34.2, 52.8, 64.1, 67.61]
```
