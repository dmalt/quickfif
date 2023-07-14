"""Custom project-level types."""
from enum import StrEnum
from pathlib import Path
from typing import Any, NewType, Protocol, TypeAlias


class Ftype(StrEnum):
    """
    Supported file types.

    We use string values of this enum as click.Choice variants for the ftype
    option. They appear as a part of CLI help message.

    """

    ica = "ica"
    raw = "raw"
    annots = "annots"
    epochs = "epochs"

    @classmethod
    def get_values(cls) -> list[str]:
        """Get values of the enum."""
        return [ft.value for ft in cls]


ReadableFpath = NewType("ReadableFpath", Path)
Ext: TypeAlias = "str"


class MneType(Protocol):
    """Protocol for defining supported types."""

    def __str__(self) -> str:  # pyright: ignore
        """Convert object to string."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc] # allow Any here
        """Convert object to dictionary."""
