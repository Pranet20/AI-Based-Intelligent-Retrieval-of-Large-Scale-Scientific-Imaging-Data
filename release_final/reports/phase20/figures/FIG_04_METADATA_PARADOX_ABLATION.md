# Figure 4: The Metadata Paradox — Impact of Multimodal Fusion on Retrieval Precision

**Caption**: Visualization showing the drop in MRR when fusing unnormalized instrument metadata into visual representations versus decoupled filtering.

**Figure Type**: Data Specification

```mermaid
xychart-beta
    title "MRR Under Multimodal Fusion vs Decoupled Architecture"
    x-axis ["Visual Alone", "Metadata Alone", "Gated MLP", "Cross-Attention", "Decoupled Filter"]
    y-axis "Mean Reciprocal Rank (MRR)" 0.0 --> 1.0
    bar [0.9658, 0.3443, 0.5896, 0.6132, 0.9658]
```
