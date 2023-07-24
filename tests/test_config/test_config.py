"""Test configuration consistency."""
from mne_cli_tools.config import ext_to_ftype, ftype_to_ext


def test_no_duplicates_in_extensions():
    """Test extensions don't have any duplicates."""
    len_specified = sum(len(set(extensions)) for extensions in ftype_to_ext.values())

    assert len_specified == len(ext_to_ftype)
