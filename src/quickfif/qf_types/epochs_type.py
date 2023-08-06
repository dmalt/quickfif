"""Plugin handling `mne.Epochs`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.epochs import EpochsFIF, read_epochs

BIDS_EXT: Final = ("_epo.fif",)
NEUROMAG_EXT: Final = ("-epo.fif",)
EXTENSIONS: Final[tuple[str, ...]] = BIDS_EXT + NEUROMAG_EXT


@dataclass
class QfEpochs(object):
    """QfType implementation for `mne.Epochs`."""

    fpath: Path
    epochs: EpochsFIF

    @property
    def summary(self) -> str:
        """Provide `mne.Epochs` object summary."""
        return str(self.epochs.info)

    def to_dict(self) -> dict[str, Path | EpochsFIF]:
        """Convert to namespace dictionary."""
        return asdict(self)


def read(fpath: Path) -> QfEpochs:  # pyright: ignore
    """Read epochs."""
    ep = read_epochs(str(fpath), verbose="ERROR")  # noqa: WPS601
    return QfEpochs(fpath, ep)


def save(qf_obj: QfEpochs, dst: Path, overwrite: bool, split_size: str = "2GB") -> None:
    """Save epochs file in a split-safe manner."""
    if dst.is_dir():
        dst = dst / qf_obj.fpath.name
    split_naming = "bids" if str(dst).endswith(BIDS_EXT) else "neuromag"

    qf_obj.epochs.save(
        fname=dst, overwrite=overwrite, split_naming=split_naming, split_size=split_size
    )
