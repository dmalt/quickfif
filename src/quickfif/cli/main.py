"""CLI entry point."""
from functools import wraps
from pathlib import Path
from typing import Callable, Concatenate, ParamSpec, Protocol, TypeVar

import click

from quickfif.cli.docs import FTYPE_HELP, get_ftype_choices
from quickfif.cli.errors import (
    BrokenFileClickError,
    ConsoleEmbedClickError,
    SaveFailedClickError,
    UnsupportedFtypeClickError,
)
from quickfif.config import Ftype, qf_read, qf_save
from quickfif.ipython import embed_ipython
from quickfif.parsers import parse_ftype
from quickfif.qf_types.base import QfType

P = ParamSpec("P")
T = TypeVar("T")


def pass_obj(wrapped: Callable[Concatenate[QfType, P], T]) -> Callable[P, T]:  # noqa: WPS221
    """Decorator to pass `click.Context.obj` instead of `click.Context`."""  # noqa: D401, D202

    @wraps(wrapped)
    @click.pass_context
    def wrapper(ctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> T:
        return ctx.invoke(wrapped, ctx.obj, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


class ClickContext(Protocol):
    """Refined part of `click.Context` that we actually use."""

    invoked_subcommand: str | None
    obj: QfType  # noqa: WPS110 (wrong variable name)


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
        qf_obj = qf_read(fpath, ftype)
    except Exception as exc:
        raise BrokenFileClickError(fpath, exc)

    if ctx.invoked_subcommand:
        ctx.obj = qf_obj  # pass the object to subcommands via context
    else:
        click.echo(qf_obj.summary)


@main.command()
@pass_obj
def inspect(qf_obj: QfType) -> None:
    """Inspect file in IPython interactive console."""
    try:
        embed_ipython(qf_obj.to_dict())
    except Exception as exc:
        raise ConsoleEmbedClickError(exc)


@main.command()
@click.argument("dst", type=click.Path(path_type=Path, dir_okay=True, writable=True))
@click.option("-o", "--overwrite", is_flag=True, default=False, help="Overwrite destination file.")
@pass_obj
def saveas(qf_obj: QfType, dst: Path, overwrite: bool) -> None:
    """Save mne file under different name. Existing destination is overwritten.

    Works correctly with large fif file splits.

    """
    try:
        qf_save(qf_obj, dst, overwrite)
    except Exception as exc:
        raise SaveFailedClickError(dst, exc)
