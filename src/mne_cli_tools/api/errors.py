"""Exceptions for communication with click API."""
from enum import IntEnum, unique

import click


@unique
class ExitCode(IntEnum):
    """Exit codes for the CLI."""

    ok = 0
    aborted = 1
    bad_click_path = 2
    broken_file = 3
    unsupported_file = 4
    write_failed = 5


class UnsupportedFtypeError(click.FileError):
    """Click error for unknown file extension."""

    exit_code: ExitCode

    def __init__(self, fpath: str):
        hint = "\n".join(
            [
                "Can`t determine file type by extension.",
                "Try specifying the type manually via --ftype option.",
            ]
        )
        super().__init__(fpath, hint=hint)
        self.exit_code = ExitCode.unsupported_file


class BrokenFileError(click.FileError):
    """Click error for broken file."""

    def __init__(self, fpath: str, exc: Exception):
        super().__init__(fpath, hint=str(exc))
        self.exit_code = ExitCode.broken_file


class WriteFailedError(click.FileError):
    """Click error for failed write."""

    def __init__(self, fpath: str, exc: Exception):
        super().__init__(fpath, hint=str(exc))
        self.exit_code = ExitCode.write_failed
