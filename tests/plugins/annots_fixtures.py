"""Fixtures for qf_types package testing."""
from typing import TYPE_CHECKING, Callable

import numpy as np
import pytest
from mne import Annotations

from quickfif.qf_types.annots_type import EXTENSIONS, QfAnnots

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


@pytest.fixture(params=EXTENSIONS)
def annots_ext(request: pytest.FixtureRequest) -> str:
    """Extension for raw fif obj."""
    return request.param


@pytest.fixture
def annots_obj(create_fake_annots: Callable[[float, float], Annotations]) -> Annotations:
    """Lighweight mne.Annotations object."""
    return create_fake_annots(0, 1)


@pytest.fixture
def qf_annots_factory(tmp_path: "Path", annots_obj: Annotations) -> Callable[[str], QfAnnots]:
    """Create QfAnnots."""
    def factory(annots_ext: str) -> QfAnnots:
        save_fpath = tmp_path / f"test{annots_ext}"
        return QfAnnots(save_fpath, annots_obj)  # pyright: ignore

    return factory


@pytest.fixture
def qf_annots(annots_ext: str, qf_annots_factory: Callable[[str], QfAnnots]) -> QfAnnots:
    """Qf annotations instance."""
    return qf_annots_factory(annots_ext)


@pytest.fixture
def saved_qf_annots(qf_annots: QfAnnots) -> QfAnnots:
    """Qf annotations instance with annots saved to fpath."""
    qf_annots.annots.save(qf_annots.fpath)
    return qf_annots
