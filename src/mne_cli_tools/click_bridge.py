from enum import IntEnum, unique
from pathlib import Path
from typing import Mapping

import click
from returns.curry import partial
from returns.functions import raise_exception
from returns.io import IO
from returns.pipeline import flow
from returns.pointfree import alt

from mne_cli_tools.config import ext_to_ftype, ftype_to_read_func
from mne_cli_tools.types import Ext, Ftype, MneType


@unique
class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    ok = 0
    aborted = 1
    bad_fname_arg = 2
    broken_file = 3
    unsupported_file = 4


class UnsupportedFtypeError(click.FileError):
    """Click error for unknown file extension."""

    def __init__(self, fpath: str):
        hint = (
            "Can`t determine file type by extension"
            + " Try specifying the type manually via --ftype option."
        )
        super().__init__(fpath, hint=hint)
        self.exit_code = ExitCode.unsupported_file


class BrokenFileError(click.FileError):
    """Click error for broken file."""

    def __init__(self, fpath: str, exc: Exception):
        super().__init__(fpath, hint=str(exc))
        self.exit_code = ExitCode.broken_file


def read_mne_obj(fpath: Path, ftype: str | None) -> IO[MneType]:
    """Read mne object. For broken files raise click exception."""
    if ftype is None:
        ftype = _parse_ftype(str(fpath), ext_to_ftype)
    else:
        ftype = Ftype(ftype)
    # Hackish. Ftype() theoretically can fail for bad ftype string but never should
    # because click.Choice is aligned with Ftype enum Enum-based choice
    # type should appear in click 8.2.0, see https://github.com/pallets/click/pull/2210
    read_func = ftype_to_read_func[ftype]
    to_click_error = partial(BrokenFileError, str(fpath))
    return flow(fpath, read_func, alt(to_click_error), alt(raise_exception)).unwrap()


def _parse_ftype(fname: str, e2f: Mapping[Ext, Ftype]) -> Ftype:
    """
    Match first `fname` extension against the provided `extensions`.

    Examples
    --------
    >>> from mne_cli_tools.config import ext_to_ftype
    >>> assert _parse_ftype("rec_raw.fif", ext_to_ftype) == Ftype.raw
    >>> _parse_ftype("rec.txt", ext_to_ftype)
    Traceback (most recent call last):
        ...
    mne_cli_tools.click_bridge.UnsupportedFtypeError: Can`t determine file type...

    """
    for ext, ftype in e2f.items():
        if fname.endswith(ext):
            return ftype
    raise UnsupportedFtypeError(fname)
