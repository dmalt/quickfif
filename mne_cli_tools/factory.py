from typing import Callable

from .mne_types import MneType
from .mne_types.unsupported import Unsupported

registered_types: dict[str, Callable[[str], MneType]] = {}


def register(type: str, constructor: Callable[[str], MneType]) -> None:
    registered_types[type] = constructor


def unregister(type: str) -> None:
    registered_types.pop(type, None)


def create(fname: str) -> MneType:
    for ext, mne_type_creator in registered_types.items():
        if fname.endswith(ext):
            break
    else:
        mne_type_creator = Unsupported
    return mne_type_creator(fname)
