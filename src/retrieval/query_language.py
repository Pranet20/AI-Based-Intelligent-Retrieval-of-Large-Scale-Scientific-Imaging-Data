"""Scientific Query Language & Explainable Retrieval Engine.

Combines structured physical metadata constraints with dense vector retrieval.
Produces grounded retrieval evidence explaining candidate ranking
without claiming unsupported pixel-level causality.
"""

from dataclasses import asdict, dataclass
import re
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class StructuredQueryResult:
    image_id: int
    rank: int
    visual_similarity: float
    filter_matches: Dict[str, bool]
    quality_status: str
    composite_quality_risk: float
    novelty_indicator: float
    acquisition_info: Dict[str, Any]
    retrieval_evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScientificQueryParser:
    """Parses domain-specific structured metadata expressions."""

    @classmethod
    def parse_expression(cls, query_str: str) -> Dict[str, Any]:
        """Parses clauses like: 'voltage >= 10 AND detector == BSE AND quality_risk < 0.5'."""
        filters: Dict[str, Any] = {}
        if not query_str:
            return filters

        clauses = re.split(r"\s+AND\s+", query_str.strip(), flags=re.IGNORECASE)
        for clause in clauses:
            clause = clause.strip()
            # Operators: ==, <=, >=, <, >, =
            m = re.match(r"^([a-zA-Z_]+)\s*(==|<=|>=|<|>|=)\s*(.+)$", clause)
            if not m:
                continue
            field, op, val = m.group(1).lower(), m.group(2), m.group(3).strip().strip("'\"")
            try:
                num_val = float(val)
            except ValueError:
                num_val = val

            filters[field] = {"operator": "==" if op == "=" else op, "value": num_val}
        return filters


class ScientificSearchExecutor:
    """Executes hybrid structured filtering and dense vector retrieval."""

    @classmethod
    def matches_filters(cls, metadata: Dict[str, Any], filters: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
        """Evaluates whether metadata satisfies all parsed structured clauses."""
        match_details: Dict[str, bool] = {}
        all_passed = True

        for field, rule in filters.items():
            op = rule["operator"]
            target_val = rule["value"]
            actual_val = metadata.get(field)

            if actual_val is None:
                match_details[field] = False
                all_passed = False
                continue

            passed = False
            if op in ("==", "="):
                passed = str(actual_val).upper() == str(target_val).upper()
            elif op == "<":
                passed = float(actual_val) < float(target_val)
            elif op == "<=":
                passed = float(actual_val) <= float(target_val)
            elif op == ">":
                passed = float(actual_val) > float(target_val)
            elif op == ">=":
                passed = float(actual_val) >= float(target_val)

            match_details[field] = passed
            if not passed:
                all_passed = False

        return all_passed, match_details

    @classmethod
    def format_retrieval_evidence(
        cls,
        image_id: int,
        rank: int,
        visual_sim: float,
        metadata: Dict[str, Any],
        filter_matches: Dict[str, bool],
        quality_risk: float,
        novelty_score: float,
    ) -> StructuredQueryResult:
        """Constructs an explainable result record grounded in empirical retrieval evidence."""
        det = metadata.get("detector", "Unspecified")
        kv = metadata.get("accelerating_voltage_kv", "Unspecified")
        mag = metadata.get("magnification", "Unspecified")
        q_label = "NOMINAL" if quality_risk < 0.5 else "RISK_FLAGGED"

        evidence = (
            f"Rank #{rank}: Visual Cosine={visual_sim:.4f}. "
            f"Instrument Profile: {det} at {kv} kV, Mag={mag}x. "
            f"Quality: {q_label} (Risk={quality_risk:.3f}). Novelty Score={novelty_score:.3f}. "
            f"Constraint Satisfaction: {sum(filter_matches.values())}/{len(filter_matches)} clauses matched."
        )

        return StructuredQueryResult(
            image_id=image_id,
            rank=rank,
            visual_similarity=round(visual_sim, 4),
            filter_matches=filter_matches,
            quality_status=q_label,
            composite_quality_risk=round(quality_risk, 3),
            novelty_indicator=round(novelty_score, 3),
            acquisition_info={
                "detector": det,
                "accelerating_voltage_kv": kv,
                "magnification": mag,
            },
            retrieval_evidence=evidence,
        )
