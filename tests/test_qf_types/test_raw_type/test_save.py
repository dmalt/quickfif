from typing import Callable

import pytest

from quickfif.qf_types.raw_type import BIDS_EXT, EXTENSIONS, QfRaw
from quickfif.qf_types.raw_type import save as save_qf_raw


@pytest.fixture
def large_raw_fif_obj(raw_fif_obj_factory: Callable[[int, float, float, str], QfRaw]) -> QfRaw:
    """`QfRaw` object wrapping mne.io.Raw of ~10MB."""
    n_ch, sfreq, dur_sec = 10, 1000, 200
    return raw_fif_obj_factory(n_ch, sfreq, dur_sec, "test_raw.fif")  # pyright: ignore


# @pytest.mark.parametrize("ext", EXTENSIONS)
# @pytest.mark.parametrize("overwrite", [True, False])
# def test_save_names_splits_according_to_dst_ext(
#     large_raw_fif_obj: QfRaw,
#     ext: str,
#     tmp_path_factory: pytest.TempPathFactory,
#     overwrite: bool,
# ) -> None:
#     """."""
#     dst = tmp_path_factory.mktemp("data") / (large_raw_fif_obj.fpath.stem + ext)

#     save_qf_raw(large_raw_fif_obj, dst, overwrite=overwrite, split_size="5MB")

#     assert len(list(dst.parent.iterdir())) > 1, "We expect at least 2 splits."
#     for i_file, fpath in enumerate(sorted(dst.parent.iterdir())):
#         if ext in BIDS_EXT:
#             assert "split-0" in fpath.name
#         elif ext in EXTENSIONS and i_file:
#             assert fpath.name.endswith(f"-{i_file}.fif")
#         else:
#             assert fpath.name == dst.name, [p.name for p in sorted(dst.parent.iterdir())]
