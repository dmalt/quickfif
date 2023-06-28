"""Test fixtures."""
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli():
    """Mock interacting with CLI from the console."""
    return CliRunner()


@pytest.fixture(params=[".empty", "_raw.fif"])
def empty_file(tmp_path: Path, request) -> str:
    """Bad _raw.fif file fixture."""
    empty_fpath = tmp_path / "tmp{ext}".format(ext=request.param)
    empty_fpath.touch(exist_ok=True)
    return str(empty_fpath)
