"""Bridge between Click API and the package core."""
from pathlib import Path
from typing import Mapping

import click
from returns.curry import partial
from returns.functions import raise_exception
from returns.io import IO, IOResult
from returns.pipeline import flow
from returns.pointfree import alt, bind

from mne_cli_tools.api.errors import BrokenFileError, UnsupportedFtypeError, WriteFailedError
from mne_cli_tools.config import Ftype, copy, ext_to_ftype, ftype_to_read_func
from mne_cli_tools.ipython import embed_ipython
from mne_cli_tools.types import Ext, MneType


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


def show_preview(mne_obj: IO[MneType]) -> IO[None]:
    """Print preview string."""
    return mne_obj.map(click.echo)


def open_in_console(mne_obj: IO[MneType]) -> IO[None]:
    """Open object for inspection in embedded ipython console."""
    return mne_obj.bind(lambda x: embed_ipython(x.to_dict()))


def safe_copy(mne_obj: IO[MneType], dst: Path) -> IO[None]:
    """Safely copy object.

    Handles raw.fif problem with splits when copying.

    """
    to_click_error = partial(WriteFailedError, str(dst))
    return flow(
        IOResult.from_io(mne_obj),
        bind(partial(copy, dst=dst)),
        alt(to_click_error),
        alt(raise_exception),
    ).unwrap()


def _parse_ftype(fname: str, e2f: Mapping[Ext, Ftype]) -> Ftype:
    """
    Parse Ftype from file name using predefined file extensions.

    Parameters
    ----------
    fname
        File name
    e2f
        Mapping from extension to the associated Ftype

    Returns
    -------
    Ftype
        Parsed file type enum

    Raises
    ------
    mne_cli_tools.api.UnsupportedFtypeError
        If fname doesn't end with one of the extensions provided by e2f

    Examples
    --------
    >>> from mne_cli_tools.config import ext_to_ftype
    >>> assert _parse_ftype("rec_raw.fif", ext_to_ftype) == Ftype.raw
    >>> _parse_ftype("rec.txt", ext_to_ftype)
    Traceback (most recent call last):
        ...
    mne_cli_tools.api.errors.UnsupportedFtypeError: Can`t determine file type by extension.
    Try specifying the type manually via --ftype option.

    """
    for ext, ftype in e2f.items():
        if fname.endswith(ext):
            return ftype
    raise UnsupportedFtypeError(fname)
