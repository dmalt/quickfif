"""Qf raw fixtures."""
from typing import TYPE_CHECKING, Callable, Protocol

import numpy as np
import pytest
from mne import create_info
from mne.io import Raw, RawArray

from quickfif.qf_types.raw_type import EXTENSIONS as RAW_EXTENSIONS
from quickfif.qf_types.raw_type import QfRaw

if TYPE_CHECKING:
    from pathlib import Path


class RawFactory(Protocol):
    """Protocol for Raw factory."""

    def __call__(
        self, n_ch: int, sfreq: float, dur_sec: float, ch_types: str = ...
    ) -> Raw:  # pyright: ignore
        """Create Raw."""


@pytest.fixture
def raw_obj_factory() -> RawFactory:
    """Sample QfRaw object factory."""

    def factory(n_ch: int, sfreq: float, dur_sec: float, ch_types: str = "misc") -> Raw:
        n_samp = int(dur_sec * sfreq) + 1
        mne_info = create_info(ch_names=n_ch, sfreq=sfreq, ch_types=ch_types)
        return RawArray(data=np.random.randn(n_ch, n_samp), info=mne_info)  # pyright: ignore

    return factory


@pytest.fixture(params=[3])
def small_raw_obj(request: pytest.FixtureRequest, raw_obj_factory: RawFactory) -> Raw:
    """Small, fast to process mne.io.Raw instance."""
    n_ch = request.param
    return raw_obj_factory(n_ch, 100, 1.1)  # noqa: WPS432


@pytest.fixture
def large_qf_raw(
    tmp_path: "Path", raw_obj_factory: Callable[[int, float, float], Raw]
) -> QfRaw:
    """`QfRaw` object wrapping mne.io.Raw of ~10MB."""
    n_ch, sfreq, dur_sec = 10, 1000, 200
    mne_raw = raw_obj_factory(n_ch, sfreq, dur_sec)  # pyright: ignore
    fpath = tmp_path / "test_raw.fif"
    return QfRaw(fpath, mne_raw)  # pyright: ignore


@pytest.fixture
def qf_raw_factory(tmp_path: "Path", small_raw_obj: Raw) -> Callable[[str], QfRaw]:
    """
    `QfType` object with fpath pointing to to saved wrapped `mne.io.Raw` object.

    fpath ends with one of the supported extensions.

    """

    def factory(raw_ext: str) -> QfRaw:
        save_fpath = tmp_path / f"test{raw_ext}"
        return QfRaw(save_fpath, small_raw_obj)  # pyright: ignore

    return factory


@pytest.fixture(params=RAW_EXTENSIONS)
def qf_raw(request: pytest.FixtureRequest, qf_raw_factory: Callable[[str], QfRaw]) -> QfRaw:
    """
    `QfType` object with fpath pointing to to saved wrapped `mne.io.Raw` object.

    fpath ends with one of the supported extensions.

    """
    return qf_raw_factory(request.param)


@pytest.fixture
def saved_qf_raw(qf_raw: QfRaw) -> QfRaw:
    """Qf raw saved to a filesystem."""
    qf_raw.raw.save(qf_raw.fpath)
    return qf_raw
