"""Plugin handling `mne.preprocessing.ICA`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.preprocessing import ICA, read_ica

EXTENSIONS: Final[tuple[str, ...]] = ("_ica.fif", "-ica.fif")


@dataclass
class IcaFif(object):
    """MctType implementation for `mne.preprocessing.ICA`."""

    fpath: Path
    ica: ICA

    @property
    def summary(self) -> str:
        """ICA object summary."""
        return str(self.ica)

    def to_dict(self) -> dict[str, Path | ICA]:
        """Convert to namespace dictionary."""
        return asdict(self)


def read(fpath: Path) -> IcaFif:
    """Read ICA solution."""
    ica = read_ica(str(fpath), verbose="ERROR")  # noqa: WPS601
    return IcaFif(fpath, ica)
