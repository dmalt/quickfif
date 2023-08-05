"""Fixtures for mct_types package testing."""
from typing import TYPE_CHECKING, Callable

import numpy as np
import pytest
from mne import Annotations

from mne_cli_tools.mct_types import annotations

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def create_fake_annots() -> Callable[[float, float], Annotations]:
    """Create fake annotations."""

    def wrapped(  # noqa: WPS430
        t_start: float,
        t_stop: float,
        n_annots: int = 10,
        dur_frac: float = 0.5,
        desc: str = "test",
    ) -> Annotations:
        onsets = np.linspace(t_start, t_stop, n_annots, endpoint=False)
        dt = (t_stop - t_start) / n_annots * dur_frac
        duration, description = [dt] * n_annots, [desc] * n_annots  # noqa: WPS435 (list multiply)
        return Annotations(onsets, duration=duration, description=description)

    return wrapped


@pytest.fixture(params=annotations.EXTENSIONS)
def annots_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def mct_annots(
    annots_ext: str, tmp_path: "Path", create_fake_annots: Callable[[float, float], Annotations]
) -> Annotations:
    """Mct annotations instance."""
    save_fpath = tmp_path / f"test{annots_ext}"
    annots = create_fake_annots(0, 1)
    return annotations.AnnotsFif(save_fpath, annots)  # pyright: ignore


@pytest.fixture
def saved_mct_annots(mct_annots: annotations.AnnotsFif) -> annotations.AnnotsFif:
    """Mct annotations instance with annots saved to fpath."""
    mct_annots.annots.save(mct_annots.fpath)
    return mct_annots
