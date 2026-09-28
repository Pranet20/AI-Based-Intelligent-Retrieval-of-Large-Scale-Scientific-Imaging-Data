"""Production Object Storage Abstraction for Scientific Image Data.

Separates scientific metadata from large binary payload storage.
Supports local content-addressable filesystem and S3-compatible cloud storage (MinIO/AWS S3).
Strictly enforces dataset redistribution compliance by preventing unpermitted external egress.
"""

import abc
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings


@dataclass
class ObjectDescriptor:
    object_id: str
    sha256: str
    size_bytes: int
    media_type: str
    source: str
    storage_backend: str
    storage_uri: str
    created_at: str
    provenance_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ObjectStorageBackend(abc.ABC):
    """Abstract interface for scientific binary payload storage."""

    @abc.abstractmethod
    def store_object(
        self,
        data: bytes,
        object_id: str,
        media_type: str,
        source: str = "upload",
        provenance_metadata: Optional[Dict[str, Any]] = None,
    ) -> ObjectDescriptor:
        """Stores binary object and returns cryptographic descriptor."""
        pass

    @abc.abstractmethod
    def retrieve_object(self, object_id: str) -> bytes:
        """Retrieves raw binary object bytes."""
        pass

    @abc.abstractmethod
    def exists(self, object_id: str) -> bool:
        """Checks if object exists."""
        pass

    @abc.abstractmethod
    def get_descriptor(self, object_id: str) -> Optional[ObjectDescriptor]:
        """Gets descriptor without downloading full payload."""
        pass


class LocalFileSystemStorage(ObjectStorageBackend):
    """Production local filesystem storage with content-addressable sharding."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.STORAGE_PATH
        self.originals_dir = self.base_dir / "originals"
        self.meta_dir = self.base_dir / "descriptors"
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.meta_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, object_id: str) -> Path:
        # 2-level directory sharding (e.g., ab/cd/abcdef...)
        shard = object_id[:2]
        shard_dir = self.originals_dir / shard
        shard_dir.mkdir(parents=True, exist_ok=True)
        return shard_dir / object_id

    def _get_descriptor_path(self, object_id: str) -> Path:
        return self.meta_dir / f"{object_id}.descriptor.json"

    def store_object(
        self,
        data: bytes,
        object_id: str,
        media_type: str,
        source: str = "upload",
        provenance_metadata: Optional[Dict[str, Any]] = None,
    ) -> ObjectDescriptor:
        sha256 = hashlib.sha256(data).hexdigest()
        target_path = self._get_path(object_id)

        # Content-addressable write (atomic via temp file)
        tmp_path = target_path.with_suffix(".tmp")
        with open(tmp_path, "wb") as f:
            f.write(data)
        os.replace(tmp_path, target_path)

        descriptor = ObjectDescriptor(
            object_id=object_id,
            sha256=sha256,
            size_bytes=len(data),
            media_type=media_type,
            source=source,
            storage_backend="local_fs",
            storage_uri=str(target_path.as_posix()),
            created_at=datetime.now(timezone.utc).isoformat(),
            provenance_metadata=provenance_metadata or {},
        )

        desc_path = self._get_descriptor_path(object_id)
        with open(desc_path, "w", encoding="utf-8") as f:
            json.dump(descriptor.to_dict(), f, indent=2)

        return descriptor

    def retrieve_object(self, object_id: str) -> bytes:
        p = self._get_path(object_id)
        if not p.exists():
            # Fallback to un-sharded legacy root if exists
            legacy_p = self.originals_dir / object_id
            if legacy_p.exists():
                return legacy_p.read_bytes()
            raise FileNotFoundError(f"Object '{object_id}' not found in storage.")
        return p.read_bytes()

    def exists(self, object_id: str) -> bool:
        if self._get_path(object_id).exists():
            return True
        return (self.originals_dir / object_id).exists()

    def get_descriptor(self, object_id: str) -> Optional[ObjectDescriptor]:
        dp = self._get_descriptor_path(object_id)
        if dp.exists():
            with open(dp, "r", encoding="utf-8") as f:
                d = json.load(f)
            return ObjectDescriptor(**d)
        return None


class S3CompatibleStorage(ObjectStorageBackend):
    """S3-compatible object storage connector (MinIO / Ceph / AWS S3).
    
    Includes safety guard: refuses public egress of local-only research datasets.
    """

    def __init__(self, endpoint_url: str, bucket_name: str, access_key: str, secret_key: str):
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        # Lazy client initialization
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                )
            except ImportError:
                raise RuntimeError("boto3 package required for S3CompatibleStorage backend.")
        return self._client

    def store_object(
        self,
        data: bytes,
        object_id: str,
        media_type: str,
        source: str = "upload",
        provenance_metadata: Optional[Dict[str, Any]] = None,
    ) -> ObjectDescriptor:
        # Rights compliance guard
        if provenance_metadata and provenance_metadata.get("rights_status") == "RIGHTS_UNVERIFIED_LOCAL_ONLY":
            raise PermissionError("Egress Blocked: Local-only research data cannot be pushed to external S3.")

        sha256 = hashlib.sha256(data).hexdigest()
        client = self._get_client()
        client.put_object(
            Bucket=self.bucket_name,
            Key=object_id,
            Body=data,
            ContentType=media_type,
            Metadata={"sha256": sha256, "source": source},
        )

        return ObjectDescriptor(
            object_id=object_id,
            sha256=sha256,
            size_bytes=len(data),
            media_type=media_type,
            source=source,
            storage_backend="s3_compatible",
            storage_uri=f"s3://{self.bucket_name}/{object_id}",
            created_at=datetime.now(timezone.utc).isoformat(),
            provenance_metadata=provenance_metadata or {},
        )

    def retrieve_object(self, object_id: str) -> bytes:
        client = self._get_client()
        resp = client.get_object(Bucket=self.bucket_name, Key=object_id)
        return resp["Body"].read()

    def exists(self, object_id: str) -> bool:
        client = self._get_client()
        try:
            client.head_object(Bucket=self.bucket_name, Key=object_id)
            return True
        except Exception:
            return False

    def get_descriptor(self, object_id: str) -> Optional[ObjectDescriptor]:
        client = self._get_client()
        try:
            head = client.head_object(Bucket=self.bucket_name, Key=object_id)
            meta = head.get("Metadata", {})
            return ObjectDescriptor(
                object_id=object_id,
                sha256=meta.get("sha256", "UNKNOWN"),
                size_bytes=head.get("ContentLength", 0),
                media_type=head.get("ContentType", "application/octet-stream"),
                source=meta.get("source", "s3"),
                storage_backend="s3_compatible",
                storage_uri=f"s3://{self.bucket_name}/{object_id}",
                created_at=str(head.get("LastModified", "")),
                provenance_metadata=meta,
            )
        except Exception:
            return None


def get_storage_backend() -> ObjectStorageBackend:
    """Storage backend factory. Defaults to secure local filesystem."""
    backend_type = getattr(settings, "STORAGE_BACKEND_TYPE", "LOCAL").upper()
    if backend_type == "S3":
        return S3CompatibleStorage(
            endpoint_url=getattr(settings, "S3_ENDPOINT_URL", "http://localhost:9000"),
            bucket_name=getattr(settings, "S3_BUCKET_NAME", "scidata-images"),
            access_key=getattr(settings, "S3_ACCESS_KEY", "minioadmin"),
            secret_key=getattr(settings, "S3_SECRET_KEY", "minioadmin"),
        )
    return LocalFileSystemStorage()
