"""Custom project-level types."""
from pathlib import Path
from typing import Any, Protocol


class QfType(Protocol):
    """Protocol for defining supported types."""

    fpath: Path

    @property
    def summary(self) -> str:  # pyright: ignore
        """Convert object to string."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc] # allow Any here
        """Convert object to dictionary."""
