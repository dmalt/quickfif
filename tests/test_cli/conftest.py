"""Doc."""

import pytest
from click.testing import CliRunner

from mne_cli_tools.config import Ftype
from mne_cli_tools.mct_types.base import MctType


@pytest.fixture
def cli():
    """Mock interacting with CLI from the console."""
    return CliRunner()


@pytest.fixture(params=[True, False], ids=["pass ft", "don't pass ft"])
def ftype_args(request, ftype: Ftype) -> list[str]:
    """Weither to pass file type to CLI or not with --ftype option."""
    return ["--ftype", str(ftype)] if request.param else []


@pytest.fixture()
def main_args(ftype_args: list[str], saved_mct_obj: MctType) -> list[str]:
    """Ftype option as returned by click."""
    return ftype_args + [str(saved_mct_obj.fpath)]
