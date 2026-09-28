"""Perceptual hashing (pHash, dHash) based near-duplicate detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import imagehash
import numpy as np
from PIL import Image
import yaml


@dataclass
class NearDuplicateGroup:
    """Cluster of near-duplicate images within distance threshold."""

    near_duplicate_group_id: str
    image_ids: List[str]
    representative_image_id: str
    max_pairwise_distance: int
    mean_pairwise_distance: float


class NearDuplicateDetector:
    """Detects visually near-identical images using pHash and dHash perceptual fingerprints."""

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        max_hamming_distance: int = 10,
        hash_size: int = 16,
    ) -> None:
        self.max_distance = max_hamming_distance
        self.hash_size = hash_size

        if config_path:
            p = Path(config_path)
            if p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "near_deduplication" in cfg:
                        sub = cfg["near_deduplication"]
                        self.max_distance = sub.get("max_hamming_distance", self.max_distance)
                        self.hash_size = sub.get("hash_size", self.hash_size)

    def compute_hashes(self, image_path: str | Path) -> Dict[str, Any]:
        """Compute perceptual hashes (pHash and dHash) for a given image."""
        p = Path(image_path)
        with Image.open(p) as img:
            # Convert to grayscale 8-bit for hashing
            gray_img = img.convert("L")
            phash_val = imagehash.phash(gray_img, hash_size=self.hash_size)
            dhash_val = imagehash.dhash(gray_img, hash_size=self.hash_size)

        return {
            "phash": str(phash_val),
            "dhash": str(dhash_val),
            "phash_obj": phash_val,
            "dhash_obj": dhash_val,
        }

    def cluster_near_duplicates(
        self,
        image_records: List[Dict[str, Any]],
        id_key: str = "image_id",
        path_key: str = "file_path",
    ) -> Tuple[Dict[str, Optional[str]], List[NearDuplicateGroup]]:
        """Compute hashes across image records and group clusters within Hamming distance threshold.

        Returns:
            mapping: Dict[image_id -> near_duplicate_group_id or None]
            groups: List[NearDuplicateGroup]
        """
        # Precompute hashes
        items: List[Dict[str, Any]] = []
        for rec in image_records:
            img_id = rec[id_key]
            fpath = rec.get(path_key)
            if not fpath or not Path(fpath).exists():
                continue
            try:
                hashes = self.compute_hashes(fpath)
                items.append({
                    "image_id": img_id,
                    "phash": hashes["phash_obj"],
                    "dhash": hashes["dhash_obj"],
                })
            except Exception:
                continue

        n = len(items)
        if n <= 1:
            mapping = {r[id_key]: None for r in image_records}
            return mapping, []

        # Build adjacency graph where distance <= max_distance
        adj: Dict[int, Set[int]] = {i: set() for i in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                # Combined distance: average of phash and dhash Hamming distance
                dist_p = items[i]["phash"] - items[j]["phash"]
                dist_d = items[i]["dhash"] - items[j]["dhash"]
                combined_dist = (dist_p + dist_d) // 2

                if combined_dist <= self.max_distance:
                    adj[i].add(j)
                    adj[j].add(i)

        # Connected components BFS
        visited: Set[int] = set()
        groups: List[NearDuplicateGroup] = []
        mapping: Dict[str, Optional[str]] = {r[id_key]: None for r in image_records}
        group_idx = 1

        for i in range(n):
            if i not in visited:
                component = []
                queue = [i]
                visited.add(i)
                while queue:
                    curr = queue.pop(0)
                    component.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(component) > 1:
                    group_id = f"near_dup_{group_idx:04d}"
                    group_idx += 1
                    member_ids = [items[idx]["image_id"] for idx in component]

                    # Compute pairwise distances within cluster
                    distances = []
                    for idx_a in component:
                        for idx_b in component:
                            if idx_a < idx_b:
                                d = ((items[idx_a]["phash"] - items[idx_b]["phash"])
                                     + (items[idx_a]["dhash"] - items[idx_b]["dhash"])) // 2
                                distances.append(d)

                    max_d = max(distances) if distances else 0
                    mean_d = float(np.mean(distances)) if distances else 0.0

                    groups.append(NearDuplicateGroup(
                        near_duplicate_group_id=group_id,
                        image_ids=member_ids,
                        representative_image_id=member_ids[0],
                        max_pairwise_distance=max_d,
                        mean_pairwise_distance=round(mean_d, 2),
                    ))

                    for mid in member_ids:
                        mapping[mid] = group_id

        return mapping, groups
