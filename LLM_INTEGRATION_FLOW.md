# 🤖 LLM INTEGRATION FLOW - How LLMs Use This System

**Date:** 2026-04-24  
**Question:** How does an LLM use this system? What context is provided?

---

## 🔄 THE FLOW

### Current Implementation (As-Is)

```
┌─────────────────────────────────────────────────────────────┐
│  LLM Session (e.g., Claude in conversation)                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
                    User asks:
              "Why does rate-limiter exist?"
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Python Code (in conversation or script)                    │
│                                                              │
│  from src import init_knowledge_system                      │
│  knowledge = init_knowledge_system()                        │
│  result = knowledge.why_does_exist("rate-limiter")          │
│  print(result)                                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Knowledge System Query                                     │
│                                                              │
│  1. Check cache (QueryCache)                                │
│  2. If not cached, query GlobalKnowledgeSystem              │
│  3. Retrieve project context                                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Context Retrieval (get_project_context)                    │
│                                                              │
│  Returns:                                                   │
│  {                                                          │
│    "project": "rate-limiter",                               │
│    "origin": {                                              │
│      "created_for": "auth-service",                         │
│      "reason": "Prevent API abuse",                         │
│      "created": "2026-04-24T...",                           │
│      "causal_chain": [...]                                  │
│    },                                                       │
│    "related_projects": [                                    │
│      {"project": "auth-service", "strength": 0.90}          │
│    ],                                                       │
│    "causal_chain": {                                        │
│      "chain": [                                             │
│        "auth-service experiencing high load",               │
│        "Brute-force attacks detected",                      │
│        "Security team recommended rate limiting",           │
│        "rate-limiter created"                               │
│      ]                                                      │
│    },                                                       │
│    "agent": {...},                                          │
│    "artifacts": {...}                                       │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Format as Summary (why_exists method)                      │
│                                                              │
│  # Why rate-limiter Exists                                  │
│                                                              │
│  Created for: auth-service                                  │
│  Reason: Prevent API abuse                                  │
│                                                              │
│  Causal Chain:                                              │
│    1. auth-service experiencing high load                   │
│    2. Brute-force attacks detected                          │
│    3. Security team recommended rate limiting               │
│    4. rate-limiter created                                  │
│                                                              │
│  Related Projects:                                          │
│    • auth-service (connection: 0.90)                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Return to LLM                                              │
│                                                              │
│  LLM receives the formatted summary (NOT raw data)          │
│  LLM can then respond to user with this context             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 CONTEXT SIZE: SUMMARY vs FULL DATA

### What Gets Stored (Full Data)

**In Hypervector Space:**
```
- 10,000-dimensional vectors per concept
- All facts encoded as vectors
- All relationships as vector bindings
- Total: ~80KB per fact
```

**In Agent Network:**
```
- Agent per project with domain knowledge
- Connection weights between agents
- Spike history and statistics
- Total: ~100KB per agent
```

**In Crystallized Artifacts:**
```
- WHY.md (human-readable, ~1-2KB)
- origin.json (structured metadata, ~1KB)
- README.md (overview, ~1KB)
- Total: ~3-4KB per project
```

**Example for 52 projects:**
- Hypervectors: ~4MB (52 projects × 76 facts × 80KB)
- Agents: ~5MB (52 agents × 100KB)
- Artifacts: ~200KB (52 × 4KB)
- **Total stored: ~9MB**

---

### What Gets Returned to LLM (Summary Only)

**For a single query like "Why does rate-limiter exist?":**

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

**Size: ~300 bytes** (0.0003 MB)

**Compression ratio: 9MB → 300 bytes = 30,000:1**

---

## 🎯 KEY INSIGHT: SUMMARY, NOT ALL

### The System Does NOT:
❌ Load all 9MB of data into LLM context  
❌ Send all 52 projects to LLM  
❌ Send raw hypervector data  
❌ Send all facts and relationships  

### The System DOES:
✅ Query specific project only  
✅ Return formatted summary (~300 bytes)  
✅ Include only relevant information:
  - Why it was created
  - What it was created for
  - Causal chain (decision history)
  - Related projects (top connections)

### Result:
**LLM gets clean, concise summary** - not the entire knowledge base.

---

## 🔍 HOW RETRIEVAL WORKS

### 1. Hypervector Query (Behind the Scenes)

```python
# System encodes query as vector
query_vec = hypervector_space.get_or_create_concept("rate-limiter")

# Searches for similar facts (cosine similarity)
results = hypervector_space.query(query_vec, top_k=10)

# Returns most relevant facts:
# - "rate-limiter created_for auth-service" (similarity: 0.95)
# - "rate-limiter prevents abuse" (similarity: 0.87)
# - "auth-service uses rate-limiter" (similarity: 0.82)
```

**This happens internally** - LLM never sees the vectors.

---

### 2. Agent Network Query (Behind the Scenes)

```python
# Agent for rate-limiter activates
agent = agent_network.agents["rate-limiter"]

# Calculates attention (relevance)
attention = agent.calculate_attention(query_vec)  # 0.95 (high)

# Propagates to connected agents
agent.spike(query_vec, propagate=True)
# → Activates auth-service agent (connection: 0.90)
# → Finds related context
```

**This happens internally** - LLM never sees the agent network.

---

### 3. Crystallized Artifacts (Read from Disk)

```python
# Reads origin.json
origin = read_json(".claude/knowledge/projects/rate-limiter/.meta/origin.json")

# Returns:
{
  "project": "rate-limiter",
  "created_for": "auth-service",
  "reason": "Prevent API abuse",
  "causal_chain": [...]
}
```

**This is what gets formatted** into the summary for the LLM.

---

### 4. Format Summary (What LLM Sees)

```python
# QueryInterface.why_exists() formats the data
def why_exists(project_name):
    context = system.get_project_context(project_name)
    
    # Format as markdown summary
    lines = [f"# Why {project_name} Exists\n"]
    lines.append(f"Created for: {context['origin']['created_for']}")
    lines.append(f"Reason: {context['origin']['reason']}\n")
    
    # Add causal chain
    for i, step in enumerate(context['causal_chain']['chain'], 1):
        lines.append(f"  {i}. {step}")
    
    # Add related projects
    for rel in context['related_projects']:
        lines.append(f"  • {rel['project']} (connection: {rel['strength']:.2f})")
    
    return "\n".join(lines)
```

**Only this formatted summary** goes to the LLM.

---

## 💡 EXAMPLE: FULL FLOW

### User asks Claude:
```
"Why does rate-limiter exist?"
```

### Claude runs Python code:
```python
from src import init_knowledge_system
knowledge = init_knowledge_system()
result = knowledge.why_does_exist("rate-limiter")
print(result)
```

### System internally:
1. **Checks cache** (QueryCache) - miss
2. **Queries hypervectors** - finds "rate-limiter created_for auth-service"
3. **Activates agent network** - rate-limiter agent → auth-service agent
4. **Reads artifacts** - origin.json, WHY.md
5. **Formats summary** - ~300 bytes of text

### Claude receives:
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

### Claude responds to user:
```
The rate-limiter project was created for auth-service to prevent API abuse.
It was created because auth-service was experiencing high load from brute-force
attacks, and the security team recommended implementing rate limiting.
```

**Total context used: ~300 bytes** (not 9MB)

---

## 🎯 CONTEXT EFFICIENCY

### Traditional Approach (Without This System)
```
LLM Context Window: 200K tokens (~800KB)

To answer "Why does rate-limiter exist?":
- Load entire conversation history (50K tokens)
- Load all project files (100K tokens)
- Load all documentation (50K tokens)
- Total: 200K tokens (full context window)

Problem: Hits context limit, loses old information
```

### With This System
```
LLM Context Window: 200K tokens (~800KB)

To answer "Why does rate-limiter exist?":
- Query knowledge system (0 tokens - happens outside)
- Receive summary (75 tokens = ~300 bytes)
- Total: 75 tokens (0.04% of context window)

Benefit: 99.96% of context window still available
```

**Efficiency gain: 2,666x less context used**

---

## 🔧 HOW TO INTEGRATE WITH LLM

### Option 1: Manual Query (Current)

```python
# In Claude conversation or script
from src import init_knowledge_system

knowledge = init_knowledge_system()

# Query specific project
result = knowledge.why_does_exist("rate-limiter")
print(result)

# Get full context
context = knowledge.query_context("rate-limiter")
print(context)

# List all projects
projects = knowledge.list_projects()
for p in projects:
    print(f"- {p['name']}: {p['reason']}")
```

**LLM receives:** Formatted summaries only

---

### Option 2: Tool Integration (Future)

```python
# Define as LLM tool
tools = [
    {
        "name": "query_knowledge",
        "description": "Query the knowledge system for project context",
        "parameters": {
            "project_name": "string"
        }
    }
]

# LLM can call tool
response = llm.generate(
    prompt="Why does rate-limiter exist?",
    tools=tools
)

# LLM automatically calls:
# query_knowledge(project_name="rate-limiter")

# Receives summary, responds to user
```

**LLM receives:** Only what it queries

---

### Option 3: Automatic Context Injection (Future)

```python
# System detects project mentions in conversation
conversation = "Let's work on rate-limiter"

# Automatically injects context
if "rate-limiter" in conversation:
    context = knowledge.why_does_exist("rate-limiter")
    system_prompt += f"\n\nContext: {context}"

# LLM now has context without explicit query
```

**LLM receives:** Relevant context automatically

---

## 📊 SUMMARY

### What Gets Stored
- **9MB** of hypervectors, agents, and artifacts
- **52 projects**, 76 facts, 71 concepts
- **Full knowledge graph** with relationships

### What LLM Receives
- **~300 bytes** per query
- **Formatted summary** only
- **Relevant context** for specific project

### Compression
- **30,000:1** compression ratio
- **99.96%** context window saved
- **Infinite scalability** (query only what's needed)

### Key Insight
**The system stores everything, but only returns summaries.**

LLM never sees:
- Raw hypervectors (10K dimensions)
- Agent network internals
- Full knowledge graph
- All projects at once

LLM only sees:
- Formatted markdown summary
- Specific project context
- Relevant relationships
- Causal chain

**This is the power of the system** - infinite storage, minimal context usage.

---

**Document:** LLM Integration Flow  
**Date:** 2026-04-24  
**Status:** Explains current implementation
