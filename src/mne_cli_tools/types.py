"""Custom types."""
from pathlib import Path
from typing import Any, Callable, NewType, Protocol

Ext = NewType("Ext", str)
Ftype = NewType("Ftype", str)
ReadableFpath = NewType("ReadableFpath", Path)


class MneType(Protocol):
    """Protocol for defining supported types."""

    def __str__(self) -> str:  # pyright: ignore
        """Convert object to string."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc] # allow Any here
        """Convert object to dictionary."""


TypeConstructors = dict[Ftype, Callable[[Path], MneType]]
