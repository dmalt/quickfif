import os
from datetime import datetime
from typing import Any, Self, TypeAlias, Union

import numpy.typing as npt  # noqa: WPS301
import pandas as pd

_Verbose: TypeAlias = Union[bool, str, int, None]

def __getattr__(name: str) -> Any: ...

class Annotations(object):
    onset: npt.ArrayLike
    duration: npt.ArrayLike | float
    description: npt.ArrayLike | str

    def __init__(
        self: Self,
        onset: npt.ArrayLike,
        duration: npt.ArrayLike | float,
        description: npt.ArrayLike | str,
        orig_time: float | str | datetime | tuple | int | None = None,
        ch_names: list[list[str]] | None = None,
    ) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __len__(self) -> int: ...
    def append(
        self,
        onset: npt.ArrayLike | float,
        duration: npt.ArrayLike | float,
        description: npt.ArrayLike | float,
        ch_names: list[list[str]] | None = None,
    ) -> Self: ...
    def copy(self) -> Self: ...
    def delete(self, idx: npt.ArrayLike | int) -> None: ...
    def to_data_frame(self) -> pd.DataFrame: ...
    def count(self) -> dict[str, int]: ...
    def save(
        self, fname: os.PathLike, *, overwrite: bool = False, verbose: _Verbose = None
    ) -> None: ...
    def crop(
        self,
        tmin: float | datetime | None = None,
        tmax: float | datetime | None = None,
        emit_warning: bool = False,
        use_orig_time: bool = True,
        verbose: _Verbose = None,
    ): ...
    def set_durations(
        self,
        mapping: dict[str, float] | float,
        verbose: _Verbose = None,
    ) -> Self: ...
    def rename(self, mapping: dict[str, str], verbose: _Verbose = None) -> Self: ...
