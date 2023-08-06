"""Fake QfType implementation for testing."""
from dataclasses import asdict, dataclass
from pathlib import Path

from quickfif.config import Ftype


@dataclass
class FakeQfType(object):
    """Fake `QfType` implementation."""

    fpath: Path
    mne_obj: str

    @property
    def summary(self) -> str:
        """Fake object summary string."""
        return str(self)

    def to_dict(self) -> dict[str, Path | Ftype]:
        """Convert do dictionary."""
        return asdict(self)
