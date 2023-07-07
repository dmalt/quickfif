"""Tests mimicking interaction with the CLI from a terminal."""
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from mne_cli_tools import main
from mne_cli_tools.config import EXTENSIONS, ExitCode


def test_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == ExitCode.bad_fname_arg


@pytest.mark.parametrize(
    "nonexist_fname", ["tmp.empty", "a.txt", "long name with spaces.longext"]
)  # type: ignore[misc]
def test_fails_on_nonexistent_file(nonexist_fname: str, cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    err_msg = "Error: Invalid value for 'FPATH': File '{0}' does not exist.".format(nonexist_fname)

    with cli.isolated_filesystem():
        cli_result = cli.invoke(main.main, [nonexist_fname])

    assert cli_result.exit_code == ExitCode.bad_fname_arg
    assert err_msg in cli_result.output


@pytest.fixture(
    params=["tmp.empty", "a.txt", "long name with spaces.longext"],
)  # type: ignore[misc]
def unsupported_fname(request, empty_file_factory) -> str:
    """Fname for existing file with unsupported extension."""
    return str(empty_file_factory(request.param))


def test_succeeds_on_existing_unknown_file(unsupported_fname: str, cli: CliRunner) -> None:
    """Unknown extensions shouldn't cause error: we just print a message to stdout."""
    cli_result = cli.invoke(main.main, [unsupported_fname])

    assert cli_result.exit_code == ExitCode.ok
    assert "unsupported" in cli_result.output.lower()


@pytest.fixture(params=[f"tmp{ext}" for ext in EXTENSIONS])  # type: ignore[misc]
def bad_supported_file(request, empty_file_factory: "Callable[[str], Path]") -> str:
    """File with supported extension but unreadable contents."""
    return str(empty_file_factory(request.param))


def test_fails_gracefully_when_object_read_fails_on_inferred_ftype(
    bad_supported_file: str, cli: CliRunner
) -> None:
    """Malformated files should not cause ugly crash (with traceback and so on)."""
    cli_result = cli.invoke(main.main, [bad_supported_file])

    assert cli_result.exit_code == ExitCode.broken_file
    # exception handled and cli teminated with sys.exit() call
    assert isinstance(cli_result.exception, SystemExit)
