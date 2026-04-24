"""LSH (Locality-Sensitive Hashing) for fast vector search.

Pure Python implementation - no external dependencies required.
For better performance, install FAISS: pip install faiss-cpu
"""

import numpy as np
from typing import List, Tuple, Dict, Any
import hashlib


class SimpleLSH:
    """Simple LSH implementation using random projections."""

    def __init__(self, dims: int = 10000, n_tables: int = 10, n_bits: int = 16):
        """
        Initialize LSH index.

        Args:
            dims: Vector dimensionality
            n_tables: Number of hash tables (more = better accuracy, slower)
            n_bits: Bits per hash (more = finer buckets)
        """
        self.dims = dims
        self.n_tables = n_tables
        self.n_bits = n_bits

        # Create random projection matrices for each table
        np.random.seed(42)
        self.projections = [
            np.random.randn(dims, n_bits) for _ in range(n_tables)
        ]

        # Hash tables: {hash_value: [indices]}
        self.tables = [{} for _ in range(n_tables)]

        # Store vectors and metadata
        self.vectors = []
        self.metadata = []

    def _hash_vector(self, vector: np.ndarray, table_idx: int) -> str:
        """Hash a vector using random projection."""
        # Project vector
        projection = np.dot(vector, self.projections[table_idx])

        # Binarize (>0 = 1, <=0 = 0)
        binary = (projection > 0).astype(int)

        # Convert to string hash
        hash_str = ''.join(map(str, binary))
        return hash_str

    def add(self, vector: np.ndarray, metadata: Dict[str, Any]) -> None:
        """Add vector to index."""
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        # Store vector and metadata
        idx = len(self.vectors)
        self.vectors.append(vector)
        self.metadata.append(metadata)

        # Add to all hash tables
        for table_idx in range(self.n_tables):
            hash_val = self._hash_vector(vector, table_idx)
            if hash_val not in self.tables[table_idx]:
                self.tables[table_idx][hash_val] = []
            self.tables[table_idx][hash_val].append(idx)

    def query(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[Dict, float]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            top_k: Number of results to return

        Returns:
            List of (metadata, similarity) tuples
        """
        # Normalize query
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        # Collect candidate indices from all tables
        candidates = set()
        for table_idx in range(self.n_tables):
            hash_val = self._hash_vector(query_vector, table_idx)
            if hash_val in self.tables[table_idx]:
                candidates.update(self.tables[table_idx][hash_val])

        # If no candidates, fall back to linear search
        if not candidates:
            candidates = set(range(len(self.vectors)))

        # Compute similarities for candidates
        results = []
        for idx in candidates:
            similarity = np.dot(query_vector, self.vectors[idx])
            results.append((self.metadata[idx], float(similarity)))

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        total_buckets = sum(len(table) for table in self.tables)
        avg_bucket_size = np.mean([
            len(bucket)
            for table in self.tables
            for bucket in table.values()
        ]) if total_buckets > 0 else 0

        return {
            "num_vectors": len(self.vectors),
            "num_tables": self.n_tables,
            "total_buckets": total_buckets,
            "avg_bucket_size": avg_bucket_size,
            "dims": self.dims
        }


class FAISSLSHWrapper:
    """Wrapper for FAISS LSH (if available)."""

    def __init__(self, dims: int = 10000, n_bits: int = 256):
        """Initialize FAISS LSH index."""
        try:
            import faiss
            self.faiss = faiss
            self.index = faiss.IndexLSH(dims, n_bits)
            self.metadata = []
            self.use_faiss = True
        except ImportError:
            print("⚠ FAISS not available, falling back to SimpleLSH")
            self.simple_lsh = SimpleLSH(dims=dims, n_tables=10, n_bits=16)
            self.use_faiss = False

    def add(self, vector: np.ndarray, metadata: Dict[str, Any]) -> None:
        """Add vector to index."""
        if self.use_faiss:
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            # Add to FAISS
            self.index.add(vector.reshape(1, -1).astype('float32'))
            self.metadata.append(metadata)
        else:
            self.simple_lsh.add(vector, metadata)

    def query(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[Dict, float]]:
        """Search for similar vectors."""
        if self.use_faiss:
            # Normalize
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector = query_vector / norm

            # Search
            distances, indices = self.index.search(
                query_vector.reshape(1, -1).astype('float32'),
                top_k
            )

            # Return results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    similarity = 1.0 - distances[0][i]
                    results.append((self.metadata[idx], float(similarity)))
            return results
        else:
            return self.simple_lsh.query(query_vector, top_k)

    def stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if self.use_faiss:
            return {
                "num_vectors": len(self.metadata),
                "backend": "FAISS",
                "index_type": "LSH"
            }
        else:
            return self.simple_lsh.stats()


# Default to FAISS wrapper (falls back to SimpleLSH if FAISS not available)
LSHIndex = FAISSLSHWrapper
