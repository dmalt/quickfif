"""Test green path for CLI."""
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from quickfif.cli import main
from quickfif.cli.errors import ExitCode
from quickfif.qf_types.base import QfType

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
def save_dst(
    request: pytest.FixtureRequest,
    saved_qf_obj: QfType,
    tmp_path_factory: pytest.TempPathFactory,
) -> "Path":
    """Destination for saveas subcommand; can be file or directory."""
    dst_dir = tmp_path_factory.mktemp("save_dst_dir")
    if request.param:
        fname = saved_qf_obj.fpath.name
        return dst_dir / fname
    return dst_dir


@pytest.fixture(params=[True, False], ids=["overwrite", "no overwrite"])
def saveas_args(
    request: pytest.FixtureRequest, main_args: list[str], save_dst: "Path"
) -> list[str]:
    """Arguments for saveas CLI subcommand."""
    args = main_args + ["saveas", str(save_dst)]
    if request.param:
        args.append("--overwrite")
    return args


def test_dst_file_appears_after_save(
    cli: CliRunner, save_dst: "Path", saveas_args: list[str]
) -> None:
    """Test saveas CLI command calls api function."""
    cli_result = cli.invoke(main.main, saveas_args)

    assert cli_result.exit_code == ExitCode.ok, cli_result.output
    assert save_dst.exists()


@pytest.mark.parametrize("saveas_args", [False], indirect=True)
@pytest.mark.parametrize("ftype_args", [False], indirect=True)
def test_saveas_fails_gracefully_on_save_exception(
    cli: CliRunner, saveas_args: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test saveas terminates gracefully when wrapped function throws exception."""

    def fake_save(mne_obj, dst, overwrite):  # noqa: WPS430  # pyright: ignore
        raise Exception  # noqa: WPS454

    monkeypatch.setattr(main, "qf_save", fake_save)
    cli_result = cli.invoke(main.main, saveas_args)

    assert cli_result.exit_code == ExitCode.save_failed
