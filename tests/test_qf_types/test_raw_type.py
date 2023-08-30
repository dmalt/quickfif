"""Test raw_type handling."""
from pathlib import Path
from typing import Callable

import mne
import pytest
from numpy.testing import assert_array_almost_equal

from quickfif.qf_types.raw_type import QfRaw
from quickfif.qf_types.raw_type import read as read_qf_raw


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def expected_summary(maybe_annotated_qf_raw: QfRaw) -> str:
    """Summary for small raw object."""
    n_ch = maybe_annotated_qf_raw.raw.info["nchan"]
    ch_names = maybe_annotated_qf_raw.raw.info["ch_names"]
    if n_ch > 4:
        chan_str = "  {0:3} misc  : {1:10} {2:10} {3:^10} {4}".format(
            n_ch, ch_names[0], ch_names[1], "...", ch_names[-1]
        )
    else:
        chan_str = "  {nchan:3} misc  : " + "".join([f"{n:10s}" for n in ch_names])

    if maybe_annotated_qf_raw.raw.annotations:
        annots_str = "\n".join(
            [
                "Annotations | duration stats, sec",
                "       count  mean  std  min  25%  50%  75%  max",
                "test      10  0.06 0.00 0.06 0.06 0.06 0.06 0.06",
                "Total     10  0.06 0.00 0.06 0.06 0.06 0.06 0.06",
            ]
        )
    else:
        annots_str = "Annotations | no annotations"

    return "\n".join(
        [
            "Raw | duration: {dur:.1f} sec, sampling rate: 100.0 Hz",
            "------------------------------------------------",
            "Channels    | total: {nchan}",
            chan_str.rstrip(),
            "Filter      | highpass: 0.0, lowpass: 50.0",
            "Recorded    | by: N/A, on: N/A",
            annots_str,
        ]
    ).format(dur=maybe_annotated_qf_raw.raw.times[-1], **maybe_annotated_qf_raw.raw.info)


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def maybe_annotated_qf_raw(
    request: pytest.FixtureRequest,
    small_raw_obj: mne.io.Raw,
    create_fake_annots: Callable[[float, float], mne.Annotations],
) -> QfRaw:
    """`QfRaw` wrapper around possibly annotated `mne.io.Raw`."""
    annotated_raw = small_raw_obj.copy()
    if request.param:
        t_start, t_stop = small_raw_obj.times[0], small_raw_obj.times[-1]
        annotated_raw.set_annotations(create_fake_annots(t_start, t_stop))
    return QfRaw(fpath=Path("test_raw.fif"), raw=annotated_raw)


def test_summary_string_contents(maybe_annotated_qf_raw: QfRaw, expected_summary: str) -> None:
    """
    Test summary for `QfRaw`.

    Check data dimensions = n_channels x n_samples are present and annotations
    section header depending on annotations presence.

    """
    assert expected_summary == maybe_annotated_qf_raw.summary, maybe_annotated_qf_raw.summary


def test_to_dict_wraps_fpath_and_raw(qf_raw: QfRaw) -> None:
    """Test to_dict wraps fpath and raw."""
    res = qf_raw.to_dict()

    assert qf_raw.fpath in res.values()
    assert qf_raw.raw in res.values()


def test_read_loads_same_data(saved_qf_raw: QfRaw) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = read_qf_raw(saved_qf_raw.fpath)

    assert_array_almost_equal(saved_qf_raw.raw.get_data(), loaded_raw.raw.get_data())
