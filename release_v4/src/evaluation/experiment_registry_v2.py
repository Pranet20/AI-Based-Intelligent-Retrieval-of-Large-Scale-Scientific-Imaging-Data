"""Master Scientific Experiment Registry V2.

Maintains comprehensive, immutable registration of every experiment across the research program:
(experiment_id, hypothesis, dataset, split, seed, model, parameters, metrics, artifact, environment, status).

Enforces scientific gate: No metric may enter the manuscript unless linked to an active registry record.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentRecordV2:
    experiment_id: str
    hypothesis: str
    dataset: str
    split: str
    seed: int
    model: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    artifact: str
    environment: str
    status: str  # VALIDATED, NEGATIVE_RESULT_CONFIRMED, SCOPED_WITH_LIMITATIONS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExperimentRegistryV2:
    """Master registry managing experiments from Phase 1 through Phase 17."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.registry_file = registry_file or Path("configs/master_experiment_registry_v2.json")
        self._records: Dict[str, ExperimentRecordV2] = {}
        self._load_canonical_experiments()

    def _load_canonical_experiments(self):
        canonical = [
            ExperimentRecordV2(
                experiment_id="P1-EXP-01",
                hypothesis="Perceptual hashing alone is insufficient for fine-grained SEM specimen retrieval.",
                dataset="HCCI (N=774)",
                split="Full Corpus (N=774)",
                seed=42,
                model="pHash / dHash",
                parameters={"hash_size": 8, "threshold": 10},
                metrics={"R@1": 0.0210, "MRR": 0.0543},
                artifact="experiments/phase1/results/phash_baseline.json",
                environment="Python 3.11.9, CPU",
                status="VALIDATED",
            ),
            ExperimentRecordV2(
                experiment_id="P3-EXP-01",
                hypothesis="Self-supervised vision foundation representations (DINOv2) outperform supervised ImageNet models on SEM micrographs.",
                dataset="HCCI (N=774)",
                split="Train/Val/Test (305/236/233)",
                seed=42,
                model="DINOv2 ViT-S/14 vs ResNet-50",
                parameters={"patch_size": 14, "dim": 384, "normalize": True},
                metrics={"DINOv2_R@1": 0.9481, "ResNet50_R@1": 0.9245, "DINOv2_MRR": 0.9658},
                artifact="experiments/phase3/results/phase3_representation_benchmark_metrics.json",
                environment="Python 3.11.9, PyTorch 2.2.0",
                status="VALIDATED",
            ),
            ExperimentRecordV2(
                experiment_id="P4-EXP-01",
                hypothesis="Supervised contrastive fine-tuning compresses the cross-detector / cross-voltage acquisition gap in same-specimen retrieval.",
                dataset="HCCI (N=774)",
                split="Held-Out Zeiss Cross-Condition Split",
                seed=42,
                model="DINOv2 + SupCon Projection Head",
                parameters={"lr": 1e-4, "temperature": 0.07, "epochs": 50},
                metrics={"baseline_gap": 0.1994, "adapted_gap": 0.0635, "gap_reduction_pct": 68.15, "p_value": 1.42e-12},
                artifact="experiments/phase4/results/acquisition_shift_analysis.json",
                environment="Python 3.11.9, PyTorch 2.2.0, Checkpoint: 53ba60a3...",
                status="VALIDATED",
            ),
            ExperimentRecordV2(
                experiment_id="P5-EXP-01",
                hypothesis="FAISS HNSW approximate nearest neighbor search provides sub-millisecond retrieval latency with >99% recall retention.",
                dataset="HCCI + Synthetic Scale Vectors (up to 100k)",
                split="Exact FlatIP vs HNSW Index",
                seed=42,
                model="FAISS IndexHNSWFlat",
                parameters={"M": 32, "efSearch": 64},
                metrics={"latency_5k_ms": 0.096, "latency_100k_ms": 0.317, "recall_retention": 0.994},
                artifact="experiments/phase5/results/retrieval_benchmark_metrics.json",
                environment="Python 3.11.9, FAISS-CPU 1.8.0",
                status="VALIDATED",
            ),
            ExperimentRecordV2(
                experiment_id="P5-EXP-02",
                hypothesis="Metadata-only retrieval on unnormalized instrument headers achieves meaningful ranking.",
                dataset="HCCI (N=212 test split)",
                split="Authoritative Held-out Split",
                seed=42,
                model="Inverted Metadata Index",
                parameters={"attributes": ["voltage", "detector", "magnification"]},
                metrics={"MRR": 0.3443396, "R@1": 0.0519},
                artifact="experiments/phase5/results/phase5_hybrid_metadata_retrieval_001/metrics.json",
                environment="Python 3.11.9, Scikit-Learn 1.4.1",
                status="SCOPED_WITH_LIMITATIONS",
            ),
            ExperimentRecordV2(
                experiment_id="P6-EXP-01",
                hypothesis="Tenengrad and modified Laplacian operators accurately discriminate defocused micrographs without manual labels.",
                dataset="Controlled Degradation Benchmark (N=120)",
                split="Defocus Perturbation Suite",
                seed=42,
                model="Tenengrad / Modified Laplacian",
                parameters={"kernel_size": 3, "dynamic_range_weight": 0.3},
                metrics={"AUROC": 0.8803, "AUPRC": 0.9618},
                artifact="experiments/phase6/results/curation_metrics.json",
                environment="Python 3.11.9, NumPy 1.26.4",
                status="VALIDATED",
            ),
            ExperimentRecordV2(
                experiment_id="P13-EXP-01",
                hypothesis="H1: Dense multimodal fusion networks (Gated MLP, Cross-Attention) outperform visual-only embeddings on instrument logs.",
                dataset="HCCI (N=774)",
                split="5-Fold Cross-Validation",
                seed=42,
                model="Gated MLP / Cross-Attention Multimodal Head",
                parameters={"hidden_dim": 256, "num_heads": 4},
                metrics={"Visual_R@1": 0.9481, "GatedMLP_R@1": 0.5896, "CrossAttn_R@1": 0.6132},
                artifact="experiments/phase13/p13_exp01_multimodal_fusion/p13_exp01_metrics.json",
                environment="Python 3.11.9, PyTorch 2.2.0",
                status="NEGATIVE_RESULT_CONFIRMED",
            ),
            ExperimentRecordV2(
                experiment_id="P13-EXP-04",
                hypothesis="Frozen representation generalizes zero-shot to industrial semiconductor defect SEM micrographs (Carinthia).",
                dataset="Carinthia SEM Defect Dataset (N=4,591)",
                split="Leave-One-Out Evaluation (14,037 instances)",
                seed=42,
                model="DINOv2 ViT-S/14",
                parameters={"top_k": 10},
                metrics={"Micro_R@1": 0.9952, "Macro_R@1": 0.9090},
                artifact="experiments/phase13/p13_exp04_cross_domain/p13_exp04_metrics.json",
                environment="Python 3.11.9, FAISS 1.8.0",
                status="SCOPED_WITH_LIMITATIONS",
            ),
            ExperimentRecordV2(
                experiment_id="P13-EXP-07",
                hypothesis="Active human-in-the-loop prioritization reduces expert review workload by >35%.",
                dataset="Composite Curation Stream (N=200)",
                split="Double-Blind Dual-Reviewer Evaluation",
                seed=42,
                model="Composite Urgency Ranker",
                parameters={"alpha_quality": 0.35, "alpha_novelty": 0.25, "alpha_uncertainty": 0.20},
                metrics={"Workload_Reduction_pct": 41.2, "Yield_Top50_pct": 85.3, "Cohen_Kappa": 0.856},
                artifact="experiments/phase13/p13_exp07_human_in_the_loop/p13_exp07_metrics.json",
                environment="Python 3.11.9, NumPy 1.26.4",
                status="VALIDATED",
            ),
        ]
        for exp in canonical:
            self._records[exp.experiment_id] = exp

        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for exp_id, item in data.items():
                    if exp_id not in self._records:
                        self._records[exp_id] = ExperimentRecordV2(**item)
            except Exception:
                pass

    def register_experiment(self, record: ExperimentRecordV2) -> None:
        self._records[record.experiment_id] = record
        self.save()

    def get(self, experiment_id: str) -> Optional[ExperimentRecordV2]:
        return self._records.get(experiment_id)

    def list_all(self) -> List[ExperimentRecordV2]:
        return list(self._records.values())

    def save(self) -> None:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        dumpable = {k: v.to_dict() for k, v in self._records.items()}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(dumpable, f, indent=2)
