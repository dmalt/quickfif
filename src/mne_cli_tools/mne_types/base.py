"""Base abstractions."""
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Unsupported(object):
    """MneType implementation for unsupported file types."""

    fpath: Path

    def __str__(self) -> str:
        """Return string representation."""
        return "Unsupported file type for {0}".format(self.fpath)

    def to_dict(self) -> dict[str, Path]:
        """Convert object to dictionary."""
        return asdict(self)
