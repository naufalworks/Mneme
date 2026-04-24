# Using the Knowledge System with Claude Code

## Quick Start

### 1. Initialize in Your Workspace

```python
from claude_code_integration import init_knowledge_system

# Initialize (automatically creates .claude/knowledge/)
knowledge = init_knowledge_system()
```

This creates:
```
your-workspace/
└── .claude/
    └── knowledge/
        ├── system_state.json
        ├── knowledge_base.json
        └── projects/
            └── (project artifacts)
```

### 2. Track Projects as You Create Them

```python
# When you create a new project/component
knowledge.track_project_creation(
    project_name="auth-service",
    reason="Handle user authentication",
    technologies=["Python", "FastAPI", "JWT"]
)
```

### 3. Track Relationships

```python
# When project 3 is created because project 1 needed it
knowledge.track_project_creation(
    project_name="rate-limiter",
    reason="Prevent API abuse",
    created_for="auth-service",  # The key link!
    causal_chain=[
        "auth-service had no rate limiting",
        "Brute-force attacks detected",
        "Decision to create rate-limiter"
    ],
    technologies=["Python", "Redis"]
)

# Add explicit relationships
knowledge.add_relationship("auth-service", "uses", "rate-limiter")
```

### 4. Query Later (Even in New Sessions!)

```python
# In a new Claude Code session (weeks later)
from claude_code_integration import init_knowledge_system

knowledge = init_knowledge_system()  # Loads existing state

# Ask why something exists
print(knowledge.why_does_exist("rate-limiter"))

# Output:
# # Why rate-limiter Exists
# 
# Created for: auth-service
# Reason: Prevent API abuse
# 
# Causal Chain:
#   1. auth-service had no rate limiting
#   2. Brute-force attacks detected
#   3. Decision to create rate-limiter
```

---

## Integration Patterns

### Pattern 1: Manual Tracking (You Control)

```python
# You explicitly tell the system what to track
knowledge = init_knowledge_system()

# When you create something
knowledge.track_project_creation(
    project_name="my-service",
    reason="Does X",
    created_for="parent-service"
)
```

### Pattern 2: During Conversations with Claude

**You:** "Create an auth service"

**Claude:** Creates the code, then:
```python
knowledge.track_project_creation(
    project_name="auth-service",
    reason="Handle authentication"
)
```

**You:** "Now create a rate limiter because auth needs it"

**Claude:** Creates the code, then:
```python
knowledge.track_project_creation(
    project_name="rate-limiter",
    reason="Prevent abuse",
    created_for="auth-service",
    causal_chain=[
        "auth-service needed rate limiting",
        "rate-limiter created"
    ]
)
```

**Later (new session):**

**You:** "Why does rate-limiter exist?"

**Claude:** 
```python
context = knowledge.why_does_exist("rate-limiter")
print(context)
# Returns: "Created for auth-service to prevent abuse"
```

### Pattern 3: Automatic Tracking (Future Enhancement)

```python
# Hook into Claude Code events (future feature)
@on_project_create
def auto_track(project_name, context):
    knowledge.track_project_creation(
        project_name=project_name,
        reason=context.get('reason'),
        created_for=context.get('parent')
    )
```

---

## Common Use Cases

### Use Case 1: Your 3-Project Scenario

```python
knowledge = init_knowledge_system()

# Project 1
knowledge.track_project_creation(
    project_name="project1",
    reason="First project"
)

# Project 2
knowledge.track_project_creation(
    project_name="project2",
    reason="Second project"
)

# Project 3 - created because project1 needed it
knowledge.track_project_creation(
    project_name="project3",
    reason="Solves project1's problem X",
    created_for="project1",
    causal_chain=[
        "project1 had problem X",
        "Investigated solutions",
        "Decided to create project3"
    ]
)

# Later: Query
print(knowledge.why_does_exist("project3"))
# Output: "Created for project1 to solve problem X"
```

### Use Case 2: Microservices Architecture

```python
knowledge = init_knowledge_system()

# Core service
knowledge.track_project_creation(
    project_name="api-gateway",
    reason="Central API gateway",
    technologies=["Node.js", "Express"]
)

# Supporting services
for service in ["auth", "payments", "notifications"]:
    knowledge.track_project_creation(
        project_name=f"{service}-service",
        reason=f"Handle {service}",
        created_for="api-gateway",
        technologies=["Python", "FastAPI"]
    )
    knowledge.add_relationship("api-gateway", "routes_to", f"{service}-service")
```

### Use Case 3: Refactoring History

```python
# Track why you refactored something
knowledge.track_project_creation(
    project_name="new-auth-module",
    reason="Refactored auth for better security",
    created_for="old-auth-module",
    causal_chain=[
        "old-auth-module had security vulnerabilities",
        "Security audit revealed issues",
        "Decision to refactor with new architecture",
        "new-auth-module created"
    ]
)
```

---

## Commands Reference

### Initialization
```python
knowledge = init_knowledge_system(workspace_path="./my-workspace")
```

### Tracking
```python
# Track project
knowledge.track_project_creation(
    project_name="name",
    reason="why it exists",
    created_for="parent",  # optional
    causal_chain=["step1", "step2"],  # optional
    technologies=["tech1", "tech2"]  # optional
)

# Add relationship
knowledge.add_relationship("subject", "relation", "object")
```

### Querying
```python
# Get full context
context = knowledge.query_context("project-name")

# Get why explanation
why = knowledge.why_does_exist("project-name")

# List all projects
projects = knowledge.list_projects()

# Visualize
print(knowledge.visualize())

# Get stats
stats = knowledge.get_stats()
```

### Export
```python
# Export summary
summary = knowledge.export_summary("./KNOWLEDGE_SUMMARY.md")
```

---

## File Structure

After using the system, your workspace will have:

```
your-workspace/
├── .claude/
│   └── knowledge/
│       ├── system_state.json          # System state
│       ├── knowledge_base.json        # Hypervector space
│       ├── SUMMARY.md                 # Exported summary
│       └── projects/
│           ├── project1/
│           │   ├── .meta/
│           │   │   └── origin.json    # Machine-readable
│           │   ├── docs/
│           │   │   └── WHY.md         # Human-readable
│           │   └── README.md
│           ├── project2/
│           └── project3/
└── (your actual code)
```

---

## Benefits

### ✅ No Context Pruning
Knowledge is stored permanently, never deleted.

### ✅ Cross-Session Memory
Works across Claude Code sessions without conversation history.

### ✅ Cross-Project Understanding
Projects know about their relationships and dependencies.

### ✅ Causal Chains
Preserves WHY decisions were made, not just WHAT was done.

### ✅ Human & Machine Readable
- WHY.md files for humans
- origin.json files for machines
- Hypervectors for semantic search

### ✅ No External Dependencies
- No API calls
- No external services
- Just Python + NumPy
- Works offline

---

## Example: Full Workflow

```python
# ============================================================
# Session 1: Building the system
# ============================================================

from claude_code_integration import init_knowledge_system

knowledge = init_knowledge_system()

# Create auth service
knowledge.track_project_creation(
    project_name="auth-service",
    reason="Handle user authentication",
    technologies=["Python", "FastAPI", "JWT"]
)

# Create API gateway
knowledge.track_project_creation(
    project_name="api-gateway",
    reason="Central routing and load balancing",
    technologies=["Node.js", "Express"]
)

# Create rate limiter (because auth needed it)
knowledge.track_project_creation(
    project_name="rate-limiter",
    reason="Prevent API abuse",
    created_for="auth-service",
    causal_chain=[
        "auth-service had no rate limiting",
        "Brute-force attacks detected",
        "Security team recommended rate limiting",
        "rate-limiter created"
    ],
    technologies=["Python", "Redis"]
)

# Add relationships
knowledge.add_relationship("api-gateway", "uses", "auth-service")
knowledge.add_relationship("api-gateway", "uses", "rate-limiter")
knowledge.add_relationship("auth-service", "uses", "rate-limiter")

print("✓ Session 1 complete - knowledge saved")

# ============================================================
# Session 2: Weeks later, new Claude Code session
# ============================================================

from claude_code_integration import init_knowledge_system

knowledge = init_knowledge_system()  # Loads existing state

# You ask: "Why does rate-limiter exist?"
print(knowledge.why_does_exist("rate-limiter"))

# Output:
# # Why rate-limiter Exists
# 
# Created for: auth-service
# Reason: Prevent API abuse
# 
# Causal Chain:
#   1. auth-service had no rate limiting
#   2. Brute-force attacks detected
#   3. Security team recommended rate limiting
#   4. rate-limiter created
# 
# Related Projects:
#   • auth-service (connection: 0.90)

# You ask: "What uses rate-limiter?"
context = knowledge.query_context("rate-limiter")
print("Used by:", [r['project'] for r in context['related_projects']])
# Output: Used by: ['auth-service', 'api-gateway']

print("✓ Session 2 complete - knowledge retrieved!")
```

---

## Next Steps

1. **Try it now:**
   ```bash
   python3 claude_code_integration.py
   ```

2. **Use in your workspace:**
   ```python
   from claude_code_integration import init_knowledge_system
   knowledge = init_knowledge_system()
   ```

3. **Track your projects:**
   - As you create them
   - Document why they exist
   - Link them together

4. **Query later:**
   - New sessions automatically load state
   - Ask "why" questions
   - Get full context

---

## FAQ

**Q: Do I need an LLM API?**  
A: No! This is a storage/retrieval system. It works standalone.

**Q: How does it integrate with Claude Code?**  
A: You (or Claude) call the Python functions during your session. The system stores knowledge to disk. Later sessions load it back.

**Q: What if I don't use it for a while?**  
A: Knowledge persists on disk. Load it anytime with `init_knowledge_system()`.

**Q: Can I use this with other tools?**  
A: Yes! It's just Python. Use it with any tool that can run Python code.

**Q: How much disk space does it use?**  
A: Very little. ~10MB per 100 projects with full knowledge graphs.

---

**Ready to use!** The system is integrated and working with Claude Code.
