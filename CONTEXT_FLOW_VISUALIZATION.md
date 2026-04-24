# 📊 CONTEXT FLOW VISUALIZATION

**Visual guide to how context flows through the system**

---

## 🎯 THE BIG PICTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER (9MB)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Hypervectors │  │ Agent Network│  │  Artifacts   │         │
│  │   (4MB)      │  │    (5MB)     │  │   (200KB)    │         │
│  │              │  │              │  │              │         │
│  │ 10K-dim      │  │ 52 agents    │  │ WHY.md       │         │
│  │ vectors      │  │ Connections  │  │ origin.json  │         │
│  │ 76 facts     │  │ Hebbian      │  │ README.md    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    QUERY HAPPENS
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  RETRIEVAL LAYER (Internal)                     │
│                                                                 │
│  1. Hypervector similarity search                              │
│     → Finds: "rate-limiter created_for auth-service"           │
│                                                                 │
│  2. Agent network activation                                   │
│     → rate-limiter agent (0.95 attention)                      │
│     → Propagates to auth-service agent (0.90 connection)       │
│                                                                 │
│  3. Read crystallized artifacts                                │
│     → origin.json: metadata                                    │
│     → WHY.md: human story                                      │
│                                                                 │
│  4. Assemble context                                           │
│     → Combine all sources                                      │
│     → Format as summary                                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    FORMAT SUMMARY
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER (300 bytes)                     │
│                                                                 │
│  # Why rate-limiter Exists                                     │
│                                                                 │
│  Created for: auth-service                                     │
│  Reason: Prevent API abuse                                     │
│                                                                 │
│  Causal Chain:                                                 │
│    1. auth-service experiencing high load                      │
│    2. Brute-force attacks detected                             │
│    3. Security team recommended rate limiting                  │
│    4. rate-limiter created                                     │
│                                                                 │
│  Related Projects:                                             │
│    • auth-service (connection: 0.90)                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                      TO LLM CONTEXT
```

---

## 📉 CONTEXT COMPRESSION

```
STORAGE (What's Saved)
═══════════════════════════════════════════════════════════════
█████████████████████████████████████████████████ 9,000,000 bytes
                                                  (9 MB)


RETRIEVAL (What's Processed Internally)
═══════════════════════════════════════════════════════════════
████████████████████████████████████ 5,000,000 bytes
                                     (5 MB - vectors + agents)


OUTPUT (What LLM Receives)
═══════════════════════════════════════════════════════════════
█ 300 bytes
  (0.0003 MB)


COMPRESSION RATIO: 30,000:1
```

---

## 🔄 QUERY FLOW: STEP BY STEP

### Step 1: User Query
```
User: "Why does rate-limiter exist?"
```

### Step 2: System Query
```python
knowledge.why_does_exist("rate-limiter")
```

### Step 3: Cache Check
```
QueryCache.get("why_exists:rate-limiter")
→ MISS (not cached)
```

### Step 4: Hypervector Search
```
Input: "rate-limiter" concept vector (10,000 dims)

Search: Cosine similarity across 76 facts
┌─────────────────────────────────────────┐
│ Fact                          Similarity│
├─────────────────────────────────────────┤
│ rate-limiter created_for ...     0.95   │
│ rate-limiter prevents abuse      0.87   │
│ auth-service uses rate-limiter   0.82   │
│ rate-limiter handles requests    0.76   │
│ ...                              ...    │
└─────────────────────────────────────────┘

Output: Top 10 relevant facts
```

### Step 5: Agent Activation
```
rate-limiter agent:
  - Domain: ["rate-limiter", "rate-limiting", "throttling"]
  - Attention: 0.95 (high relevance)
  - Spike: ACTIVATED
  
Propagates to connected agents:
  → auth-service agent (weight: 0.90)
  → api-gateway agent (weight: 0.75)
  
Hebbian learning:
  → Strengthen rate-limiter ↔ auth-service (used together)
```

### Step 6: Read Artifacts
```
Read: .claude/knowledge/projects/rate-limiter/.meta/origin.json

{
  "project": "rate-limiter",
  "created": "2026-04-24T10:30:00Z",
  "reason": "Prevent API abuse",
  "created_for": "auth-service",
  "causal_chain": [
    "auth-service experiencing high load",
    "Brute-force attacks detected",
    "Security team recommended rate limiting",
    "rate-limiter created"
  ]
}
```

### Step 7: Assemble Context
```python
context = {
    "project": "rate-limiter",
    "origin": {...},              # From origin.json
    "related_projects": [...],    # From agent connections
    "causal_chain": {...},        # From origin.json
    "agent": {...}                # From agent stats
}
```

### Step 8: Format Summary
```python
lines = []
lines.append("# Why rate-limiter Exists\n")
lines.append(f"Created for: {origin['created_for']}")
lines.append(f"Reason: {origin['reason']}\n")

for i, step in enumerate(causal_chain, 1):
    lines.append(f"  {i}. {step}")

for rel in related_projects:
    lines.append(f"  • {rel['project']} (connection: {rel['strength']:.2f})")

summary = "\n".join(lines)
```

### Step 9: Cache Result
```
QueryCache.set("why_exists:rate-limiter", summary)
→ Cached for future queries
```

### Step 10: Return to LLM
```markdown
# Why rate-limiter Exists

Created for: auth-service
Reason: Prevent API abuse

Causal Chain:
  1. auth-service experiencing high load
  2. Brute-force attacks detected
  3. Security team recommended rate limiting
  4. rate-limiter created

Related Projects:
  • auth-service (connection: 0.90)
```

**Size: 300 bytes**

---

## 💾 WHAT'S STORED vs WHAT'S RETURNED

### Stored in System (9MB total)

#### Hypervectors (4MB)
```
rate-limiter concept:
  [0.23, -0.45, 0.67, ..., 0.12]  (10,000 numbers)
  
auth-service concept:
  [-0.34, 0.56, -0.23, ..., 0.45]  (10,000 numbers)
  
Fact: "rate-limiter created_for auth-service"
  [0.12, -0.67, 0.34, ..., -0.23]  (10,000 numbers)
  
... 76 facts × 10,000 dimensions × 8 bytes = ~6MB
```

#### Agent Network (5MB)
```
rate-limiter agent:
  - domain_vector: [10,000 numbers]
  - connections: {
      auth-service: 0.90,
      api-gateway: 0.75,
      ...
    }
  - spike_history: [...]
  - statistics: {...}
  
... 52 agents × ~100KB = ~5MB
```

#### Artifacts (200KB)
```
rate-limiter/
├── .meta/origin.json (1KB)
├── docs/WHY.md (2KB)
└── README.md (1KB)

... 52 projects × 4KB = ~200KB
```

---

### Returned to LLM (300 bytes)

```markdown
# Why rate-limiter Exists

Created for: auth-service
Reason: Prevent API abuse

Causal Chain:
  1. auth-service experiencing high load
  2. Brute-force attacks detected
  3. Security team recommended rate limiting
  4. rate-limiter created

Related Projects:
  • auth-service (connection: 0.90)
```

**Only the summary - not the vectors, not the agents, not the full graph.**

---

## 🎯 KEY INSIGHTS

### 1. Infinite Storage, Minimal Context
```
Storage: Unlimited (add more projects forever)
Context: Fixed (~300 bytes per query)
Result: Scales infinitely
```

### 2. Query-Driven Retrieval
```
Don't load everything → Query what's needed
Don't send raw data → Send formatted summary
Don't use full context → Use 0.04% of context window
```

### 3. Multi-Layer Redundancy
```
Layer 1: Hypervectors (semantic search)
Layer 2: Agent Network (relationship traversal)
Layer 3: Artifacts (human-readable backup)

If one fails, others still work
```

### 4. Compression Through Summarization
```
Raw data: 9MB
Processed: 5MB (internal)
Returned: 300 bytes (to LLM)

Compression: 30,000:1
```

---

## 📊 COMPARISON: WITH vs WITHOUT

### WITHOUT This System

```
User: "Why does rate-limiter exist?"

LLM needs:
├── Full conversation history (50K tokens)
├── All project files (100K tokens)
├── All documentation (50K tokens)
└── Total: 200K tokens (full context window)

Problems:
❌ Hits context limit
❌ Loses old information
❌ Can't scale beyond window
❌ Expensive (200K tokens per query)
```

### WITH This System

```
User: "Why does rate-limiter exist?"

LLM needs:
├── Query knowledge system (0 tokens - external)
├── Receive summary (75 tokens)
└── Total: 75 tokens (0.04% of context window)

Benefits:
✅ Never hits context limit
✅ Preserves all information
✅ Scales infinitely
✅ Cheap (75 tokens per query)
```

**Efficiency: 2,666x improvement**

---

## 🔮 FUTURE: AUTOMATIC CONTEXT INJECTION

### Current (Manual)
```python
# User must explicitly query
result = knowledge.why_does_exist("rate-limiter")
```

### Future (Automatic)
```python
# System detects project mentions
conversation = "Let's work on rate-limiter"

# Automatically injects context
if mentions_project(conversation):
    context = knowledge.why_does_exist("rate-limiter")
    inject_into_system_prompt(context)

# LLM automatically has context
```

### Future (Tool Integration)
```python
# LLM has tool access
tools = [query_knowledge, list_projects, get_context]

# LLM decides when to query
llm.generate(
    prompt="Why does rate-limiter exist?",
    tools=tools
)

# LLM automatically calls: query_knowledge("rate-limiter")
```

---

## 📝 SUMMARY

### The Flow
1. **Store everything** (9MB) in hypervectors + agents + artifacts
2. **Query specific project** when needed
3. **Retrieve relevant context** (5MB processed internally)
4. **Format as summary** (300 bytes)
5. **Return to LLM** (only the summary)

### The Result
- **Infinite storage** (add unlimited projects)
- **Minimal context** (300 bytes per query)
- **Fast retrieval** (cached, LSH-indexed)
- **Scalable** (never hits context limits)

### The Key Insight
**LLM never sees the full knowledge base - only summaries of what it queries.**

This is how you give an LLM "infinite memory" without infinite context.

---

**Document:** Context Flow Visualization  
**Date:** 2026-04-24  
**Purpose:** Visual explanation of context compression
