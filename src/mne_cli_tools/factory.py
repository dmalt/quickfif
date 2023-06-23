"""Manage creation of MNE objects."""
from typing import Callable

from mne_cli_tools.mne_types.base import MneType, Unsupported

registered_types: dict[str, Callable[[str], MneType]] = {}


def register(ext: str, constructor: Callable[[str], MneType]) -> None:
    """Register constructor for a specified extension."""
    registered_types[ext] = constructor


def unregister(ext: str) -> None:
    """Unregister extension."""
    registered_types.pop(ext, None)


def create(fname: str, ext: str | None) -> MneType:
    """Create an instance of MNE object. If ext is not provided, infer it."""
    return create_by_ext(fname, ext) if ext else create_auto(fname)


def create_auto(fname: str) -> MneType:
    """Automatically infer object type from fname and construct it."""
    for ext, mne_type_creator in registered_types.items():
        if fname.endswith(ext):
            return mne_type_creator(fname)
    return Unsupported(fname)


def create_by_ext(fname: str, ext: str) -> MneType:
    """Get object type by filename extension and construct it."""
    mne_type_creator = registered_types.get(ext, Unsupported)
    return mne_type_creator(fname)
