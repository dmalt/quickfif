import json
import shutil
from pathlib import Path

import click
import matplotlib

from mne_cli_tools import factory, inspect_utils, loader

matplotlib.use("TkAgg")

default_config = Path(__file__).resolve().parent / "config.json"


def load_plugins(ctx, param, cfg_path: str) -> None:
    with open(cfg_path, "r") as f:
        cfg = json.load(f)
    loader.load_plugins(cfg["ftype_plugins"])
    return cfg


def show_extensions(ctx, param, value):
    if not value:
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
        "fname in case the file is named unconventially; use --show-config to get "
        "the list of supported extensions"
    ),
)
@click.option(
    "-c",
    "--config",
    default=default_config,
    help=f"Specify path to configuration json; default={default_config}",
    type=click.Path(exists=True),
    callback=load_plugins,
    is_eager=True,
)
@click.option(
    "--show-config",
    is_flag=True,
    callback=show_extensions,
    is_eager=False,
    expose_value=False,
    help="Show current configuration and exit",
)
@click.pass_context
def main(ctx, fname, ext, config) -> None:
    """Show file preview"""
    ctx.ensure_object(dict)
    if ext is None:
        ctx.obj["mne_object"] = factory.create_auto(fname)
    else:
        ctx.obj["mne_object"] = factory.create_by_ext(fname, ext)

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
