"""Tests for the CLI."""
import json

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
        nonexistent_fname = "i_dont_exist.fif"
        cli_result = cli_runner.invoke(main.main, [nonexistent_fname])

        assert cli_result.exit_code == 2
        err_template = "Error: Invalid value for 'FNAME': Path '{0}' does not exist."
        assert err_template.format(nonexistent_fname) in cli_result.output


def test_cli_succeeds_with_show_config_option(cli_runner: CliRunner) -> None:
    """--show-config option must work without fname argument."""
    cli_result = cli_runner.invoke(main.main, ["--show-config"])
    assert cli_result.exit_code == 0


class BadConfigurationFormatError(Exception):
    """When CLI configuration format is messed up."""


def test_show_config_shows_vaild_json(cli_runner: CliRunner) -> None:
    """--show-config option must work without fname argument."""
    cli_result = cli_runner.invoke(main.main, ["--show-config"])
    try:
        json.loads(cli_result.output)
    except json.JSONDecodeError:
        raise BadConfigurationFormatError("Printed config is not a valid JSON!")


@pytest.fixture(scope="session")
def empty_file(tmp_path_factory) -> str:
    """Empty file fixture."""
    empty_fpath = tmp_path_factory.mktemp("data") / "tmp.empty"
    empty_fpath.touch(exist_ok=True)
    return str(empty_fpath)


@pytest.fixture(scope="session")
def empty_raw_fif(tmp_path_factory) -> str:
    """Empty file fixture."""
    empty_fpath = tmp_path_factory.mktemp("data") / "tmp_raw.fif"
    empty_fpath.touch(exist_ok=True)
    return str(empty_fpath)


def test_cli_succeeds_on_empty_file_with_unsupported_ext(
    empty_file: str, cli_runner: CliRunner
) -> None:
    """Empty file should be."""
    cli_result = cli_runner.invoke(main.main, [empty_file])
    assert not cli_result.exit_code


def test_cli_fails_gracefully_on_broken_file(empty_raw_fif: str, cli_runner: CliRunner) -> None:
    """Malformated files should not crash with traceback."""
    cli_result = cli_runner.invoke(main.main, [empty_raw_fif])
    assert cli_result.exit_code == 1
    assert isinstance(cli_result.exception, SystemExit)  # temination with sys.exit() call
