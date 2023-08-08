"""Project-level fixtures."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from quickfif.config import EXT_TO_FTYPE, Ftype, qf_save
from quickfif.qf_types import annots_type, epochs_type, ica_type, raw_type
from quickfif.qf_types.base import QfType

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
        mock_fn = mocker.patch(fn_namespace_path, autospec=True)
        mock_fn.return_value = return_value
        return mock_fn

    return factory


@pytest.fixture(params=list(EXT_TO_FTYPE))
def ext(request) -> str:
    """`QfType` obj saved to a filesystem."""
    return request.param


@pytest.fixture()
def ftype(ext: str) -> Ftype:
    """Ftype instance."""
    return EXT_TO_FTYPE[ext]


@pytest.fixture
def qf_obj(  # noqa: WPS211
    ftype: Ftype,
    ext: str,
    qf_raw_factory: Callable[[str], raw_type.QfRaw],
    qf_epochs_factory: Callable[[str], epochs_type.QfEpochs],
    qf_annots_factory: Callable[[str], annots_type.QfAnnots],
    qf_ica_factory: Callable[[str], ica_type.QfIca],
) -> QfType:
    """General QfType object. Concrete type is determined by ftype."""
    ftype_to_obj: dict[Ftype, QfType] = {
        Ftype.raw: qf_raw_factory(ext),
        Ftype.epochs: qf_epochs_factory(ext),
        Ftype.annots: qf_annots_factory(ext),
        Ftype.ica: qf_ica_factory(ext),
    }
    return ftype_to_obj[ftype]


@pytest.fixture
def saved_qf_obj(qf_obj: QfType) -> QfType:
    """`QfType` object saved at `QfType.fpath`."""
    qf_save(qf_obj, qf_obj.fpath, overwrite=False)
    return qf_obj
