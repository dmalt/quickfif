"""Test green path for CLI."""
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from mne_cli_tools.cli import main
from mne_cli_tools.cli.errors import ExitCode
from mne_cli_tools.mct_types.base import MctType

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def inspect_args(main_args: list[str]) -> list[str]:
    """Arguments for inspect subcommand."""
    return main_args + ["inspect"]


def test_inspect_succeeds_on_green_path(cli: CliRunner, inspect_args: list[str]) -> None:
    """Test inspect succeeds if object creation went fine."""
    cli_result = cli.invoke(main.main, inspect_args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output


def test_inspect_fails_gracefully_on_embed_exception(
    cli: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    inspect_args: list[str],
):
    """Test we handle console embedding crash."""

    def fake_embed_ipython(ns):  # noqa: WPS430  # pyright: ignore
        raise Exception  # noqa: WPS454

    monkeypatch.setattr(main, "embed_ipython", fake_embed_ipython)

    cli_res = cli.invoke(main.main, inspect_args)

    assert cli_res.exit_code == ExitCode.embed_failed


@pytest.fixture(params=[True, False], ids=["file", "dir"])
def copy_dst(
    request: pytest.FixtureRequest,
    saved_mct_obj: MctType,
    tmp_path_factory: pytest.TempPathFactory,
) -> "Path":
    """Destination for copy subcommand; can be file or directory."""
    dst_dir = tmp_path_factory.mktemp("copy_dst_dir")
    if request.param:
        fname = saved_mct_obj.fpath.name
        return dst_dir / fname
    return dst_dir


@pytest.fixture(params=[True, False], ids=["overwrite", "no overwrite"])
def copy_args(request: pytest.FixtureRequest, main_args: list[str], copy_dst: "Path") -> list[str]:
    """Arguments for copy CLI subcommand."""
    args = main_args + ["copy", str(copy_dst)]
    if request.param:
        args.append("--overwrite")
    return args


@pytest.mark.parametrize("copy_args", [False], indirect=True)
def test_dst_file_appears_after_copy(
    cli: CliRunner, copy_dst: "Path", copy_args: list[str]
) -> None:
    """Test copy CLI command calls api function."""
    cli_result = cli.invoke(main.main, copy_args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert copy_dst.exists()


def test_copy_fail(cli: CliRunner, copy_args: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Test copy CLI command calls api function."""

    def fake_save(mne_obj, dst, overwrite):  # noqa: WPS430  # pyright: ignore
        raise Exception  # noqa: WPS454

    monkeypatch.setattr(main, "mct_save", fake_save)
    cli_result = cli.invoke(main.main, copy_args)

    assert cli_result.exit_code == ExitCode.copy_failed
