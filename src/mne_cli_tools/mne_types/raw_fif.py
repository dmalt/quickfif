"""Plugin handling `mne.io.RawFif`."""
from dataclasses import asdict, dataclass
from pathlib import Path

from mne.io import Raw, read_raw_fif
from returns.io import impure_safe

from mne_cli_tools.mne_types.annotations import get_annots_summary


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
            res.append(get_annots_summary(self.raw.annotations))
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


@impure_safe
def read(fpath: Path) -> RawFif:
    """Read raw object."""
    raw = read_raw_fif(fpath, verbose="ERROR")  # noqa: WPS601
    return RawFif(fpath, raw)
