"""Test raw_fif handling."""
from pathlib import Path
from typing import Callable

import mne
import numpy as np
import numpy.typing as npt  # noqa: WPS301 (dotted imports)
import pytest
from numpy.testing import assert_array_almost_equal
from returns.unsafe import unsafe_perform_io

from mne_cli_tools.mne_types import raw_fif

FloatArray = npt.NDArray[np.float_]


@pytest.fixture
def timeseries() -> tuple[FloatArray, float]:
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
def raw_obj(timeseries: tuple[FloatArray, float]) -> mne.io.RawArray:
    """Sample `mne.io.Raw` object."""
    sim_data, sfreq = timeseries
    n_ch = len(sim_data)
    mne_info = mne.create_info(ch_names=n_ch, ch_types="misc", sfreq=sfreq)
    return mne.io.RawArray(sim_data, mne_info)


@pytest.fixture(params=raw_fif.EXTENSIONS)
def saved_raw_fif(
    request: pytest.FixtureRequest, tmp_path: Path, raw_obj: mne.io.Raw
) -> raw_fif.RawFif:
    """`RawFif` object with fpath pointing to to saved wrapped `mne.io.Raw` object."""
    ext = request.param
    fpath = tmp_path / f"test{ext}"
    raw_obj.save(fpath)
    return raw_fif.RawFif(fpath, raw_obj)


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def maybe_annotated_raw_fif(
    request: pytest.FixtureRequest,
    raw_obj: mne.io.Raw,
    create_fake_annots: Callable[[float, float], mne.Annotations],
) -> raw_fif.RawFif:
    """`RawFif` wrapper around possibly annotated `mne.io.Raw`."""
    if request.param:
        t_start, t_stop = raw_obj.times[0], raw_obj.times[-1]
        raw_obj.set_annotations(create_fake_annots(t_start, t_stop))
    return raw_fif.RawFif(fpath=Path("test_path_raw.fif"), raw=raw_obj)


def test_read_works_with_specified_extensions(saved_raw_fif: raw_fif.RawFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = unsafe_perform_io(raw_fif.read(saved_raw_fif.fpath).unwrap())

    assert_array_almost_equal(saved_raw_fif.raw.get_data(), loaded_raw.raw.get_data())


def test_summary_string_contents(maybe_annotated_raw_fif: raw_fif.RawFif) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    n_ch = len(maybe_annotated_raw_fif.raw.ch_names)
    n_samples = len(maybe_annotated_raw_fif.raw.times)

    summary = str(maybe_annotated_raw_fif)

    assert str(n_ch) in summary
    assert str(n_samples) in summary
    if maybe_annotated_raw_fif.raw.annotations:
        assert raw_fif.ANNOTS_SECTION_HEADER in summary
    else:
        assert raw_fif.NO_ANNOTS_MSG in summary
