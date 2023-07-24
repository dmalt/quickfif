"""Test config.copy() dispatching."""
from inspect import Parameter, signature
from typing import Callable, Protocol

import pytest
from returns.functions import raise_exception
from returns.pipeline import is_successful

from mne_cli_tools.api.errors import UnsupportedOperationError
from mne_cli_tools.config import copy, ext_to_ftype, ftype_to_ext
from mne_cli_tools.types import MneType
from tests.fake_mne_type import FakeMneType


def test_no_duplicates_in_extensions():
    """Test extensions don't have any duplicates."""
    len_specified = sum(len(set(extensions)) for extensions in ftype_to_ext.values())

    assert len_specified == len(ext_to_ftype)


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
    base_required, base_default = parse_args(copy)

    for dispatch_fn in copy.registry.values():
        disp_fn_required, disp_fn_default = parse_args(dispatch_fn)
        assert base_required == disp_fn_required
        assert base_default.issubset(disp_fn_default), f"{base_default=}, {disp_fn_default=}"


def test_copy_fails_when_overwrite_false_and_dst_exists(mne_obj: MneType) -> None:
    """Test default implementation of copy fails when we try not permitted overwrite."""
    fpath = mne_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"
    dst.touch()

    res = copy(mne_obj, dst, overwrite=False)

    assert not is_successful(res)
    with pytest.raises(FileExistsError):
        res.alt(raise_exception).unwrap()


@pytest.mark.parametrize("overwrite", [True, False])
def test_copy_uses_src_fname_when_dst_is_dir(
    mne_obj: MneType, tmp_path_factory: pytest.TempPathFactory, overwrite: bool
) -> None:
    """Test copy default implementation when specifying directory as dst."""
    dst_dir = tmp_path_factory.mktemp("copy_dst_dir", numbered=True)
    dst_fpath = dst_dir / mne_obj.fpath.name
    assert not dst_fpath.exists()

    copy(mne_obj, dst_dir, overwrite)

    assert dst_fpath.exists()


@pytest.mark.parametrize("overwrite", [True, False])
def test_copy_fails_with_unsupported_operation_for_unregistered_type(
    fake_mne_obj: FakeMneType, overwrite: bool
) -> None:
    fpath = fake_mne_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"

    res = copy(fake_mne_obj, dst, overwrite)

    assert not is_successful(res)
    with pytest.raises(UnsupportedOperationError):
        res.alt(raise_exception).unwrap()
