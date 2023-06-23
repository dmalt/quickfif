from dataclasses import asdict, dataclass, field

import mne  # type: ignore

from .. import factory


@dataclass
class IcaFif:
    fname: str
    ica: mne.preprocessing.ICA = field(init=False)

    def __post_init__(self):
        self.ica = mne.preprocessing.read_ica(self.fname, verbose="ERROR")

    def __str__(self):
        return str(self.ica)

    def to_dict(self):
        return asdict(self)


def initialize(extensions: list[str]) -> None:
    for ext in extensions:
        factory.register(ext, IcaFif)
