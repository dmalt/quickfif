import json
import shutil
from collections import defaultdict
from pathlib import Path

import click
import matplotlib

from mne_cli_tools import factory, inspect_utils, loader

matplotlib.use("TkAgg")

default_config = Path(__file__).resolve().parent / "config.json"


def load_plugins(ctx, param, cfg_path: str) -> None:
    with open(cfg_path, "r") as f:
        cfg = json.load(f)
    loader.load_plugins(cfg["plugins"])


def show_extensions(ctx, param, value):
    if not value:
        return
    dd = defaultdict(list)
    for k, v in sorted(factory.registered_types.items()):
        dd[v.__name__].append(k)

    for k, v in sorted(dd.items()):
        click.echo(k + ":")
        for ext in v:
            click.echo("\t" + ext)

    ctx.exit()


@click.group(invoke_without_command=True)
@click.argument("fname", type=click.Path(exists=True))
@click.option(
    "-c",
    "--config",
    default=default_config,
    help="path to configuration json",
    type=click.Path(exists=True),
    callback=load_plugins,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--show-extensions", is_flag=True, callback=show_extensions, expose_value=False, is_eager=False
)
@click.pass_context
def main(ctx, fname) -> None:
    """Show file preview"""
    ctx.ensure_object(dict)
    ctx.obj["mne_object"] = factory.create(fname)

    if ctx.invoked_subcommand is None:
        print(ctx.obj["mne_object"])


@main.command()
@click.pass_context
def inspect(ctx):
    """Inspect file in IPython interactive console"""
    inspect_utils.embed(ctx.obj["mne_object"].to_dict())


@main.command()
@click.pass_context
@click.argument("dst", type=click.Path())
def copy(ctx, dst):
    """
    Safely copy mne file. Existing destination is overwritten.

    Works correctly also with large fif file splits

    """
    mne_object = ctx.obj["mne_object"]
    if hasattr(mne_object, "copy"):
        mne_object.copy(dst)
    else:
        shutil.copy2(mne_object.fname, dst)
