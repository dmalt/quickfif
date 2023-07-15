"""Test red path for CLI invokation without subcommands (a.k.a. preview)."""
import pytest
from click.testing import CliRunner

from mne_cli_tools import main
from mne_cli_tools.config import ExitCode
from mne_cli_tools.types import Ftype


def test_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == ExitCode.bad_fname_arg


@pytest.mark.parametrize("nonexist_fname", ["tmp.empty", "a.txt", "long name with spaces.longext"])
def test_fails_on_nonexistent_file(nonexist_fname: str, cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli.isolated_filesystem():
        cli_result = cli.invoke(main.main, [nonexist_fname])

    assert cli_result.exit_code == ExitCode.bad_fname_arg


@pytest.fixture(params=["tmp.empty", "a.txt", "long name with spaces.longext"])
def unsupported_fname(request, empty_file_factory) -> str:
    """Fname for existing file with unsupported extension."""
    return str(empty_file_factory(request.param))


def test_fails_gracefully_on_existing_unknown_file(unsupported_fname: str, cli: CliRunner) -> None:
    """Unknown file extension errors should be handled."""
    cli_result = cli.invoke(main.main, [unsupported_fname])

    assert cli_result.exit_code == ExitCode.unsupported_file
    assert isinstance(cli_result.exception, SystemExit)


@pytest.mark.parametrize("provide_ftype", [True, False])
def test_fails_gracefully_on_broken_file(
    empty_file_w_ftype: tuple[str, Ftype], cli: CliRunner, provide_ftype: bool
) -> None:
    """Malformated file errors should be handled."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname] if provide_ftype else [fname]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.broken_file
    assert isinstance(cli_result.exception, SystemExit)
