"""Test config.mct_save() dispatching."""
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable, Protocol

import pytest

from mne_cli_tools.config import UnsupportedOperationError, mct_save
from mne_cli_tools.mct_types.base import MctType
from tests.plugins.fake_mct_type import FakeMctType

if TYPE_CHECKING:
    from pathlib import Path


class ArgParseFn(Protocol):
    """Protocol for arguments parsing function."""

    def __call__(self, fn: Callable) -> tuple[set[str], set[str]]:  # type: ignore
        """Parse arguments for `fn`."""


@pytest.fixture
def parse_args() -> ArgParseFn:
    """
    Argument parsing fixture.

    For a given function return two sets of argument names: ones that don't
    have a default value and ones that do.

    """

    def wrapped(fn: Callable) -> tuple[set[str], set[str]]:  # type: ignore  # noqa: WPS430
        all_params = signature(fn).parameters.items()
        required = {n for n, p in all_params if p.default is Parameter.empty}
        default = {n for n, p in all_params if p.default is not Parameter.empty}
        return required, default

    return wrapped


def test_registered_copy_functions_have_coherent_signatures(parse_args: ArgParseFn) -> None:
    """
    Test dispatch funcitons signatures.

    Dispatch functions only allowed to add arguments with default values on top of the
    default implementation signature.

    """
    base_required, base_default = parse_args(mct_save)

    for dispatch_fn in mct_save.registry.values():
        disp_fn_required, disp_fn_default = parse_args(dispatch_fn)
        assert base_required == disp_fn_required
        assert base_default.issubset(disp_fn_default), f"{base_default=}, {disp_fn_default=}"


def test_copy_fails_when_overwrite_false_and_dst_exists(saved_mct_obj: MctType) -> None:
    """Test default implementation of mct_save fails when we try not permitted overwrite."""
    fpath = saved_mct_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"
    dst.touch()

    with pytest.raises(FileExistsError):
        mct_save(saved_mct_obj, dst, overwrite=False)


@pytest.mark.parametrize("overwrite", [True, False])
def test_copy_uses_src_fname_when_dst_is_dir(
    saved_mct_obj: MctType, tmp_path_factory: pytest.TempPathFactory, overwrite: bool
) -> None:
    """Test mct_save default implementation when specifying directory as dst."""
    dst_dir = tmp_path_factory.mktemp("copy_dst_dir", numbered=True)
    dst_fpath = dst_dir / saved_mct_obj.fpath.name
    assert not dst_fpath.exists()

    mct_save(saved_mct_obj, dst_dir, overwrite)

    assert dst_fpath.exists()


@pytest.fixture
def fake_mct_obj(tmp_path: "Path") -> FakeMctType:
    """Mne obj wrapping fpath in temporary directory."""
    src_path = tmp_path / "test_fake.fk"
    src_path.touch()
    return FakeMctType(src_path, "test_obj")


@pytest.mark.parametrize("overwrite", [True, False])
def test_copy_fails_for_unregistered_type_with_unsupported_operation_error(
    fake_mct_obj: FakeMctType, overwrite: bool
) -> None:
    """
    Test mct_save fro ftype fails when ftype-specific implementation is not registered.

    Ftypes for which mct_save is not explicitly registered shouldn't use some
    default implementation silently.

    """
    fpath = fake_mct_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"

    with pytest.raises(UnsupportedOperationError):
        mct_save(fake_mct_obj, dst, overwrite)
