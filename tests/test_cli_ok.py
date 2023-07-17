"""Test green path for CLI invokation without subcommands (a.k.a. preview)."""
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from mne_cli_tools import main
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.config import Ftype


def test_preview_succeeds_when_read_ok(
    fake_read: tuple[str, Ftype], cli: CliRunner, pass_ft: bool
) -> None:
    """Fake file reading and test the rest of preview logic."""
    fname, ftype = fake_read
    args = ["--ftype", ftype, fname] if pass_ft else [fname]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert fname in cli_result.output


@pytest.fixture
def start_ipython_mock(mocker: MockerFixture) -> Mock:
    """Mock starting ipython embedded console session."""
    return mocker.patch("IPython.start_ipython", autospec=True)


def test_inspect_succeeds_on_green_path(
    fake_read: tuple[str, Ftype], cli: CliRunner, pass_ft: bool, start_ipython_mock: Mock
) -> None:
    """Test inspect succeeds if object creation went fine."""
    fname, ftype = fake_read
    args = ["--ftype", ftype, fname, "inspect"] if pass_ft else [fname, "inspect"]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    start_ipython_mock.assert_called_once()


@pytest.fixture
def mock_copy(mocker: MockerFixture) -> Mock:
    """Mock copy function so it doesn't change the filesystem."""
    return mocker.patch("mne_cli_tools.api.commands.copy")


def test_copy_succeeds_on_green_path(
    fake_read: tuple[str, Ftype], cli: CliRunner, pass_ft: bool, mock_copy: Mock
) -> None:
    """Test inspect succeeds if object creation went fine."""
    fname, ftype = fake_read
    dst = f"{fname}.copy"
    args = ["--ftype", ftype, fname, "copy", dst] if pass_ft else [fname, "copy", dst]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    mock_copy.assert_called_once()
