# MNEME AUDIT - ACTION PLAN

**Date:** 2026-04-24  
**Status:** 🔴 6 CRITICAL + 6 HIGH + 14 MEDIUM issues found  
**Recommendation:** Fix critical issues before any production use

---

## 📊 ISSUE BREAKDOWN

```
CRITICAL (6):  ████████████████████████ 24%
HIGH (6):      ████████████████████████ 24%  
MEDIUM (14):   ████████████████████████████████████████████████████ 52%
───────────────────────────────────────────────────────────────────
TOTAL: 26 issues
```

---

## 🚨 CRITICAL PATH (Must Fix First)

### Phase 1: Core Functionality (Days 1-2)

**Issue #1: Broken Hypervector Queries** ⚠️ BLOCKS EVERYTHING
- **File:** `src/mneme/hypervector.py:143-169`
- **Problem:** Query encoding doesn't match fact encoding
- **Fix:** Change query encoding to match triple-bind structure
- **Effort:** 2 hours
- **Impact:** Enables actual hypervector queries

```python
# Current (WRONG):
def encode_query(self, subject, relation):
    query_vec = self.bind(s_vec, r_vec)  # Double bind

# Fix:
def encode_query(self, subject, relation, obj=None):
    if obj:
        query_vec = self.bind(self.bind(s_vec, r_vec), o_vec)  # Triple bind
    else:
        # Implement proper unbinding or use wildcard
        query_vec = self.bind(s_vec, r_vec)
```

**Issue #2: Data Corruption Risk**
- **File:** `src/mneme/incremental_persistence.py:25-41`
- **Problem:** No atomic writes
- **Fix:** Implement temp file + rename pattern
- **Effort:** 1 hour
- **Impact:** Prevents data loss on crash

```python
def save(self, system, force_full: bool = False) -> None:
    temp_file = self.state_file.with_suffix('.json.tmp')
    try:
        system.save(str(temp_file))
        temp_file.replace(self.state_file)  # Atomic on POSIX
        self.dirty_projects.clear()
    except Exception as e:
        temp_file.unlink(missing_ok=True)
        raise StateSaveError(f"Failed to save state: {e}")
```

**Issue #3: Cache Race Condition**
- **File:** `src/mneme/cache.py:23-42`
- **Problem:** No thread safety
- **Fix:** Add threading.Lock
- **Effort:** 30 minutes
- **Impact:** Prevents crashes in concurrent use

```python
import threading

class QueryCache:
    def __init__(self, maxsize=128, ttl=300):
        self._cache = {}
        self._access_order = []
        self._lock = threading.Lock()  # Add lock
    
    def get(self, *args, **kwargs):
        with self._lock:  # Protect all operations
            key = self._make_key(*args, **kwargs)
            # ... rest of method
```

---

### Phase 2: Memory & Scaling (Days 3-4)

**Issue #4: Memory Leak in Agent History**
- **File:** `src/mneme/neuromorphic_agent.py:96-100`
- **Fix:** Implement circular buffer
- **Effort:** 1 hour

```python
from collections import deque

class NeuromorphicAgent:
    def __init__(self, ...):
        self.query_history = deque(maxlen=1000)  # Bounded queue
```

**Issue #5: O(n²) Auto-Connect**
- **File:** `src/mneme/neuromorphic_agent.py:203-216`
- **Fix:** Use LSH index for similarity search
- **Effort:** 3 hours

```python
def auto_connect(self, threshold=0.5):
    # Build LSH index of agent domain vectors
    agent_vectors = [agent.domain_vector for agent in self.agents.values()]
    lsh = LSHIndex(dims=self.kb.dims, num_tables=8)
    for idx, vec in enumerate(agent_vectors):
        lsh.add(vec, idx)
    
    # Query for similar agents (O(n log n))
    for idx, agent in enumerate(self.agents.values()):
        similar_indices = lsh.query(agent.domain_vector, top_k=10)
        for sim_idx, similarity in similar_indices:
            if similarity > threshold:
                agent.connect(agent_list[sim_idx], weight=similarity)
```

**Issue #6: Recursive Spike Blowup**
- **File:** `neuromorphic_agent.py:73-140`
- **Fix:** Use existing OptimizedAgentNetwork
- **Effort:** 30 minutes (just enable it)

```python
# In integration.py or global_knowledge_system.py
from .optimized_network import OptimizedAgentNetwork

# Replace:
self.agent_network = AgentNetwork(self.kb)
# With:
self.agent_network = OptimizedAgentNetwork(self.kb, max_depth=3)
```

---

## 🔴 HIGH PRIORITY (Week 2)

### Issue #7: Useless Agent Network
**Decision Required:** Keep or remove?

**Option A: Remove (Recommended)**
- Delete `neuromorphic_agent.py` (400 lines)
- Replace with simple tag-based filtering
- Effort: 4 hours
- Impact: -30% code complexity, same functionality

**Option B: Fix and Enable**
- Enable propagation in `broadcast_query()`
- Fix connection strengthening logic
- Add connection decay
- Effort: 8 hours
- Impact: Agents actually learn, but adds complexity

### Issue #8-12: Code Quality Fixes
- Division by zero handling (1 hour)
- LSH bucket limits (2 hours)
- Circular reference fix (1 hour)
- Delete unused code (30 minutes)
- Vector dimension validation (1 hour)

**Total Effort:** 5.5 hours

---

## 🟡 MEDIUM PRIORITY (Week 3)

### Performance Optimizations
1. Wire up Rust bind/bundle (2 hours) → 3-5x speedup
2. Lower LSH threshold to 10 (5 minutes) → 2x speedup
3. Use numpy.save() for persistence (1 hour) → 2x faster saves
4. Optimize cache key generation (30 minutes) → 10% faster queries

### Architecture Improvements
5. Align crystallization with hypervector (4 hours)
6. Remove duplicate result handling (1 hour)
7. Fix connection strengthening logic (2 hours)
8. Add vector dimension validation (1 hour)

**Total Effort:** 11.5 hours

---

## 📋 DECISION POINTS

### Decision 1: What is Mneme Actually For?

**Current README:** "Infinite context for LLMs via summarization"  
**Current Implementation:** Project metadata tracker

**Options:**
- **A) Fix README** - Rebrand as "Project Knowledge System" (5 minutes)
- **B) Rebuild for LLM context** - Major rewrite (2-4 weeks)

**Recommendation:** Option A - current implementation is solid for project tracking

---

### Decision 2: Keep or Remove Agent Network?

**Current State:** 400+ lines, disabled by default, adds no value

**Options:**
- **A) Remove** - Simplify to tag-based filtering (4 hours)
- **B) Fix** - Enable propagation, fix learning (8 hours)
- **C) Keep disabled** - Document as experimental (0 hours)

**Recommendation:** Option A - remove unless you have specific use case for learning

---

### Decision 3: Keep or Delete Unused Code?

**Unused Files:**
- `metal_backend.py` (242 lines)
- `hybrid_dispatcher.py` (258 lines)
- `optimized_network.py` (partially used)

**Options:**
- **A) Delete** - Clean up codebase (30 minutes)
- **B) Integrate** - Wire up Metal GPU (1-2 weeks)
- **C) Keep** - Leave for future (0 hours)

**Recommendation:** Option A - delete unless actively developing GPU support

---

## 🎯 RECOMMENDED TIMELINE

### Week 1: Critical Fixes (MUST DO)
- **Day 1:** Fix hypervector query encoding (2h)
- **Day 2:** Add atomic writes (1h) + cache thread safety (0.5h)
- **Day 3:** Fix memory leak (1h) + O(n²) auto-connect (3h)
- **Day 4:** Enable OptimizedAgentNetwork (0.5h) + testing (2h)
- **Day 5:** Integration testing + bug fixes (4h)

**Total:** ~14 hours

### Week 2: High Priority (SHOULD DO)
- **Day 1:** Decision on agent network (4-8h)
- **Day 2-3:** Code quality fixes (5.5h)
- **Day 4-5:** Testing + documentation (8h)

**Total:** ~17-21 hours

### Week 3: Medium Priority (NICE TO HAVE)
- **Day 1-2:** Performance optimizations (4.5h)
- **Day 3-4:** Architecture improvements (7h)
- **Day 5:** Final testing + release (4h)

**Total:** ~15.5 hours

---

## ✅ SUCCESS CRITERIA

### After Week 1 (Critical Fixes)
- [ ] Hypervector queries return correct results (not 0.022 similarity)
- [ ] No data corruption on crash/power loss
- [ ] No race condition crashes in concurrent use
- [ ] Memory usage stable over 1000+ queries
- [ ] System scales to 100+ agents without O(n²) blowup
- [ ] All existing tests pass

### After Week 2 (High Priority)
- [ ] Decision made on agent network (keep/remove/fix)
- [ ] No division by zero errors
- [ ] LSH buckets bounded and monitored
- [ ] No circular reference memory leaks
- [ ] Unused code deleted or documented
- [ ] Test coverage > 50%

### After Week 3 (Medium Priority)
- [ ] Rust bind/bundle integrated (3-5x speedup)
- [ ] LSH threshold optimized
- [ ] Persistence uses binary format
- [ ] Cache key generation optimized
- [ ] Architecture documented
- [ ] Ready for production use

---

## 🚀 QUICK WINS (Do First)

These take < 1 hour each and have high impact:

1. **Delete unused code** (30 min) → -500 lines, cleaner codebase
2. **Lower LSH threshold** (5 min) → 2x faster queries
3. **Enable OptimizedAgentNetwork** (30 min) → Prevents recursive blowup
4. **Add cache thread lock** (30 min) → Prevents crashes
5. **Fix memory leak** (1 hour) → Stable long-term operation

**Total:** 2.5 hours for 5 major improvements

---

## 📝 NOTES

### Testing Strategy
- Add integration test for hypervector query correctness
- Add stress test for concurrent cache access
- Add memory leak test (1000+ queries)
- Add scaling test (100+ agents)

### Documentation Needed
- Update README with actual use case
- Document decision on agent network
- Add architecture diagram showing data flow
- Document performance characteristics

### Risk Assessment
- **High Risk:** Hypervector query fix could break existing behavior
- **Medium Risk:** Atomic writes change file format
- **Low Risk:** Cache thread safety is additive

---

**Next Step:** Review this plan and decide:
1. What is Mneme actually for? (Project tracking vs LLM context)
2. Keep or remove agent network?
3. Timeline: Fix all critical issues (Week 1) or just quick wins (2.5 hours)?
