"""Test api ipython embed wrapper."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from returns.io import IO

from mne_cli_tools.api import commands
from tests.fake_mne_type import FakeMneType


@pytest.fixture
def mock_embed(mock_fn_factory: Callable[[IO[None], str], Mock]) -> Mock:
    """Mock embed_ipython."""
    return mock_fn_factory(IO.from_value(None), "mne_cli_tools.api.commands.embed_ipython")


def test_open_in_console_properly_calls_wrapped_function(mock_embed: Mock) -> None:
    """Test that wrapped function was called properly."""
    mne_obj = FakeMneType(Path("test_path.ext"), "test_object")

    commands.open_in_console(mne_obj)

    mock_embed.assert_called_once_with(mne_obj.to_dict())
