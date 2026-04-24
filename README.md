# Hyperdimensional Knowledge System

Permanent knowledge storage for LLM sessions using hyperdimensional computing.

## What It Does

Stores project knowledge permanently across sessions:
- Why projects were created
- Cross-project relationships
- Causal chains (decision history)
- Works without conversation history

## Quick Start

```python
from src import init_knowledge_system

# Initialize
knowledge = init_knowledge_system()

# Track a project
knowledge.track_project_creation(
    project_name="my-service",
    reason="What it does",
    created_for="parent-service",  # Optional
    causal_chain=["step1", "step2"],  # Optional
    technologies=["Python", "FastAPI"]  # Optional
)

# Query later (even in new sessions)
print(knowledge.why_does_exist("my-service"))
```

## Installation

```bash
pip install numpy
```

## Demo

```bash
python3 demo.py
```

## Storage

Knowledge stored in `.claude/knowledge/`:
- `system_state.json` - System state
- `knowledge_base.json` - Hypervector space
- `projects/` - Project artifacts
  - `{project}/.meta/origin.json` - Machine-readable
  - `{project}/docs/WHY.md` - Human-readable

## API

### Initialize
```python
knowledge = init_knowledge_system(workspace_path="./")
```

### Track Project
```python
knowledge.track_project_creation(
    project_name="name",
    reason="why",
    created_for="parent",
    causal_chain=["step1", "step2"],
    technologies=["tech1", "tech2"]
)
```

### Query
```python
# Why does X exist?
print(knowledge.why_does_exist("project-name"))

# Full context
context = knowledge.query_context("project-name")

# List all
projects = knowledge.list_projects()

# Stats
stats = knowledge.get_stats()

# Visualize
print(knowledge.visualize())
```

### Add Relationship
```python
knowledge.add_relationship("subject", "relation", "object")
```

## Architecture

**Core Components** (do not modify):
- `hypervector.py` - 10K-dimensional vector space
- `neuromorphic_agent.py` - Agent network with Hebbian learning
- `crystallization.py` - Artifact generation
- `global_knowledge_system.py` - System coordinator

**Integration Layer** (`src/`):
- `integration.py` - Main interface
- `config.py` - Configuration
- `project_tracker.py` - Project tracking
- `query_interface.py` - Queries
- `persistence.py` - State management
- `logging_config.py` - Logging
- `exceptions.py` - Error handling

## Features

- ✅ No LLM API required
- ✅ Works offline
- ✅ Permanent storage
- ✅ Cross-session persistence
- ✅ Semantic search via hypervectors
- ✅ Structured logging
- ✅ Error handling
- ✅ Clean separation of concerns

## Technical Details

See `SYSTEM_OVERVIEW.md` for implementation details.

## License

MIT
