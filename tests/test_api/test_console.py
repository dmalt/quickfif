"""Test api ipython embed wrapper."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from returns.io import IOResult, IOResultE

from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import ConsoleEmbedError, ExitCode
from tests.fake_mne_type import FakeMneType


@pytest.fixture
def mock_embed_failure(mock_fn_factory: Callable[[IOResultE[None], str], Mock]) -> Mock:
    """Mock embed_ipython when error occured."""
    return_value = IOResult.from_failure(Exception("test error"))
    return mock_fn_factory(return_value, "mne_cli_tools.api.commands.embed_ipython")


def test_open_in_ipython_fail_causes_console_embed_error(mock_embed_failure: Mock) -> None:
    """Fail of wrapped embed_ipython should cause ConsoleEmbedError."""
    mne_obj = FakeMneType(Path("test_path.ext"), "test_object")

    with pytest.raises(ConsoleEmbedError) as exc_info:
        commands.open_in_console(mne_obj)

        assert exc_info.value.exit_code == ExitCode.write_failed
    mock_embed_failure.assert_called_once_with(mne_obj.to_dict())


@pytest.fixture
def mock_embed_success(mock_fn_factory: Callable[[IOResultE[None], str], Mock]) -> Mock:
    """Mock embed_ipython when it went fine."""
    return mock_fn_factory(IOResult.from_value(None), "mne_cli_tools.api.commands.embed_ipython")


def test_open_in_console_properly_calls_wrapped_function(mock_embed_success: Mock) -> None:
    """Test that wrapped function was called properly."""
    mne_obj = FakeMneType(Path("test_path.ext"), "test_object")

    commands.open_in_console(mne_obj)

    mock_embed_success.assert_called_once_with(mne_obj.to_dict())
