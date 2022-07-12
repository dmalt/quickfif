from dataclasses import asdict, dataclass, field
from pathlib import Path

import mne  # type: ignore

from .. import factory
from .annotations import get_annots_pandas_summary_str


def get_raw_summary_str(raw: mne.io.Raw):
    header = (
        "Raw data of shape "
        + f"{len(raw.ch_names)} channels x {len(raw.times)} samples ({raw.times[-1]} s)"
    )
    return "\n".join([header, "-" * len(header)])


@dataclass
class RawFif:
    fname: str
    raw: mne.io.Raw = field(init=False)

    def __post_init__(self):
        self.raw = mne.io.read_raw_fif(self.fname, verbose="ERROR")

    def __str__(self):
        res = [get_raw_summary_str(self.raw), str(self.raw.info)]
        if self.raw.annotations:
            res.append("Annotated segments statistics")
            res.append("-----------------------------")
            res.append(str(get_annots_pandas_summary_str(self.raw.annotations)))
        else:
            res.append("No annotated segments")
        return "\n".join(res)

    def copy(self, dst: str):
        dst_path = Path(dst)
        if dst_path.is_dir():
            dst_path = dst_path / Path(self.fname).name
        self.raw.save(dst_path, overwrite=True)

    def to_dict(self):
        return asdict(self)


def initialize():
    factory.register("raw.fif", RawFif)
    factory.register("raw_sss.fif", RawFif)
    factory.register("raw_tsss.fif", RawFif)
    factory.register("_meg.fif", RawFif)
    factory.register("_eeg.fif", RawFif)
    factory.register("_ieeg.fif", RawFif)
    factory.register("raw.fif.gz", RawFif)
    factory.register("raw_sss.fif.gz", RawFif)
    factory.register("raw_tsss.fif.gz", RawFif)
    factory.register("_meg.fif.gz", RawFif)
    factory.register("_eeg.fif.gz", RawFif)
    factory.register("_ieeg.fif.gz", RawFif)
