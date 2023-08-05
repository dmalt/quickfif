"""CLI entry point."""
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Concatenate, ParamSpec, Protocol, TypeVar

import click

from mne_cli_tools.cli.docs import FTYPE_HELP, get_ftype_choices
from mne_cli_tools.cli.errors import (
    BrokenFileClickError,
    ConsoleEmbedClickError,
    CopyFailedClickError,
    UnsupportedFtypeClickError,
)
from mne_cli_tools.config import Ftype, mct_read, mct_save
from mne_cli_tools.ipython import embed_ipython
from mne_cli_tools.mct_types.base import MctType
from mne_cli_tools.parsers import parse_ftype

P = ParamSpec("P")
T = TypeVar("T")


def pass_obj(  # type: ignore[misc] #  (explicit Any not allowed)
    wrapped: Callable[Concatenate[Any, P], T]
) -> Callable[Concatenate[click.Context, P], T]:
    """Decorator to pass `click.Context.obj` instead of `click.Context`."""  # noqa: D401, D202

    @wraps(wrapped)
    @click.pass_context
    def wrapper(ctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> T:
        return ctx.invoke(wrapped, ctx.obj, *args, **kwargs)

    return wrapper


class ClickContext(Protocol):
    """Refined part of `click.Context` that we actually use."""

    invoked_subcommand: bool
    obj: MctType  # noqa: WPS110 (wrong variable name)


@click.group(invoke_without_command=True)
@click.argument("fpath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-t", "--ftype", type=click.Choice(get_ftype_choices()), help=FTYPE_HELP)
@click.pass_context
def main(ctx: ClickContext, fpath: Path, ftype: str | None) -> None:
    """When invoked without subcommands: show file preview."""
    try:
        ftype = Ftype(ftype) if ftype else parse_ftype(fpath)
    except ValueError:
        raise UnsupportedFtypeClickError(fpath)

    try:
        mct_obj = mct_read(fpath, ftype)
    except Exception as exc:
        raise BrokenFileClickError(fpath, exc)

    if ctx.invoked_subcommand:
        ctx.obj = mct_obj  # pass the object to subcommands via context
    else:
        click.echo(mct_obj.summary)


@main.command()
@pass_obj
def inspect(mct_obj: MctType) -> None:
    """Inspect file in IPython interactive console."""
    try:
        embed_ipython(mct_obj.to_dict())
    except Exception as exc:
        raise ConsoleEmbedClickError(exc)


@main.command()
@click.argument("dst", type=click.Path(path_type=Path, dir_okay=True, writable=True))
@click.option("-o", "--overwrite", is_flag=True, default=False, help="Overwrite destination file.")
@pass_obj
def copy(mct_obj: MctType, dst: Path, overwrite: bool) -> None:
    """Safely copy mne file. Existing destination is overwritten.

    Works correctly with large fif file splits.

    """
    try:
        mct_save(mct_obj, dst, overwrite)
    except Exception as exc:
        raise CopyFailedClickError(dst, exc)
