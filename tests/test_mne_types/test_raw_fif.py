"""Test raw_fif handling."""
from pathlib import Path
from typing import Callable

import mne
import pytest

from mne_cli_tools.mne_types import raw_fif


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


def test_to_dict_wraps_fpath_and_raw(raw_obj: mne.io.Raw):
    """Test to_dict wraps fpath and raw."""
    raw_fif_obj = raw_fif.RawFif(Path("test_fpath_raw.fif"), raw_obj)

    res = raw_fif_obj.to_dict()

    assert raw_fif_obj.fpath in res.values()
    assert raw_fif_obj.raw in res.values()
