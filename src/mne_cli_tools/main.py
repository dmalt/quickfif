"""CLI entry point."""
import json
import shutil
from pathlib import Path

import click
import matplotlib

from mne_cli_tools import factory, inspect_utils
from mne_cli_tools.config import FTYPES, ext2ftype, type_constructors
from mne_cli_tools.types import Ftype, ReadableFpath


def _show_config(ctx: click.Context, _: object, should_show_config: bool) -> None:
    if not should_show_config:
        return
    click.echo(json.dumps(ctx.params["config"], indent=2))
    ctx.exit()


ftype_help = "Manually specify file type instead of guessing it from extension"


@click.group(invoke_without_command=True, epilog=str(ext2ftype))
@click.argument("fpath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-t", "--ftype", type=click.Choice(FTYPES), help=ftype_help)
@click.option(
    "--show-config",
    is_flag=True,
    callback=_show_config,
    is_eager=False,
    expose_value=False,
    help="Show current configuration and exit",
)
@click.pass_context
def main(ctx: click.Context, fpath: ReadableFpath, ftype: Ftype | None) -> None:
    """When invoked without subcommands: show file preview."""
    ctx.ensure_object(dict)
    mne_obj = factory.create(fpath, Ftype(ftype) if ftype else None, type_constructors)
    if ctx.invoked_subcommand is None:
        click.echo(mne_obj)
    ctx.obj["mne_object"] = mne_obj


@main.command()
@click.pass_context
def inspect(ctx: click.Context) -> None:
    """Inspect file in IPython interactive console."""
    matplotlib.use("TkAgg")
    inspect_utils.embed_ipython(ctx.obj["mne_object"].to_dict())


@main.command()
@click.pass_context
@click.argument("dst", type=click.Path())
def copy(ctx: click.Context, dst: str) -> None:
    """
    Safely copy mne file. Existing destination is overwritten.

    Works correctly also with large fif file splits

    """
    mne_object = ctx.obj["mne_object"]
    try:
        mne_object.copy(dst)
    except AttributeError:
        shutil.copy2(mne_object.fpath, dst)
