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


def create_fake_annots(
    t_start: float, t_stop: float, n_annots: int = 10, dur_frac: float = 0.5, desc="test"
) -> mne.Annotations:
    """Create fake annotations."""
    onsets = np.linspace(t_start, t_stop, n_annots, endpoint=False)
    dt = (t_stop - t_start) / n_annots * dur_frac
    duration, description = [dt] * n_annots, [desc] * n_annots  # noqa: WPS435 (list multiply)
    return mne.Annotations(onsets, duration=duration, description=description)


def add_fake_annots(raw: mne.io.Raw) -> None:
    """Add fake annotations to `mne.io.Raw` object."""
    t_start, t_stop = raw.times[0], raw.times[-1]
    raw.set_annotations(create_fake_annots(t_start, t_stop))


@pytest.fixture(params=raw_fif.EXTENSIONS)
def saved_raw_fif(
    request: pytest.FixtureRequest, tmp_path: Path, raw_obj: mne.io.Raw
) -> raw_fif.RawFif:
    """`RawFif` object with fpath pointing to to saved wrapped `mne.io.Raw` object."""
    ext = request.param
    fpath = tmp_path / f"test{ext}"
    raw_obj.save(fpath)
    return raw_fif.RawFif(fpath, raw_obj)


def test_read_works_with_specified_extensions(saved_raw_fif: raw_fif.RawFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = unsafe_perform_io(raw_fif.read(saved_raw_fif.fpath).unwrap())

    assert_array_almost_equal(saved_raw_fif.raw.get_data(), loaded_raw.raw.get_data())


@pytest.mark.parametrize("add_annots", [True, False])
def test_summary_no_annots(saved_raw_fif: raw_fif.RawFif, add_annots: bool) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and annotations
    are reported to be missing.

    """
    n_ch = len(saved_raw_fif.raw.ch_names)
    n_samples = len(saved_raw_fif.raw.times)
    if add_annots:
        add_fake_annots(saved_raw_fif.raw)

    summary = str(saved_raw_fif)

    assert str(n_ch) in summary
    assert str(n_samples) in summary
    if add_annots:
        assert raw_fif.ANNOTS_SECTION_HEADER in summary
    else:
        assert raw_fif.NO_ANNOTS_MSG in summary
