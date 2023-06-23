"""Tests for the CLI."""
import pytest
from click.testing import CliRunner

from mne_cli_tools import main


@pytest.fixture
def cli_runner():
    """Mock interacting with CLI from the console."""
    return CliRunner()


def test_cli_fails_wo_args(cli_runner: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli_runner.invoke(main.main).exit_code == 2


def test_cli_fails_for_nonexistent_fname(cli_runner: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli_runner.isolated_filesystem():
        cli_result = cli_runner.invoke(main.main, ["i_dont_exist.fif"])
        assert cli_result.exit_code == 2
