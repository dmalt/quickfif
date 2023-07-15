"""Test green path for CLI invokation without subcommands (a.k.a. preview)."""
import pytest
from click.testing import CliRunner
from returns.io import IOResult

from mne_cli_tools import main
from mne_cli_tools.config import ExitCode
from mne_cli_tools.types import Ftype


class FakeMneType(object):
    """Fake `MneType` implementation."""

    def __init__(self, test_str: str):
        self.test_str = test_str

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

    def factory(_x, _y):  # pyright: ignore (unused names)
        return IOResult.from_value(FakeMneType(test_msg))

    monkeypatch.setattr(main, "create", factory)
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
