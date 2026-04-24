"""Configuration management for the knowledge system."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """System configuration."""

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.knowledge_dir = self.workspace_path / ".claude" / "knowledge"
        self.projects_dir = self.knowledge_dir / "projects"
        self.state_file = self.knowledge_dir / "system_state.json"
        self.dims = 10000

    def ensure_dirs(self):
        """Create necessary directories."""
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
