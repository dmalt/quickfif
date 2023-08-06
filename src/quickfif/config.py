"""Configure dispatch on QfType objects for supported file types."""
from enum import StrEnum
from functools import singledispatch
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Final, TypeAlias

from quickfif.qf_types import annots_type, epochs_type, ica_type, raw_type
from quickfif.qf_types.base import QfType

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


_ftype_to_read_func: dict[Ftype, Callable[[Path], QfType]] = {
    Ftype.epochs: epochs_type.read,
    Ftype.annots: annots_type.read,
    Ftype.ica: ica_type.read,
    Ftype.raw: raw_type.read,
}
_ftype_to_ext: dict[Ftype, tuple[Ext, ...]] = {
    Ftype.epochs: epochs_type.EXTENSIONS,
    Ftype.annots: annots_type.EXTENSIONS,
    Ftype.ica: ica_type.EXTENSIONS,
    Ftype.raw: raw_type.EXTENSIONS,
}
_ext_to_ftype: dict[Ext, Ftype] = {}
for ft, exts in _ftype_to_ext.items():
    _ext_to_ftype.update(**{ext: ft for ext in exts})

FTYPE_TO_EXT: Final = MappingProxyType(_ftype_to_ext)
EXT_TO_FTYPE: Final = MappingProxyType(_ext_to_ftype)


def qf_read(fpath: Path, ftype: Ftype) -> QfType:
    """Read QfType object."""
    return _ftype_to_read_func[ftype](fpath)


class UnsupportedOperationError(Exception):
    """Operation not supported for this file type."""


@singledispatch
def qf_save(qf_obj: QfType, dst: Path, overwrite: bool) -> None:  # pyright: ignore
    """Save mne object."""
    raise UnsupportedOperationError(f"'Save as' is not supported for {qf_obj}")


qf_save.register(raw_type.save)
qf_save.register(epochs_type.save)
