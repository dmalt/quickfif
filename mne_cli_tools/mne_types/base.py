"""Base abstractions."""
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class MneType(Protocol):
    """Protocol for defining supported types."""

    def __str__(self) -> str:  # pyright: ignore
        """Convert object to string."""

    def to_dict(self) -> dict[str, Any]:  # pyright: ignore
        """Convert object to dictionary."""


@dataclass
class Unsupported(object):
    """Wrapper for unsupported file types."""

    fname: str

    def __str__(self) -> str:
        """Return string representation."""
        return "Unsupported format for {0}".format(self.fname)

    def to_dict(self) -> dict[str, str]:
        """Convert object to dictionary."""
        return asdict(self)
