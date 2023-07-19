from typing import Callable

import mne
import numpy as np
import pytest


@pytest.fixture
def create_fake_annots() -> Callable[[float, float], mne.Annotations]:
    """Create fake annotations."""

    def wrapped(  # noqa: WPS430
        t_start: float,
        t_stop: float,
        n_annots: int = 10,
        dur_frac: float = 0.5,
        desc: str = "test",
    ) -> mne.Annotations:
        onsets = np.linspace(t_start, t_stop, n_annots, endpoint=False)
        dt = (t_stop - t_start) / n_annots * dur_frac
        duration, description = [dt] * n_annots, [desc] * n_annots  # noqa: WPS435 (list multiply)
        return mne.Annotations(onsets, duration=duration, description=description)

    return wrapped
