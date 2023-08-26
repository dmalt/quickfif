"""Test qf annotations."""
from numpy.testing import assert_array_almost_equal, assert_array_equal

from quickfif.qf_types.annots_type import SUMMARY_HEADER, QfAnnots
from quickfif.qf_types.annots_type import read as read_qf_annots


def test_summary_string_contains_header(qf_annots: QfAnnots) -> None:
    """
    Test summary for `QfRaw`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    summary = qf_annots.summary

    assert SUMMARY_HEADER in summary


def test_to_dict_wraps_fpath_and_annots(qf_annots: QfAnnots) -> None:
    """Test to_dict wraps fpath and raw."""
    res = qf_annots.to_dict()

    assert qf_annots.fpath in res.values()
    assert qf_annots.annots in res.values()


def test_read_loads_same_data(saved_qf_annots: QfAnnots) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_annots = read_qf_annots(saved_qf_annots.fpath).annots

    assert_array_almost_equal(saved_qf_annots.annots.onset, loaded_annots.onset)
    assert_array_almost_equal(saved_qf_annots.annots.duration, loaded_annots.duration)
    assert_array_equal(saved_qf_annots.annots.description, loaded_annots.description)
