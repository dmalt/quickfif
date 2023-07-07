"""Plugin handling `mne.io.RawFif`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.io import Raw, read_raw_fif

from mne_cli_tools.mne_types.annotations import get_annots_pandas_summary
from mne_cli_tools.types import Ext, Ftype

EXTENSIONS: Final = tuple(
    Ext(ext)
    for ext in (
        "_raw.fif",
        "_raw.fif.gz",
        "-raw.fif",
        "-raw.fif.gz",
        "_raw_sss.fif",
        "_raw_sss.fif.gz",
        "-raw_sss.fif",
        "-raw_sss.fif.gz",
        "_raw_tsss.fif",
        "_raw_tsss.fif.gz",
        "-raw_tsss.fif",
        "-raw_tsss.fif.gz",
        "_meg.fif",
        "_meg.fif.gz",
        "-meg.fif",
        "_eeg.fif",
        "-eeg.fif",
        "_eeg.fif.gz",
        "_ieeg.fif",
        "_ieeg.fif.gz",
        "-ieeg.fif",
    )
)
FTYPE_ALIAS: Final = Ftype("raw")


def get_raw_summary(raw: Raw) -> str:
    """Get Raw object text summary."""
    duration_sec = raw.times[-1]
    n_samp = len(raw.times)
    size = {"n_chan": len(raw.ch_names), "n_samp": n_samp, "n_sec": duration_sec}
    header = "Raw data of shape {n_chan} channels x {n_samp} samples ({n_sec} s)".format(**size)
    return "\n".join([header, "-" * len(header)])


@dataclass
class RawFif(object):
    """MneType implementation for `mne.io.Raw` object."""

    fpath: Path
    raw: Raw

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
            dst_path = dst_path / self.fpath.name
        self.raw.save(dst_path, overwrite=True)

    def to_dict(self) -> dict[str, str | Raw]:
        """Convert to namespace dictionary."""
        return asdict(self)


def read(fpath: Path) -> RawFif:
    """Read raw object."""
    raw = read_raw_fif(fpath, verbose="ERROR")  # noqa: WPS601
    return RawFif(fpath, raw)
