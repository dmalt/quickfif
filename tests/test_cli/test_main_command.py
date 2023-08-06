"""Test CLI main command without subcommands (a.k.a. preview)."""
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Callable

import pytest
from click.testing import CliRunner

from quickfif.cli import main
from quickfif.cli.errors import ExitCode
from quickfif.config import EXT_TO_FTYPE
from quickfif.qf_types.base import QfType

if TYPE_CHECKING:
    from pathlib import Path


def test_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == ExitCode.bad_click_path


@pytest.mark.parametrize(
    "nonexist_fname", ["test_raw.fif", "tmp.empty", "a.txt", "long name with spaces.longext"]
)
def test_nonexistent_file_doesnt_pass_validation(nonexist_fname: str, cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli.isolated_filesystem():
        cli_result = cli.invoke(main.main, [nonexist_fname])

    assert cli_result.exit_code == ExitCode.bad_click_path


@pytest.fixture(params=["tmp.empty", "a.txt", "long name with spaces.longext"])
def empty_unsupported_fpath(
    request: pytest.FixtureRequest, empty_file_factory: Callable[[str], "Path"]
) -> "Path":
    """Path to empty file with unsupported extension."""
    assert not request.param.endswith(tuple(EXT_TO_FTYPE))
    return empty_file_factory(request.param)


def test_existing_file_with_unsupported_ext_doesnt_pass_validation(
    cli: CliRunner, empty_unsupported_fpath: "Path"
):
    """Test main command does extension parsing."""
    cli_result = cli.invoke(main.main, [str(empty_unsupported_fpath)])

    assert cli_result.exit_code == ExitCode.unsupported_file


@pytest.mark.parametrize("ext", list(EXT_TO_FTYPE))
def test_bad_existing_supported_file_fails_gracefully(
    cli: CliRunner,
    empty_file_factory: Callable[[str], "Path"],
    ext: str,
    ftype_args: list[str],
) -> None:
    """Test we handle reader error in case read fails."""
    bad_supported_fpath = empty_file_factory(f"bad{ext}")
    args = ftype_args + [str(bad_supported_fpath)]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.broken_file


def assert_similar(a: str, b: str, thresh: float = 0.9) -> None:
    """Assert two strings are similar using sequence matcher ratio."""
    assert SequenceMatcher(None, a, b).ratio() > thresh


@pytest.mark.parametrize("ext", ["raw.fif"])
def test_preview_outputs_qf_obj_str(
    cli: CliRunner, saved_qf_obj: QfType, main_args: list[str]
) -> None:
    """Test the whole thing on previewing."""
    cli_result = cli.invoke(main.main, main_args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    # for some qf types we print info which may differ a bit for read vs created objects
    # so we check for similarity, not equality
    assert_similar(saved_qf_obj.summary, cli_result.output)
