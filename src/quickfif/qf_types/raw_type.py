"""Plugin handling `mne.io.QfRaw`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from mne.io import Raw, read_raw_fif

from quickfif.qf_types.annots_type import get_annots_summary

_NMG_SFX = ("raw", "raw_sss", "raw_tsss")
_BIDS_SFX = ("_meg", "_eeg", "_ieeg")
_EXT = (".fif", ".fif.gz")

NEUROMAG_EXT: Final = tuple(f"{sfx}{ext}" for sfx in _NMG_SFX for ext in _EXT)
BIDS_EXT: Final = tuple(f"{sfx}{ext}" for sfx in _BIDS_SFX for ext in _EXT)

EXTENSIONS: Final[tuple[str, ...]] = NEUROMAG_EXT + BIDS_EXT
ANNOTS_SECTION_HEADER: Final = "Annotated segments statistics"
NO_ANNOTS_MSG: Final = "No annotated segments"


def _get_raw_summary(raw: Raw) -> str:
    """Get Raw object text summary."""
    duration_sec = round(raw.times[-1], 2)
    n_samp = len(raw.times)
    size = {"n_chan": len(raw.ch_names), "n_samp": n_samp, "n_sec": duration_sec}
    header = "Raw data of shape {n_chan} channels x {n_samp} samples ({n_sec} s)".format(**size)
    return "\n".join([header, "-" * len(header)])


@dataclass
class QfRaw(object):
    """QfType implementation for `mne.io.Raw` object."""

    fpath: Path
    raw: Raw

    @property
    def summary(self) -> str:
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


def read(fpath: Path) -> QfRaw:
    """Read raw object."""
    raw = read_raw_fif(fpath, verbose="ERROR")  # noqa: WPS601
    return QfRaw(fpath, raw)


def save(qf_obj: QfRaw, dst: Path, overwrite: bool, split_size: str = "2GB") -> None:
    """Save raw file in a split-safe manner."""
    if dst.is_dir():
        dst = dst / qf_obj.fpath.name
    split_naming = "bids" if str(dst).endswith(BIDS_EXT) else "neuromag"

    qf_obj.raw.save(
        fname=dst, overwrite=overwrite, split_naming=split_naming, split_size=split_size
    )
