"""Test api copy wrapper."""
from pathlib import Path
from typing import Callable, Final
from unittest.mock import Mock

import pytest
from returns.io import IOResult, IOResultE

from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import ExitCode, WriteFailedError
from tests.fake_mne_type import FakeMneType

OVERWRITE_IDS: Final = ("overwrite", "don't overwrite")


@pytest.fixture
def mock_copy_failure(mock_fn_factory: Callable[[IOResultE[None], str], Mock]) -> Mock:
    """Mock copy when it went bad."""
    return_value = IOResult.from_failure(Exception("Test fail"))
    return mock_fn_factory(return_value, "mne_cli_tools.api.commands.copy")


@pytest.fixture
def mock_copy_success(mock_fn_factory: Callable[[IOResultE[None], str], Mock]) -> Mock:
    """Mock copy when it succeeded."""
    return mock_fn_factory(IOResult.from_value(None), "mne_cli_tools.api.commands.copy")


@pytest.mark.parametrize("overwrite", [True, False], ids=OVERWRITE_IDS)
def test_copy_fail_causes_write_failed_error(overwrite: bool, mock_copy_failure: Mock) -> None:
    """Fail of wrapped config.copy() should cause WriteFailedError.

    WriteFailedError is a child of click.FileError, which is handled nicely by
    click API.

    """
    mne_obj = FakeMneType(Path("test_path.ext"), "test_object")
    dst = Path(f"{mne_obj.fpath}.copy")

    with pytest.raises(WriteFailedError) as exc_info:
        commands.safe_copy(mne_obj, dst, overwrite)

        assert exc_info.value.exit_code == ExitCode.write_failed
    mock_copy_failure.assert_called_once_with(mne_obj, dst, overwrite)


@pytest.mark.parametrize("overwrite", [True, False], ids=OVERWRITE_IDS)
def test_copy_calls_wrapped_config_copy_on_success(
    overwrite: bool, mock_copy_success: Mock
) -> None:
    """API copy function should call config.copy() with proper arguments."""
    mne_obj = FakeMneType(Path("test_path.ext"), "test_object")
    dst = Path(f"{mne_obj.fpath}.copy")

    commands.safe_copy(mne_obj, dst, overwrite)
    mock_copy_success.assert_called_once_with(mne_obj, dst, overwrite)
