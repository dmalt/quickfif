"""Test fixtures."""
from collections import defaultdict
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner
from returns.io import IOResult

from mne_cli_tools.api import commands
from mne_cli_tools.config import Ftype, ReadFunc, ext_to_ftype

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


@pytest.fixture(params=[True, False])
def pass_ft(request) -> bool:
    """Weither to pass ftype explicitly with --ftype."""
    return request.param


class FakeMneType(object):
    """Fake `MneType` implementation."""

    fpath: Path
    ftype: Ftype

    def __init__(self, test_path: Path, test_ft: Ftype):
        self.fpath = test_path
        self.ftype = test_ft

    def __str__(self) -> str:
        """Get object summary."""
        return "ftype: {0}, fpath: {1}".format(self.ftype, self.fpath)

    def to_dict(self) -> dict[str, Path | Ftype]:
        """Convert do dictionary."""
        return {"fpath": self.fpath, "ftype": self.ftype}


@pytest.fixture
def fake_read(
    monkeypatch: pytest.MonkeyPatch, empty_file_w_ftype: tuple[str, Ftype]
) -> tuple[str, Ftype]:
    """Patch mne object reading.

    Patch the mapping from file type to reader function so each function
    returns fake mne type with wrapped fpath and ftype.

    """
    fpath, ftype = empty_file_w_ftype

    def factory(_):
        return IOResult.from_value(FakeMneType(Path(fpath), ftype))

    patched: dict[Ftype, ReadFunc] = defaultdict(lambda: factory)
    monkeypatch.setattr(commands, "ftype_to_read_func", patched)
    return fpath, ftype
