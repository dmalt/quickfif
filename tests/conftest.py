"""Project-level fixtures."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from mne_cli_tools.config import EXT_TO_FTYPE, Ftype, mct_save
from mne_cli_tools.mct_types.annots_type import EXTENSIONS as ANNOTS_EXTENSIONS
from mne_cli_tools.mct_types.annots_type import MctAnnots
from mne_cli_tools.mct_types.base import MctType
from mne_cli_tools.mct_types.epochs_type import EXTENSIONS as EPOCHS_EXTENSIONS
from mne_cli_tools.mct_types.epochs_type import MctEpochs
from mne_cli_tools.mct_types.raw_type import EXTENSIONS as RAW_EXTENSIONS
from mne_cli_tools.mct_types.raw_type import MctRaw

pytest_plugins = (
    "tests.plugins.raw_fif_fixtures",
    "tests.plugins.annots_fixtures",
    "tests.plugins.ica_fixtures",
    "tests.plugins.epochs_fixtures",
)


@pytest.fixture(scope="session")
def empty_file_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Empty file factory. Parametrization by base name and extension."""

    def factory(fname: str) -> Path:
        empty_fpath = tmp_path_factory.mktemp("data", numbered=True) / fname
        empty_fpath.touch(exist_ok=False)
        return empty_fpath

    return factory


@pytest.fixture(scope="session")
def mock_fn_factory(mocker: MockerFixture) -> Callable[[object, str], Mock]:
    """Mock wrapped function with dummy returning return_value."""

    def factory(return_value: object, fn_namespace_path: str) -> Mock:  # pyright: ignore
        mock_copy = mocker.patch(fn_namespace_path, autospec=True)
        mock_copy.return_value = return_value
        return mock_copy

    return factory


@pytest.fixture(params=RAW_EXTENSIONS + EPOCHS_EXTENSIONS)
def ext(request) -> str:
    """`MctType` obj saved to a filesystem."""
    return request.param


@pytest.fixture()
def ftype(ext: str) -> Ftype:
    """Ftype instance."""
    return EXT_TO_FTYPE[ext]


@pytest.fixture
def mct_obj(
    ftype: Ftype,
    ext: str,
    mct_raw_factory: Callable[[str], MctRaw],
    mct_epochs_factory: Callable[[str], MctEpochs],
    mct_annots_factory: Callable[[str], MctAnnots],
) -> MctType:
    match ftype:
        case Ftype.raw:
            return mct_raw_factory(ext)
        case Ftype.epochs:
            return mct_epochs_factory(ext)
        case Ftype.annots:
            return mct_annots_factory(ext)
        case _:
            raise ValueError


@pytest.fixture
def saved_mct_obj(mct_obj: MctType) -> MctType:
    mct_save(mct_obj, mct_obj.fpath, overwrite=False)
    return mct_obj
