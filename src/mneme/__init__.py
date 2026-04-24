"""
Mneme - Hyperdimensional Knowledge Storage for LLM Sessions

Permanent knowledge storage using hyperdimensional computing.
Stores project origins, relationships, and causal chains across sessions.
"""

__version__ = "0.1.0"

from .integration import init_knowledge_system, KnowledgeIntegration
from .config import Config
from .exceptions import (
    KnowledgeSystemError,
    ProjectNotFoundError,
    StateLoadError,
    StateSaveError,
)

__all__ = [
    "init_knowledge_system",
    "KnowledgeIntegration",
    "Config",
    "KnowledgeSystemError",
    "ProjectNotFoundError",
    "StateLoadError",
    "StateSaveError",
]
