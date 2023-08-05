"""Test mct epochs."""
from numpy.testing import assert_array_almost_equal

from mne_cli_tools.mct_types import epochs


def test_summary_string_contains_info(mct_epochs: epochs.EpochsFif) -> None:
    """
    Test summary for `RawFif`.

    Check data dimensions = n_channels x n_samples are present and ica
    section header depending on ica presence.

    """
    summary = mct_epochs.summary

    assert "Info" in summary, summary


def test_to_dict_wraps_fpath_and_epochs(mct_epochs: epochs.EpochsFif) -> None:
    """Test to_dict wraps fpath and raw."""
    ns = mct_epochs.to_dict()

    assert mct_epochs.fpath == ns["fpath"]
    assert mct_epochs.epochs == ns["epochs"]


def test_read_loads_same_data(saved_mct_epochs: epochs.EpochsFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_epochs = epochs.read(saved_mct_epochs.fpath).epochs

    assert_array_almost_equal(loaded_epochs.get_data(), saved_mct_epochs.epochs.get_data())
