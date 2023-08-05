"""Test raw_type handling."""
from pathlib import Path
from typing import Callable

import mne
import pytest

from mne_cli_tools.mct_types import raw_type
from mne_cli_tools.mct_types.raw_type import ANNOTS_SECTION_HEADER, NO_ANNOTS_MSG, MctRaw


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def maybe_annotated_mct_raw(
    request: pytest.FixtureRequest,
    small_raw_obj: mne.io.Raw,
    create_fake_annots: Callable[[float, float], mne.Annotations],
    raw_ext: str,
) -> MctRaw:
    """`MctRaw` wrapper around possibly annotated `mne.io.Raw`."""
    annotated_raw = small_raw_obj.copy()
    if request.param:
        t_start, t_stop = small_raw_obj.times[0], small_raw_obj.times[-1]
        annotated_raw.set_annotations(create_fake_annots(t_start, t_stop))
    return MctRaw(fpath=Path(f"test_{raw_ext}"), raw=annotated_raw)


def test_summary_string_contents(maybe_annotated_mct_raw: MctRaw) -> None:
    """
    Test summary for `MctRaw`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    n_ch = len(maybe_annotated_mct_raw.raw.ch_names)
    n_samples = len(maybe_annotated_mct_raw.raw.times)

    summary = maybe_annotated_mct_raw.summary

    assert str(n_ch) in summary
    assert str(n_samples) in summary
    if maybe_annotated_mct_raw.raw.annotations:
        assert ANNOTS_SECTION_HEADER in summary
    else:
        assert NO_ANNOTS_MSG in summary


def test_to_dict_wraps_fpath_and_raw(mct_raw: MctRaw) -> None:
    """Test to_dict wraps fpath and raw."""
    res = mct_raw.to_dict()

    assert mct_raw.fpath in res.values()
    assert mct_raw.raw in res.values()
