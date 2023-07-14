"""Utils to manipulate `Path` objects and their string representations."""

from typing import Final, Iterable

from returns.result import safe

from mne_cli_tools.types import Ext

MSG: Final = (
    "Can`t determine file type by extension for '{0}.'"
    + " Try specifying the type manually via --ftype option."
)


class UnsupportedFtypeError(Exception):
    """Error when file extension is not known."""


@safe
def match_ext(fname: str, extensions: Iterable[str]) -> Ext:
    """
    Match first `fname` extension against the provided `extensions`.

    Examples
    --------
    >>> from returns.result import Success, Failure
    >>> from mne_cli_tools.files import UnsupportedFtypeError
    >>> assert match_ext("rec_raw.fif", ["_raw.fif"]) == Success("_raw.fif")
    >>> assert isinstance(match_ext("rec.txt", ["_raw.fif"]).failure(), UnsupportedFtypeError)

    """
    for ext in extensions:
        if fname.endswith(ext):
            return ext

    raise UnsupportedFtypeError(MSG.format(fname))
