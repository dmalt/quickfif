"""Configure dispatch on MneType objects for supported file types."""
import shutil
from enum import StrEnum
from functools import singledispatch
from pathlib import Path
from typing import Callable

from returns.io import IOResultE, impure

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
ftype2ext: dict[Ftype, tuple[Ext, ...]] = {
    Ftype.epochs: ("-epo.fif", "_epo.fif"),
    Ftype.annots: ("_annot.fif", "-annot.fif"),
    Ftype.ica: ("_ica.fif", "-ica.fif"),
    Ftype.raw: (
        "_raw.fif",
        "_raw.fif.gz",
        "-raw.fif",
        "-raw.fif.gz",
        "_raw_sss.fif",
        "_raw_sss.fif.gz",
        "-raw_sss.fif",
        "-raw_sss.fif.gz",
        "_raw_tsss.fif",
        "_raw_tsss.fif.gz",
        "-raw_tsss.fif",
        "-raw_tsss.fif.gz",
        "_meg.fif",
        "_meg.fif.gz",
        "-meg.fif",
        "_eeg.fif",
        "-eeg.fif",
        "_eeg.fif.gz",
        "_ieeg.fif",
        "_ieeg.fif.gz",
        "-ieeg.fif",
    ),
}
ext_to_ftype: dict[Ext, Ftype] = {}
for ft, exts in ftype2ext.items():
    ext_to_ftype.update(**{ext: ft for ext in exts})


@singledispatch
@impure
def copy(mne_obj: MneType, dst: Path) -> None:
    """Copy mne object."""
    shutil.copy2(mne_obj.fpath, dst)


copy.register(raw_fif.copy)
