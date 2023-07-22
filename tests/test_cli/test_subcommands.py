"""Test green path for CLI."""
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from mne_cli_tools import main
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.types import MneType


@pytest.fixture
def mock_open_in_console(mocker: MockerFixture) -> Mock:
    """Mock starting ipython embedded console session."""
    return mocker.patch("mne_cli_tools.main.open_in_console", autospec=True)


def test_inspect_succeeds_on_green_path(
    mock_read_mne_obj_result: MneType,
    cli: CliRunner,
    ftype_args: list[str],
    mock_open_in_console: Mock,
) -> None:
    """Test inspect succeeds if object creation went fine."""
    fname = str(mock_read_mne_obj_result.fpath)
    args = ftype_args + [fname, "inspect"]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    mock_open_in_console.assert_called_once()


@pytest.fixture
def mock_safe_copy(mocker: MockerFixture) -> Mock:
    """Mock copy function so it doesn't change the filesystem."""
    return mocker.patch("mne_cli_tools.main.safe_copy", autospec=True)


def test_copy_calls_api(
    mock_read_mne_obj_result: MneType,
    cli: CliRunner,
    ftype_args: list[str],
    mock_safe_copy: Mock,
) -> None:
    """Test copy CLI command calls api function."""
    src = str(mock_read_mne_obj_result.fpath)
    dst = f"{src}.copy"
    args = ftype_args + [src, "copy", dst]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    mock_safe_copy.assert_called_once()
