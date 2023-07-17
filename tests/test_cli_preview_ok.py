"""Test green path for CLI invokation without subcommands (a.k.a. preview)."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture
from returns.io import IOResult

from mne_cli_tools import main
from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.config import Ftype, ReaderFunc


class FakeMneType(object):
    """Fake `MneType` implementation."""

    fpath: Path
    ftype: Ftype

    def __init__(self, test_path: Path, test_ft: Ftype):
        self.fpath = test_path
        self.ftype = test_ft

    def __str__(self) -> str:
        """Get object summary."""
        return "ftype: {0}, fpath: {1}".format(self.ftype, self.fpath)

    def to_dict(self) -> dict[str, Path | Ftype]:
        """Convert do dictionary."""
        return {"fpath": self.fpath, "ftype": self.ftype}


@pytest.fixture
def fake_read(
    monkeypatch: pytest.MonkeyPatch, empty_file_w_ftype: tuple[str, Ftype]
) -> tuple[str, Ftype]:
    """Patch mne object reading.

    Pathch the mapping from file type to reader function so each function
    returns fake mne type with wrapped fpath and ftype.

    """
    fpath, ftype = empty_file_w_ftype

    def factory(_):
        return IOResult.from_value(FakeMneType(Path(fpath), ftype))

    patched: dict[Ftype, ReaderFunc] = defaultdict(lambda: factory)
    monkeypatch.setattr(commands, "ftype_to_read_func", patched)
    return fpath, ftype


@pytest.mark.parametrize("pass_ft", [True, False])
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
def start_ipython_mock(mocker: MockerFixture):
    """Mock starting ipython embedded console session."""
    return mocker.patch("IPython.start_ipython", autospec=True)


@pytest.mark.parametrize("pass_ft", [True, False])
def test_inspect_succeeds_on_green_path(
    fake_read: tuple[str, Ftype], cli: CliRunner, pass_ft: bool, start_ipython_mock: Mock
) -> None:
    """Test inspect succeeds if object creation went fine."""
    fname, ftype = fake_read
    args = ["--ftype", ftype, fname, "inspect"] if pass_ft else [fname, "inspect"]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    start_ipython_mock.assert_called_once()
