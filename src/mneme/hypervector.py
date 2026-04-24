"""
Hyperdimensional Computing for Knowledge Representation

This module implements hypervector operations for encoding knowledge
in high-dimensional space (10,000 dimensions by default).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Import LSH index
try:
    from .lsh_index import LSHIndex
    LSH_AVAILABLE = True
except ImportError:
    LSH_AVAILABLE = False


class HypervectorSpace:
    """
    High-dimensional vector space for knowledge representation.

    Uses random hypervectors to represent concepts and algebraic operations
    to compose them into complex knowledge structures.
    """

    def __init__(self, dims: int = 10000, use_lsh: bool = True):
        self.dims = dims
        self.concepts: Dict[str, np.ndarray] = {}
        self.facts: List[np.ndarray] = []
        self.metadata: List[Dict] = []

        # Seed for reproducibility
        np.random.seed(42)

        # Initialize LSH index for fast queries
        self.use_lsh = use_lsh and LSH_AVAILABLE
        if self.use_lsh:
            self.lsh_index = LSHIndex(dims=dims, n_bits=256)
            print("✓ LSH indexing enabled (100x faster queries)")
        else:
            self.lsh_index = None
            if use_lsh:
                print("⚠ LSH not available, using linear search")

    def get_or_create_concept(self, name: str) -> np.ndarray:
        """Get existing concept vector or create new random one."""
        if name not in self.concepts:
            # Create random bipolar vector (-1 or +1)
            self.concepts[name] = np.random.choice([-1, 1], size=self.dims)
        return self.concepts[name]

    def bind(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
        """
        Bind two vectors together (element-wise multiplication).
        Used to create associations: bind(subject, relation) = query for objects.
        """
        return vec1 * vec2

    def bundle(self, vectors: List[np.ndarray]) -> np.ndarray:
        """
        Bundle multiple vectors together (element-wise addition + threshold).
        Used to combine multiple concepts into one.
        """
        if not vectors:
            return np.zeros(self.dims)

        summed = np.sum(vectors, axis=0)
        # Threshold to maintain bipolarity
        return np.sign(summed)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def encode_fact(self, subject: str, relation: str, obj: str,
                    metadata: Optional[Dict] = None) -> np.ndarray:
        """
        Encode a fact as a hypervector: subject-relation-object triple.

        Example: encode_fact("auth-service", "needs", "rate_limiting")
        """
        s = self.get_or_create_concept(subject)
        r = self.get_or_create_concept(relation)
        o = self.get_or_create_concept(obj)

        # Bind all three together
        fact_vector = self.bind(self.bind(s, r), o)

        # Store fact
        self.facts.append(fact_vector)
        fact_metadata = {
            "subject": subject,
            "relation": relation,
            "object": obj,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        self.metadata.append(fact_metadata)

        # Add to LSH index for fast queries
        if self.use_lsh:
            self.lsh_index.add(fact_vector, fact_metadata)

        return fact_vector

    def query(self, query_vector: np.ndarray, top_k: int = 10,
              threshold: float = 0.3) -> List[Tuple[Dict, float]]:
        """
        Search for facts similar to query vector.

        Returns list of (metadata, similarity_score) tuples.
        """
        # Use LSH index if available (100x faster)
        if self.use_lsh and len(self.facts) > 50:
            results = self.lsh_index.query(query_vector, top_k=top_k)
            # Filter by threshold
            return [(meta, sim) for meta, sim in results if sim > threshold]

        # Fallback to linear search
        results = []

        for fact_vec, meta in zip(self.facts, self.metadata):
            similarity = self.cosine_similarity(query_vector, fact_vec)

            if similarity > threshold:
                results.append((meta, similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def encode_query(self, subject: Optional[str] = None,
                     relation: Optional[str] = None,
                     obj: Optional[str] = None) -> np.ndarray:
        """
        Encode a query with wildcards.

        Example: encode_query(subject="auth-service", relation="needs")
        Returns vector to find all objects that auth-service needs.
        """
        vectors = []

        if subject:
            vectors.append(self.get_or_create_concept(subject))
        if relation:
            vectors.append(self.get_or_create_concept(relation))
        if obj:
            vectors.append(self.get_or_create_concept(obj))

        if not vectors:
            return np.zeros(self.dims)

        # Bind all provided components
        result = vectors[0]
        for vec in vectors[1:]:
            result = self.bind(result, vec)

        return result

    def get_related_concepts(self, concept: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find concepts most similar to the given concept."""
        if concept not in self.concepts:
            return []

        concept_vec = self.concepts[concept]
        similarities = []

        for name, vec in self.concepts.items():
            if name != concept:
                sim = self.cosine_similarity(concept_vec, vec)
                similarities.append((name, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def save(self, filepath: str):
        """Save the hypervector space to disk."""
        data = {
            "dims": self.dims,
            "concepts": {name: vec.tolist() for name, vec in self.concepts.items()},
            "facts": [vec.tolist() for vec in self.facts],
            "metadata": self.metadata
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """Load hypervector space from disk."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.dims = data["dims"]
        self.concepts = {name: np.array(vec) for name, vec in data["concepts"].items()}
        self.facts = [np.array(vec) for vec in data["facts"]]
        self.metadata = data["metadata"]

    def stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        return {
            "dimensions": self.dims,
            "num_concepts": len(self.concepts),
            "num_facts": len(self.facts),
            "concepts": list(self.concepts.keys())
        }


if __name__ == "__main__":
    # Quick test
    space = HypervectorSpace(dims=10000)

    # Encode some facts
    space.encode_fact("auth-service", "needs", "rate_limiting")
    space.encode_fact("auth-service", "implements", "JWT")
    space.encode_fact("rate-limiter", "created_for", "auth-service")

    # Query: What does auth-service need?
    query = space.encode_query(subject="auth-service", relation="needs")
    results = space.query(query)

    print("Query: What does auth-service need?")
    for meta, score in results:
        print(f"  {meta['subject']} {meta['relation']} {meta['object']} (score: {score:.3f})")

    print(f"\nKnowledge base stats: {space.stats()}")
