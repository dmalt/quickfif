"""Mct raw fixtures."""
from typing import TYPE_CHECKING, Callable

import numpy as np
import pytest
from mne import create_info
from mne.io import Raw, RawArray

from mne_cli_tools.mct_types.raw_type import EXTENSIONS as RAW_EXTENSIONS
from mne_cli_tools.mct_types.raw_type import MctRaw

if TYPE_CHECKING:
    from pathlib import Path


RawFactory = Callable[[int, float, float], RawArray]


@pytest.fixture
def raw_obj_factory() -> RawFactory:
    """Sample MctRaw object factory."""

    def factory(n_ch: int, sfreq: float, dur_sec: float, ch_types="misc") -> RawArray:
        n_samp = int(dur_sec * sfreq)
        mne_info = create_info(ch_names=n_ch, sfreq=sfreq, ch_types=ch_types)
        return RawArray(data=np.random.randn(n_ch, n_samp), info=mne_info)

    return factory


@pytest.fixture
def small_raw_obj(raw_obj_factory: RawFactory) -> RawArray:
    """Small, fast to process mne.io.Raw instance."""
    return raw_obj_factory(2, 100, 1)


@pytest.fixture(params=RAW_EXTENSIONS)
def raw_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def mct_raw_factory(tmp_path: "Path", small_raw_obj: Raw) -> Callable[[str], MctRaw]:
    """
    `MctType` object with fpath pointing to to saved wrapped `mne.io.Raw` object.

    fpath ends with one of the supported extensions.

    """

    def factory(raw_ext: str) -> MctRaw:
        save_fpath = tmp_path / f"test{raw_ext}"
        return MctRaw(save_fpath, small_raw_obj)  # pyright: ignore

    return factory


@pytest.fixture
def mct_raw(raw_ext: str, mct_raw_factory: Callable[[str], MctRaw]) -> MctRaw:
    """
    `MctType` object with fpath pointing to to saved wrapped `mne.io.Raw` object.

    fpath ends with one of the supported extensions.

    """
    return mct_raw_factory(raw_ext)


@pytest.fixture
def saved_mct_raw(mct_raw: MctRaw) -> MctRaw:
    """Mct raw saved to a filesystem."""
    mct_raw.raw.save(mct_raw.fpath)
    return mct_raw
