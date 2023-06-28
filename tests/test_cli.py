"""Tests mimicking interaction with the CLI from a terminal."""
import json

import pytest
from click.testing import CliRunner

from mne_cli_tools import main


def test_cli_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == 2


def test_cli_fails_for_nonexistent_fname(cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli.isolated_filesystem():
        nonexistent_fname = "i_dont_exist.fif"
        cli_result = cli.invoke(main.main, [nonexistent_fname])

        assert cli_result.exit_code == 2
        err_template = "Error: Invalid value for 'FNAME': Path '{0}' does not exist."
        assert err_template.format(nonexistent_fname) in cli_result.output


def test_cli_succeeds_with_show_config_option(cli: CliRunner) -> None:
    """--show-config option must work without fname argument."""
    cli_result = cli.invoke(main.main, ["--show-config"])
    assert cli_result.exit_code == 0


class BadConfigurationFormatError(Exception):
    """When CLI configuration format is messed up."""


def test_show_config_shows_vaild_json(cli: CliRunner) -> None:
    """--show-config option must work without fname argument."""
    cli_result = cli.invoke(main.main, ["--show-config"])
    assert cli_result.exit_code == 0
    try:
        json.loads(cli_result.output)
    except json.JSONDecodeError:
        raise BadConfigurationFormatError("Printed config is not a valid JSON!")


@pytest.mark.parametrize("empty_file", [".empty"], indirect=True)
def test_cli_succeeds_on_empty_file_with_unsupported_ext(empty_file: str, cli: CliRunner) -> None:
    """Empty file should be."""
    cli_result = cli.invoke(main.main, [empty_file])
    assert not cli_result.exit_code


@pytest.mark.parametrize("opt", [[], ["--ext", "raw.fif"]])
@pytest.mark.parametrize("empty_file", ["_raw.fif"], indirect=True)
def test_cli_fails_gracefully_on_bad_raw_fif(
    empty_file: str, cli: CliRunner, opt: list[str]
) -> None:
    """Malformated files should not crash with traceback."""
    cli_result = cli.invoke(main.main, opt + [empty_file])
    assert cli_result.exit_code == 1
    assert isinstance(cli_result.exception, SystemExit)  # temination with sys.exit() call
