"""FAISS-based scalable vector retrieval package for scientific microscopy representations."""

from src.retrieval.faiss_index import FAISSVectorIndex, IndexType

__all__ = ["FAISSVectorIndex", "IndexType"]
