"""Mct epochs fixtures."""
from typing import TYPE_CHECKING, Callable, Protocol

import numpy as np
import pytest
from mne import EpochsArray, create_info
from mne.epochs import EpochsFIF

from mne_cli_tools.mct_types import epochs

if TYPE_CHECKING:
    from pathlib import Path


class EpochsFactory(Protocol):  # noqa: D101
    def __call__(
        self, n_epo: int, n_ch: int, sfreq: float, epo_dur_sec: float
    ) -> EpochsArray:  # pyright: ignore
        """Create `Epochs` object."""


@pytest.fixture
def epochs_obj_factory() -> EpochsFactory:
    """Sample EpochsFif object factory."""

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


@pytest.fixture(params=epochs.EXTENSIONS)
def epochs_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def mct_epochs_factory(
    tmp_path: "Path", small_epochs_obj: EpochsFIF
) -> Callable[[str], epochs.EpochsFif]:

    def factory(epochs_ext: str) -> epochs.EpochsFif:
        return epochs.EpochsFif(tmp_path / f"test{epochs_ext}", small_epochs_obj)

    return factory


@pytest.fixture
def mct_epochs(epochs_ext: str, mct_epochs_factory: Callable[[str], epochs.EpochsFif]) -> epochs.EpochsFif:
    """Mct ica instance."""
    return mct_epochs_factory(epochs_ext)


@pytest.fixture
def saved_mct_epochs(mct_epochs) -> epochs.EpochsFif:
    """Mct ica instance saved to filesystem."""
    mct_epochs.epochs.save(mct_epochs.fpath)
    return mct_epochs
