"""CLI entry point."""
import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Concatenate, NoReturn, ParamSpec, Protocol, TypeVar

import click
import matplotlib
from returns.curry import curry
from returns.io import IO, impure
from returns.maybe import Maybe

from mne_cli_tools.config import ExitCode, create, ext2ftype
from mne_cli_tools.files import UnsupportedFtypeError
from mne_cli_tools.ipython import embed_ipython
from mne_cli_tools.types import Ftype, MneType, ReadableFpath

P = ParamSpec("P")
T = TypeVar("T")


class ClickContext(Protocol):
    """Refined part of `click.Context` that we actually use."""

    invoked_subcommand: bool
    obj: IO[MneType]  # noqa: WPS110 (wrong variable name)


def pass_obj(  # type: ignore[misc]
    wrapped: Callable[Concatenate[Any, P], T]
) -> Callable[Concatenate[click.Context, P], T]:
    """Decorator to pass `click.Context.obj` instead of `click.Context`."""  # noqa: D401, D202

    @wraps(wrapped)
    @click.pass_context
    def wrapper(ctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> T:
        return ctx.invoke(wrapped, ctx.obj, *args, **kwargs)

    return wrapper


ftype_help = "Manually specify file type instead of guessing it from extension"


@curry
def _raise_click_file_error(fpath: Path, exc: Exception) -> NoReturn:
    click_exc = click.FileError(str(fpath), hint=str(exc))
    if isinstance(exc, UnsupportedFtypeError):
        click_exc.exit_code = ExitCode.unsupported_file
    else:
        click_exc.exit_code = ExitCode.broken_file
    raise click_exc


def _create_mne_obj(fpath: Path, ftype: str | None) -> IO[MneType]:
    maybe_ft = Maybe.from_optional(ftype).map(Ftype)
    # Hackish. Ftype() theoretically can fail for bad ftype string but never should
    # because click.Choice is aligned with Ftype enum Enum-based choice
    # type should appear in click 8.2.0, see https://github.com/pallets/click/pull/2210
    return create(fpath, maybe_ft).alt(_raise_click_file_error(fpath)).unwrap()  # pyright: ignore


@click.group(invoke_without_command=True, epilog=str(ext2ftype))
@click.argument("fpath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-t", "--ftype", type=click.Choice(Ftype.get_values()), help=ftype_help)
@click.pass_context
def main(ctx: ClickContext, fpath: ReadableFpath, ftype: str | None) -> None:
    """When invoked without subcommands: show file preview."""
    mne_obj = _create_mne_obj(fpath, ftype)

    if ctx.invoked_subcommand:
        ctx.obj = mne_obj
    else:
        mne_obj.map(click.echo)


@main.command()
@pass_obj
@impure
def inspect(mne_obj: IO[MneType]) -> None:
    """Inspect file in IPython interactive console."""
    matplotlib.use("TkAgg")
    mne_obj.bind(lambda x: embed_ipython(x.to_dict()))


@main.command()
@click.argument("dst", type=click.Path())
@pass_obj
def copy(mne_obj: IO[MneType], dst: str) -> None:
    """
    Safely copy mne file. Existing destination is overwritten.

    Works correctly also with large fif file splits

    """
    try:
        mne_obj.copy(dst)
    except AttributeError:
        shutil.copy2(mne_obj.fpath, dst)
