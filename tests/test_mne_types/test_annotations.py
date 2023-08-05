"""Test mct annotations."""
from numpy.testing import assert_array_almost_equal, assert_array_equal

from mne_cli_tools.mct_types import annotations


def test_summary_string_contains_header(mct_annots: annotations.AnnotsFif) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    summary = mct_annots.summary

    assert annotations.SUMMARY_HEADER in summary


def test_to_dict_wraps_fpath_and_annots(mct_annots: annotations.AnnotsFif) -> None:
    """Test to_dict wraps fpath and raw."""
    res = mct_annots.to_dict()

    assert mct_annots.fpath in res.values()
    assert mct_annots.annots in res.values()


def test_read_loads_same_data(saved_mct_annots: annotations.AnnotsFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_annots = annotations.read(saved_mct_annots.fpath).annots

    assert_array_almost_equal(saved_mct_annots.annots.onset, loaded_annots.onset)
    assert_array_almost_equal(saved_mct_annots.annots.duration, loaded_annots.duration)
    assert_array_equal(saved_mct_annots.annots.description, loaded_annots.description)
