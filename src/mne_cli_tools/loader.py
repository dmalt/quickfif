"""Plugins loading and initialization."""
import importlib
from typing import Protocol


class SupportsInitialize(Protocol):
    """Protocol defining the structure of the plugins module."""

    @staticmethod
    def initialize(extensions: list[str]) -> None:  # noqa: WPS602
        """Register constructors for extensions handled by the plugin."""


def import_module(name: str) -> SupportsInitialize:
    """Import plugin module."""
    return importlib.import_module(name)  # pyright: ignore


_ModuleConfig = dict[str, list[str]]


def load_plugins(plugins_config: dict[str, _ModuleConfig]) -> None:
    """Load plugins according to the configuration."""
    for ftype_module, module_config in plugins_config.items():
        plugin = import_module(ftype_module)
        plugin.initialize(module_config["extensions"])
