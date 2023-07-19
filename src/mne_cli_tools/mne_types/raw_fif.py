"""Plugin handling `mne.io.RawFif`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.io import Raw, read_raw_fif
from returns.io import impure_safe

from mne_cli_tools.mne_types.annotations import get_annots_summary

_BASE_EXT = ("raw.fif", "raw_sss.fif", "raw_tsss.fif", "_meg.fif", "_eeg.fif", "_ieeg.fif")
_GZ_EXT = tuple(f"{e}.gz" for e in _BASE_EXT)

EXTENSIONS: Final[tuple[str, ...]] = _BASE_EXT + _GZ_EXT
ANNOTS_SECTION_HEADER: Final = "Annotated segments statistics"
NO_ANNOTS_MSG: Final = "No annotated segments"


def _get_raw_summary(raw: Raw) -> str:
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
        res = [_get_raw_summary(self.raw), str(self.raw.info)]
        if self.raw.annotations:
            res.append(ANNOTS_SECTION_HEADER)
            res.append("-" * len(ANNOTS_SECTION_HEADER))
            res.append(get_annots_summary(self.raw.annotations))
        else:
            res.append(NO_ANNOTS_MSG)
        return "\n".join(res)

    def to_dict(self) -> dict[str, str | Raw]:
        """Convert to namespace dictionary."""
        return asdict(self)


@impure_safe
def read(fpath: Path) -> RawFif:
    """Read raw object."""
    raw = read_raw_fif(fpath, verbose="ERROR")  # noqa: WPS601
    return RawFif(fpath, raw)


@impure_safe
def copy(mne_obj: RawFif, dst: Path) -> None:
    """Copy raw file in a split-safe manner."""
    if dst.is_dir():
        dst = dst / mne_obj.fpath.name
    mne_obj.raw.save(dst, overwrite=True)
