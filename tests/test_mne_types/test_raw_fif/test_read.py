"""Test reading `mne.io.Raw` objects."""
from numpy.testing import assert_array_almost_equal

from mne_cli_tools.mct_types import raw_fif


def test_read_loads_same_data(saved_mct_raw: raw_fif.RawFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = raw_fif.read(saved_mct_raw.fpath)

    assert_array_almost_equal(saved_mct_raw.raw.get_data(), loaded_raw.raw.get_data())
