"""
Track A: Redundancy Graph and Disambiguation.

Builds an undirected redundancy graph from duplicate / near-duplicate pairs:
- Extracts connected components (redundancy clusters).
- Chooses canonical representative image per cluster based on highest image quality/sharpness.
- Assigns actionable recommendations: KEEP, REVIEW, POSSIBLE REDUNDANCY.
"""

from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np


class RedundancyGraph:
    """
    Constructs and analyzes the redundancy graph over micrographs.
    """

    def __init__(self, all_image_ids: List[str]):
        self.all_image_ids = list(all_image_ids)
        self.adj: Dict[str, Set[str]] = {img_id: set() for img_id in self.all_image_ids}
        self.edge_metadata: Dict[Tuple[str, str], dict] = {}

    def add_relationship(
        self,
        img_id_1: str,
        img_id_2: str,
        match_type: str,
        metadata: Optional[dict] = None,
    ):
        """Add an edge between two duplicate or near-duplicate micrographs."""
        if img_id_1 not in self.adj:
            self.adj[img_id_1] = set()
        if img_id_2 not in self.adj:
            self.adj[img_id_2] = set()

        self.adj[img_id_1].add(img_id_2)
        self.adj[img_id_2].add(img_id_1)

        key = tuple(sorted([img_id_1, img_id_2]))
        meta = metadata or {}
        meta["match_type"] = match_type
        self.edge_metadata[key] = meta

    def get_connected_components(self) -> List[List[str]]:
        """Extract all connected components (clusters) using breadth-first search."""
        visited: Set[str] = set()
        components: List[List[str]] = []

        for node in sorted(self.all_image_ids):
            if node not in visited:
                comp = []
                queue = [node]
                visited.add(node)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in sorted(self.adj.get(curr, set())):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(sorted(comp))

        return components

    def build_summary(
        self,
        quality_scores: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """
        Generate dataframe with redundancy cluster ID, representative flag, and action recommendation.

        Parameters
        ----------
        quality_scores : Optional dict mapping image_id -> quality/sharpness metric (higher is better).

        Returns
        -------
        pd.DataFrame with columns:
        [image_id, cluster_id, cluster_size, is_representative, redundancy_action, quality_score]
        """
        components = self.get_connected_components()
        records = []

        for cluster_idx, comp in enumerate(components):
            c_size = len(comp)
            cluster_id = f"CLUSTER_{cluster_idx:04d}"

            if c_size == 1:
                img_id = comp[0]
                q_score = quality_scores.get(img_id, 0.0) if quality_scores else 0.0
                records.append({
                    "image_id": img_id,
                    "cluster_id": cluster_id,
                    "cluster_size": 1,
                    "is_representative": True,
                    "redundancy_action": "KEEP",
                    "quality_score": q_score,
                })
            else:
                # Rank members by quality score
                scored_members = []
                for img_id in comp:
                    q_score = quality_scores.get(img_id, 0.0) if quality_scores else 0.0
                    scored_members.append((img_id, q_score))

                # Sort descending by quality score, break ties by image_id for determinism
                scored_members.sort(key=lambda x: (x[1], x[0]), reverse=True)
                rep_id = scored_members[0][0]

                for rank, (img_id, q_score) in enumerate(scored_members):
                    is_rep = (img_id == rep_id)
                    if is_rep:
                        action = "KEEP"
                    else:
                        # Check relation to representative or other members
                        action = "POSSIBLE REDUNDANCY"
                        # If edge with representative is near duplicate rather than exact, mark REVIEW
                        key = tuple(sorted([img_id, rep_id]))
                        if key in self.edge_metadata:
                            m_type = self.edge_metadata[key].get("match_type")
                            if m_type == "NEAR_DUPLICATE":
                                action = "REVIEW"

                    records.append({
                        "image_id": img_id,
                        "cluster_id": cluster_id,
                        "cluster_size": c_size,
                        "is_representative": is_rep,
                        "redundancy_action": action,
                        "quality_score": q_score,
                    })

        df = pd.DataFrame(records)
        return df.sort_values(by=["cluster_id", "is_representative", "image_id"], ascending=[True, False, True]).reset_index(drop=True)
