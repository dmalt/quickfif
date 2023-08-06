"""Mct ica fixtures."""
from typing import TYPE_CHECKING, Callable

import pytest
from mne.preprocessing import ICA

from mne_cli_tools.mct_types.ica_type import EXTENSIONS as ICA_EXTENSIONS
from mne_cli_tools.mct_types.ica_type import MctIca

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
def mct_ica_factory(tmp_path: "Path", ica_obj: ICA) -> Callable[[str], MctIca]:
    def factory(ica_ext: str) -> MctIca:
        return MctIca(tmp_path / f"test{ica_ext}", ica_obj)

    return factory


@pytest.fixture
def mct_ica(ica_ext: str, mct_ica_factory: Callable[[str], MctIca]) -> MctIca:
    """Mct ica instance."""
    return mct_ica_factory(ica_ext)


@pytest.fixture
def saved_mct_ica(mct_ica) -> MctIca:
    """Mct ica instance saved to filesystem."""
    mct_ica.ica.save(mct_ica.fpath)
    return mct_ica
