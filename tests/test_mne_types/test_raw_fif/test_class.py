"""Test raw_fif handling."""
from pathlib import Path
from typing import Callable

import mne
import pytest

from mne_cli_tools.mct_types import raw_fif


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def maybe_annotated_mct_raw(
    request: pytest.FixtureRequest,
    small_raw_obj: mne.io.Raw,
    create_fake_annots: Callable[[float, float], mne.Annotations],
    raw_ext: str,
) -> raw_fif.RawFif:
    """`RawFif` wrapper around possibly annotated `mne.io.Raw`."""
    annotated_raw = small_raw_obj.copy()
    if request.param:
        t_start, t_stop = small_raw_obj.times[0], small_raw_obj.times[-1]
        annotated_raw.set_annotations(create_fake_annots(t_start, t_stop))
    return raw_fif.RawFif(fpath=Path(f"test_{raw_ext}"), raw=annotated_raw)


def test_summary_string_contents(maybe_annotated_mct_raw: raw_fif.RawFif) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    n_ch = len(maybe_annotated_mct_raw.raw.ch_names)
    n_samples = len(maybe_annotated_mct_raw.raw.times)

    summary = maybe_annotated_mct_raw.summary

    assert str(n_ch) in summary
    assert str(n_samples) in summary
    if maybe_annotated_mct_raw.raw.annotations:
        assert raw_fif.ANNOTS_SECTION_HEADER in summary
    else:
        assert raw_fif.NO_ANNOTS_MSG in summary


def test_to_dict_wraps_fpath_and_raw(mct_raw: raw_fif.RawFif) -> None:
    """Test to_dict wraps fpath and raw."""
    res = mct_raw.to_dict()

    assert mct_raw.fpath in res.values()
    assert mct_raw.raw in res.values()
