"""Test CLI main command without subcommands (a.k.a. preview)."""
import pytest
from click.testing import CliRunner

from mne_cli_tools import main
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.types import MneType


def test_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == ExitCode.bad_click_path


@pytest.mark.parametrize("nonexist_fname", ["tmp.empty", "a.txt", "long name with spaces.longext"])
def test_nonexistent_file_doesnt_pass_validation(nonexist_fname: str, cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli.isolated_filesystem():
        cli_result = cli.invoke(main.main, [nonexist_fname])

    assert cli_result.exit_code == ExitCode.bad_click_path


def test_preview_outputs_mne_obj_str(
    mock_read_mne_obj_result: MneType, cli: CliRunner, ftype_args: list[str]
) -> None:
    """Fake file reading and test the rest of preview logic."""
    args = ftype_args + [str(mock_read_mne_obj_result.fpath)]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert str(mock_read_mne_obj_result) in cli_result.output
