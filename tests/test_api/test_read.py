"""Test api read."""
from collections import defaultdict
from pathlib import Path
from typing import Callable

import pytest
from returns.io import IOResult, IOResultE

from mne_cli_tools.api import commands
from mne_cli_tools.api.errors import BrokenFileError, ExitCode, UnsupportedFtypeError
from mne_cli_tools.config import Ftype, ReadFunc
from mne_cli_tools.types import MneType
from tests.fake_mne_type import FakeMneType


@pytest.fixture
def patch_read_dict(monkeypatch: pytest.MonkeyPatch) -> Callable[[IOResultE[MneType]], None]:
    """Patch `ftype_to_read_func` dictionary."""

    def wrapper(read_result: IOResultE[MneType]):
        def fake_read_func(_):  # noqa: WPS430
            return read_result

        patched: dict[Ftype, ReadFunc] = defaultdict(lambda: fake_read_func)
        monkeypatch.setattr(commands, "ftype_to_read_func", patched)

    return wrapper


@pytest.fixture(params=["tmp.empty", "a.txt", "long name with spaces.longext"])
def unsupported_fname(
    request: pytest.FixtureRequest, empty_file_factory: Callable[[str], Path]
) -> str:
    """Fname for existing file with unsupported extension."""
    return str(empty_file_factory(request.param))


def test_read_raises_unknown_file_error_on_existing_unknown_file(
    unsupported_fname: str,
) -> None:
    """Unknown file extension errors should raise click.Exception child to be handled nicely."""
    with pytest.raises(UnsupportedFtypeError) as exc_info:
        commands.read_mne_obj(Path(unsupported_fname), None)

        assert exc_info.value.exit_code is ExitCode.unsupported_file


@pytest.fixture
def fake_read_failure(
    empty_file_w_ftype: tuple[Path, Ftype],
    patch_read_dict: Callable[[IOResultE[MneType]], None],
) -> tuple[Path, Ftype]:
    """Fake mne object reading when the reading failed."""
    fpath, ftype = empty_file_w_ftype
    read_result = IOResult.from_failure(Exception())
    patch_read_dict(read_result)
    return fpath, ftype


@pytest.mark.parametrize("is_pass_ftype", [True, False], ids=["pass ft", "don't pass ft"])
def test_read_bad_file_causes_broken_file_error(
    fake_read_failure: tuple[Path, Ftype], is_pass_ftype: bool
) -> None:
    """Malformated file errors should raise BrokenFileError.

    BrokenFileError is a child of click.FileError, so this exception will cause
    a graceful app termination.

    """
    fpath, ftype = fake_read_failure

    with pytest.raises(BrokenFileError) as exc_info:
        commands.read_mne_obj(fpath, str(ftype) if is_pass_ftype else None)
        assert exc_info.value.exit_code == ExitCode.broken_file


@pytest.fixture
def fake_read_success(
    empty_file_w_ftype: tuple[Path, Ftype],
    patch_read_dict: Callable[[IOResultE[MneType]], None],
) -> tuple[Path, Ftype]:
    """Patch mne object reading.

    Patch the mapping from file type to reader function so each function
    returns fake mne type with wrapped fpath and ftype.

    """
    fpath, ftype = empty_file_w_ftype
    read_result = IOResult.from_value(FakeMneType(fpath, str(ftype)))
    patch_read_dict(read_result)
    return fpath, ftype


@pytest.mark.parametrize("is_pass_ftype", [True, False], ids=["pass ft", "don't pass ft"])
def test_read_returns_mne_obj_on_green_path(
    fake_read_success: tuple[Path, Ftype], is_pass_ftype: bool
) -> None:
    """Test api read function returns valid mne_obj."""
    fpath, ftype = fake_read_success

    mne_obj = commands.read_mne_obj(fpath, str(ftype) if is_pass_ftype else None)
    assert mne_obj.fpath == fpath
