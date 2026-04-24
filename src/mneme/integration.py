"""Main integration interface."""

from typing import Dict, List, Optional
from pathlib import Path

from .config import Config
from .logging_config import setup_logger
from .project_tracker import ProjectTracker
from .query_interface import QueryInterface
from .incremental_persistence import IncrementalPersistence
from .exceptions import KnowledgeSystemError
from .global_knowledge_system import GlobalKnowledgeSystem


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
        # Input validation
        if not project_name or not project_name.strip():
            raise KnowledgeSystemError("project_name cannot be empty")
        if not reason or not reason.strip():
            raise KnowledgeSystemError("reason cannot be empty")

        try:
            result = self.tracker.track_creation(
                project_name, reason, created_for, causal_chain, technologies
            )
            # Mark project as dirty for incremental save
            self.persistence.mark_dirty(project_name)
            self.persistence.save(self.system)
            # Invalidate cache for this project
            self.query.invalidate_cache(project_name)
            return result
        except Exception as e:
            self.logger.error(f"Failed to track project {project_name}: {e}")
            raise KnowledgeSystemError(f"Failed to track project: {e}") from e

    def add_relationship(self, subject: str, relation: str, obj: str) -> None:
        """Add relationship between projects."""
        # Input validation
        if not subject or not subject.strip():
            raise KnowledgeSystemError("subject cannot be empty")
        if not relation or not relation.strip():
            raise KnowledgeSystemError("relation cannot be empty")
        if not obj or not obj.strip():
            raise KnowledgeSystemError("object cannot be empty")

        try:
            self.tracker.add_relationship(subject, relation, obj)
            # Mark both projects as dirty
            self.persistence.mark_dirty(subject)
            self.persistence.mark_dirty(obj)
            self.persistence.save(self.system)
            # Invalidate cache for both projects
            self.query.invalidate_cache(subject)
            self.query.invalidate_cache(obj)
        except Exception as e:
            self.logger.error(f"Failed to add relationship {subject}-{relation}-{obj}: {e}")
            raise KnowledgeSystemError(f"Failed to add relationship: {e}") from e

    def why_does_exist(self, project_name: str) -> str:
        """Answer 'Why does X exist?' question."""
        if not project_name or not project_name.strip():
            raise KnowledgeSystemError("project_name cannot be empty")

        try:
            return self.query.why_exists(project_name)
        except Exception as e:
            self.logger.error(f"Failed to query why {project_name} exists: {e}")
            return f"Error retrieving information for {project_name}: {e}"

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
