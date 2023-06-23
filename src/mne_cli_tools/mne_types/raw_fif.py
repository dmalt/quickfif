"""Plugin handling mne.io.RawFif."""
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import mne  # type: ignore

from mne_cli_tools import factory
from mne_cli_tools.mne_types.annotations import get_annots_pandas_summary


def get_raw_summary(raw: mne.io.Raw) -> str:
    """Get Raw object text summary."""
    duration_sec = raw.times[-1]
    n_samp = len(raw.times)
    size = {"n_chan": len(raw.ch_names), "n_samp": n_samp, "n_sec": duration_sec}
    header = "Raw data of shape {n_chan} channels x {n_samp} samples ({n_sec} s)".format(**size)
    return "\n".join([header, "-" * len(header)])


@dataclass
class RawFif(object):
    """MneType implementation for mne.io.Raw object."""

    fname: str
    raw: mne.io.Raw = field(init=False)

    def __post_init__(self):
        """Read raw object."""
        self.raw = mne.io.read_raw_fif(self.fname, verbose="ERROR")  # noqa: WPS601

    def __str__(self) -> str:
        """Raw object summary."""
        res = [get_raw_summary(self.raw), str(self.raw.info)]
        if self.raw.annotations:
            res.append("Annotated segments statistics")
            res.append("-----------------------------")
            res.append(str(get_annots_pandas_summary(self.raw.annotations)))
        else:
            res.append("No annotated segments")
        return "\n".join(res)

    def copy(self, dst: str) -> None:
        """Copy raw file in a split-safe manner."""
        dst_path = Path(dst)
        if dst_path.is_dir():
            dst_path = dst_path / Path(self.fname).name
        self.raw.save(dst_path, overwrite=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def initialize(extensions: Iterable[str]) -> None:
    """Register supported extensions."""
    for ext in extensions:
        factory.register(ext, RawFif)
