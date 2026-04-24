"""State persistence management."""

import json
import logging
from pathlib import Path

from .exceptions import StateLoadError, StateSaveError


class StatePersistence:
    """Handles saving and loading system state."""

    def __init__(self, state_file: Path, logger=None):
        self.state_file = state_file
        self.logger = logger or logging.getLogger(__name__)

    def save(self, system) -> None:
        """Save system state to disk."""
        try:
            system.save(str(self.state_file))
            self.logger.debug(f"State saved to {self.state_file}")
        except Exception as e:
            raise StateSaveError(f"Failed to save state: {e}")

    def load(self, system) -> bool:
        """Load system state from disk."""
        if not self.state_file.exists():
            return False

        try:
            system.load(str(self.state_file))
            self.logger.info(f"Loaded existing knowledge from {self.state_file}")
            return True
        except Exception as e:
            raise StateLoadError(f"Failed to load state: {e}")
