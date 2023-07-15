"""Test fixtures."""
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli():
    """Mock interacting with CLI from the console."""
    return CliRunner()


@pytest.fixture(scope="session")
def empty_file_factory(tmp_path_factory) -> Callable[[str], Path]:
    """Empty file factory. Parametrization by base name and extension."""

    def factory(fname: str) -> Path:
        empty_fpath = tmp_path_factory.mktemp("data", numbered=True) / fname
        empty_fpath.touch(exist_ok=False)
        return empty_fpath

    return factory
