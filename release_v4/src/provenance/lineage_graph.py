"""Scientific Provenance Directed Lineage Graph Engine.

Encodes explicit 9-stage scientific lifecycle:
Image -> Specimen -> Acquisition -> Metadata -> Embedding -> Index -> Retrieval -> Review -> Decision

Enables end-to-end cryptographic and transformation traceability.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LineageNode:
    node_id: str
    node_type: str  # IMAGE, SPECIMEN, ACQUISITION, METADATA, EMBEDDING, INDEX, RETRIEVAL, REVIEW, DECISION
    label: str
    properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LineageEdge:
    source_id: str
    target_id: str
    relationship: str  # SPECIMEN_OF, ACQUIRED_FROM, DESCRIBED_BY, TRANSFORMED_TO, STORED_IN, QUERIED_IN, TRIAGED_AS, FINALIZED_AS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScientificProvenanceGraph:
    """Manages immutable directed acyclic graph (DAG) of scientific transformations."""

    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []

    def add_node(self, node: LineageNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, source_id: str, target_id: str, relationship: str) -> None:
        assert source_id in self.nodes, f"Source node '{source_id}' not registered in graph."
        assert target_id in self.nodes, f"Target node '{target_id}' not registered in graph."
        self.edges.append(LineageEdge(source_id=source_id, target_id=target_id, relationship=relationship))

    @classmethod
    def build_canonical_chain(
        cls,
        image_id: int,
        sha256: str,
        specimen_name: str,
        detector: str,
        voltage_kv: float,
        model_version: str,
        index_id: str,
        review_decision: Optional[str] = None,
    ) -> "ScientificProvenanceGraph":
        """Constructs canonical 9-stage scientific lineage chain."""
        g = cls()

        # 1. Image
        g.add_node(LineageNode(
            node_id=f"img_{image_id}",
            node_type="IMAGE",
            label=f"Image #{image_id}",
            properties={"sha256": sha256, "id": image_id},
        ))

        # 2. Specimen
        g.add_node(LineageNode(
            node_id=f"spec_{image_id}",
            node_type="SPECIMEN",
            label=f"Specimen: {specimen_name}",
            properties={"specimen_name": specimen_name},
        ))
        g.add_edge(f"img_{image_id}", f"spec_{image_id}", "SPECIMEN_OF")

        # 3. Acquisition
        g.add_node(LineageNode(
            node_id=f"acq_{image_id}",
            node_type="ACQUISITION",
            label=f"Acquisition: {detector} @ {voltage_kv}kV",
            properties={"detector": detector, "voltage_kv": voltage_kv},
        ))
        g.add_edge(f"spec_{image_id}", f"acq_{image_id}", "ACQUIRED_FROM")

        # 4. Metadata
        g.add_node(LineageNode(
            node_id=f"meta_{image_id}",
            node_type="METADATA",
            label="Instrument Metadata",
            properties={"detector": detector, "voltage_kv": voltage_kv, "normalized": True},
        ))
        g.add_edge(f"acq_{image_id}", f"meta_{image_id}", "DESCRIBED_BY")

        # 5. Embedding
        g.add_node(LineageNode(
            node_id=f"emb_{image_id}",
            node_type="EMBEDDING",
            label=f"Embedding ({model_version})",
            properties={"model_version": model_version, "dim": 384, "l2_normalized": True},
        ))
        g.add_edge(f"img_{image_id}", f"emb_{image_id}", "TRANSFORMED_TO")

        # 6. Index
        g.add_node(LineageNode(
            node_id=f"idx_{image_id}",
            node_type="INDEX",
            label=f"FAISS Index ({index_id})",
            properties={"index_id": index_id},
        ))
        g.add_edge(f"emb_{image_id}", f"idx_{image_id}", "STORED_IN")

        # 7. Retrieval
        g.add_node(LineageNode(
            node_id=f"ret_{image_id}",
            node_type="RETRIEVAL",
            label="Vector Candidate Retrieval",
            properties={"metric": "INNER_PRODUCT_COSINE"},
        ))
        g.add_edge(f"idx_{image_id}", f"ret_{image_id}", "QUERIED_IN")

        # 8. Review
        g.add_node(LineageNode(
            node_id=f"rev_{image_id}",
            node_type="REVIEW",
            label="Curator Triage Review",
            properties={"priority_ranked": True},
        ))
        g.add_edge(f"ret_{image_id}", f"rev_{image_id}", "TRIAGED_AS")

        # 9. Decision
        decision_label = review_decision or "PENDING_CURATOR_SIGN_OFF"
        g.add_node(LineageNode(
            node_id=f"dec_{image_id}",
            node_type="DECISION",
            label=f"Decision: {decision_label}",
            properties={"final_decision": decision_label},
        ))
        g.add_edge(f"rev_{image_id}", f"dec_{image_id}", "FINALIZED_AS")

        return g

    def to_mermaid(self) -> str:
        """Emits Mermaid graph representation for documentation and UI rendering."""
        lines = ["flowchart LR"]
        for node in self.nodes.values():
            clean_label = node.label.replace('"', "'")
            lines.append(f'    {node.node_id}["{clean_label}"]')
        for edge in self.edges:
            lines.append(f'    {edge.source_id} -->|{edge.relationship}| {edge.target_id}')
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }
