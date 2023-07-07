"""Plugin handling `mne.Epochs`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.epochs import EpochsFIF, read_epochs

from mne_cli_tools.types import Ext, Ftype

EXTENSIONS: Final = (Ext("-epo.fif"), Ext("_epo.fif"))
FTYPE_ALIAS: Final = Ftype("epochs")


@dataclass
class EpochsFif(object):
    """MneType implementation for `mne.Epochs`."""

    fpath: Path
    epochs: EpochsFIF

    def __str__(self) -> str:
        """Provide `mne.Epochs` object summary."""
        return str(self.epochs.info)

    def to_dict(self) -> dict[str, Path | EpochsFIF]:
        """Convert to namespace dictionary."""
        return asdict(self)


def read(fpath: Path) -> EpochsFif:  # pyright: ignore
    """Read epochs."""
    ep = read_epochs(str(fpath), verbose="ERROR")  # noqa: WPS601
    return EpochsFif(fpath, ep)
