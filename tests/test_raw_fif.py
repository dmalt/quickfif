"""Test raw_fif handling."""
from pathlib import Path

import mne
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from mne_cli_tools.mne_types.raw_fif import EXTENSIONS, read
from returns.unsafe import unsafe_perform_io


@pytest.fixture
def raw_obj(sfreq: float = 100) -> mne.io.RawArray:
    f1, f2 = 10, 5
    times = np.linspace(0, 1, int(sfreq), endpoint=False)
    sim_data = np.array(
        [
            np.sin(f1 * 2 * np.pi * times),
            np.cos(f2 * 2 * np.pi * times),
        ]
    )

    mne_info = mne.create_info(ch_names=len(sim_data), ch_types="misc", sfreq=sfreq)

    return mne.io.RawArray(sim_data, mne_info)


@pytest.fixture(params=EXTENSIONS)
def saved_raw_fif(request: pytest.FixtureRequest, tmp_path: Path, raw_obj: mne.io.Raw):
    """."""
    ext = request.param
    fpath = tmp_path / f"test{ext}"

    raw_obj.save(fpath)
    return fpath, raw_obj


def test_read_works_with_specified_extensions(saved_raw_fif: tuple[Path, mne.io.Raw]):
    raw_path, saved_raw = saved_raw_fif
    loaded_raw = unsafe_perform_io(read(raw_path).unwrap())
    assert_array_almost_equal(saved_raw.get_data(), loaded_raw.raw.get_data())
