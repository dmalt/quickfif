import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from mne_cli_tools.api.docs import get_ftype_choices
from tests.fake_mne_type import FakeMneType


@pytest.fixture(params=get_ftype_choices() + [None])
def ftype_args(request: pytest.FixtureRequest) -> list[str]:
    """Ftype option as returned by click."""
    return [] if request.param is None else ["--ftype", request.param]


@pytest.fixture
def cli():
    """Mock interacting with CLI from the console."""
    return CliRunner()


@pytest.fixture
def mock_read_mne_obj_result(mocker: MockerFixture, empty_file_factory) -> FakeMneType:
    """Patch mne obj reading. Return the return value of the mocked function."""
    fpath = empty_file_factory("test_base.test_ext")
    test_mne_obj = FakeMneType(fpath=fpath, mne_obj="test mne object")
    mock = mocker.patch("mne_cli_tools.main.read_mne_obj", autospec=True)
    mock.return_value = test_mne_obj

    return test_mne_obj
