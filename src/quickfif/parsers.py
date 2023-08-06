"""
Bridge between Click API and the package core.

Hides all the monadic operations and transforms exceptions wrapped in Result
into click exceptions which cause graceful app termination.

"""
from pathlib import Path

from quickfif.config import EXT_TO_FTYPE, Ftype


def parse_ftype(fpath: Path) -> Ftype:
    """
    Parse Ftype from file name using predefined file extensions.

    Parameters
    ----------
    fpath
        File path

    Returns
    -------
    Ftype
        Parsed file type enum

    Raises
    ------
    quickfif.api.UnsupportedFtypeError
        If fname doesn't end with one of the extensions provided by e2f

    Examples
    --------
    >>> from pathlib import Path
    >>> assert parse_ftype(Path("rec_raw.fif")) == Ftype.raw
    >>> parse_ftype(Path("rec.txt"))
    Traceback (most recent call last):
        ...
    ValueError

    """
    for ext, ftype in EXT_TO_FTYPE.items():
        if fpath.name.endswith(ext):
            return ftype
    raise ValueError
