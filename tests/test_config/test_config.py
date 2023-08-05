"""Test configuration consistency."""
from mne_cli_tools.config import EXT_TO_FTYPE, FTYPE_TO_EXT


def test_no_duplicates_in_extensions():
    """Test extensions don't have any duplicates."""
    len_specified = sum(len(set(extensions)) for extensions in FTYPE_TO_EXT.values())

    assert len_specified == len(EXT_TO_FTYPE)
