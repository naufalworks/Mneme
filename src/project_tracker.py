"""Project tracking and querying."""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from .exceptions import ProjectNotFoundError


class ProjectTracker:
    """Handles project tracking operations."""

    def __init__(self, system, logger=None):
        self.system = system
        self.logger = logger or logging.getLogger(__name__)

    def track_creation(self,
                      project_name: str,
                      reason: str,
                      created_for: Optional[str] = None,
                      causal_chain: Optional[List[str]] = None,
                      technologies: Optional[List[str]] = None) -> Dict:
        """Track project creation."""
        self.logger.info(f"Tracking project: {project_name}")

        domain_concepts = [project_name]
        if technologies:
            domain_concepts.extend(technologies)

        result = self.system.create_project(
            name=project_name,
            reason=reason,
            created_for=created_for,
            domain_concepts=domain_concepts,
            causal_chain=causal_chain
        )

        if created_for:
            self.logger.info(f"  → Created for: {created_for}")
        if causal_chain:
            self.logger.info(f"  → Causal chain: {len(causal_chain)} steps")

        return result

    def add_relationship(self, subject: str, relation: str, obj: str) -> None:
        """Add relationship between projects."""
        self.system.add_project_fact(subject, subject, relation, obj)
        self.logger.info(f"Added: {subject} {relation} {obj}")

    def get_context(self, project_name: str) -> Dict:
        """Get full context for a project."""
        context = self.system.get_project_context(project_name)
        if not context or 'error' in context:
            raise ProjectNotFoundError(f"Project not found: {project_name}")
        return context

    def list_all(self) -> List[Dict]:
        """List all tracked projects."""
        projects = []
        for name, info in self.system.projects.items():
            projects.append({
                "name": name,
                "reason": info["reason"],
                "created_for": info.get("created_for"),
                "created_at": info.get("created_at")
            })
        return projects
