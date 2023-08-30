"""Test raw_type handling."""
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import mne
import pytest
from numpy.testing import assert_array_almost_equal

from quickfif.qf_types.raw_type import QfRaw
from quickfif.qf_types.raw_type import read as read_qf_raw

if TYPE_CHECKING:
    from tests.plugins.raw_fixtures import RawFactory  # pragma: no cover


@pytest.fixture(params=[True, False], ids=["with annots", "without annots"])
def expected_summary(maybe_annotated_qf_raw: QfRaw) -> str:
    """Summary for small raw object."""
    ii = maybe_annotated_qf_raw.raw.info
    n_ch = ii["nchan"]
    ch_names = ii["ch_names"]
    if n_ch > 4:
        chan_str = "  {0:3} misc  : {1:10} {2:10} {3:^10} {4}".format(
            n_ch, ch_names[0], ch_names[1], "...", ch_names[-1]
        )
    else:
        chan_str = "  {nchan:3} misc  : " + "".join([f"{n:10s}" for n in ch_names])  # noqa: WPS336

    if maybe_annotated_qf_raw.raw.annotations:
        annots_str = "\n".join(
            [
                "Annotations | duration stats, sec",
                "       count  mean  std  min  25%  50%  75%  max",
                "test      10  0.08 0.00 0.08 0.08 0.08 0.08 0.08",
                "Total     10  0.08 0.00 0.08 0.08 0.08 0.08 0.08",
            ]
        )
    else:
        annots_str = "Annotations | no annotations"

    by = ii["experimenter"] or "N/A"
    on = ii["meas_date"].strftime("%d/%m/%Y, %H:%m") if ii["meas_date"] else "N/A"
    return "\n".join(
        [
            "Raw | duration: {dur:.1f} sec, sampling rate: {sfreq:.1f} Hz",
            "------------------------------------------------",
            "Channels    | total: {nchan}",
            chan_str.rstrip(),
            "Filter      | highpass: {highpass:.1f}, lowpass: {lowpass:.1f}",
            "Recorded    | by: {by}, on: {on}",
            annots_str,
        ]
    ).format(dur=maybe_annotated_qf_raw.raw.times[-1], by=by, on=on, **ii)


@pytest.fixture(
    params=[
        {"annots": True, "n_ch": 10, "experimenter": None, "meas_date": None},
        {"annots": True, "n_ch": 2, "experimenter": "test", "meas_date": 1500000000},
        {"annots": True, "n_ch": 4, "experimenter": "test", "meas_date": None},
        {"annots": False, "n_ch": 2, "experimenter": None, "meas_date": 1500000000},
    ],
)
def maybe_annotated_qf_raw(
    request: pytest.FixtureRequest,
    raw_obj_factory: "RawFactory",
    create_fake_annots: Callable[[float, float], mne.Annotations],
) -> QfRaw:
    """`QfRaw` wrapper around possibly annotated `mne.io.Raw`."""
    raw = raw_obj_factory(request.param["n_ch"], sfreq=110, dur_sec=1.7)  # noqa: WPS432
    raw.info["experimenter"] = request.param["experimenter"]
    raw.set_meas_date(request.param["meas_date"])
    if request.param["annots"]:
        t_start, t_stop = raw.times[0], raw.times[-1]
        raw.set_annotations(create_fake_annots(t_start, t_stop))
    return QfRaw(fpath=Path("test_raw.fif"), raw=raw)


def test_summary_string_contents(maybe_annotated_qf_raw: QfRaw, expected_summary: str) -> None:
    """Test summary for `QfRaw`."""
    assert expected_summary == maybe_annotated_qf_raw.summary


def test_to_dict_wraps_fpath_and_raw(qf_raw: QfRaw) -> None:
    """Test to_dict wraps fpath and raw."""
    res = qf_raw.to_dict()

    assert qf_raw.fpath in res.values()
    assert qf_raw.raw in res.values()


def test_read_loads_same_data(saved_qf_raw: QfRaw) -> None:
    """Check if raw objects saved with supported extensions are loaded fine."""
    loaded_raw = read_qf_raw(saved_qf_raw.fpath)

    assert_array_almost_equal(saved_qf_raw.raw.get_data(), loaded_raw.raw.get_data())
