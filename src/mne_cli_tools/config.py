"""Configure dispatch on MneType objects for supported file types."""
import shutil
from enum import StrEnum
from functools import singledispatch
from pathlib import Path
from typing import Callable

from returns.io import IOResultE, impure_safe

from mne_cli_tools.mne_types import annotations, epochs, ica, raw_fif
from mne_cli_tools.types import Ext, MneType


class Ftype(StrEnum):
    """
    Supported file types.

    We use string values of this enum as click.Choice variants for the ftype
    option. They appear as a part of CLI help message.

    """

    ica = "ica"
    raw = "raw"
    annots = "annots"
    epochs = "epochs"


ReaderFunc = Callable[[Path], IOResultE[MneType]]
ftype_to_read_func: dict[Ftype, ReaderFunc] = {
    Ftype.epochs: epochs.read,
    Ftype.annots: annotations.read,
    Ftype.ica: ica.read,
    Ftype.raw: raw_fif.read,
}
ftype_to_ext: dict[Ftype, tuple[Ext, ...]] = {
    Ftype.epochs: epochs.EXTENSIONS,
    Ftype.annots: annotations.EXTENSIONS,
    Ftype.ica: ica.EXTENSIONS,
    Ftype.raw: raw_fif.EXTENSIONS,
}
ext_to_ftype: dict[Ext, Ftype] = {}
for ft, exts in ftype_to_ext.items():
    ext_to_ftype.update(**{ext: ft for ext in exts})


@singledispatch
@impure_safe
def copy(mne_obj: MneType, dst: Path) -> None:
    """Copy mne object."""
    shutil.copy2(mne_obj.fpath, dst)


copy.register(raw_fif.copy)
