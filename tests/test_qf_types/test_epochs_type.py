"""Test qf epochs."""
from numpy.testing import assert_array_almost_equal

from quickfif.qf_types.epochs_type import QfEpochs
from quickfif.qf_types.epochs_type import read as read_qf_epochs


def test_summary_string_contains_info(qf_epochs: QfEpochs) -> None:
    """
    Test summary for `QfRaw`.

    Check data dimensions = n_channels x n_samples are present and ica
    section header depending on ica presence.

    """
    summary = qf_epochs.summary

    assert "Info" in summary, summary


def test_to_dict_wraps_fpath_and_epochs(qf_epochs: QfEpochs) -> None:
    """Test to_dict wraps fpath and raw."""
    ns = qf_epochs.to_dict()

    assert qf_epochs.fpath == ns["fpath"]
    assert qf_epochs.epochs == ns["epochs"]


def test_read_loads_same_data(saved_qf_epochs: QfEpochs) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_epochs = read_qf_epochs(saved_qf_epochs.fpath).epochs

    assert_array_almost_equal(loaded_epochs.get_data(), saved_qf_epochs.epochs.get_data())
