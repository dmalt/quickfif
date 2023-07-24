"""Test config module."""
from pathlib import Path
from typing import Final
from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture
from returns.functions import raise_exception
from returns.pipeline import is_successful

from mne_cli_tools.config import copy, ext_to_ftype, ftype_to_ext
from mne_cli_tools.types import MneType
from tests.fake_mne_type import FakeMneType

OVERWRITE_IDS: Final = ("overwrite", "don't overwrite")


def test_no_duplicates_in_extensions():
    """Test extensions don't have any duplicates."""
    len_specified = sum(len(set(extensions)) for extensions in ftype_to_ext.values())

    assert len_specified == len(ext_to_ftype)


@pytest.fixture
def mne_obj_of_tmp_path(tmp_path: Path) -> FakeMneType:
    """Mne obj wrapping fpath in temporary directory."""
    src_path = tmp_path / "test_path.ext"
    return FakeMneType(src_path, "test_obj")


@pytest.fixture
def mock_shutil_copy(mocker: MockFixture) -> Mock:
    """Mock shutil.copy()."""
    return mocker.patch("shutil.copy", autospec=True)


@pytest.mark.parametrize("overwrite", [True, False], ids=OVERWRITE_IDS)
def test_copy_default_calls_shutil(
    mock_shutil_copy: Mock, overwrite: bool, mne_obj_of_tmp_path: MneType
) -> None:
    """
    Test default copy implementation green path.

    Test when destination doesn't exist and is writable, we just call shutil.copy.

    """
    dst = Path(f"{mne_obj_of_tmp_path.fpath}.copy")

    copy(mne_obj_of_tmp_path, dst, overwrite)

    mock_shutil_copy.assert_called_once_with(mne_obj_of_tmp_path.fpath, dst)


def test_default_copy_fails_when_overwrite_false_and_dst_exists(
    mock_shutil_copy: Mock, mne_obj_of_tmp_path: MneType
) -> None:
    """Test default implementation of copy fails when we try not permitted overwrite."""
    dst = Path(f"{mne_obj_of_tmp_path.fpath}.copy")
    dst.touch()

    res = copy(mne_obj_of_tmp_path, dst, overwrite=False)

    assert not is_successful(res)
    with pytest.raises(ValueError):
        res.alt(raise_exception).unwrap()
    mock_shutil_copy.assert_not_called()


@pytest.mark.parametrize("overwrite", [True, False], ids=OVERWRITE_IDS)
def test_default_copy_uses_src_fname_when_dst_is_dir(
    mock_shutil_copy: Mock,
    mne_obj_of_tmp_path: MneType,
    tmp_path_factory: pytest.TempPathFactory,
    overwrite: bool,
) -> None:
    """Test copy default implementation when specifying directory as dst."""
    dst_dir = tmp_path_factory.mktemp("copy_dst_dir", numbered=True)
    dst_fpath = dst_dir / mne_obj_of_tmp_path.fpath.name

    copy(mne_obj_of_tmp_path, dst_dir, overwrite)

    mock_shutil_copy.assert_called_once_with(mne_obj_of_tmp_path.fpath, dst_fpath)
