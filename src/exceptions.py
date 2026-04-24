"""Error handling and custom exceptions."""


class KnowledgeSystemError(Exception):
    """Base exception for knowledge system errors."""
    pass


class ProjectNotFoundError(KnowledgeSystemError):
    """Raised when a project is not found."""
    pass


class InvalidProjectError(KnowledgeSystemError):
    """Raised when project data is invalid."""
    pass


class StateLoadError(KnowledgeSystemError):
    """Raised when state cannot be loaded."""
    pass


class StateSaveError(KnowledgeSystemError):
    """Raised when state cannot be saved."""
    pass
