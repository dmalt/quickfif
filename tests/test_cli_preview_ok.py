"""Test green path for CLI invokation without subcommands (a.k.a. preview)."""
from collections import defaultdict
from pathlib import Path

import pytest
from click.testing import CliRunner
from returns.io import IOResult

from mne_cli_tools import main
from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import ExitCode
from mne_cli_tools.config import Ftype, ReaderFunc


class FakeMneType(object):
    """Fake `MneType` implementation."""

    fpath: Path

    def __init__(self, test_str: str):
        self.test_str = test_str
        self.fpath = Path(test_str)

    def __str__(self) -> str:
        """Get object summary."""
        return self.test_str

    def to_dict(self) -> dict[str, str]:
        """Convert do dictionary."""
        return {"test_str": self.test_str}


@pytest.fixture
def fake_create_msg(monkeypatch: pytest.MonkeyPatch) -> str:
    """Patch create() function. Return test string wrapped inside."""
    test_msg = "Hello, Test!"

    def factory(_):
        return IOResult.from_value(FakeMneType(test_msg))

    patched: dict[Ftype, ReaderFunc] = defaultdict(lambda: factory)
    monkeypatch.setattr(commands, "ftype_to_read_func", patched)
    return test_msg


@pytest.mark.parametrize("provide_ftype", [True, False])
def test_preview_succeeds_when_read_ok(
    empty_file_w_ftype: tuple[str, Ftype],
    fake_create_msg: str,
    cli: CliRunner,
    provide_ftype: bool,
) -> None:
    """Fake file reading and test the rest of preview logic."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname] if provide_ftype else [fname]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert fake_create_msg in cli_result.output


@pytest.mark.parametrize("provide_ftype", [True, False])
def test_inspect_succeeds(
    empty_file_w_ftype: tuple[str, Ftype],
    fake_create_msg: str,
    cli: CliRunner,
    provide_ftype: bool,
) -> None:
    """Test inspect succeeds if object creation went fine."""
    fname, ftype = empty_file_w_ftype
    args = ["--ftype", ftype, fname, "inspect"] if provide_ftype else [fname, "inspect"]

    cli_result = cli.invoke(main.main, args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert fake_create_msg in cli_result.output
