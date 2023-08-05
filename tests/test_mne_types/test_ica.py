"""Test mct ica."""
from numpy.testing import assert_array_almost_equal

from mne_cli_tools.mct_types import ica


def test_summary_string(mct_ica: ica.IcaFif) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and ica
    section header depending on ica presence.

    """
    summary = mct_ica.summary

    assert "ICA" in summary, summary


def test_to_dict_wraps_fpath_and_ica(mct_ica: ica.IcaFif) -> None:
    """Test to_dict wraps fpath and raw."""
    ns = mct_ica.to_dict()

    assert mct_ica.fpath == ns["fpath"]
    assert repr(mct_ica.ica) == repr(ns["ica"])  # use repr: direct ica comparison doesn't work


def test_read_loads_same_data(saved_mct_ica: ica.IcaFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_ica = ica.read(saved_mct_ica.fpath).ica

    assert_array_almost_equal(loaded_ica.unmixing_matrix_, saved_mct_ica.ica.unmixing_matrix_)
