"""Test config.qf_save() dispatching."""
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable, Protocol

import pytest

from quickfif.config import UnsupportedOperationError, qf_save
from quickfif.qf_types.base import QfType
from tests.plugins.fake_qf_type import FakeQfType

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


def test_registered_save_functions_have_coherent_signatures(parse_args: ArgParseFn) -> None:
    """
    Test dispatch funcitons signatures.

    Dispatch functions only allowed to add arguments with default values on top of the
    default implementation signature.

    """
    base_required, base_default = parse_args(qf_save)

    for dispatch_fn in qf_save.registry.values():
        disp_fn_required, disp_fn_default = parse_args(dispatch_fn)
        assert base_required == disp_fn_required
        assert base_default.issubset(disp_fn_default), f"{base_default=}, {disp_fn_default=}"


def test_save_fails_when_overwrite_false_and_dst_exists(saved_qf_obj: QfType) -> None:
    """Test default implementation of qf_save fails when we try not permitted overwrite."""
    fpath = saved_qf_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"
    dst.touch()

    with pytest.raises(FileExistsError):
        qf_save(saved_qf_obj, dst, overwrite=False)


@pytest.mark.parametrize("overwrite", [True, False])
def test_save_uses_src_fname_when_dst_is_dir(
    saved_qf_obj: QfType, tmp_path_factory: pytest.TempPathFactory, overwrite: bool
) -> None:
    """Test qf_save default implementation when specifying directory as dst."""
    dst_dir = tmp_path_factory.mktemp("save_dst_dir", numbered=True)
    dst_fpath = dst_dir / saved_qf_obj.fpath.name
    assert not dst_fpath.exists()

    qf_save(saved_qf_obj, dst_dir, overwrite)

    assert dst_fpath.exists()


@pytest.fixture
def fake_qf_obj(tmp_path: "Path") -> FakeQfType:
    """Mne obj wrapping fpath in temporary directory."""
    src_path = tmp_path / "test_fake.fk"
    src_path.touch()
    return FakeQfType(src_path, "test_obj")


@pytest.mark.parametrize("overwrite", [True, False])
def test_save_fails_for_unregistered_type_with_unsupported_operation_error(
    fake_qf_obj: FakeQfType, overwrite: bool
) -> None:
    """
    Test qf_save fro ftype fails when ftype-specific implementation is not registered.

    Ftypes for which qf_save is not explicitly registered shouldn't use some
    default implementation silently.

    """
    fpath = fake_qf_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"

    with pytest.raises(UnsupportedOperationError):
        qf_save(fake_qf_obj, dst, overwrite)
