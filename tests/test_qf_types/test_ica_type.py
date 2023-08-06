"""Test qf ica."""
from numpy.testing import assert_array_almost_equal

from quickfif.qf_types.ica_type import QfIca
from quickfif.qf_types.ica_type import read as read_qf_ica


def test_summary_string(qf_ica: QfIca) -> None:
    """
    Test summary for `QfRaw`.

    Check data dimensions = n_channels x n_samples are present and ica
    section header depending on ica presence.

    """
    summary = qf_ica.summary

    assert "ICA" in summary, summary


def test_to_dict_wraps_fpath_and_ica(qf_ica: QfIca) -> None:
    """Test to_dict wraps fpath and raw."""
    ns = qf_ica.to_dict()

    assert qf_ica.fpath == ns["fpath"]
    assert repr(qf_ica.ica) == repr(ns["ica"])  # use repr: direct ica comparison doesn't work


def test_read_loads_same_data(saved_qf_ica: QfIca) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_ica = read_qf_ica(saved_qf_ica.fpath).ica

    assert_array_almost_equal(loaded_ica.unmixing_matrix_, saved_qf_ica.ica.unmixing_matrix_)
