"""Tests mimicking interaction with the CLI from a terminal."""
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner
from returns.io import IOResult

from mne_cli_tools import main
from mne_cli_tools.config import EXTENSIONS, ExitCode, ext2ftype


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


def test_succeeds_on_existing_unknown_file(unsupported_fname: str, cli: CliRunner) -> None:
    """Unknown extensions shouldn't cause error: we just print a message to stdout."""
    cli_result = cli.invoke(main.main, [unsupported_fname])

    assert cli_result.exit_code == ExitCode.unsupported_file


@pytest.fixture(params=EXTENSIONS)
def empty_file_w_ext(request, empty_file_factory: "Callable[[str], Path]") -> tuple[str, str]:
    """Fname for file with supported extension but unreadable contents + its extension."""
    ext = request.param
    return str(empty_file_factory(f"tmp{ext}")), ext


@pytest.fixture
def empty_file_w_ftype(empty_file_w_ext):
    """Fname for file with supported extension but unreadable contents + its ftype."""
    fname, ext = empty_file_w_ext
    return fname, ext2ftype[ext]


@pytest.mark.parametrize("provide_ftype", [True, False])
def test_fails_gracefully_when_object_read_fails(
    empty_file_w_ftype: tuple[str, str], cli: CliRunner, provide_ftype: bool
) -> None:
    """Malformated files should not cause ugly crash (with traceback and so on)."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname] if provide_ftype else [fname]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.broken_file
    # exception handled and cli teminated with sys.exit() call
    assert isinstance(cli_result.exception, SystemExit)


class FakeMneType(object):
    def __init__(self, test_str: str):
        self.test_str = test_str

    def __str__(self) -> str:
        return self.test_str

    def to_dict(self) -> dict[str, str]:
        return {"test_str": self.test_str}


def fake_create(x, y):
    return IOResult.from_value(FakeMneType(str(x) + str(y)))


@pytest.mark.parametrize("provide_ftype", [True, False])
def test_preview_succeeds_when_read_ok(
    empty_file_w_ftype: tuple[str, str],
    monkeypatch: pytest.MonkeyPatch,
    cli: CliRunner,
    provide_ftype: bool,
) -> None:
    """."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname] if provide_ftype else [fname]
    monkeypatch.setattr(main, "create", fake_create)

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert "test" in cli_result.output
