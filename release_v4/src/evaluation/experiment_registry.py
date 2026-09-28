"""Unified Experiment Registry for Phase 7.

Validates and loads experiment definitions from configs/phase7_experiments.yaml,
providing full traceability from reported numbers to experimental conditions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class ExperimentEntry:
    experiment_id: str
    research_question: str
    dataset: str
    split: str
    model_configuration: str
    features: str
    training_data: str
    validation_data: str
    test_data: str
    threshold_source: str
    hyperparameters: Dict[str, Any]
    random_seeds: List[int]
    evaluation_metrics: List[str]
    artifact_paths: Dict[str, str]
    leakage_controls: str
    evidence_type: str


class ExperimentRegistry:
    """Manages Phase 7 unified experiment specifications."""

    def __init__(self, config_path: str | Path = "configs/phase7_experiments.yaml") -> None:
        self.config_path = Path(config_path)
        self.experiments: Dict[str, ExperimentEntry] = {}
        self.load()

    def load(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f).get("experiments", {})

        for exp_id, data in raw.items():
            self.experiments[exp_id] = ExperimentEntry(**data)

    def get(self, exp_id: str) -> ExperimentEntry:
        if exp_id not in self.experiments:
            raise KeyError(f"Experiment ID '{exp_id}' not found in registry.")
        return self.experiments[exp_id]

    def list_all(self) -> List[ExperimentEntry]:
        return list(self.experiments.values())

    def filter_by_rq(self, rq: str) -> List[ExperimentEntry]:
        return [e for e in self.experiments.values() if rq in e.research_question]

    def export_json(self, output_path: str | Path = "artifacts/phase7/experiment_registry.json") -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        data = {k: asdict(v) for k, v in self.experiments.items()}
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out


if __name__ == "__main__":
    reg = ExperimentRegistry()
    out = reg.export_json()
    print(f"Experiment registry exported to {out} with {len(reg.experiments)} experiments.")
