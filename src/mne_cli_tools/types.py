"""Custom project-level types."""
from pathlib import Path
from typing import Any, NewType, Protocol, TypeAlias


ReadableFpath = NewType("ReadableFpath", Path)
Ext: TypeAlias = "str"


class MneType(Protocol):
    """Protocol for defining supported types."""

    def __str__(self) -> str:  # pyright: ignore
        """Convert object to string."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc] # allow Any here
        """Convert object to dictionary."""
