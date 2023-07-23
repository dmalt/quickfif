"""Project-level fixtures."""
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(scope="session")
def empty_file_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Empty file factory. Parametrization by base name and extension."""

    def factory(fname: str) -> Path:
        empty_fpath = tmp_path_factory.mktemp("data", numbered=True) / fname
        empty_fpath.touch(exist_ok=False)
        return empty_fpath

    return factory


@pytest.fixture
def mock_fn_factory(mocker: MockerFixture) -> Callable[[object, str], Mock]:
    """Mock wrapped function with dummy returning return_value."""

    def factory(return_value: object, fn_namespace_path: str) -> Mock:  # pyright: ignore
        mock_copy = mocker.patch(fn_namespace_path, autospec=True)
        mock_copy.return_value = return_value
        return mock_copy

    return factory
