"""Plugin handling `mne.io.QfRaw`."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from mne.channels.channels import channel_indices_by_type
from mne.io import Raw, read_raw_fif

from quickfif.qf_types.annots_type import get_annots_summary

if TYPE_CHECKING:
    from mne import Info  # pragma: no cover

_NMG_SFX = ("raw", "raw_sss", "raw_tsss")
_BIDS_SFX = ("_meg", "_eeg", "_ieeg")
_EXT = (".fif", ".fif.gz")

NEUROMAG_EXT: Final = tuple(f"{sfx}{ext}" for sfx in _NMG_SFX for ext in _EXT)
BIDS_EXT: Final = tuple(f"{sfx}{ext}" for sfx in _BIDS_SFX for ext in _EXT)

EXTENSIONS: Final[tuple[str, ...]] = NEUROMAG_EXT + BIDS_EXT
ANNOTS_HEADER: Final = "{section:10} {sep}{msg}"


@dataclass
class QfRaw(object):
    """QfType implementation for `mne.io.Raw` object."""

    fpath: Path
    raw: Raw

    @property
    def summary(self) -> str:
        """Raw object summary."""
        res = _get_raw_header(self.raw.info, self.raw.times[-1])
        res.extend(_get_ch_summary(self.raw.info))
        res.extend(_get_misc_summary(self.raw.info))

        annots_msg = " duration stats, sec" if self.raw.annotations else " no annotations"
        res.append(ANNOTS_HEADER.format(section="Annotations", sep="|", msg=annots_msg))
        if self.raw.annotations:
            res.append(get_annots_summary(self.raw.annotations))
        return "\n".join(res)

    def to_dict(self) -> dict[str, str | Raw]:
        """Convert to namespace dictionary."""
        return asdict(self)


def _get_raw_header(ii: "Info", duration: float, sep: str = "|") -> list[str]:
    """Get summary header for raw file."""
    hdr = "{section} {sep} duration: {dur:.1f} sec, sampling rate: {fs:.1f} Hz"
    hdr = hdr.format(section="Raw", sep=sep, dur=duration, fs=ii["sfreq"])
    return [hdr, "-" * len(hdr)]


def _get_misc_summary(ii: "Info", sep: str = "|") -> list[str]:
    """Get filtering, experimenter and meas_date summary."""
    hdr = "{section:11} {sep} highpass: {highpass:.1f}, lowpass: {lowpass:.1f}"
    res = [hdr.format(section="Filter", sep=sep, **ii)]

    on = f"{ii['meas_date']:%d/%m/%Y, %H:%m}" if ii["meas_date"] else "N/A"  # noqa: WPS323
    by = ii["experimenter"] or "N/A"
    hdr = "{section:11} {sep}".format(section="Recorded", sep=sep)
    res.append(hdr + " by: {by}, on: {on}".format(by=by, on=on))
    return res


def _get_ch_summary(ii: "Info", sep: str = "|") -> list[str]:
    """Get channels number and composition summary."""
    hdr = "{section:11} {sep}".format(section="Channels", sep=sep)
    res = [hdr + " total: {n_ch}".format(n_ch=ii["nchan"])]

    type_idx = channel_indices_by_type(ii).items()
    type_idx = [(t, idx) for t, idx in type_idx if idx]  # filter empty subtypes

    for t, idx in sorted(type_idx, key=lambda x: -len(x[1])):  # noqa: WPS426
        ch_names = [ii["ch_names"][i] for i in idx]
        if len(ch_names) <= 4:
            ch_names_str = "".join([f"{name:10.10s}" for name in ch_names]).rstrip()
        else:
            ch_names_str = "{0:10.10s} {1:10.10s} {2:^10s} {3}".format(
                ch_names[0], ch_names[1], "...", ch_names[-1]
            )
        res.append("  {n_ch:3} {t:6}: {names}".format(n_ch=len(idx), t=t, names=ch_names_str))
    return res


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
