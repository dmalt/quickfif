"""Qf epochs fixtures."""
from typing import TYPE_CHECKING, Callable, Protocol

import numpy as np
import pytest
from mne import EpochsArray, create_info
from mne.epochs import EpochsFIF

from quickfif.qf_types.epochs_type import EXTENSIONS as EPOCHS_EXTENSIONS
from quickfif.qf_types.epochs_type import QfEpochs

if TYPE_CHECKING:
    from pathlib import Path


class EpochsFactory(Protocol):  # noqa: D101
    def __call__(
        self, n_epo: int, n_ch: int, sfreq: float, epo_dur_sec: float
    ) -> EpochsArray:  # pyright: ignore
        """Create `Epochs` object."""


@pytest.fixture
def epochs_obj_factory() -> EpochsFactory:
    """Sample QfEpochs object factory."""

    def factory(
        n_epo: int, n_ch: int, sfreq: float, epo_dur_sec: float, ch_types="misc"
    ) -> EpochsArray:
        n_samp = int(epo_dur_sec * sfreq)
        mne_info = create_info(ch_names=n_ch, sfreq=sfreq, ch_types=ch_types)
        return EpochsArray(data=np.random.randn(n_epo, n_ch, n_samp), info=mne_info)

    return factory


@pytest.fixture
def small_epochs_obj(epochs_obj_factory: EpochsFactory) -> EpochsArray:
    """Fast to process epochs object."""
    return epochs_obj_factory(5, 2, 100, epo_dur_sec=0.2)  # noqa: WPS432


@pytest.fixture
def large_qf_epochs(  # noqa: WPS210 (too many local variables)
    tmp_path: "Path", epochs_obj_factory: Callable[[int, int, float, float], EpochsArray]
) -> QfEpochs:
    """`QfEpochs` object wrapping mne.io.Raw of ~10MB."""
    n_epo, n_ch, sfreq, dur_sec = 4, 10, 1000, 50
    mne_epochs = epochs_obj_factory(n_epo, n_ch, sfreq, dur_sec)  # pyright: ignore
    fpath = tmp_path / "test_raw.fif"
    return QfEpochs(fpath, mne_epochs)  # pyright: ignore


@pytest.fixture
def qf_epochs_factory(tmp_path: "Path", small_epochs_obj: EpochsFIF) -> Callable[[str], QfEpochs]:
    """Create QfEpochs."""
    def factory(epochs_ext: str) -> QfEpochs:
        return QfEpochs(tmp_path / f"test{epochs_ext}", small_epochs_obj)

    return factory


@pytest.fixture(params=EPOCHS_EXTENSIONS)
def qf_epochs(
    request: pytest.FixtureRequest, qf_epochs_factory: Callable[[str], QfEpochs]
) -> QfEpochs:
    """Qf ica instance."""
    return qf_epochs_factory(request.param)


@pytest.fixture
def saved_qf_epochs(qf_epochs) -> QfEpochs:
    """Qf ica instance saved to filesystem."""
    qf_epochs.epochs.save(qf_epochs.fpath)
    return qf_epochs
