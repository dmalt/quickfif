"""Exceptions for communication with click API."""
from enum import IntEnum, unique
from pathlib import Path

import click

from mne_cli_tools.cli.docs import UNSUPPORTED_FTYPE_ERROR_MSG


@unique
class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    ok = 0
    aborted = 1
    bad_click_path = 2
    broken_file = 3
    unsupported_file = 4
    copy_failed = 5
    embed_failed = 6


class UnsupportedFtypeClickError(click.FileError):
    """Click error for unknown file extension."""

    def __init__(self, fpath: Path):
        hint = UNSUPPORTED_FTYPE_ERROR_MSG
        super().__init__(str(fpath), hint=hint)
        self.exit_code = ExitCode.unsupported_file


class BrokenFileClickError(click.FileError):
    """Click error for broken file."""

    def __init__(self, fpath: Path, exc: Exception):
        super().__init__(str(fpath), hint=str(exc))
        self.exit_code = ExitCode.broken_file


class CopyFailedClickError(click.FileError):
    """Click error for failed write."""

    def __init__(self, fpath: Path, exc: Exception):
        super().__init__(str(fpath), hint=str(exc))
        self.exit_code = ExitCode.copy_failed


class ConsoleEmbedClickError(click.ClickException):
    """Error when ipython_embed failed."""

    def __init__(self, exc: Exception):
        super().__init__(message=str(exc))
        self.exit_code = ExitCode.embed_failed
