import importlib


class PluginInterface:
    @staticmethod
    def initialize(extensions: list[str]) -> None:
        ...


def import_module(name: str) -> PluginInterface:
    return importlib.import_module(name)  # pyright: ignore


def load_plugins(file_types: dict[str, dict[str, list[str]]]) -> None:
    for ftype_module, module_config in file_types.items():
        plugin = import_module(ftype_module)
        plugin.initialize(module_config["extensions"])
