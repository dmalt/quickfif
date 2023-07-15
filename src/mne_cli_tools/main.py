"""CLI entry point."""
import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Concatenate, ParamSpec, Protocol, TypeVar

import click
import matplotlib
from returns.io import IO, impure

from mne_cli_tools.click_bridge import read_mne_obj
from mne_cli_tools.config import ext_to_ftype
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


@click.group(invoke_without_command=True, epilog=str(ext_to_ftype))
@click.argument("fpath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-t", "--ftype", type=click.Choice(Ftype.get_values()), help=ftype_help)
@click.pass_context
def main(ctx: ClickContext, fpath: ReadableFpath, ftype: str | None) -> None:
    """When invoked without subcommands: show file preview."""
    mne_obj = read_mne_obj(fpath, ftype)
    if ctx.invoked_subcommand:
        ctx.obj = mne_obj  # pass the object to subcommands via context
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
    """Safely copy mne file. Existing destination is overwritten.

    Works correctly also with large fif file splits.

    """
    try:
        mne_obj.copy(dst)
    except AttributeError:
        shutil.copy2(mne_obj.fpath, dst)
