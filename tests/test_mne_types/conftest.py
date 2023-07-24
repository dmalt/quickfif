"""Fixtures for mne_types package testing."""
from pathlib import Path
from typing import Callable

import mne
import numpy as np
import pytest

from mne_cli_tools.mne_types import raw_fif


@pytest.fixture
def create_fake_annots() -> Callable[[float, float], mne.Annotations]:
    """Create fake annotations."""

    def wrapped(  # noqa: WPS430
        t_start: float,
        t_stop: float,
        n_annots: int = 10,
        dur_frac: float = 0.5,
        desc: str = "test",
    ) -> mne.Annotations:
        onsets = np.linspace(t_start, t_stop, n_annots, endpoint=False)
        dt = (t_stop - t_start) / n_annots * dur_frac
        duration, description = [dt] * n_annots, [desc] * n_annots  # noqa: WPS435 (list multiply)
        return mne.Annotations(onsets, duration=duration, description=description)

    return wrapped


@pytest.fixture
def raw_obj() -> mne.io.RawArray:
    """Sample `mne.io.Raw` object."""
    n_ch, sfreq = 2, 100
    mne_info = mne.create_info(ch_names=n_ch, sfreq=sfreq)
    return mne.io.RawArray(data=np.zeros([n_ch, sfreq]), info=mne_info)


@pytest.fixture(params=raw_fif.EXTENSIONS)
def saved_raw_fif(
    request: pytest.FixtureRequest, tmp_path: Path, raw_obj: mne.io.Raw
) -> raw_fif.RawFif:
    """
    `RawFif` object with fpath pointing to to saved wrapped `mne.io.Raw` object.

    fpath ends with one of the supported extensions.

    """
    ext = request.param
    fpath = tmp_path / f"test{ext}"
    raw_obj.save(fpath)
    return raw_fif.RawFif(fpath, raw_obj)
