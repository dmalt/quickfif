from typing import TYPE_CHECKING, Callable

import pytest

from quickfif.qf_types.raw_type import QfRaw
from quickfif.qf_types.raw_type import save as save_qf_raw

if TYPE_CHECKING:
    from pathlib import Path

    from mne.io import Raw as MneRaw


@pytest.fixture
def large_qf_raw(
    tmp_path: "Path", raw_obj_factory: Callable[[int, float, float], "MneRaw"]
) -> QfRaw:
    """`QfRaw` object wrapping mne.io.Raw of ~10MB."""
    n_ch, sfreq, dur_sec = 10, 1000, 200
    mne_raw = raw_obj_factory(n_ch, sfreq, dur_sec)  # pyright: ignore
    fpath = tmp_path / "test_raw.fif"
    return QfRaw(fpath, mne_raw)


@pytest.mark.parametrize(
    "dst_fname, expected_split_fnames",
    [
        ("test_raw.fif", {"test_raw.fif", "test_raw-1.fif"}),
        ("test_raw.fif.gz", {"test_raw.fif.gz", "test_raw.fif-1.gz"}),
        ("test_meg.fif", {"test_split-01_meg.fif", "test_split-02_meg.fif"}),
    ],
)
def test_splits_named_according_to_ext(
    large_qf_raw: QfRaw,
    dst_fname: str,
    expected_split_fnames: set[str],
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """.."""
    save_dst = tmp_path_factory.mktemp("data") / dst_fname

    save_qf_raw(large_qf_raw, save_dst, overwrite=False, split_size="5MB")

    fnames = sorted(fpath.name for fpath in save_dst.parent.iterdir())
    assert len(fnames) >= 2, "We expect at least 2 splits."
    assert expected_split_fnames.issubset(fnames)
