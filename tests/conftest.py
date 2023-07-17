"""Test fixtures."""
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from mne_cli_tools.config import Ftype, ext_to_ftype

EXTENSIONS = list(ext_to_ftype)


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


@pytest.fixture(params=EXTENSIONS)
def empty_file_w_ext(request, empty_file_factory: Callable[[str], Path]) -> tuple[str, str]:
    """Fname for file with supported extension but unreadable contents + its extension."""
    ext = request.param
    return str(empty_file_factory(f"tmp{ext}")), ext


@pytest.fixture
def empty_file_w_ftype(empty_file_w_ext: tuple[str, str]) -> tuple[str, Ftype]:
    """Fname for file with supported extension but unreadable contents + its ftype."""
    fname, ext = empty_file_w_ext
    return fname, ext_to_ftype[ext]
