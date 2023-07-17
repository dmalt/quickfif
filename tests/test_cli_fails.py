"""Test red path for CLI invokation without subcommands (a.k.a. preview)."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from mne_cli_tools import main
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.config import Ftype


def test_fails_wo_args(cli: CliRunner) -> None:
    """CLI must fail when executed without any arguments."""
    assert cli.invoke(main.main).exit_code == ExitCode.bad_click_path


@pytest.mark.parametrize("nonexist_fname", ["tmp.empty", "a.txt", "long name with spaces.longext"])
def test_fails_on_nonexistent_file(nonexist_fname: str, cli: CliRunner) -> None:
    """CLI must fail when supplied a nonexistent filename."""
    with cli.isolated_filesystem():
        cli_result = cli.invoke(main.main, [nonexist_fname])

    assert cli_result.exit_code == ExitCode.bad_click_path


@pytest.fixture(params=["tmp.empty", "a.txt", "long name with spaces.longext"])
def unsupported_fname(request, empty_file_factory) -> str:
    """Fname for existing file with unsupported extension."""
    return str(empty_file_factory(request.param))


def test_fails_gracefully_on_existing_unknown_file(unsupported_fname: str, cli: CliRunner) -> None:
    """Unknown file extension errors should be handled."""
    cli_result = cli.invoke(main.main, [unsupported_fname])

    assert cli_result.exit_code == ExitCode.unsupported_file
    assert isinstance(cli_result.exception, SystemExit)


def test_fails_gracefully_on_broken_file(
    empty_file_w_ftype: tuple[str, Ftype], cli: CliRunner, pass_ft: bool
) -> None:
    """Malformated file errors should be handled."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname] if pass_ft else [fname]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.broken_file
    assert isinstance(cli_result.exception, SystemExit)


@pytest.fixture(params=[0o444, 0o555])
def nonexistent_dst_in_readonly_dir(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    """Non-existent file path inside readonly dir."""
    nonwritable_dir = tmp_path / "subdir"
    nonwritable_dir.mkdir()
    dst = nonwritable_dir / "dst_path.nonexistent"
    mode = request.param
    nonwritable_dir.chmod(mode=mode)
    return dst


def test_copy_fails_gracefully_on_nonexist_dst_in_readonly_dir(
    fake_read: tuple[str, Ftype],
    cli: CliRunner,
    pass_ft: bool,
    nonexistent_dst_in_readonly_dir: Path,
) -> None:
    """
    Test unwritable case when dst file is inside unwritable dir and doesn't exits.

    Click Path writable checker doesn't handle this case.

    """
    fname, ftype = fake_read
    dst = str(nonexistent_dst_in_readonly_dir)
    args = ["--ftype", ftype, fname, "copy", dst] if pass_ft else [fname, "copy", dst]

    cli_result = cli.invoke(main.main, args)
    assert isinstance(cli_result.exception, SystemExit), cli_result.output
    assert cli_result.exit_code == ExitCode.write_failed
