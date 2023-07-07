"""Manage creation of MNE objects."""
from pathlib import Path
from typing import Iterable

import click

from mne_cli_tools.config import ExitCode, ext2ftype
from mne_cli_tools.mne_types.base import Unsupported
from mne_cli_tools.types import Ext, Ftype, MneType, TypeConstructors


def create(fpath: Path, ftype: Ftype | None, type_constructors: TypeConstructors) -> MneType:
    """Create an instance of MNE object. If ext is not provided, match it from fpath."""
    return create_by_ftype(fpath, ftype, type_constructors) if ftype else create_auto(fpath, type_constructors)


def create_auto(fpath: Path, type_constructors: TypeConstructors) -> MneType:
    """Automatically infer object type from fpath and construct it."""
    ext = match_ext(str(fpath), ext2ftype)
    if ext is None:
        return Unsupported(fpath)  # pyright: ignore
    return create_by_ftype(fpath, ext2ftype[ext], type_constructors)


def create_by_ftype(fpath: Path, ftype: Ftype, constructors: TypeConstructors) -> MneType:
    """Get object type by filename extension and construct it."""
    constructor = constructors.get(ftype, Unsupported)
    try:
        return constructor(fpath)
    except Exception as exc:
        click_exc = click.FileError(str(fpath), hint=str(exc))
        click_exc.exit_code = ExitCode.broken_file
        raise click_exc


def match_ext(fname: str, extensions: Iterable[Ext]) -> Ext | None:
    """
    Match first `fname` extension against the provided `extensions`.

    Examples
    --------
    >>> print(match_ext("rec_raw.fif", ["_raw.fif"]))
    _raw.fif
    >>> print(match_ext("rec.txt", ["_raw.fif"]))
    None

    """
    for ext in extensions:
        if fname.endswith(ext):
            return ext
    return None
