"""CLI entry point."""
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Concatenate, ParamSpec, Protocol, TypeVar

import click

from mne_cli_tools.api.commands import open_in_console, read_mne_obj, safe_copy
from mne_cli_tools.api.docs import ftype_help, get_ftype_choices
from mne_cli_tools.types import MneType

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
    obj: MneType  # noqa: WPS110 (wrong variable name)


@click.group(invoke_without_command=True)
@click.argument("fpath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-t", "--ftype", type=click.Choice(get_ftype_choices()), help=ftype_help)
@click.pass_context
def main(ctx: ClickContext, fpath: Path, ftype: str | None) -> None:
    """When invoked without subcommands: show file preview."""
    mne_obj = read_mne_obj(fpath, ftype)
    if ctx.invoked_subcommand:
        ctx.obj = mne_obj  # pass the object to subcommands via context
    else:
        click.echo(mne_obj)


@main.command()
@pass_obj
def inspect(mne_obj: MneType) -> None:
    """Inspect file in IPython interactive console."""
    open_in_console(mne_obj)


@main.command()
@click.argument("dst", type=click.Path(path_type=Path, dir_okay=True, writable=True))
@click.option("-o", "--overwrite", type=bool, default=False, help="Overwrite destination file.")
@pass_obj
def copy(mne_obj: MneType, dst: Path, overwrite: bool) -> None:
    """Safely copy mne file. Existing destination is overwritten.

    Works correctly with large fif file splits.

    """
    safe_copy(mne_obj, dst, overwrite)
