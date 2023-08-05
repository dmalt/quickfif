"""Configure dispatch on MctType objects for supported file types."""
from enum import StrEnum
from functools import singledispatch
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Final, TypeAlias

from mne_cli_tools.mct_types import annotations, epochs, ica, raw_fif
from mne_cli_tools.mct_types.base import MctType

Ext: TypeAlias = "str"


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


_ftype_to_read_func: dict[Ftype, Callable[[Path], MctType]] = {
    Ftype.epochs: epochs.read,
    Ftype.annots: annotations.read,
    Ftype.ica: ica.read,
    Ftype.raw: raw_fif.read,
}
_ftype_to_ext: dict[Ftype, tuple[Ext, ...]] = {
    Ftype.epochs: epochs.EXTENSIONS,
    Ftype.annots: annotations.EXTENSIONS,
    Ftype.ica: ica.EXTENSIONS,
    Ftype.raw: raw_fif.EXTENSIONS,
}
_ext_to_ftype: dict[Ext, Ftype] = {}
for ft, exts in _ftype_to_ext.items():
    _ext_to_ftype.update(**{ext: ft for ext in exts})

FTYPE_TO_EXT: Final = MappingProxyType(_ftype_to_ext)
EXT_TO_FTYPE: Final = MappingProxyType(_ext_to_ftype)


def mct_read(fpath: Path, ftype: Ftype) -> MctType:
    """Read MctType object."""
    return _ftype_to_read_func[ftype](fpath)


class UnsupportedOperationError(Exception):
    """Operation not supported for this file type."""


@singledispatch
def mct_save(mct_obj: MctType, dst: Path, overwrite: bool) -> None:  # pyright: ignore
    """Copy mne object."""
    raise UnsupportedOperationError(f"copy is not supported for {mct_obj}")


mct_save.register(raw_fif.save)
mct_save.register(epochs.save)
