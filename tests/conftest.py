"""Project-level fixtures."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import numpy as np
import pytest
from mne import create_info
from mne.io import RawArray
from pytest_mock import MockerFixture

from mne_cli_tools.mne_types import raw_fif
from mne_cli_tools.types import MneType
from tests.fake_mne_type import FakeMneType


@pytest.fixture(scope="session")
def empty_file_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Empty file factory. Parametrization by base name and extension."""

    def factory(fname: str) -> Path:
        empty_fpath = tmp_path_factory.mktemp("data", numbered=True) / fname
        empty_fpath.touch(exist_ok=False)
        return empty_fpath

    return factory


@pytest.fixture
def mock_fn_factory(mocker: MockerFixture) -> Callable[[object, str], Mock]:
    """Mock wrapped function with dummy returning return_value."""

    def factory(return_value: object, fn_namespace_path: str) -> Mock:  # pyright: ignore
        mock_copy = mocker.patch(fn_namespace_path, autospec=True)
        mock_copy.return_value = return_value
        return mock_copy

    return factory


@pytest.fixture
def fake_mne_obj(tmp_path: Path) -> FakeMneType:
    """Mne obj wrapping fpath in temporary directory."""
    src_path = tmp_path / "test_fake.fk"
    src_path.touch()
    return FakeMneType(src_path, "test_obj")


@pytest.fixture
def raw_fif_obj(tmp_path: Path) -> raw_fif.RawFif:
    """Sample `mne.io.Raw` object."""
    n_ch, sfreq = 2, 100
    mne_info = create_info(ch_names=n_ch, sfreq=sfreq)
    raw_obj = RawArray(data=np.zeros([n_ch, sfreq]), info=mne_info)
    fpath = tmp_path / "test_raw.fif"
    raw_obj.save(fpath)
    return raw_fif.RawFif(fpath=fpath, raw=raw_obj)  # pyright: ignore


@pytest.fixture(
    params=[
        "fake_mne_obj",
        "raw_fif_obj",
    ]
)
def mne_obj(request) -> MneType:
    """Instance of various subtypes of `MneType`."""
    return request.getfixturevalue(request.param)
