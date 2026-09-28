"""Automated Machine-Readable Scientific Experiment Report Generator.

Generates objective, structured experiment reports:
- Dataset specification and count breakdown
- Evaluation protocol and split definition
- Empirical metrics with confidence intervals where available
- Explicit declared limitations
- Exact reproduction command
- Zero promotional or hyperbolic conclusions
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.evaluation.experiment_registry_v2 import ExperimentRecordV2, ExperimentRegistryV2


class ScientificReportGenerator:
    """Produces standardized machine-readable experiment reports."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("reports/experiments")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, record: ExperimentRecordV2) -> Path:
        """Generates machine-readable JSON and companion markdown for an experiment."""
        exp_id = record.experiment_id

        report_data = {
            "experiment_id": exp_id,
            "hypothesis": record.hypothesis,
            "dataset": record.dataset,
            "evaluation_protocol": {
                "split": record.split,
                "random_seed": record.seed,
                "model_architecture": record.model,
                "hyperparameters": record.parameters,
            },
            "empirical_metrics": record.metrics,
            "reproducibility": {
                "artifact_path": record.artifact,
                "execution_environment": record.environment,
                "reproduction_command": f"python scripts/reproduce/final_validate_project.py --experiment {exp_id}",
            },
            "scientific_status": record.status,
            "limitations": [
                f"Scoped strictly to conditions evaluated in {record.dataset}.",
                "Evaluation performed under frozen seeds; variance reflects documented split.",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 1. Machine-readable JSON
        json_file = self.output_dir / f"{exp_id}_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        # 2. Markdown Companion
        md_file = self.output_dir / f"{exp_id}_report.md"
        metrics_md = "\n".join([f"- **{k}:** `{v}`" for k, v in record.metrics.items()])

        md_content = f"""# Scientific Experiment Report: {exp_id}

**Status:** `{record.status}`  
**Dataset:** {record.dataset}  
**Model:** {record.model}  
**Seed:** {record.seed}  

---

### 1. Hypothesis & Objective
> {record.hypothesis}

---

### 2. Empirical Benchmark Metrics
{metrics_md}

---

### 3. Protocol & Execution Environment
- **Split:** `{record.split}`
- **Parameters:** `{record.parameters}`
- **Environment:** `{record.environment}`
- **Artifact:** [`{record.artifact}`](file:///{record.artifact})

---

### 4. Reproduction Command
```bash
{report_data['reproducibility']['reproduction_command']}
```

---

### 5. Declared Scope & Limitations
- Scoped strictly to the physical and synthetic parameters of {record.dataset}.
- Results reflect frozen evaluation checkpoints and deterministic seeds.
"""
        md_file.write_text(md_content, encoding="utf-8")
        return json_file

    def generate_all_canonical_reports(self) -> List[Path]:
        registry = ExperimentRegistryV2()
        generated = []
        for exp in registry.list_all():
            p = self.generate_report(exp)
            generated.append(p)
        return generated
