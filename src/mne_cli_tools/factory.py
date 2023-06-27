"""Manage creation of MNE objects."""
from typing import Callable, Iterable

import click

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
    maybe_ext = _match_ext(fname, registered_types)
    if maybe_ext is None:
        return Unsupported(fname)
    mne_type_creator = registered_types[maybe_ext]
    try:
        return mne_type_creator(fname)
    except Exception as exc:
        raise click.FileError(fname, hint=str(exc))


def _match_ext(fname: str, extensions: Iterable[str]) -> str | None:
    for ext in extensions:
        if fname.endswith(ext):
            return ext
    return None


def create_by_ext(fname: str, ext: str) -> MneType:
    """Get object type by filename extension and construct it."""
    mne_type_creator = registered_types.get(ext, Unsupported)
    return mne_type_creator(fname)
