import json
import shutil
from pathlib import Path

import click
import matplotlib

from mne_cli_tools import factory, inspect_utils, loader

matplotlib.use("TkAgg")

default_config = Path(__file__).resolve().parent / "config.json"


@click.group(invoke_without_command=True)
@click.argument("fname", type=click.Path(exists=True))
@click.option(
    "-c",
    "--config",
    default=default_config,
    help="path to configuration json",
    type=click.Path(exists=True),
)
@click.pass_context
def main(ctx, fname, config) -> None:
    """Show file preview"""
    ctx.ensure_object(dict)
    with open(config, "r") as f:
        cfg = json.load(f)

    loader.load_plugins(cfg["plugins"])
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
