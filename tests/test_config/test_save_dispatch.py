"""Test config.qf_save() dispatching."""
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Callable, Literal, Protocol

import pytest

from quickfif.config import Ftype, UnsupportedOperationError, qf_save
from tests.plugins.fake_qf_type import FakeQfType

if TYPE_CHECKING:
    from pathlib import Path

    from quickfif.qf_types.base import QfType
    from quickfif.qf_types.epochs_type import QfEpochs
    from quickfif.qf_types.raw_type import QfRaw

    class ArgParseFn(Protocol):
        """Protocol for arguments parsing function."""

        def __call__(self, fn: Callable) -> tuple[set[str], set[str]]:  # type: ignore
            """Parse arguments for `fn`."""


@pytest.fixture
def parse_args() -> "ArgParseFn":
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


def test_registered_save_functions_have_coherent_signatures(parse_args: "ArgParseFn") -> None:
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


def test_save_fails_when_overwrite_false_and_dst_exists(saved_qf_obj: "QfType") -> None:
    """Test default implementation of qf_save fails when we try not permitted overwrite."""
    fpath = saved_qf_obj.fpath
    dst = fpath.parent / f"copy_{fpath.name}"
    dst.touch()

    with pytest.raises(FileExistsError):
        qf_save(saved_qf_obj, dst, overwrite=False)


@pytest.mark.parametrize("overwrite", [True, False])
def test_save_uses_src_fname_when_dst_is_dir(
    saved_qf_obj: "QfType", tmp_path_factory: pytest.TempPathFactory, overwrite: bool
) -> None:
    """Test qf_save uses source filename for saving when specifying directory as dst."""
    dst_dir = tmp_path_factory.mktemp("save_dst_dir", numbered=True)
    dst_fpath = dst_dir / saved_qf_obj.fpath.name
    assert not dst_fpath.exists()

    qf_save(saved_qf_obj, dst_dir, overwrite)

    assert dst_fpath.exists()


@pytest.mark.parametrize("overwrite", [True, False])
def test_save_fails_for_unregistered_type(tmp_path: "Path", overwrite: bool) -> None:
    """
    Test qf_save fails when ftype-specific implementation is not registered.

    Ftypes for which qf_save is not explicitly registered shouldn't use some
    default implementation silently. `UnsupportedOperationError` should be
    raised instead.

    """
    fpath = tmp_path / "test_fake.fk"
    fake_qf_obj = FakeQfType(fpath, "test_obj")
    dst = fpath.parent / f"copy_{fpath.name}"

    with pytest.raises(UnsupportedOperationError):
        qf_save(fake_qf_obj, dst, overwrite)


@pytest.fixture
def large_qf_obj(
    ftype: Literal[Ftype.raw, Ftype.epochs], large_qf_raw: "QfRaw", large_qf_epochs: "QfEpochs"
) -> "QfEpochs | QfRaw":
    """Large qf_raw or qf_epochs object causing splits creation when saving."""
    if ftype == Ftype.epochs:
        return large_qf_epochs
    return large_qf_raw


@pytest.mark.parametrize(
    "ftype, dst_fname, expected_split_fnames",
    [
        (Ftype.raw, "test_raw.fif", {"test_raw.fif", "test_raw-1.fif"}),
        (Ftype.raw, "test_raw.fif.gz", {"test_raw.fif.gz", "test_raw.fif-1.gz"}),
        (Ftype.raw, "test_meg.fif", {"test_split-01_meg.fif", "test_split-02_meg.fif"}),
        (Ftype.epochs, "test-epo.fif", {"test-epo.fif", "test-epo-1.fif"}),
        (Ftype.epochs, "test-epo.fif.gz", {"test-epo.fif.gz", "test-epo.fif-1.gz"}),
        (Ftype.epochs, "test_epo.fif", {"test_epo.fif", "test_split-01_epo.fif"}),
    ],
)
def test_splits_named_according_to_dst_ext(
    large_qf_obj: "QfEpochs | QfRaw",
    dst_fname: str,
    expected_split_fnames: set[str],
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Test splits naming for raw and epochs."""
    save_dst = tmp_path_factory.mktemp("data") / dst_fname

    # passing split_size is a hack and type checking rightfully complains
    qf_save(large_qf_obj, save_dst, overwrite=False, split_size="5MB")  # type: ignore[call-arg]

    fnames = {fpath.name for fpath in save_dst.parent.iterdir()}
    assert len(fnames) >= 2, "We expect at least 2 splits."
    assert expected_split_fnames.issubset(fnames), (fnames, expected_split_fnames)
