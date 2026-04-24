"""Main integration interface."""

from typing import Dict, List, Optional
from pathlib import Path

from .config import Config
from .logging_config import setup_logger
from .project_tracker import ProjectTracker
from .query_interface import QueryInterface
from .incremental_persistence import IncrementalPersistence
from .exceptions import KnowledgeSystemError

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from global_knowledge_system import GlobalKnowledgeSystem


class KnowledgeIntegration:
    """Main integration interface for the knowledge system."""

    def __init__(self, workspace_path: Optional[str] = None):
        self.config = Config(workspace_path)
        self.config.ensure_dirs()

        # Setup logging
        log_file = self.config.knowledge_dir / "system.log"
        self.logger = setup_logger("knowledge_system", log_file)

        # Initialize core system
        self.system = GlobalKnowledgeSystem(
            base_path=str(self.config.projects_dir),
            dims=self.config.dims
        )

        # Initialize components with incremental persistence
        self.persistence = IncrementalPersistence(self.config.state_file, self.logger)
        self.tracker = ProjectTracker(self.system, self.logger)
        self.query = QueryInterface(self.system)

        # Load existing state
        if self.persistence.load(self.system):
            self.logger.info("System initialized with existing knowledge")
        else:
            self.logger.info(f"New knowledge system at {self.config.knowledge_dir}")

    def track_project_creation(self,
                              project_name: str,
                              reason: str,
                              created_for: Optional[str] = None,
                              causal_chain: Optional[List[str]] = None,
                              technologies: Optional[List[str]] = None) -> Dict:
        """Track project creation."""
        result = self.tracker.track_creation(
            project_name, reason, created_for, causal_chain, technologies
        )
        # Mark project as dirty for incremental save
        self.persistence.mark_dirty(project_name)
        self.persistence.save(self.system)
        # Invalidate cache for this project
        self.query.invalidate_cache(project_name)
        return result

    def add_relationship(self, subject: str, relation: str, obj: str) -> None:
        """Add relationship between projects."""
        self.tracker.add_relationship(subject, relation, obj)
        # Mark both projects as dirty
        self.persistence.mark_dirty(subject)
        self.persistence.mark_dirty(obj)
        self.persistence.save(self.system)
        # Invalidate cache for both projects
        self.query.invalidate_cache(subject)
        self.query.invalidate_cache(obj)

    def why_does_exist(self, project_name: str) -> str:
        """Answer 'Why does X exist?' question."""
        return self.query.why_exists(project_name)

    def query_context(self, project_name: str) -> Dict:
        """Get full context for a project."""
        return self.tracker.get_context(project_name)

    def list_projects(self) -> List[Dict]:
        """List all tracked projects."""
        return self.tracker.list_all()

    def visualize(self) -> str:
        """Get ASCII visualization."""
        return self.query.visualize()

    def get_stats(self) -> Dict:
        """Get system statistics."""
        stats = self.query.get_stats()
        stats["workspace"] = str(self.config.workspace_path)
        stats["knowledge_dir"] = str(self.config.knowledge_dir)
        return stats


def init_knowledge_system(workspace_path: Optional[str] = None) -> KnowledgeIntegration:
    """Initialize the knowledge system."""
    return KnowledgeIntegration(workspace_path)
