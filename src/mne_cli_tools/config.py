"""Configure MneType objects creation for supported file types."""
import operator as op
from enum import IntEnum, unique
from functools import reduce
from pathlib import Path
from typing import Callable, Final

from mne_cli_tools.mne_types import annotations, epochs, ica, raw_fif
from mne_cli_tools.types import Ext, Ftype, MneType

MODULES: Final = (annotations, epochs, ica, raw_fif)
EXTENSIONS: Final = reduce(op.add, (mo.EXTENSIONS for mo in MODULES))
FTYPES: Final = tuple(mo.FTYPE_ALIAS for mo in MODULES)

type_constructors: dict[Ftype, Callable[[Path], MneType]] = {}
ext2ftype: dict[Ext, Ftype] = {}
ftype2ext: dict[Ftype, tuple[Ext, ...]] = {}

for mdl in MODULES:
    type_constructors[mdl.FTYPE_ALIAS] = mdl.read
    ftype2ext[mdl.FTYPE_ALIAS] = mdl.EXTENSIONS
    ext2ftype.update(**{ext: mdl.FTYPE_ALIAS for ext in mdl.EXTENSIONS})


@unique
class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    ok = 0
    aborted = 1
    bad_fname_arg = 2
    broken_file = 3
