"""Incremental state persistence for performance."""

import json
import logging
from pathlib import Path
from typing import Set
from datetime import datetime

from .exceptions import StateSaveError, StateLoadError


class IncrementalPersistence:
    """Handles incremental state saves (only changed data)."""

    def __init__(self, state_file: Path, logger=None):
        self.state_file = state_file
        self.logger = logger or logging.getLogger(__name__)
        self.dirty_projects: Set[str] = set()
        self.last_save = None

    def mark_dirty(self, project_name: str) -> None:
        """Mark a project as modified."""
        self.dirty_projects.add(project_name)

    def save(self, system, force_full: bool = False) -> None:
        """Save system state (uses system's native save)."""
        try:
            # Use system's native save method (handles serialization correctly)
            system.save(str(self.state_file))

            num_dirty = len(self.dirty_projects)
            self.dirty_projects.clear()
            self.last_save = datetime.now()

            if num_dirty > 0:
                self.logger.debug(f"Saved state ({num_dirty} projects modified)")
            else:
                self.logger.debug("Saved state (no changes)")

        except Exception as e:
            raise StateSaveError(f"Failed to save state: {e}")

    def load(self, system) -> bool:
        """Load system state from disk."""
        if not self.state_file.exists():
            return False

        try:
            system.load(str(self.state_file))
            self.last_save = datetime.now()
            self.logger.info(f"Loaded existing knowledge from {self.state_file}")
            return True
        except json.JSONDecodeError as e:
            # Corrupted JSON file - create backup and start fresh
            backup_file = self.state_file.with_suffix('.json.corrupted')
            self.logger.error(f"Corrupted state file detected: {e}")
            self.logger.info(f"Creating backup at {backup_file}")
            try:
                self.state_file.rename(backup_file)
                self.logger.warning("Starting with fresh state due to corruption")
                return False
            except Exception as backup_error:
                self.logger.error(f"Failed to backup corrupted file: {backup_error}")
                raise StateLoadError(f"Corrupted state file and backup failed: {e}") from e
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            raise StateLoadError(f"Failed to load state: {e}") from e
