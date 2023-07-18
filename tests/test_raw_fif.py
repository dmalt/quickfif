"""Test raw_fif handling."""
from pathlib import Path

import mne
import numpy as np
import numpy.typing as npt  # noqa: WPS301 (dotted imports)
import pytest
from numpy.testing import assert_array_almost_equal
from returns.unsafe import unsafe_perform_io

from mne_cli_tools.mne_types import raw_fif


@pytest.fixture
def timeseries() -> tuple[npt.NDArray, float]:
    """Sample timeseries data with sampling frequency."""
    sfreq, f1, f2 = 100, 7, 5
    times = np.linspace(0, 1, int(sfreq), endpoint=False)
    sim_data = np.array(
        [
            np.sin(f1 * 2 * np.pi * times),
            np.cos(f2 * 2 * np.pi * times),
        ]
    )
    return sim_data, sfreq


@pytest.fixture
def raw_obj(timeseries: tuple[npt.NDArray, float]) -> mne.io.RawArray:
    """Sample `mne.io.Raw` object."""
    sim_data, sfreq = timeseries
    n_ch = len(sim_data)
    mne_info = mne.create_info(ch_names=n_ch, ch_types="misc", sfreq=sfreq)
    return mne.io.RawArray(sim_data, mne_info)


@pytest.fixture(params=raw_fif.EXTENSIONS)
def saved_raw_fif(request: pytest.FixtureRequest, tmp_path: Path, raw_obj: mne.io.Raw):
    """Path to saved `Raw` object and the object itself."""
    ext = request.param
    fpath = tmp_path / f"test{ext}"
    raw_obj.save(fpath)
    return fpath, raw_obj


def test_read_works_with_specified_extensions(saved_raw_fif: tuple[Path, mne.io.Raw]):
    """Check if raw objects saved with supported extensions are loaded fine."""
    raw_path, saved_raw = saved_raw_fif

    loaded_raw = unsafe_perform_io(raw_fif.read(raw_path).unwrap())

    assert_array_almost_equal(saved_raw.get_data(), loaded_raw.raw.get_data())
