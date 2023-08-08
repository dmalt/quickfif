"""Test ipython console embedding."""
import sys
from io import StringIO
from typing import Callable

import pytest

from quickfif.ipython import embed_ipython


@pytest.fixture
def patch_io(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], StringIO]:
    """Patch stdin and stdtout. Return fake_stdout stream."""

    def factory(stdin_str: str) -> StringIO:
        fake_stdin = StringIO(stdin_str)
        fake_stdout = StringIO()
        monkeypatch.setattr(sys, "stdout", fake_stdout)
        monkeypatch.setattr(sys, "stdin", fake_stdin)
        return fake_stdout

    return factory


def test_real_ipython_launch_outputs_header(patch_io: Callable[[str], StringIO]) -> None:
    """Mock stdout and check printed header when ipython is launched for real."""
    fake_stdout = patch_io("exit")
    test_key, test_value = "test_key", "test_value"

    embed_ipython({test_key: test_value})
    output = fake_stdout.getvalue()

    assert test_key in output
    assert str(test_value) in output
