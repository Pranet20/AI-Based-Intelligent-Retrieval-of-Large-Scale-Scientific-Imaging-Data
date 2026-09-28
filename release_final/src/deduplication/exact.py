"""SHA-256 based exact duplicate detection and cluster reporting."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DuplicateAuditStats:
    """Exact duplicate detection statistics."""

    total_files: int
    unique_files: int
    duplicate_files: int
    duplicate_groups_count: int
    largest_duplicate_groups: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files": self.total_files,
            "unique_files": self.unique_files,
            "duplicate_files": self.duplicate_files,
            "duplicate_groups_count": self.duplicate_groups_count,
            "largest_duplicate_groups": self.largest_duplicate_groups,
        }


class ExactDuplicateDetector:
    """Identifies exact byte-for-byte identical images using SHA-256 hashes."""

    @staticmethod
    def identify_duplicates(
        records: List[Dict[str, Any]],
        hash_key: str = "sha256",
        id_key: str = "image_id",
    ) -> Tuple[Dict[str, Optional[str]], DuplicateAuditStats]:
        """Group records by hash and assign duplicate_group_id.

        Returns:
            mapping: Dict[image_id -> duplicate_group_id (or None if unique)]
            stats: DuplicateAuditStats
        """
        hash_to_ids: Dict[str, List[str]] = defaultdict(list)
        for rec in records:
            img_id = rec[id_key]
            sha = rec.get(hash_key)
            if sha:
                hash_to_ids[sha].append(img_id)

        mapping: Dict[str, Optional[str]] = {}
        dup_groups: List[Dict[str, Any]] = []
        group_idx = 1
        duplicate_files_count = 0

        for sha, ids in hash_to_ids.items():
            if len(ids) > 1:
                group_id = f"exact_dup_{group_idx:04d}"
                group_idx += 1
                duplicate_files_count += len(ids)
                dup_groups.append({
                    "duplicate_group_id": group_id,
                    "sha256": sha,
                    "count": len(ids),
                    "image_ids": ids,
                })
                for iid in ids:
                    mapping[iid] = group_id
            else:
                mapping[ids[0]] = None

        dup_groups.sort(key=lambda g: g["count"], reverse=True)
        total_files = len(records)
        unique_hashes = len(hash_to_ids)

        stats = DuplicateAuditStats(
            total_files=total_files,
            unique_files=unique_hashes,
            duplicate_files=duplicate_files_count,
            duplicate_groups_count=len(dup_groups),
            largest_duplicate_groups=dup_groups[:10],
        )

        return mapping, stats
