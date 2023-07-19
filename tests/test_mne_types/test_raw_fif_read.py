from numpy.testing import assert_array_almost_equal
from returns.unsafe import unsafe_perform_io

from mne_cli_tools.mne_types import raw_fif


def test_read_works_with_specified_extensions(saved_raw_fif: raw_fif.RawFif) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = unsafe_perform_io(raw_fif.read(saved_raw_fif.fpath).unwrap())

    assert_array_almost_equal(saved_raw_fif.raw.get_data(), loaded_raw.raw.get_data())
