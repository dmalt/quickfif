from pathlib import Path
from typing import Callable

import pytest

from mne_cli_tools.config import Ftype, ext_to_ftype

EXTENSIONS = list(ext_to_ftype)


@pytest.fixture(params=EXTENSIONS)
def empty_file_w_ftype(request, empty_file_factory: Callable[[str], Path]) -> tuple[Path, Ftype]:
    """Fname for file with supported extension but unreadable contents + its ftype."""
    ext = request.param
    fpath = empty_file_factory(f"tmp{ext}")
    return fpath, ext_to_ftype[ext]
