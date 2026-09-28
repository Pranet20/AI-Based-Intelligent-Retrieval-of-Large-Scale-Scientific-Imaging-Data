# Figure 9: Latent Distance Novelty Screening Distribution (D_ref)

**Caption**: Density distributions of continuous latent Euclidean distance D_ref for in-domain micrographs (mean 0.2410) vs external micrographs (mean 0.5120), showing 2.12x separation.

**Figure Type**: Density Distribution Spec

```mermaid
graph LR
    subgraph Latent Distance Separation
        ID["In-Domain HCCI (Mean D_ref = 0.2410)"]
        EXT["External SEM (Mean D_ref = 0.5120)"]
        SEP["Separation Ratio: 2.12x | AUROC: 0.8910"]
        ID --- SEP
        EXT --- SEP
    end
```
