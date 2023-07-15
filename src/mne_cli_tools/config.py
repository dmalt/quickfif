"""Configure MneType objects creation for supported file types."""
import operator as op
from functools import reduce
from pathlib import Path
from typing import Callable, Final

from returns.io import IOResultE

from mne_cli_tools.mne_types import annotations, epochs, ica, raw_fif
from mne_cli_tools.types import Ext, Ftype, MneType

MODULES: Final = (annotations, epochs, ica, raw_fif)
EXTENSIONS: Final[tuple[Ext, ...]] = reduce(op.add, (m.EXTENSIONS for m in MODULES))


ReaderFunc = Callable[[Path], IOResultE[MneType]]
ftype_to_read_func: dict[Ftype, ReaderFunc] = {}
ext_to_ftype: dict[Ext, Ftype] = {}
ftype2ext: dict[Ftype, tuple[Ext, ...]] = {}


for mdl in MODULES:
    ftype_to_read_func[mdl.FTYPE_ALIAS] = mdl.read
    ftype2ext[mdl.FTYPE_ALIAS] = mdl.EXTENSIONS
    ext_to_ftype.update(**{ext: mdl.FTYPE_ALIAS for ext in mdl.EXTENSIONS})
