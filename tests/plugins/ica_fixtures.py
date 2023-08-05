"""Mct ica fixtures."""
from typing import TYPE_CHECKING, Callable

import pytest
from mne.preprocessing import ICA

from mne_cli_tools.mct_types import ica

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


@pytest.fixture(params=ica.EXTENSIONS)
def ica_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def mct_ica(tmp_path: "Path", ica_obj: ICA, ica_ext: str) -> ica.IcaFif:
    """Mct ica instance."""
    return ica.IcaFif(tmp_path / f"test{ica_ext}", ica_obj)


@pytest.fixture
def saved_mct_ica(mct_ica) -> ica.IcaFif:
    """Mct ica instance saved to filesystem."""
    mct_ica.ica.save(mct_ica.fpath)
    return mct_ica
