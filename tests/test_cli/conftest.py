"""Doc."""

import pytest
from click.testing import CliRunner

from quickfif.config import Ftype
from quickfif.qf_types.base import QfType


@pytest.fixture
def cli():
    """Mock interacting with CLI from the console."""
    return CliRunner()


@pytest.fixture(params=[True, False], ids=["pass ft", "don't pass ft"])
def ftype_args(request, ftype: Ftype) -> list[str]:
    """Weither to pass file type to CLI or not with --ftype option."""
    return ["--ftype", str(ftype)] if request.param else []


@pytest.fixture()
def main_args(ftype_args: list[str], saved_qf_obj: QfType) -> list[str]:
    """Ftype option as returned by click."""
    return ftype_args + [str(saved_qf_obj.fpath)]
