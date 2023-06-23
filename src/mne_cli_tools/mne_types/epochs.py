from dataclasses import asdict, dataclass, field

import mne  # type: ignore

from .. import factory


@dataclass
class EpochsFif:
    fname: str
    epochs: mne.Epochs = field(init=False)

    def __post_init__(self):
        self.epochs = mne.read_epochs(self.fname, verbose="ERROR")  # pyright: ignore

    def __str__(self):
        return str(self.epochs.info)

    def to_dict(self):
        return asdict(self)


def initialize(extensions: list[str]) -> None:
    for ext in extensions:
        factory.register(ext, EpochsFif)
