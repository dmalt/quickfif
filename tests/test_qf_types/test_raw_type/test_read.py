"""Test reading `mne.io.Raw` objects."""
from numpy.testing import assert_array_almost_equal

from quickfif.qf_types.raw_type import QfRaw
from quickfif.qf_types.raw_type import read as read_qf_raw


def test_read_loads_same_data(saved_qf_raw: QfRaw) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = read_qf_raw(saved_qf_raw.fpath)

    assert_array_almost_equal(saved_qf_raw.raw.get_data(), loaded_raw.raw.get_data())
