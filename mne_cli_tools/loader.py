import importlib


class PluginInterface:
    @staticmethod
    def initialize() -> None:
        ...


def import_module(name: str) -> PluginInterface:
    return importlib.import_module(name)  # pyright: ignore


def load_plugins(plugins: list[str]) -> None:
    for plugin in plugins:
        plugin = import_module(plugin)
        plugin.initialize()
