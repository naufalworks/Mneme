"""
Hyperdimensional Knowledge System - Core Modules

Core system components (do not modify):
- hypervector.py: Vector space operations
- neuromorphic_agent.py: Agent network
- crystallization.py: Artifact generation
- global_knowledge_system.py: System coordinator
"""

# Re-export for backward compatibility
import sys
from pathlib import Path

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypervector import HypervectorSpace
from neuromorphic_agent import NeuromorphicAgentNetwork
from crystallization import ContextCrystallization
from global_knowledge_system import GlobalKnowledgeSystem

__all__ = [
    'HypervectorSpace',
    'NeuromorphicAgentNetwork',
    'ContextCrystallization',
    'GlobalKnowledgeSystem'
]
