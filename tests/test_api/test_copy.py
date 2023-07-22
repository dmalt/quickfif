"""Test api copy wrapper."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from returns.io import IO, IOResult, IOResultE

from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import ExitCode, WriteFailedError
from mne_cli_tools.types import MneType
from tests.fake_mne_type import FakeMneType


@pytest.fixture
def mne_obj() -> FakeMneType:
    """Test mne object wrapping not existing fpath."""
    return FakeMneType(Path("test_path.ext"), "test_object")


@pytest.fixture(params=[True, False], ids=["overwrite", "don't overwrite"])
def overwrite(request: pytest.FixtureRequest) -> bool:
    """Weither to overwrite on copy."""
    return request.param


@pytest.fixture
def mock_copy_factory(mocker: MockerFixture) -> Callable[[IOResultE[None]], Mock]:
    """Patch wrapped copy function with dummy returning copy_result."""

    def factory(copy_result: IOResultE[None]) -> Mock:
        mock_copy = mocker.patch("mne_cli_tools.api.commands.copy", autospec=True)
        mock_copy.return_value = copy_result
        return mock_copy

    return factory


@pytest.fixture
def mock_copy_failure(mock_copy_factory: Callable[[IOResultE[None]], Mock]) -> Mock:
    """Fake copy when it went bad."""
    return mock_copy_factory(IOResult.from_failure(Exception("Test fail")))


def test_copy_fail_causes_write_failed_error(
    overwrite: bool, mne_obj: MneType, mock_copy_failure: Mock
) -> None:
    """Fail of wrapped config.copy() should cause WriteFailedError.

    WriteFailedError is a child of click.FileError, which is handled nicely by
    click API.

    """
    dst = Path(f"{mne_obj.fpath}.copy")

    with pytest.raises(WriteFailedError) as exc_info:
        commands.safe_copy(mne_obj, dst, overwrite)
        mock_copy_failure.assert_called_once_with(IO.from_value(mne_obj), dst, overwrite)
        assert exc_info.value.exit_code == ExitCode.write_failed


@pytest.fixture
def mock_copy_success(mock_copy_factory: Callable[[IOResultE[None]], Mock]) -> Mock:
    """Fake copy when it went bad."""
    return mock_copy_factory(IOResult.from_value(None))


def test_copy_calls_wrapped_config_copy_on_success(
    overwrite: bool, mne_obj: MneType, mock_copy_success: Mock
) -> None:
    """API copy function should call config.copy() with proper arguments."""
    dst = Path(f"{mne_obj.fpath}.copy")

    commands.safe_copy(mne_obj, dst, overwrite)
    mock_copy_success.assert_called_once_with(mne_obj, dst, overwrite)
