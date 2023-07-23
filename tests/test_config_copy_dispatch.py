"""Test config.copy() dispatching."""
from inspect import Parameter, signature
from typing import Callable, Protocol

import pytest

from mne_cli_tools.config import copy


class ArgParseFn(Protocol):
    """Protocol for arguments parsing function."""

    def __call__(self, fn: Callable) -> tuple[set[str], set[str]]:  # type: ignore
        """Parse arguments for `fn`."""


@pytest.fixture
def parse_args_fn() -> ArgParseFn:
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


def test_registered_copy_functions_have_coherent_signatures(parse_args_fn: ArgParseFn) -> None:
    """
    Test dispatch funcitons signatures.

    Dispatch functions only allowed to add arguments with default values on top of the
    default implementation signature.

    """
    base_required, base_default = parse_args_fn(copy)

    for dispatch_fn in copy.registry.values():
        disp_fn_required, disp_fn_default = parse_args_fn(dispatch_fn)
        assert base_required == disp_fn_required
        assert base_default.issubset(disp_fn_default), f"{base_default=}, {disp_fn_default=}"
