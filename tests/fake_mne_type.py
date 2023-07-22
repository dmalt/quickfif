"""Fake MneType implementation for testing."""
from dataclasses import asdict, dataclass
from pathlib import Path

from mne_cli_tools.config import Ftype


@dataclass
class FakeMneType(object):
    """Fake `MneType` implementation."""

    fpath: Path
    mne_obj: str

    def to_dict(self) -> dict[str, Path | Ftype]:
        """Convert do dictionary."""
        return asdict(self)
