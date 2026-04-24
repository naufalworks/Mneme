# Implementation Plan: Advanced Optimizations

**Target:** M4 Mac  
**Keep:** 10K dimensions (accuracy > memory)  
**Focus:** Speed + Features

---

## Phase 1: LSH Indexing (Weekend Project)

**Goal:** 100x query speedup  
**Time:** 2-3 hours  
**Difficulty:** Medium

### What You'll Build
```python
# Before: O(n) - checks every fact
query_time = 0.18ms × num_facts

# After: O(log n) - checks only similar bucket
query_time = 0.002ms (constant!)
```

### Implementation Steps

**Step 1: Install Dependencies**
```bash
pip install scikit-learn faiss-cpu
# For M4 GPU acceleration (optional):
pip install faiss-gpu
```

**Step 2: Create LSH Module**
```python
# src/lsh_index.py
import numpy as np
import faiss

class LSHIndex:
    """Locality-Sensitive Hashing for fast vector search."""
    
    def __init__(self, dims=10000, n_bits=256):
        self.dims = dims
        self.n_bits = n_bits
        
        # Create FAISS LSH index
        self.index = faiss.IndexLSH(dims, n_bits)
        self.fact_metadata = []
        
    def add_fact(self, fact_vector, metadata):
        """Add fact to index."""
        # Normalize vector
        norm = np.linalg.norm(fact_vector)
        if norm > 0:
            fact_vector = fact_vector / norm
            
        # Add to FAISS index
        self.index.add(fact_vector.reshape(1, -1).astype('float32'))
        self.fact_metadata.append(metadata)
        
    def query(self, query_vector, top_k=10):
        """Search for similar facts."""
        # Normalize query
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
            
        # Search index
        distances, indices = self.index.search(
            query_vector.reshape(1, -1).astype('float32'), 
            top_k
        )
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.fact_metadata):
                results.append((
                    self.fact_metadata[idx],
                    1.0 - distances[0][i]  # Convert distance to similarity
                ))
        return results
```

**Step 3: Integrate with Hypervector Space**
```python
# Edit hypervector.py
from src.lsh_index import LSHIndex

class HypervectorSpace:
    def __init__(self, dims=10000, use_lsh=True):
        self.dims = dims
        self.concepts = {}
        self.facts = []
        self.metadata = []
        
        # Add LSH index
        self.use_lsh = use_lsh
        if use_lsh:
            self.lsh_index = LSHIndex(dims=dims)
    
    def encode_fact(self, subject, relation, obj, metadata=None):
        # ... existing code ...
        
        # Add to LSH index
        if self.use_lsh:
            self.lsh_index.add_fact(fact_vector, {
                "subject": subject,
                "relation": relation,
                "object": obj,
                **(metadata or {})
            })
        
        return fact_vector
    
    def query(self, query_vector, top_k=10, threshold=0.3):
        if self.use_lsh:
            # Use LSH (fast!)
            return self.lsh_index.query(query_vector, top_k)
        else:
            # Fallback to linear search
            # ... existing code ...
```

**Step 4: Test**
```python
# test_lsh.py
import time
from src import init_knowledge_system

knowledge = init_knowledge_system()

# Add 1000 facts
for i in range(1000):
    knowledge.track_project_creation(
        f"service-{i}",
        f"Service {i}",
        technologies=["Python"]
    )

# Benchmark
start = time.time()
result = knowledge.why_does_exist("service-500")
print(f"Query time: {(time.time() - start)*1000:.2f}ms")
# Expected: <5ms (vs 500ms without LSH)
```

**Expected Results:**
- 1000 facts: 500ms → 5ms (100x speedup)
- 10,000 facts: 5s → 50ms (100x speedup)
- Accuracy: 95%+ (configurable)

---

## Phase 2: M4 Neural Engine (Next Weekend)

**Goal:** Hardware-accelerated vector operations  
**Time:** 4-6 hours  
**Difficulty:** Hard

### What You'll Build
```python
# Use M4's 16-core Neural Engine (38 TOPS)
# 100x speedup for batch operations
```

### Implementation Steps

**Step 1: Install CoreML Tools**
```bash
pip install coremltools torch
```

**Step 2: Create Neural Engine Module**
```python
# src/neural_engine.py
import coremltools as ct
import torch
import torch.nn as nn
import numpy as np

class NeuralEngineAccelerator:
    """Use M4 Neural Engine for vector operations."""
    
    def __init__(self, dims=10000):
        self.dims = dims
        self.model = self._create_model()
        
    def _create_model(self):
        """Create CoreML model for cosine similarity."""
        
        class CosineSimilarity(nn.Module):
            def forward(self, vec1, vec2):
                # Batch cosine similarity
                dot = torch.sum(vec1 * vec2, dim=1)
                norm1 = torch.norm(vec1, dim=1)
                norm2 = torch.norm(vec2, dim=1)
                return dot / (norm1 * norm2)
        
        model = CosineSimilarity()
        
        # Trace model
        example_input = (
            torch.randn(100, self.dims),  # Batch of 100 vectors
            torch.randn(100, self.dims)
        )
        traced = torch.jit.trace(model, example_input)
        
        # Convert to CoreML (runs on Neural Engine)
        coreml_model = ct.convert(
            traced,
            inputs=[
                ct.TensorType(name="vec1", shape=(100, self.dims)),
                ct.TensorType(name="vec2", shape=(100, self.dims))
            ],
            compute_units=ct.ComputeUnit.ALL  # Use Neural Engine + GPU
        )
        
        return coreml_model
    
    def batch_similarity(self, query_vec, all_vecs):
        """Compute similarity with all vectors (on Neural Engine)."""
        # Prepare batch
        batch_size = len(all_vecs)
        query_batch = np.tile(query_vec, (batch_size, 1))
        
        # Run on Neural Engine
        result = self.model.predict({
            'vec1': query_batch.astype('float32'),
            'vec2': np.array(all_vecs).astype('float32')
        })
        
        return result['output']
```

**Step 3: Integrate**
```python
# Edit hypervector.py
from src.neural_engine import NeuralEngineAccelerator

class HypervectorSpace:
    def __init__(self, dims=10000, use_neural_engine=True):
        self.dims = dims
        # ... existing code ...
        
        # Add Neural Engine
        if use_neural_engine:
            try:
                self.neural_engine = NeuralEngineAccelerator(dims)
                print("✓ M4 Neural Engine enabled")
            except:
                self.neural_engine = None
                print("⚠ Neural Engine not available, using CPU")
    
    def query(self, query_vector, top_k=10):
        if self.neural_engine and len(self.facts) > 100:
            # Use Neural Engine for batch operations
            similarities = self.neural_engine.batch_similarity(
                query_vector, 
                self.facts
            )
            # ... process results ...
        else:
            # Fallback to CPU
            # ... existing code ...
```

**Expected Results:**
- Batch query (1000 facts): 500ms → 5ms (100x speedup)
- Single query: 0.18ms → 0.05ms (3.6x speedup)
- Power efficiency: 10x better (Neural Engine uses less power)

---

## Phase 3: Temporal Facts (Week 2)

**Goal:** Track knowledge evolution over time  
**Time:** 1 day  
**Difficulty:** Medium

### Implementation

**Step 1: Create Temporal Module**
```python
# src/temporal.py
from datetime import datetime
from typing import Optional

class TemporalFact:
    def __init__(self, subject, relation, obj, 
                 valid_from=None, valid_until=None):
        self.subject = subject
        self.relation = relation
        self.object = obj
        self.valid_from = valid_from or datetime.min
        self.valid_until = valid_until or datetime.max
        
    def is_valid_at(self, timestamp):
        return self.valid_from <= timestamp <= self.valid_until

class TemporalKnowledgeSystem:
    def __init__(self, base_system):
        self.base_system = base_system
        self.temporal_facts = []
        
    def add_temporal_fact(self, subject, relation, obj, 
                         valid_from=None, valid_until=None):
        fact = TemporalFact(subject, relation, obj, valid_from, valid_until)
        self.temporal_facts.append(fact)
        
        # Also add to base system if currently valid
        if fact.is_valid_at(datetime.now()):
            self.base_system.add_fact(subject, relation, obj)
    
    def query_at_time(self, timestamp, subject=None):
        results = []
        for fact in self.temporal_facts:
            if fact.is_valid_at(timestamp):
                if subject is None or fact.subject == subject:
                    results.append(fact)
        return results
    
    def query_history(self, subject):
        """Get all facts about subject across time."""
        history = []
        for fact in self.temporal_facts:
            if fact.subject == subject:
                history.append({
                    'relation': fact.relation,
                    'object': fact.object,
                    'valid_from': fact.valid_from,
                    'valid_until': fact.valid_until
                })
        return history
```

**Step 2: Integrate**
```python
# src/integration.py
from .temporal import TemporalKnowledgeSystem

class KnowledgeIntegration:
    def __init__(self, workspace_path=None):
        # ... existing code ...
        self.temporal = TemporalKnowledgeSystem(self.system)
    
    def track_project_creation_temporal(self, project_name, reason,
                                       valid_from=None, valid_until=None):
        """Track project with time validity."""
        self.temporal.add_temporal_fact(
            project_name, "exists", "true",
            valid_from, valid_until
        )
        # ... rest of tracking ...
```

**Usage:**
```python
# Track that we used MongoDB from Jan-Mar 2024
knowledge.temporal.add_temporal_fact(
    "auth-service", "uses", "mongodb",
    valid_from=datetime(2024, 1, 1),
    valid_until=datetime(2024, 3, 1)
)

# Query: What did we use in February?
facts = knowledge.temporal.query_at_time(datetime(2024, 2, 15))
# Returns: mongodb

# Query: When did we switch?
history = knowledge.temporal.query_history("auth-service")
# Returns full timeline
```

---

## Phase 4: Explainable AI (Week 3)

**Goal:** Show reasoning for every answer  
**Time:** 1 day  
**Difficulty:** Easy

### Implementation

```python
# src/explainable.py
class ExplainableQuery:
    def __init__(self, system):
        self.system = system
        self.trace = []
        
    def why_does_exist_explained(self, project_name):
        self.trace = []
        
        # Step 1: Search
        self.trace.append(f"Searching for '{project_name}'")
        query_vec = self.system.hypervector_space.get_or_create_concept(project_name)
        
        # Step 2: Find facts
        facts = self.system.hypervector_space.query(query_vec, top_k=5)
        self.trace.append(f"Found {len(facts)} related facts")
        
        # Step 3: Analyze
        created_for = None
        for fact, similarity in facts:
            if fact['relation'] == 'created_for':
                created_for = fact['object']
                self.trace.append(
                    f"Found: {project_name} created_for {created_for} "
                    f"(confidence: {similarity:.2%})"
                )
        
        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(facts)
        
        return {
            "answer": f"Created for {created_for}" if created_for else "Unknown",
            "reasoning": self.trace,
            "confidence": confidence,
            "sources": ["hypervector_space", "agent_network"]
        }
```

---

## Phase 5: Causal Inference (Week 4)

**Goal:** Automatically discover WHY  
**Time:** 2 days  
**Difficulty:** Hard

### Implementation

```python
# src/causal_inference.py
class CausalInferenceEngine:
    def __init__(self):
        self.events = []  # (timestamp, type, project, metadata)
        
    def record_event(self, event_type, project, metadata=None):
        self.events.append((time.time(), event_type, project, metadata))
        
    def infer_causality(self, project):
        creation_time = self._get_creation_time(project)
        prior_events = [e for e in self.events if e[0] < creation_time]
        
        causes = []
        
        # Pattern 1: Temporal proximity (within 1 hour)
        recent = [e for e in prior_events if creation_time - e[0] < 3600]
        
        # Pattern 2: Semantic similarity
        for event in recent:
            if self._are_related(project, event[2]):
                causes.append(f"{event[2]} triggered {project}")
        
        return causes
```

---

## Phase 6: Federated Sync (Week 5-6)

**Goal:** Team collaboration  
**Time:** 1 week  
**Difficulty:** Hard

### Implementation

```python
# src/federated.py
class FederatedKnowledge:
    def __init__(self, team_id):
        self.team_id = team_id
        self.facts = {}
        self.vector_clock = {}
        
    def sync_with_peer(self, peer_url):
        # Fetch peer's facts
        peer_facts = requests.get(f"{peer_url}/facts").json()
        
        # Merge using CRDT
        self.merge(peer_facts)
```

---

## Timeline Summary

```
Week 1 (Weekend 1):
├─ LSH Indexing (2-3 hours) ✓ 100x speedup
└─ Testing & benchmarking (1 hour)

Week 2 (Weekend 2):
├─ M4 Neural Engine (4-6 hours) ✓ 100x speedup
└─ Testing & benchmarking (2 hours)

Week 3:
├─ Temporal Facts (1 day)
└─ Explainable AI (1 day)

Week 4:
└─ Causal Inference (2 days)

Week 5-6:
└─ Federated Sync (1 week)
```

---

## Priority Order

**Must Have (Do First):**
1. ✅ LSH Indexing - Biggest impact, easiest to implement
2. ✅ M4 Neural Engine - Hardware acceleration

**Should Have (Do Next):**
3. Explainable AI - Better debugging
4. Temporal Facts - Track evolution

**Nice to Have (Do Later):**
5. Causal Inference - Automatic discovery
6. Federated Sync - Team collaboration

---

## Expected Performance After All Optimizations

```
Metric                  Before      After       Improvement
──────────────────────────────────────────────────────────
Query (100 facts)       5ms         0.05ms      100x
Query (1000 facts)      50ms        0.5ms       100x
Query (10K facts)       500ms       5ms         100x
Batch query (1000)      500ms       5ms         100x
Memory usage            800MB       800MB       Same
Accuracy                99.2%       95%+        Slight loss
Power efficiency        Baseline    10x better  M4 Neural Engine
```

---

## Next Steps

**This Weekend:**
1. Implement LSH indexing (2-3 hours)
2. Test with 1000+ facts
3. Benchmark before/after

**Want me to start implementing LSH now?**
