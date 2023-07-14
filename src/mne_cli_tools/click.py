from pathlib import Path
from typing import NoReturn, Protocol

import click
from returns.curry import curry
from returns.io import IO

from mne_cli_tools.config import ExitCode
from mne_cli_tools.files import UnsupportedFtypeError
from mne_cli_tools.types import MneType


class ClickContext(Protocol):
    """Refined part of `click.Context` that we actually use."""

    invoked_subcommand: bool
    obj: IO[MneType]  # noqa: WPS110 (wrong variable name)


@curry
def raise_click_file_error(fpath: Path, exc: Exception) -> NoReturn:
    click_exc = click.FileError(str(fpath), hint=str(exc))
    if isinstance(exc, UnsupportedFtypeError):
        click_exc.exit_code = ExitCode.unsupported_file
    else:
        click_exc.exit_code = ExitCode.broken_file
    raise click_exc
