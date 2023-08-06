"""Qf ica fixtures."""
from typing import TYPE_CHECKING, Callable

import pytest
from mne.preprocessing import ICA

from quickfif.qf_types.ica_type import EXTENSIONS as ICA_EXTENSIONS
from quickfif.qf_types.ica_type import QfIca

if TYPE_CHECKING:
    from pathlib import Path

    from mne.io import RawArray


@pytest.fixture
def ica_obj(raw_obj_factory: Callable[[int, float, float, str], "RawArray"]) -> ICA:
    """Fitted `mne.preprocessing.ICA` instance.

    ICA doesn't allow saving without fitting, so we fit it.

    """
    ica = ICA(n_components=4, fit_params={"tol": 1})  # set high tolerance to avoid warnings
    ica.fit(raw_obj_factory(10, 100, 5, "eeg"), verbose="ERROR")
    return ica


@pytest.fixture(params=ICA_EXTENSIONS)
def ica_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def qf_ica_factory(tmp_path: "Path", ica_obj: ICA) -> Callable[[str], QfIca]:
    def factory(ica_ext: str) -> QfIca:
        return QfIca(tmp_path / f"test{ica_ext}", ica_obj)

    return factory


@pytest.fixture
def qf_ica(ica_ext: str, qf_ica_factory: Callable[[str], QfIca]) -> QfIca:
    """Qf ica instance."""
    return qf_ica_factory(ica_ext)


@pytest.fixture
def saved_qf_ica(qf_ica) -> QfIca:
    """Qf ica instance saved to filesystem."""
    qf_ica.ica.save(qf_ica.fpath)
    return qf_ica
