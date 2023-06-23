"""CLI entry point."""
import json
import shutil
from pathlib import Path
from typing import Any

import click
import matplotlib

from mne_cli_tools import factory, inspect_utils, loader

matplotlib.use("TkAgg")

default_config = Path(__file__).resolve().parent / "config.json"


def _load_config(unused1: click.Context, unused2: Any, cfg_path: str) -> dict[str, Any]:
    del unused1, unused2  # noqa: WPS420
    with open(cfg_path, "r") as cfg_file:
        return json.load(cfg_file)


def _show_config(ctx: click.Context, _: Any, should_show_config: bool) -> None:
    if not should_show_config:
        return
    click.echo(json.dumps(ctx.params["config"], indent=2))
    ctx.exit()


@click.group(invoke_without_command=True)
@click.argument("fname", type=click.Path(exists=True))
@click.option(
    "-e",
    "--ext",
    help=(
        "Manually specify filetype via extension instead of getting it from"
        + "fname in case the file is named unconventially; use --show-config to get "
        + "the list of supported extensions"
    ),
)
@click.option(
    "-c",
    "--config",
    default=default_config,
    help="Path to configuration JSON; default={0}".format(default_config),
    type=click.Path(exists=True),
    callback=_load_config,
    is_eager=True,
)
@click.option(
    "--show-config",
    is_flag=True,
    callback=_show_config,
    is_eager=False,
    expose_value=False,
    help="Show current configuration and exit",
)
@click.pass_context
def main(ctx: click.Context, fname: str, ext: str | None, _: str) -> None:  # noqa: WPS216
    """When invoked without subcommands: show file preview."""
    ctx.ensure_object(dict)

    loader.load_plugins(ctx.params["config"]["ftype_plugins"])
    mne_obj = factory.create(fname, ext)

    if ctx.invoked_subcommand is None:
        click.echo(mne_obj)
    ctx.obj["mne_object"] = mne_obj


@main.command()
@click.pass_context
def inspect(ctx: click.Context) -> None:
    """Inspect file in IPython interactive console."""
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
        shutil.copy2(mne_object.fname, dst)
