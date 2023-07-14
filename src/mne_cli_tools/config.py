"""Configure MneType objects creation for supported file types."""
import operator as op
from enum import IntEnum, unique
from functools import reduce
from pathlib import Path
from typing import Callable, Final

from returns.io import IOResult, IOResultE
from returns.maybe import Maybe

from mne_cli_tools.mne_types import annotations, epochs, ica, raw_fif
from mne_cli_tools.files import match_ext
from mne_cli_tools.types import Ext, Ftype, MneType

MODULES: Final = (annotations, epochs, ica, raw_fif)
EXTENSIONS: Final[tuple[Ext, ...]] = reduce(op.add, (m.EXTENSIONS for m in MODULES))


ReaderFunc = Callable[[Path], IOResultE[MneType]]
reader: dict[Ftype, ReaderFunc] = {}
ext2ftype: dict[Ext, Ftype] = {}
ftype2ext: dict[Ftype, tuple[Ext, ...]] = {}


for mdl in MODULES:
    reader[mdl.FTYPE_ALIAS] = mdl.read
    ftype2ext[mdl.FTYPE_ALIAS] = mdl.EXTENSIONS
    ext2ftype.update(**{ext: mdl.FTYPE_ALIAS for ext in mdl.EXTENSIONS})


def create(fpath: Path, ftype: Maybe[Ftype]) -> IOResultE[MneType]:
    """Create an instance of MNE object. If ext isn`t provided, match it from fpath."""
    # fmt: off
    return Maybe.do(
        reader[ft](fpath) for ft in ftype
    ).value_or(_create_auto(fpath))
    # fmt: on


def _create_auto(fpath: Path) -> IOResultE[MneType]:
    """Create an instance of MNE object automatically inferring the type."""
    return IOResult.from_result(
        match_ext(str(fpath), extensions=EXTENSIONS),
    ).bind(lambda ext: reader[ext2ftype[ext]](fpath))


@unique
class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    ok = 0
    aborted = 1
    bad_fname_arg = 2
    broken_file = 3
    unsupported_file = 4
